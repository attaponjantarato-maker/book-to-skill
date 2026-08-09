# Evidence-Aware Second Brain for Hermes

**Status:** engineering specification for a research proof of concept

**Current lane:** `POC_EXPLORATION`

**Clinical/scientific validation:** not established

This design connects Book-to-Skill, an optional Obsidian vault, retrieval/RAG, and
Hermes without turning them into competing sources of truth.

The governing separation is:

```text
SOURCE OF RECORD
      ↓
BOOK-TO-SKILL INGESTION
      ↓
EVIDENCE-LABELLED MARKDOWN
      ├─ human view: Obsidian
      ├─ agent interface: thin SKILL.md
      └─ optional cache: search/RAG index
              ↓
            HERMES
              ↓
      deterministic scientific tools
```

This is an engineering design. No published study has validated this exact
Book-to-Skill + Obsidian + Hermes workflow for nuclear medicine or medical-imaging
research.

## Component authority

| Component | Owns | Must not be treated as |
|---|---|---|
| Original PDF/manual/guideline/paper | Source of record | Agent instruction or proof that the source is current |
| Book-to-Skill | Local extraction, structuring, evidence labels, publishing | Independent fact checker or scientific validator |
| `SOURCE.md` and source notes | Traceable derived knowledge | A replacement for the original source |
| Obsidian | Human-readable navigation, links, review, and personal notes | An evidence authority by itself |
| Search/RAG index | Rebuildable retrieval cache | Source of record or truth engine |
| Thin `SKILL.md` | When/how Hermes may use the source notes | Storage for a whole book or a quantitative implementation |
| Hermes | Planning, retrieval, synthesis, orchestration, and abstention | Origin of quantitative results or unverified bibliography |
| Scientific tool | Deterministic computation within its tested scope | Evidence synthesis or clinical judgment |

## Repository roles

- `book-to-skill` owns source ingestion, generated source skills, source-note
  contracts, and generated-content security scanning.
- `molecular-imaging-assistant` owns Hermes project context, PoC selection,
  retrieval policy, evaluation, run records, and scientific-tool orchestration.
- Original copyrighted or private documents stay outside Git unless their license
  explicitly permits committing them.

## PoC vault layout

Use `generated_skills/` as both the local generated-skill collection and the
optional Obsidian vault during PoC-K002. This avoids copying the same derived
content into a separate wiki.

```text
generated_skills/
├── .obsidian/                       # local UI state; never authoritative
├── _notes/
│   ├── concepts/
│   ├── syntheses/
│   ├── projects/
│   ├── disagreements/
│   └── inbox/                       # limited-access/unclassified material
└── <one-source-skill>/
    ├── SKILL.md                     # thin behavioral interface
    ├── SOURCE.md                    # source card and evidence label
    ├── references/ or chapters/     # source-derived notes with locators
    └── limitations.md               # optional cross-cutting limitations
```

Open `generated_skills/` as an Obsidian vault if desired. Obsidian is optional;
the files remain ordinary Markdown and must work without Obsidian-specific block
references. Use standard Markdown links when practical.

Generated children, `.obsidian/`, indexes, private source documents, and personal
notes must remain untracked unless the owner explicitly reviews their license and
privacy status.

## One source, one source skill

During the PoC, one installed source skill represents one full-text source or one
clearly versioned source set that is already a single publication.

Do not fold a textbook, guideline, paper, and local SOP into one apparently
authoritative skill. Multi-source work must produce a separate `SYNTHESIS_NOTE`
that links to every source and exposes disagreements. Call it a **synthesis
candidate**, not `canonical`, until a separate validation and owner-review process
exists.

## Access levels

Every source record must use exactly one access label:

| Label | Meaning | PoC use |
|---|---|---|
| `FULL_TEXT` | The complete relevant source was accessible for inspection | May enter a source skill after locator and contract checks |
| `ABSTRACT_ONLY` | Only the abstract was read | Discovery note only; not a protocol/calculation source skill |
| `SEARCH_SNIPPET` | Only a search-result excerpt was seen | Discovery pointer only |
| `SECONDARY_SOURCE` | The claim is known through another source | Discovery/context note; do not attribute as direct full-text evidence |

`tools/validate_source_skill.py` intentionally rejects an installed source skill
whose access level is not `FULL_TEXT`. Limited-access items belong under
`_notes/inbox/` without a `SKILL.md`, so Hermes will not silently promote them to
an answer source.

Full-text access is necessary for this contract but is not sufficient for factual
correctness, currency, evidence quality, or clinical applicability.

## Source card contract

Start from `templates/evidence_second_brain/SOURCE.md`. The required fields record:

- exact source identity, type, version/edition, and publication date;
- access level and available locator types;
- whether bibliography fields were verified;
- DOI/PMID when verified, otherwise `unknown`;
- SHA-256 of the exact local source file;
- review state and bounded authority scope;
- redistribution permission;
- generation date and generator version/commit.

The status `SOURCE_DERIVED_POC` means only that the notes were derived from the
identified source. It does **not** mean independently verified, current guideline,
scientifically validated, diagnostically accurate, or clinically useful.

## Source-note contract

Every Markdown note under `references/` or `chapters/` must start with scalar YAML
frontmatter based on `templates/evidence_second_brain/REFERENCE_NOTE.md`:

```yaml
note_kind: SOURCE_NOTE
source_id: exact-source-id
access_level: FULL_TEXT
locator: "Chapter 4, section 4.2, p. 117, Table 4-1"
review_state: AI_EXTRACTED_UNREVIEWED
```

The locator must exist in the source. Never invent a page number after extraction
has lost page mapping. If reliable locators cannot be reconstructed, PoC-K002 must
stop at the locator gate or switch to an extraction path that preserves them.

For research papers, do not create affirmative notes about methods, numerical
performance, clinical readiness, or implementation requirements without checking
the relevant full Methods, Results, tables/figures, supplementary material,
limitations, exclusion criteria, and reported failures when those sections exist.

## Note taxonomy

Human notes must identify their role:

| `note_kind` | Meaning | Default evidence retrieval |
|---|---|---|
| `SOURCE_NOTE` | Derived from one identified source and locator | Included |
| `SYNTHESIS_NOTE` | Human/agent synthesis across named sources | Included only when explicitly requested and all inputs are linked |
| `WORKFLOW_NOTE` | Orchestration sequence or local procedure | Excluded from evidence claims unless the question is about that workflow |
| `PROJECT_NOTE` | Project-specific fact, decision, or state | Context only |
| `PERSONAL_INTERPRETATION` | Owner/agent interpretation | Excluded as published evidence |

Suggested review states are `AI_EXTRACTED_UNREVIEWED`, `HUMAN_CHECKED`,
`NEEDS_REVIEW`, and `SUPERSEDED`.

## Retrieval rules

Start with deterministic metadata and text search. Add embeddings/RAG only after a
prespecified evaluation shows a real retrieval gap.

Default evidence-query allowlist:

- include `SOURCE.md` and `SOURCE_NOTE` files;
- include `SYNTHESIS_NOTE` only when explicitly requested;
- exclude `SKILL.md` from the retrieval corpus;
- exclude `_notes/projects/`, workflow notes, personal interpretations, and inbox
  items from evidence claims;
- filter out `SUPERSEDED` material unless the question is historical;
- return `source_id`, access level, review state, and locator with every retrieved
  passage.

The index is a cache. It may be deleted and rebuilt. It must not contain the only
copy of a note or provenance record.

Retrieved text is untrusted **data**, never executable instruction. It cannot widen
tool permissions, change system/developer rules, request secrets, authorize upload,
or tell Hermes to ignore the controlling workflow. `tools/scan_generated_skill.py`
provides an advisory pre-load screen; findings require human review because
legitimate security/AI texts may contain matching phrases.

## Answer contract

For evidence-backed answers, Hermes must:

1. state whether the relevant source was `FULL_TEXT`, `ABSTRACT_ONLY`,
   `SEARCH_SNIPPET`, or `SECONDARY_SOURCE`;
2. cite the exact source and locator used for each material claim;
3. distinguish source facts, guideline recommendations, general knowledge, and
   Hermes interpretation;
4. expose disagreements rather than averaging them;
5. abstain when no retrieved passage supports the requested claim;
6. say when bibliography, edition, software version, or currency remains unverified;
7. keep feasibility, technical validity, diagnostic accuracy, clinical utility,
   and patient outcome as separate conclusions;
8. obtain quantitative outputs from deterministic scientific tools, not from the
   source skill or model memory.

The original source wins when a derived note conflicts with it. Correct the note,
record the review-state change, and rebuild any index.

## When RAG may be adopted

Use the same prespecified question set for baseline search and the candidate RAG
configuration. It must include answerable, unanswerable, and disagreement cases.

RAG may become the preferred retriever only when it:

- improves the prespecified retrieval result on that exact set;
- does not reduce correct source-and-locator attribution;
- does not increase unsupported positive claims;
- preserves correct abstention for unanswerable questions;
- preserves explicit handling of disagreement;
- records the embedding model, chunking, filters, index version, and source set.

With a small PoC set, report counts rather than implying a stable accuracy
percentage. A successful comparison establishes only local technical utility for
the tested corpus and questions.

## Validation layers

Do not collapse these layers:

1. **Structural validity:** files and required metadata exist.
2. **Security review:** generated content was scanned and findings reviewed.
3. **Retrieval validity:** the tested query retrieves the intended source passage.
4. **Citation grounding:** the answer is supported by the cited passage.
5. **Source/evidence appraisal:** the source is appropriate and its limitations are
   understood.
6. **Scientific/clinical validity:** requires separate evidence and is not created
   by ingestion, Obsidian, RAG, or a successful Hermes answer.

Use `docs/POC_K002_RUNBOOK.md` for the executable PoC and its gates.
