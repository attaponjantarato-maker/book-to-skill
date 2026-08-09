# Project Bootstrap Guide

Use this workflow whenever a new project is created in this repository.

## 1. Create the workspace

```text
projects/<project-slug>/
```

Copy the starter files from `templates/project/`.

## 2. Fill project context

Populate `PROJECT_CONTEXT.md` with everything already known from the user/request. Keep unknown values explicit as `TBD` or `unknown`.

For imaging projects, capture modality, tracer/isotope, scanner, acquisition, reconstruction, corrections, quantification, segmentation/registration, available data, intended outputs, and tool preferences when known.

## 3. Fill machine-readable metadata

Update `project.yaml` so an agent can quickly identify the project domain, modality, tracer, tools, policy mode, and workflow status.

Do not duplicate long prose; keep it compact.

## 4. Create the initial plan

`PLAN.md` should contain:

- current objective
- current phase
- completed items
- next steps
- blockers / unknowns
- validation/tests to run

## 5. Record meaningful decisions

Use `DECISIONS.md` for architecture, methodology, tool selection, data-model, or workflow choices that future agents should know.

Do not record every small edit.

## 6. Work

Before implementation, the agent should identify relevant:

- repository architecture
- medical/domain skills
- source material
- project-specific constraints
- available tools/MCPs

Then implement and test the smallest coherent unit of work.

## 7. Update project memory

At the end of a meaningful work session:

- update `PLAN.md`
- update `DECISIONS.md` if a durable choice changed
- update `PROJECT_CONTEXT.md` / `project.yaml` if facts or constraints changed

The goal is that another agent can enter the repository later and continue without reconstructing the project from old chat messages.
