import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
RENDERER = ROOT / "tools" / "render-preview.mjs"


def run_renderer(input_path, desktop_path, mobile_path):
    assert NODE is not None, "Node.js is required for render-preview"
    return subprocess.run(
        [
            NODE,
            str(RENDERER),
            "--input",
            str(input_path),
            "--desktop",
            str(desktop_path),
            "--mobile",
            str(mobile_path),
        ],
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


def test_renderer_fails_for_missing_input(tmp_path):
    result = run_renderer(tmp_path / "missing.html", tmp_path / "desktop.png", tmp_path / "mobile.png")

    assert result.returncode != 0
    assert "input" in result.stderr.lower() or "input" in result.stdout.lower()
