"""Nodo de lista circular: { valor, siguiente }.

La diferencia con NodoSimple no está en el nodo sino en la lista: el
``siguiente`` del último nodo apunta de vuelta al primero (nunca es None).
"""


class NodoCircular:
    """Nodo de una lista circular simple."""

    __slots__ = ("valor", "siguiente")

    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente

    def __repr__(self):
        return f"NodoCircular({self.valor!r})"
