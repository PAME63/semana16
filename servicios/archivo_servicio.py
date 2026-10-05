"""Lectura y escritura de archivos JSON (única capa que toca el disco)."""
import json
import os


class ArchivoServicio:
    @staticmethod
    def leer_json(ruta):
        if not os.path.exists(ruta):
            return []
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    @staticmethod
    def guardar_json(ruta, datos):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
