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
        }
    )

    return response.json()

def get_analysis(analysis_id):

    api_key = os.getenv("VT_API_KEY")

    headers = {
        "x-apikey": api_key
    }

    response = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
        headers=headers
    )

    return response.json()

def analisar_virustotal(url):

    resultado = scan_url(url)

    analysis_id = resultado['data']['id']

    while True:

        analise = get_analysis(analysis_id)

        status = analise ["data"]["attributes"]["status"]

        print("Status:", status)

        if status == "completed":
            return analise["data"]["attributes"]["stats"]

        time.sleeps(5)


if __name__ == "__main__":

    resultado = analisar_virustotal("https://example.com")

    print(resultado)