"""Keep fork identity and the cross-repository source-skill contract explicit."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fork_install_surfaces_point_to_medical_extension_repo() -> None:
    fork_url = "https://github.com/attaponjantarato-maker/book-to-skill"
    for relative in ("README.md", "docs/install.md", "docs/index.md", "CONTRIBUTING.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert fork_url in text, relative
    assert "Medical/Hermes experimental fork" in (ROOT / "README.md").read_text(
        encoding="utf-8"
    )


def test_upstream_custom_domain_deployment_is_disabled() -> None:
    assert not (ROOT / "docs/CNAME").exists()
    workflow = (ROOT / ".github/workflows/deploy-docs.yml").read_text(encoding="utf-8")
    assert "mkdocs gh-deploy" not in workflow
    assert "contents: read" in workflow
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "booktoskill.is-a.dev" not in mkdocs


def test_source_skill_contract_declares_quarantine_and_promotion_gate() -> None:
    contract = (ROOT / "contracts/source-skill-contract.yaml").read_text(encoding="utf-8")
    assert 'schema_version: "1.1.0"' in contract
    assert "scanner_scope: all_regular_utf8_text_files" in contract
    assert "staging_root: .skill_staging" in contract
    assert "promotion_gate: tools/promote_generated_skill.py" in contract

    factory = (ROOT / "hermes/skills/medical-book-to-skill/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "Never generate directly under `generated_skills/`" in factory
    assert "--check-only" in factory
    assert "PROMOTION_APPROVAL.example.json" in factory
