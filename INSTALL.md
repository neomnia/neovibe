# Installer neovibe sur une autre machine

Une commande, puis un assistant de configuration — comme `claude` au premier lancement.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
```

(nécessite `kubectl` et `python3` déjà installés)

## Premier lancement

```bash
neo
```

Comme `claude` te demande une clé API la première fois, `neo` te demande **deux choses** à coller
(demandé une seule fois, stocké dans `~/.neovibe/`, jamais versionné) :

1. **Clé API de l'agent** — protège l'agent lui-même.
2. **Jeton d'accès cluster** — portée strictement limitée (port-forward + lecture des pods, un
   seul namespace, vérifié en pratique : refusé sur tout le reste du cluster). Le certificat et
   l'adresse du cluster sont déjà connus par le programme, pas besoin de les fournir.

Récupère ces deux valeurs auprès de Charles (ou génère-les toi-même côté kubinote si tu y as accès,
voir `CLAUDE-agent-topology.md` §9 dans le repo Kubinote-GitOps).

Ensuite, à chaque lancement, `neo` détecte que c'est déjà configuré et démarre directement.

## Prérequis réseau

La machine doit pouvoir joindre `REDACTED-INTERNAL-IP:6443` (API K8s de kubinote) :
- Sur le même LAN que kubinote → ça marche directement.
- À distance → via le VPN WireGuard personnel de Charles (clé réservée dans Vault, à connecter
  si pas déjà fait).

## Reconfigurer / changer de clé

```bash
rm -rf ~/.neovibe
neo   # relance l'assistant
```

## Sécurité

- Le jeton distribué n'a **aucun droit d'administration** — juste port-forward vers le namespace
  de Neo. Compromis ≠ accès au cluster.
- La clé API protège l'agent lui-même (401 sans elle).
- Deux couches indépendantes — voler l'une ne suffit pas.
