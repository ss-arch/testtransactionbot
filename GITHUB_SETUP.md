# GitHub Setup Guide

## Quick Setup Steps

### 1. Initialize Git Repository

```bash
cd /Users/ss/my-app
git init
```

### 2. Configure Git (if not already done)

```bash
# Set your GitHub username
git config --global user.name "YourGitHubUsername"

# Set your GitHub email
git config --global user.email "your.email@example.com"
```

### 3. Add All Files

```bash
git add .
```

### 4. Create Initial Commit

```bash
git commit -m "Initial commit: Multi-network transaction monitor bot

- TON, Everscale, Venom, Humanode (HUMO) support
- Telegram notifications for $100k+ transactions
- Comprehensive test suite (82% passing)
- HUMO token monitoring implementation
- Automated testing with pytest

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 5. Connect to Your GitHub Repository

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual values:

```bash
# If using HTTPS
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# OR if using SSH (recommended)
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

### 6. Set Main Branch and Push

```bash
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Detailed Instructions

### If You Get "Permission Denied" Error

This means you need to set up authentication with GitHub.

**Option A: Use Personal Access Token (Easier)**

1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a name like "Transaction Monitor Bot"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token (you won't see it again!)
7. When pushing, use:
   ```bash
   git push -u origin main
   # When prompted for password, paste your token
   ```

**Option B: Use SSH Keys (More Secure)**

1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   # Press Enter to accept default location
   # Optionally set a passphrase
   ```

2. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. Add to GitHub:
   - Go to GitHub.com → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste your public key
   - Click "Add SSH key"

4. Test connection:
   ```bash
   ssh -T git@github.com
   # Should see: "Hi USERNAME! You've successfully authenticated"
   ```

5. Use SSH URL for remote:
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
   ```

---

## What Gets Pushed to GitHub

Based on the `.gitignore` file, these files will be **excluded**:
- ❌ `.env` (your secrets - GOOD!)
- ❌ `bot.log` (log files)
- ❌ `__pycache__/` (Python cache)
- ❌ `.pytest_cache/` (test cache)
- ❌ `htmlcov/` (coverage reports)

These files **will be included**:
- ✅ All Python source code
- ✅ `.env.example` (template, no secrets)
- ✅ Test files
- ✅ Documentation (README, TESTING.md, etc.)
- ✅ Configuration files

---

## Repository Structure on GitHub

After pushing, your repo will look like:

```
your-repo/
├── .gitignore
├── .env.example
├── README.md
├── QUICKSTART.md
├── TESTING.md
├── TEST_RESULTS.md
├── PROJECT_SUMMARY.md
├── GITHUB_SETUP.md (this file)
├── requirements.txt
├── pytest.ini
├── run_tests.sh
├── main.py
├── config.py
├── telegram_bot.py
├── monitors/
│   ├── __init__.py
│   ├── base_monitor.py
│   ├── ton_monitor.py
│   ├── everscale_monitor.py
│   ├── venom_monitor.py
│   └── humanode_monitor.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_monitors.py
    ├── test_telegram_bot.py
    └── test_integration.py
```

---

## Recommended GitHub Repository Settings

### 1. Repository Description
```
Multi-network blockchain transaction monitor bot. Tracks $100k+ transactions on TON, Everscale, Venom, and Humanode (HUMO) networks with Telegram notifications.
```

### 2. Topics/Tags
Add these topics to your repository:
- `telegram-bot`
- `blockchain`
- `ton`
- `everscale`
- `venom`
- `humanode`
- `humo-token`
- `cryptocurrency`
- `transaction-monitoring`
- `python`
- `pytest`
- `asyncio`

### 3. Create a Good README Badge Section

Add to top of README.md:
```markdown
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-23%2F28%20passing-green.svg)](./TEST_RESULTS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

---

## After First Push

### Create GitHub Issues (Optional)

Document known issues:
1. "Improve HTTP mock library for tests"
2. "Add Docker support"
3. "Implement webhook support"
4. "Add database for historical tracking"

### Set Up GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest -v
```

---

## Common Issues & Solutions

### "Repository not found"
- Check the URL is correct
- Ensure you have access to the repository
- Verify your authentication (token or SSH key)

### "Permission denied (publickey)"
- You need to set up SSH keys (see Option B above)
- Or use HTTPS with a personal access token

### "Updates were rejected"
- Someone else pushed to the repo
- Run: `git pull origin main --rebase`
- Then: `git push origin main`

### "Nothing to commit"
- Files might already be in .gitignore
- Check: `git status` to see what's staged
- Use: `git add -f filename` to force-add if needed

---

## Updating Repository Later

```bash
# After making changes
git add .
git commit -m "Your commit message"
git push

# Or shorter version
git commit -am "Your commit message" && git push
```

---

## Need Help?

Check the repository status:
```bash
git status          # See what's changed
git log --oneline   # See commit history
git remote -v       # See remote URLs
```

Good luck! 🚀
