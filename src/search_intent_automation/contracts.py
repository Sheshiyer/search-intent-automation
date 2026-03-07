"""JSON contract validation helpers for Search Intent Automation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeAlias

KNOWN_SOURCES = ("ubersuggest", "answer_the_public")
VALID_SOURCE_STATE_STATUSES = ("pending", "ok", "blocked", "deferred")

JsonMap: TypeAlias = dict[str, Any]
SourceState: TypeAlias = dict[str, str | None]
CaptureManifest: TypeAlias = dict[str, JsonMap]


def _require_mapping(data: object, label: str) -> JsonMap:
    if not isinstance(data, dict):
        raise ValueError(f"{label} must contain a JSON object.")
    return data


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    return normalized


def _require_optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, label)


def _validate_status(value: object, label: str, valid_values: Sequence[str]) -> str:
    normalized = _require_string(value, label).lower()
    if normalized not in valid_values:
        expected = ", ".join(valid_values)
        raise ValueError(f"{label} must be one of: {expected}.")
    return normalized


def validate_source_statuses(
    data: object,
    *,
    valid_issues: Sequence[str],
) -> dict[str, SourceState]:
    """Validate a `source_statuses` mapping."""
    mapping = _require_mapping(data, "source_statuses")
    missing_sources = [source for source in KNOWN_SOURCES if source not in mapping]
    if missing_sources:
        missing = ", ".join(missing_sources)
        raise ValueError(f"source_statuses is missing required sources: {missing}.")

    validated: dict[str, SourceState] = {}
    for source in KNOWN_SOURCES:
        entry = _require_mapping(mapping[source], f"source_statuses.{source}")
        status = _validate_status(
            entry.get("status"),
            f"source_statuses.{source}.status",
            VALID_SOURCE_STATE_STATUSES,
        )
        issue_value = entry.get("issue")
        issue = None
        if issue_value is not None:
            issue = _validate_status(
                issue_value,
                f"source_statuses.{source}.issue",
                valid_issues,
            )
        validated[source] = {"status": status, "issue": issue}
    return validated


def validate_capture_manifest(
    data: object,
    *,
    valid_statuses: Sequence[str],
) -> CaptureManifest:
    """Validate and normalize a capture-status manifest."""
    mapping = _require_mapping(data, "capture status manifest")
    missing_sources = [source for source in KNOWN_SOURCES if source not in mapping]
    if missing_sources:
        missing = ", ".join(missing_sources)
        raise ValueError(f"capture status manifest is missing required sources: {missing}.")

    validated: CaptureManifest = {}
    for source in KNOWN_SOURCES:
        raw_entry = mapping[source]
        if isinstance(raw_entry, str):
            validated[source] = {
                "status": _validate_status(
                    raw_entry,
                    f"capture status manifest.{source}.status",
                    valid_statuses,
                ),
                "artifact": None,
                "issue": None,
            }
            continue

        entry = _require_mapping(raw_entry, f"capture status manifest.{source}")
        artifact = entry.get("artifact")
        if artifact is not None and not isinstance(artifact, str):
            raise ValueError(f"capture status manifest.{source}.artifact must be a string or null.")
        issue_value = entry.get("issue")
        issue = None
        if issue_value is not None:
            issue = _validate_status(
                issue_value,
                f"capture status manifest.{source}.issue",
                valid_statuses,
            )
        validated[source] = {
            "status": _validate_status(
                entry.get("status"),
                f"capture status manifest.{source}.status",
                valid_statuses,
            ),
            "artifact": artifact,
            "issue": issue,
        }
    return validated


def validate_checkpoint_payload(
    data: object,
    *,
    valid_issues: Sequence[str],
) -> JsonMap:
    """Validate a checkpoint payload."""
    payload = _require_mapping(data, "checkpoint payload")
    checkpoint_status = _require_string(payload.get("status"), "checkpoint payload.status")
    if checkpoint_status != "needs_user_direction":
        raise ValueError("checkpoint payload.status must be 'needs_user_direction'.")

    taxonomy = _validate_status(
        payload.get("taxonomy"),
        "checkpoint payload.taxonomy",
        valid_issues,
    )
    _require_string(payload.get("seed"), "checkpoint payload.seed")
    _require_string(payload.get("goal"), "checkpoint payload.goal")
    _require_string(payload.get("workdir"), "checkpoint payload.workdir")
    _require_string(
        payload.get("recommended_option_1"),
        "checkpoint payload.recommended_option_1",
    )
    _require_string(
        payload.get("recommended_option_2"),
        "checkpoint payload.recommended_option_2",
    )
    _require_string(payload.get("custom_direction"), "checkpoint payload.custom_direction")
    selected_direction = payload.get("selected_direction")
    if selected_direction is not None:
        _require_string(selected_direction, "checkpoint payload.selected_direction")
    if not isinstance(payload.get("exit_code"), int):
        raise ValueError("checkpoint payload.exit_code must be an integer.")
    _require_string(payload.get("generated_at"), "checkpoint payload.generated_at")

    decision_prompt = _require_mapping(
        payload.get("decision_prompt"),
        "checkpoint payload.decision_prompt",
    )
    prompt_taxonomy = _validate_status(
        decision_prompt.get("taxonomy"),
        "checkpoint payload.decision_prompt.taxonomy",
        valid_issues,
    )
    if prompt_taxonomy != taxonomy:
        raise ValueError("checkpoint payload.decision_prompt.taxonomy must match taxonomy.")
    options = decision_prompt.get("options")
    if not isinstance(options, list) or len(options) != 3:
        raise ValueError("checkpoint payload.decision_prompt.options must contain three options.")
    for index, option in enumerate(options, start=1):
        option_map = _require_mapping(
            option,
            f"checkpoint payload.decision_prompt.options[{index}]",
        )
        _require_string(
            option_map.get("id"),
            f"checkpoint payload.decision_prompt.options[{index}].id",
        )
        _require_string(
            option_map.get("label"),
            f"checkpoint payload.decision_prompt.options[{index}].label",
        )

    resume_hints = _require_mapping(
        payload.get("resume_hints"),
        "checkpoint payload.resume_hints",
    )
    _require_string(
        resume_hints.get("recommended_1"),
        "checkpoint payload.resume_hints.recommended_1",
    )
    _require_string(
        resume_hints.get("recommended_2"),
        "checkpoint payload.resume_hints.recommended_2",
    )
    _require_string(resume_hints.get("custom"), "checkpoint payload.resume_hints.custom")
    _require_optional_string(
        resume_hints.get("resume_from"),
        "checkpoint payload.resume_hints.resume_from",
    )

    validate_source_statuses(payload.get("source_statuses"), valid_issues=valid_issues)
    return payload


def validate_opportunity_map(
    data: object,
    *,
    valid_issues: Sequence[str],
    valid_statuses: Sequence[str],
) -> JsonMap:
    """Validate an opportunity-map payload."""
    payload = _require_mapping(data, "opportunity map")
    _validate_status(payload.get("status"), "opportunity map.status", valid_statuses)
    _require_string(payload.get("seed"), "opportunity map.seed")
    _require_string(payload.get("goal"), "opportunity map.goal")
    direction = payload.get("direction")
    if direction is not None:
        _require_string(direction, "opportunity map.direction")
    _require_optional_string(
        payload.get("resumed_from_checkpoint"),
        "opportunity map.resumed_from_checkpoint",
    )
    _require_string(payload.get("generated_at"), "opportunity map.generated_at")

    source_counts = _require_mapping(payload.get("source_counts"), "opportunity map.source_counts")
    for source in KNOWN_SOURCES:
        if source not in source_counts:
            raise ValueError(f"opportunity map.source_counts is missing '{source}'.")
        if not isinstance(source_counts[source], int):
            raise ValueError(f"opportunity map.source_counts.{source} must be an integer.")

    validate_source_statuses(payload.get("source_statuses"), valid_issues=valid_issues)

    deferred_sources = payload.get("deferred_sources")
    if not isinstance(deferred_sources, list):
        raise ValueError("opportunity map.deferred_sources must be a list.")
    for index, source in enumerate(deferred_sources, start=1):
        normalized = _validate_status(
            source,
            f"opportunity map.deferred_sources[{index}]",
            KNOWN_SOURCES,
        )
        if normalized not in KNOWN_SOURCES:
            raise ValueError(f"opportunity map.deferred_sources[{index}] is unknown.")

    if not isinstance(payload.get("review_required"), bool):
        raise ValueError("opportunity map.review_required must be a boolean.")

    opportunity_map = _require_mapping(
        payload.get("opportunity_map"),
        "opportunity map.opportunity_map",
    )
    for key in ("keyword_rows", "question_rows"):
        rows = opportunity_map.get(key)
        if not isinstance(rows, list):
            raise ValueError(f"opportunity map.opportunity_map.{key} must be a list.")
        for index, row in enumerate(rows, start=1):
            _require_mapping(row, f"opportunity map.opportunity_map.{key}[{index}]")

    notes = payload.get("notes")
    if not isinstance(notes, list) or not notes:
        raise ValueError("opportunity map.notes must be a non-empty list.")
    for index, note in enumerate(notes, start=1):
        _require_string(note, f"opportunity map.notes[{index}]")
    return payload
