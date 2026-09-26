/*
 * CATÁLOGO LOCAL DE DIPLOMACIA GLOBAL
 * -----------------------------------
 * Esta es la "base de datos" de demostración. Funciona sin internet y sin servidor.
 *
 * Cada elemento tiene esta forma:
 *   id            Identificador único (texto sin espacios).
 *   tipo          "noticia" | "paper" | "libro".
 *   titulo        Título que verá la persona.
 *   resumen       2 o 3 líneas en lenguaje sencillo.
 *   autor         Autor o institución.
 *   fuente        Editorial, revista o medio.
 *   fecha         "AAAA-MM-DD" o "AAAA".
 *   enlace        Página original (se abre en una pestaña nueva).
 *   descarga      null, o { url, formato, nombreArchivo } si el documento es de acceso libre.
 *   etiquetas     Palabras clave (en español e inglés) que ayudan a encontrarlo.
 *   destacado     true si debe aparecer en la portada de su sección.
 *   ejemplo       true si es contenido de DEMOSTRACIÓN (no es una noticia real).
 *
 * Para agregar un documento nuevo, copie un bloque { ... }, cambie los datos y guarde.
 *
 * El archivo funciona tanto en el navegador (window.CATALOGO_DIPLOMACIA)
 * como en el servidor Node.js (require).
 */
(function (raiz) {
  'use strict';

  var CATALOGO = [
    /* ============================== LIBROS ============================== */
    {
      id: 'libro-kissinger-diplomacia',
      tipo: 'libro',
      titulo: 'Diplomacia',
      resumen: 'Un recorrido por la historia de las relaciones entre países, desde Richelieu hasta el fin de la Guerra Fría. Explica cómo el equilibrio de poder y los intereses nacionales han guiado a los grandes líderes.',
      autor: 'Henry Kissinger',
      fuente: 'Ediciones B (edición en español, 1996)',
      fecha: '1994',
      enlace: 'https://openlibrary.org/search?q=Kissinger+Diplomacy',
      descarga: null,
      etiquetas: ['historia', 'equilibrio de poder', 'realpolitik', 'guerra fria', 'cold war', 'concierto de europa', 'bismarck', 'richelieu', 'wilson', 'versalles', 'estados unidos', 'vietnam', 'detente', 'realismo'],
      destacado: true
    },
    {
      id: 'libro-berridge-diplomacy',
      tipo: 'libro',
      titulo: 'Diplomacy: Theory and Practice (6.ª edición)',
      resumen: 'Manual muy completo sobre cómo trabaja la diplomacia hoy: ministerios de relaciones exteriores, embajadas, consulados, cumbres y el arte de negociar. Escrito en inglés, con ejemplos claros.',
      autor: 'G. R. Berridge',
      fuente: 'Palgrave Macmillan',
      fecha: '2022',
      enlace: 'https://openlibrary.org/search?q=Berridge+Diplomacy+Theory+and+Practice',
      descarga: null,
      etiquetas: ['negociacion', 'negotiation', 'embajadas', 'embassies', 'consulados', 'cumbres', 'summits', 'ministerio de relaciones exteriores', 'foreign ministry', 'mediacion', 'teoria', 'practica diplomatica'],
      destacado: true
    },
    {
      id: 'libro-kissinger-orden-mundial',
      tipo: 'libro',
      titulo: 'Orden Mundial',
      resumen: 'Reflexión sobre cómo distintas regiones (Europa, el mundo islámico, China y Estados Unidos) entienden el orden internacional, y por qué hoy cuesta ponerse de acuerdo sobre unas reglas comunes.',
      autor: 'Henry Kissinger',
      fuente: 'Debate',
      fecha: '2014',
      enlace: 'https://openlibrary.org/search?q=Kissinger+World+Order',
      descarga: null,
      etiquetas: ['orden internacional', 'world order', 'westfalia', 'westphalia', 'china', 'islam', 'europa', 'geopolitica'],
      destacado: true
    },
    {
      id: 'libro-morgenthau-politica',
      tipo: 'libro',
      titulo: 'Política entre las naciones: la lucha por el poder y la paz',
      resumen: 'Obra fundadora del realismo político. Sostiene que los Estados actúan según su interés, entendido como poder, y que la diplomacia prudente es la mejor herramienta para preservar la paz.',
      autor: 'Hans J. Morgenthau',
      fuente: 'Grupo Editor Latinoamericano (edición en español)',
      fecha: '1948',
      enlace: 'https://openlibrary.org/search?q=Morgenthau+Politics+Among+Nations',
      descarga: null,
      etiquetas: ['realismo', 'realism', 'poder', 'interes nacional', 'paz', 'teoria', 'relaciones internacionales'],
      destacado: true
    },
    {
      id: 'libro-carr-veinte-anos',
      tipo: 'libro',
      titulo: 'La crisis de los veinte años (1919-1939)',
      resumen: 'Analiza por qué fracasó la paz entre las dos guerras mundiales. Critica el idealismo de la época y explica la importancia de tener en cuenta el poder real de cada país.',
      autor: 'Edward Hallett Carr',
      fuente: 'Los Libros de la Catarata (edición en español)',
      fecha: '1939',
      enlace: 'https://openlibrary.org/search?q=Carr+Twenty+Years+Crisis',
      descarga: null,
      etiquetas: ['entreguerras', 'sociedad de naciones', 'idealismo', 'realismo', 'versalles', 'segunda guerra mundial'],
      destacado: false
    },
    {
      id: 'libro-nicolson-diplomacia',
      tipo: 'libro',
      titulo: 'La diplomacia',
      resumen: 'Libro breve y clásico escrito por un diplomático británico. Describe las cualidades del buen negociador: veracidad, precisión, calma, paciencia y modestia.',
      autor: 'Harold Nicolson',
      fuente: 'Fondo de Cultura Económica (edición en español)',
      fecha: '1939',
      enlace: 'https://openlibrary.org/search?q=Harold+Nicolson+Diplomacy',
      descarga: null,
      etiquetas: ['diplomatico', 'negociacion', 'clasico', 'historia de la diplomacia', 'reino unido'],
      destacado: false
    },
    {
      id: 'libro-kennan-diplomacia-americana',
      tipo: 'libro',
      titulo: 'American Diplomacy',
      resumen: 'Conferencias del diplomático que ideó la política de “contención” frente a la Unión Soviética. Critica que la política exterior se base en principios morales o legales sin medir las consecuencias.',
      autor: 'George F. Kennan',
      fuente: 'University of Chicago Press',
      fecha: '1951',
      enlace: 'https://openlibrary.org/search?q=Kennan+American+Diplomacy',
      descarga: null,
      etiquetas: ['contencion', 'containment', 'guerra fria', 'cold war', 'estados unidos', 'union sovietica'],
      destacado: false
    },
    {
      id: 'libro-waltz-teoria',
      tipo: 'libro',
      titulo: 'Teoría de la política internacional',
      resumen: 'Explica que el comportamiento de los países depende sobre todo de la estructura del sistema internacional, donde no existe un gobierno mundial. Base del llamado “neorrealismo”.',
      autor: 'Kenneth N. Waltz',
      fuente: 'Grupo Editor Latinoamericano (edición en español)',
      fecha: '1979',
      enlace: 'https://openlibrary.org/search?q=Waltz+Theory+of+International+Politics',
      descarga: null,
      etiquetas: ['neorrealismo', 'neorealism', 'anarquia', 'sistema internacional', 'teoria'],
      destacado: false
    },
    {
      id: 'libro-tucidides-guerra',
      tipo: 'libro',
      titulo: 'Historia de la Guerra del Peloponeso (texto completo, en inglés)',
      resumen: 'Relato de la guerra entre Atenas y Esparta hace 2.400 años. Incluye el famoso “Diálogo de los Melios”, una de las primeras discusiones escritas sobre poder y justicia entre pueblos.',
      autor: 'Tucídides (trad. Richard Crawley)',
      fuente: 'Proyecto Gutenberg — dominio público',
      fecha: '-0400',
      enlace: 'https://www.gutenberg.org/ebooks/7142',
      descarga: { url: 'https://www.gutenberg.org/cache/epub/7142/pg7142.txt', formato: 'Texto', nombreArchivo: 'Tucidides-Guerra-del-Peloponeso.txt' },
      etiquetas: ['antigua grecia', 'atenas', 'esparta', 'melios', 'clasico', 'dominio publico', 'guerra', 'poder'],
      destacado: true
    },
    {
      id: 'libro-maquiavelo-principe',
      tipo: 'libro',
      titulo: 'El Príncipe (texto completo, en inglés)',
      resumen: 'Consejos de Maquiavelo a los gobernantes de su época sobre cómo conseguir y conservar el poder. Un texto breve que sigue influyendo en la política y la diplomacia.',
      autor: 'Nicolás Maquiavelo',
      fuente: 'Proyecto Gutenberg — dominio público',
      fecha: '1532',
      enlace: 'https://www.gutenberg.org/ebooks/1232',
      descarga: { url: 'https://www.gutenberg.org/cache/epub/1232/pg1232.txt', formato: 'Texto', nombreArchivo: 'Maquiavelo-El-Principe.txt' },
      etiquetas: ['renacimiento', 'poder', 'gobernante', 'florencia', 'clasico', 'dominio publico', 'realismo'],
      destacado: true
    },
    {
      id: 'libro-kant-paz-perpetua',
      tipo: 'libro',
      titulo: 'La paz perpetua (texto completo, en inglés)',
      resumen: 'Propuesta del filósofo Kant para acabar con las guerras: repúblicas con leyes, una federación de pueblos libres y respeto al visitante extranjero. Inspiró la idea de la ONU.',
      autor: 'Immanuel Kant',
      fuente: 'Proyecto Gutenberg — dominio público',
      fecha: '1795',
      enlace: 'https://www.gutenberg.org/ebooks/50922',
      descarga: null,
      etiquetas: ['paz', 'filosofia', 'liberalismo', 'federacion', 'clasico', 'dominio publico', 'tratados de paz'],
      destacado: false
    },
    {
      id: 'libro-clausewitz-guerra',
      tipo: 'libro',
      titulo: 'De la guerra (texto completo, en inglés)',
      resumen: 'Obra clásica que explica que “la guerra es la continuación de la política por otros medios”. Ayuda a entender la relación entre diplomacia, poder militar y objetivos políticos.',
      autor: 'Carl von Clausewitz',
      fuente: 'Proyecto Gutenberg — dominio público',
      fecha: '1832',
      enlace: 'https://www.gutenberg.org/ebooks/1946',
      descarga: { url: 'https://www.gutenberg.org/cache/epub/1946/pg1946.txt', formato: 'Texto', nombreArchivo: 'Clausewitz-De-la-guerra.txt' },
      etiquetas: ['guerra', 'estrategia', 'politica', 'clasico', 'dominio publico', 'prusia'],
      destacado: false
    },
    {
      id: 'libro-sun-tzu-arte-guerra',
      tipo: 'libro',
      titulo: 'El arte de la guerra (texto completo, en inglés)',
      resumen: 'Antiguo tratado chino de estrategia. Enseña que la mejor victoria es la que se logra sin combatir, una idea muy cercana a la diplomacia.',
      autor: 'Sun Tzu (trad. Lionel Giles)',
      fuente: 'Proyecto Gutenberg — dominio público',
      fecha: '-0500',
      enlace: 'https://www.gutenberg.org/ebooks/132',
      descarga: { url: 'https://www.gutenberg.org/cache/epub/132/pg132.txt', formato: 'Texto', nombreArchivo: 'Sun-Tzu-El-arte-de-la-guerra.txt' },
      etiquetas: ['china', 'estrategia', 'clasico', 'dominio publico', 'guerra'],
      destacado: false
    },

    /* ============================ PAPERS ============================== */
    {
      id: 'paper-carta-onu',
      tipo: 'paper',
      titulo: 'Carta de las Naciones Unidas (documento oficial, PDF)',
      resumen: 'El tratado que creó la ONU en 1945. Establece sus propósitos: mantener la paz, fomentar la amistad entre naciones y resolver los conflictos de forma pacífica.',
      autor: 'Organización de las Naciones Unidas',
      fuente: 'Colección de Tratados de la ONU',
      fecha: '1945-06-26',
      enlace: 'https://www.un.org/es/about-us/un-charter',
      descarga: { url: 'https://treaties.un.org/doc/publication/ctc/uncharter.pdf', formato: 'PDF', nombreArchivo: 'Carta-de-las-Naciones-Unidas.pdf' },
      etiquetas: ['onu', 'naciones unidas', 'united nations', 'tratado', 'treaty', 'paz', 'consejo de seguridad', 'derecho internacional', 'documento oficial'],
      destacado: true
    },
    {
      id: 'paper-convencion-viena-1961',
      tipo: 'paper',
      titulo: 'Convención de Viena sobre Relaciones Diplomáticas, 1961 (PDF)',
      resumen: 'Las reglas básicas de la diplomacia moderna: cómo se abren las embajadas y qué protección tienen los diplomáticos (la llamada “inmunidad diplomática”).',
      autor: 'Naciones Unidas — Comisión de Derecho Internacional',
      fuente: 'Oficina de Asuntos Jurídicos de la ONU',
      fecha: '1961-04-18',
      enlace: 'https://legal.un.org/ilc/texts/9_1.shtml',
      descarga: { url: 'https://legal.un.org/ilc/texts/instruments/english/conventions/9_1_1961.pdf', formato: 'PDF', nombreArchivo: 'Convencion-Viena-Relaciones-Diplomaticas-1961.pdf' },
      etiquetas: ['convencion de viena', 'vienna convention', 'inmunidad diplomatica', 'embajadas', 'derecho diplomatico', 'tratado', 'documento oficial'],
      destacado: true
    },
    {
      id: 'paper-convencion-viena-1963',
      tipo: 'paper',
      titulo: 'Convención de Viena sobre Relaciones Consulares, 1963 (PDF)',
      resumen: 'Explica qué hacen los consulados: ayudar a los ciudadanos en el extranjero, emitir documentos y visas, y cómo deben ser tratados los cónsules.',
      autor: 'Naciones Unidas — Comisión de Derecho Internacional',
      fuente: 'Oficina de Asuntos Jurídicos de la ONU',
      fecha: '1963-04-24',
      enlace: 'https://legal.un.org/ilc/texts/9_2.shtml',
      descarga: { url: 'https://legal.un.org/ilc/texts/instruments/english/conventions/9_2_1963.pdf', formato: 'PDF', nombreArchivo: 'Convencion-Viena-Relaciones-Consulares-1963.pdf' },
      etiquetas: ['convencion de viena', 'consulados', 'consular', 'consules', 'visas', 'tratado', 'documento oficial'],
      destacado: false
    },
    {
      id: 'paper-convencion-viena-tratados',
      tipo: 'paper',
      titulo: 'Convención de Viena sobre el Derecho de los Tratados, 1969 (PDF)',
      resumen: 'El “manual de instrucciones” de los tratados internacionales: cómo se firman, cómo se interpretan y cuándo dejan de valer.',
      autor: 'Naciones Unidas — Comisión de Derecho Internacional',
      fuente: 'Oficina de Asuntos Jurídicos de la ONU',
      fecha: '1969-05-23',
      enlace: 'https://legal.un.org/ilc/texts/1_1.shtml',
      descarga: { url: 'https://legal.un.org/ilc/texts/instruments/english/conventions/1_1_1969.pdf', formato: 'PDF', nombreArchivo: 'Convencion-Viena-Derecho-de-los-Tratados-1969.pdf' },
      etiquetas: ['tratados', 'treaties', 'tratados de paz', 'derecho internacional', 'convencion de viena', 'documento oficial'],
      destacado: false
    },
    {
      id: 'paper-putnam-dos-niveles',
      tipo: 'paper',
      titulo: 'Diplomacy and Domestic Politics: The Logic of Two-Level Games',
      resumen: 'Explica que un negociador internacional juega dos partidas a la vez: una con los otros países y otra con su propio parlamento y opinión pública. Ambas deben aceptar el acuerdo.',
      autor: 'Robert D. Putnam',
      fuente: 'International Organization, vol. 42, n.º 3',
      fecha: '1988',
      enlace: 'https://doi.org/10.1017/S0020818300027697',
      descarga: null,
      etiquetas: ['negociacion', 'negotiation', 'politica interna', 'juegos de dos niveles', 'two-level games', 'acuerdos'],
      destacado: true
    },
    {
      id: 'paper-fearon-guerra',
      tipo: 'paper',
      titulo: 'Rationalist Explanations for War',
      resumen: 'Se pregunta por qué los países van a la guerra si siempre sería más barato llegar a un acuerdo. Señala la falta de información confiable y la desconfianza en las promesas.',
      autor: 'James D. Fearon',
      fuente: 'International Organization, vol. 49, n.º 3',
      fecha: '1995',
      enlace: 'https://doi.org/10.1017/S0020818300033324',
      descarga: null,
      etiquetas: ['guerra', 'war', 'negociacion', 'bargaining', 'informacion', 'compromiso', 'conflicto'],
      destacado: true
    },
    {
      id: 'paper-wendt-anarquia',
      tipo: 'paper',
      titulo: 'Anarchy is What States Make of It',
      resumen: 'Propone que la desconfianza entre países no es inevitable: depende de las ideas e identidades que los Estados construyen al relacionarse. Base del “constructivismo”.',
      autor: 'Alexander Wendt',
      fuente: 'International Organization, vol. 46, n.º 2',
      fecha: '1992',
      enlace: 'https://doi.org/10.1017/S0020818300027764',
      descarga: null,
      etiquetas: ['constructivismo', 'constructivism', 'anarquia', 'identidad', 'teoria'],
      destacado: false
    },
    {
      id: 'paper-jervis-dilema',
      tipo: 'paper',
      titulo: 'Cooperation Under the Security Dilemma',
      resumen: 'Cuando un país se arma para protegerse, sus vecinos se sienten amenazados y también se arman. El artículo explica este “dilema de seguridad” y cómo reducirlo.',
      autor: 'Robert Jervis',
      fuente: 'World Politics, vol. 30, n.º 2',
      fecha: '1978',
      enlace: 'https://doi.org/10.2307/2009958',
      descarga: null,
      etiquetas: ['dilema de seguridad', 'security dilemma', 'cooperacion', 'armamento', 'desarme', 'guerra fria'],
      destacado: false
    },
    {
      id: 'paper-mearsheimer-instituciones',
      tipo: 'paper',
      titulo: 'The False Promise of International Institutions',
      resumen: 'Sostiene, desde el realismo, que las organizaciones internacionales tienen poca capacidad para evitar guerras, porque los países más fuertes siguen decidiendo.',
      autor: 'John J. Mearsheimer',
      fuente: 'International Security, vol. 19, n.º 3',
      fecha: '1994',
      enlace: 'https://doi.org/10.2307/2539078',
      descarga: null,
      etiquetas: ['instituciones', 'organizaciones internacionales', 'realismo', 'onu', 'otan'],
      destacado: false
    },
    {
      id: 'paper-nye-poder-blando',
      tipo: 'paper',
      titulo: 'Soft Power',
      resumen: 'Presenta la idea de “poder blando”: la capacidad de un país para atraer y convencer mediante su cultura, sus valores y su diplomacia, sin usar la fuerza.',
      autor: 'Joseph S. Nye Jr.',
      fuente: 'Foreign Policy, n.º 80',
      fecha: '1990',
      enlace: 'https://doi.org/10.2307/1148580',
      descarga: null,
      etiquetas: ['poder blando', 'soft power', 'diplomacia publica', 'cultura', 'estados unidos'],
      destacado: false
    },

    /* ======================= NOTICIAS (EJEMPLO) ======================= */
    /* Estas "noticias" son TEXTOS DE DEMOSTRACIÓN: explican temas de actualidad
       de forma general y enlazan a la portada de medios reales. Cuando el servidor
       tiene internet, se reemplazan por titulares reales (ver servidor/fuentes). */
    {
      id: 'noticia-ejemplo-asamblea-onu',
      tipo: 'noticia',
      titulo: 'Qué ocurre cada septiembre en la Asamblea General de la ONU',
      resumen: 'Cada año, jefes de Estado de casi todo el mundo viajan a Nueva York para hablar ante la Asamblea General. Es una gran ocasión para reuniones diplomáticas en privado.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'Noticias ONU (portada)',
      fecha: '2026-09-22',
      enlace: 'https://news.un.org/es/',
      descarga: null,
      etiquetas: ['onu', 'naciones unidas', 'asamblea general', 'cumbres', 'multilateralismo'],
      destacado: true,
      ejemplo: true
    },
    {
      id: 'noticia-ejemplo-alto-el-fuego',
      tipo: 'noticia',
      titulo: 'Cómo se negocia un alto el fuego: los pasos habituales',
      resumen: 'Antes de un tratado de paz suele llegar un alto el fuego. Mediadores de terceros países ayudan a acordar dónde se detienen las tropas y quién vigila que se cumpla.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'BBC Mundo (portada)',
      fecha: '2026-09-18',
      enlace: 'https://www.bbc.com/mundo',
      descarga: null,
      etiquetas: ['alto el fuego', 'mediacion', 'tratados de paz', 'conflicto', 'negociacion'],
      destacado: true,
      ejemplo: true
    },
    {
      id: 'noticia-ejemplo-cumbre-g20',
      tipo: 'noticia',
      titulo: 'El G20: qué es y por qué sus cumbres importan',
      resumen: 'El G20 reúne a las mayores economías del mundo. En sus cumbres se habla de comercio, clima y deuda, y los líderes aprovechan para reunirse cara a cara.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'El País — Internacional (portada)',
      fecha: '2026-09-12',
      enlace: 'https://elpais.com/internacional/',
      descarga: null,
      etiquetas: ['g20', 'cumbres', 'economia', 'comercio', 'clima', 'geopolitica'],
      destacado: true,
      ejemplo: true
    },
    {
      id: 'noticia-ejemplo-embajadas',
      tipo: 'noticia',
      titulo: 'Por qué un país llama a consultas a su embajador',
      resumen: 'Cuando hay un desacuerdo serio, un gobierno puede pedir a su embajador que regrese temporalmente. Es una forma de mostrar molestia sin romper relaciones.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'DW Español (portada)',
      fecha: '2026-09-05',
      enlace: 'https://www.dw.com/es/',
      descarga: null,
      etiquetas: ['embajadas', 'embajador', 'crisis diplomatica', 'relaciones diplomaticas'],
      destacado: false,
      ejemplo: true
    },
    {
      id: 'noticia-ejemplo-clima',
      tipo: 'noticia',
      titulo: 'La diplomacia del clima: cómo se negocian los acuerdos ambientales',
      resumen: 'En las conferencias sobre cambio climático casi 200 países deben ponerse de acuerdo por consenso. Por eso las negociaciones suelen durar hasta la última noche.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'France 24 Español (portada)',
      fecha: '2026-08-28',
      enlace: 'https://www.france24.com/es/',
      descarga: null,
      etiquetas: ['clima', 'cambio climatico', 'cop', 'acuerdo de paris', 'multilateralismo', 'negociacion'],
      destacado: false,
      ejemplo: true
    },
    {
      id: 'noticia-ejemplo-sanciones',
      tipo: 'noticia',
      titulo: 'Sanciones económicas: qué son y para qué se usan',
      resumen: 'Las sanciones son castigos económicos, como prohibir el comercio o congelar cuentas, que un país o grupo de países aplica a otro para presionarlo sin usar la fuerza.',
      autor: 'Equipo Diplomacia Global',
      fuente: 'Noticias ONU (portada)',
      fecha: '2026-08-20',
      enlace: 'https://news.un.org/es/',
      descarga: null,
      etiquetas: ['sanciones', 'economia', 'consejo de seguridad', 'geopolitica', 'presion'],
      destacado: false,
      ejemplo: true
    }
  ];

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = CATALOGO;
  } else {
    raiz.CATALOGO_DIPLOMACIA = CATALOGO;
  }
})(typeof window !== 'undefined' ? window : globalThis);
