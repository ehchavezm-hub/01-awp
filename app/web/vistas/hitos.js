// Hitos AWP (H0–H10 por fase): línea de tiempo, tabla con filtros y edición.
import { html, useState, useEffect } from '../vendor/preact-htm.js';
import { sb, q } from '../lib/db.js';
import { avisar, avisarError, confirmar } from '../lib/estado.js';
import { Ic, Chip, Campo, Modal, Vacio, celebrar } from '../lib/ui.js';
import { LineaTiempo, estadoHito } from '../lib/graficos.js';
import { fmt, dias, hoyISO } from '../lib/fechas.js';
import { atrasados, proximos } from '../lib/metricas.js';

const ESTADOS = ['Pendiente', 'En curso', 'Cumplido', 'No aplica'];
const SITUACION = { ok: 'A tiempo', critico: 'Atrasado', atencion: 'Pendiente', neutro: 'No aplica' };

function FormHito({ hito, d, onCerrar, recargar }) {
  const nuevo = !hito.id;
  const [f, setF] = useState(hito);
  const [e, setE] = useState({});
  const c = (k, v) => setF(prev => ({ ...prev, [k]: v }));
  const guardar = async (extra = {}) => {
    const g = { ...f, ...extra };
    const err = {};
    if (!g.codigo?.trim()) err.codigo = 'Escribe un código, por ejemplo H11 o PC1 (puerta de control).';
    if (!g.nombre?.trim()) err.nombre = 'Escribe el nombre del hito.';
    if (g.estado === 'Cumplido' && !g.fecha_real) err.fecha_real = 'Para marcarlo como cumplido, indica la fecha real en que se cumplió.';
    if (g.fecha_real && g.fecha_real > hoyISO()) err.fecha_real = 'La fecha real no puede ser futura. Si aún no se cumple, deja el hito pendiente y ajusta la fecha plan.';
    if (g.estado === 'Cumplido' && !g.evidencia_real?.trim()) err.evidencia_real = `Anota la evidencia (${g.evidencia || 'documento o acta'}): un hito se cumple cuando existe la evidencia.`;
    setE(err);
    if (Object.keys(err).length) return;
    const datos = { proyecto_id: d.proyecto.id, fase_id: g.fase_id || null, codigo: g.codigo.trim(), nombre: g.nombre.trim(), criterio: g.criterio || null, evidencia: g.evidencia || null,
      aprueba: g.aprueba || null, fecha_plan: g.fecha_plan || null, fecha_real: g.fecha_real || null, estado: g.estado, comentario: [g.evidencia_real?.trim() && 'Evidencia: ' + g.evidencia_real.trim(), g.nota?.trim()].filter(Boolean).join(' · ') || null };
    try {
      if (nuevo) await q(sb.from('hitos').insert(datos)); else await q(sb.from('hitos').update(datos).eq('id', g.id));
      if (g.estado === 'Cumplido' && hito.estado !== 'Cumplido') { celebrar(); avisar(`¡Hito ${g.codigo} cumplido!`); } else avisar(nuevo ? 'Hito agregado.' : 'Hito actualizado.');
      onCerrar(); recargar();
    } catch (err2) { avisarError(err2); }
  };
  const vencido = f.fecha_plan && f.estado !== 'Cumplido' && f.fecha_plan < d.corte;
  return html`<${Modal} titulo=${nuevo ? 'Agregar hito' : `${hito.codigo} · ${hito.nombre}`} icono="flag" onCerrar=${onCerrar}
    pie=${html`<button class="btn" onClick=${onCerrar}>Cancelar</button>
      ${!nuevo && f.estado !== 'Cumplido' && html`<button class="btn btn-suave" onClick=${() => { setF({ ...f, estado: 'Cumplido', fecha_real: f.fecha_real || hoyISO() }); }}><${Ic} n="circle-check-big" />Marcar cumplido</button>`}
      <button class="btn btn-primario" onClick=${() => guardar()}><${Ic} n="save" />Guardar</button>`}>
    ${!nuevo && f.criterio && html`<div class="aviso aviso-info" style="margin-bottom:12px"><${Ic} n="target" /><div><b>Criterio de cumplimiento:</b> ${f.criterio}${f.evidencia ? html`<br /><b>Evidencia esperada:</b> ${f.evidencia}` : ''}${f.aprueba ? html`<br /><b>Aprueba:</b> ${f.aprueba}` : ''}</div></div>`}
    ${vencido && html`<div class="aviso aviso-error" style="margin-bottom:12px"><${Ic} n="circle-alert" />Este hito debía cumplirse el ${fmt(f.fecha_plan)} (hace ${dias(f.fecha_plan, d.corte)} días). Márcalo como cumplido con su evidencia o replanifica la fecha.</div>`}
    <div class="campos">
      ${nuevo && html`<${Campo} etiqueta="Código" req error=${e.codigo}><input value=${f.codigo} onInput=${x => c('codigo', x.target.value)} /><//>`}
      ${nuevo && html`<${Campo} etiqueta="Nombre" req error=${e.nombre}><input value=${f.nombre} onInput=${x => c('nombre', x.target.value)} /><//>`}
      <${Campo} etiqueta="Fase del proyecto"><select value=${f.fase_id || ''} onChange=${x => c('fase_id', x.target.value)} disabled=${!nuevo}><option value="">Programa (todas las fases)</option>${d.fases.map(fa => html`<option value=${fa.id}>Fase ${fa.numero} · ${fa.nombre}</option>`)}</select><//>
      <${Campo} etiqueta="Estado"><select value=${f.estado} onChange=${x => c('estado', x.target.value)}>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select><//>
      <${Campo} etiqueta="Fecha plan"><input type="date" value=${f.fecha_plan || ''} onInput=${x => c('fecha_plan', x.target.value)} /><//>
      <${Campo} etiqueta="Fecha real" error=${e.fecha_real}><input type="date" value=${f.fecha_real || ''} onInput=${x => c('fecha_real', x.target.value)} /><//>
      ${nuevo && html`<${Campo} etiqueta="Criterio de cumplimiento" ancho><textarea rows="2" value=${f.criterio || ''} onInput=${x => c('criterio', x.target.value)}></textarea><//>`}
      <${Campo} etiqueta="Evidencia registrada" ancho error=${e.evidencia_real} ayuda="Documento, acta o enlace que demuestra el cumplimiento."><input value=${f.evidencia_real || ''} onInput=${x => c('evidencia_real', x.target.value)} placeholder="Ej.: Plano de CWA rev. 1 aprobado el 15/03" /><//>
      <${Campo} etiqueta="Nota" ancho><input value=${f.nota || ''} onInput=${x => c('nota', x.target.value)} /><//>
    </div>
  <//>`;
}

// El comentario guarda «Evidencia: … · nota»: se separa para editarlo.
function paraEditar(h) {
  const partes = (h.comentario || '').split(' · ');
  const ev = partes.find(p => p.startsWith('Evidencia: '));
  return { ...h, evidencia_real: ev ? ev.slice(11) : '', nota: partes.filter(p => p !== ev).join(' · ') };
}

export function VistaHitos({ d, params, recargar, puedeEditar }) {
  const [fase, setFase] = useState(params.fase || '');
  const [estado, setEstado] = useState('');
  const [sit, setSit] = useState(params.filtro || '');
  const [buscar, setBuscar] = useState('');
  const [editando, setEditando] = useState(null);
  useEffect(() => { if (params.hito) { const h = d.hitos.find(x => x.id === params.hito); if (h) setEditando(paraEditar(h)); } }, [params.hito]);

  const nombreFase = id => { const f = d.fases.find(x => x.id === id); return f ? `Fase ${f.numero}` : 'Programa'; };
  const atr = new Set(atrasados(d.hitos, d.corte).map(h => h.id));
  const prox = new Set(proximos(d.hitos, d.corte, 30).map(h => h.id));
  const lista = d.hitos.filter(h => (!fase || (fase === 'programa' ? !h.fase_id : h.fase_id === fase)) && (!estado || h.estado === estado)
    && (!sit || (sit === 'atrasados' ? atr.has(h.id) : sit === 'proximos' ? prox.has(h.id) : h.estado === 'Cumplido'))
    && (!buscar || (h.codigo + ' ' + h.nombre).toLowerCase().includes(buscar.toLowerCase())));
  const cumplidos = d.hitos.filter(h => h.estado === 'Cumplido');
  const aTiempo = cumplidos.filter(h => !h.fecha_plan || h.fecha_real <= h.fecha_plan).length;
  const titulo = atr.size ? `${atr.size} hito${atr.size > 1 ? 's' : ''} atrasado${atr.size > 1 ? 's' : ''}; ${cumplidos.length} cumplido${cumplidos.length === 1 ? '' : 's'} (${aTiempo} a tiempo)`
    : `${cumplidos.length} de ${d.hitos.length} hitos cumplidos, ninguno atrasado`;

  if (!d.hitos.length) return html`<div class="tarjeta"><${Vacio} ilustracion="hitos" titulo="Aún no hay hitos" texto="Los hitos H0–H10 del kit marcan los puntos de control de la implementación: CWA definidas, Path of Construction aprobado, primer IWP liberado, cierre de fase…">
    ${puedeEditar && html`<button class="btn btn-primario" onClick=${() => setEditando({ codigo: '', nombre: '', estado: 'Pendiente', fase_id: d.fases[0]?.id || '' })}><${Ic} n="plus" />Agregar un hito</button>`}<//></div>`;

  return html`
    <div class="rejilla r-4 estadisticas" style="margin-bottom:16px">
      <button class="tarjeta estadistica" style="text-align:left" onClick=${() => setSit('')}><span class="etq"><${Ic} n="flag" />Hitos</span><span class="valor num">${d.hitos.length}</span><span class="delta">en ${d.fases.length} fases + programa</span></button>
      <button class="tarjeta estadistica" style="text-align:left" onClick=${() => setSit('cumplidos')}><span class="etq"><${Ic} n="circle-check-big" />Cumplidos</span><span class="valor num" style="color:var(--ok-texto)">${cumplidos.length}</span><span class="delta">${aTiempo} a tiempo</span></button>
      <button class="tarjeta estadistica" style="text-align:left" onClick=${() => setSit('atrasados')}><span class="etq"><${Ic} n="circle-alert" />Atrasados</span><span class="valor num" style=${atr.size ? 'color:var(--critico-texto)' : ''}>${atr.size}</span><span class="delta">toca para verlos</span></button>
      <button class="tarjeta estadistica" style="text-align:left" onClick=${() => setSit('proximos')}><span class="etq"><${Ic} n="clock" />Próximos 30 días</span><span class="valor num" style=${prox.size ? 'color:var(--atencion-texto)' : ''}>${prox.size}</span><span class="delta">prepara su evidencia</span></button>
    </div>

    <div class="tarjeta" style="margin-bottom:16px">
      <h2>${titulo}</h2>
      <p class="leer">Cómo leerlo: círculo vacío = fecha plan; círculo lleno = fecha real (verde a tiempo, rojo con atraso); rombo = pendiente (ámbar a tiempo, rojo atrasado). Toca un hito para editarlo.</p>
      <${LineaTiempo} hitos=${lista.map(h => ({ ...h, fase: nombreFase(h.fase_id) }))} corte=${d.corte} onClick=${h => setEditando(paraEditar(h))} />
    </div>

    <div class="tarjeta">
      <div class="barra-tabla">
        <label class="buscar">Buscar<input value=${buscar} onInput=${e => setBuscar(e.target.value)} placeholder="Código o nombre" /></label>
        <label>Fase<select value=${fase} onChange=${e => setFase(e.target.value)}><option value="">Todas</option><option value="programa">Programa</option>${d.fases.map(f => html`<option value=${f.id}>Fase ${f.numero}</option>`)}</select></label>
        <label>Estado<select value=${estado} onChange=${e => setEstado(e.target.value)}><option value="">Todos</option>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select></label>
        <label>Situación<select value=${sit} onChange=${e => setSit(e.target.value)}><option value="">Todas</option><option value="atrasados">Atrasados</option><option value="proximos">Próximos 30 días</option><option value="cumplidos">Cumplidos</option></select></label>
        ${puedeEditar && html`<button class="btn btn-primario" style="margin-left:auto" onClick=${() => setEditando({ codigo: '', nombre: '', estado: 'Pendiente', fase_id: fase && fase !== 'programa' ? fase : '' })}><${Ic} n="plus" />Agregar hito</button>`}
      </div>
      ${!lista.length ? html`<p style="color:var(--texto-2)">Ningún hito coincide con los filtros.</p>` : html`<div class="tabla-env"><table class="tabla-movil num">
        <thead><tr><th>Hito</th><th>Fase</th><th>Fecha plan</th><th>Fecha real</th><th>Situación</th><th></th></tr></thead>
        <tbody>${lista.map(h => { const est = estadoHito(h, d.corte); return html`<tr class=${atr.has(h.id) ? 'fila-atrasada' : ''} onClick=${() => setEditando(paraEditar(h))}>
          <td data-etq="Hito"><b>${h.codigo}</b> ${h.nombre}</td><td data-etq="Fase">${nombreFase(h.fase_id)}</td>
          <td data-etq="Plan">${fmt(h.fecha_plan)}</td><td data-etq="Real">${fmt(h.fecha_real)}</td>
          <td data-etq="Situación"><${Chip} estado=${est}>${h.estado === 'Cumplido' ? (est === 'ok' ? 'Cumplido a tiempo' : 'Cumplido con atraso') : atr.has(h.id) ? `Atrasado ${dias(h.fecha_plan, d.corte)} días` : h.estado === 'No aplica' ? 'No aplica' : h.estado}<//></td>
          <td class="celda-acciones">${puedeEditar && html`<button class="btn-ic" style="color:var(--texto-3)" onClick=${async ev => { ev.stopPropagation();
            if (await confirmar({ titulo: `¿Borrar el hito ${h.codigo}?`, texto: 'Se quitará de la línea de tiempo y de los indicadores. Esta acción no se puede deshacer.', boton: 'Borrar hito', peligro: true })) {
              try { await q(sb.from('hitos').delete().eq('id', h.id)); avisar('Hito borrado.'); recargar(); } catch (er) { avisarError(er); } } }} aria-label=${'Borrar ' + h.codigo}><${Ic} n="trash-2" /></button>`}</td></tr>`; })}</tbody></table></div>`}
    </div>
    ${editando && puedeEditar && html`<${FormHito} hito=${editando} d=${d} onCerrar=${() => { setEditando(null); if (params.hito) history.replaceState(null, '', location.hash.split('?')[0]); }} recargar=${recargar} />`}`;
}
