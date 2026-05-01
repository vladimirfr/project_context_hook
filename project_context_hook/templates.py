import re
from pathlib import Path
from typing import Any

from project_context_hook.paths import BASE_PROMPT, PROMPTS_ROOT
from project_context_hook.project import ProjectDetector


class PromptTemplateResolver:
    def __init__(self, root: Path, project: dict[str, Any], detector: ProjectDetector, has_ddev: bool):
        self.root = root
        self.project = project
        self.detector = detector
        self.has_ddev = has_ddev

    def resolve(self) -> Path:
        for directory in self._directories():
            for candidate in self._template_candidates(directory):
                if candidate.is_file():
                    return candidate

        return BASE_PROMPT

    def _directories(self) -> list[Path]:
        if self.has_ddev:
            return [PROMPTS_ROOT / "ddev", PROMPTS_ROOT / "no_ddev"]

        return [PROMPTS_ROOT / "no_ddev"]

    def _template_candidates(self, directory: Path) -> list[Path]:
        candidates: list[Path] = []

        project_type = self.detector.detect_project_type(self.project)
        if project_type:
            candidates.append(directory / f"{self._template_name(project_type)}.md")

        family = self._project_family()
        if family:
            family_name, family_value = family
            family_value_name = self._template_name(family_value)

            subtype = self.project.get("Subtype")
            if subtype:
                subtype_name = self._template_name(subtype)
                candidates.extend([
                    directory / family_name / family_value_name / f"{subtype_name}.md",
                    directory / family_name / f"{family_value_name}-{subtype_name}.md",
                ])

            candidates.extend([
                directory / family_name / f"{family_value_name}.md",
                directory / f"{family_value_name}.md",
            ])

        return candidates

    def _project_family(self) -> tuple[str, str] | None:
        for family in ("CMS", "FRAMEWORK"):
            value = self.project.get(family)
            if value:
                return family, str(value)

        return None

    @staticmethod
    def _template_name(value: Any) -> str:
        name = str(value).strip()
        name = name.replace("/", "-")
        name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name)
        return name.strip("-")
