import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEGACY_ANDROID_DATA_DIR = Path("/storage/emulated/0/csbot/cs4")


def resolve_data_file(filename: str) -> Path:
    env_data_dir = os.getenv("BOT_DATA_DIR")
    candidates = [
        DATA_DIR / filename,
        Path(env_data_dir) / filename if env_data_dir else None,
        LEGACY_ANDROID_DATA_DIR / filename,
    ]

    for path in candidates:
        if path and path.exists():
            return path

    checked = ", ".join(str(path) for path in candidates if path)
    raise FileNotFoundError(
        f"Required data file not found: {filename}. Checked: {checked}"
    )


BUTTONS_PATH = resolve_data_file("terms_btn2cmd.json")
VALUES_PATH = resolve_data_file("terms_cmd2values.json")
