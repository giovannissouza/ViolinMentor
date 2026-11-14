from datetime import datetime

import customtkinter as ctk
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.catalog import REPERTOIRE_CATALOG
from core.history import HistoryStore


class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        try:
            history = HistoryStore().load()
        except (OSError, ValueError) as error:
            ctk.CTkLabel(
                self,
                text=f"Não foi possível carregar o histórico de desempenho: {error}",
                text_color="#c93c37",
                wraplength=700,
                justify="left",
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=12)
            return

        recordings = history["recordings"]
        sessions = history["practice_sessions"]
        repertoire_statuses = history["repertoire"]
        total_seconds = sum(session["duration_seconds"] for session in sessions)
        studying_count = sum(
            repertoire_statuses.get(piece["id"]) == "Estudando"
            for piece in REPERTOIRE_CATALOG
        )
        completed_count = sum(
            repertoire_statuses.get(piece["id"]) == "Concluída"
            for piece in REPERTOIRE_CATALOG
        )

        ctk.CTkLabel(
            self,
            text="Olá! Acompanhe sua evolução",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(4, 18))

        stats = [
            ("Tempo total praticado", self._format_duration(total_seconds)),
            ("Gravações", str(len(recordings))),
            ("Repertório", f"{studying_count} estudando • {completed_count} concluídas"),
        ]
        for column, (title, value) in enumerate(stats):
            card = ctk.CTkFrame(self, corner_radius=14)
            card.grid(row=1, column=column, padx=(0, 12), sticky="nsew")
            ctk.CTkLabel(card, text=title, text_color=("gray40", "gray70")).pack(
                anchor="w", padx=18, pady=(16, 5)
            )
            ctk.CTkLabel(
                card, text=value, font=ctk.CTkFont(size=22, weight="bold")
            ).pack(anchor="w", padx=18, pady=(0, 16))

        ctk.CTkLabel(
            self,
            text="Evolução da precisão de afinação",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(26, 10))
        chart_frame = ctk.CTkFrame(self, corner_radius=14)
        chart_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        self._build_chart(chart_frame, recordings)

        ctk.CTkLabel(
            self,
            text="Gravações recentes",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(24, 10))
        recent_recordings = sorted(
            recordings, key=lambda item: item["timestamp"], reverse=True
        )[:5]
        if not recent_recordings:
            ctk.CTkLabel(
                self,
                text="Suas gravações e resultados serão exibidos aqui.",
                text_color=("gray45", "gray65"),
            ).grid(row=5, column=0, columnspan=3, sticky="w", pady=6)
        for row, recording in enumerate(recent_recordings, start=5):
            card = ctk.CTkFrame(self, corner_radius=10)
            card.grid(row=row, column=0, columnspan=3, sticky="ew", pady=4)
            card.grid_columnconfigure(0, weight=1)
            timestamp = datetime.fromisoformat(recording["timestamp"])
            accuracy = recording["accuracy_percent"]
            accuracy_text = (
                "Precisão indisponível"
                if accuracy is None
                else f"Precisão {accuracy:.1f}%"
            )
            duration = self._format_duration(recording["duration_seconds"])
            ctk.CTkLabel(
                card,
                text=f"{recording['file']}  •  {timestamp:%d/%m/%Y %H:%M}",
                anchor="w",
            ).grid(row=0, column=0, padx=16, pady=12, sticky="w")
            ctk.CTkLabel(
                card,
                text=f"{duration}  •  {accuracy_text}",
                text_color=("gray40", "gray70"),
            ).grid(row=0, column=1, padx=16, pady=12, sticky="e")
        ctk.CTkLabel(
            self,
            text=(
                "A precisão usa a proporção de quadros sonoros até ±20 cents da nota "
                "temperada mais próxima. Silêncios não são contabilizados."
            ),
            wraplength=700,
            justify="left",
            text_color=("gray45", "gray65"),
        ).grid(
            row=6 if not recent_recordings else 5 + len(recent_recordings),
            column=0,
            columnspan=3,
            sticky="w",
            pady=(12, 4),
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total_minutes = int(seconds // 60)
        hours, minutes = divmod(total_minutes, 60)
        if hours:
            return f"{hours}h {minutes:02d}min"
        return f"{minutes} min"

    def _build_chart(self, parent, recordings: list) -> None:
        dark_mode = ctk.get_appearance_mode() == "Dark"
        background = "#242424" if dark_mode else "#f2f2f2"
        foreground = "#eeeeee" if dark_mode else "#252525"
        figure = Figure(figsize=(7.2, 3.1), dpi=90, facecolor=background)
        axes = figure.add_subplot(111)
        axes.set_facecolor(background)
        axes.tick_params(colors=foreground)
        axes.xaxis.label.set_color(foreground)
        axes.yaxis.label.set_color(foreground)
        axes.title.set_color(foreground)
        axes.spines["bottom"].set_color(foreground)
        axes.spines["left"].set_color(foreground)
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        axes.set_title("Precisão por gravação")
        axes.set_xlabel("Data")
        axes.set_ylabel("Precisão (%)")
        axes.set_ylim(0, 100)
        axes.set_yticks((0, 20, 40, 60, 80, 100))
        axes.grid(axis="y", alpha=0.25)

        points = [
            (datetime.fromisoformat(item["timestamp"]), item["accuracy_percent"])
            for item in recordings
            if item["accuracy_percent"] is not None
        ]
        if points:
            points.sort(key=lambda point: point[0])
            axes.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                color="#3b82f6",
                marker="o",
                linewidth=2,
            )
            axes.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
            figure.autofmt_xdate(rotation=30, ha="right")
        else:
            axes.text(
                0.5,
                0.5,
                "Grave uma sessão com notas detectáveis para ver sua evolução.",
                horizontalalignment="center",
                verticalalignment="center",
                transform=axes.transAxes,
                color=foreground,
                wrap=True,
            )

        figure.tight_layout()
        chart = FigureCanvasTkAgg(figure, master=parent)
        chart.draw()
        chart.get_tk_widget().configure(highlightthickness=0)
        chart.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
