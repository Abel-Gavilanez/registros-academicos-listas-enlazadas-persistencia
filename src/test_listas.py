"""Pruebas unitarias:  python -m unittest src/test_listas.py -v  (o desde src/: python -m unittest -v)"""

import os
import tempfile
import unittest

from lista_circular import ListaCircular
from lista_doble import ListaDoble
from lista_simple import ListaSimple
from modelos import Estudiante, Grupo, RegistroSemestre, parse_semestre
from persistencia_csv import exportar_csv, importar_csv
from persistencia_json import exportar_json, importar_json


def est(i):
    return Estudiante(str(i), f"Nombre {i}", f"u{i}@uni.edu")


def sem(a, t, *notas):
    r = RegistroSemestre(a, t)
    for i, n in enumerate(notas):
        r.agregar_materia(f"M{i}", f"Materia {i}", n)
    return r


def grp(n):
    return Grupo(f"G{n}", "Tutor", "Tema")


class TestSimple(unittest.TestCase):
    def test_insertar_eliminar_buscar(self):
        ls = ListaSimple()
        for i in (1, 2, 3):
            ls.insertar_final(est(i))
        self.assertEqual([e.id for e in ls.recorrer()], ["1", "2", "3"])
        self.assertIsNotNone(ls.eliminar("1"))      # cabeza
        self.assertIsNotNone(ls.eliminar("3"))      # cola
        self.assertIs(ls.cabeza, ls.cola)
        ls.insertar_final(est(4))                   # la cola sigue válida
        self.assertEqual([e.id for e in ls.recorrer()], ["2", "4"])
        self.assertIsNone(ls.eliminar("99"))
        self.assertEqual(len(ls), 2)

    def test_duplicado_y_validaciones(self):
        ls = ListaSimple()
        ls.insertar_final(est(1))
        with self.assertRaises(ValueError):
            ls.insertar_final(est(1))
        with self.assertRaises(ValueError):
            Estudiante("", "x", "a@b.co")
        with self.assertRaises(ValueError):
            Estudiante("1", "x", "correo-malo")

    def test_vacia(self):
        ls = ListaSimple()
        self.assertIsNone(ls.eliminar("1"))
        self.assertEqual(list(ls.recorrer()), [])

    def test_to_from_dict(self):
        ls = ListaSimple()
        ls.insertar_final(est(1))
        ls.insertar_final(est(2))
        self.assertEqual([e.id for e in ListaSimple.from_dict(ls.to_dict()).recorrer()], ["1", "2"])


class TestDoble(unittest.TestCase):
    def test_orden_y_enlaces(self):
        ld = ListaDoble()
        for a, t in ((2024, 2), (2023, 1), (2025, 1), (2024, 1), (2023, 2)):
            ld.insertar_ordenado(sem(a, t, 8))
        adel = [r.etiqueta for r in ld.recorrer_adelante()]
        self.assertEqual(adel, ["2023-1", "2023-2", "2024-1", "2024-2", "2025-1"])
        self.assertEqual([r.etiqueta for r in ld.recorrer_atras()], adel[::-1])

    def test_duplicado(self):
        ld = ListaDoble()
        ld.insertar_ordenado(sem(2024, 1, 8))
        ld.insertar_ordenado(sem(2024, 2, 8))
        for dup in ((2024, 1), (2024, 2)):
            with self.assertRaises(ValueError):
                ld.insertar_ordenado(sem(*dup, 5))
        self.assertEqual(len(ld), 2)

    def test_eliminar_extremos_y_medio(self):
        ld = ListaDoble()
        for a in (2020, 2021, 2022, 2023):
            ld.insertar_ordenado(sem(a, 1, 8))
        ld.eliminar("2020-1")
        ld.eliminar("2023-1")
        ld.eliminar("2021-1")
        self.assertEqual([r.etiqueta for r in ld.recorrer_adelante()], ["2022-1"])
        self.assertIs(ld.cabeza, ld.cola)
        self.assertIsNone(ld.cabeza.anterior)
        self.assertIsNone(ld.eliminar("1999-1"))

    def test_buscar_formatos(self):
        ld = ListaDoble()
        ld.insertar_ordenado(sem(2024, 1, 8))
        self.assertIsNotNone(ld.buscar("2024-1"))
        self.assertIsNotNone(ld.buscar("2024/1"))
        self.assertIsNotNone(ld.buscar((2024, 1)))
        self.assertIsNone(ld.buscar("2024-2"))
        with self.assertRaises(ValueError):
            ld.buscar("abc")

    def test_top_promedios(self):
        ld = ListaDoble()
        for (a, t), notas in {(2023, 1): (6, 7), (2023, 2): (9, 9), (2024, 1): (8, 8),
                              (2024, 2): (10, 8), (2025, 1): (5,)}.items():
            ld.insertar_ordenado(sem(a, t, *notas))
        ld.insertar_ordenado(RegistroSemestre(2026, 1))            # sin notas: se ignora
        top = [(r.etiqueta, p) for r, p in ld.top_promedios(3)]
        self.assertEqual(top, [("2023-2", 9.0), ("2024-2", 9.0), ("2024-1", 8.0)])
        self.assertEqual(len(list(ld.top_promedios(10))), 5)

    def test_notas_invalidas(self):
        with self.assertRaises(ValueError):
            sem(2024, 1, 11)
        with self.assertRaises(ValueError):
            RegistroSemestre(2024, 5)
        self.assertEqual(parse_semestre("2024-1"), (2024, 1))


class TestCircular(unittest.TestCase):
    def armar(self, n=3):
        lc = ListaCircular()
        for i in range(1, n + 1):
            lc.insertar(grp(i))
        return lc

    def test_ciclo_y_recorrido(self):
        lc = self.armar()
        self.assertIs(lc.cola.siguiente, lc.cabeza)
        self.assertEqual([g.nombre_grupo for g in lc.recorrer(2)], ["G1", "G2", "G3", "G1", "G2", "G3"])

    def test_un_solo_nodo(self):
        lc = self.armar(1)
        self.assertIs(lc.cabeza.siguiente, lc.cabeza)
        self.assertEqual(lc.rotar(5).nombre_grupo, "G1")
        self.assertIsNotNone(lc.buscar_recursivo("G1"))
        self.assertIsNone(lc.buscar_recursivo("G2"))
        lc.eliminar("G1")
        self.assertTrue(lc.esta_vacia())

    def test_busqueda_recursiva(self):
        lc = self.armar(5)
        for i in range(1, 6):
            self.assertEqual(lc.buscar_recursivo(f"G{i}").nombre_grupo, f"G{i}")
        self.assertEqual(lc.buscar_recursivo("  g3 ").nombre_grupo, "G3")   # sin distinguir mayúsculas
        self.assertIsNone(lc.buscar_recursivo("G9"))
        self.assertIsNone(ListaCircular().buscar_recursivo("G1"))

    def test_rotar(self):
        lc = self.armar()
        self.assertEqual(lc.rotar(1).nombre_grupo, "G2")
        self.assertEqual(lc.rotar(0).nombre_grupo, "G2")
        self.assertEqual(lc.rotar(7).nombre_grupo, "G3")      # 7 % 3 = 1
        with self.assertRaises(ValueError):
            lc.rotar(-1)
        self.assertIsNone(ListaCircular().rotar(2))

    def test_eliminar_conserva_ciclo(self):
        lc = self.armar(4)
        lc.rotar(1)                                            # turno: G2
        lc.eliminar("G4")                                      # cola
        self.assertIs(lc.cola.siguiente, lc.cabeza)
        lc.eliminar("G1")                                      # cabeza
        self.assertIs(lc.cola.siguiente, lc.cabeza)
        self.assertEqual(lc.cabeza.valor.nombre_grupo, "G2")
        lc.eliminar("G2")                                      # grupo en turno
        self.assertEqual(lc.grupo_en_turno().nombre_grupo, "G3")
        self.assertEqual([g.nombre_grupo for g in lc.recorrer(2)], ["G3", "G3"])
        self.assertIsNone(lc.eliminar("G99"))

    def test_recorrer_infinito(self):
        lc = self.armar(2)
        gen = lc.recorrer(None)
        self.assertEqual([next(gen).nombre_grupo for _ in range(5)], ["G1", "G2", "G1", "G2", "G1"])

    def test_duplicado(self):
        lc = self.armar(2)
        with self.assertRaises(ValueError):
            lc.insertar(Grupo("g1", "T", "X"))


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def ruta(self, nombre):
        return os.path.join(self.dir, nombre)

    def test_csv_roundtrip_y_errores(self):
        ls = ListaSimple()
        ls.insertar_final(Estudiante("1", 'Ana "La Crack", Ruiz', "ana@uni.edu"))   # comas y comillas
        ls.insertar_final(est(2))
        exportar_csv(self.ruta("a.csv"), ls)
        lista = importar_csv(self.ruta("a.csv"))
        self.assertEqual(lista.buscar("1").nombres, 'Ana "La Crack", Ruiz')
        self.assertEqual(len(lista), 2)
        with open(self.ruta("mal.csv"), "w", encoding="utf-8") as f:
            f.write("id,nombres,correo\n1,Ok,ok@uni.edu\n1,Repetido,r@uni.edu\n2,Sin correo valido,xx\n3,Bien,b@uni.edu\n")
        avisos = []
        lista = importar_csv(self.ruta("mal.csv"), reportar=avisos.append)
        self.assertEqual(len(lista), 2)
        self.assertEqual(len(avisos), 2)
        with open(self.ruta("enc.csv"), "w", encoding="utf-8") as f:
            f.write("a,b,c\n")
        with self.assertRaises(ValueError):
            importar_csv(self.ruta("enc.csv"))
        with self.assertRaises(ValueError):
            importar_csv(self.ruta("noexiste.csv"))

    def test_json_doble(self):
        ld = ListaDoble()
        ld.insertar_ordenado(sem(2024, 2, 9, 8))
        ld.insertar_ordenado(sem(2024, 1, 7))
        exportar_json(self.ruta("h.json"), ld)
        nueva = importar_json(self.ruta("h.json"), tipo_esperado="doble")
        self.assertEqual([r.etiqueta for r in nueva.recorrer_adelante()], ["2024-1", "2024-2"])
        self.assertEqual(nueva.buscar("2024-2").promedio(), 8.5)
        with self.assertRaises(ValueError):
            importar_json(self.ruta("h.json"), tipo_esperado="circular")

    def test_json_circular_conserva_turno(self):
        lc = ListaCircular()
        for i in (1, 2, 3):
            lc.insertar(grp(i))
        lc.rotar(2)
        exportar_json(self.ruta("g.json"), lc)
        nueva = importar_json(self.ruta("g.json"))
        self.assertEqual(nueva.grupo_en_turno().nombre_grupo, "G3")
        self.assertIs(nueva.cola.siguiente, nueva.cabeza)

    def test_json_malformado(self):
        with open(self.ruta("x.json"), "w", encoding="utf-8") as f:
            f.write("{no es json")
        with self.assertRaises(ValueError):
            importar_json(self.ruta("x.json"))


if __name__ == "__main__":
    unittest.main()
