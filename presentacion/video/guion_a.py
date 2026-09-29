"""Guion de narración del video: láminas 1 a 60 (español latinoamericano).

Se escribe con la ortografía normal; la pronunciación de siglas y términos en inglés
la resuelve pronunciacion.py antes de sintetizar la voz.
"""

GUION_A = {
    1: "Bienvenidos. En este video vamos a ver cómo implementar Advanced Work Packaging, o AWP, en un proyecto real. "
       "La idea central es simple: construir el proyecto en el orden en que se va a construir. "
       "Primero se decide cómo se armará la planta, y después Ingeniería y Compras entregan su trabajo en ese mismo orden.",
    2: "El recorrido tiene trece módulos. Empezamos por el porqué y el qué de AWP, y por cómo preparar la organización. "
       "Luego seguimos las cuatro fases del proyecto: planificación preliminar, ingeniería y compras, construcción y puesta en marcha. "
       "Cerramos con información, roles, medición, escalabilidad, errores comunes y una hoja de ruta.",
    3: "Al terminar, su equipo sabrá qué hacer, quién lo hace y cuándo. "
       "Entenderá la jerarquía de paquetes, conocerá los entregables de cada fase, sabrá asignar los roles nuevos "
       "y podrá evitar los errores más frecuentes. AWP es un cambio de sistema: involucra a todo el proyecto, no solo a Construcción.",
    4: "Las cifras de esta guía vienen de tres fuentes principales. "
       "El Construction Industry Institute, o CII, aporta los estudios y la definición oficial. "
       "La COAA, de Canadá, aporta las buenas prácticas y el modelo escalable. "
       "E Insight AWP aporta la guía de inicio rápido y los procedimientos. Cuando las fuentes no coinciden, lo vamos a señalar.",
    5: "Módulo uno. Por qué AWP. El problema no es la cuadrilla, es la planificación.",
    6: "Empecemos por los datos. El sesenta y cinco por ciento de los megaproyectos fracasa en costo, plazo o desempeño. "
       "Y el setenta por ciento de los proyectos de construcción termina sobre presupuesto y con retraso. "
       "Es un problema del sistema, no de una empresa en particular.",
    7: "La productividad de la construcción no ha mejorado en setenta años, mientras otras industrias sí avanzaron. "
       "Como la mano de obra es una de las partidas más grandes del presupuesto, "
       "cualquier mejora en su productividad cambia el resultado del proyecto.",
    8: "De una jornada de diez horas, solo tres coma siete se usan realmente trabajando con herramientas. "
       "El resto se pierde esperando planos, buscando materiales, esperando andamios o trasladándose. "
       "Con AWP, ese tiempo productivo sube a cuatro coma seis horas.",
    9: "Los retrasos que vemos en campo nacen en la oficina. "
       "Si Ingeniería emite planos en su propio orden, la cuadrilla espera información. "
       "Si Compras no sigue la secuencia de construcción, faltan materiales en el frente. "
       "Workface Planning ataca el síntoma en campo; AWP ataca la causa en la oficina.",
    10: "Un trabajador ejecuta cuando tiene cinco cosas: información, herramientas, materiales, acceso y voluntad. "
        "Las cuatro primeras las tiene que asegurar la gerencia. "
        "La voluntad crece sola cuando las otras cuatro están resueltas.",
    11: "Workface Planning, o WFP, fue el primer paso: organizar el trabajo de cada cuadrilla en campo. "
        "Pero solo no basta, porque llega tarde. Si la ingeniería y las compras no llegaron en orden, "
        "el planificador solo administra la escasez. AWP adelanta la planificación a las fases de definición del proyecto.",
    12: "¿Y cuál es el resultado? Según los estudios del CII, con AWP la productividad en campo sube un veinticinco por ciento "
        "y el costo total instalado baja un diez por ciento. "
        "También mejoran el cumplimiento del cronograma, la seguridad y la calidad.",
    13: "Módulo dos. Qué es AWP. Y lo primero que hay que aclarar: AWP es un proceso, no un software.",
    14: "El CII define AWP como el flujo general de todos los paquetes de trabajo detallados: de construcción, de ingeniería y de instalación. "
        "Es un proceso planificado y ejecutable, que va desde la planificación inicial hasta la construcción, "
        "y siempre está dirigido por Construcción.",
    15: "AWP integra tres procesos. Advanced Work Packaging alinea los paquetes de ingeniería, compras y construcción. "
        "Information Management estandariza los datos, el modelo tres D y la nomenclatura. "
        "Y Workface Planning lleva el plan a cada cuadrilla. Los tres se implementan juntos.",
    16: "Todo se ordena en una jerarquía. Arriba está la CWA, el área de construcción. "
        "Cada área se divide en CWP, un paquete por disciplina. Cada CWP recibe su ingeniería en un EWP y sus materiales en un PWP. "
        "Y cada CWP se divide en varios IWP: el paquete que recibe el capataz cada semana.",
    17: "La Construction Work Area, o CWA, es la primera división del terreno. "
        "Es una parte lógica del plano de implantación, incluye todas las disciplinas "
        "y funciona como contenedor de los paquetes de construcción. En el cronograma es una actividad de nivel dos.",
    18: "Un Construction Work Package, o CWP, es una sola disciplina dentro de una CWA. Por ejemplo, las tuberías del área dos. "
        "Tiene menos de cuarenta mil horas hombre, es una actividad de nivel tres y, como los CWP no se superponen, "
        "sirven como alcance para licitar.",
    19: "Un Engineering Work Package, o EWP, entrega toda la ingeniería que necesita un CWP: "
        "alcance, planos aprobados para construcción, especificaciones, lista de materiales y vistas del modelo. "
        "Un tamaño típico va de cinco mil a veinte mil horas hombre de campo.",
    20: "Un Procurement Work Package, o PWP, asegura los materiales y equipos de un CWP. "
        "Más que una caja física, es un identificador que alinea las compras con la secuencia de construcción. "
        "El CII todavía está terminando de definirlo.",
    21: "Un Installation Work Package, o IWP, es el trabajo de una cuadrilla en una semana. "
        "Lo ejecuta un capataz con unos diez trabajadores, está formado por planos completos "
        "y solo se entrega a campo cuando está libre de restricciones.",
    22: "La regla base es: un EWP, igual a un PWP, igual a un CWP. "
        "Alinear los tres paquetes simplifica el seguimiento. "
        "Hay excepciones razonables, como los materiales a granel o un CWP que depende de varias disciplinas de ingeniería.",
    23: "Para la puesta en marcha, la lógica cambia: ya no se empaqueta por áreas, sino por sistemas. "
        "Ahí aparecen el System Work Package y el Turnover Package. "
        "Este cambio de enfoque se acelera cerca del setenta por ciento de avance físico.",
    24: "Un aviso importante: las fuentes no coinciden en algunos números, como el nivel del IWP, su duración o el tamaño del backlog. "
        "No es grave, pero cada proyecto debe fijar sus propios valores en el procedimiento y aplicarlos de forma consistente.",
    25: "Módulo tres. Preparar la organización. Porque AWP empieza antes del primer plano.",
    26: "Para arrancar bastan siete componentes: un AWP Champion, procedimientos escritos, un modelo tres D con datos de fabricantes, "
        "un software de Workface Planning, planificadores dedicados, un formato de IWP "
        "y un proceso para eliminar restricciones.",
    27: "El primer nombramiento es el AWP Champion, y debe ser a tiempo completo. "
        "Representa al propietario, coordina a todos los actores con imparcialidad y actúa como coach del proyecto. "
        "No asuman que este rol lo puede cubrir el gerente del proyecto en sus ratos libres.",
    28: "Los procedimientos fijan quién, qué, cuándo, cómo y por qué. "
        "Por sí solos no cambian la cultura, pero crean la obligación de cumplir y permiten auditar el proceso.",
    29: "Los procedimientos cubren tres áreas. El de AWP define contratos, secuencia y controles. "
        "El de Information Management define la estructura de desglose, la nomenclatura y el modelo. "
        "Y el de Workface Planning define planificadores, paquetes, restricciones y reportes.",
    30: "AWP se exige en el contrato, o no ocurre. El procedimiento va con la licitación, el postor se compromete a cumplirlo, "
        "el cronograma se desglosa hasta los niveles tres y cinco, y los planificadores son aprobados por el propietario.",
    31: "Al elegir contratistas, evalúen su capacidad en AWP en una conversación, no solo en un papel. "
        "Muchos dicen ser expertos. Un contratista novato dispuesto a aprender suele ser mejor socio "
        "que un experto que no practica lo que escribe.",
    32: "Elijan el software de Workface Planning antes de la ingeniería básica, o FEED, "
        "y según lo que ya usan para el modelo tres D, los materiales y el control documental. "
        "Recuerden: primero las personas y el proceso; el software acelera, no reemplaza.",
    33: "La estructura de desglose del trabajo, o WBS, y una nomenclatura común son el idioma del proyecto. "
        "Un mismo código identifica la planta, el área, la disciplina, el paquete y el IWP, "
        "y conecta el cronograma, los costos, el modelo y los planos.",
    34: "Arranquen con un seminario de lanzamiento dentro de los treinta días de adjudicado el contrato. "
        "En la mañana, capacitación; en la tarde, lecciones aprendidas de otros proyectos. "
        "Y formen un comité con todos los actores que se reúna cada mes.",
    35: "Módulo cuatro. Fase uno, planificación preliminar. En FEL dos se decide cómo se construirá la planta.",
    36: "AWP se implementa en cuatro etapas ligadas a las compuertas del proyecto: "
        "planificación preliminar en FEL dos, ingeniería y compras en FEL tres, construcción, y comisionamiento y arranque. "
        "FEL significa Front End Loading: las etapas de definición antes de decidir la inversión.",
    37: "Cada etapa tiene una compuerta y un entregable de AWP. "
        "En FEL dos se entregan el plan AWP, las áreas y el primer Path of Construction. "
        "En FEL tres, ese Path of Construction se firma antes de iniciar la ingeniería de detalle.",
    38: "Dividan el terreno en áreas de construcción antes de diseñar. "
        "Los criterios son prioridad, contratación, racks de tuberías, horas de campo similares, función y proceso. "
        "Esta discusión la lidera Construcción, y el resultado es un plano marcado que se comparte con todos.",
    39: "El Path of Construction, o POC, responde una pregunta clave: ¿cómo y en qué orden se construye? "
        "¿De norte a sur? ¿Qué va primero? ¿Con qué accesos, grúas y zonas de acopio? "
        "La respuesta se dibuja sobre el plano como una secuencia de áreas.",
    40: "El POC tiene componentes definidos: un plano marcado, una matriz de paquetes por disciplina y área, "
        "un informe con objetivos, prioridades y restricciones, y una simulación para validar la secuencia con todos los actores.",
    41: "Construcción lidera el POC, e Ingeniería y Compras lo validan. "
        "El Construction Manager es su dueño. Ingeniería expone sus límites técnicos como restricciones, "
        "Compras aporta los plazos de los equipos críticos, y el contratista participa o lo revisa en la licitación.",
    42: "El POC se construye en tres pasos. Primero, un POC sin restricciones, solo con Construcción. "
        "Luego, un taller interactivo donde Ingeniería y Compras presentan sus plazos y limitaciones. "
        "Y finalmente, un POC firmado que sirve de base para el cronograma de nivel tres.",
    43: "Del taller sale el plan de liberación. Por cada disciplina se ordenan el EWP, el PWP y el CWP en serie, uno tras otro. "
        "Ingeniería y Compras calculan hacia atrás, desde la fecha en que Construcción necesita iniciar cada paquete.",
    44: "El POC se define en FEL dos y se congela al final de FEL tres. "
        "Congelarlo a tiempo le da a Ingeniería la mejor oportunidad de cumplir el plan. "
        "Después se puede actualizar, pero con gestión formal del cambio.",
    45: "El cronograma se escalona en siete niveles, del año a la hora. "
        "Las áreas van en el nivel dos, los CWP en el nivel tres y los IWP en el nivel cinco. "
        "El planificador divide cada CWP en IWP y le entrega esa secuencia al programador.",
    46: "Los entregables de la fase uno son: el plan AWP, el plano con las áreas, el Path of Construction, "
        "la matriz de paquetes, el plan de liberación preliminar, los procedimientos aprobados y una estrategia de contratación con cláusulas AWP.",
    47: "Módulo cinco. Fase dos, ingeniería y compras. La ingeniería se entrega en el orden en que se construye.",
    48: "Aclaremos un temor frecuente. AWP no le agrega trabajo a Ingeniería: le cambia el orden. "
        "Se puede seguir diseñando por sistemas. Lo que cambia es cómo se entregan los paquetes y qué prioridad guía la secuencia.",
    49: "Comparemos. En el enfoque tradicional, Ingeniería avanza según su propia lógica y el campo trabaja donde hay información. "
        "Con AWP, el Path of Construction fija el orden, los EWP se entregan en esa secuencia "
        "y cada paquete llega completo a campo.",
    50: "Gestionar la ingeniería por área convierte cada área en un miniproyecto. "
        "Los entregables son más pequeños y el seguimiento es más fino, "
        "así que los atrasos se detectan semanas antes y se sabe exactamente qué área se está atrasando.",
    51: "Cada EWP tiene su propio flujo: se define el marco, se capacita al equipo, se diseña y revisa, "
        "el propietario y el contratista lo revisan, y finalmente se libera. "
        "Esa liberación es el hito que da inicio al paquete de construcción.",
    52: "El avance de Ingeniería se mide con reglas de crédito por EWP. "
        "Fíjense que la mitad del crédito se gana solo cuando el paquete se emite aprobado para construcción y sin retenciones. "
        "Así se premia entregar paquetes completos, no planos sueltos.",
    53: "Los EWP los prepara el contratista de Ingeniería, sea cual sea el tipo de contrato. "
        "Los lidera el gerente de Ingeniería, los revisan el propietario y el contratista de construcción, "
        "y su liberación queda como hito en el cronograma.",
    54: "Compras también cambia. En lugar de ordenar por fecha de requisición, se secuencia por paquete de construcción. "
        "Se define desde el inicio quién suministra qué, la fecha en que cada material se necesita en obra, "
        "y se mantiene la trazabilidad completa.",
    55: "El Procurement Work Number conecta cada compra con su paquete. "
        "El mismo código acompaña al material desde el EWP, pasando por la lista de materiales, el pedido y el envío, "
        "hasta la recepción en obra.",
    56: "El CWP se arma cuando se libera su EWP. "
        "Construcción revisa la ingeniería, redacta el paquete con su alcance, límites, seguridad y calidad, "
        "el propietario lo revisa, y el CWP se libera como base del alcance para los contratistas.",
    57: "¿Quién redacta los CWP? Construcción define su tamaño, contenido y secuencia, "
        "pero quién los escribe depende del modelo de contrato. En proyectos pequeños, incluso puede hacerlo Ingeniería. "
        "Lo importante es definirlo antes de licitar.",
    58: "Los entregables de la fase dos son: EWP emitidos en secuencia, PWP con fechas requeridas en obra, "
        "CWP liberados, el modelo tres D con atributos, el estimado por área y disciplina, "
        "el cronograma de nivel tres y los planes de liberación al día.",
    59: "Módulo seis. Fase tres, construcción. En campo, cada capataz recibe un paquete listo para ejecutar.",
    60: "Esta es la meta de todo AWP: que cada lunes, cada capataz reciba un IWP listo. "
        "Con el alcance claro, los materiales y herramientas disponibles, el trabajo previo terminado y el andamio armado.",
}
