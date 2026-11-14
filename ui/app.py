import logging
from tkinter import TclError, messagebox

import customtkinter as ctk

from core.content import NAVIGATION_ITEMS
from core.paths import get_data_directory, resource_path
from ui.pages import (
    DashboardPage,
    PracticePage,
    RepertoirePage,
    SheetReadingPage,
    TechniquePage,
)


class ViolinMentorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ViolinMentor")
        self.geometry("1180x760")
        self.minsize(900, 620)
        self._logger = logging.getLogger("violinmentor")
        self._logger.setLevel(logging.ERROR)
        self._log_path = get_data_directory() / "logs" / "app.log"
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(self._log_path, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            self._logger.addHandler(handler)
        except OSError as error:
            self._log_path = None
            messagebox.showwarning(
                "Registro de erros indisponível",
                f"Não foi possível preparar o arquivo de log: {error}",
                parent=self,
            )
        try:
            self.iconbitmap(resource_path("assets", "violino.ico"))
        except TclError as error:
            self._logger.error("Não foi possível carregar o ícone da janela: %s", error)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._pages = {
            "Início": DashboardPage,
            "Postura e Técnica": TechniquePage,
            "Leitura de Partituras": SheetReadingPage,
            "Prática e Afinador": PracticePage,
            "Repertório e Gravações": RepertoirePage,
        }
        self._navigation_buttons = {}
        self._current_page = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_content_area()
        self.show_page("Início")

    def report_callback_exception(self, exception_type, exception, traceback) -> None:
        self._logger.error(
            "Erro não tratado em callback da interface",
            exc_info=(exception_type, exception, traceback),
        )
        log_message = (
            f"\n\nDetalhes registrados em:\n{self._log_path}"
            if self._log_path is not None
            else ""
        )
        messagebox.showerror(
            "Erro inesperado",
            f"A operação não pôde ser concluída.\n\n{exception}{log_message}",
            parent=self,
        )

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=245, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="ViolinMentor",
            font=ctk.CTkFont(size=25, weight="bold"),
        ).grid(row=0, column=0, padx=22, pady=(28, 4), sticky="w")
        ctk.CTkLabel(
            self.sidebar,
            text="Seu espaço de estudo",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, padx=24, pady=(0, 24), sticky="w")

        for row, (label, icon) in enumerate(NAVIGATION_ITEMS, start=2):
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}   {label}",
                anchor="w",
                height=44,
                corner_radius=10,
                fg_color="transparent",
                text_color=("gray15", "gray90"),
                hover_color=("gray85", "gray25"),
                command=lambda page=label: self.show_page(page),
            )
            button.grid(row=row, column=0, padx=14, pady=4, sticky="ew")
            self._navigation_buttons[label] = button

        ctk.CTkLabel(
            self.sidebar,
            text="VIOLINMENTOR  •  VERSÃO 1.0",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray45", "gray65"),
        ).grid(row=8, column=0, padx=22, pady=22, sticky="sw")

    def _build_content_area(self) -> None:
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=28, pady=24)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)
        self.page_title = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=28, weight="bold")
        )
        self.page_title.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Aparência").grid(row=0, column=1, padx=(12, 8))
        self.appearance = ctk.CTkOptionMenu(
            header,
            values=["Escuro", "Claro", "Sistema"],
            width=115,
            command=self._set_appearance,
        )
        self.appearance.set("Escuro")
        self.appearance.grid(row=0, column=2, sticky="e")
        self.page_container = ctk.CTkFrame(self.content, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def _set_appearance(self, selection: str) -> None:
        mode = {"Escuro": "dark", "Claro": "light", "Sistema": "system"}[selection]
        ctk.set_appearance_mode(mode)

    def show_page(self, page_name: str) -> None:
        page_class = self._pages[page_name]
        self.page_title.configure(text=page_name)
        for label, button in self._navigation_buttons.items():
            button.configure(
                fg_color=("gray82", "gray25") if label == page_name else "transparent"
            )
        if self._current_page is not None:
            self._current_page.destroy()
        self._current_page = page_class(self.page_container)
        self._current_page.grid(row=0, column=0, sticky="nsew")
