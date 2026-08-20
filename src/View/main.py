def resultado_analise(url, score, reasons):

    return {
            "url": url,
            "Nivel de perigo": score,
            "Motivo:": reasons
        }

def pagina_inicial():

    return {
        "Message": "URL Checker API is running"
    }