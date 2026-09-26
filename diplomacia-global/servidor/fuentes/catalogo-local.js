/*
 * FUENTE: CATÁLOGO LOCAL
 * Los mismos datos de demostración que usa el navegador (public/datos/catalogo.js).
 * Siempre está disponible y sirve de respaldo cuando internet falla.
 */
'use strict';

const catalogo = require('../../public/datos/catalogo.js');

module.exports = {
  nombre: 'Catálogo local',
  tipos: ['noticia', 'paper', 'libro'],

  async buscar() {
    return catalogo;
  },

  obtenerPorId(id) {
    return catalogo.find((d) => d.id === id) || null;
  }
};
