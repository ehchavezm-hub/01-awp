/*
 * NOVEDADES DE LA ÚLTIMA SEMANA
 * Reúne lo publicado en los últimos 7 días por las fuentes de prestigio
 * (public/js/fuentes-prestigio.js): noticias de organismos y medios de referencia,
 * y artículos de las revistas académicas más importantes de relaciones internacionales.
 *
 * Lo usan:
 *   - el servidor (ruta /api/semana), y
 *   - herramientas/actualizar-semana.js, que guarda el resultado en
 *     public/datos/ultima-semana.json para la versión publicada en internet.
 */
'use strict';

const noticiasRss = require('./fuentes/noticias-rss');
const crossref = require('./fuentes/crossref');
const Motor = require('../public/js/motor-busqueda.js');

const DIAS = 7;

function haceDias(dias, ahora = new Date()) {
  return new Date(ahora.getTime() - dias * 86400000);
}

/**
 * @param {{ahora?: Date, esperaMs?: number}} op
 * @returns {Promise<{generado: string, desde: string, dias: number, fuentes: Array, resultados: Array}>}
 */
async function obtenerSemana({ ahora = new Date(), esperaMs } = {}) {
  const desde = haceDias(DIAS, ahora);
  const informe = [];

  const { noticias, informe: informeRss } = await noticiasRss.leerTodos(esperaMs);
  informe.push(...informeRss);

  let papers = [];
  try {
    papers = await crossref.consultar({ desde: desde.toISOString().slice(0, 10), filas: 30 });
    informe.push({ fuente: 'Revistas académicas (Crossref)', ok: true, cantidad: papers.length });
  } catch (e) {
    informe.push({ fuente: 'Revistas académicas (Crossref)', ok: false, cantidad: 0 });
  }

  const recientes = [...noticias, ...papers].filter((d) => {
    const t = Date.parse(d.fecha);
    return !isNaN(t) && t >= desde.getTime() && t <= ahora.getTime() + 86400000;
  });

  // Sin duplicados (el mismo titular en dos medios) y de lo más nuevo a lo más antiguo.
  const vistos = new Set();
  const resultados = recientes
    .filter((d) => {
      const clave = Motor.normalizar(d.titulo);
      if (vistos.has(clave)) return false;
      vistos.add(clave);
      return true;
    })
    .sort((a, b) => Date.parse(b.fecha) - Date.parse(a.fecha));

  return {
    // Si ninguna fuente respondió, no hay datos: la página lo dirá con un mensaje amable.
    generado: informe.some((f) => f.ok) ? ahora.toISOString() : null,
    desde: desde.toISOString(),
    dias: DIAS,
    fuentes: informe,
    resultados
  };
}

module.exports = { obtenerSemana, DIAS };
