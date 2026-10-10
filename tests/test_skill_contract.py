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
    assert re.search(r"max(?:imum)?\s+2\s+(?:automatic\s+)?repairs", body, re.I)
    assert re.search(r"explicit profile choice.{0,80}(skip|bypass|does not require).{0,80}recommendation gate", body, re.I | re.S)
    assert re.search(r"normal generation.{0,80}corpus.{0,30}read-only", body, re.I | re.S)
