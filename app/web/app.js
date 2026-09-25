// Aplicación AWP: rutas, sesión y estructura general de la pantalla.
import { html, render, useEffect, useState } from './vendor/preact-htm.js';
import { SPRITE } from './lib/iconos.js';
import { sb, q, cargarCatalogos, limpiarCatalogos } from './lib/db.js';
import { actualizar, obtener, useEstado } from './lib/estado.js';
import { Ic, Glosa, Toast, Confirmacion } from './lib/ui.js';
import { Tour, iniciarTour } from './lib/guia.js';
import { leerRuta, ir } from './lib/rutas.js';
import { VistaEntrar, VistaNuevaClave } from './vistas/entrar.js';
import { VistaPortafolio } from './vistas/portafolio.js';
import { VistaAsistente } from './vistas/asistente.js';
import { VistaProyecto } from './vistas/proyecto.js';
import { VistaRecursos } from './vistas/recursos.js';

document.body.insertAdjacentHTML('afterbegin', SPRITE);

// ---------------------------------------------------------------- rutas
function useRuta() {
  const [ruta, setRuta] = useState(leerRuta());
  useEffect(() => { const f = () => { setRuta(leerRuta()); }; addEventListener('hashchange', f); return () => removeEventListener('hashchange', f); }, []);
  return ruta;
}
const PUBLICAS = ['entrar', 'recursos', 'nueva-clave'];

// ---------------------------------------------------------------- tema
function oscuroActivo() {
  const t = document.documentElement.dataset.theme;
  return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
}
function BotonTema() {
  const [oscuro, setOscuro] = useState(oscuroActivo());
  const cambiar = () => {
    const nuevo = oscuroActivo() ? 'light' : 'dark';
    document.documentElement.dataset.theme = nuevo;
    try { localStorage.setItem('awp-tema', nuevo); } catch (e) {}
    setOscuro(nuevo === 'dark');
  };
  return html`<button class="btn-ic" data-tour="tema" onClick=${cambiar} title="Cambiar a modo ${oscuro ? 'claro' : 'oscuro'}" aria-label="Cambiar a modo ${oscuro ? 'claro' : 'oscuro'}"><${Ic} n=${oscuro ? 'sun' : 'moon'} /></button>`;
}

// ---------------------------------------------------------------- cabecera
function MenuUsuario({ sesion }) {
  const [abierto, setAbierto] = useState(false);
  useEffect(() => {
    if (!abierto) return;
    const f = e => !e.target.closest('.menu-usuario') && setAbierto(false);
    addEventListener('click', f); return () => removeEventListener('click', f);
  }, [abierto]);
  const correo = sesion.user.email || '';
  const salir = async () => { await sb.auth.signOut(); limpiarCatalogos(); ir('/entrar'); };
  return html`<div class="menu-usuario">
    <button class="avatar" onClick=${() => setAbierto(!abierto)} aria-haspopup="menu" aria-expanded=${abierto} title="Tu cuenta">${correo.slice(0, 2).toUpperCase()}</button>
    ${abierto && html`<div class="desplegable" role="menu">
      <div class="quien">Sesión iniciada como<br /><b>${correo}</b></div>
      <button role="menuitem" onClick=${() => { setAbierto(false); ir('/portafolio'); setTimeout(iniciarTour, 300); }}><${Ic} n="circle-help" />Ver el recorrido guiado</button>
      <a role="menuitem" href="#/recursos" onClick=${() => setAbierto(false)}><${Ic} n="library" />Recursos del kit</a>
      <button role="menuitem" onClick=${salir}><${Ic} n="log-out" />Cerrar sesión</button>
    </div>`}
  </div>`;
}

function Cabecera({ sesion, ruta }) {
  const seccion = ruta.partes[0];
  const actual = s => seccion === s ? 'page' : null;
  return html`<header class="cabecera"><div class="cabecera-in">
    <a class="marca" href="#/portafolio" data-tour="marca"><${Ic} n="package" cls="ic ic-lg" />AWP <small>Implementación</small></a>
    <nav class="nav-sup" aria-label="Principal">
      ${sesion && html`<a href="#/portafolio" data-tour="portafolio" aria-current=${actual('portafolio') || (seccion === 'p' ? 'page' : null)}><${Ic} n="layout-grid" />Portafolio</a>`}
      <a href="#/recursos" data-tour="recursos" aria-current=${actual('recursos')}><${Ic} n="library" />Recursos</a>
    </nav>
    <span style="margin-left:auto"></span>
    <${BotonTema} />
    ${sesion && html`<button class="btn-ic" data-tour="ayuda" onClick=${() => { if (seccion !== 'portafolio') ir('/portafolio'); setTimeout(iniciarTour, 300); }} title="Recorrido guiado" aria-label="Iniciar el recorrido guiado"><${Ic} n="circle-help" /></button>`}
    ${sesion ? html`<${MenuUsuario} sesion=${sesion} />` : seccion !== 'entrar' && html`<a class="btn btn-chico" style="color:var(--texto)" href="#/entrar"><${Ic} n="log-out" />Iniciar sesión</a>`}
  </div></header>`;
}

function BarraInferior({ sesion, ruta }) {
  if (!sesion) return null;
  const s = ruta.partes[0];
  let ultimo = null; try { ultimo = localStorage.getItem('awp-ultimo-proyecto'); } catch (e) {}
  return html`<nav class="barra-inferior" aria-label="Navegación inferior">
    <a href="#/portafolio" aria-current=${s === 'portafolio' ? 'page' : null}><${Ic} n="layout-grid" cls="ic ic-lg" />Inicio</a>
    ${ultimo && html`<a href=${'#/p/' + ultimo} aria-current=${s === 'p' ? 'page' : null}><${Ic} n="building-2" cls="ic ic-lg" />Proyecto</a>`}
    <a href="#/proyectos/nuevo" aria-current=${s === 'proyectos' ? 'page' : null}><${Ic} n="plus" cls="ic ic-lg" />Nuevo</a>
    <a href="#/recursos" aria-current=${s === 'recursos' ? 'page' : null}><${Ic} n="library" cls="ic ic-lg" />Recursos</a>
    <a href="#" onClick=${e => { e.preventDefault(); ir('/portafolio'); setTimeout(iniciarTour, 300); }}><${Ic} n="circle-help" cls="ic ic-lg" />Ayuda</a>
  </nav>`;
}

// ---------------------------------------------------------------- aplicación
function App() {
  const { sesion, catalogos, recuperando } = useEstado();
  const ruta = useRuta();
  const [error, setError] = useState(null);

  useEffect(() => {
    sb.auth.getSession().then(({ data }) => actualizar({ sesion: data.session || null }));
    const { data } = sb.auth.onAuthStateChange((evento, s) => {
      actualizar({ sesion: s || null });
      if (evento === 'PASSWORD_RECOVERY') { actualizar({ recuperando: true }); ir('/nueva-clave'); }
    });
    return () => data.subscription.unsubscribe();
  }, []);

  // Catálogos y perfil al iniciar sesión; recorrido guiado la primera vez.
  useEffect(() => {
    if (!sesion) return;
    cargarCatalogos().then(c => actualizar({ catalogos: c })).catch(e => setError(e));
    q(sb.from('perfiles').select('*').eq('id', sesion.user.id).maybeSingle()).then(p => {
      actualizar({ perfil: p });
      let visto = false; try { visto = localStorage.getItem('awp-tour-visto') === '1'; } catch (e) {}
      if (!p?.tour_visto && !visto) setTimeout(() => { if (leerRuta().partes[0] === 'portafolio') iniciarTour(); }, 900);
    }).catch(() => {});
  }, [sesion?.user?.id]);

  const seccion = ruta.partes[0];
  if (sesion === undefined) return html`<div class="cargando-inicial"><span class="girador"></span>Cargando…</div>`;
  if (!sesion && !PUBLICAS.includes(seccion)) {
    const volver = location.hash.slice(1);
    if (!volver.startsWith('/entrar')) ir('/entrar' + (volver && volver !== '/portafolio' ? '?volver=' + encodeURIComponent(volver) : ''));
    return null;
  }
  if (sesion && seccion === 'entrar' && !recuperando) { ir(ruta.params.volver || '/portafolio'); return null; }

  let vista;
  if (seccion === 'entrar') vista = html`<${VistaEntrar} ruta=${ruta} />`;
  else if (seccion === 'nueva-clave') vista = html`<${VistaNuevaClave} />`;
  else if (seccion === 'recursos') vista = html`<${VistaRecursos} sesion=${sesion} />`;
  else if (error) vista = html`<main><div class="aviso aviso-error"><${Ic} n="circle-alert" /><div><b>${error.message}</b><br />${error.ayuda}</div></div></main>`;
  else if (!catalogos) vista = html`<div class="cargando-inicial"><span class="girador"></span>Cargando catálogos del kit…</div>`;
  else if (seccion === 'proyectos' && ruta.partes[1] === 'nuevo') vista = html`<${VistaAsistente} />`;
  else if (seccion === 'p' && ruta.partes[1]) vista = html`<${VistaProyecto} key=${ruta.partes[1]} id=${ruta.partes[1]} ruta=${ruta} />`;
  else vista = html`<${VistaPortafolio} ruta=${ruta} />`;

  return html`<${Cabecera} sesion=${sesion} ruta=${ruta} />
    ${vista}
    <${BarraInferior} sesion=${sesion} ruta=${ruta} />
    <${Glosa} /><${Toast} /><${Confirmacion} /><${Tour} />`;
}

render(html`<${App} />`, document.getElementById('app'));
