// Componentes de interfaz compartidos.
import { html, useEffect, useRef, useState } from '../vendor/preact-htm.js';
import { CONFIG } from '../config.js';
import { GLOSARIO } from '../datos/glosario.js';
import { RECURSOS, PRESENTACION } from '../datos/recursos.js';
import { actualizar, useEstado } from './estado.js';

export const Ic = ({ n, cls = 'ic', titulo, style }) => html`<svg class=${cls} style=${style} aria-hidden=${titulo ? null : 'true'}>${titulo ? html`<title>${titulo}</title>` : null}<use href=${'#i-' + n} /></svg>`;

const ESTADOS = { ok: ['chip-ok', 'check'], atencion: ['chip-atencion', 'triangle-alert'], critico: ['chip-critico', 'circle-alert'], neutro: ['chip-neutro', 'clock'], info: ['chip-neutro', 'info'] };
export const Chip = ({ estado = 'neutro', children, icono }) => {
  const [c, i] = ESTADOS[estado] || ESTADOS.neutro;
  return html`<span class=${'chip ' + c}><${Ic} n=${icono || i} />${children}</span>`;
};
export const colorEstado = s => ({ ok: 'var(--ok)', atencion: 'var(--atencion)', critico: 'var(--critico)', neutro: 'var(--neutro)' })[s] || 'var(--primario)';

export function Anillo({ pct = 0, tam = 64, grosor = 7, color, texto = true }) {
  const r = (tam - grosor) / 2, c = 2 * Math.PI * r;
  const [off, setOff] = useState(c);
  useEffect(() => { const t = requestAnimationFrame(() => setOff(c * (1 - Math.max(0, Math.min(100, pct)) / 100))); return () => cancelAnimationFrame(t); }, [pct, c]);
  const col = color || (pct >= 100 ? 'var(--ok)' : 'var(--primario)');
  return html`<span class="anillo" style=${`width:${tam}px;height:${tam}px`} role="img" aria-label=${`${Math.round(pct)} %`}>
    <svg width=${tam} height=${tam}><circle class="anillo-pista" cx=${tam / 2} cy=${tam / 2} r=${r} fill="none" stroke-width=${grosor} />
      <circle class="anillo-valor" cx=${tam / 2} cy=${tam / 2} r=${r} fill="none" stroke=${col} stroke-width=${grosor} stroke-linecap="round" stroke-dasharray=${c} stroke-dashoffset=${off} /></svg>
    ${texto && html`<span class="pct num" style=${`font-size:${tam > 60 ? 15 : 12}px`}>${Math.round(pct)} %</span>`}</span>`;
}

// ---------------------------------------------------------------- glosario
export function Termino({ t, children }) {
  const abrir = e => {
    e.stopPropagation(); e.preventDefault();
    const r = e.currentTarget.getBoundingClientRect();
    actualizar({ glosa: { t, x: Math.min(r.left, innerWidth - 326), y: Math.min(r.bottom + 8, innerHeight - 260) } });
  };
  return html`<span class="termino" tabindex="0" role="button" onClick=${abrir} onMouseEnter=${abrir} onKeyDown=${e => e.key === 'Enter' && abrir(e)}>${children || t}</span>`;
}
export function Glosa() {
  const { glosa } = useEstado();
  useEffect(() => {
    if (!glosa) return;
    const cerrar = e => { if (!e.target.closest?.('.glosa') && !e.target.closest?.('.termino')) actualizar({ glosa: null }); };
    const esc = e => e.key === 'Escape' && actualizar({ glosa: null });
    addEventListener('click', cerrar); addEventListener('keydown', esc);
    return () => { removeEventListener('click', cerrar); removeEventListener('keydown', esc); };
  }, [glosa]);
  if (!glosa) return null;
  const g = GLOSARIO[glosa.t] || {};
  return html`<div class="glosa" role="dialog" style=${`left:${glosa.x}px;top:${glosa.y}px`}>
    <h4><${Ic} n="graduation-cap" />${glosa.t}</h4>
    ${g.nombre && html`<p><b>${g.nombre}</b></p>`}
    ${g.definicion && html`<p>${g.definicion}</p>`}
    ${g.ejemplo && html`<div class="ej"><b>Ejemplo:</b> ${g.ejemplo}</div>`}
    ${g.pagina && html`<a href=${CONFIG.web + g.pagina} target="_blank" rel="noopener">Leer más en la web</a>`}
    <a href=${CONFIG.web + 'referencia/glosario/'} target="_blank" rel="noopener">Glosario</a>
  </div>`;
}

// ---------------------------------------------------------------- formularios
export function Campo({ etiqueta, req, ayuda, error, ancho, children, termino }) {
  return html`<div class=${'campo' + (ancho ? ' ancho' : '') + (error ? ' con-error' : '')}>
    <label>${termino ? html`<${Termino} t=${termino}>${etiqueta}<//>` : etiqueta}${req && html` <span class="req" aria-label="obligatorio">*</span>`}</label>
    ${children}
    ${error ? html`<span class="error" role="alert"><${Ic} n="circle-alert" />${error}</span>` : ayuda && html`<span class="ayuda">${ayuda}</span>`}
  </div>`;
}

export function Modal({ titulo, icono, onCerrar, pie, chico, children }) {
  const ref = useRef();
  useEffect(() => {
    const esc = e => e.key === 'Escape' && onCerrar?.();
    addEventListener('keydown', esc);
    ref.current?.querySelector('input, select, textarea')?.focus();
    return () => removeEventListener('keydown', esc);
  }, []);
  return html`<div class="fondo-modal" onMouseDown=${e => e.target === e.currentTarget && onCerrar?.()}>
    <div class=${'modal' + (chico ? ' modal-chico' : '')} role="dialog" aria-modal="true" aria-label=${titulo} ref=${ref}>
      <div class="modal-cab">${icono && html`<${Ic} n=${icono} cls="ic ic-lg" />`}<h2>${titulo}</h2>
        <button class="btn-ic" style="color:var(--texto-2)" onClick=${onCerrar} aria-label="Cerrar"><${Ic} n="x" /></button></div>
      <div class="modal-cuerpo">${children}</div>
      ${pie && html`<div class="modal-pie">${pie}</div>`}
    </div></div>`;
}

export function Confirmacion() {
  const { modal } = useEstado();
  if (!modal) return null;
  const fin = v => { modal.resolver(v); actualizar({ modal: null }); };
  return html`<${Modal} titulo=${modal.titulo} icono=${modal.peligro ? 'triangle-alert' : 'circle-help'} chico onCerrar=${() => fin(false)}
    pie=${html`<button class="btn" onClick=${() => fin(false)}>Cancelar</button>
      <button class=${'btn ' + (modal.peligro ? 'btn-peligro' : 'btn-primario')} onClick=${() => fin(true)}>${modal.boton}</button>`}>
    <p style="margin:0;color:var(--texto-2)">${modal.texto}</p><//>`;
}

export function Toast() {
  const { toast } = useEstado();
  if (!toast) return null;
  return html`<div class=${'toast' + (toast.tipo === 'error' ? ' error' : '')} role="status" key=${toast.id}>
    <span class="check"><${Ic} n=${toast.tipo === 'error' ? 'x' : 'check'} /></span><span>${toast.texto}</span></div>`;
}

export function celebrar() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const capa = document.createElement('div');
  capa.className = 'celebracion';
  const colores = ['#3f51b5', '#ffc107', '#0ca30c', '#eb6834', '#1baf7a', '#e87ba4'];
  for (let i = 0; i < 60; i++) {
    const p = document.createElement('i');
    p.style.left = Math.random() * 100 + 'vw';
    p.style.background = colores[i % colores.length];
    p.style.animationDelay = Math.random() * .5 + 's';
    p.style.transform = `rotate(${Math.random() * 180}deg)`;
    capa.appendChild(p);
  }
  document.body.appendChild(capa);
  setTimeout(() => capa.remove(), 2400);
}

// ---------------------------------------------------------------- vacío e ilustraciones
const ILUSTRACIONES = {
  proyectos: html`<svg class="ilustracion" viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 100h140" opacity=".35"/><rect x="22" y="48" width="34" height="52" rx="3"/><rect x="64" y="22" width="40" height="78" rx="3"/><rect x="112" y="60" width="28" height="40" rx="3"/>
    <path d="M30 58h6M44 58h6M30 70h6M44 70h6M72 32h8M88 32h8M72 46h8M88 46h8M72 60h8M88 60h8M120 70h4M130 70h4" opacity=".6"/>
    <path d="M104 22 124 8v14" stroke="var(--acento)"/><circle cx="130" cy="30" r="10" stroke="var(--acento)"/><path d="M126 30l3 3 5-6" stroke="var(--acento)"/></svg>`,
  hitos: html`<svg class="ilustracion" viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 80h136" opacity=".4"/>
    <circle cx="30" cy="80" r="6"/><circle cx="70" cy="80" r="6"/><circle cx="110" cy="80" r="6" stroke-dasharray="3 3"/><path d="M110 74V28l26 10-26 10" stroke="var(--acento)"/></svg>`,
  lista: html`<svg class="ilustracion" viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="36" y="10" width="88" height="94" rx="8"/>
    <path d="M52 34l5 5 9-10M52 58l5 5 9-10" stroke="var(--ok)"/><rect x="50" y="78" width="14" height="14" rx="3" opacity=".6"/><path d="M76 36h32M76 60h32M76 85h24" opacity=".6"/></svg>`,
  fases: html`<svg class="ilustracion" viewBox="0 0 160 110" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M80 14 140 42 80 70 20 42z"/><path d="M20 58l60 28 60-28" opacity=".6"/><path d="M20 74l60 28 60-28" opacity=".35"/></svg>`,
};
export function Vacio({ ilustracion = 'lista', titulo, texto, children }) {
  return html`<div class="vacio">${ILUSTRACIONES[ilustracion]}<h3>${titulo}</h3><p>${texto}</p>${children && html`<div class="acciones">${children}</div>`}</div>`;
}

// ---------------------------------------------------------------- ayuda y recursos del módulo
export function AyudaModulo({ modulo }) {
  const clave = 'awp-ayuda-' + modulo.id;
  const [abierta, setAbierta] = useState(() => { try { return localStorage.getItem(clave) !== 'cerrada'; } catch (e) { return true; } });
  const cambiar = v => { setAbierta(v); try { localStorage.setItem(clave, v ? 'abierta' : 'cerrada'); } catch (e) {} };
  if (!modulo.ayuda) return null;
  if (!abierta) return html`<button class="btn btn-texto btn-chico" style="margin:-6px 0 10px" onClick=${() => cambiar(true)}><${Ic} n="lightbulb" />¿Qué es esto y para qué sirve?</button>`;
  return html`<section class="ayuda-modulo" aria-label="Ayuda del módulo">
    <h3><${Ic} n="lightbulb" />¿Qué es esto y para qué sirve?
      <button class="btn-ic" style="margin-left:auto;color:var(--texto-3)" onClick=${() => cambiar(false)} aria-label="Ocultar ayuda" title="Ocultar ayuda"><${Ic} n="x" /></button></h3>
    <p>${modulo.ayuda.que}</p>
    <div class="fila-ayuda"><div class="caja"><b><${Ic} n="info" />Ejemplo</b>${modulo.ayuda.ejemplo}</div>
      <div class="caja"><b><${Ic} n="sparkles" />Consejo práctico</b>${modulo.ayuda.consejo}</div></div>
  </section>`;
}

export const urlRecurso = archivo => archivo.includes('/') && !archivo.endsWith('.pptx') ? CONFIG.web + archivo
  : archivo.endsWith('.pptx') ? CONFIG.web + archivo : CONFIG.web + 'implementacion/descargas/' + archivo;

export function Contexto({ modulo }) {
  const recs = (modulo.recursos || []).map(a => RECURSOS.find(r => r.archivo === a)).filter(Boolean);
  const mod = modulo.presentacion && PRESENTACION.modulos.find(m => m.n === modulo.presentacion);
  return html`<div class="contexto">
    ${recs.map(r => html`<a href=${urlRecurso(r.archivo)} download><${Ic} n=${r.tipo === 'xlsx' ? 'file-spreadsheet' : 'file-text'} />${r.tipo === 'xlsx' ? 'Plantilla' : 'Documento'}: ${r.nombre}</a>`)}
    ${mod && html`<a href="#/recursos"><${Ic} n="presentation" />Aprende: módulo ${mod.n} de la presentación («${mod.nombre}»)</a>`}
  </div>`;
}
