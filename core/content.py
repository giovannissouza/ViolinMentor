"""Conteúdo demonstrativo usado pelas páginas iniciais do aplicativo."""

NAVIGATION_ITEMS = [
    ("Início", "⌂"),
    ("Postura e Técnica", "♫"),
    ("Leitura de Partituras", "♪"),
    ("Prática e Afinador", "◉"),
    ("Repertório e Gravações", "▤"),
]
TECHNIQUE_GUIDES = {
    "Como segurar o arco": {
        "asset_stem": "segurar_arco",
        "tips": [
            "Apoie o polegar curvado próximo ao talão, sem travar a articulação.",
            "Deixe os dedos repousarem naturalmente sobre a vareta.",
            "Mantenha o punho flexível e os ombros relaxados.",
            "Comece com movimentos lentos em cordas soltas e observe o arco no espelho.",
        ],
    },
    "Ombro e queixeira": {
        "asset_stem": "ombro_queixeira",
        "tips": [
            "Apoie o instrumento sobre a clavícula e ajuste a queixeira ao seu conforto.",
            "Sustente o violino sem apertar com a mandíbula.",
            "Mantenha a cabeça alinhada e os ombros baixos.",
            "Se houver dor ou tensão, pare e peça orientação ao professor para ajustar o apoio.",
        ],
    },
    "Postura da mão esquerda": {
        "asset_stem": "mao_esquerda",
        "tips": [
            "Mantenha o pulso alinhado, evitando deixá-lo colapsar em direção ao braço.",
            "Use o polegar como apoio leve; não aperte o braço do violino.",
            "Curve os dedos e aproxime-os da corda antes de tocar.",
            "Pratique cada dedo devagar, conferindo a afinação e mantendo a mão relaxada.",
        ],
    },
    "Postura ao tocar": {
        "asset_stem": "postura",
        "tips": [
            "Fique em pé com os pés apoiados e o peso distribuído.",
            "Mantenha o tronco confortável e os joelhos sem rigidez.",
            "Deixe os ombros soltos enquanto movimenta o arco.",
            "Faça pausas curtas durante o estudo para evitar tensão acumulada.",
        ],
    },
}

# Cada questão associa uma nota escrita à sua digitação na primeira posição.
NOTE_QUIZ = [
    {"pitch": "G3", "note": "Sol", "octave": 3, "staff_step": -5, "string": "Sol", "finger": 0},
    {"pitch": "A3", "note": "Lá", "octave": 3, "staff_step": -4, "string": "Sol", "finger": 1},
    {"pitch": "B3", "note": "Si", "octave": 3, "staff_step": -3, "string": "Sol", "finger": 2},
    {"pitch": "C4", "note": "Dó", "octave": 4, "staff_step": -2, "string": "Sol", "finger": 3},
    {"pitch": "D4", "note": "Ré", "octave": 4, "staff_step": -1, "string": "Ré", "finger": 0},
    {"pitch": "E4", "note": "Mi", "octave": 4, "staff_step": 0, "string": "Ré", "finger": 1},
    {"pitch": "F#4", "note": "Fá♯", "octave": 4, "staff_step": 1, "string": "Ré", "finger": 2},
    {"pitch": "G4", "note": "Sol", "octave": 4, "staff_step": 2, "string": "Ré", "finger": 3},
    {"pitch": "A4", "note": "Lá", "octave": 4, "staff_step": 3, "string": "Lá", "finger": 0},
    {"pitch": "B4", "note": "Si", "octave": 4, "staff_step": 4, "string": "Lá", "finger": 1},
    {"pitch": "C#5", "note": "Dó♯", "octave": 5, "staff_step": 5, "string": "Lá", "finger": 2},
    {"pitch": "D5", "note": "Ré", "octave": 5, "staff_step": 6, "string": "Lá", "finger": 3},
    {"pitch": "E5", "note": "Mi", "octave": 5, "staff_step": 7, "string": "Mi", "finger": 0},
    {"pitch": "F#5", "note": "Fá♯", "octave": 5, "staff_step": 8, "string": "Mi", "finger": 1},
    {"pitch": "G#5", "note": "Sol♯", "octave": 5, "staff_step": 9, "string": "Mi", "finger": 2},
    {"pitch": "A5", "note": "Lá", "octave": 5, "staff_step": 10, "string": "Mi", "finger": 3},
]
