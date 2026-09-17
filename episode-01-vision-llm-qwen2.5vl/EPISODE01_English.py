import base64
import os
import matplotlib.pyplot as plt
import requests
import yfinance as yf


# =====================================================================
# 1. CREATE IMAGE (e.g., Stock/Index Chart)
# =====================================================================
def generate_chart_image(ticker: str = "VUSD.L", filename: str = "chart.png") -> str:
    """Downloads market data, generates a chart image, and saves it."""
    data = yf.download(ticker, period="3mo")

    plt.figure(figsize=(10, 5), dpi=150)
    plt.plot(data.index, data['Close'], label=f"{ticker} Price History", color='#1f77b4', lw=2)
    plt.title(f"Current Trend for {ticker}", fontsize=14, fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    print(f"[INFO] Chart saved as image: {filename}")
    return filename


# =====================================================================
# 2. CONVERT IMAGE TO BASE64
# =====================================================================
def encode_image_to_base64(image_path: str) -> str:
    """Encodes a local image into a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# =====================================================================
# 3. SEND IMAGE TO VISION LLM IN OLLAMA
# =====================================================================
def analyze_chart_with_ollama(
        image_path: str,
        ollama_url: str = "http://localhost:11434/api/generate",
        model_name: str = "qwen2.5vl"
) -> str:
    """Sends the image to the Vision model hosted in Ollama."""

    # Convert image to Base64
    base64_image = encode_image_to_base64(image_path)

    prompt_text = (
        "You are a technical chart analyst. Analyze the attached chart image:\n"
        "1. What trend (Upward, Downward, Sideways) is visible?\n"
        "2. Identify notable breakouts or consolidations along the trajectory.\n"
        "3. Provide a concise summary of the visual situation in 3 sentences."
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
        print(f"\n[INFO] Sending image to Ollama ({model_name})...")
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()

        result_json = response.json()
        return result_json.get("response", "No response received from model.")

    except requests.exceptions.RequestException as e:
        return f"[ERROR]: Request to Ollama failed: {e}"


def print_ollama_instructions():
    instructions = """
=====================================================================
  INSTRUCTIONS: STARTING & SETTING UP OLLAMA
=====================================================================
1. CHECK OLLAMA IN SYSTEM TRAY:
   - Check bottom right in the Windows system tray (next to the clock).
   - Is the Ollama icon visible? -> Ollama is already running!

2. START OLLAMA MANUALLY (if inactive):
   - Option A: Open Windows Start Menu and click "Ollama".
   - Option B: Open any terminal / PowerShell and type:
               ollama serve

3. DOWNLOAD MODEL ONCE (if not done yet):
   - Open PowerShell and execute the following command:
               ollama run qwen2.5vl

4. SCRIPT PREREQUISITE:
   - The Python script sends requests to: http://localhost:11434
   - As long as Ollama runs in the background, image analysis 
     will process successfully.
=====================================================================
"""
    print(instructions)


# =====================================================================
# EXECUTION EXAMPLE
# =====================================================================
if __name__ == "__main__":
    print_ollama_instructions()

    chart_file = "Kurve.jpg"

    if not os.path.exists(chart_file):
        chart_file = generate_chart_image(ticker="VUSD.L", filename="chart.png")

    analysis_result = analyze_chart_with_ollama(chart_file)

    print("\n" + "=" * 50)
    print("  VISUAL RECOGNITION FROM LLM (OLLAMA):")
    print("=" * 50)
    print(analysis_result)