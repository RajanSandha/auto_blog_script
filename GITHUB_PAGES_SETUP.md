# Setting Up GitHub Pages With Auto Blog

This guide will help you set up GitHub Pages to work with the automated blog system.

## 1. Create the GitHub Repository

For GitHub Pages, you have two options:

### Option A: Using a User/Organization Site

For a site at `username.github.io`:

1. Create a new repository named exactly `username.github.io` (where `username` is your GitHub username)
2. This will be accessible at `https://username.github.io`

### Option B: Using a Project Site

For a site at `username.github.io/repository-name`:

1. Create any repository with any name (e.g., `myblog`)
2. This will be accessible at `https://username.github.io/myblog`

## 2. Update Your .env File

Set up your `.env` file with the following GitHub configuration:

```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_repository_name
GITHUB_EMAIL=your_email@example.com
GITHUB_BRANCH=main  # or gh-pages depending on your setup
```

### Generating a GitHub Token

1. Go to GitHub Settings → Developer Settings → Personal access tokens → Tokens (classic)
2. Generate a new token with the `repo` scope
3. Copy the token and add it to your `.env` file

## 3. Run the Auto Blog System

```bash
./run.py
```

The system will:
1. Clone the repository if it doesn't exist locally
2. Set up the proper Jekyll structure for GitHub Pages
3. Generate posts from RSS feeds using AI
4. Commit and push the changes to GitHub

## 4. Enable GitHub Pages in Repository Settings

1. Go to your repository on GitHub
2. Click on "Settings"
3. Scroll down to "GitHub Pages" section
4. Select the branch (main or gh-pages) as the source
5. Choose "/" (root) as the directory
6. Click "Save"

GitHub will build your site and provide you with the URL.

## 5. Customizing Your Jekyll Theme

Our system sets up your blog with the default "minima" theme. You can customize this in several ways:

### Changing the Theme

To use a different built-in GitHub Pages theme:

1. Edit the `_config.yml` file in your repository
2. Change the `theme:` line to use one of these supported themes:
   ```yaml
   theme: jekyll-theme-cayman   # Clean, responsive theme
   ```
   Other options include: `jekyll-theme-minimal`, `jekyll-theme-hacker`, `jekyll-theme-slate`, etc.

### Using a Remote Theme

To use themes from outside the GitHub Pages supported themes:

1. Edit the `_config.yml` file
2. Comment out the `theme:` line and uncomment the `remote_theme:` line:
   ```yaml
   # theme: minima
   remote_theme: owner/name   # e.g., "mmistakes/minimal-mistakes"
   ```

### Customizing CSS

To customize the existing theme's CSS:

1. Edit the `assets/css/style.scss` file
2. Add your custom CSS after the `@import` line

### Customizing Layouts

To customize layouts:

1. Create or edit files in the `_layouts` directory
2. Create or edit files in the `_includes` directory

The system already sets up basic layouts for you.

## 6. Using a Custom Domain (Optional)

If you want to use a custom domain like `myblog.com`:

1. Add `CUSTOM_DOMAIN=myblog.com` to your `.env` file
2. Run the auto blog system again
3. In your domain registrar's DNS settings:
   - Add an A record pointing to `185.199.108.153`
   - Add an A record pointing to `185.199.109.153`
   - Add an A record pointing to `185.199.110.153`
   - Add an A record pointing to `185.199.111.153`
   - Or, add a CNAME record pointing to `username.github.io`
4. In the repository settings, under GitHub Pages, add your custom domain
5. Check "Enforce HTTPS" (optional but recommended)

## 7. Wait for Propagation

DNS changes and GitHub Pages setup can take up to 24 hours to fully propagate.

## Troubleshooting

- If your site isn't building, check the "Actions" tab in your GitHub repository for build errors
- Make sure your repository has the correct Jekyll structure (the auto blog system should set this up for you)
- Ensure the Jekyll build is completing successfully by checking the GitHub Pages section in repository settings 