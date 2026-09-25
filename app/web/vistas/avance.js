// Avance AWP: checklist de implementación por etapa del ciclo de vida.
import { html, useState } from '../vendor/preact-htm.js';
import { sb, q } from '../lib/db.js';
import { avisar, avisarError } from '../lib/estado.js';
import { Ic, Chip, Campo, Modal, Anillo, Vacio } from '../lib/ui.js';
import { fmt, hoyISO } from '../lib/fechas.js';
import { avancePorEtapa, porcentajeTotal } from '../lib/metricas.js';
import { urlRecurso } from '../lib/ui.js';

const ESTADOS = ['Pendiente', 'En curso', 'Completada', 'No aplica'];
const CLASE = { Pendiente: '', 'En curso': 'en-curso', Completada: 'completada', 'No aplica': 'no-aplica' };
const SIGUIENTE = { Pendiente: 'En curso', 'En curso': 'Completada', Completada: 'Pendiente', 'No aplica': 'Pendiente' };

function Detalle({ a, d, catalogos, onCerrar, recargar }) {
  const [f, setF] = useState({ ...a });
  const [e, setE] = useState({});
  const c = (k, v) => setF(prev => ({ ...prev, [k]: v }));
  const guardar = async () => {
    const err = {};
    if (f.estado === 'No aplica' && !f.comentario?.trim()) err.comentario = 'Explica por qué no aplica: así el % de avance refleja la realidad y queda registro de la decisión.';
    if (f.fecha_real && f.fecha_real > hoyISO()) err.fecha_real = 'La fecha real no puede ser futura. Si aún no se completó, usa la fecha objetivo.';
    setE(err);
    if (Object.keys(err).length) return;
    try {
      await q(sb.from('avance_actividades').update({ estado: f.estado, responsable_rol: f.responsable_rol || null, fecha_objetivo: f.fecha_objetivo || null,
        fecha_real: f.fecha_real || (f.estado === 'Completada' ? hoyISO() : null), evidencia: f.evidencia || null, comentario: f.comentario || null }).eq('id', a.id));
      avisar('Actividad actualizada.'); onCerrar(); recargar();
    } catch (err2) { avisarError(err2); }
  };
  return html`<${Modal} titulo=${a.cat.nombre} icono="list-checks" onCerrar=${onCerrar}
    pie=${html`<button class="btn" onClick=${onCerrar}>Cancelar</button><button class="btn btn-primario" onClick=${guardar}><${Ic} n="save" />Guardar</button>`}>
    <p style="color:var(--texto-2);margin:0 0 12px">${a.cat.descripcion}</p>
    ${(a.cat.hito || a.cat.plantilla) && html`<p style="font-size:13px;margin:0 0 12px">${a.cat.hito ? html`<${Chip} estado="info" icono="flag">Relacionada con el hito ${a.cat.hito}<//> ` : ''}${a.cat.plantilla ? html`<a href=${urlRecurso(a.cat.plantilla)} download><${Ic} n="download" /> ${a.cat.plantilla}</a>` : ''}</p>`}
    <div class="campos">
      <${Campo} etiqueta="Estado"><select value=${f.estado} onChange=${x => c('estado', x.target.value)}>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select><//>
      <${Campo} etiqueta="Responsable (rol)"><select value=${f.responsable_rol || ''} onChange=${x => c('responsable_rol', x.target.value)}><option value="">—</option>${catalogos.roles.map(r => html`<option value=${r.codigo}>${r.nombre}</option>`)}</select><//>
      <${Campo} etiqueta="Fecha objetivo"><input type="date" value=${f.fecha_objetivo || ''} onInput=${x => c('fecha_objetivo', x.target.value)} /><//>
      <${Campo} etiqueta="Fecha real" error=${e.fecha_real} ayuda="Si la marcas como completada sin fecha, se usa la de hoy."><input type="date" value=${f.fecha_real || ''} onInput=${x => c('fecha_real', x.target.value)} /><//>
      <${Campo} etiqueta="Evidencia" ancho ayuda="Documento, acta o enlace que demuestra que se hizo."><input value=${f.evidencia || ''} onInput=${x => c('evidencia', x.target.value)} placeholder="Ej.: Acta del taller IPP del 12/03" /><//>
      <${Campo} etiqueta="Comentario" ancho error=${e.comentario}><textarea rows="2" value=${f.comentario || ''} onInput=${x => c('comentario', x.target.value)}></textarea><//>
    </div>
  <//>`;
}

export function VistaAvance({ d, catalogos, recargar, params, puedeEditar }) {
  const etapas = avancePorEtapa(d.actividades, catalogos.etapas);
  const [sel, setSel] = useState(params.etapa || (etapas.find(e => e.total && e.pct < 100) || etapas[0]).etapa.codigo);
  const [detalle, setDetalle] = useState(null);
  const [filtro, setFiltro] = useState('');
  const etapa = catalogos.etapas.find(e => e.codigo === sel);
  const acts = d.actividades.filter(a => a.cat?.etapa === etapa.nombre && (!filtro || a.estado === filtro));
  const info = etapas.find(e => e.etapa.codigo === sel);

  const cambiar = async (a, estado) => {
    if (!puedeEditar) return;
    const antes = info.pct;
    try {
      await q(sb.from('avance_actividades').update({ estado, fecha_real: estado === 'Completada' ? (a.fecha_real || hoyISO()) : a.fecha_real }).eq('id', a.id));
      const nuevas = d.actividades.map(x => x.id === a.id ? { ...x, estado } : x);
      const despues = avancePorEtapa(nuevas, catalogos.etapas).find(e => e.etapa.codigo === sel).pct;
      if (antes < 100 && despues >= 100) avisar(`¡Completaste la etapa «${etapa.nombre}»! 🎉`);
      else avisar(estado === 'Completada' ? `«${a.cat.nombre}» completada.` : `«${a.cat.nombre}»: ${estado.toLowerCase()}.`);
      recargar();
    } catch (e) { avisarError(e); }
  };

  if (!d.actividades.length) return html`<div class="tarjeta"><${Vacio} titulo="El checklist está vacío" texto="Este proyecto no tiene cargadas las actividades del kit. Normalmente se cargan al crear el proyecto con el asistente." /></div>`;

  return html`
    <div class="tarjeta" style="margin-bottom:14px;display:flex;gap:16px;align-items:center;flex-wrap:wrap">
      <${Anillo} pct=${porcentajeTotal(d.actividades)} tam=${80} grosor=${8} />
      <div style="flex:1;min-width:220px"><h2 style="margin:0">Implementación AWP del proyecto: ${Math.round(porcentajeTotal(d.actividades))} %</h2>
        <p class="leer" style="margin:2px 0 0">${d.actividades.filter(a => a.estado === 'Completada').length} de ${d.actividades.filter(a => a.estado !== 'No aplica').length} actividades completadas. Toca el círculo de una actividad para cambiar su estado (pendiente → en curso → completada) o «Detalles» para registrar responsable, fechas y evidencia.</p></div>
    </div>
    <div class="pestanas-etapas" role="tablist">${etapas.map(e => html`<button class="pestana-etapa" role="tab" aria-selected=${e.etapa.codigo === sel} onClick=${() => setSel(e.etapa.codigo)}>
      <${Anillo} pct=${e.pct} tam=${46} grosor=${5} />${e.etapa.nombre}<small>${e.completadas}/${e.total}</small></button>`)}</div>
    <div class="tarjeta">
      <div class="barra-tabla" style="align-items:center"><h2 style="flex:1;margin:0">${etapa.nombre}: ${Math.round(info.pct)} %</h2>
        <label>Mostrar<select value=${filtro} onChange=${e => setFiltro(e.target.value)}><option value="">Todas</option>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select></label></div>
      ${!acts.length ? html`<p style="color:var(--texto-2)">No hay actividades con ese estado.</p>` : acts.map(a => html`<div class=${'actividad ' + CLASE[a.estado]}>
        <button class="marca" onClick=${() => cambiar(a, SIGUIENTE[a.estado])} disabled=${!puedeEditar} aria-label=${`${a.cat.nombre}: ${a.estado}. Cambiar a ${SIGUIENTE[a.estado]}`} title=${'Cambiar a ' + SIGUIENTE[a.estado]}>
          ${a.estado === 'Completada' && html`<${Ic} n="check" />`}</button>
        <div><h4>${a.cat.nombre}</h4><p>${a.cat.descripcion.replace(a.cat.nombre, '').trim().replace(/^[,:]\s*/, '') || a.cat.descripcion}</p>
          <div class="meta-act"><span>${a.actividad}</span>
            ${a.responsable_rol && html`<span><${Ic} n="user" /> ${catalogos.rol[a.responsable_rol]?.nombre}</span>`}
            ${a.fecha_objetivo && html`<span><${Ic} n="calendar" /> objetivo ${fmt(a.fecha_objetivo)}</span>`}
            ${a.fecha_real && html`<span><${Ic} n="check" /> ${fmt(a.fecha_real)}</span>`}
            ${a.cat.hito && html`<span><${Ic} n="flag" /> ${a.cat.hito}</span>`}
            ${a.evidencia && html`<span><${Ic} n="file" /> ${a.evidencia}</span>`}
            ${a.estado === 'No aplica' && a.comentario && html`<span>No aplica: ${a.comentario}</span>`}</div></div>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <${Chip} estado=${{ Completada: 'ok', 'En curso': 'atencion', Pendiente: 'neutro', 'No aplica': 'neutro' }[a.estado]}>${a.estado}<//>
          ${puedeEditar && html`<button class="btn btn-chico btn-texto" onClick=${() => setDetalle(a)}>Detalles</button>`}</div>
      </div>`)}
    </div>
    ${detalle && html`<${Detalle} a=${detalle} d=${d} catalogos=${catalogos} onCerrar=${() => setDetalle(null)} recargar=${recargar} />`}`;
}
