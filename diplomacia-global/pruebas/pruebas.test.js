/*
 * PRUEBAS AUTOMÁTICAS
 * Ejecutar con:  npm test
 * No usan internet: las fuentes externas se prueban con datos de ejemplo.
 */
'use strict';

process.env.FUENTES_EN_VIVO = 'no';

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const catalogo = require('../public/datos/catalogo.js');
const Motor = require('../public/js/motor-busqueda.js');
const Crossref = require('../public/js/crossref.js');
const Fuentes = require('../public/js/fuentes-prestigio.js');
const { obtenerSemana } = require('../servidor/semana');
const rss = require('../servidor/fuentes/noticias-rss');
const biblioteca = require('../servidor/fuentes/biblioteca-personal');

describe('Catálogo', () => {
  test('cada documento tiene los campos obligatorios y un id único', () => {
    const ids = new Set();
    for (const d of catalogo) {
      assert.ok(d.id && d.titulo && d.resumen && d.autor && d.fecha, `Faltan datos en ${d.id}`);
      assert.ok(['noticia', 'paper', 'libro'].includes(d.tipo), `Tipo inválido en ${d.id}`);
      assert.ok(/^https:\/\//.test(d.enlace), `Enlace inválido en ${d.id}`);
      assert.ok(!ids.has(d.id), `Id repetido: ${d.id}`);
      ids.add(d.id);
      if (d.descarga) assert.ok(/^https:\/\//.test(d.descarga.url) && d.descarga.formato);
    }
  });

  test('todas las noticias locales están marcadas como ejemplo', () => {
    catalogo.filter((d) => d.tipo === 'noticia').forEach((d) => assert.equal(d.ejemplo, true, d.id));
  });
});

describe('Motor de búsqueda', () => {
  test('ignora mayúsculas y tildes', () => {
    assert.equal(Motor.normalizar('¿Guerra FRÍA?'), 'guerra fria');
    const a = Motor.buscar(catalogo, { consulta: 'guerra fria' }).map((d) => d.id);
    const b = Motor.buscar(catalogo, { consulta: 'GUERRA FRÍA' }).map((d) => d.id);
    assert.deepEqual(a, b);
    assert.ok(a.includes('libro-kissinger-diplomacia'));
  });

  test('entiende sinónimos en inglés y español', () => {
    const ids = Motor.buscar(catalogo, { consulta: 'United Nations' }).map((d) => d.id);
    assert.ok(ids.includes('paper-carta-onu'));
  });

  test('filtra por tipo', () => {
    const libros = Motor.buscar(catalogo, { consulta: 'Kissinger', tipo: 'libro' });
    assert.ok(libros.length >= 2);
    assert.ok(libros.every((d) => d.tipo === 'libro'));
    assert.equal(Motor.buscar(catalogo, { consulta: 'Kissinger', tipo: 'noticia' }).length, 0);
  });

  test('el título pesa más que el resumen', () => {
    const [primero] = Motor.buscar(catalogo, { consulta: 'soft power' });
    assert.equal(primero.id, 'paper-nye-poder-blando');
  });

  test('sin coincidencias devuelve una lista vacía', () => {
    assert.deepEqual(Motor.buscar(catalogo, { consulta: 'zzzqqq' }), []);
  });

  test('sin texto ordena por fecha, de lo más nuevo a lo más antiguo (incluye años a. C.)', () => {
    const libros = Motor.buscar(catalogo, { tipo: 'libro' });
    const valores = libros.map((d) => Motor.valorFecha(d.fecha));
    assert.deepEqual(valores, [...valores].sort((x, y) => y - x));
    assert.equal(libros[libros.length - 1].id, 'libro-sun-tzu-arte-guerra');
  });
});

describe('Fuente Crossref', () => {
  test('convierte un registro y solo ofrece descarga con licencia abierta', () => {
    const base = {
      DOI: '10.1234/abc',
      title: ['A <i>Test</i> Paper'],
      author: [{ given: 'Ana', family: 'Pérez' }],
      issued: { 'date-parts': [[2020, 3]] },
      'container-title': ['Journal of Diplomacy'],
      abstract: '<jats:p>Short abstract.</jats:p>',
      link: [{ URL: 'https://ejemplo.org/a.pdf', 'content-type': 'application/pdf' }]
    };
    const cerrado = Crossref.convertir(base);
    assert.equal(cerrado.titulo, 'A Test Paper');
    assert.equal(cerrado.autor, 'Ana Pérez');
    assert.equal(cerrado.fecha, '2020-03');
    assert.equal(cerrado.resumen, 'Short abstract.');
    assert.equal(cerrado.descarga, null);

    const abierto = Crossref.convertir({ ...base, license: [{ URL: 'https://creativecommons.org/licenses/by/4.0/' }] });
    assert.equal(abierto.descarga.url, 'https://ejemplo.org/a.pdf');
  });

  test('solo consulta revistas de prestigio y puede limitar por fecha', () => {
    const url = new URL(Crossref.construirUrl({ consulta: 'guerra fria', desde: '2026-09-19' }));
    assert.equal(url.hostname, 'api.crossref.org');
    assert.equal(url.searchParams.get('query'), 'guerra fria');
    const filtro = url.searchParams.get('filter');
    assert.match(filtro, /issn:0020-8183/); // International Organization
    assert.match(filtro, /from-pub-date:2026-09-19/);
    assert.equal((filtro.match(/issn:/g) || []).length, Fuentes.revistas.length);
  });
});

describe('Fuente RSS', () => {
  test('lee titulares, enlaces y fechas', () => {
    const xml = `<rss><channel>
      <item><title><![CDATA[Cumbre de paz]]></title><link>https://ejemplo.org/1</link>
        <description>&lt;p&gt;Texto &amp; más&lt;/p&gt;</description><pubDate>Tue, 22 Sep 2026 10:00:00 GMT</pubDate></item>
      <item><title>Sin enlace</title></item>
    </channel></rss>`;
    const noticias = rss.interpretarRss(xml, 'Medio de prueba');
    assert.equal(noticias.length, 1);
    assert.equal(noticias[0].titulo, 'Cumbre de paz');
    assert.equal(noticias[0].fecha, '2026-09-22T10:00:00.000Z');
    assert.equal(noticias[0].resumen, 'Texto & más');
    assert.equal(noticias[0].tipo, 'noticia');
  });
});

describe('Fuentes de prestigio', () => {
  test('cada medio tiene nombre, idioma y dirección segura', () => {
    for (const m of Fuentes.medios) {
      assert.ok(m.id && m.nombre && m.tipoFuente, m.id);
      assert.ok(['es', 'en'].includes(m.idioma), m.id);
      assert.match(m.url, /^https:\/\//, m.id);
    }
    assert.ok(Fuentes.revistas.every((r) => /^\d{4}-\d{3}[\dX]$/.test(r.issn)));
  });

  test('de un medio general solo toma noticias diplomáticas', () => {
    assert.equal(Fuentes.esRelevante('Peace talks resume in Doha', ''), true);
    assert.equal(Fuentes.esRelevante('La ONU pide un alto el fuego', ''), true);
    assert.equal(Fuentes.esRelevante('Weather warning for the weekend', ''), false);
    assert.equal(Fuentes.esRelevante('Receta de pan casero', ''), false);

    const xml = `<rss><channel>
      <item><title>Cumbre del G20 termina con acuerdo</title><link>https://ejemplo.org/a</link></item>
      <item><title>Gana el equipo local</title><link>https://ejemplo.org/b</link></item>
    </channel></rss>`;
    const general = rss.interpretarRss(xml, { nombre: 'Diario', especializado: false, idioma: 'es' });
    assert.deepEqual(general.map((n) => n.titulo), ['Cumbre del G20 termina con acuerdo']);
    const especializado = rss.interpretarRss(xml, { nombre: 'Revista', especializado: true });
    assert.equal(especializado.length, 2);
  });

  test('también entiende feeds Atom', () => {
    const xml = `<feed><entry><title>New treaty signed</title>
      <link rel="alternate" href="https://ejemplo.org/t"/><updated>2026-09-24T08:00:00Z</updated>
      <summary>Details</summary></entry></feed>`;
    const [n] = rss.interpretarRss(xml, { nombre: 'Atom', especializado: true, idioma: 'en' });
    assert.equal(n.enlace, 'https://ejemplo.org/t');
    assert.equal(n.fecha, '2026-09-24T08:00:00.000Z');
    assert.equal(n.idioma, 'en');
  });
});

describe('Novedades de la última semana', () => {
  test('solo últimos 7 días, sin duplicados, de lo más nuevo a lo más antiguo', async () => {
    const ahora = new Date('2026-09-26T12:00:00Z');
    const rssFalso = `<rss><channel>
      <item><title>Nueva cumbre de la ONU sobre clima</title><link>https://ejemplo.org/1</link><pubDate>Thu, 24 Sep 2026 10:00:00 GMT</pubDate></item>
      <item><title>Acuerdo de paz firmado</title><link>https://ejemplo.org/2</link><pubDate>Fri, 25 Sep 2026 10:00:00 GMT</pubDate></item>
      <item><title>Tratado antiguo</title><link>https://ejemplo.org/3</link><pubDate>Mon, 07 Sep 2026 10:00:00 GMT</pubDate></item>
    </channel></rss>`;
    const crossrefFalso = { message: { items: [{
      DOI: '10.1/x', title: ['Diplomacy after the war'], issued: { 'date-parts': [[2026, 9, 23]] },
      'container-title': ['International Security']
    }] } };
    const fetchOriginal = global.fetch;
    global.fetch = async (url) => {
      if (String(url).startsWith('https://api.crossref.org')) {
        return new Response(JSON.stringify(crossrefFalso), { status: 200 });
      }
      if (String(url).includes('bbc')) return new Response('', { status: 500 }); // un medio caído
      return new Response(rssFalso, { status: 200 });
    };
    try {
      const semana = await obtenerSemana({ ahora, esperaMs: 1000 });
      assert.deepEqual(semana.resultados.map((d) => d.titulo),
        ['Acuerdo de paz firmado', 'Nueva cumbre de la ONU sobre clima', 'Diplomacy after the war']);
      assert.equal(semana.dias, 7);
      assert.ok(semana.fuentes.some((f) => !f.ok), 'informa del medio caído');
      assert.ok(semana.fuentes.some((f) => f.fuente.includes('Crossref') && f.ok));
    } finally {
      global.fetch = fetchOriginal;
    }
  });

  test('si ninguna fuente responde, lo indica (generado = null)', async () => {
    const fetchOriginal = global.fetch;
    global.fetch = async () => { throw new Error('sin internet'); };
    try {
      const semana = await obtenerSemana({ esperaMs: 500 });
      assert.equal(semana.generado, null);
      assert.deepEqual(semana.resultados, []);
    } finally {
      global.fetch = fetchOriginal;
    }
  });

  test('el archivo publicado tiene el formato esperado', () => {
    const datos = require('../public/datos/ultima-semana.json');
    assert.ok('generado' in datos && Array.isArray(datos.resultados) && datos.dias === 7);
  });
});

describe('Biblioteca personal', () => {
  test('recuerda el capítulo de cada párrafo e ignora líneas cortas', () => {
    const largo = 'La Guerra Fría fue un largo periodo de tensión entre bloques. '.repeat(3);
    const texto = `# CAPÍTULO UNO \n\nEl nuevo orden mundial\n\nCorto.\n\n${largo}\n`;
    const parrafos = biblioteca.indexarTexto(texto);
    assert.equal(parrafos.length, 1);
    assert.equal(parrafos[0].capitulo, 'Capítulo uno: El nuevo orden mundial');
  });
});

describe('Servidor', () => {
  let servidor;
  let base;

  before(async () => {
    servidor = require('../servidor');
    await new Promise((ok) => servidor.listen(0, ok));
    base = `http://127.0.0.1:${servidor.address().port}`;
  });
  after(() => servidor.close());

  test('entrega la página principal', async () => {
    const r = await fetch(base + '/');
    assert.equal(r.status, 200);
    assert.match(await r.text(), /Diplomacia Global/);
  });

  test('busca por API y respeta el filtro', async () => {
    const r = await fetch(base + '/api/buscar?q=Kissinger&tipo=libro');
    const datos = await r.json();
    assert.ok(datos.total > 0);
    assert.ok(datos.resultados.every((d) => d.tipo === 'libro'));
  });

  test('entrega las novedades de la semana (vacías si no hay internet)', async () => {
    const datos = await (await fetch(base + '/api/semana')).json();
    assert.equal(datos.dias, 7);
    assert.ok(Array.isArray(datos.resultados));
  });

  test('un tipo desconocido se trata como "todos"', async () => {
    const datos = await (await fetch(base + '/api/buscar?q=ONU&tipo=<script>')).json();
    assert.equal(datos.tipo, 'todos');
  });

  test('no permite salir de la carpeta public', async () => {
    const r = await fetch(base + '/%2e%2e/servidor.js');
    assert.notEqual(r.status, 200);
  });

  test('descarga con un clic: entrega el archivo con su nombre', async () => {
    const http = require('http');
    const origen = http.createServer((req, res) => {
      res.writeHead(200, { 'Content-Type': 'application/pdf' });
      res.end('%PDF-prueba');
    });
    await new Promise((ok) => origen.listen(0, ok));
    const doc = catalogo.find((d) => d.id === 'paper-carta-onu');
    const urlOriginal = doc.descarga.url;
    doc.descarga.url = `http://127.0.0.1:${origen.address().port}/carta.pdf`;
    try {
      const r = await fetch(base + '/api/descargar/paper-carta-onu');
      assert.equal(r.status, 200);
      assert.match(r.headers.get('content-disposition'), /attachment; filename="Carta-de-las-Naciones-Unidas\.pdf"/);
      assert.equal(await r.text(), '%PDF-prueba');
    } finally {
      doc.descarga.url = urlOriginal;
      origen.close();
    }
  });

  test('no descarga documentos que no son de acceso libre', async () => {
    const r = await fetch(base + '/api/descargar/libro-kissinger-diplomacia');
    assert.equal(r.status, 404);
  });
});
