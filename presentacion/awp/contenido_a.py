"""Módulos M0 a M4 (láminas 1 a 46)."""
from . import fuentes as F
from .diseno import (AZUL, AZUL_MEDIO, GRIS_MEDIO, NARANJA, NARANJA_OSC, bloques, bloques_horizontales,
                     checklist, cita, comparacion, dato, linea_tiempo, notas, pares, plano, proceso, separador,
                     tabla, portada)
from .especiales import agenda, codigo_wbs, gantt_liberacion, jerarquia, regla_1a1, tres_procesos


def m0(d):
    d.pie = "APERTURA"
    s = portada(d, "GUÍA PRÁCTICA DE IMPLEMENTACIÓN", "Implementar AWP",
                ["Construir el proyecto en el orden", "en que se va a construir"],
                [[{"t": "Advanced Work Packaging (AWP)", "negrita": True, "color": "FFFFFF"},
                  {"t": " fase por fase: roles, entregables, errores comunes y lecciones aprendidas.",
                   "color": "BCBEC0"}]],
                "Basado en guías del CII, la COAA e Insight-AWP")
    notas(s, """
Portada. Presente el propósito: esta guía explica cómo implementar Advanced Work Packaging (AWP) en un proyecto real, fase por fase.
Idea central: AWP es un proceso dirigido por Construcción. Primero se decide cómo y en qué orden se construirá la planta (Path of Construction); luego Ingeniería y Compras entregan sus productos en ese mismo orden.
Los bloques de la derecha anticipan la jerarquía que se verá en detalle: Construction Work Area (CWA) → Construction Work Package (CWP) → Installation Work Package (IWP).
Resultados que respaldan el método: +25 % de productividad y −10 % de costo total instalado (TIC), según los estudios RT-272 y RT-319 del Construction Industry Institute (CII).
""", f"{F.FW} (definición y beneficios); {F.QS} (Introducción).")

    s = agenda(d, "Apertura · Agenda", "Esta guía recorre un proyecto real, fase por fase", [
        (1, "Por qué AWP", None), (2, "Qué es AWP", None), (3, "Preparar la organización", None),
        (4, "Planificación preliminar", "Fase 1 · FEL 2"), (5, "Ingeniería y compras", "Fase 2 · FEL 3"),
        (6, "Construcción y WFP", "Fase 3 · Ejecución"), (7, "Puesta en marcha", "Fase 4 · Entrega"),
        (8, "Información y tecnología", None), (9, "Roles y organización", None), (10, "Medición y KPIs", None),
        (11, "Escalar y adoptar", None), (12, "Errores y lecciones", None), (13, "Hoja de ruta", None)])
    notas(s, """
La presentación tiene 13 módulos. Los tres primeros explican el porqué, el qué y cómo preparar la organización. Los módulos 4 a 7 (en oscuro) siguen el ciclo de vida del proyecto: planificación preliminar (FEL 2), ingeniería de detalle y compras (FEL 3), construcción y puesta en marcha.
Los módulos 8 a 13 son transversales: gestión de la información, roles, medición, escalabilidad y relación con Lean, errores comunes y la hoja de ruta para empezar.
Sugerencia: si el tiempo es corto, presente los módulos 1, 2, 4 a 7 y 13.
""", f"Estructura propia de la presentación, basada en {F.IDX} (sugerencias de lectura) y en las cuatro etapas del CII descritas en {F.OMG}.")

    s = bloques(d, "Apertura · Objetivos", "Al terminar, su equipo sabrá qué hacer, quién lo hace y cuándo", [
        ("sitemap", "Entender la jerarquía", "CWA, CWP, EWP, PWP e IWP y cómo se conectan"),
        ("clipcheck", "Conocer los entregables", "Qué se produce en cada fase y en qué compuerta"),
        ("users", "Asignar los roles", "AWP Champion, Workface Planners y Construction Manager"),
        ("warning", "Evitar errores típicos", "Lecciones de proyectos que ya aplicaron AWP")],
        nota="AWP es un cambio de sistema: afecta a todas las personas del proyecto, no solo a Construcción.")
    notas(s, """
Objetivos de aprendizaje. Al final de la sesión el equipo debe poder:
1) explicar la jerarquía de paquetes y la relación entre ellos;
2) saber qué entregable se espera en cada fase y en qué compuerta (stage gate) se revisa;
3) asignar los roles nuevos (AWP Champion, Workface Planner) y entender cómo cambian los tradicionales;
4) reconocer los errores más frecuentes al implementar AWP.
El curso integrado AWP 2023 insiste en que la adopción de AWP es un cambio sistémico que afecta a cada persona del proyecto; por eso los objetivos cubren a todas las áreas.
""", f"{F.CUR} (objetivos de lección; 'Role of the AWP Champion'); {F.PRI}.")

    s = tabla(d, "Apertura · Fuentes", "Las cifras de esta guía vienen del CII, la COAA e Insight-AWP",
              ["Organismo", "Qué aporta", "Documentos del repositorio"],
              [["CII · Construction Industry Institute", "Estudios RT-272 y RT-319, definición oficial y glosario",
                "Education Primer, Education Framework, Glosario, AWP vs Lean"],
               ["COAA · Construction Owners Association of Alberta", "Buenas prácticas de WFP y modelo de AWP escalable",
                "Resumen COAA 2016; Framework (AWP escalable)"],
               ["Insight-AWP", "Guía de inicio rápido y procedimientos AWP, IM y WFP",
                "Quick Start Guide; Procedimientos 1.0, 2.0 y 3.0"],
               ["Otras fuentes", "Curso integrado y enfoque digital", "Curso AWP 2023; Omega 365; presentación 2022"]],
              [3.6, 4.2, 4.3], mono=(), tam=12.5, alto_fila=0.9,
              nota="Cuando las fuentes no coinciden en una cifra, la lámina lo indica y el procedimiento del proyecto debe fijarla.")
    notas(s, """
Presente de dónde vienen los datos. El CII (Construction Industry Institute, EE. UU.) formalizó AWP como mejor práctica en 2015 a partir del equipo de investigación RT-272; sus estudios reportan +25 % de productividad y −10 % de costo total instalado.
La COAA (Construction Owners Association of Alberta, Canadá) desarrolló las primeras buenas prácticas de Workface Planning (2005-2006) y el modelo de AWP escalable (2019).
Insight-AWP aporta la guía de inicio rápido y un juego de procedimientos (AWP, Information Management y Workface Planning) de 2017, con plantillas.
Otras fuentes: un curso integrado de 2023 (sin autor declarado) y un artículo de Omega 365 (2025) con enfoque digital.
El INDICE.md del repositorio documenta las inconsistencias entre fuentes; se señalan en la lámina 24 y donde corresponda.
""", f"{F.IDX} (§1 y §3); {F.COAA}; {F.FW}.")


def m1(d):
    d.pie = "M1 · POR QUÉ AWP"
    s = separador(d, 1, "Módulo 1 · Por qué AWP", "El problema no es la cuadrilla, es la planificación",
                  "Qué dicen los datos sobre sobrecostos, productividad y tiempo perdido en campo.")
    notas(s, """
Separador del Módulo 1. Antes de explicar qué es AWP, conviene mostrar el problema que resuelve: proyectos que terminan tarde y sobre presupuesto, y cuadrillas que pasan la mayor parte de la jornada sin trabajar en herramientas.
Mensaje para el público: la baja productividad no es culpa del trabajador; es la consecuencia de que la información, los materiales y los accesos no llegan a tiempo al frente de trabajo.
""", f"{F.CUR} (Lección 1: AWP and Field Productivity).")

    s = dato(d, "Módulo 1 · El problema", "El 65 % de los megaproyectos fracasa en costo, plazo o desempeño",
             "65 %", "de los megaproyectos fracasa",
             "Fracasar es terminar con sobrecosto, con retraso o con un desempeño operativo menor al prometido.",
             apoyos=[("70 %", "de los proyectos de construcción termina sobre presupuesto y con retraso"),
                     ("189 %", "del presupuesto inicial: donde termina el 52 % de los proyectos")],
             icono_nombre="warning_o")
    notas(s, """
El curso AWP 2023 cita a IPA Global: el 65 % de los megaproyectos fracasa, entendiendo por fracaso el sobrecosto, el retraso o el bajo desempeño en operación. Entregar tarde y por encima del presupuesto es un problema común en todo el mundo.
El Education Framework del CII añade, al responder la objeción "nuestro proceso actual está bien", que el 70 % de los proyectos de construcción termina sobre presupuesto y con retraso, y que el 52 % termina en el 189 % de su presupuesto inicial. Atribuye buena parte del problema a la desalineación entre ingeniería, compras y construcción.
Use la cifra para abrir la conversación, no para culpar: el problema es sistémico.
""", f"{F.CUR} (Lección 1: '65% of Mega Projects Fail', IPA Global); {F.FW} (Overcoming Common AWP Objections: 'Our current process is just fine').")

    s = dato(d, "Módulo 1 · El problema", "La productividad de la construcción no ha mejorado en 70 años",
             "70 años", "sin mejora de productividad en construcción",
             "Otras industrias sí mejoraron. La mano de obra es una de las mayores partidas del presupuesto.",
             apoyos=[("< 4 h", "productivas en una jornada de 10 horas"),
                     ("< 2 h", "al día de supervisión directa de la cuadrilla")], icono_nombre="chart_o",
             tam_cifra=100)
    notas(s, """
Según el curso AWP 2023, la productividad de la construcción no ha mejorado en los últimos setenta años, mientras otros sectores han visto mejoras significativas.
Como la mano de obra es una de las partidas más grandes del presupuesto, mejorar su productividad tiene un impacto directo en el resultado del proyecto.
Dos datos del mismo curso ilustran el problema: menos de 4 horas de una jornada de 10 son productivas, y menos de 2 horas al día se dedican a supervisión directa de la cuadrilla. El tiempo de supervisión es un indicador del apoyo que recibe la cuadrilla para trabajar con seguridad y eficiencia.
Nota de diseño: en la estructura esta lámina figuraba como diagrama de tendencia; se presenta como dato clave porque las fuentes no incluyen la serie histórica.
""", f"{F.CUR} (Lección 1: 'Construction productivity has failed to improve in the last seventy years'; Lección 2: 'Less than 2 hours of the day are spent in direct supervision').")

    s = dato(d, "Módulo 1 · El problema", "Menos de 4 de cada 10 horas de la jornada son productivas",
             "3,7 h", "de 10 horas en herramientas (37 %)",
             "El resto se pierde en esperas, traslados, búsqueda de materiales e información y pausas.",
             apoyos=[("6,3 h", "sin herramientas por trabajador y día en proyectos tradicionales"),
                     ("4,6 h", "en herramientas en proyectos con AWP (46 %)")], icono_nombre="clock_o")
    notas(s, """
El tool time, o tiempo en herramientas, es la fracción de la jornada en que el trabajador está instalando. En proyectos tradicionales es del 37 %: 3,7 horas de una jornada de 10. Las otras 6,3 horas se van en esperas por información, materiales, herramientas o accesos, en traslados y en pausas.
Con AWP, el Education Framework del CII reporta un 46 % (4,6 horas); el curso 2023 cita un 47 %.
Mensaje: la diferencia no se logra exigiendo más a la cuadrilla, sino entregándole un paquete de trabajo completo y sin restricciones.
""", f"{F.FW} (Benefits & Value of AWP: 37 % / 3,7 h frente a 46 % / 4,6 h); {F.CUR} (Lección 2: Tool Time 37 % / 47 %).")

    s = pares(d, "Módulo 1 · Causas", "Los retrasos en campo nacen en la oficina", "En la oficina (causa)",
              "En el campo (síntoma)", [
                  ("Ingeniería emite planos en su propio orden", "La cuadrilla espera información o trabaja fuera de secuencia"),
                  ("Compras sin la secuencia de construcción", "Faltan materiales en el frente de trabajo"),
                  ("Andamios y equipos sin planificar", "Horas perdidas esperando acceso o grúas"),
                  ("Revisiones de planos sin control", "Consultas técnicas (RFI) y retrabajo en el frente")],
              nota="Workface Planning ataca el síntoma en campo; AWP ataca la causa en la oficina.")
    notas(s, """
El curso AWP 2023 lo resume así: los problemas de campo están ligados a la oficina. Los problemas típicos de ejecución (esperar planos, buscar materiales, esperar andamios o grúas, rehacer trabajo) son síntomas. Sus causas están aguas arriba: una ingeniería que se entrega en su propio orden, compras que no siguen la secuencia de construcción, recursos de apoyo que no se planifican con anticipación.
RFI (Request for Information) es la consulta técnica que el campo envía a Ingeniería cuando falta o no está clara la información.
Esta es la razón de que AWP "adelante" la planificación al inicio del ciclo de vida del proyecto: el adjetivo advanced viene de ahí.
""", f"{F.CUR} (Lección 2: 'Typical Construction Execution Issues', 'Refresher … field issues are linked to the office', 'The Advanced aspect comes from pulling the planning process earlier').")

    s = bloques(d, "Módulo 1 · Habilitadores",
                "El trabajador ejecuta cuando tiene información, herramientas, materiales, acceso y voluntad", [
                    ("file", "Información", "Planos IFC vigentes y alcance claro"),
                    ("wrench", "Herramientas", "Equipos y consumibles en el frente"),
                    ("boxes", "Materiales", "Completos y a mano antes del inicio"),
                    ("road", "Acceso", "Andamios, permisos y frente libre"),
                    ("thumbsup", "Voluntad", "Una cuadrilla motivada y respaldada")],
                nota="La gerencia debe asegurar las cuatro primeras; la voluntad crece cuando ellas están resueltas.",
                tam_titulo=14, cols=5)
    notas(s, """
El Procedimiento 3.0 de Insight-AWP, en la sección de estudios de tool time, parte de un principio: los trabajadores ejecutan el trabajo cuando tienen información, herramientas, materiales, acceso y voluntad. El papel de la gerencia del proyecto y de la construcción es entregar esos elementos a la fuerza laboral.
Por eso los estudios de tool time se consideran una "nota" para la gerencia y no para los trabajadores: los retrasos en la jornada revelan la ausencia de uno o más de estos elementos.
IFC (Issued for Construction) es el estado del plano aprobado para construir.
""", f"{F.P3} (§18 Tool Time Studies: 'Information, Tools, Materials, Access and Desire').")

    s = comparacion(d, "Módulo 1 · Por qué no basta WFP", "Workface Planning (WFP) solo no basta: llega tarde",
                    dict(titulo="Solo WFP", color=GRIS_MEDIO, icono_res="xmark_g", numerado=False,
                         puntos=[("Se planifica en campo", "El planificador arma paquetes con lo que llega"),
                                 ("Ingeniería y Compras siguen su lógica", "Los paquetes quedan incompletos o esperan"),
                                 ("Se administra la escasez", "Mejora local, sin tocar la causa")],
                         resultado="Mejora limitada al frente de trabajo"),
                    dict(titulo="AWP (incluye WFP)", color=NARANJA, icono_res="check_o", numerado=False,
                         puntos=[("La planificación empieza en FEL 2", "Construcción define el orden antes de diseñar"),
                                 ("Ingeniería y Compras siguen ese orden", "EWP y PWP llegan completos y en secuencia"),
                                 ("WFP ejecuta sin restricciones", "IWP listos para cada cuadrilla")],
                         resultado="Mejora en todo el ciclo del proyecto"))
    notas(s, """
Workface Planning (WFP) nació para atacar la productividad en campo: definir, crear, ejecutar y seguir paquetes de instalación para cada cuadrilla. Fue el primer paso del camino hacia AWP.
Pero WFP solo no basta: si la ingeniería y las compras no llegaron en la secuencia correcta, el planificador de campo solo administra la escasez y arma paquetes con lo que tiene.
AWP extiende la planificación hacia atrás, a las fases de definición (Front End Loading, FEL), para que ingeniería y compras se entreguen en el orden en que se va a construir. WFP sigue siendo la etapa final de AWP, donde toda esa planificación se usa en campo.
""", f"{F.CUR} (Lección 1: 'Why is Workface Planning alone not enough?', 'From Workface Planning to AWP'); {F.COAA}.")

    s = dato(d, "Módulo 1 · Beneficios", "Con AWP la productividad sube 25 % y el costo total baja 10 %",
             "+25 %", "de productividad en campo",
             "Resultados de proyectos con AWP maduro según los estudios RT-272 y RT-319 del CII.",
             apoyos=[("−10 %", "de costo total instalado (TIC)"), ("SPI +25 %", "mejora del desempeño en plazo"),
                     ("CPI +33 %", "mejora del desempeño en costo")], icono_nombre="money_o")
    notas(s, """
La Quick Start Guide y el Education Framework coinciden: con AWP, la productividad aumenta típicamente un 25 % y el costo total instalado (TIC, Total Installed Cost) baja un 10 %. Todas las fuentes remiten a los estudios RT-272 y RT-319 del CII.
El Framework cita además un estudio con mejoras del índice de desempeño del cronograma (SPI) del 25 % y del índice de desempeño del costo (CPI) del 33 % frente a proyectos sin AWP.
Otros beneficios citados por el curso 2023: mayor seguridad (menos cambios, menos incidentes), alcances más precisos para licitar (menos contingencia), mejor calidad (menos RFI y retrabajo), mejor constructabilidad, colaboración entre disciplinas y estimados y cronogramas más certeros.
Advierta que los beneficios varían según el punto de partida y la madurez de la implementación.
""", f"{F.QS} (Introducción); {F.FW} (Benefits & Value of AWP; RS272-1); {F.CUR} (Other Benefits of AWP).")


def m2(d):
    d.pie = "M2 · QUÉ ES AWP"
    s = separador(d, 2, "Módulo 2 · Qué es AWP", "AWP es un proceso, no un software",
                  "Definición, los tres procesos que lo componen y la familia de paquetes de trabajo.")
    notas(s, """
Separador del Módulo 2. Aclare desde el inicio un malentendido frecuente: AWP no es un programa informático ni una plantilla. Es un proceso de entrega de proyectos que alinea ingeniería, compras y construcción. El software ayuda, pero no lo reemplaza.
En este módulo se ven la definición oficial, los tres procesos que integran AWP y la jerarquía de paquetes.
""", f"{F.INS}; {F.FW}.")

    s = cita(d, "Módulo 2 · Definición",
             "AWP alinea ingeniería, compras y construcción según cómo se va a construir",
             "“El flujo general de todos los paquetes de trabajo detallados: de construcción, de ingeniería y de "
             "instalación. Un proceso planificado y ejecutable, desde la planificación inicial hasta el diseño "
             "detallado y la construcción.”", "DEFINICIÓN DEL CONSTRUCTION INDUSTRY INSTITUTE (CII) · TRADUCCIÓN",
             puntos=[("helmet", "Dirigido por Construcción: el orden lo fija cómo se va a construir"),
                     ("project", "Abarca desde la planificación inicial hasta la puesta en marcha"),
                     ("puzzle", "Supone un plan de ejecución de la construcción")])
    notas(s, """
Definición del CII (traducción): "AWP es el flujo general de todos los paquetes de trabajo detallados (de construcción, de ingeniería y de instalación). AWP es un proceso planificado y ejecutable que abarca el trabajo de un proyecto EPC, desde la planificación inicial hasta el diseño detallado y la ejecución de la construcción. AWP provee el marco para una construcción productiva y progresiva y presupone la existencia de un plan de ejecución de la construcción."
Es la cita más repetida del repositorio (Primer, Framework, Overview del CII, Glosario y la presentación de 2022).
El Framework lo complementa: AWP es un método de entrega de proyectos que va desde la planificación temprana (Front End Planning) hasta el comisionamiento, y alinea ingeniería, compras y construcción.
EPC: Engineering, Procurement and Construction (ingeniería, compras y construcción).
""", f"{F.FW} ('What is it?'); {F.OVR}; {F.PRI}; {F.GLO}; {F.PPT}.")

    s = tres_procesos(d, "Módulo 2 · Tres procesos",
                      "AWP integra tres procesos: AWP, Information Management (IM) y Workface Planning (WFP)", [
                          ("AWP", "Advanced Work Packaging", "Alinea EWP, PWP y CWP con la secuencia de construcción",
                           NARANJA_OSC),
                          ("IM", "Information Management", "Estandariza WBS, nomenclatura, modelo 3D e intercambio de datos",
                           AZUL),
                          ("WFP", "Workface Planning", "Crea, libera y sigue los paquetes de cada cuadrilla", NARANJA)],
                      nota="Los tres se implementan juntos: sin datos confiables (IM) no hay paquetes confiables (WFP).")
    notas(s, """
Insight-AWP describe AWP como un sistema de planificación dirigido por Construcción, compuesto por tres procesos:
• Advanced Work Packaging: alinea los paquetes de ingeniería (EWP), de compras (PWP) y de construcción (CWP) con el camino óptimo de construcción.
• Information Management (IM): define la estructura de desglose del trabajo (WBS, Work Breakdown Structure), la nomenclatura, el modelo 3D con atributos y los formatos de intercambio entre sistemas.
• Workface Planning (WFP): lleva el plan al frente de trabajo mediante paquetes de instalación (IWP) libres de restricciones.
Por eso los procedimientos de Insight-AWP son tres (1.0 AWP, 2.0 IM y 3.0 WFP) y se aplican como un conjunto.
""", f"{F.INS}; {F.P1} (§4 Overview of AWP, IM & WFP).")

    s = jerarquia(d, "Módulo 2 · Jerarquía de paquetes",
                  "Todo se ordena en una jerarquía: del área al paquete que recibe el capataz")
    notas(s, """
La jerarquía de paquetes es el esqueleto de AWP. Léala de arriba hacia abajo:
• Construction Work Area (CWA): división lógica del plano de implantación; actividad de nivel 2 del cronograma.
• Construction Work Package (CWP): una sola disciplina dentro de una CWA, con menos de 40 000 horas-hombre (HH); actividad de nivel 3.
• Engineering Work Package (EWP): toda la ingeniería que necesita un CWP (alcance, planos, datos de proveedor, lista de materiales y especificaciones).
• Procurement Work Package (PWP): materiales y equipos de un CWP. El CII todavía lo trata como paquete en definición (RT-363).
• Installation Work Package (IWP): trabajo de un capataz y su cuadrilla en unos 7 días, formado por planos completos; actividad de nivel 5.
Regla base: 1 EWP = 1 PWP = 1 CWP, con excepciones que se ven en la lámina 22.
Advierta que el Glosario del CII ubica el IWP en el nivel 4; cada proyecto debe fijar su criterio.
""", f"{F.P1} (§2 Definiciones); {F.OMG} (jerarquía de paquetes); {F.GLO}; {F.IDX} §3.")

    s = plano(d, "Módulo 2 · CWA", "La Construction Work Area (CWA) es la primera división del terreno",
              destacar="CWA-01", nota_lateral=[
                  ("map", "Parte lógica del plano", "Incluye todas las disciplinas del área"),
                  ("calendar", "Nivel 2 del cronograma", "Horizonte de unos 6 meses"),
                  ("sitemap", "Contenedor de CWP", "Una CWA tiene varios CWP, uno por disciplina")])
    notas(s, """
La CWA es una porción del plano de implantación que el proyecto define como un área lógica de trabajo. Incluye todas las disciplinas (civil, estructuras, mecánica, tuberías, electricidad e instrumentación). El número de CWA depende del tamaño y la complejidad del proyecto.
Los procedimientos de Insight la definen como actividad de nivel 2 del cronograma, con un horizonte de unos 6 meses. Los cables y las obras subterráneas pueden dividirse en áreas propias que cruzan todo el proyecto.
El plano de la lámina es un ejemplo ilustrativo: una planta con unidad de proceso, compresión, subestación, sala de control, rack de tuberías, tanques, torre de enfriamiento y servicios.
Las CWA forman la base del Path of Construction, dan prioridades a Ingeniería y Compras y dividen el alcance en paquetes ejecutables.
""", f"{F.CUR} ('What is a Construction Work Area', 'Advanced Work Packaging Structure'); {F.P3} (§2 Definiciones); {F.OMG}.")

    s = bloques(d, "Módulo 2 · CWP", "Un Construction Work Package (CWP) es una disciplina dentro de una CWA", [
        ("helmet", "Una disciplina, una CWA", "Ej.: tuberías del área 2 o electricidad del área 4"),
        ("hourglass", "Menos de 40 000 HH", "Tamaño que permite controlar y contratar"),
        ("calendar", "Nivel 3 del cronograma", "Horizonte de unos 3 meses"),
        ("contract", "Límite contractual", "Los CWP no se superponen: sirven como alcance de licitación")],
        nota="El CWP es la unidad central de ejecución: integra ingeniería, compras, instalación y comisionamiento.")
    notas(s, """
El CWP es el alcance completo de una sola disciplina en una sola CWA; por ejemplo, tuberías del área 2 o electricidad del área 4.
Según los procedimientos de Insight: menos de 40 000 horas-hombre (HH), componente de la WBS, una sola actividad de nivel 3 del cronograma y producto de un EWP y un PWP. Los CWP no se superponen, por lo que pueden usarse como límites contractuales.
El curso 2023 detalla su contenido típico: alcance, puntos de interfaz, planos IFC, información de ingeniería, suministro de materiales y equipos, mano de obra y andamios, seguridad, calidad, permisos, izajes críticos, controles y documentos de entrega.
Recomendaciones: el EWP es la base técnica del CWP, pero el contratista recibe el CWP, así que toda la información relevante debe estar en él; defina con claridad el límite del alcance y no incluya lenguaje contractual.
""", f"{F.P1} y {F.P3} (§2 Definiciones); {F.CUR} ('What is a CWP?', 'Standard components of a CWP'); {F.OMG}.")

    s = bloques(d, "Módulo 2 · EWP", "Un Engineering Work Package (EWP) entrega toda la ingeniería que necesita un CWP", [
        ("file", "Alcance y exclusiones", "Qué incluye, qué no y dónde están las interfaces"),
        ("ruler", "Planos IFC", "Lista de planos de ingeniería y de proveedores"),
        ("book", "Especificaciones", "Normas y estándares aplicables"),
        ("boxes", "Materiales", "Lista de materiales (MTO) y quién suministra cada ítem"),
        ("cube", "Vistas del modelo 3D", "Imágenes del alcance para ubicarlo en planta")],
        nota="Tamaño típico: de 5 000 a 20 000 HH de campo. Evite EWP de más de 50 000 HH: son difíciles de controlar.",
        tam_titulo=14)
    notas(s, """
El EWP es un entregable de Ingeniería que contiene la documentación de una disciplina para una CWA. Tiene relación 1:1 con el CWP (CWA × disciplina = EWP).
Componentes estándar según el curso 2023: alcance del trabajo, trabajo excluido, puntos terminales, equipos y materiales suministrados por el propietario y por el contratista, especificaciones y normas, lista de planos de ingeniería y de proveedores, soporte de proveedores, cronograma de órdenes de compra, vistas del modelo 3D y lista de referencias.
Los EWP son por área, no por sistema, y no cruzan el límite de una CWA salvo casos excepcionales (por ejemplo, cables largos).
Recomendaciones: evite el texto repetido de otras especificaciones y el lenguaje contractual; describa qué es el trabajo, no cómo ejecutarlo.
MTO: Material Take-Off, lista de materiales cuantificada desde el diseño.
""", f"{F.CUR} ('What is an EWP?', 'Features of an EWP', 'EWP Size'); {F.P1} (§2 Definiciones).")

    s = bloques(d, "Módulo 2 · PWP", "Un Procurement Work Package (PWP) asegura los materiales de un CWP", [
        ("truck", "Materiales y equipos del CWP", "Uno o varios pedidos de compra"),
        ("barcode", "Un identificador, no una caja", "Alinea las compras con la secuencia de construcción"),
        ("boxes", "Granel agrupado", "Bandejas o soportes pueden compartir un PWP"),
        ("clock", "En definición en el CII", "El estudio RT-363 aún lo desarrolla")],
        nota="Para acero y tuberías, el PWP se convierte en un paquete de fabricación con entrega conjunta.")
    notas(s, """
El PWP define los materiales, equipos y consumibles necesarios para ejecutar el alcance de un CWP. Normalmente se inicia a partir de los productos del EWP: requisiciones técnicas, hojas de datos y especificaciones.
Omega 365 aclara que el PWP no es necesariamente un paquete físico en campo: es un identificador que alinea la secuencia de compras con la de construcción. Puede incluir uno o varios pedidos, equipos de largo plazo de entrega o materiales a granel.
La mejor práctica es la relación 1:1 con el CWP, pero los materiales de uso común (bandejas, soportes, infraestructura) suelen agruparse en PWP compartidos.
En los procedimientos de Insight, para acero y tuberías el PWP se convierte en un paquete de fabricación que se fabrica y entrega como un grupo.
El Primer y el Framework del CII lo marcan como opcional; el Glosario indica que su definición está en desarrollo (RT-363).
""", f"{F.OMG} (Procurement Work Packages); {F.P3} (§2 Definiciones); {F.GLO}; {F.IDX} §3 y §4.3.")

    s = bloques(d, "Módulo 2 · IWP", "Un Installation Work Package (IWP) es el trabajo de una cuadrilla en una semana", [
        ("users", "Un capataz, una cuadrilla", "Unos 10 trabajadores por capataz"),
        ("calendar", "Unos 7 días", "Actividad de nivel 5 del cronograma"),
        ("file", "Planos completos", "Nunca se corta un isométrico a la mitad"),
        ("unlock", "Libre de restricciones", "Solo así se entrega a campo")],
        nota="Tamaño de referencia: de 500 a 1 000 HH, según el tamaño de la cuadrilla.")
    notas(s, """
El IWP es una porción discreta de trabajo de construcción, libre de restricciones, que puede ejecutar un solo capataz con su cuadrilla en un período de 7 días. Se obtiene de un solo CWP, está formado por planos completos y es una actividad de nivel 5 del cronograma (procedimientos de Insight).
Contiene todo lo que la cuadrilla necesita: alcance, planos, materiales, equipos, herramientas, seguridad, calidad, restricciones, recursos, cronograma, información de proveedores y vistas del modelo.
Las fuentes difieren en su tamaño y duración: unas 500 horas (Quick Start), 500 a 1 000 horas (curso 2023), una o dos semanas, o "un solo turno" en otra lámina del mismo curso. La lámina 24 resume estas diferencias.
""", f"{F.P3} (§2 Definiciones); {F.QS} (§6 Installation Work Packages); {F.CUR} ('What is an IWP, and how is it made?'); {F.IDX} §3.")

    s = regla_1a1(d, "Módulo 2 · Alineación", "La regla base es 1 EWP = 1 PWP = 1 CWP")
    notas(s, """
El Procedimiento 1.0 de Insight establece que el método de planificación se basa en el estándar "un EWP = un PWP = un CWP". El EWP termina con el último plano IFC; el PWP termina con el último componente recibido en obra. Los paquetes se entregan completos, no plano por plano ni pieza por pieza, y las actividades van en serie (fin a inicio).
Alinear los tres paquetes simplifica el seguimiento: cada CWP sabe exactamente de qué ingeniería y de qué compras depende.
Omega 365 y el curso 2023 admiten excepciones: materiales a granel agrupados en un PWP común; un EWP de criterios de diseño que sirve a varios CWP; o un CWP que depende de varios EWP por dependencias entre disciplinas.
""", f"{F.P1} (§14 Interactive Planning Workshop); {F.OMG} (Engineering Work Packages y Procurement Work Packages); {F.CUR}.")

    s = comparacion(d, "Módulo 2 · Sistemas", "Para la puesta en marcha se empaqueta por sistemas, no por áreas",
                    dict(titulo="Por áreas · construcción", color=AZUL, numerado=False,
                         puntos=[("CWA → CWP → IWP", "Organiza el trabajo por ubicación física"),
                                 ("Una disciplina por paquete", "Facilita la ejecución y el control"),
                                 ("Relación uno a muchos", "Cada CWP se divide en varios IWP")]),
                    dict(titulo="Por sistemas · puesta en marcha", color=NARANJA, numerado=False,
                         puntos=[("System Work Package (SWP)", "Agrupa partes de CWP e IWP por sistema funcional"),
                                 ("Turnover Package (TOP)", "Consolida el sistema para su entrega y arranque"),
                                 ("Relación muchos a muchos", "Un sistema cruza varias CWA y varios CWP")]),
                    nota="El cambio de enfoque de áreas a sistemas se acelera hacia el 70 % de avance físico.")
    notas(s, """
Mientras se construye, AWP organiza el trabajo por áreas (CWA, CWP, IWP). Para el comisionamiento y el arranque, la lógica cambia a sistemas funcionales, como agua de enfriamiento, compresión de gas o distribución eléctrica.
• System Work Package (SWP): agrupa porciones de CWP e IWP por sistema; conecta construcción y comisionamiento (completamiento mecánico, inspección, pruebas y certificación).
• Turnover Package (TOP): consolida esos alcances en circuitos cerrados listos para la entrega, las pruebas y el arranque.
La relación entre CWP/IWP y SWP/TOP es de muchos a muchos. Según Omega 365, este cambio de perspectiva se acelera hacia el 70 % de avance físico de la construcción, para detectar a tiempo los faltantes por sistema.
El Glosario del CII indica que la definición del TOP estaba en desarrollo (RT-364); el Primer rotula el SWP como "TWP".
""", f"{F.OMG} (System Work Packages y Turnover Packages); {F.GLO}; {F.IDX} §3.")

    s = tabla(d, "Módulo 2 · Cifras en discusión",
              "Las fuentes no coinciden en algunos números: fije los suyos en el procedimiento",
              ["Tema", "Qué dicen las fuentes", "Qué debe decidir"],
              [["Nivel del IWP", "Nivel 5 (Insight, Quick Start) · nivel 4 (Glosario CII)", "Un solo criterio"],
               ["Duración del IWP", "Un turno · 7 días · 1 a 2 semanas", "Ventana estándar"],
               ["Tamaño del IWP", "~500 h (Quick Start) · 500 a 1 000 h (curso 2023)", "Rango por disciplina"],
               ["Backlog", "2 a 4 semanas · 4 semanas · 30 días", "Meta por disciplina"],
               ["Supervisión", "Capataz general (GF): 4 o 5 capataces · superintendente: 3 o 4 GF", "Ratios del proyecto"],
               ["Plazo de restricciones", "2 a 3 semanas · 6 o 12 semanas según tamaño", "Calendario por tamaño"]],
              [2.9, 6.3, 2.9], mono=(), tam=12.5,
              nota="Documente la decisión y su justificación en el procedimiento AWP del proyecto.")
    notas(s, """
El INDICE.md del repositorio identificó inconsistencias entre fuentes. No son errores graves: reflejan contextos distintos. Pero cada proyecto debe fijar sus propios valores y aplicarlos de forma consistente.
• Nivel del IWP: nivel 5 según los procedimientos de Insight, la Quick Start y la presentación de 2022; nivel 4 según el Glosario del CII.
• Duración: 7 días o una semana (Insight, Glosario); 1 a 2 semanas (curso 2023); un turno (otra lámina del mismo curso).
• Tamaño: unas 500 horas (Quick Start); 500 a 1 000 horas (curso 2023).
• Backlog: 4 semanas (Quick Start); 2 a 4 semanas (Procedimiento 3.0); 30 días (curso 2023).
• Supervisión: el capataz general (GF, General Foreman) supervisa hasta 4 capataces y el superintendente hasta 3 GF (Insight); 5 y 4 según el Glosario del CII.
• Restricciones: liberadas 2 a 3 semanas antes (curso 2023); calendario de 6 o 12 semanas según tamaño (Framework).
""", f"{F.IDX} (§3 Inconsistencias detectadas entre archivos).")


def m3(d):
    d.pie = "M3 · PREPARAR LA ORGANIZACIÓN"
    s = separador(d, 3, "Módulo 3 · Preparar la organización", "AWP empieza antes del primer plano",
                  "Qué debe tener lista la empresa antes de iniciar: un responsable, procedimientos, contrato, software y nomenclatura.")
    notas(s, """
Separador del Módulo 3. Antes de la primera compuerta del proyecto, la organización debe preparar las condiciones: nombrar al responsable (AWP Champion), escribir los procedimientos, incluir AWP en los contratos, elegir el software y definir la nomenclatura común.
Sin estas bases, AWP se queda en buenas intenciones.
""", f"{F.QS}; {F.P1}.")

    s = bloques(d, "Módulo 3 · Componentes", "Siete componentes bastan para arrancar", [
        ("star", "1 · AWP Champion", "Líder dedicado a tiempo completo"),
        ("book", "2 · Procedimientos", "AWP, IM y WFP por escrito"),
        ("cube", "3 · Modelo 3D", "Con los datos de los fabricantes"),
        ("laptop", "4 · Software WFP", "Paquetes armados sobre el modelo"),
        ("usertie", "5 · Workface Planners", "Un cargo nuevo en la obra"),
        ("clip", "6 · IWP", "Lo que el capataz necesita"),
        ("unlock", "7 · Restricciones", "Eliminarlas antes de liberar")], cols=4, tam_titulo=14)
    notas(s, """
La Quick Start Guide de Insight-AWP identifica siete componentes básicos para empezar:
1) Asignar un AWP Champion. 2) Escribir procedimientos de AWP. 3) Contar con un modelo 3D con atributos y con los datos de fabricación. 4) Seleccionar un software de Workface Planning. 5) Crear el cargo de Workface Planner. 6) Definir el contenido del IWP. 7) Establecer el proceso de eliminación de restricciones, que es el mayor cambio respecto de la forma tradicional de construir.
Una vez establecidos, con poco esfuerzo adicional se pueden optimizar otros sistemas: controles, materiales, control documental, andamios, equipos de construcción y alineación de la ingeniería (se ven en el Módulo 8).
""", f"{F.QS} (§1 a §7 y §8 Extended Benefits); {F.IDX} §1.2.")

    s = bloques_horizontales(d, "Módulo 3 · AWP Champion",
                             "El AWP Champion es el primer nombramiento y debe ser a tiempo completo", [
                                 ("handshake", "Representa al propietario", "Coordina a todos los actores con imparcialidad"),
                                 ("teach", "Actúa como coach", "Guía la aplicación de los procedimientos AWP, IM y WFP"),
                                 ("users", "Se enfoca en las personas", "Ayuda a cada rol a adaptarse al cambio"),
                                 ("usertie", "Perfil experto", "AWP, gestión de proyectos y construcción")],
                             nota="No asuma que el rol recae en el gerente del proyecto: requiere dedicación exclusiva.")
    notas(s, """
La Quick Start Guide llama a la designación del AWP Champion el primer paso crítico. Es miembro del equipo de gestión del proyecto, suele representar al propietario y coordina los entregables de todos los actores con imparcialidad, con el único foco de beneficiar al proyecto completo. Funciona como coach del proyecto.
El curso 2023 agrega: es un líder dedicado por completo a la transición; su foco principal son las personas, porque casi todos necesitarán ayuda para adaptarse a roles y exigencias nuevas.
Errores comunes al designarlo: asumir que el rol le toca al gerente del proyecto, subestimar la carga de trabajo, ignorar el efecto en su carrera y dejarlo solo.
El perfil ideal es un experto en AWP y gestión de proyectos con experiencia en gestión de construcción.
""", f"{F.QS} (§1 Assign an AWP Champion); {F.CUR} ('Role of the AWP Champion', 'Common Pitfalls in Hiring the AWP Champion').")

    s = bloques(d, "Módulo 3 · Procedimientos", "Los procedimientos fijan quién, qué, cuándo, cómo y por qué", [
        ("user", "¿Quién?", "Responsable de cada entregable"),
        ("file", "¿Qué?", "Entregable y su contenido"),
        ("calendar", "¿Cuándo?", "Fase y plazo de entrega"),
        ("gears", "¿Cómo?", "Diagramas de flujo y plantillas"),
        ("bulb", "¿Por qué?", "El propósito que da sentido al cambio")],
        nota="Los procedimientos no cambian la cultura por sí solos, pero crean la obligación de cumplir y permiten auditar.")
    notas(s, """
La Quick Start Guide explica que, para que los actores sigan una dirección común, debe existir un estándar. Los procedimientos por sí solos no generan el cambio, pero establecen una expectativa de cumplimiento y facilitan las auditorías posteriores.
Idealmente son específicos y detallados, e identifican quién, qué, cuándo, cómo y por qué, con diagramas de flujo y plantillas.
El Procedimiento 1.0 de Insight señala que el propietario puede aplicar cualquiera de los procedimientos complementarios según el proyecto, pero los tres procedimientos centrales (AWP, IM y WFP) forman un conjunto.
""", f"{F.QS} (§2 Advanced Work Packaging Procedures); {F.P1} (introducción).")

    s = tabla(d, "Módulo 3 · Procedimientos", "Los procedimientos cubren tres áreas: AWP, IM y WFP",
              ["Procedimiento", "Qué establece", "Responsable típico"],
              [["1.0 AWP", "Cláusulas contractuales, Path of Construction, secuencia de ingeniería y compras, estándares de control",
                "Gerencia del proyecto y AWP Champion"],
               ["2.0 IM", "WBS, nomenclatura, intercambio de datos, interfaces de software y atributos del modelo 3D",
                "Information Manager"],
               ["3.0 WFP", "Workface Planners, IWP, gestión de restricciones, ejecución en campo y reportes",
                "Contratista de construcción con el WFP Coordinator"]],
              [2.0, 6.7, 3.4], tam=12.5, alto_fila=0.95,
              nota="Insight-AWP incluye plantillas: estrategia de ejecución, IWP, plan diario, informe semanal, auditoría y perfiles de puesto.")
    notas(s, """
La Quick Start Guide indica que los procedimientos deben cubrir tres áreas clave:
• Advanced Work Packaging: lenguaje contractual, el camino óptimo de construcción, la secuencia de ingeniería y compras y los estándares de control del proyecto.
• Information Management: estándares para la WBS, la nomenclatura, la generación e intercambio de datos, las interfaces de software y la estructura y atributos del modelo 3D.
• Workface Planning: Workface Planners, IWP, gestión de restricciones, ejecución en campo y reportes.
Los procedimientos de Insight se apoyan en una "caja de herramientas" (Toolbox) con documentos modelo (SD01 a SD07), procedimientos complementarios (andamios, equipos, capacitación, empaquetamiento) y perfiles de puesto (JD01 a JD05). Ojo: el INDICE.md señala referencias cruzadas erróneas entre SD06 y SD07.
""", f"{F.QS} (§2); {F.P1}; {F.P2}; {F.P3} (WFP Toolbox); {F.IDX} §4.2.")

    s = bloques(d, "Módulo 3 · Contrato", "AWP se exige en el contrato o no ocurre", [
        ("contract", "Procedimiento en la licitación", "Va con la solicitud de propuesta (RFP) en todo tipo de contrato"),
        ("clipcheck", "Compromiso del postor", "La oferta declara su intención de cumplirlo"),
        ("calendar", "Cronograma a nivel 3 y 5", "CWP en el nivel 3 e IWP en el nivel 5"),
        ("usertie", "Planificadores calificados", "Currículos entrevistados y aprobados por el propietario")],
        nota="Incluya también los datos del modelo 3D y de los fabricantes como entregables del contrato.")
    notas(s, """
El Procedimiento 3.0 de Insight establece que el procedimiento de WFP se entrega a los postores como parte de la solicitud de propuesta (RFP, Request for Proposal) para todo tipo de contrato, y que la oferta debe declarar la intención de cumplirlo.
La cláusula modelo dice, en síntesis: el contratista participará en el programa de Workface Planning del propietario; su cronograma se desglosará al nivel 3 con CWP y al nivel 5 con IWP; presentará currículos de planificadores calificados, que el propietario entrevistará; el número de planificadores seguirá la tabla de carga de recursos; y los costos se mostrarán en el formulario de precios.
La Quick Start Guide añade que la entrega del modelo 3D y de los datos de los fabricantes también se asegura con una cláusula contractual que los identifica como entregables.
""", f"{F.P3} (§3 How to apply this procedure: 'Contract language'); {F.QS} (§3 3D Model and Fabrication); {F.P1} (§5).")

    s = proceso(d, "Módulo 3 · Selección de contratistas",
                "Evalúe la capacidad AWP de cada postor en una conversación, no en un papel", [
                    ("listcheck", "Aplicar la tabla de puntuación", "El Champion califica cada oferta con la plantilla de evaluación"),
                    ("comments", "Entrevistar al postor", "Un representante explica cómo aplicaría WFP en la obra"),
                    ("percent", "Calcular el puntaje", "Resultado como porcentaje del máximo alcanzable"),
                    ("scale", "Integrar a la evaluación técnica", "El equipo de contratos lo pondera con el resto")],
                nota="Un contratista novato dispuesto a aprender es mejor socio que un «experto» que no practica.")
    notas(s, """
Según el Procedimiento 1.0 de Insight (§10), el AWP Champion trabaja con el equipo de contratos y la gerencia del proyecto para evaluar cada oferta. Aplica la tabla de puntuación de ofertas (plantilla SD02) a cada propuesta y entrevista a un representante de cada postor para completar la segunda parte de la evaluación. El puntaje final, expresado como porcentaje del máximo alcanzable, orienta sobre la capacidad del postor para cumplir su parte de los procedimientos de WFP, y el equipo de contratos lo considera en la evaluación técnica.
El curso 2023 aporta dos lecciones: muchos contratistas dicen ser expertos e incluso envían procedimientos bien escritos, pero la única forma de saberlo es sentarse a conversar con ellos; y no ser experto no debería excluir a un contratista: es mejor un novato que quiere aprender que un "experto" que no aplica el proceso.
""", f"{F.P1} (§10 Bid Assessments); {F.CUR} (AWP Related Lessons Learned, lecciones 4 y 5).")

    s = proceso(d, "Módulo 3 · Software", "Elija el software WFP antes del FEED, según lo que ya usa", [
        ("search", "Relevar los sistemas actuales", "Modelo 3D, gestión de materiales y control documental"),
        ("listcheck", "Definir las necesidades", "Paquetes en 3D, valor planificado y simulación 4D"),
        ("link", "Evaluar la compatibilidad", "El Champion y el Information Manager comparan productos"),
        ("check", "Seleccionar antes del FEED", "Front End Engineering Design: antes del diseño detallado")],
        nota=("Recuerde: ", "primero las personas y el proceso; el software lo acelera, no lo reemplaza."))
    notas(s, """
El software de Workface Planning organiza los datos del proyecto sobre el modelo 3D para que los planificadores creen y gestionen IWP en un entorno virtual. También calcula el valor planificado a partir de tasas de instalación y reglas de avance del estimado, muestra el estado de preparación de cada IWP (materiales y planos recibidos) y permite simulaciones 4D.
Antes del inicio del FEED (Front End Engineering Design, ingeniería básica), el AWP Champion y el Information Manager evalúan las funciones y la compatibilidad de los productos con el software que ya se usa para el modelo 3D, la gestión de materiales y el control documental.
Nota: en 2017 los procedimientos citaban ConstructSim y SmartPlant Construction; el mercado ha cambiado, por lo que conviene revisar las opciones actuales.
""", f"{F.QS} (§4 Workface Planning Software); {F.P1} (§8); {F.P2} (§6); {F.IDX} §4.2.")

    s = codigo_wbs(d, "Módulo 3 · Nomenclatura", "La WBS y la nomenclatura comunes son el idioma del proyecto",
                   "El mismo código identifica componentes, planos, spools, actividades, códigos de costo y paquetes.")
    notas(s, """
La estructura de desglose del trabajo (WBS, Work Breakdown Structure) es el sistema de numeración que divide el proyecto en partes manejables. Alinea trabajo, tiempo y costo: sirve de base para los paquetes, el cronograma y los códigos de costo.
Ejemplo de los procedimientos de Insight: WTF-I-12-E4-C05-14 = planta de tratamiento de agua (WTF) · zona ISBL (I; O sería OSBL) · CWA 12 · disciplina E (movimiento de tierras) y subdisciplina 4 (excavación) · paquete C05 (C = CWP; E = ingeniería, M = módulos, F = fabricación, P = compras) · 14 = IWP, plano o spool.
ISBL/OSBL: dentro o fuera de los límites de batería de la planta.
Consejo del curso 2023: la WBS de AWP no se ocupa del costo, sino de que el campo sea eficiente. Si Controles quiere niveles adicionales (tipo de costo, CapEx/OpEx), no los mezcle en el desglose de AWP; alinee solo los niveles importantes.
""", f"{F.P3} y {F.P2} (§2 Definiciones: WBS y Project Nomenclature); {F.CUR} ('What is the AWP-based Work Breakdown Structure?').")

    s = proceso(d, "Módulo 3 · Arranque", "Arranque con un kick-off AWP y un registro de lecciones aprendidas", [
        ("calendar", "Dentro de 30 días", "Seminario de un día tras la adjudicación del contrato"),
        ("teach", "Mañana: capacitación", "Conceptos, entregables e interdependencias de AWP, IM y WFP"),
        ("bulb", "Tarde: lecciones", "Experiencias de otros proyectos y registro abierto a todos"),
        ("group", "Comité de dirección", "Representantes de cada actor; reunión mensual")],
        nota="El Champion consolida el registro de lecciones y lo difunde en todo el proyecto.")
    notas(s, """
El Procedimiento 1.0 de Insight (§11) establece que el AWP Champion, con apoyo de la gerencia del proyecto, realiza un seminario de lanzamiento y lecciones aprendidas con representantes de todos los actores, dentro de los 30 días posteriores a la adjudicación del contrato.
La jornada completa se divide así: por la mañana, un programa de capacitación sobre los conceptos, entregables e interdependencias de AWP, IM y WFP; por la tarde, lecciones aprendidas de otros proyectos y los procedimientos del proyecto, con una sesión interactiva en la que cada actor aporta sus propias lecciones a un registro.
Luego se forma un comité de dirección de WFP con un representante de cada grupo, que se reúne mensualmente durante todo el proyecto para plantear problemas y resolverlos.
""", f"{F.P1} (§11 AWP-IM-WFP Kick-off and Lessons Learned).")


def m4(d):
    d.pie = "M4 · FASE 1: PLANIFICACIÓN PRELIMINAR"
    s = separador(d, 4, "Módulo 4 · Fase 1: Planificación preliminar", "En FEL 2 se decide cómo se construirá la planta",
                  "Áreas de construcción, Path of Construction, talleres de planificación y plan de liberación de paquetes.",
                  fase=1)
    notas(s, """
Separador del Módulo 4, primera fase del ciclo AWP. La mejor práctica es iniciar las actividades de planificación de AWP en FEL 2 (etapa de selección). Aquí se definen las áreas de construcción (CWA), se desarrolla el Path of Construction en talleres interactivos y se obtiene el primer plan de liberación de paquetes.
Todo lo que se decide en esta fase condiciona a Ingeniería y Compras en la siguiente.
""", f"{F.CUR} ('AWP and the Stage Gate System'); {F.OMG} (Stage 1 – Preliminary Planning).")

    s = linea_tiempo(d, "Módulo 4 · Etapas", "AWP se implementa en cuatro etapas ligadas a las compuertas del proyecto", [
        ("FEL 2", "Planificación preliminar", "Marco AWP, CWA y primer Path of Construction"),
        ("FEL 3", "Ingeniería y compras", "POC congelado; EWP y PWP en secuencia"),
        ("EJECUCIÓN", "Construcción e integración", "IWP, restricciones y backlog en campo"),
        ("ARRANQUE", "Comisionamiento y puesta en marcha", "SWP, TOP y entrega por sistemas")],
        nota=("FEL: ", "Front End Loading, etapas de definición del proyecto previas a la decisión de inversión."),
        colores=[NARANJA_OSC, NARANJA, AZUL_MEDIO, AZUL])
    notas(s, """
El CII describe cuatro etapas para implementar AWP a lo largo del proceso de Front End Loading (FEL), que se corresponden con FEL 2, FEL 3, la ejecución y el comisionamiento:
• Etapa 1, planificación preliminar (FEL 2): se establece el marco AWP, las CWA y el primer Path of Construction (POC).
• Etapa 2, ingeniería de detalle y compras (FEL 3): con el POC definido, la ingeniería y las compras se secuencian en consecuencia.
• Etapa 3, construcción e integración: disciplina en el frente de trabajo e integración continua.
• Etapa 4, comisionamiento y puesta en marcha: el foco pasa del avance de construcción a la preparación de sistemas.
El Framework y la COAA describen el mismo flujo en tres etapas (planificación preliminar, ingeniería de detalle y construcción) más la entrega y el arranque.
""", f"{F.OMG} (Planning and Implementation Stages); {F.FW} (Stage I, II, III).")

    s = tabla(d, "Módulo 4 · Compuertas", "Cada etapa tiene una compuerta y un entregable AWP",
              ["Etapa", "Compuerta", "Entregables AWP", "Estimado"],
              [["FEL 1 · Evaluar", "Compuerta 1", "Sin requisitos AWP", "—"],
               ["FEL 2 · Seleccionar", "Compuerta 2", "Plan AWP, CWA, primer POC, matriz EWP/CWP", "Por CWA y disciplina"],
               ["FEL 3 · Definir (FEED)", "Compuerta 3 · decisión de inversión (FID)", "POC final firmado, planes de liberación, WBS",
                "Por CWA, disciplina y secuencia"],
               ["Ejecución", "—", "EWP, CWP e IWP", "Ofertas contra estimado por CWP"]],
              [2.6, 3.1, 3.9, 2.5], destacar={2}, mono=(), tam=12, alto_fila=0.85,
              nota="El Path of Construction es un entregable de la compuerta 3: debe firmarse antes de la ingeniería de detalle.")
    notas(s, """
La mayoría de las empresas usa un sistema de compuertas (stage gates) para verificar los objetivos y el avance del proyecto antes de pasar a la siguiente fase. El curso 2023 describe cinco etapas: FEL 1 (evaluar), FEL 2 (seleccionar), FEL 3 (definir, también llamada FEED), ejecución y operación. La compuerta 3 corresponde normalmente a la decisión final de inversión (FID, Final Investment Decision).
La mejor práctica es empezar la planificación AWP en FEL 2 e incluir los entregables AWP en las revisiones de compuerta. El POC es un entregable de la compuerta 3 y debe completarse y aprobarse antes de iniciar la ingeniería de detalle.
El estimado también evoluciona: sin requisitos AWP en FEL 1; separado por CWA y disciplina en FEL 2; por CWA, disciplina y secuencia en FEL 3; y en ejecución las ofertas de los contratistas se evalúan contra el estimado por CWP.
""", f"{F.CUR} ('AWP and the Stage Gate System', 'Timing of Estimate Requirements').")

    s = bloques(d, "Módulo 4 · CWA", "Divida el terreno en CWA antes de diseñar", [
        ("target", "Prioridad", "Aislar las áreas de alta prioridad"),
        ("contract", "Contratación", "Áreas a cargo de contratistas distintos"),
        ("road", "Racks de tuberías", "Delimitar bien su espacio"),
        ("hourglass", "Horas similares", "Mismo orden de horas de campo, no el mismo tamaño"),
        ("industry", "Función", "Áreas con función propia, como un patio de tanques"),
        ("project", "Proceso", "No tienen que coincidir con las unidades de proceso")], cols=3,
        nota="Cree las CWA a inicios de FEL 2 (o al comienzo de FEL 3, como máximo) y publíquelas en un plano marcado.")
    notas(s, """
Cuándo: las CWA deben crearse temprano en FEL 2 o, a más tardar, al comienzo de FEL 3, para usarlas en el POC, el cronograma y el desglose del estimado.
Qué se necesita: el plano de implantación, una comprensión temprana del alcance y las consideraciones clave para la secuencia de construcción.
Quién participa: es una oportunidad temprana de colaboración con el equipo de proyecto e Ingeniería, pero la discusión la lidera Construcción.
Criterios del curso 2023: prioridad (aislar áreas prioritarias), contratación (áreas de contratistas distintos), racks de tuberías (delimitar bien), tamaño (no tienen que ser iguales), horas (horas de campo similares), función (por ejemplo, patios de tanques), proceso (no tienen que coincidir con las unidades de proceso). Las instalaciones existentes sin alcance no reciben CWA.
Resultado: un plano de implantación marcado con las CWA, emitido a todos los actores.
""", f"{F.CUR} ('When are CWAs created?', 'What should be considered in defining CWAs?', 'What is the output?').")

    s = plano(d, "Módulo 4 · Path of Construction", "El Path of Construction (POC) responde: ¿cómo y en qué orden se construye?",
              secuencia=True, nota_lateral=[
                  ("compass", "¿En qué dirección?", "¿De norte a sur? ¿De izquierda a derecha?"),
                  ("target", "¿Qué va primero?", "Prioridades y áreas críticas"),
                  ("crane", "¿Con qué recursos?", "Accesos, grúas, acopio y módulos")])
    notas(s, """
El Path of Construction (POC) es la secuencia óptima de ejecución de las actividades de construcción, dentro de las CWA y los CWP, para lograr el desempeño deseado del proyecto. El cronograma de entregables de ingeniería debe alinearse con él.
Responde preguntas como: ¿cómo se construirá la planta? ¿De norte a sur? ¿De izquierda a derecha? ¿Cuáles son las prioridades? ¿Cómo se aprovechan mejor los recursos y las condiciones del sitio?
Omega 365 lo llama la piedra angular de AWP: define el orden en que se ejecutarán, probarán y entregarán las actividades, sistemas y áreas.
El plano muestra una secuencia ilustrativa (números naranjas): primero la subestación, luego la unidad de proceso y el rack, etc. Cada proyecto tendrá la suya.
""", f"{F.CUR} ('Definition - A Path of Construction', 'Defining Your Construction Driven Plan'); {F.OMG} (Path of Construction).")

    s = bloques(d, "Módulo 4 · Componentes del POC", "El POC tiene componentes definidos, no es un dibujo libre", [
        ("map", "Plano marcado", "CWA y secuencia sobre el plano de implantación"),
        ("sitemap", "Matriz de CWP", "Disciplina × área, con horas por paquete"),
        ("file", "Informe del POC", "Objetivos, alcance, prioridades, restricciones y compras críticas"),
        ("play", "Simulación", "Recorrido 4D para validar la secuencia con los actores")],
        nota="Anexos típicos: ruta de carga pesada, plan de izajes, lista de equipos y plazos de compra.")
    notas(s, """
Según el curso 2023, el POC tiene componentes concretos:
• Plano de implantación marcado con las CWA y la secuencia.
• Matriz de CWP (disciplina × área): compara el alcance previsto con las horas para detectar anomalías.
• Informe del POC: objetivos, proceso y momento de desarrollo, alcance (y lo que queda fuera), prioridades del proyecto, restricciones principales, lista de CWA, consideraciones de compras (equipos de largo plazo de entrega), consideraciones operativas, etc.
• Anexos: estudio de ruta de carga pesada, plan de modularización o fabricación, lista de equipos, resumen de plazos de compra, programa de paradas de planta, plan de izajes y grúas, evaluación de mano de obra.
• Simulación: una animación de la secuencia ayuda a detectar errores y a comunicar el plan a los actores.
""", f"{F.CUR} ('The Components of the Path of Construction', 'Output - POC Report Components', 'Output - POC Simulation').")

    s = tabla(d, "Módulo 4 · Roles del POC", "Construcción lidera el POC; Ingeniería y Compras lo validan",
              ["Rol", "Papel en el Path of Construction"],
              [["Construction Manager", "Dueño del POC: lidera su desarrollo y lo mantiene actualizado"],
               ["Gerente del proyecto", "Convoca el proceso y asegura que domine la lógica de construcción"],
               ["Líder de Ingeniería", "Expone límites técnicos como restricciones blandas o duras"],
               ["Líder de Compras", "Aporta plazos de equipos críticos y la estrategia de compras"],
               ["Contratista de construcción", "Participa en los talleres o revisa el POC durante la licitación"]],
              [3.6, 8.5], destacar={0}, mono=(), tam=13.5)
    notas(s, """
El POC es un entregable dirigido por Construcción: su objetivo es traer la planificación de la construcción al proyecto lo antes posible. Por eso su dueño final es el Construction Manager (curso 2023).
El Procedimiento 1.0 de Insight (§13) asigna al gerente sénior del proyecto la responsabilidad de convocar el proceso y asegurar que la lógica de construcción optimizada sea la influencia dominante en el POC final.
Ingeniería ayuda a Construcción a entender los límites del plan (por ejemplo, que no se puede diseñar una fundación sin los datos del equipo), y esos límites se expresan como restricciones blandas o duras. Compras aporta los plazos de equipos críticos.
El contratista de construcción participa en las reuniones si la fase y el tipo de contrato lo permiten; si no, recibe el POC en la licitación para alinear su plan de ejecución.
Omega 365 ubica la propiedad del POC en el EPC/EPCM bajo la gobernanza del propietario: defina el criterio según su modelo de contrato.
""", f"{F.CUR} ('Path of Construction - Roles & Responsibilities'); {F.P1} (§13 Optimal Path of Construction); {F.OMG} (Governance of the PoC).")

    s = proceso(d, "Módulo 4 · Talleres", "El POC se construye en sesiones de planificación interactiva", [
        ("helmet", "POC sin restricciones", "Solo Construcción: el plan ideal a partir del plano de implantación y el cronograma de nivel 1"),
        ("comments", "POC con restricciones", "Taller interactivo: Ingeniería y Compras presentan plazos y restricciones blandas y duras"),
        ("flag", "POC final", "Con datos de FEL 3 y todos los actores: base del cronograma EPC de nivel 3")],
        nota=("IPP: ", "Interactive Planning Session. Todos los actores, en la misma sala, frente al plano."))
    notas(s, """
El curso 2023 propone un enfoque iterativo en tres pasos:
1) POC sin restricciones: solo personal de Construcción, sin limitaciones; es un plan puramente constructivo (insumos: plano de implantación, cronograma de nivel 1, estimado FEL 1).
2) POC con restricciones: se incorporan los aportes de Ingeniería y Compras y se revisan las restricciones blandas y duras (estrategias preliminares de compras, recursos, modularización y contratación; cronograma y estimado de nivel 2). Normalmente se hace en una reunión de planificación interactiva donde cada actor presenta sus plazos y restricciones.
3) POC final: con los planes finales y los datos técnicos de FEL 3, con todos los actores; es la base del cronograma EPC de nivel 3 y un entregable de la compuerta 3.
AWP vs Lean destaca que en AWP el POC se desarrolla colaborativamente en una serie de sesiones interactivas.
""", f"{F.CUR} ('Developing the POC: An iterative approach', 'How is it done?'); {F.P1} (§14); {F.LC} (tema 1).")

    s = gantt_liberacion(d, "Módulo 4 · Plan de liberación", "Del taller sale el plan de liberación de CWP y EWP",
                         "Ingeniería y Compras calculan hacia atrás desde la fecha de inicio de cada CWP.")
    notas(s, """
El resultado ideal del taller del POC es la lista completa de CWP de una sola disciplina y la secuencia en que deben iniciar la construcción: el plan de liberación de CWP (CWP Release Plan). Establece, en formato de cronograma, la secuencia ideal y el desfase aproximado entre los inicios de cada CWP.
Luego Ingeniería y Compras hacen un "cálculo hacia atrás": estiman la duración de cada EWP y cada PWP que debe soportar cada CWP. El EWP termina con el último plano IFC; el PWP, con el último componente recibido en obra. Las actividades van en serie (fin a inicio).
El diagrama reproduce el ejemplo del Procedimiento 1.0 ("Instalar intercambiadores de calor") de forma ilustrativa: pilotes, concreto, acero, tuberías, electricidad e instrumentación (E & I), traceado eléctrico y aislamiento, escalonados.
Si hay módulos, un grupo de menos de 10 módulos se trata como un solo CWP. En esta etapa las duraciones son estimados de orden de magnitud (±25 %).
""", f"{F.P1} (§14 Interactive Planning Workshop: CWP Release Plan y EWP Release Plan).")

    s = linea_tiempo(d, "Módulo 4 · Congelar el POC", "El POC se define en FEL 2 y se congela en FEL 3", [
        ("FEL 1", "Evaluar", "Sin requisitos AWP"),
        ("FEL 2", "Crear el POC", "Primera secuencia de prioridades para evaluar los demás planes"),
        ("FEL 3 · INICIO", "Actualizar", "Se ajusta con restricciones y datos técnicos"),
        ("FEL 3 · FIN", "Congelar y firmar", "Entregable de la compuerta 3, antes de la ingeniería de detalle")],
        nota="Congelar el POC a tiempo da a Ingeniería la mejor oportunidad de cumplir el plan.",
        colores=["6D6E71", NARANJA_OSC, NARANJA, NARANJA])
    notas(s, """
Cuándo se crea: el POC debe crearse inicialmente en FEL 2 (selección). Así se tiene una secuencia de prioridades contra la cual evaluar todos los demás planes del proyecto.
Cuándo se finaliza: se actualiza al inicio de FEL 3 (definición) y se cierra al final de FEL 3. Fijarlo en ese momento da al contratista de ingeniería la mejor oportunidad de entregar según el plan.
Omega 365 recuerda que el POC es un documento vivo: después de congelarlo se mantiene y se actualiza si cambian las condiciones, pero los cambios se gestionan formalmente porque afectan la secuencia de CWP, de ingeniería y de compras.
""", f"{F.CUR} ('When is the POC created?', 'When is the POC finalized?'); {F.OMG} (Development of the PoC); {F.PRI}.")

    s = tabla(d, "Módulo 4 · Niveles del cronograma", "El cronograma se escalona en 7 niveles, del año a la hora",
              ["Nivel", "Unidad de planificación", "Horizonte", "Paquete AWP"],
              [["1", "Planta", "Año", ""], ["2", "Construction Work Area", "6 meses", "CWA"],
               ["3", "Construction Work Package", "3 meses", "CWP"], ["4", "Código de función", "Mes", ""],
               ["5", "Installation Work Package", "Semana", "IWP"], ["6", "Plan diario del capataz", "Día", ""],
               ["7", "Tarea", "Hora", ""]],
              [1.2, 5.2, 2.4, 2.6], destacar={2, 4}, mono=(0, 3), tam=14, alto_fila=0.52,
              nota=[[{"t": "El CWP se divide en IWP: ", "negrita": True, "color": "1A1A1A"},
                     {"t": "el planificador entrega esa secuencia al programador como cronograma de nivel 5."}]])
    notas(s, """
Los procedimientos de Insight-AWP (2017) definen siete niveles de cronograma, cada uno con su unidad de planificación y su horizonte:
Nivel 1: planta, año. Nivel 2: CWA, 6 meses. Nivel 3: CWP, 3 meses. Nivel 4: código de función, mes. Nivel 5: IWP, semana. Nivel 6: plan diario, día. Nivel 7: tarea, hora.
En la práctica, el cronograma del proyecto se lleva hasta el nivel 3 con CWP. Luego el Workface Planner lo baja al nivel 5 dividiendo cada CWP en IWP y entregando la secuencia al programador. Según la Quick Start Guide, el cronograma de nivel 5 solo debe contener CWP, IWP e hitos.
Advertencia: el Glosario del CII ubica el IWP en el nivel 4. Defina el criterio en el procedimiento del proyecto.
""", f"{F.P1} (§2 Definiciones: niveles de cronograma); {F.QS} (§6 The Project Schedule); {F.IDX} §3.")

    s = checklist(d, "Módulo 4 · Entregables", "Entregables de la Fase 1: la lista de verificación",
                  "Fase 1 · Planificación preliminar (FEL 2)", [
                      ("Plan AWP del proyecto", "objetivos, alcance y responsables"),
                      ("Plano con las CWA", "emitido a todos los actores"),
                      ("Path of Construction", "informe, plano marcado y simulación"),
                      ("Matriz EWP/CWP", "disciplina × área"),
                      ("Plan de liberación preliminar", "CWP, EWP y PWP"),
                      ("Procedimientos AWP, IM y WFP", "aprobados"),
                      ("Estrategia de contratación", "con cláusulas AWP")],
                  nota="Todo entra en la revisión de la compuerta 2 y se completa durante FEL 3.")
    notas(s, """
Lista de verificación de la Fase 1. Estos entregables entran en la revisión de la compuerta 2 y se completan o congelan durante FEL 3:
• Plan AWP del proyecto, que el curso 2023 describe como el acuerdo entre propietario, contratista de ingeniería y construcción, actualizado durante las fases tempranas.
• Plano de implantación con las CWA, emitido a todos los actores.
• Path of Construction: informe, plano marcado, matriz de CWP y simulación.
• Matriz EWP/CWP por disciplina y área (en FEL 2 aparece cada disciplina en cada área; se refina en FEL 3).
• Plan de liberación preliminar de CWP, EWP y PWP.
• Procedimientos AWP, IM y WFP aprobados.
• Estrategia de contratación con las cláusulas AWP.
Las CWA dan un desglose coherente para el estimado, la WBS y el cronograma, lo que ayuda a alinearlos.
""", f"{F.CUR} ('FEL2 / Select Stage AWP Activities', 'How does AWP help?', 'EWPs Through the Phases'); {F.OMG} (Stage 1); {F.PRI}.")
