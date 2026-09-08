from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from src.Model.Checks import analisar_url
from src.View.main import resultado_analise, pagina_inicial
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


class URLCheckerRequest(BaseModel):
    url: HttpUrl


def criar_app():

    app = FastAPI()



    app.mount(
        "/static",
        StaticFiles(directory="src/View/static"),
        name="static"
    )

    print(app.routes)

    templates = Jinja2Templates(
        directory="src/View/templates"
    )


    @app.get("/")
    def home(request: Request):

        return templates.TemplateResponse(
            request=request,
            name="index.html"
        )
        


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