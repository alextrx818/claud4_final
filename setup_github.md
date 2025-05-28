# 🚀 GitHub Setup Instructions for Football Bot

## Option 1: Using GitHub Web Interface (Recommended)

### Step 1: Create Repository on GitHub
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `football-bot-pipeline`
   - **Description**: `⚽ Real-time football match data pipeline with 4-stage processing, live odds, and comprehensive analytics`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### Step 2: Connect Local Repository to GitHub
After creating the repository, GitHub will show you commands. Use these:

```bash
cd /root/Football_bot

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/football-bot-pipeline.git

# Push the code to GitHub
git branch -M main
git push -u origin main
```

## Option 2: Using GitHub CLI (if available)

If you have GitHub CLI installed and authenticated:

```bash
cd /root/Football_bot

# Create repository and push in one command
gh repo create football-bot-pipeline --public --description "⚽ Real-time football match data pipeline with 4-stage processing, live odds, and comprehensive analytics" --push
```

## Option 3: Manual Git Commands

If you already have a GitHub repository URL:

```bash
cd /root/Football_bot

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔧 Post-Setup Configuration

### Repository Settings
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Features" section
4. Enable:
   - ✅ Issues
   - ✅ Projects
   - ✅ Wiki
   - ✅ Discussions (optional)

### Branch Protection (Optional)
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

### Topics and Description
1. Go to repository main page
2. Click the gear icon next to "About"
3. Add topics: `football`, `soccer`, `api`, `pipeline`, `real-time`, `data-processing`, `python`, `asyncio`
4. Add website URL if you have one

## 📋 Verification Steps

After pushing, verify everything is working:

1. **Check Files**: Ensure all files are visible on GitHub
2. **README Display**: Verify README.md displays correctly
3. **License**: Check that LICENSE file is recognized
4. **Releases**: Consider creating a v1.0.0 release

## 🔐 Security Considerations

### API Credentials
⚠️ **IMPORTANT**: The current code has API credentials hardcoded in `step1.py`. Before making the repository public:

1. **Remove credentials** from the code:
```python
# In Step1_json_fetch_logger/step1.py
USER = os.getenv("THESPORTS_USER", "your_username")
SECRET = os.getenv("THESPORTS_SECRET", "your_secret")
```

2. **Add to .env file** (already in .gitignore):
```bash
echo "THESPORTS_USER=your_username" > .env
echo "THESPORTS_SECRET=your_secret" >> .env
```

3. **Update documentation** to mention environment variables

### GitHub Secrets (for CI/CD)
If you plan to use GitHub Actions:
1. Go to Settings → Secrets and variables → Actions
2. Add repository secrets:
   - `THESPORTS_USER`
   - `THESPORTS_SECRET`

## 🎯 Next Steps

1. **Create Issues**: Document known issues or feature requests
2. **Add CI/CD**: Set up GitHub Actions for testing
3. **Documentation**: Add more detailed API documentation
4. **Examples**: Add example output files
5. **Contributing**: Create CONTRIBUTING.md file

## 📞 Troubleshooting

### Common Issues

**Authentication Error**:
```bash
# If you get authentication errors, use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/football-bot-pipeline.git
```

**Large Files**:
```bash
# If you have large files, use Git LFS
git lfs track "*.json"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

**Permission Denied**:
```bash
# Make sure you have write access to the repository
# Check your GitHub permissions or create the repo under your account
```

---

**Repository URL**: `https://github.com/YOUR_USERNAME/football-bot-pipeline`  
**Clone Command**: `git clone https://github.com/YOUR_USERNAME/football-bot-pipeline.git` 