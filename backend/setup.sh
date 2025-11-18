#!/bin/bash
set -e  # Exit on error

echo "🚀 Bizy AI Backend Setup Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [[ ! -f "requirements-dev.txt" ]]; then
    echo -e "${RED}❌ Error: Run this script from the backend/ directory${NC}"
    echo "   cd backend && ./setup.sh"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check Python version (macOS compatible)
PYTHON_VERSION=$(python3 --version 2>&1 | sed 's/Python //')
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "🐍 Detected Python version: $PYTHON_VERSION"

# Warn if Python 3.13 (known compatibility issues)
if [[ "$PYTHON_MINOR" -ge 13 ]]; then
    echo -e "${YELLOW}⚠️  Warning: Python 3.13+ detected${NC}"
    echo "   Some packages may not have pre-built wheels yet."
    echo "   Recommendation: Use Python 3.11 or 3.12 for best compatibility."
    echo ""
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Step 1: Create virtual environment
echo ""
echo "📦 Step 1: Creating virtual environment..."
if [[ -d "venv" ]]; then
    echo -e "${YELLOW}   Virtual environment already exists${NC}"
    read -p "   Delete and recreate? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Deleting old venv..."
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}   ✅ New virtual environment created${NC}"
    else
        echo "   Using existing venv"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}   ✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "🔌 Step 2: Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}   ✅ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "📦 Step 3: Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}   ✅ pip upgraded${NC}"

# Install dependencies with fallback strategy
echo ""
echo "📚 Step 4: Installing dependencies..."
echo "   This may take 2-3 minutes..."

# Create a minimal requirements file for Python 3.13+
if [[ "$PYTHON_MINOR" -ge 13 ]]; then
    echo "   Using Python 3.13+ compatible versions..."
    cat > requirements-minimal.txt << 'EOF'
# Core dependencies with Python 3.13 support
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9

# Database
sqlalchemy>=2.0.27
alembic>=1.13.1
aiosqlite>=0.20.0

# Pydantic (use latest for Python 3.13 support)
pydantic>=2.6.0
pydantic-settings>=2.2.0
email-validator>=2.1.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.1.2

# WebSocket
python-socketio>=5.11.0
websockets>=12.0

# HTTP clients
httpx>=0.26.0
aiohttp>=3.9.3

# AI
anthropic>=0.18.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0

# Code quality
black>=24.0.0
isort>=5.13.0
flake8>=7.0.0

# Utilities
python-dotenv>=1.0.0
pytz>=2024.1
python-dateutil>=2.8.2
rich>=13.7.0
click>=8.1.7
EOF
    REQUIREMENTS_FILE="requirements-minimal.txt"
else
    REQUIREMENTS_FILE="requirements-dev.txt"
fi

# Install with retry and better error messages
if pip install -r $REQUIREMENTS_FILE; then
    echo -e "${GREEN}   ✅ All dependencies installed successfully${NC}"
else
    echo -e "${RED}   ❌ Some dependencies failed to install${NC}"
    echo ""
    echo "   Trying with --no-cache-dir and --use-pep517..."
    if pip install --no-cache-dir --use-pep517 -r $REQUIREMENTS_FILE; then
        echo -e "${GREEN}   ✅ Dependencies installed (second attempt)${NC}"
    else
        echo -e "${RED}   ❌ Installation failed${NC}"
        echo ""
        echo "   Troubleshooting options:"
        echo "   1. Use Python 3.11 or 3.12 (recommended)"
        echo "      ./install-python312.sh"
        echo ""
        echo "   2. Install Rust compiler (needed for some packages on Python 3.13):"
        echo "      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo "      source \$HOME/.cargo/env"
        echo "      ./setup.sh"
        echo ""
        echo "   3. Install core packages only:"
        echo "      pip install fastapi uvicorn sqlalchemy anthropic python-dotenv"
        exit 1
    fi
fi

# Cleanup temporary requirements file
if [[ -f "requirements-minimal.txt" ]]; then
    rm requirements-minimal.txt
fi

# Step 5: Set up environment variables
echo ""
echo "🔧 Step 5: Setting up environment variables..."
if [[ ! -f ".env" ]]; then
    cp .env.example .env
    echo -e "${GREEN}   ✅ Created .env file${NC}"
    echo -e "${YELLOW}   ⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY${NC}"
else
    echo "   .env already exists"
fi

# Step 6: Verify installation
echo ""
echo "✅ Step 6: Verifying installation..."
python -c "import fastapi; print(f'   FastAPI: {fastapi.__version__}')" 2>/dev/null || echo -e "${RED}   ❌ FastAPI not found${NC}"
python -c "import uvicorn; print(f'   Uvicorn: {uvicorn.__version__}')" 2>/dev/null || echo -e "${RED}   ❌ Uvicorn not found${NC}"
python -c "import sqlalchemy; print(f'   SQLAlchemy: {sqlalchemy.__version__}')" 2>/dev/null || echo -e "${RED}   ❌ SQLAlchemy not found${NC}"
python -c "import anthropic; print(f'   Anthropic: {anthropic.__version__}')" 2>/dev/null || echo -e "${RED}   ❌ Anthropic not found${NC}"

echo ""
echo "================================"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "     nano .env"
echo ""
echo "  2. Run the server:"
echo "     source venv/bin/activate"
echo "     uvicorn api.main:app --reload"
echo ""
echo "     OR use the run script:"
echo "     ./run.sh"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:8000/health"
echo "     Open http://localhost:8000/api/docs"
echo ""
echo "  4. To deactivate virtual environment later:"
echo "     deactivate"
echo ""
