"""Verificación de fidelidad: compara, palabra por palabra, el texto de referencia
(extraído del original por un camino independiente de Docling) con el Markdown
generado.

La comparación es por multiconjunto de palabras (no depende del orden, porque el
orden de lectura en PDFs con columnas o tablas no es único). El orden se informa
aparte como dato orientativo.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

# Palabra = secuencia de letras o dígitos (sin guion bajo).
_PALABRA = re.compile(r"[^\W_]+", re.UNICODE)

_COMENTARIO_HTML = re.compile(r"<!--.*?-->", re.DOTALL)
_IMAGEN_MD = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_ENLACE_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_ETIQUETA_HTML = re.compile(r"</?[a-zA-Z][^>]*>")
_ENTIDAD_HTML = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&nbsp;": " "}

# Caracteres invisibles o de maquetación que no forman parte del contenido.
_INVISIBLES = dict.fromkeys(map(ord, "­​‌‍⁠﻿"), None)


def normalizar(texto: str) -> str:
    """Normaliza representaciones distintas del mismo carácter (ligaduras "ﬁ",
    anchos, guiones blandos). No cambia mayúsculas ni elimina contenido."""
    return unicodedata.normalize("NFKC", texto).translate(_INVISIBLES)


def texto_de_markdown(md: str) -> str:
    """Quita la sintaxis Markdown/HTML que no es contenido del documento
    (comentarios, rutas de imágenes, URLs de enlaces, etiquetas)."""
    md = _COMENTARIO_HTML.sub(" ", md)
    md = _IMAGEN_MD.sub(" ", md)
    md = _ENLACE_MD.sub(r"\1", md)
    md = _ETIQUETA_HTML.sub(" ", md)
    for entidad, caracter in _ENTIDAD_HTML.items():
        md = md.replace(entidad, caracter)
    return md


def palabras(texto: str) -> list[str]:
    return _PALABRA.findall(normalizar(texto))


@dataclass
class Resultado:
    """Resultado de comparar una unidad (una página o un capítulo)."""

    etiqueta: str
    total_referencia: int
    faltantes: Counter = field(default_factory=Counter)
    sobrantes: Counter = field(default_factory=Counter)
    excluidas: Counter = field(default_factory=Counter)
    unidas_por_guion: list[tuple[str, str]] = field(default_factory=list)
    similitud_orden: float = 1.0
    sin_referencia: bool = False
    ocr: bool = False
    notas: list[str] = field(default_factory=list)

    @property
    def cobertura(self) -> float:
        if self.total_referencia == 0:
            return 1.0
        return 1 - sum(self.faltantes.values()) / self.total_referencia

    def aprobado(self, umbral: float) -> bool:
        if self.sin_referencia or self.ocr:
            return False
        return self.cobertura >= umbral and not self.sobrantes


def comparar(
    etiqueta: str,
    referencia: str,
    markdown: str,
    excluido: str = "",
    opcional: str = "",
) -> Resultado:
    """Compara el texto de referencia con el Markdown.

    `excluido` es texto que la conversión dejó fuera a propósito (encabezados y
    pies de página detectados); sus palabras no cuentan como faltantes, pero se
    registran en el informe. `opcional` es texto del original que puede o no
    aparecer (el texto alternativo de imágenes); no cuenta como sobrante.
    """
    ref = palabras(referencia)
    md = palabras(texto_de_markdown(markdown))
    res = Resultado(etiqueta=etiqueta, total_referencia=len(ref))

    faltantes = Counter(ref) - Counter(md)
    sobrantes = Counter(md) - Counter(ref)

    # Palabras cortadas con guion al final de línea en el original ("infor-" +
    # "mación") que la conversión unió correctamente ("información").
    for a, b in zip(ref, ref[1:]):
        unida = a + b
        if faltantes[a] and faltantes[b] and sobrantes[unida] and (a != b or faltantes[a] >= 2):
            faltantes[a] -= 1
            faltantes[b] -= 1
            sobrantes[unida] -= 1
            res.unidas_por_guion.append((a, b))
    faltantes = +faltantes
    sobrantes = +sobrantes

    if opcional:
        sobrantes -= Counter(palabras(opcional))

    if excluido:
        excluidas = Counter(palabras(excluido)) & faltantes
        faltantes -= excluidas
        res.excluidas = excluidas

    res.faltantes = faltantes
    res.sobrantes = sobrantes
    if ref and md:
        res.similitud_orden = difflib.SequenceMatcher(None, ref, md, autojunk=False).ratio()
    elif ref or md:
        res.similitud_orden = 0.0
    return res
