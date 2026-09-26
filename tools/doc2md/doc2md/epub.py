"""Conversión de EPUB: cada capítulo (documento XHTML del "spine", en orden de
lectura) se convierte con el backend HTML de Docling y se verifica por separado
contra el texto visible de ese mismo XHTML."""

from __future__ import annotations

import posixpath
import re
import shutil
import tempfile
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import defusedxml.ElementTree as ET

from .salida import markdown_de_documento
from .verificar import Resultado, comparar

_NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
}
_TIPOS_HTML = {"application/xhtml+xml", "text/html"}


class _TextoVisible(HTMLParser):
    """Texto que ve el lector de un XHTML: excluye <head>, <script> y <style>, e
    incluye los números que el navegador genera para las listas <ol>. El texto
    alternativo de las imágenes se guarda aparte en `alternativos`."""

    _OCULTOS = {"head", "script", "style", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.partes: list[str] = []
        self.alternativos: list[str] = []
        self._oculto = 0
        self._listas: list[int | None] = []  # contador por lista abierta (None = <ul>)

    def handle_starttag(self, tag, attrs):
        if tag in self._OCULTOS:
            self._oculto += 1
        self.partes.append(" ")
        if tag == "img" and not self._oculto:
            self.alternativos.append(dict(attrs).get("alt") or "")
        if tag == "ol":
            inicio = dict(attrs).get("start") or "1"
            self._listas.append(int(inicio) - 1 if inicio.lstrip("-").isdigit() else 0)
        elif tag == "ul":
            self._listas.append(None)
        elif tag == "li" and self._listas and self._listas[-1] is not None:
            valor = dict(attrs).get("value")
            self._listas[-1] = int(valor) if valor and valor.isdigit() else self._listas[-1] + 1
            if not self._oculto:
                self.partes.append(f" {self._listas[-1]} ")

    def handle_endtag(self, tag):
        if tag in self._OCULTOS and self._oculto:
            self._oculto -= 1
        if tag in ("ol", "ul") and self._listas:
            self._listas.pop()
        self.partes.append(" ")

    def handle_data(self, data):
        if not self._oculto:
            self.partes.append(data)


def texto_visible(xhtml: str) -> tuple[str, str]:
    """Devuelve (texto visible, texto alternativo de las imágenes)."""
    p = _TextoVisible()
    p.feed(xhtml)
    p.close()
    return "".join(p.partes), "\n".join(p.alternativos)


def capitulos(epub: zipfile.ZipFile) -> list[str]:
    """Rutas (dentro del ZIP) de los documentos XHTML en orden de lectura."""
    container = ET.fromstring(epub.read("META-INF/container.xml"))
    rootfile = container.find(".//c:rootfile", _NS)
    if rootfile is None:
        raise ValueError("EPUB sin rootfile en META-INF/container.xml")
    opf_ruta = rootfile.get("full-path")
    opf_dir = posixpath.dirname(opf_ruta)
    opf = ET.fromstring(epub.read(opf_ruta))

    manifiesto = {
        item.get("id"): item
        for item in opf.findall(".//opf:manifest/opf:item", _NS)
    }
    rutas = []
    for itemref in opf.findall(".//opf:spine/opf:itemref", _NS):
        item = manifiesto.get(itemref.get("idref"))
        if item is None or item.get("media-type") not in _TIPOS_HTML:
            continue
        rutas.append(posixpath.normpath(posixpath.join(opf_dir, unquote(item.get("href")))))
    return rutas


_ATRIBUTO_RECURSO = re.compile(
    r'(<(?:img|image)\b[^>]*?\s(?:src|xlink:href|href)\s*=\s*)(["\'])(.*?)\2',
    re.IGNORECASE | re.DOTALL,
)


def _rutas_desde_raiz(xhtml: str, ruta_capitulo: str) -> str:
    """Reescribe las rutas de imágenes para que sean relativas a la raíz del
    EPUB (Docling bloquea rutas con "../" fuera de la carpeta del documento)."""
    base = posixpath.dirname(ruta_capitulo)

    def reemplazar(m: re.Match) -> str:
        valor = m.group(3)
        if re.match(r"^[a-z][a-z0-9+.-]*:", valor, re.IGNORECASE) or valor.startswith("#"):
            return m.group(0)
        ruta = posixpath.normpath(posixpath.join(base, unquote(valor)))
        return f"{m.group(1)}{m.group(2)}{ruta}{m.group(2)}"

    return _ATRIBUTO_RECURSO.sub(reemplazar, xhtml)


def _extraer(epub: zipfile.ZipFile, destino: Path) -> None:
    raiz = destino.resolve()
    for miembro in epub.infolist():
        ruta = (destino / miembro.filename).resolve()
        if not ruta.is_relative_to(raiz):
            raise ValueError(f"Ruta insegura dentro del EPUB: {miembro.filename}")
    epub.extractall(destino)


def convertir(origen: Path, salida_md: Path, dir_imagenes: Path) -> tuple[str, list[Resultado], list[str]]:
    from docling.datamodel.backend_options import HTMLBackendOptions
    from docling.datamodel.base_models import ConversionStatus, InputFormat
    from docling.document_converter import DocumentConverter, HTMLFormatOption

    convertidor = DocumentConverter(
        allowed_formats=[InputFormat.HTML],
        format_options={
            InputFormat.HTML: HTMLFormatOption(
                backend_options=HTMLBackendOptions(
                    enable_local_fetch=True, enable_remote_fetch=False, fetch_images=True
                )
            )
        },
    )

    partes: list[str] = []
    resultados: list[Resultado] = []
    avisos: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="doc2md_epub_"))
    try:
        with zipfile.ZipFile(origen) as epub:
            rutas = capitulos(epub)
            _extraer(epub, tmp)
        if not rutas:
            raise ValueError("El EPUB no tiene capítulos XHTML en su spine")

        for n, ruta in enumerate(rutas, 1):
            archivo = tmp / ruta
            etiqueta = f"Capítulo {n} (`{ruta}`)"
            xhtml = archivo.read_text(encoding="utf-8", errors="strict")
            # Copia en la raíz del EPUB extraído, con rutas de imagen desde la raíz.
            copia = tmp / f"__doc2md_{n:04}.xhtml"
            copia.write_text(_rutas_desde_raiz(xhtml, ruta), encoding="utf-8")
            conv = convertidor.convert(copia, raises_on_error=False)
            if conv.status != ConversionStatus.SUCCESS:
                errores = "; ".join(e.error_message for e in conv.errors) or str(conv.status)
                avisos.append(f"{etiqueta}: la conversión falló ({errores}).")
                md = ""
            else:
                md = markdown_de_documento(conv.document, salida_md, dir_imagenes)
            partes.append(f"<!-- capítulo {n}: {ruta} -->\n\n{md}".rstrip() + "\n")
            visible, alternativo = texto_visible(xhtml)
            resultados.append(comparar(etiqueta, visible, md, opcional=alternativo))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return "\n".join(partes), resultados, avisos
