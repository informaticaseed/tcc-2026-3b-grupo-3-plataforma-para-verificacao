import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ANALYSIS_TIMEOUT_SECONDS = 180
ANALYSIS_POLL_INTERVAL_SECONDS = 20

def scan_url(url):

    api_key = os.getenv("VT_API_KEY")

    print("API KEY EXISTS:", api_key is not None)
    print("API KEY LENGTH:", len(api_key) if api_key else 0)


    headers = {
        "x-apikey": api_key
    }

    try:
        response = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={
                "url": url
            },
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as erro:
        return {
            "error": str(erro)
        }

def get_analysis(analysis_id, timeout=10):

    api_key = os.getenv("VT_API_KEY")

    headers = {
        "x-apikey": api_key
    }

    print("GETTING ANALYSIS...")

    try:
        response = requests.get(
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
            headers=headers,
            timeout=timeout
        )

        response.raise_for_status()

        print("GOT RESPONSE:", response.status_code)

        return response.json()

    except requests.exceptions.RequestException as erro:

        print("ERROR GETTING ANALYSIS:", erro)

        return {
            "error": str(erro)
        }


def scan_file(filename, content, content_type):
    api_key = os.getenv("VT_API_KEY")
    headers = {
        "x-apikey": api_key
    }

    print(f"[File scan] Uploading {filename} ({len(content)} bytes) to VirusTotal...")

    try:
        response = requests.post(
            "https://www.virustotal.com/api/v3/files",
            headers=headers,
            files={
                "file": (filename, content, content_type)
            },
            timeout=30
        )
        response.raise_for_status()
        print(f"[File scan] VirusTotal accepted the upload (HTTP {response.status_code}).")
        return response.json()
    except requests.exceptions.RequestException as erro:
        print(f"[File scan] Upload failed: {erro}")
        return {
            "error": str(erro)
        }


def aguardar_analise(analysis_id, scan_type="URL"):
    inicio = time.monotonic()
    limite = inicio + ANALYSIS_TIMEOUT_SECONDS
    print(
        f"[{scan_type} scan] Waiting for VirusTotal analysis "
        f"(timeout: {ANALYSIS_TIMEOUT_SECONDS}s)..."
    )

    while time.monotonic() < limite:
        restante = limite - time.monotonic()
        request_timeout = min(10, restante)
        decorrido = ANALYSIS_TIMEOUT_SECONDS - restante

        print(
            f"[{scan_type} scan] Checking analysis status "
            f"({decorrido:.0f}s elapsed)..."
        )

        try:
            analise = get_analysis(analysis_id, timeout=request_timeout)
        except requests.exceptions.Timeout:
            if time.monotonic() >= limite:
                break
            raise

        if "error" in analise:
            if time.monotonic() >= limite:
                break
            print(f"[{scan_type} scan] Failed to retrieve analysis: {analise['error']}")
            return {
                "erro": analise['error']
            }

        attributes = analise.get("data", {}).get("attributes", {})
        status = attributes.get("status")

        if not status:
            print(f"[{scan_type} scan] VirusTotal returned no analysis status.")
            return {
                "erro": "Resposta inesperada do VirusTotal"
            }

        print(f"[{scan_type} scan] VirusTotal status: {status}")

        if status == "completed":
            print(f"[{scan_type} scan] Analysis completed successfully.")
            return analise["data"]["attributes"]["stats"]

        restante = limite - time.monotonic()
        if restante > 0:
            time.sleep(min(ANALYSIS_POLL_INTERVAL_SECONDS, restante))

    print(f"[{scan_type} scan] Timed out after {ANALYSIS_TIMEOUT_SECONDS} seconds.")
    return {
        "erro": "Timeout"
    }


def analisar_virustotal(url):
    resultado = scan_url(url)

    print("================================")
    print("VT RESPONSE:")
    print(resultado)
    print("================================")

    if "error" in resultado:
        return {
            "erro": resultado["error"]
        }

    analysis_id = resultado.get("data", {}).get("id")

    if not analysis_id:
        return {
            "erro": "resposta inesperada do virustotal"
        }

    return aguardar_analise(analysis_id, "URL")


def analisar_arquivo(filename, content, content_type):
    print(f"[File scan] Starting analysis for {filename} ({len(content)} bytes).")
    resultado = scan_file(filename, content, content_type)

    if "error" in resultado:
        return {
            "erro": resultado["error"]
        }

    analysis_id = resultado.get("data", {}).get("id")

    if not analysis_id:
        print("[File scan] VirusTotal response did not include an analysis ID.")
        return {
            "erro": "resposta inesperada do virustotal"
        }

    print("[File scan] Upload complete. Waiting for the analysis result.")
    return aguardar_analise(analysis_id, "File")


if __name__ == "__main__":

    resultado = analisar_virustotal("https://example.com")

    print(resultado)