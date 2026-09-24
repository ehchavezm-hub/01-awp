"""Módulos M9 a M13 (láminas 87 a 122)."""
from pptx.enum.text import PP_ALIGN

from . import fuentes as F
from .diseno import (AZUL, AZUL_MEDIO, GRIS_MEDIO, NARANJA, NARANJA_OSC, bloques, bloques_horizontales,
                     checklist, ciclo, cita, comparacion, dato, linea_tiempo, matriz2x2, notas, proceso, separador,
                     tabla)
from .especiales import barras_tool_time, cierre, organigrama, resumen_fases

CENTRO = PP_ALIGN.CENTER


def m9(d):
    d.pie = "M9 · ROLES Y ORGANIZACIÓN"
    s = separador(d, 9, "Módulo 9 · Roles y organización", "AWP redistribuye responsabilidades, no solo agrega cargos",
                  "Actores del proyecto, cargos nuevos y cómo cambian los roles tradicionales.")
    notas(s, """
Separador del Módulo 9. AWP crea dos cargos nuevos (AWP Champion y Workface Planner), pero su mayor efecto está en cómo cambian los roles existentes: propietario, EPC, Ingeniería, Compras, Construcción, Controles y supervisión de campo.
El curso 2023 recuerda que un componente central de AWP es la alineación: todos los miembros del equipo deben entender qué se espera de ellos.
""", f"{F.CUR} ('AWP Implications on Traditional Project Roles'); {F.OMG} (Typical roles).")

    s = organigrama(d, "Módulo 9 · Actores", "Cada actor tiene un papel en AWP")
    notas(s, """
Roles según Omega 365:
• Propietario o patrocinador: da respaldo corporativo, asegura la adopción de AWP por todos los actores y mantiene el foco en los resultados operativos.
• EPC/EPCM: lidera la planificación de la ejecución AWP, define y mantiene el POC, estructura las CWA y los CWP y coordina los entregables de ingeniería, compras y construcción.
• Ingeniería: desarrolla EWP alineados al POC, gestiona las dependencias entre disciplinas e incorpora los datos de proveedores.
• Compras y cadena de suministro: gestiona los PWP, las órdenes de compra y los datos de proveedores, alineando las entregas con las necesidades de construcción.
• Contratistas de construcción: desarrollan los IWP, ejecutan y retroalimentan la planificación.
• Comisionamiento y operaciones: definen las prioridades de sistemas, los SWP y los TOP.
• AWP Champion y equipo de soporte: integran AWP con los procesos de la empresa, capacitan e impulsan la mejora continua.
Omega 365 sugiere visualizar estas responsabilidades con diagramas de carriles (swim lanes).
""", f"{F.OMG} (Typical roles, responsibilities and organizational alignment; Integrating AWP with Existing Organizational Processes).")

    s = bloques(d, "Módulo 9 · AWP Champion", "El AWP Champion guía; no ejecuta por los demás", [
        ("rocket", "Adopción de AWP", "Lidera el cambio en la organización"),
        ("handshake", "Enlace con el propietario", "Punto de contacto AWP del contratista"),
        ("contract", "Subcontratistas", "Fija requisitos AWP y vigila su cumplimiento"),
        ("teach", "Mentor del equipo", "Guía, revisa y asegura el proceso"),
        ("helmet", "Workface Planning", "Supervisa su aplicación en obra")], cols=5, tam_titulo=14,
        nota="Errores al designarlo: asumir que es el gerente, subestimar su carga, ignorar su carrera y dejarlo solo.")
    notas(s, """
El curso 2023 describe cinco funciones del AWP Champion:
1) Adopción: lidera la adopción de AWP en la organización y actúa como agente de cambio.
2) Trabajo con propietarios: en empresas contratistas, es el punto de contacto para la coordinación AWP con el propietario.
3) Trabajo con subcontratistas: en el propietario o el contratista principal, establece los requisitos AWP para los subcontratistas y vigila su desempeño.
4) Trabajo con el equipo del proyecto: guía y mentoría; revisa que AWP se aplique según el procedimiento, como revisión de aseguramiento, y alinea a los actores (en especial Ingeniería y Compras) con el plan.
5) Workface Planning: supervisa la implementación de WFP en obra y comunica los requisitos a todos los contratistas.
El Procedimiento 1.0 añade: es el representante de la gerencia del proyecto que inicia y pilotea los procesos AWP, IM y WFP.
""", f"{F.CUR} ('Role of the AWP Champion', funciones 1-5; 'Common Pitfalls in Hiring the AWP Champion'); {F.P1} (§7).")

    s = bloques_horizontales(d, "Módulo 9 · Workface Planner",
                             "El Workface Planner es un oficio con experiencia, no un oficinista", [
                                 ("hammer", "Oficio con experiencia", "Entiende el trabajo que planifica"),
                                 ("helmet", "Supervisión en campo", "Varios años como supervisor"),
                                 ("laptop", "Computación básica", "Maneja el software WFP"),
                                 ("usertie", "Reporta al superintendente", "Uno por superintendente y disciplina"),
                                 ("ban", "Dedicación exclusiva", "Solo planifica, sin otras tareas"),
                                 ("grad", "Capacitación formal", "Curso de WFP tras incorporarse")])
    notas(s, """
La Quick Start Guide considera la creación del cargo de Workface Planner el componente crítico de WFP: un puesto adicional en la organización de construcción, dedicado a desarrollar los planes del capataz según la estrategia del superintendente.
Perfil típico: un trabajador de oficio que entiende el trabajo, con experiencia en supervisión y ejecución en campo y conocimientos básicos de computación; forma parte de la organización de construcción y reporta directamente al superintendente (cada superintendente tiene uno).
El Procedimiento 3.0 agrega: puede ser un técnico de oficio o de ingeniería con varios años de supervisión; solo arma IWP de su disciplina y se dedica exclusivamente a WFP; tiene una línea funcional con el WFP Coordinator del propietario, que entrevista, selecciona y capacita a los candidatos buscando un equipo con balance de experiencia, juventud y disciplinas.
Consejos prácticos de la Quick Start: inscríbalos en un curso de WFP, deles a leer el libro "Schedule for Sale" y prepare un área común con escritorios, computadoras y teléfonos.
""", f"{F.QS} (§5 Workface Planners); {F.P3} (§5 Workface Planners).")

    s = dato(d, "Módulo 9 · Dimensionamiento", "Un planificador por cada 50 trabajadores",
             "1 : 50", "un Workface Planner por cada 50 trabajadores",
             "Ajuste por complejidad: la instrumentación exige más planificación que el concreto o el movimiento de tierras.",
             apoyos=[("20 IWP", "al mes por planificador: 1 IWP por 10 trabajadores por semana, con 5 cuadrillas"),
                     ("80 → 2", "80 montadores de acero en el pico requieren 2 planificadores"),
                     ("−4 sem", "inicio de la generación de IWP antes de construir")], icono_nombre="users_o")
    notas(s, """
La proporción aproximada es de un planificador por cada 50 trabajadores de campo, con ajustes por complejidad: la instrumentación requiere más recursos de planificación que el vaciado de concreto o el movimiento de tierras (Quick Start).
El Procedimiento 3.0 da una regla de cálculo: 1 IWP por cada 10 trabajadores por semana × 5 cuadrillas = 20 IWP al mes = 1 Workface Planner. Su ejemplo para montadores de acero: con una dotación directa que sube de 25 a 80 personas, se necesitan 1 a 2 planificadores según el mes.
El WFP Coordinator elabora con el contratista una matriz por disciplina que relaciona la carga de personal (del cronograma de nivel 3), la cantidad de IWP necesarios y el número de planificadores. La generación de IWP comienza al menos 4 semanas antes de la ejecución.
""", f"{F.QS} (§5); {F.P3} (§5 Workface Planners: ejemplo 'Iron Workers').")

    s = bloques_horizontales(d, "Módulo 9 · Construction Manager", "El Construction Manager es dueño de AWP en la obra", [
        ("rocket", "Adopción", "Explica por qué se usa AWP"),
        ("route", "Path of Construction", "Lo lidera y reúne las restricciones"),
        ("hammer", "Constructabilidad", "Lidera las revisiones desde las fases tempranas"),
        ("file", "Entregables", "Revisa el desglose de paquetes y el estimado"),
        ("warning", "Restricciones", "Sigue fechas y el impacto de las abiertas")],
        nota="Si el Construction Manager no cree en AWP, la implementación será solo un trámite.")
    notas(s, """
El proceso AWP pertenece a Construcción y busca el mayor beneficio para la ejecución; por eso el papel del Construction Manager es crítico. El curso 2023 describe cinco funciones:
1) Adopción: entiende AWP y explica al equipo por qué se usa.
2) Path of Construction: es dueño del proceso; convoca a los actores para que planteen sus restricciones.
3) Constructabilidad: es dueño del proceso de constructabilidad desde las fases tempranas.
4) Entregables: participa en la revisión de entregables clave (desglose de paquetes, estimado) y en la definición de metas y beneficios de AWP.
5) Workface Planning: promueve WFP en obra, audita IWP, conversa con las cuadrillas y revisa el plan diario o el look-ahead por IWP.
El Education Framework añade su papel en las restricciones: sigue fechas planificadas frente a reales, vigila las cantidades retenidas y entiende la criticidad de las restricciones abiertas.
Consejo del curso: si el Construction Manager no entiende o no cree en AWP, la implementación será un trámite y no se obtendrán los beneficios.
""", f"{F.CUR} ('Role of the Construction Manager', 'Pro Tip!'); {F.FW} (Who is Involved in Constraint Management?).")

    s = tabla(d, "Módulo 9 · Supervisión de campo", "Superintendente, capataz general y capataz cambian su rutina",
              ["Nivel", "Supervisa a", "Qué cambia con AWP"],
              [["Superintendente", "Hasta 3 capataces generales",
                "Define la secuencia con el planificador y elige IWP del backlog para el look-ahead"],
               ["Capataz general (GF)", "Hasta 4 capataces",
                "Pide el material una semana antes, entrega los IWP y los recibe al terminar"],
               ["Capataz", "Unos 10 trabajadores", "Revisa su IWP, arma el plan diario y registra avance y demoras"]],
              [3.0, 3.1, 6.0], mono=(), tam=13, alto_fila=1.0,
              nota="Ratios de los procedimientos de Insight-AWP; el Glosario del CII usa otros (ver la lámina siguiente).")
    notas(s, """
Los procedimientos de Insight definen tres niveles de supervisión de campo, con ratios que varían según la complejidad y pueden adaptarse a la norma local:
• Capataz (Foreman): supervisa directamente una cuadrilla de una disciplina, típicamente 1 capataz por 10 trabajadores. Con AWP revisa su IWP antes del inicio, arma su plan diario en la reunión de alineación de 15 minutos y registra el avance y las demoras.
• Capataz general (General Foreman, GF): supervisa hasta 4 capataces de una disciplina. Pide el material de cada IWP una semana antes, entrega el IWP al capataz y lo devuelve al planificador al terminar.
• Superintendente: supervisa hasta 3 capataces generales de una disciplina. Describe al planificador cómo dividir y secuenciar el CWP, aprueba los IWP, mantiene el backlog y elige cada semana los IWP del look-ahead.
El curso 2023 menciona también los cambios para la alta gerencia, Ingeniería, Compras, Controles (misma WBS y nomenclatura), Materiales, Calidad, Seguridad y Operaciones.
""", f"{F.P3} (§2 Field Supervision; §14 y §15); {F.QS} (§6-§7); {F.CUR} ('AWP Implications on Traditional Project Roles').")

    s = comparacion(d, "Módulo 9 · Ratios", "Los ratios de supervisión difieren entre fuentes: defina los suyos",
                    dict(titulo="Insight-AWP (2017)", color=AZUL, numerado=False,
                         puntos=[("Capataz: unos 10 trabajadores", "Una cuadrilla de una disciplina"),
                                 ("Capataz general: hasta 4 capataces", "En una sola disciplina"),
                                 ("Superintendente: hasta 3 GF", "En una sola disciplina")]),
                    dict(titulo="Glosario del CII (2021)", color=NARANJA, numerado=False,
                         puntos=[("Capataz: una cuadrilla", "Supervisión directa del trabajo"),
                                 ("Capataz general: hasta 5 capataces", "En una sola disciplina"),
                                 ("Superintendente: hasta 4 GF", "En una sola disciplina")]),
                    nota="Los ratios dependen de la complejidad y la criticidad del trabajo: fíjelos en el procedimiento.")
    notas(s, """
Las fuentes difieren en la amplitud de control de la supervisión:
• Procedimientos de Insight-AWP (2017): capataz general hasta 4 capataces; superintendente hasta 3 capataces generales; capataz con unos 10 trabajadores.
• Glosario del CII (CII-EOC, marzo de 2021): capataz general hasta 5 capataces; superintendente hasta 4 capataces generales.
Ambas fuentes aclaran que los ratios dependen de la complejidad y lo crítico de las tareas. Como la cantidad de planificadores se vincula a los superintendentes (al menos uno por superintendente), esta decisión afecta también al dimensionamiento del equipo de WFP.
""", f"{F.P3} (§2 Field Supervision); {F.GLO} (Superintendent, General Foreman); {F.IDX} §3.")

    s = tabla(d, "Módulo 9 · Matriz de responsabilidades", "Matriz de responsabilidades AWP por entregable: una propuesta",
              ["Entregable", "Propietario", "Champion", "Ingeniería", "Compras", "Construcción"],
              [["Plan AWP y procedimientos", "A", "R", "C", "C", "C"],
               ["Path of Construction", "A", "C", "C", "C", "R"],
               ["EWP", "I", "C", "R", "I", "C"],
               ["PWP", "I", "I", "C", "R", "I"],
               ["CWP", "A", "C", "C", "I", "R"],
               ["IWP", "I", "C", "I", "I", "R"],
               ["SWP y TOP", "A", "C", "C", "I", "R"]],
              [3.6, 1.7, 1.7, 1.7, 1.7, 1.7], mono=(1, 2, 3, 4, 5), tam=14,
              alinear_col={1: CENTRO, 2: CENTRO, 3: CENTRO, 4: CENTRO, 5: CENTRO},
              nota="R: responsable · A: aprueba · C: consultado · I: informado. Ajústela a su modelo de contrato.")
    notas(s, """
Esta matriz es una propuesta de síntesis, no una tabla de una fuente única. Se construyó a partir de:
• Procedimiento 1.0 de Insight (§5): Ingeniería desarrolla y entrega los EWP en la secuencia correcta; Compras gestiona la fabricación secuencial e incluye AWP en los contratos; la gerencia de construcción mapea el POC y define los CWP; la gerencia del proyecto exige AWP en los contratos y nombra al Champion.
• Omega 365: el EPC/EPCM mantiene el POC; los contratistas de construcción desarrollan los IWP; comisionamiento y operaciones definen SWP y TOP.
• Curso 2023: el Construction Manager es dueño del POC; los EWP los prepara el contratista de Ingeniería.
En la columna Construcción se agrupan la gerencia de construcción y los contratistas; separe ambos si su modelo de contrato lo requiere. Úsela como punto de partida para el taller de roles del proyecto.
""", f"{F.P1} (§5 Key Stakeholder Deliverables); {F.OMG} (roles); {F.CUR} (roles del POC y de los EWP). Síntesis propia.")


def m10(d):
    d.pie = "M10 · MEDICIÓN: KPIs, CONTROLES Y PRODUCTIVIDAD"
    s = separador(d, 10, "Módulo 10 · Medición", "Lo que no se mide en paquetes no se mejora",
                  "Indicadores de ingeniería y de construcción, valor planificado, tool time y auditorías.")
    notas(s, """
Separador del Módulo 10. Los indicadores clave de desempeño (KPI, Key Performance Indicators) permiten evaluar la "salud" de la implementación de AWP y su efectividad en el proyecto.
En este módulo: las dos familias de KPI, el valor planificado por IWP, los estudios de tool time y las auditorías del proceso.
""", f"{F.CUR} (Lección 'Monitoring AWP KPIs').")

    s = comparacion(d, "Módulo 10 · KPI", "Hay dos familias de indicadores (KPI): de Ingeniería y de Construcción",
                    dict(titulo="KPI de Ingeniería", color=AZUL, numerado=False,
                         puntos=[("FEL: lista de entregables", "Alineada al procedimiento AWP del propietario"),
                                 ("Ejecución en curso", "Reglas de crédito por EWP"),
                                 ("Ejecución completada", "Planes de liberación de EWP y CWP")]),
                    dict(titulo="KPI de Construcción", color=NARANJA, numerado=False,
                         puntos=[("IWP listos frente al total", "Salud del backlog"),
                                 ("Cierre de restricciones", "Tasa de cierre y antigüedad"),
                                 ("Cumplimiento del plan", "IWP a tiempo y productividad por disciplina")]),
                    nota="La salud de AWP se mide en ambas fases: un atraso en Ingeniería anticipa uno en campo.")
    notas(s, """
El curso 2023 divide los KPI de AWP en dos familias:
• KPI de Ingeniería: en las etapas FEL, toman la forma de una lista de verificación de entregables, desarrollada en el plan AWP y alineada al procedimiento del propietario. En la ejecución, mientras la ingeniería avanza, se mide con las reglas de crédito de cada EWP; cuando se completa, se sigue con los planes de liberación de EWP y CWP (fechas planificadas frente a reales).
• KPI de Construcción: validan el esfuerzo de Workface Planning y el cumplimiento de metas. Omega 365 menciona tableros con IWP listos frente al total, tasa de cierre de restricciones, avance hacia RFCC/RFOC, porcentaje de plan completado (PPC) y productividad por disciplina.
Nota: las listas detalladas de KPI de campo del curso 2023 se perdieron en la conversión; la lámina 99 las reconstruye con Omega 365 y los procedimientos.
""", f"{F.CUR} ('Two Primary Types of AWP KPIs', 'Engineering KPIs'); {F.OMG} (Features: dashboards y KPI); {F.IDX} §4.3.")

    s = tabla(d, "Módulo 10 · Liberaciones", "En Ingeniería, compare liberaciones planificadas con reales",
              ["Paquete", "Planificado", "Real", "Desvío", "Estado"],
              [["EWP-12-C01", "15-feb", "14-feb", "−1 d", "A tiempo"],
               ["EWP-12-S02", "01-mar", "08-mar", "+7 d", "Atrasado"],
               ["EWP-13-P03", "20-mar", "20-mar", "0 d", "A tiempo"],
               ["CWP-12-C01", "01-mar", "28-feb", "−1 d", "A tiempo"],
               ["CWP-12-S02", "15-mar", "29-mar", "+14 d", "Atrasado"]],
              [3.0, 2.3, 2.3, 2.0, 2.5], destacar={1, 4}, mono=(0, 3), tam=14, alto_fila=0.6,
              nota="Ejemplo ilustrativo: los 7 días de atraso del EWP se convierten en 14 días de atraso en su CWP.",
              icono_nota="warning_o")
    notas(s, """
Durante la ejecución, cuando los paquetes de Ingeniería se completan, se siguen con el plan de liberación de EWP y el de CWP. Estas hojas deben contener las fechas planificadas (tomadas del cronograma EPC aprobado) y las reales, para medir el desempeño.
El ejemplo es ilustrativo: muestra cómo un atraso de 7 días en un EWP de acero se amplifica en el CWP que depende de él, porque el CWP no puede empezar hasta que el EWP se libera y además requiere la revisión de Construcción.
Úselo para explicar por qué el plan de liberación es un indicador adelantado de los problemas de campo.
""", f"{F.CUR} ('Engineering KPIs - Execute Stage - Complete'; 'Managing EWPs / CWPs - The Release Plan'). Datos del ejemplo: ilustrativos.")

    s = bloques(d, "Módulo 10 · KPI de campo", "En campo, mida IWP listos, restricciones cerradas y plan cumplido", [
        ("clipcheck", "IWP listos frente al total", "Cuántos paquetes están libres de restricciones"),
        ("unlock", "Cierre de restricciones", "Tasa de cierre y restricciones vencidas"),
        ("hourglass", "Días de backlog", "Horas libres ÷ horas ganadas por día"),
        ("calendar", "IWP completados a tiempo", "Dentro de su ventana de ejecución"),
        ("percent", "Plan completado (PPC)", "Compromisos cumplidos en la semana"),
        ("gauge", "Productividad por disciplina", "Horas reales frente a valor ganado")], cols=3)
    notas(s, """
KPI de Construcción recomendados, reconstruidos a partir de las fuentes:
• IWP listos frente al total, tasa de cierre de restricciones, porcentaje de plan completado (PPC, Percent Plan Complete) y productividad por disciplina: tableros de Omega 365.
• Días de backlog: cálculo del curso 2023 (horas de IWP libres ÷ horas que gana la dotación por día).
• IWP completados dentro de su ventana y devueltos: el Pack Track del Procedimiento 3.0 registra cuántos IWP de cada CWP se emitieron a campo y se devolvieron.
El curso 2023 menciona también estadísticas generales, como las fechas de emisión planificadas y reales de cada paquete y las horas en obra por IWP.
""", f"{F.OMG} (dashboards: IWPs ready vs total, constraint closure rate, Percent Plan Complete, productivity per discipline); {F.CUR} ('How to Calculate Backlog', 'Construction KPIs'); {F.P3} (§7 Pack Track).")

    s = proceso(d, "Módulo 10 · Valor planificado", "El valor planificado se calcula por IWP con tasas estándar", [
        ("calendar", "Planificación por olas", "CWP → IWP no antes de 3 meses de su ejecución"),
        ("calculator", "Valor planificado", "Cantidades IFC × tasas estándar de instalación"),
        ("clock", "Horas por IWP", "Las hojas de tiempo usan el IWP como código de costo"),
        ("chart", "Avance físico", "El capataz registra los componentes instalados")],
        nota=("Regla: ", "cantidad × tasa = horas; horas ÷ dotación = duración realista."))
    notas(s, """
Según la Quick Start Guide (§8A), empaquetar el trabajo con anticipación crea una base sólida para los controles del proyecto. La clave: desarrollar los CWP en IWP no antes de tres meses de su ejecución (cronograma por olas o rolling wave); calcular el valor planificado con los planos IFC y tasas estándar de instalación; codificar las hojas de tiempo con el número de IWP; y hacer que los capataces registren el avance físico por componente. El resultado son datos precisos y oportunos que forman una sola versión de la verdad.
El Procedimiento 2.0 asigna a Controles establecer un estándar único de tasas de instalación y reglas de crédito, y prevé un estimado de presupuesto (±10 %) cuando el CWP se emite IFC, con cantidades del modelo 3D.
El curso 2023 resume la lógica del estimado alineado a la WBS: cantidad × tasa de colocación = horas; horas ÷ dotación = duración.
""", f"{F.QS} (§8A Project Controls); {F.P2} (§8 Project Controls); {F.CUR} ('Building an AWP-Based Estimate').")

    s = barras_tool_time(d, "Módulo 10 · Productividad", "El tool time pasa de 37 % a 46 % con AWP")
    notas(s, """
El tool time, o tiempo en herramientas, es el porcentaje de la jornada en que el trabajador está instalando. Es el indicador principal de productividad en campo.
Según el Education Framework del CII, en proyectos tradicionales es del 37 % (3,7 h de una jornada de 10 h) y con AWP sube al 46 % (4,6 h); el curso 2023 cita 47 %. El resto del tiempo se pierde esperando información, materiales, herramientas o accesos, en traslados o en pausas.
0,9 h adicionales de trabajo efectivo por persona y día equivalen a un aumento de productividad de alrededor del 24-25 %, coherente con el +25 % que reportan los estudios del CII.
Cómo medirlo: el Procedimiento 3.0 recomienda estudios de tool time realizados por terceros cada 2 o 3 meses. Son una "nota" para la gerencia, no para los trabajadores: miden si se entregan a tiempo información, herramientas, materiales y acceso.
""", f"{F.FW} (Benefits & Value of AWP: 37 % frente a 46 %); {F.CUR} (Lección 2: Tool Time 37 % / 47 %); {F.P3} (§18 Tool Time Studies).")

    s = proceso(d, "Módulo 10 · Auditorías", "Audite el proceso AWP, no solo el cronograma", [
        ("eye", "Revisión independiente", "Revisión «en frío» (cold eyes) del plan de WFP"),
        ("listcheck", "Auditoría periódica", "Con la plantilla de auditoría de WFP"),
        ("file", "Informe semanal", "Tablero del Pack Track en el informe de gestión"),
        ("group", "Comité mensual", "Resuelve los problemas entre actores")],
        nota="El procedimiento es la vara de medida: se escribió también para poder auditarlo.")
    notas(s, """
Los procedimientos de Insight incluyen auditorías como parte del ciclo. El Procedimiento 3.0 declara que el documento guía la implementación del contratista y luego se usa periódicamente para auditar su cumplimiento (§1 y §19).
El Toolbox incluye plantillas para una revisión independiente del plan de WFP (SD01, WFP Cold Eyes Review) y para la auditoría (SD07, WFP Audit Template); el INDICE.md advierte que el Procedimiento 3.0 intercambia por error las referencias SD06 y SD07.
El WFP Coordinator prepara cada semana un tablero desde el Pack Track para el informe de gestión, y el comité de dirección de WFP se reúne mensualmente para plantear y resolver problemas durante todo el proyecto.
La Quick Start Guide recuerda que los procedimientos crean la expectativa de cumplimiento y facilitan las auditorías posteriores.
""", f"{F.P3} (WFP Toolbox; §1; §7; §19 Audits); {F.P1} (§11); {F.QS} (§2); {F.IDX} §4.2.")


def m11(d):
    d.pie = "M11 · ESCALAR Y ADOPTAR AWP"
    s = separador(d, 11, "Módulo 11 · Escalar y adoptar", "AWP se ajusta al tamaño del proyecto",
                  "AWP escalable, paradas de planta, relación con Lean y respuestas a las objeciones.")
    notas(s, """
Separador del Módulo 11. Muchas empresas empezaron a aplicar AWP en proyectos grandes y luego quisieron llevar sus beneficios a proyectos menores. Este módulo trata el modelo de AWP escalable de la COAA, la diferencia de plazos para paradas de planta, la relación con Lean Construction y las objeciones más comunes con sus respuestas.
""", f"{F.FW} (Scaling AWP; Overcoming Common AWP Objections); {F.LC}.")

    s = dato(d, "Módulo 11 · AWP escalable", "AWP también sirve para proyectos de menos de USD 100 millones",
             "< 100 M", "de dólares: rango del AWP escalable",
             "La COAA diseñó en 2019 un modelo de AWP escalable que no renuncia a sus principios.",
             apoyos=[("2019", "año del modelo escalable de la COAA"),
                     ("40", "profesionales de la industria en cuatro comités de trabajo"),
                     ("A–D", "categorías según familiaridad y complejidad")], icono_nombre="stairs_o", tam_cifra=100)
    notas(s, """
Según el Education Framework del CII, la COAA recibió pedidos para desarrollar una guía de AWP escalable aplicable a proyectos de menos de USD 100 millones sin comprometer los principios que mejoran el desempeño.
El resultado es el informe "COAA Scalable Advanced Work Packaging Model Report", desarrollado por cuatro comités de trabajo con 40 profesionales de la industria y un comité directivo de 5 miembros, basado en el trabajo del CII y la COAA. El modelo se diseñó en 2019, incluye proyectos de ejemplo y herramientas desarrolladas por expertos, y está pensado para distintos tipos, tamaños, complejidades y sectores.
Nota: el repositorio solo contiene extractos del informe; no incluye la herramienta de clasificación ni el detalle de las categorías.
""", f"{F.FW} (Scaling AWP; COAA Scalable AWP); {F.IDX} §4.3.")

    s = matriz2x2(d, "Módulo 11 · Categorías", "Familiaridad y complejidad definen cuánto AWP necesita",
                  "FAMILIARIDAD  →", "COMPLEJIDAD  →", [
                      ("C", "Poco familiar · alta complejidad", "Tipo de proyecto nuevo para la empresa y complejo", NARANJA),
                      ("D", "Familiar · alta complejidad", "Complejo, pero ya hecho antes por el mismo equipo (programa)",
                       NARANJA_OSC),
                      ("A", "Poco familiar · baja complejidad", "Simple, pero nuevo para la empresa", AZUL_MEDIO),
                      ("B", "Familiar · baja complejidad", "Simple y repetido: un programa de proyectos", AZUL)],
                  nota_lateral=["Una herramienta de clasificación (screening tool) ubica al proyecto con una serie de preguntas.",
                                "El modelo escala hacia arriba o hacia abajo el mismo diagrama de flujo integrado de AWP.",
                                "Los proyectos familiares se tratan como programa: reutilizan plantillas y aprendizajes."])
    notas(s, """
El informe de AWP escalable de la COAA identifica dos factores que cambian las prácticas de entrega:
• Familiaridad: si el tipo de proyecto es nuevo para la empresa, se considera poco familiar; si el mismo equipo ya lo hizo, es familiar.
• Complejidad: de extremadamente simple a extremadamente complejo.
Con ellos define cuatro categorías: A, poco familiar y de baja complejidad (proyecto); B, familiar y de baja complejidad (programa); C, poco familiar y de alta complejidad (proyecto); D, familiar y de alta complejidad (programa).
Una herramienta de clasificación (screening tool) con una serie de preguntas determina la categoría. El modelo usa el diagrama de flujo integrado del ciclo de vida de la mejor práctica AWP, formateado para escalarlo según familiaridad y complejidad.
El repositorio no contiene el detalle de qué actividades se simplifican en cada categoría; consulte el informe de la COAA.
""", f"{F.FW} (COAA Scalable AWP Model and Report; Key Excerpts: categorías A-D); {F.IDX} §4.3.")

    s = comparacion(d, "Módulo 11 · Paradas de planta", "Paradas de planta: el mismo ciclo, más corto",
                    dict(titulo="Parada de planta o proyecto pequeño", color=NARANJA, flechas=False,
                         puntos=[("IWP iniciado", "6 semanas antes"), ("Restricciones identificadas", "4 semanas antes"),
                                 ("Restricciones asignadas", "3 semanas antes"), ("Restricciones liberadas", "2 semanas antes")]),
                    dict(titulo="Megaproyecto", color=AZUL, flechas=False,
                         puntos=[("IWP iniciado", "12 semanas antes"), ("Restricciones identificadas", "10 semanas antes"),
                                 ("Restricciones asignadas", "8 semanas antes"), ("Restricciones liberadas", "4 semanas antes")]),
                    nota="Mismo proceso, distinto horizonte: ajuste el calendario al tamaño, no los pasos.")
    notas(s, """
El Education Framework del CII muestra el calendario típico de restricciones de un IWP según el tamaño o tipo de proyecto. En una parada de planta (shutdown o turnaround) o un proyecto pequeño, el ciclo completo cabe en 6 semanas; en un proyecto grande, mega o giga, se extiende a 12.
Los pasos no cambian: iniciar el IWP, identificar las restricciones, asignarlas a un responsable y liberarlas antes de entregar el paquete. Lo que cambia es el horizonte.
Las paradas de planta (STO/SDTA/STA en el Glosario del CII) son proyectos en los que se detiene la operación de una planta o de parte de ella para reparaciones, mantenimiento, ampliaciones o mejoras; su duración corta hace aún más valiosa la preparación previa de paquetes.
""", f"{F.FW} (Typical IWP Constraint Schedule by Project Size / Type); {F.GLO} (Shutdown / Turnaround).")

    s = comparacion(d, "Módulo 11 · AWP y Lean", "AWP y Lean Construction se complementan",
                    dict(titulo="AWP", color=NARANJA, numerado=False,
                         puntos=[("Planificadores dedicados", "Con experiencia de oficio o de ingeniería de campo"),
                                 ("Restricciones con proceso formal", "Útil en instalaciones muy técnicas"),
                                 ("Avance frente al plan", "Valor ganado y cumplimiento del cronograma")]),
                    dict(titulo="Lean · Last Planner System", color=AZUL, numerado=False,
                         puntos=[("El «último planificador»", "Capataces y superintendentes planifican juntos"),
                                 ("Compromisos confiables", "Conversaciones facilitadas y muy visuales"),
                                 ("Flujo y adaptabilidad", "Confiabilidad del flujo de trabajo")]),
                    nota="La eliminación rigurosa de restricciones de WFP puede reforzar el Last Planner System.")
    notas(s, """
El informe especial 22-01c del CII, elaborado con el Lean Construction Institute (LCI) en 2023, compara AWP con Lean Construction y su Last Planner System (LPS).
• Quién planifica: en AWP, planificadores dedicados con experiencia de oficio o de ingeniería de campo, a partir de un POC desarrollado en sesiones interactivas. En Lean, los capataces y superintendentes conversan directamente para mapear el trabajo próximo, a menudo con facilitadores, centrados en compromisos confiables más que en asignaciones. Lean insiste en no separar "planificar" de "hacer".
• Restricciones: el proceso de WFP es más estructurado y puede ser más adecuado para instalaciones muy técnicas; puede complementar el esfuerzo del LPS.
• Avance: AWP compara el avance real con el plan original; Last Planner pone el acento en la adaptabilidad y la confiabilidad del flujo.
Mensaje: no son excluyentes; muchas empresas combinan ambos.
""", f"{F.LC} (temas 1, 2, 5 y 6).")

    s = tabla(d, "Módulo 11 · AWP frente a Lean", "Once temas muestran dónde coinciden y dónde difieren",
              ["Tema", "Coincidencia o diferencia"],
              [["1 · Quién planifica", "AWP: planificadores dedicados · Lean: el «último planificador», cerca del trabajo"],
               ["2 · Programador maestro", "Lean limita el detalle temprano; WFP puede reforzar la eliminación de restricciones"],
               ["3 · Quién ejecuta", "Mismo enfoque, con técnicas distintas"],
               ["4 · Empaquetamiento", "Lean/IPD ya usa paquetes; cambian el momento y la participación de los oficios"],
               ["5 · Restricciones", "El proceso de WFP es más estructurado, útil en montajes técnicos"],
               ["6 · Avance", "AWP compara con el plan; Lean prioriza la confiabilidad del flujo"],
               ["7 · KPI", "Lean se centra en el flujo más que en el valor ganado"],
               ["8 · Alineación", "AWP integra documentos; IPD integra equipos"],
               ["9 · Organización", "IPD distribuido frente a una estructura jerárquica en AWP"],
               ["10 · Seguridad y calidad", "Ambos las priorizan; Lean amplía la seguridad a la salud mental"],
               ["11 · Puesta en marcha", "AWP le presta cada vez más atención"]],
              [3.5, 8.6], mono=(), tam=11.5)
    notas(s, """
Resumen de los once temas del informe CII/LCI 22-01c:
1) Quién planifica: planificadores dedicados en AWP; el "último planificador" en Lean.
2) Rol del programador maestro: limitar el detalle temprano del cronograma maestro (LPS) evita sobrestimar su certeza; la eliminación de restricciones de WFP puede complementarlo.
3) Quién ejecuta: el mismo enfoque con técnicas distintas.
4) Cómo se empaqueta: algunos proyectos Lean/IPD (Integrated Project Delivery) ya usan paquetes muy parecidos; la diferencia es cuándo se desarrollan y cuánto participan los oficios ("Big Room").
5) Restricciones: WFP más estructurado.
6) Avance: plan frente a flujo.
7) KPI: la crítica Lean a AWP es su foco en el valor ganado frente a la gestión del flujo.
8) Alineación: AWP integra documentos (IWP para las cuadrillas); IPD integra equipos que producen los documentos que necesitan.
9) Organización: marco distribuido de Lean/IPD frente al mando jerárquico asociado a AWP.
10) Seguridad y calidad: ambos las priorizan.
11) Puesta en marcha: AWP le presta más atención recientemente.
Advertencia: en el archivo, algunos títulos de tema están desfasados y varios textos truncados; se usó el orden de las comparaciones.
""", f"{F.LC} (Comparison Topics 1-11); {F.IDX} §4.1.")

    s = tabla(d, "Módulo 11 · Objeciones", "Doce objeciones frecuentes tienen respuesta",
              ["Objeción", "Respuesta breve"],
              [["«No tengo suficiente gente»", "Sin compromiso de la organización, el programa fracasa en el proyecto"],
               ["«Así no trabaja Ingeniería»", "Casi no afecta su productividad: cambia el orden de los entregables"],
               ["«Es muy difícil o complejo»", "Los clientes exigen entregas más inteligentes; quien no innova, desaparece"],
               ["«Nuestro proceso está bien»", "El 70 % de los proyectos termina sobre presupuesto y con retraso"],
               ["«No tengo la tecnología»", "Los sistemas integrados permiten hacer más con menos personal"],
               ["«AWP es una moda»", "Es mejor práctica del CII y la COAA y requisito de grandes clientes"],
               ["«No sirve para mi proyecto»", "El concepto se aplica a cualquier proyecto: es escalable"],
               ["«No tengo tiempo para aprender»", "Hay recursos de formación disponibles, incluido apoyo del CII"],
               ["«Mi proyecto es muy pequeño»", "El modelo escalable de la COAA responde a este caso"],
               ["«Mi proyecto está muy avanzado»", "Aplique al menos WFP con gestión de restricciones por IWP"],
               ["«Es un contrato a suma alzada»", "Mejor aún: más productividad y menos costo elevan su margen"],
               ["«Ya hacemos AWP»", "AWP abarca desde la planificación temprana hasta el comisionamiento"]],
              [4.0, 8.1], mono=(), tam=11.5)
    notas(s, """
El Education Framework del CII responde doce objeciones frecuentes:
1) "No tengo suficiente gente": hay que comprometerse con AWP a nivel de organización; si no, fracasa en el proyecto. Quien dice no tener gente, en general no se ha comprometido.
2) "Así no trabaja Ingeniería": es una falacia; el impacto en su productividad es pequeño, puede seguir diseñando por sistemas y cambia la distribución y prioridad de los entregables.
3) "Es muy difícil": los clientes piden entregas más inteligentes; las empresas que no innovan dejan de existir.
4) "Nuestro proceso está bien": 70 % de los proyectos termina sobre presupuesto y con retraso; 52 % termina en el 189 % de su presupuesto.
5) "No tengo la tecnología": los sistemas integrados permiten controlar más con menos personal.
6) "Es una moda": es mejor práctica reconocida por el CII y la COAA y requisito de muchos clientes de petróleo, gas y química.
7) "No sirve para mi proyecto" y 9) "es muy pequeño": el concepto es escalable.
8) "No tengo tiempo": hay recursos disponibles y el CII desarrolla un servicio de acompañamiento.
10) "Está muy avanzado": si cambiar el rumbo es costoso, gestione al menos las restricciones de los IWP con WFP.
11) "Suma alzada": más seguridad, productividad y menor costo aumentan el margen.
12) "Ya hacemos AWP": muchos no dimensionan su alcance completo.
""", f"{F.FW} (Overcoming Common AWP Objections).")

    s = cita(d, "Módulo 11 · La objeción más peligrosa", "«Ya hacemos AWP» es la objeción más peligrosa",
             "“Muchas empresas no dimensionan el alcance de AWP: es un método de entrega completo, que va desde la "
             "planificación temprana hasta el comisionamiento.”", "EDUCATION FRAMEWORK DEL CII · RESPUESTA A LA OBJECIÓN",
             puntos=[("route", "¿Hay un POC firmado en la compuerta 3?"),
                     ("hourglass", "¿Cuántos días de backlog libre tiene cada disciplina?"),
                     ("listcheck", "¿Dónde está el Pack Track de esta semana?")])
    notas(s, """
Es la objeción más peligrosa porque cierra la conversación. El Education Framework responde que muchas empresas tienen una idea equivocada del alcance de AWP: no se dan cuenta de que es un método integral de entrega de proyectos, desde la planificación temprana hasta el comisionamiento.
El curso 2023 (lección 3, "Espere resistencia") añade que muchas personas, sobre todo en Construcción, se ponen a la defensiva y dicen que ya lo hacen. Conviene reconocer que AWP no es un concepto totalmente nuevo: toma lo mejor de lo que ya se hace y lo estandariza.
Use las tres preguntas de la lámina para verificarlo: si no hay POC firmado, backlog medido ni Pack Track actualizado, lo que se hace es planificación de campo, no AWP.
""", f"{F.FW} (objeción 'We already do AWP'); {F.CUR} (AWP Related Lessons Learned, lección 3).")


def m12(d):
    d.pie = "M12 · ERRORES COMUNES Y LECCIONES APRENDIDAS"
    s = separador(d, 12, "Módulo 12 · Errores y lecciones", "Otros ya cometieron estos errores",
                  "Lecciones aprendidas de proyectos que implementaron AWP y los errores más caros.")
    notas(s, """
Separador del Módulo 12. El curso 2023 dedica una lección a las lecciones aprendidas en la implementación de AWP. Aquí se presentan junto con una síntesis de los errores más costosos que se desprenden de todas las fuentes.
""", f"{F.CUR} (AWP Related Lessons Learned).")

    s = cita(d, "Módulo 12 · Lección 1", "AWP es un camino: no saldrá perfecto la primera vez",
             "“No lo hará todo bien la primera vez. Aprenda de los tropiezos y celebre los avances.”",
             "CURSO AWP 2023 · LECCIÓN APRENDIDA 1 (ADAPTACIÓN)",
             puntos=[("bulb", "Registre lo que no funcionó"), ("trophy", "Celebre las mejoras visibles"),
                     ("cycle", "Ajuste el procedimiento en cada proyecto")])
    notas(s, """
Lección 1 del curso 2023: AWP es un camino (a journey). No saldrá todo bien la primera vez; lo importante es aprender de lo que no funciona y reconocer los avances.
Relaciónelo con la lámina de mejora continua (118): el registro de lecciones empieza en el seminario de arranque y alimenta al proyecto siguiente.
""", f"{F.CUR} (AWP Related Lessons Learned, lección 1: 'AWP is a Journey').")

    s = proceso(d, "Módulo 12 · Lección 2", "Gatear, caminar, correr: implemente por etapas", [
        ("baby", "Gatear", "Primer proyecto: CWP más precisos para licitar y un IWP piloto"),
        ("walk", "Caminar", "WFP completo: restricciones, backlog y look-ahead en toda la obra"),
        ("run", "Correr", "AWP de extremo a extremo: POC en FEL 2, EWP y PWP en secuencia")],
        nota="No hace falta hacerlo todo de inmediato: algunas empresas empezaron solo con CWP mejores.")
    notas(s, """
Lección 2 del curso 2023: no hace falta abordar todo de inmediato. Algunas empresas eligieron un enfoque de "gatear, caminar, correr".
El ejemplo de etapas de la lámina es una propuesta basada en las fuentes: el curso 2023 cuenta que algunas empresas empezaron su camino AWP con el objetivo de producir CWP más precisos para usarlos como paquetes de licitación, con excelentes resultados; el Framework recuerda que, si el proyecto está avanzado, al menos puede aplicarse WFP con gestión de restricciones por IWP.
Adapte las etapas a la madurez de su empresa y a la categoría del proyecto (lámina 105).
""", f"{F.CUR} (lección 2: 'Crawl, Walk, Run'; 'The Value of a Good CWP'); {F.FW} (objeción 'My project is too far along').")

    s = bloques(d, "Módulo 12 · Lecciones 3 y 6", "Espere resistencia y respóndala con un lenguaje común", [
        ("comments", "«Lo hacemos hace años»", "Reconozca lo que ya hacen: AWP estandariza las mejores prácticas"),
        ("grad", "Capacitación constante", "Enseñe el idioma de AWP a todos los equipos"),
        ("book", "Úselo en todo", "En reuniones, documentos y correspondencia")],
        nota="Un vocabulario común alinea al equipo y genera adhesión a la cultura AWP.")
    notas(s, """
Lección 3 del curso 2023, "Espere resistencia": mucha gente, en especial en Construcción, se pone a la defensiva y dice que ya lo hace. Es importante recordar que AWP no es un concepto totalmente nuevo: toma lo mejor de lo que ya se hace y lo ordena. La nota del curso lo dice así: "no decimos que lo estén haciendo mal; solo estandarizamos los mejores métodos de la industria".
Lección 6, "Capacitación, capacitación, capacitación": enseñe a los equipos el lenguaje de AWP y úselo en reuniones, documentos y correspondencia. Que todos usen la misma terminología es una gran ventaja para alinear al equipo y lograr adhesión a la cultura AWP.
""", f"{F.CUR} (lecciones 3 y 6; 'Note...' en 'Understanding the Process of Workface Planning').")

    s = comparacion(d, "Módulo 12 · Lecciones 4 y 5",
                    "Un contratista novato con ganas vale más que un «experto» que no practica",
                    dict(titulo="El «experto» de papel", color=GRIS_MEDIO, icono_res="xmark_g", numerado=False,
                         puntos=[("Dice dominar AWP", "Asiente cuando se le pregunta"),
                                 ("Envía procedimientos impecables", "Pero no los aplica en la obra"),
                                 ("No acepta aprender", "Resiste los cambios del propietario")],
                         resultado="Riesgo alto de simular el proceso"),
                    dict(titulo="El novato dispuesto", color=NARANJA, icono_res="check_o", numerado=False,
                         puntos=[("Reconoce lo que no sabe", "Pide apoyo y capacitación"),
                                 ("Aplica el procedimiento del propietario", "Con acompañamiento del Champion"),
                                 ("Aprende en el proyecto", "Mejora semana a semana")],
                         resultado="Un socio para implementar AWP de verdad"))
    notas(s, """
Lección 4 del curso 2023, "Contratistas expertos": muchos contratistas, cuando se les pregunta por su experiencia en AWP, asienten y dicen ser expertos; algunos incluso envían procedimientos muy bien escritos. Pero la única forma real de saberlo es sentarse a conversar con ellos.
Lección 5, "Contratistas novatos": no ser experto en AWP no debería excluir a un contratista de la licitación o del proyecto. Es mejor trabajar con un novato que quiere aprender el proceso que con uno que dice ser experto pero no lo aplica.
Conecte con la lámina 31: la entrevista forma parte de la evaluación de ofertas.
""", f"{F.CUR} (lecciones 4 y 5); {F.P1} (§10 Bid Assessments).")

    s = tabla(d, "Módulo 12 · Errores caros", "Los siete errores más caros al implementar AWP",
              ["Error", "Consecuencia", "Cómo evitarlo"],
              [["Champion a medio tiempo", "Nadie impulsa el cambio", "Rol dedicado desde FEL 2"],
               ["POC tardío o sin firmar", "Ingeniería diseña en su propio orden", "POC como entregable de la compuerta 3"],
               ["IWP con restricciones abiertas", "Cuadrillas esperando en el frente", "Regla de oro y firmas de liberación"],
               ["Sin backlog antes de movilizar", "Cuadrillas sin trabajo listo", "Planificadores antes que cuadrillas"],
               ["Software antes que proceso", "Herramienta cara y subutilizada", "Personas y proceso primero"],
               ["Sin cláusula contractual", "El contratista no está obligado", "Procedimiento WFP en la licitación"],
               ["Sin medición", "No se sabe si funciona", "Tool time, Pack Track y KPI"]],
              [3.6, 4.1, 4.4], mono=(), tam=12.5, colores_col={2: NARANJA_OSC})
    notas(s, """
Esta tabla es una síntesis propia de las fuentes; cada fila se apoya en una recomendación explícita:
1) Champion a medio tiempo: curso 2023, lección 8 ("debe ser un rol dedicado a tiempo completo") y errores al designarlo.
2) POC tardío: curso 2023 (el POC es entregable de la compuerta 3 y debe firmarse antes de la ingeniería de detalle).
3) IWP con restricciones: Quick Start, regla de oro.
4) Sin backlog: curso 2023 ("cree el backlog antes de movilizar cuadrillas; los planificadores se movilizan antes") y el riesgo de "empezar demasiado pronto" sin backlog suficiente.
5) Software antes que proceso: curso 2023, lección 7.
6) Sin cláusula: Procedimiento 3.0 (§3) y Quick Start (§3).
7) Sin medición: Procedimiento 3.0 (§18 y §19) y lección de KPI del curso 2023.
""", f"Síntesis de {F.CUR} (lecciones 7 y 8; backlog; cronograma), {F.QS} (§3, §7), {F.P3} (§3, §18, §19) y {F.FW}.")

    s = checklist(d, "Módulo 12 · Autoevaluación", "Diagnóstico rápido: ¿dónde está su proyecto hoy?",
                  "Autoevaluación en 7 preguntas", [
                      ("¿Hay un AWP Champion dedicado?", ""),
                      ("¿Están aprobados los procedimientos AWP, IM y WFP?", ""),
                      ("¿Se firmó el POC antes de la ingeniería de detalle?", ""),
                      ("¿Los EWP se liberan en la secuencia del POC?", ""),
                      ("¿Hay un Workface Planner por cada 50 trabajadores?", ""),
                      ("¿Ningún IWP sale a campo con restricciones?", ""),
                      ("¿Se miden el tool time y el backlog?", "")],
                  nota="Cada «no» es una prioridad para los próximos 90 días.", rotulo="DIAGNÓSTICO")
    notas(s, """
Use esta lista como diagnóstico rápido en la sesión: pida al público que responda sí o no para su proyecto actual.
Las preguntas siguen los siete componentes de la Quick Start Guide y los hitos de las fases:
1) Champion dedicado (Quick Start §1). 2) Procedimientos aprobados (§2). 3) POC firmado en la compuerta 3 (curso 2023). 4) EWP liberados según el POC (Procedimiento 1.0 §14). 5) Planificadores 1:50 (Quick Start §5). 6) Regla de oro de las restricciones (Quick Start §7). 7) Medición de tool time y backlog (Procedimiento 3.0 §18; curso 2023).
Cada respuesta negativa se convierte en una acción de la hoja de ruta de 90 días (lámina 120).
""", f"{F.QS} (§1-§7); {F.CUR}; {F.P1} (§14); {F.P3} (§18).")

    s = ciclo(d, "Módulo 12 · Mejora continua", "Registre y reutilice las lecciones de cada proyecto", [
        ("chart", "Medir", "Desempeño de paquetes y del cronograma"),
        ("search", "Analizar", "Tendencias de restricciones y causas raíz"),
        ("book", "Registrar", "Registro de lecciones del proyecto"),
        ("rocket", "Reutilizar", "Base más madura para el siguiente")], "Mejora continua",
        nota_lateral=["El registro empieza en el kick-off:", "• Lecciones de otros proyectos",
                      "• Aportes de cada actor", "• Comité mensual de WFP",
                      "El cierre alimenta el siguiente proyecto con datos reales."])
    notas(s, """
Omega 365 sitúa la mejora continua en el centro de AWP: al terminar el proyecto, los equipos deben revisar el desempeño de los paquetes, las tendencias de restricciones, el cumplimiento del cronograma y las causas raíz de los retrasos. Las lecciones se guardan para aplicarlas en proyectos futuros; así cada proyecto empieza con una base AWP más madura y basada en datos.
El Procedimiento 1.0 de Insight inicia el registro de lecciones en el seminario de arranque, dentro de los 30 días de la adjudicación, con aportes de todos los actores; el AWP Champion lo consolida y lo comunica, y el comité de dirección de WFP se reúne mensualmente.
""", f"{F.OMG} (Lessons Learned and Continuous Improvement); {F.P1} (§11 Kick-off and Lessons Learned).")


def m13(d):
    d.pie = "M13 · HOJA DE RUTA"
    s = separador(d, 13, "Módulo 13 · Hoja de ruta", "Empiece el lunes con tres acciones",
                  "Una hoja de ruta de 90 días y el resumen de todo el recorrido.")
    notas(s, """
Separador del último módulo. Cierre con acciones concretas: qué hacer en los próximos 90 días para empezar a implementar AWP en el primer proyecto, y el resumen del recorrido completo.
""", f"{F.QS}; {F.CUR} (AWP Related Lessons Learned).")

    s = linea_tiempo(d, "Módulo 13 · Hoja de ruta", "Hoja de ruta de 90 días para el primer proyecto", [
        ("DÍAS 1 A 30", "Nombrar y preparar", "AWP Champion dedicado, diagnóstico de 7 preguntas y capacitación inicial"),
        ("DÍAS 31 A 60", "Escribir y contratar", "Procedimientos AWP, IM y WFP, WBS y cláusulas para la licitación"),
        ("DÍAS 61 A 90", "Pilotear", "Taller del POC y un CWP piloto dividido en IWP, con Pack Track")],
        nota=("Gatear, caminar, correr: ", "el piloto enseña más que cualquier documento."),
        colores=[NARANJA_OSC, NARANJA, AZUL])
    notas(s, """
Hoja de ruta propuesta (síntesis de las fuentes) para el primer proyecto:
• Días 1 a 30, nombrar y preparar: designar un AWP Champion dedicado (Quick Start §1; lección 8 del curso 2023), aplicar el diagnóstico de la lámina 117 y capacitar al equipo en el lenguaje de AWP (lección 6).
• Días 31 a 60, escribir y contratar: redactar o adaptar los procedimientos AWP, IM y WFP (Quick Start §2; plantillas de Insight), definir la WBS y la nomenclatura, e incluir el procedimiento de WFP y la entrega de datos en las licitaciones (Procedimiento 3.0 §3).
• Días 61 a 90, pilotear: realizar el taller del POC (o, si el proyecto ya está en ejecución, elegir un CWP a 90 días de su inicio), dividirlo en IWP con el superintendente, gestionar sus restricciones y seguirlo con un Pack Track (Quick Start §6-§7).
Recuerde que el Procedimiento 1.0 dejó vacía su sección 12 ("Roadmap"); esta hoja de ruta la completa de forma práctica.
""", f"Síntesis de {F.QS} (§1-§7), {F.CUR} (lecciones 2, 6 y 8), {F.P3} (§3) y {F.P1} (§12, vacía en el original).")

    s = resumen_fases(d, "Módulo 13 · Resumen", "Resumen: cuatro fases, un solo hilo conductor", [
        ("Fase 1 · FEL 2", "Construcción", "CWA, Path of Construction y plan de liberación", NARANJA_OSC),
        ("Fase 2 · FEL 3", "Ingeniería y Compras", "EWP, PWP y CWP en la secuencia del POC", AZUL),
        ("Fase 3 · Ejecución", "Workface Planners y supervisión", "IWP sin restricciones, backlog y avance diario", NARANJA),
        ("Fase 4 · Arranque", "Comisionamiento y Operaciones", "SWP, TOP y certificados RFCC y RFOC", AZUL_MEDIO)],
        "Construcción define el orden; Ingeniería y Compras lo siguen; el campo lo ejecuta sin restricciones.")
    notas(s, """
Resumen del recorrido:
• Fase 1 (FEL 2): Construcción lidera la división en CWA, el Path of Construction en talleres interactivos y el plan de liberación de paquetes. El POC se congela al final de FEL 3.
• Fase 2 (FEL 3 y ejecución): Ingeniería entrega EWP completos en la secuencia del POC; Compras alinea los PWP y las fechas requeridas en obra; Construcción prepara los CWP.
• Fase 3 (ejecución): los Workface Planners dividen los CWP en IWP, liberan sus restricciones y mantienen el backlog; la supervisión ejecuta y registra el avance.
• Fase 4 (arranque): comisionamiento y operaciones reciben el proyecto por sistemas (SWP, TOP, RFCC, RFOC).
El hilo conductor, en palabras de la Quick Start Guide, es "empezar con el fin en mente": cuando ingeniería y compras se entregan en la secuencia correcta, la construcción puede avanzar sin interrupciones.
""", f"{F.OMG} (Planning and Implementation Stages); {F.QS} (§8F Engineering Alignment with Construction).")

    s = cierre(d, "Construya en el orden correcto y la productividad llega sola", [
        ("helmet_o", "Construcción define el orden", "Path of Construction (POC) y CWP"),
        ("ruler_o", "Ingeniería y Compras lo siguen", "EWP y PWP en la secuencia del POC"),
        ("clip_o", "El campo ejecuta sin restricciones", "IWP listos, backlog y avance diario")],
        "¿Preguntas?", "Siguiente paso: nombrar al AWP Champion del proyecto")
    notas(s, """
Cierre. Resuma el hilo conductor en tres ideas:
1. Construcción define el orden. El POC se construye en sesiones de planificación interactiva, se define en FEL 2 y se congela en FEL 3. De él salen las CWA y los CWP.
2. Ingeniería y Compras siguen ese orden. Los EWP y PWP se entregan en la secuencia del POC (1 EWP = 1 PWP = 1 CWP).
3. El campo ejecuta sin restricciones. Cada capataz recibe un IWP libre de restricciones, tomado de un backlog, y registra el avance a diario.
Siguiente paso concreto: nombrar un AWP Champion dedicado a tiempo completo. Es el primer componente de la Quick Start Guide y la lección 8 del curso 2023.
Abra la ronda de preguntas.
""", f"{F.QS} (§1 y §8); {F.CUR} (AWP Related Lessons Learned, lección 8); síntesis de la presentación.")
