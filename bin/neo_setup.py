#!/usr/bin/env python3
"""Assistant de configuration neovibe — lancé automatiquement par `neo` selon le besoin réel :
  --api-key-only     : demande juste la clé API de l'agent (toujours nécessaire)
  --kubeconfig-only  : demande le jeton d'accès cluster (seulement si l'accès local ne marche pas déjà)
Sans argument : demande les deux (usage manuel / reconfiguration complète).
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


def _write_settings(api_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({"api_key": api_key}, indent=2))
    SETTINGS_FILE.chmod(0o600)


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
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    KUBECONFIG_FILE.write_text(content)
    KUBECONFIG_FILE.chmod(0o600)


def ask_api_key() -> None:
    print(f"{BOLD}=== Configuration neovibe — clé API ==={RESET}")
    api_key = input(f"{BOLD}Clé API de l'agent : {RESET}").strip()
    if not api_key:
        print("Clé vide — rien n'a été sauvegardé.", file=sys.stderr)
        sys.exit(1)
    _write_settings(api_key)
    print(f"{GREEN}✓ Clé enregistrée.{RESET}\n")


def ask_kubeconfig() -> None:
    print(f"{BOLD}=== Configuration neovibe — accès cluster ==={RESET}")
    print(f"{DIM}Cette machine n'a pas encore accès au cluster NeoKube.{RESET}")
    token = input(f"{BOLD}Jeton d'accès cluster : {RESET}").strip()
    if not token:
        print("Jeton vide — rien n'a été sauvegardé.", file=sys.stderr)
        sys.exit(1)
    _write_kubeconfig(token)
    print(f"{GREEN}✓ Accès configuré.{RESET}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--api-key-only" in args:
        ask_api_key()
    elif "--kubeconfig-only" in args:
        ask_kubeconfig()
    else:
        ask_api_key()
        ask_kubeconfig()
