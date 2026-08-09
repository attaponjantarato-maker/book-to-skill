# Project Workspace Standard

Every substantial experimental/research project created in this repository should have an explicit, persistent project context that an AI agent can read before starting work.

## Why

Conversation memory is not a reliable project database. Project files make goals, constraints, decisions, and current state durable across agents and sessions.

## Minimum required files

```text
projects/<project-slug>/
├── PROJECT_CONTEXT.md
├── PLAN.md
├── DECISIONS.md
└── project.yaml
```

### `PROJECT_CONTEXT.md`
Human-readable source of truth for the project: objective, scope, modality/tracer, data, constraints, tools, outputs, and known assumptions.

### `PLAN.md`
Current execution state: what is being built/tested now, what is complete, what is next, and blockers.

### `DECISIONS.md`
Short architecture/methodology decision records. Use this to prevent future agents from reopening already-resolved choices without a reason.

### `project.yaml`
Machine-readable project metadata/configuration for agent orchestration. It should mirror stable facts from `PROJECT_CONTEXT.md`, not contain a second conflicting narrative.

## Recommended optional folders

```text
src/          implementation code
workflows/    workflow definitions and orchestration configs
tests/        project-specific tests
notes/        scratch research notes worth keeping
outputs/      generated results; normally not authoritative source code
docs/         project-specific documentation
```

Only add directories that the project actually needs.

## Agent startup rule

Before changing an existing project, an agent should read, in order:

1. repository `AGENTS.md`
2. project `PROJECT_CONTEXT.md`
3. project `project.yaml`
4. project `PLAN.md`
5. project `DECISIONS.md`
6. relevant domain/medical architecture or source-skill files

The agent should then summarize internally what it understands about the current project before implementing changes.

## Project creation rule

For a new project:

1. Choose a short stable slug.
2. Copy `templates/project/` into `projects/<slug>/`.
3. Fill known fields from the request/context.
4. Never invent unknown scanner, tracer, protocol, dataset, or methodology details; mark them `unknown` / `TBD` instead.
5. Create an initial plan.
6. Record important design choices as decisions.
7. Keep context files updated as the project evolves.

## Medical/Nuclear Medicine projects

For projects involving PET, SPECT, CT, MRI, dosimetry, nuclear medicine, medical physics, image processing, segmentation, quantification, reconstruction, or related analysis, include relevant fields when known:

- clinical/research objective
- modality and scanner type
- radiopharmaceutical/tracer/isotope
- acquisition protocol
- reconstruction/corrections
- calibration/quantification metric
- segmentation/registration methods
- available data and metadata
- intended analysis and outputs
- preferred tools/MCPs/software
- computational constraints
- validation/reference data

This is an organizational convention, not a clinical-production safety framework. The default medical knowledge policy in this fork remains advisory.

## Decision record format

Use compact entries such as:

```markdown
## D-003 — Keep source skills separate before canonical synthesis
Status: Accepted
Date: YYYY-MM-DD

**Decision**
Keep each textbook as an independent source skill.

**Reason**
Preserves provenance and disagreements across sources.

**Consequences**
Canonical multi-source synthesis is a later explicit step.
```

## Keeping project memory useful

Good project memory is compact, current, and actionable. Do not turn these files into raw chat transcripts or exhaustive activity logs.
