def resultado_analise(url, score, reasons, virustotal):

    return {
            "url": url,
            "Nivel de perigo": score,
            "Motivo:": reasons,
            "VirusTotal": virustotal
        }

def pagina_inicial():

    return {
        "Message": "URL Checker API is running"
    }