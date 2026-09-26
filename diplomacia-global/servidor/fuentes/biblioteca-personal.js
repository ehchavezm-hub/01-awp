/*
 * FUENTE: MI BIBLIOTECA PERSONAL
 * Busca DENTRO de los libros que usted guarde en la carpeta "biblioteca/"
 * (archivos .md o .txt) y muestra los párrafos donde aparece lo que busca.
 *
 * - Los textos NUNCA se publican ni se descargan desde la aplicación: solo se
 *   muestran fragmentos breves en su propia computadora.
 * - Opcional: "biblioteca/libros.json" asigna título, autor y año a cada archivo.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const config = require('../config');
const { normalizar, interpretarConsulta } = require('../../public/js/motor-busqueda.js');
const { recortar, idDesdeTexto } = require('./utilidades');

const MAX_POR_LIBRO = 3;
const MAX_TOTAL = 6;
const indices = new Map(); // archivo -> { modificado, libro }

function leerMetadatos() {
  try {
    return JSON.parse(fs.readFileSync(path.join(config.carpetaBiblioteca, 'libros.json'), 'utf8'));
  } catch {
    return {};
  }
}

function metadatosDe(archivo, todos) {
  const clave = Object.keys(todos).find((k) => archivo.includes(k));
  if (clave) return todos[clave];
  return { titulo: path.basename(archivo, path.extname(archivo)).replace(/^\d+-/, '').replace(/[_-]+/g, ' ') };
}

/** "CAPÍTULO TREINTA " -> "Capítulo treinta" */
function formatearCapitulo(texto) {
  const t = texto.trim();
  if (t !== t.toUpperCase()) return t;
  return t.charAt(0) + t.slice(1).toLowerCase();
}

/** Detecta entradas de bibliografía: "Apellido, Nombre, Título (Editorial, 1999)". */
function pareceBibliografia(linea) {
  return /^[A-ZÁÉÍÓÚÑ][\w'’-]+, [A-ZÁÉÍÓÚÑ][\w.'’-]*[ ,.]/.test(linea) && /\b(1[5-9]|20)\d{2}\b/.test(linea);
}

/** Divide un libro en párrafos útiles y recuerda en qué capítulo está cada uno. */
function indexarTexto(texto) {
  const lineas = texto.split(/\r?\n/);
  const parrafos = [];
  let capitulo = '';
  let esperandoTituloCapitulo = false;

  for (const linea of lineas) {
    // Se quitan caracteres invisibles que dejan algunas conversiones de libros electrónicos.
    const l = linea.replace(/[\uE000-\uF8FF\u200B-\u200D\uFEFF]/g, '').trim();
    if (!l) continue;
    if (/^#{1,3}\s/.test(l)) {
      capitulo = formatearCapitulo(l.replace(/^#+\s*/, '').replace(/\*/g, ''));
      esperandoTituloCapitulo = /^cap[ií]tulo\b/i.test(capitulo);
      continue;
    }
    if (esperandoTituloCapitulo && l.length < 140) {
      capitulo += ': ' + l.replace(/\*/g, '');
      esperandoTituloCapitulo = false;
      continue;
    }
    esperandoTituloCapitulo = false;
    // Se ignoran líneas cortas, imágenes, enlaces del índice, comentarios y bibliografía.
    if (l.length < 120 || /^(!\[|\[|<!--)/.test(l) || pareceBibliografia(l)) continue;
    if (/^(notas|bibliograf|referencias|further reading|notes|index)/i.test(capitulo)) continue;
    parrafos.push({ texto: l.replace(/\*/g, ''), normal: ' ' + normalizar(l), capitulo });
  }
  return parrafos;
}

function listarArchivos() {
  try {
    return fs.readdirSync(config.carpetaBiblioteca)
      .filter((f) => /\.(md|txt)$/i.test(f) && !/^leeme/i.test(f))
      .map((f) => path.join(config.carpetaBiblioteca, f));
  } catch {
    return [];
  }
}

function obtenerIndice(archivo) {
  const modificado = fs.statSync(archivo).mtimeMs;
  const guardado = indices.get(archivo);
  if (guardado && guardado.modificado === modificado) return guardado.parrafos;
  const parrafos = indexarTexto(fs.readFileSync(archivo, 'utf8'));
  indices.set(archivo, { modificado, parrafos });
  return parrafos;
}

const VARIANTES_LETRA = { a: '[aáàâä]', e: '[eéèêë]', i: '[iíìîï]', o: '[oóòôö]', u: '[uúùûü]', n: '[nñ]' };

/** Expresión que encuentra una palabra en el texto original sin importar tildes ni mayúsculas. */
function patronFlexible(variante) {
  const cuerpo = variante.split('').map((c) => {
    if (c === ' ') return '[\\s\\W]+';
    return VARIANTES_LETRA[c] || c.replace(/[.*+?^${}()|[\]\\-]/g, '\\$&');
  }).join('');
  return new RegExp('(^|[^\\p{L}])' + cuerpo, 'iu');
}

/** Recorta el párrafo alrededor de la primera coincidencia. */
function extracto(parrafo, variantes) {
  const posiciones = variantes
    .map((v) => parrafo.texto.search(patronFlexible(v)))
    .filter((i) => i >= 0);
  const pos = posiciones.length ? Math.min(...posiciones) : 0;
  if (pos < 120) return recortar(parrafo.texto, 320);
  const desde = parrafo.texto.lastIndexOf(' ', pos - 80) + 1;
  return '…' + recortar(parrafo.texto.slice(desde), 320);
}

function buscarEnTexto(parrafos, conceptos) {
  const encontrados = [];
  parrafos.forEach((p, posicion) => {
    let puntos = 0;
    for (const variantes of conceptos) {
      const veces = variantes.reduce((n, v) => n + (p.normal.split(' ' + v).length - 1), 0);
      if (!veces) return;
      puntos += veces;
    }
    encontrados.push({ p, posicion, puntos });
  });
  return encontrados.sort((a, b) => b.puntos - a.puntos);
}

module.exports = {
  nombre: 'Mi biblioteca',
  tipos: ['libro'],
  indexarTexto,

  async buscar(consulta) {
    const conceptos = interpretarConsulta(consulta);
    if (!conceptos.length) return [];
    const metadatos = leerMetadatos();
    const resultados = [];

    for (const archivo of listarArchivos()) {
      const meta = metadatosDe(path.basename(archivo), metadatos);
      const parrafos = obtenerIndice(archivo);
      const todasLasVariantes = conceptos.flat();
      for (const { p, posicion } of buscarEnTexto(parrafos, conceptos).slice(0, MAX_POR_LIBRO)) {
        const porcentaje = Math.max(1, Math.round((posicion / parrafos.length) * 100));
        resultados.push({
          id: idDesdeTexto('bib', archivo + posicion),
          tipo: 'libro',
          titulo: meta.titulo,
          capitulo: p.capitulo || '',
          ubicacion: `Aproximadamente al ${porcentaje} % del libro`,
          resumen: extracto(p, todasLasVariantes),
          autor: meta.autor || 'Autor no indicado',
          fuente: 'Mi biblioteca personal',
          fecha: meta.fecha || '',
          enlace: meta.enlace || null,
          descarga: null,
          etiquetas: [],
          fragmento: true,
          origen: 'Biblioteca'
        });
      }
    }
    return resultados.slice(0, MAX_TOTAL);
  }
};
