---
command: sprint-plan
description: Review PRD and SDD to create comprehensive sprint plan with clarification of uncertainties
---

Use the sprint-planner-pm agent to create a detailed sprint plan based on the existing PRD and SDD documents.

## Your Mission

You are tasked with creating a comprehensive sprint plan that will guide the engineering team through MVP development. This requires careful analysis, proactive clarification, and strategic planning.

## Phase 1: Document Review and Analysis

1. **Carefully review `docs/prd.md`** (Product Requirements Document):
   - Understand all business requirements and user stories
   - Note the project timeline and success criteria
   - Identify any requirements that seem incomplete or ambiguous

2. **Thoroughly analyze `docs/sdd.md`** (Software Design Document):
   - Understand the technical architecture and technology choices
   - Review the implementation approach and dependencies
   - Note any technical decisions that may impact sprint planning

3. **Cross-reference both documents** to identify:
   - Any misalignments between requirements and design
   - Missing information that would impact implementation
   - Dependencies that affect sprint sequencing

## Phase 2: Interactive Clarification (CRITICAL)

**IMPORTANT**: Before generating any sprint plan, you MUST:

1. **List ALL uncertainties and questions** you have about:
   - Unclear or ambiguous requirements
   - Technical implementation details
   - Priority of features
   - Resource assumptions
   - Timeline constraints
   - Testing approach
   - Deployment strategy

2. **For each uncertainty**:
   - Clearly explain what is unclear or missing
   - Propose 2-3 specific options for resolution
   - Provide your recommendation with rationale
   - Wait for user feedback and confirmation

3. **Examples of questions to ask**:
   - "The PRD mentions X but the SDD implements Y. Which approach should we follow?"
   - "Should Sprint 1 focus on infrastructure or can we start with user-facing features?"
   - "The timeline shows 2 weeks. Should we plan for 4 sprints of 2.5 days each, or adjust?"
   - "What is the team size assumption? This affects sprint capacity planning."
   - "Should we include deployment and production setup in the final sprint?"

4. **Continue the dialogue** until:
   - All your questions are answered
   - You have no remaining doubts
   - The user explicitly confirms to proceed with sprint planning

## Phase 3: Sprint Plan Generation (Only after clarification)

Once all uncertainties are resolved and you have user approval:

1. **Create a comprehensive sprint plan** that includes:
   - Executive summary with total sprints and timeline
   - Detailed breakdown of each 2.5-day sprint
   - Clear sprint goals and deliverables
   - Specific acceptance criteria for each sprint
   - Progress tracking checkboxes
   - Dependencies and risk factors

2. **Ensure the plan**:
   - Covers all requirements from the PRD
   - Follows the architecture defined in the SDD
   - Provides a realistic path to MVP completion
   - Includes testing and quality assurance
   - Has buffer time for unexpected issues

3. **Save the final sprint plan** to `docs/sprint.md`

## Key Principles

- **NO ASSUMPTIONS**: Never assume when information is unclear - always ask
- **BE SPECIFIC**: Vague plans lead to failed sprints
- **THINK DEPENDENCIES**: Sequence work logically
- **INCLUDE TESTING**: Quality is part of each sprint, not an afterthought
- **STAY REALISTIC**: Better to under-promise and over-deliver

Remember: A good sprint plan is built on clear understanding, not guesswork. Take the time to clarify everything before planning.