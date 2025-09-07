# Google Calendar OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select an existing project
3. Name your project (e.g., "claude-pa-calendar")

## Step 2: Enable Google Calendar API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External (or Internal if using G Suite)
   - Fill in required fields
   - Add your email to test users
4. Application type: Select "Desktop app"
5. Name: "Claude PA Desktop"
6. Click "Create"

## Step 4: Download Credentials

1. After creation, click the download button (⬇️) for your OAuth client
2. Save the file somewhere secure on your system (e.g., `~/Documents/google-credentials.json`)
3. Note the full path to this file - you'll need it for the environment variable

## Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set the path to your credentials file:
```bash
GOOGLE_OAUTH_CREDENTIALS=/full/path/to/your/credentials.json
```

For example:
- macOS/Linux: `GOOGLE_OAUTH_CREDENTIALS=/Users/username/Documents/google-credentials.json`
- Windows: `GOOGLE_OAUTH_CREDENTIALS=C:\Users\username\Documents\google-credentials.json`

3. Export the environment variable in your shell:
```bash
export GOOGLE_OAUTH_CREDENTIALS=/full/path/to/your/credentials.json
```

Or add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence.

## Step 5: Configure MCP Server

The Google Calendar MCP server is already configured in `.mcp.json`. The server will automatically use the `GOOGLE_OAUTH_CREDENTIALS` environment variable.

## Step 6: First-Time Authentication

On first use, you'll be prompted to authenticate:
1. A browser window will open
2. Sign in with your Google account
3. Grant calendar permissions
4. Token will be saved automatically

## Troubleshooting

- If token expires (after 7 days in test mode), you'll be re-prompted to authenticate
- For production use, consider publishing your OAuth app to avoid token expiration
- Check `.claude/settings.local.json` for MCP configuration details

## Security Notes

- Never commit `credentials.json`, `.env`, or `token.json` to version control
- Keep OAuth credentials file in a secure location outside the project directory
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Consider using a password manager to store the credentials file path