# Medical Knowledge Architecture v0.1

This fork extends Book-to-Skill with a medical-domain knowledge layer while keeping the upstream extraction pipeline intact.

## Design goals

1. Preserve source provenance down to chapter/section/page when available.
2. Separate stable foundational knowledge from implementation-dependent technical knowledge and time-sensitive clinical/protocol knowledge.
3. Prevent textbook material from being promoted to a current clinical recommendation without current external verification.
4. Require scanner/software/project context before technical knowledge is used for implementation decisions.
5. Keep the medical layer deterministic and unit-testable. LLM extraction may propose knowledge units, but policy validation is code, not prompt-only behavior.

## Knowledge classes

| Class | Meaning | Default use policy |
|---|---|---|
| A — Fundamental | Stable physics/mathematics and core mechanisms | May support explanation and reasoning when provenance is valid |
| B — Technical | Scanner/software/reconstruction/quantification/QC implementation knowledge | Requires relevant project context before implementation decisions |
| C — Clinical | Protocol, administered activity, patient preparation, diagnostic criteria, thresholds, therapy eligibility | Requires current guideline or approved local SOP before current clinical recommendations |

The classifier is conservative: when a knowledge unit spans multiple topics, the most restrictive class wins (C > B > A).

## Source skill vs canonical skill

A source skill represents what one source says. It should not silently merge disagreements across books.

```text
Textbook A -> Source Skill A --\
Textbook B -> Source Skill B ----> Canonical Domain Skill (future phase)
Textbook C -> Source Skill C --/
```

Canonical synthesis is intentionally deferred until provenance, disagreement handling, and validation are tested on multiple source skills.

## Intended pipeline

```text
PDF / EPUB / DOCX
      |
      v
upstream extraction + sanitization
      |
      v
medical knowledge extraction
      |
      +--> concept / mechanism / equation / assumption
      +--> limitation / do-not-infer / use-when
      +--> source provenance
      |
      v
A/B/C classification
      |
      v
policy validation
      |
      +--> project context
      +--> current guideline / local SOP verification
      |
      v
agent-usable source skill
```

## Source precedence for operational use

The medical layer should eventually enforce the following policy at orchestration time:

1. Project-specific validated information
2. Approved local SOP
3. Current professional guideline / standard
4. Current high-quality technical evidence
5. Canonical textbook knowledge
6. Individual textbook source skill
7. Unverified model world knowledge

This is a use-policy hierarchy, not an evidence-quality score for every research question.

## v0.1 scope

Implemented now:

- `MedicalKnowledgeUnit`
- explicit source provenance
- deterministic A/B/C topic classification
- provenance validation
- technical context guard
- clinical/current-authority guard
- time-sensitive knowledge guard
- unit tests for the above rules

Not implemented yet:

- LLM prompt/schema that converts extracted chapters into knowledge units
- serialization to `manifest.yaml` / JSON
- page-level extraction validation against source PDFs
- DOI/PMID verification
- guideline retrieval
- canonical multi-book synthesis
- Hermes/MCP integration

## Proposed generated source-skill layout

```text
<source-skill>/
├── SKILL.md
├── manifest.json
├── chapters/
├── concepts/
├── equations/
├── limitations/
├── provenance/
├── glossary.md
└── cheatsheet.md
```

The generated content should remain private/internal unless the source license permits redistribution.
