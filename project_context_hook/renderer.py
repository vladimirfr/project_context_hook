import re
from pathlib import Path
from string import Template
from typing import Any

from project_context_hook.io import IOUtility


class MarkdownRenderer:
    _IF_ELSE_RE = re.compile(
        r"{%\s*if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*%}"
        r"(.*?)"
        r"(?:{%\s*else\s*%}(.*?))?"
        r"{%\s*endif\s*%}",
        re.DOTALL,
    )

    def __init__(self, path: Path, variables: dict[str, Any]):
        self.template_path = path
        self.variables = variables
        self._template: str | None = None

    @staticmethod
    def _format_dict(data: dict[str, Any]) -> str:
        return "\n".join([f" - {key}: {value}" for key, value in data.items()])

    def _replace_if(self, match: re.Match[str]) -> str:
        name = match.group(1)
        true_body = match.group(2)
        false_body = match.group(3) or ""
        return true_body if self.variables.get(name) else false_body

    def _prepare_variables(self) -> dict[str, str]:
        prepared: dict[str, str] = {}

        for key, value in self.variables.items():
            if isinstance(value, dict):
                prepared[key] = self._format_dict(value)
            elif value is None:
                prepared[key] = ""
            else:
                prepared[key] = str(value)

        return prepared

    def _render_md(self) -> str:
        variables = self._prepare_variables()
        processed = self._IF_ELSE_RE.sub(self._replace_if, self._template or "")
        result = Template(processed).safe_substitute(variables)

        return re.sub(r"\n{3,}", "\n\n", result).strip()

    def render(self) -> str:
        if self._template is None:
            self._template = IOUtility.read_text(self.template_path)

        return self._render_md()
