from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from src.Model.Checks import analisar_url
from src.View.main import resultado_analise, pagina_inicial


class URLCheckerRequest(BaseModel):
    url: HttpUrl


def criar_app():

    app = FastAPI()


    @app.get("/")
    def home():

        return pagina_inicial()


    @app.post("/check_url")
    async def check_url(payload: URLCheckerRequest):

        # Converte a URL recebida pelo Pydantic para string
        url = str(payload.url)

        # Envia a URL para o Model
        score, reasons = analisar_url(url)

        # Envia o resultado para a View
        return resultado_analise(
            url,
            score,
            reasons
        )


    return app