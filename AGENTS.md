# Project Context Hook

## Scope

This project implements a Codex hook that detects project context and renders Markdown session context from templates.

## Working Rules

- Keep `main.py` as a thin executable entry point.
- Put application logic inside the `project_context_hook/` package.
- Keep prompt templates in `prompts/`.
- Do not add runtime dependencies unless the hook genuinely needs them.
- Prefer standard-library tests unless a dependency is already justified.
- Preserve the hook contract: read JSON from stdin and write hook output JSON to stdout.

## Checks

Run these before finishing code changes:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile main.py project_context_hook/*.py tests/*.py
```

If dev dependencies are installed, also run:

```bash
ruff check .
ruff format --check .
```
