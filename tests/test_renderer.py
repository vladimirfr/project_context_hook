import tempfile
import unittest
from pathlib import Path

from project_context_hook.renderer import MarkdownRenderer


class MarkdownRendererTest(unittest.TestCase):
    def test_renders_variables_dicts_and_conditionals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            template = Path(temp_dir) / "template.md"
            template.write_text(
                "Hello $NAME\n\n"
                "{% if PROJECT %}\n"
                "Project:\n"
                "$PROJECT\n"
                "{% else %}\n"
                "No project\n"
                "{% endif %}",
                encoding="utf-8",
            )

            content = MarkdownRenderer(
                template,
                {
                    "NAME": "Codex",
                    "PROJECT": {
                        "CMS": "WordPress",
                        "Version": "6.5.3",
                    },
                },
            ).render()

            self.assertEqual(
                content,
                "Hello Codex\n\nProject:\n - CMS: WordPress\n - Version: 6.5.3",
            )


if __name__ == "__main__":
    unittest.main()
