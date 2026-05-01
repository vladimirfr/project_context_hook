# Project Context Hook

This hook detects basic project context and returns it to Codex as additional session context.

It is intended to run from a Codex hook payload. The hook reads JSON from standard input, detects the current project root, identifies the CMS or framework, gathers runtime details when DDEV is available, renders a Markdown prompt template, and writes the hook output JSON to standard output.

## Enable hook

1. Put project inside hooks directory `~/.codex/hooks/`
2. Add Hook registration to Codex config `~/.codex/config.toml`

```toml
[features]
codex_hooks = true

[[hooks.SessionStart]]
matcher = "startup"

[[hooks.SessionStart.hooks]]
type = "command"
command = "python3 ~/.codex/hooks/project_context_hook/main.py"
timeout = 10
statusMessage = "Add project context"
```

## Entry Point

Run the hook with:

```bash
python3 main.py
```

The script expects a JSON payload on standard input. The most important payload fields are:

- `cwd`: working directory for the active project.
- `model`: model name used in desktop notifications.
- `hook_event_name`: hook event name echoed in the hook output.

## Module Layout

- `main.py`: thin executable entry point.
- `project_context_hook/app.py`: application orchestration.
- `project_context_hook/project.py`: CMS and framework detection.
- `project_context_hook/templates.py`: prompt template resolution.
- `project_context_hook/renderer.py`: Markdown template rendering.
- `project_context_hook/ddev.py`: DDEV environment discovery.
- `project_context_hook/composer.py`: Composer lock parsing.
- `project_context_hook/repository.py`: git root and AGENTS file checks.
- `project_context_hook/io.py`: JSON and text file helpers.
- `project_context_hook/notifier.py`: desktop notifications.
- `project_context_hook/paths.py`: shared filesystem paths.

## Template Resolution

Templates live in `prompts/`.

The base fallback is:

```text
prompts/BASE.md
```

DDEV projects are resolved first from:

```text
prompts/ddev/
```

If no DDEV-specific template is found, the resolver falls back to:

```text
prompts/no_ddev/
```

Non-DDEV projects only use `prompts/no_ddev/`.

Within the selected directory, templates are checked in this order:

1. Future project type template.
2. CMS or framework subtype template.
3. CMS or framework template.
4. `prompts/BASE.md`.

Examples:

```text
prompts/ddev/CMS/WordPress/Bedrock.md
prompts/ddev/CMS/WordPress-Bedrock.md
prompts/ddev/CMS/WordPress.md
prompts/ddev/WordPress.md
prompts/no_ddev/CMS/WordPress.md
```

The future project type hook is currently implemented as `ProjectDetector.detect_project_type(...)` and returns `None`.

## Supported Detection

Composer-based detection currently supports:

- TYPO3
- Drupal
- WordPress Bedrock
- WordPress Composer
- Symfony
- Laravel variants
- Yii2
- CodeIgniter
- CakePHP

Filesystem-based fallback detection currently supports:

- WordPress
- TYPO3

## Development Checks

The test suite uses standard-library `unittest` and can also be run by `pytest` when dev dependencies are installed.

Run the local checks that do not require extra packages:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile main.py project_context_hook/*.py tests/*.py
```

Install optional development tools with:

```bash
python3 -m pip install -e ".[dev]"
```

Run linting and format checks with:

```bash
ruff check .
ruff format --check .
```
