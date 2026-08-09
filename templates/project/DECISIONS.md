# Project Decisions

Record durable architecture, methodology, workflow, or tool decisions here. Keep entries compact and decision-relevant.

## D-001 — Initialize project workspace

**Status:** Accepted  
**Date:** YYYY-MM-DD

**Decision**
Use the repository project-workspace standard with `PROJECT_CONTEXT.md`, `PLAN.md`, `DECISIONS.md`, and `project.yaml` as persistent project memory.

**Reason**
Allows different AI agents and future sessions to recover project state without depending on chat history.

**Consequences**
Project context files should be updated when meaningful facts, plans, or decisions change.

---

## Decision Template

### D-XXX — <short title>

**Status:** Proposed / Accepted / Superseded / Rejected  
**Date:** YYYY-MM-DD

**Decision**
<what was decided>

**Reason**
<why>

**Alternatives considered**
- <optional>

**Consequences**
- <what changes because of this decision>
