#!/bin/bash
# Script to build and publish the auto-blog Docker image to Docker Hub

# Configuration - CHANGE THESE VALUES
DOCKER_HUB_USERNAME="yourusername"  # Replace with your Docker Hub username
IMAGE_NAME="auto-blog"
IMAGE_VERSION="latest"
# Optional additional tags (e.g., version numbers)
ADDITIONAL_TAGS=("1.0.0" "stable")

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if jq is installed (used for getting version information)
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️ jq is not installed. Version tagging may not work correctly.${NC}"
fi

# Check if logged in to Docker Hub
echo -e "${BLUE}==== Checking Docker Hub login ====${NC}"
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}🔑 Not logged in to Docker Hub. Please login:${NC}"
    docker login
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to login to Docker Hub. Aborting.${NC}"
        exit 1
    fi
fi

# Build the Docker image
echo -e "${BLUE}==== Building Docker image ====${NC}"
FULL_IMAGE_NAME="${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_VERSION}"
echo -e "${YELLOW}🔨 Building image: ${FULL_IMAGE_NAME}${NC}"

docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build Docker image. Aborting.${NC}"
    exit 1
fi

# Tag with additional tags if specified
if [ ${#ADDITIONAL_TAGS[@]} -gt 0 ]; then
    echo -e "${BLUE}==== Adding additional tags ====${NC}"
    
    for tag in "${ADDITIONAL_TAGS[@]}"; do
        echo -e "${YELLOW}🏷️ Tagging as: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${tag}${NC}"
        docker tag "${FULL_IMAGE_NAME}" "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${tag}"
    done
fi

# Push to Docker Hub
echo -e "${BLUE}==== Pushing to Docker Hub ====${NC}"
echo -e "${YELLOW}📤 Pushing ${FULL_IMAGE_NAME}${NC}"
docker push "${FULL_IMAGE_NAME}"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to push Docker image. Aborting.${NC}"
    exit 1
fi

# Push additional tags if specified
if [ ${#ADDITIONAL_TAGS[@]} -gt 0 ]; then
    for tag in "${ADDITIONAL_TAGS[@]}"; do
        echo -e "${YELLOW}📤 Pushing ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${tag}${NC}"
        docker push "${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${tag}"
    done
fi

echo -e "${GREEN}✅ Successfully built and pushed Docker image to Docker Hub.${NC}"
echo -e "${GREEN}✅ Image: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}${NC}"
echo -e "${GREEN}✅ Tags: ${IMAGE_VERSION} ${ADDITIONAL_TAGS[*]}${NC}"
echo ""
echo -e "${BLUE}==== Usage Instructions ====${NC}"
echo -e "To use this image, run:"
echo -e "${YELLOW}docker run --rm -v \"\$(pwd)/.env:/app/.env\" \\
  -v auto-blog-repo:/app/github_repo \\
  -v auto-blog-logs:/app/logs \\
  ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${IMAGE_VERSION} run${NC}" 