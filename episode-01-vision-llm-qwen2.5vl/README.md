# 📷 Episode 1: Image Recognition with Local Vision LLM (`qwen2.5vl`)

Welcome to the code repository for **Episode 1** of **Data, Paper & Code**!

In this episode, we demonstrate how to build an automated, fully local image recognition pipeline using Python, Ollama, and the multimodal model `qwen2.5vl`. We generate financial/scientific chart data, encode it as Base64, and pass it via REST API to extract key visual trends and breakout points.

---

## 📺 Watch the Episode

[![YouTube Video](https://img.shields.io/badge/YouTube-Watch%20Video-red?style=for-the-badge&logo=youtube)](https://youtube.com)
*(Replace link with your actual YouTube video link once published)*

---

## 📂 Included Files

| File | Language | Description |
| :--- | :---: | :--- |
| `EPISODE01_English.py` | 🇬🇧 English | Main Python script with English comments & console output. |
| `EPSISODE01_Deutsch.py` | 🇩🇪 German | Main Python script with German comments & console output. |
| `EPISODE01_English.pdf` | 🇬🇧 English | The compiled LaTeX protocol in English (theory, VLM architecture, mathematical background). |
| `EPISODE01_Deutsch.pdf` | 🇩🇪 German | The compiled LaTeX protocol in German (theory, VLM architecture, mathematical background). |
| `Kurve.jpg` | — | Example test chart image analyzed in the tutorial video. |
| `requirements.txt` | — | List of required Python dependencies (`requests`, `matplotlib`, `yfinance`). |

---

## ⚙️ Prerequisites & Setup

### 1. Install & Start Ollama
1. Download and install **Ollama** from [ollama.com](https://ollama.com).
2. Ensure Ollama is running in the background (check your system tray/taskbar or run `ollama serve` in a terminal).

### 2. Pull the Vision LLM Model
Open a terminal (PowerShell or Bash) and download the multimodal model:
```bash
ollama run qwen2.5vl
