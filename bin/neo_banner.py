"""neovibe startup banner — real logo (https://www.neokube.fr) rendered via chafa if
available (true colors, Unicode blocks, transparent background), otherwise falls back to a
simple ASCII hexagon. Info (name, version, session) is placed to the right of the logo."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
RESET = "\033[0m"

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
LOGO_SIZE = "18x9"  # compact, transparent background — info sits to the right

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

# Fallback if chafa isn't installed (`apt install chafa` / `brew install chafa`).
FALLBACK_LINES = [
    "  ╱◥◤╲  ",
    " ╱    ╲ ",
    "│ ┏━┓  │",
    "│ ┃N┃  │",
    "│ ┗━┛  │",
    " ╲    ╱ ",
    "  ╲◢◣╱  ",
]


def _render_logo_lines() -> list[str] | None:
    if not shutil.which("chafa") or not LOGO_PATH.exists():
        return None
    try:
        result = subprocess.run(
            ["chafa", f"--size={LOGO_SIZE}", "--colors=full", "--symbols=block", str(LOGO_PATH)],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        lines = result.stdout.split("\n")
        return [ln for ln in lines if ln.strip("\x1b[?25l").strip()]
    except Exception:
        return None


def print_banner(version: str = "", session: str = "") -> None:
    if not sys.stdout.isatty():
        print(f"{BOLD}neovibe{RESET}")
        return

    logo_lines = _render_logo_lines()
    if not logo_lines:
        logo_lines = [f"{CYAN}{line}{RESET}" for line in FALLBACK_LINES]
        visible_width = len(FALLBACK_LINES[0])
    else:
        visible_width = max(len(ANSI_RE.sub("", ln)) for ln in logo_lines)

    info_lines = [f"{BOLD}neovibe{RESET}"]
    if version:
        info_lines.append(f"{DIM}v{version}{RESET}")
    info_lines.append(f"{DIM}NeoKube client{RESET}")
    if session:
        info_lines.append(f"{DIM}session {session}{RESET}")

    # Vertically center the info block against the logo block.
    pad_top = max(0, (len(logo_lines) - len(info_lines)) // 2)
    info_padded = [""] * pad_top + info_lines
    info_padded += [""] * (len(logo_lines) - len(info_padded))

    for logo_line, info_line in zip(logo_lines, info_padded):
        visible_len = len(ANSI_RE.sub("", logo_line))
        pad = " " * (visible_width - visible_len + 2)
        print(f"{logo_line}{pad}{info_line}")
    print()


if __name__ == "__main__":
    print_banner(version="0.0.0", session="demo-session")
