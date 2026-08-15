"""Bannière de démarrage neovibe — logo réel (https://www.neokube.fr) rendu via chafa si
disponible (vraies couleurs, blocs Unicode), sinon repli sur un hexagone ASCII simple."""
import shutil
import subprocess
import sys
from pathlib import Path

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
RESET = "\033[0m"

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.jpg"

# Repli si chafa n'est pas installé (`apt install chafa` / `brew install chafa`).
FALLBACK_LINES = [
    "         ╱◥◤╲         ",
    "       ╱      ╲       ",
    "     ╱          ╲     ",
    "    │   ┏━━━┓    │    ",
    "    │   ┃ N ┃    │    ",
    "    │   ┗━━━┛    │    ",
    "     ╲          ╱     ",
    "       ╲      ╱       ",
    "         ╲◢◣╱         ",
]


def _render_with_chafa() -> str | None:
    if not shutil.which("chafa") or not LOGO_PATH.exists():
        return None
    try:
        result = subprocess.run(
            ["chafa", "--size=28x14", "--colors=full", "--symbols=block", str(LOGO_PATH)],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None


def print_banner() -> None:
    if not sys.stdout.isatty():
        print(f"{BOLD}neovibe{RESET}")
        return

    rendered = _render_with_chafa()
    if rendered:
        print(rendered)
    else:
        for line in FALLBACK_LINES:
            print(f"{CYAN}{line}{RESET}")
    print(f"{BOLD}neovibe{RESET}{DIM} — client NeoKube{RESET}\n")


if __name__ == "__main__":
    print_banner()
