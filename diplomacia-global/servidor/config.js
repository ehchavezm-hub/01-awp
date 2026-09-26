/*
 * CONFIGURACIÓN
 * Cada valor puede cambiarse con una variable de entorno, sin tocar el código.
 * Ejemplo (Mac/Linux):   PUERTO=8080 npm start
 * Ejemplo (Windows):     set PUERTO=8080 && npm start
 */
'use strict';

const path = require('path');

module.exports = {
  // Puerto donde se abre la aplicación: http://localhost:3000
  puerto: Number(process.env.PUERTO) || 3000,

  // "si" = intenta traer noticias y papers reales de internet (con respaldo local).
  // "no" = usa solo el catálogo de demostración (útil sin conexión).
  // También se desactiva con:  npm run sin-internet
  fuentesEnVivo: (process.env.FUENTES_EN_VIVO || 'si').toLowerCase() !== 'no' &&
    !process.argv.includes('--sin-internet'),

  // Segundos máximos de espera a una fuente externa antes de usar el respaldo.
  tiempoEsperaMs: (Number(process.env.TIEMPO_ESPERA_SEG) || 5) * 1000,

  // Minutos que se guardan en memoria las respuestas externas (evita repetir consultas).
  cacheMinutos: Number(process.env.CACHE_MINUTOS) || 15,

  // Correo opcional para Crossref (recomendado por ellos; da un servicio más estable).
  correoCrossref: process.env.CORREO_CROSSREF || '',

  // Las fuentes de noticias y revistas están en public/js/fuentes-prestigio.js

  // Carpetas
  carpetaPublica: path.join(__dirname, '..', 'public'),
  carpetaBiblioteca: process.env.CARPETA_BIBLIOTECA || path.join(__dirname, '..', 'biblioteca')
};
