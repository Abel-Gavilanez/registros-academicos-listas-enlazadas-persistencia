"""Casos de prueba MÍNIMOS (guion para el video de ejecución).

    python src/casos_prueba.py          # deja los archivos de ejemplo en data/
    python src/casos_prueba.py --tmp    # usa una carpeta temporal (no toca data/)
"""

import os
import sys
import tempfile

from lista_circular import ListaCircular
from lista_doble import ListaDoble
from lista_simple import ListaSimple
from modelos import Estudiante, Grupo, RegistroSemestre
from persistencia_csv import exportar_csv, importar_csv
from persistencia_json import exportar_json, importar_json

if "--tmp" in sys.argv:
    DATA = tempfile.mkdtemp(prefix="reto3_")
else:
    DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def encabezado(texto):
    print("\n" + "=" * 68)
    print(texto)
    print("=" * 68)


def verificar(condicion, mensaje):
    print(f"  [{'OK' if condicion else 'FALLO'}] {mensaje}")
    if not condicion:
        raise AssertionError(mensaje)


def semestre(anio, term, *materias):
    r = RegistroSemestre(anio, term)
    for cod, nombre, nota in materias:
        r.agregar_materia(cod, nombre, nota)
    return r


# ------------------------------------------------------------------ Lista Simple
def caso_lista_simple():
    encabezado("CASO 1 - LISTA SIMPLE: agregar 3, buscar, eliminar 1, mostrar, CSV, limpiar, importar")
    ruta = os.path.join(DATA, "inscritos.csv")
    ls = ListaSimple()
    for datos in (("1001", "Ana Torres", "ana.torres@uni.edu"),
                  ("1002", "Luis Mena", "luis.mena@uni.edu"),
                  ("1003", "Sofía Paredes", "sofia.paredes@uni.edu")):
        ls.insertar_final(Estudiante(*datos))
    print("  Tras agregar 3 inscritos:")
    for e in ls.recorrer():
        print("   ", e)
    verificar(len(ls) == 3, "hay 3 inscritos")

    print("  buscar('1002') ->", ls.buscar("1002"))
    verificar(ls.buscar("1002").nombres == "Luis Mena", "búsqueda por id encuentra a Luis Mena")
    verificar(ls.buscar("9999") is None, "búsqueda de id inexistente devuelve None")

    eliminado = ls.eliminar("1002")
    print("  eliminar('1002') ->", eliminado)
    verificar(len(ls) == 2 and ls.buscar("1002") is None, "se eliminó el nodo del medio")
    print("  Tras eliminar:")
    for e in ls.recorrer():
        print("   ", e)

    try:
        ls.insertar_final(Estudiante("1001", "Repetido", "r@uni.edu"))
        verificar(False, "debía rechazar id duplicado")
    except ValueError as e:
        verificar(True, f"id duplicado rechazado ({e})")

    n = exportar_csv(ruta, ls)
    verificar(os.path.isfile(ruta), f"exportado a CSV ({n} registros)")
    ls.limpiar()
    verificar(len(ls) == 0 and ls.cabeza is None, "estructura limpiada (0 elementos)")
    ls = importar_csv(ruta)
    print("  Tras importar el CSV:")
    for e in ls.recorrer():
        print("   ", e)
    verificar(len(ls) == 2 and ls.buscar("1003").nombres == "Sofía Paredes", "importación restituye los datos")
    return ls


# ------------------------------------------------------------------ Lista Doble
def caso_lista_doble():
    encabezado("CASO 2 - LISTA DOBLE: insertar DESORDENADO, comprobar orden, adelante/atrás, JSON")
    ruta = os.path.join(DATA, "historial.json")
    ld = ListaDoble()
    for reg in (semestre(2024, 1, ("MAT101", "Cálculo I", 8.0), ("PRO101", "Programación I", 9.0), ("FIS101", "Física I", 7.0)),
                semestre(2023, 2, ("MAT102", "Cálculo II", 7.0), ("PRO102", "Programación II", 8.0)),
                semestre(2025, 1, ("EST201", "Estadística", 9.0), ("BDD201", "Bases de Datos", 9.5)),
                semestre(2023, 1, ("INT100", "Introducción a la Ingeniería", 6.5), ("COM100", "Comunicación", 7.5)),
                semestre(2024, 2, ("ALG201", "Estructuras de Datos", 8.5), ("RED201", "Redes", 8.0))):
        print("  insertando", reg.etiqueta)
        ld.insertar_ordenado(reg)

    adelante = [r.etiqueta for r in ld.recorrer_adelante()]
    atras = [r.etiqueta for r in ld.recorrer_atras()]
    print("  recorrer_adelante():", " -> ".join(adelante))
    print("  recorrer_atras()   :", " -> ".join(atras))
    verificar(adelante == ["2023-1", "2023-2", "2024-1", "2024-2", "2025-1"], "queda ORDENADA por (anio, term)")
    verificar(atras == adelante[::-1], "el recorrido hacia atrás es el inverso exacto")

    print("  buscar('2024-1') ->", ld.buscar("2024-1"))
    verificar(ld.buscar("2024-1").promedio() == 8.0, "búsqueda por semestre encontró 2024-1 (promedio 8.00)")
    verificar(ld.buscar("2030-1") is None, "semestre inexistente devuelve None")
    try:
        ld.insertar_ordenado(semestre(2024, 1, ("X", "Duplicado", 5)))
        verificar(False, "debía rechazar semestre duplicado")
    except ValueError as e:
        verificar(True, f"semestre duplicado rechazado ({e})")

    print("  Top 3 promedios:")
    top = [(r.etiqueta, p) for r, p in ld.top_promedios(3)]
    for i, (etq, p) in enumerate(top, 1):
        print(f"    {i}. {etq} -> {p:.2f}")
    verificar([t[0] for t in top] == ["2025-1", "2024-2", "2024-1"], "Top 3 correcto (2025-1, 2024-2, 2024-1)")

    exportar_json(ruta, ld)
    ld.limpiar()
    verificar(len(ld) == 0, "historial limpiado")
    ld = importar_json(ruta, tipo_esperado="doble")
    verificar([r.etiqueta for r in ld.recorrer_adelante()] == adelante, "importación JSON conserva el orden y los datos")

    eliminado = ld.eliminar("2023-2")
    verificar(eliminado is not None and [r.etiqueta for r in ld.recorrer_atras()] == ["2025-1", "2024-2", "2024-1", "2023-1"],
              "eliminar('2023-2') mantiene los enlaces anterior/siguiente")
    return ld


# ------------------------------------------------------------------ Lista Circular
def caso_lista_circular():
    encabezado("CASO 3 - LISTA CIRCULAR: 3 grupos, búsqueda recursiva, rotar(2), ciclo, eliminar, JSON")
    ruta = os.path.join(DATA, "grupos.json")
    lc = ListaCircular()
    for datos in (("Grupo A", "Ing. Salazar", "Pilas y colas"),
                  ("Grupo B", "Ing. Vera", "Listas enlazadas"),
                  ("Grupo C", "Ing. Núñez", "Recursividad")):
        lc.insertar(Grupo(*datos))
    print("  Grupos:", " -> ".join(g.nombre_grupo for g in lc.recorrer(1)), "-> (vuelve a Grupo A)")
    verificar(lc.cola.siguiente is lc.cabeza, "el último nodo apunta a la cabeza (ciclo cerrado)")

    print("  buscar_recursivo('Grupo B') con traza:")
    g = lc.buscar_recursivo("Grupo B", verbose=True)
    verificar(g is not None and g.tutor == "Ing. Vera", "búsqueda recursiva encuentra Grupo B")
    print("  buscar_recursivo('Grupo Z') con traza:")
    verificar(lc.buscar_recursivo("Grupo Z", verbose=True) is None, "grupo inexistente: la recursión termina (no se cicla)")

    print("  Turno inicial:", lc.grupo_en_turno().nombre_grupo)
    lc.rotar(2)
    print("  rotar(2) -> turno:", lc.grupo_en_turno().nombre_grupo)
    verificar(lc.grupo_en_turno().nombre_grupo == "Grupo C", "rotar(2) deja el turno en Grupo C")
    nombres = [g.nombre_grupo for g in lc.recorrer(2)]
    print("  recorrer(2 vueltas) desde el turno:", nombres)
    verificar(nombres == ["Grupo C", "Grupo A", "Grupo B", "Grupo C", "Grupo A", "Grupo B"], "DEMUESTRA EL CICLO: tras C vuelve a A")
    lc.rotar(3)
    verificar(lc.grupo_en_turno().nombre_grupo == "Grupo C", "rotar(3) con 3 grupos = vuelta completa (mismo grupo)")

    exportar_json(ruta, lc)
    lc2 = importar_json(ruta, tipo_esperado="circular")
    verificar(lc2.grupo_en_turno().nombre_grupo == "Grupo C" and len(lc2) == 3, "JSON conserva grupos y el turno actual")

    eliminado = lc.eliminar("Grupo A")
    print("  eliminar('Grupo A') ->", eliminado.nombre_grupo)
    nombres = [g.nombre_grupo for g in lc.recorrer(2)]
    print("  recorrer(2 vueltas):", nombres)
    verificar(nombres == ["Grupo C", "Grupo B", "Grupo C", "Grupo B"], "tras eliminar, el ciclo se conserva (C -> B -> C ...)")
    verificar(lc.cola.siguiente is lc.cabeza, "el último nodo sigue apuntando a la cabeza")
    lc.eliminar("Grupo C")                      # se elimina el nodo en turno
    verificar(lc.grupo_en_turno().nombre_grupo == "Grupo B", "si se elimina el grupo en turno, el turno pasa al siguiente")
    lc.eliminar("Grupo B")
    verificar(lc.esta_vacia() and lc.grupo_en_turno() is None, "eliminar el último deja la lista vacía sin errores")
    return lc


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    print(f"Carpeta de datos: {os.path.normpath(DATA)}")
    caso_lista_simple()
    caso_lista_doble()
    caso_lista_circular()
    encabezado("RESULTADO: TODOS LOS CASOS MÍNIMOS PASARON")
