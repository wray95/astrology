# How to Push to GitLab

## Quick Start (5 minutes)

### 1. Create a GitLab Project

Go to https://gitlab.com and:
1. Click **"New project"**
2. Name it: `astrology-research`
3. Set visibility: **Private** (or Public if you want to share)
4. Click **Create**

Copy the project URL: `https://gitlab.com/YOUR_USERNAME/astrology-research.git`

---

## Option A: SSH Push (Recommended)

### Setup SSH Key (One-time)

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your.email@gmail.com"
# Press Enter for all prompts (use defaults)

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub

# Add to GitLab:
# 1. Go to https://gitlab.com/-/user_settings/ssh_keys
# 2. Paste the key
# 3. Click "Add key"

# Test connection
ssh -T git@gitlab.com
# Expected output: "Welcome to GitLab, @YOUR_USERNAME!"
```

### Push Repository

```bash
cd /home/claude/astrology-research

# Initialize git repo
git init
git config user.email "your.email@gmail.com"
git config user.name "Your Name"

# Add remote
git remote add origin git@gitlab.com:YOUR_USERNAME/astrology-research.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: 5,070 verified birth records with astrological charts and life events"

# Push to GitLab
git branch -M main
git push -u origin main

# Done!
echo "✓ Repository pushed to GitLab"
```

---

## Option B: HTTPS Push (Simpler, No SSH Setup)

### Setup GitLab Personal Access Token

1. Go to https://gitlab.com/-/user_settings/personal_access_tokens
2. Click **"Add new token"**
3. Name: `gitlab_push`
4. Scopes: Check `api` and `write_repository`
5. Click **Create**
6. **Copy the token** (you won't see it again!)

### Push Repository

```bash
cd /home/claude/astrology-research

# Initialize git repo
git init
git config user.email "your.email@gmail.com"
git config user.name "Your Name"

# Add remote (replace TOKEN and USERNAME)
git remote add origin https://YOUR_TOKEN@gitlab.com/YOUR_USERNAME/astrology-research.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: 5,070 verified birth records with astrological charts and life events"

# Push to GitLab
git branch -M main
git push -u origin main

# Done!
echo "✓ Repository pushed to GitLab"
```

**Note:** Git will store your credentials locally after first push.

---

## Option C: Automated Script

### Create `push.sh`

Save this as `push.sh` in the project root:

```bash
#!/bin/bash

set -e

echo "=== Pushing Astrology Research to GitLab ==="
echo ""

# Prompt for GitLab username
read -p "Your GitLab username: " GITLAB_USER
read -p "Use SSH (ssh) or HTTPS (https)? [ssh/https]: " PUSH_METHOD

if [ "$PUSH_METHOD" = "https" ]; then
    read -p "GitLab Personal Access Token: " GITLAB_TOKEN
    REMOTE_URL="https://${GITLAB_TOKEN}@gitlab.com/${GITLAB_USER}/astrology-research.git"
else
    REMOTE_URL="git@gitlab.com:${GITLAB_USER}/astrology-research.git"
fi

# Initialize git repo
echo "Initializing git repository..."
git init
git config user.email "$(git config user.email || echo 'user@example.com')"
git config user.name "$(git config user.name || echo 'Astrology Researcher')"

# Add remote
echo "Adding remote: $REMOTE_URL"
git remote add origin "$REMOTE_URL" 2>/dev/null || git remote set-url origin "$REMOTE_URL"

# Add all files
echo "Adding files..."
git add .

# Commit
echo "Creating commit..."
git commit -m "Initial commit: 5,070 verified birth records with astrological calculations

- births_20000.csv: Verified birth data (Rodden AA/A)
- charts_20000.json: D1, D9, yogas, Vimshottari dasha
- events_20000.csv: 22,783 linked life events
- Documentation: Schema, sources, methodology" || echo "Nothing to commit"

# Push
echo "Pushing to GitLab..."
git branch -M main
git push -u origin main --force

echo ""
echo "✅ Successfully pushed to GitLab!"
echo "Repository: https://gitlab.com/${GITLAB_USER}/astrology-research"
```

### Run Script

```bash
chmod +x push.sh
./push.sh
```

---

## Project Structure After Push

```
astrology-research/
├── README.md                       [Project overview]
├── .gitignore                      [Git settings]
├── .gitlab-ci.yml                  [CI/CD pipeline]
├── PUSH_TO_GITLAB.md              [This file]
├── data/
│   ├── births_20000.csv           [5,070 birth records]
│   ├── charts_20000.json          [Astrological charts]
│   └── events_20000.csv           [22,783 life events]
└── docs/
    ├── SCHEMA_AND_METHODOLOGY.md  [Complete schema + pipeline]
    └── DATA_SOURCES.md            [Sources + validation]
```

---

## Verify Push Success

After pushing, check:

```bash
# Check local repo status
git log --oneline
# Should show your commit

# Check remote
git remote -v
# Should show your GitLab URL

# Verify files on GitLab
# Go to: https://gitlab.com/YOUR_USERNAME/astrology-research
# Should see all files listed
```

---

## CI/CD Pipeline (Automatic Validation)

GitLab will automatically run validation tests on push:

1. **Validate births** — Check all records
2. **Validate charts** — Verify D1, D9, yogas, dasha
3. **Validate events** — Check event dates and links
4. **Generate report** — Summary statistics

Check pipeline status: https://gitlab.com/YOUR_USERNAME/astrology-research/-/pipelines

---

## Troubleshooting

### "Permission denied (publickey)"
**Problem:** SSH key not working  
**Solution:**
```bash
# Check SSH key loaded
ssh-add ~/.ssh/id_ed25519

# Test connection
ssh -T git@gitlab.com
```

### "Authentication failed"
**Problem:** Token expired or wrong  
**Solution:**
```bash
# Generate new token at:
# https://gitlab.com/-/user_settings/personal_access_tokens

# Reset remote URL
git remote set-url origin https://NEW_TOKEN@gitlab.com/USERNAME/astrology-research.git
```

### "Repository not found"
**Problem:** Wrong username or project doesn't exist  
**Solution:**
```bash
# Verify GitLab project exists:
# https://gitlab.com/YOUR_USERNAME/astrology-research

# Check remote URL
git remote -v
```

### Large files warning
**Problem:** JSON file is 7.4 MB  
**Solution:** This is fine! GitLab allows up to 5 GB per repository.  
If you get warnings, you can use Git LFS (Large File Storage):

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.json"
git add .gitattributes

# Re-push
git add data/*.json
git commit -m "Track large JSON with Git LFS"
git push
```

---

## Next Steps After Push

1. **Share the link:**
   ```
   https://gitlab.com/YOUR_USERNAME/astrology-research
   ```

2. **Invite collaborators** (if Private):
   - Project → Members → Add members

3. **Explore data** on GitLab:
   - View CSV files directly in browser
   - Download raw data files
   - Check CI/CD validation results

4. **Analyze locally:**
   ```bash
   git clone git@gitlab.com:YOUR_USERNAME/astrology-research.git
   cd astrology-research
   python analysis_script.py
   ```

---

## File Sizes

```
births_20000.csv    391 KB
charts_20000.json   7.4 MB
events_20000.csv    1.7 MB
─────────────────────────
Total:              9.5 MB
```

All files track fine in Git (no need for LFS unless you plan to add more data).

---

## Support

- **GitLab Help:** https://docs.gitlab.com/
- **Git Docs:** https://git-scm.com/doc
- **Report Issues:** Create issue in repository

---

**Ready to push?** Follow **Option A** (SSH) or **Option B** (HTTPS) above!
