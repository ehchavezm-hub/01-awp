'use strict';

const { limpiarTexto, recortar, idDesdeTexto } = require('../../public/js/crossref.js');

/** fetch con tiempo máximo de espera. Lanza un error si se agota. */
async function traerConTiempo(url, ms, opciones = {}) {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), ms);
  try {
    const respuesta = await fetch(url, { ...opciones, signal: control.signal });
    if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status} en ${url}`);
    return respuesta;
  } finally {
    clearTimeout(temporizador);
  }
}

/** Caché sencilla en memoria con vencimiento. */
function crearCache(minutos) {
  const datos = new Map();
  return {
    obtener(clave) {
      const e = datos.get(clave);
      if (e && e.vence > Date.now()) return e.valor;
      datos.delete(clave);
      return undefined;
    },
    guardar(clave, valor) {
      datos.set(clave, { valor, vence: Date.now() + minutos * 60000 });
    }
  };
}

module.exports = { traerConTiempo, limpiarTexto, recortar, crearCache, idDesdeTexto };
