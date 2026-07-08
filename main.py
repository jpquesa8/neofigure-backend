from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {
        "mensaje": "Backend NeoFigure CR funcionando"
    }
