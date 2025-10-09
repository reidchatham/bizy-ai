#!/bin/bash
# Business Agent Setup Script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🤖 Business Agent Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "   Get your key from: https://console.anthropic.com/"
    echo
    read -p "Press Enter to open .env in your default editor..."
    ${EDITOR:-nano} .env
else
    echo "✓ .env file already exists"
fi
echo

# Create necessary directories
echo "Creating directories..."
mkdir -p data
mkdir -p data/logs
echo "✓ Directories created"
echo

# Initialize database
echo "Setting up database..."
python3 scripts/init_db.py
echo

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.py
chmod +x main.py
echo "✓ Scripts are now executable"
echo

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✨ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Next steps:"
echo
echo "1. Test the agent:"
echo "   python scripts/morning_brief.py"
echo
echo "2. Start the automated scheduler:"
echo "   python main.py"
echo
echo "📚 Read README.md for full documentation"
echo
