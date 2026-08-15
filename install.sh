#!/bin/bash
# One-command neovibe installation.
#   curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash
set -e

REPO_DIR="$HOME/repos/neovibe"
BIN_DIR="$HOME/.local/bin"

echo "=== Installing neovibe ==="

if ! command -v kubectl >/dev/null 2>&1; then
  echo "⚠ kubectl is not installed. Install it first: https://kubernetes.io/docs/tasks/tools/"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠ python3 is not installed."
  exit 1
fi

mkdir -p "$(dirname "$REPO_DIR")" "$BIN_DIR"

if [ -d "$REPO_DIR/.git" ]; then
  echo "Repository already present — updating..."
  git -C "$REPO_DIR" pull -q origin main
else
  echo "Cloning..."
  git clone -q https://github.com/neomnia/neovibe.git "$REPO_DIR"
fi

ln -sf "$REPO_DIR/bin/neo" "$BIN_DIR/neo"
ln -sf "$REPO_DIR/bin/neo_term.py" "$BIN_DIR/neo_term.py"
ln -sf "$REPO_DIR/bin/neo_setup.py" "$BIN_DIR/neo_setup.py"
ln -sf "$REPO_DIR/bin/neo_banner.py" "$BIN_DIR/neo_banner.py"
chmod +x "$REPO_DIR/bin/neo" "$REPO_DIR/bin/neo_term.py" "$REPO_DIR/bin/neo_setup.py" "$REPO_DIR/bin/neo_banner.py"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "⚠ $BIN_DIR is not in your PATH — add this line to your .bashrc/.zshrc:"
     echo "  export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac

if ! command -v chafa >/dev/null 2>&1; then
  echo "(tip: install 'chafa' for the startup banner with the real NeoKube logo in color — optional)"
fi

echo ""
echo "✓ Installed. Just run:"
echo ""
echo "    neo"
echo ""
echo "On first run, you'll be asked to paste your API key and access token."
