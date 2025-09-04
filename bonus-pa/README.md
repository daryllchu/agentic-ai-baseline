# Personal assistant

Directory: `bonus-pa/`.

This is a project directory that holds Claude Code config files that would allow for tool use, agents and commands that would function like a human personal assistant.

This is a bonus demonstration project to showcase Claude Code's usage beyond software development.

## MCP connection

1. Gmail
2. Calendar

### Functions

1. `/morning`
- Scans through Calendar and provide a good summary for the day. Highlight any events that I need to attend and roughly plan my day, including my travel times.
- Scans through Gmail for any important emails and provide a summary to start the day. Highlight any key emails and any emails that I need to respond to. Take note of `_TODO` tag.

2. `/book`
- Go through future calendar events that seems like it needs a restaurant booking, ask for how many pax (via CLI), budget, and suggest a list of restaurants that have tables available (via chope.co).
