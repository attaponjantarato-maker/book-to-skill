# Hermes Integration

This fork can be used directly by Hermes as the **knowledge/skill factory** for the Molecular Imaging Research Assistant environment.

Hermes supports project context through `AGENTS.md` and can scan external skill directories. This repository exposes:

```text
hermes/skills/medical-book-to-skill/   # factory skill
generated_skills/                      # generated textbook/domain skills
```

## Recommended sibling-repository layout

```text
D:\ResearchAI\
├── molecular-imaging-assistant\
└── book-to-skill\
```

Use `molecular-imaging-assistant` as the Hermes working directory and add this repository's skill directories to Hermes config:

```yaml
skills:
  external_dirs:
    - "D:\\ResearchAI\\molecular-imaging-assistant\\skills"
    - "D:\\ResearchAI\\book-to-skill\\hermes\\skills"
    - "D:\\ResearchAI\\book-to-skill\\generated_skills"
```

## Factory skill

After Hermes scans `hermes/skills`, the factory skill can be invoked as:

```text
/medical-book-to-skill
```

Examples:

```text
/medical-book-to-skill สร้าง source skill จากหนังสือ PET physics เล่มนี้สำหรับใช้ในงานวิจัยส่วนตัว
```

```text
/medical-book-to-skill อัปเดต skill เดิมด้วย guideline PDF ฉบับนี้ แต่เก็บ provenance และความขัดแย้งของแหล่งข้อมูลไว้
```

The factory skill should use the upstream extraction/generation workflow in this repository and the medical extension rules in `docs/MEDICAL_KNOWLEDGE_ARCHITECTURE.md`.

## Default output for Hermes

Prefer:

```text
generated_skills/<skill-slug>/
├── SKILL.md
├── chapters/ or references/
├── concepts/
├── equations/
├── provenance/
├── glossary.md
└── cheatsheet.md
```

Not every generated skill needs every folder. Create only what is useful for that source.

## Source skill vs project context

Keep source knowledge separate from research-project context:

```text
Textbook / paper / guideline
        ↓
Book-to-Skill
        ↓
generated source/domain skill
        ↓
Hermes loads on demand
        +
MIA project context
        ↓
research reasoning / workflow
```

A project-specific scanner protocol, dataset location, hypothesis, or analysis decision belongs in the Molecular Imaging Assistant project workspace rather than in a textbook source skill.

## Medical knowledge behavior

Default policy is `ADVISORY` for personal research. Preserve:

- concepts and mechanisms;
- equations and assumptions;
- technical/clinical context labels when useful;
- limitations and `do_not_infer` notes;
- source title/edition/chapter/page or other locator when available.

Warnings should inform research reasoning without automatically blocking exploratory use.

## Refreshing skills in Hermes

After adding or changing a generated skill, start a fresh Hermes session if the running session has not discovered the new directory yet.

The generated skill is then available as a slash command according to its `name` in `SKILL.md`, and Hermes can also load it when relevant to a natural-language request.
