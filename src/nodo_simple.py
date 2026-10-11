"""Nodo de lista simplemente enlazada: { valor, siguiente }."""


class NodoSimple:
    """Nodo con una sola referencia (hacia adelante)."""

    __slots__ = ("valor", "siguiente")

    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente

    def __repr__(self):
        return f"NodoSimple({self.valor!r})"
