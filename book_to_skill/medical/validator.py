from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from .models import IntendedUse, KnowledgeClass, MedicalKnowledgeUnit, SourceType


class Severity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: Severity = Severity.ERROR


@dataclass(frozen=True)
class VerificationContext:
    """External checks completed at the point where knowledge is used."""

    current_guideline_verified: bool = False
    local_sop_verified: bool = False
    project_context_verified: bool = False


@dataclass(frozen=True)
class UseDecision:
    allowed: bool
    issues: Tuple[ValidationIssue, ...] = field(default_factory=tuple)


def validate_unit(unit: MedicalKnowledgeUnit) -> Tuple[ValidationIssue, ...]:
    issues = []
    if not unit.knowledge_id.strip():
        issues.append(ValidationIssue("missing_id", "knowledge_id is required"))
    if not unit.concept.strip():
        issues.append(ValidationIssue("missing_concept", "concept is required"))
    if not unit.statement.strip():
        issues.append(ValidationIssue("missing_statement", "statement is required"))
    if not unit.provenance.title.strip():
        issues.append(ValidationIssue("missing_source_title", "source title is required"))
    if not unit.provenance.has_locator:
        issues.append(
            ValidationIssue(
                "missing_source_locator",
                "source must include a chapter, section, or starting page",
            )
        )
    if (
        unit.provenance.page_start is not None
        and unit.provenance.page_end is not None
        and unit.provenance.page_end < unit.provenance.page_start
    ):
        issues.append(
            ValidationIssue(
                "invalid_page_range", "page_end cannot be earlier than page_start"
            )
        )
    return tuple(issues)


def evaluate_use(
    unit: MedicalKnowledgeUnit,
    intended_use: IntendedUse,
    context: VerificationContext = VerificationContext(),
) -> UseDecision:
    issues = list(validate_unit(unit))

    if unit.knowledge_class is KnowledgeClass.TECHNICAL:
        if (
            intended_use is IntendedUse.IMPLEMENTATION_DECISION
            and not context.project_context_verified
        ):
            issues.append(
                ValidationIssue(
                    "technical_context_required",
                    "Technical knowledge requires scanner/software/project context before an implementation decision.",
                )
            )

    if unit.knowledge_class is KnowledgeClass.CLINICAL:
        if intended_use is IntendedUse.CURRENT_CLINICAL_RECOMMENDATION:
            if not (context.current_guideline_verified or context.local_sop_verified):
                issues.append(
                    ValidationIssue(
                        "current_authority_required",
                        "Clinical/protocol knowledge requires a current guideline or approved local SOP before being used as a current recommendation.",
                    )
                )

            if (
                unit.provenance.source_type is SourceType.TEXTBOOK
                and not context.current_guideline_verified
            ):
                issues.append(
                    ValidationIssue(
                        "textbook_not_current_authority",
                        "A textbook may provide background but cannot by itself establish a current clinical recommendation.",
                    )
                )

    if unit.time_sensitive and intended_use in {
        IntendedUse.IMPLEMENTATION_DECISION,
        IntendedUse.CURRENT_CLINICAL_RECOMMENDATION,
    }:
        if not (
            context.current_guideline_verified
            or context.local_sop_verified
            or context.project_context_verified
        ):
            issues.append(
                ValidationIssue(
                    "time_sensitive_verification_required",
                    "Time-sensitive knowledge requires current external verification before operational use.",
                )
            )

    allowed = not any(issue.severity is Severity.ERROR for issue in issues)
    return UseDecision(allowed=allowed, issues=tuple(issues))
