/*
 * SERVICIO DE DATOS
 * Decide de dónde salen los resultados. Hay tres formas de abrir la aplicación:
 *
 *   'servidor'  Con "npm start" (http://localhost:3000). Pregunta a /api/buscar y /api/semana.
 *   'web'       Publicada en internet como página estática (GitHub Pages). Usa:
 *                 - el catálogo local,
 *                 - datos/ultima-semana.json (lo actualiza GitHub Actions varias veces al día),
 *                 - Crossref directamente desde el navegador para papers de revistas de prestigio.
 *   'archivo'   Abriendo index.html con doble clic. Solo el catálogo local.
 *
 * La persona usuaria nunca ve estos detalles técnicos.
 */
(function (DG) {
  'use strict';

  var modoPromesa = null;
  var semanaPromesa = null;

  /** Conexión con tiempo máximo de espera. */
  function traer(url, ms) {
    var control = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var t = setTimeout(function () { if (control) control.abort(); }, ms || 8000);
    return fetch(url, control ? { signal: control.signal, headers: { Accept: 'application/json' } } : {})
      .then(function (r) {
        clearTimeout(t);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }, function (e) { clearTimeout(t); throw e; });
  }

  function modo() {
    if (!modoPromesa) {
      modoPromesa = !/^https?:$/.test(window.location.protocol)
        ? Promise.resolve('archivo')
        : traer('api/estado', 3000)
          .then(function (d) { return d && d.ok ? 'servidor' : 'web'; })
          .catch(function () { return 'web'; });
    }
    return modoPromesa;
  }

  /* ----------------------- Novedades de la semana ----------------------- */

  /**
   * @returns {Promise<{generado: string|null, dias: number, fuentes: Array, resultados: Array}>}
   */
  function datosSemana() {
    if (!semanaPromesa) {
      semanaPromesa = modo().then(function (m) {
        if (m === 'archivo') return null;
        return traer(m === 'servidor' ? 'api/semana' : 'datos/ultima-semana.json', 20000);
      }).catch(function () { return null; }).then(function (d) {
        return d || { generado: null, dias: 7, fuentes: [], resultados: [] };
      });
    }
    return semanaPromesa;
  }

  /**
   * Novedades de los últimos 7 días, opcionalmente filtradas por tema e idioma.
   * @param {{consulta?: string, idioma?: 'todos'|'es', ahora?: Date}} op
   */
  function semana(op) {
    op = op || {};
    return datosSemana().then(function (d) {
      var ahora = op.ahora || new Date();
      var limite = ahora.getTime() - (d.dias || 7) * 86400000;
      var lista = d.resultados.filter(function (x) {
        var t = Date.parse(x.fecha);
        return !isNaN(t) && t >= limite;
      });
      if (op.idioma === 'es') lista = lista.filter(function (x) { return x.idioma === 'es'; });
      if (op.consulta) lista = window.MotorBusqueda.buscar(lista, { consulta: op.consulta });
      return { generado: d.generado, dias: d.dias || 7, fuentes: d.fuentes, resultados: lista };
    });
  }

  /* ------------------------------ Búsqueda ------------------------------ */

  function buscarCrossref(consulta) {
    return traer(window.Crossref.construirUrl({ consulta: consulta, filas: 10 }), 8000)
      .then(function (j) { return ((j.message && j.message.items) || []).map(window.Crossref.convertir); })
      .catch(function () { return []; });
  }

  function buscarSinServidor(opciones, m) {
    var tipo = opciones.tipo || 'todos';
    var consulta = opciones.consulta || '';
    var quierePapers = consulta && m === 'web' && (tipo === 'todos' || tipo === 'paper');

    return Promise.all([datosSemana(), quierePapers ? buscarCrossref(consulta) : Promise.resolve([])])
      .then(function (r) {
        var recientes = r[0].resultados;
        var hayNoticiasReales = recientes.some(function (d) { return d.tipo === 'noticia'; });
        // Con noticias reales disponibles, las noticias de ejemplo del catálogo se ocultan.
        var catalogo = window.CATALOGO_DIPLOMACIA.filter(function (d) { return !(hayNoticiasReales && d.ejemplo); });
        var locales = window.MotorBusqueda.buscar(recientes.concat(catalogo), opciones);
        var titulos = {};
        locales.forEach(function (d) { titulos[window.MotorBusqueda.normalizar(d.titulo)] = true; });
        var papers = r[1].filter(function (d) { return !titulos[window.MotorBusqueda.normalizar(d.titulo)]; });
        return { resultados: locales.concat(papers), avisos: [], modo: m };
      });
  }

  /**
   * @param {{consulta: string, tipo: string}} opciones
   * @returns {Promise<{resultados: Array, avisos: string[], modo: string}>}
   */
  function buscar(opciones) {
    return modo().then(function (m) {
      if (m !== 'servidor') return buscarSinServidor(opciones, m);
      var url = 'api/buscar?q=' + encodeURIComponent(opciones.consulta || '') +
                '&tipo=' + encodeURIComponent(opciones.tipo || 'todos');
      return traer(url, 20000)
        .then(function (d) { return { resultados: d.resultados, avisos: d.avisos || [], modo: m }; })
        .catch(function () { return buscarSinServidor(opciones, 'web'); });
    });
  }

  var modoActual = null;
  modo().then(function (m) { modoActual = m; });

  /** Dirección para descargar un documento con un clic. */
  function urlDescarga(doc) {
    if (!doc.descarga) return null;
    return modoActual === 'servidor' ? 'api/descargar/' + encodeURIComponent(doc.id) : doc.descarga.url;
  }

  DG.Datos = {
    modo: modo,
    buscar: buscar,
    semana: semana,
    urlDescarga: urlDescarga,
    hayServidor: function () { return modoActual === 'servidor'; }
  };
})(window.DG = window.DG || {});
