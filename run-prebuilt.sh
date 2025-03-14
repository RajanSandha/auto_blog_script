#!/bin/bash
# Script to run a prebuilt auto-blog Docker image from Docker Hub

# Configuration
# Change this to the Docker Hub username where the image is hosted
DOCKER_HUB_USERNAME="rajansandha"
IMAGE_NAME="auto-blog"
IMAGE_TAG="latest"

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}======== Auto-Blog Prebuilt Docker Runner ========${NC}"
    echo ""
    echo "Usage: ./run-prebuilt.sh [command]"
    echo ""
    echo "Commands:"
    echo "  run     - Generate and publish blog posts (default)"
    echo "  push    - Push all files to GitHub"
    echo "  setup   - Only setup the repository"
    echo "  shell   - Get a shell inside the container"
    echo "  pull    - Pull/update the latest Docker image"
    echo "  help    - Show this help message"
    echo ""
    echo "Example: ./run-prebuilt.sh run"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Parse command
CMD=${1:-run}

# Full image name
FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

case "$CMD" in
    pull)
        echo -e "${YELLOW}📥 Pulling latest Docker image: ${FULL_IMAGE_NAME}...${NC}"
        docker pull "${FULL_IMAGE_NAME}"
        echo -e "${GREEN}✅ Image pulled successfully.${NC}"
        ;;
    run)
        echo -e "${YELLOW}🚀 Running auto-blog to generate and publish posts...${NC}"
        
        # Check if image exists and pull if not
        if ! docker image inspect "${FULL_IMAGE_NAME}" &> /dev/null; then
            echo -e "${YELLOW}📥 Image not found locally. Pulling from Docker Hub...${NC}"
            docker pull "${FULL_IMAGE_NAME}" || { 
                echo -e "${RED}❌ Failed to pull image. Please check your internet connection or run ./run-prebuilt.sh pull first.${NC}"; 
                exit 1; 
            }
        fi
        
        # Run the container
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            "${FULL_IMAGE_NAME}" run
        ;;
    push)
        echo -e "${YELLOW}📤 Pushing all changes to GitHub...${NC}"
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            "${FULL_IMAGE_NAME}" push
        ;;
    setup)
        echo -e "${YELLOW}🔧 Setting up GitHub repository...${NC}"
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            "${FULL_IMAGE_NAME}" setup
        ;;
    shell)
        echo -e "${YELLOW}🐚 Starting shell in container...${NC}"
        docker run -it --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            "${FULL_IMAGE_NAME}" shell
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