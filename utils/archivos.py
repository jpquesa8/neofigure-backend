import json
from pathlib import Path

RUTA_PRECIOS = Path("storage/precios.json")


def leer_precios():
    if not RUTA_PRECIOS.exists():
        return {}

    with open(RUTA_PRECIOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_precios(datos):
    RUTA_PRECIOS.parent.mkdir(parents=True, exist_ok=True)

    with open(RUTA_PRECIOS, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
