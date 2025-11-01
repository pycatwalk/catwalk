#!/usr/bin/env bash
set -e

echo "Installing CatWalk v0.1.0 ..."

# Clone repository
rm -rf ~/.catwalk
git clone https://github.com/<your-repo>/catwalk ~/.catwalk

# Install Python dependencies
python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r ~/.catwalk/requirements.txt

# Create CLI launcher
mkdir -p ~/.local/bin
cat <<'EOF' > ~/.local/bin/catwalk
#!/usr/bin/env bash
python3 ~/.catwalk/cli.py "$@"
EOF
chmod +x ~/.local/bin/catwalk

# Add to PATH if missing
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ CatWalk installed successfully."
echo "Run: catwalk --help"
