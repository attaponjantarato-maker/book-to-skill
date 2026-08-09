#!/usr/bin/env python3
"""Validate the evidence labels and locators of a medical source skill.

This validator intentionally supports a small, scalar-only YAML frontmatter
contract so it can run with the Python standard library. It does not validate
whether a scientific statement is true. It checks only whether the generated
artifact is traceable enough to enter the evidence-aware PoC lane.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Mapping, Sequence


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024

REQUIRED_SOURCE_FIELDS = {
    "schema_version",
    "artifact_kind",
    "status",
    "source_id",
    "source_title",
    "source_type",
    "source_version_or_edition",
    "publication_date",
    "access_level",
    "locator_types",
    "bibliography_verified",
    "doi",
    "pmid",
    "source_file_hash_sha256",
    "review_state",
    "authority_scope",
    "redistribution_allowed",
    "generated_at",
    "generator_version",
}

REQUIRED_NOTE_FIELDS = {
    "note_kind",
    "source_id",
    "access_level",
    "locator",
    "review_state",
}

SOURCE_TYPES = {
    "textbook",
    "guideline",
    "consensus",
    "research_paper",
    "manufacturer_manual",
    "technical_standard",
    "local_sop",
    "technical_document",
    "other",
}
ACCESS_LEVELS = {
    "FULL_TEXT",
    "ABSTRACT_ONLY",
    "SEARCH_SNIPPET",
    "SECONDARY_SOURCE",
}
SOURCE_STATUSES = {
    "SOURCE_DERIVED_POC",
    "HUMAN_CHECKED",
    "SUPERSEDED",
}
REVIEW_STATES = {
    "AI_EXTRACTED_UNREVIEWED",
    "HUMAN_CHECKED",
    "NEEDS_REVIEW",
    "SUPERSEDED",
}
LOCATOR_TYPES = {"page", "chapter", "section", "figure", "table", "equation"}


class ContractError(RuntimeError):
    """Raised when the complete source-skill contract cannot be inspected."""


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        return value[1:-1]
    return value


def parse_scalar_frontmatter(path: Path) -> Mapping[str, str]:
    """Parse the bounded scalar-only frontmatter used by this PoC contract."""

    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ContractError(f"cannot stat {path.name}") from exc
    if size > MAX_FILE_BYTES:
        raise ContractError(f"{path.name} exceeds the {MAX_FILE_BYTES:,}-byte limit")
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise ContractError(f"{path.name} is not valid UTF-8") from exc
    except OSError as exc:
        raise ContractError(f"cannot read {path.name}") from exc

    if not lines or lines[0].strip() != "---":
        raise ContractError(f"{path.name} has no YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ContractError(f"{path.name} has unterminated YAML frontmatter") from exc

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_]*):\s*(.*?)\s*", line)
        if not match:
            raise ContractError(
                f"{path.name}:{line_number} must use one scalar key: value pair"
            )
        key, value = match.group(1), _unquote(match.group(2))
        if key in fields:
            raise ContractError(f"{path.name}:{line_number} duplicates {key}")
        if not value:
            raise ContractError(f"{path.name}:{line_number} leaves {key} empty")
        fields[key] = value
    return fields


def _missing(fields: Mapping[str, str], required: set[str]) -> list[str]:
    return sorted(required - fields.keys())


def _valid_boolean(value: str) -> bool:
    return value.lower() in {"true", "false"}


def _validate_source_card(fields: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    missing = _missing(fields, REQUIRED_SOURCE_FIELDS)
    if missing:
        errors.append("SOURCE.md missing field(s): " + ", ".join(missing))
        return errors

    if fields["schema_version"] != "1.0":
        errors.append("SOURCE.md schema_version must be 1.0")
    if fields["artifact_kind"] != "SOURCE_SKILL":
        errors.append("SOURCE.md artifact_kind must be SOURCE_SKILL")
    if fields["status"] not in SOURCE_STATUSES:
        errors.append("SOURCE.md status is not recognized")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["source_id"]):
        errors.append("SOURCE.md source_id must be a lowercase hyphenated slug")
    if fields["source_title"].lower() in {"unknown", "none", "null"}:
        errors.append("SOURCE.md source_title must identify the source")
    if fields["source_type"] not in SOURCE_TYPES:
        errors.append("SOURCE.md source_type is not recognized")
    if fields["access_level"] not in ACCESS_LEVELS:
        errors.append("SOURCE.md access_level is not recognized")
    elif fields["access_level"] != "FULL_TEXT":
        errors.append(
            "an installed source skill requires FULL_TEXT; limited-access material belongs in _notes/inbox without SKILL.md"
        )
    if fields["review_state"] not in REVIEW_STATES:
        errors.append("SOURCE.md review_state is not recognized")

    locator_types = {item.strip() for item in fields["locator_types"].split("|") if item.strip()}
    if not locator_types:
        errors.append("SOURCE.md locator_types must contain at least one locator type")
    elif not locator_types <= LOCATOR_TYPES:
        errors.append("SOURCE.md locator_types contains an unsupported value")

    for field in ("bibliography_verified", "redistribution_allowed"):
        if not _valid_boolean(fields[field]):
            errors.append(f"SOURCE.md {field} must be true or false")

    if not re.fullmatch(r"unknown|\d{4}(?:-\d{2}(?:-\d{2})?)?", fields["publication_date"]):
        errors.append("SOURCE.md publication_date must be unknown, YYYY, YYYY-MM, or YYYY-MM-DD")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["generated_at"]):
        errors.append("SOURCE.md generated_at must be YYYY-MM-DD")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", fields["source_file_hash_sha256"]):
        errors.append("SOURCE.md source_file_hash_sha256 must be a 64-character SHA-256")
    if fields["pmid"] != "unknown" and not fields["pmid"].isdigit():
        errors.append("SOURCE.md pmid must be unknown or numeric")
    if fields["authority_scope"].lower() in {"unknown", "none", "null"}:
        errors.append("SOURCE.md authority_scope must state what the source can support")
    return errors


def _validate_reference_note(
    path: Path,
    fields: Mapping[str, str],
    expected_source_id: str,
) -> list[str]:
    errors: list[str] = []
    missing = _missing(fields, REQUIRED_NOTE_FIELDS)
    relative_name = path.as_posix()
    if missing:
        return [f"{relative_name} missing field(s): " + ", ".join(missing)]
    if fields["note_kind"] != "SOURCE_NOTE":
        errors.append(f"{relative_name} note_kind must be SOURCE_NOTE")
    if fields["source_id"] != expected_source_id:
        errors.append(f"{relative_name} source_id does not match SOURCE.md")
    if fields["access_level"] != "FULL_TEXT":
        errors.append(f"{relative_name} access_level must be FULL_TEXT")
    if fields["review_state"] not in REVIEW_STATES:
        errors.append(f"{relative_name} review_state is not recognized")
    if fields["locator"].lower() in {"unknown", "none", "null"}:
        errors.append(f"{relative_name} locator must point back to the source")
    return errors


def validate_source_skill(path: Path) -> list[str]:
    requested = path.expanduser()
    if requested.name.lower() == "skill.md":
        requested = requested.parent
    if requested.is_symlink():
        raise ContractError("the source-skill directory must not be a symbolic link")
    try:
        root = requested.resolve(strict=True)
    except OSError as exc:
        raise ContractError("the source-skill directory does not exist") from exc
    if not root.is_dir():
        raise ContractError("the source-skill path is not a directory")

    skill_path = root / "SKILL.md"
    source_path = root / "SOURCE.md"
    for required_path in (skill_path, source_path):
        if required_path.is_symlink() or not required_path.is_file():
            raise ContractError(f"{required_path.name} is missing or is a symbolic link")

    source_fields = parse_scalar_frontmatter(source_path)
    errors = _validate_source_card(source_fields)

    note_files: list[Path] = []
    for directory_name in ("chapters", "references"):
        directory = root / directory_name
        if not directory.exists():
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise ContractError(f"{directory_name} must be a real directory")
        for note_path in sorted(directory.rglob("*.md")):
            if note_path.is_symlink():
                raise ContractError("reference notes must not be symbolic links")
            note_files.append(note_path)

    if not note_files:
        errors.append("source skill must contain at least one Markdown note in chapters/ or references/")
        return errors

    total_bytes = source_path.stat().st_size
    for note_path in note_files:
        total_bytes += note_path.stat().st_size
        if total_bytes > MAX_TOTAL_BYTES:
            raise ContractError(
                f"source-skill Markdown exceeds the {MAX_TOTAL_BYTES:,}-byte validation limit"
            )
        try:
            note_fields = parse_scalar_frontmatter(note_path)
        except ContractError as exc:
            errors.append(str(exc))
            continue
        relative_path = note_path.relative_to(root)
        errors.extend(
            _validate_reference_note(
                relative_path,
                note_fields,
                source_fields.get("source_id", ""),
            )
        )
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", help="Generated source-skill directory or SKILL.md")
    args = parser.parse_args(argv)

    try:
        errors = validate_source_skill(Path(args.path))
    except ContractError as exc:
        print(f"ERROR source-skill validation incomplete: {exc}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"  ERROR {error}")
        print(f"Source-skill contract failed: {len(errors)} error(s)")
        return 1

    print("Source-skill contract passed: provenance, access labels, and locators are structurally complete.")
    print("This does not establish scientific validity, clinical currency, or factual correctness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
