import re
from pathlib import Path
from typing import Any

from project_context_hook.composer import ComposerUtility
from project_context_hook.io import IOUtility


class ProjectDetector:
    MAPPING = {
        "CMS": {
            "typo3/cms-core": "TYPO3",
            "drupal/core": "Drupal",
            "roots/wordpress": "WordPress/Bedrock",
            "johnpbloch/wordpress-core": "WordPress/Composer",
        },
        "FRAMEWORK": {
            "symfony/framework-bundle": "Symfony",
            "laravel-zero/framework": "Laravel/Laravel Zero",
            "laravel/lumen-framework": "Laravel/Laravel Lumen",
            "laravel/octane": "Laravel/Laravel Octane",
            "laravel/framework": "Laravel",
            "yiisoft/yii2": "Yii2",
            "codeigniter/framework": "CodeIgniter",
            "cakephp/cakephp": "CakePHP",
        },
    }

    def __init__(self, root: Path, composer: ComposerUtility):
        self.root = root
        self.composer = composer

    def detect(self) -> dict[str, Any]:
        if self.composer.is_present():
            return self._detect_from_composer()

        return self._detect_from_files()

    def detect_project_type(self, project: dict[str, Any]) -> str | None:
        """Placeholder for future project type detection."""
        return None

    def _detect_from_composer(self) -> dict[str, Any]:
        for installation_type, packages in self.MAPPING.items():
            for package, name in packages.items():
                version = self.composer.get_package_version(package)
                if not version:
                    continue

                if "/" in name:
                    name, subtype = name.split("/", 1)
                    return {
                        installation_type: name,
                        "Subtype": subtype,
                        "Version": version,
                    }

                return {
                    installation_type: name,
                    "Version": version,
                }

        return {}

    def _detect_from_files(self) -> dict[str, Any]:
        if (self.root / "wp-includes").exists():
            text = IOUtility.read_text(self.root / "wp-includes" / "version.php")
            match = re.search(r"\$wp_version\s*=\s*'([^']+)'", text)

            return {
                "CMS": "WordPress",
                "Version": match.group(1) if match else None,
            }

        if (self.root / "typo3conf").exists():
            return {
                "CMS": "TYPO3",
                "Version": self._detect_typo3_version(),
            }

        return {}

    def _detect_typo3_version(self) -> str:
        legacy_path = self.root / "t3lib/config_default.php"
        modern_path = self.root / "typo3/sysext/core/Classes/Core/SystemEnvironmentBuilder.php"

        if legacy_path.exists():
            text = IOUtility.read_text(legacy_path)
            match = re.search(r"\$TYPO_VERSION\s*=\s*['\"]([^'\"]+)['\"]", text)
            return match.group(1) if match else "3-4"

        if modern_path.exists():
            text = IOUtility.read_text(modern_path)
            pattern = r"define\s*\(\s*['\"]TYPO3_version['\"]\s*,\s*['\"]([^'\"]+)['\"]"
            match = re.search(pattern, text)
            return match.group(1) if match else "6-9"

        return "-"
