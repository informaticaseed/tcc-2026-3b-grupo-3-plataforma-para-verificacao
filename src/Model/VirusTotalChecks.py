import os
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


if __name__ == "__main__":

    resultado = scan_url("https://example.com")

    analysis_id = resultado["data"]["id"]

    analise = get_analysis(analysis_id)

    attributes = analise["data"]["attributes"]

    print("STATUS:", attributes.get("status"))
    print("STATS:", attributes.get("stats"))