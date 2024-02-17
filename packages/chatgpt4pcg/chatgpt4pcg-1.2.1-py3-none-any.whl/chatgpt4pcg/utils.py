from datetime import datetime
from pathlib import Path


def log(log_path: Path, message: str):
    """
    Log a message.
    :param log_path: path to log file
    :param message: message to log
    :return: None
    """
    open(log_path, "a").write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
