/*
 * FUENTES DE PRESTIGIO
 * --------------------
 * Única lista de medios, organismos y revistas académicas que usa la aplicación
 * para "Novedades de la última semana" y para buscar papers en internet.
 * Solo se muestran resultados de estas fuentes.
 *
 * - medios: fuentes RSS de organismos internacionales, centros de análisis y
 *   periódicos de referencia mundial.
 *     especializado: true  -> todo su contenido trata de política internacional.
 *     especializado: false -> medio general: solo se toman las noticias que
 *                             mencionan temas diplomáticos (ver PALABRAS_CLAVE).
 * - revistas: revistas académicas de relaciones internacionales de mayor impacto
 *   (se consultan en Crossref por su ISSN).
 *
 * Para añadir una fuente, copie una línea y cambie sus datos.
 * Se usa en el navegador (window.FuentesPrestigio) y en Node.js (require).
 */
(function (raiz) {
  'use strict';

  var medios = [
    // Organismos internacionales
    { id: 'onu-es', nombre: 'Noticias ONU', tipoFuente: 'Organismo internacional', idioma: 'es', especializado: true,
      url: 'https://news.un.org/feed/subscribe/es/news/all/rss.xml' },
    { id: 'onu-paz', nombre: 'UN News — Paz y seguridad', tipoFuente: 'Organismo internacional', idioma: 'en', especializado: true,
      url: 'https://news.un.org/feed/subscribe/en/news/topic/peace-and-security/feed/rss.xml' },

    // Revistas y centros de análisis de política exterior
    { id: 'foreign-affairs', nombre: 'Foreign Affairs', tipoFuente: 'Revista de política exterior', idioma: 'en', especializado: true,
      url: 'https://www.foreignaffairs.com/rss.xml' },
    { id: 'foreign-policy', nombre: 'Foreign Policy', tipoFuente: 'Revista de política exterior', idioma: 'en', especializado: true,
      url: 'https://foreignpolicy.com/feed/' },
    { id: 'the-diplomat', nombre: 'The Diplomat', tipoFuente: 'Revista de política exterior', idioma: 'en', especializado: true,
      url: 'https://thediplomat.com/feed/' },
    { id: 'crisis-group', nombre: 'International Crisis Group', tipoFuente: 'Centro de análisis', idioma: 'en', especializado: true,
      url: 'https://www.crisisgroup.org/rss.xml' },
    { id: 'brookings', nombre: 'Brookings Institution', tipoFuente: 'Centro de análisis', idioma: 'en', especializado: false,
      url: 'https://www.brookings.edu/feed/' },

    // Periódicos y cadenas de referencia mundial
    { id: 'bbc-mundo', nombre: 'BBC Mundo', tipoFuente: 'Medio de referencia', idioma: 'es', especializado: false,
      url: 'https://feeds.bbci.co.uk/mundo/rss.xml' },
    { id: 'el-pais', nombre: 'El País — Internacional', tipoFuente: 'Medio de referencia', idioma: 'es', especializado: false,
      url: 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada' },
    { id: 'france24-es', nombre: 'France 24 Español', tipoFuente: 'Medio de referencia', idioma: 'es', especializado: false,
      url: 'https://www.france24.com/es/rss' },
    { id: 'dw-es', nombre: 'DW Español', tipoFuente: 'Medio de referencia', idioma: 'es', especializado: false,
      url: 'https://rss.dw.com/xml/rss-sp-all' },
    { id: 'bbc-world', nombre: 'BBC News — World', tipoFuente: 'Medio de referencia', idioma: 'en', especializado: false,
      url: 'https://feeds.bbci.co.uk/news/world/rss.xml' },
    { id: 'guardian', nombre: 'The Guardian — World', tipoFuente: 'Medio de referencia', idioma: 'en', especializado: false,
      url: 'https://www.theguardian.com/world/rss' },
    { id: 'nyt', nombre: 'The New York Times — World', tipoFuente: 'Medio de referencia', idioma: 'en', especializado: false,
      url: 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml' },
    { id: 'al-jazeera', nombre: 'Al Jazeera', tipoFuente: 'Medio de referencia', idioma: 'en', especializado: false,
      url: 'https://www.aljazeera.com/xml/rss/all.xml' }
  ];

  var revistas = [
    { nombre: 'International Organization', issn: '0020-8183' },
    { nombre: 'International Security', issn: '0162-2889' },
    { nombre: 'World Politics', issn: '0043-8871' },
    { nombre: 'Foreign Affairs', issn: '0015-7120' },
    { nombre: 'International Affairs', issn: '0020-5850' },
    { nombre: 'International Studies Quarterly', issn: '0020-8833' },
    { nombre: 'Journal of Conflict Resolution', issn: '0022-0027' },
    { nombre: 'Journal of Peace Research', issn: '0022-3433' },
    { nombre: 'European Journal of International Relations', issn: '1354-0661' },
    { nombre: 'Review of International Studies', issn: '0260-2105' },
    { nombre: 'Survival', issn: '0039-6338' },
    { nombre: 'Diplomacy & Statecraft', issn: '0959-2296' },
    { nombre: 'The Hague Journal of Diplomacy', issn: '1871-1901' }
  ];

  // Temas que hacen "relevante" una noticia de un medio general (sin tildes, en minúsculas).
  // Cada término busca el comienzo de una palabra ("diplomac" = diplomacia, diplomático…);
  // si termina en espacio, debe ser la palabra exacta ("war " no encuentra "warning").
  var PALABRAS_CLAVE = [
    'diplomac', 'diplomat', 'embajad', 'embass', 'ambassador', 'canciller', 'cancilleria',
    'ministro de exteriores', 'ministra de exteriores', 'ministro de relaciones exteriores',
    'foreign minister', 'foreign secretary', 'secretary of state', 'foreign policy', 'politica exterior',
    'cumbre', 'summit', 'tratado', 'treaty', 'acuerdo de paz', 'peace deal', 'peace talks',
    'negociacion', 'negociaciones', 'negotiat', 'talks ', 'dialogo', 'mediacion', 'mediat',
    'alto el fuego', 'tregua', 'ceasefire', 'truce', 'sancion', 'sanction', 'aranceles', 'tariff',
    'onu ', 'naciones unidas', 'united nations', 'consejo de seguridad', 'security council',
    'otan ', 'nato ', 'g7 ', 'g20 ', 'brics ', 'union europea', 'european union', 'oea ', 'asean ',
    'geopolit', 'relaciones internacionales', 'international relations', 'bilateral', 'multilateral',
    'conflicto', 'conflict', 'guerra', 'war ', 'wars ', 'invasion', 'refugiad', 'refugee', 'derechos humanos',
    'human rights', 'nuclear', 'desarme', 'disarmament', 'frontera', 'border', 'soberan', 'sovereign'
  ];

  function sinTildes(texto) {
    return String(texto || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  /** ¿La noticia de un medio general trata un tema diplomático o internacional? */
  function esRelevante(titulo, resumen) {
    var texto = ' ' + sinTildes(titulo + ' ' + resumen).replace(/[^a-z0-9ñ]+/g, ' ') + ' ';
    return PALABRAS_CLAVE.some(function (p) { return texto.indexOf(' ' + p) > -1; });
  }

  var FuentesPrestigio = { medios: medios, revistas: revistas, PALABRAS_CLAVE: PALABRAS_CLAVE, esRelevante: esRelevante };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = FuentesPrestigio;
  } else {
    raiz.FuentesPrestigio = FuentesPrestigio;
  }
})(typeof window !== 'undefined' ? window : globalThis);
