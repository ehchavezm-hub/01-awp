// Editar proyecto: datos generales, equipo (roles AWP), archivar y borrar.
import { html, useState } from '../vendor/preact-htm.js';
import { sb, q } from '../lib/db.js';
import { avisar, avisarError, confirmar, obtener } from '../lib/estado.js';
import { Ic, Campo, Chip, Modal, Termino } from '../lib/ui.js';
import { fmt } from '../lib/fechas.js';
import { ir } from '../lib/rutas.js';

const TIPOS = ['Industrial', 'Minería', 'Energía', 'Infraestructura', 'Edificación', 'Hospitalario', 'Logístico', 'Otro'];
const ESTADOS = ['Planificado', 'En ejecución', 'En pausa', 'Cerrado'];
const CLAVE = ['CHA', 'LWF', 'CON'];

function Datos({ d, recargar }) {
  const [f, setF] = useState({ ...d.proyecto });
  const [e, setE] = useState({});
  const c = (k, v) => setF(prev => ({ ...prev, [k]: v }));
  const guardar = async () => {
    const err = {};
    if (!f.nombre?.trim()) err.nombre = 'El nombre es obligatorio.';
    if (!/^[A-Za-z0-9][A-Za-z0-9-]{0,14}$/.test(f.codigo || '')) err.codigo = 'Usa hasta 15 letras, números o guiones, sin espacios.';
    if (f.fecha_inicio && f.fecha_fin && f.fecha_fin <= f.fecha_inicio) err.fecha_fin = `Debe ser posterior al inicio (${fmt(f.fecha_inicio)}).`;
    const fueraDeRango = d.fases.filter(fa => (f.fecha_inicio && fa.fecha_inicio && fa.fecha_inicio < f.fecha_inicio) || (f.fecha_fin && fa.fecha_fin && fa.fecha_fin > f.fecha_fin));
    if (fueraDeRango.length) err.fecha_fin = err.fecha_fin || `Las fechas dejan fuera a la Fase ${fueraDeRango.map(x => x.numero).join(', ')}. Ajusta primero las fechas de esas fases.`;
    setE(err);
    if (Object.keys(err).length) return;
    try {
      await q(sb.from('proyectos').update({ codigo: f.codigo.toUpperCase(), nombre: f.nombre.trim(), cliente: f.cliente || null, ubicacion: f.ubicacion || null, tipo: f.tipo || null,
        responsable: f.responsable || null, estado: f.estado, descripcion: f.descripcion || null, fecha_inicio: f.fecha_inicio || null, fecha_fin: f.fecha_fin || null,
        fecha_corte: f.fecha_corte || null }).eq('id', d.proyecto.id));
      avisar('Datos del proyecto guardados.'); recargar();
    } catch (err2) { avisarError(err2); }
  };
  return html`<div class="tarjeta">
    <div class="campos">
      <${Campo} etiqueta="Código" req error=${e.codigo}><input value=${f.codigo} maxlength="15" onInput=${x => c('codigo', x.target.value.toUpperCase())} /><//>
      <${Campo} etiqueta="Nombre" req error=${e.nombre}><input value=${f.nombre} onInput=${x => c('nombre', x.target.value)} /><//>
      <${Campo} etiqueta="Cliente"><input value=${f.cliente || ''} onInput=${x => c('cliente', x.target.value)} /><//>
      <${Campo} etiqueta="Ubicación"><input value=${f.ubicacion || ''} onInput=${x => c('ubicacion', x.target.value)} /><//>
      <${Campo} etiqueta="Tipo"><select value=${f.tipo || ''} onChange=${x => c('tipo', x.target.value)}><option value="">—</option>${TIPOS.map(t => html`<option value=${t}>${t}</option>`)}</select><//>
      <${Campo} etiqueta="Responsable"><input value=${f.responsable || ''} onInput=${x => c('responsable', x.target.value)} /><//>
      <${Campo} etiqueta="Inicio"><input type="date" value=${f.fecha_inicio || ''} onInput=${x => c('fecha_inicio', x.target.value)} /><//>
      <${Campo} etiqueta="Fin" error=${e.fecha_fin}><input type="date" value=${f.fecha_fin || ''} onInput=${x => c('fecha_fin', x.target.value)} /><//>
      <${Campo} etiqueta="Estado"><select value=${f.estado} onChange=${x => c('estado', x.target.value)}>${ESTADOS.map(t => html`<option value=${t}>${t}</option>`)}</select><//>
      <${Campo} etiqueta="Fecha de corte" ayuda="Vacía = hoy. Úsala para ver el proyecto «como estaba» en una fecha (por ejemplo, para un reporte mensual)."><input type="date" value=${f.fecha_corte || ''} onInput=${x => c('fecha_corte', x.target.value)} /><//>
      <${Campo} etiqueta="Descripción" ancho><textarea rows="3" value=${f.descripcion || ''} onInput=${x => c('descripcion', x.target.value)}></textarea><//>
    </div>
    <div class="pie-form"><span class="autoguardado"><${Ic} n="history" />Última modificación: ${new Date(d.proyecto.actualizado_en).toLocaleString('es')}${d.proyecto.actualizado_por === obtener().sesion.user.id ? ' (tú)' : ''}</span>
      <div class="der"><button class="btn btn-primario" onClick=${guardar}><${Ic} n="save" />Guardar cambios</button></div></div>
  </div>`;
}

function FormPersona({ p, d, catalogos, onCerrar, recargar }) {
  const [f, setF] = useState(p);
  const [e, setE] = useState({});
  const c = (k, v) => setF(prev => ({ ...prev, [k]: v }));
  const guardar = async () => {
    const err = {};
    if (!f.nombre?.trim()) err.nombre = 'Escribe el nombre de la persona.';
    if (!f.rol_codigo) err.rol = 'Elige su rol AWP.';
    if (f.correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.correo)) err.correo = 'Correo no válido. Ejemplo: nombre@empresa.com.';
    setE(err);
    if (Object.keys(err).length) return;
    const datos = { proyecto_id: d.proyecto.id, nombre: f.nombre.trim(), rol_codigo: f.rol_codigo, organizacion: f.organizacion || null, correo: f.correo || null, telefono: f.telefono || null, activo: f.activo !== false };
    try {
      if (f.id) await q(sb.from('personas').update(datos).eq('id', f.id)); else await q(sb.from('personas').insert(datos));
      avisar(f.id ? 'Persona actualizada.' : `${datos.nombre} se sumó al equipo.`); onCerrar(); recargar();
    } catch (err2) { avisarError(err2); }
  };
  return html`<${Modal} titulo=${f.id ? 'Editar persona' : 'Agregar persona al equipo'} icono="user" onCerrar=${onCerrar}
    pie=${html`<button class="btn" onClick=${onCerrar}>Cancelar</button><button class="btn btn-primario" onClick=${guardar}><${Ic} n="save" />Guardar</button>`}>
    <div class="campos">
      <${Campo} etiqueta="Nombre" req error=${e.nombre}><input value=${f.nombre || ''} onInput=${x => c('nombre', x.target.value)} /><//>
      <${Campo} etiqueta="Rol AWP" req error=${e.rol}><select value=${f.rol_codigo || ''} onChange=${x => c('rol_codigo', x.target.value)}><option value="">Elige…</option>${catalogos.roles.map(r => html`<option value=${r.codigo}>${r.nombre}</option>`)}</select><//>
      <${Campo} etiqueta="Organización"><input value=${f.organizacion || ''} onInput=${x => c('organizacion', x.target.value)} /><//>
      <${Campo} etiqueta="Correo" error=${e.correo}><input type="email" value=${f.correo || ''} onInput=${x => c('correo', x.target.value)} /><//>
      <${Campo} etiqueta="Teléfono"><input value=${f.telefono || ''} onInput=${x => c('telefono', x.target.value)} /><//>
      <${Campo} etiqueta="Estado"><select value=${f.activo === false ? 'no' : 'si'} onChange=${x => c('activo', x.target.value === 'si')}><option value="si">Activa en el proyecto</option><option value="no">Ya no está en el proyecto</option></select><//>
    </div>
    ${f.rol_codigo && html`<div class="aviso aviso-info" style="margin-top:12px"><${Ic} n="info" /><div><b>${catalogos.rol[f.rol_codigo]?.nombre}:</b> ${catalogos.rol[f.rol_codigo]?.responsabilidades}</div></div>`}
  <//>`;
}

function Equipo({ d, catalogos, recargar }) {
  const [editando, setEditando] = useState(null);
  const activos = d.personas.filter(p => p.activo);
  const faltan = CLAVE.filter(r => !activos.some(p => p.rol_codigo === r));
  const sinAsignar = catalogos.roles.filter(r => !activos.some(p => p.rol_codigo === r.codigo));
  const pico = Math.max(0, ...d.fases.map(f => f.pico_personal || 0));
  const planificadores = activos.filter(p => p.rol_codigo === 'WFP').length;
  return html`
    ${faltan.length > 0 && html`<div class="aviso aviso-atencion" style="margin-bottom:12px"><${Ic} n="triangle-alert" /><div>Faltan roles clave para arrancar: <b>${faltan.map(r => catalogos.rol[r].nombre).join(', ')}</b>.</div></div>`}
    ${pico > 0 && html`<div class="aviso aviso-info" style="margin-bottom:12px"><${Ic} n="users" /><div>Con un pico de ${pico} trabajadores, el kit recomienda <b>${Math.ceil(pico / 50)} planificadores de frente de trabajo</b> (1 por cada 50). Tienes ${planificadores} registrado${planificadores === 1 ? '' : 's'}.</div></div>`}
    <div class="tarjeta">
      <div class="barra-tabla" style="align-items:center"><h2 style="flex:1;margin:0">Equipo AWP (${activos.length})</h2>
        <button class="btn btn-primario" onClick=${() => setEditando({ activo: true })}><${Ic} n="plus" />Agregar persona</button></div>
      ${d.personas.length ? html`<div class="tabla-env"><table class="tabla-movil"><thead><tr><th>Nombre</th><th>Rol AWP</th><th>Organización</th><th>Correo</th><th></th></tr></thead>
        <tbody>${d.personas.map(p => html`<tr onClick=${() => setEditando({ ...p })} style=${p.activo ? '' : 'opacity:.55'}>
          <td data-etq="Nombre"><b>${p.nombre}</b>${!p.activo && ' (inactiva)'}</td><td data-etq="Rol">${catalogos.rol[p.rol_codigo]?.nombre || '—'}</td>
          <td data-etq="Organización">${p.organizacion || '—'}</td><td data-etq="Correo">${p.correo || '—'}</td>
          <td class="celda-acciones"><button class="btn-ic" style="color:var(--texto-3)" aria-label=${'Quitar a ' + p.nombre} onClick=${async ev => { ev.stopPropagation();
            if (await confirmar({ titulo: `¿Quitar a ${p.nombre} del equipo?`, texto: 'Si solo dejó el proyecto, es mejor editarla y marcarla como «Ya no está en el proyecto» para conservar el historial.', boton: 'Quitar', peligro: true })) {
              try { await q(sb.from('personas').delete().eq('id', p.id)); avisar('Persona quitada del equipo.'); recargar(); } catch (er) { avisarError(er); } } }}><${Ic} n="trash-2" /></button></td></tr>`)}</tbody></table></div>`
        : html`<p style="color:var(--texto-2)">Aún no hay personas en el equipo.</p>`}
      ${sinAsignar.length > 0 && html`<p style="font-size:12.5px;color:var(--texto-2);margin:12px 0 0">Roles sin persona asignada: ${sinAsignar.map(r => r.nombre).join(' · ')}. La matriz RACI completa se edita en el módulo Roles (Etapa 4).</p>`}
    </div>
    ${editando && html`<${FormPersona} p=${editando} d=${d} catalogos=${catalogos} onCerrar=${() => setEditando(null)} recargar=${recargar} />`}`;
}

function Peligro({ d, recargar }) {
  const [texto, setTexto] = useState('');
  const [borrando, setBorrando] = useState(false);
  const p = d.proyecto;
  const archivar = async () => {
    const ok = await confirmar({ titulo: p.archivado ? '¿Reactivar el proyecto?' : '¿Archivar el proyecto?', texto: p.archivado ? 'Volverá a aparecer en tu portafolio.' : 'Dejará de aparecer en el portafolio (puedes verlo con «Ver archivados») y sus datos se conservan intactos.', boton: p.archivado ? 'Reactivar' : 'Archivar' });
    if (!ok) return;
    try { await q(sb.from('proyectos').update({ archivado: !p.archivado }).eq('id', p.id)); avisar(p.archivado ? 'Proyecto reactivado.' : 'Proyecto archivado.'); recargar(); } catch (e) { avisarError(e); }
  };
  const borrar = async () => {
    setBorrando(true);
    try { await q(sb.from('proyectos').delete().eq('id', p.id)); avisar(`Proyecto ${p.codigo} borrado.`); ir('/portafolio'); } catch (e) { setBorrando(false); avisarError(e); }
  };
  return html`<div class="tarjeta" style="border-color:var(--critico-fondo)">
    <h2>Archivar</h2><p class="leer">Oculta el proyecto del portafolio sin perder nada. Útil para proyectos terminados.</p>
    <button class="btn" onClick=${archivar}><${Ic} n=${p.archivado ? 'archive-restore' : 'archive'} />${p.archivado ? 'Reactivar proyecto' : 'Archivar proyecto'}</button>
    ${d.rol === 'propietario' && html`<hr style="border:0;border-top:1px solid var(--borde);margin:18px 0" />
      <h2 style="color:var(--critico-texto)">Borrar el proyecto</h2>
      <p class="leer">Borra el proyecto y <b>todos</b> sus datos (fases, hitos, checklist, equipo…). No se puede deshacer. Para confirmar, escribe el código <b>${p.codigo}</b>.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><input value=${texto} onInput=${e => setTexto(e.target.value)} placeholder=${p.codigo} aria-label="Código del proyecto para confirmar" style="border:1px solid var(--borde);border-radius:9px;padding:8px 10px;background:var(--superficie)" />
        <button class="btn btn-peligro" disabled=${texto.trim().toUpperCase() !== p.codigo.toUpperCase() || borrando} onClick=${borrar}><${Ic} n="trash-2" />Borrar definitivamente</button></div>`}
  </div>`;
}

export function VistaEditar({ d, recargar, params }) {
  const { catalogos } = obtener();
  const [pestana, setPestana] = useState(params.pestana || 'datos');
  const PEST = [['datos', 'Datos del proyecto', 'building-2'], ['equipo', 'Equipo y roles', 'users'], ['peligro', 'Archivar o borrar', 'archive']];
  return html`
    <div class="pestanas" role="tablist">${PEST.map(([k, t, i]) => html`<button class="pestana" role="tab" aria-selected=${pestana === k} onClick=${() => setPestana(k)}><${Ic} n=${i} />${t}</button>`)}</div>
    ${pestana === 'datos' && html`<${Datos} d=${d} recargar=${recargar} />`}
    ${pestana === 'equipo' && html`<${Equipo} d=${d} catalogos=${catalogos} recargar=${recargar} />`}
    ${pestana === 'peligro' && html`<${Peligro} d=${d} recargar=${recargar} />`}`;
}
