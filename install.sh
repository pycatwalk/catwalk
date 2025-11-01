#!/usr/bin/env bash
set -e

echo "Installing CatWalk v0.1.0 ..."

# Clone or refresh repository
rm -rf ~/.catwalk
git clone https://github.com/pycatwalk/catwalk ~/.catwalk

# Create isolated virtual environment
python3 -m venv ~/.catwalk/venv
source ~/.catwalk/venv/bin/activate

# Ensure pip exists and is updated
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r ~/.catwalk/requirements.txt

deactivate

# Create CLI launcher
mkdir -p ~/.local/bin
cat <<'EOF' > ~/.local/bin/catwalk
#!/usr/bin/env bash
source ~/.catwalk/venv/bin/activate
python ~/.catwalk/cli.py "$@"
deactivate
EOF
chmod +x ~/.local/bin/catwalk

# Add to PATH if missing
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ CatWalk installed successfully."
echo "Run: catwalk --help"
