import time
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from core.history import HistoryStore
from core.metronome import Metronome, MetronomeError
from core.recorder import AudioCaptureError, AudioRecorder


class PracticePage(ctk.CTkScrollableFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self._recorder = AudioRecorder()
        self._history_store = HistoryStore()
        self._timer_running = False
        self._activity_started_at = None
        self._display_elapsed = 0.0
        self._timer_job = None
        self._metronome = Metronome()
        self._metronome_running = False
        self._metronome_job = None
        self._bpm = 100

        timer_card = ctk.CTkFrame(self, corner_radius=14)
        timer_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            timer_card,
            text="Cronômetro de prática",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(20, 8))
        self.timer_label = ctk.CTkLabel(
            timer_card, text="00:00", font=ctk.CTkFont(size=40, weight="bold")
        )
        self.timer_label.pack(anchor="w", padx=22, pady=(0, 12))
        self.timer_button = ctk.CTkButton(
            timer_card, text="Iniciar prática", command=self._toggle_timer
        )
        self.timer_button.pack(anchor="w", padx=22, pady=(0, 20))

        metronome_card = ctk.CTkFrame(self, corner_radius=14)
        metronome_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            metronome_card,
            text="Metrônomo integrado",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(20, 8))
        ctk.CTkLabel(
            metronome_card,
            text="Ajuste o andamento entre 40 e 240 BPM e use o clique durante a prática.",
            text_color=("gray40", "gray70"),
        ).pack(anchor="w", padx=22, pady=(0, 12))
        metronome_controls = ctk.CTkFrame(metronome_card, fg_color="transparent")
        metronome_controls.pack(fill="x", padx=22, pady=(0, 8))
        self.bpm_slider = ctk.CTkSlider(
            metronome_controls,
            from_=40,
            to=240,
            number_of_steps=200,
            command=self._change_bpm,
        )
        self.bpm_slider.set(self._bpm)
        self.bpm_slider.pack(side="left", fill="x", expand=True, padx=(0, 14))
        self.bpm_label = ctk.CTkLabel(
            metronome_controls, text=f"{self._bpm} BPM", width=75
        )
        self.bpm_label.pack(side="left", padx=(0, 12))
        self.metronome_button = ctk.CTkButton(
            metronome_controls,
            text="Iniciar metrônomo",
            command=self._toggle_metronome,
        )
        self.metronome_button.pack(side="left")
        self.metronome_status = ctk.CTkLabel(
            metronome_card,
            text="O som usa a saída padrão. Fones evitam que o clique entre na gravação.",
            anchor="w",
            justify="left",
            wraplength=650,
            text_color=("gray45", "gray65"),
        )
        self.metronome_status.pack(anchor="w", padx=22, pady=(0, 16))

        recording_card = ctk.CTkFrame(self, corner_radius=14)
        recording_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(
            recording_card,
            text="Gravador de prática",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(20, 8))
        ctk.CTkLabel(
            recording_card,
            text=(
                "Grave pelo microfone. Ao encerrar, o áudio será salvo como WAV e "
                "analisado quanto à estabilidade de afinação."
            ),
            wraplength=650,
            justify="left",
            text_color=("gray40", "gray70"),
        ).pack(anchor="w", padx=22, pady=(0, 12))
        self.record_button = ctk.CTkButton(
            recording_card,
            text="Gravar Sessão",
            command=self._toggle_recording,
        )
        self.record_button.pack(anchor="w", padx=22, pady=(0, 10))
        self.recording_status = ctk.CTkLabel(
            recording_card,
            text="As gravações serão salvas em data/recordings/.",
            anchor="w",
            justify="left",
            wraplength=650,
        )
        self.recording_status.pack(anchor="w", padx=22, pady=(0, 18))
        ctk.CTkLabel(
            recording_card,
            text=(
                "A precisão é a porcentagem de quadros sonoros até ±20 cents da "
                "nota temperada mais próxima; silêncios não entram no cálculo."
            ),
            wraplength=650,
            justify="left",
            text_color=("gray45", "gray65"),
        ).pack(anchor="w", padx=22, pady=(0, 18))

        tuner = ctk.CTkFrame(self, corner_radius=14)
        tuner.pack(fill="x")
        ctk.CTkLabel(
            tuner, text="Afinador", font=ctk.CTkFont(size=19, weight="bold")
        ).pack(anchor="w", padx=22, pady=(20, 8))
        ctk.CTkLabel(
            tuner,
            text=(
                "O gravador já usa a entrada de áudio para registrar e analisar "
                "uma sessão. O visor de afinação em tempo real será uma melhoria futura."
            ),
            wraplength=650,
            justify="left",
            text_color=("gray40", "gray70"),
        ).pack(anchor="w", padx=22, pady=(0, 12))
        ctk.CTkButton(
            tuner,
            text="Testar visor (demonstração)",
            command=self._show_demo_pitch,
        ).pack(anchor="w", padx=22, pady=(0, 10))
        self.pitch_label = ctk.CTkLabel(tuner, text="Aguardando demonstração")
        self.pitch_label.pack(anchor="w", padx=22, pady=(0, 20))

    def _begin_activity(self) -> None:
        if self._activity_started_at is None:
            self._activity_started_at = time.monotonic()
            self._update_timer()

    def _toggle_timer(self) -> None:
        self._timer_running = not self._timer_running
        if self._timer_running:
            self.timer_button.configure(text="Encerrar prática")
            self._begin_activity()
        else:
            self.timer_button.configure(text="Iniciar prática")
            self._finish_activity_if_idle()

    def _update_timer(self) -> None:
        self._timer_job = None
        if self._activity_started_at is None:
            return
        elapsed = self._display_elapsed + time.monotonic() - self._activity_started_at
        self._render_time(elapsed)
        self._timer_job = self.after(1000, self._update_timer)

    def _finish_activity_if_idle(self, show_dialog: bool = False) -> None:
        if self._timer_running or self._recorder.is_recording:
            return
        if self._activity_started_at is None:
            return

        duration = max(0.0, time.monotonic() - self._activity_started_at)
        self._display_elapsed += duration
        self._activity_started_at = None
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
            self._timer_job = None
        self._render_time(self._display_elapsed)
        try:
            self._history_store.add_practice_session(
                datetime.now().astimezone().isoformat(timespec="seconds"), duration
            )
        except (OSError, ValueError) as error:
            message = f"A sessão terminou, mas não foi possível salvar o histórico: {error}"
            self.recording_status.configure(text=message)
            if show_dialog:
                messagebox.showerror("Erro ao salvar histórico", message, parent=self)

    def _render_time(self, elapsed: float) -> None:
        seconds = int(elapsed)
        self.timer_label.configure(text=f"{seconds // 60:02d}:{seconds % 60:02d}")

    def _change_bpm(self, value: float) -> None:
        self._bpm = int(round(value))
        self.bpm_label.configure(text=f"{self._bpm} BPM")
        if self._metronome_running:
            self._schedule_metronome_click()

    def _toggle_metronome(self) -> None:
        if self._metronome_running:
            self._stop_metronome()
            return
        try:
            self._metronome.play_click()
        except MetronomeError as error:
            self.metronome_status.configure(
                text=f"Não foi possível iniciar o metrônomo: {error}",
                text_color="#c93c37",
            )
            return
        self._metronome_running = True
        self.metronome_button.configure(text="Parar metrônomo")
        self.metronome_status.configure(
            text=f"Metrônomo ativo a {self._bpm} BPM.",
            text_color=("gray40", "gray70"),
        )
        self._schedule_metronome_click()

    def _schedule_metronome_click(self) -> None:
        if self._metronome_job is not None:
            self.after_cancel(self._metronome_job)
        interval = max(1, round(60000 / self._bpm))
        self._metronome_job = self.after(interval, self._play_metronome_tick)

    def _play_metronome_tick(self) -> None:
        self._metronome_job = None
        if not self._metronome_running:
            return
        try:
            self._metronome.play_click()
        except MetronomeError as error:
            self._metronome_running = False
            self.metronome_button.configure(text="Iniciar metrônomo")
            self.metronome_status.configure(
                text=f"O metrônomo foi interrompido: {error}",
                text_color="#c93c37",
            )
            return
        self._schedule_metronome_click()

    def _stop_metronome(self, show_dialog: bool = False) -> None:
        self._metronome_running = False
        if self._metronome_job is not None:
            self.after_cancel(self._metronome_job)
            self._metronome_job = None
        self.metronome_button.configure(text="Iniciar metrônomo")
        try:
            self._metronome.stop()
        except MetronomeError as error:
            message = f"Não foi possível parar o metrônomo: {error}"
            self.metronome_status.configure(text=message, text_color="#c93c37")
            if show_dialog:
                messagebox.showerror("Erro no metrônomo", message, parent=self)
            return
        self.metronome_status.configure(
            text="Metrônomo parado.", text_color=("gray40", "gray70")
        )

    def _toggle_recording(self) -> None:
        if self._recorder.is_recording:
            self._stop_recording()
            return
        try:
            self._recorder.start()
        except AudioCaptureError as error:
            self.recording_status.configure(text=f"Não foi possível gravar: {error}")
            return
        self.record_button.configure(text="Parar gravação")
        self.recording_status.configure(text="Gravando pelo microfone…")
        self._begin_activity()

    def _stop_recording(self, show_dialog: bool = False) -> None:
        try:
            recording = self._recorder.stop()
        except (AudioCaptureError, OSError, ValueError) as error:
            self.record_button.configure(text="Gravar Sessão")
            message = f"Falha ao finalizar a gravação: {error}"
            self.recording_status.configure(text=message)
            self._finish_activity_if_idle(show_dialog=show_dialog)
            if show_dialog:
                messagebox.showerror("Erro na gravação", message, parent=self)
            return

        self.record_button.configure(text="Gravar Sessão")
        try:
            self._history_store.add_recording(recording.to_history_entry())
        except (OSError, ValueError) as error:
            message = (
                f"Áudio salvo em {recording.path}, mas não foi possível atualizar "
                f"o histórico: {error}"
            )
            self.recording_status.configure(text=message)
            if show_dialog:
                messagebox.showerror("Erro ao salvar histórico", message, parent=self)
        else:
            if recording.accuracy_percent is None:
                accuracy_text = "Precisão indisponível: nenhuma nota sustentada foi detectada."
            else:
                accuracy_text = (
                    f"Precisão de afinação: {recording.accuracy_percent:.1f}% "
                    f"({recording.in_tune_frames}/{recording.voiced_frames} quadros)"
                )
            if recording.warnings:
                accuracy_text += f"\nAvisos do dispositivo de áudio: {'; '.join(recording.warnings)}"
            self.recording_status.configure(
                text=f"Gravação salva: {recording.path}\n{accuracy_text}"
            )
        self._finish_activity_if_idle(show_dialog=show_dialog)

    def _show_demo_pitch(self) -> None:
        self.pitch_label.configure(text="Demonstração: Lá (A4) • 440 Hz — sem áudio ao vivo")

    def destroy(self) -> None:
        if hasattr(self, "_metronome_running") and self._metronome_running:
            self._stop_metronome(show_dialog=True)
        if hasattr(self, "_recorder") and self._recorder.is_recording:
            self._stop_recording(show_dialog=True)
        if hasattr(self, "_timer_running"):
            self._timer_running = False
            self.timer_button.configure(text="Iniciar prática")
            self._finish_activity_if_idle(show_dialog=True)
        super().destroy()
