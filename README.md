# Demo project files for my talk NUS-ISS Learning Fest 2025

## Talk

Title: Practical Agentic AI in Software Development

Explore how agentic AI is transforming software development across the entire lifecycle. From requirement analysis to deployment, AI agents accelerate every phase, enhancing requirement gathering, product planning, PRD writing, implementation, automated testing, debugging, and DevOps. Learn how these agents coordinate tasks, share context, and maintain consistency throughout the process. Gain insights into the Model Context Protocol (MCP), which enables seamless integration between agents and tools, allowing interaction with databases, APIs, and development platforms. Join us to explore practical applications and strategies that will help you harness practical agentic AI.

## Projects

### Personal assistant

Directory: `bonus-pa/`.

This is a project directory that holds Claude Code config files that would allow for tool use, agents and commands that would function like a human personal assistant.

#### MCP connection

1. Gmail
2. Calendar

#### Functions

1. `/morning`
- Scans through Calendar and provide a good summary for the day. Highlight any events that I need to attend and roughly plan my day, including my travel times. 
- Scans through Gmail for any important emails and provide a summary to start the day. Highlight any key emails and any emails that I need to respond to. Take note of `_TODO` tag.

2. `/book`
- Go through future calendar events that seems like it needs a restaurant booking, ask for how many pax (via CLI), budget, and suggest a list of restaurants that have tables available (via chope.co).


