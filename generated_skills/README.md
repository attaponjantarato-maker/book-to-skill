# Generated Hermes Source Skills / Optional Local Vault

This directory is the default local output for reusable source skills generated
from authorized full-text textbooks, papers, guidelines, manuals, standards, and
technical documents.

Hermes may scan it through:

```yaml
skills:
  external_dirs:
    - "BOOK_TO_SKILL_ROOT\\generated_skills"
```

It may also be opened directly as an Obsidian vault during PoC-K002. This keeps the
human view and Hermes source notes on the same Markdown instead of copying derived
knowledge into a second wiki.

## PoC layout

```text
generated_skills/
├── .obsidian/                       # local UI state; not authoritative
├── _notes/
│   ├── concepts/
│   ├── syntheses/
│   ├── projects/
│   ├── disagreements/
│   └── inbox/                       # limited-access/discovery material; no SKILL.md
└── pet-physics-source-v2/
    ├── SKILL.md
    ├── SOURCE.md
    ├── references/
    │   └── count-statistics.md
    └── limitations.md
```

Each installed child source skill must contain a valid `SKILL.md`, a scalar
`SOURCE.md` based on `templates/evidence_second_brain/SOURCE.md`, and at least one
source note under `references/` or `chapters/` with a real locator.

`SOURCE_DERIVED_POC` means the notes were derived from the source identified by
title/version/hash. It does not mean independently verified, current guideline,
scientifically validated, diagnostically accurate, or clinically useful.

## Required checks

Before loading a medical source skill into Hermes:

```bash
python tools/validate_skill.py generated_skills/<source-slug>/SKILL.md
python tools/validate_source_skill.py generated_skills/<source-slug>
python tools/scan_generated_skill.py generated_skills/<source-slug>
```

Security-scan findings require human review. Passing the contracts does not prove
factual or scientific correctness. Follow `docs/POC_K002_RUNBOOK.md` for source
spot-checks, Hermes discovery, and evaluation.

## Retrieval boundary

Start with metadata/text search. If a future RAG index is tested, it should include
source cards and `SOURCE_NOTE` files but exclude:

- `SKILL.md` behavioral instructions;
- limited-access `_notes/inbox` items;
- project notes and personal interpretations from published-evidence claims;
- superseded notes unless the query is historical.

The index is a rebuildable cache and must return source ID, access level, review
state, and locator with each passage.

## Privacy, copyright, and Git

Generated children, private source files, Obsidian state, personal notes, and local
indexes are ignored by default. Do not commit or redistribute content derived from
private/copyrighted sources unless the owner has explicitly reviewed the license,
privacy, and intended audience.

Use standard Markdown links when practical so the vault remains usable without
Obsidian.
