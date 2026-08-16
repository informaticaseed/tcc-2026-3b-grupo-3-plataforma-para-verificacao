import base64
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
import httpx

app = FastAPI()

@app.get("/")
#Rota Get feita apenas para verificar se o FastAPI está funcionando(quando o codigo estiver pronto ela sera excluida)
def home():
    return{"message:": "URL Checker API is running!"}

class URLCheckerRequest(BaseModel):
    url: HttpUrl

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
    
#def check_ip_adress(url):


#TDL: adicionar verificação de IP(Em progresso)
#TDL: adicionar verificador de keywords, eg: login, bank, etc
#TDL: adicionar um ngc pra verificar quantos subdominios o link tem, eg google.com.confiavel.mimmimi.123




@app.post("/check_url")
async def check_url(payload: URLCheckerRequest):

#Transforma o que o pydantic recebe(URL) em uma string para ser analizada pelas funções acima.
    url = str(payload.url)

    score = 0
    reasons = []

#As funções retornam os valores e o motivo, sendo esses adicionados e listados através do codigo abaixo
    points, reason = check_at_symbol(url)
    score += points
    reasons.append(reason)

    points, reason = check_length(url)
    score += points
    reasons.append(reason)

    points, reason = check_http(url)
    score += points
    reasons.append(reason)

#Os pontos são mostrados na frontend para o usuario através desse return abaixo
    return {
        "url": url,
        "Nivel de perigo": score,
        "Motivo:": reasons
    }

