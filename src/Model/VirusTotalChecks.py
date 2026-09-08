import os
import time
import requests


def scan_url(url):

    api_key = os.getenv("VT_API_KEY")

    headers = {
        "x-apikey": api_key
    }

    response = requests.post(
    "https://www.virustotal.com/api/v3/urls",
    headers=headers,
    data={
        "url": url
    },
    timeout=10
    )

    return response.json()

def get_analysis(analysis_id):

    api_key = os.getenv("VT_API_KEY")

    headers = {
        "x-apikey": api_key
    }

    print("GETTING ANALYSIS...")

    response = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
        headers=headers,
        timeout=10
    )

    print("GOT RESPONSE:", response.status_code)

    return response.json()

def analisar_virustotal(url):

    resultado = scan_url(url)

    print("================================")
    print("VT RESPONSE:")
    print(resultado)
    print("================================")

    if "error" in resultado:
        return {
            "erro": resultado["error"]["message"]
        }

    analysis_id = resultado["data"]["id"]

    tentativas = 0

    while tentativas < 10:

        print("Before GET")

        analise = get_analysis(analysis_id)
        print("ANALYISIS RESPONSE:")
        print(analise)

        print("After GET")

        status = analise["data"]["attributes"]["status"]

        print("Status:", status)

        if status == "completed":
            return analise["data"]["attributes"]["stats"]

        time.sleep(20)

        tentativas += 1
    return {
        "erro": "Timeout"
    }


if __name__ == "__main__":

    resultado = analisar_virustotal("https://example.com")

    print(resultado)