# Auto-Blog Docker Guide

This guide explains how to use the Docker container for the Auto-Blog system, making it easy to run on any platform with just a single command.

## Benefits of Docker Version

- **No Python or dependencies required** - everything is packaged in the container
- **Easy to run** - just a single command to generate blog posts
- **Cross-platform** - runs on Linux, macOS, Windows, and even Android
- **Consistent environment** - same behavior everywhere
- **Easy updates** - just pull the latest image
- **No virtual environment hassle** - everything is pre-configured

## Setup Instructions

### Prerequisites

- Docker installed on your system
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
  - Docker Engine (Linux)
  - Termux with Docker (Android - see Android section below)

### Quick Start for Desktop/Server

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/auto_blog.git
   cd auto_blog
   ```

2. **Create your .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and GitHub credentials
   ```

3. **Build the Docker image**
   ```bash
   ./run-docker.sh build
   ```

4. **Run Auto-Blog**
   ```bash
   ./run-docker.sh run
   ```
   
That's it! The system will generate blog posts and push them to your GitHub repository.

## Available Commands

The `run-docker.sh` script provides several commands:

- `./run-docker.sh build` - Build the Docker image
- `./run-docker.sh run` - Generate and publish blog posts
- `./run-docker.sh push` - Push all changes to GitHub
- `./run-docker.sh setup` - Only setup the repository
- `./run-docker.sh shell` - Get a shell inside the container
- `./run-docker.sh stop` - Stop any running containers
- `./run-docker.sh help` - Show help message

## Using Docker Compose

For advanced users, we also provide a `docker-compose.yml` file:

```bash
# Build and start the container
docker-compose up --build

# Run in the background
docker-compose up -d

# Stop the container
docker-compose down
```

## Running on Android

The Auto-Blog system can run on Android using Termux with Docker:

1. **Install Termux from F-Droid**
   - [F-Droid Termux Link](https://f-droid.org/en/packages/com.termux/)

2. **Run the Android Docker setup script**
   ```bash
   ./android-docker.sh setup
   ```

   This will:
   - Install necessary packages
   - Set up Docker in Termux
   - Prepare the environment

3. **Build the Docker image**
   ```bash
   ./android-docker.sh build
   ```

4. **Run Auto-Blog**
   ```bash
   ./android-docker.sh run
   ```

### Android Commands

The `android-docker.sh` script provides these commands:

- `./android-docker.sh setup` - Install Docker on Termux and set up environment
- `./android-docker.sh build` - Build the Docker image
- `./android-docker.sh run` - Generate and publish blog posts
- `./android-docker.sh push` - Push all changes to GitHub
- `./android-docker.sh shell` - Get a shell inside the container
- `./android-docker.sh help` - Show help message

## Advanced Topics

### Persistent Data

The Docker container uses volumes to store persistent data:

- `auto-blog-repo` - Stores the GitHub repository
- `auto-blog-logs` - Stores log files

This ensures your data persists between container runs.

### Customizing the Container

You can customize the container by:

1. **Modifying the Dockerfile** - If you need additional dependencies
2. **Changing the entrypoint script** - If you need custom logic
3. **Adding environment variables** in your .env file

### Automated Runs with Cron

You can schedule the Docker container to run automatically:

```bash
# Run the blog generator daily at 8 AM
0 8 * * * cd /path/to/auto_blog && ./run-docker.sh run >> /path/to/logfile.log 2>&1
```

On Android/Termux, you can use Termux's job scheduler:

```bash
# Install cronie
pkg install cronie

# Edit crontab
crontab -e

# Add this line to run daily at 8 AM
0 8 * * * cd ~/auto_blog && ./android-docker.sh run
```

## Troubleshooting

### GitHub Authentication Issues

When running in a Docker container, GitHub authentication can sometimes be challenging. The system handles this in several ways:

1. **Embedded Token Authentication**: The container automatically embeds your GitHub token in the repository URL to authenticate pushes.

2. **If you encounter authentication errors**, make sure:
   - Your GitHub token in the .env file has the correct permissions (repo scope)
   - The token is valid and not expired
   - The GITHUB_USERNAME and GITHUB_REPO values in .env match your actual GitHub username and repository name

3. **Manual Authentication Fix**: If pushes still fail, you can run a shell in the container and fix it:
   ```bash
   # Get a shell in the container
   ./run-docker.sh shell
   
   # Inside the container, set the remote URL with the token
   cd github_repo
   git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO.git
   ```

### Permission Issues

If you encounter permission issues with Docker volumes:

```bash
sudo chown -R $(id -u):$(id -g) ~/.docker/volumes/auto-blog-*
```

### Image Build Fails

If the image build fails, try:

```bash
docker system prune -a
./run-docker.sh build
```

### Container Crashes

Check logs with:

```bash
docker logs auto-blog
```

## Using Pre-built Image (coming soon)

We plan to provide a pre-built image on Docker Hub:

```bash
# Pull the image
docker pull yourusername/auto-blog:latest

# Run it
docker run --rm -v "$(pwd)/.env:/app/.env" \
  -v auto-blog-repo:/app/github_repo \
  -v auto-blog-logs:/app/logs \
  yourusername/auto-blog:latest run
``` 