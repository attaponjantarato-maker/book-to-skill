from book_to_skill.medical import (
    IntendedUse,
    KnowledgeClass,
    KnowledgeTopic,
    MedicalKnowledgeUnit,
    PolicyMode,
    Severity,
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
    issues = validate_unit(unit)
    codes = {issue.code for issue in issues}
    assert "missing_source_locator" in codes
    assert any(issue.severity is Severity.ERROR for issue in issues)


def test_personal_research_mode_warns_but_does_not_block_textbook_protocol():
    unit = _unit(
        klass=KnowledgeClass.CLINICAL,
        topics=[KnowledgeTopic.PROTOCOL],
        time_sensitive=True,
    )
    decision = evaluate_use(unit, IntendedUse.CURRENT_CLINICAL_RECOMMENDATION)
    codes = {issue.code for issue in decision.issues}
    assert decision.allowed is True
    assert "current_authority_recommended" in codes
    assert "textbook_may_be_outdated" in codes
    assert "time_sensitive_check_recommended" in codes
    assert all(issue.severity is Severity.WARNING for issue in decision.issues)


def test_strict_mode_can_block_unverified_textbook_protocol():
    unit = _unit(
        klass=KnowledgeClass.CLINICAL,
        topics=[KnowledgeTopic.PROTOCOL],
        time_sensitive=True,
    )
    decision = evaluate_use(
        unit,
        IntendedUse.CURRENT_CLINICAL_RECOMMENDATION,
        policy_mode=PolicyMode.STRICT,
    )
    assert decision.allowed is False
    assert any(issue.severity is Severity.ERROR for issue in decision.issues)


def test_current_guideline_context_removes_clinical_policy_findings():
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
    assert decision.issues == ()


def test_personal_research_mode_warns_but_allows_technical_implementation():
    unit = _unit(
        klass=KnowledgeClass.TECHNICAL,
        topics=[KnowledgeTopic.RECONSTRUCTION_PARAMETER],
    )
    decision = evaluate_use(unit, IntendedUse.IMPLEMENTATION_DECISION)
    assert decision.allowed is True
    assert "technical_context_recommended" in {
        issue.code for issue in decision.issues
    }
    assert all(issue.severity is Severity.WARNING for issue in decision.issues)


def test_strict_mode_blocks_technical_implementation_without_context():
    unit = _unit(
        klass=KnowledgeClass.TECHNICAL,
        topics=[KnowledgeTopic.RECONSTRUCTION_PARAMETER],
    )
    decision = evaluate_use(
        unit,
        IntendedUse.IMPLEMENTATION_DECISION,
        policy_mode=PolicyMode.STRICT,
    )
    assert decision.allowed is False
    assert "technical_context_recommended" in {
        issue.code for issue in decision.issues
    }


def test_technical_implementation_has_no_warning_after_project_context_check():
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
    assert decision.issues == ()
