import requests
from bs4 import BeautifulSoup
from datetime import datetime

from modules.precios import guardar_precio, obtener_precio
from modules.materiales import MATERIALES

URL = "https://www.capris.cr/es/catalog/category/view/id/19596"


def obtener_precio_pla():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        respuesta = requests.get(URL, headers=headers, timeout=20)
        respuesta.raise_for_status()

        soup = BeautifulSoup(respuesta.text, "html.parser")
        texto = soup.get_text(" ", strip=True)

        precio_detectado = None

        for palabra in texto.split():
            if "₡" in palabra:
                precio_detectado = palabra.replace("₡", "").replace(",", "").strip()
                break

        if precio_detectado is None:
            respaldo = obtener_precio("PLA")
            return {
                "PLA": {
                    "precio_detectado": respaldo[1] if respaldo else None,
                    "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fuente": "Capris",
                    "estado": "usando_respaldo" if respaldo else "sin_datos"
                }
            }

        precio_numero = float(precio_detectado)
        guardar_precio("PLA", precio_numero, MATERIALES["PLA"]["unidad"], "Capris")

        return {
            "PLA": {
                "precio_detectado": precio_numero,
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fuente": "Capris",
                "estado": "actualizado"
            }
        }

    except Exception:
        respaldo = obtener_precio("PLA")
        return {
            "PLA": {
                "precio_detectado": respaldo[1] if respaldo else None,
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fuente": "Capris",
                "estado": "error_usando_respaldo" if respaldo else "error_sin_respaldo"
            }
        }


if __name__ == "__main__":
    print(obtener_precio_pla())
