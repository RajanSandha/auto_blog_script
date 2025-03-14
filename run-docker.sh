#!/bin/bash
# Helper script to run the auto-blog Docker container

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Function to display usage
show_usage() {
    echo "Usage: ./run-docker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build   - Build the Docker image"
    echo "  run     - Generate and publish blog posts (default)"
    echo "  push    - Push all files to GitHub"
    echo "  setup   - Only setup the repository"
    echo "  shell   - Get a shell inside the container"
    echo "  stop    - Stop the running container"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-docker.sh build   # Build the Docker image"
    echo "  ./run-docker.sh run     # Run the blog generator"
    echo "  ./run-docker.sh push    # Push changes to GitHub"
}

# Parse command
CMD=${1:-run}

case "$CMD" in
    build)
        echo "🔨 Building Docker image..."
        docker build -t auto-blog .
        echo "✅ Docker image built successfully."
        ;;
    run)
        echo "🚀 Running auto-blog to generate and publish posts..."
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog run
        ;;
    push)
        echo "📤 Pushing all changes to GitHub..."
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog push
        ;;
    setup)
        echo "🔧 Setting up GitHub repository..."
        docker run --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog setup
        ;;
    shell)
        echo "🐚 Starting shell in container..."
        docker run -it --rm -v "$(pwd)/.env:/app/.env" \
            -v auto-blog-repo:/app/github_repo \
            -v auto-blog-logs:/app/logs \
            auto-blog shell
        ;;
    stop)
        echo "🛑 Stopping any running auto-blog containers..."
        docker stop $(docker ps -q --filter "ancestor=auto-blog") 2>/dev/null || echo "No containers running."
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $CMD"
        show_usage
        exit 1
        ;;
esac 