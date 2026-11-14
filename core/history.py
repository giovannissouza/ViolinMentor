import json
import math
import os
from datetime import datetime
from pathlib import Path

from core.catalog import REPERTOIRE_STATUSES
from core.paths import get_data_directory


class HistoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_data_directory() / "history.json"

    @staticmethod
    def _empty_history() -> dict:
        return {
            "version": 1,
            "repertoire": {},
            "recordings": [],
            "practice_sessions": [],
        }

    def load(self) -> dict:
        if not self.path.exists():
            return self._empty_history()
        try:
            history = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"O arquivo de histórico está inválido: {self.path}") from error
        if not isinstance(history, dict):
            raise ValueError(f"O formato do histórico é inválido: {self.path}")
        if history.get("version") != 1:
            raise ValueError(f"A versão do histórico não é compatível: {self.path}")
        for key, expected_type in (
            ("repertoire", dict),
            ("recordings", list),
            ("practice_sessions", list),
        ):
            if not isinstance(history.get(key), expected_type):
                raise ValueError(f"A seção '{key}' do histórico é inválida: {self.path}")
        if any(
            not isinstance(piece_id, str) or status not in REPERTOIRE_STATUSES
            for piece_id, status in history["repertoire"].items()
        ):
            raise ValueError(f"Há status de repertório inválido no histórico: {self.path}")
        for recording in history["recordings"]:
            if not isinstance(recording, dict):
                raise ValueError(f"Há gravação inválida no histórico: {self.path}")
            self._validate_timestamp(recording.get("timestamp"))
            self._validate_duration(recording.get("duration_seconds"))
            accuracy = recording.get("accuracy_percent")
            if accuracy is not None and (
                not self._is_finite_number(accuracy) or not 0 <= accuracy <= 100
            ):
                raise ValueError(f"Há pontuação de gravação inválida no histórico: {self.path}")
            if not isinstance(recording.get("file"), str):
                raise ValueError(f"Há nome de gravação inválido no histórico: {self.path}")
            if (
                Path(recording["file"]).name != recording["file"]
                or Path(recording["file"]).suffix.lower() != ".wav"
            ):
                raise ValueError(f"Há caminho de gravação inválido no histórico: {self.path}")
            tolerance = recording.get("tolerance_cents", 0)
            self._validate_duration(tolerance)
            if tolerance <= 0:
                raise ValueError(f"Há tolerância de afinação inválida no histórico: {self.path}")
            voiced_frames = recording.get("voiced_frames", 0)
            in_tune_frames = recording.get("in_tune_frames", 0)
            if (
                not isinstance(voiced_frames, int)
                or isinstance(voiced_frames, bool)
                or not isinstance(in_tune_frames, int)
                or isinstance(in_tune_frames, bool)
                or voiced_frames < 0
                or not 0 <= in_tune_frames <= voiced_frames
            ):
                raise ValueError(f"Há contagem de notas inválida no histórico: {self.path}")
        for session in history["practice_sessions"]:
            if not isinstance(session, dict):
                raise ValueError(f"Há sessão de prática inválida no histórico: {self.path}")
            self._validate_timestamp(session.get("timestamp"))
            self._validate_duration(session.get("duration_seconds"))
        return history

    @staticmethod
    def _is_finite_number(value) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )

    def _validate_timestamp(self, value) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Há data inválida no histórico: {self.path}")
        try:
            datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"Há data inválida no histórico: {self.path}") from error

    def _validate_duration(self, value) -> None:
        if not self._is_finite_number(value) or value < 0:
            raise ValueError(f"Há duração inválida no histórico: {self.path}")

    def _save(self, history: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, self.path)

    def add_recording(self, recording: dict) -> None:
        history = self.load()
        history["recordings"].append(recording)
        self._save(history)

    def add_practice_session(self, timestamp: str, duration_seconds: float) -> None:
        if duration_seconds <= 0:
            return
        history = self.load()
        history["practice_sessions"].append(
            {
                "timestamp": timestamp,
                "duration_seconds": round(duration_seconds, 1),
            }
        )
        self._save(history)

    def set_repertoire_status(self, piece_id: str, status: str) -> None:
        if status not in REPERTOIRE_STATUSES:
            raise ValueError(f"Status de repertório inválido: {status}")
        history = self.load()
        history["repertoire"][piece_id] = status
        self._save(history)
