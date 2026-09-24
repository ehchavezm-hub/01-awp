"""Biblioteca de diseño de la presentación AWP.

Se apoya en plantilla_ppt.pptx (paleta AECOM, Arial, franja naranja superior) y ofrece
diseños de lámina reutilizables: portada, separador, bloques, proceso, comparación, tabla,
dato clave, cita, diagramas y cierre. Cada texto se mide con las métricas de Liberation Sans
(equivalente métrico de Arial) para detectar desbordes antes de renderizar.
"""
import math
from pathlib import Path

from PIL import ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = RAIZ / "plantilla_ppt.pptx"
ICONOS = RAIZ / "presentacion" / "assets" / "iconos"

# Paleta AECOM de plantilla_ppt.pptx (lámina 10, "Configuración maestra").
NEGRO = "1A1A1A"
FONDO = "F2F2F2"
NARANJA = "FF6600"
NARANJA_OSC = "CC4400"
NARANJA_MED = "FF8833"
NARANJA_CLARO = "FF9955"
NARANJA_TINTE = "FFE3CF"
TEXTO = "2E2E2E"
AZUL = "003087"
AZUL_CORP = "005A9C"
AZUL_MEDIO = "0078C1"
AZUL_CLARO = "5A9FD4"
AZUL_PALIDO = "A8CFE8"
AZUL_TINTE = "E3EEF7"
GRIS = "6D6E71"
GRIS_MEDIO = "555555"
GRIS_OSC = "2E2E2E"
TARJETA = "222222"
BORDE = "BCBEC0"
BORDE_OSC = "333333"
GRIS_SUAVE = "8A8B8E"
BLANCO = "FFFFFF"
FUENTE = "Arial"
MONO = "Courier New"

ANCHO, ALTO = 13.333, 7.5
M = 0.6                      # margen lateral
UTIL = ANCHO - 2 * M         # ancho útil
Y0 = 2.0                     # inicio del área de contenido
Y1 = 6.75                    # fin del área de contenido

# ---------------------------------------------------------------- medición de texto

_FUENTES = {}
_DIR_FUENTES = Path("/usr/share/fonts/truetype/liberation")


def _fuente(nombre, negrita, tam):
    fam = "LiberationMono" if nombre == MONO else "LiberationSans"
    archivo = f"{fam}-{'Bold' if negrita else 'Regular'}.ttf"
    clave = (archivo, tam)
    if clave not in _FUENTES:
        try:
            _FUENTES[clave] = ImageFont.truetype(str(_DIR_FUENTES / archivo), int(round(tam * 10)))
        except OSError:
            _FUENTES[clave] = None
    return _FUENTES[clave]


def _ancho(runs):
    """Ancho en pulgadas de una lista de runs (t, fuente, negrita, tam, esp)."""
    total = 0.0
    for t, fuente, negrita, tam, esp in runs:
        f = _fuente(fuente, negrita, tam)
        if f is None:
            return None
        total += f.getlength(t) / 10 / 72 + esp * len(t) / 72
    return total


def _lineas(runs, ancho):
    """Número de líneas que ocupa un párrafo con ajuste por palabras."""
    palabras = []
    for t, fuente, negrita, tam, esp in runs:
        for i, trozo in enumerate(t.split(" ")):
            palabras.append(((" " if i else "") + trozo, fuente, negrita, tam, esp))
    lineas, actual = 1, 0.0
    for p in palabras:
        w = _ancho([p])
        if w is None:
            return 1
        if _ancho([(p[0].strip(),) + p[1:]]) > ancho + 0.02:
            AVISOS.append(f"palabra más ancha que su caja: {p[0].strip()}")
        if actual + w > ancho + 1e-3 and actual > 0:
            lineas += 1
            actual = _ancho([(p[0].lstrip(),) + p[1:]])
        else:
            actual += w
    return lineas


AVISOS = []

# ---------------------------------------------------------------- primitivas


def rgb(h):
    return RGBColor.from_string(h)


def _alfa(shape, pct):
    """Aplica transparencia (0-100) al relleno sólido de una forma."""
    clr = shape.fill._xPr.find(qn("a:solidFill"))[0]
    a = clr.makeelement(qn("a:alpha"), {"val": str(int((100 - pct) * 1000))})
    clr.append(a)


def caja(s, x, y, w, h, relleno=None, borde=None, grosor=0.75, forma=MSO_SHAPE.RECTANGLE, alfa=None,
         guiones=False):
    shp = s.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    if relleno:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(relleno)
        if alfa:
            _alfa(shp, alfa)
    else:
        shp.fill.background()
    if borde:
        shp.line.color.rgb = rgb(borde)
        shp.line.width = Pt(grosor)
        if guiones:
            shp.line.dash_style = 7  # MSO_LINE.DASH
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    shp.text_frame.text = ""
    return shp


def texto(s, x, y, w, h, parrafos, tam=14, color=TEXTO, negrita=False, alinear=PP_ALIGN.LEFT,
          ancla=MSO_ANCHOR.TOP, fuente=FUENTE, espaciado=0, interlineado=None, espacio_despues=0,
          nombre=None, cursiva=False, verificar=True):
    """parrafos: str | lista de párrafos; cada párrafo es str, dict o lista de runs (dict: t, tam, color,
    negrita, fuente, esp, cursiva)."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if nombre:
        tb.name = nombre
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ancla
    if isinstance(parrafos, str):
        parrafos = [parrafos]
    alto_total = 0.0
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinear
        if interlineado:
            p.line_spacing = interlineado
        if espacio_despues:
            p.space_after = Pt(espacio_despues)
        runs = [par] if isinstance(par, (str, dict)) else par
        medidas = []
        for r in runs:
            if isinstance(r, str):
                r = {"t": r}
            run = p.add_run()
            run.text = r["t"]
            f = run.font
            f.name = r.get("fuente", fuente)
            f.size = Pt(r.get("tam", tam))
            f.bold = r.get("negrita", negrita)
            f.italic = r.get("cursiva", cursiva)
            f.color.rgb = rgb(r.get("color", color))
            esp = r.get("esp", espaciado)
            if esp:
                run._r.get_or_add_rPr().set("spc", str(int(esp * 100)))
            medidas.append((r["t"], f.name, f.bold, r.get("tam", tam), esp))
        tmax = max(m[3] for m in medidas)
        n = _lineas(medidas, w)
        alto_total += n * tmax * 1.17 * (interlineado or 1.0) / 72
        if i < len(parrafos) - 1:
            alto_total += espacio_despues / 72
    if verificar and alto_total > h + 0.06:
        AVISOS.append(f"desborde vertical ({alto_total:.2f} > {h:.2f} in): "
                      f"{' / '.join(str(p)[:50] for p in parrafos)[:90]}")
    return tb


def icono(s, nombre, x, y, lado):
    return s.shapes.add_picture(str(ICONOS / f"{nombre}.png"), Inches(x), Inches(y), Inches(lado), Inches(lado))


def icono_circulo(s, nombre, x, y, d, relleno=NARANJA, color_icono="w"):
    caja(s, x, y, d, d, relleno=relleno, forma=MSO_SHAPE.OVAL)
    lado = d * 0.52
    icono(s, f"{nombre}_{color_icono}", x + (d - lado) / 2, y + (d - lado) / 2, lado)


def numero_circulo(s, n, x, y, d, relleno=NARANJA, tam=None, color=BLANCO):
    caja(s, x, y, d, d, relleno=relleno, forma=MSO_SHAPE.OVAL)
    texto(s, x, y, d, d, str(n), tam=tam or d * 30, negrita=True, color=color,
          alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE, verificar=False)


def flecha(s, x1, y1, x2, y2, color=GRIS, grosor=1.75, punta=True):
    con = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    con.line.color.rgb = rgb(color)
    con.line.width = Pt(grosor)
    if punta:
        ln = con.line._get_or_add_ln()
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))
    return con


def linea(s, x1, y1, x2, y2, color=BORDE, grosor=1.0):
    return flecha(s, x1, y1, x2, y2, color=color, grosor=grosor, punta=False)


# ---------------------------------------------------------------- mazo


class Mazo:
    """Presentación basada en la plantilla, con numeración y pie automáticos."""

    def __init__(self):
        self.prs = Presentation(str(PLANTILLA))
        lista = self.prs.slides._sldIdLst
        for sld in list(lista):
            self.prs.part.drop_rel(sld.rId)
            lista.remove(sld)
        # El patrón de notas de la plantilla no tiene marcador de cuerpo: se usa el estándar.
        pres = self.prs.part._element
        nm = pres.find(qn("p:notesMasterIdLst"))
        if nm is not None:
            self.prs.part.drop_rel(nm[0].get(qn("r:id")))
            pres.remove(nm)
        self.n = 0
        self.pie = ""
        self.modulo = 0

    def nueva(self, color_fondo):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[0])
        self.n += 1
        fill = s.background.fill
        fill.solid()
        fill.fore_color.rgb = rgb(color_fondo)
        caja(s, 0, 0, ANCHO, 0.055, relleno=NARANJA)  # franja superior de la plantilla
        s._awp_n = self.n
        return s

    def pie_de_pagina(self, s, oscuro=False, texto_pie=None):
        color = GRIS_SUAVE if oscuro else GRIS
        texto(s, M, 7.02, 9.5, 0.25, f"IMPLEMENTACIÓN DE AWP  ·  {texto_pie or self.pie}", tam=9, color=color,
              espaciado=1, verificar=False)
        texto(s, ANCHO - M - 2, 7.02, 2, 0.25, f"{self.n:03d}", tam=9, color=color, fuente=MONO,
              alinear=PP_ALIGN.RIGHT, verificar=False)

    def contenido(self, etiqueta, titulo, oscuro=False):
        s = self.nueva(NEGRO if oscuro else FONDO)
        texto(s, M, 0.42, 12, 0.3, etiqueta.upper(), tam=11, color=NARANJA, negrita=True, espaciado=3)
        texto(s, M, 0.74, UTIL, 1.05, titulo, tam=28, negrita=True, color=BLANCO if oscuro else NEGRO,
              interlineado=0.95, nombre="Título")
        self.pie_de_pagina(s, oscuro)
        return s

    def guardar(self, ruta, titulo):
        self.prs.core_properties.title = titulo
        self.prs.core_properties.language = "es-PE"
        self.prs.save(str(ruta))


def notas(s, explicacion, fuentes):
    tf = s.notes_slide.notes_text_frame
    tf.text = explicacion.strip() + "\n\nFUENTE: " + fuentes.strip()


# ---------------------------------------------------------------- diseños


def separador(d, num, etiqueta, titulo, sub, fase=None, total_modulos=13):
    s = d.nueva(NEGRO)
    texto(s, M, 1.2, 4, 2.4, f"{num:02d}", tam=150, color=NARANJA, negrita=True, verificar=False)
    texto(s, 4.55, 1.62, 8.2, 0.3, etiqueta.upper(), tam=12, color=NARANJA, negrita=True, espaciado=3)
    tam_t = 36 if _lineas([(titulo, FUENTE, True, 36, 0)], 8.15) <= 2 else 30
    texto(s, 4.55, 2.05, 8.15, 1.65, titulo, tam=tam_t, color=BLANCO, negrita=True, interlineado=0.95,
          nombre="Título")
    texto(s, 4.55, 3.8, 8.1, 0.75, sub, tam=15, color=BORDE, interlineado=1.1)
    if fase is not None:
        fases = [("FASE 1", "Planificación · FEL 2"), ("FASE 2", "Ingeniería y compras · FEL 3"),
                 ("FASE 3", "Construcción"), ("FASE 4", "Puesta en marcha")]
        x, w, gap, y = M, 2.85, 0.24, 5.35
        for i, (f, n) in enumerate(fases):
            activo = i == fase - 1
            caja(s, x, y, w, 0.95, relleno=NARANJA if activo else TARJETA, borde=None if activo else BORDE_OSC)
            texto(s, x + 0.25, y + 0.17, w - 0.4, 0.25, f, tam=10, negrita=True, espaciado=2,
                  color=BLANCO if activo else NARANJA)
            texto(s, x + 0.25, y + 0.47, w - 0.4, 0.3, n, tam=12, negrita=activo, color=BLANCO if activo else BORDE)
            x += w + gap
    else:
        # Indicador de avance por módulo.
        n = total_modulos
        gap = 0.1
        w = (UTIL - gap * (n - 1)) / n
        y = 5.55
        for i in range(1, n + 1):
            activo = i == num
            hecho = i < num
            caja(s, M + (i - 1) * (w + gap), y, w, 0.55,
                 relleno=NARANJA if activo else (BORDE_OSC if hecho else TARJETA),
                 borde=None if activo else BORDE_OSC)
            texto(s, M + (i - 1) * (w + gap), y, w, 0.55, f"{i:02d}", tam=11, negrita=activo, fuente=MONO,
                  color=BLANCO if activo else GRIS_SUAVE, alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
        texto(s, M, y - 0.4, 6, 0.3, "MÓDULOS", tam=10, color=GRIS_SUAVE, negrita=True, espaciado=2)
    d.pie_de_pagina(s, oscuro=True)
    return s


def barra_nota(s, texto_nota, y=None, icono_nombre="flag_o", etiqueta="Clave: ", alto=0.72):
    """Barra oscura inferior con la idea que el público debe recordar. texto_nota: str o (etiqueta, str)."""
    if isinstance(texto_nota, tuple):
        etiqueta, texto_nota = texto_nota
    y = y if y is not None else Y1 - alto
    caja(s, M, y, UTIL, alto, relleno=NEGRO)
    icono(s, icono_nombre, M + 0.3, y + (alto - 0.4) / 2, 0.4)
    texto(s, M + 0.95, y, UTIL - 1.2, alto,
          [[{"t": etiqueta, "negrita": True, "color": NARANJA}, {"t": texto_nota, "color": BLANCO}]],
          tam=14, ancla=MSO_ANCHOR.MIDDLE)


def bloques(d, etiqueta, titulo, items, cols=None, nota=None, color_icono="o", tam_titulo=15, tam_desc=12,
            y0=Y0, alto_max=2.7):
    """Rejilla de tarjetas: items = [(icono, título, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(items)
    cols = cols or (n if n <= 4 else math.ceil(n / 2))
    filas = math.ceil(n / cols)
    gap = 0.28
    y_fin = (Y1 - 0.72 - 0.3) if nota else Y1
    w = (UTIL - gap * (cols - 1)) / cols
    h = min((y_fin - y0 - gap * (filas - 1)) / filas, alto_max)
    for i, (ic, t, desc) in enumerate(items):
        f, c = divmod(i, cols)
        x = M + c * (w + gap)
        y = y0 + f * (h + gap)
        caja(s, x, y, w, h, relleno=BLANCO, borde=BORDE)
        if h < 2.0:
            # Tarjeta compacta: ícono a la izquierda del título.
            icono(s, f"{ic}_{color_icono}", x + 0.3, y + 0.25, 0.42)
            texto(s, x + 0.9, y + 0.2, w - 1.15, 0.52, t, tam=tam_titulo, negrita=True, color=NEGRO,
                  interlineado=0.95, ancla=MSO_ANCHOR.MIDDLE)
            texto(s, x + 0.3, y + 0.85, w - 0.55, h - 0.95, desc, tam=tam_desc, color=GRIS, interlineado=1.05)
            continue
        lado = 0.5
        icono(s, f"{ic}_{color_icono}", x + 0.3, y + 0.28, lado)
        ty = y + 0.28 + lado + 0.18
        alto_t = 0.62 if h >= 2.0 else 0.34
        texto(s, x + 0.3, ty, w - 0.55, alto_t, t, tam=tam_titulo, negrita=True, color=NEGRO, interlineado=0.95,
              ancla=MSO_ANCHOR.TOP)
        dy = ty + 0.68
        texto(s, x + 0.3, dy, w - 0.55, y + h - dy - 0.15, desc, tam=tam_desc, color=GRIS, interlineado=1.05)
    if nota:
        barra_nota(s, nota)
    return s


def bloques_horizontales(d, etiqueta, titulo, items, nota=None, cols=2, tam_desc=12):
    """Filas con ícono en círculo a la izquierda: items = [(icono, título, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(items)
    filas = math.ceil(n / cols)
    gap_x, gap_y = 0.35, 0.22
    y_fin = (Y1 - 0.72 - 0.3) if nota else Y1
    w = (UTIL - gap_x * (cols - 1)) / cols
    h = min((y_fin - Y0 - gap_y * (filas - 1)) / filas, 1.25)
    for i, (ic, t, desc) in enumerate(items):
        f, c = divmod(i, cols)
        x = M + c * (w + gap_x)
        y = Y0 + f * (h + gap_y)
        caja(s, x, y, w, h, relleno=BLANCO, borde=BORDE)
        dc = min(0.7, h - 0.3)
        icono_circulo(s, ic, x + 0.25, y + (h - dc) / 2, dc)
        texto(s, x + 0.25 + dc + 0.25, y + 0.14, w - dc - 0.75, h - 0.28,
              [[{"t": t, "negrita": True, "color": NEGRO, "tam": 14}], [{"t": desc, "color": GRIS}]],
              tam=tam_desc, ancla=MSO_ANCHOR.MIDDLE, interlineado=1.05, espacio_despues=3)
    if nota:
        barra_nota(s, nota)
    return s


def proceso(d, etiqueta, titulo, pasos, nota=None, y0=2.05):
    """Pasos horizontales numerados: pasos = [(icono, título, descripción, [(etiqueta, valor, color)])]."""
    s = d.contenido(etiqueta, titulo)
    n = len(pasos)
    gap = 0.3 if n <= 4 else 0.26
    w = (UTIL - gap * (n - 1)) / n
    tiene_extras = any(len(p) > 3 and p[3] for p in pasos)
    y_fin = (Y1 - 0.75 - 0.3) if nota else Y1
    h = min(y_fin - y0, 3.45 if tiene_extras else 3.1)
    tt = 15 if n <= 4 else 14
    for i, p in enumerate(pasos):
        ic, t, desc = p[:3]
        extras = p[3] if len(p) > 3 else None
        x = M + i * (w + gap)
        caja(s, x, y0, w, h, relleno=BLANCO, borde=BORDE)
        numero_circulo(s, i + 1, x + 0.25, y0 + 0.28, 0.52, tam=17)
        icono(s, f"{ic}_o", x + w - 0.72, y0 + 0.3, 0.46)
        texto(s, x + 0.25, y0 + 1.02, w - 0.45, 0.62, t, tam=tt, negrita=True, color=NEGRO, interlineado=0.95)
        dh = (h - 1.7 - (0.95 if tiene_extras else 0.15))
        texto(s, x + 0.25, y0 + 1.7, w - 0.45, dh, desc, tam=12, color=GRIS, interlineado=1.05)
        if extras:
            yl = y0 + h - 0.95
            linea(s, x + 0.25, yl, x + w - 0.25, yl)
            for j, (etq, val, col) in enumerate(extras):
                yy = yl + 0.12 + j * 0.36
                texto(s, x + 0.25, yy, w - 1.3, 0.3, etq, tam=10, color=GRIS, ancla=MSO_ANCHOR.MIDDLE)
                texto(s, x + w - 1.3, yy, 1.05, 0.3, val, tam=12, negrita=True, color=col, fuente=MONO,
                      alinear=PP_ALIGN.RIGHT, ancla=MSO_ANCHOR.MIDDLE)
        if i < n - 1:
            flecha(s, x + w + 0.04, y0 + h / 2, x + w + gap - 0.04, y0 + h / 2, color=NARANJA, grosor=2)
    if nota:
        # nota: "texto" o ("Etiqueta: ", "texto")
        etq, txt = nota if isinstance(nota, tuple) else ("Clave: ", nota)
        barra_nota(s, txt, etiqueta=etq)
    return s


def comparacion(d, etiqueta, titulo, izq, der, nota=None):
    """Dos paneles. Cada panel: dict(titulo, color, icono_res, puntos=[(t, desc)], resultado, numerado)."""
    s = d.contenido(etiqueta, titulo)
    w, gap, y = (UTIL - 0.33) / 2, 0.33, Y0
    h = (Y1 - y) - (1.02 if nota else 0)
    x = M
    for panel in (izq, der):
        color = panel["color"]
        caja(s, x, y, w, h, relleno=BLANCO, borde=BORDE)
        caja(s, x, y, w, 0.55, relleno=color)
        texto(s, x + 0.3, y, w - 0.6, 0.55, panel["titulo"].upper(), tam=12, negrita=True, color=BLANCO,
              espaciado=2, ancla=MSO_ANCHOR.MIDDLE)
        puntos = panel["puntos"]
        res = panel.get("resultado")
        area = h - 0.55 - 0.25 - (1.0 if res else 0.15)
        paso = min(area / len(puntos), 0.95)
        yy = y + 0.8
        numerado = panel.get("numerado", True)
        for k, (p, desc) in enumerate(puntos):
            if numerado:
                numero_circulo(s, k + 1, x + 0.3, yy, 0.42, relleno=color, tam=13)
            else:
                caja(s, x + 0.42, yy + 0.12, 0.17, 0.17, relleno=color, forma=MSO_SHAPE.OVAL)
            texto(s, x + 0.95, yy - 0.02, w - 1.25, 0.3, p, tam=14, negrita=True, color=NEGRO)
            if desc:
                texto(s, x + 0.95, yy + 0.3, w - 1.25, paso - 0.35, desc, tam=11.5, color=GRIS)
            if numerado and panel.get("flechas", True) and k < len(puntos) - 1:
                flecha(s, x + 0.51, yy + 0.47, x + 0.51, yy + paso - 0.07, color=color, grosor=1.5)
            yy += paso
        if res:
            caja(s, x + 0.3, y + h - 0.95, w - 0.6, 0.7, relleno=FONDO)
            icono(s, panel.get("icono_res", "check_o"), x + 0.5, y + h - 0.8, 0.4)
            texto(s, x + 1.1, y + h - 0.95, w - 1.5, 0.7, res, tam=13.5, negrita=True, color=NEGRO,
                  ancla=MSO_ANCHOR.MIDDLE)
        x += w + gap
    if nota:
        barra_nota(s, nota)
    return s


def tabla(d, etiqueta, titulo, encabezados, filas, anchos, destacar=(), nota=None, tam=13, alto_fila=None,
          mono=(0,), colores_col=None, y0=Y0, alinear_col=None, icono_nota="layers_o"):
    s = d.contenido(etiqueta, titulo)
    total = sum(anchos)
    x0 = M + (UTIL - total) / 2
    hh = 0.5
    disponible = (Y1 - y0) - (0.7 if nota else 0) - hh
    hf = alto_fila or min(disponible / len(filas), 0.62)
    shp = s.shapes.add_table(len(filas) + 1, len(encabezados), Inches(x0), Inches(y0), Inches(total),
                             Inches(hh + hf * len(filas)))
    tbl = shp.table
    tblPr = tbl._tbl.tblPr
    tblPr.set("bandRow", "0")
    tblPr.set("firstRow", "0")
    for i, wc in enumerate(anchos):
        tbl.columns[i].width = Inches(wc)
    tbl.rows[0].height = Inches(hh)
    for r in range(1, len(filas) + 1):
        tbl.rows[r].height = Inches(hf)

    def celda(c, txt, t, color, negrita, relleno, fuente=FUENTE, alinear=PP_ALIGN.LEFT, esp=0, ancho=1.0,
              alto=hf):
        c.fill.solid()
        c.fill.fore_color.rgb = rgb(relleno)
        c.margin_left = Inches(0.15)
        c.margin_right = Inches(0.1)
        c.margin_top = c.margin_bottom = Inches(0.03)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame
        tf.word_wrap = True
        tf.text = ""
        p = tf.paragraphs[0]
        p.alignment = alinear
        run = p.add_run()
        run.text = txt
        run.font.size = Pt(t)
        run.font.bold = negrita
        run.font.name = fuente
        run.font.color.rgb = rgb(color)
        if esp:
            run._r.get_or_add_rPr().set("spc", str(esp * 100))
        n = _lineas([(txt, fuente, negrita, t, esp)], ancho - 0.25)
        if n * t * 1.17 / 72 + 0.06 > alto + 0.02:
            AVISOS.append(f"desborde en celda ({n} líneas): {txt[:60]}")

    for j, t in enumerate(encabezados):
        celda(tbl.cell(0, j), t.upper(), 10, BLANCO, True, NEGRO, esp=1, ancho=anchos[j], alto=hh)
    for i, fila in enumerate(filas, start=1):
        dest = (i - 1) in destacar
        base = NARANJA_TINTE if dest else (BLANCO if i % 2 else "F7F7F7")
        for j, val in enumerate(fila):
            col = TEXTO
            neg = dest and j == 1
            fnt = FUENTE
            if j in mono:
                col, neg, fnt = (NARANJA if dest else GRIS_MEDIO), True, MONO
            if colores_col and j in colores_col:
                col, neg = colores_col[j], True
            if j == 0 and j not in mono:
                col, neg = NEGRO, True
            al = (alinear_col or {}).get(j, PP_ALIGN.LEFT)
            celda(tbl.cell(i, j), val, tam, col, neg, base, fuente=fnt, ancho=anchos[j], alinear=al)
    if nota:
        yb = y0 + hh + hf * len(filas) + 0.22
        icono(s, icono_nota, x0, yb + 0.04, 0.32)
        texto(s, x0 + 0.5, yb, total - 0.5, 0.42, nota if isinstance(nota, list) else [nota], tam=12,
              color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)
    return s


def dato(d, etiqueta, titulo, cifra, rotulo, desc, apoyos=(), icono_nombre="chart_o", color_cifra=NARANJA,
         tam_cifra=120):
    """Dato clave: cifra grande a la izquierda y tarjetas oscuras de apoyo a la derecha."""
    s = d.contenido(etiqueta, titulo)
    icono(s, icono_nombre, M, Y0 + 0.15, 0.6)
    ancho_izq = 6.6 if apoyos else UTIL
    texto(s, M, Y0 + 0.75, ancho_izq, 1.9, cifra, tam=tam_cifra, negrita=True, color=color_cifra,
          ancla=MSO_ANCHOR.MIDDLE)
    texto(s, M, Y0 + 2.8, ancho_izq - 0.3, 0.45, rotulo, tam=20, negrita=True, color=NEGRO)
    texto(s, M, Y0 + 3.35, ancho_izq - 0.4, 1.3, desc, tam=14, color=GRIS, interlineado=1.1)
    if apoyos:
        xc = M + 7.0
        wc = UTIL - 7.0
        gap = 0.25
        hc = (Y1 - Y0 - gap * (len(apoyos) - 1)) / len(apoyos)
        for i, (c, t) in enumerate(apoyos):
            y = Y0 + i * (hc + gap)
            caja(s, xc, y, wc, hc, relleno=NEGRO)
            texto(s, xc + 0.35, y + 0.2, 2.2, hc - 0.4, c, tam=30 if len(c) <= 6 else 24, negrita=True,
                  color=NARANJA_CLARO, ancla=MSO_ANCHOR.MIDDLE)
            texto(s, xc + 2.6, y + 0.15, wc - 2.85, hc - 0.3, t, tam=12.5, color=BLANCO, ancla=MSO_ANCHOR.MIDDLE,
                  interlineado=1.05)
    return s


def cita(d, etiqueta, titulo, frase, autor, puntos=()):
    """Lámina oscura con una frase destacada de la fuente y, opcionalmente, 2-3 ideas de apoyo."""
    s = d.contenido(etiqueta, titulo, oscuro=True)
    icono(s, "quote_o", M, Y0 + 0.1, 0.6)
    alto_frase = 1.9 if puntos else 2.9
    texto(s, M + 0.95, Y0, UTIL - 0.95, alto_frase, frase, tam=24 if puntos else 26, color=BLANCO, cursiva=True,
          interlineado=1.1, ancla=MSO_ANCHOR.MIDDLE)
    texto(s, M + 0.95, Y0 + alto_frase + 0.1, UTIL - 0.95, 0.3, autor, tam=11, color=NARANJA_CLARO,
          negrita=True, espaciado=1)
    if puntos:
        n = len(puntos)
        gap = 0.28
        w = (UTIL - gap * (n - 1)) / n
        y = Y0 + alto_frase + 0.65
        h = Y1 - y
        for i, (ic, t) in enumerate(puntos):
            x = M + i * (w + gap)
            caja(s, x, y, w, h, relleno=TARJETA, borde=BORDE_OSC)
            icono(s, f"{ic}_o", x + 0.3, y + (h - 0.42) / 2, 0.42)
            texto(s, x + 0.95, y + 0.1, w - 1.15, h - 0.2, t, tam=13, color=BLANCO, ancla=MSO_ANCHOR.MIDDLE,
                  interlineado=1.05)
    return s


def checklist(d, etiqueta, titulo, fase, items, nota=None, rotulo="ENTREGABLES"):
    """Entregables de una fase: panel oscuro a la izquierda y lista de verificación a la derecha."""
    s = d.contenido(etiqueta, titulo)
    wp = 3.3
    h = Y1 - Y0
    caja(s, M, Y0, wp, h, relleno=NEGRO)
    icono(s, "clipcheck_o", M + 0.35, Y0 + 0.4, 0.6)
    texto(s, M + 0.35, Y0 + 1.25, wp - 0.6, 0.3, rotulo, tam=11, negrita=True, color=NARANJA, espaciado=2)
    texto(s, M + 0.35, Y0 + 1.6, wp - 0.6, 1.3, fase, tam=22, negrita=True, color=BLANCO, interlineado=0.95)
    if nota:
        texto(s, M + 0.35, Y0 + h - 1.55, wp - 0.6, 1.3, nota, tam=12, color=BORDE, interlineado=1.1,
              ancla=MSO_ANCHOR.BOTTOM)
    x = M + wp + 0.35
    w = UTIL - wp - 0.35
    n = len(items)
    paso = min(h / n, 0.72)
    for i, (t, desc) in enumerate(items):
        y = Y0 + i * paso
        caja(s, x, y + 0.04, w, paso - 0.08, relleno=BLANCO, borde=BORDE)
        icono(s, "check_o", x + 0.22, y + (paso - 0.34) / 2, 0.34)
        texto(s, x + 0.75, y + 0.04, w - 0.95, paso - 0.08,
              [[{"t": t, "negrita": True, "color": NEGRO}, {"t": ("  ·  " + desc) if desc else "", "color": GRIS,
                                                            "tam": 12}]],
              tam=13.5, ancla=MSO_ANCHOR.MIDDLE)
    return s


def flujo(d, etiqueta, titulo, nodos, nota=None, y=None, colores=None, subtitulo=None):
    """Cadena de nodos (círculo con ícono + rótulo + descripción) unidos por flechas.
    nodos = [(icono, rótulo, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(nodos)
    w = UTIL / n
    dc = 1.15 if n <= 5 else 0.95
    y = y if y is not None else (2.75 if nota else 2.9)
    if subtitulo:
        texto(s, M, Y0, UTIL, 0.35, subtitulo, tam=13, color=GRIS)
    for i, (ic, t, desc) in enumerate(nodos):
        cx = M + w * i + w / 2
        col = (colores or [NARANJA] * n)[i]
        icono_circulo(s, ic, cx - dc / 2, y, dc, relleno=col)
        texto(s, cx - w / 2 + 0.1, y + dc + 0.2, w - 0.2, 0.62, t, tam=14, negrita=True, color=NEGRO,
              alinear=PP_ALIGN.CENTER, interlineado=0.95)
        texto(s, cx - w / 2 + 0.12, y + dc + 0.85, w - 0.24, 1.25, desc, tam=11.5, color=GRIS,
              alinear=PP_ALIGN.CENTER, interlineado=1.05)
        if i < n - 1:
            flecha(s, cx + dc / 2 + 0.1, y + dc / 2, cx + w - dc / 2 - 0.1, y + dc / 2, color=GRIS, grosor=1.75)
    if nota:
        barra_nota(s, nota)
    return s


def pares(d, etiqueta, titulo, tit_izq, tit_der, filas, nota=None, color_izq=AZUL, color_der=NARANJA,
          icono_izq="building_w", icono_der="helmet_w"):
    """Filas causa → efecto (o antes → después): filas = [(izq, der)]."""
    s = d.contenido(etiqueta, titulo)
    wc = 5.2
    xg = M + wc
    xd = ANCHO - M - wc
    y = Y0
    for x, t, col, ic in ((M, tit_izq, color_izq, icono_izq), (xd, tit_der, color_der, icono_der)):
        caja(s, x, y, wc, 0.55, relleno=col)
        icono(s, ic, x + 0.22, y + 0.1, 0.35)
        texto(s, x + 0.75, y, wc - 0.9, 0.55, t.upper(), tam=12, negrita=True, color=BLANCO, espaciado=2,
              ancla=MSO_ANCHOR.MIDDLE)
    y_fin = (Y1 - 1.02) if nota else Y1
    paso = min((y_fin - y - 0.7) / len(filas), 0.95)
    yy = y + 0.7
    for a, b in filas:
        for x, t in ((M, a), (xd, b)):
            caja(s, x, yy, wc, paso - 0.14, relleno=BLANCO, borde=BORDE)
            texto(s, x + 0.25, yy, wc - 0.45, paso - 0.14, t, tam=13, color=NEGRO, ancla=MSO_ANCHOR.MIDDLE)
        flecha(s, xg + 0.15, yy + (paso - 0.14) / 2, xd - 0.15, yy + (paso - 0.14) / 2, color=NARANJA, grosor=2)
        yy += paso
    if nota:
        barra_nota(s, nota)
    return s


def linea_tiempo(d, etiqueta, titulo, hitos, nota=None, colores=None):
    """Línea horizontal con hitos: hitos = [(rótulo_superior, título, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(hitos)
    w = UTIL / n
    yl = 3.05
    caja(s, M, yl - 0.03, UTIL, 0.06, relleno=BORDE)
    for i, (sup, t, desc) in enumerate(hitos):
        cx = M + w * i + w / 2
        col = (colores or [NARANJA] * n)[i]
        texto(s, cx - w / 2 + 0.1, Y0 + 0.05, w - 0.2, 0.55, sup, tam=13, negrita=True, color=col,
              alinear=PP_ALIGN.CENTER, fuente=MONO, ancla=MSO_ANCHOR.BOTTOM)
        caja(s, cx - 0.2, yl - 0.2, 0.4, 0.4, relleno=col, forma=MSO_SHAPE.OVAL)
        y_c = yl + 0.45
        h_c = (Y1 - 1.02 if nota else Y1) - y_c
        caja(s, cx - w / 2 + 0.08, y_c, w - 0.16, h_c, relleno=BLANCO, borde=BORDE)
        texto(s, cx - w / 2 + 0.28, y_c + 0.2, w - 0.56, 0.62, t, tam=14, negrita=True, color=NEGRO,
              interlineado=0.95)
        texto(s, cx - w / 2 + 0.28, y_c + 0.85, w - 0.56, h_c - 1.0, desc, tam=11.5, color=GRIS, interlineado=1.05)
    if nota:
        barra_nota(s, nota)
    return s


def matriz2x2(d, etiqueta, titulo, eje_x, eje_y, cuadrantes, nota_lateral=None):
    """cuadrantes = [(código, título, descripción, color)] en orden: sup-izq, sup-der, inf-izq, inf-der."""
    s = d.contenido(etiqueta, titulo)
    x0, y0 = M + 0.9, Y0
    wq, hq = 3.55, 2.1
    gap = 0.15
    for i, (cod, t, desc, col) in enumerate(cuadrantes):
        f, c = divmod(i, 2)
        x = x0 + c * (wq + gap)
        y = y0 + f * (hq + gap)
        caja(s, x, y, wq, hq, relleno=col)
        oscuro = col in (NEGRO, AZUL, NARANJA_OSC, AZUL_CORP, NARANJA, AZUL_MEDIO, GRIS_MEDIO)
        texto(s, x + 0.3, y + 0.2, 1.0, 0.6, cod, tam=30, negrita=True, color=BLANCO if oscuro else NEGRO,
              fuente=MONO)
        texto(s, x + 0.3, y + 0.9, wq - 0.5, 0.35, t, tam=14, negrita=True, color=BLANCO if oscuro else NEGRO)
        texto(s, x + 0.3, y + 1.28, wq - 0.5, hq - 1.4, desc, tam=11.5, color=BLANCO if oscuro else TEXTO,
              interlineado=1.05)
    # ejes
    ya = y0 + 2 * hq + gap + 0.12
    flecha(s, x0, ya, x0 + 2 * wq + gap, ya, color=GRIS, grosor=1.5)
    texto(s, x0, ya + 0.08, 2 * wq + gap, 0.3, eje_x, tam=11, negrita=True, color=GRIS, alinear=PP_ALIGN.CENTER,
          espaciado=1)
    flecha(s, x0 - 0.2, y0 + 2 * hq + gap, x0 - 0.2, y0, color=GRIS, grosor=1.5)
    tb = texto(s, x0 - 0.62 - 2.15, y0 + hq - 0.15, 4.3, 0.3, eje_y, tam=11, negrita=True, color=GRIS,
               alinear=PP_ALIGN.CENTER, espaciado=1)
    tb.rotation = -90
    if nota_lateral:
        xl = x0 + 2 * wq + gap + 0.4
        wl = ANCHO - M - xl
        caja(s, xl, y0, wl, 2 * hq + gap, relleno=NEGRO)
        texto(s, xl + 0.3, y0 + 0.3, wl - 0.6, 2 * hq + gap - 0.6, nota_lateral, tam=13, color=BLANCO,
              interlineado=1.15, espacio_despues=8)
    return s


def plano(d, etiqueta, titulo, secuencia=False, nota_lateral=None, destacar=None):
    """Plano de implantación esquemático dividido en CWA; con secuencia=True dibuja el Path of Construction."""
    s = d.contenido(etiqueta, titulo)
    x0, y0, W, H = M, Y0, 7.6, 4.75
    caja(s, x0, y0, W, H, relleno=BLANCO, borde=BORDE)
    # Rack de tuberías central
    caja(s, x0 + 0.25, y0 + 2.2, W - 0.5, 0.35, relleno=AZUL_TINTE, borde=AZUL_PALIDO)
    texto(s, x0 + 2.0, y0 + 2.2, W - 2.4, 0.35, "RACK DE TUBERÍAS · CWA-05", tam=9, negrita=True, color=AZUL,
          alinear=PP_ALIGN.RIGHT, ancla=MSO_ANCHOR.MIDDLE, espaciado=1)
    areas = [  # (código, nombre, x, y, w, h)
        ("CWA-01", "Unidad de proceso", 0.25, 0.25, 2.3, 1.8),
        ("CWA-02", "Compresión", 2.7, 0.25, 2.1, 1.8),
        ("CWA-03", "Subestación", 4.95, 0.25, 2.4, 0.85),
        ("CWA-04", "Sala de control", 4.95, 1.2, 2.4, 0.85),
        ("CWA-06", "Tanques", 0.25, 2.7, 3.0, 1.8),
        ("CWA-07", "Torre de enfriamiento", 3.4, 2.7, 2.0, 1.8),
        ("CWA-08", "Servicios", 5.55, 2.7, 1.8, 1.8),
    ]
    orden = ["CWA-03", "CWA-04", "CWA-02", "CWA-01", "CWA-05", "CWA-06", "CWA-07", "CWA-08"]
    centros = {"CWA-05": (x0 + 1.4, y0 + 2.375)}
    for cod, nom, ax, ay, aw, ah in areas:
        dest = destacar == cod
        caja(s, x0 + ax, y0 + ay, aw, ah, relleno=NARANJA_TINTE if dest else FONDO,
             borde=NARANJA if dest else BORDE)
        texto(s, x0 + ax + 0.12, y0 + ay + 0.08, aw - 0.2, 0.25, cod, tam=10, negrita=True, fuente=MONO,
              color=NARANJA_OSC if dest else AZUL)
        texto(s, x0 + ax + 0.12, y0 + ay + 0.33, aw - 0.2, 0.3, nom, tam=10, color=GRIS)
        centros[cod] = (x0 + ax + aw - 0.4, y0 + ay + ah - 0.24)
    if secuencia:
        for k, cod in enumerate(orden):
            cx, cy = centros[cod]
            numero_circulo(s, k + 1, cx - 0.2, cy - 0.2, 0.4, tam=12)
        for a, b in zip(orden, orden[1:]):
            (ax, ay), (bx, by) = centros[a], centros[b]
            dx, dy = bx - ax, by - ay
            dist = math.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist
            flecha(s, ax + ux * 0.25, ay + uy * 0.25, bx - ux * 0.27, by - uy * 0.27, color=NARANJA, grosor=1.5)
    if nota_lateral:
        xl = x0 + W + 0.35
        wl = ANCHO - M - xl
        items = nota_lateral
        paso = H / len(items)
        for i, (ic, t, desc) in enumerate(items):
            y = y0 + i * paso
            caja(s, xl, y, wl, paso - 0.15, relleno=BLANCO, borde=BORDE)
            icono(s, f"{ic}_o", xl + 0.25, y + 0.22, 0.4)
            texto(s, xl + 0.85, y + 0.12, wl - 1.05, paso - 0.4,
                  [[{"t": t, "negrita": True, "color": NEGRO, "tam": 13.5}], [{"t": desc, "color": GRIS}]],
                  tam=11.5, interlineado=1.05, espacio_despues=2, ancla=MSO_ANCHOR.MIDDLE)
    return s


def ciclo(d, etiqueta, titulo, pasos, centro, nota_lateral=None):
    """Pasos dispuestos en círculo alrededor de un rótulo central: pasos = [(icono, título, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(pasos)
    if nota_lateral:
        cx, cy, rx, ry, wl = 4.6, Y0 + 2.35, 1.6, 1.75, 1.9
    else:
        cx, cy, rx, ry, wl = ANCHO / 2, Y0 + 2.35, 2.75, 1.75, 2.2
    caja(s, cx - 0.95, cy - 0.6, 1.9, 1.2, relleno=NEGRO, forma=MSO_SHAPE.OVAL)
    texto(s, cx - 0.9, cy - 0.5, 1.8, 1.0, centro, tam=13, negrita=True, color=BLANCO, alinear=PP_ALIGN.CENTER,
          ancla=MSO_ANCHOR.MIDDLE)
    pts = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        flecha(s, ax + ux * 0.55, ay + uy * 0.55, bx - ux * 0.6, by - uy * 0.6, color=NARANJA, grosor=1.75)
    for i, ((px, py), (ic, t, desc)) in enumerate(zip(pts, pasos)):
        icono_circulo(s, ic, px - 0.4, py - 0.4, 0.8)
        # Rótulo fuera del círculo
        derecha = px > cx + 0.3
        izquierda = px < cx - 0.3
        if derecha:
            tx, al = px + 0.5, PP_ALIGN.LEFT
        elif izquierda:
            tx, al = px - 0.5 - wl, PP_ALIGN.RIGHT
        else:
            tx, al = px + 0.5, PP_ALIGN.LEFT
        texto(s, tx, py - 0.42, wl, 0.9, [[{"t": t, "negrita": True, "color": NEGRO, "tam": 13}],
                                          [{"t": desc, "color": GRIS}]], tam=11, ancla=MSO_ANCHOR.MIDDLE,
              alinear=al, interlineado=1.0)
    if nota_lateral:
        xl = M + 8.3
        wl2 = ANCHO - M - xl
        caja(s, xl, Y0, wl2, Y1 - Y0, relleno=NEGRO)
        texto(s, xl + 0.3, Y0 + 0.3, wl2 - 0.6, Y1 - Y0 - 0.6, nota_lateral, tam=13, color=BLANCO,
              interlineado=1.15, espacio_despues=8)
    return s


def embudo(d, etiqueta, titulo, etapas, nota=None):
    """Etapas apiladas de ancho decreciente: etapas = [(rótulo, semanas, descripción)]."""
    s = d.contenido(etiqueta, titulo)
    n = len(etapas)
    y_fin = (Y1 - 1.02) if nota else Y1
    h = (y_fin - Y0 - 0.12 * (n - 1)) / n
    wmax, wmin = 8.2, 4.2
    cx = M + wmax / 2
    colores = [AZUL, AZUL_CORP, AZUL_MEDIO, NARANJA_OSC, NARANJA][-n:] if n <= 5 else [NARANJA] * n
    for i, (rot, sem, desc) in enumerate(etapas):
        w = wmax - (wmax - wmin) * i / max(n - 1, 1)
        y = Y0 + i * (h + 0.12)
        caja(s, cx - w / 2, y, w, h, relleno=colores[i])
        texto(s, cx - w / 2 + 0.25, y, w - 0.5, h, rot, tam=14, negrita=True, color=BLANCO, alinear=PP_ALIGN.CENTER,
              ancla=MSO_ANCHOR.MIDDLE)
        xl = M + wmax + 0.35
        texto(s, xl, y, 1.2, h, sem, tam=13, negrita=True, color=colores[i], fuente=MONO, ancla=MSO_ANCHOR.MIDDLE)
        texto(s, xl + 1.25, y, ANCHO - M - xl - 1.25, h, desc, tam=11.5, color=GRIS, ancla=MSO_ANCHOR.MIDDLE,
              interlineado=1.05)
    if nota:
        barra_nota(s, nota)
    return s


def portada(d, kicker, titulo, subtitulo, bajada, pie):
    s = d.nueva(NEGRO)
    texto(s, M, 1.25, 7, 0.3, kicker, tam=12, color=NARANJA, negrita=True, espaciado=3)
    texto(s, M, 1.75, 7.2, 1.0, titulo, tam=54, color=BLANCO, negrita=True, nombre="Título")
    texto(s, M, 2.85, 6.9, 1.1, subtitulo, tam=24, color=NARANJA_CLARO, interlineado=1.05)
    texto(s, M, 4.35, 6.6, 0.8, bajada, tam=15, interlineado=1.15)
    texto(s, M, 6.35, 7, 0.3, pie, tam=11, color=GRIS)
    x0, w = 8.35, 4.38
    niveles = [
        ("CWA", "Construction Work Area", "Área del terreno", NARANJA_OSC, "map_w"),
        ("CWP", "Construction Work Package", "Una disciplina del área", NARANJA, "helmet_w"),
        ("IWP", "Installation Work Package", "Una cuadrilla, una semana", NARANJA_CLARO, "clip_w"),
    ]
    y = 1.25
    for sigla, nombre, desc, color, ic in niveles:
        caja(s, x0, y, w, 1.05, relleno=color)
        icono(s, ic, x0 + 0.3, y + 0.3, 0.45)
        texto(s, x0 + 1.0, y + 0.18, 3.2, 0.4, sigla, tam=22, color=BLANCO, negrita=True, fuente=MONO)
        texto(s, x0 + 1.0, y + 0.6, 3.2, 0.3, nombre, tam=11, color=BLANCO)
        caja(s, x0, y + 1.05, w, 0.42, relleno=TARJETA)
        texto(s, x0 + 0.3, y + 1.05, w - 0.5, 0.42, desc, tam=11, color=BORDE, ancla=MSO_ANCHOR.MIDDLE)
        y += 1.72
    return s
