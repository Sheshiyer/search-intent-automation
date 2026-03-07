# Development

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Quality loop

```bash
ruff check .
mypy src
pytest
python -m build
python -m twine check dist/*
./scripts/smoke-examples.sh
```

## Layout

- `src/search_intent_automation/`: package code
- `tests/`: unit and integration tests
- `docs/`: public docs
- `examples/`: sample manifests and fixture artifacts
