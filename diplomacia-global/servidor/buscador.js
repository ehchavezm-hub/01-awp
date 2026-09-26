/*
 * BUSCADOR CENTRAL
 * Reúne los resultados de todas las fuentes, quita duplicados y los ordena.
 *
 * Para conectar una base de datos real en el futuro, cree un archivo en
 * servidor/fuentes/ con esta forma y agréguelo a la lista FUENTES_EN_VIVO:
 *
 *   module.exports = {
 *     nombre: 'Mi fuente',
 *     tipos: ['paper'],                 // qué tipos de contenido entrega
 *     async buscar(consulta) { return [ ...documentos con el formato común... ]; }
 *   };
 */
'use strict';

const config = require('./config');
const Motor = require('../public/js/motor-busqueda.js');
const { crearCache } = require('./fuentes/utilidades');
const catalogoLocal = require('./fuentes/catalogo-local');
const crossref = require('./fuentes/crossref');
const noticiasRss = require('./fuentes/noticias-rss');
const bibliotecaPersonal = require('./fuentes/biblioteca-personal');

const FUENTES_EN_VIVO = [noticiasRss, crossref];
const cache = crearCache(config.cacheMinutos);

// Resultados externos recientes, para poder descargarlos por su id.
const vistos = new Map();

async function consultarFuente(fuente, consulta) {
  const clave = `${fuente.nombre}|${consulta}`;
  const enCache = cache.obtener(clave);
  if (enCache) return enCache;
  const docs = await fuente.buscar(consulta);
  cache.guardar(clave, docs);
  return docs;
}

/**
 * @param {{consulta?: string, tipo?: string, limite?: number}} opciones
 * @returns {Promise<{resultados: Array, avisos: string[]}>}
 */
async function buscar({ consulta = '', tipo = 'todos', limite = 30 } = {}) {
  const avisos = [];
  const quiere = (t) => tipo === 'todos' || tipo === t;

  // 1) Catálogo local: siempre.
  const locales = Motor.buscar(await catalogoLocal.buscar(), { consulta, tipo });

  // 2) Biblioteca personal: solo si hay texto que buscar.
  let biblioteca = [];
  if (consulta && quiere('libro')) {
    try {
      biblioteca = await bibliotecaPersonal.buscar(consulta);
    } catch (e) {
      avisos.push('No se pudo leer la biblioteca personal.');
    }
  }

  // 3) Fuentes de internet: en paralelo, con respaldo si fallan.
  let externos = [];
  if (config.fuentesEnVivo) {
    const activas = FUENTES_EN_VIVO.filter((f) => f.tipos.some(quiere));
    const respuestas = await Promise.allSettled(activas.map((f) => consultarFuente(f, consulta)));
    respuestas.forEach((r, i) => {
      if (r.status === 'fulfilled') {
        // Las noticias RSS llegan todas; se filtran aquí por la consulta.
        const docs = activas[i] === noticiasRss ? Motor.buscar(r.value, { consulta }) : r.value;
        externos.push(...docs);
      } else {
        avisos.push(`${activas[i].nombre} no respondió; se muestran datos de respaldo.`);
      }
    });
  }

  externos.forEach((d) => vistos.set(d.id, d));

  // Orden: noticias reales más recientes primero; luego fragmentos de su biblioteca;
  // luego el catálogo; por último papers externos.
  const noticiasReales = externos.filter((d) => d.tipo === 'noticia');
  const papersExternos = externos.filter((d) => d.tipo === 'paper');
  // Si hay noticias reales, las noticias de ejemplo se ocultan.
  const localesFiltrados = noticiasReales.length ? locales.filter((d) => !d.ejemplo) : locales;

  const todos = [...noticiasReales, ...biblioteca, ...localesFiltrados, ...papersExternos];
  const unicos = [];
  const titulos = new Set();
  for (const d of todos) {
    const clave = Motor.normalizar(d.titulo) + '|' + (d.capitulo || d.id);
    if (titulos.has(clave)) continue;
    titulos.add(clave);
    unicos.push(d);
  }
  return { resultados: unicos.slice(0, limite), avisos };
}

/** Busca un documento por id (catálogo local o resultados externos vistos). */
function obtenerPorId(id) {
  return catalogoLocal.obtenerPorId(id) || vistos.get(id) || null;
}

module.exports = { buscar, obtenerPorId };
