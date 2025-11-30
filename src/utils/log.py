import datetime


def log_info(message: str):
    """Lightweight console logger for info messages."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {timestamp} - {message}")


def log_error(message: str):
    """Lightweight console logger for error messages."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERROR] {timestamp} - {message}")
