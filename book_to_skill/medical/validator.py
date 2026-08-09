from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from .models import IntendedUse, KnowledgeClass, MedicalKnowledgeUnit, SourceType
from .policy import PolicyMode


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
    """Optional context available when a knowledge unit is used."""

    current_guideline_verified: bool = False
    local_sop_verified: bool = False
    project_context_verified: bool = False


@dataclass(frozen=True)
class UseDecision:
    allowed: bool
    issues: Tuple[ValidationIssue, ...] = field(default_factory=tuple)


def validate_unit(unit: MedicalKnowledgeUnit) -> Tuple[ValidationIssue, ...]:
    """Validate structural integrity of a knowledge unit.

    Structural failures remain errors in every policy mode because a knowledge
    object without an id, statement, or source locator cannot be traced or used
    reliably even in an experimental workflow.
    """

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


def _policy_severity(policy_mode: PolicyMode) -> Severity:
    return Severity.ERROR if policy_mode is PolicyMode.STRICT else Severity.WARNING


def evaluate_use(
    unit: MedicalKnowledgeUnit,
    intended_use: IntendedUse,
    context: VerificationContext = VerificationContext(),
    policy_mode: PolicyMode = PolicyMode.ADVISORY,
) -> UseDecision:
    """Evaluate a knowledge unit for a proposed use.

    The default is ADVISORY for personal research and experimentation. In that
    mode, technical/clinical caveats are surfaced as warnings but do not block
    use. STRICT promotes the same policy findings to errors.
    """

    issues = list(validate_unit(unit))
    policy_severity = _policy_severity(policy_mode)

    if unit.knowledge_class is KnowledgeClass.TECHNICAL:
        if (
            intended_use is IntendedUse.IMPLEMENTATION_DECISION
            and not context.project_context_verified
        ):
            issues.append(
                ValidationIssue(
                    "technical_context_recommended",
                    "Scanner/software/project context is recommended before applying technical knowledge to an implementation decision.",
                    severity=policy_severity,
                )
            )

    if unit.knowledge_class is KnowledgeClass.CLINICAL:
        if intended_use is IntendedUse.CURRENT_CLINICAL_RECOMMENDATION:
            if not (context.current_guideline_verified or context.local_sop_verified):
                issues.append(
                    ValidationIssue(
                        "current_authority_recommended",
                        "A current guideline or local SOP is recommended when treating clinical/protocol knowledge as current practice.",
                        severity=policy_severity,
                    )
                )

            if (
                unit.provenance.source_type is SourceType.TEXTBOOK
                and not context.current_guideline_verified
            ):
                issues.append(
                    ValidationIssue(
                        "textbook_may_be_outdated",
                        "The source is a textbook; current practice may differ from the edition being used.",
                        severity=policy_severity,
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
                    "time_sensitive_check_recommended",
                    "This knowledge is marked time-sensitive; checking current context is recommended.",
                    severity=policy_severity,
                )
            )

    allowed = not any(issue.severity is Severity.ERROR for issue in issues)
    return UseDecision(allowed=allowed, issues=tuple(issues))
