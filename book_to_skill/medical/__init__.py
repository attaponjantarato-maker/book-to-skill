"""Medical-domain knowledge structures and optional validation policy."""

from .classifier import classify_topic, classify_topics
from .models import (
    IntendedUse,
    KnowledgeClass,
    KnowledgeTopic,
    MedicalKnowledgeUnit,
    SourceProvenance,
    SourceType,
)
from .policy import PolicyMode
from .validator import (
    Severity,
    UseDecision,
    ValidationIssue,
    VerificationContext,
    evaluate_use,
    validate_unit,
)

__all__ = [
    "IntendedUse",
    "KnowledgeClass",
    "KnowledgeTopic",
    "MedicalKnowledgeUnit",
    "PolicyMode",
    "Severity",
    "SourceProvenance",
    "SourceType",
    "UseDecision",
    "ValidationIssue",
    "VerificationContext",
    "classify_topic",
    "classify_topics",
    "evaluate_use",
    "validate_unit",
]
