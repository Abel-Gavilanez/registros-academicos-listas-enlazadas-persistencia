"""Entidades académicas que se guardan como ``valor`` dentro de los nodos.

* Estudiante        -> ListaSimple   (Módulo 1: inscritos)
* RegistroSemestre  -> ListaDoble    (Módulo 2: historial académico)
* Grupo             -> ListaCircular (Módulo 3: rotación de prácticas)

Cada clase valida sus datos y sabe convertirse a/desde ``dict``
(esto es lo único para lo que se usa ``dict`` en el proyecto: serializar).
"""

import re

NOTA_MIN = 0.0
NOTA_MAX = 10.0          # escala de calificación; cámbiela aquí si usa otra (p. ej. 5.0)
TERMS_VALIDOS = (1, 2, 3)  # 1 = primer periodo, 2 = segundo, 3 = verano/intensivo

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _texto_obligatorio(valor, campo):
    texto = str(valor).strip() if valor is not None else ""
    if not texto:
        raise ValueError(f"El campo '{campo}' no puede estar vacío.")
    return texto


# --------------------------------------------------------------------------
# Módulo 1
# --------------------------------------------------------------------------
class Estudiante:
    """Estudiante inscrito en una asignatura: id, nombres, correo."""

    __slots__ = ("id", "nombres", "correo")

    def __init__(self, id, nombres, correo):
        self.id = _texto_obligatorio(id, "id")
        self.nombres = _texto_obligatorio(nombres, "nombres")
        self.correo = _texto_obligatorio(correo, "correo")
        if not _EMAIL.match(self.correo):
            raise ValueError(f"Correo no válido: '{self.correo}'.")

    def to_dict(self):
        return {"id": self.id, "nombres": self.nombres, "correo": self.correo}

    @classmethod
    def from_dict(cls, d):
        try:
            return cls(d["id"], d["nombres"], d["correo"])
        except KeyError as e:
            raise ValueError(f"Falta el campo {e} en el estudiante.") from None

    def __str__(self):
        return f"[{self.id}] {self.nombres} <{self.correo}>"

    __repr__ = __str__


# --------------------------------------------------------------------------
# Módulo 2
# --------------------------------------------------------------------------
def parse_semestre(texto):
    """Convierte '2024-1' (también '2024/1' o '2024 1') en la clave (2024, 1)."""
    partes = re.split(r"[-/\s]+", str(texto).strip())
    if len(partes) != 2:
        raise ValueError(f"Semestre no válido: '{texto}'. Use el formato AAAA-T (ej. 2024-1).")
    try:
        anio, term = int(partes[0]), int(partes[1])
    except ValueError:
        raise ValueError(f"Semestre no válido: '{texto}'. Use el formato AAAA-T (ej. 2024-1).") from None
    return _validar_clave(anio, term)


def _validar_clave(anio, term):
    if not isinstance(anio, int) or isinstance(anio, bool) or not 1900 <= anio <= 2100:
        raise ValueError("El año debe ser un entero entre 1900 y 2100.")
    if term not in TERMS_VALIDOS:
        raise ValueError(f"El periodo (term) debe ser uno de {TERMS_VALIDOS}.")
    return (anio, term)


class RegistroSemestre:
    """Un semestre del historial: anio, term y materias [{cod, nombre, nota}]."""

    __slots__ = ("anio", "term", "materias")

    def __init__(self, anio, term, materias=None):
        self.anio, self.term = _validar_clave(anio, term)
        self.materias = []   # datos del registro (no son nodos de ninguna lista)
        for m in materias or ():
            self.agregar_materia(m["cod"], m["nombre"], m["nota"])

    # clave de ordenamiento de la lista doble: (anio, term)
    @property
    def clave(self):
        return (self.anio, self.term)

    @property
    def etiqueta(self):
        return f"{self.anio}-{self.term}"

    def agregar_materia(self, cod, nombre, nota):
        cod = _texto_obligatorio(cod, "cod")
        nombre = _texto_obligatorio(nombre, "nombre")
        try:
            nota = float(nota)
        except (TypeError, ValueError):
            raise ValueError(f"La nota de '{cod}' debe ser numérica.") from None
        if not NOTA_MIN <= nota <= NOTA_MAX:
            raise ValueError(f"La nota debe estar entre {NOTA_MIN:g} y {NOTA_MAX:g}.")
        self.materias.append({"cod": cod, "nombre": nombre, "nota": nota})

    def promedio(self):
        """Promedio simple de las notas del semestre (None si no hay materias)."""
        if not self.materias:
            return None
        return sum(m["nota"] for m in self.materias) / len(self.materias)

    def to_dict(self):
        return {
            "anio": self.anio,
            "term": self.term,
            "materias": [dict(m) for m in self.materias],
        }

    @classmethod
    def from_dict(cls, d):
        try:
            return cls(d["anio"], d["term"], d.get("materias", []))
        except KeyError as e:
            raise ValueError(f"Falta el campo {e} en el semestre.") from None

    def __str__(self):
        p = self.promedio()
        prom = "sin notas" if p is None else f"promedio {p:.2f}"
        return f"{self.etiqueta} ({len(self.materias)} materias, {prom})"

    __repr__ = __str__


# --------------------------------------------------------------------------
# Módulo 3
# --------------------------------------------------------------------------
class Grupo:
    """Grupo/paralelo de prácticas: nombre_grupo, tutor, tema."""

    __slots__ = ("nombre_grupo", "tutor", "tema")

    def __init__(self, nombre_grupo, tutor, tema):
        self.nombre_grupo = _texto_obligatorio(nombre_grupo, "nombre_grupo")
        self.tutor = _texto_obligatorio(tutor, "tutor")
        self.tema = _texto_obligatorio(tema, "tema")

    def to_dict(self):
        return {"nombre_grupo": self.nombre_grupo, "tutor": self.tutor, "tema": self.tema}

    @classmethod
    def from_dict(cls, d):
        try:
            return cls(d["nombre_grupo"], d["tutor"], d["tema"])
        except KeyError as e:
            raise ValueError(f"Falta el campo {e} en el grupo.") from None

    def __str__(self):
        return f"{self.nombre_grupo} (tutor: {self.tutor}, tema: {self.tema})"

    __repr__ = __str__


def normalizar(texto):
    """Normaliza un nombre para compararlo sin distinguir mayúsculas ni espacios extra."""
    return " ".join(str(texto).split()).casefold()
