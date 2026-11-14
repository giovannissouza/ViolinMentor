import numpy as np
import sounddevice as sd


class MetronomeError(RuntimeError):
    """Falha ao reproduzir o clique do metrônomo."""


class Metronome:
    SAMPLE_RATE = 44100
    FREQUENCY = 1100
    CLICK_DURATION = 0.035

    def __init__(self) -> None:
        sample_count = int(self.SAMPLE_RATE * self.CLICK_DURATION)
        time_axis = np.arange(sample_count, dtype=np.float32) / self.SAMPLE_RATE
        envelope = np.exp(-90 * time_axis)
        click = 0.3 * np.sin(2 * np.pi * self.FREQUENCY * time_axis) * envelope
        self._click = click.astype(np.float32).reshape(-1, 1)

    def play_click(self) -> None:
        try:
            sd.play(self._click, samplerate=self.SAMPLE_RATE, blocking=False)
        except (sd.PortAudioError, ValueError) as error:
            raise MetronomeError(f"Não foi possível reproduzir o clique: {error}") from error

    def stop(self) -> None:
        try:
            sd.stop()
        except sd.PortAudioError as error:
            raise MetronomeError(f"Não foi possível parar o clique: {error}") from error
