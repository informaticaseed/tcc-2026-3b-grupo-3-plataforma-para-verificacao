import ipaddress
import re
from urllib.parse import urlparse


MAX_RISK_SCORE = 100
SUSPICIOUS_HOST_TOKENS = {
    "account",
    "bank",
    "confirm",
    "login",
    "password",
    "payment",
    "secure",
    "signin",
    "verify",
    "wallet",
}
SUSPICIOUS_PATH_TOKENS = {
    "account",
    "confirm",
    "login",
    "password",
    "signin",
    "verify",
    "wallet",
}


def check_length(url):
    length = len(url)
    if length > 200:
        return 15, "O URL tem mais de 200 caracteres"
    if length > 120:
        return 10, "O URL tem mais de 120 caracteres"
    if length > 75:
        return 5, "O URL tem mais de 75 caracteres"
    return 0, ""


def check_http(url):
    scheme = urlparse(url).scheme.lower()
    if scheme == "http":
        return 10, "O URL usa HTTP sem criptografia"
    if scheme != "https":
        return 15, "O URL não usa HTTP ou HTTPS"
    return 0, ""


def check_at_symbol(url):
    parsed = urlparse(url)
    if "@" in parsed.netloc:
        return 25, "O URL contém credenciais antes do domínio (@)"
    return 0, ""


def check_ip(url):
    hostname = urlparse(url).hostname
    if not hostname:
        return 0, ""

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return 0, ""

    return 25, "O domínio é um endereço IP, em vez de um nome de domínio"


def check_subdomains(url):
    hostname = urlparse(url).hostname
    if not hostname:
        return 0, ""

    labels = hostname.rstrip(".").split(".")
    if len(labels) > 6:
        return 12, "O domínio tem muitos níveis de subdomínio"
    if len(labels) > 4:
        return 8, "O domínio tem vários níveis de subdomínio"
    return 0, ""


def check_punycode(url):
    hostname = urlparse(url).hostname or ""
    if any(label.startswith("xn--") for label in hostname.lower().split(".")):
        return 20, "O domínio contém um rótulo internacional codificado em Punycode"
    return 0, ""


def check_suspicious_terms(url):
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    host_tokens = set(filter(None, re.split(r"[^a-z0-9]+", hostname)))
    flagged_host_tokens = host_tokens & SUSPICIOUS_HOST_TOKENS
    host_points = min(len(flagged_host_tokens) * 12, 24)

    path_tokens = set(filter(None, re.split(r"[^a-z0-9]+", parsed.path.lower())))
    flagged_path_tokens = path_tokens & SUSPICIOUS_PATH_TOKENS
    path_points = min(len(flagged_path_tokens) * 6, 12)

    points = host_points + path_points
    if not points:
        return 0, ""

    matched = sorted(flagged_host_tokens | flagged_path_tokens)
    return points, f"O domínio ou caminho contém termos usados em páginas de acesso/conta ({', '.join(matched)})"


def check_port(url):
    parsed = urlparse(url)
    try:
        port = parsed.port
    except ValueError:
        return 15, "O URL contém uma porta inválida"

    standard_port = {"http": 80, "https": 443}.get(parsed.scheme.lower())
    if port is not None and port != standard_port:
        return 10, f"O URL usa uma porta não padrão ({port})"
    return 0, ""


def analisar_url(url):
    checks = (
        check_at_symbol,
        check_length,
        check_http,
        check_ip,
        check_subdomains,
        check_punycode,
        check_suspicious_terms,
        check_port,
    )
    score = 0
    reasons = []

    for check in checks:
        points, reason = check(url)
        score += points
        if reason:
            reasons.append(f"{reason} (+{points})")

    score = min(score, MAX_RISK_SCORE)
    if not reasons:
        reasons.append("Nenhum indicador de risco foi encontrado nas verificações locais.")

    return score, reasons
