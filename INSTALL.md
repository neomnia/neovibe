# Installing neovibe on another machine

One command, then a setup wizard — same as `claude` on first run.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
```

(requires `kubectl` and `python3` already installed)

Optional but recommended — for the startup banner with the real NeoKube logo in color:
```bash
sudo apt install chafa   # or: brew install chafa
```
Without `chafa`, `neo` shows a simplified ASCII logo instead — works the same either way.

## First run

```bash
neo
```

Just like `claude` asks for an API key the first time, `neo` asks for **two things** to paste
(asked once, stored in `~/.neovibe/`, never versioned):

1. **Agent API key** — protects the agent itself.
2. **Cluster access token** — strictly scoped (port-forward + reading pods, a single namespace,
   verified in practice: rejected on everything else in the cluster). The certificate and cluster
   address are already known by the program, no need to provide them.

Get these two values from Charles (or generate them yourself on kubinote if you have access there,
see `CLAUDE-agent-topology.md` §9 in the Kubinote-GitOps repo).

After that, `neo` detects it's already configured and starts directly on every launch.

## Network requirements

The machine must be able to reach `REDACTED-INTERNAL-IP:6443` (kubinote's K8s API):
- On the same LAN as kubinote → works directly.
- Remotely → via Charles's personal WireGuard VPN (key reserved in Vault, connect it if not
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
