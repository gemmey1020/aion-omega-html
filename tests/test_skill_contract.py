from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_skill_frontmatter_and_scope_contract():
    path = ROOT / "SKILL.md"
    assert path.is_file(), "SKILL.md must exist"
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*\n(?P<body>.*)\Z", text, re.S)
    assert match, "SKILL.md must start with YAML frontmatter"
    frontmatter = match.group("frontmatter")
    body = match.group("body")
    assert re.search(r"^name:\s*aion-omega-html\s*$", frontmatter, re.M)
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
    assert description and description.group(1).startswith("Use when")
    assert 250 <= len(body.split()) <= 500
    for required in (
        "index/profile-summary.json",
        "tools/search-catalog.py",
        "profiles/",
        "tools/render-preview.mjs",
    ):
        assert required in body
    assert re.search(r"Master.{0,30}(must not|do not|never).{0,30}(preload|loaded)", body, re.I | re.S)
    assert re.search(r"max(?:imum)?\s+2\s+(?:automatic\s+)?(?:repairs|repair rounds)", body, re.I)
    assert re.search(r"explicit profile choice.{0,80}(skip|bypass|does not require).{0,80}recommendation gate", body, re.I | re.S)
    assert re.search(r"normal generation.{0,80}corpus.{0,30}read-only", body, re.I | re.S)


def test_skill_loads_only_scoped_learning_after_profile_selection():
    body = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2]

    selected_profile = body.index("After the profile is chosen")
    learning_query = body.index("query_relevant")

    assert learning_query > selected_profile
    assert "tools/learning-store.py" in body
    assert "relevant learning" in body.lower()
    assert "origin" in body and "scope" in body and "source_generation" in body


def test_skill_gates_founder_learning_and_keeps_generation_read_only():
    body = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2]

    assert re.search(r"explicit Founder feedback.{0,160}(?:overlap|conflict).{0,100}before.{0,60}activation", body, re.I | re.S)
    assert re.search(r"agent inference.{0,60}candidate-only", body, re.I | re.S)
    assert re.search(r"potential.{0,30}direct.{0,50}conflict", body, re.I | re.S)
    for choice in ("KEEP OLD", "OVERRIDE", "SCOPE SPLIT", "ONE-OFF EXCEPTION"):
        assert choice in body
    assert re.search(r"one-off exception.{0,120}(?:generation|persistent|later generation)", body, re.I | re.S)
    assert re.search(r"normal GENERATE mode.{0,100}(?:read-only|cannot mutate).{0,80}(?:profile|profiles).{0,40}library.{0,40}canon", body, re.I | re.S)
    assert "knowledge/learning-protocol.json" in body
