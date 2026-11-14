import math
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd

from core.paths import get_data_directory


class AudioCaptureError(RuntimeError):
    """Falha ao iniciar ou encerrar a captura de áudio."""


@dataclass(frozen=True)
class RecordingResult:
    path: Path
    timestamp: str
    duration_seconds: float
    accuracy_percent: float | None
    voiced_frames: int
    in_tune_frames: int
    tolerance_cents: float
    warnings: tuple[str, ...]

    def to_history_entry(self) -> dict:
        return {
            "file": self.path.name,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "accuracy_percent": self.accuracy_percent,
            "voiced_frames": self.voiced_frames,
            "in_tune_frames": self.in_tune_frames,
            "tolerance_cents": self.tolerance_cents,
            "warnings": list(self.warnings),
        }


class AudioRecorder:
    SAMPLE_RATE = 44100
    TUNING_TOLERANCE_CENTS = 20.0
    FRAME_SIZE = 4096
    HOP_SIZE = 2048
    MIN_FREQUENCY = 150.0
    MAX_FREQUENCY = 1500.0

    def __init__(self, recordings_directory: Path | None = None) -> None:
        self.recordings_directory = recordings_directory or (
            get_data_directory() / "recordings"
        )
        self._stream = None
        self._chunks = []
        self._started_at = None
        self._warnings = []

    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    def _capture(self, audio, frames, time_info, status) -> None:
        if status:
            self._warnings.append(str(status))
        self._chunks.append(bytes(audio))

    def start(self) -> None:
        if self.is_recording:
            raise AudioCaptureError("Já existe uma gravação em andamento.")
        self._chunks = []
        self._warnings = []
        stream = None
        try:
            stream = sd.RawInputStream(
                samplerate=self.SAMPLE_RATE,
                channels=1,
                dtype="int16",
                callback=self._capture,
            )
            stream.start()
        except (sd.PortAudioError, ValueError) as error:
            if stream is not None:
                try:
                    stream.close()
                except sd.PortAudioError as close_error:
                    raise AudioCaptureError(
                        f"Não foi possível iniciar o microfone: {error}. "
                        f"Também houve falha ao liberar o dispositivo: {close_error}"
                    ) from error
            raise AudioCaptureError(f"Não foi possível iniciar o microfone: {error}") from error
        self._stream = stream
        self._started_at = datetime.now().astimezone()

    def stop(self) -> RecordingResult:
        if not self.is_recording:
            raise AudioCaptureError("Não há gravação em andamento.")
        stream = self._stream
        errors = []
        try:
            stream.stop()
        except sd.PortAudioError as error:
            errors.append(error)
        try:
            stream.close()
        except sd.PortAudioError as error:
            errors.append(error)
        self._stream = None
        if errors:
            self._chunks = []
            details = "; ".join(str(error) for error in errors)
            raise AudioCaptureError(f"Falha ao encerrar a captura de áudio: {details}")

        audio_size = sum(len(chunk) for chunk in self._chunks)
        if not audio_size:
            self._chunks = []
            raise AudioCaptureError("Nenhum áudio foi capturado pelo microfone.")
        started_at = self._started_at
        timestamp = started_at.isoformat(timespec="seconds")
        filename = started_at.strftime("%Y%m%d_%H%M%S_%f") + ".wav"
        self.recordings_directory.mkdir(parents=True, exist_ok=True)
        recording_path = self.recordings_directory / filename
        try:
            with wave.open(str(recording_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.SAMPLE_RATE)
                for chunk in self._chunks:
                    wav_file.writeframesraw(chunk)
        except (OSError, wave.Error) as error:
            self._chunks = []
            raise AudioCaptureError(f"Não foi possível salvar o arquivo WAV: {error}") from error

        self._chunks = []
        self._started_at = None
        accuracy, voiced_frames, in_tune_frames = self._analyze_wav(recording_path)
        duration = audio_size / (2 * self.SAMPLE_RATE)
        return RecordingResult(
            path=recording_path,
            timestamp=timestamp,
            duration_seconds=round(duration, 2),
            accuracy_percent=accuracy,
            voiced_frames=voiced_frames,
            in_tune_frames=in_tune_frames,
            tolerance_cents=self.TUNING_TOLERANCE_CENTS,
            warnings=tuple(self._warnings),
        )

    def analyze_tuning(self, audio: bytes) -> tuple[float | None, int, int]:
        samples = np.frombuffer(audio, dtype=np.int16).astype(np.float32)
        voiced_frames, in_tune_frames = self._analyze_samples(samples)
        return self._score(voiced_frames, in_tune_frames)

    def _analyze_wav(self, recording_path: Path) -> tuple[float | None, int, int]:
        voiced_frames = 0
        in_tune_frames = 0
        carry = b""
        try:
            with wave.open(str(recording_path), "rb") as wav_file:
                while True:
                    audio_chunk = wav_file.readframes(65536)
                    if not audio_chunk:
                        break
                    buffered_audio = carry + audio_chunk
                    samples = np.frombuffer(buffered_audio, dtype=np.int16).astype(np.float32)
                    chunk_voiced, chunk_in_tune = self._analyze_samples(samples)
                    voiced_frames += chunk_voiced
                    in_tune_frames += chunk_in_tune
                    complete_frames = max(
                        0,
                        (samples.size - self.FRAME_SIZE) // self.HOP_SIZE + 1,
                    )
                    carry = buffered_audio[complete_frames * self.HOP_SIZE * 2 :]
        except (OSError, wave.Error) as error:
            raise AudioCaptureError(f"Não foi possível analisar o arquivo WAV: {error}") from error
        return self._score(voiced_frames, in_tune_frames)

    @staticmethod
    def _score(voiced_frames: int, in_tune_frames: int) -> tuple[float | None, int, int]:
        if voiced_frames == 0:
            return None, 0, 0
        accuracy = round(100 * in_tune_frames / voiced_frames, 1)
        return accuracy, voiced_frames, in_tune_frames

    def _analyze_samples(self, samples: np.ndarray) -> tuple[int, int]:
        frame_size = self.FRAME_SIZE
        if samples.size < frame_size:
            return 0, 0

        min_lag = max(1, int(self.SAMPLE_RATE / self.MAX_FREQUENCY))
        max_lag = int(self.SAMPLE_RATE / self.MIN_FREQUENCY)
        fft_size = 1 << (2 * frame_size - 1).bit_length()
        window = np.hanning(frame_size).astype(np.float32)
        voiced_frames = 0
        in_tune_frames = 0

        for offset in range(0, samples.size - frame_size + 1, self.HOP_SIZE):
            frame = samples[offset : offset + frame_size].copy()
            if float(np.sqrt(np.mean(frame * frame))) < 120.0:
                continue
            frame -= np.mean(frame)
            spectrum = np.fft.rfft(frame * window, n=fft_size)
            autocorrelation = np.fft.irfft(
                spectrum * np.conjugate(spectrum), n=fft_size
            )
            energy = float(autocorrelation[0])
            if energy <= 0:
                continue

            candidates = autocorrelation[min_lag : max_lag + 1]
            peak_index = int(np.argmax(candidates))
            lag = min_lag + peak_index
            confidence = float(candidates[peak_index] / energy)
            if confidence < 0.3:
                continue
            if 0 < lag < autocorrelation.size - 1:
                left, center, right = autocorrelation[lag - 1 : lag + 2]
                denominator = float(left - 2 * center + right)
                if denominator:
                    lag += 0.5 * float(left - right) / denominator
            frequency = self.SAMPLE_RATE / lag
            if not self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY:
                continue

            nearest_midi_note = round(69 + 12 * math.log2(frequency / 440.0))
            expected_frequency = 440.0 * 2 ** ((nearest_midi_note - 69) / 12)
            cents_deviation = 1200 * math.log2(frequency / expected_frequency)
            voiced_frames += 1
            if abs(cents_deviation) <= self.TUNING_TOLERANCE_CENTS:
                in_tune_frames += 1

        return voiced_frames, in_tune_frames
