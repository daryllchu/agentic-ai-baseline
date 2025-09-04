## demo-1-idea

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

## demo-1-idea

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

## demo-1-idea


---

## Codex review

You are a senior technical lead. For context, read the following documents: docs/prd.md, docs/sdd.md, docs/sprint.md.

The engineers have carried out the work for Sprint 1. Review the work done carefully. Point out any issues, any bugs


---

Tips:

1. `script -r` to start a recording session.
2. `script -p typescript` to play the recorded session.
