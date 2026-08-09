from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class KnowledgeClass(str, Enum):
    """Epistemic/use class for medical knowledge."""

    FUNDAMENTAL = "A_fundamental"
    TECHNICAL = "B_technical"
    CLINICAL = "C_clinical"


class SourceType(str, Enum):
    TEXTBOOK = "textbook"
    GUIDELINE = "guideline"
    CONSENSUS = "consensus"
    TECHNICAL_STANDARD = "technical_standard"
    RESEARCH_PAPER = "research_paper"
    LOCAL_SOP = "local_sop"


class KnowledgeTopic(str, Enum):
    PHYSICS = "physics"
    MATHEMATICS = "mathematics"
    COUNTING_STATISTICS = "counting_statistics"
    DETECTOR_PHYSICS = "detector_physics"
    RADIATION_DECAY = "radiation_decay"
    HARDWARE_IMPLEMENTATION = "hardware_implementation"
    SOFTWARE_IMPLEMENTATION = "software_implementation"
    RECONSTRUCTION = "reconstruction"
    RECONSTRUCTION_PARAMETER = "reconstruction_parameter"
    QUANTIFICATION = "quantification"
    IMAGE_PROCESSING = "image_processing"
    QC_QA = "qc_qa"
    PROTOCOL = "protocol"
    ADMINISTERED_ACTIVITY = "administered_activity"
    PATIENT_PREPARATION = "patient_preparation"
    DIAGNOSTIC_CRITERION = "diagnostic_criterion"
    CLINICAL_THRESHOLD = "clinical_threshold"
    THERAPY_ELIGIBILITY = "therapy_eligibility"


class IntendedUse(str, Enum):
    EXPLANATION = "explanation"
    PHYSICS_REASONING = "physics_reasoning"
    IMPLEMENTATION_DECISION = "implementation_decision"
    CURRENT_CLINICAL_RECOMMENDATION = "current_clinical_recommendation"


@dataclass(frozen=True)
class SourceProvenance:
    title: str
    source_type: SourceType
    authors: Tuple[str, ...] = field(default_factory=tuple)
    edition: Optional[str] = None
    year: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None

    @property
    def has_locator(self) -> bool:
        return any(
            value not in (None, "")
            for value in (self.chapter, self.section, self.page_start)
        )


@dataclass(frozen=True)
class MedicalKnowledgeUnit:
    knowledge_id: str
    concept: str
    statement: str
    knowledge_class: KnowledgeClass
    topics: Tuple[KnowledgeTopic, ...]
    provenance: SourceProvenance
    mechanism: Optional[str] = None
    equations: Tuple[str, ...] = field(default_factory=tuple)
    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    do_not_infer: Tuple[str, ...] = field(default_factory=tuple)
    use_when: Tuple[str, ...] = field(default_factory=tuple)
    time_sensitive: bool = False
