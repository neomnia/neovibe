#!/bin/bash
# Installation neovibe en une commande.
#   curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
set -e

REPO_DIR="$HOME/repos/neovibe"
BIN_DIR="$HOME/.local/bin"

echo "=== Installation neovibe ==="

if ! command -v kubectl >/dev/null 2>&1; then
  echo "⚠ kubectl n'est pas installé. Installe-le d'abord : https://kubernetes.io/docs/tasks/tools/"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠ python3 n'est pas installé."
  exit 1
fi

mkdir -p "$(dirname "$REPO_DIR")" "$BIN_DIR"

if [ -d "$REPO_DIR/.git" ]; then
  echo "Dépôt déjà présent — mise à jour..."
  git -C "$REPO_DIR" pull -q origin main
else
  echo "Clonage..."
  git clone -q https://github.com/neomnia/neovibe.git "$REPO_DIR"
fi

ln -sf "$REPO_DIR/bin/neo" "$BIN_DIR/neo"
ln -sf "$REPO_DIR/bin/neo_term.py" "$BIN_DIR/neo_term.py"
ln -sf "$REPO_DIR/bin/neo_setup.py" "$BIN_DIR/neo_setup.py"
chmod +x "$REPO_DIR/bin/neo" "$REPO_DIR/bin/neo_term.py" "$REPO_DIR/bin/neo_setup.py"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "⚠ $BIN_DIR n'est pas dans ton PATH — ajoute cette ligne à ton .bashrc/.zshrc :"
     echo "  export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac

if ! command -v chafa >/dev/null 2>&1; then
  echo "(astuce : installe 'chafa' pour la bannière avec le vrai logo NeoKube en couleurs — optionnel)"
fi

echo ""
echo "✓ Installé. Lance simplement :"
echo ""
echo "    neo"
echo ""
echo "Au premier lancement, il te sera demandé de coller ta clé API et ton jeton d'accès."
