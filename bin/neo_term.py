#!/usr/bin/env python3
"""Neo Code — terminal client for the Neo agent (SSE /mission/stream), multi-cluster topology pilot.

Persistent session (conversation memory on the agent side via a fixed session_id),
live display of tool calls and reasoning steps, Claude-Code-style.
"""
import json
import os
import sys
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


API_KEY = _load_api_key()
VERSION = _load_version()

DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def stream_mission(message: str) -> None:
    print(f"\n{BOLD}Request:{RESET} {message}", flush=True)

    payload = json.dumps({
        "message": message,
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
                if etype == "tool":
                    if not printed_work_header:
                        print(f"\n{BOLD}Working:{RESET}", flush=True)
                        printed_work_header = True
                    name = ev.get("name", "?")
                    print(f"{DIM}{CYAN}  ⚙ tool: {name}{RESET}", flush=True)
                elif etype == "step":
                    if not printed_work_header:
                        print(f"\n{BOLD}Working:{RESET}", flush=True)
                        printed_work_header = True
                    text = ev.get("text", "")
                    print(f"{DIM}{YELLOW}  → {text}{RESET}", flush=True)
                elif etype == "token":
                    if not printed_response_header:
                        print(f"\n{BOLD}Response:{RESET}", flush=True)
                        print(f"{BOLD}{GREEN}neo:{RESET} ", end="", flush=True)
                        printed_response_header = True
                    print(ev.get("text", ""), end="", flush=True)
                elif etype == "error":
                    print(f"\n{RED}✗ {ev.get('text', 'unknown error')}{RESET}", flush=True)
                elif etype == "done":
                    if not printed_response_header:
                        print(f"\n{BOLD}Response:{RESET}", flush=True)
                        print(f"{BOLD}{GREEN}neo:{RESET} {ev.get('answer', '')}", flush=True)
                    print("", flush=True)
                elif etype == "heartbeat":
                    pass
    except urllib.error.URLError as e:
        print(f"\n{RED}[connection error to Neo: {e}]{RESET}", flush=True)
    except Exception as e:
        print(f"\n{RED}[error: {e}]{RESET}", flush=True)


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
            msg = input(f"{BOLD}> {RESET}").strip()
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
