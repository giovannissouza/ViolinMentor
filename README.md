# ViolinMentor
Aplicativo de mentoria para Violinistas0

# 🎻 ViolinMentor

Um assistente interativo de desktop desenvolvido em Python para auxiliar estudantes de violino no aprendizado de teoria musical, postura, afinação em tempo real e acompanhamento de prática.

---

## ✨ Funcionalidades

* **📊 Dashboard de Progresso:** Acompanhamento visual da evolução da precisão de afinação e tempo acumulado de estudo.
* **🧍 Postura e Técnica:** Guias visuais interativos sobre como segurar o arco, posicionamento na queixeira/espaldeira e postura da mão esquerda.
* **🎼 Leitura de Partituras:** Módulo interativo para aprendizado da Clave de Sol, notas nas cordas soltas (Sol, Ré, Lá, Mi) e primeira posição com quiz visual no pentagrama.
* **🎙️ Afinador Cromático e Ouvido Inteligente:** Captação de áudio pelo microfone em tempo real para detectar a frequência (Hz), indicar a nota tocada e guiar exercícios nota por nota.
* **⏺️ Gravação e Repertório:** Gravação de sessões em formato `.wav`, análise automática de precisão e catálogo de músicas organizadas por nível de dificuldade com metrônomo integrado.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface Gráfica:** CustomTkinter / Pillow
* **Processamento de Áudio:** SoundDevice / NumPy / Librosa
* **Gráficos e Visualização:** Matplotlib
* **Empacotamento:** PyInstaller (geração de executável `.exe` para Windows)

---

## 📁 Estrutura do Projeto

```text
ViolinMentor/
├── assets/          # Ícones, imagens de postura e recursos visuais
├── core/            # Lógica de áudio, detecção de pitch, metrônomo e dados
├── data/            # Histórico de progresso (JSON/SQLite) e gravações (.wav)
├── ui/              # Telas e componentes da interface gráfica
├── main.py          # Ponto de entrada da aplicação
├── requirements.txt # Dependências do projeto
└── README.md        # Documentação do repositório
