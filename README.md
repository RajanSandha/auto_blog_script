# Automated Blog Publishing System

A fully automated system for generating and publishing daily tech news blog posts using AI and RSS feeds. This system fetches the latest tech news, uses AI to generate blog content, and publishes to GitHub Pages with minimal human interaction.

## Features

- Fetches tech news from multiple RSS feeds
- Generates high-quality blog posts using AI (supports OpenAI and Google Gemini)
- Downloads and locally stores images from news articles
- Creates properly formatted Jekyll posts
- Publishes to GitHub repository automatically
- Flexible AI provider system - switch between different AI providers easily
- Modular design for easy maintenance and extension

## Requirements

- Python 3.8+
- GitHub account
- API keys for AI providers (OpenAI and/or Google Gemini)
- Jekyll-based GitHub Pages blog setup

## Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/auto_blog.git
cd auto_blog
```

2. Set up the virtual environment and install dependencies using one of these methods:

### Standard Setup
```bash
# On Linux/Mac
./setup.py

# On Windows
python setup.py
```

### Alternative Setup (if you encounter errors with the standard setup)
If you have issues with the standard setup (like missing venv module), try the alternative setup:

```bash
# On Linux/Mac
./setup_alt.py

# On Windows
python setup_alt.py
```

The alternative setup uses `virtualenv` instead of the built-in `venv` module and may work better on some systems.

### Manual Setup
If both setup scripts fail, you can manually create a virtual environment:

```bash
# Install virtualenv if needed
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Copy the example environment file and fill in your details
```bash
cp auto_blog/.env.example .env
```

4. Edit the configuration in `.env` with your API keys and other settings

## Configuration

The `.env` file should include:

```
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_blog_repository_name
GITHUB_EMAIL=your_email@example.com

# AI Provider Settings
AI_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# RSS Feed Configuration
# Comma-separated list of RSS feed URLs
RSS_FEEDS=https://techcrunch.com/feed/,https://www.theverge.com/rss/index.xml
```

See the `.env.example` file for all available configuration options.

## Usage

You have several options to run the automated blog system:

### Option 1: Using the all-in-one run script

This automatically activates the virtual environment and runs the system:

```bash
# On Linux/Mac
./run.py

# On Windows
python run.py
```

### Option 2: Activating the virtual environment first

```bash
# On Linux/Mac
source ./run_blog.sh
python run_autoblog.py

# On Windows
run_blog.bat
python run_autoblog.py
```

### Scheduling

#### On Linux (using cron)

Add a cron job to run the script daily:

```bash
crontab -e
```

Add the following line to run the script at 8 AM every day:

```
0 8 * * * cd /path/to/auto_blog && ./run.py >> logs/cron.log 2>&1
```

#### On Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the Trigger to run daily
4. Set the Action to start a program
5. Enter the path to the `run.py` script or to the Python executable in the virtual environment

## Project Structure

```
auto_blog/
├── __init__.py
├── main.py                  # Main entry point
├── config.py                # Configuration handling
├── rss_fetcher/             # RSS feed handling
├── ai_content/              # AI integration for different providers
├── image_handler/           # Image downloading and processing
├── post_generator/          # Jekyll post generation
├── github_manager/          # GitHub repository management
└── utils/                   # Utility functions
```

## Troubleshooting

### Virtual Environment Issues

#### "externally-managed-environment" Error
If you see an error like:
```
error: externally-managed-environment
```

This happens on Debian/Ubuntu systems that protect the system Python. Use the provided setup scripts which create a virtual environment automatically.

#### Missing venv Module
If you see an error like:
```
The virtual environment was not created successfully because ensurepip is not available
```

Try one of these solutions:
1. Install the required package: `sudo apt install python3-venv` or `sudo apt install python3.X-venv` (replace X with your Python version)
2. Use the alternative setup script: `./setup_alt.py`
3. Follow the manual setup instructions

#### Other Environment Issues

1. Delete the `venv` directory and run `setup.py` or `setup_alt.py` again
2. Check the logs in the `logs/` directory for error messages
3. Ensure you have appropriate permissions to create directories and files

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.