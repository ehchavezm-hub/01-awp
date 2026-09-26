/*
 * FUENTE: CROSSREF (papers académicos reales)
 * API pública y gratuita: https://api.crossref.org  — no requiere clave.
 * Documentación: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
 */
'use strict';

const config = require('../config');
const { traerConTiempo, limpiarTexto, recortar, idDesdeTexto } = require('./utilidades');

// Palabras que se añaden a la consulta para mantener el tema (diplomacia / RR. II.).
const CONTEXTO = 'diplomacy international relations';

function construirUrl(consulta, filas = 10) {
  const params = new URLSearchParams({
    query: `${consulta} ${CONTEXTO}`,
    rows: String(filas),
    filter: 'type:journal-article',
    select: 'DOI,title,author,issued,container-title,abstract,link,license,URL'
  });
  if (config.correoCrossref) params.set('mailto', config.correoCrossref);
  return `https://api.crossref.org/works?${params}`;
}

/** Convierte un registro de Crossref al formato común de la aplicación. */
function convertir(item) {
  const autores = (item.author || [])
    .map((a) => [a.given, a.family].filter(Boolean).join(' ') || a.name)
    .filter(Boolean);
  const partesFecha = (item.issued && item.issued['date-parts'] && item.issued['date-parts'][0]) || [];
  const fecha = partesFecha.length
    ? partesFecha.map((n, i) => (i === 0 ? String(n) : String(n).padStart(2, '0'))).join('-')
    : '';

  // Solo se ofrece descarga si hay licencia abierta (Creative Commons) y un enlace PDF.
  const abierto = (item.license || []).some((l) => /creativecommons\.org/i.test(l.URL || ''));
  const pdf = (item.link || []).find((l) => /pdf/i.test(l['content-type'] || ''));

  const resumenOriginal = recortar(limpiarTexto(item.abstract || ''), 300);

  return {
    id: idDesdeTexto('crossref', item.DOI),
    tipo: 'paper',
    titulo: limpiarTexto((item.title || ['Sin título'])[0]),
    resumen: resumenOriginal || 'Artículo académico. Pulse “Visitar enlace original” para leer el resumen completo en la página de la revista.',
    autor: autores.length > 3 ? `${autores.slice(0, 3).join(', ')} y otros` : autores.join(', ') || 'Autor no indicado',
    fuente: limpiarTexto((item['container-title'] || ['Revista académica'])[0]),
    fecha,
    enlace: item.URL || `https://doi.org/${item.DOI}`,
    descarga: abierto && pdf ? { url: pdf.URL, formato: 'PDF', nombreArchivo: `${item.DOI.replace(/[^\w.-]+/g, '_')}.pdf` } : null,
    etiquetas: [],
    origen: 'Crossref'
  };
}

module.exports = {
  nombre: 'Crossref',
  tipos: ['paper'],
  construirUrl,
  convertir,

  /** Devuelve papers reales; si no hay consulta no hace nada (Crossref necesita un tema). */
  async buscar(consulta) {
    if (!consulta) return [];
    const respuesta = await traerConTiempo(construirUrl(consulta), config.tiempoEsperaMs, {
      headers: { 'User-Agent': `DiplomaciaGlobal/1.0 (${config.correoCrossref || 'sin correo'})` }
    });
    const json = await respuesta.json();
    return ((json.message && json.message.items) || []).map(convertir);
  }
};
