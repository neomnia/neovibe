# Paramétrage neovibe — inspiré de Claude Code

Neovibe est le client terminal pour dialoguer avec les agents NeoKube (aujourd'hui Neo). Ce document
mappe les paramètres génériques réels de Claude Code vers leur équivalent proposé pour neovibe.

## Correspondance

| Claude Code | Rôle | Équivalent neovibe proposé |
|---|---|---|
| `~/.claude/settings.json` (global) + `.claude/settings.json` (projet) + `.claude/settings.local.json` (perso, non versionné) | Config en couches, la plus locale gagne | `~/.neovibe/settings.json` + `.neovibe/settings.json` (si lancé depuis un repo) + `.neovibe/settings.local.json` |
| `model` | Quel modèle utiliser | `agent` — quel agent NeoKube contacter (aujourd'hui : `neo` codé en dur via `NEO_URL`) — généraliser pour supporter Charlotte, futurs agents |
| `permissions.allow/deny/ask` + `defaultMode` (`default`/`acceptEdits`/`bypassPermissions`/`plan`) | Approbation des actions risquées côté client, pas juste côté serveur | **Aujourd'hui absent, et pas trivial à ajouter — voir limite architecturale ci-dessous.** |
| `hooks` (PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, Stop...) | Commandes shell locales déclenchées à des moments précis | Mêmes points d'ancrage côté client : avant envoi d'un message, à chaque `tool` reçu, à la fin d'une session — utile pour logger localement, notifier, etc. |
| `env` | Variables d'environnement injectées dans la session | Idem — ex. contexte kubectl par défaut, région, etc. |
| `CLAUDE.md` (racine projet, chargé comme contexte) | Mémoire/instructions projet | `NEOVIBE.md` ou réutilisation directe des `CLAUDE-*.md` déjà existants — le client pourrait charger le `CLAUDE-agent-topology.md` local et l'envoyer en contexte système à chaque session |
| `.claude/commands/*.md` | Commandes slash personnalisées | Commandes locales type `/nodes`, `/staging`, `/promote` — raccourcis qui envoient un message pré-formaté à l'agent |
| `cleanupPeriodDays` | Rétention des transcripts locaux | Rétention des logs de session neovibe (`~/.neovibe/sessions/`) |
| `statusLine` | Ligne de statut personnalisée | Affichage du cluster/nœud ciblé, session_id, coût/tokens si exposé par l'agent |
| `.mcp.json` (serveurs MCP externes) | Outils tiers branchés à l'agent | Hors périmètre client — c'est une préoccupation du **backend** agent (Neo), pas de neovibe |

## Limite architecturale — permissions côté client (important, lu avant de coder #5)

`/mission/stream` (SSE) est **à sens unique serveur→client**. Quand le client reçoit l'événement
`tool`, l'agent (`pydantic_ai`, dans `neomnia/neokube-agents`) a déjà décidé de l'appel et
l'exécute à l'itération suivante de sa boucle interne — il n'existe aucun canal pour que le client
interrompe cette boucle *avant* exécution. **Un vrai blocage/confirmation nécessite un changement
côté backend** (l'agent doit lui-même pauser avant d'exécuter un outil sensible et attendre une
confirmation via un aller-retour séparé — pas juste un filtre côté client sur le flux SSE).

Ce que le client peut faire *seul*, honnêtement : détecter après coup qu'un outil sensible vient
d'être appelé et l'afficher en alerte distincte (visibilité), pas l'empêcher. Ne pas confondre les
deux en implémentant — un "avertissement" qui ressemble à une protection sans en être une est pire
que rien.

## Ce qui a le plus de valeur à construire en premier

1. **`~/.neovibe/settings.json`** — fichier de config de base : `agent_url`, `agent_name`, `session_retention_days`. Remplace le hardcode `NEO_URL` actuel.
2. **Permissions côté client** — voir la limite architecturale ci-dessus avant de commencer. Un vrai blocage est un chantier à deux volets (backend + client), pas juste un filtre client sur le flux SSE.
3. **Mémoire projet (`NEOVIBE.md`)** — charger un contexte local avant chaque session, comme `CLAUDE.md`.
4. Hooks et commandes slash — utiles mais moins prioritaires que les deux premiers.

Pas encore implémenté — proposition à valider avant de coder, voir tickets Plane projet Neovibe.
