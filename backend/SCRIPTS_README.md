# Backend Setup Scripts

Automated scripts to make backend setup and testing easier.

---

## 📜 Available Scripts

### 1. `setup.sh` - Complete Backend Setup

**What it does:**
- Detects Python version and warns about compatibility issues
- Creates virtual environment
- Upgrades pip, setuptools, wheel
- Installs all dependencies (with Python 3.13 compatibility handling)
- Creates .env file from template
- Verifies installation

**Usage:**
```bash
cd backend
./setup.sh
```

**Features:**
- ✅ Automatic Python version detection
- ✅ Python 3.13+ compatibility handling (uses newer package versions)
- ✅ Retry logic with multiple installation strategies
- ✅ Color-coded output for easy reading
- ✅ Installation verification
- ✅ Interactive prompts for safety

---

### 2. `run.sh` - Start the Server

**What it does:**
- Activates virtual environment
- Checks for .env file
- Warns if ANTHROPIC_API_KEY is missing
- Starts FastAPI server with hot reload

**Usage:**
```bash
cd backend
./run.sh

# Or on a different port:
./run.sh 8001
```

**Output:**
- Server URL
- API docs URL
- Health check URL

---

### 3. `test-api.sh` - Test API Endpoints

**What it does:**
- Tests health check endpoint
- Tests root endpoint
- Tests OpenAPI schema
- Shows HTTP status codes and responses

**Usage:**
```bash
# Make sure server is running first!
# In another terminal:
cd backend
./test-api.sh

# Or test a different server:
./test-api.sh http://localhost:8001
```

**Output:**
- ✅ Green checkmark for successful tests
- ❌ Red X for failed tests
- Full response bodies

---

### 4. `install-python312.sh` - Install Python 3.12

**What it does:**
- Checks for Homebrew
- Installs Python 3.12 (recommended version)
- Shows installation instructions

**Usage:**
```bash
cd backend
./install-python312.sh
```

**Why Python 3.12?**
- Most stable version
- All packages have pre-built wheels
- No compilation required
- Recommended over 3.13 (too new, some packages don't have wheels yet)

---

## 🚀 Quick Start (Recommended)

### Option A: One-Line Setup (Python 3.13 - May Have Issues)

```bash
cd /Users/reidchatham/Developer/business-agent/backend && ./setup.sh
```

### Option B: Install Python 3.12 First (Recommended)

```bash
cd /Users/reidchatham/Developer/business-agent/backend
./install-python312.sh
rm -rf venv
python3.12 -m venv venv
./setup.sh
```

### Option C: Use Existing Python 3.11/3.12

```bash
cd /Users/reidchatham/Developer/business-agent/backend
python3.12 -m venv venv  # or python3.11
./setup.sh
```

---

## 🐛 Troubleshooting

### Issue: `pydantic-core` build fails

**Cause:** Python 3.13 is too new, packages don't have pre-built wheels

**Solution 1:** Install Python 3.12 (recommended)
```bash
./install-python312.sh
rm -rf venv
python3.12 -m venv venv
./setup.sh
```

**Solution 2:** Install Rust compiler (needed to build from source)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
./setup.sh
```

**Solution 3:** Use pyenv to manage Python versions
```bash
brew install pyenv
pyenv install 3.12.0
pyenv local 3.12.0
./setup.sh
```

---

### Issue: `setup.sh` permission denied

**Solution:**
```bash
chmod +x setup.sh run.sh test-api.sh install-python312.sh
./setup.sh
```

---

### Issue: Virtual environment activation fails

**Solution:**
```bash
# Make sure you're in the backend directory
cd /Users/reidchatham/Developer/business-agent/backend

# Source the script (don't execute it)
source venv/bin/activate

# Or manually activate
. venv/bin/activate
```

---

### Issue: `uvicorn: command not found`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify uvicorn is installed
pip list | grep uvicorn

# If not installed:
pip install uvicorn[standard]
```

---

### Issue: Port 8000 already in use

**Solution 1:** Use a different port
```bash
./run.sh 8001
```

**Solution 2:** Kill the process
```bash
lsof -ti:8000 | xargs kill -9
./run.sh
```

---

## 📊 Script Output Examples

### `setup.sh` Success Output
```
🚀 Bizy AI Backend Setup Script
================================

📍 Current directory: /Users/reidchatham/Developer/business-agent/backend
🐍 Detected Python version: 3.12

📦 Step 1: Creating virtual environment...
   ✅ Virtual environment created

🔌 Step 2: Activating virtual environment...
   ✅ Virtual environment activated

📦 Step 3: Upgrading pip...
   ✅ pip upgraded

📚 Step 4: Installing dependencies...
   This may take 2-3 minutes...
   ✅ All dependencies installed successfully

🔧 Step 5: Setting up environment variables...
   ✅ Created .env file
   ⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY

✅ Step 6: Verifying installation...
   FastAPI: 0.110.0
   Uvicorn: 0.27.0
   SQLAlchemy: 2.0.27
   Anthropic: 0.18.0

================================
🎉 Setup Complete!
================================
```

---

### `run.sh` Output
```
🚀 Starting Bizy AI Backend Server...

📍 Server will start at: http://localhost:8000
📚 API Docs: http://localhost:8000/api/docs
❤️  Health Check: http://localhost:8000/health

Press Ctrl+C to stop the server

INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### `test-api.sh` Output
```
🧪 Testing Bizy AI Backend API
================================
API URL: http://localhost:8000

Test 1: Health Check
GET http://localhost:8000/health
✅ Status: 200
Response: {"status":"healthy","service":"bizy-ai-api","version":"0.1.0"}

Test 2: Root Endpoint
GET http://localhost:8000/
✅ Status: 200
Response: {"message":"Bizy AI API","version":"0.1.0","docs":"/api/docs","health":"/health"}

Test 3: OpenAPI Schema
GET http://localhost:8000/api/openapi.json
✅ Status: 200
Schema available ✓

================================
🎉 API Testing Complete

View interactive docs at:
  📚 Swagger UI: http://localhost:8000/api/docs
  📖 ReDoc: http://localhost:8000/api/redoc
```

---

## 🔧 Customization

### Modify Dependencies

Edit `requirements-dev.txt` and re-run setup:
```bash
# Edit requirements
nano requirements-dev.txt

# Reinstall
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Change Default Port

Edit `run.sh` line 27:
```bash
PORT="${1:-8080}"  # Change 8000 to 8080
```

### Add Custom Environment Variables

Edit `.env.example` and `.env`:
```bash
# Add new variables
MY_CUSTOM_VAR=value

# Then update config.py
```

---

## 📝 Notes

- **Scripts assume you're on macOS/Linux** - Windows users should use WSL or Git Bash
- **Internet connection required** for package downloads
- **Disk space needed:** ~500MB for all dependencies
- **Time required:** 2-5 minutes for full setup

---

## 🎯 Next Steps After Setup

1. **Edit `.env`** - Add your `ANTHROPIC_API_KEY`
2. **Run the server** - `./run.sh`
3. **Test the API** - Open http://localhost:8000/api/docs
4. **Start coding** - Implement endpoints in `api/routes/`

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Backend README](README.md)
- [Phase 3 Architecture](../docs/PHASE_3_ARCHITECTURE.md)

---

**All scripts are located in:** `/Users/reidchatham/Developer/business-agent/backend/`
