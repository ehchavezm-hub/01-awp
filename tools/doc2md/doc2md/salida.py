"""Exportación a Markdown con las imágenes guardadas como archivos locales."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def markdown_de_documento(
    doc,
    salida_md: Path,
    dir_imagenes: Path,
    page_no: int | None = None,
    capas=None,
) -> str:
    """Markdown de un DoclingDocument (o de una sola página, con `page_no`).

    Las imágenes se guardan en `dir_imagenes` (hermano de `salida_md`) y se
    referencian con rutas relativas, para que el Markdown sea portable.
    """
    from docling_core.types.doc import ImageRefMode

    salida_md.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".md", dir=salida_md.parent)
    os.close(fd)
    try:
        doc.save_as_markdown(
            Path(tmp),
            # Relativo: Docling lo resuelve junto al .md y escribe rutas relativas.
            artifacts_dir=Path(dir_imagenes.name),
            image_mode=ImageRefMode.REFERENCED,
            page_no=page_no,
            included_content_layers=capas,
            # Incluye el texto que Docling ubica dentro de figuras (p. ej. texto
            # de diagramas o de páginas escaneadas).
            traverse_pictures=True,
        )
        return Path(tmp).read_text(encoding="utf-8")
    finally:
        Path(tmp).unlink(missing_ok=True)
