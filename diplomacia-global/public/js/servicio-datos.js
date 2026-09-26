/*
 * SERVICIO DE DATOS
 * Decide de dónde salen los resultados:
 *   1) Si la página se abrió desde el servidor (http://localhost:3000), pregunta a /api/buscar,
 *      que combina el catálogo, internet (noticias y papers reales) y su biblioteca personal.
 *   2) Si no hay servidor (por ejemplo, se abrió index.html con doble clic), usa el
 *      catálogo local de demostración. Así la aplicación nunca queda en blanco.
 */
(function (DG) {
  'use strict';

  var hayServidor = /^https?:$/.test(window.location.protocol);

  function buscarLocal(opciones) {
    return {
      resultados: window.MotorBusqueda.buscar(window.CATALOGO_DIPLOMACIA, opciones),
      avisos: [],
      modo: 'local'
    };
  }

  /**
   * @param {{consulta: string, tipo: string}} opciones
   * @returns {Promise<{resultados: Array, avisos: string[], modo: 'servidor'|'local'}>}
   */
  function buscar(opciones) {
    if (!hayServidor) return Promise.resolve(buscarLocal(opciones));

    var url = 'api/buscar?q=' + encodeURIComponent(opciones.consulta || '') +
              '&tipo=' + encodeURIComponent(opciones.tipo || 'todos');

    return fetch(url, { headers: { Accept: 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (datos) {
        return { resultados: datos.resultados, avisos: datos.avisos || [], modo: 'servidor' };
      })
      .catch(function () {
        // El servidor no está (por ejemplo, se publicó solo la carpeta public/).
        hayServidor = false;
        return buscarLocal(opciones);
      });
  }

  /** Dirección para descargar un documento con un clic. */
  function urlDescarga(doc) {
    if (!doc.descarga) return null;
    return hayServidor ? 'api/descargar/' + encodeURIComponent(doc.id) : doc.descarga.url;
  }

  DG.Datos = {
    buscar: buscar,
    urlDescarga: urlDescarga,
    hayServidor: function () { return hayServidor; }
  };
})(window.DG = window.DG || {});
