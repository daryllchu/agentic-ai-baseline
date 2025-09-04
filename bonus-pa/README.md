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

### 🍽️ Restaurant Booking Assistant (`/book`)
- Scans upcoming calendar events for potential dining occasions
- Interactive CLI for booking details (party size, budget, cuisine)
- Provides restaurant recommendations based on preferences
- Simulates Chope.co integration for availability
- Can create calendar reminders for bookings
- Supports dietary restrictions and special requests

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

### Restaurant Booking Assistant

Find and book restaurants for upcoming events:

```bash
npm run book
# or
node commands/book.js
```

This will:
1. Scan your calendar for potential dining events
2. Let you select an event or create a new booking
3. Ask for booking details (party size, budget, cuisine)
4. Provide restaurant recommendations
5. Optionally add a reminder to your calendar

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

### Restaurant Booking Not Working
- The Chope.co integration is simulated for demonstration
- In production, you would integrate with Chope's actual API

## Future Enhancements

- [ ] Real Chope.co API integration
- [ ] Gmail integration for email summaries
- [ ] Weather information in morning briefing
- [ ] Traffic data for accurate travel times
- [ ] Smart meeting preparation reminders
- [ ] Integration with task management systems
- [ ] Voice interface support

## License

MIT
