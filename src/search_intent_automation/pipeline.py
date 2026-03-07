"""Deterministic orchestrator for Search Intent Automation runs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .contracts import (
    KNOWN_SOURCES,
    CaptureManifest,
    JsonMap,
    SourceState,
    validate_capture_manifest,
    validate_checkpoint_payload,
    validate_opportunity_map,
)

PROGRAM_NAME = "search-intent-automation"
CUSTOM_DIRECTION_PROMPT = "Provide a custom direction to change the flow."
OUTPUT_STATUSES = ("ok", "partial", "review_required", "partial_review_required")
SUBCOMMANDS = frozenset({"run", "resume", "validate", "init"})
RUN_COMPAT_FLAGS = frozenset(
    {
        "--seed",
        "--goal",
        "--workdir",
        "--capture-status-json",
        "--ubersuggest-input",
        "--answer-input",
        "--ubersuggest-status",
        "--answer-status",
        "--output-json",
        "--checkpoint-json",
        "--direction",
        "--resume-from-checkpoint",
    }
)
VALIDATE_KINDS = ("capture-status", "checkpoint", "opportunity-map")

ISSUE_RECOMMENDATIONS: dict[str, tuple[str, str]] = {
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

INIT_UBERSUGGEST_SAMPLE = {
    "rows": [
        {"keyword": "search intent automation", "volume": 250},
    ]
}
INIT_ANSWER_SAMPLE = (
    "question,intent\n"
    "what is search intent automation,informational\n"
    "how to automate search intent clustering,informational\n"
)
INIT_CAPTURE_STATUS = {
    "ubersuggest": {"status": "ok", "artifact": "ubersuggest.json"},
    "answer_the_public": {"status": "ok", "artifact": "answer-the-public.csv"},
}


def resolve_path(path: Path, *, base_dir: Path | None = None) -> Path:
    """Resolve a path, optionally relative to a base directory."""
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    if base_dir is not None:
        return (base_dir / expanded).resolve()
    return expanded.resolve()


def load_artifact(path: Path) -> object:
    """Load a JSON or CSV artifact."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported artifact format: {path}")


def write_json(path: Path, payload: JsonMap) -> None:
    """Write a formatted JSON payload."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def checkpoint_payload(
    issue: str,
    seed: str,
    goal: str,
    workdir: Path,
    *,
    source_statuses: dict[str, SourceState] | None = None,
    selected_direction: str | None = None,
    resume_from: Path | None = None,
) -> JsonMap:
    """Create a structured checkpoint with two recommended branches and one custom branch."""
    option_1, option_2 = ISSUE_RECOMMENDATIONS[issue]
    resume_stub = [
        PROGRAM_NAME,
        "  resume",
        f'  --resume-from-checkpoint "{workdir / "checkpoint.json"}"',
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
        "custom_direction": CUSTOM_DIRECTION_PROMPT,
        "selected_direction": selected_direction,
        "decision_prompt": {
            "taxonomy": issue,
            "options": [
                {"id": "recommended-1", "label": option_1},
                {"id": "recommended-2", "label": option_2},
                {"id": "custom", "label": CUSTOM_DIRECTION_PROMPT},
            ],
        },
        "resume_hints": {
            "recommended_1": "\n".join(resume_stub + ["  --direction recommended-1"]),
            "recommended_2": "\n".join(resume_stub + ["  --direction recommended-2"]),
            "custom": "\n".join(
                resume_stub + ['  --direction "custom:YOUR-DIRECTION"']
            ),
            "resume_from": str(resume_from) if resume_from else None,
        },
        "exit_code": EXIT_CODES[issue],
        "generated_at": datetime.now(UTC).isoformat(),
    }


def write_checkpoint(path: Path, payload: JsonMap) -> None:
    """Write a checkpoint file and mirror the decision prompt to stdout."""
    validated = validate_checkpoint_payload(payload, valid_issues=VALID_ISSUES)
    write_json(path, validated)
    print(f"STUCK [{validated['taxonomy']}]")
    print(f"taxonomy: {validated['taxonomy']}")
    print(f"recommended option 1: {validated['recommended_option_1']}")
    print(f"recommended option 2: {validated['recommended_option_2']}")
    print(f"custom direction: {validated['custom_direction']}")
    print(f"Checkpoint written to: {path}")


def normalize_rows(artifact: object, source_name: str) -> list[JsonMap]:
    """Normalize loaded artifact data to a row list."""
    rows: list[object]
    if isinstance(artifact, list):
        rows = artifact
    elif isinstance(artifact, dict):
        if "rows" in artifact and isinstance(artifact["rows"], list):
            rows = list(artifact["rows"])
        elif "data" in artifact and isinstance(artifact["data"], list):
            rows = list(artifact["data"])
        else:
            rows = [artifact]
    else:
        rows = []

    normalized: list[JsonMap] = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append({"source": source_name, **row})
        else:
            normalized.append({"source": source_name, "value": str(row)})
    return normalized


def summarize_partial_signal(rows: list[JsonMap]) -> bool:
    """Return True when the loaded rows are likely too thin to trust."""
    return len(rows) < 3


def parse_direction(value: str | None) -> str | None:
    """Normalize direction values."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


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
        expected = ", ".join(VALID_SOURCE_STATUSES)
        raise ValueError(f"Unsupported source status '{value}'. Expected one of: {expected}")
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


def load_checkpoint(path: Path) -> JsonMap:
    """Load and validate a checkpoint file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_checkpoint_payload(data, valid_issues=VALID_ISSUES)


def load_capture_status(path: Path) -> CaptureManifest:
    """Load and validate a Playwright capture-status manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_capture_manifest(data, valid_statuses=VALID_SOURCE_STATUSES)


def build_output(
    seed: str,
    goal: str,
    ubersuggest_rows: list[JsonMap],
    answer_rows: list[JsonMap],
    direction: str | None,
    source_statuses: dict[str, SourceState],
    deferred_sources: list[str],
    review_required: bool,
    resumed_from: Path | None,
) -> JsonMap:
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
        "generated_at": datetime.now(UTC).isoformat(),
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
            "This Python package handles deterministic downstream normalization and merging.",
            "If blocked, use the checkpoint taxonomy instead of improvising hidden fallback logic.",
        ],
    }


def add_shared_execution_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared file/status arguments to a subcommand parser."""
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
        "--ubersuggest-status",
        help=f"Capture status for Ubersuggest: {', '.join(VALID_SOURCE_STATUSES)}",
    )
    parser.add_argument(
        "--answer-status",
        help=f"Capture status for AnswerThePublic: {', '.join(VALID_SOURCE_STATUSES)}",
    )
    parser.add_argument(
        "--capture-status-json",
        type=Path,
        help="Path to a Playwright-generated capture status manifest JSON.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Search Intent Automation pipeline.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    run_parser = subparsers.add_parser(
        "run",
        help="Merge captured source artifacts into an opportunity map.",
    )
    run_parser.add_argument("--seed", required=True, help="Seed topic or offer.")
    run_parser.add_argument("--goal", required=True, help="Primary goal for the run.")
    run_parser.add_argument(
        "--workdir",
        type=Path,
        required=True,
        help="Run directory for outputs and checkpoints.",
    )
    run_parser.add_argument(
        "--direction",
        help="Direction override: recommended-1, recommended-2, or custom:<text>",
    )
    add_shared_execution_arguments(run_parser)
    run_parser.set_defaults(command_fn=run_command)

    resume_parser = subparsers.add_parser("resume", help="Resume from an existing checkpoint.")
    resume_parser.add_argument(
        "--resume-from-checkpoint",
        type=Path,
        required=True,
        help="Resume from an existing checkpoint JSON file.",
    )
    resume_parser.add_argument("--seed", help="Override the checkpoint seed.")
    resume_parser.add_argument("--goal", help="Override the checkpoint goal.")
    resume_parser.add_argument(
        "--workdir",
        type=Path,
        help="Override the checkpoint workdir.",
    )
    resume_parser.add_argument(
        "--direction",
        help="Direction override: recommended-1, recommended-2, or custom:<text>",
    )
    add_shared_execution_arguments(resume_parser)
    resume_parser.set_defaults(command_fn=resume_command)

    validate_parser = subparsers.add_parser("validate", help="Validate a JSON contract file.")
    validate_parser.add_argument(
        "--kind",
        choices=VALIDATE_KINDS,
        required=True,
        help="Contract kind to validate.",
    )
    validate_parser.add_argument("path", type=Path, help="Path to the JSON contract file.")
    validate_parser.set_defaults(command_fn=validate_command)

    init_parser = subparsers.add_parser("init", help="Create a runnable workdir scaffold.")
    init_parser.add_argument(
        "--workdir",
        type=Path,
        required=True,
        help="Directory to initialize.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite scaffold files in an existing directory.",
    )
    init_parser.set_defaults(command_fn=init_command)
    return parser


def normalize_command_argv(argv: Sequence[str] | None) -> list[str]:
    """Inject compatibility commands for legacy flat invocation."""
    args = list(argv) if argv is not None else []
    if not args:
        return args
    if args[0] in SUBCOMMANDS:
        return args
    if args[0] in {"-h", "--help", "--version"}:
        return args
    if "--resume-from-checkpoint" in args:
        return ["resume", *args]
    if any(arg in RUN_COMPAT_FLAGS for arg in args):
        return ["run", *args]
    return args


def resolve_manifest_artifact(entry: JsonMap, *, manifest_path: Path) -> Path | None:
    """Resolve a manifest artifact path relative to the manifest location."""
    artifact = entry.get("artifact")
    if artifact is None:
        return None
    return resolve_path(Path(str(artifact)), base_dir=manifest_path.parent)


def execute_pipeline(args: argparse.Namespace, *, resumed_from: Path | None = None) -> int:
    """Run the pipeline using parsed CLI arguments."""
    checkpoint_state: JsonMap | None = None
    if resumed_from is not None:
        checkpoint_state = load_checkpoint(resumed_from)

    seed = args.seed or (str(checkpoint_state["seed"]) if checkpoint_state else None)
    goal = args.goal or (str(checkpoint_state["goal"]) if checkpoint_state else None)
    raw_workdir = args.workdir or (
        Path(str(checkpoint_state["workdir"])) if checkpoint_state else None
    )
    if not seed or not goal or raw_workdir is None:
        raise SystemExit(
            "Seed, goal, and workdir are required unless --resume-from-checkpoint supplies them."
        )

    workdir = resolve_path(raw_workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    output_json = (
        resolve_path(args.output_json)
        if args.output_json
        else workdir / "opportunity-map.json"
    )
    checkpoint_json = (
        resolve_path(args.checkpoint_json)
        if args.checkpoint_json
        else workdir / "checkpoint.json"
    )

    try:
        direction = validate_direction(parse_direction(args.direction))
        ubersuggest_status = parse_source_status(args.ubersuggest_status)
        answer_status = parse_source_status(args.answer_status)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    capture_manifest: CaptureManifest | None = None
    manifest_path: Path | None = None
    if args.capture_status_json:
        try:
            manifest_path = resolve_path(args.capture_status_json)
            capture_manifest = load_capture_status(manifest_path)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Invalid capture status manifest: {exc}") from exc

    ubersuggest_input = resolve_path(args.ubersuggest_input) if args.ubersuggest_input else None
    answer_input = resolve_path(args.answer_input) if args.answer_input else None
    if capture_manifest and manifest_path is not None:
        ubersuggest_entry = capture_manifest["ubersuggest"]
        answer_entry = capture_manifest["answer_the_public"]
        if ubersuggest_input is None:
            ubersuggest_input = resolve_manifest_artifact(
                ubersuggest_entry,
                manifest_path=manifest_path,
            )
        if answer_input is None:
            answer_input = resolve_manifest_artifact(
                answer_entry,
                manifest_path=manifest_path,
            )
        if ubersuggest_status is None:
            ubersuggest_status = parse_source_status(
                str(ubersuggest_entry.get("issue") or ubersuggest_entry.get("status") or "")
            )
        if answer_status is None:
            answer_status = parse_source_status(
                str(answer_entry.get("issue") or answer_entry.get("status") or "")
            )

    if checkpoint_state:
        prior_statuses = checkpoint_state.get("source_statuses", {})
        if isinstance(prior_statuses, dict):
            if ubersuggest_status is None:
                prior_ubersuggest = prior_statuses.get("ubersuggest", {})
                if isinstance(prior_ubersuggest, dict):
                    ubersuggest_status = (
                        parse_source_status(str(prior_ubersuggest.get("issue")))
                        if prior_ubersuggest.get("issue")
                        else ("ok" if prior_ubersuggest.get("status") == "ok" else None)
                    )
            if answer_status is None:
                prior_answer = prior_statuses.get("answer_the_public", {})
                if isinstance(prior_answer, dict):
                    answer_status = (
                        parse_source_status(str(prior_answer.get("issue")))
                        if prior_answer.get("issue")
                        else ("ok" if prior_answer.get("status") == "ok" else None)
                    )

    ubersuggest_rows: list[JsonMap] = []
    answer_rows: list[JsonMap] = []
    source_statuses: dict[str, SourceState] = {
        source: {"status": "pending", "issue": None} for source in KNOWN_SOURCES
    }

    for source_name, source_path, status_override in (
        ("ubersuggest", ubersuggest_input, ubersuggest_status),
        ("answer_the_public", answer_input, answer_status),
    ):
        rows_target = ubersuggest_rows if source_name == "ubersuggest" else answer_rows
        issue = None if status_override in {None, "ok"} else status_override
        if source_path is not None:
            try:
                artifact = load_artifact(source_path)
                normalized_name = (
                    "answer-the-public" if source_name == "answer_the_public" else source_name
                )
                rows_target.extend(normalize_rows(artifact, normalized_name))
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
        (state["issue"] for state in source_statuses.values() if state["issue"] is not None),
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
        for source_name, state in source_statuses.items():
            if state["issue"] is not None:
                state["status"] = "deferred"
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
    validated_output = validate_opportunity_map(
        output,
        valid_issues=VALID_ISSUES,
        valid_statuses=OUTPUT_STATUSES,
    )
    write_json(output_json, validated_output)
    print(f"Opportunity map written to: {output_json}")
    return 0


def run_command(args: argparse.Namespace) -> int:
    """Execute a fresh run."""
    return execute_pipeline(args)


def resume_command(args: argparse.Namespace) -> int:
    """Resume from a checkpoint."""
    resumed_from = resolve_path(args.resume_from_checkpoint)
    return execute_pipeline(args, resumed_from=resumed_from)


def validate_command(args: argparse.Namespace) -> int:
    """Validate a contract file on disk."""
    path = resolve_path(args.path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if args.kind == "capture-status":
            validate_capture_manifest(data, valid_statuses=VALID_SOURCE_STATUSES)
        elif args.kind == "checkpoint":
            validate_checkpoint_payload(data, valid_issues=VALID_ISSUES)
        else:
            validate_opportunity_map(
                data,
                valid_issues=VALID_ISSUES,
                valid_statuses=OUTPUT_STATUSES,
            )
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"Invalid {args.kind} contract: {exc}") from exc
    print(f"{args.kind} contract is valid: {path}")
    return 0


def init_command(args: argparse.Namespace) -> int:
    """Initialize a runnable workdir scaffold."""
    workdir = resolve_path(args.workdir)
    if workdir.exists() and any(workdir.iterdir()) and not args.force:
        raise SystemExit(
            "Workdir already exists and is not empty: "
            f"{workdir}. Use --force to overwrite scaffold files."
        )

    workdir.mkdir(parents=True, exist_ok=True)
    ubersuggest_path = workdir / "ubersuggest.json"
    answer_path = workdir / "answer-the-public.csv"
    capture_status_path = workdir / "capture-status.json"

    ubersuggest_path.write_text(
        json.dumps(INIT_UBERSUGGEST_SAMPLE, indent=2) + "\n",
        encoding="utf-8",
    )
    answer_path.write_text(INIT_ANSWER_SAMPLE, encoding="utf-8")
    write_json(capture_status_path, INIT_CAPTURE_STATUS)

    manifest = load_capture_status(capture_status_path)
    resolve_manifest_artifact(manifest["ubersuggest"], manifest_path=capture_status_path)
    resolve_manifest_artifact(manifest["answer_the_public"], manifest_path=capture_status_path)

    print(f"Initialized workdir: {workdir}")
    print(f"- capture status: {capture_status_path}")
    print(f"- ubersuggest sample: {ubersuggest_path}")
    print(f"- answer-the-public sample: {answer_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    raw_argv = sys.argv[1:] if argv is None else list(argv)
    normalized_argv = normalize_command_argv(raw_argv)
    args = parser.parse_args(normalized_argv)

    command_fn = getattr(args, "command_fn", None)
    if command_fn is None:
        parser.print_help()
        return 0

    try:
        return command_fn(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
