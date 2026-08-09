from typing import Iterable

from .models import KnowledgeClass, KnowledgeTopic


_FUNDAMENTAL_TOPICS = {
    KnowledgeTopic.PHYSICS,
    KnowledgeTopic.MATHEMATICS,
    KnowledgeTopic.COUNTING_STATISTICS,
    KnowledgeTopic.DETECTOR_PHYSICS,
    KnowledgeTopic.RADIATION_DECAY,
}

_TECHNICAL_TOPICS = {
    KnowledgeTopic.HARDWARE_IMPLEMENTATION,
    KnowledgeTopic.SOFTWARE_IMPLEMENTATION,
    KnowledgeTopic.RECONSTRUCTION,
    KnowledgeTopic.RECONSTRUCTION_PARAMETER,
    KnowledgeTopic.QUANTIFICATION,
    KnowledgeTopic.IMAGE_PROCESSING,
    KnowledgeTopic.QC_QA,
}

_CLINICAL_TOPICS = {
    KnowledgeTopic.PROTOCOL,
    KnowledgeTopic.ADMINISTERED_ACTIVITY,
    KnowledgeTopic.PATIENT_PREPARATION,
    KnowledgeTopic.DIAGNOSTIC_CRITERION,
    KnowledgeTopic.CLINICAL_THRESHOLD,
    KnowledgeTopic.THERAPY_ELIGIBILITY,
}


def classify_topic(topic: KnowledgeTopic) -> KnowledgeClass:
    if topic in _CLINICAL_TOPICS:
        return KnowledgeClass.CLINICAL
    if topic in _TECHNICAL_TOPICS:
        return KnowledgeClass.TECHNICAL
    if topic in _FUNDAMENTAL_TOPICS:
        return KnowledgeClass.FUNDAMENTAL
    raise ValueError("Unmapped medical knowledge topic: %s" % topic)


def classify_topics(topics: Iterable[KnowledgeTopic]) -> KnowledgeClass:
    """Return the most restrictive class represented by the topics.

    C (clinical/time-sensitive) outranks B (technical/context-dependent),
    which outranks A (fundamental/stable).
    """
    classes = {classify_topic(topic) for topic in topics}
    if not classes:
        raise ValueError("At least one knowledge topic is required")
    if KnowledgeClass.CLINICAL in classes:
        return KnowledgeClass.CLINICAL
    if KnowledgeClass.TECHNICAL in classes:
        return KnowledgeClass.TECHNICAL
    return KnowledgeClass.FUNDAMENTAL
