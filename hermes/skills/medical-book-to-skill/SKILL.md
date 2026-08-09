---
name: medical-book-to-skill
description: Convert an authorized full-text textbook, paper, guideline, manual, standard, or technical document into one evidence-labelled Hermes source skill for medical imaging, nuclear medicine, medical physics, or image analysis. Use when the user wants to ingest, update, organize, or test source-derived knowledge while preserving access level, source hash, real locators, review state, disagreement, and limitations.
license: MIT
metadata:
  version: "0.2"
  author: "Attapon Jantarato"
---

# Medical Book-to-Skill for Hermes

## Role and authority

This is the Hermes-facing **knowledge factory**. It extracts and publishes
traceable source-derived notes. It does not independently verify truth, establish
guideline currency, calculate scientific results, or validate clinical use.

`SOURCE_DERIVED_POC` means derived from the identified source. It does not mean
verified, validated, current, accurate for another population/scanner/software
version, or suitable for patient care.

Before acting, read completely:

- repository `AGENTS.md`;
- `docs/MEDICAL_KNOWLEDGE_ARCHITECTURE.md`;
- `docs/EVIDENCE_AWARE_SECOND_BRAIN.md`;
- `docs/HERMES_INTEGRATION.md`;
- `docs/POC_K002_RUNBOOK.md` when executing PoC-K002.

## Default destination

Unless the owner selects another approved local path, write one source skill to:

```text
generated_skills/<source-slug>/
```

Never silently overwrite an existing source/version. If the slug exists, compare
source ID, version, and SHA-256, then ask whether to update the same source, create a
new versioned slug, or stop.

## Mandatory workflow

### 0. Perform knowledge-scoped P0-Lite

Check existing generated skills, Hermes external skill directories, the source
identity/version, and any existing vault/search integration for the same topic.
Choose `REUSE`, `WRAP`, `BUILD_THIN`, or `DEFER` and record the rationale in the
active MIA PoC state.

Do not create a Book-to-Skill MCP, vector database, or knowledge graph in this step.

### 1. Register the source boundary

Confirm or obtain only the missing critical fields:

- exact local source file or authorized source set;
- title, type, version/edition, and publication date when known;
- intended topic and use;
- processing/redistribution permission;
- access level;
- source-file SHA-256;
- DOI/PMID only when verified, otherwise `unknown`;
- bounded authority scope and time sensitivity.

An installed source skill requires `FULL_TEXT`. If access is `ABSTRACT_ONLY`,
`SEARCH_SNIPPET`, or `SECONDARY_SOURCE`, do not create `SKILL.md`. At most create a
clearly labelled discovery note under `generated_skills/_notes/inbox/` when the
owner wants it. Never use limited-access material alone to reconstruct calculation
steps, protocols, accuracy, implementation requirements, or clinical readiness.

Stop if authorization, source identity, or destination is ambiguous.

### 2. Keep sources separate

Default to one publication/source version per installed source skill. For multiple
sources:

1. create or reuse a separate source skill for each source;
2. preserve its own provenance and locators;
3. create a separate `SYNTHESIS_NOTE` only when explicitly requested;
4. label agreement and disagreement without averaging;
5. call the result a `synthesis candidate`, not `canonical`.

### 3. Extract locally

Use the repository's existing extraction path and select the content mode that fits
the source. Do not upload a private source merely to improve extraction.

```bash
python scripts/extract.py "<source-path>" --mode technical --install-missing ask
```

Use `--mode text` for mostly prose material. Inspect `metadata.json`, representative
text from the beginning/middle/end, headings, and any tables/equations needed for
the bounded topic.

If required content or locators are lost, stop or choose a better local extraction
path. Never invent page or section locators.

### 4. Inspect evidence before affirmative extraction

For a research paper, inspect the relevant full Methods, Results, tables/figures,
supplementary material, limitations, exclusion criteria, and reported failures when
present before extracting claims about method steps, numerical performance,
availability, implementation, or clinical use.

For manuals and technical documents, bind notes to the matching product/software
version and do not generalize operational instructions to another version.

For guidelines, record exact version/date and do not claim it is current until that
status is verified.

### 5. Generate the bounded source skill

Create only what the source needs:

```text
generated_skills/<source-slug>/
├── SKILL.md
├── SOURCE.md
├── references/ or chapters/
└── limitations.md               # optional
```

Use:

- `templates/evidence_second_brain/SOURCE.md` for the source card;
- `templates/evidence_second_brain/REFERENCE_NOTE.md` for every source note.

`SKILL.md` must stay thin and contain:

- when this exact source is relevant;
- source identity/version, access, and review warning;
- an index to source notes;
- instructions to show source/locator and abstain when unsupported;
- limitations and `do_not_infer` boundaries;
- no copied whole-book text, no tool grants, and no hidden computation.

Every note under `references/` or `chapters/` must identify `SOURCE_NOTE`, the exact
matching `source_id`, `FULL_TEXT`, a real locator, and review state. Preserve
population, tracer, scanner, acquisition, reconstruction, correction, segmentation,
reference standard, failure cases, and other material conditions when relevant.

### 6. Validate before Hermes loads it

Run from the repository root:

```bash
python tools/validate_skill.py generated_skills/<source-slug>/SKILL.md
python tools/validate_source_skill.py generated_skills/<source-slug>
python tools/scan_generated_skill.py generated_skills/<source-slug>
```

Do not reinterpret a contract pass as factual or scientific validation. The
security scanner is advisory; every finding requires a human disposition. Stop on
unreviewed authority-changing, secret-reading, or external-transmission content.

### 7. Human spot-check and publish locally

Ask the owner to spot-check source/locator agreement at the beginning, middle, and
end of the bounded scope, plus every equation/threshold and at least one
limitation/failure statement that will be tested. Change `review_state` only for
notes actually checked.

After checks, report:

- output directory and skill name;
- source ID, hash, access level, version, and review state;
- validation/security results and human-review status;
- known extraction/locator/bibliography limitations;
- the next MIA PoC gate.

Start a fresh Hermes session when the installed version does not refresh changed
skills automatically, then verify the intended skill is discovered and inbox notes
are not.

## Answer-use rules for generated source skills

When Hermes later uses a generated source skill:

1. retrieve the exact source note rather than answering from the skill description;
2. show access level and cite source plus locator for each material claim;
3. distinguish source fact, guideline recommendation, general knowledge, and Hermes
   interpretation;
4. expose disagreement and scope conditions;
5. abstain when the source notes do not support the request;
6. do not use a source skill as a calculator or generate quantitative run results;
7. separate feasibility, technical validity, diagnostic accuracy, clinical utility,
   and patient outcome.

## Stop conditions

Stop, record `BLOCKED`, and ask the owner when:

- source identity, full-text access, rights, or destination is unclear;
- necessary Methods/Results/tables/supplements/limitations/failures cannot be
  inspected for the requested claim;
- real locators cannot be preserved;
- an existing skill would be silently overwritten;
- multiple sources would be collapsed into one truth;
- generated content attempts to alter agent/tool authority or transmit sensitive
  content;
- patient data, clinical systems, or an unapproved external index enters scope;
- the requested conclusion exceeds the source or completed validation layer.

## Example requests

```text
/medical-book-to-skill สร้าง source skill จาก PET physics textbook PDF นี้ตาม
PoC-K002 โดยจำกัด scope ที่ count statistics และ reconstruction พร้อม source hash,
chapter/page locator, limitations และ do-not-infer
```

```text
/medical-book-to-skill นำ guideline ฉบับนี้เข้าเป็น source skill แยกจาก textbook
เดิม ตรวจ full Methods/appendix ที่เกี่ยวข้อง และห้ามเรียกว่า current guideline
จนกว่าจะยืนยัน version/date
```
