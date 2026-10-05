import os
from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from pydantic import BaseModel, HttpUrl
from src.Model.Checks import analisar_url
from src.View.main import resultado_analise, resultado_arquivo, pagina_inicial
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.Model.VirusTotalChecks import analisar_arquivo, analisar_virustotal

MAX_FILE_SIZE = 32 * 1024 * 1024

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

    @app.get("/file")
    def file_page(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="file.html"
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

    @app.post("/check_file")
    def check_file(file: UploadFile = File(...)):
        filename = file.filename or "arquivo"
        print(f"[File scan] Received upload: {filename}")

        content = file.file.read(MAX_FILE_SIZE + 1)
        print(f"[File scan] Read {len(content)} bytes from upload.")

        if len(content) > MAX_FILE_SIZE:
            print(f"[File scan] Rejected {filename}: file exceeds the 32 MB limit.")
            raise HTTPException(
                status_code=413,
                detail="O arquivo deve ter no máximo 32 MB."
            )

        print(f"[File scan] Sending {filename} to VirusTotal for analysis.")
        virustotal = analisar_arquivo(
            filename,
            content,
            file.content_type or "application/octet-stream"
        )
        print(f"[File scan] Analysis finished for {filename}: {virustotal}")

        return resultado_arquivo(filename, virustotal)


    return app