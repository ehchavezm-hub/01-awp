# Guion de narración: Implementar AWP

Narración en español latinoamericano de las 122 láminas del video `implementacion_awp.mp4`.
Para cambiar lo que dice la voz, edite `guion_a.py` (láminas 1–60) o `guion_b.py` (61–122) y regenere el video.

## Apertura

**Lámina 1.** Bienvenidos. En este video vamos a ver cómo implementar Advanced Work Packaging, o AWP, en un proyecto real. La idea central es simple: construir el proyecto en el orden en que se va a construir. Primero se decide cómo se armará la planta, y después Ingeniería y Compras entregan su trabajo en ese mismo orden.

**Lámina 2.** El recorrido tiene trece módulos. Empezamos por el porqué y el qué de AWP, y por cómo preparar la organización. Luego seguimos las cuatro fases del proyecto: planificación preliminar, ingeniería y compras, construcción y puesta en marcha. Cerramos con información, roles, medición, escalabilidad, errores comunes y una hoja de ruta.

**Lámina 3.** Al terminar, su equipo sabrá qué hacer, quién lo hace y cuándo. Entenderá la jerarquía de paquetes, conocerá los entregables de cada fase, sabrá asignar los roles nuevos y podrá evitar los errores más frecuentes. AWP es un cambio de sistema: involucra a todo el proyecto, no solo a Construcción.

**Lámina 4.** Las cifras de esta guía vienen de tres fuentes principales. El Construction Industry Institute, o CII, aporta los estudios y la definición oficial. La COAA, de Canadá, aporta las buenas prácticas y el modelo escalable. E Insight AWP aporta la guía de inicio rápido y los procedimientos. Cuando las fuentes no coinciden, lo vamos a señalar.

## 1. Por qué AWP

**Lámina 5.** Módulo uno. Por qué AWP. El problema no es la cuadrilla, es la planificación.

**Lámina 6.** Empecemos por los datos. El sesenta y cinco por ciento de los megaproyectos fracasa en costo, plazo o desempeño. Y el setenta por ciento de los proyectos de construcción termina sobre presupuesto y con retraso. Es un problema del sistema, no de una empresa en particular.

**Lámina 7.** La productividad de la construcción no ha mejorado en setenta años, mientras otras industrias sí avanzaron. Como la mano de obra es una de las partidas más grandes del presupuesto, cualquier mejora en su productividad cambia el resultado del proyecto.

**Lámina 8.** De una jornada de diez horas, solo tres coma siete se usan realmente trabajando con herramientas. El resto se pierde esperando planos, buscando materiales, esperando andamios o trasladándose. Con AWP, ese tiempo productivo sube a cuatro coma seis horas.

**Lámina 9.** Los retrasos que vemos en campo nacen en la oficina. Si Ingeniería emite planos en su propio orden, la cuadrilla espera información. Si Compras no sigue la secuencia de construcción, faltan materiales en el frente. Workface Planning ataca el síntoma en campo; AWP ataca la causa en la oficina.

**Lámina 10.** Un trabajador ejecuta cuando tiene cinco cosas: información, herramientas, materiales, acceso y voluntad. Las cuatro primeras las tiene que asegurar la gerencia. La voluntad crece sola cuando las otras cuatro están resueltas.

**Lámina 11.** Workface Planning, o WFP, fue el primer paso: organizar el trabajo de cada cuadrilla en campo. Pero solo no basta, porque llega tarde. Si la ingeniería y las compras no llegaron en orden, el planificador solo administra la escasez. AWP adelanta la planificación a las fases de definición del proyecto.

**Lámina 12.** ¿Y cuál es el resultado? Según los estudios del CII, con AWP la productividad en campo sube un veinticinco por ciento y el costo total instalado baja un diez por ciento. También mejoran el cumplimiento del cronograma, la seguridad y la calidad.

## 2. Qué es AWP

**Lámina 13.** Módulo dos. Qué es AWP. Y lo primero que hay que aclarar: AWP es un proceso, no un software.

**Lámina 14.** El CII define AWP como el flujo general de todos los paquetes de trabajo detallados: de construcción, de ingeniería y de instalación. Es un proceso planificado y ejecutable, que va desde la planificación inicial hasta la construcción, y siempre está dirigido por Construcción.

**Lámina 15.** AWP integra tres procesos. Advanced Work Packaging alinea los paquetes de ingeniería, compras y construcción. Information Management estandariza los datos, el modelo tres D y la nomenclatura. Y Workface Planning lleva el plan a cada cuadrilla. Los tres se implementan juntos.

**Lámina 16.** Todo se ordena en una jerarquía. Arriba está la CWA, el área de construcción. Cada área se divide en CWP, un paquete por disciplina. Cada CWP recibe su ingeniería en un EWP y sus materiales en un PWP. Y cada CWP se divide en varios IWP: el paquete que recibe el capataz cada semana.

**Lámina 17.** La Construction Work Area, o CWA, es la primera división del terreno. Es una parte lógica del plano de implantación, incluye todas las disciplinas y funciona como contenedor de los paquetes de construcción. En el cronograma es una actividad de nivel dos.

**Lámina 18.** Un Construction Work Package, o CWP, es una sola disciplina dentro de una CWA. Por ejemplo, las tuberías del área dos. Tiene menos de cuarenta mil horas hombre, es una actividad de nivel tres y, como los CWP no se superponen, sirven como alcance para licitar.

**Lámina 19.** Un Engineering Work Package, o EWP, entrega toda la ingeniería que necesita un CWP: alcance, planos aprobados para construcción, especificaciones, lista de materiales y vistas del modelo. Un tamaño típico va de cinco mil a veinte mil horas hombre de campo.

**Lámina 20.** Un Procurement Work Package, o PWP, asegura los materiales y equipos de un CWP. Más que una caja física, es un identificador que alinea las compras con la secuencia de construcción. El CII todavía está terminando de definirlo.

**Lámina 21.** Un Installation Work Package, o IWP, es el trabajo de una cuadrilla en una semana. Lo ejecuta un capataz con unos diez trabajadores, está formado por planos completos y solo se entrega a campo cuando está libre de restricciones.

**Lámina 22.** La regla base es: un EWP, igual a un PWP, igual a un CWP. Alinear los tres paquetes simplifica el seguimiento. Hay excepciones razonables, como los materiales a granel o un CWP que depende de varias disciplinas de ingeniería.

**Lámina 23.** Para la puesta en marcha, la lógica cambia: ya no se empaqueta por áreas, sino por sistemas. Ahí aparecen el System Work Package y el Turnover Package. Este cambio de enfoque se acelera cerca del setenta por ciento de avance físico.

**Lámina 24.** Un aviso importante: las fuentes no coinciden en algunos números, como el nivel del IWP, su duración o el tamaño del backlog. No es grave, pero cada proyecto debe fijar sus propios valores en el procedimiento y aplicarlos de forma consistente.

## 3. Preparar la organización

**Lámina 25.** Módulo tres. Preparar la organización. Porque AWP empieza antes del primer plano.

**Lámina 26.** Para arrancar bastan siete componentes: un AWP Champion, procedimientos escritos, un modelo tres D con datos de fabricantes, un software de Workface Planning, planificadores dedicados, un formato de IWP y un proceso para eliminar restricciones.

**Lámina 27.** El primer nombramiento es el AWP Champion, y debe ser a tiempo completo. Representa al propietario, coordina a todos los actores con imparcialidad y actúa como coach del proyecto. No asuman que este rol lo puede cubrir el gerente del proyecto en sus ratos libres.

**Lámina 28.** Los procedimientos fijan quién, qué, cuándo, cómo y por qué. Por sí solos no cambian la cultura, pero crean la obligación de cumplir y permiten auditar el proceso.

**Lámina 29.** Los procedimientos cubren tres áreas. El de AWP define contratos, secuencia y controles. El de Information Management define la estructura de desglose, la nomenclatura y el modelo. Y el de Workface Planning define planificadores, paquetes, restricciones y reportes.

**Lámina 30.** AWP se exige en el contrato, o no ocurre. El procedimiento va con la licitación, el postor se compromete a cumplirlo, el cronograma se desglosa hasta los niveles tres y cinco, y los planificadores son aprobados por el propietario.

**Lámina 31.** Al elegir contratistas, evalúen su capacidad en AWP en una conversación, no solo en un papel. Muchos dicen ser expertos. Un contratista novato dispuesto a aprender suele ser mejor socio que un experto que no practica lo que escribe.

**Lámina 32.** Elijan el software de Workface Planning antes de la ingeniería básica, o FEED, y según lo que ya usan para el modelo tres D, los materiales y el control documental. Recuerden: primero las personas y el proceso; el software acelera, no reemplaza.

**Lámina 33.** La estructura de desglose del trabajo, o WBS, y una nomenclatura común son el idioma del proyecto. Un mismo código identifica la planta, el área, la disciplina, el paquete y el IWP, y conecta el cronograma, los costos, el modelo y los planos.

**Lámina 34.** Arranquen con un seminario de lanzamiento dentro de los treinta días de adjudicado el contrato. En la mañana, capacitación; en la tarde, lecciones aprendidas de otros proyectos. Y formen un comité con todos los actores que se reúna cada mes.

## 4. Fase 1: Planificación preliminar

**Lámina 35.** Módulo cuatro. Fase uno, planificación preliminar. En FEL dos se decide cómo se construirá la planta.

**Lámina 36.** AWP se implementa en cuatro etapas ligadas a las compuertas del proyecto: planificación preliminar en FEL dos, ingeniería y compras en FEL tres, construcción, y comisionamiento y arranque. FEL significa Front End Loading: las etapas de definición antes de decidir la inversión.

**Lámina 37.** Cada etapa tiene una compuerta y un entregable de AWP. En FEL dos se entregan el plan AWP, las áreas y el primer Path of Construction. En FEL tres, ese Path of Construction se firma antes de iniciar la ingeniería de detalle.

**Lámina 38.** Dividan el terreno en áreas de construcción antes de diseñar. Los criterios son prioridad, contratación, racks de tuberías, horas de campo similares, función y proceso. Esta discusión la lidera Construcción, y el resultado es un plano marcado que se comparte con todos.

**Lámina 39.** El Path of Construction, o POC, responde una pregunta clave: ¿cómo y en qué orden se construye? ¿De norte a sur? ¿Qué va primero? ¿Con qué accesos, grúas y zonas de acopio? La respuesta se dibuja sobre el plano como una secuencia de áreas.

**Lámina 40.** El POC tiene componentes definidos: un plano marcado, una matriz de paquetes por disciplina y área, un informe con objetivos, prioridades y restricciones, y una simulación para validar la secuencia con todos los actores.

**Lámina 41.** Construcción lidera el POC, e Ingeniería y Compras lo validan. El Construction Manager es su dueño. Ingeniería expone sus límites técnicos como restricciones, Compras aporta los plazos de los equipos críticos, y el contratista participa o lo revisa en la licitación.

**Lámina 42.** El POC se construye en tres pasos. Primero, un POC sin restricciones, solo con Construcción. Luego, un taller interactivo donde Ingeniería y Compras presentan sus plazos y limitaciones. Y finalmente, un POC firmado que sirve de base para el cronograma de nivel tres.

**Lámina 43.** Del taller sale el plan de liberación. Por cada disciplina se ordenan el EWP, el PWP y el CWP en serie, uno tras otro. Ingeniería y Compras calculan hacia atrás, desde la fecha en que Construcción necesita iniciar cada paquete.

**Lámina 44.** El POC se define en FEL dos y se congela al final de FEL tres. Congelarlo a tiempo le da a Ingeniería la mejor oportunidad de cumplir el plan. Después se puede actualizar, pero con gestión formal del cambio.

**Lámina 45.** El cronograma se escalona en siete niveles, del año a la hora. Las áreas van en el nivel dos, los CWP en el nivel tres y los IWP en el nivel cinco. El planificador divide cada CWP en IWP y le entrega esa secuencia al programador.

**Lámina 46.** Los entregables de la fase uno son: el plan AWP, el plano con las áreas, el Path of Construction, la matriz de paquetes, el plan de liberación preliminar, los procedimientos aprobados y una estrategia de contratación con cláusulas AWP.

## 5. Fase 2: Ingeniería y compras

**Lámina 47.** Módulo cinco. Fase dos, ingeniería y compras. La ingeniería se entrega en el orden en que se construye.

**Lámina 48.** Aclaremos un temor frecuente. AWP no le agrega trabajo a Ingeniería: le cambia el orden. Se puede seguir diseñando por sistemas. Lo que cambia es cómo se entregan los paquetes y qué prioridad guía la secuencia.

**Lámina 49.** Comparemos. En el enfoque tradicional, Ingeniería avanza según su propia lógica y el campo trabaja donde hay información. Con AWP, el Path of Construction fija el orden, los EWP se entregan en esa secuencia y cada paquete llega completo a campo.

**Lámina 50.** Gestionar la ingeniería por área convierte cada área en un miniproyecto. Los entregables son más pequeños y el seguimiento es más fino, así que los atrasos se detectan semanas antes y se sabe exactamente qué área se está atrasando.

**Lámina 51.** Cada EWP tiene su propio flujo: se define el marco, se capacita al equipo, se diseña y revisa, el propietario y el contratista lo revisan, y finalmente se libera. Esa liberación es el hito que da inicio al paquete de construcción.

**Lámina 52.** El avance de Ingeniería se mide con reglas de crédito por EWP. Fíjense que la mitad del crédito se gana solo cuando el paquete se emite aprobado para construcción y sin retenciones. Así se premia entregar paquetes completos, no planos sueltos.

**Lámina 53.** Los EWP los prepara el contratista de Ingeniería, sea cual sea el tipo de contrato. Los lidera el gerente de Ingeniería, los revisan el propietario y el contratista de construcción, y su liberación queda como hito en el cronograma.

**Lámina 54.** Compras también cambia. En lugar de ordenar por fecha de requisición, se secuencia por paquete de construcción. Se define desde el inicio quién suministra qué, la fecha en que cada material se necesita en obra, y se mantiene la trazabilidad completa.

**Lámina 55.** El Procurement Work Number conecta cada compra con su paquete. El mismo código acompaña al material desde el EWP, pasando por la lista de materiales, el pedido y el envío, hasta la recepción en obra.

**Lámina 56.** El CWP se arma cuando se libera su EWP. Construcción revisa la ingeniería, redacta el paquete con su alcance, límites, seguridad y calidad, el propietario lo revisa, y el CWP se libera como base del alcance para los contratistas.

**Lámina 57.** ¿Quién redacta los CWP? Construcción define su tamaño, contenido y secuencia, pero quién los escribe depende del modelo de contrato. En proyectos pequeños, incluso puede hacerlo Ingeniería. Lo importante es definirlo antes de licitar.

**Lámina 58.** Los entregables de la fase dos son: EWP emitidos en secuencia, PWP con fechas requeridas en obra, CWP liberados, el modelo tres D con atributos, el estimado por área y disciplina, el cronograma de nivel tres y los planes de liberación al día.

## 6. Fase 3: Construcción y Workface Planning

**Lámina 59.** Módulo seis. Fase tres, construcción. En campo, cada capataz recibe un paquete listo para ejecutar.

**Lámina 60.** Esta es la meta de todo AWP: que cada lunes, cada capataz reciba un IWP listo. Con el alcance claro, los materiales y herramientas disponibles, el trabajo previo terminado y el andamio armado.

**Lámina 61.** Workface Planning es un ciclo de cuatro pasos: definir, crear, ejecutar y seguir los IWP. El Workface Planner además verifica el alcance de cada CWP, gestiona las restricciones y el backlog, y prepara los paquetes para la entrega por sistemas.

**Lámina 62.** El IWP contiene todo lo que el capataz necesita: una portada con el valor planificado, los contactos de emergencia, la lista de restricciones, el alcance, los requisitos de seguridad y calidad, los planos justos y la lista de materiales verificada.

**Lámina 63.** Del CWP al IWP hay cuatro pasos, unos noventa días antes de ejecutar. Se elige el CWP, el superintendente explica cómo dividir y ordenar el trabajo, el planificador arma los IWP en el modelo tres D, y el superintendente los aprueba.

**Lámina 64.** ¿Qué tamaño debe tener un IWP? Empiecen con unas quinientas horas y ajusten según la experiencia. Los paquetes pequeños son más fáciles de seguir para el capataz. La referencia es un capataz, unos diez trabajadores y una ventana de siete días.

**Lámina 65.** La regla de oro es clara: ningún IWP va a campo con restricciones. Las críticas son los documentos, los materiales y los andamios. Cada restricción se libera con una firma en la página de restricciones del paquete.

**Lámina 66.** Las restricciones se liberan en cuatro pasos: el IWP se inicia, las restricciones se identifican, se asignan y se liberan. En una parada de planta el ciclo dura unas seis semanas; en un megaproyecto, unas doce.

**Lámina 67.** Cada restricción tiene dueño, fecha y prioridad. Las buenas prácticas son: una lista única, un flujo formal de aprobación, una reunión estándar, un árbol de decisión para los paquetes que siguen abiertos y un reporte de estado para toda la gerencia.

**Lámina 68.** El backlog es el conjunto de IWP libres de restricciones, listos para elegir. Los paquetes avanzan como en un embudo, desde la ventana de noventa días hasta el campo. La meta es tener entre dos y cuatro semanas de trabajo listo por disciplina.

**Lámina 69.** El look ahead de tres semanas se alimenta solo del backlog. Cada semana, el superintendente elige paquetes libres y los carga en el cronograma de nivel cinco. Si una disciplina se queda sin IWP disponibles, es una alerta temprana.

**Lámina 70.** El Pack Track es una sola hoja que muestra el estado de todos los IWP: cuándo se crearon, cuándo llegaron sus planos y materiales, cuándo entraron al backlog y cuándo se emitieron a campo. Con ella se arma un tablero semanal para la gerencia.

**Lámina 71.** Cada IWP tiene fecha de caducidad. Si no se termina en su ventana, puede tener una prórroga corta de uno o dos días. Si aun así no se completa, vuelve al planificador y el alcance pendiente pasa a un nuevo paquete.

**Lámina 72.** El capataz registra el avance cada día en su IWP. El planificador lo carga en el software, Controles lo compara con el valor planificado y la gerencia obtiene una sola versión de la verdad. Además, las horas se cargan usando el número de IWP como código de costo.

**Lámina 73.** Los códigos de demora explican cada hora perdida: esperar planos, falta de material, andamio no disponible, equipo ausente o un permiso pendiente. Esta tabla es un ejemplo; cada proyecto define la suya.

**Lámina 74.** Los entregables de la fase tres son: IWP liberados sin restricciones, el Pack Track semanal, un backlog de dos a cuatro semanas, el look ahead de tres semanas, el plan diario del capataz, el avance diario y el registro de restricciones y demoras.

## 7. Fase 4: Puesta en marcha

**Lámina 75.** Módulo siete. Fase cuatro, puesta en marcha. Al final se entrega por sistemas, no por áreas.

**Lámina 76.** Cerca del setenta por ciento de avance, el enfoque cambia. Antes se medía el avance por área; ahora se mide la preparación por sistema. El System Work Package agrupa partes de varios paquetes que pertenecen al mismo sistema funcional.

**Lámina 77.** Por eso el Path of Construction también debe mirar la secuencia de sistemas. Operaciones define las prioridades de arranque, el POC ordena las áreas pensando en esos sistemas, y los paquetes terminados se agrupan hasta formar el Turnover Package.

**Lámina 78.** El Turnover Package documenta que el sistema está listo. Primero se verifica el completamiento mecánico, luego se hacen las pruebas, después se certifica que está listo para comisionar y, por último, que está listo para operar.

**Lámina 79.** Los entregables de la fase cuatro son: paquetes por sistema, paquetes de prueba, Turnover Packages, certificados de listo para comisionar y para operar, el dossier de calidad y las lecciones aprendidas.

## 8. Información y tecnología

**Lámina 80.** Módulo ocho. Información y tecnología. Sin datos confiables no hay paquetes confiables.

**Lámina 81.** El modelo tres D con atributos es la plataforma de planificación. Cada componente lleva datos como su código, su área, su EWP, su CWP y su IWP. Una matriz de atributos le dice a Ingeniería qué información debe cargar para que Construcción la pueda usar.

**Lámina 82.** Los datos de los fabricantes se piden en el contrato. Cada intercambio tiene un formato recomendado, por ejemplo archivos de tuberías y de acero que el software puede leer. Si no se exige en la compra, no llega.

**Lámina 83.** Un solo repositorio documental elimina el desfase de revisiones. Ingeniería carga los planos, el repositorio los ordena por código, el modelo enlaza cada objeto con su plano vigente y Construcción consulta e imprime su IWP.

**Lámina 84.** Los materiales se agrupan por IWP hasta ocho semanas antes. El planificador envía la lista, el almacén separa las entregas por paquete, el material se etiqueta al entrar al look ahead y se pide al frente una semana antes.

**Lámina 85.** Andamios y equipos se piden desde el IWP con al menos dos semanas de anticipación. Así se reducen las esperas en campo y también baja el costo total de andamios y grúas.

**Lámina 86.** Una lección clave: primero las personas y el proceso; después la tecnología. La tecnología acelera lo que ya funciona, pero no arregla un proceso que no está definido.

## 9. Roles y organización

**Lámina 87.** Módulo nueve. Roles y organización. AWP redistribuye responsabilidades, no solo agrega cargos.

**Lámina 88.** Cada actor tiene un papel. El propietario respalda. El EPC lidera el plan y mantiene el POC. Ingeniería entrega los EWP, Compras los PWP y Construcción ejecuta los IWP. Y el AWP Champion, de forma transversal, integra y capacita.

**Lámina 89.** El AWP Champion guía; no ejecuta por los demás. Lidera la adopción, coordina con el propietario y los subcontratistas, acompaña al equipo y supervisa Workface Planning en obra. Nunca lo dejen solo.

**Lámina 90.** El Workface Planner es alguien de oficio con experiencia, no un oficinista. Conoce el trabajo, ha supervisado en campo, maneja el software básico, reporta al superintendente y se dedica solo a planificar.

**Lámina 91.** La proporción de referencia es un planificador por cada cincuenta trabajadores. Se ajusta por complejidad: la instrumentación exige más planificación que el concreto o el movimiento de tierras.

**Lámina 92.** El Construction Manager es el dueño de AWP en la obra. Explica por qué se usa, lidera el Path of Construction y la constructabilidad, revisa los entregables y sigue el impacto de las restricciones. Si él no cree en AWP, la implementación será un trámite.

**Lámina 93.** La supervisión de campo también cambia su rutina. El superintendente elige paquetes del backlog, el capataz general pide el material una semana antes y el capataz revisa su IWP, arma su plan diario y registra el avance.

**Lámina 94.** Los ratios de supervisión difieren entre fuentes: un capataz general puede tener cuatro o cinco capataces, y un superintendente, tres o cuatro capataces generales. Definan los suyos según la complejidad del trabajo.

**Lámina 95.** Esta matriz de responsabilidades es una propuesta para empezar. Indica quién es responsable, quién aprueba, a quién se consulta y a quién se informa en cada entregable. Ajústenla a su modelo de contrato.

## 10. Medición

**Lámina 96.** Módulo diez. Medición. Lo que no se mide en paquetes no se mejora.

**Lámina 97.** Hay dos familias de indicadores. Los de Ingeniería siguen la lista de entregables, las reglas de crédito y los planes de liberación. Los de Construcción siguen los IWP listos, el cierre de restricciones y el cumplimiento del plan.

**Lámina 98.** En Ingeniería, comparen siempre las fechas planificadas con las reales. En este ejemplo, siete días de atraso en un EWP se convierten en catorce días de atraso en su CWP. El plan de liberación es un indicador adelantado de los problemas en campo.

**Lámina 99.** En campo, midan seis cosas: IWP listos frente al total, cierre de restricciones, días de backlog, IWP completados a tiempo, porcentaje del plan cumplido y productividad por disciplina.

**Lámina 100.** El valor planificado se calcula por IWP. Los paquetes se preparan no antes de tres meses de ejecutarse, las cantidades se multiplican por tasas estándar, las horas se cargan por IWP y el capataz registra el avance físico. Cantidad por tasa da horas; horas entre dotación da duración.

**Lámina 101.** El indicador más directo es el tiempo en herramientas. Pasa del treinta y siete al cuarenta y seis por ciento con AWP, de tres coma siete a cuatro coma seis horas por jornada. Mídanlo con estudios independientes cada dos o tres meses.

**Lámina 102.** Auditen el proceso AWP, no solo el cronograma. Hagan revisiones independientes, auditorías periódicas con una plantilla, un informe semanal desde el Pack Track y un comité mensual que resuelva los problemas entre actores.

## 11. Escalar y adoptar

**Lámina 103.** Módulo once. Escalar y adoptar. AWP se ajusta al tamaño del proyecto.

**Lámina 104.** AWP también sirve para proyectos de menos de cien millones de dólares. En dos mil diecinueve, la COAA diseñó un modelo de AWP escalable, desarrollado por cuarenta profesionales de la industria, que no renuncia a los principios.

**Lámina 105.** Dos factores definen cuánto AWP necesita un proyecto: qué tan familiar es para la empresa y qué tan complejo es. Con ellos se forman cuatro categorías, de la A a la D, y una herramienta de preguntas ubica al proyecto en su categoría.

**Lámina 106.** En una parada de planta el ciclo es el mismo, pero más corto: el IWP se inicia seis semanas antes y las restricciones se liberan dos semanas antes. En un megaproyecto, esos plazos son de doce y cuatro semanas. Cambia el horizonte, no los pasos.

**Lámina 107.** AWP y Lean Construction se complementan. AWP usa planificadores dedicados y un proceso formal de restricciones. Lean se apoya en el último planificador y en compromisos confiables. Muchas empresas combinan ambos.

**Lámina 108.** Un informe conjunto del CII y del Lean Construction Institute compara ambos enfoques en once temas. Coinciden en seguridad y calidad; difieren en quién planifica, cómo se mide el avance y cómo se organiza el equipo.

**Lámina 109.** Y hay doce objeciones frecuentes, todas con respuesta. Por ejemplo: mi proyecto es muy pequeño; existe el modelo escalable. O: es un contrato a suma alzada; entonces AWP aumenta su margen.

**Lámina 110.** La objeción más peligrosa es: ya hacemos AWP. Para comprobarlo, hagan tres preguntas: ¿hay un POC firmado? ¿Cuántos días de backlog tiene cada disciplina? ¿Dónde está el Pack Track de esta semana?

## 12. Errores y lecciones

**Lámina 111.** Módulo doce. Errores y lecciones. Otros ya cometieron estos errores; aprovechemos su experiencia.

**Lámina 112.** Primera lección: AWP es un camino. No va a salir perfecto la primera vez. Registren lo que no funcionó, celebren las mejoras y ajusten el procedimiento en cada proyecto.

**Lámina 113.** Segunda lección: gatear, caminar, correr. Empiecen con paquetes más precisos y un piloto, luego apliquen Workface Planning en toda la obra, y finalmente implementen AWP de principio a fin.

**Lámina 114.** Esperen resistencia, y respóndanla con un lenguaje común. Reconozcan lo que la gente ya hace bien, capaciten de forma constante y usen el vocabulario de AWP en reuniones y documentos.

**Lámina 115.** Un contratista novato con ganas de aprender vale más que un experto de papel. El experto de papel envía procedimientos impecables, pero no los aplica. El novato reconoce lo que no sabe y mejora semana a semana.

**Lámina 116.** Estos son los siete errores más caros: un Champion a medio tiempo, un POC tardío, IWP con restricciones abiertas, movilizar sin backlog, comprar software antes de definir el proceso, no incluir AWP en el contrato y no medir.

**Lámina 117.** Hagan este diagnóstico rápido con su equipo. Son siete preguntas de sí o no. Cada respuesta negativa se convierte en una prioridad para los próximos noventa días.

**Lámina 118.** Finalmente, registren y reutilicen las lecciones de cada proyecto: midan, analicen, registren y reutilicen. Así, cada nuevo proyecto empieza con una base más madura.

## 13. Hoja de ruta

**Lámina 119.** Módulo trece. Hoja de ruta. Empiecen el lunes con tres acciones.

**Lámina 120.** Esta es una hoja de ruta de noventa días. En el primer mes, nombren al Champion y capaciten al equipo. En el segundo, escriban los procedimientos y las cláusulas de contrato. Y en el tercero, hagan un piloto con un paquete real.

**Lámina 121.** En resumen: cuatro fases y un solo hilo conductor. Construcción define el orden, Ingeniería y Compras lo siguen, el campo ejecuta sin restricciones y Operaciones recibe por sistemas.

**Lámina 122.** Construyan en el orden correcto y la productividad llegará. El siguiente paso es concreto: nombrar al AWP Champion del proyecto. Gracias por acompañarnos.
