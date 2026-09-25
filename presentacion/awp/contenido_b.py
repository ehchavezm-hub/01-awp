"""Módulos M5 a M8 (láminas 47 a 86)."""
from . import fuentes as F
from .diseno import (AZUL, AZUL_MEDIO, GRIS_MEDIO, NARANJA, NARANJA_OSC, bloques, bloques_horizontales,
                     checklist, ciclo, cita, comparacion, dato, embudo, flujo, notas, pares, proceso, separador,
                     tabla)
from .especiales import calendario


def m5(d):
    d.pie = "M5 · FASE 2: INGENIERÍA DE DETALLE Y COMPRAS"
    s = separador(d, 5, "Módulo 5 · Fase 2: Ingeniería y compras", "La ingeniería se entrega en el orden en que se construye",
                  "Path of Engineering, paquetes de ingeniería y de compras, planes de liberación y preparación de los CWP.",
                  fase=2)
    notas(s, """
Separador del Módulo 5, segunda fase. Con el Path of Construction congelado al final de FEL 3, Ingeniería y Compras secuencian su trabajo según ese orden.
En este módulo: la ingeniería dirigida por construcción, el flujo y la medición de los EWP, el impacto en compras (Procurement Work Number) y la preparación de los CWP.
""", f"{F.CUR} (Lecciones 'Construction Driven Engineering', 'Understanding EWP Workflows', 'How Does AWP Impact Procurement?'); {F.OMG} (Stage 2).")

    s = cita(d, "Módulo 5 · Ingeniería", "AWP no agrega trabajo a Ingeniería: cambia el orden",
             "“La intención no es crear trabajo extra para Ingeniería ni cambiar su forma de trabajar, sino darle "
             "prioridades para que avance en las áreas correctas.”", "CURSO AWP 2023 · LECCIÓN 3 (ADAPTACIÓN)",
             puntos=[("ruler", "AWP no debería aumentar el alcance ni las horas de Ingeniería"),
                     ("cycle", "Se puede seguir diseñando por sistemas: cambia cómo se entregan los paquetes"),
                     ("handshake", "Exige el compromiso del liderazgo de Ingeniería")])
    notas(s, """
Esta es una de las objeciones más frecuentes ("así no trabaja Ingeniería; esto la va a frenar"). El Education Framework del CII la llama una de las grandes falacias sobre AWP: el proceso debería tener poco impacto en la productividad de Ingeniería, que puede seguir diseñando por sistemas. La diferencia está en cómo se distribuyen los entregables y en la prioridad que guía la secuencia.
El curso 2023 aporta consideraciones para el primer proyecto: la ingeniería dirigida por construcción cambia hábitos y procesos, puede generar resistencia y requiere compromiso del liderazgo de Ingeniería; a veces obliga a usar supuestos de diseño que la ingeniería tradicional no haría, y es común que propietarios o EPC incentiven a sus equipos para la transición.
""", f"{F.CUR} ('How Does AWP Impact Engineering?', 'Is AWP an Engineering burden?', 'Pilot Considerations'); {F.FW} (objeción 'This isn't how engineering works').")

    s = comparacion(d, "Módulo 5 · Path of Engineering",
                    "Tradicional: se diseña lo disponible. AWP: se diseña lo que se construirá primero",
                    dict(titulo="Enfoque tradicional", color=GRIS_MEDIO, icono_res="xmark_g",
                         puntos=[("Secuencia de ingeniería", "Ingeniería avanza según su propia lógica"),
                                 ("Liberación a construcción", "Se emiten planos a medida que se terminan"),
                                 ("Se ejecuta el alcance disponible", "El campo trabaja donde hay información")],
                         resultado="Frentes incompletos, esperas y retrabajo"),
                    dict(titulo="Enfoque AWP", color=NARANJA, icono_res="check_o",
                         puntos=[("Secuencia de construcción", "El Path of Construction (POC) fija el orden"),
                                 ("Secuencia de ingeniería", "Los EWP se entregan en el orden del POC"),
                                 ("Se ejecuta según el plan acordado", "Cada CWP llega completo a campo")],
                         resultado="Paquetes completos, en orden y a tiempo"))
    notas(s, """
La diferencia no está en cuánto trabajo hace Ingeniería, sino en el orden en que lo entrega.
Enfoque tradicional: Ingeniería define su propia secuencia, libera documentos a Construcción a medida que los termina, y Construcción ejecuta el alcance que tenga disponible. Resultado: frentes de trabajo incompletos y cuadrillas esperando información.
Enfoque AWP: Construcción define primero el POC; Ingeniería lo usa como base de su Path of Engineering y entrega EWP completos por CWA ("construimos de norte a sur: denos primero los planos de la unidad norte"); Construcción ejecuta según el plan acordado.
Para lograr esta "ingeniería dirigida por construcción" hacen falta dos cosas: el compromiso del contratista de Ingeniería y un buen POC. Ingeniería, a su vez, explica los límites del plan (por ejemplo, pilotes → fundación → equipo) como restricciones en los talleres del POC.
""", f"{F.CUR} (Lección 3: 'Understanding the Path of Engineering'; 'Construction Driven Engineering'; 'Limitations').")

    s = flujo(d, "Módulo 5 · Control de la ingeniería", "Gestionar la ingeniería por CWA da alertas tempranas", [
        ("map", "CWA como miniproyecto", "Cada área con su alcance, horas y fechas"),
        ("file", "Entregables discretos", "EWP pequeños y completos"),
        ("chart", "Seguimiento fino", "Avance por paquete, no por disciplina global"),
        ("warning", "Alerta temprana", "Los desvíos se ven semanas antes")],
        nota="Una ingeniería medida por CWA muestra qué área se atrasa, no solo cuánto se atrasa.")
    notas(s, """
Usar el desglose por CWA para Ingeniería crea una serie de miniproyectos. Combinado con el enfoque tradicional por disciplina, permite un seguimiento más claro y granular.
Se completan entregables discretos de ingeniería que permiten a Construcción empezar; y la granularidad de AWP permite seguir entregables más pequeños, lo que da una indicación más temprana de problemas y retrasos.
En un proyecto sin AWP, el avance de Ingeniería se reporta como un porcentaje global por disciplina; con AWP se sabe qué EWP de qué área está atrasado y a qué CWP afecta.
""", f"{F.CUR} (Lección 3: 'Managing Engineering by CWA'; 'The Outcome').")

    s = proceso(d, "Módulo 5 · Flujo del EWP", "El EWP tiene un flujo propio, de la definición a la liberación", [
        ("sitemap", "Definir el marco", "CWA, WBS y matriz de EWP"),
        ("teach", "Desplegar al equipo", "Capacitar y asignar documentos a cada EWP"),
        ("ruler", "Diseñar y revisar", "Revisión interna de Ingeniería"),
        ("eye", "Revisión externa", "Propietario y contratista revisan a tiempo"),
        ("flag", "Liberar el EWP", "Hito de interfaz que inicia el CWP")],
        nota="Cada EWP se sigue en un plan de liberación con fechas planificadas y reales.")
    notas(s, """
Según el curso 2023, antes de que Ingeniería empiece a desarrollar EWP conviene mapear tres flujos: desarrollo del EWP, despliegue al equipo del proyecto, y revisión y aprobación.
• Marco: establecer el desglose de CWA, crear la WBS y la matriz de EWP.
• Despliegue: capacitar al equipo en la estructura, asignar documentos a los EWP, desglosar el estimado por EWP, organizar el modelo por CWA y gestionar la información por EWP (el número de EWP se marca en los planos).
• Revisión y aprobación: en ejecución los EWP son el entregable final de Ingeniería, emitidos por área y disciplina; la revisión oportuna del propietario y del contratista de construcción es clave.
• Liberación: es el hito de interfaz del cronograma; cada EWP debe estar representado en él. El plan de liberación registra las fechas planificadas (del cronograma EPC aprobado) y las reales.
""", f"{F.CUR} ('Understanding EWP Workflows', 'EWP Rollout', 'EWP Review and Approval', 'Managing EWPs - The Release Plan', 'EWP Preparation - Schedule').")

    s = tabla(d, "Módulo 5 · Reglas de crédito", "Mida el avance de Ingeniería con reglas de crédito por EWP",
              ["Etapa del EWP", "Peso", "Acumulado"],
              [["Inicio del diseño", "5 %", "5 %"], ["Revisión interna de Ingeniería", "20 %", "25 %"],
               ["Emitido para revisión (IFR)", "10 %", "35 %"], ["Revisión y comentarios del cliente", "5 %", "40 %"],
               ["Emitido para construcción (IFC), sin retenciones", "50 %", "90 %"],
               ["Revisión y aprobación de Construcción", "10 %", "100 %"]],
              [7.1, 2.5, 2.5], destacar={4}, mono=(1, 2), tam=14,
              nota="Avance por reglas de crédito × horas asignadas a cada EWP = valor ganado real de Ingeniería.",
              icono_nota="chart_o")
    notas(s, """
Durante la ejecución, mientras la ingeniería avanza, se mide con reglas de crédito para cada EWP. El ejemplo del curso 2023: inicio del diseño 5 %; revisión interna de Ingeniería 20 % (acumulado 25 %); emitido para revisión (IFR, Issued for Review) 10 % (35 %); revisión y comentarios del cliente 5 % (40 %); emitido para construcción (IFC) sin retenciones 50 % (90 %); revisión y aprobación de Construcción 10 % (100 %).
Observe que la mitad del crédito se gana solo cuando el paquete se emite IFC sin retenciones: se premia entregar paquetes completos, no planos sueltos.
Las reglas las propone el contratista de Ingeniería y las revisa y acepta el propietario. Combinadas con las horas asignadas a cada EWP, dan el valor ganado de Ingeniería.
""", f"{F.CUR} ('Engineering KPIs - Execute Stage - In Progress'; 'EWP Rules of Credit').")

    s = flujo(d, "Módulo 5 · Quién prepara los EWP",
              "El contratista de Ingeniería prepara los EWP; Construcción los revisa", [
                  ("usertie", "Gerente de Ingeniería", "Responsable de crear los EWP"),
                  ("ruler", "Equipo de Ingeniería", "Diseña y arma cada paquete"),
                  ("eye", "Propietario y contratista", "Revisan antes de liberar"),
                  ("flag", "Liberación del EWP", "Hito del cronograma que inicia el CWP")],
              nota="En ejecución, los EWP los produce el contratista de Ingeniería, sea cual sea el tipo de contrato.",
              colores=[AZUL, AZUL, NARANJA_OSC, NARANJA])
    notas(s, """
El curso 2023 establece que los EWP los produce el contratista de Ingeniería para la fase de ejecución, independientemente del tipo de contrato. El equipo, liderado por el gerente de Ingeniería, es responsable de crearlos.
Para producir EWP precisos, el contratista de Ingeniería debe conocer el POC y la estructura de paquetes. Debe existir una definición clara de cuándo se completa cada EWP y de la transferencia de información a Construcción, representada en el cronograma como interfaz: EWP completo → revisión del propietario o del contratista de construcción → EWP liberado → desarrollo del CWP.
Si el contratista de Ingeniería cambia entre fases, conviene planificar la transición para no interrumpir el proceso AWP.
""", f"{F.CUR} ('Who Prepares EWPs?', 'EWP Preparation - Schedule', 'EWP Preparation - Roles', 'EWP Preparation - Transition').")

    s = comparacion(d, "Módulo 5 · Compras", "Compras se secuencia por CWP, no por fecha de requisición",
                    dict(titulo="Compras tradicional", color=GRIS_MEDIO, icono_res="xmark_g", numerado=False,
                         puntos=[("Pedidos por conveniencia", "Se agrupan para obtener mejor precio"),
                                 ("Llegada según el proveedor", "Sin vínculo con el frente que la necesita"),
                                 ("Granel sin trazabilidad", "No se sabe qué EWP cubre cada pedido")],
                         resultado="Material en obra, pero no el que se necesita"),
                    dict(titulo="Compras con AWP", color=NARANJA, icono_res="check_o", numerado=False,
                         puntos=[("Matriz de responsabilidad (MRM)", "Quién suministra qué, desde el inicio"),
                                 ("Fecha requerida en obra por EWP", "La primera entrega llega cuando la pide el CWP"),
                                 ("Trazabilidad completa", "Recepción → pedido → requisición → MTO → EWP")],
                         resultado="El material llega en el orden del POC"))
    notas(s, """
Compras es un componente esencial de AWP. El curso 2023 explica:
• Quién suministra qué se define temprano con una matriz de responsabilidad de materiales (MRM, Material Responsibility Matrix).
• El contratista de compras adquiere todo el material que suministra el propietario según la MTO de cada EWP y trabaja con los proveedores para que su documentación apoye el proceso AWP. El contratista de construcción suele encargarse de la recepción, inspección y almacenamiento.
• Los materiales a granel no se compran por EWP: se agregan en pedidos grandes para obtener mejor precio. Para no perder la secuencia, Compras debe verificar que la primera entrega para cada EWP llegue en su fecha requerida en obra (RAS, Required at Site).
• El control exige poder rastrear la compra desde el informe de recepción (MRR), al pedido (PO), a la requisición, a la MTO y al EWP.
""", f"{F.CUR} ('How Does AWP Impact Procurement?', 'Who Supplies What', 'Procurement Roles and Responsibilities', 'Timing', 'Procurement - Methods Used to Control').")

    s = flujo(d, "Módulo 5 · Procurement Work Number", "El Procurement Work Number conecta cada compra con su CWP", [
        ("ruler", "EWP", "Define el alcance y los materiales"),
        ("listcheck", "MTO", "Lista cuantificada de materiales"),
        ("contract", "Pedido (PO)", "Orden de compra al proveedor"),
        ("ship", "Envío", "Documento de despacho"),
        ("warehouse", "Recepción (MRR)", "Informe de material recibido")],
        subtitulo="Cada eslabón lleva el código del EWP/CWP: ese código es el Procurement Work Number.",
        nota="Ítems con tag y fabricados se rastrean uno a uno; el granel se agrega y necesita el código para repartirse.")
    notas(s, """
Desde la perspectiva de AWP, la clave de compras y de la gestión de materiales es la codificación: asignar cada componente a su EWP/CWP. Ese código es el Procurement Work Number.
El curso 2023 distingue tres tipos de compra:
• Ítems con tag: materiales o equipos únicos con nombre propio en el proyecto. Siguen la cadena diseño → MTO → pedido (PO) → documento de envío → informe de recepción (MRR, Material Receiving Report) → cierre.
• Ítems a granel: se piden en grandes cantidades, no son únicos y sirven a varios EWP (tubería, accesorios, válvulas). Es el caso más complejo, porque los pedidos agregan varios EWP.
• Ítems fabricados: se ensamblan fuera de obra (por ejemplo, spools o estructuras) y se gestionan igual que los ítems con tag.
El requisito es poder rastrear la compra desde el MRR hasta el EWP.
""", f"{F.CUR} ('What is a Procurement Work Number?', 'Tagged Items', 'Bulk Items', 'Fabricated Items').")

    s = proceso(d, "Módulo 5 · Flujo del CWP", "El CWP se arma cuando se libera su EWP", [
        ("flag", "EWP liberado", "Hito de interfaz en el cronograma"),
        ("search", "Revisión del EWP", "Construcción verifica errores y faltantes"),
        ("file", "Redacción del CWP", "Alcance, límites, seguridad, calidad y ejecución"),
        ("eye", "Revisión del propietario", "A tiempo para mantener el plan"),
        ("contract", "Liberación del CWP", "Base del alcance para los contratistas")],
        nota="Controle el avance del CWP con reglas de crédito y un plan de liberación que parte de la fecha del EWP.")
    notas(s, """
El marco de los CWP sigue el mismo proceso que el de los EWP. En ejecución, los CWP son el entregable final de Construcción, emitidos por área y disciplina, y suelen usarse como alcance de los contratos de construcción.
Como el EWP es el punto de partida del CWP, es crítico que la información de Ingeniería se libere a tiempo; en el cronograma, el desarrollo del CWP empieza cuando el EWP se libera.
Antes de desarrollar el CWP, Construcción revisa el EWP para detectar problemas. El avance del CWP se mide con reglas de crédito propuestas por quien lo prepara y aceptadas por el propietario. El plan de liberación de CWP toma como punto de partida la fecha de liberación del EWP.
Recomendaciones de redacción: cuidado con el lenguaje que pueda leerse como instrucción; defina con claridad el límite del alcance y lo que harán otros; evite el texto repetido y el lenguaje contractual; y para equipos de proveedores, indique el alcance que queda por hacer en obra.
""", f"{F.CUR} ('Understanding CWP Workflows', 'CWP Preparation - Schedule', 'CWP Preparation - EWP Review', 'CWP Rules of Credit', 'CWP Content - Recommendations').")

    s = bloques_horizontales(d, "Módulo 5 · Quién prepara los CWP",
                             "Construcción define los CWP; quién los redacta depende del contrato", [
                                 ("sitemap", "EPC / EPCM", "Estructura las CWA y los CWP y coordina los entregables (Omega 365)"),
                                 ("helmet", "Gerencia de construcción", "Define tamaño, contenido y secuencia de los CWP (Insight)"),
                                 ("usercheck", "WFP Coordinator", "Crea y gestiona los CWP y entrega la información a los planificadores"),
                                 ("ruler", "Proyectos pequeños", "El contratista de Ingeniería puede preparar también el CWP")],
                             nota="Defina el responsable en el procedimiento AWP antes de licitar.")
    notas(s, """
El curso 2023 indica que quién prepara los CWP depende en gran medida del modelo de contratación del proyecto. En proyectos pequeños, con recursos limitados, el contratista de Ingeniería puede producir también el CWP.
Los procedimientos de Insight asignan a la gerencia de construcción mapear el POC e identificar el tamaño, contenido y secuencia de los CWP, y al WFP Coordinator la creación y gestión de los CWP y la entrega de la información del proyecto a los Workface Planners del contratista.
Omega 365 ubica en el EPC/EPCM la definición de las CWA y los CWP y la coordinación de los entregables de ingeniería, compras y construcción.
Recomendación: fije el responsable en el procedimiento del proyecto antes de licitar, para que las ofertas lo incluyan.
""", f"{F.CUR} ('Who Prepares CWPs?', 'EWP / CWP Preparation - Small Projects'); {F.P1} (§5 y §7); {F.OMG} (roles).")

    s = checklist(d, "Módulo 5 · Entregables", "Entregables de la Fase 2: la lista de verificación",
                  "Fase 2 · Ingeniería y compras (FEL 3 y ejecución)", [
                      ("EWP emitidos en secuencia", "según el plan de liberación"),
                      ("PWP y matriz de responsabilidad", "MRM y fechas requeridas en obra"),
                      ("CWP liberados", "con alcance, límites y requisitos"),
                      ("Modelo 3D con atributos", "organizado por CWA, EWP y CWP"),
                      ("Estimado por CWA, disciplina y secuencia", ""),
                      ("Cronograma de nivel 3", "con hitos de interfaz EWP → CWP"),
                      ("Planes de liberación al día", "planificado frente a real")],
                  nota="En ejecución, los EWP son el entregable final de Ingeniería y los CWP, el de Construcción.")
    notas(s, """
Lista de verificación de la Fase 2:
• EWP emitidos en la secuencia del POC, seguidos con el plan de liberación.
• PWP y matriz de responsabilidad de materiales, con fechas requeridas en obra por EWP.
• CWP liberados, con alcance, límites, seguridad, calidad y requisitos de ejecución.
• Modelo 3D con atributos, estructurado por CWA, EWP y CWP (Procedimiento 2.0).
• Estimado separado por CWA, disciplina y secuencia; en ejecución, las ofertas se evalúan contra el estimado por CWP.
• Cronograma de nivel 3 con una actividad por EWP y por CWP y sus hitos de interfaz.
• Planes de liberación de EWP y CWP con fechas planificadas y reales.
""", f"{F.CUR} ('EWP Review and Approval', 'CWP Review and Approval', 'Timing of Estimate Requirements'); {F.OMG} (Stage 2); {F.P1} (§5); {F.P2}.")


def m6(d):
    d.pie = "M6 · CONSTRUCCIÓN Y WORKFACE PLANNING"
    s = separador(d, 6, "Módulo 6 · Fase 3: Construcción", "En campo, cada capataz recibe un paquete listo para ejecutar",
                  "Workface Planning (WFP), gestión de restricciones, backlog y seguimiento diario del avance.", fase=3)
    notas(s, """
Separador del Módulo 6. Hasta aquí, Construcción definió el orden (Fase 1) e Ingeniería y Compras entregaron sus paquetes en ese orden (Fase 2). Ahora el plan llega al frente de trabajo.
En este módulo se ve el proceso de Workface Planning (WFP): cómo se dividen los CWP en IWP, cómo se eliminan las restricciones antes de liberar un paquete, cómo se mantiene un backlog y cómo se registra el avance.
La barra inferior indica en qué fase del proyecto estamos; se repite en todos los separadores de fase.
""", f"{F.QS} (secciones 5-7); {F.P3}.")

    s = cita(d, "Módulo 6 · La meta", "La meta: cada lunes, un IWP listo para cada capataz",
             "“Dar a cada capataz, al inicio de cada semana, un IWP listo para ejecutar: alcance identificado, "
             "materiales y herramientas disponibles, trabajos previos terminados y andamio listo.”",
             "QUICK START GUIDE · INSIGHT-AWP (TRADUCCIÓN)",
             puntos=[("clip", "Alcance identificado y planos vigentes"),
                     ("boxes", "Materiales y herramientas disponibles"),
                     ("stairs", "Trabajo previo terminado y andamio listo")])
    notas(s, """
Así resume la Quick Start Guide el objetivo final de AWP: dar a cada capataz, al comienzo de cada semana, un IWP "listo para ejecutar". El alcance está identificado, los materiales y herramientas están disponibles, el trabajo previo está terminado y el andamio está montado y apto.
La expectativa del superintendente es que el capataz y su cuadrilla completen el trabajo dentro de la ventana programada y de las horas estimadas. Todo lo anterior (POC, EWP, PWP, CWP) existe para que esta entrega semanal sea posible.
""", f"{F.QS} (Introducción).")

    s = ciclo(d, "Módulo 6 · Workface Planning", "WFP es definir, crear, ejecutar y seguir los IWP", [
        ("search", "Definir", "Revisar el CWP y la secuencia"),
        ("clip", "Crear", "Armar el IWP y liberar restricciones"),
        ("helmet", "Ejecutar", "Entregar el IWP al capataz"),
        ("chart", "Seguir", "Registrar avance y desempeño")], "Workface Planning",
        nota_lateral=["El Workface Planner no solo crea IWP:",
                      "• Verifica el alcance del CWP", "• Gestiona restricciones y backlog",
                      "• Registra avance y desempeño", "• Arma paquetes para la entrega por sistemas"])
    notas(s, """
Definición del curso 2023: Workface Planning es la definición, creación, ejecución y seguimiento de los IWP. Estos paquetes dividen el alcance mayor en tareas ejecutables que se entregan a una cuadrilla. Su propósito es mejorar la eficiencia en campo asegurando que la cuadrilla tenga toda la información y los recursos necesarios.
WFP es la etapa final de AWP, donde toda la planificación se usa en campo.
El Workface Planner hace más que crear IWP: verifica el alcance del CWP (busca errores), gestiona restricciones, crea y mantiene el backlog, sigue el avance con el capataz, reporta el desempeño de instalación y arma paquetes específicos por sistema para la entrega.
Nota del curso: muchos contratistas ya hacen parte de esto de manera informal; AWP no dice que lo estén haciendo mal, sino que estandariza las mejores prácticas.
""", f"{F.CUR} ('Definition - Workface Planning', 'What do Workface Planners do?', 'Understanding the Process of Workface Planning').")

    s = bloques(d, "Módulo 6 · Contenido del IWP", "El IWP contiene todo lo que el capataz necesita", [
        ("file", "Portada", "Nombre, valor planificado y vista del alcance"),
        ("warning", "Emergencias", "Nombres y teléfonos de contacto"),
        ("unlock", "Restricciones", "Lista con firmas de liberación"),
        ("listcheck", "Alcance", "Secuencia básica del trabajo"),
        ("shield", "Seguridad", "Extracto del análisis de riesgos (JHA)"),
        ("clipcheck", "Calidad", "Extracto del plan de inspección (ITP)"),
        ("ruler", "Documentos", "Solo los planos que la cuadrilla necesita"),
        ("boxes", "Materiales y equipos", "Lista verificada contra el almacén")], cols=4, tam_titulo=14)
    notas(s, """
La Quick Start Guide parte de una pregunta simple: ¿qué necesita un capataz para ejecutar el trabajo? La respuesta es el contenido del IWP: portada (nombre del IWP, valor planificado y una imagen del alcance), información de emergencia, restricciones (lista de elementos por satisfacer), alcance y secuencia básica, seguridad, calidad (requisitos del plan de inspección y ensayos, ITP, Inspection and Test Plan), documentos técnicos, materiales, herramientas y equipos, andamios y registro de avance.
Seguridad: el IWP incluye los pasajes pertinentes del análisis de riesgos del trabajo (JHA, Job Hazard Analysis), resaltados, y lleva la firma del área de seguridad.
Recomendación del curso 2023: el IWP no debe ser un documento largo; incluya solo lo que la cuadrilla necesita para ese paquete y evite texto genérico como "recuerde usar su EPP".
""", f"{F.QS} (§6 Installation Work Packages); {F.P3} (§12 Safety y §13 Quality Control); {F.CUR} ('Step 6 - Write the IWP document').")

    s = proceso(d, "Módulo 6 · Del CWP al IWP", "Del CWP al IWP en cuatro pasos, 90 días antes", [
        ("calendar", "Elegir el CWP", "Uno que se ejecutará dentro de unos 90 días"),
        ("comments", "Acordar la secuencia", "El superintendente explica cómo dividir y ordenar el trabajo"),
        ("cube", "Armar los IWP en 3D", "El planificador los define y redacta el alcance de cada uno"),
        ("usercheck", "Aprobar y completar", "El superintendente aprueba; el planificador llena cada sección")],
        nota="No espere trabajar un CWP al día siguiente de recibirlo: convertirlo en IWP toma tiempo.")
    notas(s, """
Proceso de la Quick Start Guide: elija un CWP que se ejecutará en unos 90 días y pida al superintendente que se siente con el planificador y describa cómo dividir y secuenciar el trabajo. El planificador arma los IWP en el entorno 3D y redacta el alcance de cada uno; el superintendente revisa y aprueba la división y la secuencia; luego el planificador completa cada sección del IWP según su alcance.
El curso 2023 detalla seis pasos: revisar el CWP; dividirlo en IWP (sin cortar un isométrico o un tendido de cable a la mitad); crear la lista de planos y verificar que estén IFC (si falta alguno, emitir una RFI); estimar las horas-hombre con tasas estándar; listar y verificar los materiales contra el estado de materiales; y redactar el IWP.
Los CWP se dividen en IWP no antes de tres meses de su ejecución, en una planificación "por olas" (rolling wave).
""", f"{F.QS} (§6 'The process of developing IWPs'); {F.CUR} ('What is an IWP, and how is it made?' pasos 1-6; 'Pro Tip!'); {F.P3} (§9).")

    s = dato(d, "Módulo 6 · Tamaño del IWP", "Empiece con IWP de unas 500 horas y ajuste",
             "500 h", "tamaño inicial de un IWP",
             "Empiece con una rotación (~500 h) y ajuste. Paquetes más pequeños son más fáciles de seguir.",
             apoyos=[("500–1 000", "horas, según el curso 2023 y el tamaño de la cuadrilla"),
                     ("1 : 10", "un capataz por unos 10 trabajadores"),
                     ("7 días", "ventana de ejecución de un IWP")], icono_nombre="clip_o")
    notas(s, """
¿Cuánto trabajo debe contener un IWP? La Quick Start Guide recomienda empezar con una rotación, aproximadamente 500 horas, y dejar que el modelo evolucione hasta adaptarse al proyecto. En general, los paquetes más pequeños son mejores para los capataces: son más fáciles de seguir y guían la ejecución de una secuencia específica.
El curso 2023 da un rango de 500 a 1 000 horas según el tamaño de la cuadrilla, y pide que el trabajo pueda completarse sin detenerse.
Los procedimientos de Insight definen al capataz como responsable de una cuadrilla de una disciplina, típicamente con 10 trabajadores, y el IWP como el trabajo de ese capataz y su cuadrilla en 7 días.
""", f"{F.QS} (§6 'How much work should be in an IWP?'); {F.CUR} ('Step 2 - Break the CWP into IWPs'); {F.P3} (§2 Field Supervision).")

    s = cita(d, "Módulo 6 · Restricciones", "La regla de oro: ningún IWP va a campo con restricciones",
             "“Los IWP no se liberan a campo hasta que estén libres de restricciones y listos para ejecutar.”",
             "QUICK START GUIDE · LA REGLA DE ORO",
             puntos=[("warning", "Críticas: documentos, materiales y andamios"),
                     ("gears", "Secundarias: equipos, controles, seguridad, calidad y personal"),
                     ("clipcheck", "Se liberan con firmas en la página de restricciones")])
    notas(s, """
Según la Quick Start Guide, la eliminación y gestión de restricciones es el mayor cambio respecto de la forma habitual de construir. La regla de oro: los IWP no se liberan a campo hasta que estén libres de restricciones y listos para ejecutar.
Restricción (curso 2023): cualquier elemento que pueda impedir el inicio o el avance del trabajo; por ejemplo, planos faltantes, materiales faltantes, falta de acceso, equipos no disponibles o falta de personal.
Las restricciones críticas suelen ser documentos, materiales y andamios. Las secundarias (equipos de construcción, controles, seguridad, calidad y personal) se resuelven internamente en poco tiempo.
El proceso se gestiona con las firmas de la página de restricciones del IWP; el Workface Planner las recoge. Cuando el IWP queda libre, se imprime, se archiva en control documental y se registra en el Pack Track.
""", f"{F.QS} (§7 Constraint Removal); {F.CUR} ('How to Manage Constraints', 'Standard types of constraints').")

    s = proceso(d, "Módulo 6 · Calendario de restricciones",
                "Las restricciones se liberan en cuatro pasos, con semanas de anticipación", [
                    ("clip", "IWP iniciado", "El planificador crea el paquete a partir del CWP",
                     [("Pequeño / parada", "−6 sem", NARANJA), ("Megaproyecto", "−12 sem", AZUL)]),
                    ("search", "Restricciones identificadas", "Documentos, materiales, andamios, equipos, permisos",
                     [("Pequeño / parada", "−4 sem", NARANJA), ("Megaproyecto", "−10 sem", AZUL)]),
                    ("usercheck", "Restricciones asignadas", "Cada una con dueño, fecha y prioridad",
                     [("Pequeño / parada", "−3 sem", NARANJA), ("Megaproyecto", "−8 sem", AZUL)]),
                    ("unlock", "Restricciones liberadas", "El IWP pasa al backlog, listo para campo",
                     [("Pequeño / parada", "−2 sem", NARANJA), ("Megaproyecto", "−4 sem", AZUL)])],
                nota=("Regla de oro: ", "ningún IWP va a campo mientras tenga una restricción abierta."))
    notas(s, """
El Education Framework del CII propone un calendario típico de restricciones para cada IWP, en semanas antes de su ejecución:
• Proyecto pequeño, parada de planta o turnaround: IWP iniciado 6 semanas antes; restricciones identificadas a las 4; asignadas a las 3; liberadas a las 2, cuando el paquete se libera.
• Proyecto grande, mega o giga: 12, 10, 8 y 4 semanas.
El curso 2023 recomienda eliminar todas las restricciones 2 a 3 semanas antes. Cuando no es posible (trabajo previo, andamios), basta con que estén planificadas antes del IWP, pero el planificador debe vigilar que se cumplan.
Cómo verificar: algunas restricciones se revisan con datos (lista de planos IFC, informe de materiales); otras exigen recorrer la obra (espacio de acopio, acceso libre); otras, conversar (con el capataz general sobre el personal, con el responsable de equipos sobre las grúas).
""", f"{F.FW} (Typical IWP Constraint Schedule by Project Size / Type); {F.CUR} ('Timing of Review', 'How to Check Constraints', 'Pro tip!').")

    s = bloques(d, "Módulo 6 · Gestión de restricciones", "Cada restricción tiene dueño, fecha y prioridad", [
        ("listcheck", "Lista única", "Todas las restricciones abiertas en un solo registro"),
        ("usercheck", "Dueño, fecha y prioridad", "Para cada restricción abierta"),
        ("clipcheck", "Flujo de aprobación", "Cierre formal según el tipo de paquete"),
        ("comments", "Reunión estándar", "Herramientas comunes para revisarlas"),
        ("signs", "Árbol de decisión", "Qué hacer con paquetes que siguen abiertos"),
        ("chart", "Reporte de estado", "Visibilidad para toda la gerencia")], cols=3,
        nota="Los dueños de restricciones informan su avance; el Construction Manager vigila su impacto.")
    notas(s, """
Buenas prácticas de gestión de restricciones del Education Framework del CII: una lista consolidada de todas las restricciones abiertas; asignación de dueño, fecha límite y prioridad para cada una; flujo de aprobación del cierre según el tipo de paquete; herramientas estandarizadas para la reunión de revisión; árbol de decisión para paquetes que mantienen restricciones abiertas; y reporte del estado de las restricciones.
Quién participa: los responsables de despejar cada restricción (permisos, materiales, equipos de seguridad, equipos) informan el avance; el Construction Manager sigue las fechas de inicio planificadas frente a reales, vigila las cantidades retenidas por restricciones para priorizar y entiende el impacto y la criticidad de las restricciones abiertas.
La lista estándar de restricciones del curso 2023 incluye: planos IFC, cronograma, materiales y fabricación, acceso y acopio, disponibilidad de personal, alcance, coordinación con otros oficios, seguridad, permisos, control de calidad, equipos y herramientas, andamios, subcontratistas y proveedores de servicios.
""", f"{F.FW} (Constraint Management Best Practices; Who is Involved in Constraint Management?); {F.CUR} ('Standard types of constraints').")

    s = embudo(d, "Módulo 6 · Backlog", "Mantenga un backlog de IWP libres de restricciones", [
        ("Ventana de 90 días", "−12 sem", "IWP creado en 3D e incluido en el cronograma de nivel 5"),
        ("Armado del IWP", "−4 sem", "Documentos IFC y materiales confirmados"),
        ("Backlog", "−3 sem", "IWP libre de restricciones, listo para elegir"),
        ("Look-ahead de 3 semanas", "−2 sem", "Material separado; andamio y grúas pedidos"),
        ("Campo", "0", "Emitido al capataz y ejecutado")],
        nota="Meta: de 2 a 4 semanas de trabajo libre de restricciones por disciplina.")
    notas(s, """
El backlog es el conjunto de IWP disponibles y libres de restricciones: indica cuánto trabajo hay listo para cada disciplina. La Quick Start Guide lo considera una de las mayores influencias sobre la productividad: el superintendente debe mantener un colchón de trabajo libre de restricciones, planificando al mismo ritmo que se ejecuta.
Cifras: 4 semanas (Quick Start), 2 a 4 semanas (Procedimiento 3.0), 30 días (curso 2023). El backlog debe incluir trabajo "plan B" por si algo falla.
Cómo se calcula (curso 2023): en horas (suma de horas de los IWP libres) o en días (horas disponibles ÷ horas que gana la dotación por día). Ejemplo: 50 personas × 10 h = 500 h/día; con 5 000 h de IWP libres, el backlog es de 10 días.
Cree el backlog antes de movilizar a las cuadrillas: los planificadores se movilizan antes que ellas. El embudo muestra las etapas del Pack Track del Procedimiento 3.0.
""", f"{F.QS} (§7 Backlog); {F.P3} (§7 Pack Track y §8 Backlog); {F.CUR} ('How to Manage a Backlog', 'How to Calculate Backlog').")

    s = calendario(d, "Módulo 6 · Look-ahead", "El look-ahead de tres semanas se alimenta solo del backlog",
                   "Cada semana el superintendente toma IWP libres del backlog y los carga como actividades de nivel 5.")
    notas(s, """
El plan look-ahead es un "minicronograma" que ayuda al Construction Manager a planificar el trabajo. Con Workface Planning, cada entrada del plan es un número de IWP (curso 2023).
Cada semana el superintendente toma IWP libres de restricciones del backlog y los incorpora al cronograma como actividades de nivel 5, formando el look-ahead de tres semanas (Quick Start Guide). El Procedimiento 3.0 añade que se eligen según el cronograma y la realidad del campo.
Todos los IWP de un CWP deben completarse dentro del plazo que el cronograma maestro asigna a ese CWP.
La celda punteada ilustra una alerta: si una disciplina no tiene IWP libres para la semana 3, el backlog está por agotarse y hay que reaccionar ahora.
""", f"{F.CUR} ('The Look-ahead Plan', 'The Look-ahead Plan & Workface Planning'); {F.QS} (§7 Three week look ahead); {F.P3} (§8).")

    s = tabla(d, "Módulo 6 · Pack Track", "Pack Track: una sola hoja muestra el estado de todos los IWP",
              ["Etapa", "Semanas antes", "Hitos que se marcan"],
              [["Ventana de 90 días", "12", "Alcance definido · IWP creado en 3D · incluido en nivel 5"],
               ["Armado del IWP", "4", "Documentos IFC · materiales disponibles · revisión técnica (RFI)"],
               ["Backlog", "3", "Ingreso al backlog · ingreso al look-ahead"],
               ["Look-ahead de 3 semanas", "2", "Material separado y etiquetado · andamio y grúas pedidos"],
               ["Look-ahead de 3 semanas", "1", "Copia impresa · firmas de seguridad y calidad · recursos confirmados"],
               ["Ejecución", "0", "Emitido a campo · trabajo completo"]],
              [3.3, 1.9, 6.9], destacar={2}, mono=(1,), tam=12.5, alinear_col={1: 2},
              nota="El WFP Coordinator arma cada semana un tablero desde el Pack Track para el informe de gestión.")
    notas(s, """
El Pack Track es la hoja de cálculo del Procedimiento 3.0 que sigue el desarrollo de cada IWP y su avance en la eliminación de restricciones. La gestiona el WFP Coordinator del propietario y la alimentan los Workface Planners del contratista.
Cada IWP entra en la ventana de planificación de 90 días cuando se desarrolla en el software WFP; tras incorporarse al cronograma de nivel 5 pasa al armado del IWP, donde permanece hasta que documentos y materiales están listos; luego entra al backlog y, finalmente, al look-ahead de tres semanas cuando se elige para ejecutarse.
La tabla resume las columnas del ejemplo original con las semanas previas a la ejecución. El informe también muestra cuántos IWP de cada CWP se han emitido a campo y devuelto para registrar su avance.
Nota: la tabla original se conservó parcialmente en la conversión; la asignación de semanas es aproximada.
""", f"{F.P3} (§7 Removing Constraints: Pack Track); {F.IDX} §4.1.")

    s = proceso(d, "Módulo 6 · Fecha límite", "Cada IWP tiene fecha de caducidad", [
        ("calendar", "Fecha límite de uso", "La ventana en la que debe completarse"),
        ("clock", "Prórroga corta", "Uno o dos días si falta poco"),
        ("cycle", "Devolución", "Si no se termina, vuelve al capataz general y al planificador"),
        ("clip", "Reorganización", "El alcance pendiente pasa a un nuevo IWP")],
        nota="La fecha límite le dice al capataz que su trabajo sostiene el cronograma.")
    notas(s, """
Lección aprendida de la Quick Start Guide: cada IWP debe tener una fecha límite de uso ("use by date") que muestre al capataz que el trabajo debe completarse en esa ventana para cumplir el cronograma. Si queda trabajo pendiente, la ventana puede extenderse uno o dos días. Si aun así no se completa, el IWP vuelve al capataz general y luego al planificador para reorganizar el trabajo y ubicarlo en un nuevo paquete.
Complemento del Procedimiento 3.0 (ejecución en campo): el capataz general pide el material de cada IWP una semana antes de la fecha planificada y entrega el IWP al capataz antes del inicio. Al terminar, devuelve el IWP al planificador, que retira los documentos originales de calidad y los envía al área de calidad.
""", f"{F.QS} (§7 Execution: 'Lesson Learned'); {F.P3} (§14 Field Execution).")

    s = flujo(d, "Módulo 6 · Avance", "El capataz registra el avance a diario en el IWP", [
        ("helmet", "Capataz", "Anota el avance físico por componente"),
        ("usertie", "Workface Planner", "Lo carga en el software WFP"),
        ("calculator", "Controles", "Valor ganado frente a valor planificado"),
        ("chart", "Gerencia", "Una sola versión de la verdad")],
        nota="Las hojas de tiempo usan el número de IWP como código de costo.")
    notas(s, """
El capataz es responsable de ejecutar el trabajo y registrar el avance a diario en el IWP (Quick Start). Según el Procedimiento 3.0, lo informa cada día a los Workface Planners, que lo cargan en el software WFP; el contratista puede registrarlo también en su propio sistema.
Con el valor planificado calculado a partir de los planos IFC y de tasas de instalación estándar, las horas codificadas por IWP en las hojas de tiempo y el avance físico registrado por componente, se obtienen datos muy precisos y oportunos que se consolidan en una sola versión de la verdad.
El Procedimiento 3.0 también prevé una reunión diaria de alineación de 15 minutos, en la que cada capataz arma su plan diario a partir del IWP semanal y registra el avance.
""", f"{F.QS} (§7 Progress; §8A Project Controls); {F.P3} (§9 Project Controls y §15 Daily Alignment); {F.P2} (§8 Cost Codes).")

    s = tabla(d, "Módulo 6 · Códigos de demora", "Los códigos de demora explican cada hora perdida",
              ["Código", "Causa de la demora", "Habilitador ausente"],
              [["D01", "Esperando planos o información", "Información"],
               ["D02", "Falta de material en el frente", "Materiales"],
               ["D03", "Andamio o acceso no disponible", "Acceso"],
               ["D04", "Equipo o herramienta no disponible", "Herramientas"],
               ["D05", "Permiso de trabajo pendiente", "Acceso"],
               ["D06", "Trabajo previo de otra cuadrilla incompleto", "Acceso"],
               ["D07", "Clima u otras causas externas", "—"]],
              [1.6, 6.6, 3.9], mono=(0,), tam=13.5, alto_fila=0.5,
              nota="Ejemplo ilustrativo: la tabla original no se conservó. Registre horas enteras de cuadrilla por causa.",
              icono_nota="warning_o")
    notas(s, """
El Procedimiento 2.0 establece que el contratista imprime una matriz de códigos de demora al reverso de las hojas de tiempo. Los capataces registran las desviaciones del plan en la sección de notas de la hoja diaria, en horas enteras que reflejan el tiempo total perdido por la cuadrilla.
Con estos datos se analizan tendencias y se identifica qué habilitador falla (información, herramientas, materiales, acceso), en línea con el principio de los estudios de tool time.
Importante: la tabla de códigos del Procedimiento 3.0 original era una imagen y no se conservó en la conversión a Markdown. Los códigos de esta lámina son un ejemplo construido a partir de la lista estándar de restricciones del curso 2023; defina los suyos en el procedimiento del proyecto.
""", f"{F.P2} (§8 Delay Codes); {F.P3} (Delay Codes, §18); {F.CUR} ('Standard types of constraints'); {F.IDX} §4.1.")

    s = checklist(d, "Módulo 6 · Entregables", "Entregables de la Fase 3: la lista de verificación",
                  "Fase 3 · Construcción y Workface Planning", [
                      ("IWP liberados sin restricciones", "con firmas completas"),
                      ("Pack Track semanal", "estado de cada IWP"),
                      ("Backlog de 2 a 4 semanas", "por disciplina"),
                      ("Look-ahead de 3 semanas", "por número de IWP"),
                      ("Plan diario del capataz", "reunión de 15 minutos"),
                      ("Avance diario por IWP", "valor ganado"),
                      ("Registro de restricciones y demoras", "con sus causas")],
                  nota="Al terminar, el capataz general devuelve el IWP con los registros de calidad al planificador.")
    notas(s, """
Lista de verificación de la Fase 3:
• IWP liberados solo cuando están libres de restricciones, con las firmas de seguridad y calidad.
• Pack Track actualizado cada semana, con un tablero para el informe de gestión.
• Backlog de 2 a 4 semanas por disciplina.
• Look-ahead de tres semanas expresado en números de IWP.
• Plan diario del capataz en la reunión de alineación de 15 minutos.
• Avance diario registrado por IWP y cargado en el software WFP.
• Registro de restricciones y de demoras con sus causas.
Además, el Procedimiento 3.0 incluye estrategia de ejecución de WFP del contratista, capacitación de planificadores, subcontratistas, entrega (turnover), estudios de tool time y auditorías.
""", f"{F.P3} (§7-§19); {F.QS} (§7).")


def m7(d):
    d.pie = "M7 · FASE 4: PUESTA EN MARCHA Y ENTREGA"
    s = separador(d, 7, "Módulo 7 · Fase 4: Puesta en marcha", "Al final se entrega por sistemas, no por áreas",
                  "System Work Packages, Turnover Packages y certificados de listo para comisionar y para operar.", fase=4)
    notas(s, """
Separador del Módulo 7, cuarta fase. En la etapa final el foco pasa del avance de construcción a la preparación de los sistemas para el comisionamiento y el arranque.
Es un tema en evolución: el CII todavía trabaja en la definición de los paquetes de puesta en marcha (RT-364), y la fuente más detallada del repositorio (Omega 365) lo explica ligado a su producto.
""", f"{F.OMG} (Stage 4 – Commissioning & Start-Up); {F.GLO}; {F.IDX} §4.3.")

    s = pares(d, "Módulo 7 · De áreas a sistemas", "La puesta en marcha exige cambiar del CWP al SWP",
              "Hasta ~70 % de avance", "Desde ~70 % de avance", [
                  ("Se mide el avance por área y disciplina", "Se mide la preparación por sistema"),
                  ("CWP e IWP ordenan el trabajo", "El SWP agrupa partes de CWP e IWP por sistema"),
                  ("El POC fija el orden de las áreas", "El POC fija también el orden de los sistemas"),
                  ("Meta: productividad en campo", "Meta: completamiento y arranque")],
              nota="Adelante la vista por sistemas para detectar faltantes antes del arranque.",
              color_izq=AZUL, icono_izq="map_w", icono_der="industry_w")
    notas(s, """
A medida que avanza la construcción, el proyecto pasa de una ejecución por áreas a una preparación por sistemas. Los System Work Packages (SWP) agrupan porciones de CWP e IWP en sistemas funcionales (agua de enfriamiento, compresión de gas, distribución eléctrica) y conectan construcción y comisionamiento: completamiento mecánico, inspección, pruebas y certificación.
Según Omega 365, este cambio de perspectiva se acelera hacia el 70 % de avance físico de la construcción, para identificar temprano los faltantes por sistema y resolverlos antes del arranque.
El curso 2023 advierte sobre una limitación en proyectos industriales: la tubería se diseña por sistema pero se construye por área; hay que entender cómo gestionar esos enfoques en conflicto.
""", f"{F.OMG} (System Work Packages and Turnover Packages); {F.CUR} ('Limitations - System vs Area').")

    s = flujo(d, "Módulo 7 · Sistemas en el POC", "El Path of Construction debe mirar la secuencia de sistemas", [
        ("industry", "Operaciones", "Define las prioridades de arranque"),
        ("route", "POC", "Ordena las áreas pensando en los sistemas"),
        ("clip", "IWP", "Se completan en ese orden"),
        ("layers", "SWP", "Agrupan lo terminado por sistema"),
        ("flag", "TOP", "Sistema listo para entregar")],
        nota="Operaciones y comisionamiento deben participar en los talleres del POC desde FEL 2.",
        colores=[NARANJA_OSC, NARANJA, NARANJA, AZUL_MEDIO, AZUL])
    notas(s, """
Omega 365 define el POC como la secuencia óptima en que se ejecutarán, probarán y entregarán las actividades, sistemas y áreas; por eso en los talleres participan también comisionamiento y operaciones. El representante de Operaciones aporta al POC, apoya la planificación del comisionamiento y acepta los sistemas en el RFOC.
A nivel de ejecución, el POC guía la división de CWP en IWP y su secuencia en el look-ahead; los IWP completados se agregan en SWP y TOP según las secuencias de sistemas definidas por el POC. El POC sostiene tanto la vista macro (CWA/CWP) como la micro (IWP/SWP/TOP).
El curso 2023 recomienda considerar en el cronograma de nivel 3 cómo se superpondrán las actividades de comisionamiento con las de construcción.
""", f"{F.OMG} (Path of Construction; 'PoC and IWPs/SWPs/TOPs'; roles); {F.CUR} ('Pro Tips!' del cronograma de nivel 3).")

    s = proceso(d, "Módulo 7 · Entrega", "El TOP documenta que el sistema está listo para operar", [
        ("clipcheck", "Completamiento mecánico", "Verificación progresiva de lo construido"),
        ("search", "Pruebas (TWP)", "Test Work Package: inspecciones y pruebas previas"),
        ("key", "RFCC", "Ready for Commissioning: listo para comisionar"),
        ("industry", "RFOC", "Ready for Operation: el sistema pasa a Operaciones")],
        nota="Cada certificado se vincula a su SWP; el CII todavía está definiendo el TOP (RT-364).")
    notas(s, """
El Turnover Package (TOP) consolida los alcances de un sistema en circuitos cerrados listos para la entrega, las pruebas y el arranque. El Glosario del CII lo define como un paquete de entrega que alinea los sistemas con la preparación de los TWP, CWP e IWP, e indica que RT-364 trabaja en su definición junto con el comisionamiento y la puesta en marcha.
Test Work Package (TWP): paquete discreto de inspección o prueba que se realiza antes de apoyar el plan de comisionamiento y arranque.
Omega 365 describe la verificación progresiva y el registro de resultados de pruebas, con emisión de certificados RFCC (Ready for Commissioning, listo para comisionar) y RFOC (Ready for Operation, listo para operar) vinculados a sus SWP y activos.
""", f"{F.GLO} (Test Work Package, Turnover Package); {F.OMG} (Features of Omega 365: mechanical completion and commissioning).")

    s = checklist(d, "Módulo 7 · Entregables", "Entregables de la Fase 4: la lista de verificación",
                  "Fase 4 · Puesta en marcha y entrega", [
                      ("SWP definidos", "por sistema funcional"),
                      ("Paquetes de prueba (TWP)", "inspecciones y pruebas"),
                      ("TOP por sistema", "con la documentación de entrega"),
                      ("Certificados RFCC y RFOC", "vinculados a cada SWP"),
                      ("Dossier de calidad", "registros devueltos en los IWP"),
                      ("Lecciones aprendidas", "desempeño de paquetes y restricciones")],
                  nota="La entrega cierra el ciclo: los datos de este proyecto alimentan el siguiente.")
    notas(s, """
Lista de verificación de la Fase 4:
• System Work Packages por sistema funcional.
• Paquetes de prueba (TWP) con inspecciones y pruebas.
• Turnover Packages con la documentación de entrega.
• Certificados RFCC y RFOC.
• Dossier de calidad, armado con los registros que cada IWP devolvió al área de calidad (Procedimiento 3.0, §13).
• Lecciones aprendidas: al terminar el proyecto, revise el desempeño de los paquetes, las tendencias de restricciones, el cumplimiento del cronograma y las causas raíz de los retrasos (Omega 365).
""", f"{F.OMG} (Stage 4; Lessons Learned and Continuous Improvement); {F.P3} (§13 y §17 Turnover); {F.GLO}.")


def m8(d):
    d.pie = "M8 · INFORMACIÓN Y TECNOLOGÍA"
    s = separador(d, 8, "Módulo 8 · Información y tecnología", "Sin datos confiables no hay paquetes confiables",
                  "Modelo 3D, datos de fabricantes, control documental, materiales, andamios y equipos.")
    notas(s, """
Separador del Módulo 8. Information Management (IM) es el segundo de los tres procesos de AWP. Diseña las convenciones de nombres y los procesos de intercambio de datos para que todos los generadores y usuarios de información (Ingeniería, Compras, Materiales, Control Documental, Controles y Construcción) hablen el mismo idioma.
Este módulo cubre el modelo 3D, los datos de fabricantes, el control documental y los sistemas de soporte que se benefician de AWP: materiales, andamios y equipos.
""", f"{F.P2} (§4 Information Management Overview); {F.QS} (§8 Extended Benefits).")

    s = tabla(d, "Módulo 8 · Modelo 3D", "El modelo 3D con atributos es la plataforma de planificación",
              ["Atributo", "Responsable", "Civil", "Acero", "Tuberías", "Cables"],
              [["Tag único", "Ingeniería", "Sí", "Sí", "Sí", "Sí"],
               ["N.º de pieza (piece mark)", "Ingeniería", "—", "Sí", "—", "—"],
               ["N.º de spool", "Workface Planning", "—", "—", "Sí", "—"],
               ["Longitud (cantidad de diseño)", "Ingeniería", "—", "Sí", "Sí", "Sí"],
               ["CWA", "Ingeniería", "Sí", "Sí", "Sí", "Sí"],
               ["EWP", "Ingeniería", "Sí", "Sí", "Sí", "Sí"],
               ["CWP", "Construcción", "Sí", "Sí", "Sí", "Sí"],
               ["IWP", "Workface Planning", "Sí", "Sí", "Sí", "Sí"]],
              [3.6, 2.7, 1.45, 1.45, 1.45, 1.45], destacar={6, 7}, mono=(), tam=12.5,
              alinear_col={2: 2, 3: 2, 4: 2, 5: 2},
              nota="La matriz completa del Procedimiento 2.0 cubre nueve tipos de componente y más de veinte atributos.")
    notas(s, """
La Quick Start Guide explica que la mayoría de los proyectos ya produce un modelo 3D con atributos y datos inteligentes de los fabricantes. Obtenerlos y ponerlos a disposición del equipo de WFP facilita la planificación. El AWP Champion y la gerencia del proyecto impulsan una matriz de atributos que guía a Ingeniería al poblar el modelo, para que Construcción pueda extraer los datos que necesita.
El Procedimiento 2.0 propone la matriz base: atributos obligatorios o secundarios, responsable y fuente, por tipo de componente (civil, pilotes, concreto, acero, equipos, tuberías, equipos eléctricos, cables e instrumentos). La tabla muestra un extracto. Además: tipo de componente, peso, volumen, clase, diámetro, espesor, servicio, aislamiento, ignifugado, traceado, módulo, WBS, tipo de material y código de costo.
El modelo debe estructurarse por CWA, EWP y CWP, las piezas de acero deben tener números únicos y los spools deben identificarse como subconjuntos de los isométricos.
""", f"{F.P2} (§7 Standard Model Attributes); {F.QS} (§3 3D Model and Fabrication); {F.P1} (§7 Information Manager).")

    s = tabla(d, "Módulo 8 · Intercambio de datos", "Los datos de fabricantes se piden en el contrato",
              ["Intercambio", "Formato recomendado"],
              [["Fabricación de tuberías → Construcción", "Archivos PCF/IDF y PDF inteligente"],
               ["Fabricación de acero → Construcción", "Archivos CIS2 y PDF inteligente"],
               ["Ingeniería → Construcción", "Modelo 3D con todos sus atributos"],
               ["Ingeniería → Control documental", "PCF/IDF para planos; PDF inteligente para especificaciones"],
               ["Proveedores de equipos → Materiales", "Base de datos común u hoja de cálculo"],
               ["Construcción → Controles", "Avance exportado desde el software WFP"]],
              [5.4, 6.7], mono=(), tam=13.5,
              nota="Compras incluye en cada contrato la obligación de entregar estos datos junto con el producto.",
              icono_nota="contract_o")
    notas(s, """
El Procedimiento 2.0 de Insight lista los formatos de intercambio recomendados entre actores:
• Materiales a granel: hojas de cálculo. Fabricación de acero y tuberías: modelo 3D, archivos PCF/IDF y PDF inteligentes.
• Ingeniería a control documental: planos en PCF/IDF y PDF inteligentes; especificaciones y hojas de datos en PDF inteligente.
• Fabricación a construcción: acero en CIS2 y PDF inteligente; tuberías en PCF/IDF y PDF inteligente.
• Ingeniería a construcción: modelo 3D con todos sus atributos. Revisiones y as-built: PCF/IDF y modelo 3D actualizados.
• Construcción a controles: avance en hoja de cálculo (desde el software WFP) y costos a partir de las hojas de tiempo.
Para lograrlo, Compras debe establecer obligaciones contractuales para que proveedores y fabricantes entreguen datos completos junto con sus productos (Procedimiento 2.0, §10). Siempre que sea posible, los datos deben cumplir la norma ISO 15926.
""", f"{F.P2} (§4 y §10); {F.P1} (§16 Information Management).")

    s = flujo(d, "Módulo 8 · Control documental", "Un solo repositorio documental elimina el desfase de revisiones", [
        ("ruler", "Ingeniería", "Carga planos y revisiones"),
        ("cloud", "Repositorio en la nube", "Documentos ordenados por WBS, con permisos"),
        ("cube", "Modelo 3D", "Enlaza cada objeto con su plano vigente"),
        ("helmet", "Construcción", "Consulta e imprime su IWP")],
        nota="Sin desfase entre la emisión de una revisión y su llegada a campo, y con menos personal documental en obra.",
        colores=[AZUL, AZUL_MEDIO, AZUL_MEDIO, NARANJA])
    notas(s, """
La Quick Start Guide describe el modelo ideal de control documental: un único repositorio electrónico al que todos los actores acceden según sus permisos. Ingeniería carga los documentos y los contratistas de construcción los descargan. Es también la mejor forma de enlazar el modelo 3D de planificación con la revisión vigente de cada plano.
Resultado: la revisión se gestiona sin desfase entre la emisión de Ingeniería y la recepción del contratista, y se reduce mucho el personal necesario para gestionar documentos en obra.
El Procedimiento 3.0 añade que el software WFP enlaza el modelo 3D con la base documental en la nube: los planificadores acceden a los documentos seleccionando objetos en el modelo, y los contratistas tienen acceso de lectura para revisar el look-ahead e imprimir sus IWP.
""", f"{F.QS} (§8C Document Control); {F.P3} (§10 Document Control); {F.P2} (§9).")

    s = proceso(d, "Módulo 8 · Materiales", "Los materiales se agrupan por IWP hasta 8 semanas antes", [
        ("listcheck", "Lista por IWP", "El planificador envía la lista de materiales del paquete",
         [("Anticipación", "−8 sem", NARANJA)]),
        ("warehouse", "Agrupar al recibir", "El almacén separa las entregas por paquete",
         [("Al recibir", "continuo", AZUL)]),
        ("barcode", "Separar y etiquetar", "Material del IWP listo al entrar al look-ahead",
         [("Look-ahead", "−2 sem", NARANJA)]),
        ("truck", "Pedir al frente", "El capataz general lo solicita una semana antes",
         [("Pedido", "−1 sem", NARANJA)])],
        nota="Con una base de datos de materiales, el IWP se carga como una reserva y el material se asigna al recibirse.")
    notas(s, """
Según la Quick Start Guide, en un sistema de Workface Planning plenamente funcional los planificadores envían la lista de materiales de cada IWP al equipo de gestión de materiales hasta 8 semanas antes de la fecha programada. Así, el equipo puede agrupar las entregas por IWP a medida que se reciben. Si se usa una base de datos de materiales, los IWP pueden cargarse como reservas.
El Pack Track incluye el hito "separar y etiquetar el material" (bag and tag) al entrar al look-ahead, y el Procedimiento 3.0 establece que el superintendente o el capataz general piden el material de cada IWP una semana antes de su ejecución.
El Procedimiento 1.0 asigna a la gestión de materiales en obra seguir y reportar los materiales requeridos, pedidos y recibidos por IWP.
""", f"{F.QS} (§8B Material Management; §7 Execution); {F.P3} (§7 Pack Track); {F.P1} (§5).")

    s = proceso(d, "Módulo 8 · Andamios y equipos",
                "Andamios y equipos se piden desde el IWP con 2 semanas de anticipación", [
                    ("clip", "El IWP detecta la necesidad", "Andamios, grúas, elevadores y soldadoras"),
                    ("file", "Solicitud electrónica", "El planificador la envía al responsable de andamios o de equipos"),
                    ("calendar", "Programación", "Montaje y asignación con al menos 2 semanas"),
                    ("check", "ID en el IWP", "El número de solicitud vuelve al paquete")],
                nota="Además de reducir esperas, baja el costo total de andamios y equipos.")
    notas(s, """
Andamios (Quick Start, §8D): el objetivo principal es minimizar las demoras de las cuadrillas, pero planificar los andamios con anticipación también reduce su costo total. Al desarrollar cada IWP, el planificador genera la solicitud de los andamios que requiere el alcance; normalmente llega al grupo de andamios al menos dos semanas antes de la ejecución. Así se programa el montaje, se siguen los componentes y se registra la mano de obra.
El Procedimiento 3.0 detalla que la solicitud es electrónica: el planificador de andamios la registra en su base de datos, le asigna un número y lo devuelve para insertarlo en el IWP.
Equipos de construcción (Quick Start, §8E): grúas, elevadores y soldadoras se gestionan de forma similar. Identificar las necesidades con dos semanas de anticipación asegura suficientes equipos y ayuda a programar su uso.
""", f"{F.QS} (§8D Scaffold Management y §8E Construction Equipment); {F.P3} (§7 Scaffold Request).")

    s = cita(d, "Módulo 8 · Tecnología", "Primero las personas y el proceso; después la tecnología",
             "“Antes de pensar en tecnología, hay que tener bien el proceso. Trátelo como bloques de construcción: "
             "el proceso es la base.”", "CURSO AWP 2023 · LECCIÓN APRENDIDA 7 (ADAPTACIÓN)",
             puntos=[("users", "Personas: roles claros y capacitación"),
                     ("gears", "Proceso: procedimientos y flujos probados"),
                     ("laptop", "Tecnología: acelera lo que ya funciona")])
    notas(s, """
Lección 7 del curso 2023: hay mucha tecnología útil para implementar AWP, especialmente para WFP en obra, pero antes de pensar en tecnología hay que tener el proceso correcto. Trátelo como bloques de construcción: el proceso es la base.
Omega 365 coincide: la tecnología facilita AWP al ofrecer una vista única y consistente del proyecto (hilo digital o digital thread, visualización 3D/BIM y planificación 4D, tableros de KPI), pero su propósito es simplificar la ejecución, no añadir complejidad. La integración entre sistemas sigue siendo un desafío: defina temprano la propiedad de los datos, los mecanismos de transferencia y los responsables de actualizarlos.
El Framework responde a la objeción "no tengo la tecnología": los sistemas integrados permiten hacer más con menos personal, pero no son un requisito para empezar.
""", f"{F.CUR} (AWP Related Lessons Learned, lección 7); {F.OMG} (Digital Enablement of AWP); {F.FW} (objeción 'I don't have the technology').")
