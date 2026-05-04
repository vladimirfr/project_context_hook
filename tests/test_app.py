import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from project_context_hook.app import ProjectContextHookApp


class ProjectContextHookAppTest(unittest.TestCase):
    def test_unknown_non_git_project_writes_empty_hook_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = self._run_app({
                "cwd": temp_dir,
                "hook_event_name": "SessionStart",
                "model": "Codex",
            })

            self.assertEqual(
                json.loads(output),
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "",
                    },
                },
            )

    def test_existing_agents_file_writes_empty_hook_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")

            output = self._run_app({
                "cwd": temp_dir,
                "hook_event_name": "SessionStart",
                "model": "Codex",
            })

            self.assertEqual(
                json.loads(output),
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "",
                    },
                },
            )

    @staticmethod
    def _run_app(payload: dict[str, str]) -> str:
        stdin = io.StringIO(json.dumps(payload))
        stdout = io.StringIO()

        with (
            patch("sys.stdin", stdin),
            patch("project_context_hook.app.NotificationUtility.notify"),
            redirect_stdout(stdout),
        ):
            ProjectContextHookApp().run()

        return stdout.getvalue()


if __name__ == "__main__":
    unittest.main()
