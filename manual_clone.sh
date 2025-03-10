#!/bin/bash
# Manual script to clone minimal-mistakes repository and set it up for use with auto_blog

echo "======================================================="
echo "Manual minimal-mistakes clone script for auto_blog"
echo "======================================================="

# Create github_repo directory
if [ -d "github_repo" ]; then
  echo "github_repo directory already exists. Delete it? (y/n)"
  read -r response
  if [ "$response" = "y" ]; then
    rm -rf github_repo
    echo "Removed existing github_repo directory."
  else
    echo "Keeping existing github_repo directory."
    exit 0
  fi
fi

# Clone minimal-mistakes repository
echo "Cloning minimal-mistakes repository..."
git clone https://github.com/mmistakes/minimal-mistakes.git github_repo

# Check if clone was successful
if [ $? -ne 0 ]; then
  echo "Failed to clone repository. Please check your internet connection."
  exit 1
fi

# Remove .git directory to disconnect from original repository
echo "Removing .git directory to disconnect from original repository..."
rm -rf github_repo/.git

# Initialize new git repository
echo "Initializing new git repository..."
cd github_repo
git init

# Clean up unnecessary files as recommended in minimal-mistakes docs
echo "Cleaning up unnecessary files and directories..."
rm -rf .editorconfig .gitattributes .github/ docs/ test/ CHANGELOG.md 
rm -rf minimal-mistakes-jekyll.gemspec README.md screenshot.png screenshot-layouts.png .travis.yml

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p _posts assets/images

echo "======================================================="
echo "Setup complete!"
echo "======================================================="
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Add the remote origin:"
echo "   cd github_repo"
echo "   git remote add origin https://github.com/yourusername/your-repo.git"
echo ""
echo "3. Edit _config.yml to customize your site"
echo "4. Continue with auto_blog setup to generate posts." 