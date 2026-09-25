// Gráficos SVG ligeros (estilo validado en la maqueta de la Etapa 1).
import { html, useEffect, useRef, useState } from '../vendor/preact-htm.js';
import { aFecha, fmt, dias } from './fechas.js';

// ---------------------------------------------------------------- tooltip único
let tip;
function elTip() {
  if (!tip) { tip = document.createElement('div'); tip.id = 'tooltip'; tip.setAttribute('role', 'tooltip'); document.body.appendChild(tip); }
  return tip;
}
export function mostrarTip(e, contenido) {
  const t = elTip();
  t.innerHTML = contenido; t.style.opacity = 1;
  const x = Math.min(e.clientX + 14, innerWidth - t.offsetWidth - 8);
  const y = e.clientY + 14 + t.offsetHeight > innerHeight ? e.clientY - t.offsetHeight - 10 : e.clientY + 14;
  t.style.left = x + 'px'; t.style.top = y + 'px';
}
export function ocultarTip() { if (tip) tip.style.opacity = 0; }
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const conTip = contenido => ({ onMouseMove: e => mostrarTip(e, contenido), onMouseLeave: ocultarTip, onTouchStart: e => mostrarTip(e.touches[0], contenido) });

// Ancho real del contenedor (se redibuja al cambiar el tamaño).
function useAncho(min = 260) {
  const ref = useRef(); const [w, setW] = useState(600);
  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setW(Math.max(min, Math.floor(e.contentRect.width))));
    ro.observe(ref.current); return () => ro.disconnect();
  }, []);
  return [ref, w];
}
const corto = (t, n) => t.length > n ? t.slice(0, n - 1) + '…' : t;

// ---------------------------------------------------------------- barras horizontales
export function BarrasH({ datos, max = 100, sufijo = ' %', etiquetaAncho = 150, aria }) {
  const [ref, W] = useAncho();
  const fila = 34, izq = W < 480 ? Math.min(100, etiquetaAncho) : etiquetaAncho, der = 52, H = datos.length * fila + 22;
  const x = v => izq + (W - izq - der) * Math.max(0, v) / max;
  const nc = Math.floor(izq / 7);
  return html`<div ref=${ref}><svg class="grafico" viewBox=${`0 0 ${W} ${H}`} width=${W} height=${H} role="img" aria-label=${aria}>
    ${[0, .25, .5, .75, 1].map(t => html`<line class="grilla" x1=${x(t * max)} x2=${x(t * max)} y1="0" y2=${H - 18} /><text x=${x(t * max)} y=${H - 4} text-anchor="middle">${Math.round(t * max)}${sufijo}</text>`)}
    ${datos.map((d, i) => { const y = i * fila + 6; return html`<g>
      <text x=${izq - 8} y=${y + 13} text-anchor="end">${corto(d.etq, nc)}</text>
      <rect class="marca-dato" x=${izq} y=${y} width=${Math.max(x(d.valor) - izq, 2)} height="18" rx="4" fill=${d.color || 'var(--primario)'}
        onClick=${d.onClick} style=${d.onClick ? 'cursor:pointer' : ''} ...${conTip(`<b>${esc(d.etq)}</b>${esc(d.tip || `${Math.round(d.valor)}${sufijo}`)}`)} />
      ${d.meta != null && html`<line class="meta" x1=${x(d.meta)} x2=${x(d.meta)} y1=${y - 3} y2=${y + 21} />`}
      <text class="valor-txt num" x=${x(Math.max(d.valor, d.meta ?? 0)) + 6} y=${y + 13}>${Math.round(d.valor)}${sufijo}</text></g>`; })}
  </svg></div>`;
}

// ---------------------------------------------------------------- línea de tiempo de hitos
export const estadoHito = (h, corte) => h.estado === 'Cumplido'
  ? (h.fecha_plan && h.fecha_real > h.fecha_plan ? 'critico' : 'ok')
  : h.estado === 'No aplica' ? 'neutro'
  : (h.fecha_plan && h.fecha_plan < corte ? 'critico' : 'atencion');

export function LineaTiempo({ hitos, corte, onClick }) {
  const [ref, W] = useAncho(300);
  const conFecha = hitos.filter(h => h.fecha_plan || h.fecha_real);
  if (!conFecha.length) return html`<div ref=${ref} style="color:var(--texto-2);font-size:13px">Aún no hay hitos con fecha.</div>`;
  const fechas = conFecha.flatMap(h => [h.fecha_plan, h.fecha_real]).filter(Boolean).concat(corte).sort();
  const ini = fechas[0], fin = fechas.at(-1), span = Math.max(dias(ini, fin), 30);
  const iz = 18, de = 18, H = 100, yy = 50;
  const x = f => iz + (W - iz - de) * dias(ini, f) / span;
  const meses = [];
  const f0 = aFecha(ini); f0.setDate(1);
  const paso = Math.max(1, Math.ceil(span / 30 / (W < 500 ? 4 : 10)));
  for (let f = new Date(f0); f <= aFecha(fin); f.setMonth(f.getMonth() + paso)) {
    const iso = f.toISOString().slice(0, 10);
    if (iso >= ini) meses.push(iso);
  }
  return html`<div ref=${ref}><svg class="grafico" viewBox=${`0 0 ${W} ${H}`} width=${W} height=${H} role="img" aria-label="Línea de tiempo de hitos">
    <line class="eje" x1=${iz} x2=${W - de} y1=${yy} y2=${yy} />
    ${meses.map(m => html`<line class="grilla" x1=${x(m)} x2=${x(m)} y1=${yy - 5} y2=${yy + 5} /><text x=${x(m)} y=${yy + 22} text-anchor="middle">${aFecha(m).toLocaleDateString('es', { month: 'short', year: '2-digit' }).replace('.', '')}</text>`)}
    <line x1=${x(corte)} x2=${x(corte)} y1="6" y2=${yy + 30} stroke="var(--primario)" stroke-width="1.5" /><text x=${x(corte) + 5} y=${yy + 40} style="fill:var(--primario);font-weight:600">Hoy</text>
    ${conFecha.map((h, i) => {
      const est = estadoHito(h, corte), col = { ok: 'var(--ok)', critico: 'var(--critico)', atencion: 'var(--atencion)', neutro: 'var(--neutro)' }[est];
      const tipo = `<b>${esc(h.codigo)} ${esc(h.nombre)}</b>Plan: ${fmt(h.fecha_plan)}${h.fecha_real ? ' · Real: ' + fmt(h.fecha_real) : ' · pendiente'}${h.fase ? '<br>' + esc(h.fase) : ''}`;
      const xr = x(h.fecha_real || h.fecha_plan);
      return html`<g style=${onClick ? 'cursor:pointer' : ''} onClick=${() => onClick?.(h)} ...${conTip(tipo)}>
        ${h.fecha_real && h.fecha_plan && html`<circle cx=${x(h.fecha_plan)} cy=${yy} r="6" fill="var(--superficie)" stroke="var(--texto-2)" stroke-width="1.5" />`}
        ${h.fecha_real ? html`<circle class="marca-dato" cx=${xr} cy=${yy} r="6.5" fill=${col} stroke="var(--superficie)" stroke-width="2" />`
          : html`<rect class="marca-dato" x=${xr - 6} y=${yy - 6} width="12" height="12" transform=${`rotate(45 ${xr} ${yy})`} fill=${col} stroke="var(--superficie)" stroke-width="2" />`}
        ${(W >= 500 || i % 2 === 0) && html`<text x=${xr} y=${yy - 14 - (i % 2) * 13} text-anchor="middle" style="fill:var(--texto);font-weight:600">${h.codigo}</text>`}
      </g>`;
    })}
  </svg></div>`;
}

// ---------------------------------------------------------------- tendencia
export function Tendencia({ puntos, color = 'var(--primario)', sufijo = '', aria }) {
  const [ref, W] = useAncho();
  const H = 170, iz = 34, ab = 22, ar = 22, de = 14;
  if (puntos.length < 2) return html`<div ref=${ref} style="color:var(--texto-2);font-size:13px;padding:8px 0">La tendencia aparece a partir de la segunda semana: cada semana que abras el proyecto se guarda una foto de los indicadores.</div>`;
  const max = Math.max(...puntos.map(p => p.valor), 1) * 1.15;
  const x = i => iz + (W - iz - de) * i / (puntos.length - 1), y = v => ar + (H - ar - ab) * (1 - v / max);
  const pts = puntos.map((p, i) => `${x(i)},${y(p.valor)}`).join(' ');
  const marcas = [0, max / 2, max].map(v => Math.round(v));
  return html`<div ref=${ref}><svg class="grafico" viewBox=${`0 0 ${W} ${H}`} width=${W} height=${H} role="img" aria-label=${aria}>
    ${marcas.map(t => html`<line class="grilla" x1=${iz} x2=${W - de} y1=${y(t)} y2=${y(t)} /><text x=${iz - 6} y=${y(t) + 4} text-anchor="end">${t}</text>`)}
    ${puntos.map((p, i) => (i % Math.ceil(puntos.length / 6) === 0 || i === puntos.length - 1) && html`<text x=${x(i)} y=${H - 5} text-anchor="middle">${fmt(p.fecha).slice(0, 5)}</text>`)}
    <polyline points=${pts} fill="none" stroke=${color} stroke-width="2" stroke-linejoin="round" />
    ${puntos.map((p, i) => html`<circle class="marca-dato" cx=${x(i)} cy=${y(p.valor)} r=${i === puntos.length - 1 ? 5 : 3.5} fill=${color} stroke="var(--superficie)" stroke-width="2"
      ...${conTip(`<b>Semana del ${fmt(p.fecha)}</b>${Math.round(p.valor * 10) / 10}${sufijo}`)} />`)}
  </svg></div>`;
}
