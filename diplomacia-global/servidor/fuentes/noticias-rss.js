/*
 * FUENTE: NOTICIAS POR RSS (titulares reales)
 * Lee los "feeds" RSS configurados en servidor/config.js (por defecto, Noticias ONU en español).
 * Para agregar otro medio, añada { nombre, url } a config.feedsNoticias.
 */
'use strict';

const config = require('../config');
const { traerConTiempo, limpiarTexto, recortar, idDesdeTexto } = require('./utilidades');

function etiqueta(xml, nombre) {
  const m = xml.match(new RegExp(`<${nombre}[^>]*>([\\s\\S]*?)</${nombre}>`, 'i'));
  return m ? limpiarTexto(m[1]) : '';
}

/** Convierte el texto XML de un feed RSS en noticias con el formato común. */
function interpretarRss(xml, nombreFuente) {
  const items = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || [];
  return items.map((item) => {
    const enlace = etiqueta(item, 'link') || etiqueta(item, 'guid');
    const fechaTexto = etiqueta(item, 'pubDate') || etiqueta(item, 'dc:date');
    const fecha = fechaTexto && !isNaN(Date.parse(fechaTexto))
      ? new Date(fechaTexto).toISOString().slice(0, 10)
      : '';
    return {
      id: idDesdeTexto('rss', enlace || etiqueta(item, 'title')),
      tipo: 'noticia',
      titulo: etiqueta(item, 'title'),
      resumen: recortar(etiqueta(item, 'description'), 280),
      autor: etiqueta(item, 'dc:creator') || nombreFuente,
      fuente: nombreFuente,
      fecha,
      enlace,
      descarga: null,
      etiquetas: [],
      origen: 'RSS'
    };
  }).filter((n) => n.titulo && n.enlace);
}

module.exports = {
  nombre: 'Noticias RSS',
  tipos: ['noticia'],
  interpretarRss,

  async buscar() {
    const resultados = await Promise.allSettled(
      config.feedsNoticias.map(async (feed) => {
        const r = await traerConTiempo(feed.url, config.tiempoEsperaMs);
        return interpretarRss(await r.text(), feed.nombre);
      })
    );
    const noticias = resultados.filter((r) => r.status === 'fulfilled').flatMap((r) => r.value);
    if (!noticias.length && resultados.length) throw new Error('Ningún feed de noticias respondió');
    return noticias;
  }
};
