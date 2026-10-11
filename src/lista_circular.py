"""Módulo 3 - Lista circular simple: rotación de grupos de prácticas.

El ``siguiente`` del último nodo (``cola``) apunta a la ``cabeza``; nunca hay None
en la cadena.  El puntero ``actual`` marca el grupo al que le toca el turno.

Complejidades (n = número de grupos, k = pasos de rotación):
    insertar           : O(n) (verifica duplicados; el enlace es O(1) con ``cola``)
    eliminar           : O(n)
    buscar_recursivo   : O(n) tiempo y O(n) espacio de pila (una llamada por nodo)
    rotar(k)           : O(k)  (O(min(k, n)) porque se reduce k módulo n)
                         O(1) si solo se avanza una posición manteniendo ``actual``
    recorrer(v)        : O(v * n)
"""

import sys

from modelos import Grupo, normalizar
from nodo_circular import NodoCircular


def _nombre(valor):
    """Acepta un Grupo o directamente el nombre del grupo."""
    return normalizar(valor.nombre_grupo if isinstance(valor, Grupo) else valor)


class ListaCircular:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.actual = None      # grupo al que le corresponde el turno
        self._tam = 0

    def __len__(self):
        return self._tam

    def esta_vacia(self):
        return self.cabeza is None

    def limpiar(self):
        # Se rompe el ciclo para no dejar nodos referenciándose entre sí.
        if self.cola is not None:
            self.cola.siguiente = None
        self.cabeza = self.cola = self.actual = None
        self._tam = 0

    # ----------------------------------------------------------- operaciones
    def _existe(self, nombre_normalizado):
        """Búsqueda iterativa (solo para validar duplicados sin consumir pila)."""
        nodo = self.cabeza
        for _ in range(self._tam):
            if normalizar(nodo.valor.nombre_grupo) == nombre_normalizado:
                return True
            nodo = nodo.siguiente
        return False

    def insertar(self, grupo):
        """Inserta un Grupo al final del ciclo. ValueError si el nombre ya existe."""
        if self._existe(_nombre(grupo)):
            raise ValueError(f"Ya existe el grupo '{grupo.nombre_grupo}'.")
        nuevo = NodoCircular(grupo)
        if self.cabeza is None:
            nuevo.siguiente = nuevo                 # un solo nodo: se apunta a sí mismo
            self.cabeza = self.cola = self.actual = nuevo
        else:
            nuevo.siguiente = self.cabeza           # cierra el ciclo
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._tam += 1

    def eliminar(self, nombre_grupo):
        """Elimina por nombre conservando el ciclo. Devuelve el Grupo o None."""
        if self.cabeza is None:
            return None
        objetivo = _nombre(nombre_grupo)
        previo, nodo = self.cola, self.cabeza
        for _ in range(self._tam):                  # a lo sumo una vuelta completa
            if normalizar(nodo.valor.nombre_grupo) == objetivo:
                break
            previo, nodo = nodo, nodo.siguiente
        else:
            return None

        grupo = nodo.valor
        if self._tam == 1:                          # era el único: lista vacía
            self.cabeza = self.cola = self.actual = None
        else:
            previo.siguiente = nodo.siguiente       # se salta el nodo; el ciclo se mantiene
            if nodo is self.cabeza:
                self.cabeza = nodo.siguiente
            if nodo is self.cola:
                self.cola = previo
            if nodo is self.actual:                 # el turno pasa al siguiente grupo
                self.actual = nodo.siguiente
        nodo.siguiente = None
        self._tam -= 1
        return grupo

    # ------------------------------------------------- búsqueda RECURSIVA (obligatoria)
    def buscar_recursivo(self, valor, verbose=False):
        """Busca un grupo por nombre (o por Grupo) de forma RECURSIVA.

        Devuelve el Grupo encontrado o None.  Con ``verbose=True`` imprime la
        pila de llamadas (útil para el diagrama del informe y para el video).
        """
        if self.cabeza is None:
            return None
        if self._tam > sys.getrecursionlimit() - 100:
            raise RecursionError(
                "La lista es demasiado grande para la búsqueda recursiva "
                f"(límite de Python: {sys.getrecursionlimit()} llamadas)."
            )
        return self._buscar_rec(self.cabeza, _nombre(valor), 0, verbose)

    def _buscar_rec(self, nodo, objetivo, nivel, verbose):
        if verbose:
            print(f"{'   ' * nivel}buscar_rec(nodo='{nodo.valor.nombre_grupo}')  [llamada {nivel + 1}]")
        # Caso base 1: encontrado
        if normalizar(nodo.valor.nombre_grupo) == objetivo:
            if verbose:
                print(f"{'   ' * nivel}-> ENCONTRADO: {nodo.valor.nombre_grupo}")
            return nodo.valor
        # Caso base 2: se dio la vuelta completa (el siguiente es la cabeza) -> no existe
        if nodo.siguiente is self.cabeza:
            if verbose:
                print(f"{'   ' * nivel}-> el siguiente es la cabeza: vuelta completa, NO existe")
            return None
        # Caso recursivo: avanzar un nodo
        return self._buscar_rec(nodo.siguiente, objetivo, nivel + 1, verbose)

    # -------------------------------------------------------------- rotación
    def rotar(self, k):
        """Avanza el puntero ``actual`` k posiciones. Devuelve el grupo en turno."""
        if not isinstance(k, int) or isinstance(k, bool) or k < 0:
            raise ValueError("k debe ser un entero >= 0 (la lista circular simple solo avanza).")
        if self.actual is None:
            return None
        for _ in range(k % self._tam):              # k % n evita vueltas completas inútiles
            self.actual = self.actual.siguiente
        return self.actual.valor

    def grupo_en_turno(self):
        """Grupo al que le toca el turno ahora (O(1)). None si no hay grupos."""
        return self.actual.valor if self.actual else None

    def recorrer(self, n_vueltas=1):
        """Generador que da ``n_vueltas`` vueltas completas empezando en el turno actual.

        Con ``n_vueltas=None`` el recorrido es infinito (para playlists / rondas).
        No modifica el puntero ``actual``.
        """
        if self.actual is None:
            return
        nodo = self.actual
        if n_vueltas is None:
            while True:
                yield nodo.valor
                nodo = nodo.siguiente
        if not isinstance(n_vueltas, int) or n_vueltas < 0:
            raise ValueError("n_vueltas debe ser un entero >= 0 o None.")
        for _ in range(n_vueltas * self._tam):
            yield nodo.valor
            nodo = nodo.siguiente

    # ----------------------------------------------------------- persistencia
    def to_dict(self):
        """Los grupos se guardan desde la cabeza; ``actual`` guarda de quién es el turno."""
        grupos = []
        nodo = self.cabeza
        for _ in range(self._tam):
            grupos.append(nodo.valor.to_dict())
            nodo = nodo.siguiente
        return {
            "tipo": "circular",
            "actual": self.actual.valor.nombre_grupo if self.actual else None,
            "grupos": grupos,
        }

    @classmethod
    def from_dict(cls, datos):
        if datos.get("tipo") != "circular":
            raise ValueError("El archivo no contiene una lista circular.")
        lista = cls()
        for d in datos.get("grupos", []):
            lista.insertar(Grupo.from_dict(d))
        nombre_actual = datos.get("actual")
        if nombre_actual is not None and lista.cabeza is not None:
            objetivo = normalizar(nombre_actual)
            nodo = lista.cabeza
            for _ in range(len(lista)):
                if normalizar(nodo.valor.nombre_grupo) == objetivo:
                    lista.actual = nodo
                    break
                nodo = nodo.siguiente
        return lista
