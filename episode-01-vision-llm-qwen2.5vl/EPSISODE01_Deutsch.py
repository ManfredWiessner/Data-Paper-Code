import base64
import os
import matplotlib.pyplot as plt
import requests
import yfinance as yf


# =====================================================================
# 1. BILD ERSTELLEN (z.B. DAX-Chart)
# =====================================================================
def generate_chart_image(ticker: str = "VUSD.L", filename: str = "chart.png") -> str:
    """Lädt Börsendaten, erstellt ein Chart-Bild und speichert es ab."""
    data = yf.download(ticker, period="3mo")

    plt.figure(figsize=(10, 5), dpi=150)
    plt.plot(data.index, data['Close'], label=f"{ticker} Kursverlauf", color='#1f77b4', lw=2)
    plt.title(f"Aktueller Trend für {ticker}", fontsize=14, fontweight='bold')
    plt.xlabel("Datum")
    plt.ylabel("Kurs")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    print(f"[INFO] Chart als Bild gespeichert: {filename}")
    return filename


# =====================================================================
# 2. BILD ZU BASE64 KONVERTIEREN
# =====================================================================
def encode_image_to_base64(image_path: str) -> str:
    """Wandelt ein lokales Bild in einen Base64-String um."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# =====================================================================
# 3. BILD AN DAS VISION-LLM IN OLLAMA SENDEN
# =====================================================================
def analyze_chart_with_ollama(
        image_path: str,
        ollama_url: str = "http://localhost:11434/api/generate",
        model_name: str = "qwen2.5vl"
) -> str:
    """Sendet das Bild an das in Ollama geladene Vision-Modell."""

    # Bild in Base64 umwandeln
    base64_image = encode_image_to_base64(image_path)

    prompt_text = (
        "Du bist ein technischer Chart-Analyst. Analysiere das angehängte Chart-Bild:\n"
        "1. Welcher Trend (Aufwärts, Abwärts, Seitwärts) ist erkennbar?\n"
        "2. Identifiziere auffällige Ausbrüche oder Konsolidierungen im Verlauf.\n"
        "3. Gib eine prägnante Zusammenfassung der visuellen Lage in 3 Sätzen."
    )

    payload = {
        "model": model_name,
        "prompt": prompt_text,
        "images": [base64_image],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        print(f"\n[INFO] Sende Bild an Ollama ({model_name})...")
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()

        result_json = response.json()
        return result_json.get("response", "Keine Antwort vom Modell erhalten.")

    except requests.exceptions.RequestException as e:
        return f"[FEHLER]: Anfrage an Ollama fehlgeschlagen: {e}"


def print_ollama_instructions():
    instructions = """
=====================================================================
  ANLEITUNG: OLLAMA STARTEN & EINRICHTEN
=====================================================================
1. OLLAMA IN DER TASKLEISTE PRÜFEN:
   - Schau unten rechts in der Windows-Taskleiste (neben der Uhr).
   - Ist das Ollama-Icon (Lama) sichtbar? -> Ollama läuft bereits!

2. OLLAMA MANUELL STARTEN (falls nicht aktiv):
   - Option A: Öffne das Windows-Startmenü und klicke auf "Ollama".
   - Option B: Öffne ein beliebiges Terminal / PowerShell und tippe:
               ollama serve

3. MODELL EINMALIG HERUNTERLADEN (falls noch nicht geschehen):
   - Öffne eine PowerShell und führe folgenden Befehl aus:
               ollama run qwen2.5vl

4. SKRIPT-VORAUSSETZUNG:
   - Das Python-Skript sendet die Anfragen an: http://localhost:11434
   - Solange Ollama im Hintergrund läuft, wird die Bildanalyse
     erfolgreich verarbeitet.
=====================================================================
"""
    print(instructions)


# =====================================================================
# EXECUTION BEISPIEL
# =====================================================================
if __name__ == "__main__":
    print_ollama_instructions()

    chart_file = "Kurve.jpg"

    if not os.path.exists(chart_file):
        chart_file = generate_chart_image(ticker="VUSD.L", filename="chart.png")

    analysis_result = analyze_chart_with_ollama(chart_file)

    print("\n" + "=" * 50)
    print("  VISUELLE ERKENNUNG DES LLM (OLLAMA):")
    print("=" * 50)
    print(analysis_result)