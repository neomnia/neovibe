#!/usr/bin/env python3
"""neovibe setup wizard — launched automatically by `neo` when needed:
  --api-key-only     : asks just for the agent's API key (always required)
  --kubeconfig-only  : asks for the cluster access token (only if local access doesn't already work)
No argument: asks for both (manual use / full reconfiguration).
"""
import json
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".neovibe"
SETTINGS_FILE = CONFIG_DIR / "settings.local.json"
KUBECONFIG_FILE = CONFIG_DIR / "kubeconfig"

# Not secret — public cluster CA certificate. The server address, on the other hand, is
# deployment-specific (private LAN IP) and asked interactively below rather than hardcoded, so
# this file has nothing deployment-specific baked in (this repo is public).
CLUSTER_CA_B64 = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJlRENDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUzTnpVMk16QTRNak13SGhjTk1qWXdOREE0TURVME56QXpXaGNOTXpZd05EQTFNRFUwTnpBegpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUzTnpVMk16QTRNak13V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFSRFRqdTJjWjZoY0RzdFBGd3c2WmIzS3Jpdm9iZTJQNVp4eGJVNzA1eVkKZHBpZ0R2bW0vS0Zid0RhZm5icFpseERqREZsdTVlVHpTa1c3cVJOYlZ0dmdvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVVk1S2pMbkh3TU95Y2RpZ01acUt6CkNMRFA4YXN3Q2dZSUtvWkl6ajBFQXdJRFNRQXdSZ0loQU56MEtIS1BJSEM1U3k1VVlscmdabDVtTEdxbWx6ZUYKeitnZ0tzdWgxM0Z5QWlFQTNrNTg3V09RSUJPc3VQQ2NWNnN3cEVnQVRwQUJpeHMzM3pESlQwRHpLVmc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RESET = "\033[0m"


def _write_settings(api_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({"api_key": api_key}, indent=2))
    SETTINGS_FILE.chmod(0o600)


def _write_kubeconfig(token: str, server: str) -> None:
    content = f"""apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: {CLUSTER_CA_B64}
    server: {server}
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
    print(f"{BOLD}=== neovibe setup — API key ==={RESET}")
    api_key = input(f"{BOLD}Agent API key: {RESET}").strip()
    if not api_key:
        print("Empty key — nothing was saved.", file=sys.stderr)
        sys.exit(1)
    _write_settings(api_key)
    print(f"{GREEN}✓ Key saved.{RESET}\n")


def ask_kubeconfig() -> None:
    print(f"{BOLD}=== neovibe setup — cluster access ==={RESET}")
    print(f"{DIM}This machine doesn't have access to the NeoKube cluster yet.{RESET}")
    server = input(f"{BOLD}Cluster API server (e.g. https://10.0.0.5:6443): {RESET}").strip()
    token = input(f"{BOLD}Cluster access token: {RESET}").strip()
    if not server or not token:
        print("Empty server/token — nothing was saved.", file=sys.stderr)
        sys.exit(1)
    _write_kubeconfig(token, server)
    print(f"{GREEN}✓ Access configured.{RESET}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--api-key-only" in args:
        ask_api_key()
    elif "--kubeconfig-only" in args:
        ask_kubeconfig()
    else:
        ask_api_key()
        ask_kubeconfig()
