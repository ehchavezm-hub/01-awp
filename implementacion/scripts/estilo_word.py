"""Estilo común de los documentos Word del kit de implementación AWP.

Lo usan generar_plan_word.py (plan de implementación) y generar_word.py
(plantillas y procedimientos), para que todos los documentos compartan
portada, encabezados, tablas y colores.
"""

from datetime import date

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AZUL = RGBColor(0x1F, 0x38, 0x64)
AZUL_HEX = "1F3864"
AZUL_CLARO_HEX = "DCE6F2"
GRIS_HEX = "F2F2F2"
GRIS_BORDE = "A6A6A6"
FUENTE = "Calibri"

PROYECTO = "Proyecto Tipo (PT) – Complejo de instalaciones en tres fases"
KIT = "Kit de implementación de AWP"


# --------------------------------------------------------------------------
# Utilidades de bajo nivel
# --------------------------------------------------------------------------

def sombrear(celda, color_hex):
    tc_pr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def bordes_tabla(tabla, color=GRIS_BORDE, grosor=4):
    tbl_pr = tabla._tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{lado}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(grosor))
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color)
        bordes.append(b)
    tbl_pr.append(bordes)


def repetir_encabezado(fila):
    tr_pr = fila._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def no_dividir_fila(fila):
    tr_pr = fila._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def margenes_celda(tabla, cm=0.12):
    tbl_pr = tabla._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for lado in ("top", "bottom", "left", "right"):
        m = OxmlElement(f"w:{lado}")
        m.set(qn("w:w"), str(int(cm * 567)))
        m.set(qn("w:type"), "dxa")
        mar.append(m)
    tbl_pr.append(mar)


def campo(parrafo, instruccion, texto_previo=""):
    """Inserta un campo de Word (PAGE, NUMPAGES, TOC...)."""
    run = parrafo.add_run()
    ini = OxmlElement("w:fldChar")
    ini.set(qn("w:fldCharType"), "begin")
    run._r.append(ini)
    run = parrafo.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruccion
    run._r.append(instr)
    run = parrafo.add_run()
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run._r.append(sep)
    if texto_previo:
        parrafo.add_run(texto_previo)
    run = parrafo.add_run()
    fin = OxmlElement("w:fldChar")
    fin.set(qn("w:fldCharType"), "end")
    run._r.append(fin)


def actualizar_campos_al_abrir(doc):
    """Pide a Word que actualice el índice y los números de página al abrir."""
    settings = doc.settings.element
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


# --------------------------------------------------------------------------
# Documento y estilos
# --------------------------------------------------------------------------

def nuevo_documento(horizontal=False):
    doc = Document()
    sec = doc.sections[0]
    if horizontal:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    else:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.header_distance = Cm(1.0)
    sec.footer_distance = Cm(1.0)

    estilos = doc.styles
    normal = estilos["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.1

    tamanos = {1: 16, 2: 13, 3: 11.5, 4: 11}
    for nivel, tam in tamanos.items():
        est = estilos[f"Heading {nivel}"]
        est.font.name = FUENTE
        est.element.rPr.rFonts.set(qn("w:asciiTheme"), "")
        est.element.rPr.rFonts.set(qn("w:hAnsiTheme"), "")
        est.font.size = Pt(tam)
        est.font.bold = True
        est.font.italic = False
        est.font.color.rgb = AZUL
        est.paragraph_format.space_before = Pt(18 if nivel == 1 else 12)
        est.paragraph_format.space_after = Pt(6)
        est.paragraph_format.keep_with_next = True

    for nombre in ("List Bullet", "List Number"):
        estilos[nombre].font.name = FUENTE
        estilos[nombre].font.size = Pt(10.5)
        estilos[nombre].paragraph_format.space_after = Pt(3)

    titulo = estilos["Title"]
    titulo.font.name = FUENTE
    titulo.font.color.rgb = AZUL
    return doc


def encabezado_pie(doc, titulo_doc, codigo=""):
    for sec in doc.sections:
        sec.different_first_page_header_footer = True
        enc = sec.header.paragraphs[0]
        enc.text = ""
        r = enc.add_run(f"{KIT}  |  {titulo_doc}")
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
        if codigo:
            enc.add_run("\t")
            r2 = enc.add_run(codigo)
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
        linea_inferior(enc)

        pie = sec.footer.paragraphs[0]
        pie.text = ""
        pie.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = pie.add_run(f"{PROYECTO}   ·   Página ")
        r.font.size = Pt(8.5)
        campo(pie, "PAGE", "1")
        r = pie.add_run(" de ")
        r.font.size = Pt(8.5)
        campo(pie, "NUMPAGES", "1")
        for run in pie.runs:
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(0x59, 0x59, 0x59)


def linea_inferior(parrafo, color=AZUL_HEX):
    p_pr = parrafo._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), "6")
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color)
    bdr.append(b)
    p_pr.append(bdr)


def portada(doc, titulo, subtitulo, datos, nota=""):
    """Portada sobria: franja de título, subtítulo y tabla de control."""
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run(KIT.upper())
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x7F, 0x7F, 0x7F)
    p = doc.add_paragraph()
    r = p.add_run(titulo)
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = AZUL
    linea_inferior(p)
    p = doc.add_paragraph()
    r = p.add_run(subtitulo)
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    for _ in range(4):
        doc.add_paragraph()
    tabla = doc.add_table(rows=0, cols=2)
    bordes_tabla(tabla)
    margenes_celda(tabla)
    for clave, valor in datos:
        fila = tabla.add_row().cells
        fila[0].text = clave
        fila[1].text = valor
        sombrear(fila[0], AZUL_CLARO_HEX)
        for c in fila:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(0)
                for run in par.runs:
                    run.font.size = Pt(10)
        fila[0].paragraphs[0].runs[0].font.bold = True
    anchos(tabla, [5.0, 12.0])
    if nota:
        doc.add_paragraph()
        p = doc.add_paragraph()
        r = p.add_run(nota)
        r.font.size = Pt(9)
        r.italic = True
        r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    salto_pagina(doc)


def salto_pagina(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def indice(doc, entradas_previas=None):
    """Índice de contenido como campo TOC. Se muestra una versión previa
    con los títulos para que el índice sea legible incluso antes de que
    Word actualice los números de página."""
    p = doc.add_paragraph()
    r = p.add_run("Índice")
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = AZUL
    linea_inferior(p)
    p = doc.add_paragraph()
    previo = ""
    campo(p, 'TOC \\o "1-2" \\h \\z \\u', previo)
    # El contenido previo se añade como párrafos simples después del campo
    if entradas_previas:
        # Se insertan dentro del resultado del campo para que Word los reemplace.
        sep_run = p.runs[2]
        fin_run = p.runs[-1]
        for nivel, texto in entradas_previas:
            r = OxmlElement("w:r")
            if nivel == 1:
                rpr = OxmlElement("w:rPr")
                b = OxmlElement("w:b")
                rpr.append(b)
                r.append(rpr)
            t = OxmlElement("w:t")
            t.set(qn("xml:space"), "preserve")
            t.text = ("    " if nivel > 1 else "") + texto
            r.append(t)
            br = OxmlElement("w:br")
            r.append(br)
            fin_run._r.addprevious(r)
    actualizar_campos_al_abrir(doc)
    salto_pagina(doc)


def anchos(tabla, cms):
    tabla.autofit = False
    for fila in tabla.rows:
        for i, ancho in enumerate(cms):
            if i < len(fila.cells):
                fila.cells[i].width = Cm(ancho)


def tabla_datos(doc, encabezados, filas, cms=None, tam=9, primera_negrita=False):
    """Tabla con encabezado azul, filas alternadas y bordes finos."""
    tabla = doc.add_table(rows=1, cols=len(encabezados))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    bordes_tabla(tabla)
    margenes_celda(tabla)
    enc = tabla.rows[0]
    repetir_encabezado(enc)
    for i, texto in enumerate(encabezados):
        c = enc.cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(texto)
        run.font.bold = True
        run.font.size = Pt(tam)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        sombrear(c, AZUL_HEX)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
    for n, fila in enumerate(filas):
        celdas = tabla.add_row()
        no_dividir_fila(celdas)
        for i, valor in enumerate(fila):
            c = celdas.cells[i]
            c.text = ""
            par = c.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            if callable(valor):
                valor(par)
            else:
                run = par.add_run(str(valor))
                run.font.size = Pt(tam)
                if primera_negrita and i == 0:
                    run.font.bold = True
            for run in par.runs:
                run.font.size = Pt(tam)
            if n % 2 == 1:
                sombrear(c, GRIS_HEX)
    if cms:
        anchos(tabla, cms)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tabla


def recuadro(doc, titulo, texto, color_hex=AZUL_CLARO_HEX):
    """Recuadro de nota (equivalente a las notas de la web)."""
    tabla = doc.add_table(rows=1, cols=1)
    bordes_tabla(tabla, color=AZUL_HEX, grosor=6)
    margenes_celda(tabla, 0.2)
    c = tabla.rows[0].cells[0]
    sombrear(c, color_hex)
    c.text = ""
    p = c.paragraphs[0]
    r = p.add_run(titulo)
    r.font.bold = True
    r.font.color.rgb = AZUL
    r.font.size = Pt(10)
    if isinstance(texto, str):
        texto = [texto]
    for t in texto:
        p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if callable(t):
            t(p)
        else:
            r = p.add_run(t)
            r.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return tabla


def fecha_hoy():
    return date.today().strftime("%d/%m/%Y")
