# Agentic software development demo

## Overview

This is the main project directory that demonstrates the usage of agentic AI via Claude Code for software development. It is a companion project for my talk at NUS-ISS Learning Fest 2025.

My talk details:

Title: Practical Agentic AI in Software Development

Explore how agentic AI is transforming software development across the entire lifecycle. From requirement analysis to deployment, AI agents accelerate every phase, enhancing requirement gathering, product planning, PRD writing, implementation, automated testing, debugging, and DevOps. Learn how these agents coordinate tasks, share context, and maintain consistency throughout the process. Gain insights into the Model Context Protocol (MCP), which enables seamless integration between agents and tools, allowing interaction with databases, APIs, and development platforms. Join us to explore practical applications and strategies that will help you harness practical agentic AI.


## Details

Project should run in Claude Code, demonstrating the entire software development lifecycle using agentic AI, namely (based on [IBM's Software Development Life Cycle](https://www.ibm.com/think/topics/sdlc)):

1. Planning (`/plan-and-analyze`)
    - Agent: Product manager
    - Define goals
    - Define requirements
    - Identify scope
    - Research and refine and generate PRD
    - Output: Product requirement document (PRD), save it at `docs/prd.md`

2. Architect (`/architect`)
    - Agent: Software architect
    - Define project architecture
    - Software stack
    - Database design
    - UI
    - Output: Software design document (SDD), save it at `docs/sdd.md`

3. Sprint planning (`/sprint-plan`)
    - Agent: Product manager (Scrum master)
    - Read PRD and SDD, break down into sprints.
    - Each sprint must have clear goals, deliverables, and acceptance criteria
    - Each sprint should be no longer than 2.5 days (half a week)
    - Each sprint must have checkboxes for tracking progress
    - Output: Sprint planing plan to achieve PRD and SDD, save it at `docs/sprint.md`.
