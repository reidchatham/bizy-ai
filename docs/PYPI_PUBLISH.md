# Publishing to PyPI

Your package is ready to publish! Here's how to upload it to PyPI.

## Files Created

✅ `dist/business_agent-1.0.0-py3-none-any.whl` (29KB)
✅ `dist/business_agent-1.0.0.tar.gz` (29KB)

## Step 1: Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account and verify your email
3. Enable 2FA (required for uploading)

## Step 2: Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `business-agent-upload`
4. Scope: "Entire account" (or specific to this project after first upload)
5. Copy the token (starts with `pypi-...`)

**Save this token securely - you won't see it again!**

## Step 3: Configure Credentials

```bash
# Option A: Use keyring (recommended)
source venv/bin/activate
pip install keyring
python -c "import keyring; keyring.set_password('pypi', '__token__', 'YOUR_TOKEN_HERE')"

# Option B: Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = YOUR_TOKEN_HERE
EOF
chmod 600 ~/.pypirc
```

## Step 4: Test on TestPyPI (Optional but Recommended)

Test your package on TestPyPI first:

```bash
# Create TestPyPI account at https://test.pypi.org/account/register/
# Create API token at https://test.pypi.org/manage/account/token/

source venv/bin/activate

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ business-agent
```

## Step 5: Upload to PyPI

```bash
source venv/bin/activate

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

You'll see:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading business_agent-1.0.0-py3-none-any.whl
Uploading business_agent-1.0.0.tar.gz
```

## Step 6: Verify Upload

Visit: https://pypi.org/project/business-agent/

## Step 7: Test Installation

```bash
# Anyone can now install with:
pip install business-agent

# Test it works:
bizy --help
bizy task list
```

## Updating the Package

When you make changes and want to release a new version:

```bash
# 1. Update version in pyproject.toml
# Change: version = "1.0.0" → version = "1.0.1"

# 2. Clean old builds
rm -rf dist/ build/ *.egg-info

# 3. Build new package
python -m build

# 4. Upload
twine upload dist/*
```

## Troubleshooting

### "File already exists"
- You've already uploaded this version
- Increment version number in `pyproject.toml`

### "Invalid authentication credentials"
- Check your API token is correct
- Make sure you're using `__token__` as username

### "Package name already taken"
- Someone else owns `business-agent`
- Choose a different name in `pyproject.toml`
- Try: `bizy-ai`, `business-agent-cli`, etc.

## Important Notes

⚠️ **You cannot delete or re-upload the same version**
⚠️ **Package names are first-come, first-served**
⚠️ **Keep your API token secure**

## After Publishing

Update your README.md to show:
```bash
pip install business-agent
```

Consider adding a badge:
```markdown
[![PyPI version](https://badge.fury.io/py/business-agent.svg)](https://badge.fury.io/py/business-agent)
```
