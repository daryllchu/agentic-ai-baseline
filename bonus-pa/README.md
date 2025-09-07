# Personal Assistant with Claude Code

A personal assistant implementation using Claude Code with Google Calendar MCP integration. This project demonstrates how Claude Code can be used beyond software development as an intelligent personal assistant.

## Features

### 🌅 Morning Briefing (`/morning`)
- Fetches and displays all calendar events for the day
- Calculates estimated travel times between locations
- Highlights high-priority meetings
- Provides a daily summary with meeting counts
- Offers time-based productivity recommendations
- Distinguishes between virtual and in-person meetings

### 📅 Smart Scheduling Assistant (`/book`)
- Analyzes calendar to find optimal meeting times
- Suggests appropriate time slots based on event type:
  - Dinner meetings → Evening slots (6:30-8 PM)
  - Business lunch → Noon slots (12-1 PM)
  - Coffee meetings → Morning or afternoon slots
- Checks calendar availability to avoid conflicts
- Creates calendar events with smart defaults
- Provides contextual tips for different event types

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Claude Code CLI** installed and configured
3. **Google Cloud Project** with Calendar API enabled
4. **OAuth 2.0 credentials** for Google Calendar

## Installation

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd bonus-pa

# Install dependencies
npm install
```

### Step 2: Google Calendar OAuth Setup

Follow the instructions in [`SETUP_GOOGLE_OAUTH.md`](./SETUP_GOOGLE_OAUTH.md) to:
1. Create a Google Cloud Project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download credentials JSON file

### Step 3: Configure Environment

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and set your credentials path:
```bash
GOOGLE_OAUTH_CREDENTIALS=/path/to/your/credentials.json
```

3. Export the environment variable:
```bash
export GOOGLE_OAUTH_CREDENTIALS=/path/to/your/credentials.json
```

### Step 4: Load MCP Server

The Google Calendar MCP server is already configured in `.mcp.json`.
Restart Claude Code to load the MCP configuration with your environment variables.

### Step 5: Verify MCP Connection

```bash
# Check if MCP server is configured
claude mcp list

# You should see:
# google-calendar (stdio)
```

## Usage

### Morning Briefing

Get your daily schedule with travel time estimates:

```bash
npm run morning
# or
node commands/morning.js
```

This will:
- Display all events for today in chronological order
- Show event details (time, location, attendees)
- Calculate travel times between different locations
- Highlight important meetings
- Provide a summary with total events and travel time

### Smart Scheduling Assistant

Find the perfect time for your meetings and events:

```bash
npm run book
# or
node commands/book.js
```

This will:
1. Scan your calendar for available time slots
2. Suggest optimal times based on event type (dinner, lunch, coffee, etc.)
3. Check for conflicts with existing events
4. Create calendar events with appropriate durations
5. Provide helpful tips for different meeting types

## Project Structure

```
bonus-pa/
├── .claude/
│   └── settings.local.json # Local MCP settings
├── commands/
│   ├── morning.js          # Morning briefing command
│   └── book.js             # Restaurant booking command
├── .env.example            # Environment variable template
├── .mcp.json               # MCP server configuration
├── package.json            # Node.js dependencies
├── SETUP_GOOGLE_OAUTH.md   # OAuth setup guide
└── README.md               # This file
```

## Security Notes

- Never commit `credentials.json`, `.env`, or `token.json`
- Store OAuth credentials file in a secure location outside the project
- Environment variables are used to keep paths flexible and secure
- The `.gitignore` file excludes all sensitive files
- Tokens expire after 7 days in test mode

## Troubleshooting

### MCP Server Not Working
1. Ensure Claude Code is running: `claude --version`
2. Check MCP configuration: `claude mcp list`
3. Verify environment variable is set: `echo $GOOGLE_OAUTH_CREDENTIALS`
4. Ensure credentials file exists at the specified path
5. Restart Claude Code after configuration changes

### Calendar Events Not Loading
1. Ensure OAuth is properly configured
2. Check if token has expired (re-authenticate if needed)
3. Verify Google Calendar API is enabled in your project
4. Check console for specific error messages

### Scheduling Assistant Not Working
1. Ensure calendar has proper read/write permissions
2. Check that event creation is enabled in your Google Calendar API
3. Verify time zone settings are correct

## Future Enhancements

- [ ] Integration with team members' calendars for group scheduling
- [ ] Weather information in morning briefing
- [ ] Traffic data for accurate travel times
- [ ] Smart meeting preparation reminders
- [ ] Integration with task management systems
- [ ] Voice interface support
- [ ] Automatic conflict resolution suggestions
- [ ] Meeting room booking integration

## License

MIT
