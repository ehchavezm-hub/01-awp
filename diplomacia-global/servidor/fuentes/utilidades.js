'use strict';

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

/** Quita etiquetas HTML/XML y decodifica entidades básicas. */
function limpiarTexto(texto) {
  return String(texto || '')
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    // Muchos feeds envían el HTML "escapado" (&lt;p&gt;): primero se recupera y luego se quita.
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Recorta un texto a un largo máximo sin cortar palabras. */
function recortar(texto, max = 280) {
  if (texto.length <= max) return texto;
  return texto.slice(0, texto.lastIndexOf(' ', max)) + '…';
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

/** Identificador corto y estable a partir de un texto (para ids de resultados externos). */
function idDesdeTexto(prefijo, texto) {
  let h = 0;
  for (const c of String(texto)) h = (Math.imul(31, h) + c.charCodeAt(0)) | 0;
  return `${prefijo}-${(h >>> 0).toString(36)}`;
}

module.exports = { traerConTiempo, limpiarTexto, recortar, crearCache, idDesdeTexto };
