#!/usr/bin/env python3
"""Validate and atomically promote one staged medical source skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence


TOOLS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_ROOT))
import scan_generated_skill as scanner  # noqa: E402
import validate_skill  # noqa: E402
import validate_source_skill  # noqa: E402


REPO_ROOT = TOOLS_ROOT.parent
STAGING_ROOT = REPO_ROOT / ".skill_staging"
GENERATED_ROOT = REPO_ROOT / "generated_skills"
MAX_APPROVAL_BYTES = 256 * 1024
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")


class PromotionError(RuntimeError):
    """Raised when a staged candidate cannot be promoted safely."""


@dataclass(frozen=True)
class CandidateAudit:
    candidate_sha256: str
    scanner_fingerprints: tuple[str, ...]
    skill_warning_fingerprints: tuple[str, ...]


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _fingerprint(*parts: object) -> str:
    digest = hashlib.sha256()
    for part in parts:
        encoded = str(part).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def scanner_finding_fingerprint(finding: scanner.Finding) -> str:
    return _fingerprint(finding.path, finding.line, finding.rule_id, finding.message)


def skill_warning_fingerprint(warning: str) -> str:
    return _fingerprint("validate_skill", warning)


def _candidate_hash(root: Path, files: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        if path.is_symlink():
            raise PromotionError("candidate changed to a symbolic link during audit")
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _resolve_staged_candidate(path: Path, target_slug: str) -> Path:
    if not SLUG_PATTERN.fullmatch(target_slug):
        raise PromotionError("target slug must be a lowercase hyphenated name of 3-64 characters")
    if not STAGING_ROOT.exists() or STAGING_ROOT.is_symlink():
        raise PromotionError(".skill_staging must be an existing real directory")
    staging_root = STAGING_ROOT.resolve(strict=True)
    requested = path.expanduser()
    if requested.is_symlink():
        raise PromotionError("staged candidate must not be a symbolic link")
    try:
        candidate = requested.resolve(strict=True)
    except OSError as exc:
        raise PromotionError("staged candidate does not exist") from exc
    if not candidate.is_dir() or not _is_within(candidate, staging_root):
        raise PromotionError("staged candidate must be a directory under .skill_staging")
    if candidate == staging_root or candidate.name != target_slug:
        raise PromotionError("staged directory name must match the target slug")
    return candidate


def audit_staged_candidate(path: Path, target_slug: str) -> CandidateAudit:
    candidate = _resolve_staged_candidate(path, target_slug)
    try:
        findings = scanner.scan_generated_skill(candidate)
        source_errors = validate_source_skill.validate_source_skill(candidate)
        skill_errors, skill_warnings = validate_skill.audit(
            str(candidate / "SKILL.md"), lens="claude"
        )
        files = scanner._collect_skill_files(candidate)
    except (
        OSError,
        scanner.ScanError,
        validate_source_skill.ContractError,
    ) as exc:
        raise PromotionError(f"candidate audit could not complete: {exc}") from exc

    validation_errors = [*skill_errors, *source_errors]
    if validation_errors:
        raise PromotionError("candidate validation failed: " + " | ".join(validation_errors))

    try:
        candidate_hash = _candidate_hash(candidate, files)
    except OSError as exc:
        raise PromotionError("candidate changed or became unreadable during audit") from exc
    return CandidateAudit(
        candidate_sha256=candidate_hash,
        scanner_fingerprints=tuple(
            sorted(scanner_finding_fingerprint(finding) for finding in findings)
        ),
        skill_warning_fingerprints=tuple(
            sorted(skill_warning_fingerprint(warning) for warning in skill_warnings)
        ),
    )


def _read_approval(path: Path, candidate: Path) -> dict[str, object]:
    requested = path.expanduser()
    if requested.is_symlink():
        raise PromotionError("approval receipt must not be a symbolic link")
    try:
        approval = requested.resolve(strict=True)
    except OSError as exc:
        raise PromotionError("approval receipt does not exist") from exc
    staging_root = STAGING_ROOT.resolve(strict=True)
    if not approval.is_file() or not _is_within(approval, staging_root):
        raise PromotionError("approval receipt must be a file under .skill_staging")
    if _is_within(approval, candidate):
        raise PromotionError("approval receipt must be outside the candidate directory")
    if approval.stat().st_size > MAX_APPROVAL_BYTES:
        raise PromotionError("approval receipt exceeds the size limit")
    try:
        payload = json.loads(approval.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PromotionError("approval receipt must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise PromotionError("approval receipt root must be an object")
    return payload


def _validate_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _validate_acknowledgements(
    value: object,
    expected: tuple[str, ...],
    *,
    disposition: str,
    label: str,
) -> None:
    if not isinstance(value, list):
        raise PromotionError(f"{label} acknowledgements must be an array")
    fingerprints: list[str] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {
            "fingerprint",
            "disposition",
            "rationale",
        }:
            raise PromotionError(f"each {label} acknowledgement has invalid fields")
        if item["disposition"] != disposition:
            raise PromotionError(f"each {label} disposition must be {disposition}")
        if not isinstance(item["rationale"], str) or not item["rationale"].strip():
            raise PromotionError(f"each {label} acknowledgement requires a rationale")
        if not isinstance(item["fingerprint"], str):
            raise PromotionError(f"each {label} fingerprint must be a string")
        fingerprints.append(item["fingerprint"])
    if tuple(sorted(fingerprints)) != expected or len(fingerprints) != len(set(fingerprints)):
        raise PromotionError(f"{label} acknowledgements must exactly match the current audit")


def _validate_approval(
    payload: dict[str, object],
    audit: CandidateAudit,
    target_slug: str,
) -> None:
    expected_fields = {
        "schema_version",
        "approved",
        "approved_by",
        "approved_at",
        "target_slug",
        "candidate_sha256",
        "spot_checks",
        "scanner_findings",
        "skill_validator_warnings",
    }
    if set(payload) != expected_fields:
        raise PromotionError("approval receipt fields do not match schema version 1.0")
    if payload["schema_version"] != "1.0" or payload["approved"] is not True:
        raise PromotionError("approval receipt must explicitly approve schema version 1.0")
    if payload["target_slug"] != target_slug:
        raise PromotionError("approval target_slug does not match the requested target")
    if payload["candidate_sha256"] != audit.candidate_sha256:
        raise PromotionError("candidate changed after approval or the approval hash is incorrect")
    if not isinstance(payload["approved_by"], str) or not payload["approved_by"].strip():
        raise PromotionError("approval receipt requires approved_by")
    if not _validate_timestamp(payload["approved_at"]):
        raise PromotionError("approval receipt requires a timezone-aware approved_at timestamp")

    spot_checks = payload["spot_checks"]
    required_checks = {
        "beginning",
        "middle",
        "end",
        "equations_and_thresholds",
        "limitation_or_failure",
    }
    if not isinstance(spot_checks, dict) or set(spot_checks) != required_checks:
        raise PromotionError("approval receipt has incomplete spot-check fields")
    for required_pass in ("beginning", "middle", "end", "limitation_or_failure"):
        if spot_checks[required_pass] != "PASS":
            raise PromotionError(f"spot check {required_pass} must be PASS")
    if spot_checks["equations_and_thresholds"] not in {"PASS", "NOT_APPLICABLE"}:
        raise PromotionError("equations_and_thresholds must be PASS or NOT_APPLICABLE")

    _validate_acknowledgements(
        payload["scanner_findings"],
        audit.scanner_fingerprints,
        disposition="ACCEPTED_FALSE_POSITIVE",
        label="scanner finding",
    )
    _validate_acknowledgements(
        payload["skill_validator_warnings"],
        audit.skill_warning_fingerprints,
        disposition="ACKNOWLEDGED",
        label="skill validator warning",
    )


def promote_staged_skill(
    staged_path: Path,
    *,
    target_slug: str,
    approval_path: Path,
) -> Path:
    candidate = _resolve_staged_candidate(staged_path, target_slug)
    audit = audit_staged_candidate(candidate, target_slug)
    approval = _read_approval(approval_path, candidate)
    _validate_approval(approval, audit, target_slug)

    if not GENERATED_ROOT.is_dir() or GENERATED_ROOT.is_symlink():
        raise PromotionError("generated_skills must be an existing real directory")
    generated_root = GENERATED_ROOT.resolve(strict=True)
    target = generated_root / target_slug
    if target.exists() or target.is_symlink():
        raise PromotionError("target already exists; promotion is no-clobber")
    if candidate.stat().st_dev != generated_root.stat().st_dev:
        raise PromotionError("staging and generated_skills must be on the same filesystem")

    lock_path = generated_root / f".{target_slug}.promotion.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise PromotionError("another promotion holds the target lock") from exc
    try:
        os.write(descriptor, audit.candidate_sha256.encode("ascii"))
        os.fsync(descriptor)
        if target.exists() or target.is_symlink():
            raise PromotionError("target appeared during promotion; refusing to replace it")
        os.rename(candidate, target)
    except OSError as exc:
        raise PromotionError(f"atomic promotion failed: {exc}") from exc
    finally:
        os.close(descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
    return target


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("staged_path", type=Path)
    parser.add_argument("target_slug")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        audit = audit_staged_candidate(args.staged_path, args.target_slug)
        if args.check_only:
            print(json.dumps(audit.__dict__, indent=2))
            return 0
        if args.approval is None:
            raise PromotionError("--approval is required unless --check-only is used")
        target = promote_staged_skill(
            args.staged_path,
            target_slug=args.target_slug,
            approval_path=args.approval,
        )
    except PromotionError as exc:
        print(f"ERROR promotion blocked: {exc}", file=sys.stderr)
        return 1

    print(f"Promoted approved source skill to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
