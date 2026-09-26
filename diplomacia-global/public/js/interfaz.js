/*
 * INTERFAZ
 * Dibuja las tarjetas de resultados y los avisos.
 * Todo el texto se inserta con textContent (nunca innerHTML con datos externos),
 * para que ningún título o resumen pueda ejecutar código.
 */
(function (DG) {
  'use strict';

  var TIPOS = {
    noticia: { icono: '📰', nombre: 'Noticia' },
    paper: { icono: '📄', nombre: 'Paper Académico' },
    libro: { icono: '📘', nombre: 'Libro' }
  };

  var ICONOS = {
    enlace: '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    descarga: '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    whatsapp: '<path d="M21 11.5a8.4 8.4 0 0 1-12.5 7.4L3 21l2.1-5.3A8.4 8.4 0 1 1 21 11.5z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>'
  };

  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

  /** Crea un elemento con clase y texto. */
  function crear(etiqueta, clase, texto) {
    var el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  function icono(nombre, clase) {
    var span = document.createElement('span');
    span.innerHTML = '<svg class="' + (clase || 'icono') + '" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + ICONOS[nombre] + '</svg>';
    return span.firstChild;
  }

  /** "2026-09-22" -> "22 de septiembre de 2026"; "1994" -> "1994"; "-0400" -> "Hacia el año 400 a. C." */
  function formatearFecha(fecha) {
    if (!fecha) return 'Sin fecha';
    var m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(fecha);
    if (m) {
      var mes = MESES[Number(m[2]) - 1];
      return m[3] ? Number(m[3]) + ' de ' + mes + ' de ' + m[1] : mes + ' de ' + m[1];
    }
    var anio = parseInt(fecha, 10);
    if (anio < 0) return 'Hacia el año ' + Math.abs(anio) + ' a. C.';
    return String(anio || fecha);
  }

  /** Para noticias recientes: "hoy", "ayer" o "hace 3 días". */
  function haceCuanto(fecha, ahora) {
    var t = Date.parse(fecha);
    if (isNaN(t) || !/^\d{4}-\d{2}-\d{2}T/.test(fecha)) return '';
    var dias = Math.floor(((ahora || new Date()) - t) / 86400000);
    if (dias < 0 || dias > 13) return '';
    return dias === 0 ? 'hoy' : dias === 1 ? 'ayer' : 'hace ' + dias + ' días';
  }

  function dato(lista, nombre, valor) {
    var fila = crear('div');
    fila.appendChild(crear('dt', null, nombre + ': '));
    fila.appendChild(crear('dd', null, valor));
    lista.appendChild(fila);
  }

  function textoParaCompartir(doc) {
    var partes = ['Te comparto esto que encontré en Diplomacia Global:', '', '*' + doc.titulo + '*'];
    if (doc.autor) partes.push(doc.autor);
    if (doc.fragmento) partes.push('', '«' + doc.resumen + '»');
    if (doc.enlace) partes.push('', doc.enlace);
    return partes.join('\n');
  }

  /**
   * Crea la tarjeta de un resultado.
   * @param {Object} doc  Documento con el formato común.
   * @param {Object} acciones { alDescargar(doc, enlace), alCompartir(doc) }
   */
  function crearTarjeta(doc, acciones) {
    var tipo = TIPOS[doc.tipo] || TIPOS.paper;
    var item = crear('li');
    var tarjeta = crear('article', 'tarjeta');
    tarjeta.setAttribute('data-tipo', doc.tipo);
    var idTitulo = 'titulo-' + doc.id;
    tarjeta.setAttribute('aria-labelledby', idTitulo);

    // Etiquetas superiores
    var cabecera = crear('div', 'flex flex-wrap gap-2');
    var etiqueta = crear('span', 'etiqueta-tipo');
    etiqueta.setAttribute('data-tipo', doc.tipo);
    etiqueta.appendChild(crear('span', null, tipo.icono)).setAttribute('aria-hidden', 'true');
    etiqueta.appendChild(document.createTextNode(doc.fragmento ? tipo.nombre + ' · Fragmento de mi biblioteca' : tipo.nombre));
    cabecera.appendChild(etiqueta);
    if (doc.ejemplo) cabecera.appendChild(crear('span', 'etiqueta-ejemplo', 'Contenido de ejemplo'));
    var cuando = haceCuanto(doc.fecha);
    if (cuando) cabecera.appendChild(crear('span', 'etiqueta-extra', 'Publicado ' + cuando)).setAttribute('data-clase', 'nuevo');
    if (doc.idioma === 'en') cabecera.appendChild(crear('span', 'etiqueta-extra', 'En inglés'));
    if (doc.descarga) cabecera.appendChild(crear('span', 'etiqueta-extra', 'Acceso libre ✓')).setAttribute('data-clase', 'libre');
    tarjeta.appendChild(cabecera);

    // Título
    var titulo = crear('h2', 'titulo-tarjeta', doc.titulo);
    titulo.id = idTitulo;
    tarjeta.appendChild(titulo);

    // Resumen o fragmento
    if (doc.fragmento) {
      if (doc.capitulo) tarjeta.appendChild(crear('p', 'text-lg font-bold mb-2', doc.capitulo));
      tarjeta.appendChild(crear('blockquote', 'fragmento', doc.resumen));
    } else {
      tarjeta.appendChild(crear('p', 'resumen-tarjeta', doc.resumen));
    }

    // Datos
    var datos = crear('dl', 'datos-tarjeta');
    if (doc.autor !== doc.fuente) dato(datos, 'Autor', doc.autor || 'No indicado');
    dato(datos, doc.ejemplo ? 'Enlace a' : 'Fuente',
      (doc.fuente || 'No indicada') + (doc.tipoFuente ? ' (' + doc.tipoFuente.toLowerCase() + ')' : ''));
    if (doc.fragmento) dato(datos, 'Ubicación', doc.ubicacion);
    else dato(datos, 'Fecha', formatearFecha(doc.fecha));
    tarjeta.appendChild(datos);

    // Acciones
    var botones = crear('div', 'acciones-tarjeta');

    if (doc.enlace) {
      var visitar = crear('a', 'boton boton-principal');
      visitar.href = doc.enlace;
      visitar.target = '_blank';
      visitar.rel = 'noopener noreferrer';
      visitar.appendChild(icono('enlace'));
      visitar.appendChild(document.createTextNode('Visitar enlace original'));
      visitar.appendChild(crear('span', 'sr-only', ' (se abre en una pestaña nueva)'));
      botones.appendChild(visitar);
    }

    var enlaceDescarga = DG.Datos.urlDescarga(doc);
    if (enlaceDescarga) {
      var descargar = crear('a', 'boton boton-descarga');
      descargar.href = enlaceDescarga;
      // El servidor envía el archivo como descarga (Content-Disposition). Se usa una pestaña
      // nueva y no el atributo "download": así, si la descarga directa falla, se abre el
      // documento original sin que la persona pierda sus resultados.
      descargar.target = '_blank';
      descargar.rel = 'noopener';
      descargar.appendChild(icono('descarga'));
      descargar.appendChild(document.createTextNode('Descargar documento (' + doc.descarga.formato + ')'));
      descargar.addEventListener('click', function () { acciones.alDescargar(doc); });
      botones.appendChild(descargar);
    } else if (!doc.fragmento && doc.tipo !== 'noticia') {
      var nota = crear('p', 'nota-sin-descarga');
      nota.appendChild(icono('info'));
      nota.appendChild(document.createTextNode('No es de descarga libre. Puede leerlo en el enlace original.'));
      botones.appendChild(nota);
    }

    var compartir = crear('a', 'boton boton-whatsapp');
    compartir.href = 'https://wa.me/?text=' + encodeURIComponent(textoParaCompartir(doc));
    compartir.target = '_blank';
    compartir.rel = 'noopener noreferrer';
    compartir.appendChild(icono('whatsapp'));
    compartir.appendChild(document.createTextNode('Compartir por WhatsApp'));
    compartir.appendChild(crear('span', 'sr-only', ' (se abre WhatsApp en una pestaña nueva)'));
    compartir.addEventListener('click', function () { acciones.alCompartir(doc); });
    botones.appendChild(compartir);

    tarjeta.appendChild(botones);
    item.appendChild(tarjeta);
    return item;
  }

  var POR_PAGINA = 10;

  function quitarVerMas(lista) {
    var siguiente = lista.nextElementSibling;
    if (siguiente && siguiente.classList.contains('boton-ver-mas')) siguiente.remove();
  }

  /**
   * Muestra la lista de resultados (de 10 en 10, para no abrumar) y un mensaje de estado.
   */
  function mostrarResultados(lista, estado, resultados, mensaje, acciones) {
    lista.replaceChildren();
    quitarVerMas(lista);
    estado.classList.remove('cargando');
    estado.textContent = mensaje;
    var mostrados = 0;

    function mostrarMas() {
      var fragmento = document.createDocumentFragment();
      var primeraNueva = null;
      resultados.slice(mostrados, mostrados + POR_PAGINA).forEach(function (doc) {
        var tarjeta = crearTarjeta(doc, acciones);
        if (!primeraNueva) primeraNueva = tarjeta;
        fragmento.appendChild(tarjeta);
      });
      mostrados = Math.min(resultados.length, mostrados + POR_PAGINA);
      lista.appendChild(fragmento);
      quitarVerMas(lista);
      if (mostrados < resultados.length) {
        var boton = crear('button', 'boton boton-ver-mas');
        boton.type = 'button';
        var restantes = resultados.length - mostrados;
        boton.textContent = 'Ver ' + Math.min(POR_PAGINA, restantes) + ' resultados más (quedan ' + restantes + ')';
        boton.addEventListener('click', function () {
          var siguiente = mostrarMas();
          // Se lleva el foco al primer resultado nuevo, para seguir leyendo desde ahí.
          var titulo = siguiente && siguiente.querySelector('h2');
          if (titulo) { titulo.setAttribute('tabindex', '-1'); titulo.focus(); }
        });
        lista.after(boton);
      }
      return primeraNueva;
    }
    mostrarMas();
  }

  function mostrarCargando(lista, estado) {
    lista.replaceChildren();
    quitarVerMas(lista);
    estado.textContent = 'Buscando… un momento, por favor.';
    estado.classList.add('cargando');
  }

  var temporizadorAviso;
  /** Mensaje flotante que desaparece solo (y que leen los lectores de pantalla). */
  function avisar(texto, tipo) {
    var aviso = document.getElementById('aviso');
    clearTimeout(temporizadorAviso);
    aviso.textContent = texto;
    aviso.setAttribute('data-tipo', tipo || 'exito');
    aviso.hidden = false;
    temporizadorAviso = setTimeout(function () { aviso.hidden = true; }, 6000);
  }

  DG.Interfaz = {
    crearTarjeta: crearTarjeta,
    mostrarResultados: mostrarResultados,
    mostrarCargando: mostrarCargando,
    avisar: avisar,
    formatearFecha: formatearFecha,
    haceCuanto: haceCuanto
  };
})(window.DG = window.DG || {});
