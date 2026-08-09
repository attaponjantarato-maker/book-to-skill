# AGENTS.md

## Purpose

This repository is a personal/experimental fork of Book-to-Skill for building reusable medical imaging and nuclear medicine knowledge skills.

Its primary role in the Hermes ecosystem is **Knowledge / Skill Factory**. The sibling `molecular-imaging-assistant` repository is the recommended Hermes research-project workspace and orchestrator.

The upstream extraction pipeline should remain usable. Medical-domain behavior is added as an extension layer rather than by rewriting unrelated upstream components.

## Read this before starting work

Before making changes, an AI agent should:

1. Read this file completely.
2. Read `docs/MEDICAL_KNOWLEDGE_ARCHITECTURE.md` when the task touches medical knowledge, nuclear medicine, medical physics, imaging, source skills, or knowledge validation.
3. Read `docs/HERMES_INTEGRATION.md` when the task involves Hermes, skill installation/discovery, or the Molecular Imaging Assistant repository.
4. Identify whether the task is upstream Book-to-Skill work, medical knowledge work, Hermes integration, or project-specific work.
5. Preserve source provenance when extracting or transforming textbook/guideline/paper knowledge.

## Repository working style

- Default medical policy is **ADVISORY**. This repository is for personal research and experimentation; warnings should inform the agent without blocking exploration.
- Do not introduce hard clinical-production gates unless explicitly requested.
- Keep source-derived knowledge traceable to the source. A source skill represents what that source says; do not silently merge multiple books into one truth.
- Prefer extending `book_to_skill/medical/` over modifying unrelated upstream extraction code.
- Keep changes focused and testable.
- Run relevant tests before considering an implementation complete.
- Avoid committing private textbooks, patient data, DICOM datasets, credentials, or generated large outputs.

## Hermes integration

Hermes should see this repository through two external skill directories:

```text
book-to-skill/hermes/skills       # factory/orchestration skills
book-to-skill/generated_skills    # generated textbook/domain source skills
```

The factory skill is:

```text
hermes/skills/medical-book-to-skill/SKILL.md
```

When Hermes creates a reusable skill from a source for this personal research environment, prefer writing it under:

```text
generated_skills/<skill-slug>/
```

unless the user explicitly chooses another destination.

Generated skills should contain a valid `SKILL.md` and may contain chapter/reference/concept/equation/provenance files for progressive loading.

## Relationship to Molecular Imaging Assistant

Recommended architecture:

```text
book-to-skill
   ├─ factory skill
   └─ generated source/domain skills
               \
                -> Hermes Research Assistant <- MIA skills + MCP/native tools
               /
molecular-imaging-assistant
   └─ projects/<research-project>/
```

Use `molecular-imaging-assistant` for persistent research projects unless there is a specific reason to keep a project here.

## Project workspace standard

If a project is created inside this repository, follow `docs/PROJECT_WORKSPACE_STANDARD.md`.

Minimum project files:

```text
projects/<project-slug>/
├── PROJECT_CONTEXT.md
├── PLAN.md
├── DECISIONS.md
└── project.yaml
```

When bootstrapping a new project here, start from `templates/project/` and follow `docs/PROJECT_BOOTSTRAP.md`.

## Updating project memory

For projects stored here:

- `PROJECT_CONTEXT.md`: facts, constraints, goals, available data/tools.
- `PLAN.md`: current work, completed steps, next steps, blockers.
- `DECISIONS.md`: accepted/rejected architecture or methodology decisions and rationale.
- `project.yaml`: stable machine-readable project metadata and configuration.

Keep these compact and decision-relevant rather than as verbose activity logs.
