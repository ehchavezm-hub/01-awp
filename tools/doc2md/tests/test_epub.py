import io
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("defusedxml")

from doc2md.epub import _rutas_desde_raiz, capitulos, texto_visible  # noqa: E402

_CONTAINER = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""

_OPF = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <manifest>
    <item id="c2" href="text/cap%202.xhtml" media-type="application/xhtml+xml"/>
    <item id="c1" href="text/cap1.xhtml" media-type="application/xhtml+xml"/>
    <item id="img" href="media/fig.png" media-type="image/png"/>
  </manifest>
  <spine><itemref idref="c1"/><itemref idref="c2"/><itemref idref="img"/></spine>
</package>"""

_CAP1 = """<html xmlns="http://www.w3.org/1999/xhtml"><head><title>No visible</title>
<style>p { color: red }</style></head><body>
<h1>Capítulo 1</h1><p>Texto &amp; más <b>texto</b>.</p>
<ol start="3"><li>tercero</li><li>cuarto</li></ol><ul><li>viñeta</li></ul>
<img src="../media/fig.png" alt="figura"/></body></html>"""


def _epub(tmp_path: Path) -> Path:
    ruta = tmp_path / "libro.epub"
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("META-INF/container.xml", _CONTAINER)
        z.writestr("OEBPS/content.opf", _OPF)
        z.writestr("OEBPS/text/cap1.xhtml", _CAP1)
        z.writestr("OEBPS/text/cap 2.xhtml", "<html><body><p>Fin del libro</p></body></html>")
        buf = io.BytesIO()
        pytest.importorskip("PIL").Image.new("RGB", (40, 20), "blue").save(buf, "PNG")
        z.writestr("OEBPS/media/fig.png", buf.getvalue())
    return ruta


def test_capitulos_en_orden_del_spine(tmp_path):
    with zipfile.ZipFile(_epub(tmp_path)) as z:
        assert capitulos(z) == ["OEBPS/text/cap1.xhtml", "OEBPS/text/cap 2.xhtml"]


def test_texto_visible_numera_listas_y_omite_head():
    visible, alternativo = texto_visible(_CAP1)
    assert " ".join(visible.split()) == "Capítulo 1 Texto & más texto . 3 tercero 4 cuarto viñeta"
    assert alternativo == "figura"


def test_rutas_de_imagen_desde_la_raiz():
    assert 'src="OEBPS/media/fig.png"' in _rutas_desde_raiz(_CAP1, "OEBPS/text/cap1.xhtml")
    assert _rutas_desde_raiz('<img src="http://x.org/a.png"/>', "a/b.xhtml") == '<img src="http://x.org/a.png"/>'


def test_conversion_completa(tmp_path):
    pytest.importorskip("docling")
    from doc2md import epub

    md, res, avisos = epub.convertir(_epub(tmp_path), tmp_path / "libro.md", tmp_path / "libro_imagenes")
    assert not avisos
    assert [r.aprobado(1.0) for r in res] == [True, True], [(r.faltantes, r.sobrantes) for r in res]
    assert "<!-- capítulo 2: OEBPS/text/cap 2.xhtml -->" in md
    assert "](libro_imagenes/" in md
    assert len(list((tmp_path / "libro_imagenes").glob("*.png"))) == 1
