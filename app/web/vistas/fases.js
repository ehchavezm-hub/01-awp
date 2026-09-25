// Fases del proyecto: lista, alta, edición y borrado.
import { html, useState } from '../vendor/preact-htm.js';
import { sb, q } from '../lib/db.js';
import { avisar, avisarError, confirmar, obtener } from '../lib/estado.js';
import { Ic, Chip, Campo, Modal, Vacio, Termino } from '../lib/ui.js';
import { fmt, dias } from '../lib/fechas.js';
import { atrasados } from '../lib/metricas.js';

const COLOR = n => ['var(--f1)', 'var(--f2)', 'var(--f3)'][(n - 1) % 3];
const ESTADOS = ['Planificada', 'En ejecución', 'Cerrada'];
const PLAZOS = [['sem_iwp_iniciado', 'IWP iniciado'], ['sem_identificadas', 'Restricciones identificadas'], ['sem_asignadas', 'Asignadas'], ['sem_levantadas', 'Levantadas'], ['sem_liberacion', 'Liberación'], ['backlog_meta_sem', 'Meta de backlog']];
const ESTADO_CHIP = { Planificada: 'neutro', 'En ejecución': 'atencion', Cerrada: 'ok' };

function validar(f, proyecto, otras) {
  const e = {};
  if (!f.nombre?.trim()) e.nombre = 'Ponle un nombre a la fase, por ejemplo «Instalación principal».';
  if (!(Number(f.numero) > 0)) e.numero = 'Usa un número mayor que cero.';
  else if (otras.some(o => o.numero === Number(f.numero))) e.numero = `Ya existe la Fase ${f.numero}. Usa otro número.`;
  if (f.fecha_inicio && f.fecha_fin && f.fecha_fin <= f.fecha_inicio) e.fecha_fin = 'La fecha de fin debe ser posterior al inicio.';
  if (f.fecha_inicio && proyecto.fecha_inicio && f.fecha_inicio < proyecto.fecha_inicio) e.fecha_inicio = `El proyecto empieza el ${fmt(proyecto.fecha_inicio)}: la fase no puede empezar antes.`;
  if (f.fecha_fin && proyecto.fecha_fin && f.fecha_fin > proyecto.fecha_fin) e.fecha_fin = `El proyecto termina el ${fmt(proyecto.fecha_fin)}: la fase no puede terminar después.`;
  const p = PLAZOS.slice(0, 5).map(([k]) => Number(f[k]));
  if (p.some(x => !(x >= 0))) e.plazos = 'Completa los cinco plazos en semanas (números desde 0).';
  else if (!p.every((x, i) => i === 0 || p[i - 1] >= x)) e.plazos = 'Los plazos van de mayor a menor: IWP iniciado ≥ identificadas ≥ asignadas ≥ levantadas ≥ liberación.';
  return e;
}

export function FormFase({ fase, d, onCerrar, recargar }) {
  const nueva = !fase.id;
  const [f, setF] = useState(fase);
  const [e, setE] = useState({});
  const [guardando, setGuardando] = useState(false);
  const c = (k, v) => setF(prev => ({ ...prev, [k]: v }));
  const guardar = async () => {
    const err = validar(f, d.proyecto, d.fases.filter(o => o.id !== f.id));
    setE(err);
    if (Object.keys(err).length) return;
    setGuardando(true);
    const datos = { proyecto_id: d.proyecto.id, numero: Number(f.numero), nombre: f.nombre.trim(), alcance: f.alcance || null, estado: f.estado,
      fecha_inicio: f.fecha_inicio || null, fecha_fin: f.fecha_fin || null, madurez_objetivo: f.madurez_objetivo ? Number(f.madurez_objetivo) : null,
      hh_estimadas: f.hh_estimadas === '' || f.hh_estimadas == null ? null : Number(f.hh_estimadas), pico_personal: f.pico_personal === '' || f.pico_personal == null ? null : Number(f.pico_personal),
      ...Object.fromEntries(PLAZOS.map(([k]) => [k, Number(f[k])])) };
    try {
      if (nueva) {
        const creada = await q(sb.from('fases').insert(datos).select().single());
        // Hitos H1–H10 del kit para la fase nueva (sin fecha: se planifican en Hitos).
        const cat = obtener().catalogos.hitos.filter(h => h.codigo !== 'H0');
        await q(sb.from('hitos').insert(cat.map(h => ({ proyecto_id: d.proyecto.id, fase_id: creada.id, codigo: h.codigo, nombre: h.nombre, criterio: h.criterio, evidencia: h.evidencia, aprueba: h.aprueba }))));
        avisar(`Fase ${datos.numero} creada, con sus hitos H1–H10 listos para planificar.`);
      } else {
        await q(sb.from('fases').update(datos).eq('id', f.id));
        avisar(`Fase ${datos.numero} actualizada.`);
      }
      onCerrar(); recargar();
    } catch (err) { setGuardando(false); avisarError(err); }
  };
  return html`<${Modal} titulo=${nueva ? 'Agregar fase' : `Editar la Fase ${fase.numero}`} icono="layers" onCerrar=${onCerrar}
    pie=${html`<button class="btn" onClick=${onCerrar}>Cancelar</button><button class="btn btn-primario" onClick=${guardar} disabled=${guardando}><${Ic} n="save" />${nueva ? 'Agregar fase' : 'Guardar cambios'}</button>`}>
    <div class="campos">
      <${Campo} etiqueta="Número" req error=${e.numero}><input type="number" min="1" value=${f.numero} onInput=${x => c('numero', x.target.value)} /><//>
      <${Campo} etiqueta="Estado"><select value=${f.estado} onChange=${x => c('estado', x.target.value)}>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select><//>
      <${Campo} etiqueta="Nombre" req ancho error=${e.nombre}><input value=${f.nombre} onInput=${x => c('nombre', x.target.value)} /><//>
      <${Campo} etiqueta="Alcance" ancho><textarea rows="2" value=${f.alcance || ''} onInput=${x => c('alcance', x.target.value)}></textarea><//>
      <${Campo} etiqueta="Inicio" error=${e.fecha_inicio}><input type="date" value=${f.fecha_inicio || ''} onInput=${x => c('fecha_inicio', x.target.value)} /><//>
      <${Campo} etiqueta="Fin" error=${e.fecha_fin}><input type="date" value=${f.fecha_fin || ''} onInput=${x => c('fecha_fin', x.target.value)} /><//>
      <${Campo} etiqueta="Madurez AWP objetivo" ayuda="1 inicial · 2 básico · 3 integrado · 4 optimizado · 5 excelencia"><select value=${f.madurez_objetivo || ''} onChange=${x => c('madurez_objetivo', x.target.value)}><option value="">—</option>${[1, 2, 3, 4, 5].map(n => html`<option value=${n}>${n}</option>`)}</select><//>
      <${Campo} etiqueta="HH directas estimadas"><input type="number" min="0" value=${f.hh_estimadas ?? ''} onInput=${x => c('hh_estimadas', x.target.value)} /><//>
      <${Campo} etiqueta="Pico de personal" ayuda="Sirve para dimensionar planificadores: 1 por cada 50 trabajadores."><input type="number" min="0" value=${f.pico_personal ?? ''} onInput=${x => c('pico_personal', x.target.value)} /><//>
    </div>
    <h3 style="font-size:14.5px;margin:16px 0 6px">Plazos de liberación de <${Termino} t="IWP" /> (semanas antes de la ejecución)</h3>
    <div class="plazos">${PLAZOS.map(([k, t]) => html`<${Campo} etiqueta=${t}><input type="number" min="0" max="52" value=${f[k]} onInput=${x => c(k, x.target.value)} /><//>`)}</div>
    ${e.plazos ? html`<div class="campo con-error"><span class="error"><${Ic} n="circle-alert" />${e.plazos}</span></div>` : html`<span style="font-size:12px;color:var(--texto-2)">Referencia del kit: 12/10/8/4/2 semanas en fases grandes; 8/6/5/3/2 en fases más simples.</span>`}
  <//>`;
}

export function VistaFases({ d, recargar, puedeEditar }) {
  const [editando, setEditando] = useState(null);
  const nueva = () => {
    const ultima = d.fases.at(-1);
    setEditando({ numero: (ultima?.numero || 0) + 1, nombre: '', alcance: '', estado: 'Planificada', fecha_inicio: ultima?.fecha_fin || d.proyecto.fecha_inicio || '', fecha_fin: d.proyecto.fecha_fin || '',
      madurez_objetivo: 3, sem_iwp_iniciado: 8, sem_identificadas: 6, sem_asignadas: 5, sem_levantadas: 3, sem_liberacion: 2, backlog_meta_sem: 2 });
  };
  const borrar = async f => {
    const ok = await confirmar({ titulo: `¿Borrar la Fase ${f.numero}?`, texto: `Se borrarán también sus hitos y los datos de la fase. Esta acción no se puede deshacer. Si la fase ya tiene CWA o paquetes, no se podrá borrar.`, boton: 'Borrar fase', peligro: true });
    if (!ok) return;
    try { await q(sb.from('fases').delete().eq('id', f.id)); avisar(`Fase ${f.numero} borrada.`); recargar(); } catch (e) { avisarError(e); }
  };
  return html`
    ${puedeEditar && d.fases.length > 0 && html`<div style="display:flex;justify-content:flex-end;margin-bottom:12px"><button class="btn btn-primario" onClick=${nueva}><${Ic} n="plus" />Agregar fase</button></div>`}
    ${!d.fases.length ? html`<div class="tarjeta"><${Vacio} ilustracion="fases" titulo="Aún no hay fases"
        texto="Una fase es una parte de la ejecución del proyecto (por ejemplo, obras tempranas, instalación principal, ampliación). Cada fase recorre todas las etapas del ciclo de vida y tiene sus propios hitos.">
        ${puedeEditar && html`<button class="btn btn-primario" onClick=${nueva}><${Ic} n="plus" />Agregar la primera fase</button>`}<//></div>`
    : html`<div class="rejilla r-3">${d.fases.map(f => {
      const hs = d.hitos.filter(h => h.fase_id === f.id);
      const cumplidos = hs.filter(h => h.estado === 'Cumplido').length, atr = atrasados(hs, d.corte).length;
      return html`<article class="tarjeta" style=${'border-top:4px solid ' + COLOR(f.numero)}>
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px"><span class="chip chip-fase" style=${'background:' + COLOR(f.numero)}>Fase ${f.numero}</span><${Chip} estado=${ESTADO_CHIP[f.estado]}>${f.estado}<//></div>
        <h3 style="margin:0 0 4px;font-size:16px">${f.nombre}</h3>
        ${f.alcance && html`<p style="margin:0 0 8px;color:var(--texto-2);font-size:13px">${f.alcance}</p>`}
        <dl style="display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:13px;margin:0 0 10px">
          <dt style="color:var(--texto-3)">Fechas</dt><dd style="margin:0">${fmt(f.fecha_inicio)} → ${fmt(f.fecha_fin)}${f.fecha_inicio && f.fecha_fin ? ` (${Math.round(dias(f.fecha_inicio, f.fecha_fin) / 30.4)} meses)` : ''}</dd>
          <dt style="color:var(--texto-3)">Madurez objetivo</dt><dd style="margin:0">${f.madurez_objetivo ?? '—'}</dd>
          <dt style="color:var(--texto-3)">Plazos IWP</dt><dd style="margin:0">${f.sem_iwp_iniciado}/${f.sem_identificadas}/${f.sem_asignadas}/${f.sem_levantadas}/${f.sem_liberacion} sem · backlog ≥ ${f.backlog_meta_sem} sem</dd>
          ${f.pico_personal ? html`<dt style="color:var(--texto-3)">Planificadores</dt><dd style="margin:0">${Math.ceil(f.pico_personal / 50)} (1 por cada 50 de ${f.pico_personal})</dd>` : ''}
          <dt style="color:var(--texto-3)">Hitos</dt><dd style="margin:0">${cumplidos} de ${hs.length} cumplidos${atr ? html` · <span style="color:var(--critico-texto)">${atr} atrasado${atr > 1 ? 's' : ''}</span>` : ''}</dd>
        </dl>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <a class="btn btn-chico" href=${`#/p/${d.proyecto.id}/hitos?fase=${f.id}`}><${Ic} n="flag" />Hitos</a>
          ${puedeEditar && html`<button class="btn btn-chico" onClick=${() => setEditando({ ...f })}><${Ic} n="pencil" />Editar</button>
            <button class="btn btn-chico btn-texto" style="color:var(--critico-texto)" onClick=${() => borrar(f)}><${Ic} n="trash-2" />Borrar</button>`}
        </div>
        <p style="margin:8px 0 0;font-size:11.5px;color:var(--texto-3)">Modificada ${f.actualizado_en ? new Date(f.actualizado_en).toLocaleString('es') : '—'}</p>
      </article>`; })}</div>`}
    ${editando && html`<${FormFase} fase=${editando} d=${d} onCerrar=${() => setEditando(null)} recargar=${recargar} />`}`;
}
