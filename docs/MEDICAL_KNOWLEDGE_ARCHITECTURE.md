# Medical Knowledge Architecture v0.2

This fork extends Book-to-Skill with an evidence-labelled medical knowledge layer
while keeping the upstream extraction pipeline intact.

`source-derived` means traceably derived from an identified source. It does not
mean verified, current, scientifically validated, or clinically approved.

## Design goals

1. Preserve source identity, exact-file hash, access level, version/edition, and
   chapter/section/page or other real locators.
2. Separate source notes, synthesis, project context, orchestration, and
   deterministic computation.
3. Prevent limited-access material from becoming an installed source skill.
4. Prevent a textbook/manual from being promoted to current clinical guidance
   outside its authority scope.
5. Keep one source per source skill during the PoC and expose disagreement.
6. Treat retrieved document text as untrusted data rather than agent instruction.
7. Keep structural/policy checks deterministic and testable while stating clearly
   what they do not validate.

## Knowledge classes

| Class | Meaning | Default use policy |
|---|---|---|
| A — Fundamental | Stable physics/mathematics and core mechanisms | May support explanation/reasoning when provenance is valid |
| B — Technical | Scanner/software/reconstruction/quantification/QC implementation knowledge | Requires relevant version and project context for implementation decisions |
| C — Clinical | Protocol, administered activity, preparation, diagnostic criteria, thresholds, or therapy eligibility | Requires a current guideline or approved local SOP before being presented as current practice |

The deterministic topic classifier is conservative: when a knowledge unit spans
multiple topics, the most restrictive class wins (`C > B > A`). This is a use-policy
classification, not an evidence-quality score.

## Evidence access is separate from knowledge class

Every source is labelled `FULL_TEXT`, `ABSTRACT_ONLY`, `SEARCH_SNIPPET`, or
`SECONDARY_SOURCE`.

Only `FULL_TEXT` may become an installed evidence-aware source skill in PoC-K002.
The other levels may be retained as discovery pointers under `_notes/inbox/`
without `SKILL.md`. Abstracts/snippets must not be used alone to reconstruct a
calculation, protocol, diagnostic accuracy estimate, implementation requirement,
or clinical readiness claim.

Full-text access does not establish evidence quality or currency. Source suitability
depends on the question:

| Question | Usually preferred authority |
|---|---|
| Exact operation of a scanner/software version | Matching manufacturer manual or technical documentation |
| Current clinical protocol/recommendation | Current professional guideline/consensus and approved local SOP |
| Fundamental physics | Authoritative textbook/standard plus relevant primary evidence when needed |
| Diagnostic accuracy or patient outcome | Appropriate primary studies and systematic review/meta-analysis |
| Method implementation from a paper | Full Methods/equations/supplement plus reported validation and failures |
| Local operational practice | Approved local SOP, explicitly labelled as local policy |

This is not one universal ranking. A manual may be authoritative for a software
button but not for clinical utility; a textbook may explain physics well but be
outdated for a current protocol.

## Source skill, synthesis candidate, and project notes

A source skill represents what one source says. It must not silently merge another
source, owner interpretation, or model knowledge.

```text
Source A → Source Skill A ─┐
Source B → Source Skill B ─┼→ Synthesis candidate + disagreement record
Source C → Source Skill C ─┘
```

Canonical synthesis is deferred. A synthesis candidate must link every input and
preserve scope, version, population, tracer, scanner, acquisition, reconstruction,
reference standard, limitations, exclusions, and failure cases when relevant.

Project-specific data locations, hypotheses, scanner settings, analysis decisions,
and local run state belong in the sibling Molecular Imaging Assistant project, not
inside a reusable source skill.

## Evidence-aware pipeline

```text
AUTHORIZED LOCAL SOURCE
        ↓
upstream extraction + sanitization
        ↓
extraction/locator QC
        ↓
one evidence-labelled source skill
        ↓
source-contract validation + generated-content security review
        ↓
Hermes skill discovery
        ↓
baseline metadata/text retrieval
        ↓ only after measured gap
optional rebuildable RAG index
```

See `docs/EVIDENCE_AWARE_SECOND_BRAIN.md` for component authority and retrieval
rules, and `docs/POC_K002_RUNBOOK.md` for execution gates.

## Generated source-skill contract

Minimum PoC layout:

```text
<source-skill>/
├── SKILL.md
├── SOURCE.md
├── references/ or chapters/
└── limitations.md              # optional
```

- `SKILL.md` is a thin behavioral interface and navigation index.
- `SOURCE.md` records source identity, access, hash, authority scope, review state,
  and bibliography-verification state.
- every note under `references/` or `chapters/` records `SOURCE_NOTE`, matching
  `source_id`, `FULL_TEXT`, a real locator, and its review state.
- quantitative computation remains outside the skill.

Start from `templates/evidence_second_brain/` and validate with:

```bash
python tools/validate_skill.py generated_skills/<source-slug>/SKILL.md
python tools/validate_source_skill.py generated_skills/<source-slug>
python tools/scan_generated_skill.py generated_skills/<source-slug>
```

Passing these checks establishes structural completeness and known-pattern
screening only. It does not validate factual truth, scientific performance, source
quality, guideline currency, diagnostic accuracy, clinical utility, or patient
outcome.

## Use-policy behavior

The medical Python layer supports:

- explicit `SourceProvenance` and `MedicalKnowledgeUnit` structures;
- deterministic A/B/C topic classification;
- structural provenance validation;
- technical project-context warnings/gates;
- current-authority warnings/gates for clinical material;
- time-sensitive knowledge warnings/gates;
- `ADVISORY` and optional `STRICT` policy modes.

Default personal-research policy remains `ADVISORY`, but malformed provenance is a
structural error in every mode. The evidence-aware source-skill validator is a
separate PoC publishing gate and requires full text, a real source hash, and real
locators.

## Implementation status

Implemented:

- upstream deterministic extraction and sanitization;
- medical provenance models, classification, and advisory/strict policy checks;
- Hermes factory skill and external skill-directory integration documentation;
- generated-content scanner covering `SKILL.md`, `SOURCE.md`, supporting files,
  and Markdown under chapters/references/concepts/equations/limitations/provenance;
- standard-library validator for the PoC source-card and source-note contract;
- templates and PoC-K002 runbook.

Not yet implemented or validated:

- automatic conversion from extractor output into the complete medical source-skill
  contract without agent generation;
- automatic comparison of every note against the original PDF page;
- automated DOI/PMID/correction/retraction verification;
- guideline freshness retrieval;
- Obsidian-specific plugin or API integration;
- a search/RAG implementation or index schema;
- canonical multi-source synthesis;
- scientific or clinical validation of the complete system.

Hermes integration currently means skill-directory discovery and a factory skill.
There is no Book-to-Skill MCP, and PoC-K002 does not require one.

## Validation layers and claim limits

Keep these conclusions separate:

1. **Feasibility:** the document can be processed and the skill discovered.
2. **Structural/technical validity:** source IDs, hashes, locators, retrieval, and
   citation grounding work for the tested cases.
3. **Diagnostic accuracy:** requires an appropriate population and reference
   standard; not supplied by this pipeline.
4. **Clinical utility:** requires evidence that use improves a clinical decision or
   workflow; not supplied by this pipeline.
5. **Patient outcome:** not evaluated.

The maximum status after the current runbook is `WORKS_FOR_POC` for the exact source,
configuration, and prespecified questions tested.

The generated content should remain private/internal unless the source license
permits redistribution.
