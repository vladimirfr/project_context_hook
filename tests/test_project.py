import json
import tempfile
import unittest
from pathlib import Path

from project_context_hook.composer import ComposerUtility
from project_context_hook.project import ProjectDetector


class ProjectDetectorTest(unittest.TestCase):
    def test_detects_composer_cms_subtype(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "composer.lock").write_text(
                json.dumps({
                    "packages": [
                        {"name": "roots/wordpress", "version": "6.5.0"},
                    ],
                }),
                encoding="utf-8",
            )

            detector = ProjectDetector(root, ComposerUtility(root / "composer.lock"))

            self.assertEqual(
                detector.detect(),
                {
                    "CMS": "WordPress",
                    "Subtype": "Bedrock",
                    "Version": "6.5.0",
                },
            )

    def test_detects_filesystem_wordpress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wp_includes = root / "wp-includes"
            wp_includes.mkdir()
            (wp_includes / "version.php").write_text(
                "<?php\n$wp_version = '6.5.3';\n",
                encoding="utf-8",
            )

            detector = ProjectDetector(root, ComposerUtility(root / "composer.lock"))

            self.assertEqual(
                detector.detect(),
                {
                    "CMS": "WordPress",
                    "Version": "6.5.3",
                },
            )

    def test_project_type_is_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            detector = ProjectDetector(root, ComposerUtility(root / "composer.lock"))

            self.assertIsNone(detector.detect_project_type({}))


if __name__ == "__main__":
    unittest.main()
