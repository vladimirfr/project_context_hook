import json
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any


class DdevUtility:
    def __init__(self, path: str | Path = "."):
        self.path = path
        self.result = self._describe()

    def is_available(self) -> bool:
        return self.result["status"] == "success"

    def data(self) -> dict[str, Any]:
        return self.result.get("data", {})

    def _describe(self) -> dict[str, Any]:
        result = {
            "status": "error",
        }

        try:
            subprocess_result = subprocess.run(
                ["ddev", "describe", "-j"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            result["status"] = "success"
            result["data"] = json.loads(subprocess_result.stdout).get("raw", {})
        except subprocess.TimeoutExpired:
            result["error"] = "ddev describe timed out"
        except CalledProcessError as error:
            try:
                result["data"] = json.loads(error.stderr).get("msg", "")
            except Exception as nested_error:
                result["error"] = str(nested_error)
        except Exception as error:
            result["error"] = str(error)

        return result
