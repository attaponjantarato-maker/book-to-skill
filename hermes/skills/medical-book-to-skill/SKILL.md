---
name: medical-book-to-skill
description: Convert textbooks, papers, guidelines, technical documents, or research notes into reusable Hermes skills for medical imaging, nuclear medicine, medical physics, image analysis, and related research. Use when the user wants to create, update, or organize source/domain knowledge skills from documents.
license: MIT
metadata:
  version: "0.1"
  author: "Attapon Jantarato"
---

# Medical Book-to-Skill for Hermes

## Role

This is the Hermes-facing factory skill for the personal medical-research knowledge library.

Use the repository's upstream Book-to-Skill extraction/generation workflow, then apply the medical extension conventions from:

- `docs/MEDICAL_KNOWLEDGE_ARCHITECTURE.md`
- `docs/HERMES_INTEGRATION.md`
- repository `AGENTS.md`

## Default destination

Unless the user specifies another location, write reusable outputs under:

```text
generated_skills/<skill-slug>/
```

Each generated skill must have a valid `SKILL.md` so Hermes can discover it through `skills.external_dirs`.

## Workflow

1. Identify the input source(s) and intended knowledge scope.
2. Use the existing Book-to-Skill extraction path appropriate for the document type.
3. Preserve useful document structure such as chapters, sections, tables, formulas, and source locators.
4. Generate a source skill rather than a generic summary.
5. For medical/scientific material, capture when relevant:
   - concept/principle;
   - mechanism;
   - equations;
   - assumptions;
   - use-when context;
   - limitations/failure modes;
   - `do_not_infer` notes;
   - provenance.
6. Classify knowledge as fundamental, technical, or clinical when that distinction helps later reasoning. The default policy is advisory, not blocking.
7. Keep project-specific facts out of the reusable source skill unless the source itself is a project document.
8. Write the resulting skill under `generated_skills/` and report its skill name and entry files.

## Multi-source behavior

Do not silently erase disagreement between sources.

For multiple textbooks/papers/guidelines:

- preserve source-specific provenance;
- distinguish agreement from disagreement;
- label technology-, population-, tracer-, scanner-, or protocol-dependent statements when relevant;
- create a canonical/synthesized skill only when the user asks for synthesis.

## Integration with Molecular Imaging Assistant

The generated skill is knowledge, not the research project itself.

Expected flow:

```text
source documents
     ↓
medical-book-to-skill
     ↓
generated_skills/<skill>/
     ↓
Hermes
     +
Molecular Imaging Assistant project context
     +
MCP/native scientific tools
     ↓
research workflow
```

## Example requests

```text
/medical-book-to-skill เปลี่ยนหนังสือ PET Physics PDF นี้เป็น skill สำหรับ Hermes โดยเน้น count statistics, reconstruction, corrections และ quantification
```

```text
/medical-book-to-skill สร้าง source skill จาก EANM guideline นี้และเก็บ section/page provenance ไว้
```

```text
/medical-book-to-skill รวม source skills PET physics 3 เล่มเป็น canonical skill แต่ห้ามกลบจุดที่หนังสือให้ข้อมูลต่างกัน
```
