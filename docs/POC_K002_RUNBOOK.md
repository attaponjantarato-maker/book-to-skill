# PoC-K002 — Evidence-Aware Second Brain Runbook

**Goal:** full-text source → evidence-labelled source skill → optional Obsidian
view → baseline Hermes retrieval/answer → optional RAG comparison

**Mode:** `POC_EXPLORATION`

**Initial state:** `PLANNED`

**Maximum claim:** `WORKS_FOR_POC`

This runbook is the executable knowledge PoC shared with the sibling
`molecular-imaging-assistant` repository. It must not displace PoC-001 or imply
clinical/scientific validation.

## Inputs that the owner must choose

- one locally available source that the owner is authorized to process;
- one bounded topic within that source;
- an intended use such as explanation, technical reference, or current clinical
  recommendation;
- approximately ten prespecified evaluation questions, including at least two
  unanswerable questions and one disagreement/limitation case when two sources are
  intentionally tested.

Prefer an openly licensed test document for the first run. Do not commit private
or copyrighted source text to Git.

## State machine

```text
PLANNED
  → SOURCE_REGISTERED
  → EXTRACTED
  → SOURCE_SKILL_BUILT
  → STRUCTURE_VALIDATED
  → SECURITY_REVIEWED
  → HERMES_DISCOVERED
  → BASELINE_EVALUATED
  → POC_COMPLETE
```

`RAG_EVALUATED` is an optional branch after `BASELINE_EVALUATED`. Any gate may move
to `BLOCKED`; Hermes must record the reason and stop instead of filling missing
facts from memory.

Copy `templates/evidence_second_brain/POC_K002_STATE.yaml` into the active MIA PoC
workspace and update it after each gate. Do not mark a later gate complete while an
earlier required gate is pending.

## Gate 0 — P0-Lite

Inspect only the knowledge neighborhood:

- existing generated source skills for the same source/topic/version;
- the current Hermes external skill directories;
- existing Obsidian/vault folders and search/RAG integrations;
- the Book-to-Skill extractor and medical factory skill.

Choose and record `REUSE`, `WRAP`, `BUILD_THIN`, or `DEFER`. Do not install a vector
database or create a new MCP during this pass.

**Pass:** a reasonable source-skill path is selected.

**Stop:** the source/version is ambiguous, the existing skill would be overwritten,
or the data/rights boundary is unclear.

## Gate 1 — Register the source

Before extraction, record:

- exact title, edition/version, publication date if known, and source type;
- local path or private registry identifier;
- authorization for local processing and redistribution status;
- access level;
- SHA-256 of the exact input file;
- DOI/PMID only after verification; otherwise `unknown`;
- intended authority scope and whether the material is time-sensitive.

An installed source skill requires `FULL_TEXT`. Abstracts, search snippets, and
secondary mentions may be recorded under `_notes/inbox/` without `SKILL.md`, but
cannot pass this PoC.

**Pass:** source identity, authorization, full-text access, and hash are recorded.

**Stop:** authorization is unclear, the file is incomplete, or only limited-access
text is available for protocol/calculation/performance claims.

## Gate 2 — Extract and inspect

Run the existing local extractor. Select `technical` when tables, equations, code,
or layout need preservation; otherwise use `text`.

```bash
python scripts/extract.py "<source-path>" --mode technical --install-missing ask
```

The extractor writes `full_text.txt` and `metadata.json` under its reported
temporary work directory. Inspect `metadata.json`, the beginning/end of the text,
chapter boundaries, representative tables/equations, and source locators before
generation.

For a research paper, inspect Methods, Results, tables/figures, supplementary
material, limitations, exclusion criteria, and reported failures when present
before creating affirmative technical or clinical notes.

**Pass:** extraction is readable for the bounded topic and real locators can be
preserved.

**Stop:** material sections are missing/unreadable, equations or tables needed for
the question were lost, or page/section locators cannot be mapped reliably.

## Gate 3 — Build one source skill

Invoke `/medical-book-to-skill` and create:

```text
generated_skills/<source-slug>/
├── SKILL.md
├── SOURCE.md
├── references/ or chapters/
└── limitations.md                 # only when useful
```

Start `SOURCE.md` and every reference note from the templates under
`templates/evidence_second_brain/`. `SKILL.md` must remain a thin interface: scope,
retrieval instructions, access/review warning, and do-not-infer boundaries. It must
not reproduce the whole source, grant tools, or contain quantitative computation.

Default to one source per skill. A multi-source request produces separate source
skills plus an explicitly labelled synthesis candidate.

## Gate 4 — Structural validation

Run all applicable checks from the repository root:

```bash
python tools/validate_skill.py generated_skills/<source-slug>/SKILL.md
python tools/validate_source_skill.py generated_skills/<source-slug>
python tools/scan_generated_skill.py generated_skills/<source-slug>
```

The source validator checks traceability and labels, not factual truth. The security
scanner is advisory: no findings is a clean pass; any finding requires a human to
review and record `accepted_false_positive`, `removed`, or `blocked`. Do not load a
flagged skill merely because the text came from a reputable source.

**Pass:** skill and source contracts pass, and security findings receive a recorded
human disposition.

**Stop:** missing/mismatched source IDs, missing real locators, unresolved source
hash, authority-changing content, external-upload instructions, or unreviewed
scanner findings.

## Gate 5 — Human source spot-check

Sample at least:

- one claim from the beginning, middle, and end of the bounded source scope;
- every equation or numerical threshold that will be tested;
- one limitation/failure/exclusion statement;
- bibliography identifiers if they will be displayed as verified.

Compare the note with the original source and locator. Record discrepancies and
change `review_state` only for the notes actually checked.

**Pass:** sampled notes and locators match the source, with discrepancies corrected.

**Stop:** systematic extraction drift, missing context that changes meaning, or
locators that cannot be reproduced.

## Gate 6 — Hermes discovery

Verify that Hermes is started from `molecular-imaging-assistant` and its configured
external skill directories include:

```text
book-to-skill/hermes/skills
book-to-skill/generated_skills
```

Start a fresh Hermes session if the installed version does not refresh changed
skills automatically. Confirm the exact source skill is discoverable and that a
limited-access `_notes/inbox` item is not exposed as a skill.

**Pass:** Hermes discovers the intended source skill and no unintended notes become
skills.

**Stop:** duplicate triggers, stale skill content, or unintended directory
discovery.

## Gate 7 — Baseline evaluation

Use deterministic metadata/text search first. Run the prespecified questions
without editing them after seeing results. For each answer record:

- retrieved note and locator;
- whether the source/locator supports every material positive claim;
- whether the access and review labels were shown;
- whether unanswerable questions caused abstention;
- whether disagreements/limitations were exposed;
- unsupported claims and retrieval failures.

Baseline completion requires:

- every substantive answer either cites a correct source/locator or abstains;
- zero known unsupported positive claims in the test set;
- all prespecified unanswerable cases are reported as unsupported rather than
  completed from model memory;
- all prespecified disagreement cases expose the conflict;
- failures remain visible in the result record.

Report raw counts. With approximately ten questions, do not describe the result as
a stable accuracy estimate.

## Optional Gate 8 — RAG comparison

Run only if baseline search misses semantic matches that matter to the prespecified
questions. Keep the same corpus, questions, answer policy, and evaluation fields.
Record model, chunking, filters, index version, and indexed source hashes.

Adopt RAG for this corpus only if it improves the prespecified retrieval result
without worsening source/locator correctness, unsupported claims, abstention, or
disagreement handling. Otherwise keep baseline search and record `RAG_DEFERRED` or
`RAG_REJECTED_FOR_POC`.

The index must be deletable/rebuildable and must exclude `SKILL.md`, project notes,
personal interpretations, and limited-access inbox material from evidence claims.

## Gate 9 — Closeout

Allowed final states:

- `WORKS_FOR_POC`: the bounded end-to-end path passed its local gates;
- `PARTIAL`: some gates passed but a named gap remains;
- `FAIL`: the path ran but did not meet the PoC contract;
- `BLOCKED`: a prerequisite or safety/authority condition prevented execution.

Record separately what the PoC establishes and does not establish. Even
`WORKS_FOR_POC` establishes only local feasibility, structural traceability, and
the measured retrieval/grounding behavior for the tested source and questions. It
does not establish scientific validity, diagnostic accuracy, clinical utility,
patient outcome, or general performance.

## Non-negotiable stop conditions

Hermes must stop and ask the owner or record `BLOCKED` when:

- the source or intended destination is ambiguous;
- processing or redistribution authorization is unclear;
- the source is not full text for an installed source skill;
- required sections, tables, supplements, failure cases, or locators cannot be
  inspected for the requested claim;
- a source skill would silently overwrite another source/version;
- multi-source disagreements would be collapsed into a single truth;
- generated content attempts to change agent/tool authority or transmit secrets;
- patient data or a clinical system enters scope;
- a RAG/index service would send private content outside the approved boundary;
- the requested conclusion exceeds the source or the completed validation layer.
