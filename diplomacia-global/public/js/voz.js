/*
 * BÚSQUEDA POR VOZ
 * Usa el reconocimiento de voz del navegador (funciona en Chrome, Edge y Safari).
 * Si el navegador no lo permite, el botón explica cómo escribir en su lugar.
 */
(function (DG) {
  'use strict';

  var Reconocimiento = window.SpeechRecognition || window.webkitSpeechRecognition;

  /**
   * @param {Object} op
   *   boton, textoBoton, estado: elementos de la página
   *   alReconocer(texto): se llama con lo que dijo la persona
   */
  function iniciar(op) {
    if (!Reconocimiento) {
      op.boton.addEventListener('click', function () {
        op.estado.textContent = 'Su navegador no permite dictar. Pruebe con Google Chrome o escriba en la caja.';
      });
      return;
    }

    var rec = new Reconocimiento();
    rec.lang = 'es-ES';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    var escuchando = false;

    function cambiarEstado(activo) {
      escuchando = activo;
      op.boton.setAttribute('aria-pressed', String(activo));
      op.textoBoton.textContent = activo ? 'Detener' : 'Buscar hablando';
    }

    op.boton.setAttribute('aria-pressed', 'false');

    op.boton.addEventListener('click', function () {
      if (escuchando) { rec.stop(); return; }
      try {
        rec.start();
        cambiarEstado(true);
        op.estado.textContent = 'Le escucho… diga lo que busca, por ejemplo: «Guerra Fría».';
      } catch (e) { /* ya estaba escuchando */ }
    });

    rec.onresult = function (evento) {
      var texto = evento.results[0][0].transcript.replace(/[.。]$/, '');
      op.estado.textContent = 'Entendí: «' + texto + '». Buscando…';
      op.alReconocer(texto);
    };

    rec.onerror = function (evento) {
      var mensajes = {
        'not-allowed': 'No hay permiso para usar el micrófono. Pulse el candado junto a la dirección web y permita el micrófono.',
        'no-speech': 'No le escuché. Pulse el botón e inténtelo otra vez, hablando cerca del micrófono.',
        'audio-capture': 'No se encontró un micrófono conectado.',
        'network': 'El dictado necesita conexión a internet.'
      };
      op.estado.textContent = mensajes[evento.error] || 'No se pudo usar el micrófono. Puede escribir en la caja.';
    };

    rec.onend = function () { cambiarEstado(false); };
  }

  DG.Voz = { iniciar: iniciar, disponible: !!Reconocimiento };
})(window.DG = window.DG || {});
