# Installing neovibe on another machine

One command, then a setup wizard — same as `claude` on first run.

## Installation

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
```

(requires `kubectl` and `python3` already installed)

Optional but recommended — for the startup banner with the real NeoKube logo in color:
```bash
sudo apt install chafa   # or: brew install chafa
```
Without `chafa`, `neo` shows a simplified ASCII logo instead — works the same either way.

### Windows

neovibe is a bash + Python client (kubectl port-forward under the hood) — there's no native
Windows rewrite, it runs through **WSL** (Windows Subsystem for Linux), exactly like on Linux.
One command in PowerShell:

```powershell
irm https://raw.githubusercontent.com/neomnia/neovibe/main/install.ps1 | iex
```

If WSL isn't installed yet, the script tells you to run `wsl --install` (as Administrator),
restart, then re-run the command — it installs neovibe inside WSL automatically once WSL is
available. Afterwards, launch `neo` from a WSL terminal (the "Ubuntu" app, or `wsl` in
PowerShell/Windows Terminal).

## First run

```bash
neo
```

Just like `claude` asks for an API key the first time, `neo` asks for a few things to paste
(asked once, stored in `~/.neovibe/`, never versioned):

1. **Agent API key** — protects the agent itself.
2. **Cluster API server address** — deployment-specific, ask your NeoKube admin.
3. **Cluster access token** — strictly scoped (port-forward + reading pods, a single namespace,
   verified in practice: rejected on everything else in the cluster). The CA certificate is
   already known by the program (public, not secret), no need to provide it.

Get these values from your NeoKube admin (or generate them yourself on kubinote if you have
access there — see the internal topology docs in the private GitOps repo).

After that, `neo` detects it's already configured and starts directly on every launch.

## Network requirements

The machine must be able to reach kubinote's K8s API on the internal network:
- On the same LAN as kubinote → works directly.
- Remotely → via the admin's WireGuard VPN (ask your NeoKube admin for access, connect it if not
  already done).

## Reconfigure / change key

```bash
rm -rf ~/.neovibe
neo   # relaunches the wizard
```

## Security

- The distributed token has **no admin rights** — just port-forward to Neo's namespace.
  A compromised token ≠ cluster access.
- The API key protects the agent itself (401 without it).
- Two independent layers — stealing one isn't enough.
