from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from search_intent_automation.pipeline import EXIT_CODES


def write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_capture_status(
    path: Path,
    *,
    ubersuggest_artifact: Path | None = None,
    ubersuggest_status: str = "ok",
    answer_artifact: Path | None = None,
    answer_status: str = "ok",
) -> Path:
    return write_json(
        path,
        {
            "ubersuggest": {
                "status": ubersuggest_status,
                "artifact": str(ubersuggest_artifact) if ubersuggest_artifact else None,
            },
            "answer_the_public": {
                "status": answer_status,
                "artifact": str(answer_artifact) if answer_artifact else None,
            },
        },
    )


def run_console(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    script = Path(sys.executable).with_name("search-intent-automation")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    command: list[str]
    if script.exists():
        command = [str(script), *args]
    else:
        command = [sys.executable, "-m", "search_intent_automation", *args]
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def build_success_fixture(workdir: Path) -> tuple[Path, Path, Path]:
    ubersuggest = write_json(
        workdir / "ubersuggest.json",
        {
            "rows": [
                {"keyword": "seo automation", "volume": 1900},
                {"keyword": "search intent automation", "volume": 250},
            ]
        },
    )
    answer = write_json(
        workdir / "answer-the-public.json",
        {
            "rows": [
                {"question": "what is search intent automation"},
                {"question": "how to automate search intent clustering"},
            ]
        },
    )
    capture_status = write_capture_status(
        workdir / "capture-status.json",
        ubersuggest_artifact=ubersuggest,
        answer_artifact=answer,
    )
    return ubersuggest, answer, capture_status


def test_console_entrypoint_writes_opportunity_map(tmp_path: Path) -> None:
    workdir = tmp_path / "run"
    workdir.mkdir()
    _, _, capture_status = build_success_fixture(workdir)

    result = run_console(
        "run",
        "--seed",
        "search intent automation",
        "--goal",
        "build opportunity map",
        "--workdir",
        str(workdir),
        "--capture-status-json",
        str(capture_status),
        cwd=workdir,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads((workdir / "opportunity-map.json").read_text(encoding="utf-8"))
    assert output["status"] == "ok"
    assert output["source_counts"] == {"ubersuggest": 2, "answer_the_public": 2}
    assert output["source_statuses"]["ubersuggest"] == {"status": "ok", "issue": None}
    assert output["source_statuses"]["answer_the_public"] == {
        "status": "ok",
        "issue": None,
    }


def test_console_entrypoint_writes_checkpoint_when_capture_is_blocked(
    tmp_path: Path,
) -> None:
    workdir = tmp_path / "run"
    workdir.mkdir()
    answer = write_json(
        workdir / "answer-the-public.json",
        {
            "rows": [
                {"question": "what is search intent automation"},
                {"question": "how to automate search intent clustering"},
                {"question": "best search intent tools"},
            ]
        },
    )
    capture_status = write_capture_status(
        workdir / "capture-status.json",
        ubersuggest_status="rate-limited",
        answer_artifact=answer,
    )

    result = run_console(
        "run",
        "--seed",
        "search intent automation",
        "--goal",
        "build opportunity map",
        "--workdir",
        str(workdir),
        "--capture-status-json",
        str(capture_status),
        cwd=workdir,
    )

    assert result.returncode == EXIT_CODES["rate-limited"]
    checkpoint = json.loads((workdir / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["taxonomy"] == "rate-limited"
    assert checkpoint["source_statuses"]["ubersuggest"] == {
        "status": "blocked",
        "issue": "rate-limited",
    }
    assert checkpoint["resume_hints"]["recommended_2"].endswith(
        '  --direction recommended-2'
    )


def test_console_entrypoint_resumes_from_checkpoint_with_direction(
    tmp_path: Path,
) -> None:
    workdir = tmp_path / "run"
    workdir.mkdir()
    answer = write_json(
        workdir / "answer-the-public.json",
        {
            "rows": [
                {"question": "what is search intent automation"},
                {"question": "how to automate search intent clustering"},
                {"question": "best search intent tools"},
            ]
        },
    )
    capture_status = write_capture_status(
        workdir / "capture-status.json",
        ubersuggest_status="rate-limited",
        answer_artifact=answer,
    )

    initial = run_console(
        "run",
        "--seed",
        "search intent automation",
        "--goal",
        "build opportunity map",
        "--workdir",
        str(workdir),
        "--capture-status-json",
        str(capture_status),
        cwd=workdir,
    )
    checkpoint_path = workdir / "checkpoint.json"
    assert initial.returncode == EXIT_CODES["rate-limited"]
    assert checkpoint_path.exists()

    resumed = run_console(
        "resume",
        "--resume-from-checkpoint",
        str(checkpoint_path),
        "--capture-status-json",
        str(capture_status),
        "--direction",
        "recommended-2",
        cwd=workdir,
    )

    assert resumed.returncode == 0, resumed.stderr
    output = json.loads((workdir / "opportunity-map.json").read_text(encoding="utf-8"))
    assert output["status"] == "partial"
    assert output["direction"] == "recommended-2"
    assert output["deferred_sources"] == ["ubersuggest"]
    assert output["resumed_from_checkpoint"] == str(checkpoint_path.resolve())


def test_console_validate_and_init_subcommands(tmp_path: Path) -> None:
    workdir = tmp_path / "initialized"
    init_result = run_console("init", "--workdir", str(workdir), cwd=tmp_path)
    assert init_result.returncode == 0, init_result.stderr

    validate_result = run_console(
        "validate",
        "--kind",
        "capture-status",
        str(workdir / "capture-status.json"),
        cwd=tmp_path,
    )
    assert validate_result.returncode == 0, validate_result.stderr
    assert "capture-status contract is valid" in validate_result.stdout


def test_flat_cli_invocation_still_routes_to_run(tmp_path: Path) -> None:
    workdir = tmp_path / "run"
    workdir.mkdir()
    _, _, capture_status = build_success_fixture(workdir)

    result = run_console(
        "--seed",
        "search intent automation",
        "--goal",
        "build opportunity map",
        "--workdir",
        str(workdir),
        "--capture-status-json",
        str(capture_status),
        cwd=workdir,
    )

    assert result.returncode == 0, result.stderr
    assert (workdir / "opportunity-map.json").exists()


def test_compatibility_shim_runs_without_site_packages(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workdir = tmp_path / "shim-run"
    workdir.mkdir()
    _, _, capture_status = build_success_fixture(workdir)

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            sys.executable,
            "-S",
            str(repo_root / "Tools" / "OpportunityPipeline.py"),
            "--seed",
            "search intent automation",
            "--goal",
            "build opportunity map",
            "--workdir",
            str(workdir),
            "--capture-status-json",
            str(capture_status),
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads((workdir / "opportunity-map.json").read_text(encoding="utf-8"))
    assert output["status"] == "ok"
