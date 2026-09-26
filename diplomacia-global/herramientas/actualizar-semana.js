/*
 * ACTUALIZAR "NOVEDADES DE LA ÚLTIMA SEMANA"
 * Consulta las fuentes de prestigio y guarda el resultado en
 * public/datos/ultima-semana.json, que usa la versión publicada en internet.
 *
 * Lo ejecuta GitHub Actions automáticamente varias veces al día
 * (.github/workflows/publicar-web.yml). También puede ejecutarse a mano:
 *     npm run actualizar
 *
 * Nunca termina con error: si una fuente falla, se omite y se informa.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { obtenerSemana } = require('../servidor/semana');

const DESTINO = path.join(__dirname, '..', 'public', 'datos', 'ultima-semana.json');

(async () => {
  try {
    const datos = await obtenerSemana({ esperaMs: 20000 });
    console.log(`Novedades de los últimos ${datos.dias} días: ${datos.resultados.length} publicaciones.`);
    for (const f of datos.fuentes) {
      console.log(`  ${f.ok ? '✔' : '✘'} ${f.fuente}: ${f.ok ? f.cantidad : 'no respondió'}`);
    }
    if (!datos.resultados.length && fs.existsSync(DESTINO)) {
      const anterior = JSON.parse(fs.readFileSync(DESTINO, 'utf8'));
      if (anterior.resultados && anterior.resultados.length) {
        console.log('Ninguna fuente respondió: se conservan las novedades anteriores.');
        return;
      }
    }
    fs.writeFileSync(DESTINO, JSON.stringify(datos, null, 1) + '\n');
    console.log('Guardado en', path.relative(process.cwd(), DESTINO));
  } catch (e) {
    console.error('No se pudieron actualizar las novedades:', e.message);
  }
})();
