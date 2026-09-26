/*
 * MOTOR DE BÚSQUEDA
 * -----------------
 * Busca dentro de una lista de documentos y los ordena por relevancia.
 * - No distingue mayúsculas ni tildes ("guerra fria" encuentra "Guerra Fría").
 * - Entiende algunos sinónimos en español e inglés ("ONU" = "Naciones Unidas").
 * - Da más peso al título que al resumen.
 *
 * Se usa en el navegador (window.MotorBusqueda) y en el servidor (require).
 */
(function (raiz) {
  'use strict';

  var PALABRAS_VACIAS = [
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 'a',
    'y', 'o', 'e', 'en', 'con', 'por', 'para', 'sobre', 'que', 'se', 'su', 'sus',
    'lo', 'como', 'es', 'mas', 'the', 'of', 'and', 'in', 'on', 'to', 'for'
  ];

  // Grupos de palabras que significan lo mismo. Todas se buscan juntas.
  var SINONIMOS = [
    ['onu', 'naciones unidas', 'united nations'],
    ['guerra fria', 'cold war'],
    ['tratado', 'tratados', 'treaty', 'treaties', 'acuerdo', 'acuerdos'],
    ['paz', 'peace'],
    ['guerra', 'war', 'conflicto'],
    ['negociacion', 'negociaciones', 'negociar', 'negotiation', 'bargaining'],
    ['embajada', 'embajadas', 'embajador', 'embassy', 'embassies'],
    ['diplomacia', 'diplomacy', 'diplomatico', 'diplomatica'],
    ['realismo', 'realism', 'realista'],
    ['estados unidos', 'eeuu', 'ee uu', 'usa', 'norteamerica'],
    ['union sovietica', 'urss', 'soviet'],
    ['geopolitica', 'geopolitics'],
    ['clima', 'cambio climatico', 'climate']
  ];

  var PESOS = { titulo: 4, etiquetas: 3, autor: 3, fuente: 1, resumen: 1 };

  /** Pasa a minúsculas, quita tildes y signos. "¿Guerra Fría?" -> "guerra fria" */
  function normalizar(texto) {
    return String(texto || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9ñ\s-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Convierte la consulta en una lista de "conceptos". Cada concepto es una lista
   * de variantes equivalentes (por sinónimos). Un documento debe coincidir con
   * todos los conceptos para aparecer.
   */
  function interpretarConsulta(consulta) {
    var texto = ' ' + normalizar(consulta) + ' ';
    var conceptos = [];

    // 1) Primero, frases de varias palabras reconocidas como sinónimos.
    SINONIMOS.forEach(function (grupo) {
      grupo.forEach(function (variante) {
        if (variante.indexOf(' ') > -1 && texto.indexOf(' ' + variante + ' ') > -1) {
          conceptos.push(grupo.slice());
          texto = texto.split(' ' + variante + ' ').join(' ');
        }
      });
    });

    // 2) Luego, palabras sueltas.
    texto.split(' ').forEach(function (palabra) {
      if (!palabra || palabra.length < 2 || PALABRAS_VACIAS.indexOf(palabra) > -1) return;
      var grupo = SINONIMOS.filter(function (g) { return g.indexOf(palabra) > -1; })[0];
      conceptos.push(grupo ? grupo.slice() : [palabra]);
    });

    return conceptos;
  }

  function contiene(textoNormalizado, variante) {
    // Coincide al inicio de una palabra: "tratad" encuentra "tratados".
    return (' ' + textoNormalizado).indexOf(' ' + variante) > -1;
  }

  function puntuar(doc, conceptos) {
    var campos = {
      titulo: normalizar(doc.titulo),
      etiquetas: normalizar((doc.etiquetas || []).join(' ')),
      autor: normalizar(doc.autor),
      fuente: normalizar(doc.fuente),
      resumen: normalizar(doc.resumen)
    };
    var total = 0;
    for (var i = 0; i < conceptos.length; i++) {
      var mejor = 0;
      for (var campo in campos) {
        for (var j = 0; j < conceptos[i].length; j++) {
          if (contiene(campos[campo], conceptos[i][j])) mejor = Math.max(mejor, PESOS[campo]);
        }
      }
      if (mejor === 0) return 0; // Falta un concepto: no es relevante.
      total += mejor;
    }
    return total;
  }

  /** Convierte "1994", "1994-05" o "-0400" en un número para ordenar. */
  function valorFecha(fecha) {
    var t = Date.parse(fecha);
    if (!isNaN(t) && /^\d{4}-\d{2}/.test(fecha)) return t;
    var anio = parseInt(fecha, 10);
    return isNaN(anio) ? -Infinity : Date.UTC(0, 0, 1) + (anio - 1900) * 31557600000;
  }

  /**
   * Busca documentos.
   * @param {Array} documentos Lista de documentos (ver datos/catalogo.js).
   * @param {Object} opciones { consulta: "texto", tipo: "todos"|"noticia"|"paper"|"libro" }
   * @returns {Array} Documentos ordenados: primero los más relevantes y, a igualdad, los más recientes.
   */
  function buscar(documentos, opciones) {
    opciones = opciones || {};
    var tipo = opciones.tipo || 'todos';
    var conceptos = interpretarConsulta(opciones.consulta || '');

    return documentos
      .filter(function (d) { return tipo === 'todos' || d.tipo === tipo; })
      .map(function (d) { return { doc: d, puntos: conceptos.length ? puntuar(d, conceptos) : 1 }; })
      .filter(function (r) { return r.puntos > 0; })
      .sort(function (a, b) {
        return (b.puntos - a.puntos) || (valorFecha(b.doc.fecha) - valorFecha(a.doc.fecha));
      })
      .map(function (r) { return r.doc; });
  }

  var MotorBusqueda = {
    normalizar: normalizar,
    interpretarConsulta: interpretarConsulta,
    buscar: buscar,
    valorFecha: valorFecha
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = MotorBusqueda;
  } else {
    raiz.MotorBusqueda = MotorBusqueda;
  }
})(typeof window !== 'undefined' ? window : globalThis);
