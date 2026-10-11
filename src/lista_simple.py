"""Módulo 1 - Lista simplemente enlazada de estudiantes inscritos.

Los nodos se encadenan solo con referencias (``siguiente``); no se usa
``list`` para almacenarlos.  ``dict``/``list`` aparecen únicamente en
``to_dict``/``from_dict`` para empaquetar los datos en la persistencia.

Complejidades (n = número de inscritos):
    insertar_final : O(n)  (verifica id duplicado; el enlace en sí es O(1) gracias a ``cola``)
    eliminar       : O(n)
    buscar         : O(n)
    recorrer       : O(n)
"""

from modelos import Estudiante
from nodo_simple import NodoSimple


class ListaSimple:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tam = 0

    # ---------------------------------------------------------------- estado
    def __len__(self):
        return self._tam

    def esta_vacia(self):
        return self.cabeza is None

    def limpiar(self):
        """Vacía la estructura (los nodos quedan sin referencias)."""
        self.cabeza = self.cola = None
        self._tam = 0

    # ----------------------------------------------------------- operaciones
    def insertar_final(self, estudiante):
        """Agrega un estudiante al final. Lanza ValueError si el id ya existe."""
        if self.buscar(estudiante.id) is not None:           # O(n)
            raise ValueError(f"Ya existe un estudiante con id '{estudiante.id}'.")
        nodo = NodoSimple(estudiante)
        if self.cabeza is None:
            self.cabeza = self.cola = nodo
        else:
            self.cola.siguiente = nodo                       # O(1) gracias a 'cola'
            self.cola = nodo
        self._tam += 1

    def eliminar(self, id_estudiante):
        """Elimina por id y devuelve el Estudiante eliminado (None si no existe)."""
        id_estudiante = str(id_estudiante).strip()
        anterior, actual = None, self.cabeza
        while actual is not None and actual.valor.id != id_estudiante:
            anterior, actual = actual, actual.siguiente
        if actual is None:
            return None
        if anterior is None:                 # se elimina la cabeza
            self.cabeza = actual.siguiente
        else:
            anterior.siguiente = actual.siguiente
        if actual is self.cola:              # se elimina la cola
            self.cola = anterior
        actual.siguiente = None
        self._tam -= 1
        return actual.valor

    def buscar(self, id_estudiante):
        """Devuelve el Estudiante con ese id o None."""
        id_estudiante = str(id_estudiante).strip()
        actual = self.cabeza
        while actual is not None:
            if actual.valor.id == id_estudiante:
                return actual.valor
            actual = actual.siguiente
        return None

    def recorrer(self):
        """Generador: produce cada Estudiante de cabeza a cola."""
        actual = self.cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    # ----------------------------------------------------------- persistencia
    def to_dict(self):
        return {"tipo": "simple", "estudiantes": [e.to_dict() for e in self.recorrer()]}

    @classmethod
    def from_dict(cls, datos):
        if datos.get("tipo") != "simple":
            raise ValueError("El archivo no contiene una lista simple.")
        lista = cls()
        for d in datos.get("estudiantes", []):
            lista.insertar_final(Estudiante.from_dict(d))
        return lista
