#!/bin/bash
# Script to install Python 3.12 (recommended version) via Homebrew

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐍 Python 3.12 Installation Script${NC}"
echo "===================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo -e "${RED}❌ Homebrew not found${NC}"
    echo ""
    echo "Install Homebrew first:"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo -e "${GREEN}✅ Homebrew found${NC}"
echo ""

# Check if Python 3.12 is already installed
if brew list python@3.12 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3.12 is already installed${NC}"
    python3.12 --version
    echo ""
    read -p "Reinstall anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Install Python 3.12
echo "📦 Installing Python 3.12..."
echo "   This may take a few minutes..."
echo ""

if brew install python@3.12; then
    echo ""
    echo -e "${GREEN}✅ Python 3.12 installed successfully${NC}"
    echo ""

    # Show version
    python3.12 --version
    echo ""

    # Instructions
    echo "================================"
    echo -e "${GREEN}🎉 Installation Complete!${NC}"
    echo "================================"
    echo ""
    echo "To use Python 3.12 for the backend:"
    echo ""
    echo "  1. Remove existing venv (if any):"
    echo "     cd backend"
    echo "     rm -rf venv"
    echo ""
    echo "  2. Create new venv with Python 3.12:"
    echo "     python3.12 -m venv venv"
    echo ""
    echo "  3. Run setup script:"
    echo "     ./setup.sh"
    echo ""
    echo "Or use the quick setup command:"
    echo "  cd backend && rm -rf venv && python3.12 -m venv venv && ./setup.sh"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Installation failed${NC}"
    echo ""
    echo "Try manual installation:"
    echo "  brew install python@3.12"
    exit 1
fi
