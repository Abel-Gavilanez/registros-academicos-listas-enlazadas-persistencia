"""Persistencia en CSV (usada para Inscritos -> ListaSimple)."""

import csv
import os

from lista_simple import ListaSimple
from modelos import Estudiante

CAMPOS = ("id", "nombres", "correo")


def exportar_csv(ruta, lista):
    """Guarda la ListaSimple en ``ruta`` con encabezado id,nombres,correo.

    La escritura es atómica: primero a un archivo temporal y luego ``os.replace``,
    así un fallo a mitad de camino no corrompe el archivo anterior.
    """
    carpeta = os.path.dirname(os.path.abspath(ruta))
    os.makedirs(carpeta, exist_ok=True)
    temporal = ruta + ".tmp"
    with open(temporal, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        for est in lista.recorrer():
            escritor.writerow(est.to_dict())
    os.replace(temporal, ruta)
    return len(lista)


def importar_csv(ruta, reportar=print):
    """Lee un CSV y devuelve una ListaSimple nueva.

    * Si el archivo no existe o el encabezado no es id,nombres,correo -> ValueError.
    * Las filas inválidas o con id repetido se omiten y se informan con ``reportar``.
    """
    if not os.path.isfile(ruta):
        raise ValueError(f"No existe el archivo: {ruta}")
    lista = ListaSimple()
    with open(ruta, newline="", encoding="utf-8-sig") as f:    # utf-8-sig tolera BOM de Excel
        lector = csv.DictReader(f)
        if tuple(lector.fieldnames or ()) != CAMPOS:
            raise ValueError(f"Encabezado inválido. Se esperaba: {','.join(CAMPOS)}")
        for fila in lector:
            try:
                lista.insertar_final(Estudiante.from_dict(fila))
            except (ValueError, TypeError) as e:
                reportar(f"  Línea {lector.line_num} omitida: {e}")
    return lista
