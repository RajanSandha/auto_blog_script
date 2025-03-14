# Automated Blog Publishing System

A fully automated system for generating and publishing daily tech news blog posts using AI and RSS feeds. This system fetches the latest tech news, uses AI to generate blog content, and publishes to GitHub Pages with minimal human interaction using the Minimal Mistakes Jekyll theme.

## Features

- 🤖 Fully automated blog posting from RSS feeds
- 📱 Mobile-responsive design using Minimal Mistakes Jekyll theme
- 🔍 SEO optimization for better visibility
- 🔄 Daily updates via scheduled jobs
- 🌐 Multiple language support
- 📊 Analytics integration
- 💰 Ad monetization support (Google AdSense, Amazon Associates)
- 🐳 Docker support for easy deployment
- Fetches tech news from multiple RSS feeds
- Generates high-quality blog posts using AI (supports OpenAI and Google Gemini)
- Downloads and locally stores images from news articles
- Creates properly formatted Jekyll posts for Minimal Mistakes theme
- Publishes to GitHub repository automatically
- Flexible AI provider system - switch between different AI providers easily
- Modular design for easy maintenance and extension

## Requirements

- Python 3.8+ (standard method) OR Docker (containerized method)
- GitHub account
- API keys for AI providers (OpenAI and/or Google Gemini)
- GitHub Personal Access Token with repo scope

## Quick Start

### Standard Method (with Python)

1. **Clone this Repository**
```bash
git clone https://github.com/yourusername/auto_blog.git
cd auto_blog
```

2. **Configure Environment Variables**
Copy the example environment file and fill in your details:
```bash
cp auto_blog/.env.example .env
```

Edit the `.env` file with your API keys and GitHub credentials.

3. **Run the Setup Script**
This will create a virtual environment and set up the Minimal Mistakes blog repository:
```bash
# On Linux/Mac
./setup.py

# On Windows
python setup.py
```

4. **Run the System**
Generate and publish blog posts:
```bash
# On Linux/Mac
./run.py

# On Windows
python run.py
```

### Docker Method (cross-platform, including Android)

For the easiest experience, especially on Android or other platforms, use our Docker container:

1. **Get the Code and Configure**
```bash
git clone https://github.com/yourusername/auto_blog.git
cd auto_blog
cp .env.example .env
# Edit .env with your credentials
```

2. **Build and Run with Docker**
```bash
# Build the Docker image
./run-docker.sh build

# Run the system
./run-docker.sh run
```

That's it! The Docker container includes all dependencies and handles everything automatically.

3. **For Android Users**
```bash
# Install and setup Docker on Termux
./android-docker.sh setup

# Build and run
./android-docker.sh build
./android-docker.sh run
```

See [DOCKER_USAGE.md](DOCKER_USAGE.md) for detailed Docker instructions.

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

#### Docker Method (all platforms)
```bash
# Add to crontab
0 8 * * * cd /path/to/auto_blog && ./run-docker.sh run >> logs/cron.log 2>&1
```

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

## Monetization

Auto-Blog supports ad monetization through:

- **Google AdSense**: Integrate your AdSense publisher ID and ad slots
- **Amazon Associates**: Add your Amazon affiliate tracking ID
- **Custom Ad Code**: Insert your own custom HTML ad code

Configure ad settings in your `.env` file:

```
# Ad Configuration
ADS_ENABLED=true
ADS_GOOGLE_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX
ADS_GOOGLE_SIDEBAR_SLOT=XXXXXXXXXX
ADS_GOOGLE_CONTENT_SLOT=XXXXXXXXXX
ADS_AMAZON_TRACKING_ID=XXXX-XX
ADS_CUSTOM_AD_CODE=<div>Your custom ad HTML</div>
```

Ads are automatically placed in strategic locations on your site. For more details, see [Ad Configuration Guide](auto_blog/docs/AD_CONFIGURATION.md).

## Environment Variables

Auto-Blog uses environment variables for configuration. Create a `.env` file in the root directory with the following:

```
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username
GITHUB_REPO=your_repo_name
GITHUB_EMAIL=your_email@example.com
GITHUB_BRANCH=main

# RSS Configuration
RSS_FEEDS=https://example.com/feed1.xml,https://example2.com/feed2.xml
MAX_POSTS_PER_SOURCE=5
POSTS_PER_DAY=3

# Blog Configuration
BLOG_TITLE=My Automated Blog
BLOG_DESCRIPTION=Automatically generated blog posts from my favorite sources
AUTHOR_NAME=Your Name
SITE_URL=https://yourusername.github.io/your-repo-name

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# SEO Configuration
SEO_KEYWORDS=blog,automation,technology,news
SEO_DESCRIPTION=My automated blog featuring the latest tech news and insights

# Ad Configuration
ADS_ENABLED=false
ADS_GOOGLE_PUBLISHER_ID=
ADS_GOOGLE_SIDEBAR_SLOT=
ADS_GOOGLE_CONTENT_SLOT=
ADS_AMAZON_TRACKING_ID=
ADS_CUSTOM_AD_CODE=
```