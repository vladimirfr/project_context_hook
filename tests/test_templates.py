import tempfile
import unittest
from pathlib import Path

import project_context_hook.templates as templates
from project_context_hook.composer import ComposerUtility
from project_context_hook.project import ProjectDetector
from project_context_hook.templates import PromptTemplateResolver


class ProjectTypeDetector(ProjectDetector):
    def detect_project_type(self, project: dict) -> str | None:
        return "Ecommerce"


class PromptTemplateResolverTest(unittest.TestCase):
    def test_ddev_template_wins_over_no_ddev_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_root = Path(temp_dir)
            self._patch_template_paths(prompts_root)

            ddev_template = prompts_root / "ddev" / "CMS" / "WordPress" / "Bedrock.md"
            no_ddev_template = prompts_root / "no_ddev" / "CMS" / "WordPress.md"
            ddev_template.parent.mkdir(parents=True)
            no_ddev_template.parent.mkdir(parents=True)
            ddev_template.write_text("ddev bedrock", encoding="utf-8")
            no_ddev_template.write_text("wordpress", encoding="utf-8")

            detector = ProjectDetector(prompts_root, ComposerUtility(prompts_root / "composer.lock"))
            resolver = PromptTemplateResolver(
                prompts_root,
                {"CMS": "WordPress", "Subtype": "Bedrock"},
                detector,
                True,
            )

            self.assertEqual(resolver.resolve(), ddev_template)

    def test_project_type_template_wins_before_cms_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_root = Path(temp_dir)
            self._patch_template_paths(prompts_root)

            project_type_template = prompts_root / "no_ddev" / "Ecommerce.md"
            cms_template = prompts_root / "no_ddev" / "CMS" / "WordPress.md"
            project_type_template.parent.mkdir(parents=True)
            cms_template.parent.mkdir(parents=True)
            project_type_template.write_text("ecommerce", encoding="utf-8")
            cms_template.write_text("wordpress", encoding="utf-8")

            detector = ProjectTypeDetector(prompts_root, ComposerUtility(prompts_root / "composer.lock"))
            resolver = PromptTemplateResolver(
                prompts_root,
                {"CMS": "WordPress"},
                detector,
                False,
            )

            self.assertEqual(resolver.resolve(), project_type_template)

    def test_base_template_is_final_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_root = Path(temp_dir)
            base_template = self._patch_template_paths(prompts_root)

            detector = ProjectDetector(prompts_root, ComposerUtility(prompts_root / "composer.lock"))
            resolver = PromptTemplateResolver(
                prompts_root,
                {"CMS": "Drupal"},
                detector,
                False,
            )

            self.assertEqual(resolver.resolve(), base_template)

    @staticmethod
    def _patch_template_paths(prompts_root: Path) -> Path:
        base_template = prompts_root / "BASE.md"
        base_template.write_text("base", encoding="utf-8")
        templates.PROMPTS_ROOT = prompts_root
        templates.BASE_PROMPT = base_template
        return base_template


if __name__ == "__main__":
    unittest.main()
