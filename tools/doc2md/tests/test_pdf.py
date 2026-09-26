"""Prueba del recorrido por páginas del PDF con un documento Docling construido
a mano (no necesita los modelos de Docling ni un PDF real)."""

from pathlib import Path

import pytest

pytest.importorskip("docling")

from docling_core.types.doc import (  # noqa: E402
    BoundingBox,
    ContentLayer,
    DocItemLabel,
    DoclingDocument,
    ProvenanceItem,
    Size,
)

from doc2md import pdf  # noqa: E402


def _prov(pagina, texto):
    return ProvenanceItem(page_no=pagina, bbox=BoundingBox(l=0, t=0, r=10, b=10), charspan=(0, len(texto)))


def _documento():
    doc = DoclingDocument(name="prueba")
    for n in (1, 2, 3):
        doc.add_page(page_no=n, size=Size(width=595, height=842))
    textos = {
        1: "La planificación de frentes de trabajo organiza la construcción.",
        2: "Texto de la segunda página con acentos: acción, niño.",
        3: "Texto reconocido por OCR",
    }
    for n in (1, 2):
        enc = "Document ID: CII-EOC-March2021-V1.2"
        doc.add_text(label=DocItemLabel.PAGE_HEADER, text=enc, prov=_prov(n, enc),
                     content_layer=ContentLayer.FURNITURE)
    for n, t in textos.items():
        doc.add_text(label=DocItemLabel.TEXT, text=t, prov=_prov(n, t))
    return doc


class _Resultado:
    def __init__(self, doc):
        from docling.datamodel.base_models import ConversionStatus

        self.document = doc
        self.status = ConversionStatus.SUCCESS
        self.errors = []


class _Convertidor:
    def __init__(self, *a, **k):
        self.opciones = k["format_options"]

    def convert(self, origen, raises_on_error=False):
        return _Resultado(_documento())


@pytest.fixture
def entorno(monkeypatch):
    import docling.document_converter as dc

    referencias = [
        "Document ID: CII-EOC-March2021-V1.2\r\nLa planificación de frentes de trabajo organiza la construcción.",
        "Document ID: CII-EOC-March2021-V1.2\r\nTexto de la segunda página con acentos: acción, niño, información.",
        "",  # página escaneada
    ]
    monkeypatch.setattr(pdf, "texto_por_pagina", lambda origen: referencias)
    monkeypatch.setattr(dc, "DocumentConverter", _Convertidor)


def test_paginas_verificadas(entorno, tmp_path: Path):
    md, res, avisos = pdf.convertir(Path("x.pdf"), tmp_path / "x.md", tmp_path / "x_imagenes", ocr="nunca")

    assert "<!-- página 1 -->" in md and "<!-- página 3 -->" in md
    assert "Document ID" not in md  # encabezado omitido del cuerpo...
    assert sum(res[0].excluidas.values()) == 7  # ...pero registrado en el informe

    assert res[0].aprobado(0.995)
    assert not res[1].aprobado(0.995)  # falta "información" en la página 2
    assert res[1].faltantes == {"información": 1}

    assert res[2].sin_referencia and not res[2].aprobado(0.0)
    assert any("OCR desactivado" in a for a in avisos)


def test_conservar_encabezados(entorno, tmp_path: Path):
    md, res, _ = pdf.convertir(
        Path("x.pdf"), tmp_path / "x.md", tmp_path / "x_imagenes", ocr="nunca", conservar_encabezados=True
    )
    assert md.count("Document ID") == 2
    assert res[0].aprobado(0.995) and not res[0].excluidas
