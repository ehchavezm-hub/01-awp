"""Guion de narración del video: láminas 61 a 122 (español latinoamericano)."""

GUION_B = {
    61: "Workface Planning es un ciclo de cuatro pasos: definir, crear, ejecutar y seguir los IWP. "
        "El Workface Planner además verifica el alcance de cada CWP, gestiona las restricciones y el backlog, "
        "y prepara los paquetes para la entrega por sistemas.",
    62: "El IWP contiene todo lo que el capataz necesita: una portada con el valor planificado, los contactos de emergencia, "
        "la lista de restricciones, el alcance, los requisitos de seguridad y calidad, los planos justos y la lista de materiales verificada.",
    63: "Del CWP al IWP hay cuatro pasos, unos noventa días antes de ejecutar. "
        "Se elige el CWP, el superintendente explica cómo dividir y ordenar el trabajo, "
        "el planificador arma los IWP en el modelo tres D, y el superintendente los aprueba.",
    64: "¿Qué tamaño debe tener un IWP? Empiecen con unas quinientas horas y ajusten según la experiencia. "
        "Los paquetes pequeños son más fáciles de seguir para el capataz. "
        "La referencia es un capataz, unos diez trabajadores y una ventana de siete días.",
    65: "La regla de oro es clara: ningún IWP va a campo con restricciones. "
        "Las críticas son los documentos, los materiales y los andamios. "
        "Cada restricción se libera con una firma en la página de restricciones del paquete.",
    66: "Las restricciones se liberan en cuatro pasos: el IWP se inicia, las restricciones se identifican, se asignan y se liberan. "
        "En una parada de planta el ciclo dura unas seis semanas; en un megaproyecto, unas doce.",
    67: "Cada restricción tiene dueño, fecha y prioridad. Las buenas prácticas son: una lista única, "
        "un flujo formal de aprobación, una reunión estándar, un árbol de decisión para los paquetes que siguen abiertos "
        "y un reporte de estado para toda la gerencia.",
    68: "El backlog es el conjunto de IWP libres de restricciones, listos para elegir. "
        "Los paquetes avanzan como en un embudo, desde la ventana de noventa días hasta el campo. "
        "La meta es tener entre dos y cuatro semanas de trabajo listo por disciplina.",
    69: "El look ahead de tres semanas se alimenta solo del backlog. "
        "Cada semana, el superintendente elige paquetes libres y los carga en el cronograma de nivel cinco. "
        "Si una disciplina se queda sin IWP disponibles, es una alerta temprana.",
    70: "El Pack Track es una sola hoja que muestra el estado de todos los IWP: "
        "cuándo se crearon, cuándo llegaron sus planos y materiales, cuándo entraron al backlog y cuándo se emitieron a campo. "
        "Con ella se arma un tablero semanal para la gerencia.",
    71: "Cada IWP tiene fecha de caducidad. Si no se termina en su ventana, puede tener una prórroga corta de uno o dos días. "
        "Si aun así no se completa, vuelve al planificador y el alcance pendiente pasa a un nuevo paquete.",
    72: "El capataz registra el avance cada día en su IWP. El planificador lo carga en el software, "
        "Controles lo compara con el valor planificado y la gerencia obtiene una sola versión de la verdad. "
        "Además, las horas se cargan usando el número de IWP como código de costo.",
    73: "Los códigos de demora explican cada hora perdida: esperar planos, falta de material, andamio no disponible, "
        "equipo ausente o un permiso pendiente. Esta tabla es un ejemplo; cada proyecto define la suya.",
    74: "Los entregables de la fase tres son: IWP liberados sin restricciones, el Pack Track semanal, "
        "un backlog de dos a cuatro semanas, el look ahead de tres semanas, el plan diario del capataz, "
        "el avance diario y el registro de restricciones y demoras.",
    75: "Módulo siete. Fase cuatro, puesta en marcha. Al final se entrega por sistemas, no por áreas.",
    76: "Cerca del setenta por ciento de avance, el enfoque cambia. "
        "Antes se medía el avance por área; ahora se mide la preparación por sistema. "
        "El System Work Package agrupa partes de varios paquetes que pertenecen al mismo sistema funcional.",
    77: "Por eso el Path of Construction también debe mirar la secuencia de sistemas. "
        "Operaciones define las prioridades de arranque, el POC ordena las áreas pensando en esos sistemas, "
        "y los paquetes terminados se agrupan hasta formar el Turnover Package.",
    78: "El Turnover Package documenta que el sistema está listo. "
        "Primero se verifica el completamiento mecánico, luego se hacen las pruebas, "
        "después se certifica que está listo para comisionar y, por último, que está listo para operar.",
    79: "Los entregables de la fase cuatro son: paquetes por sistema, paquetes de prueba, Turnover Packages, "
        "certificados de listo para comisionar y para operar, el dossier de calidad y las lecciones aprendidas.",
    80: "Módulo ocho. Información y tecnología. Sin datos confiables no hay paquetes confiables.",
    81: "El modelo tres D con atributos es la plataforma de planificación. "
        "Cada componente lleva datos como su código, su área, su EWP, su CWP y su IWP. "
        "Una matriz de atributos le dice a Ingeniería qué información debe cargar para que Construcción la pueda usar.",
    82: "Los datos de los fabricantes se piden en el contrato. "
        "Cada intercambio tiene un formato recomendado, por ejemplo archivos de tuberías y de acero que el software puede leer. "
        "Si no se exige en la compra, no llega.",
    83: "Un solo repositorio documental elimina el desfase de revisiones. "
        "Ingeniería carga los planos, el repositorio los ordena por código, el modelo enlaza cada objeto con su plano vigente "
        "y Construcción consulta e imprime su IWP.",
    84: "Los materiales se agrupan por IWP hasta ocho semanas antes. "
        "El planificador envía la lista, el almacén separa las entregas por paquete, "
        "el material se etiqueta al entrar al look ahead y se pide al frente una semana antes.",
    85: "Andamios y equipos se piden desde el IWP con al menos dos semanas de anticipación. "
        "Así se reducen las esperas en campo y también baja el costo total de andamios y grúas.",
    86: "Una lección clave: primero las personas y el proceso; después la tecnología. "
        "La tecnología acelera lo que ya funciona, pero no arregla un proceso que no está definido.",
    87: "Módulo nueve. Roles y organización. AWP redistribuye responsabilidades, no solo agrega cargos.",
    88: "Cada actor tiene un papel. El propietario respalda. El EPC lidera el plan y mantiene el POC. "
        "Ingeniería entrega los EWP, Compras los PWP y Construcción ejecuta los IWP. "
        "Y el AWP Champion, de forma transversal, integra y capacita.",
    89: "El AWP Champion guía; no ejecuta por los demás. "
        "Lidera la adopción, coordina con el propietario y los subcontratistas, acompaña al equipo "
        "y supervisa Workface Planning en obra. Nunca lo dejen solo.",
    90: "El Workface Planner es alguien de oficio con experiencia, no un oficinista. "
        "Conoce el trabajo, ha supervisado en campo, maneja el software básico, reporta al superintendente "
        "y se dedica solo a planificar.",
    91: "La proporción de referencia es un planificador por cada cincuenta trabajadores. "
        "Se ajusta por complejidad: la instrumentación exige más planificación que el concreto o el movimiento de tierras.",
    92: "El Construction Manager es el dueño de AWP en la obra. "
        "Explica por qué se usa, lidera el Path of Construction y la constructabilidad, revisa los entregables "
        "y sigue el impacto de las restricciones. Si él no cree en AWP, la implementación será un trámite.",
    93: "La supervisión de campo también cambia su rutina. "
        "El superintendente elige paquetes del backlog, el capataz general pide el material una semana antes "
        "y el capataz revisa su IWP, arma su plan diario y registra el avance.",
    94: "Los ratios de supervisión difieren entre fuentes: un capataz general puede tener cuatro o cinco capataces, "
        "y un superintendente, tres o cuatro capataces generales. Definan los suyos según la complejidad del trabajo.",
    95: "Esta matriz de responsabilidades es una propuesta para empezar. "
        "Indica quién es responsable, quién aprueba, a quién se consulta y a quién se informa en cada entregable. "
        "Ajústenla a su modelo de contrato.",
    96: "Módulo diez. Medición. Lo que no se mide en paquetes no se mejora.",
    97: "Hay dos familias de indicadores. Los de Ingeniería siguen la lista de entregables, las reglas de crédito y los planes de liberación. "
        "Los de Construcción siguen los IWP listos, el cierre de restricciones y el cumplimiento del plan.",
    98: "En Ingeniería, comparen siempre las fechas planificadas con las reales. "
        "En este ejemplo, siete días de atraso en un EWP se convierten en catorce días de atraso en su CWP. "
        "El plan de liberación es un indicador adelantado de los problemas en campo.",
    99: "En campo, midan seis cosas: IWP listos frente al total, cierre de restricciones, días de backlog, "
        "IWP completados a tiempo, porcentaje del plan cumplido y productividad por disciplina.",
    100: "El valor planificado se calcula por IWP. Los paquetes se preparan no antes de tres meses de ejecutarse, "
         "las cantidades se multiplican por tasas estándar, las horas se cargan por IWP y el capataz registra el avance físico. "
         "Cantidad por tasa da horas; horas entre dotación da duración.",
    101: "El indicador más directo es el tiempo en herramientas. Pasa del treinta y siete al cuarenta y seis por ciento con AWP, "
         "de tres coma siete a cuatro coma seis horas por jornada. "
         "Mídanlo con estudios independientes cada dos o tres meses.",
    102: "Auditen el proceso AWP, no solo el cronograma. "
         "Hagan revisiones independientes, auditorías periódicas con una plantilla, un informe semanal desde el Pack Track "
         "y un comité mensual que resuelva los problemas entre actores.",
    103: "Módulo once. Escalar y adoptar. AWP se ajusta al tamaño del proyecto.",
    104: "AWP también sirve para proyectos de menos de cien millones de dólares. "
         "En dos mil diecinueve, la COAA diseñó un modelo de AWP escalable, desarrollado por cuarenta profesionales de la industria, "
         "que no renuncia a los principios.",
    105: "Dos factores definen cuánto AWP necesita un proyecto: qué tan familiar es para la empresa y qué tan complejo es. "
         "Con ellos se forman cuatro categorías, de la A a la D, y una herramienta de preguntas ubica al proyecto en su categoría.",
    106: "En una parada de planta el ciclo es el mismo, pero más corto: "
         "el IWP se inicia seis semanas antes y las restricciones se liberan dos semanas antes. "
         "En un megaproyecto, esos plazos son de doce y cuatro semanas. Cambia el horizonte, no los pasos.",
    107: "AWP y Lean Construction se complementan. "
         "AWP usa planificadores dedicados y un proceso formal de restricciones. "
         "Lean se apoya en el último planificador y en compromisos confiables. Muchas empresas combinan ambos.",
    108: "Un informe conjunto del CII y del Lean Construction Institute compara ambos enfoques en once temas. "
         "Coinciden en seguridad y calidad; difieren en quién planifica, cómo se mide el avance y cómo se organiza el equipo.",
    109: "Y hay doce objeciones frecuentes, todas con respuesta. "
         "Por ejemplo: mi proyecto es muy pequeño; existe el modelo escalable. "
         "O: es un contrato a suma alzada; entonces AWP aumenta su margen.",
    110: "La objeción más peligrosa es: ya hacemos AWP. "
         "Para comprobarlo, hagan tres preguntas: ¿hay un POC firmado? ¿Cuántos días de backlog tiene cada disciplina? "
         "¿Dónde está el Pack Track de esta semana?",
    111: "Módulo doce. Errores y lecciones. Otros ya cometieron estos errores; aprovechemos su experiencia.",
    112: "Primera lección: AWP es un camino. No va a salir perfecto la primera vez. "
         "Registren lo que no funcionó, celebren las mejoras y ajusten el procedimiento en cada proyecto.",
    113: "Segunda lección: gatear, caminar, correr. "
         "Empiecen con paquetes más precisos y un piloto, luego apliquen Workface Planning en toda la obra, "
         "y finalmente implementen AWP de principio a fin.",
    114: "Esperen resistencia, y respóndanla con un lenguaje común. "
         "Reconozcan lo que la gente ya hace bien, capaciten de forma constante y usen el vocabulario de AWP en reuniones y documentos.",
    115: "Un contratista novato con ganas de aprender vale más que un experto de papel. "
         "El experto de papel envía procedimientos impecables, pero no los aplica. "
         "El novato reconoce lo que no sabe y mejora semana a semana.",
    116: "Estos son los siete errores más caros: un Champion a medio tiempo, un POC tardío, IWP con restricciones abiertas, "
         "movilizar sin backlog, comprar software antes de definir el proceso, no incluir AWP en el contrato y no medir.",
    117: "Hagan este diagnóstico rápido con su equipo. Son siete preguntas de sí o no. "
         "Cada respuesta negativa se convierte en una prioridad para los próximos noventa días.",
    118: "Finalmente, registren y reutilicen las lecciones de cada proyecto: midan, analicen, registren y reutilicen. "
         "Así, cada nuevo proyecto empieza con una base más madura.",
    119: "Módulo trece. Hoja de ruta. Empiecen el lunes con tres acciones.",
    120: "Esta es una hoja de ruta de noventa días. En el primer mes, nombren al Champion y capaciten al equipo. "
         "En el segundo, escriban los procedimientos y las cláusulas de contrato. "
         "Y en el tercero, hagan un piloto con un paquete real.",
    121: "En resumen: cuatro fases y un solo hilo conductor. "
         "Construcción define el orden, Ingeniería y Compras lo siguen, "
         "el campo ejecuta sin restricciones y Operaciones recibe por sistemas.",
    122: "Construyan en el orden correcto y la productividad llegará. "
         "El siguiente paso es concreto: nombrar al AWP Champion del proyecto. "
         "Gracias por acompañarnos.",
}
