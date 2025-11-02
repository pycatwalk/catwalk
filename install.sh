#!/bin/sh
# CatWalk installer - compatible with sh and bash
set -e

# Detect operating system
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "Installing CatWalk v0.1.0 for $OS ($ARCH)..."

# Set platform-specific variables
case "$OS" in
    Darwin*)
        PLATFORM="macOS"
        PYTHON_CMD="python3"
        SHELL_RC="$HOME/.zshrc"
        if [ ! -f "$SHELL_RC" ]; then
            SHELL_RC="$HOME/.bash_profile"
        fi
        ;;
    Linux*)
        PLATFORM="Linux"
        PYTHON_CMD="python3"
        SHELL_RC="$HOME/.bashrc"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        PLATFORM="Windows"
        PYTHON_CMD="python"
        SHELL_RC="$HOME/.bashrc"
        ;;
    *)
        echo "❌ Unsupported operating system: $OS"
        echo "Please install manually or use Docker."
        exit 1
        ;;
esac

echo "Detected platform: $PLATFORM"

# Check for required dependencies
check_dependency() {
    local cmd="$1"
    local display_name="${2:-$1}"
    
    if ! command -v "$cmd" >/dev/null 2>&1 && ! which "$cmd" >/dev/null 2>&1 && ! type "$cmd" >/dev/null 2>&1; then
        echo "❌ $display_name is required but not installed."
        case "$PLATFORM" in
            "macOS")
                if [ "$cmd" = "git" ]; then
                    echo "Install with: xcode-select --install"
                    echo "Or with Homebrew: brew install git"
                elif [ "$cmd" = "python3" ]; then
                    echo "Install with: brew install python"
                    echo "Or download from: https://python.org/"
                fi
                ;;
            "Linux")
                if [ "$cmd" = "git" ]; then
                    echo "Install with: sudo apt install git (Ubuntu/Debian)"
                    echo "Or: sudo yum install git (RHEL/CentOS)"
                    echo "Or: sudo pacman -S git (Arch)"
                elif [ "$cmd" = "python3" ]; then
                    echo "Install with: sudo apt install python3 python3-venv (Ubuntu/Debian)"
                    echo "Or: sudo yum install python3 python3-venv (RHEL/CentOS)"
                fi
                ;;
            "Windows")
                echo "Install from: https://git-scm.com/ and https://python.org/"
                ;;
        esac
        return 1
    fi
    return 0
}

echo "Checking dependencies..."

# Debug information
echo "Current PATH: $PATH"
echo "Looking for git..."
if command -v git >/dev/null 2>&1; then
    echo "✅ Git found at: $(command -v git)"
elif which git >/dev/null 2>&1; then
    echo "✅ Git found at: $(which git)"
elif type git >/dev/null 2>&1; then
    echo "✅ Git found via type command"
elif [ -x "/usr/bin/git" ]; then
    echo "✅ Git found at: /usr/bin/git"
    # Add /usr/bin to PATH if it's missing
    if [[ ":$PATH:" != *":/usr/bin:"* ]]; then
        export PATH="/usr/bin:$PATH"
        echo "Added /usr/bin to PATH"
    fi
else
    echo "❌ Git not found. Please install git:"
    echo "  sudo apt install git (Ubuntu/Debian)"
    echo "  sudo yum install git (RHEL/CentOS)"
    echo "  sudo pacman -S git (Arch)"
    exit 1
fi

echo "Looking for $PYTHON_CMD..."
if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "✅ $PYTHON_CMD found at: $(command -v "$PYTHON_CMD")"
elif which "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "✅ $PYTHON_CMD found at: $(which "$PYTHON_CMD")"
elif [ -x "/usr/bin/$PYTHON_CMD" ]; then
    echo "✅ $PYTHON_CMD found at: /usr/bin/$PYTHON_CMD"
    # Add /usr/bin to PATH if it's missing
    if [[ ":$PATH:" != *":/usr/bin:"* ]]; then
        export PATH="/usr/bin:$PATH"
        echo "Added /usr/bin to PATH"
    fi
else
    echo "❌ $PYTHON_CMD not found. Please install Python 3.8+:"
    echo "  sudo apt install python3 python3-venv (Ubuntu/Debian)"
    echo "  sudo yum install python3 python3-venv (RHEL/CentOS)"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Clone or refresh repository
echo "Downloading CatWalk..."
rm -rf ~/.catwalk
git clone https://github.com/pycatwalk/catwalk ~/.catwalk

# Create isolated virtual environment
echo "Setting up virtual environment..."
$PYTHON_CMD -m venv ~/.catwalk/venv

# Activate virtual environment (platform-specific)
case "$PLATFORM" in
    "Windows")
        . ~/.catwalk/venv/Scripts/activate
        ;;
    *)
        . ~/.catwalk/venv/bin/activate
        ;;
esac

# Ensure pip exists and is updated
echo "Installing dependencies..."
$PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || true
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel

# Install dependencies
if [ -f ~/.catwalk/requirements.txt ]; then
    pip install -r ~/.catwalk/requirements.txt
else
    # Fallback dependencies if requirements.txt doesn't exist
    pip install fastapi uvicorn click pydantic
fi

deactivate

# Create CLI launcher (platform-specific)
echo "Creating CLI launcher..."
case "$PLATFORM" in
    "Windows")
        mkdir -p ~/.local/bin
        cat <<'EOF' > ~/.local/bin/catwalk.bat
@echo off
call "%USERPROFILE%\.catwalk\venv\Scripts\activate.bat"
python "%USERPROFILE%\.catwalk\cli.py" %*
call "%USERPROFILE%\.catwalk\venv\Scripts\deactivate.bat"
EOF
        chmod +x ~/.local/bin/catwalk.bat
        
        # Create a bash-compatible wrapper for Git Bash/WSL
        cat <<'EOF' > ~/.local/bin/catwalk
#!/usr/bin/env bash
. ~/.catwalk/venv/Scripts/activate
python ~/.catwalk/cli.py "$@"
deactivate
EOF
        chmod +x ~/.local/bin/catwalk
        ;;
    *)
        mkdir -p ~/.local/bin
        cat <<'EOF' > ~/.local/bin/catwalk
#!/usr/bin/env bash
. ~/.catwalk/venv/bin/activate
python ~/.catwalk/cli.py "$@"
deactivate
EOF
        chmod +x ~/.local/bin/catwalk
        ;;
esac

# Add to PATH if missing (platform-specific)
echo "Updating PATH..."
case "$PLATFORM" in
    "macOS")
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            export PATH="$HOME/.local/bin:$PATH"
            echo "Added ~/.local/bin to PATH in $SHELL_RC"
        fi
        ;;
    "Linux")
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            export PATH="$HOME/.local/bin:$PATH"
            echo "Added ~/.local/bin to PATH in $SHELL_RC"
        fi
        ;;
    "Windows")
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            export PATH="$HOME/.local/bin:$PATH"
            echo "Added ~/.local/bin to PATH in $SHELL_RC"
            echo "Note: You may need to restart your terminal or run '. $SHELL_RC'"
        fi
        ;;
esac

echo ""
echo "🎉 CatWalk installed successfully!"
echo ""
case "$PLATFORM" in
    "macOS"|"Linux")
        echo "Run: catwalk --help"
        echo "Or restart your terminal and run: catwalk --help"
        ;;
    "Windows")
        echo "Run: catwalk --help (in Git Bash/WSL)"
        echo "Or: catwalk.bat --help (in Command Prompt/PowerShell)"
        echo "You may need to restart your terminal first."
        ;;
esac
echo ""
echo "Get started: https://github.com/pycatwalk/catwalk#quick-start"