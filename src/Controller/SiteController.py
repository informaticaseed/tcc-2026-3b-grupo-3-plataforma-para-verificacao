import os
from fastapi import FastAPI, Request
from pydantic import BaseModel, HttpUrl
from src.Model.Checks import analisar_url
from src.View.main import resultado_analise, pagina_inicial
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.Model.VirusTotalChecks import analisar_virustotal


class URLCheckerRequest(BaseModel):
    url: HttpUrl


def criar_app():

    app = FastAPI()


    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(current_dir, "..", "View", "static")

    
    app.mount(
        "/static",
        StaticFiles(directory=static_path),
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

        print("Chamando o VT")

      # Envia a URL para o Model
        score, reasons = analisar_url(url)

        virustotal = analisar_virustotal(url)

        print("VT finished")


        # Envia o resultado para a View
        return resultado_analise(
            url,
            score,
            reasons,
            virustotal
        )


    return app