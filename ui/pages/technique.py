import os
import subprocess
import sys

import customtkinter as ctk
from PIL import Image

from core.content import TECHNIQUE_GUIDES
from core.paths import get_resource_path


class TechniquePage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self._asset_directory = get_resource_path("assets", "technique")
        self._media_image = None
        self._selected_topic = None
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Selecione um guia. Imagens e vídeos locais são opcionais.",
            text_color=("gray40", "gray70"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        topics = ctk.CTkFrame(self, corner_radius=12)
        topics.grid(row=1, column=0, sticky="nsw", padx=(0, 18))
        self.detail = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.detail.grid(row=1, column=1, sticky="nsew")
        self.detail.grid_columnconfigure(0, weight=1)

        for row, title in enumerate(TECHNIQUE_GUIDES):
            ctk.CTkButton(
                topics,
                text=title,
                anchor="w",
                width=205,
                command=lambda topic=title: self._select_topic(topic),
            ).grid(row=row, column=0, padx=12, pady=(12 if row == 0 else 0, 8))

        self.preview = ctk.CTkLabel(
            self.detail,
            text="",
            width=320,
            height=230,
            corner_radius=10,
            fg_color=("gray90", "gray20"),
            justify="center",
            wraplength=290,
        )
        self.preview.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="ew")
        self.video_button = ctk.CTkButton(
            self.detail,
            text="Abrir vídeo demonstrativo",
            command=self._open_video,
        )
        self.video_button.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="w")
        self.media_status = ctk.CTkLabel(
            self.detail,
            text="",
            anchor="w",
            justify="left",
            wraplength=450,
            text_color=("gray40", "gray70"),
        )
        self.media_status.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="ew")
        ctk.CTkLabel(
            self.detail,
            text="Dicas de estudo",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=3, column=0, padx=18, pady=(10, 4), sticky="w")
        self.tips = ctk.CTkFrame(self.detail, fg_color="transparent")
        self.tips.grid(row=4, column=0, padx=18, pady=(0, 16), sticky="ew")
        self._select_topic(next(iter(TECHNIQUE_GUIDES)))

    def _select_topic(self, topic: str) -> None:
        self._selected_topic = topic
        guide = TECHNIQUE_GUIDES[topic]
        for child in self.tips.winfo_children():
            child.destroy()
        for index, tip in enumerate(guide["tips"]):
            ctk.CTkLabel(
                self.tips,
                text=f"•  {tip}",
                anchor="w",
                justify="left",
                wraplength=460,
            ).grid(row=index, column=0, sticky="ew", pady=4)
        self._load_image(guide["asset_stem"])

    def _load_image(self, asset_stem: str) -> None:
        image_path = next(
            (
                self._asset_directory / f"{asset_stem}{extension}"
                for extension in (".png", ".jpg", ".jpeg", ".webp")
                if (self._asset_directory / f"{asset_stem}{extension}").is_file()
            ),
            None,
        )
        self._media_image = None
        if image_path is None:
            self.preview.configure(
                image=None,
                text=(
                    "Espaço para imagem demonstrativa\n\n"
                    f"Adicione {asset_stem}.png (ou .jpg) em:\n"
                    f"{self._asset_directory}"
                ),
            )
            self.media_status.configure(
                text="Você também pode adicionar um vídeo .mp4 com o mesmo nome do tópico."
            )
            return

        try:
            with Image.open(image_path) as source:
                image = source.convert("RGB")
            self._media_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(300, 210),
            )
        except (OSError, ValueError) as error:
            self.preview.configure(image=None, text="Não foi possível carregar a imagem.")
            self.media_status.configure(text=f"Erro ao abrir {image_path}: {error}")
            return
        self.preview.configure(image=self._media_image, text="")
        self.media_status.configure(text=f"Imagem local: {image_path.name}")

    def _open_video(self) -> None:
        asset_stem = TECHNIQUE_GUIDES[self._selected_topic]["asset_stem"]
        video_path = self._asset_directory / f"{asset_stem}.mp4"
        if not video_path.is_file():
            self.media_status.configure(
                text=f"Vídeo não encontrado. Adicione o arquivo local: {video_path}"
            )
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(video_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(video_path)])
            else:
                subprocess.Popen(["xdg-open", str(video_path)])
        except OSError as error:
            self.media_status.configure(text=f"Erro ao abrir o vídeo: {error}")
            return
        self.media_status.configure(text=f"Abrindo vídeo: {video_path.name}")
