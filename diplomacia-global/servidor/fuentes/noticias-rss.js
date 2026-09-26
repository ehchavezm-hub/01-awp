/*
 * FUENTE: NOTICIAS POR RSS (titulares reales de fuentes de prestigio)
 * Lee los medios de public/js/fuentes-prestigio.js. Entiende RSS y Atom.
 * De los medios generales solo toma las noticias sobre temas internacionales.
 */
'use strict';

const config = require('../config');
const Fuentes = require('../../public/js/fuentes-prestigio.js');
const { traerConTiempo, limpiarTexto, recortar, idDesdeTexto } = require('./utilidades');

const MAX_POR_MEDIO = 15;

function etiqueta(xml, nombre) {
  const m = xml.match(new RegExp(`<${nombre}(?:\\s[^>]*)?>([\\s\\S]*?)</${nombre}>`, 'i'));
  return m ? limpiarTexto(m[1]) : '';
}

function enlaceAtom(xml) {
  const alterno = xml.match(/<link[^>]*rel=["']alternate["'][^>]*href=["']([^"']+)["']/i) ||
                  xml.match(/<link[^>]*href=["']([^"']+)["']/i);
  return alterno ? alterno[1] : '';
}

function aFecha(texto) {
  const t = Date.parse(texto);
  return isNaN(t) ? '' : new Date(t).toISOString();
}

/**
 * Convierte el XML de un feed (RSS o Atom) en noticias con el formato común.
 * @param {string} xml
 * @param {Object|string} medio  Objeto de fuentes-prestigio.js o solo el nombre.
 */
function interpretarRss(xml, medio) {
  if (typeof medio === 'string') medio = { nombre: medio, especializado: true };
  const bloques = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || xml.match(/<entry[\s>][\s\S]*?<\/entry>/gi) || [];

  return bloques.map((b) => {
    const enlace = etiqueta(b, 'link') || enlaceAtom(b) || etiqueta(b, 'guid');
    const titulo = etiqueta(b, 'title');
    const resumen = recortar(etiqueta(b, 'description') || etiqueta(b, 'summary') || etiqueta(b, 'content'), 280);
    return {
      id: idDesdeTexto('rss', enlace || titulo),
      tipo: 'noticia',
      titulo,
      resumen,
      autor: etiqueta(b, 'dc:creator') || etiqueta(b, 'name') || medio.nombre,
      fuente: medio.nombre,
      tipoFuente: medio.tipoFuente || 'Medio de referencia',
      idioma: medio.idioma || 'es',
      fecha: aFecha(etiqueta(b, 'pubDate') || etiqueta(b, 'dc:date') || etiqueta(b, 'published') || etiqueta(b, 'updated')),
      enlace,
      descarga: null,
      etiquetas: [],
      origen: 'RSS'
    };
  })
    .filter((n) => n.titulo && /^https?:\/\//.test(n.enlace))
    .filter((n) => medio.especializado || Fuentes.esRelevante(n.titulo, n.resumen))
    .slice(0, MAX_POR_MEDIO);
}

/** Lee todos los medios. Devuelve noticias y un informe de qué fuente respondió. */
async function leerTodos(ms = config.tiempoEsperaMs) {
  const resultados = await Promise.allSettled(
    Fuentes.medios.map(async (medio) => {
      const r = await traerConTiempo(medio.url, ms, {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; DiplomaciaGlobal/1.0)' }
      });
      return interpretarRss(await r.text(), medio);
    })
  );
  const informe = resultados.map((r, i) => ({
    fuente: Fuentes.medios[i].nombre,
    ok: r.status === 'fulfilled',
    cantidad: r.status === 'fulfilled' ? r.value.length : 0
  }));
  const noticias = resultados.filter((r) => r.status === 'fulfilled').flatMap((r) => r.value);
  return { noticias, informe };
}

module.exports = {
  nombre: 'Noticias de prestigio',
  tipos: ['noticia'],
  interpretarRss,
  leerTodos,

  async buscar() {
    const { noticias, informe } = await leerTodos();
    if (!noticias.length && informe.length) throw new Error('Ningún medio respondió');
    return noticias;
  }
};
