"""Conversión de PDF con Docling y verificación página por página contra el
texto extraído con pdfium (un lector de PDF independiente del de Docling)."""

from __future__ import annotations

import shutil
from pathlib import Path

from .salida import markdown_de_documento
from .verificar import Resultado, comparar, palabras

# Menos palabras que esto en la capa de texto = página tratada como escaneada.
_MIN_PALABRAS_CAPA_TEXTO = 3


def texto_por_pagina(origen: Path) -> list[str]:
    """Texto de la capa de texto de cada página (índice 0 = página 1)."""
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(origen)
    try:
        textos = []
        for pagina in pdf:
            tp = pagina.get_textpage()
            textos.append(tp.get_text_range())
            tp.close()
            pagina.close()
        return textos
    finally:
        pdf.close()


def _opciones_ocr(idiomas: list[str], avisos: list[str]):
    from docling.datamodel.pipeline_options import RapidOcrOptions, TesseractCliOcrOptions

    if shutil.which("tesseract"):
        return TesseractCliOcrOptions(lang=idiomas)
    avisos.append(
        "No se encontró Tesseract; el OCR usa RapidOCR, que reconoce peor los acentos y la ñ. "
        "Instala Tesseract con los idiomas spa/eng para mejores resultados."
    )
    return RapidOcrOptions()


def convertir(
    origen: Path,
    salida_md: Path,
    dir_imagenes: Path,
    ocr: str = "auto",
    idiomas: list[str] | None = None,
    conservar_encabezados: bool = False,
    modelos: Path | None = None,
) -> tuple[str, list[Resultado], list[str]]:
    from docling.datamodel.base_models import ConversionStatus, InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import ContentLayer

    avisos: list[str] = []
    referencias = texto_por_pagina(origen)
    escaneadas = {
        n for n, t in enumerate(referencias, 1) if len(palabras(t)) < _MIN_PALABRAS_CAPA_TEXTO
    }

    opciones = PdfPipelineOptions(
        do_table_structure=True,
        generate_picture_images=True,
        images_scale=2.0,
    )
    opciones.table_structure_options.mode = TableFormerMode.ACCURATE
    # El texto de las celdas se toma de la capa de texto del PDF, no se predice.
    opciones.table_structure_options.do_cell_matching = True
    if modelos:
        opciones.artifacts_path = modelos

    usar_ocr = ocr == "siempre" or (ocr == "auto" and escaneadas)
    opciones.do_ocr = bool(usar_ocr)
    if usar_ocr:
        opciones.ocr_options = _opciones_ocr(idiomas or ["spa", "eng"], avisos)
        if ocr == "siempre":
            opciones.ocr_options.force_full_page_ocr = True
    elif escaneadas:
        avisos.append(
            f"Páginas sin capa de texto y OCR desactivado: {sorted(escaneadas)}. Su texto no se convertirá."
        )

    convertidor = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opciones)},
    )
    try:
        conv = convertidor.convert(origen, raises_on_error=False)
    except Exception as e:
        if modelos is None:
            raise RuntimeError(
                f"{e}. Si Docling no pudo descargar sus modelos (se bajan de huggingface.co la "
                "primera vez), ejecútalo con internet o descárgalos con "
                "`docling-tools models download` y pásalos con --modelos."
            ) from e
        raise
    if conv.status not in (ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS):
        errores = "; ".join(e.error_message for e in conv.errors) or str(conv.status)
        raise RuntimeError(f"Docling no pudo convertir {origen.name}: {errores}")
    if conv.status == ConversionStatus.PARTIAL_SUCCESS:
        avisos.append(
            "Docling informó una conversión parcial: "
            + ("; ".join(e.error_message for e in conv.errors) or "sin detalle")
        )

    doc = conv.document
    capas = {ContentLayer.BODY}
    if conservar_encabezados:
        capas.add(ContentLayer.FURNITURE)

    partes: list[str] = []
    resultados: list[Resultado] = []
    for n, referencia in enumerate(referencias, 1):
        md = markdown_de_documento(doc, salida_md, dir_imagenes, page_no=n, capas=capas)
        partes.append(f"<!-- página {n} -->\n\n{md}".rstrip() + "\n")

        excluido = ""
        if not conservar_encabezados:
            excluido = "\n".join(
                item.text
                for item, _ in doc.iterate_items(
                    page_no=n, included_content_layers={ContentLayer.FURNITURE}
                )
                if getattr(item, "text", None)
            )

        if n in escaneadas:
            r = comparar(f"Página {n}", "", md)
            r.sin_referencia = True
            r.ocr = usar_ocr
            r.sobrantes.clear()
            r.notas.append(
                "Página sin capa de texto (escaneada): "
                + ("el texto proviene de OCR y no hay referencia para verificarlo; compárala con el original."
                   if usar_ocr else "no se extrajo texto.")
            )
        else:
            r = comparar(f"Página {n}", referencia, md, excluido=excluido)
            if ocr == "siempre":
                r.ocr = True
                r.notas.append("OCR forzado en todas las páginas: revisar contra el original.")
        resultados.append(r)

    return "\n".join(partes), resultados, avisos
