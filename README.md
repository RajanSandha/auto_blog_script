# Automated Blog Publishing System

A fully automated system for generating and publishing daily tech news blog posts using AI and RSS feeds. This system fetches the latest tech news, uses AI to generate blog content, and publishes to GitHub Pages with minimal human interaction using the Minimal Mistakes Jekyll theme.

## Features

- Fetches tech news from multiple RSS feeds
- Generates high-quality blog posts using AI (supports OpenAI and Google Gemini)
- Downloads and locally stores images from news articles
- Creates properly formatted Jekyll posts for Minimal Mistakes theme
- Publishes to GitHub repository automatically
- Flexible AI provider system - switch between different AI providers easily
- Modular design for easy maintenance and extension

## Requirements

- Python 3.8+
- GitHub account
- API keys for AI providers (OpenAI and/or Google Gemini)
- GitHub Personal Access Token with repo scope

## Quick Start

### 1. Clone this Repository
```bash
git clone https://github.com/yourusername/auto_blog.git
cd auto_blog
```

### 2. Configure Environment Variables
Copy the example environment file and fill in your details:
```bash
cp auto_blog/.env.example .env
```

Edit the `.env` file with your API keys and GitHub credentials:
```
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_blog_repository_name
GITHUB_EMAIL=your_email@example.com
GITHUB_BRANCH=main

# AI Provider Settings
AI_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# RSS Feed Configuration
# Comma-separated list of RSS feed URLs
RSS_FEEDS=https://techcrunch.com/feed/,https://www.theverge.com/rss/index.xml,https://arstechnica.com/feed/
```

### 3. Run the Setup Script
This will create a virtual environment and set up the Minimal Mistakes blog repository:
```bash
# On Linux/Mac
./setup.py

# On Windows
python setup.py
```

### 4. Run the System
Generate and publish blog posts:
```bash
# On Linux/Mac
./run.py

# On Windows
python run.py
```

### 5. Enable GitHub Pages
1. Go to your GitHub repository
2. Navigate to Settings → Pages
3. Under "Source", select "Deploy from a branch"
4. Select your branch (main) and the root folder (/)
5. Click Save

Your blog will be available at: `https://yourusername.github.io/yourrepository/`

## Detailed Setup

### Setting Up GitHub

1. **Create a GitHub Repository**
   - Go to GitHub and create a new repository with the name you specified in `.env`
   - You don't need to initialize it with any files

2. **Create a Personal Access Token**
   - Go to GitHub Settings → Developer Settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token", give it a descriptive name
   - Select the "repo" scope (gives full control of private repositories)
   - Copy the token and add it to your `.env` file as `GITHUB_TOKEN`

### AI Providers

You can choose between OpenAI (GPT models) and Google Gemini for content generation:

1. **Using OpenAI**
   - Sign up for an API key at [OpenAI](https://platform.openai.com/)
   - Set `AI_PROVIDER=openai` in your `.env` file
   - Add your API key as `OPENAI_API_KEY` in the `.env` file

2. **Using Google Gemini**
   - Sign up for an API key at [Google AI Studio](https://makersuite.google.com/)
   - Set `AI_PROVIDER=gemini` in your `.env` file
   - Add your API key as `GEMINI_API_KEY` in the `.env` file

### RSS Feeds

The system comes with default tech news feeds, but you can customize them:

```
RSS_FEEDS=https://techcrunch.com/feed/,https://www.theverge.com/rss/index.xml,https://www.wired.com/feed,https://arstechnica.com/feed/
```

Add or remove feeds as needed, separating them with commas.

## Customizing Your Blog

### Theme Customization

You can customize the Minimal Mistakes theme by editing these files:

1. **_config.yml**: Main configuration file in the `github_repo` directory
   - Set site name, description, author information
   - Change color scheme with `minimal_mistakes_skin`
   - Configure navigation, analytics, comments

2. **Navigation**: Create or edit `github_repo/_data/navigation.yml`
   ```yaml
   main:
     - title: "Posts"
       url: /posts/
     - title: "Categories"
       url: /categories/
     - title: "Tags"
       url: /tags/
     - title: "About"
       url: /about/
   ```

3. **Profile Picture**: Add your photo to `github_repo/assets/images/` and update `_config.yml`

For more detailed customization, refer to the [Minimal Mistakes documentation](https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/).

## Automatic Deployment

### Running Daily Updates

To automatically generate posts daily, you can set up a cron job (Linux/Mac) or Task Scheduler (Windows).

#### Linux/Mac (cron)
```bash
# Open crontab
crontab -e

# Add this line to run daily at 8 AM
0 8 * * * cd /path/to/auto_blog && ./run.py >> logs/cron.log 2>&1
```

#### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create a new Basic Task
3. Set trigger to Daily
4. Action: Start a Program
5. Program/script: `C:\path\to\python.exe`
6. Arguments: `C:\path\to\auto_blog\run.py`

## Troubleshooting

### Common Issues

- **Authentication Errors**: Ensure your GitHub token has the correct permissions and is correctly set in the `.env` file

- **Dependency Issues**: If you encounter errors with dependencies, try running:
  ```bash
  pip install -r requirements.txt
  ```

- **GitHub Pages Not Building**: Check if your repository has GitHub Pages enabled in Settings → Pages

- **Missing Images**: If images aren't displaying, check that they're being correctly saved to `github_repo/assets/images/`

- **RSS Feed Issues**: If specific feeds like Wired.com are causing problems, they will be automatically skipped after multiple timeout attempts

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

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.