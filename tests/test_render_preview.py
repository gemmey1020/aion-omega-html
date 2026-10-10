import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
RENDERER = ROOT / "tools" / "render-preview.mjs"


def run_renderer(input_path, desktop_path, mobile_path, qa_json_path=None):
    assert NODE is not None, "Node.js is required for render-preview"
    command = [
        NODE,
        str(RENDERER),
        "--input",
        str(input_path),
        "--desktop",
        str(desktop_path),
        "--mobile",
        str(mobile_path),
    ]
    if qa_json_path is not None:
        command.extend(("--qa-json", str(qa_json_path)))
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def test_renderer_writes_nonempty_desktop_and_mobile_pngs(tmp_path):
    source = tmp_path / "sample.html"
    source.write_text("<!doctype html><html><body><h1>Render smoke</h1></body></html>", encoding="utf-8")
    desktop = tmp_path / "desktop.png"
    mobile = tmp_path / "mobile.png"

    result = run_renderer(source, desktop, mobile)

    assert result.returncode == 0, result.stdout + result.stderr
    assert desktop.is_file() and desktop.stat().st_size > 0
    assert mobile.is_file() and mobile.stat().st_size > 0


def test_renderer_writes_machine_readable_desktop_and_mobile_qa_receipts(tmp_path):
    source = tmp_path / "sample.html"
    source.write_text("<!doctype html><html><body><h1>Render smoke</h1></body></html>", encoding="utf-8")
    desktop = tmp_path / "desktop.png"
    mobile = tmp_path / "mobile.png"
    qa_json = tmp_path / "qa" / "receipt.json"

    result = run_renderer(source, desktop, mobile, qa_json)

    assert result.returncode == 0, result.stdout + result.stderr
    assert desktop.is_file() and desktop.stat().st_size > 0
    assert mobile.is_file() and mobile.stat().st_size > 0
    receipt = json.loads(qa_json.read_text(encoding="utf-8"))
    assert set(receipt) == {"desktop", "mobile"}
    for key, viewport, screenshot in (
        ("desktop", {"width": 1440, "height": 1000}, desktop),
        ("mobile", {"width": 390, "height": 844}, mobile),
    ):
        record = receipt[key]
        assert record["viewport"] == viewport
        assert isinstance(record["scrollWidth"], int)
        assert isinstance(record["clientWidth"], int)
        assert record["horizontalOverflow"] is False
        assert record["consoleErrors"] == []
        assert record["pageErrors"] == []
        assert Path(record["screenshot"]) == screenshot.resolve()
        assert Path(record["screenshot"]).stat().st_size > 0


def test_renderer_receipt_reports_horizontal_overflow_per_viewport(tmp_path):
    source = tmp_path / "overflow.html"
    source.write_text(
        "<!doctype html><html><head><style>body{margin:0}.wide{width:1200px;height:20px}</style></head>"
        "<body><div class='wide'></div></body></html>",
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"

    result = run_renderer(source, tmp_path / "desktop.png", tmp_path / "mobile.png", qa_json)

    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(qa_json.read_text(encoding="utf-8"))
    assert receipt["desktop"]["horizontalOverflow"] is False
    assert receipt["mobile"]["horizontalOverflow"] is True


def test_renderer_receipt_captures_unhandled_page_errors(tmp_path):
    source = tmp_path / "throws.html"
    source.write_text(
        "<!doctype html><html><body><script>throw new Error('fixture page failure')</script></body></html>",
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"

    result = run_renderer(source, tmp_path / "desktop.png", tmp_path / "mobile.png", qa_json)

    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(qa_json.read_text(encoding="utf-8"))
    assert any("fixture page failure" in error for error in receipt["desktop"]["pageErrors"])
    assert any("fixture page failure" in error for error in receipt["mobile"]["pageErrors"])


def test_renderer_fails_for_missing_input(tmp_path):
    result = run_renderer(tmp_path / "missing.html", tmp_path / "desktop.png", tmp_path / "mobile.png")

    assert result.returncode != 0
    assert "input" in result.stderr.lower() or "input" in result.stdout.lower()
