/*
 * APLICACIÓN PRINCIPAL
 * Une todas las piezas: menú, buscador, filtros, voz, tamaño de letra y ayuda.
 */
(function (DG) {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var SECCIONES = ['buscar', 'noticias', 'papers', 'libros'];
  var TIPO_DE_SECCION = { noticias: 'noticia', papers: 'paper', libros: 'libro' };
  var NOMBRE_TIPO = { todos: '', noticia: ' en Noticias', paper: ' en Papers', libro: ' en Libros' };
  var cargadas = {};

  var acciones = {
    alDescargar: function () {
      DG.Interfaz.avisar('¡Descarga iniciada con éxito! Encontrará el archivo en su carpeta «Descargas».');
    },
    alCompartir: function () {
      DG.Interfaz.avisar('Abriendo WhatsApp… elija a quién enviarlo.');
    }
  };

  /* ------------------------ Avisos de las fuentes ------------------------ */
  function mostrarAvisoModo(respuesta) {
    var aviso = $('aviso-modo');
    if (respuesta.modo === 'local') {
      aviso.textContent = 'Está viendo el catálogo de demostración (sin conexión al servidor). Para ver noticias reales, inicie la aplicación con «npm start».';
      aviso.hidden = false;
    } else if (respuesta.avisos.length) {
      aviso.textContent = 'Algunas fuentes de internet no respondieron en este momento. Le mostramos nuestro catálogo guardado; puede intentarlo de nuevo más tarde.';
      aviso.title = respuesta.avisos.join(' '); // detalle técnico, para quien lo necesite
      aviso.hidden = false;
    } else {
      aviso.hidden = true;
    }
  }

  /* ------------------------------ Búsqueda ------------------------------ */
  function tipoElegido() {
    var marcado = document.querySelector('input[name="tipo"]:checked');
    return marcado ? marcado.value : 'todos';
  }

  function buscar() {
    var consulta = $('caja-busqueda').value.trim();
    var tipo = tipoElegido();
    var lista = $('lista-buscar');
    var estado = $('estado-buscar');
    DG.Interfaz.mostrarCargando(lista, estado);

    DG.Datos.buscar({ consulta: consulta, tipo: tipo }).then(function (r) {
      mostrarAvisoModo(r);
      var resultados = r.resultados;
      if (!consulta) {
        // Sin texto: se muestran solo los recomendados para no abrumar.
        var destacados = resultados.filter(function (d) { return d.destacado; });
        if (destacados.length) resultados = destacados;
      }
      var n = resultados.length;
      var mensaje;
      if (!n) {
        mensaje = 'No encontramos resultados para «' + consulta + '»' + NOMBRE_TIPO[tipo] +
                  '. Pruebe con otras palabras, elija «Todos» o pulse uno de los temas sugeridos.';
      } else if (consulta) {
        mensaje = 'Encontramos ' + n + (n === 1 ? ' resultado' : ' resultados') + ' para «' + consulta + '»' + NOMBRE_TIPO[tipo] + '.';
      } else {
        mensaje = 'Le recomendamos estos ' + n + ' documentos' + NOMBRE_TIPO[tipo] + ' para empezar. Escriba un tema para buscar otros.';
      }
      DG.Interfaz.mostrarResultados(lista, estado, resultados, mensaje, acciones);
    });
  }

  function cargarSeccion(seccion) {
    if (cargadas[seccion]) return;
    var lista = $('lista-' + seccion);
    var estado = $('estado-' + seccion);
    DG.Interfaz.mostrarCargando(lista, estado);
    DG.Datos.buscar({ consulta: '', tipo: TIPO_DE_SECCION[seccion] }).then(function (r) {
      mostrarAvisoModo(r);
      var resultados = r.resultados;
      if (seccion === 'libros') {
        // Primero los destacados, luego el resto.
        resultados = resultados.filter(function (d) { return d.destacado; })
          .concat(resultados.filter(function (d) { return !d.destacado; }));
      }
      cargadas[seccion] = true;
      DG.Interfaz.mostrarResultados(lista, estado, resultados, resultados.length + ' documentos disponibles.', acciones);
    });
  }

  /* --------------------------- Navegación --------------------------- */
  function seccionActual() {
    var s = window.location.hash.replace('#', '');
    return SECCIONES.indexOf(s) > -1 ? s : 'buscar';
  }

  function mostrarSeccion(moverFoco) {
    var actual = seccionActual();
    document.querySelectorAll('main section[data-seccion]').forEach(function (s) {
      s.hidden = s.getAttribute('data-seccion') !== actual;
    });
    document.querySelectorAll('.pestana').forEach(function (p) {
      if (p.getAttribute('data-seccion') === actual) p.setAttribute('aria-current', 'page');
      else p.removeAttribute('aria-current');
    });
    if (actual !== 'buscar') cargarSeccion(actual);
    if (moverFoco) $('titulo-' + actual).focus();
  }

  /* ------------------------- Tamaño de letra ------------------------- */
  var ESCALAS = [0.9, 1, 1.15, 1.3, 1.5];
  var nivel = 1;

  function aplicarEscala() {
    document.documentElement.style.setProperty('--escala', ESCALAS[nivel]);
    $('btn-letra-menos').disabled = nivel === 0;
    $('btn-letra-mas').disabled = nivel === ESCALAS.length - 1;
    try { localStorage.setItem('dg-escala', String(nivel)); } catch (e) { /* sin almacenamiento */ }
  }

  function cambiarEscala(paso) {
    nivel = Math.max(0, Math.min(ESCALAS.length - 1, nivel + paso));
    aplicarEscala();
    DG.Interfaz.avisar(paso > 0 ? 'Letra más grande' : 'Letra más pequeña');
  }

  /* ----------------------------- Inicio ----------------------------- */
  function iniciar() {
    try {
      var guardado = parseInt(localStorage.getItem('dg-escala'), 10);
      if (!isNaN(guardado) && ESCALAS[guardado]) nivel = guardado;
    } catch (e) { /* sin almacenamiento */ }
    aplicarEscala();

    $('formulario-busqueda').addEventListener('submit', function (e) {
      e.preventDefault();
      buscar();
    });

    // Al cambiar el filtro se repite la búsqueda automáticamente.
    document.querySelectorAll('input[name="tipo"]').forEach(function (radio) {
      radio.addEventListener('change', buscar);
    });

    $('sugerencias').addEventListener('click', function (e) {
      var boton = e.target.closest('.sugerencia');
      if (!boton) return;
      $('caja-busqueda').value = boton.textContent;
      buscar();
      $('estado-buscar').scrollIntoView({ block: 'start' });
    });

    DG.Voz.iniciar({
      boton: $('btn-voz'),
      textoBoton: $('texto-btn-voz'),
      estado: $('estado-voz'),
      alReconocer: function (texto) {
        $('caja-busqueda').value = texto;
        buscar();
      }
    });

    $('btn-letra-mas').addEventListener('click', function () { cambiarEscala(1); });
    $('btn-letra-menos').addEventListener('click', function () { cambiarEscala(-1); });
    $('btn-ayuda').addEventListener('click', function () { $('dialogo-ayuda').showModal(); });

    window.addEventListener('hashchange', function () { mostrarSeccion(true); });
    mostrarSeccion(false);

    // Al abrir la página, se muestran los destacados para que no aparezca vacía.
    buscar();
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})(window.DG = window.DG || {});
