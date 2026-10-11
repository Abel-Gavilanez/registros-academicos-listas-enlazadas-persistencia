"""Menú principal en consola - Reto 3: Registros académicos con listas enlazadas.

Ejecutar:   python src/app.py
"""

import os

from lista_circular import ListaCircular
from lista_doble import ListaDoble
from lista_simple import ListaSimple
from modelos import NOTA_MAX, NOTA_MIN, Estudiante, Grupo, RegistroSemestre
from persistencia_csv import exportar_csv, importar_csv
from persistencia_json import exportar_json, importar_json

DIR_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
RUTA_INSCRITOS = os.path.join(DIR_DATA, "inscritos.csv")
RUTA_HISTORIAL = os.path.join(DIR_DATA, "historial.json")
RUTA_GRUPOS = os.path.join(DIR_DATA, "grupos.json")


# ----------------------------------------------------------------- utilidades de entrada
def pedir_texto(mensaje, opcional=False):
    while True:
        texto = input(mensaje).strip()
        if texto or opcional:
            return texto
        print("  ! Este dato es obligatorio.")


def pedir_entero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            n = int(input(mensaje).strip())
        except ValueError:
            print("  ! Ingrese un número entero.")
            continue
        if (minimo is not None and n < minimo) or (maximo is not None and n > maximo):
            print(f"  ! El valor debe estar entre {minimo} y {maximo}." if None not in (minimo, maximo)
                  else f"  ! El valor debe ser >= {minimo}.")
            continue
        return n


def pedir_nota(mensaje):
    while True:
        try:
            nota = float(input(mensaje).strip().replace(",", "."))
        except ValueError:
            print("  ! Ingrese un número (ej. 8.5).")
            continue
        if NOTA_MIN <= nota <= NOTA_MAX:
            return nota
        print(f"  ! La nota debe estar entre {NOTA_MIN:g} y {NOTA_MAX:g}.")


def mostrar_ruta(ruta):
    """Ruta legible (relativa a la carpeta desde donde se ejecuta, si es posible)."""
    try:
        return os.path.relpath(ruta)
    except ValueError:                 # p. ej. otra unidad en Windows
        return os.path.normpath(ruta)


def pedir_ruta(mensaje, por_defecto):
    texto = input(f"{mensaje} [Enter = {mostrar_ruta(por_defecto)}]: ").strip()
    return texto or por_defecto


def confirmar(mensaje):
    return input(f"{mensaje} (s/n): ").strip().lower() in ("s", "si", "sí", "y")


def titulo(texto):
    print("\n" + "=" * 62)
    print(f" {texto}")
    print("=" * 62)


def mostrar_menu(nombre, opciones):
    titulo(nombre)
    for clave, (texto, _) in opciones.items():
        print(f"  {clave}. {texto}")
    return input("Opción: ").strip()


def ejecutar_seguro(accion):
    """Ejecuta una acción mostrando los errores de validación sin cerrar el programa."""
    try:
        accion()
    except (ValueError, RecursionError, OSError) as e:
        print(f"  ! Error: {e}")


# --------------------------------------------------------------------------- aplicación
class Aplicacion:
    def __init__(self):
        self.inscritos = ListaSimple()
        self.historial = ListaDoble()
        self.grupos = ListaCircular()

    # ============================================================ 1. Inscritos
    def menu_inscritos(self):
        opciones = {
            "1": ("Agregar inscrito (al final)", self.ins_agregar),
            "2": ("Eliminar inscrito por id", self.ins_eliminar),
            "3": ("Buscar inscrito por id", self.ins_buscar),
            "4": ("Mostrar inscritos (recorrer)", self.ins_mostrar),
            "5": ("Exportar a CSV", self.ins_exportar),
            "6": ("Importar desde CSV", self.ins_importar),
            "7": ("Limpiar estructura", self.ins_limpiar),
            "0": ("Volver", None),
        }
        self._bucle("1. INSCRITOS (Lista simple)", opciones)

    def ins_agregar(self):
        id_ = pedir_texto("  id: ")
        nombres = pedir_texto("  nombres: ")
        correo = pedir_texto("  correo: ")
        self.inscritos.insertar_final(Estudiante(id_, nombres, correo))
        print("  ✔ Inscrito agregado al final.")

    def ins_eliminar(self):
        eliminado = self.inscritos.eliminar(pedir_texto("  id a eliminar: "))
        print(f"  ✔ Eliminado: {eliminado}" if eliminado else "  ! No existe ese id.")

    def ins_buscar(self):
        est = self.inscritos.buscar(pedir_texto("  id a buscar: "))
        print(f"  ✔ Encontrado: {est}" if est else "  ! No existe ese id.")

    def ins_mostrar(self):
        if self.inscritos.esta_vacia():
            print("  (no hay inscritos)")
            return
        print(f"  Inscritos ({len(self.inscritos)}):")
        for i, est in enumerate(self.inscritos.recorrer(), 1):
            print(f"   {i}. {est}")

    def ins_exportar(self):
        ruta = pedir_ruta("  Ruta CSV", RUTA_INSCRITOS)
        n = exportar_csv(ruta, self.inscritos)
        print(f"  ✔ {n} inscritos exportados a {mostrar_ruta(ruta)}")

    def ins_importar(self):
        ruta = pedir_ruta("  Ruta CSV", RUTA_INSCRITOS)
        self.inscritos = importar_csv(ruta)
        print(f"  ✔ {len(self.inscritos)} inscritos importados.")

    def ins_limpiar(self):
        self.inscritos.limpiar()
        print("  ✔ Estructura de inscritos limpiada (0 elementos).")

    # ============================================================ 2. Historial
    def menu_historial(self):
        opciones = {
            "1": ("Agregar semestre (inserción ordenada)", self.his_agregar),
            "2": ("Eliminar semestre", self.his_eliminar),
            "3": ("Buscar semestre (ej. 2024-1)", self.his_buscar),
            "4": ("Recorrer hacia adelante (antiguo -> reciente)", self.his_adelante),
            "5": ("Recorrer hacia atrás (reciente -> antiguo)", self.his_atras),
            "6": ("Exportar a JSON", self.his_exportar),
            "7": ("Importar desde JSON", self.his_importar),
            "8": ("Limpiar estructura", self.his_limpiar),
            "0": ("Volver", None),
        }
        self._bucle("2. HISTORIAL ACADÉMICO (Lista doble)", opciones)

    def his_agregar(self):
        anio = pedir_entero("  año (ej. 2024): ", 1900, 2100)
        term = pedir_entero("  term/periodo (1, 2 o 3): ", 1, 3)
        registro = RegistroSemestre(anio, term)
        print("  Materias (deje el código vacío para terminar):")
        while True:
            cod = pedir_texto("    cod: ", opcional=True)
            if not cod:
                break
            nombre = pedir_texto("    nombre: ")
            nota = pedir_nota(f"    nota ({NOTA_MIN:g}-{NOTA_MAX:g}): ")
            registro.agregar_materia(cod, nombre, nota)
        self.historial.insertar_ordenado(registro)
        print(f"  ✔ Semestre {registro.etiqueta} insertado en su posición ordenada.")

    def his_eliminar(self):
        eliminado = self.historial.eliminar(pedir_texto("  semestre a eliminar (ej. 2024-1): "))
        print(f"  ✔ Eliminado: {eliminado}" if eliminado else "  ! No existe ese semestre.")

    def his_buscar(self):
        reg = self.historial.buscar(pedir_texto("  semestre a buscar (ej. 2024-1): "))
        if not reg:
            print("  ! No existe ese semestre.")
            return
        print(f"  ✔ {reg}")
        for m in reg.materias:
            print(f"      {m['cod']:<8} {m['nombre']:<28} nota: {m['nota']:.2f}")

    def _imprimir_evolucion(self, recorrido, etiqueta_cambio):
        if self.historial.esta_vacia():
            print("  (historial vacío)")
            return
        previo = None
        print(f"  {'Semestre':<10}{'Materias':<10}{'Promedio':<10}{etiqueta_cambio}")
        for reg in recorrido:
            prom = reg.promedio()
            if prom is None:
                texto_prom, cambio = "--", ""
            else:
                texto_prom = f"{prom:.2f}"
                if previo is None:
                    cambio = ""
                elif prom > previo + 1e-9:
                    cambio = f"▲ +{prom - previo:.2f}"
                elif prom < previo - 1e-9:
                    cambio = f"▼ {prom - previo:.2f}"
                else:
                    cambio = "= sin cambio"
                previo = prom
            print(f"  {reg.etiqueta:<10}{len(reg.materias):<10}{texto_prom:<10}{cambio}")

    def his_adelante(self):
        print("  Evolución cronológica (recorrer_adelante):")
        self._imprimir_evolucion(self.historial.recorrer_adelante(), "cambio vs. semestre anterior")

    def his_atras(self):
        print("  Del más reciente al más antiguo (recorrer_atras):")
        self._imprimir_evolucion(self.historial.recorrer_atras(), "cambio vs. semestre más reciente")

    def his_exportar(self):
        ruta = pedir_ruta("  Ruta JSON", RUTA_HISTORIAL)
        n = exportar_json(ruta, self.historial)
        print(f"  ✔ {n} semestres exportados a {mostrar_ruta(ruta)}")

    def his_importar(self):
        ruta = pedir_ruta("  Ruta JSON", RUTA_HISTORIAL)
        self.historial = importar_json(ruta, tipo_esperado="doble")
        print(f"  ✔ {len(self.historial)} semestres importados (ordenados).")

    def his_limpiar(self):
        self.historial.limpiar()
        print("  ✔ Historial limpiado (0 elementos).")

    # ============================================================ 3. Grupos
    def menu_grupos(self):
        opciones = {
            "1": ("Agregar grupo", self.gru_agregar),
            "2": ("Eliminar grupo por nombre", self.gru_eliminar),
            "3": ("Buscar grupo (RECURSIVO)", self.gru_buscar),
            "4": ("Rotar k posiciones", self.gru_rotar),
            "5": ("Recorrer n vueltas", self.gru_recorrer),
            "6": ("Exportar a JSON", self.gru_exportar),
            "7": ("Importar desde JSON", self.gru_importar),
            "8": ("Limpiar estructura", self.gru_limpiar),
            "0": ("Volver", None),
        }
        self._bucle("3. GRUPOS DE PRÁCTICAS (Lista circular)", opciones)

    def gru_agregar(self):
        nombre = pedir_texto("  nombre_grupo: ")
        tutor = pedir_texto("  tutor: ")
        tema = pedir_texto("  tema: ")
        self.grupos.insertar(Grupo(nombre, tutor, tema))
        print("  ✔ Grupo agregado al ciclo.")

    def gru_eliminar(self):
        eliminado = self.grupos.eliminar(pedir_texto("  nombre_grupo a eliminar: "))
        if eliminado:
            en_turno = self.grupos.grupo_en_turno()
            print(f"  ✔ Eliminado: {eliminado.nombre_grupo}. El ciclo se conserva "
                  f"({len(self.grupos)} grupos; turno: {en_turno.nombre_grupo if en_turno else '-'}).")
        else:
            print("  ! No existe ese grupo.")

    def gru_buscar(self):
        nombre = pedir_texto("  nombre_grupo a buscar: ")
        traza = confirmar("  ¿Mostrar la pila de llamadas recursivas?")
        grupo = self.grupos.buscar_recursivo(nombre, verbose=traza)
        print(f"  ✔ Encontrado: {grupo}" if grupo else "  ! No existe ese grupo.")

    def gru_rotar(self):
        if self.grupos.esta_vacia():
            print("  ! No hay grupos para rotar.")
            return
        k = pedir_entero("  k (posiciones a avanzar): ", 0)
        antes = self.grupos.grupo_en_turno().nombre_grupo
        despues = self.grupos.rotar(k).nombre_grupo
        print(f"  ✔ Rotación de {k}: turno {antes} -> {despues}")

    def gru_recorrer(self):
        if self.grupos.esta_vacia():
            print("  (no hay grupos)")
            return
        vueltas = pedir_entero("  n_vueltas (1 = una vuelta): ", 1)
        print(f"  Recorrido desde el turno actual, {vueltas} vuelta(s):")
        for i, g in enumerate(self.grupos.recorrer(vueltas), 1):
            marca = "  <- turno actual" if i == 1 else ""
            print(f"   {i}. {g}{marca}")

    def gru_exportar(self):
        ruta = pedir_ruta("  Ruta JSON", RUTA_GRUPOS)
        n = exportar_json(ruta, self.grupos)
        print(f"  ✔ {n} grupos exportados a {mostrar_ruta(ruta)}")

    def gru_importar(self):
        ruta = pedir_ruta("  Ruta JSON", RUTA_GRUPOS)
        self.grupos = importar_json(ruta, tipo_esperado="circular")
        print(f"  ✔ {len(self.grupos)} grupos importados (ciclo reconstruido).")

    def gru_limpiar(self):
        self.grupos.limpiar()
        print("  ✔ Grupos limpiados (0 elementos).")

    # ============================================================ 4. Reportes
    def menu_reportes(self):
        opciones = {
            "1": ("Top 3 mejores promedios del historial", self.rep_top3),
            "2": ("Siguiente grupo en turno (después de rotar)", self.rep_turno),
            "3": ("Cantidad de inscritos", self.rep_cantidad),
            "0": ("Volver", None),
        }
        self._bucle("4. REPORTES", opciones)

    def rep_top3(self):
        if self.historial.esta_vacia():
            print("  (historial vacío)")
            return
        print("  Top 3 mejores promedios por semestre:")
        hubo = False
        for puesto, (reg, prom) in enumerate(self.historial.top_promedios(3), 1):
            hubo = True
            print(f"   {puesto}. {reg.etiqueta}  ->  {prom:.2f}")
        if not hubo:
            print("   (ningún semestre tiene notas)")
        acum = self.historial.promedio_acumulado()
        if acum is not None:
            print(f"  Promedio acumulado de todo el historial: {acum:.2f}")

    def rep_turno(self):
        grupo = self.grupos.grupo_en_turno()
        if grupo is None:
            print("  (no hay grupos)")
        else:
            print(f"  Grupo en turno: {grupo}")

    def rep_cantidad(self):
        print(f"  Cantidad de inscritos: {len(self.inscritos)}")

    # ============================================================ bucle genérico
    def _bucle(self, nombre, opciones):
        while True:
            eleccion = mostrar_menu(nombre, opciones)
            if eleccion == "0":
                return
            if eleccion in opciones:
                ejecutar_seguro(opciones[eleccion][1])
            else:
                print("  ! Opción no válida.")

    def guardar_todo(self):
        exportar_csv(RUTA_INSCRITOS, self.inscritos)
        exportar_json(RUTA_HISTORIAL, self.historial)
        exportar_json(RUTA_GRUPOS, self.grupos)
        print("  ✔ Datos guardados en la carpeta data/.")

    def ejecutar(self):
        principal = {
            "1": ("Inscritos (lista simple)", self.menu_inscritos),
            "2": ("Historial académico (lista doble)", self.menu_historial),
            "3": ("Grupos de prácticas (lista circular)", self.menu_grupos),
            "4": ("Reportes", self.menu_reportes),
            "5": ("Salir", None),
        }
        while True:
            eleccion = mostrar_menu("REGISTROS ACADÉMICOS - MENÚ PRINCIPAL", principal)
            if eleccion == "5":
                if confirmar("¿Guardar los datos antes de salir?"):
                    ejecutar_seguro(self.guardar_todo)
                print("Hasta pronto.")
                return
            if eleccion in principal:
                principal[eleccion][1]()
            else:
                print("  ! Opción no válida.")


def main():
    try:
        Aplicacion().ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido. Hasta pronto.")


if __name__ == "__main__":
    main()
