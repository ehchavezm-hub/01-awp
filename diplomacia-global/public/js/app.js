/*
 * APLICACIÓN PRINCIPAL
 * Une todas las piezas: menú, buscador, novedades de la semana, filtros, voz,
 * tamaño de letra y ayuda.
 */
(function (DG) {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var SECCIONES = ['buscar', 'noticias', 'papers', 'libros'];
  var TIPO_DE_SECCION = { papers: 'paper', libros: 'libro' };
  var NOMBRE_TIPO = { todos: '', noticia: ' en Noticias', paper: ' en Papers', libro: ' en Libros' };
  var cargadas = {};
  var vista = 'busqueda'; // 'busqueda' o 'semana': qué se muestra en la zona de resultados

  var acciones = {
    alDescargar: function () {
      DG.Interfaz.avisar(DG.Datos.hayServidor()
        ? '¡Descarga iniciada con éxito! Encontrará el archivo en su carpeta «Descargas».'
        : '¡Descarga iniciada con éxito! Si el documento se abre en una pestaña nueva, pulse el botón de descarga del navegador para guardarlo.');
    },
    alCompartir: function () {
      DG.Interfaz.avisar('Abriendo WhatsApp… elija a quién enviarlo.');
    }
  };

  /* ------------------------------ Utilidades ------------------------------ */
  function tipoElegido() {
    var marcado = document.querySelector('input[name="tipo"]:checked');
    return marcado ? marcado.value : 'todos';
  }

  function idiomaElegido() {
    var marcado = document.querySelector('input[name="idioma"]:checked');
    return marcado ? marcado.value : 'todos';
  }

  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }

  function fechaCorta(d) {
    var meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    return d.getDate() + ' de ' + meses[d.getMonth()];
  }

  function mostrarAvisoServidor(respuesta) {
    var aviso = $('aviso-modo');
    if (respuesta.avisos && respuesta.avisos.length) {
      aviso.textContent = 'Algunas fuentes no respondieron en este momento. Le mostramos lo que tenemos guardado; puede intentarlo de nuevo más tarde.';
      aviso.hidden = false;
    } else {
      aviso.hidden = true;
    }
  }

  /* ------------------------------ Búsqueda ------------------------------ */
  function buscar() {
    vista = 'busqueda';
    $('filtro-idioma').hidden = true;
    var consulta = $('caja-busqueda').value.trim();
    var tipo = tipoElegido();
    var lista = $('lista-buscar');
    var estado = $('estado-buscar');
    DG.Interfaz.mostrarCargando(lista, estado);

    DG.Datos.buscar({ consulta: consulta, tipo: tipo }).then(function (r) {
      mostrarAvisoServidor(r);
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
        mensaje = 'Encontramos ' + plural(n, 'resultado', 'resultados') + ' para «' + consulta + '»' + NOMBRE_TIPO[tipo] + '.';
      } else {
        mensaje = 'Le recomendamos estos ' + n + ' documentos' + NOMBRE_TIPO[tipo] + ' para empezar. Escriba un tema para buscar otros.';
      }
      DG.Interfaz.mostrarResultados(lista, estado, resultados, mensaje, acciones);
    });
  }

  /* ---------------------- Novedades de la última semana ---------------------- */
  function verSemana() {
    vista = 'semana';
    $('filtro-idioma').hidden = false;
    $('aviso-modo').hidden = true;
    var consulta = $('caja-busqueda').value.trim();
    var tipo = tipoElegido();
    var lista = $('lista-buscar');
    var estado = $('estado-buscar');
    DG.Interfaz.mostrarCargando(lista, estado);
    estado.textContent = 'Buscando las novedades de la última semana… un momento, por favor.';

    DG.Datos.semana({ consulta: consulta, idioma: idiomaElegido() }).then(function (r) {
      var resultados = r.resultados.filter(function (d) { return tipo === 'todos' || d.tipo === tipo; });
      var sobre = consulta ? ' sobre «' + consulta + '»' : '';
      var hasta = new Date();
      var desde = new Date(hasta.getTime() - r.dias * 86400000);
      var periodo = ' (del ' + fechaCorta(desde) + ' al ' + fechaCorta(hasta) + ')';
      var mensaje;

      if (!r.generado) {
        mensaje = 'En este momento no podemos consultar las novedades. Por favor, inténtelo de nuevo en unos minutos.';
      } else if (!resultados.length) {
        mensaje = 'No encontramos novedades' + sobre + NOMBRE_TIPO[tipo] + ' en los últimos ' + r.dias + ' días. ' +
                  (consulta ? 'Pruebe con otro tema, o borre la caja de búsqueda para ver todas las novedades.' : 'Elija «Todos» para ver más.');
      } else {
        var fuentes = {};
        resultados.forEach(function (d) { fuentes[d.fuente] = true; });
        mensaje = 'Novedades de los últimos ' + r.dias + ' días' + periodo + sobre + NOMBRE_TIPO[tipo] + ': ' +
                  plural(resultados.length, 'publicación', 'publicaciones') + ' de ' +
                  plural(Object.keys(fuentes).length, 'fuente de prestigio', 'fuentes de prestigio') + '. Las más recientes, primero.';
      }
      DG.Interfaz.mostrarResultados(lista, estado, resultados, mensaje, acciones);
    });
  }

  function mostrarActualizacion() {
    DG.Datos.semana().then(function (r) {
      if (!r.generado) return;
      var d = new Date(r.generado);
      var hora = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
      var dia = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      $('pie-actualizado').textContent = 'Novedades actualizadas por última vez el ' +
        DG.Interfaz.formatearFecha(dia) + ' a las ' + hora + '.';
    });
  }

  /* ------------------------------ Secciones ------------------------------ */
  function cargarNoticias() {
    var lista = $('lista-noticias');
    var estado = $('estado-noticias');
    DG.Interfaz.mostrarCargando(lista, estado);
    DG.Datos.semana().then(function (r) {
      var noticias = r.resultados.filter(function (d) { return d.tipo === 'noticia'; });
      if (noticias.length) {
        DG.Interfaz.mostrarResultados(lista, estado, noticias,
          plural(noticias.length, 'noticia', 'noticias') + ' de los últimos ' + r.dias + ' días. Las más recientes, primero.', acciones);
        return;
      }
      // Sin conexión con las fuentes: se muestran textos explicativos de ejemplo.
      var ejemplos = window.CATALOGO_DIPLOMACIA.filter(function (d) { return d.tipo === 'noticia'; });
      DG.Interfaz.mostrarResultados(lista, estado, ejemplos,
        'En este momento no podemos traer las noticias del día. Mientras tanto, le dejamos estos textos que explican temas de actualidad.', acciones);
    });
  }

  function cargarSeccion(seccion) {
    if (cargadas[seccion]) return;
    cargadas[seccion] = true;
    if (seccion === 'noticias') { cargarNoticias(); return; }

    var lista = $('lista-' + seccion);
    var estado = $('estado-' + seccion);
    DG.Interfaz.mostrarCargando(lista, estado);
    DG.Datos.buscar({ consulta: '', tipo: TIPO_DE_SECCION[seccion] }).then(function (r) {
      // Primero los destacados, luego el resto.
      var resultados = r.resultados.filter(function (d) { return d.destacado; })
        .concat(r.resultados.filter(function (d) { return !d.destacado; }));
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

    $('btn-semana').addEventListener('click', function () {
      verSemana();
      $('estado-buscar').scrollIntoView({ block: 'start' });
    });

    // Al cambiar un filtro se repite lo que se estaba viendo.
    document.querySelectorAll('input[name="tipo"]').forEach(function (radio) {
      radio.addEventListener('change', function () { (vista === 'semana' ? verSemana : buscar)(); });
    });
    document.querySelectorAll('input[name="idioma"]').forEach(function (radio) {
      radio.addEventListener('change', verSemana);
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
    mostrarActualizacion();

    // Al abrir la página, se muestran los destacados para que no aparezca vacía.
    buscar();
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})(window.DG = window.DG || {});
