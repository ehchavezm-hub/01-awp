"""Genera las plantillas y procedimientos Word del kit de implementación AWP
en implementacion/plantillas/.

Uso:
    python implementacion/scripts/generar_word.py
"""

import re
import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datos_proyecto as dp  # noqa: E402
import estilo_word as ew  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "implementacion" / "plantillas"
GRIS_TEXTO = RGBColor(0x80, 0x80, 0x80)
AZUL_INSTR = RGBColor(0x2F, 0x55, 0x97)
C = "‹completar›"
FASES_CHECK = "☐ Fase 1   ☐ Fase 2   ☐ Fase 3"


# --------------------------------------------------------------------------
# Renderizador de secciones
# --------------------------------------------------------------------------

class Documento:
    """Construye un documento a partir de una lista de bloques."""

    def __init__(self, titulo, codigo, subtitulo, tipo="formulario", horizontal=False):
        self.titulo = titulo
        self.codigo = codigo
        self.subtitulo = subtitulo
        self.tipo = tipo
        self.doc = ew.nuevo_documento(horizontal)
        self.ancho = 25.7 if horizontal else 17.0
        self.n = [0, 0, 0]
        self.fig = 0

    # ---- encabezados
    def portada(self, bloques, datos_extra=()):
        ew.portada(self.doc, self.titulo, self.subtitulo, [
            ("Proyecto", dp.PROYECTO),
            ("Documento", f"{self.codigo} – {self.titulo}"),
            ("Revisión", "0 – Emitido para uso"),
            ("Fecha", ew.fecha_hoy()),
            *datos_extra,
            ("Elaborado por", "AWP Champion"),
            ("Aprobado por", "Gerente de Proyecto"),
        ])
        previo, n1, n2 = [], 0, 0
        for b in bloques:
            if b[0] == "h1":
                n1 += 1
                n2 = 0
                previo.append((1, f"{n1}.  {b[1]}"))
            elif b[0] == "h2":
                n2 += 1
                previo.append((2, f"{n1}.{n2}  {b[1]}"))
        ew.indice(self.doc, previo)

    def cabecera_formulario(self):
        p = self.doc.add_paragraph()
        r = p.add_run(ew.KIT.upper())
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = GRIS_TEXTO
        p.paragraph_format.space_after = Pt(0)
        p = self.doc.add_paragraph()
        r = p.add_run(self.titulo)
        r.font.size = Pt(20)
        r.font.bold = True
        r.font.color.rgb = ew.AZUL
        ew.linea_inferior(p)
        p = self.doc.add_paragraph()
        r = p.add_run(self.subtitulo)
        r.italic = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
        self.campos([("Proyecto", dp.PROYECTO), ("Código del formato", self.codigo),
                     ("Revisión del formato", "0"), ("Fecha de emisión", ew.fecha_hoy())], 4, valores_reales=True)

    # ---- elementos
    def h(self, nivel, texto):
        if nivel == 1:
            self.n = [self.n[0] + 1, 0, 0]
            num = f"{self.n[0]}."
        elif nivel == 2:
            self.n = [self.n[0], self.n[1] + 1, 0]
            num = f"{self.n[0]}.{self.n[1]}"
        else:
            self.n[2] += 1
            num = f"{self.n[0]}.{self.n[1]}.{self.n[2]}"
        self.doc.add_heading(f"{num}  {texto}", level=nivel)

    def p(self, texto):
        par = self.doc.add_paragraph()
        self._texto(par, texto)

    def _texto(self, par, texto, tam=None):
        for trozo in re.split(r"(\*\*[^*]+\*\*)", texto):
            if not trozo:
                continue
            negrita = trozo.startswith("**")
            r = par.add_run(trozo.strip("*") if negrita else trozo)
            r.bold = negrita
            if tam:
                r.font.size = Pt(tam)

    def viñetas(self, items, numeradas=False):
        for it in items:
            par = self.doc.add_paragraph(style="List Number" if numeradas else "List Bullet")
            self._texto(par, it)

    def instr(self, texto):
        par = self.doc.add_paragraph()
        r = par.add_run("Instrucción: ")
        r.bold = True
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = AZUL_INSTR
        r = par.add_run(texto)
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = AZUL_INSTR

    def campos(self, pares, columnas=2, valores_reales=False):
        """Tabla de campos etiqueta/valor (2 o 4 columnas)."""
        filas = [pares[i:i + columnas // 2] for i in range(0, len(pares), columnas // 2)]
        tabla = self.doc.add_table(rows=0, cols=columnas)
        ew.bordes_tabla(tabla)
        ew.margenes_celda(tabla)
        for grupo in filas:
            celdas = tabla.add_row().cells
            ew.no_dividir_fila(tabla.rows[-1])
            for k, (etq, val) in enumerate(grupo):
                ce, cv = celdas[2 * k], celdas[2 * k + 1]
                ce.text = ""
                r = ce.paragraphs[0].add_run(etq)
                r.bold = True
                r.font.size = Pt(9)
                ew.sombrear(ce, ew.AZUL_CLARO_HEX)
                cv.text = ""
                r = cv.paragraphs[0].add_run(val if val is not None else C)
                r.font.size = Pt(9)
                if not valores_reales and (val is None or val == C or val.startswith("‹") or "☐" in val):
                    r.font.color.rgb = GRIS_TEXTO if val is None or val.startswith("‹") else RGBColor(0, 0, 0)
                for c in (ce, cv):
                    c.paragraphs[0].paragraph_format.space_after = Pt(0)
        if columnas == 2:
            ew.anchos(tabla, [self.ancho * 0.32, self.ancho * 0.68])
        else:
            a = self.ancho
            ew.anchos(tabla, [a * 0.18, a * 0.32, a * 0.18, a * 0.32])
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def tabla(self, encabezados, filas, anchos_rel=None, vacias=0, tam=9):
        filas = [list(f) for f in filas] + [[""] * len(encabezados) for _ in range(vacias)]
        cms = None
        if anchos_rel:
            s = sum(anchos_rel)
            cms = [self.ancho * a / s for a in anchos_rel]
        valores = []
        for fila in filas:
            conv = []
            for v in fila:
                v = str(v)
                if v.startswith("‹"):
                    conv.append(lambda par, v=v: _gris(par, v, tam))
                else:
                    conv.append(lambda par, v=v, s=self: s._texto(par, v, tam))
            valores.append(conv)
        ew.tabla_datos(self.doc, encabezados, valores, cms, tam)

    def firmas(self, roles, titulo_col="Rol"):
        self.tabla([titulo_col, "Nombre", "Firma", "Fecha"], [[r, "", "", ""] for r in roles], [4, 4, 3, 2])

    def nota(self, titulo, texto):
        ew.recuadro(self.doc, titulo, texto)

    def figura(self, codigo_mermaid, leyenda):
        from generar_plan_word import imagen_diagrama
        import struct

        png = imagen_diagrama(codigo_mermaid, False)
        if not png:
            return
        ancho, alto = struct.unpack(">II", png.read_bytes()[16:24])
        ancho_cm = min(self.ancho - 1, 16.0)
        if alto / ancho * ancho_cm > 18:
            ancho_cm = 18 * ancho / alto
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(str(png), width=Cm(ancho_cm))
        self.fig += 1
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = par.add_run(f"Figura {self.fig}. {leyenda}")
        r.italic = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    def salto(self):
        ew.salto_pagina(self.doc)

    # ---- render
    def render(self, bloques):
        for b in bloques:
            tipo, args = b[0], b[1:]
            if tipo == "h1":
                self.h(1, *args)
            elif tipo == "h2":
                self.h(2, *args)
            elif tipo == "p":
                self.p(*args)
            elif tipo == "ul":
                self.viñetas(*args)
            elif tipo == "ol":
                self.viñetas(args[0], True)
            elif tipo == "instr":
                self.instr(*args)
            elif tipo == "campos":
                self.campos(*args)
            elif tipo == "tabla":
                self.tabla(*args)
            elif tipo == "firmas":
                self.firmas(*args)
            elif tipo == "nota":
                self.nota(*args)
            elif tipo == "figura":
                self.figura(*args)
            elif tipo == "salto":
                self.salto()

    def guardar(self, nombre, bloques):
        if self.tipo == "documento":
            self.portada(bloques)
        else:
            self.cabecera_formulario()
        self.render(bloques)
        _reiniciar_listas(self.doc)
        ew.encabezado_pie(self.doc, self.titulo, f"{self.codigo} Rev. 0")
        if self.tipo != "documento":
            for sec in self.doc.sections:
                sec.different_first_page_header_footer = False
        self.doc.core_properties.title = self.titulo
        self.doc.core_properties.subject = dp.PROYECTO
        self.doc.core_properties.author = "Kit de implementación AWP"
        self.doc.core_properties.language = "es-ES"
        self.doc.save(SALIDA / nombre)
        print("Generado:", nombre)


def _gris(par, texto, tam):
    r = par.add_run(texto)
    r.font.color.rgb = GRIS_TEXTO
    r.font.size = Pt(tam)


def _reiniciar_listas(doc):
    from generar_plan_word import reiniciar_numeracion
    reiniciar_numeracion(doc)


def mermaid_de(pagina, indice):
    texto = (RAIZ / "docs" / "implementacion" / pagina).read_text(encoding="utf-8")
    return re.findall(r"```mermaid\n(.*?)\n```", texto, re.S)[indice]


ROLES_FIRMA_IWP = ["Planificador de frente de trabajo", "Superintendente / capataz general", "Líder de HSE", "Líder de calidad (QA/QC)", "Líder de WFP (aprueba la liberación)"]


# ==========================================================================
# Plantilla de IWP
# ==========================================================================

def plantilla_iwp():
    d = Documento("Paquete de trabajo de instalación (IWP)", "PT-AWP-FOR-IWP",
                  "Plantilla para preparar, liberar y cerrar un IWP: una cuadrilla, un capataz, alrededor de una semana (300 a 600 HH).")
    bloques = [
        ("instr", "Complete todos los campos en gris. Borre las instrucciones en azul antes de emitir el IWP. Un IWP solo se entrega a campo cuando la sección 10 (liberación) está firmada y todas las restricciones de la sección 9 están liberadas o canceladas."),
        ("h1", "Identificación"),
        ("campos", [("Código del IWP", "‹IWP-2.01-EST-01-001›"), ("Revisión del IWP", "‹0›"),
                    ("CWP", "‹CWP-2.01-EST-01›"), ("CWA", "‹CWA-2.01›"),
                    ("Fase del proyecto", FASES_CHECK), ("Disciplina", "‹EST›"),
                    ("Sistema", "‹Estructura bloque A›"), ("Área / ubicación", "‹Ejes A1–A4, nivel 1›"),
                    ("Planificador", C), ("Superintendente", C),
                    ("Capataz", C), ("Personas en la cuadrilla", C),
                    ("Inicio plan", "‹dd/mm/aaaa›"), ("Fin plan", "‹dd/mm/aaaa›"),
                    ("HH estimadas", "‹420›"), ("Actividad nivel 5", "‹ID en el cronograma›")], 4),
        ("h1", "Alcance del trabajo"),
        ("instr", "Describa qué se hace y qué NO se hace en este IWP, con límites físicos claros (ejes, niveles, líneas, equipos)."),
        ("campos", [("Descripción del alcance", C), ("Límites", C), ("Exclusiones", C)]),
        ("tabla", ["Ítem", "Descripción", "Unidad", "Cantidad", "HH estimadas"], [["1", C, "", "", ""]], [1, 6, 1.5, 1.5, 1.5], 4),
        ("h1", "Documentos de referencia"),
        ("instr", "Solo documentos emitidos para construcción (IFC) y vigentes. Adjunte copia o vista 3D en el anexo."),
        ("tabla", ["N.°", "Código del documento", "Título", "Revisión", "Estado"], [["1", C, "", "", "IFC"]], [1, 4, 6, 1.5, 1.5], 5),
        ("h1", "Secuencia de trabajo"),
        ("tabla", ["Paso", "Actividad", "Recursos / equipos", "HH", "Punto de inspección"], [["1", C, "", "", ""]], [1, 6, 3.5, 1.2, 3], 6),
        ("h1", "Materiales"),
        ("instr", "Todos los materiales deben estar recibidos, inspeccionados y reservados para este IWP antes de la liberación."),
        ("tabla", ["Código / tag", "Descripción", "Unidad", "Cantidad", "PWP", "Reserva / ubicación", "Estado"], [[C, "", "", "", "‹PWP-2.01-EST-01›", "", "‹Reservado›"]], [2.5, 4.5, 1.2, 1.5, 2.8, 2.5, 1.8], 6),
        ("h1", "Equipos, herramientas y andamios"),
        ("tabla", ["Recurso", "Descripción / capacidad", "Fecha requerida", "Confirmado por", "Estado"], [["‹Grúa›", "", "", "", "☐ Confirmado"], ["‹Andamio›", "", "", "", "☐ Montado e inspeccionado"]], [2.5, 5, 2.5, 3, 3], 3),
        ("h1", "Seguridad (HSE)"),
        ("campos", [("JHA / análisis de riesgos", "‹Código y revisión›"),
                    ("Permisos requeridos", "☐ Trabajo en altura   ☐ Excavación   ☐ Trabajo en caliente   ☐ Izaje crítico   ☐ Espacio confinado   ☐ Aislamiento de energía   ☐ Otro: ______"),
                    ("Riesgos principales y controles", C), ("EPP especial", C)]),
        ("h1", "Calidad"),
        ("campos", [("ITP aplicable", "‹Código›"), ("Procedimientos de trabajo", C),
                    ("Puntos de espera / inspección", C), ("Registros a entregar", "‹Protocolos, ITR›")]),
        ("h1", "Restricciones del IWP"),
        ("instr", "Copie las restricciones del Registro_Restricciones.xlsx. Para liberar, todas deben estar «Liberada» o «Cancelada»."),
        ("tabla", ["ID", "Tipo", "Descripción", "Responsable (rol)", "Fecha requerida", "Estado"], [["‹R-0000›", "", "", "", "", ""]], [1.6, 2.4, 5.5, 3, 2, 2], 5),
        ("h1", "Liberación del IWP"),
        ("campos", [("Checklist de liberación", "☐ Completo (Checklist_Liberacion_IWP.xlsx, resultado «LIBERAR»)"),
                    ("Fecha de liberación", "‹dd/mm/aaaa›"), ("Ingreso al backlog", "‹dd/mm/aaaa›"),
                    ("Semana de ejecución (lookahead)", "‹Semana›")]),
        ("firmas", ROLES_FIRMA_IWP),
        ("h1", "Cierre del IWP"),
        ("instr", "Complete al terminar el trabajo o si el IWP se devuelve de campo sin terminar."),
        ("campos", [("Resultado", "☐ Completado   ☐ Completado parcialmente   ☐ Devuelto de campo"),
                    ("Fecha de término real", "‹dd/mm/aaaa›"), ("HH reales", C), ("% avance final", C),
                    ("Causa de desviación / devolución", "‹Use las causas del lookahead: materiales, ingeniería, permisos…›"),
                    ("Trabajo pendiente (nuevo IWP)", C),
                    ("Registros de calidad cerrados", "☐ Sí   ☐ No"),
                    ("Lección aprendida", "‹Registrar en Registro_Lecciones_Aprendidas.xlsx si aplica›")]),
        ("firmas", ["Capataz", "Superintendente / capataz general", "Líder de calidad (QA/QC)", "Planificador de frente de trabajo (recibe y cierra)"]),
        ("h1", "Anexos"),
        ("ul", ["Anexo A: planos IFC y vistas 3D del alcance.", "Anexo B: lista de materiales reservados (vale de almacén).",
                "Anexo C: JHA y permisos.", "Anexo D: ITP y formatos de inspección.", "Anexo E: checklist de liberación firmado."]),
    ]
    d.guardar("Plantilla_IWP.docx", bloques)


# ==========================================================================
# Plantilla de CWP
# ==========================================================================

def plantilla_cwp():
    d = Documento("Paquete de trabajo de construcción (CWP)", "PT-AWP-FOR-CWP",
                  "Plantilla para definir y emitir un CWP: una disciplina dentro de una CWA, menos de 40 000 HH, una actividad de nivel 3.")
    bloques = [
        ("instr", "El CWP lo prepara construcción con los aportes de ingeniería (EWP) y procura (PWP). Se emite 10 semanas antes del inicio en la Fase 2 (8 semanas en las Fases 1 y 3), para que los planificadores lo dividan en IWP."),
        ("h1", "Identificación"),
        ("campos", [("Código del CWP", "‹CWP-2.01-EST-01›"), ("Revisión", "‹0›"),
                    ("CWA", "‹CWA-2.01›"), ("Fase del proyecto", FASES_CHECK),
                    ("Disciplina", "‹EST›"), ("Contratista / subcontratista", C),
                    ("EWP asociado", "‹EWP-2.01-EST-01›"), ("PWP asociado", "‹PWP-2.01-EST-01›"),
                    ("Responsable (rol)", "Gerente de Construcción"), ("Actividad nivel 3", "‹ID en el cronograma›"),
                    ("Inicio plan", "‹dd/mm/aaaa›"), ("Fin plan", "‹dd/mm/aaaa›"),
                    ("HH estimadas", "‹< 40 000›"), ("Posición en el PoC", "‹Secuencia N.°›")], 4),
        ("h1", "Alcance y límites"),
        ("campos", [("Descripción del alcance", C), ("Límites físicos", "‹Ejes, niveles, sistemas; adjuntar plano de límites›"),
                    ("Exclusiones", C), ("Supuestos", C)]),
        ("h1", "Entregables de ingeniería (EWP)"),
        ("tabla", ["Documento", "Título", "Revisión", "Estado", "Fecha IFC plan", "Fecha IFC real"], [[C, "", "", "‹IFC›", "", ""]], [3, 5, 1.5, 1.5, 2, 2], 5),
        ("h1", "Materiales y equipos (PWP)"),
        ("tabla", ["Ítem / tag", "Descripción", "Tipo", "Cantidad", "Fecha RAS", "Estado"], [[C, "", "‹Granel / tag / equipo›", "", "", ""]], [2.5, 5, 2.5, 1.5, 2, 2], 5),
        ("h1", "Estimación de cantidades y horas-hombre"),
        ("tabla", ["Partida", "Descripción", "Unidad", "Cantidad", "Rendimiento (HH/u)", "HH"], [[C, "", "", "", "", ""]], [1.5, 6, 1.5, 1.5, 2, 1.5], 5),
        ("h1", "Secuencia y división en IWP"),
        ("instr", "Lista preliminar de IWP. El planificador la detalla dentro de la ventana de planificación de la fase."),
        ("tabla", ["IWP", "Alcance", "HH", "Inicio plan", "Sistema", "Predecesor"], [["‹IWP-2.01-EST-01-001›", "", "", "", "", ""]], [3.5, 5, 1.2, 2, 2.5, 2.5], 6),
        ("h1", "Estrategia de ejecución"),
        ("campos", [("Recursos y cuadrillas", C), ("Equipos mayores (grúas, izajes)", C), ("Andamios y accesos", C),
                    ("Logística y acopio", C), ("Prefabricación / modularización", C), ("Turnos y horarios", C)]),
        ("h1", "Seguridad (HSE)"),
        ("campos", [("Riesgos principales", C), ("Permisos típicos", C), ("Planes específicos (izaje, excavación)", C)]),
        ("h1", "Calidad"),
        ("campos", [("ITP", "‹Código›"), ("Ensayos y pruebas", C), ("Registros de entrega", C)]),
        ("h1", "Restricciones del CWP"),
        ("tabla", ["ID", "Tipo", "Descripción", "Responsable (rol)", "Fecha requerida", "Estado"], [["‹R-0000›", "", "", "", "", ""]], [1.6, 2.4, 5.5, 3, 2, 2], 4),
        ("h1", "Interfaces"),
        ("instr", "Incluya las interfaces con otros CWP y con otras fases del proyecto (entregas de área, conexiones, recursos compartidos)."),
        ("tabla", ["Interfaz con", "Descripción", "Fase", "Fecha requerida", "Responsable"], [["‹CWP / fase›", "", "", "", ""]], [3, 6, 1.5, 2, 3], 3),
        ("h1", "Comisionamiento"),
        ("campos", [("Sistemas / subsistemas", C), ("Requisitos de entrega (SWP / TOP)", C)]),
        ("h1", "Aprobaciones"),
        ("firmas", ["Gerente de Construcción (aprueba)", "Líder de WFP", "Líder de Ingeniería", "Líder de Procura", "Líder de HSE", "Líder de calidad (QA/QC)"]),
    ]
    d.guardar("Plantilla_CWP.docx", bloques)


# ==========================================================================
# Plantilla de EWP
# ==========================================================================

def plantilla_ewp():
    d = Documento("Paquete de trabajo de ingeniería (EWP)", "PT-AWP-FOR-EWP",
                  "Plantilla para planificar y emitir un EWP completo, en la secuencia del Path of Construction, para un único CWP.")
    bloques = [
        ("instr", "La fecha requerida del EWP se calcula hacia atrás desde el inicio del CWP (Path_of_Construction.xlsx). Un EWP está completo cuando incluye todo lo que construcción y procura necesitan para su CWP."),
        ("h1", "Identificación"),
        ("campos", [("Código del EWP", "‹EWP-2.01-EST-01›"), ("Revisión", "‹0›"),
                    ("CWP que alimenta", "‹CWP-2.01-EST-01›"), ("CWA", "‹CWA-2.01›"),
                    ("Fase del proyecto", FASES_CHECK), ("Disciplina", "‹EST›"),
                    ("Líder de disciplina", C), ("PWP asociado", "‹PWP-2.01-EST-01›"),
                    ("Fecha requerida IFC (PoC)", "‹dd/mm/aaaa›"), ("Fecha IFC real", "‹dd/mm/aaaa›"),
                    ("HH de ingeniería", C), ("Inicio del CWP", "‹dd/mm/aaaa›")], 4),
        ("h1", "Alcance del EWP"),
        ("campos", [("Descripción", C), ("Límites (coinciden con el CWP)", C), ("Datos de entrada requeridos", "‹Datos de proveedor, estudios, geotecnia…›")]),
        ("h1", "Lista de entregables"),
        ("tabla", ["Código", "Título", "Tipo", "Revisión", "Fecha plan", "Fecha real", "Estado"],
         [[C, "", "‹Plano / especificación / MTO / hoja de datos›", "", "", "", "‹IFR / IFC›"]], [2.5, 4.5, 3, 1.3, 1.8, 1.8, 1.5], 7),
        ("h1", "Lista de materiales (MTO)"),
        ("campos", [("MTO emitido", "☐ Sí   ☐ No   Fecha: ‹dd/mm/aaaa›"), ("Transferido a procura (PWP)", "☐ Sí   ☐ No")]),
        ("h1", "Revisión de constructabilidad"),
        ("tabla", ["N.°", "Comentario de construcción", "Respuesta de ingeniería", "Estado"], [["1", C, "", ""]], [1, 6, 6, 2], 3),
        ("h1", "RFI relacionadas"),
        ("tabla", ["RFI", "Asunto", "Fecha de respuesta requerida", "Estado", "ID de restricción"], [[C, "", "", "", "‹R-0000›"]], [2, 6, 3, 2, 2], 3),
        ("h1", "Emisión y aprobación"),
        ("campos", [("Criterio de EWP completo", "☐ Planos IFC   ☐ Especificaciones   ☐ MTO   ☐ Datos de proveedor   ☐ Modelo 3D actualizado con atributos AWP")]),
        ("firmas", ["Líder de disciplina", "Líder de Ingeniería (aprueba)", "Gerente de Construcción (recibe)"]),
    ]
    d.guardar("Plantilla_EWP.docx", bloques)


# ==========================================================================
# Procedimiento de gestión de restricciones
# ==========================================================================

def procedimiento_restricciones():
    d = Documento("Procedimiento de gestión de restricciones", "PT-AWP-PRO-001",
                  "Identificación, registro, seguimiento, escalamiento y liberación de restricciones, y liberación de IWP libres de restricciones.",
                  tipo="documento")
    tipos = [
        ("Ingeniería", "Plano no emitido IFC, RFI abierta, revisión pendiente", "Líder de Ingeniería", "4 semanas"),
        ("Materiales", "Material no recibido, no conforme o no reservado", "Líder de Procura / Gestor de materiales", "4 semanas"),
        ("Equipos de construcción", "Grúa, plataforma o equipo pesado no disponible", "Gerente de Construcción", "3 semanas"),
        ("Permisos", "Permiso de trabajo, excavación, trabajo en caliente, licencia", "Líder de HSE", "3 semanas"),
        ("Mano de obra", "Cuadrilla o especialista no disponible, acreditaciones", "Superintendente / capataz general", "2 semanas"),
        ("Andamios", "Andamio no solicitado, no montado o no inspeccionado", "Superintendente / capataz general", "3 semanas"),
        ("Acceso / interferencias", "Frente ocupado por otra cuadrilla, vía cerrada", "Gerente de Construcción", "2 semanas"),
        ("Trabajos predecesores", "Trabajo previo no terminado o no aceptado", "Superintendente / capataz general", "1 semana"),
        ("Calidad", "ITP no aprobado, procedimiento no calificado", "Líder de calidad (QA/QC)", "2 semanas"),
        ("HSE", "JHA no aprobado, plan de izaje pendiente", "Líder de HSE", "2 semanas"),
        ("Documentación del proveedor", "Planos certificados o manuales pendientes", "Líder de Procura", "4 semanas"),
        ("Interfaz entre fases", "Entrega de área o conexión de otra fase pendiente", "AWP Champion", "6 semanas"),
    ]
    bloques = [
        ("h1", "Propósito"),
        ("p", "Establecer cómo se identifican, registran, gestionan y liberan las restricciones de los paquetes de trabajo del proyecto, para que **ningún IWP se entregue a campo con restricciones abiertas** (regla de oro de Workface Planning) y para que las cuadrillas trabajen con todo lo necesario disponible."),
        ("h1", "Alcance"),
        ("p", "Aplica a todas las fases del proyecto (Fase 1, Fase 2 y Fase 3), a todos los CWP e IWP y a todos los participantes: cliente, contratista principal, proveedores y subcontratistas. Cubre desde que un IWP entra en la ventana de planificación hasta su cierre."),
        ("h1", "Referencias"),
        ("ul", ["Plan de implementación de AWP (PT-AWP-PLN-001), secciones «Restricciones y liberación de IWP» y «Organización y roles».",
                "Procedimiento 3.0 Workface Planning (Insight-AWP, 2017): backlog, look-ahead de tres semanas y Pack Track.",
                "AWP Education Framework v1.0 (CII, 2020): gestión de restricciones y programa típico de restricciones.",
                "Plantillas: Registro_Restricciones.xlsx, Programa_Liberacion_IWP.xlsx, Checklist_Liberacion_IWP.xlsx, Lookahead_3_Semanas.xlsx y Plantilla_IWP.docx."]),
        ("h1", "Definiciones"),
        ("tabla", ["Término", "Definición"], [
            ["Restricción", "Cualquier información, material, equipo, permiso, acceso u otro factor que impida o retrase la ejecución segura y completa de un trabajo."],
            ["Restricción vencida", "Restricción no liberada ni cancelada cuya fecha requerida ya pasó."],
            ["Fecha requerida", "Fecha límite para liberar la restricción sin afectar la liberación del IWP."],
            ["IWP liberado", "IWP sin restricciones abiertas, con checklist de liberación firmado, que ingresa al backlog."],
            ["Backlog", "Conjunto de IWP liberados y listos para ejecutar (meta de 2 a 4 semanas de trabajo)."],
            ["Ventana de planificación", "Periodo previo a la ejecución en que el IWP se prepara y se levantan sus restricciones (8 a 12 semanas según la fase)."],
            ["Fase del proyecto", "Fase 1, Fase 2 o Fase 3 del proyecto tipo."],
            ["Etapa del ciclo de vida", "Planificación temprana (FEL), ingeniería, procura, construcción o comisionamiento."],
        ], [3, 12]),
        ("h1", "Responsabilidades"),
        ("tabla", ["Rol", "Responsabilidad en este procedimiento"], [
            ["Planificador de frente de trabajo", "Identifica y registra las restricciones de sus IWP; propone fecha requerida; prepara el checklist de liberación."],
            ["Líder de WFP", "Dirige la reunión semanal de restricciones; asigna responsables; escala; aprueba la liberación de IWP; consolida KPI."],
            ["Responsable de la restricción", "Levanta la restricción asignada antes de la fecha requerida y aporta la evidencia."],
            ["Gerente de Construcción", "Prioriza las restricciones críticas; resuelve conflictos de recursos; recibe el primer escalamiento."],
            ["Gerente de Proyecto", "Resuelve las restricciones escaladas que afectan al lookahead o a la ruta crítica."],
            ["AWP Champion", "Vela por el cumplimiento del procedimiento; gestiona las restricciones de interfaz entre fases; audita."],
            ["Superintendente", "Selecciona del backlog solo IWP liberados; informa restricciones nuevas detectadas en campo."],
        ], [4, 11]),
        ("h1", "Tipos de restricción"),
        ("p", "El registro usa una lista única de tipos para todas las fases. La anticipación indicada es el plazo mínimo recomendado entre la identificación y la fecha requerida."),
        ("tabla", ["Tipo", "Ejemplos", "Responsable habitual", "Anticipación mínima"], [list(t) for t in tipos], [3, 6, 4, 2]),
        ("nota", "Restricciones por defecto", "Todo IWP nuevo se registra con estas restricciones por defecto hasta verificarlas: planos IFC, materiales, permisos, andamios (si hay trabajo en altura), JHA e ITP. Esta regla incorpora la lección LA-03 de la Fase 1."),
        ("h1", "Procedimiento"),
        ("h2", "Identificación"),
        ("ol", ["Cuando un IWP entra en la ventana de planificación, el planificador revisa su alcance con planos, modelo 3D, estado de materiales, recursos y trabajos predecesores.",
                "Identifica toda condición que falte para ejecutar el IWP, incluidas las restricciones por defecto.",
                "Las restricciones detectadas en campo, en auditorías o en IWP devueltos se registran igual que las demás."]),
        ("h2", "Registro"),
        ("ol", ["Registrar cada restricción en Registro_Restricciones.xlsx con: ID correlativo, fase del proyecto, CWP, IWP, tipo, descripción verificable, responsable (rol y nombre), fecha identificada y fecha requerida.",
                "La fecha requerida se toma del programa de liberación de IWP (restricciones levantadas antes de la ejecución: 3 semanas en las Fases 1 y 3, 4 semanas en la Fase 2).",
                "Estado inicial: «Abierta»."]),
        ("h2", "Asignación"),
        ("ol", ["En la reunión semanal se confirma el responsable y la fecha requerida de cada restricción nueva.",
                "Cuando el responsable acepta y empieza a gestionarla, el estado pasa a «En gestión»."]),
        ("h2", "Seguimiento semanal"),
        ("tabla", ["Día", "Actividad", "Responsable"], [
            ["Lunes", "Actualizar el registro con las restricciones nuevas de los IWP que entran a la ventana.", "Planificadores"],
            ["Martes", "Reunión de restricciones por fase: vencidas, por vencer (≤ 7 días) y nuevas.", "Líder de WFP"],
            ["Miércoles", "Actualizar estado y adjuntar evidencia de liberación.", "Responsables"],
            ["Jueves", "Reunión de lookahead de 3 semanas: selección de IWP liberados del backlog.", "Gerente de Construcción"],
            ["Viernes", "Liberar los IWP de la semana siguiente con el checklist y publicar KPI.", "Líder de WFP"],
        ], [2, 10, 4]),
        ("h2", "Escalamiento"),
        ("tabla", ["Nivel", "Condición", "Escala a", "Plazo de respuesta"], [
            ["1", "Restricción abierta a 7 días o menos de su fecha requerida", "Gerente de Construcción", "3 días"],
            ["2", "Restricción vencida que afecta a un IWP del lookahead", "Gerente de Proyecto", "2 días"],
            ["3", "Restricción vencida que afecta a la ruta crítica o a otra fase", "Comité AWP / cliente", "Próxima reunión o convocatoria extraordinaria"],
        ], [1.2, 7, 4, 3]),
        ("h2", "Liberación de la restricción"),
        ("ol", ["El responsable informa la liberación con evidencia verificable (transmittal IFC, vale de almacén, permiso aprobado, acta de inspección de andamio, etc.).",
                "El planificador verifica la evidencia, registra la fecha de liberación y cambia el estado a «Liberada».",
                "Si la restricción deja de aplicar, se marca «Cancelada» con la justificación en observaciones."]),
        ("h2", "Liberación del IWP"),
        ("ol", ["Cuando todas las restricciones del IWP están liberadas o canceladas, el planificador aplica el checklist de liberación (Checklist_Liberacion_IWP.xlsx).",
                "Si el resultado es «LIBERAR», el superintendente y el Líder de WFP firman la sección de liberación del IWP y este ingresa al backlog.",
                "Si no, las condiciones faltantes se registran como nuevas restricciones."]),
        ("figura", mermaid_de("restricciones-liberacion.md", 1), "Proceso de liberación de IWP"),
        ("h2", "IWP devuelto de campo"),
        ("p", "Si un IWP se retira de campo sin terminar por una restricción no detectada: se registra la causa en el cierre del IWP, se crea la restricción en el registro, el trabajo pendiente se reprograma (nuevo IWP o revisión) y se evalúa una lección aprendida. El KPI K09 mide estos casos."),
        ("h1", "Plazos por fase del proyecto"),
        ("tabla", ["Concepto", "Fase 1", "Fase 2", "Fase 3"], [
            ["Ventana de planificación de IWP", "8 semanas", "12 semanas", "8 semanas"],
            ["Restricciones identificadas", "6 semanas antes", "10 semanas antes", "6 semanas antes"],
            ["Restricciones asignadas", "5 semanas antes", "8 semanas antes", "5 semanas antes"],
            ["Restricciones levantadas", "3 semanas antes", "4 semanas antes", "3 semanas antes"],
            ["Liberación (ingreso al backlog)", "2 semanas antes", "2 a 4 semanas antes", "2 semanas antes"],
            ["Backlog objetivo", "≥ 2 semanas", "2 a 4 semanas", "3 a 4 semanas"],
            ["Tolerancia de IWP liberados con restricciones", "≤ 15 %", "≤ 5 %", "≤ 2 %"],
        ], [6, 3, 3, 3]),
        ("h1", "Restricciones de interfaz entre fases"),
        ("ul", ["Se registran con el tipo «Interfaz entre fases» y la fase del proyecto que recibe el trabajo.",
                "Su responsable es el AWP Champion, que coordina con los gerentes de construcción de ambas fases.",
                "Durante la superposición de fases, la reunión de restricciones revisa las interfaces antes que las demás.",
                "Las entregas de área entre fases se liberan con acta de entrega firmada por ambas fases."]),
        ("h1", "Indicadores"),
        ("tabla", ["KPI", "Fórmula", "Meta F1 / F2 / F3"], [
            ["K03 IWP liberados sin restricciones", "IWP liberados sin restricciones abiertas ÷ IWP liberados", "≥ 85 % / 95 % / 98 %"],
            ["K05 Restricciones liberadas a tiempo", "Liberadas en o antes de la fecha requerida ÷ liberadas", "≥ 80 % / 90 % / 95 %"],
            ["K06 Atraso promedio de restricciones", "Días de atraso promedio de las vencidas", "≤ 7 / 5 / 3 días"],
            ["K09 IWP devueltos", "IWP devueltos ÷ IWP entregados a campo", "≤ 8 % / 5 % / 3 %"],
        ], [5, 7, 4]),
        ("h1", "Registros"),
        ("tabla", ["Registro", "Responsable", "Conservación"], [
            ["Registro_Restricciones.xlsx", "Líder de WFP", "Hasta el cierre del proyecto"],
            ["Checklist de liberación de cada IWP", "Planificador", "En el dossier del IWP"],
            ["Actas de la reunión semanal de restricciones", "Líder de WFP", "Hasta el cierre de la fase"],
        ], [6, 4, 5]),
        ("h1", "Control de cambios"),
        ("tabla", ["Revisión", "Fecha", "Descripción del cambio", "Aprobó"], [["0", ew.fecha_hoy(), "Emisión inicial.", "Gerente de Proyecto"]], [2, 3, 8, 3], 3),
    ]
    d.guardar("Procedimiento_Gestion_Restricciones.docx", bloques)


# ==========================================================================
# Acta del taller de Path of Construction
# ==========================================================================

def acta_taller_poc():
    d = Documento("Acta del taller de Path of Construction (IPP)", "PT-AWP-FOR-IPP",
                  "Registro de los acuerdos del taller de planificación interactiva en que se desarrolla o actualiza el Path of Construction de una fase.")
    bloques = [
        ("instr", "Se usa en cada taller de planificación interactiva (IPP). El PoC se desarrolla en FEL 2 y se congela en FEL 3 (hito H2). Adjunte la versión de Path_of_Construction.xlsx acordada."),
        ("h1", "Datos del taller"),
        ("campos", [("Fase del proyecto", FASES_CHECK), ("Taller N.°", "‹1 de 3›"),
                    ("Fecha", "‹dd/mm/aaaa›"), ("Lugar / modalidad", C),
                    ("Facilitador", "AWP Champion"), ("Etapa del ciclo de vida", "☐ FEL 2   ☐ FEL 3   ☐ Actualización en ejecución")], 4),
        ("h1", "Participantes"),
        ("tabla", ["Nombre", "Rol", "Organización", "Asistió"], [[C, "Gerente de Construcción", "", "☐"], [C, "Líder de Ingeniería", "", "☐"],
                                                               [C, "Líder de Procura", "", "☐"], [C, "Líder de comisionamiento", "", "☐"],
                                                               [C, "Gerente del proyecto del cliente", "", "☐"], [C, "Controles del proyecto", "", "☐"]], [5, 5, 4, 1.5], 4),
        ("h1", "Objetivos y agenda"),
        ("ol", ["Revisar las CWA y sus límites (Definicion_CWA.xlsx).",
                "Acordar la secuencia de construcción de CWA y CWP, empezando por los sistemas a entregar primero.",
                "Identificar predecesores, interfaces entre fases y recursos críticos (grúas, accesos, acopio).",
                "Calcular hacia atrás las fechas requeridas de EWP, emisión de CWP y RAS de materiales.",
                "Acordar acciones y responsables."]),
        ("h1", "Insumos revisados"),
        ("campos", [("Plano de CWA", "☐ Revisado   Revisión: ‹›"), ("Cronograma nivel 2 / 3", "☐ Revisado   Revisión: ‹›"),
                    ("Lista de sistemas", "☐ Revisado"), ("Lecciones aprendidas de la fase anterior", "☐ Revisadas (Registro_Lecciones_Aprendidas.xlsx)")]),
        ("h1", "Secuencia acordada"),
        ("tabla", ["Secuencia", "CWA", "CWP", "Inicio plan", "Predecesor", "Justificación"], [["1", "‹CWA-2.03›", "‹CWP-2.03-ELE-01›", "", "", "‹Energización temprana›"]], [1.5, 2, 3.2, 2, 3, 5], 7),
        ("h1", "Supuestos, riesgos e interfaces"),
        ("tabla", ["Tipo", "Descripción", "Fase afectada", "Responsable"], [["‹Supuesto / riesgo / interfaz›", "", "", ""]], [3, 8, 2, 3], 4),
        ("h1", "Decisiones"),
        ("tabla", ["N.°", "Decisión", "Tomada por"], [["1", C, ""]], [1, 11, 4], 3),
        ("h1", "Acciones"),
        ("tabla", ["N.°", "Acción", "Responsable (rol)", "Fecha", "Estado"], [["1", C, "", "", ""]], [1, 8, 3.5, 2, 2], 5),
        ("h1", "Aprobación del Path of Construction"),
        ("campos", [("Estado del PoC", "☐ Borrador   ☐ Acordado   ☐ Congelado (hito H2)")]),
        ("firmas", ["Gerente de Construcción", "AWP Champion", "Gerente del proyecto del cliente"]),
    ]
    d.guardar("Acta_Taller_Path_of_Construction.docx", bloques)


# ==========================================================================
# Informe de cierre de fase
# ==========================================================================

def informe_cierre_fase():
    from generar_excel import KPIS
    d = Documento("Informe de cierre AWP de fase", "PT-AWP-INF-CIE",
                  "Resultados de la implementación de AWP en una fase del proyecto y transferencia de lecciones a la fase siguiente (hito H10).")
    def meta(v, unidad):
        if unidad == "%":
            return f"{v * 100:.0f} %"
        return f"{v:g}".replace(".", ",")

    kpis = [[f"{k[0]} {k[1]}", f"{k[4]} " + " / ".join(meta(v, k[3]) for v in k[5]), "", "", ""] for k in KPIS]
    bloques = [
        ("instr", "Lo prepara el AWP Champion al cierre de cada fase del proyecto (M14, M30 y M36) con los datos de Tablero_KPI.xlsx, Seguimiento_Paquetes.xlsx, Registro_Restricciones.xlsx y Registro_Lecciones_Aprendidas.xlsx. Se aprueba antes de la puerta de control de la fase siguiente."),
        ("h1", "Datos generales"),
        ("campos", [("Fase del proyecto", FASES_CHECK), ("Periodo", "‹M_ a M_›"),
                    ("Nivel de madurez objetivo", "‹2 / 3 / 4›"), ("Nivel de madurez alcanzado", C),
                    ("Elaborado por", "AWP Champion"), ("Fecha", "‹dd/mm/aaaa›")], 4),
        ("h1", "Resumen ejecutivo"),
        ("instr", "Máximo media página: qué se implementó, resultados principales frente a las metas y las tres recomendaciones más importantes para la fase siguiente."),
        ("campos", [("Resumen", C)]),
        ("h1", "Resultados de los indicadores"),
        ("tabla", ["KPI", "Meta F1 / F2 / F3", "Valor de la fase", "Semáforo", "Comentario"], kpis, [5, 3.5, 2, 2, 4.5], 8),
        ("h1", "Hitos AWP"),
        ("tabla", ["Hito", "Fecha plan", "Fecha real", "Criterio cumplido", "Comentario"],
         [["H1 CWA definidas", "", "", "☐", ""], ["H2 Path of Construction aprobado", "", "", "☐", ""], ["H3 CWP, EWP y PWP definidos", "", "", "☐", ""],
          ["H4 Requisitos AWP en contratos", "", "", "☐", ""], ["H5 Primer EWP emitido IFC", "", "", "☐", ""], ["H6 Primer CWP emitido", "", "", "☐", ""],
          ["H7 Primer IWP liberado", "", "", "☐", ""], ["H8 Backlog estable", "", "", "☐", ""], ["H9 Primer sistema o área entregado", "", "", "☐", ""],
          ["H10 Cierre AWP de la fase", "", "", "☐", ""]], [5, 2.2, 2.2, 2.2, 4.5]),
        ("h1", "Paquetes de la fase"),
        ("tabla", ["Tipo", "Planificados", "Cerrados", "Cerrados con atraso", "Atraso promedio (días)"],
         [["CWA", "", "", "", ""], ["CWP", "", "", "", ""], ["EWP", "", "", "", ""], ["PWP", "", "", "", ""], ["IWP", "", "", "", ""]], [3, 3, 3, 3, 3]),
        ("h1", "Restricciones"),
        ("tabla", ["Tipo de restricción", "Cantidad", "% del total", "Liberadas a tiempo", "Comentario"],
         [[t, "", "", "", ""] for t in dp.TIPOS_RESTRICCION], [4.5, 2, 2, 2.5, 5]),
        ("h1", "Lecciones aprendidas y acciones para la fase siguiente"),
        ("tabla", ["ID", "Lección", "Acción", "Responsable", "Fecha", "Estado"], [["‹LA-00›", "", "", "", "", ""]], [1.5, 5, 5, 2.5, 1.8, 1.8], 6),
        ("h1", "Recomendaciones de escala para la fase siguiente"),
        ("campos", [("Procesos y plantillas", C), ("Herramientas e información", C), ("Organización y dotación", C),
                    ("Metas de KPI propuestas", C), ("Contratos", C)]),
        ("h1", "Aprobaciones"),
        ("firmas", ["AWP Champion", "Gerente de Construcción", "Gerente de Proyecto", "Gerente del proyecto del cliente"]),
    ]
    d.guardar("Informe_Cierre_Fase_AWP.docx", bloques)


# ==========================================================================
# Perfiles de puesto AWP
# ==========================================================================

def perfiles_puesto():
    d = Documento("Perfiles de puesto AWP", "PT-AWP-PER-001",
                  "Perfiles de los roles dedicados a AWP: AWP Champion, Líder de WFP, planificador de frente de trabajo y coordinador de gestión de información.",
                  tipo="documento")
    perfiles = [
        ("AWP Champion", "Gerente de Proyecto (con acceso directo al Gerente del proyecto del cliente)",
         "Completa, desde la planificación temprana global hasta el cierre del proyecto.",
         "Liderar la implementación de AWP en las tres fases del proyecto y asegurar que la secuencia de construcción dirija la ingeniería y la procura.",
         ["Elaborar y mantener el plan de implementación, procedimientos y plantillas AWP.", "Facilitar los talleres de Path of Construction.",
          "Formar al equipo del cliente, del contratista y de los subcontratistas.", "Consolidar y presentar los KPI en el Comité AWP.",
          "Gestionar las interfaces entre fases superpuestas.", "Auditar el proceso y liderar las lecciones aprendidas y el informe de cierre de cada fase."],
         ["Profesional en ingeniería o construcción.", "10 años o más en proyectos de construcción, con experiencia en planificación y en campo.",
          "Conocimiento de AWP (CII / COAA), WFP y cronogramas CPM.", "Liderazgo, facilitación y comunicación con la gerencia."],
         "Hitos AWP cumplidos; K03, K08 y K10 por fase; lecciones implementadas antes de cada puerta de control."),
        ("Líder de WFP", "AWP Champion (funcional) y Gerente de Construcción (operativo)",
         "Completa durante la construcción de cada fase.",
         "Coordinar a los planificadores de frente de trabajo y asegurar un flujo continuo de IWP liberados.",
         ["Dirigir la reunión semanal de restricciones.", "Aprobar la liberación de IWP con el checklist.", "Controlar el backlog y el programa de liberación.",
          "Consolidar el reporte semanal de WFP.", "Formar y evaluar a los planificadores."],
         ["Técnico o profesional con experiencia de supervisión en campo.", "5 años o más en construcción; experiencia como planificador de frente de trabajo.",
          "Manejo del software de WFP, cronogramas y hojas de cálculo."],
         "K03, K04, K05, K06 y K09."),
        ("Planificador de frente de trabajo", "Líder de WFP (funcional) y superintendente de su área (operativo)",
         "Completa. Proporción de referencia: 1 por cada 50 trabajadores directos.",
         "Preparar IWP completos y libres de restricciones para las cuadrillas de su área.",
         ["Dividir los CWP en IWP de una semana (300 a 600 HH).", "Identificar, registrar y seguir las restricciones.",
          "Armar el IWP con documentos, materiales, recursos, HSE y calidad.", "Aplicar el checklist de liberación.",
          "Recibir los IWP terminados y registrar avance, HH y causas de desviación."],
         ["Oficio de la disciplina con experiencia de supervisión (capataz o similar).", "Lectura de planos y modelos 3D.", "Manejo básico de software de WFP y hojas de cálculo."],
         "Calidad de los IWP (auditoría), K03 y K09 de su área."),
        ("Coordinador de gestión de información (IM)", "AWP Champion",
         "Completa en las Fases 2 y 3; parcial en la Fase 1.",
         "Asegurar que modelo 3D, cronograma, materiales y documentos compartan la codificación AWP y estén integrados.",
         ["Definir la codificación y los atributos AWP del modelo 3D.", "Administrar el software de WFP y sus integraciones.",
          "Controlar la calidad de los datos de paquetes.", "Dar soporte a planificadores e ingeniería."],
         ["Profesional con experiencia en BIM, modelos 3D o sistemas de información de proyectos.", "Conocimiento de cronogramas y control documental."],
         "Integridad de datos (auditoría), disponibilidad del software de WFP."),
    ]
    bloques = [
        ("h1", "Propósito"),
        ("p", "Definir los perfiles de los roles dedicados a AWP del proyecto tipo, para su selección, contratación y evaluación. Complementa la sección «Organización y roles» del plan de implementación y la Matriz_Roles_RACI.xlsx. Las fuentes insisten en que el AWP Champion y los planificadores de frente de trabajo deben ser roles dedicados."),
    ]
    for nombre, reporta, dedic, proposito, resp, req, kpi in perfiles:
        bloques += [
            ("h1", nombre),
            ("campos", [("Reporta a", reporta), ("Dedicación", dedic), ("Propósito del puesto", proposito)]),
            ("h2", "Responsabilidades"), ("ul", resp),
            ("h2", "Requisitos"), ("ul", req),
            ("h2", "Indicadores de desempeño"), ("p", kpi),
        ]
    bloques += [
        ("h1", "Formación"),
        ("tabla", ["Curso", "Dirigido a", "Duración", "Momento"], [
            ["Introducción a AWP", "Todo el equipo del proyecto", "8 h", "Arranque de cada fase"],
            ["Workface Planning para planificadores", "Planificadores y Líder de WFP", "40 h", "Antes del primer IWP de cada fase"],
            ["Uso del IWP en campo", "Capataces y superintendentes", "4 h", "Antes de su primer IWP"],
            ["Casos de la fase anterior", "Personal nuevo de las Fases 2 y 3", "4 h", "Al incorporarse"],
        ], [5, 5, 2, 4]),
    ]
    d.guardar("Perfiles_Puesto_AWP.docx", bloques)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for f in (plantilla_iwp, plantilla_cwp, plantilla_ewp, procedimiento_restricciones, acta_taller_poc, informe_cierre_fase, perfiles_puesto):
        f()


if __name__ == "__main__":
    main()
