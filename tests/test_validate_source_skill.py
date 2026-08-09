"""Tests for the evidence-aware medical source-skill contract."""

import importlib.util
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
spec = importlib.util.spec_from_file_location(
    "validate_source_skill",
    TOOLS_DIR / "validate_source_skill.py",
)
validator = importlib.util.module_from_spec(spec)
sys.modules["validate_source_skill"] = validator
spec.loader.exec_module(validator)


SOURCE_HASH = "a" * 64


def _write_source_skill(root: Path) -> Path:
    references = root / "references"
    references.mkdir(parents=True)
    (root / "SKILL.md").write_text(
        """---
name: pet-reference
description: A traceable PET source skill.
---

# PET Reference
""",
        encoding="utf-8",
    )
    (root / "SOURCE.md").write_text(
        f"""---
schema_version: "1.0"
artifact_kind: SOURCE_SKILL
status: SOURCE_DERIVED_POC
source_id: pet-reference-2026
source_title: "Example PET Reference"
source_type: textbook
source_version_or_edition: "2"
publication_date: "2026"
access_level: FULL_TEXT
locator_types: chapter|section|page
bibliography_verified: false
doi: unknown
pmid: unknown
source_file_hash_sha256: {SOURCE_HASH}
review_state: AI_EXTRACTED_UNREVIEWED
authority_scope: "Foundational PET concepts in the cited sections"
redistribution_allowed: false
generated_at: "2026-08-09"
generator_version: test-fixture
---

# Source Card
""",
        encoding="utf-8",
    )
    (references / "chapter-01.md").write_text(
        """---
note_kind: SOURCE_NOTE
source_id: pet-reference-2026
access_level: FULL_TEXT
locator: "Chapter 1, section 1.2, p. 12"
review_state: AI_EXTRACTED_UNREVIEWED
---

# Chapter 1

Example source-derived content.
""",
        encoding="utf-8",
    )
    return root


def test_valid_source_skill_passes(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "pet-reference")

    assert validator.validate_source_skill(skill) == []


def test_limited_access_cannot_be_installed_as_source_skill(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "abstract-reference")
    source = skill / "SOURCE.md"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "access_level: FULL_TEXT", "access_level: ABSTRACT_ONLY", 1
        ),
        encoding="utf-8",
    )

    errors = validator.validate_source_skill(skill)

    assert any("requires FULL_TEXT" in error for error in errors)


def test_source_hash_is_required_for_traceability(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "unhashed-reference")
    source = skill / "SOURCE.md"
    source.write_text(
        source.read_text(encoding="utf-8").replace(SOURCE_HASH, "unknown"),
        encoding="utf-8",
    )

    errors = validator.validate_source_skill(skill)

    assert any("source_file_hash_sha256" in error for error in errors)


def test_reference_source_id_must_match_source_card(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "mismatched-reference")
    note = skill / "references" / "chapter-01.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            "source_id: pet-reference-2026", "source_id: another-source"
        ),
        encoding="utf-8",
    )

    errors = validator.validate_source_skill(skill)

    assert any("source_id does not match" in error for error in errors)


def test_reference_note_requires_a_real_locator(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "unlocated-reference")
    note = skill / "references" / "chapter-01.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            'locator: "Chapter 1, section 1.2, p. 12"', "locator: unknown"
        ),
        encoding="utf-8",
    )

    errors = validator.validate_source_skill(skill)

    assert any("locator must point back" in error for error in errors)


def test_source_skill_rejects_symlinked_source_card(tmp_path: Path):
    skill = _write_source_skill(tmp_path / "symlink-reference")
    external = tmp_path / "external-source.md"
    external.write_text("# External\n", encoding="utf-8")
    source = skill / "SOURCE.md"
    source.unlink()
    try:
        source.symlink_to(external)
    except OSError:
        return

    try:
        validator.validate_source_skill(skill)
    except validator.ContractError as exc:
        assert "SOURCE.md is missing or is a symbolic link" in str(exc)
    else:
        raise AssertionError("symlinked SOURCE.md should fail closed")


def test_cli_states_that_contract_pass_is_not_scientific_validation(
    tmp_path: Path, capsys
):
    skill = _write_source_skill(tmp_path / "cli-reference")

    assert validator.main([str(skill)]) == 0
    output = capsys.readouterr().out
    assert "does not establish scientific validity" in output
