import shutil
import subprocess


class NotificationUtility:
    @staticmethod
    def notify(title: str, message: str) -> None:
        if not shutil.which("notify-send"):
            return

        try:
            subprocess.run(
                ["notify-send", title, message],
                check=False,
                capture_output=True,
                timeout=3,
            )
        except OSError:
            pass
