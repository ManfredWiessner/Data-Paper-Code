import base64
import os
import subprocess
import sys
import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
CODER_MODEL = "qwen2.5vl"
VISION_MODEL = "qwen2.5vl"

SCRIPT_FILE = "generated_chart_script.py"
TEMPLATE_IMAGE = "Kurve_Vorlage.jpg"  # Deine Vorlage
BASE_IMAGE_NAME = "Kurve"
MAX_ATTEMPTS = 4


def encode_image_to_base64(image_path: str) -> str:
    """Wandelt ein lokales Bild in einen Base64-String um."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_chart_with_ollama(
        image_path: str,
        prompt_text: str,
        ollama_url: str = OLLAMA_GENERATE_URL,
        model_name: str = VISION_MODEL
) -> str:
    """Sende das Bild an das Vision-Modell in Ollama."""
    if not os.path.exists(image_path):
        return "[FEHLER] Das Bild wurde nicht erstellt."

    base64_image = encode_image_to_base64(image_path)

    payload = {
        "model": model_name,
        "prompt": prompt_text,
        "images": [base64_image],
        "stream": False,
        "options": {"temperature": 0.2}
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "Keine Antwort vom Modell erhalten.")
    except requests.exceptions.RequestException as e:
        return f"[FEHLER]: Anfrage an Ollama fehlgeschlagen: {e}"


def run_code_llm(prompt: str) -> str:
    """Ruft das Coder-Modell über Ollama ab."""
    full_prompt = (
        "<|im_start|>system\n"
        "You are an expert Python developer. Write complete, valid Python code.\n"
        "Do NOT use markdown backticks (no ```python). Return ONLY the executable Python code.<|im_end|>\n"
        f"<|im_start|>user\n{prompt}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

    payload = {
        "model": CODER_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 1024
        }
    }

    try:
        response = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=90)
        response.raise_for_status()

        result_json = response.json()
        code_output = result_json.get("response", "").strip()

        if not code_output:
            payload["prompt"] = prompt
            res = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=90).json()
            code_output = res.get("response", "").strip()

        return code_output

    except Exception as e:
        print(f"❌ Fehler bei Anfrage an Coder-Modell ({CODER_MODEL}): {e}")
        return ""


def run_agent(task_description_en: str):
    print("==================================================")
    print("AGENT: Chart Code Generator & Visual Validator")
    print(f"Vorlage: {TEMPLATE_IMAGE}")
    print("==================================================\n")

    history = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"--- Iteration {attempt}/{MAX_ATTEMPTS} ---")

        # Dynamischer Dateiname pro Durchlauf, damit Kurve_Vorlage.jpg unberührt bleibt
        current_image_file = f"{BASE_IMAGE_NAME}_iter_{attempt}.jpg"

        # 1. CODE GENERIEREN
        prompt = (
            f"You are a Python developer. Task: {task_description_en}\n"
            f"Requirements:\n"
            f"- Save the generated chart image strictly as '{current_image_file}'.\n"
            f"- Return ONLY the raw executable Python code. No markdown blocks, no conversational text.\n"
            f"{history}"
        )

        raw_code = run_code_llm(prompt)

        if not raw_code or len(raw_code.strip()) == 0:
            print("❌ Fehler: Das LLM hat einen leeren String zurückgegeben. Erneuter Versuch...")
            history += "\nYour last response was completely empty. You MUST generate valid Python code!"
            continue

        # Markdown-Tags bereinigen
        code = raw_code
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])

        with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
            f.write(code)

        # 2. CODE AUSFÜHREN
        res = subprocess.run([sys.executable, SCRIPT_FILE], capture_output=True, text=True)

        if res.returncode != 0:
            print(f"❌ Syntax/Runtime Error:\n{res.stderr.strip()}")
            history += f"\nPrevious attempt failed with error:\n{res.stderr}\nFix the code."
            continue

        if not os.path.exists(current_image_file):
            print(f"❌ Fehler: Das Skript ist durchgelaufen, hat aber '{current_image_file}' nicht erzeugt.")
            history += f"\nThe script ran, but failed to save the image to '{current_image_file}'. Make sure to call plt.savefig('{current_image_file}')."
            continue

        print(f"✔ Skript fehlerfrei ausgeführt und '{current_image_file}' erzeugt.")

        # 3. VISION-ANALYSE
        vision_prompt = (
            "Analyze the generated chart picture critically:\n"
            "1. Is the chart correctly rendered and legible?\n"
            "2. Are axes labeled properly without overlapping text?\n"
            "If the chart looks complete and well-formatted, reply with 'APPROVED'. "
            "Otherwise, explain shortly what needs to be improved."
        )

        print(f"[INFO] Sende '{current_image_file}' zur visuellen Prüfung an {VISION_MODEL}...")

        evaluation = analyze_chart_with_ollama(current_image_file, vision_prompt)
        print(f"Vision Feedback:\n{evaluation}\n")

        if "APPROVED" in evaluation.upper():
            print("✅ ERFOLG: Das Skript erzeugt ein fehlerfreies und visuell geprüftes Diagramm!\n")
            print("=" * 50)
            print(" INHALT VON generated_chart_script.py:")
            print("=" * 50)
            print(code)

            # Kopiert das freigegebene Bild als finale Kurve_final.jpg
            final_image = f"{BASE_IMAGE_NAME}_final.jpg"
            with open(current_image_file, "rb") as src, open(final_image, "wb") as dst:
                dst.write(src.read())
            print(f"🖼️ Das finale Diagramm wurde als '{final_image}' abgespeichert.")
            break

        history += f"\nThe generated image had visual issues:\n{evaluation}\nPlease update the code."


if __name__ == "__main__":
    task = (
        "Write a Python script using yfinance and matplotlib to download 3 months of data for 'VUSD.L'. "
        "Plot the Close price with a grid and proper title."
    )
    run_agent(task)