# Installer neovibe sur une autre machine

`neo` fonctionne via `kubectl port-forward` — la machine distante a besoin d'un accès **scopé**
au cluster kubinote (jamais le kubeconfig admin complet), plus la clé API de l'agent.

## Prérequis réseau

La machine doit pouvoir joindre `REDACTED-INTERNAL-IP:6443` (API K8s de kubinote) :
- Sur le même LAN que kubinote → ça marche directement.
- À distance → via le VPN WireGuard personnel de Charles (`secret/neokube/tenants/<redacted>/wireguard-vpn`
  dans Vault — clé réservée, à connecter si pas déjà fait).

## Étapes

1. **kubectl** installé sur la machine (`brew install kubectl` / `apt install kubectl` / etc.)

2. **Récupérer les deux fichiers d'accès** (générés côté kubinote, à copier de façon sécurisée —
   pas par email/Slack en clair) :
   - `~/.neovibe/kubeconfig` — accès **limité** : juste port-forward + lister les pods dans le
     namespace `client-agent-core-staging`, rien d'autre (vérifié : refusé sur tout autre namespace).
   - `~/.neovibe/settings.local.json` — contient la clé API (`NEOVIBE_API_KEY`).

3. **Cloner et installer** :
   ```bash
   git clone https://github.com/neomnia/neovibe.git ~/repos/neovibe
   mkdir -p ~/.local/bin
   ln -s ~/repos/neovibe/bin/neo ~/.local/bin/neo
   ln -s ~/repos/neovibe/bin/neo_term.py ~/.local/bin/neo_term.py
   # ~/.local/bin doit être dans le PATH
   ```

4. **Dire à kubectl d'utiliser ce kubeconfig limité** — soit en le mettant à l'emplacement par
   défaut (`~/.kube/config`, si rien d'autre dessus), soit en l'exportant :
   ```bash
   export KUBECONFIG=~/.neovibe/kubeconfig
   ```
   (à ajouter dans `.bashrc`/`.zshrc` pour que ce soit permanent)

5. **Lancer** :
   ```bash
   neo
   ```

## Sécurité

- Le kubeconfig distribué n'a **aucun droit d'administration** — juste port-forward vers le
  namespace de Neo. Compromis ≠ accès au cluster.
- La clé API protège l'agent lui-même (401 sans elle).
- Deux couches indépendantes — voler l'une ne suffit pas.
