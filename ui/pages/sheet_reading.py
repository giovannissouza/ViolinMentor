import random

import customtkinter as ctk
import tkinter as tk

from core.content import NOTE_QUIZ


class SheetReadingPage(ctk.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._current_question = None
        self._answered = False
        self._correct_answers = 0
        self._answered_count = 0
        self._option_buttons = []

        lesson = ctk.CTkFrame(self, corner_radius=14)
        lesson.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        lesson.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            lesson,
            text="Clave de Sol e notas no violino",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 8), sticky="w")
        ctk.CTkLabel(
            lesson,
            text="Na clave de Sol, as linhas de baixo para cima são Mi, Sol, Si, Ré e Fá. "
            "Os espaços são Fá, Lá, Dó e Mi.",
            wraplength=700,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 14), sticky="w")

        ctk.CTkLabel(
            lesson,
            text="Cordas soltas",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=2, column=0, padx=20, pady=(0, 4), sticky="w")
        ctk.CTkLabel(
            lesson,
            text="Sol (G3)   •   Ré (D4)   •   Lá (A4)   •   Mi (E5)",
            wraplength=340,
            justify="left",
        ).grid(row=3, column=0, padx=20, pady=(0, 16), sticky="w")
        ctk.CTkLabel(
            lesson,
            text="Primeira posição",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=2, column=1, padx=20, pady=(0, 4), sticky="w")
        ctk.CTkLabel(
            lesson,
            text=(
                "Sol: Lá₁ Si₂ Dó₃ Ré₄   •   Ré: Mi₁ Fá♯₂ Sol₃ Lá₄\n"
                "Lá: Si₁ Dó♯₂ Ré₃ Mi₄   •   Mi: Fá♯₁ Sol♯₂ Lá₃ Si₄\n"
                "O número indica o dedo; ₄ é o quarto dedo."
            ),
            wraplength=430,
            justify="left",
        ).grid(row=3, column=1, padx=20, pady=(0, 16), sticky="w")

        quiz = ctk.CTkFrame(self, corner_radius=14)
        quiz.grid(row=1, column=0, sticky="ew")
        quiz.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            quiz, text="Quiz visual", font=ctk.CTkFont(size=19, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
        ctk.CTkLabel(
            quiz,
            text="Observe a nota na pauta e selecione a opção com nota, corda e dedo.",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.staff = tk.Canvas(
            quiz,
            width=470,
            height=225,
            background="#fffef9",
            highlightthickness=0,
        )
        self.staff.grid(row=2, column=0, padx=20, pady=(0, 8), sticky="w")
        self._draw_staff()
        self.score_label = ctk.CTkLabel(quiz, text="")
        self.score_label.grid(row=3, column=0, padx=20, pady=(0, 8), sticky="w")
        self.option_area = ctk.CTkFrame(quiz, fg_color="transparent")
        self.option_area.grid(row=4, column=0, padx=16, pady=(0, 8), sticky="ew")
        self.option_area.grid_columnconfigure((0, 1), weight=1)
        self.feedback = ctk.CTkLabel(quiz, text="", anchor="w")
        self.feedback.grid(row=5, column=0, padx=20, pady=4, sticky="w")
        self.next_button = ctk.CTkButton(
            quiz, text="Próxima nota", command=self._next_question
        )
        self.next_button.grid(row=6, column=0, padx=20, pady=(4, 18), sticky="w")

        self._next_question()

    def _draw_staff(self) -> None:
        left, right, bottom_y, spacing = 105, 450, 145, 20
        for index in range(5):
            y = bottom_y - index * spacing
            self.staff.create_line(left, y, right, y, fill="#393939", width=1)
        self.staff.create_text(
            58,
            105,
            text="𝄞",
            font=("Segoe UI Symbol", 66),
            fill="#202020",
        )
        self.staff.create_text(
            110,
            14,
            text="Pentagrama • clave de Sol",
            anchor="w",
            font=("Segoe UI", 10),
            fill="#555555",
        )
        self.staff.create_text(
            110,
            210,
            text="Linhas: Mi  Sol  Si  Ré  Fá     Espaços: Fá  Lá  Dó  Mi",
            anchor="w",
            font=("Segoe UI", 9),
            fill="#555555",
        )

    def _draw_note(self, question: dict) -> None:
        self.staff.delete("quiz_note")
        step = question["staff_step"]
        bottom_y = 145
        note_y = bottom_y - step * 10
        note_x = 320
        if step <= -2:
            ledger_steps = range(-2, step - 1, -2)
        elif step >= 10:
            ledger_steps = range(10, step + 1, 2)
        else:
            ledger_steps = ()
        for ledger_step in ledger_steps:
            y = bottom_y - ledger_step * 10
            self.staff.create_line(
                note_x - 17,
                y,
                note_x + 17,
                y,
                fill="#393939",
                width=1,
                tags="quiz_note",
            )
        if "♯" in question["note"]:
            self.staff.create_text(
                note_x - 21,
                note_y,
                text="♯",
                font=("Segoe UI Symbol", 18),
                fill="#202020",
                tags="quiz_note",
            )
        self.staff.create_oval(
            note_x - 8,
            note_y - 5,
            note_x + 8,
            note_y + 5,
            fill="#202020",
            outline="#202020",
            tags="quiz_note",
        )
        if step < 4:
            self.staff.create_line(
                note_x + 7,
                note_y,
                note_x + 7,
                note_y - 42,
                fill="#202020",
                width=2,
                tags="quiz_note",
            )
        else:
            self.staff.create_line(
                note_x - 7,
                note_y,
                note_x - 7,
                note_y + 42,
                fill="#202020",
                width=2,
                tags="quiz_note",
            )

    @staticmethod
    def _fingering_text(question: dict) -> str:
        if question["finger"] == 0:
            return f"corda {question['string']} solta"
        return f"corda {question['string']}, {question['finger']}º dedo"

    def _next_question(self) -> None:
        self._current_question = random.choice(NOTE_QUIZ)
        self._answered = False
        self.feedback.configure(text="")
        self.next_button.configure(state="disabled")
        self._draw_note(self._current_question)
        choices = [self._current_question]
        distractors = [
            note for note in NOTE_QUIZ if note["pitch"] != self._current_question["pitch"]
        ]
        choices.extend(random.sample(distractors, min(3, len(distractors))))
        random.shuffle(choices)

        for child in self.option_area.winfo_children():
            child.destroy()
        self._option_buttons = []
        for index, choice in enumerate(choices):
            row, column = divmod(index, 2)
            button = ctk.CTkButton(
                self.option_area,
                text=f"{choice['note']}{choice['octave']}  •  "
                f"{self._fingering_text(choice)}",
                anchor="w",
                command=lambda pitch=choice["pitch"]: self._submit_answer(pitch),
            )
            button.grid(row=row, column=column, padx=4, pady=4, sticky="ew")
            self._option_buttons.append((button, choice["pitch"]))

        self._update_score()

    def _submit_answer(self, pitch: str) -> None:
        if self._answered:
            return
        self._answered = True
        self._answered_count += 1
        correct_pitch = self._current_question["pitch"]
        is_correct = pitch == correct_pitch
        if is_correct:
            self._correct_answers += 1
            self.feedback.configure(text="Correto!", text_color="#238636")
        else:
            answer = self._current_question
            self.feedback.configure(
                text=(
                    f"A resposta era {answer['note']}{answer['octave']} — "
                    f"{self._fingering_text(answer)}."
                ),
                text_color="#c93c37",
            )
        for button, option_pitch in self._option_buttons:
            if option_pitch == correct_pitch:
                button.configure(fg_color="#238636")
            elif option_pitch == pitch and not is_correct:
                button.configure(fg_color="#c93c37")
            button.configure(state="disabled")
        self.next_button.configure(state="normal")
        self._update_score()

    def _update_score(self) -> None:
        self.score_label.configure(
            text=f"Acertos: {self._correct_answers} de {self._answered_count}"
        )
