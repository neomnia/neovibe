"""Bannière de démarrage neovibe — inspirée du logo NeoKube (cube + N), https://www.neokube.fr."""
import sys
import time

CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Cube hexagonal filaire + N, dérivé du logo neokube.fr (hexagone = cube en isométrique)
BANNER_LINES = [
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


def print_banner(animate: bool = True) -> None:
    """Affiche la bannière. Animation légère (dessin ligne par ligne) si animate=True et sortie TTY."""
    if animate and sys.stdout.isatty():
        for line in BANNER_LINES:
            print(f"{CYAN}{line}{RESET}")
            time.sleep(0.03)
    else:
        for line in BANNER_LINES:
            print(f"{CYAN}{line}{RESET}")
    print(f"{BOLD}neovibe{RESET}{DIM} — client NeoKube{RESET}\n")


if __name__ == "__main__":
    print_banner()
