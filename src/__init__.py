import uvicorn

from src.Controller.SiteController import criar_app

def Inicializar():

        app = criar_app()

        uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
        )