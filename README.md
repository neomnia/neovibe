# neovibe

Client terminal pour dialoguer avec les agents NeoKube — équivalent du CLI `claude` pour Claude Code.

Aujourd'hui : branché sur **Neo** (agent de pilotage de la topologie multi-cluster NeoKube, `client-agent-core-staging` sur kubinote). Conçu pour être réutilisable avec d'autres agents NeoKube à terme (Charlotte, futurs agents), via la variable d'environnement `NEO_URL`.

## Installation

```bash
git clone https://github.com/neomnia/neovibe.git
ln -s $(pwd)/neovibe/bin/neo ~/.local/bin/neo
ln -s $(pwd)/neovibe/bin/neo_term.py ~/.local/bin/neo_term.py
```

## Usage

```bash
neo
```

Ouvre automatiquement un `kubectl port-forward` vers le service `neo` (namespace `client-agent-core-staging`,
cluster `kubinote`) et lance une session terminal interactive — streaming de la réponse, mémoire de session
persistante côté agent. `Ctrl+D` ou `exit` pour quitter (le port-forward est coupé proprement).

## Architecture

- `bin/neo` — script bash, gère le port-forward + lance le client Python.
- `bin/neo_term.py` — client terminal, consomme le flux SSE `/mission/stream` de l'agent (mêmes types
  d'événements que Charlotte : `tool`, `step`, `token`, `error`, `done`, `heartbeat`).

Le code de l'**agent** (backend, PydanticAI, outils multi-cluster) vit dans `Kubinote-GitOps/apps/agents-core/base/configmap-neo-script.yaml`, pas ici — ce dépôt est uniquement le client, comme `claude` (CLI) est séparé du modèle/backend Claude.

Voir `CLAUDE-agent-topology.md` (repo Kubinote-GitOps) pour le contexte complet.
