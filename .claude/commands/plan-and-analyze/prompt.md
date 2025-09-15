---
command: plan-and-analyze
description: Define goals, requirements, scope, research and generate Product Requirement Document (PRD)
---

Use the product-manager-prd agent to:

## Phase 1: Review and Refine Idea Document
1. **First, review `docs/idea.md`** to assess if it contains sufficient detail
2. **Validate that all sections are properly filled out**:
   - Goals section has clear, specific objectives (not placeholders)
   - Requirements section has concrete, actionable requirements
   - Scope sections (in/out) are clearly defined
   - Notes/constraints section provides relevant context
3. **If `idea.md` is incomplete or unclear**:
   - DO NOT generate PRD yet
   - Work interactively with the user to refine `docs/idea.md`
   - Help identify gaps and suggest improvements
   - Edit the document iteratively until it's comprehensive
   - Continue refinement until user confirms they are satisfied

## Phase 2: Generate PRD (only after idea validation)
Once `docs/idea.md` is properly refined and user approves:
1. Use the validated idea document as foundation
2. Conduct systematic interview to extract additional details
3. Define comprehensive project goals
4. Elaborate on requirements with technical specifications
5. Clearly identify project scope and boundaries
6. Research and refine all aspects
7. Generate a comprehensive Product Requirements Document (PRD)
8. Save the output at `docs/prd.md`

**IMPORTANT**: Only proceed to PRD generation after `docs/idea.md` is validated and refined. The idea document must be complete and approved by the user before generating the PRD.
