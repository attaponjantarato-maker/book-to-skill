from book_to_skill.medical import (
    IntendedUse,
    KnowledgeClass,
    KnowledgeTopic,
    MedicalKnowledgeUnit,
    SourceProvenance,
    SourceType,
    VerificationContext,
    classify_topics,
    evaluate_use,
    validate_unit,
)


def _unit(*, klass, topics, source_type=SourceType.TEXTBOOK, time_sensitive=False):
    return MedicalKnowledgeUnit(
        knowledge_id="nm-test-001",
        concept="Example concept",
        statement="Example knowledge statement.",
        knowledge_class=klass,
        topics=tuple(topics),
        provenance=SourceProvenance(
            title="Example Nuclear Medicine Textbook",
            source_type=source_type,
            edition="4",
            chapter="7",
            page_start=143,
            page_end=151,
        ),
        limitations=("Example limitation",),
        do_not_infer=("Do not generalize beyond the stated conditions",),
        time_sensitive=time_sensitive,
    )


def test_fundamental_topics_classify_as_a():
    assert classify_topics(
        [KnowledgeTopic.PHYSICS, KnowledgeTopic.COUNTING_STATISTICS]
    ) is KnowledgeClass.FUNDAMENTAL


def test_technical_topic_makes_mixed_unit_class_b():
    assert classify_topics(
        [KnowledgeTopic.PHYSICS, KnowledgeTopic.RECONSTRUCTION_PARAMETER]
    ) is KnowledgeClass.TECHNICAL


def test_clinical_topic_is_most_restrictive_class():
    assert classify_topics(
        [KnowledgeTopic.QUANTIFICATION, KnowledgeTopic.ADMINISTERED_ACTIVITY]
    ) is KnowledgeClass.CLINICAL


def test_provenance_requires_source_locator():
    unit = MedicalKnowledgeUnit(
        knowledge_id="nm-test-002",
        concept="SUV",
        statement="SUV is a semiquantitative metric.",
        knowledge_class=KnowledgeClass.FUNDAMENTAL,
        topics=(KnowledgeTopic.QUANTIFICATION,),
        provenance=SourceProvenance(
            title="PET Textbook",
            source_type=SourceType.TEXTBOOK,
        ),
    )
    codes = {issue.code for issue in validate_unit(unit)}
    assert "missing_source_locator" in codes


def test_textbook_protocol_cannot_be_current_recommendation_without_verification():
    unit = _unit(
        klass=KnowledgeClass.CLINICAL,
        topics=[KnowledgeTopic.PROTOCOL],
        time_sensitive=True,
    )
    decision = evaluate_use(unit, IntendedUse.CURRENT_CLINICAL_RECOMMENDATION)
    codes = {issue.code for issue in decision.issues}
    assert decision.allowed is False
    assert "current_authority_required" in codes
    assert "textbook_not_current_authority" in codes


def test_current_guideline_verification_can_unlock_textbook_background_for_clinical_use():
    unit = _unit(
        klass=KnowledgeClass.CLINICAL,
        topics=[KnowledgeTopic.PROTOCOL],
        time_sensitive=True,
    )
    decision = evaluate_use(
        unit,
        IntendedUse.CURRENT_CLINICAL_RECOMMENDATION,
        VerificationContext(current_guideline_verified=True),
    )
    assert decision.allowed is True


def test_technical_implementation_requires_project_context():
    unit = _unit(
        klass=KnowledgeClass.TECHNICAL,
        topics=[KnowledgeTopic.RECONSTRUCTION_PARAMETER],
    )
    decision = evaluate_use(unit, IntendedUse.IMPLEMENTATION_DECISION)
    assert decision.allowed is False
    assert "technical_context_required" in {issue.code for issue in decision.issues}


def test_technical_implementation_allowed_after_project_context_check():
    unit = _unit(
        klass=KnowledgeClass.TECHNICAL,
        topics=[KnowledgeTopic.RECONSTRUCTION_PARAMETER],
    )
    decision = evaluate_use(
        unit,
        IntendedUse.IMPLEMENTATION_DECISION,
        VerificationContext(project_context_verified=True),
    )
    assert decision.allowed is True
