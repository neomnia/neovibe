# neovibe

Terminal client to talk to NeoKube agents — the equivalent of the `claude` CLI for Claude Code.

Today: connected to **Neo** (multi-cluster NeoKube topology pilot agent, `client-agent-core-staging`
on kubinote). Designed to be reusable with other NeoKube agents later (Charlotte, future agents),
via the `NEO_URL` environment variable.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
```

See `INSTALL.md` for details (including setup on a machine other than kubinote).

## Usage

```bash
neo
```

Automatically opens a `kubectl port-forward` to the `neo` service (namespace `client-agent-core-staging`,
`kubinote` cluster) and starts an interactive terminal session — streamed response, persistent session
memory on the agent side. `Ctrl+D` or `exit` to quit (the port-forward is cleanly closed).

Each turn shows three clearly labeled sections: **Request** (what you asked), **Working** (tool
calls made live, if any), and **Response** (the agent's final answer).

## Architecture

- `bin/neo` — bash script, handles the port-forward + launches the Python client.
- `bin/neo_term.py` — terminal client, consumes the agent's `/mission/stream` SSE feed (same event
  types as Charlotte: `tool`, `step`, `token`, `error`, `done`, `heartbeat`).
- `bin/neo_banner.py` — startup banner (real NeoKube logo via `chafa`, ASCII fallback).
- `bin/neo_setup.py` — first-run configuration wizard (API key + cluster access token).

The **agent** code (backend, PydanticAI, multi-cluster tools) lives in
`Kubinote-GitOps/apps/agents-core/base/configmap-neo-script.yaml`, not here — this repo is only the
client, the same way `claude` (CLI) is separate from the Claude model/backend.

See `CLAUDE-agent-topology.md` (Kubinote-GitOps repo) for the full context.

## Versioning — patch vs release

Automatic via semantic-release (Conventional Commits) — no manual action, just follow the commit
message prefix:

| Prefix | Effect | Example |
|---|---|---|
| `fix:` | **Patch version** (bug fix) — 0.1.0 → 0.1.1 | `fix: handle the case where the agent doesn't respond` |
| `feat:` | **Minor version** (new feature) — 0.1.0 → 0.2.0 | `feat: add client-side permissions` |
| `feat!:` or `BREAKING CHANGE:` in the body | **Major version** — 0.1.0 → 1.0.0 | A change that breaks compatibility (e.g. incompatible settings.json format) |
| `docs:`, `chore:`, `refactor:` (without `fix`/`feat`) | No new version | Documentation, cleanup |

A Git tag + a `CHANGELOG.md` entry are generated automatically on every push to `main` that contains
a "releasable" commit. The current version is displayed in the `neo` banner at every launch.
