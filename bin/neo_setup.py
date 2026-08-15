#!/usr/bin/env python3
"""Assistant de configuration neovibe — lance automatiquement au premier `neo` si non configuré.
Deux informations à coller, rien d'autre (le certificat et l'adresse du cluster sont déjà connus) :
  1. La clé API de l'agent
  2. Le jeton d'accès (portée limitée : port-forward + lecture des pods, un seul namespace)
"""
import json
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".neovibe"
SETTINGS_FILE = CONFIG_DIR / "settings.local.json"
KUBECONFIG_FILE = CONFIG_DIR / "kubeconfig"

# Non secret — certificat public de l'autorité du cluster + adresse du serveur.
CLUSTER_CA_B64 = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJlRENDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUzTnpVMk16QTRNak13SGhjTk1qWXdOREE0TURVME56QXpXaGNOTXpZd05EQTFNRFUwTnpBegpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUzTnpVMk16QTRNak13V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFSRFRqdTJjWjZoY0RzdFBGd3c2WmIzS3Jpdm9iZTJQNVp4eGJVNzA1eVkKZHBpZ0R2bW0vS0Zid0RhZm5icFpseERqREZsdTVlVHpTa1c3cVJOYlZ0dmdvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVVk1S2pMbkh3TU95Y2RpZ01acUt6CkNMRFA4YXN3Q2dZSUtvWkl6ajBFQXdJRFNRQXdSZ0loQU56MEtIS1BJSEM1U3k1VVlscmdabDVtTEdxbWx6ZUYKeitnZ0tzdWgxM0Z5QWlFQTNrNTg3V09RSUJPc3VQQ2NWNnN3cEVnQVRwQUJpeHMzM3pESlQwRHpLVmc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
CLUSTER_SERVER = "https://REDACTED-INTERNAL-IP:6443"

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RESET = "\033[0m"


def _write_kubeconfig(token: str) -> None:
    content = f"""apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: {CLUSTER_CA_B64}
    server: {CLUSTER_SERVER}
  name: kubinote-neovibe
contexts:
- context:
    cluster: kubinote-neovibe
    user: neovibe-client
    namespace: client-agent-core-staging
  name: kubinote
current-context: kubinote
users:
- name: neovibe-client
  user:
    token: {token}
"""
    KUBECONFIG_FILE.write_text(content)
    KUBECONFIG_FILE.chmod(0o600)


def is_configured() -> bool:
    if not SETTINGS_FILE.exists() or not KUBECONFIG_FILE.exists():
        return False
    try:
        data = json.loads(SETTINGS_FILE.read_text())
        return bool(data.get("api_key"))
    except json.JSONDecodeError:
        return False


def run_wizard() -> None:
    print(f"{BOLD}=== Configuration de neovibe ==={RESET}")
    print(f"{DIM}Deux informations à coller (demandées une seule fois, stockées dans"
          f" ~/.neovibe/, jamais versionnées).{RESET}\n")

    api_key = input(f"{BOLD}Clé API de l'agent : {RESET}").strip()
    token = input(f"{BOLD}Jeton d'accès cluster : {RESET}").strip()

    if not api_key or not token:
        print("Configuration incomplète — rien n'a été sauvegardé.", file=sys.stderr)
        sys.exit(1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({"api_key": api_key}, indent=2))
    SETTINGS_FILE.chmod(0o600)
    _write_kubeconfig(token)

    print(f"\n{GREEN}✓ Configuré.{RESET} Lance `neo` pour démarrer.\n")


if __name__ == "__main__":
    if is_configured():
        print("Déjà configuré — rien à faire. (Pour reconfigurer : supprime ~/.neovibe/ et relance.)")
    else:
        run_wizard()
