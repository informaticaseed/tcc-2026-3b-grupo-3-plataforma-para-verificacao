from src import Inicializar
from dotenv import load_dotenv

load_dotenv()

import os

load_dotenv()

print("VT KEY LOADED:", bool(os.getenv("VT_API_KEY")))

if __name__ == "__main__":
    Inicializar()