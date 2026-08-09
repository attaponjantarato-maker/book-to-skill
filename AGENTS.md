# AGENTS.md

## Purpose

This repository is a personal/experimental fork of Book-to-Skill for building reusable medical imaging and nuclear medicine knowledge skills and, later, agent-orchestrated research workflows.

The upstream extraction pipeline should remain usable. Medical-domain behavior is added as an extension layer rather than by rewriting unrelated upstream components.

## Read this before starting work

Before making changes, an AI agent should:

1. Read this file completely.
2. Read `docs/MEDICAL_KNOWLEDGE_ARCHITECTURE.md` when the task touches medical knowledge, nuclear medicine, medical physics, imaging, source skills, or knowledge validation.
3. If working inside a project under `projects/`, read that project's `PROJECT_CONTEXT.md`, `PLAN.md`, `DECISIONS.md`, and `project.yaml` before proposing or implementing work.
4. Identify whether the task is upstream Book-to-Skill work, medical knowledge work, or project-specific workflow work.
5. Preserve source provenance when extracting or transforming textbook/guideline/paper knowledge.

## Repository working style

- Default medical policy is **ADVISORY**. This repository is for personal research and experimentation; warnings should inform the agent without blocking exploration.
- Do not introduce hard clinical-production gates unless explicitly requested.
- Keep source-derived knowledge traceable to the source. A source skill represents what that source says; do not silently merge multiple books into one truth.
- Prefer extending `book_to_skill/medical/` over modifying unrelated upstream extraction code.
- Keep changes focused and testable.
- Run relevant tests before considering an implementation complete.
- Avoid committing private textbooks, patient data, DICOM datasets, credentials, generated large outputs, or other sensitive/local-only material.

## Project workspace standard

Every new project created in this repository should follow `docs/PROJECT_WORKSPACE_STANDARD.md`.

Minimum project files:

```text
projects/<project-slug>/
├── PROJECT_CONTEXT.md
├── PLAN.md
├── DECISIONS.md
└── project.yaml
```

Recommended working layout:

```text
projects/<project-slug>/
├── PROJECT_CONTEXT.md
├── PLAN.md
├── DECISIONS.md
├── project.yaml
├── src/
├── tests/
├── workflows/
├── notes/
└── outputs/          # normally local/generated, not source-of-truth
```

When bootstrapping a new project, start from the files in `templates/project/` and follow `docs/PROJECT_BOOTSTRAP.md`.

## Project startup sequence for agents

When asked to work on an existing project:

```text
AGENTS.md
   ↓
PROJECT_CONTEXT.md + project.yaml
   ↓
PLAN.md
   ↓
DECISIONS.md
   ↓
relevant medical/domain skills and source material
   ↓
plan → implement → test → update project memory
```

When asked to create a new project:

1. Create `projects/<project-slug>/`.
2. Copy the project templates.
3. Fill in known context from the user/request; mark unknown fields clearly rather than inventing them.
4. Record the initial implementation plan in `PLAN.md`.
5. Record non-obvious architecture/methodology choices in `DECISIONS.md` as they are made.
6. Keep `project.yaml` aligned with the human-readable context so agents can read project state without reparsing long prose.
7. Add domain-specific folders only when needed; do not create empty complexity for its own sake.

## Updating project memory

Agents should update project memory when meaningful state changes occur:

- `PROJECT_CONTEXT.md`: facts, constraints, goals, available data/tools.
- `PLAN.md`: current work, completed steps, next steps, blockers.
- `DECISIONS.md`: accepted/rejected architecture or methodology decisions and their rationale.
- `project.yaml`: stable machine-readable project metadata and configuration.

Do not use these files as verbose activity logs. Keep them compact and decision-relevant.
