import subprocess
from pathlib import Path


class RepositoryContext:
    def __init__(self, cwd: Path):
        self.cwd = cwd

    def git_root(self) -> Path:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=True,
                timeout=3,
            )
            return Path(result.stdout.strip()).resolve()
        except Exception:
            return self.cwd

    @staticmethod
    def has_agents_file(root: Path) -> bool:
        return (root / "AGENTS.override.md").is_file() or (root / "AGENTS.md").is_file()
