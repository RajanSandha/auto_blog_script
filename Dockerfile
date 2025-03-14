FROM python:3.12-slim

# Set up working directory
WORKDIR /app

# Install git and other dependencies
RUN apt-get update && \
    apt-get install -y git git-lfs wget curl gnupg2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure Git globally to not require interaction
RUN git config --system credential.helper store && \
    git config --system pull.rebase false && \
    git config --system advice.detachedHead false && \
    git config --system core.askPass ""

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make scripts executable
RUN chmod +x run_autoblog.py push_all.py

# Create necessary directories
RUN mkdir -p github_repo logs data

# Create a volume for persistent data (GitHub repo, logs, config)
VOLUME ["/app/github_repo", "/app/logs", "/app/.env"]

# Environment variable for non-interactive mode
ENV PYTHONUNBUFFERED=1
ENV GIT_TERMINAL_PROMPT=0
ENV GIT_ASKPASS=/bin/echo

# Set the entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set the entry point
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["run"] 