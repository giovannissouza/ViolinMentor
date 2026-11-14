import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ICON_PATH = PROJECT_ROOT / "assets" / "violino.ico"
OUTPUT_DIRECTORY = PROJECT_ROOT / "dist" / "ViolinMentor"


def main() -> None:
    if os.name != "nt":
        raise SystemExit("Este script de empacotamento foi preparado para Windows.")

    if not ICON_PATH.is_file():
        raise FileNotFoundError(f"Ícone necessário não encontrado: {ICON_PATH}")

    if importlib.util.find_spec("PyInstaller") is None:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pyinstaller>=6.10,<7.0",
            ],
            check=True,
        )

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="violinmentor-build-") as temporary:
        staged_data = Path(temporary) / "data"
        staged_data.mkdir()
        (staged_data / "README.txt").write_text(
            "Runtime data is stored in the user's local application data folder.\n",
            encoding="utf-8",
        )

        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--noconsole",
            "--onefile",
            "--name=ViolinMentor",
            f"--icon={ICON_PATH}",
            f"--specpath={PROJECT_ROOT / 'build'}",
            f"--distpath={OUTPUT_DIRECTORY}",
            f"--add-data={PROJECT_ROOT / 'assets'};assets",
            f"--add-data={staged_data};data",
            "--collect-all=customtkinter",
            "--collect-data=matplotlib",
            "--collect-all=PIL",
            "--collect-all=_sounddevice_data",
            str(PROJECT_ROOT / "main.py"),
        ]
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)

    executable = OUTPUT_DIRECTORY / "ViolinMentor.exe"
    if not executable.is_file():
        raise FileNotFoundError(f"PyInstaller não gerou o executável esperado: {executable}")
    print(f"Executável criado: {executable}")


if __name__ == "__main__":
    main()
