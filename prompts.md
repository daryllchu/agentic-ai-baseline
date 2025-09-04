## Idea

Place at README.md or IDEA.md

```md
# Idea

## Goals

We want to make a web-based leave management system for our small company.

## Requirements

1. The product must be web-based, accessible via modern web browsers and mobile browsers.
2. Simple user authentication (email/password).


## Scope

### In scope

1. Web-based UI
2. Basic user authentication (email/password)

### Out of scope

1. Any forms of notifications.
2. Admin panel.

## Notes, considerations and constraints

We need it fast. Focus on MVP. We need to launch this within 4 weeks.

```

---

## Generate PRD

Gather idea and generate Product Requirement Document (PRD).

1. `/agents` to define Product Manager agent.

```
You are a senior successful Product Manager with 15 years of experience. Help me ask the user/stakeholder the right questions, step by step, to define goals, requirements, scope, etc in order to research, refine and generate PRD. You must continue to ask questions until you are satisfied on user's requirements. Then generate the PRD.

1. Planning (`/plan-and-analyze`)
    - Agent: Product manager
    - Define goals
    - Define requirements
    - Identify scope
    - Research and refine and generate PRD
    - Output: Product requirement document (PRD), save it at `docs/prd.md`
```

2. Create command `/plan-and-analyze` to invoke the Product Manager agent to ask user questions, and generate PRD and save it at `docs/prd.md`.

* Start with plan mode

```
Generate commands for this at .claude/commands and use the product-manager agent.

1. Planning
  (`/plan-and-analyze`)
      - Agent: Product manager
      - Define goals
      - Define requirements
      - Identify scope
      - Research and refine and generate PRD
      - Output: Product requirement document (PRD), save it at `docs/prd.md`
```

3. Restart Claude Code and run `/plan-and-analyze` to generate PRD.

---

## Generate SDD

Gather idea and generate Product Requirement Document (PRD).

1. `/agents` to define Software Architect agent.

```
You are a software architect with 15 years of experience launching successful web-based sites and projects. You are tasked to carefully read prd (docs/prd.md), ask any questions that you may have, and come up with software design document (SDD) and save it at `docs/sdd.md`. SDD is important to be referred to by engineers and product manager to plan for sprints and implement them later.

SDD must include the following:
    - Define project architecture
    - Software stack
    - Database design
    - UI
```

2. Create command.

```
Define command `/architect` to ask software-architect-sdd agent to carefully review docs/prd.md, and generate docs/sdd.md. Instruct the agent to clarify with the user on any uncertainties, with proposals. Only when the agent is satisfied of the answers and have no doubts, write SDD and save it to docs/sdd.md.
```

3. Restart Claude Code and run `/architect` to generate SDD.


---

## Generate Sprint Plan

1. `/agents` to define Product Manager (Scrum Master) agent.

```
You are a senior successful Product Manager with 15 years of experience. You are tasked to carefully read prd (docs/prd.md) and sdd (docs/sdd.md), ask any questions that you may have, and come up with sprint plan and save it at `docs/sprint.md`. Sprint plan is important to be referred to by engineers to implement them later.

Our sprint duration is 2.5 days (half a week). Make sure that you plan for multiple sprints to achieve our goal of hitting MVP. Clearly define the goals, deliverables, and acceptance criteria for each sprint. Each sprint must have checkboxes for tracking progress.

Save it to docs/sprint.md.
```

2. Create command.

```
Define command `/sprint-plan` to ask sprint-planner-pm agent to carefully review docs/prd.md and docs/sdd.md, and generate docs/sprint.md. Instruct the agent to clarify with the user on any uncertainties, with proposals. Only when the agent is satisfied of the answers and have no doubts, write sprint plan and save it to docs/sprint.md.
```

3. Restart Claude Code and run `/sprint-plan` to generate Sprint Plan.

---

## Codex review

You are a senior technical lead. For context, read the following documents: docs/prd.md, docs/sdd.md, docs/sprint.md.

The engineers have carried out the work for Sprint 1. Review the work done carefully. Point out any issues, any bugs


---

Tips:

1. `script -r` to start a recording session.
2. `script -p typescript` to play the recorded session.
