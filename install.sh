#!/usr/bin/env bash
set -e
echo "Installing CatWalk..."

mkdir -p ~/.catwalk
git clone https://github.com/pycatwalk/catwalk ~/.catwalk || true

cat <<'EOF' > /usr/local/bin/catwalk
#!/usr/bin/env bash
python3 ~/.catwalk/catwalk.py "$@"
EOF

chmod +x /usr/local/bin/catwalk

echo "✅ CatWalk installed. Try:"
echo "   catwalk --help"
