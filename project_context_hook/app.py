import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from project_context_hook.composer import ComposerUtility
from project_context_hook.ddev import DdevUtility
from project_context_hook.io import IOUtility
from project_context_hook.notifier import NotificationUtility
from project_context_hook.project import ProjectDetector
from project_context_hook.renderer import MarkdownRenderer
from project_context_hook.repository import RepositoryContext
from project_context_hook.templates import PromptTemplateResolver


class ProjectContextHookApp:
    def run(self) -> None:
        payload = IOUtility.read_input()
        cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
        root = RepositoryContext(cwd).git_root()

        if RepositoryContext.has_agents_file(root):
            NotificationUtility.notify(
                payload.get("model", "Codex"),
                f"AGENTS.md already exists in {str(root)}",
            )
            self._write_hook_output(payload, "")
            return

        composer = ComposerUtility(root / "composer.lock")
        detector = ProjectDetector(root, composer)
        project_info = detector.detect()

        if not project_info:
            NotificationUtility.notify("Codex", "Unknown project type")
            self._write_hook_output(payload, "")
            return

        ddev = DdevUtility(root)
        variables = self._build_variables(root, composer, ddev, project_info)
        template = PromptTemplateResolver(root, project_info, detector, ddev.is_available()).resolve()
        content = MarkdownRenderer(template, variables).render()

        NotificationUtility.notify("Project Context", content)
        self._write_hook_output(payload, content)

    def _build_variables(
        self,
        root: Path,
        composer: ComposerUtility,
        ddev: DdevUtility,
        project_info: dict[str, Any],
    ) -> dict[str, Any]:
        variables: dict[str, Any] = {
            "DATETIME": datetime.now().isoformat(),
            "ROOT": str(root),
        }
        tooling: list[str] = []
        runtime: dict[str, Any] = {}
        environment: dict[str, Any] = {}

        if composer.is_present():
            tooling.append(f"Composer {composer.get_version()}")

        if ddev.is_available():
            tooling.append("DDEV")
            ddev_data = ddev.data()

            runtime["PHP"] = ddev_data.get("php_version", "-")
            runtime["Web server"] = ddev_data.get("webserver_type", "-")

            if ddev_data.get("dbinfo", {}):
                runtime["Database"] = "{type} {version}".format(
                    type=ddev_data.get("database_type", "-"),
                    version=ddev_data.get("database_version", "-"),
                )

            variables["DDEV"] = ddev_data
            variables["ROOT"] = ddev_data.get("shortroot", "")
            variables["DOCROOT"] = ddev_data.get("docroot", "")
            environment["Hostname"] = ddev_data.get("hostname", "")

        environment["Tooling"] = ", ".join(tooling)

        variables["ENVIRONMENT"] = environment
        variables["RUNTIME"] = runtime
        variables["PROJECT"] = project_info

        return variables

    @staticmethod
    def _write_hook_output(payload: dict[str, Any], content: str) -> None:
        event = payload.get("hook_event_name")
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": content,
            },
        }, sys.stdout)

        sys.stdout.write("\n")
