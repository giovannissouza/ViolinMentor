import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from core.catalog import (
    REPERTOIRE_CATALOG,
    REPERTOIRE_LEVELS,
    REPERTOIRE_STATUSES,
)
from core.history import HistoryStore
from core.paths import get_data_directory


class RepertoirePage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._history_store = HistoryStore()
        self._status_by_id = {}
        self._status_variables = {}
        self._recordings = []
        self._load_error = None
        self._selected_level = REPERTOIRE_LEVELS[0]
        self._recordings_directory = get_data_directory() / "recordings"

        ctk.CTkLabel(
            self,
            text="Repertório de estudo",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        ctk.CTkLabel(
            self,
            text="Sugestões por nível, com andamento inicial ajustável à sua prática.",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="new")
        self.level_selector = ctk.CTkSegmentedButton(
            controls,
            values=list(REPERTOIRE_LEVELS),
            command=self._select_level,
        )
        self.level_selector.set(self._selected_level)
        self.level_selector.pack(anchor="w", pady=(0, 10))
        self.status_message = ctk.CTkLabel(
            controls, text="", anchor="w", justify="left", wraplength=700
        )
        self.status_message.pack(anchor="w", pady=(0, 8))
        self.catalog_frame = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.catalog_frame.grid(row=3, column=0, sticky="nsew")
        self.catalog_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._load_statuses()
        self._render_catalog()

    def _load_statuses(self) -> None:
        try:
            history = self._history_store.load()
        except (OSError, ValueError) as error:
            self._load_error = str(error)
            self.status_message.configure(
                text=f"Não foi possível carregar o histórico: {error}",
                text_color="#c93c37",
            )
            return
        self._status_by_id = history["repertoire"]
        self._recordings = history["recordings"]

    def _select_level(self, level: str) -> None:
        self._selected_level = level
        self._render_catalog()

    def _render_catalog(self) -> None:
        for child in self.catalog_frame.winfo_children():
            child.destroy()
        self._status_variables = {}
        pieces = [
            piece
            for piece in REPERTOIRE_CATALOG
            if piece["level"] == self._selected_level
        ]
        for row, piece in enumerate(pieces):
            card = ctk.CTkFrame(self.catalog_frame, corner_radius=12)
            card.grid(row=row, column=0, sticky="ew", padx=8, pady=6)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                card,
                text=piece["title"],
                font=ctk.CTkFont(size=17, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, padx=16, pady=(14, 2), sticky="ew")
            ctk.CTkLabel(
                card,
                text=f"{piece['composer']}  •  {piece['bpm']} BPM recomendado",
                text_color=("gray40", "gray70"),
                anchor="w",
            ).grid(row=1, column=0, padx=16, pady=(0, 6), sticky="ew")
            ctk.CTkLabel(
                card,
                text=piece["description"],
                justify="left",
                anchor="w",
                wraplength=620,
            ).grid(row=2, column=0, padx=16, pady=(0, 10), sticky="ew")

            status = self._status_by_id.get(piece["id"], REPERTOIRE_STATUSES[0])
            status_variable = ctk.StringVar(value=status)
            self._status_variables[piece["id"]] = status_variable
            status_menu = ctk.CTkOptionMenu(
                card,
                values=list(REPERTOIRE_STATUSES),
                variable=status_variable,
                width=160,
                command=lambda selected, item_id=piece["id"]: self._change_status(
                    item_id, selected
                ),
            )
            status_menu.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="w")
            if self._load_error:
                status_menu.configure(state="disabled")

        recording_heading_row = len(pieces)
        ctk.CTkLabel(
            self.catalog_frame,
            text="Gravações recentes",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=recording_heading_row,
            column=0,
            padx=8,
            pady=(22, 8),
            sticky="w",
        )
        recent_recordings = sorted(
            self._recordings, key=lambda recording: recording["timestamp"], reverse=True
        )[:5]
        if not recent_recordings:
            ctk.CTkLabel(
                self.catalog_frame,
                text="As gravações finalizadas aparecerão aqui.",
                text_color=("gray45", "gray65"),
            ).grid(
                row=recording_heading_row + 1,
                column=0,
                padx=8,
                pady=(0, 12),
                sticky="w",
            )
        for index, recording in enumerate(recent_recordings, start=recording_heading_row + 1):
            card = ctk.CTkFrame(self.catalog_frame, corner_radius=10)
            card.grid(row=index, column=0, sticky="ew", padx=8, pady=5)
            card.grid_columnconfigure(0, weight=1)
            timestamp = datetime.fromisoformat(recording["timestamp"])
            accuracy = recording["accuracy_percent"]
            accuracy_text = (
                "Precisão indisponível"
                if accuracy is None
                else f"Precisão {accuracy:.1f}%"
            )
            ctk.CTkLabel(
                card,
                text=f"{recording['file']}  •  {timestamp:%d/%m/%Y %H:%M}",
                anchor="w",
            ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")
            ctk.CTkLabel(
                card,
                text=f"{recording['duration_seconds']:.0f} s  •  {accuracy_text}",
                text_color=("gray40", "gray70"),
                anchor="w",
            ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")
            ctk.CTkButton(
                card,
                text="Abrir WAV",
                width=105,
                command=lambda filename=recording["file"]: self._open_recording(
                    filename
                ),
            ).grid(row=0, column=1, rowspan=2, padx=14, pady=8)

    def _change_status(self, piece_id: str, selected_status: str) -> None:
        previous_status = self._status_by_id.get(piece_id, REPERTOIRE_STATUSES[0])
        if self._load_error:
            self._status_variables[piece_id].set(previous_status)
            return
        try:
            self._history_store.set_repertoire_status(piece_id, selected_status)
        except (OSError, ValueError) as error:
            self._status_variables[piece_id].set(previous_status)
            self.status_message.configure(
                text=f"Não foi possível salvar o status: {error}",
                text_color="#c93c37",
            )
            return
        self._status_by_id[piece_id] = selected_status
        self.status_message.configure(
            text="Status salvo no histórico local.",
            text_color=("gray40", "gray70"),
        )

    def _open_recording(self, filename: str) -> None:
        recording_path = self._recordings_directory / Path(filename).name
        if not recording_path.is_file():
            self.status_message.configure(
                text=f"Arquivo de gravação não encontrado: {recording_path}",
                text_color="#c93c37",
            )
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(recording_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(recording_path)])
            else:
                subprocess.Popen(["xdg-open", str(recording_path)])
        except OSError as error:
            self.status_message.configure(
                text=f"Não foi possível abrir a gravação: {error}",
                text_color="#c93c37",
            )
            return
        self.status_message.configure(
            text=f"Abrindo {recording_path.name}.",
            text_color=("gray40", "gray70"),
        )
