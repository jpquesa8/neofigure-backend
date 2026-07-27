MATERIALES = {
    "PLA": {
        "busqueda": "filamento PLA",
        "unidad": "gramos"
    },
    "PLA_SILK": {
        "busqueda": "filamento PLA Silk",
        "unidad": "gramos"
    },
    "PETG": {
        "busqueda": "filamento PETG",
        "unidad": "gramos"
    },
    "RESINA_UV": {
        "busqueda": "resina UV",
        "unidad": "ml"
    }
}

def listar_materiales():
    return MATERIALES

def material_existe(clave: str) -> bool:
    return clave in MATERIALES

def obtener_material(clave: str):
    return MATERIALES.get(clave)

def obtener_unidad(clave: str):
    material = MATERIALES.get(clave)
    return material["unidad"] if material else None

def obtener_busqueda(clave: str):
    material = MATERIALES.get(clave)
    return material["busqueda"] if material else None
