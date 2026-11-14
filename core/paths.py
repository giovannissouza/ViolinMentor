import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_resource_path(*parts: str) -> Path:
    bundle_root = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return bundle_root.joinpath(*parts)


def resource_path(*parts: str) -> str:
    return str(get_resource_path(*parts))


def get_data_directory() -> Path:
    if not getattr(sys, "frozen", False):
        return PROJECT_ROOT / "data"
    if sys.platform == "win32":
        base_directory = Path(
            os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        )
    else:
        base_directory = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )
    return base_directory / "ViolinMentor" / "data"
