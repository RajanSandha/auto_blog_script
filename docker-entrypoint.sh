#!/bin/bash
set -e

# Function to check if .env file exists
check_env_file() {
  if [ ! -f .env ]; then
    if [ -f .env.example ]; then
      echo "⚠️ .env file not found. Creating from example..."
      cp .env.example .env
      echo "⚠️ Please update .env file with your API keys and GitHub credentials."
      echo "⚠️ You can do this by mounting a volume with the correct .env file."
    else
      echo "❌ No .env or .env.example file found."
      exit 1
    fi
  fi
}

# Function to setup GitHub repository
setup_github_repo() {
  if [ ! -d "github_repo/.git" ]; then
    echo "🔧 Setting up minimal-mistakes repository..."
    
    # Clone minimal-mistakes theme and setup
    if [ -d "github_repo" ] && [ "$(ls -A github_repo)" ]; then
      echo "📂 GitHub repo directory exists and is not empty. Skipping clone."
    else
      echo "📥 Cloning minimal-mistakes theme..."
      git clone https://github.com/mmistakes/minimal-mistakes.git github_repo
      
      # Clean up unnecessary files as recommended in minimal-mistakes docs
      rm -rf github_repo/.git github_repo/.editorconfig github_repo/.gitattributes \
             github_repo/.github/ github_repo/docs/ github_repo/test/ \
             github_repo/CHANGELOG.md github_repo/minimal-mistakes-jekyll.gemspec \
             github_repo/README.md github_repo/screenshot.png github_repo/screenshot-layouts.png \
             github_repo/.travis.yml
      
      # Create necessary directories
      mkdir -p github_repo/_posts github_repo/assets/images
    fi
    
    # Initialize new git repo
    cd github_repo
    git init
    
    # Configure git with environment variables
    source ../.env
    git config user.name "${GITHUB_USERNAME:-auto-blog-user}"
    git config user.email "${GITHUB_EMAIL:-auto-blog@example.com}"
    
    # Configure Git to store credentials for HTTPS
    git config credential.helper 'store --file=/tmp/git-credentials'
    
    # Add remote if specified in .env
    if [ -n "$GITHUB_USERNAME" ] && [ -n "$GITHUB_REPO" ] && [ -n "$GITHUB_TOKEN" ]; then
      # Use token in the URL for authentication
      echo "🔑 Setting up GitHub remote with authentication..."
      git remote add origin "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
      echo "✅ Added git remote with authentication"
      
      # Save credentials to the credential store
      echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > /tmp/git-credentials
      chmod 600 /tmp/git-credentials
    else
      echo "⚠️ Missing GitHub credentials in .env file. Push operations may fail."
      if [ -n "$GITHUB_USERNAME" ] && [ -n "$GITHUB_REPO" ]; then
        git remote add origin "https://github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
        echo "✅ Added git remote: https://github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
      fi
    fi
    
    # Create and switch to main branch
    git checkout -b main
    
    cd ..
    echo "✅ GitHub repository setup completed."
  else
    echo "✅ GitHub repository already setup."
    
    # Re-configure authentication in case .env has changed
    cd github_repo
    source ../.env
    
    # Update remote URL with token
    if [ -n "$GITHUB_USERNAME" ] && [ -n "$GITHUB_REPO" ] && [ -n "$GITHUB_TOKEN" ]; then
      git remote set-url origin "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
      echo "🔑 Updated GitHub remote with authentication token"
      
      # Save credentials to the credential store
      git config credential.helper 'store --file=/tmp/git-credentials'
      echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > /tmp/git-credentials
      chmod 600 /tmp/git-credentials
    fi
    
    cd ..
  fi
}

# Main execution
echo "============================================="
echo "🤖 Auto-Blog Docker Container"
echo "============================================="

# Check for .env file
check_env_file

# Handle different commands
case "$1" in
  run)
    setup_github_repo
    echo "🚀 Running auto-blog to generate and publish posts..."
    python run_autoblog.py
    ;;
    
  push)
    setup_github_repo
    echo "📤 Pushing all changes to GitHub..."
    ./push_all.py
    ;;
    
  setup)
    setup_github_repo
    echo "✅ Setup completed."
    ;;
    
  shell)
    echo "🐚 Starting shell session..."
    exec /bin/bash
    ;;
    
  *)
    echo "🔧 Available commands:"
    echo "   run   - Generate and publish blog posts"
    echo "   push  - Push all files to GitHub"
    echo "   setup - Only setup the repository"
    echo "   shell - Start a shell session"
    echo ""
    echo "🚀 Running $1 command..."
    exec "$@"
    ;;
esac 