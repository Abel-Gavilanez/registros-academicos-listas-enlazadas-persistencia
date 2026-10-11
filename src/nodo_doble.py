"""Nodo de lista doblemente enlazada: { valor, anterior, siguiente }."""


class NodoDoble:
    """Nodo con referencias hacia atrás (anterior) y hacia adelante (siguiente)."""

    __slots__ = ("valor", "anterior", "siguiente")

    def __init__(self, valor, anterior=None, siguiente=None):
        self.valor = valor
        self.anterior = anterior
        self.siguiente = siguiente

    def __repr__(self):
        return f"NodoDoble({self.valor!r})"
