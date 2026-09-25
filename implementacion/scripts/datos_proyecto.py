"""Datos maestros del proyecto tipo, compartidos por todas las plantillas.

Todas las listas desplegables, códigos de paquetes, roles y estados de las
plantillas Excel y Word salen de aquí, para que el kit sea consistente.
Coinciden con la sección «Implementación» de la web.
"""

from datetime import date

PROYECTO = "Proyecto Tipo (PT) – Complejo de instalaciones en tres fases"

# Fecha de corte de los ejemplos (mes M18 del proyecto). En uso real se
# reemplaza por la fecha del reporte o por la fórmula =HOY().
FECHA_CORTE = date(2028, 6, 15)
INICIO_PROYECTO = date(2027, 1, 1)  # M1

FASES = ["Fase 1", "Fase 2", "Fase 3"]
FASES_EXT = FASES + ["Fases 1 y 2", "Fases 2 y 3", "Todas las fases"]
NOMBRE_FASE = {
    "Fase 1": "Infraestructura y obras tempranas",
    "Fase 2": "Instalación principal",
    "Fase 3": "Edificaciones complementarias y ampliación",
}

ETAPAS = [
    "Planificación temprana (FEL)",
    "Ingeniería",
    "Procura",
    "Construcción",
    "Comisionamiento",
]

DISCIPLINAS = [
    ("CIV", "Civil"),
    ("EST", "Estructuras"),
    ("ARQ", "Arquitectura"),
    ("MEC", "Mecánica"),
    ("TUB", "Tuberías"),
    ("ELE", "Eléctrica"),
    ("INS", "Instrumentación y control"),
    ("VAR", "Varias disciplinas"),
]
COD_DISCIPLINAS = [c for c, _ in DISCIPLINAS]

TIPOS_PAQUETE = ["CWA", "CWP", "EWP", "PWP", "IWP"]

ESTADOS_PAQUETE = [
    "Planificado",
    "En desarrollo",
    "En revisión",
    "Aprobado",
    "Liberado",
    "En ejecución",
    "Cerrado",
    "Suspendido",
]
SIGNIFICADO_ESTADO_PAQUETE = {
    "Planificado": "Identificado en el plan de liberación; aún no se trabaja en él.",
    "En desarrollo": "Se está preparando (diseño, compra o armado del paquete).",
    "En revisión": "Preparado y en revisión interna o del cliente.",
    "Aprobado": "Aprobado: EWP emitido IFC, PWP con orden de compra, CWP aprobado, CWA/IWP aprobados.",
    "Liberado": "IWP sin restricciones abiertas y con checklist firmado (en backlog); CWP emitido a construcción.",
    "En ejecución": "Trabajo en campo en curso (CWA, CWP e IWP) o material en fabricación/entrega (PWP).",
    "Cerrado": "Trabajo terminado y documentación cerrada (calidad, avance, materiales).",
    "Suspendido": "Detenido o devuelto de campo; registrar la causa en observaciones.",
}

ESTADOS_RESTRICCION = ["Abierta", "En gestión", "Liberada", "Cancelada"]

TIPOS_RESTRICCION = [
    "Ingeniería",
    "Materiales",
    "Equipos de construcción",
    "Permisos",
    "Mano de obra",
    "Andamios",
    "Acceso / interferencias",
    "Trabajos predecesores",
    "Calidad",
    "HSE",
    "Documentación del proveedor",
    "Interfaz entre fases",
]

# Causas de no cumplimiento del plan semanal (lookahead / PPC).
CAUSAS_NO_CUMPLIMIENTO = TIPOS_RESTRICCION + ["Clima", "Cambio de prioridad", "Productividad menor a la prevista", "Otro"]

ROLES = [
    ("CLI", "Gerente del proyecto del cliente"),
    ("GP", "Gerente de Proyecto"),
    ("CHA", "AWP Champion"),
    ("LWF", "Líder de WFP"),
    ("WFP", "Planificador de frente de trabajo"),
    ("ING", "Líder de Ingeniería"),
    ("PRO", "Líder de Procura"),
    ("MAT", "Gestor de materiales"),
    ("CON", "Gerente de Construcción"),
    ("SUP", "Superintendente / capataz general"),
    ("CTR", "Controles del proyecto"),
    ("IM", "Coordinador de gestión de información"),
    ("HSE", "Líder de HSE"),
    ("CAL", "Líder de calidad (QA/QC)"),
    ("COM", "Líder de comisionamiento"),
    ("SUB", "Subcontratista de especialidad"),
]
NOMBRES_ROL = [n for _, n in ROLES]
ROL = dict(ROLES)

ESTADOS_RIESGO = ["Abierto", "En tratamiento", "Cerrado", "Materializado"]
CATEGORIAS_RIESGO = [
    "Organización y liderazgo",
    "Personas y competencias",
    "Procesos",
    "Contratos",
    "Herramientas e información",
    "Interfaces entre fases",
    "Medición",
]

ESTADOS_LECCION = ["Registrada", "En análisis", "Aprobada", "Implementada", "Verificada", "Descartada"]
CATEGORIAS_LECCION = [
    "Definición de paquetes",
    "Path of Construction",
    "Restricciones",
    "Materiales",
    "Ingeniería",
    "Herramientas e información",
    "Organización y roles",
    "HSE",
    "Calidad",
    "Comisionamiento",
    "Interfaces entre fases",
]

SI_NO = ["Sí", "No"]
CUMPLE = ["Sí", "No", "Pendiente", "No aplica"]
NIVELES_1_5 = [1, 2, 3, 4, 5]
IMPACTO_CUALITATIVO = ["Alto", "Medio", "Bajo"]

# --------------------------------------------------------------------------
# Paquetes del proyecto tipo
# --------------------------------------------------------------------------

CWAS = [
    # código, fase, nombre, disciplinas, HH, secuencia, predecesora, límites
    ("CWA-1.01", "Fase 1", "Plataformas y movimiento de tierras", "CIV", 120000, 1, "—", "Plataformas norte y sur, taludes y drenaje superficial"),
    ("CWA-1.02", "Fase 1", "Redes enterradas", "CIV, TUB, ELE", 110000, 2, "CWA-1.01", "Redes de agua, desagüe y bancos de ductos en todo el terreno"),
    ("CWA-1.03", "Fase 1", "Vías de acceso e instalaciones temporales", "CIV, ELE, ARQ", 70000, 1, "—", "Vía de acceso principal, patio de acopio y oficinas de obra"),
    ("CWA-2.01", "Fase 2", "Instalación principal – bloque A", "Todas", 380000, 2, "CWA-2.03", "Ejes A1–A12 de la instalación principal"),
    ("CWA-2.02", "Fase 2", "Instalación principal – bloque B", "Todas", 360000, 3, "CWA-2.01", "Ejes B1–B10 de la instalación principal"),
    ("CWA-2.03", "Fase 2", "Sala eléctrica y de servicios", "CIV, EST, ELE, INS", 160000, 1, "CWA-1.02", "Edificio de sala eléctrica y cuarto de servicios"),
    ("CWA-2.04", "Fase 2", "Galería de servicios e interconexiones", "EST, TUB, ELE", 200000, 4, "CWA-2.01", "Galería elevada entre bloques y sala eléctrica"),
    ("CWA-3.01", "Fase 3", "Edificaciones complementarias", "CIV, EST, ARQ, ELE", 180000, 1, "CWA-1.02", "Almacén, oficinas y talleres"),
    ("CWA-3.02", "Fase 3", "Ampliación de la instalación principal", "Todas", 200000, 2, "CWA-2.04", "Ejes C1–C6, contiguos al bloque B"),
    ("CWA-3.03", "Fase 3", "Urbanización y obras exteriores", "CIV, ELE", 70000, 3, "CWA-3.01", "Pavimentos, veredas, alumbrado y cercos"),
]

# CWP del Path of Construction: código, fase, descripción, disciplina, HH,
# inicio plan, duración (semanas), predecesor, sistema, justificación.
CWPS = [
    ("CWP-1.01-CIV-01", "Fase 1", "Movimiento de tierras plataforma norte", "CIV", 42000, date(2027, 6, 7), 7, "—", "Plataformas", "Libera la plataforma de la instalación principal para la Fase 2."),
    ("CWP-1.02-TUB-01", "Fase 1", "Redes de agua y desagüe", "TUB", 26000, date(2027, 8, 2), 18, "CWP-1.01-CIV-01", "Agua y desagüe", "Redes enterradas antes de cimentaciones para evitar interferencias."),
    ("CWP-1.02-ELE-01", "Fase 1", "Bancos de ductos eléctricos", "ELE", 18000, date(2027, 8, 16), 16, "CWP-1.01-CIV-01", "Energía de obra", "Alimenta la subestación de obra y la futura sala eléctrica."),
    ("CWP-2.03-ELE-01", "Fase 2", "Equipos y cableado de sala eléctrica", "ELE", 30000, date(2028, 3, 6), 30, "CWP-1.02-ELE-01", "Distribución eléctrica", "Energización temprana para pruebas de los bloques A y B."),
    ("CWP-2.01-CIV-01", "Fase 2", "Cimentaciones bloque A", "CIV", 36000, date(2028, 2, 7), 11, "CWP-1.01-CIV-01", "Estructura bloque A", "Primer frente de la instalación principal."),
    ("CWP-2.01-EST-01", "Fase 2", "Estructura metálica bloque A", "EST", 9600, date(2028, 4, 25), 17, "CWP-2.01-CIV-01", "Estructura bloque A", "Requiere cimentaciones curadas y estructura fabricada (RAS)."),
    ("CWP-2.01-TUB-01", "Fase 2", "Tuberías de servicios bloque A", "TUB", 34000, date(2028, 8, 28), 26, "CWP-2.01-EST-01", "Agua de servicio", "Tuberías montadas sobre estructura terminada por niveles."),
    ("CWP-3.01-ARQ-01", "Fase 3", "Arquitectura edificio de oficinas", "ARQ", 22000, date(2029, 3, 5), 20, "CWP-1.02-TUB-01", "Edificio de oficinas", "Edificio independiente; permite adelantar su entrega."),
    ("CWP-3.02-CIV-01", "Fase 3", "Cimentaciones de la ampliación", "CIV", 28000, date(2029, 2, 5), 14, "CWP-2.01-CIV-01", "Estructura ampliación", "Inicia cuando la Fase 2 libera el acceso lateral del bloque B."),
    ("CWP-3.02-TUB-01", "Fase 3", "Empalmes a la galería de servicios", "TUB", 12000, date(2029, 7, 2), 12, "CWP-2.01-TUB-01", "Agua de servicio", "Empalmes durante parada programada de la Fase 2 (interfaz entre fases)."),
]
