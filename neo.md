# neo.md — context index, loaded at the start of every neovibe session

This file is neovibe's equivalent of `CLAUDE.md` — loaded automatically by `neo` at session start
and sent to the agent as context. This is a **template**: the real, deployment-specific context
(who the operator is, cluster topology, tool details, safety conventions) is meant to live in
`~/.neovibe/neo.md`, which **overrides this repo default automatically if present** — nothing to
configure, just create that file locally. Keeping deployment-specific details (names, internal
hostnames, infrastructure topology) out of the public repo and in a local, gitignored override is
intentional — see `~/.neovibe/` in `.gitignore`.

## Who you're talking to

(Fill in via `~/.neovibe/neo.md` — e.g. the operator's name/role and what agent you are.)

## Reference docs (not auto-loaded — consult on demand)

Add local reference files under `~/.neovibe/` for anything you want available on demand but not
sent with every message (topology maps, tool documentation, safety conventions) — same pattern as
this file's override mechanism. Point to them by name here once added.

## How to behave (kept here, not split out — applies to every single turn)

- Be direct and concrete — no filler, no re-explaining what was just asked.
- If you're missing a permission (RBAC, Vault scope), say so plainly instead of guessing.
- Never take a destructive action without it being explicit in your reply that you're about to.
