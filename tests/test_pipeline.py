from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest

from search_intent_automation import __version__
from search_intent_automation.pipeline import main

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _write_answer_csv(path: Path) -> None:
    path.write_text(
        "question,intent\n"
        "what is local seo,informational\n"
        "best local seo agency,comparative\n"
        "local seo cost,transactional\n",
        encoding="utf-8",
    )


def test_successful_run_from_manifest(tmp_path: Path) -> None:
    ubersuggest_path = tmp_path / "ubersuggest.json"
    ubersuggest_path.write_text(
        json.dumps({"rows": [{"keyword": "seo agency", "volume": 1000}]}),
        encoding="utf-8",
    )
    answer_path = tmp_path / "answer.csv"
    _write_answer_csv(answer_path)
    manifest_path = tmp_path / "capture-status.json"
    manifest_path.write_text(
        json.dumps(
            {
                "ubersuggest": {"status": "ok", "artifact": str(ubersuggest_path)},
                "answer_the_public": {"status": "ok", "artifact": str(answer_path)},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--seed",
            "local seo",
            "--goal",
            "rank service pages",
            "--workdir",
            str(tmp_path),
            "--capture-status-json",
            str(manifest_path),
        ]
    )

    assert exit_code == 0
    output = json.loads((tmp_path / "opportunity-map.json").read_text(encoding="utf-8"))
    assert output["status"] == "ok"
    assert output["source_counts"] == {"ubersuggest": 1, "answer_the_public": 3}


def test_blocked_auth_expired_checkpoint(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    answer_path = tmp_path / "answer.csv"
    _write_answer_csv(answer_path)
    manifest_path = tmp_path / "capture-status.json"
    manifest_path.write_text(
        json.dumps(
            {
                "ubersuggest": {"status": "auth-expired", "artifact": None},
                "answer_the_public": {"status": "ok", "artifact": str(answer_path)},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--seed",
            "seo services",
            "--goal",
            "find content angles",
            "--workdir",
            str(tmp_path),
            "--capture-status-json",
            str(manifest_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 30
    assert "taxonomy: auth-expired" in captured.out
    checkpoint = json.loads((tmp_path / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["recommended_option_1"].startswith("Refresh auth")


def test_resume_partial_from_checkpoint(tmp_path: Path) -> None:
    answer_path = tmp_path / "answer.csv"
    _write_answer_csv(answer_path)
    manifest_path = tmp_path / "capture-status.json"
    manifest_path.write_text(
        json.dumps(
            {
                "ubersuggest": {"status": "auth-expired", "artifact": None},
                "answer_the_public": {"status": "ok", "artifact": str(answer_path)},
            }
        ),
        encoding="utf-8",
    )
    blocked = main(
        [
            "--seed",
            "seo services",
            "--goal",
            "find content angles",
            "--workdir",
            str(tmp_path),
            "--capture-status-json",
            str(manifest_path),
        ]
    )
    assert blocked == 30

    resumed = main(
        [
            "--resume-from-checkpoint",
            str(tmp_path / "checkpoint.json"),
            "--capture-status-json",
            str(manifest_path),
            "--direction",
            "recommended-2",
        ]
    )
    assert resumed == 0
    output = json.loads((tmp_path / "opportunity-map.json").read_text(encoding="utf-8"))
    assert output["status"] == "partial"
    assert output["deferred_sources"] == ["ubersuggest"]


def test_low_signal_checkpoint_requires_direction(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ubersuggest_path = tmp_path / "ubersuggest.json"
    ubersuggest_path.write_text(
        json.dumps({"rows": [{"keyword": "seo agency", "volume": 1000}]}),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "capture-status.json"
    manifest_path.write_text(
        json.dumps(
            {
                "ubersuggest": {"status": "ok", "artifact": str(ubersuggest_path)},
                "answer_the_public": {"status": "ok", "artifact": None},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--seed",
            "local seo",
            "--goal",
            "build opportunity map",
            "--workdir",
            str(tmp_path),
            "--capture-status-json",
            str(manifest_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 23
    assert "taxonomy: low-signal-data" in captured.out
    checkpoint = json.loads((tmp_path / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["taxonomy"] == "low-signal-data"


def test_invalid_direction_is_rejected() -> None:
    with pytest.raises(SystemExit, match="Unsupported direction"):
        main(["--seed", "x", "--goal", "y", "--workdir", "/tmp/z", "--direction", "later"])


def test_module_invocation_reports_version() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(
        [sys.executable, "-m", "search_intent_automation", "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert __version__ in result.stdout
    assert metadata.version("search-intent-automation") == __version__


def test_compatibility_shim_runs(tmp_path: Path) -> None:
    ubersuggest_path = tmp_path / "ubersuggest.json"
    ubersuggest_path.write_text(
        json.dumps({"rows": [{"keyword": "seo agency", "volume": 1000}]}),
        encoding="utf-8",
    )
    answer_path = tmp_path / "answer.csv"
    _write_answer_csv(answer_path)
    manifest_path = tmp_path / "capture-status.json"
    manifest_path.write_text(
        json.dumps(
            {
                "ubersuggest": {"status": "ok", "artifact": str(ubersuggest_path)},
                "answer_the_public": {"status": "ok", "artifact": str(answer_path)},
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Tools" / "OpportunityPipeline.py"),
            "--seed",
            "local seo",
            "--goal",
            "rank service pages",
            "--workdir",
            str(tmp_path),
            "--capture-status-json",
            str(manifest_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Opportunity map written" in result.stdout
