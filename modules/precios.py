import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "materiales.db")


def conectar_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def crear_tabla_precios():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                precio_actual REAL NOT NULL,
                unidad TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL,
                fuente TEXT NOT NULL
            )
        """)
        conn.commit()


def guardar_precio(nombre, precio_actual, unidad, fuente="Capris"):
    fecha_actualizacion = datetime.now().strftime("%d-%m-%Y")

    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO materiales (nombre, precio_actual, unidad, fecha_actualizacion, fuente)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(nombre) DO UPDATE SET
                precio_actual=excluded.precio_actual,
                unidad=excluded.unidad,
                fecha_actualizacion=excluded.fecha_actualizacion,
                fuente=excluded.fuente
        """, (nombre, precio_actual, unidad, fecha_actualizacion, fuente))
        conn.commit()


def obtener_precio(nombre):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, precio_actual, unidad, fecha_actualizacion, fuente
            FROM materiales
            WHERE nombre = ?
        """, (nombre,))
        return cursor.fetchone()


def listar_precios():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, precio_actual, unidad, fecha_actualizacion, fuente
            FROM materiales
            ORDER BY nombre ASC
        """)
        return cursor.fetchall()


def eliminar_precio(nombre):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materiales WHERE nombre = ?", (nombre,))
        conn.commit()


def inicializar():
    crear_tabla_precios()
