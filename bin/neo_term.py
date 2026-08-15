#!/usr/bin/env python3
"""Neo Code — terminal client for the Neo agent (SSE /mission/stream), multi-cluster topology pilot.

Persistent session (conversation memory on the agent side via a fixed session_id),
live display of tool calls and reasoning steps, Claude-Code-style.
"""
import json
import os
import re
import sys
import threading
import time
import urllib.request
import urllib.error
import uuid
from pathlib import Path

NEO_URL = os.getenv("NEO_URL", "http://neo.client-agent-core-staging.svc.cluster.local:8495")
SESSION_ID = os.getenv("NEO_SESSION_ID") or f"ttyd-{uuid.uuid4().hex[:12]}"


def _load_api_key() -> str:
    """API key: env NEOVIBE_API_KEY takes priority, else ~/.neovibe/settings.local.json (not versioned)."""
    if os.getenv("NEOVIBE_API_KEY"):
        return os.environ["NEOVIBE_API_KEY"]
    settings_path = Path.home() / ".neovibe" / "settings.local.json"
    try:
        data = json.loads(settings_path.read_text())
        return data.get("api_key", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


def _load_version() -> str:
    package_json = Path(__file__).resolve().parent.parent / "package.json"
    try:
        return json.loads(package_json.read_text()).get("version", "0.0.0")
    except (FileNotFoundError, json.JSONDecodeError):
        return "0.0.0"


def _load_context() -> str:
    """neo.md, neovibe's equivalent of CLAUDE.md — loaded once, sent with the first message of
    the session so Neo has it without it being repeated every turn. Kept short by design: it
    only carries always-relevant behavior rules, and points at neo-topology.md/neo-tools.md/
    neo-conventions.md as reference (those aren't auto-loaded, to avoid bloating every session).
    ~/.neovibe/neo.md overrides the repo's default if present (local customization)."""
    local_override = Path.home() / ".neovibe" / "neo.md"
    repo_default = Path(__file__).resolve().parent.parent / "neo.md"
    for path in (local_override, repo_default):
        try:
            return path.read_text()
        except FileNotFoundError:
            continue
    return ""


API_KEY = _load_api_key()
VERSION = _load_version()
CONTEXT = _load_context()
_context_sent = False

DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
CLEAR_LINE = "\033[2K\r"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class Spinner:
    """Live 'still working' indicator for the gaps between SSE events — Claude-Code-style
    reassurance that something is actually happening, not just a static line."""

    def __init__(self, label: str = "Working"):
        self.label = label
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _spin(self) -> None:
        i = 0
        while not self._stop.is_set():
            frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
            sys.stdout.write(f"{CLEAR_LINE}{BOLD}{CYAN}  {frame} {self.label}...{RESET}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.08)

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.5)
        sys.stdout.write(CLEAR_LINE)
        sys.stdout.flush()


def _render_markdown_line(line: str) -> str:
    """Light Markdown -> ANSI rendering so headers/bold don't show up as raw '#'/'**' in the
    terminal. Deliberately minimal — not a full Markdown renderer, just the common cases Neo
    actually produces (headers, bold, table rows left as-is since they're already readable)."""
    heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
    if heading_match:
        text = heading_match.group(2)
        text = re.sub(r"\*\*(.+?)\*\*", rf"{BOLD}\1{RESET}{BOLD}{CYAN}", text)
        return f"{BOLD}{CYAN}{text}{RESET}"
    line = re.sub(r"\*\*(.+?)\*\*", rf"{BOLD}\1{RESET}", line)
    return line


def stream_mission(message: str) -> None:
    global _context_sent
    wire_message = message
    if CONTEXT and not _context_sent:
        wire_message = f"[Context — neo.md]\n{CONTEXT}\n\n[User message]\n{message}"
        _context_sent = True

    payload = json.dumps({
        "message": wire_message,
        "session_id": SESSION_ID,
        "interface": "ttyd-neo",
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{NEO_URL}/mission/stream",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            **({"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}),
        },
        method="POST",
    )
    spinner = Spinner()
    spinner_running = False
    line_buffer = ""

    def flush_line(final: bool = False) -> None:
        """Print the buffered response line once it's complete (rendered through Markdown),
        since we can't tell if a line is a heading/bold until it's finished streaming."""
        nonlocal line_buffer
        if line_buffer or final:
            print(f"  {_render_markdown_line(line_buffer)}", flush=True)
            line_buffer = ""

    try:
        with urllib.request.urlopen(req, timeout=310) as resp:
            printed_work_header = False
            printed_response_header = False
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n")
                if not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if not data:
                    continue
                try:
                    ev = json.loads(data)
                except json.JSONDecodeError:
                    continue
                etype = ev.get("type")

                if spinner_running and etype != "heartbeat":
                    spinner.stop()
                    spinner_running = False

                if etype == "tool":
                    if not printed_work_header:
                        print(f"\n{BOLD}Working:{RESET}", flush=True)
                        printed_work_header = True
                    name = ev.get("name", "?")
                    print(f"{CYAN}  ⚙ tool: {name}{RESET}", flush=True)
                    spinner.start()
                    spinner_running = True
                elif etype == "step":
                    if not printed_work_header:
                        print(f"\n{BOLD}Working:{RESET}", flush=True)
                        printed_work_header = True
                    text = ev.get("text", "")
                    print(f"{YELLOW}  → {text}{RESET}", flush=True)
                    spinner.start()
                    spinner_running = True
                elif etype == "token":
                    if not printed_response_header:
                        print(f"\n{BOLD}Response:{RESET}", flush=True)
                        print(f"{BOLD}{GREEN}neo:{RESET}", flush=True)
                        printed_response_header = True
                    text = ev.get("text", "")
                    for ch in text:
                        if ch == "\n":
                            flush_line()
                        else:
                            line_buffer += ch
                elif etype == "error":
                    print(f"\n{RED}✗ {ev.get('text', 'unknown error')}{RESET}", flush=True)
                elif etype == "done":
                    if not printed_response_header:
                        answer = ev.get("answer", "")
                        print(f"\n{BOLD}Response:{RESET}", flush=True)
                        print(f"{BOLD}{GREEN}neo:{RESET}", flush=True)
                        for md_line in answer.split("\n"):
                            print(f"  {_render_markdown_line(md_line)}", flush=True)
                    else:
                        flush_line(final=True)
                    print("", flush=True)
                elif etype == "heartbeat":
                    if not spinner_running:
                        spinner.start()
                        spinner_running = True
    except urllib.error.URLError as e:
        if spinner_running:
            spinner.stop()
        print(f"\n{RED}[connection error to Neo: {e}]{RESET}", flush=True)
    except Exception as e:
        if spinner_running:
            spinner.stop()
        print(f"\n{RED}[error: {e}]{RESET}", flush=True)
    finally:
        if spinner_running:
            spinner.stop()


def _prompt_input() -> str:
    """Framed, distinctly-colored input line — Claude-Code-style, so the user always knows
    unambiguously where they're typing vs. where Neo is talking."""
    width = shutil_width()
    print(f"{MAGENTA}┌{'─' * (width - 1)}{RESET}")
    try:
        msg = input(f"{MAGENTA}│{RESET} {BOLD}{MAGENTA}❯{RESET} ").strip()
    finally:
        print(f"{MAGENTA}└{'─' * (width - 1)}{RESET}")
    return msg


def shutil_width() -> int:
    try:
        import shutil
        return shutil.get_terminal_size(fallback=(70, 20)).columns
    except Exception:
        return 70


def main():
    try:
        from neo_banner import print_banner
        print_banner(version=VERSION, session=SESSION_ID)
    except ImportError:
        print(f"{BOLD}neovibe{RESET} {DIM}v{VERSION}{RESET}")
    print(f"{DIM}API: {NEO_URL}/mission/stream{RESET}")
    if not API_KEY:
        print(f"{RED}⚠ No API key found (NEOVIBE_API_KEY or ~/.neovibe/settings.local.json) — "
              f"the connection will fail if the agent requires authentication.{RESET}")
    print("Type a message and press Enter. Ctrl+D or 'exit' to quit.\n")
    while True:
        try:
            msg = _prompt_input()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not msg:
            continue
        if msg.lower() in ("exit", "quit"):
            break
        stream_mission(msg)


if __name__ == "__main__":
    main()
