from contextlib import asynccontextmanager
from fastapi import FastAPI

from modules.precios import inicializar

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código al iniciar
    inicializar()
    yield
    # Código al cerrar (vacío por ahora)

app = FastAPI(lifespan=lifespan)

@app.get("/")
def inicio():
    return {
        "mensaje": "Backend NeoFigure CR funcionando"
    }
