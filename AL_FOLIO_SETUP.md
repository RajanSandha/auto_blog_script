# Setting Up Auto Blog with al-folio Jekyll Theme

This guide will help you set up your automated blog system with the [al-folio](https://github.com/alshedivat/al-folio) Jekyll theme.

## 1. Run the Setup Script

The setup script will install dependencies and clone the al-folio repository:

```bash
# On Linux/Mac
./setup.py

# On Windows
python setup.py
```

If you encounter any issues with the above script, try the alternative setup:

```bash
# On Linux/Mac
./setup_alt.py

# On Windows
python setup_alt.py
```

Both scripts will attempt multiple methods to create a virtual environment.

### Manual Setup Option

If you continue to have issues with the setup scripts, you can use the manual clone script to at least get the al-folio repository:

```bash
# On Linux/Mac/Git Bash
./manual_clone.sh
```

After using the manual clone script, you'll need to set up a virtual environment and install dependencies manually:

```bash
# Create virtual environment
python -m venv venv   # or: virtualenv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

These scripts will:
1. Create a virtual environment
2. Install all required dependencies
3. Clone the al-folio repository to `github_repo` directory
4. Set up activation scripts

## 2. Configure Your Environment

Create your `.env` file based on the example:

```bash
cp auto_blog/.env.example .env
```

Edit the `.env` file with your GitHub details:

```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_blog_repository_name
GITHUB_EMAIL=your_email@example.com
GITHUB_BRANCH=main
```

## 3. Customize al-folio

Before running the system, you may want to customize the al-folio theme. Here are some key files to consider:

- `github_repo/_config.yml`: Main configuration file (will be partially updated automatically)
- `github_repo/_data/`: Data files for various parts of the site
- `github_repo/_pages/`: Content pages (about, cv, projects, etc.)
- `github_repo/_sass/`: SCSS files for styling

For more detailed customization, refer to the [al-folio documentation](https://github.com/alshedivat/al-folio#customization).

## 4. Run the Auto Blog System

```bash
./run.py
```

This will:
1. Initialize a Git repository in the al-folio directory (if not already done)
2. Configure it to push to your GitHub repository
3. Generate blog posts from RSS feeds using AI
4. Add the posts to the `_posts` directory
5. Commit and push changes to GitHub

## 5. Set Up GitHub Pages

1. Go to your GitHub repository
2. Navigate to Settings > Pages
3. Under "Source", select "Deploy from a branch"
4. Select the branch (main) and save

If you're using al-folio's default settings, you'll need to enable GitHub Actions:

1. Go to Settings > Actions > General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Save

## 6. Wait for GitHub Actions to Build Your Site

The al-folio theme uses GitHub Actions to build and deploy your site. This may take a few minutes.

You can check the progress in the Actions tab of your repository.

## 7. Troubleshooting

### Common Issues

- **Building Locally**: al-folio can be tested locally using:
  ```bash
  cd github_repo
  bundle install
  bundle exec jekyll serve
  ```

- **GitHub Actions Failing**: Check the Actions tab for detailed error messages

- **Posts Not Showing**: Check that your posts:
  - Are in the `_posts` directory
  - Have the correct front matter (layout: post)
  - Have filenames in the format `YYYY-MM-DD-title.md`

For more complex issues, refer to the [al-folio issues](https://github.com/alshedivat/al-folio/issues) page. 