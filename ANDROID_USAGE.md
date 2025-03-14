# Running Auto-Blog System on Android

This guide will help you run the Auto-Blog system on your Android device.

## Prerequisites

1. Install [Termux](https://f-droid.org/en/packages/com.termux/) from F-Droid
   - Note: The Google Play version is no longer updated regularly
   - F-Droid link: https://f-droid.org/en/packages/com.termux/

2. Install required packages in Termux:
   ```bash
   pkg update
   pkg upgrade
   pkg install python git openssl
   ```

## Setup Instructions

1. **Extract the zip file**
   - Use any file manager to extract the `auto_blog_android.zip` file to a directory on your device

2. **Open Termux and navigate to the extracted directory**
   ```bash
   cd /storage/emulated/0/path/to/extracted/folder
   ```
   - Note: You may need to grant Termux storage permissions first:
     ```bash
     termux-setup-storage
     ```

3. **Run the Android setup script**
   ```bash
   bash android_run.sh
   ```

4. **Configure your .env file**
   - After first run, edit the `.env` file with a text editor to add your:
     - GitHub credentials
     - API keys (OpenAI or Google Gemini)
     - RSS feed URLs

## Troubleshooting

### Storage Access Issues
If Termux cannot access your storage:
```bash
termux-setup-storage
```
Then restart Termux.

### Python Installation Issues
If you have issues with Python:
```bash
pkg reinstall python
```

### GitHub Authentication Issues
If you have issues with GitHub authentication, make sure:
- Your GitHub token is valid
- The token has the correct permissions (repo scope)
- Your GitHub username and email are correctly set in the .env file

### Environment Setup Issues
If you have issues with the virtual environment:
```bash
rm -rf venv
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Regular Usage

After initial setup, you can simply run:
```bash
bash android_run.sh
```

This will:
1. Activate the virtual environment
2. Run the auto-blog system
3. Generate new posts and push them to GitHub

## Limitations on Android

- Some packages might be slower to install on Android
- Battery optimization might interrupt long-running processes
- Make sure to disable battery optimization for Termux if running for extended periods

## Getting Help

If you encounter issues, check the logs in the `logs/` directory for detailed error messages. 