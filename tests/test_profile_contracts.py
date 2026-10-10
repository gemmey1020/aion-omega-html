import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "profiles"
EXPECTED_IDS = {"prime", "gold", "silver", "cyan"}
REQUIRED_FIELDS = {
    "id",
    "character",
    "gradient_grammar",
    "token_semantics",
    "density",
    "motion_budget",
    "composition_affinity",
    "representation_affinity",
    "anti_patterns",
}
EXPECTED_ARCHETYPES = {
    "executive",
    "editorial",
    "evidence-led",
    "decision-led",
    "technical",
    "architecture-led",
    "operational",
    "narrative",
    "data-first",
    "investigative",
    "hybrid",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_exactly_four_profile_manifests_exist():
    manifests = [read_json(path) for path in PROFILES.glob("*.json")]
    assert {manifest.get("id") for manifest in manifests} == EXPECTED_IDS
    assert len(manifests) == 4


def test_each_profile_manifest_has_the_contract_fields():
    for path in PROFILES.glob("*.json"):
        manifest = read_json(path)
        assert REQUIRED_FIELDS <= manifest.keys(), path.name


def test_profile_characters_are_materially_distinct():
    manifests = {read_json(path)["id"]: read_json(path) for path in PROFILES.glob("*.json")}
    assert "executive" in manifests["gold"]["character"].lower()
    assert "editorial" in manifests["gold"]["character"].lower()
    assert "hybrid" in manifests["gold"]["character"].lower()
    assert any(term in manifests["silver"]["character"].lower() for term in ("evidence", "analytical"))
    assert any(term in manifests["cyan"]["character"].lower() for term in ("technical", "systems"))


def test_prime_points_to_the_approved_seed():
    prime = read_json(PROFILES / "prime.json")
    assert prime.get("seed_reference") == "references/founder-approved/PRIME_SEED.html"


def test_profile_summary_is_recommendation_only_and_lightweight():
    summary = read_json(ROOT / "index/profile-summary.json")
    assert summary.get("recommendation_only") is True
    assert {item["id"] for item in summary.get("profiles", [])} == EXPECTED_IDS
    for item in summary["profiles"]:
        assert "gradient_grammar" not in item
        assert "token_semantics" not in item


def test_v01_composition_archetypes_are_exact():
    knowledge = read_json(ROOT / "knowledge/composition-archetypes.json")
    assert set(knowledge["archetypes"]) == EXPECTED_ARCHETYPES


def test_required_anti_patterns_are_present():
    knowledge = read_json(ROOT / "knowledge/anti-patterns.json")
    ids = {item["id"] for item in knowledge["anti_patterns"]}
    assert {
        "card-spam",
        "giant-hero-abuse",
        "fake-dashboard",
        "neon-overload",
        "repeated-3-column-layout",
        "weak-hierarchy",
        "decorative-graph",
        "mobile-hero-disaster",
    } <= ids


def test_capabilities_keep_html_css_default_and_advanced_tools_optional():
    knowledge = read_json(ROOT / "knowledge/capabilities.json")
    assert knowledge["default"] == "HTML/CSS"
    for capability in ("SVG", "Canvas", "D3", "React", "Astro"):
        assert knowledge["capabilities"][capability]["optional"] is True
