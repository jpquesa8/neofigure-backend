import requests
from bs4 import BeautifulSoup
from datetime import datetime

from utils.archivos import guardar_precios

URL = "https://www.capris.cr/es/catalog/category/view/id/19596"


def obtener_precio_pla():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    respuesta = requests.get(URL, headers=headers, timeout=20)
    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")

    texto = soup.get_text(" ", strip=True)

    precio_detectado = "No encontrado"

    for palabra in texto.split():
        if "₡" in palabra:
            precio_detectado = palabra
            break

    datos = {
        "PLA": {
            "precio_detectado": precio_detectado,
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fuente": "Capris"
        }
    }

    guardar_precios(datos)

    return datos


if __name__ == "__main__":
    print(obtener_precio_pla())
