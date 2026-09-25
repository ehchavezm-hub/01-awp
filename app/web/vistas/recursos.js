// Biblioteca de recursos del kit (pública: no requiere iniciar sesión).
import { html, useState } from '../vendor/preact-htm.js';
import { RECURSOS, PRESENTACION } from '../datos/recursos.js';
import { MODULOS, disponible } from '../datos/modulos.js';
import { Ic, Vacio, urlRecurso } from '../lib/ui.js';
import { avisar } from '../lib/estado.js';
import { ir } from '../lib/rutas.js';

const CATEGORIAS = [['Todas', 'library'], ['Planificación', 'route'], ['Control', 'gauge'], ['Organización', 'users'], ['Capacitación', 'graduation-cap']];
const TIPOS = { xlsx: 'Excel', docx: 'Word', pptx: 'PowerPoint', web: 'Página web' };

function Tarjeta({ r, sesion }) {
  const mod = r.formulario && MODULOS.find(m => m.id === r.formulario);
  const llenar = () => {
    if (!sesion) { avisar('Inicia sesión para llenar el formulario en la aplicación.'); ir('/entrar'); return; }
    if (!disponible(mod)) { avisar(`El formulario «${r.nombre}» se habilita en la Etapa ${mod.etapa} de la aplicación.`); return; }
    avisar('Abre un proyecto y entra al módulo «' + mod.nombre + '».'); ir('/portafolio');
  };
  return html`<article class="tarjeta recurso">
    <div class="recurso-cab">
      <div class=${'tipo-archivo tipo-' + r.tipo} title=${TIPOS[r.tipo]}>${r.tipo === 'web' ? html`<${Ic} n="book-open" cls="ic ic-lg" style="stroke:#fff" />` : r.tipo.toUpperCase()}</div>
      <div><div class="cat">${r.categoria} · ${TIPOS[r.tipo]}</div><h3>${r.nombre}</h3></div>
    </div>
    <dl><dt>Para qué</dt><dd>${r.para}</dd><dt>Cuándo</dt><dd>${r.cuando}</dd><dt>Quién</dt><dd>${r.quien}</dd></dl>
    <div class="botones">
      <a class="btn btn-chico" href=${urlRecurso(r.archivo)} ...${r.tipo === 'web' ? { target: '_blank', rel: 'noopener' } : { download: '' }}>
        <${Ic} n=${r.tipo === 'web' ? 'external-link' : 'download'} />${r.tipo === 'web' ? 'Abrir' : 'Descargar'}</a>
      ${mod && html`<button class="btn btn-chico btn-suave" onClick=${llenar}><${Ic} n="pencil" />Llenar en la aplicación${!disponible(mod) ? ` (etapa ${mod.etapa})` : ''}</button>`}
    </div>
  </article>`;
}

export function VistaRecursos({ sesion }) {
  const [cat, setCat] = useState('Todas');
  const [buscar, setBuscar] = useState('');
  const texto = buscar.trim().toLowerCase();
  const filtrados = RECURSOS.filter(r => (cat === 'Todas' || r.categoria === cat) && (!texto || [r.nombre, r.para, r.cuando, r.quien].join(' ').toLowerCase().includes(texto)));
  const verPresentacion = ['Todas', 'Capacitación'].includes(cat) && (!texto || (PRESENTACION.nombre + ' presentación capacitación').toLowerCase().includes(texto));
  return html`<main>
    <div class="titulo-pantalla">
      <div><h1>Recursos del kit AWP</h1><p>Plantillas, plan de implementación y material de capacitación. Disponibles sin iniciar sesión.</p></div>
      <div class="acciones"><label class="filtros" style="margin:0;padding:6px 10px;display:flex;align-items:center;gap:6px"><${Ic} n="search" />
        <input value=${buscar} onInput=${e => setBuscar(e.target.value)} placeholder="Buscar recurso" aria-label="Buscar recurso" style="border:0;background:none;min-width:180px;outline:0;padding:0" /></label></div>
    </div>
    <div class="pestanas" role="tablist">${CATEGORIAS.map(([c, i]) => html`<button class="pestana" role="tab" aria-selected=${c === cat} onClick=${() => setCat(c)}><${Ic} n=${i} />${c}</button>`)}</div>

    ${verPresentacion && html`<section class="tarjeta destacado" style="margin-bottom:16px">
      <div class="recurso-cab">
        <div class="tipo-archivo tipo-pptx"><${Ic} n="presentation" cls="ic ic-lg" style="stroke:#fff" /></div>
        <div style="flex:1"><div class="cat">Capacitación · PowerPoint · ${PRESENTACION.laminas} láminas</div>
          <h3 style="font-size:18px">${PRESENTACION.nombre}</h3>
          <p style="margin:4px 0 0;color:var(--texto-2)">${PRESENTACION.para}</p>
          <p style="margin:4px 0 0;color:var(--texto-3);font-size:12.5px"><b>Cuándo:</b> ${PRESENTACION.cuando} · <b>Quién:</b> ${PRESENTACION.quien}</p></div>
        <div class="botones"><a class="btn btn-primario" href=${urlRecurso(PRESENTACION.archivo)} download><${Ic} n="download" />Descargar</a></div>
      </div>
      <div class="modulos">${PRESENTACION.modulos.map(m => { const mod = m.modulo_app && MODULOS.find(x => x.id === m.modulo_app); return html`<div class="modulo"><b><span>${m.n}</span>${m.nombre}</b><small>Láminas ${m.laminas}${mod ? ` · En la app: ${mod.nombre}` : ''}</small></div>`; })}</div>
      <p style="margin:10px 0 0;font-size:12.5px;color:var(--texto-2)"><${Ic} n="info" /> ${PRESENTACION.nota} En la aplicación se llaman «etapas del ciclo de vida»; «fase del proyecto» es Fase 1, 2, 3…</p>
    </section>`}

    ${filtrados.length ? html`<div class="rejilla r-3">${filtrados.map(r => html`<${Tarjeta} r=${r} sesion=${sesion} />`)}</div>`
      : !verPresentacion && html`<div class="tarjeta"><${Vacio} titulo="No encontramos recursos" texto=${`Nada coincide con «${buscar}». Prueba con otra palabra o elige «Todas».`}><button class="btn" onClick=${() => { setBuscar(''); setCat('Todas'); }}>Ver todos</button><//></div>`}
  </main>`;
}
