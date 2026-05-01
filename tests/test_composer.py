import json
import tempfile
import unittest
from pathlib import Path

from project_context_hook.composer import ComposerUtility


class ComposerUtilityTest(unittest.TestCase):
    def test_reads_packages_from_lock_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_path = Path(temp_dir) / "composer.lock"
            lock_path.write_text(
                json.dumps({
                    "plugin-api-version": "2.6.0",
                    "packages": [
                        {"name": "laravel/framework", "version": "11.0.0"},
                    ],
                    "packages-dev": [
                        {"name": "phpunit/phpunit", "version": "10.5.0"},
                    ],
                }),
                encoding="utf-8",
            )

            composer = ComposerUtility(lock_path)

            self.assertTrue(composer.is_present())
            self.assertEqual(composer.get_version(), "2.6.0")
            self.assertEqual(composer.get_package_version("laravel/framework"), "11.0.0")
            self.assertEqual(composer.get_package_version("phpunit/phpunit"), "10.5.0")

    def test_missing_lock_file_is_not_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            composer = ComposerUtility(Path(temp_dir) / "composer.lock")

            self.assertFalse(composer.is_present())
            self.assertEqual(composer.get_version(), "2")
            self.assertIsNone(composer.get_package_version("laravel/framework"))


if __name__ == "__main__":
    unittest.main()
