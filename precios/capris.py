import requests
from precios.materiales import MATERIALES

URL_CAPRIS = "https://www.capris.cr/"


def obtener_precios():
    resultados = {}

    for nombre, datos in MATERIALES.items():
        resultados[nombre] = {
            "busqueda": datos["busqueda"],
            "unidad": datos["unidad"],
            "precio": None,
            "estado": "pendiente"
        }

    return resultados


if __name__ == "__main__":
    precios = obtener_precios()
    print(precios)
