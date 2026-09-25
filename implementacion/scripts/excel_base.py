"""Funciones comunes para construir las plantillas Excel del kit AWP.

Cada plantilla tiene:
- una hoja «Instrucciones» (propósito, cómo llenarla, significado de columnas);
- una o más hojas de datos con encabezado fijo, filtros, listas desplegables,
  fórmulas y formato condicional, listas para imprimir;
- una hoja «Listas» con los valores de las listas desplegables (rangos con nombre).
"""

from datetime import date

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

import datos_proyecto as dp

AZUL = "1F3864"
AZUL_CLARO = "DCE6F2"
GRIS = "F2F2F2"
AMARILLO_EJEMPLO = "FFF2CC"
ROJO = "F8CBAD"
ROJO_TEXTO = "9C0006"
AMBAR = "FFE699"
VERDE = "C6EFCE"
VERDE_TEXTO = "006100"
BLANCO = "FFFFFF"

FUENTE = "Calibri"
fino = Side(style="thin", color="BFBFBF")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)

FILA_TITULO = 1
FILA_SUBTITULO = 2
FILA_PARAM = 3
FILA_ENC = 5
FILA_DATOS = 6

FORMATO = {
    "fecha": "DD/MM/YYYY",
    "num": "#,##0",
    "dec": "#,##0.00",
    "pct": "0%",
    "pct1": "0.0%",
    "texto": "@",
}


def relleno(color):
    return PatternFill("solid", start_color=color, end_color=color)


# --------------------------------------------------------------------------
# Libro y listas
# --------------------------------------------------------------------------

LISTAS_BASE = {
    "Fases": dp.FASES,
    "FasesExt": dp.FASES_EXT,
    "Etapas": dp.ETAPAS,
    "Disciplinas": dp.COD_DISCIPLINAS,
    "TiposPaquete": dp.TIPOS_PAQUETE,
    "EstadosPaquete": dp.ESTADOS_PAQUETE,
    "EstadosRestriccion": dp.ESTADOS_RESTRICCION,
    "TiposRestriccion": dp.TIPOS_RESTRICCION,
    "Roles": dp.NOMBRES_ROL,
    "CodigosRol": [c for c, _ in dp.ROLES],
    "SiNo": dp.SI_NO,
}


class Libro:
    def __init__(self, archivo, titulo, listas=()):
        self.archivo = archivo
        self.titulo = titulo
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        self.listas = {}
        self.instrucciones = self.wb.create_sheet("Instrucciones")
        self._nombres_listas = list(listas)
        self.wb.properties.title = titulo
        self.wb.properties.creator = "Kit de implementación AWP"
        self.wb.properties.subject = dp.PROYECTO

    def crear_listas(self, extra=None):
        """Hoja «Listas» con un rango con nombre por cada lista usada."""
        ws = self.wb.create_sheet("Listas")
        ws["A1"] = "Valores de las listas desplegables. Puede ampliarlas agregando valores al final de cada columna y ajustando el rango con nombre (Fórmulas > Administrador de nombres)."
        ws["A1"].font = Font(name=FUENTE, italic=True, size=9)
        listas = {n: LISTAS_BASE[n] for n in self._nombres_listas}
        listas.update(extra or {})
        for i, (nombre, valores) in enumerate(listas.items(), start=1):
            col = get_column_letter(i)
            ws.cell(row=2, column=i, value=nombre).font = Font(name=FUENTE, bold=True, color=BLANCO)
            ws.cell(row=2, column=i).fill = relleno(AZUL)
            for j, v in enumerate(valores, start=3):
                ws.cell(row=j, column=i, value=v).font = Font(name=FUENTE, size=10)
            ws.column_dimensions[col].width = max(14, min(42, max(len(str(v)) for v in valores) + 2))
            ref = f"Listas!${col}$3:${col}${len(valores) + 2}"
            self.wb.defined_names[nombre] = DefinedName(nombre, attr_text=ref)
            self.listas[nombre] = valores
        ws.freeze_panes = "A3"
        ws.sheet_properties.tabColor = "7F7F7F"
        return ws

    def guardar(self):
        # «Instrucciones» queda como hoja activa al abrir.
        self.wb.active = 0
        for ws in self.wb.worksheets:
            ws.sheet_view.tabSelected = ws.title == "Instrucciones"
        self.wb.save(self.archivo)


# --------------------------------------------------------------------------
# Hoja de datos genérica
# --------------------------------------------------------------------------

class Col:
    """Definición de una columna de una hoja de datos.

    tipo: texto | fecha | num | dec | pct | pct1
    lista: nombre de rango con nombre para lista desplegable
    formula: función (fila, c) -> str; c(clave) devuelve la letra de columna
    """

    def __init__(self, clave, titulo, ancho=14, tipo="texto", lista=None, formula=None,
                 desc="", ajustar=False, lista_valores=None):
        self.clave = clave
        self.titulo = titulo
        self.ancho = ancho
        self.tipo = tipo
        self.lista = lista
        self.lista_valores = lista_valores
        self.formula = formula
        self.desc = desc
        self.ajustar = ajustar

    @property
    def origen(self):
        if self.formula:
            return "Calculado"
        if self.lista or self.lista_valores:
            return "Lista"
        return "Manual"


def estilo_titulo(ws, titulo, subtitulo, ultima_col):
    ws.cell(row=FILA_TITULO, column=1, value=titulo)
    ws.cell(row=FILA_TITULO, column=1).font = Font(name=FUENTE, size=15, bold=True, color=AZUL)
    ws.cell(row=FILA_SUBTITULO, column=1, value=subtitulo)
    ws.cell(row=FILA_SUBTITULO, column=1).font = Font(name=FUENTE, size=10, italic=True, color="595959")
    ws.row_dimensions[FILA_TITULO].height = 24


def hoja_datos(libro, nombre, titulo, columnas, ejemplos, n_filas=200, params=None,
               congelar_col=2, subtitulo=None, alto_enc=42, orientacion="landscape"):
    """Crea una hoja de datos. `ejemplos` es una lista de dicts clave -> valor.

    Devuelve (ws, c, ultima_fila) donde c(clave) da la letra de la columna.
    """
    ws = libro.wb.create_sheet(nombre)
    letras = {col.clave: get_column_letter(i) for i, col in enumerate(columnas, start=1)}

    def c(clave):
        return letras[clave]

    ultima = FILA_DATOS + n_filas - 1
    ncol = len(columnas)
    estilo_titulo(
        ws, titulo,
        subtitulo or f"{dp.PROYECTO}. Las filas en amarillo marcadas «EJEMPLO» son de ejemplo: bórrelas o reemplácelas.",
        ncol,
    )

    # Parámetros (por ejemplo, fecha de corte) en la fila 3.
    celdas_param = {}
    if params:
        colp = 1
        for clave, etiqueta, valor, fmt in params:
            ws.cell(row=FILA_PARAM, column=colp, value=etiqueta).font = Font(name=FUENTE, bold=True, size=10)
            ws.cell(row=FILA_PARAM, column=colp).alignment = Alignment(horizontal="right")
            celda = ws.cell(row=FILA_PARAM, column=colp + 1, value=valor)
            celda.fill = relleno(AZUL_CLARO)
            celda.border = BORDE
            celda.font = Font(name=FUENTE, bold=True, size=10)
            if fmt:
                celda.number_format = FORMATO.get(fmt, fmt)
            celdas_param[clave] = f"${get_column_letter(colp + 1)}${FILA_PARAM}"
            colp += 3

    # Encabezados
    for i, col in enumerate(columnas, start=1):
        celda = ws.cell(row=FILA_ENC, column=i, value=col.titulo)
        celda.font = Font(name=FUENTE, bold=True, color=BLANCO, size=10)
        celda.fill = relleno(AZUL if col.origen != "Calculado" else "2F5597")
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        celda.border = BORDE
        ws.column_dimensions[get_column_letter(i)].width = col.ancho
    ws.row_dimensions[FILA_ENC].height = alto_enc

    # Filas: ejemplos + filas vacías con formato y fórmulas
    for n in range(n_filas):
        fila = FILA_DATOS + n
        ejemplo = ejemplos[n] if n < len(ejemplos) else None
        for i, col in enumerate(columnas, start=1):
            celda = ws.cell(row=fila, column=i)
            if col.formula:
                celda.value = col.formula(fila, c, celdas_param)
            elif ejemplo is not None and col.clave in ejemplo:
                celda.value = ejemplo[col.clave]
            celda.border = BORDE
            celda.font = Font(name=FUENTE, size=10, color="404040" if col.formula else "000000")
            celda.alignment = Alignment(vertical="top", wrap_text=col.ajustar,
                                        horizontal="center" if col.tipo in ("fecha", "pct", "pct1") or col.clave == "ejemplo" else None)
            if col.tipo in FORMATO and col.tipo != "texto":
                celda.number_format = FORMATO[col.tipo]
            if ejemplo is not None:
                celda.fill = relleno(AMARILLO_EJEMPLO)
            elif col.formula:
                celda.fill = relleno(GRIS)

    # Listas desplegables
    for col in columnas:
        if col.lista or col.lista_valores:
            formula = f"={col.lista}" if col.lista else '"' + ",".join(col.lista_valores) + '"'
            dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
            dv.error = "Seleccione un valor de la lista."
            dv.errorTitle = "Valor no válido"
            dv.prompt = f"Seleccione {col.titulo.lower()}"
            dv.showErrorMessage = True
            dv.add(f"{c(col.clave)}{FILA_DATOS}:{c(col.clave)}{ultima}")
            ws.add_data_validation(dv)

    # Encabezado fijo, filtros e impresión
    ws.freeze_panes = f"{get_column_letter(congelar_col + 1)}{FILA_DATOS}"
    ws.auto_filter.ref = f"A{FILA_ENC}:{get_column_letter(ncol)}{ultima}"
    # Se imprimen 50 filas de datos para no generar páginas vacías; el área
    # se amplía en Diseño de página > Área de impresión.
    configurar_impresion(ws, titulo, orientacion, filas_titulo=f"{FILA_ENC}:{FILA_ENC}",
                         area=f"A1:{get_column_letter(ncol)}{min(ultima, FILA_DATOS + 49)}")
    ws.sheet_properties.tabColor = AZUL
    ws._kit_celdas_param = celdas_param
    return ws, c, ultima


def configurar_impresion(ws, titulo, orientacion="landscape", filas_titulo=None, area=None):
    ws.page_setup.orientation = orientacion
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = 0.6
    ws.page_margins.bottom = 0.6
    if filas_titulo:
        ws.print_title_rows = filas_titulo
    if area:
        ws.print_area = area
    ws.oddHeader.left.text = "Kit de implementación AWP"
    ws.oddHeader.left.size = 8
    ws.oddHeader.right.text = titulo
    ws.oddHeader.right.size = 8
    ws.oddFooter.left.text = dp.PROYECTO
    ws.oddFooter.left.size = 8
    ws.oddFooter.right.text = "Página &P de &N"
    ws.oddFooter.right.size = 8


def resaltar_fila(ws, rango, formula, color_fondo, color_texto=None, negrita=False):
    fuente = Font(color=color_texto, bold=negrita) if (color_texto or negrita) else None
    ws.conditional_formatting.add(
        rango, FormulaRule(formula=[formula], fill=relleno(color_fondo), font=fuente, stopIfTrue=True)
    )


def semaforo_texto(ws, rango, primera_celda):
    """Colorea celdas con texto Verde / Ámbar / Rojo (o equivalentes)."""
    for texto, fondo, letra in (
        ("Rojo", ROJO, ROJO_TEXTO), ("Ámbar", AMBAR, "7F6000"), ("Verde", VERDE, VERDE_TEXTO),
    ):
        resaltar_fila(ws, rango, f'{primera_celda}="{texto}"', fondo, letra, True)


# --------------------------------------------------------------------------
# Hoja de instrucciones
# --------------------------------------------------------------------------

def hoja_instrucciones(libro, proposito, cuando, quien, pasos, hojas_columnas, notas=(), justificacion=None):
    ws = libro.instrucciones
    ws.sheet_properties.tabColor = "548235"
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 70
    ws.column_dimensions["C"].width = 14
    fila = 1
    ws.cell(row=fila, column=1, value=libro.titulo).font = Font(name=FUENTE, size=16, bold=True, color=AZUL)
    fila += 1
    ws.cell(row=fila, column=1, value=f"Kit de implementación AWP · {dp.PROYECTO}").font = Font(name=FUENTE, italic=True, size=10, color="595959")
    fila += 2

    def bloque(titulo, texto):
        nonlocal fila
        ws.cell(row=fila, column=1, value=titulo).font = Font(name=FUENTE, bold=True, color=AZUL, size=11)
        ws.cell(row=fila, column=1).alignment = Alignment(vertical="top")
        celda = ws.cell(row=fila, column=2, value=texto)
        celda.alignment = Alignment(wrap_text=True, vertical="top")
        celda.font = Font(name=FUENTE, size=10)
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=3)
        lineas = sum(max(1, len(t) // 95 + 1) for t in str(texto).split("\n"))
        ws.row_dimensions[fila].height = max(16, 14 * lineas)
        fila += 1

    bloque("Propósito", proposito)
    if justificacion:
        bloque("Por qué se incluye", justificacion)
    bloque("Cuándo se usa", cuando)
    bloque("Quién la llena", quien)
    bloque("Cómo llenarla", "\n".join(f"{i}. {p}" for i, p in enumerate(pasos, 1)))
    bloque("Colores", "Amarillo: fila de ejemplo (bórrela o reemplácela). Encabezado azul oscuro: dato que se ingresa. "
                      "Encabezado azul medio y celda gris: columna calculada con fórmula (no la sobrescriba). "
                      "Rojo: vencido o fuera de meta. Ámbar: por vencer o cerca del límite. Verde: cumplido.")
    bloque("Impresión", "Cada hoja está configurada en A4, ajustada al ancho de la página, con el encabezado repetido en cada página. "
                        "El área de impresión de las hojas de datos cubre las primeras 50 filas: si usa más, amplíela en Diseño de página > Área de impresión.")
    for nota in notas:
        bloque(nota[0], nota[1])
    fila += 1

    for nombre_hoja, columnas in hojas_columnas:
        ws.cell(row=fila, column=1, value=f"Columnas de la hoja «{nombre_hoja}»").font = Font(name=FUENTE, bold=True, size=12, color=AZUL)
        fila += 1
        for i, t in enumerate(("Columna", "Significado", "Tipo de dato"), start=1):
            celda = ws.cell(row=fila, column=i, value=t)
            celda.font = Font(name=FUENTE, bold=True, color=BLANCO)
            celda.fill = relleno(AZUL)
            celda.border = BORDE
        fila += 1
        for col in columnas:
            if isinstance(col, Col):
                datos = (col.titulo, col.desc, col.origen)
            else:
                datos = col
            for i, v in enumerate(datos, start=1):
                celda = ws.cell(row=fila, column=i, value=v)
                celda.border = BORDE
                celda.alignment = Alignment(wrap_text=True, vertical="top")
                celda.font = Font(name=FUENTE, size=10, bold=(i == 1))
                if datos[2] == "Calculado":
                    celda.fill = relleno(GRIS)
            ws.row_dimensions[fila].height = max(15, 14 * (len(str(datos[1])) // 80 + 1))
            fila += 1
        fila += 1

    ws.freeze_panes = "A4"
    configurar_impresion(ws, libro.titulo, "portrait", area=f"A1:C{fila}")
    return ws


def fecha(a, m, d):
    return date(a, m, d)
