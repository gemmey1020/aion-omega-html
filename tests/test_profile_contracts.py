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


def test_profile_representation_affinities_use_existing_stable_ids():
    catalog_ids = {
        json.loads(line)["id"]
        for line in (ROOT / "index/catalog.ndjson").read_text(encoding="utf-8").splitlines()
    }
    for path in PROFILES.glob("*.json"):
        profile = read_json(path)
        affinities = profile["representation_affinity"]
        assert isinstance(affinities, list), path.name
        assert set(affinities) <= catalog_ids, path.name


def test_profiles_define_contextual_treatments_for_their_native_work():
    profiles = {read_json(path)["id"]: read_json(path) for path in PROFILES.glob("*.json")}
    for profile in profiles.values():
        assert isinstance(profile.get("contextual_treatments"), dict), profile["id"]

    prime = profiles["prime"]["contextual_treatments"]["founder_strategy"]
    assert prime["rhythm"] == "open_editorial"
    assert prime["density"]["panel_density"] == "low"

    gold = profiles["gold"]["contextual_treatments"]["external_client"]
    assert gold["rhythm"] == "executive_editorial"
    assert gold["print_aware"] is True

    assert "audit_evidence" in profiles["silver"]["contextual_treatments"]
    assert "architecture_systems" in profiles["cyan"]["contextual_treatments"]


def test_composition_archetypes_expose_structured_rhythm_guidance():
    knowledge = read_json(ROOT / "knowledge/composition-archetypes.json")
    archetypes = knowledge["archetypes"]
    assert {item["id"] for item in archetypes} == EXPECTED_ARCHETYPES
    required_fields = {
        "id",
        "opening_tendencies",
        "rhythm",
        "density",
        "transition_tendencies",
        "family_affinity",
        "avoid",
    }
    for item in archetypes:
        assert required_fields <= item.keys(), item.get("id")


def test_capability_guidance_covers_cost_accessibility_offline_and_families():
    knowledge = read_json(ROOT / "knowledge/capabilities.json")
    assert knowledge["default"] == "HTML/CSS"
    required_fields = {"use_when", "avoid_when", "complexity", "accessibility", "offline", "best_families"}
    for capability, details in knowledge["capabilities"].items():
        assert required_fields <= details.keys(), capability
        assert isinstance(details["best_families"], list), capability


def test_learning_protocol_encodes_authority_and_exact_founder_choices():
    protocol = read_json(ROOT / "knowledge/learning-protocol.json")
    expected_authorities = {
        "founder_explicit",
        "founder_approved",
        "repeated_observation",
        "agent_inference",
    }
    assert set(protocol["authority_classes"]) == expected_authorities
    assert protocol["authority_classes"]["agent_inference"]["destination"] == "candidate_only"
    labels = {item["label"] for item in protocol["conflict_resolutions"]}
    assert labels == {"KEEP OLD", "OVERRIDE", "SCOPE SPLIT", "ONE-OFF EXCEPTION"}


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
