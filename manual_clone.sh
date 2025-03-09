#!/bin/bash
# Manual script to clone al-folio repository and set it up for use with auto_blog

echo "======================================================="
echo "Manual al-folio clone script for auto_blog"
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

# Clone al-folio repository
echo "Cloning al-folio repository..."
git clone https://github.com/alshedivat/al-folio.git github_repo

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
echo "3. Continue with auto_blog setup to generate posts." 