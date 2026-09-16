import os
import time
import requests


def scan_url(url):

    api_key = os.getenv("VT_API_KEY")

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

def get_analysis(analysis_id):

    api_key = os.getenv("VT_API_KEY")

    headers = {
        "x-apikey": api_key
    }

    print("GETTING ANALYSIS...")

    try:
        response = requests.get(
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        print("GOT RESPONSE:", response.status_code)

        return response.json()

    except requests.exceptions.RequestException as erro:

        print("ERROR GETTING ANALYSIS:", erro)

        return {
            "error": str(erro)
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
        return{
            "erro": "resposta inesperada do virustotal"
        }

    inicio = time.time()

    while time.time() - inicio <180:

        print("Before GET")

        analise = get_analysis(analysis_id)
        print("ANALYISIS RESPONSE:")
        print(analise)

        print("After GET")

        if "error" in analise:
            return {
                "erro": analise['error']
            }

        attributes = analise.get("data", {}).get("attributes", {})
        status = attributes.get("status")

        if not status:
            return {
                "erro": "Resposta inesperada do VirusTotal"
            }

        print("Status:", status)

        if status == "completed":
            return analise["data"]["attributes"]["stats"]

        time.sleep(20)

        
    return {
        "erro": "Timeout"
    }


if __name__ == "__main__":

    resultado = analisar_virustotal("https://example.com")

    print(resultado)