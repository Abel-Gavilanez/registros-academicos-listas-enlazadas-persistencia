"""Módulo 2 - Lista doblemente enlazada: historial académico por semestre.

Cada nodo guarda un RegistroSemestre.  La lista se mantiene SIEMPRE ordenada
por (anio, term); por eso se puede recorrer hacia adelante (cronológico) y
hacia atrás (del más reciente al más antiguo) con el mismo costo.

Complejidades (n = número de semestres):
    insertar_ordenado : O(n) en promedio (O(1) si el semestre es el más reciente)
    eliminar / buscar : O(n)
    recorrer_*        : O(n)
    top_promedios     : O(n * k) con k constante (=3)  ->  O(n)
"""

from modelos import RegistroSemestre, parse_semestre
from nodo_doble import NodoDoble
from nodo_simple import NodoSimple


def _a_clave(semestre):
    """Acepta '2024-1', (2024, 1) o un RegistroSemestre y devuelve (2024, 1)."""
    if isinstance(semestre, RegistroSemestre):
        return semestre.clave
    if isinstance(semestre, tuple):
        return parse_semestre(f"{semestre[0]}-{semestre[1]}")
    return parse_semestre(semestre)


class ListaDoble:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tam = 0

    def __len__(self):
        return self._tam

    def esta_vacia(self):
        return self.cabeza is None

    def limpiar(self):
        self.cabeza = self.cola = None
        self._tam = 0

    # ----------------------------------------------------------- operaciones
    def insertar_ordenado(self, registro_semestre):
        """Inserta manteniendo el orden por (anio, term). ValueError si ya existe."""
        clave = registro_semestre.clave
        nuevo = NodoDoble(registro_semestre)

        if self.cabeza is None:                                   # lista vacía
            self.cabeza = self.cola = nuevo
        elif clave < self.cabeza.valor.clave:                     # nuevo primero
            nuevo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo
            self.cabeza = nuevo
        elif clave > self.cola.valor.clave:                       # nuevo último (caso común)
            nuevo.anterior = self.cola
            self.cola.siguiente = nuevo
            self.cola = nuevo
        else:                                                     # en medio: buscar posición
            actual = self.cabeza
            while actual.valor.clave < clave:                     # termina: clave <= cola
                actual = actual.siguiente
            if actual.valor.clave == clave:
                raise ValueError(f"El semestre {registro_semestre.etiqueta} ya existe en el historial.")
            nuevo.anterior = actual.anterior
            nuevo.siguiente = actual
            actual.anterior.siguiente = nuevo
            actual.anterior = nuevo
        self._tam += 1

    def _nodo(self, semestre):
        clave = _a_clave(semestre)
        actual = self.cabeza
        while actual is not None and actual.valor.clave < clave:  # se detiene antes: está ordenada
            actual = actual.siguiente
        if actual is not None and actual.valor.clave == clave:
            return actual
        return None

    def buscar(self, semestre):
        """Devuelve el RegistroSemestre (ej. '2024-1') o None."""
        nodo = self._nodo(semestre)
        return nodo.valor if nodo else None

    def eliminar(self, semestre):
        """Elimina el semestre y devuelve el registro eliminado (None si no existe)."""
        nodo = self._nodo(semestre)
        if nodo is None:
            return None
        if nodo.anterior is None:
            self.cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self.cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        nodo.anterior = nodo.siguiente = None
        self._tam -= 1
        return nodo.valor

    def recorrer_adelante(self):
        """Generador: del semestre más antiguo al más reciente."""
        actual = self.cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def recorrer_atras(self):
        """Generador: del semestre más reciente al más antiguo."""
        actual = self.cola
        while actual is not None:
            yield actual.valor
            actual = actual.anterior

    # --------------------------------------------------------------- reportes
    def top_promedios(self, n=3):
        """Genera hasta ``n`` tuplas (registro, promedio) con los mejores promedios.

        El ranking se arma con una cadena de NodoSimple ordenada de mayor a
        menor y recortada a ``n`` nodos (no se usa ``list``).  En empates se
        conserva primero el semestre más antiguo.
        """
        if n < 1:
            raise ValueError("n debe ser >= 1.")
        cab, tam = None, 0
        for reg in self.recorrer_adelante():
            prom = reg.promedio()
            if prom is None:
                continue
            previo, cur = None, cab
            while cur is not None and cur.valor[1] >= prom:
                previo, cur = cur, cur.siguiente
            nodo = NodoSimple((reg, prom), cur)
            if previo is None:
                cab = nodo
            else:
                previo.siguiente = nodo
            tam += 1
            if tam > n:                       # descartar el peor (último de la cadena)
                p = cab
                for _ in range(n - 1):
                    p = p.siguiente
                p.siguiente = None
                tam = n
        cur = cab
        while cur is not None:
            yield cur.valor
            cur = cur.siguiente

    def promedio_acumulado(self):
        """Promedio de TODAS las notas del historial (None si no hay notas)."""
        suma, cant = 0.0, 0
        for reg in self.recorrer_adelante():
            for m in reg.materias:
                suma += m["nota"]
                cant += 1
        return suma / cant if cant else None

    # ----------------------------------------------------------- persistencia
    def to_dict(self):
        return {"tipo": "doble", "semestres": [r.to_dict() for r in self.recorrer_adelante()]}

    @classmethod
    def from_dict(cls, datos):
        if datos.get("tipo") != "doble":
            raise ValueError("El archivo no contiene una lista doble.")
        lista = cls()
        for d in datos.get("semestres", []):
            lista.insertar_ordenado(RegistroSemestre.from_dict(d))  # reordena si hiciera falta
        return lista
