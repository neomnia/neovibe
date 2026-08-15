#!/usr/bin/env python3
"""Neo Code — terminal agentique branche sur /mission/stream (SSE) de Neo (pilotage topologie multi-cluster).

Session persistante (memoire de conversation cote Charlotte via session_id fixe),
affichage en direct des outils utilises et des etapes de raisonnement, comme une
session Claude Code.
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
    """Clé API : env NEOVIBE_API_KEY prioritaire, sinon ~/.neovibe/settings.local.json (non versionné)."""
    if os.getenv("NEOVIBE_API_KEY"):
        return os.environ["NEOVIBE_API_KEY"]
    settings_path = Path.home() / ".neovibe" / "settings.local.json"
    try:
        data = json.loads(settings_path.read_text())
        return data.get("api_key", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


API_KEY = _load_api_key()

DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def stream_mission(message: str) -> None:
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
            buf = ""
            printed_tokens = False
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
                    name = ev.get("name", "?")
                    print(f"\n{DIM}{CYAN}  ⚙ outil: {name}{RESET}", flush=True)
                elif etype == "step":
                    text = ev.get("text", "")
                    print(f"{DIM}{YELLOW}  → {text}{RESET}", flush=True)
                elif etype == "token":
                    if not printed_tokens:
                        print(f"\n{BOLD}{GREEN}neo:{RESET} ", end="", flush=True)
                        printed_tokens = True
                    print(ev.get("text", ""), end="", flush=True)
                elif etype == "error":
                    print(f"\n{RED}✗ {ev.get('text', 'erreur inconnue')}{RESET}", flush=True)
                elif etype == "done":
                    if not printed_tokens:
                        print(f"\n{BOLD}{GREEN}neo:{RESET} {ev.get('answer', '')}", flush=True)
                    print("", flush=True)
                elif etype == "heartbeat":
                    pass
    except urllib.error.URLError as e:
        print(f"\n{RED}[erreur connexion Neo: {e}]{RESET}", flush=True)
    except Exception as e:
        print(f"\n{RED}[erreur: {e}]{RESET}", flush=True)


def main():
    print(f"{BOLD}=== Neo Code — Pilotage Topologie ==={RESET}")
    print(f"{DIM}API : {NEO_URL}/mission/stream")
    print(f"session : {SESSION_ID}{RESET}")
    if not API_KEY:
        print(f"{RED}⚠ Aucune clé API trouvée (NEOVIBE_API_KEY ou ~/.neovibe/settings.local.json) — "
              f"la connexion échouera si l'agent exige une authentification.{RESET}")
    print("Tapez un message puis Entrée. Ctrl+D ou 'exit' pour quitter.\n")
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

