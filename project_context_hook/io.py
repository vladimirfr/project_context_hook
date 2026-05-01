import json
import sys
from pathlib import Path
from typing import Any


class IOUtility:
    @staticmethod
    def read_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    @staticmethod
    def read_json(path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {}

        try:
            return json.loads(IOUtility.read_text(path))
        except Exception:
            return {}

    @staticmethod
    def read_input() -> dict[str, Any]:
        try:
            return json.load(sys.stdin)
        except Exception:
            return {}
