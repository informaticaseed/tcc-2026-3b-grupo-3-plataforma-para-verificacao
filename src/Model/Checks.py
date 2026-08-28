from urllib.parse import urlparse


def check_length(url):
#URLS muito grandes podem ser utilizados para fazer o usuario "se perder" e não encontrar o dominio principal do site.
    if len(url) > 75:
        return 10, "O URL é muito grande"
    else:
        return 0, "O tamanho da URL é normal"
    
def check_http(url):
#O https é seguro e encriptado, já o http não.
    if url.startswith("https"):
        return 0, "O URL utiliza HTTPS"
    else:
        return 20, "O URL utiliza HTTP"
    
def check_at_symbol(url):
#O @ pode ser utilizado para esconder o dominio real do site, sendo utilizado em links de phishing.
    if "@" in url:
        return 10, "O URL possui um @"
    else:
        return 0, "O URL não possui um @"

def check_ip(url):
    # URLs que utilizam um endereço IP tem mais chance de ser phishing(Não garante pois sites de roteadores utilizam ipv4 como "link")
    hostname = urlparse(url).hostname

    if hostname is None:
        return 0, "O link não tem formato em IP"

    parts = hostname.split(".")

    if len(parts) == 4 and all(part.isnumeric() for part in parts):
        return 20, "O URL utiliza um endereço IP"

    return 0, "O URL utiliza um domínio"


def analisar_url(url):

    score = 0; reasons=[]
    
    points, reason = check_at_symbol(url)
    score += points
    reasons.append(reason)
    
    points, reason = check_length(url)
    score += points
    reasons.append(reason)
    
    points, reason = check_http(url)
    score += points
    reasons.append(reason)

    points, reason = check_ip(url)
    score += points
    reasons.append(reason)

    return score, reasons