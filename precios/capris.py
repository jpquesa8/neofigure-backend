import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional

from modules.precios import guardar_precio, obtener_precio
from modules.materiales import MATERIALES

# URLs de búsqueda por código (SKU) en Capris (Magento)
BASE_URL = "https://www.capris.cr/es/catalogsearch/result/"

# Lista de códigos de productos PLA
CODIGOS_PLA = [
    "075556",  # CREALITY PLA negro 1kg
    "070130",  # DREMEL PLA oro
    "075680",  # CREALITY Hyper PLA café
]

# Lista de códigos de productos PETG
CODIGOS_PETG = [
    "075630",  # CREALITY PETG rojo 1kg
]

# Lista de códigos de resinas
CODIGOS_RESINA = [
    "075648",  # Resina rígida verde
    "075690",  # Resina lavable gris
    "075689",  # Resina lavable blanca
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}

TIMEOUT = 15


def _extraer_precio_texto(texto: str) -> Optional[float]:
    """
    Extrae un precio numérico de un string que puede venir con símbolo ₡, comas, etc.
    Ejemplos:
      - "₡3,898.50"
      - "3,898.50"
      - "CRC3898.50"
    Devuelve float o None si no hay número válido.
    """
    if not texto:
        return None

    # Eliminar todo lo que no sea dígito, punto o coma
    texto_limpio = re.sub(r"[^\d.,]", "", texto)
    if not texto_limpio:
        return None

    # Estrategia simple: si hay más de un separador, asumimos que el último es el decimal
    n_puntos = texto_limpio.count(".")
    n_comas = texto_limpio.count(",")

    if n_puntos == 0 and n_comas == 0:
        try:
            return float(texto_limpio)
        except ValueError:
            return None

    # Si hay ambos, usamos el último separador como decimal
    if n_puntos > 0 and n_comas > 0:
        if texto_limpio.rfind(".") > texto_limpio.rfind(","):
            texto_limpio = texto_limpio.replace(",", "")
        else:
            texto_limpio = texto_limpio.replace(".", "")

        texto_limpio = texto_limpio.replace(",", ".")
        try:
            return float(texto_limpio)
        except ValueError:
            return None

    # Solo un tipo de separador
    texto_limpio = texto_limpio.replace(",", ".")
    try:
        return float(texto_limpio)
    except ValueError:
        return None


def _buscar_producto_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Busca un producto en Capris por código (SKU).
    Devuelve:
      {
          "nombre": str,
          "precio": float,
          "url": str,
          "codigo": str,
      }
    o None si no se encuentra precio válido.
    """
    params = {"q": codigo}
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Ajusta selectores si ves que Capris usa otros nombres de clase
    for item in soup.select(".product-item, .product-item-info"):
        nombre_el = item.select_one(
            ".product-item-link, .product-name a, a.product-item-link"
        )
        precio_el = item.select_one(
            ".price-wrapper .price, .price, [data-price-amount]"
        )

        if not nombre_el:
            continue

        nombre = nombre_el.get_text(strip=True)
        precio: Optional[float] = None

        if precio_el:
            texto_precio = precio_el.get_text(strip=True)
            precio = _extraer_precio_texto(texto_precio)

        if precio is not None and precio > 0:
            url_producto = nombre_el.get("href", "")
            if url_producto and not url_producto.startswith("http"):
                url_producto = "https://www.capris.cr" + url_producto

            return {
                "nombre": nombre,
                "precio": precio,
                "url": url_producto,
                "codigo": codigo,
            }

    # No se encontró precio en HTML crudo
    return None


def obtener_precios_por_codigos(
    codigos: List[str],
    nombre_material: str,
) -> Dict[str, Any]:
    """
    Obtiene precios para una lista de códigos asociados a un material (PLA, PETG, resina, etc.).
    Guarda en SQLite el primer precio válido que encuentre y devuelve información detallada.
    """
    precio_detectado: Optional[float] = None
    codigo_usado: Optional[str] = None
    nombre_producto: Optional[str] = None
    url_producto: Optional[str] = None
    detalles_codigos: List[Dict[str, Any]] = []

    for codigo in codigos:
        info = _buscar_producto_por_codigo(codigo)
        registro = {
            "codigo": codigo,
            "encontrado": bool(info),
            "precio": info["precio"] if info else None,
            "nombre": info["nombre"] if info else None,
        }
        detalles_codigos.append(registro)

        if info and precio_detectado is None:
            precio_detectado = info["precio"]
            codigo_usado = codigo
            nombre_producto = info["nombre"]
            url_producto = info["url"]

    fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Si no se obtuvo precio, usar respaldo de SQLite
    if precio_detectado is None:
        respaldo = obtener_precio(nombre_material)
        return {
            "material": nombre_material,
            "precio_detectado": None,
            "fecha_actualizacion": fecha_actualizacion,
            "fuente": "Capris",
            "estado": "usando_respaldo" if respaldo else "error_sin_respaldo",
            "tiene_respaldo": bool(respaldo),
            "codigos_revisados": detalles_codigos,
        }

    # Guardar precio en SQLite
    guardar_precio(
        nombre_material,
        precio_detectado,
        MATERIALES[nombre_material]["unidad"],
        "Capris"
    )

    return {
        "material": nombre_material,
        "precio_detectado": precio_detectado,
        "fecha_actualizacion": fecha_actualizacion,
        "fuente": "Capris",
        "codigo_usado": codigo_usado,
        "nombre_producto": nombre_producto,
        "url_producto": url_producto,
        "codigos_revisados": detalles_codigos,
    }


def obtener_precio_pla() -> Dict[str, Any]:
    """
    Obtiene precio de PLA desde Capris usando búsqueda por código (SKU).
    """
    return obtener_precios_por_codigos(CODIGOS_PLA, "PLA")


def obtener_precio_petg() -> Dict[str, Any]:
    """
    Obtiene precio de PETG desde Capris usando búsqueda por código (SKU).
    """
    return obtener_precios_por_codigos(CODIGOS_PETG, "PETG")


def obtener_precio_resina() -> Dict[str, Any]:
    """
    Obtiene precio de resina desde Capris usando búsqueda por código (SKU).
    Usa el primer código de resina como referencia para el precio.
    """
    return obtener_precios_por_codigos(CODIGOS_RESINA, "RESINA")


def obtener_todos_los_precios() -> Dict[str, Any]:
    """
    Obtiene precios para todos los materiales configurados (PLA, PETG, resina).
    Devuelve un diccionario con los resultados de cada uno.
    """
    resultados = {}

    resultados["PLA"] = obtener_precio_pla()
    resultados["PETG"] = obtener_precio_petg()
    resultados["RESINA"] = obtener_precio_resina()

    return resultados


if __name__ == "__main__":
    # Prueba con todos los materiales
    import json
    resultados = obtener_todos_los_precios()
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
