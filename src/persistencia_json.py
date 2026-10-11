"""Persistencia en JSON (Historial -> ListaDoble, Grupos -> ListaCircular).

El JSON incluye el campo "tipo" ("simple" | "doble" | "circular"), de modo que
``importar_json`` reconstruye la clase de lista correcta sin que el llamador
tenga que indicarla.
"""

import json
import os

from lista_circular import ListaCircular
from lista_doble import ListaDoble
from lista_simple import ListaSimple

_TIPOS = {"simple": ListaSimple, "doble": ListaDoble, "circular": ListaCircular}


def exportar_json(ruta, lista):
    """Guarda cualquiera de las tres listas en ``ruta`` (escritura atómica)."""
    carpeta = os.path.dirname(os.path.abspath(ruta))
    os.makedirs(carpeta, exist_ok=True)
    temporal = ruta + ".tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(lista.to_dict(), f, ensure_ascii=False, indent=2)
    os.replace(temporal, ruta)
    return len(lista)


def importar_json(ruta, tipo_esperado=None):
    """Lee un JSON y devuelve la lista correspondiente.

    ``tipo_esperado`` ('doble', 'circular'...) permite rechazar un archivo
    que contenga otra estructura.
    """
    if not os.path.isfile(ruta):
        raise ValueError(f"No existe el archivo: {ruta}")
    try:
        with open(ruta, encoding="utf-8-sig") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON mal formado ({e}).") from None
    if not isinstance(datos, dict) or datos.get("tipo") not in _TIPOS:
        raise ValueError('El JSON no tiene un campo "tipo" válido (simple, doble o circular).')
    if tipo_esperado and datos["tipo"] != tipo_esperado:
        raise ValueError(f"Se esperaba una lista '{tipo_esperado}' pero el archivo es '{datos['tipo']}'.")
    return _TIPOS[datos["tipo"]].from_dict(datos)
