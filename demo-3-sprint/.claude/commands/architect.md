---
name: architect
description: Generate Software Design Document from PRD
---

You are invoking the software-architect-sdd agent to create a comprehensive Software Design Document based on the Product Requirements Document.

**Your task is to**:
1. Carefully review the PRD at `docs/prd.md`
2. Analyze all requirements and identify any ambiguities or uncertainties
3. **IMPORTANT**: Before writing the SDD, clarify ALL uncertainties with the user by:
   - Listing specific questions about unclear requirements
   - Providing proposals for how to handle each uncertainty
   - Waiting for user confirmation and feedback
4. Only when you are completely satisfied with the answers and have no remaining doubts, proceed to:
   - Create a comprehensive Software Design Document
   - Save it to `docs/sdd.md`

**Key Requirements**:
- Do not make assumptions about unclear requirements
- Engage in dialogue with the user to resolve all questions
- Propose solutions when requirements are ambiguous
- Ensure the SDD is detailed enough for implementation without ambiguity

Please begin by reviewing the PRD and identifying any areas that need clarification.