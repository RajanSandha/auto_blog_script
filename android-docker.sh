#!/bin/bash
# Helper script to run the auto-blog Docker container on Android via Termux

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a package is installed in Termux
check_package() {
    if ! pkg list-installed | grep -q "^$1"; then
        echo -e "${YELLOW}⚠️ $1 is not installed. Installing...${NC}"
        pkg install -y $1
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install $1. Please install it manually: pkg install $1${NC}"
            exit 1
        fi
        echo -e "${GREEN}✅ $1 installed successfully.${NC}"
    else
        echo -e "${GREEN}✅ $1 is already installed.${NC}"
    fi
}

# Function to display usage
show_usage() {
    echo -e "${BLUE}=== Auto-Blog Docker for Android ====${NC}"
    echo ""
    echo "Usage: ./android-docker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup   - Install Docker on Termux and setup environment"
    echo "  build   - Build the Docker image"
    echo "  run     - Generate and publish blog posts (default)"
    echo "  push    - Push all files to GitHub"
    echo "  shell   - Get a shell inside the container"
    echo "  help    - Show this help message"
    echo ""
}

# Setup function to install Docker on Termux
setup_docker() {
    echo -e "${BLUE}===== Setting up Docker on Termux =====${NC}"
    
    # Check if running in Termux
    if [ ! -d "/data/data/com.termux" ]; then
        echo -e "${RED}❌ This script is designed to run in Termux on Android.${NC}"
        exit 1
    fi
    
    # Install required packages
    echo -e "${YELLOW}📦 Installing required packages...${NC}"
    pkg update -y
    
    check_package "proot"
    check_package "git"
    check_package "python"
    check_package "wget"
    
    # Install Docker using termux-docker script if not already installed
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Docker...${NC}"
        
        # Download and install termux-docker
        cd ~
        if [ ! -d "termux-docker" ]; then
            git clone https://github.com/termux/termux-docker.git
            cd termux-docker
            pip install -e .
        else
            cd termux-docker
            git pull
        fi
        
        echo -e "${GREEN}✅ termux-docker installed.${NC}"
        echo -e "${YELLOW}📦 Running initial docker setup...${NC}"
        termux-docker setup
        
        # Create symlink for docker
        if [ ! -f "$PREFIX/bin/docker" ]; then
            ln -s $PREFIX/bin/termux-docker $PREFIX/bin/docker
        fi
        
        echo -e "${GREEN}✅ Docker installed successfully.${NC}"
    else
        echo -e "${GREEN}✅ Docker is already installed.${NC}"
    fi
    
    echo -e "${GREEN}✅ Docker setup complete.${NC}"
    echo -e "${YELLOW}ℹ️ You can now build and run the auto-blog container.${NC}"
}

# Parse command
CMD=${1:-help}

case "$CMD" in
    setup)
        setup_docker
        ;;
    build)
        echo -e "${YELLOW}🔨 Building Docker image for Android...${NC}"
        if [ -f "Dockerfile.android" ]; then
            echo -e "${YELLOW}ℹ️ Using Android-optimized Dockerfile${NC}"
            docker build -t auto-blog -f Dockerfile.android .
        else
            echo -e "${YELLOW}ℹ️ Using standard Dockerfile${NC}"
            docker build -t auto-blog .
        fi
        echo -e "${GREEN}✅ Docker image built successfully.${NC}"
        ;;
    run)
        echo -e "${YELLOW}🚀 Running auto-blog to generate and publish posts...${NC}"
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog run
        ;;
    push)
        echo -e "${YELLOW}📤 Pushing all changes to GitHub...${NC}"
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog push
        ;;
    shell)
        echo -e "${YELLOW}🐚 Starting shell in container...${NC}"
        docker run -it --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog shell
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $CMD${NC}"
        show_usage
        exit 1
        ;;
esac 