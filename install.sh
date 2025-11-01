#!/usr/bin/env bash
set -e
echo "Installing CatWalk v0.1.0 ..."

mkdir -p ~/.catwalk
git clone https://github.com/pycatwalk/catwalk ~/.catwalk || true

mkdir -p ~/.local/bin
cat <<'EOF' > ~/.local/bin/catwalk
#!/usr/bin/env bash
python3 ~/.catwalk/cli.py "$@"
EOF
chmod +x ~/.local/bin/catwalk

export PATH="$HOME/.local/bin:$PATH"

echo "✅ CatWalk installed. Try:"
echo "   catwalk --help"
