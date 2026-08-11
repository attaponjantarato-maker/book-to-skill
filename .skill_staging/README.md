# Generated-skill quarantine

The medical/Hermes factory writes new candidates to
`.skill_staging/<run-id>/<source-slug>/`. Hermes must not include this directory in
`skills.external_dirs`.

Candidate contents and approval receipts are ignored by Git. Run all validators,
record the candidate hash, complete source spot-checks, and use
`tools/promote_generated_skill.py` for the explicit no-clobber move into
`generated_skills/`. Never copy a candidate directly into the discovery path.
