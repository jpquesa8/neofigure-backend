import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional

from modules.precios import guardar_precio, obtener_precio
from modules.materiales import MATERIALES, obtener_unidad

# URLs de búsqueda por código (SKU) en Capris (Magento)
BASE_URL = "https://www.capris.cr/es/catalogsearch/result/"

# Lista de códigos de productos PLA estándar
CODIGOS_PLA = [
    "075556",  # CREALITY PLA negro 1kg
    "070130",  # DREMEL PLA oro
    "075680",  # CREALITY Hyper PLA café
]

# Lista de códigos de productos PLA Silk (si luego quieres agregar códigos específicos)
CODIGOS_PLA_SILK: List[str] = [
    # Ejemplo: "XXXXXX",  # PLA Silk XXX
]

# Lista de códigos de productos PETG
CODIGOS_PETG = [
    "075630",  # CREALITY PETG rojo 1kg
]

# Lista de códigos de resinas UV
CODIGOS_RESINA_UV = [
    "075648",  # Resina rígida verde (puede usarse como UV genérica)
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
    """
    if not texto:
        return None

    # Eliminar todo lo que no sea dígito, punto o coma
    texto_limpio = re.sub(r"[^\d.,]", "", texto)
    if not texto_limpio:
        return None

    n_puntos = texto_limpio.count(".")
    n_comas = texto_limpio.count(",")

    if n_puntos == 0 and n_comas == 0:
        try:
            return float(texto_limpio)
        except ValueError:
            return None

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

    texto_limpio = texto_limpio.replace(",", ".")
    try:
        return float(texto_limpio)
    except ValueError:
        return None


def _buscar_producto_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Busca un producto en 
    
