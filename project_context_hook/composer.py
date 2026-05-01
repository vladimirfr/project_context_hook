from pathlib import Path
from typing import Any

from project_context_hook.io import IOUtility


class ComposerUtility:
    def __init__(self, path: Path):
        composer = IOUtility.read_json(path)
        self._has_lock = len(composer) > 0

        if self._has_lock:
            self.version = composer.get("plugin-api-version", "2")
            self.packages = self._read_packages(composer)
        else:
            self.version = "2"
            self.packages = {}

    @staticmethod
    def _read_packages(composer: dict[str, Any]) -> dict[str, str]:
        return {
            package["name"]: package["version"]
            for section in ("packages", "packages-dev")
            for package in composer.get(section, [])
        }

    def is_present(self) -> bool:
        return self._has_lock

    def get_version(self) -> str:
        return self.version

    def get_package_version(self, package: str) -> str | None:
        return self.packages.get(package)
