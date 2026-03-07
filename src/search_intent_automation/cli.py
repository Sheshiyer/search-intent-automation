"""CLI entrypoints for Search Intent Automation."""

from __future__ import annotations

from collections.abc import Sequence

from .pipeline import main as pipeline_main


def main(argv: Sequence[str] | None = None) -> int:
    """Run the primary CLI."""
    return pipeline_main(argv)
