# Generated Hermes Skills

This directory is the default local output location for reusable skills generated from textbooks, papers, guidelines, notes, and other sources.

Hermes can scan this directory directly through:

```yaml
skills:
  external_dirs:
    - "BOOK_TO_SKILL_ROOT\\generated_skills"
```

Each generated child directory should contain a valid `SKILL.md`.

Example:

```text
generated_skills/
└── pet-physics-foundations/
    ├── SKILL.md
    ├── chapters/
    ├── concepts/
    ├── equations/
    └── provenance/
```

Generated skills from private or copyrighted sources are normally local working artifacts and should not be committed to the public repository unless you intentionally decide otherwise.
