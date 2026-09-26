/*
 * FUENTE: CROSSREF (papers académicos reales de revistas de prestigio)
 * La lógica común está en public/js/crossref.js (también la usa el navegador).
 */
'use strict';

const config = require('../config');
const Comun = require('../../public/js/crossref.js');
const { traerConTiempo } = require('./utilidades');

async function consultar(op) {
  const url = Comun.construirUrl({ ...op, correo: config.correoCrossref });
  const respuesta = await traerConTiempo(url, config.tiempoEsperaMs, {
    headers: { 'User-Agent': `DiplomaciaGlobal/1.0 (${config.correoCrossref || 'sin correo'})` }
  });
  const json = await respuesta.json();
  return ((json.message && json.message.items) || []).map(Comun.convertir);
}

module.exports = {
  nombre: 'Crossref',
  tipos: ['paper'],
  consultar,

  /** Papers de revistas de prestigio sobre un tema (Crossref necesita un tema). */
  async buscar(consulta) {
    if (!consulta) return [];
    return consultar({ consulta, filas: 10 });
  }
};
