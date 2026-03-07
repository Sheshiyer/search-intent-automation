#!/usr/bin/env python3
"""Deterministic orchestrator for SearchIntentAutomation runs."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ISSUE_RECOMMENDATIONS = {
    "auth-expired": (
        "Refresh auth and retry the same Playwright capture step.",
        "Continue from cached artifacts if they are recent enough.",
    ),
    "selector-drift": (
        "Retry capture with fallback selectors and the same target.",
        "Switch to screenshot/manual-export mode for the blocked step.",
    ),
    "rate-limited": (
        "Back off and retry after a cooling interval.",
        "Continue with partial data and mark the source deferred.",
    ),
    "missing-export": (
        "Retry capture with an explicit export path.",
        "Continue with the remaining source and mark the output partial.",
    ),
    "schema-mismatch": (
        "Patch normalization for the current schema and continue.",
        "Re-run capture with a simpler export format.",
    ),
    "low-signal-data": (
        "Refine the seed and retry with a narrower topic.",
        "Proceed with manual review instead of full automation.",
    ),
}

VALID_ISSUES = tuple(ISSUE_RECOMMENDATIONS)
VALID_SOURCE_STATUSES = ("ok", *VALID_ISSUES)
EXIT_CODES = {
    "auth-expired": 30,
    "selector-drift": 31,
    "rate-limited": 32,
    "missing-export": 20,
    "schema-mismatch": 22,
    "low-signal-data": 23,
}


def load_artifact(path: Path) -> object:
    """Load a JSON or CSV artifact."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported artifact format: {path}")


def checkpoint_payload(
    issue: str,
    seed: str,
    goal: str,
    workdir: Path,
    *,
    source_statuses: dict | None = None,
    selected_direction: str | None = None,
    resume_from: Path | None = None,
) -> dict:
    """Create a structured checkpoint with two recommended branches and one custom branch."""
    option_1, option_2 = ISSUE_RECOMMENDATIONS[issue]
    resume_stub = [
        "python3 ~/.claude/skills/SearchIntentAutomation/Tools/OpportunityPipeline.py",
        f'  --resume-from-checkpoint "{workdir / "checkpoint.json"}"',
        "  --direction recommended-1",
    ]
    return {
        "status": "needs_user_direction",
        "taxonomy": issue,
        "seed": seed,
        "goal": goal,
        "workdir": str(workdir),
        "source_statuses": source_statuses or {},
        "recommended_option_1": option_1,
        "recommended_option_2": option_2,
        "custom_direction": "Provide a custom direction to change the flow.",
        "selected_direction": selected_direction,
        "decision_prompt": {
            "taxonomy": issue,
            "options": [
                {"id": "recommended-1", "label": option_1},
                {"id": "recommended-2", "label": option_2},
                {
                    "id": "custom",
                    "label": "Provide a custom direction to change the flow.",
                },
            ],
        },
        "resume_hints": {
            "recommended_1": "\n".join(resume_stub),
            "recommended_2": "\n".join(
                resume_stub[:-1] + ["  --direction recommended-2"]
            ),
            "custom": "\n".join(
                resume_stub[:-1] + ['  --direction "custom:YOUR-DIRECTION"']
            ),
            "resume_from": str(resume_from) if resume_from else None,
        },
        "exit_code": EXIT_CODES[issue],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_checkpoint(path: Path, payload: dict) -> None:
    """Write a checkpoint file and mirror the decision prompt to stdout."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"STUCK [{payload['taxonomy']}]")
    print(f"taxonomy: {payload['taxonomy']}")
    print(f"recommended option 1: {payload['recommended_option_1']}")
    print(f"recommended option 2: {payload['recommended_option_2']}")
    print(f"custom direction: {payload['custom_direction']}")
    print(f"Checkpoint written to: {path}")


def normalize_rows(artifact: object, source_name: str) -> list[dict]:
    """Normalize loaded artifact data to a row list."""
    if isinstance(artifact, list):
        rows = artifact
    elif isinstance(artifact, dict):
        if "rows" in artifact and isinstance(artifact["rows"], list):
            rows = artifact["rows"]
        elif "data" in artifact and isinstance(artifact["data"], list):
            rows = artifact["data"]
        else:
            rows = [artifact]
    else:
        rows = []

    normalized: list[dict] = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append({"source": source_name, **row})
        else:
            normalized.append({"source": source_name, "value": str(row)})
    return normalized


def summarize_partial_signal(rows: list[dict]) -> bool:
    """Return True when the loaded rows are likely too thin to trust."""
    return len(rows) < 3


def parse_direction(value: str | None) -> str | None:
    """Normalize direction values."""
    if value is None:
        return None
    value = value.strip()
    return value or None


def validate_direction(value: str | None) -> str | None:
    """Validate supported direction overrides."""
    if value is None:
        return None
    if value in {"recommended-1", "recommended-2"}:
        return value
    if value.startswith("custom:"):
        return value
    raise ValueError(
        "Unsupported direction. Expected recommended-1, recommended-2, or custom:<text>."
    )


def parse_source_status(value: str | None) -> str | None:
    """Normalize source status overrides."""
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized not in VALID_SOURCE_STATUSES:
        raise ValueError(
            f"Unsupported source status '{value}'. Expected one of: {', '.join(VALID_SOURCE_STATUSES)}"
        )
    return normalized


def can_continue(issue: str, direction: str | None, valid_source_count: int) -> bool:
    """Return True when the selected direction permits a partial continuation."""
    if valid_source_count == 0 or direction is None:
        return False
    if direction == "recommended-2":
        return True
    if direction.startswith("custom:"):
        return True
    if issue == "low-signal-data" and direction in {"recommended-1", "recommended-2"}:
        return direction == "recommended-2"
    return False


def load_checkpoint(path: Path) -> dict:
    """Load a checkpoint file."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_capture_status(path: Path) -> dict:
    """Load a Playwright capture-status manifest."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Capture status manifest must be a JSON object.")
    return manifest


def manifest_entry(manifest: dict, source_name: str) -> dict:
    """Normalize a single capture manifest entry."""
    raw_entry = manifest.get(source_name, {})
    if isinstance(raw_entry, str):
        return {"status": raw_entry}
    if isinstance(raw_entry, dict):
        return raw_entry
    return {}


def build_output(
    seed: str,
    goal: str,
    ubersuggest_rows: list[dict],
    answer_rows: list[dict],
    direction: str | None,
    source_statuses: dict,
    deferred_sources: list[str],
    review_required: bool,
    resumed_from: Path | None,
) -> dict:
    """Build the non-interactive output payload."""
    status = "ok"
    if deferred_sources and review_required:
        status = "partial_review_required"
    elif deferred_sources:
        status = "partial"
    elif review_required:
        status = "review_required"
    return {
        "status": status,
        "seed": seed,
        "goal": goal,
        "direction": direction,
        "resumed_from_checkpoint": str(resumed_from) if resumed_from else None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_counts": {
            "ubersuggest": len(ubersuggest_rows),
            "answer_the_public": len(answer_rows),
        },
        "source_statuses": source_statuses,
        "deferred_sources": deferred_sources,
        "review_required": review_required,
        "opportunity_map": {
            "keyword_rows": ubersuggest_rows,
            "question_rows": answer_rows,
        },
        "notes": [
            "Playwright MCP is responsible for browser capture.",
            "This Python script handles deterministic downstream normalization and merging.",
            "If blocked, use the checkpoint taxonomy instead of improvising hidden fallback logic.",
        ],
    }


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="SearchIntentAutomation pipeline.")
    parser.add_argument("--seed", help="Seed topic or offer.")
    parser.add_argument("--goal", help="Primary goal for the run.")
    parser.add_argument(
        "--workdir",
        type=Path,
        help="Run directory for outputs and checkpoints.",
    )
    parser.add_argument(
        "--ubersuggest-input",
        type=Path,
        help="Path to Playwright-captured Ubersuggest JSON/CSV.",
    )
    parser.add_argument(
        "--answer-input",
        type=Path,
        help="Path to Playwright-captured AnswerThePublic JSON/CSV.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Output file for the merged opportunity map JSON.",
    )
    parser.add_argument(
        "--checkpoint-json",
        type=Path,
        help="Output file for checkpoint JSON when blocked.",
    )
    parser.add_argument(
        "--direction",
        help="Direction override: recommended-1, recommended-2, or custom:<text>",
    )
    parser.add_argument(
        "--ubersuggest-status",
        help=f"Capture status for Ubersuggest: {', '.join(VALID_SOURCE_STATUSES)}",
    )
    parser.add_argument(
        "--answer-status",
        help=f"Capture status for AnswerThePublic: {', '.join(VALID_SOURCE_STATUSES)}",
    )
    parser.add_argument(
        "--resume-from-checkpoint",
        type=Path,
        help="Resume from an existing checkpoint JSON file.",
    )
    parser.add_argument(
        "--capture-status-json",
        type=Path,
        help="Path to a Playwright-generated capture status manifest JSON.",
    )
    args = parser.parse_args()

    resumed_from: Path | None = None
    checkpoint_state: dict | None = None
    if args.resume_from_checkpoint:
        resumed_from = args.resume_from_checkpoint.expanduser().resolve()
        checkpoint_state = load_checkpoint(resumed_from)

    seed = args.seed or (checkpoint_state["seed"] if checkpoint_state else None)
    goal = args.goal or (checkpoint_state["goal"] if checkpoint_state else None)
    raw_workdir = args.workdir or (
        Path(checkpoint_state["workdir"]) if checkpoint_state else None
    )
    if not seed or not goal or raw_workdir is None:
        raise SystemExit(
            "Seed, goal, and workdir are required unless --resume-from-checkpoint supplies them."
        )

    workdir = raw_workdir.expanduser().resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    output_json = (
        args.output_json.expanduser().resolve()
        if args.output_json
        else workdir / "opportunity-map.json"
    )
    checkpoint_json = (
        args.checkpoint_json.expanduser().resolve()
        if args.checkpoint_json
        else workdir / "checkpoint.json"
    )
    direction = parse_direction(args.direction)
    try:
        direction = validate_direction(direction)
        ubersuggest_status = parse_source_status(args.ubersuggest_status)
        answer_status = parse_source_status(args.answer_status)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    capture_manifest: dict | None = None
    if args.capture_status_json:
        try:
            capture_manifest = load_capture_status(
                args.capture_status_json.expanduser().resolve()
            )
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Invalid capture status manifest: {exc}") from exc

    ubersuggest_input = args.ubersuggest_input
    answer_input = args.answer_input
    if capture_manifest:
        ubersuggest_entry = manifest_entry(capture_manifest, "ubersuggest")
        answer_entry = manifest_entry(capture_manifest, "answer_the_public")
        if ubersuggest_input is None and ubersuggest_entry.get("artifact"):
            ubersuggest_input = Path(str(ubersuggest_entry["artifact"]))
        if answer_input is None and answer_entry.get("artifact"):
            answer_input = Path(str(answer_entry["artifact"]))
        if ubersuggest_status is None:
            ubersuggest_status = parse_source_status(
                ubersuggest_entry.get("issue") or ubersuggest_entry.get("status")
            )
        if answer_status is None:
            answer_status = parse_source_status(
                answer_entry.get("issue") or answer_entry.get("status")
            )

    if checkpoint_state:
        prior_statuses = checkpoint_state.get("source_statuses", {})
        if ubersuggest_status is None:
            ubersuggest_status = prior_statuses.get("ubersuggest", {}).get("issue") or (
                "ok" if prior_statuses.get("ubersuggest", {}).get("status") == "ok" else None
            )
        if answer_status is None:
            answer_status = prior_statuses.get("answer_the_public", {}).get("issue") or (
                "ok"
                if prior_statuses.get("answer_the_public", {}).get("status") == "ok"
                else None
            )

    ubersuggest_rows: list[dict] = []
    answer_rows: list[dict] = []
    source_statuses = {
        "ubersuggest": {"status": "pending", "issue": None},
        "answer_the_public": {"status": "pending", "issue": None},
    }

    for source_name, source_path, status_override in (
        ("ubersuggest", ubersuggest_input, ubersuggest_status),
        ("answer_the_public", answer_input, answer_status),
    ):
        rows_target = ubersuggest_rows if source_name == "ubersuggest" else answer_rows
        issue = None if status_override in {None, "ok"} else status_override
        if source_path:
            try:
                artifact = load_artifact(source_path.expanduser().resolve())
                rows_target.extend(
                    normalize_rows(
                        artifact,
                        "answer-the-public" if source_name == "answer_the_public" else source_name,
                    )
                )
            except FileNotFoundError:
                issue = "missing-export"
            except (json.JSONDecodeError, ValueError):
                issue = "schema-mismatch"
        elif issue is None:
            issue = "missing-export"

        if issue is None:
            source_statuses[source_name] = {"status": "ok", "issue": None}
        else:
            source_statuses[source_name] = {"status": "blocked", "issue": issue}

    first_issue = next(
        (
            status["issue"]
            for status in source_statuses.values()
            if status["issue"] is not None
        ),
        None,
    )
    valid_source_count = int(bool(ubersuggest_rows)) + int(bool(answer_rows))

    if first_issue is not None and not can_continue(first_issue, direction, valid_source_count):
        payload = checkpoint_payload(
            first_issue,
            seed,
            goal,
            workdir,
            source_statuses=source_statuses,
            selected_direction=direction,
            resume_from=resumed_from,
        )
        write_checkpoint(checkpoint_json, payload)
        return EXIT_CODES[first_issue]

    review_required = False
    if summarize_partial_signal(ubersuggest_rows + answer_rows):
        if direction is None:
            payload = checkpoint_payload(
                "low-signal-data",
                seed,
                goal,
                workdir,
                source_statuses=source_statuses,
                selected_direction=direction,
                resume_from=resumed_from,
            )
            write_checkpoint(checkpoint_json, payload)
            return EXIT_CODES["low-signal-data"]
        review_required = True

    deferred_sources: list[str] = []
    if first_issue is not None:
        for source_name, status in source_statuses.items():
            if status["issue"] is not None:
                status["status"] = "deferred"
                deferred_sources.append(source_name)

    output = build_output(
        seed=seed,
        goal=goal,
        ubersuggest_rows=ubersuggest_rows,
        answer_rows=answer_rows,
        direction=direction,
        source_statuses=source_statuses,
        deferred_sources=deferred_sources,
        review_required=review_required,
        resumed_from=resumed_from,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Opportunity map written to: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
