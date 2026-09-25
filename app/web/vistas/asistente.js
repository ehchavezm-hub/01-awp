// Asistente paso a paso para crear un proyecto: datos → fases → roles → hitos.
import { html, useEffect, useState } from '../vendor/preact-htm.js';
import { sb, q, traducirError } from '../lib/db.js';
import { avisar, obtener } from '../lib/estado.js';
import { Ic, Campo, Termino, celebrar } from '../lib/ui.js';
import { fmt, interpolar, sumarDias, hoyISO, hace } from '../lib/fechas.js';
import { leerBorrador, guardarBorrador, borrarBorrador } from '../lib/guia.js';
import { ir } from '../lib/rutas.js';

const CLAVE = 'asistente-proyecto';
const TIPOS = ['Industrial', 'Minería', 'Energía', 'Infraestructura', 'Edificación', 'Hospitalario', 'Logístico', 'Otro'];
const PASOS = [['Datos generales', 'building-2'], ['Fases', 'layers'], ['Roles', 'users'], ['Hitos', 'flag']];
const OBLIGATORIOS = ['CHA', 'LWF', 'CON'];
// Propuesta del kit (proyecto tipo): posición relativa de cada fase dentro del
// proyecto y de cada hito dentro de su fase (Fase 2: M6–M30).
const FASES_KIT = [
  { nombre: 'Infraestructura y obras tempranas', ini: 2 / 36, fin: 14 / 36, madurez: 2, plazos: [8, 6, 5, 3, 2], backlog: 2 },
  { nombre: 'Instalación principal', ini: 5 / 36, fin: 30 / 36, madurez: 3, plazos: [12, 10, 8, 4, 2], backlog: 2 },
  { nombre: 'Edificaciones complementarias y ampliación', ini: 15 / 36, fin: 1, madurez: 4, plazos: [8, 6, 5, 3, 2], backlog: 3 },
];
const POS_HITO = { H1: 0, H2: .083, H3: .125, H4: .167, H5: .208, H6: .333, H7: .333, H8: .458, H9: .75, H10: 1 };

const vacio = () => ({
  paso: 0,
  datos: { codigo: '', nombre: '', cliente: '', ubicacion: '', tipo: '', fecha_inicio: '', fecha_fin: '', responsable: '', estado: 'Planificado', descripcion: '' },
  fases: [], personas: {}, hitos: [], firmaHitos: '',
});

function proponerFases(d) {
  return FASES_KIT.map((k, i) => ({
    numero: i + 1, nombre: k.nombre, alcance: '', estado: 'Planificada',
    fecha_inicio: interpolar(d.fecha_inicio, d.fecha_fin, k.ini), fecha_fin: interpolar(d.fecha_inicio, d.fecha_fin, k.fin),
    madurez_objetivo: k.madurez, sem_iwp_iniciado: k.plazos[0], sem_identificadas: k.plazos[1], sem_asignadas: k.plazos[2],
    sem_levantadas: k.plazos[3], sem_liberacion: k.plazos[4], backlog_meta_sem: k.backlog,
  }));
}

function proponerHitos(d, fases, cat) {
  const lista = [];
  const h0 = cat.find(h => h.codigo === 'H0');
  lista.push({ fase: null, codigo: 'H0', nombre: h0.nombre, criterio: h0.criterio, evidencia: h0.evidencia, aprueba: h0.aprueba, fecha_plan: sumarDias(d.fecha_inicio, 30) > d.fecha_fin ? d.fecha_fin : sumarDias(d.fecha_inicio, 30) });
  for (const f of fases) {
    for (const h of cat.filter(h => h.codigo !== 'H0')) {
      lista.push({ fase: f.numero, codigo: h.codigo, nombre: h.nombre, criterio: h.criterio, evidencia: h.evidencia, aprueba: h.aprueba, fecha_plan: interpolar(f.fecha_inicio, f.fecha_fin, POS_HITO[h.codigo] ?? 1) });
    }
  }
  return lista;
}
const firma = fases => JSON.stringify(fases.map(f => [f.numero, f.fecha_inicio, f.fecha_fin]));

// ---------------------------------------------------------------- validación por paso
function validar(paso, s, codigosExistentes) {
  const e = {};
  const d = s.datos;
  if (paso === 0) {
    if (!d.codigo.trim()) e.codigo = 'Escribe un código corto para el proyecto, por ejemplo «PTN».';
    else if (!/^[A-Za-z0-9][A-Za-z0-9-]{0,14}$/.test(d.codigo.trim())) e.codigo = 'Usa hasta 15 letras, números o guiones, sin espacios. Ejemplo: PTN-2027.';
    else if (codigosExistentes.includes(d.codigo.trim().toUpperCase())) e.codigo = 'Ya tienes un proyecto con ese código. Elige otro.';
    if (!d.nombre.trim()) e.nombre = 'El nombre es obligatorio. Ejemplo: «Planta de tratamiento Norte».';
    if (!d.fecha_inicio) e.fecha_inicio = 'Indica la fecha de inicio: sirve para proponer las fases y los hitos.';
    if (!d.fecha_fin) e.fecha_fin = 'Indica la fecha de fin estimada.';
    else if (d.fecha_inicio && d.fecha_fin <= d.fecha_inicio) e.fecha_fin = `La fecha de fin debe ser posterior al inicio (${fmt(d.fecha_inicio)}).`;
  }
  if (paso === 1) {
    if (!s.fases.length) e.general = 'Agrega al menos una fase. Si el proyecto no se divide, crea solo la Fase 1.';
    s.fases.forEach((f, i) => {
      const pre = `f${i}.`;
      if (!f.nombre.trim()) e[pre + 'nombre'] = 'Ponle un nombre a la fase.';
      if (!f.fecha_inicio) e[pre + 'fecha_inicio'] = 'Indica la fecha de inicio.';
      if (!f.fecha_fin) e[pre + 'fecha_fin'] = 'Indica la fecha de fin.';
      else if (f.fecha_inicio && f.fecha_fin <= f.fecha_inicio) e[pre + 'fecha_fin'] = 'Debe ser posterior al inicio de la fase.';
      if (f.fecha_inicio && f.fecha_inicio < d.fecha_inicio) e[pre + 'fecha_inicio'] = `No puede empezar antes que el proyecto (${fmt(d.fecha_inicio)}).`;
      if (f.fecha_fin && f.fecha_fin > d.fecha_fin) e[pre + 'fecha_fin'] = `No puede terminar después del proyecto (${fmt(d.fecha_fin)}).`;
      const p = [f.sem_iwp_iniciado, f.sem_identificadas, f.sem_asignadas, f.sem_levantadas, f.sem_liberacion].map(Number);
      if (p.some(x => !(x >= 0))) e[pre + 'plazos'] = 'Completa los cinco plazos en semanas.';
      else if (!p.every((x, k) => k === 0 || p[k - 1] >= x)) e[pre + 'plazos'] = 'Los plazos van de mayor a menor: IWP iniciado ≥ identificadas ≥ asignadas ≥ levantadas ≥ liberación.';
    });
  }
  if (paso === 2) {
    OBLIGATORIOS.forEach(r => { if (!s.personas[r]?.nombre?.trim()) e['rol.' + r] = 'Este rol es clave para arrancar: escribe quién lo ocupa (puedes cambiarlo después).'; });
    Object.entries(s.personas).forEach(([r, p]) => { if (p.correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.correo)) e['correo.' + r] = 'Correo no válido.'; });
  }
  if (paso === 3) {
    s.hitos.forEach((h, i) => { if (!h.fecha_plan) e['h' + i] = 'Indica la fecha plan.'; });
  }
  return e;
}

// ---------------------------------------------------------------- pasos
function PasoDatos({ s, set, e }) {
  const d = s.datos, c = (k, v) => set(prev => ({ ...prev, datos: { ...prev.datos, [k]: v } }));
  return html`<h2 style="font-size:18px;margin:0 0 4px">1. Datos generales</h2>
    <p style="color:var(--texto-2);margin:0 0 16px">Lo básico del proyecto. Los campos con * son obligatorios.</p>
    <div class="campos">
      <${Campo} etiqueta="Código" req error=${e.codigo} ayuda="Corto y único; aparece en reportes y archivos. Ejemplo: PTN."><input value=${d.codigo} maxlength="15" onInput=${x => c('codigo', x.target.value.toUpperCase())} /><//>
      <${Campo} etiqueta="Nombre del proyecto" req error=${e.nombre}><input value=${d.nombre} onInput=${x => c('nombre', x.target.value)} placeholder="Planta de tratamiento Norte" /><//>
      <${Campo} etiqueta="Cliente"><input value=${d.cliente} onInput=${x => c('cliente', x.target.value)} /><//>
      <${Campo} etiqueta="Ubicación"><input value=${d.ubicacion} onInput=${x => c('ubicacion', x.target.value)} placeholder="Ciudad, región" /><//>
      <${Campo} etiqueta="Tipo de proyecto"><select value=${d.tipo} onChange=${x => c('tipo', x.target.value)}><option value="">Elige…</option>${TIPOS.map(t => html`<option value=${t}>${t}</option>`)}</select><//>
      <${Campo} etiqueta="Responsable del proyecto" ayuda="Quien responde por el proyecto (por ejemplo, el Gerente de Proyecto)."><input value=${d.responsable} onInput=${x => c('responsable', x.target.value)} /><//>
      <${Campo} etiqueta="Fecha de inicio" req error=${e.fecha_inicio} ayuda="Incluye la planificación temprana (FEL)."><input type="date" value=${d.fecha_inicio} onInput=${x => c('fecha_inicio', x.target.value)} /><//>
      <${Campo} etiqueta="Fecha de fin estimada" req error=${e.fecha_fin}><input type="date" value=${d.fecha_fin} onInput=${x => c('fecha_fin', x.target.value)} /><//>
      <${Campo} etiqueta="Estado"><select value=${d.estado} onChange=${x => c('estado', x.target.value)}>${['Planificado', 'En ejecución', 'En pausa', 'Cerrado'].map(t => html`<option value=${t}>${t}</option>`)}</select><//>
      <${Campo} etiqueta="Descripción" ancho><textarea rows="3" value=${d.descripcion} onInput=${x => c('descripcion', x.target.value)} placeholder="Alcance general, contrato, particularidades…"></textarea><//>
    </div>`;
}

function PasoFases({ s, set, e }) {
  const cambiarFase = (i, k, v) => set(prev => { const fases = prev.fases.slice(); fases[i] = { ...fases[i], [k]: v }; return { ...prev, fases }; });
  const agregar = () => {
    const ultima = s.fases.at(-1);
    set({ ...s, fases: [...s.fases, { numero: (ultima?.numero || 0) + 1, nombre: '', alcance: '', estado: 'Planificada', fecha_inicio: ultima?.fecha_fin || s.datos.fecha_inicio, fecha_fin: s.datos.fecha_fin, madurez_objetivo: 3, sem_iwp_iniciado: 8, sem_identificadas: 6, sem_asignadas: 5, sem_levantadas: 3, sem_liberacion: 2, backlog_meta_sem: 2 }] });
  };
  const quitar = i => set({ ...s, fases: s.fases.filter((_, k) => k !== i).map((f, k) => ({ ...f, numero: k + 1 })) });
  return html`<h2 style="font-size:18px;margin:0 0 4px">2. <${Termino} t="Fase del proyecto">Fases del proyecto<//></h2>
    <p style="color:var(--texto-2);margin:0 0 12px">Te proponemos las 3 fases del proyecto tipo del kit, con fechas proporcionales a tu proyecto. Cámbialas, quítalas o agrega otras.</p>
    ${e.general && html`<div class="aviso aviso-error" style="margin-bottom:10px"><${Ic} n="circle-alert" />${e.general}</div>`}
    ${s.fases.map((f, i) => html`<div class="fase-editor">
      <div class="cab"><span class="chip chip-fase" style=${`background:${['var(--f1)', 'var(--f2)', 'var(--f3)'][i % 3]}`}>Fase ${f.numero}</span><b></b>
        <button class="btn btn-texto btn-chico" onClick=${() => quitar(i)} aria-label=${'Quitar la Fase ' + f.numero}><${Ic} n="trash-2" />Quitar</button></div>
      <div class="campos">
        <${Campo} etiqueta="Nombre" req error=${e[`f${i}.nombre`]}><input value=${f.nombre} onInput=${x => cambiarFase(i, 'nombre', x.target.value)} /><//>
        <${Campo} etiqueta="Nivel de madurez AWP objetivo" ayuda="1 inicial · 2 básico · 3 integrado · 4 optimizado · 5 excelencia"><select value=${f.madurez_objetivo} onChange=${x => cambiarFase(i, 'madurez_objetivo', Number(x.target.value))}>${[1, 2, 3, 4, 5].map(n => html`<option value=${n}>${n}</option>`)}</select><//>
        <${Campo} etiqueta="Inicio" req error=${e[`f${i}.fecha_inicio`]}><input type="date" value=${f.fecha_inicio} onInput=${x => cambiarFase(i, 'fecha_inicio', x.target.value)} /><//>
        <${Campo} etiqueta="Fin" req error=${e[`f${i}.fecha_fin`]}><input type="date" value=${f.fecha_fin} onInput=${x => cambiarFase(i, 'fecha_fin', x.target.value)} /><//>
        <${Campo} etiqueta="Alcance" ancho><input value=${f.alcance} onInput=${x => cambiarFase(i, 'alcance', x.target.value)} placeholder="Qué se construye en esta fase" /><//>
      </div>
      <details class="mas"><summary>Plazos de liberación de <${Termino} t="IWP" /> (semanas antes de la ejecución)</summary>
        <div class="plazos">${[['sem_iwp_iniciado', 'IWP iniciado'], ['sem_identificadas', 'Restricciones identificadas'], ['sem_asignadas', 'Asignadas'], ['sem_levantadas', 'Levantadas'], ['sem_liberacion', 'Liberación'], ['backlog_meta_sem', 'Meta de backlog']].map(([k, t]) => html`
          <${Campo} etiqueta=${t}><input type="number" min="0" max="52" value=${f[k]} onInput=${x => cambiarFase(i, k, x.target.value)} /><//>`)}</div>
        ${e[`f${i}.plazos`] ? html`<div class="campo con-error"><span class="error"><${Ic} n="circle-alert" />${e[`f${i}.plazos`]}</span></div>` : html`<span class="ayuda" style="font-size:12px;color:var(--texto-2)">Referencia del kit: 12/10/8/4/2 semanas en proyectos grandes; 8/6/5/3/2 en fases más simples.</span>`}
      </details>
    </div>`)}
    <button class="btn btn-suave" onClick=${agregar}><${Ic} n="plus" />Agregar fase</button>
    ${!s.fases.length && html` <button class="btn" onClick=${() => set({ ...s, fases: proponerFases(s.datos) })}><${Ic} n="sparkles" />Usar la propuesta del kit</button>`}`;
}

function PasoRoles({ s, set, e, roles }) {
  const c = (r, k, v) => set(prev => ({ ...prev, personas: { ...prev.personas, [r]: { ...(prev.personas[r] || {}), [k]: v } } }));
  return html`<h2 style="font-size:18px;margin:0 0 4px">3. Roles AWP</h2>
    <p style="color:var(--texto-2);margin:0 0 12px">Quién ocupa cada rol del kit. Los marcados con <span class="oblig">*</span> son clave para arrancar; el resto puedes completarlo después. El <${Termino} t="AWP Champion" /> debe ser a tiempo completo.</p>
    <div class="tabla-env"><table class="tabla-roles tabla-movil"><thead><tr><th>Rol</th><th>Nombre</th><th>Organización</th><th>Correo</th></tr></thead><tbody>
      ${roles.map(r => { const p = s.personas[r.codigo] || {}; return html`<tr>
        <td data-etq="Rol"><b>${r.nombre}</b>${OBLIGATORIOS.includes(r.codigo) && html` <span class="oblig">*</span>`}<br /><small style="color:var(--texto-3)">${r.codigo}</small></td>
        <td data-etq="Nombre"><input value=${p.nombre || ''} onInput=${x => c(r.codigo, 'nombre', x.target.value)} aria-label=${'Nombre para ' + r.nombre} style=${e['rol.' + r.codigo] ? 'border-color:var(--critico)' : ''} />
          ${e['rol.' + r.codigo] && html`<div class="campo con-error"><span class="error"><${Ic} n="circle-alert" />${e['rol.' + r.codigo]}</span></div>`}</td>
        <td data-etq="Organización"><input value=${p.organizacion || ''} onInput=${x => c(r.codigo, 'organizacion', x.target.value)} aria-label=${'Organización para ' + r.nombre} placeholder=${r.codigo === 'CLI' ? 'Cliente' : 'Contratista'} /></td>
        <td data-etq="Correo"><input type="email" value=${p.correo || ''} onInput=${x => c(r.codigo, 'correo', x.target.value)} aria-label=${'Correo para ' + r.nombre} />
          ${e['correo.' + r.codigo] && html`<div class="campo con-error"><span class="error">${e['correo.' + r.codigo]}</span></div>`}</td></tr>`; })}
    </tbody></table></div>`;
}

function PasoHitos({ s, set, e }) {
  const c = (i, v) => set(prev => { const hitos = prev.hitos.slice(); hitos[i] = { ...hitos[i], fecha_plan: v }; return { ...prev, hitos }; });
  const grupos = [null, ...s.fases.map(f => f.numero)];
  return html`<h2 style="font-size:18px;margin:0 0 4px">4. <${Termino} t="Hito">Hitos AWP<//></h2>
    <p style="color:var(--texto-2);margin:0 0 12px">Propuesta del kit: H0 para todo el proyecto y H1–H10 para cada fase, con fechas proporcionales a la fase. Ajusta las que conozcas.</p>
    ${grupos.map(g => { const filas = s.hitos.map((h, i) => [h, i]).filter(([h]) => h.fase === g); return html`<details open=${g === null || g === 1} class="fase-editor" style="padding:8px 12px">
      <summary style="cursor:pointer;font-weight:600;padding:4px 0">${g === null ? 'Programa (todas las fases)' : `Fase ${g} · ${s.fases.find(f => f.numero === g)?.nombre || ''}`} · ${filas.length} hitos</summary>
      <div class="tabla-env"><table class="tabla-movil"><thead><tr><th>Hito</th><th>Criterio de cumplimiento</th><th>Fecha plan</th></tr></thead><tbody>
        ${filas.map(([h, i]) => html`<tr><td data-etq="Hito"><b>${h.codigo}</b> ${h.nombre}</td><td data-etq="Criterio"><small style="color:var(--texto-2)">${h.criterio}</small></td>
          <td data-etq="Fecha plan"><input type="date" value=${h.fecha_plan} onInput=${x => c(i, x.target.value)} style=${'border:1px solid var(--borde);border-radius:7px;padding:5px;background:var(--superficie)' + (e['h' + i] ? ';border-color:var(--critico)' : '')} /></td></tr>`)}
      </tbody></table></div></details>`; })}`;
}

function Resumen({ s }) {
  const asignados = Object.values(s.personas).filter(p => p.nombre?.trim()).length;
  return html`<div class="resumen-final" style="margin-top:16px">
    <div class="tarjeta estadistica"><span class="etq"><${Ic} n="layers" />Fases</span><span class="valor">${s.fases.length}</span></div>
    <div class="tarjeta estadistica"><span class="etq"><${Ic} n="users" />Roles asignados</span><span class="valor">${asignados}</span></div>
    <div class="tarjeta estadistica"><span class="etq"><${Ic} n="flag" />Hitos</span><span class="valor">${s.hitos.length}</span></div>
    <div class="tarjeta estadistica"><span class="etq"><${Ic} n="list-checks" />Actividades AWP</span><span class="valor">30</span></div>
  </div>
  <p style="color:var(--texto-2);font-size:13px">Al crear el proyecto también se cargan el checklist de implementación (30 actividades por etapa del ciclo de vida) y la matriz RACI propuesta del kit (37 actividades).</p>`;
}

// ---------------------------------------------------------------- creación
async function crear(s, catalogos) {
  const d = s.datos;
  const proyecto = await q(sb.from('proyectos').insert({
    codigo: d.codigo.trim().toUpperCase(), nombre: d.nombre.trim(), cliente: d.cliente || null, ubicacion: d.ubicacion || null,
    tipo: d.tipo || null, fecha_inicio: d.fecha_inicio, fecha_fin: d.fecha_fin, responsable: d.responsable || null,
    estado: d.estado, descripcion: d.descripcion || null,
  }).select().single());
  try {
    const fases = await q(sb.from('fases').insert(s.fases.map(f => ({
      proyecto_id: proyecto.id, numero: f.numero, nombre: f.nombre.trim(), alcance: f.alcance || null, estado: f.estado,
      fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin, madurez_objetivo: f.madurez_objetivo,
      sem_iwp_iniciado: Number(f.sem_iwp_iniciado), sem_identificadas: Number(f.sem_identificadas), sem_asignadas: Number(f.sem_asignadas),
      sem_levantadas: Number(f.sem_levantadas), sem_liberacion: Number(f.sem_liberacion), backlog_meta_sem: Number(f.backlog_meta_sem),
    }))).select());
    const idFase = Object.fromEntries(fases.map(f => [f.numero, f.id]));
    const personas = Object.entries(s.personas).filter(([, p]) => p.nombre?.trim())
      .map(([rol, p]) => ({ proyecto_id: proyecto.id, rol_codigo: rol, nombre: p.nombre.trim(), organizacion: p.organizacion || null, correo: p.correo || null }));
    await Promise.all([
      personas.length ? q(sb.from('personas').insert(personas)) : null,
      q(sb.from('hitos').insert(s.hitos.map(h => ({ proyecto_id: proyecto.id, fase_id: h.fase ? idFase[h.fase] : null, codigo: h.codigo, nombre: h.nombre, criterio: h.criterio, evidencia: h.evidencia, aprueba: h.aprueba, fecha_plan: h.fecha_plan })))),
      q(sb.from('avance_actividades').insert(catalogos.actividades.map(a => ({ proyecto_id: proyecto.id, actividad: a.codigo })))),
      q(sb.from('raci').insert(catalogos.raci.map(r => ({ proyecto_id: proyecto.id, orden: r.orden, etapa: r.etapa, actividad: r.actividad, fase: r.fase, asignaciones: r.asignaciones })))),
    ]);
    return proyecto;
  } catch (e) {
    // Si algo falla, se deshace todo: el proyecto se borra con sus datos en cascada.
    await sb.from('proyectos').delete().eq('id', proyecto.id);
    throw traducirError(e);
  }
}

export function VistaAsistente() {
  const { catalogos } = obtener();
  const [s, setS] = useState(vacio());
  const [errores, setErrores] = useState({});
  const [codigos, setCodigos] = useState([]);
  const [recuperable, setRecuperable] = useState(null);
  const [guardado, setGuardado] = useState(null);
  const [creando, setCreando] = useState(false);

  const [tocado, setTocado] = useState(false);
  useEffect(() => {
    q(sb.from('proyectos').select('codigo')).then(p => setCodigos(p.map(x => x.codigo.toUpperCase()))).catch(() => {});
    // El borrador se ofrece solo si existía antes de empezar a escribir aquí.
    leerBorrador(CLAVE).then(b => { if (b && (b.datos?.nombre || b.datos?.codigo)) setRecuperable(r => (tocadoRef.v ? null : b)); });
  }, []);
  const tocadoRef = useState({ v: false })[0];

  // Acepta un objeto o una función (estado anterior → nuevo), para no perder cambios rápidos seguidos.
  const set = upd => { tocadoRef.v = true; setTocado(true); setRecuperable(null); setS(prev => { const nuevo = typeof upd === 'function' ? upd(prev) : upd; setGuardado(guardarBorrador(CLAVE, nuevo)); return nuevo; }); };
  const irPaso = destino => {
    if (destino > s.paso) {
      const e = validar(s.paso, s, codigos);
      setErrores(e);
      if (Object.keys(e).length) { avisar('Revisa los campos marcados en rojo: cada uno explica cómo corregirlo.', 'error'); return; }
    } else setErrores({});
    let nuevo = { ...s, paso: destino };
    if (destino >= 1 && !s.fases.length && s.paso === 0) nuevo.fases = proponerFases(s.datos);
    if (destino === 3 && nuevo.firmaHitos !== firma(nuevo.fases)) { nuevo.hitos = proponerHitos(nuevo.datos, nuevo.fases, catalogos.hitos); nuevo.firmaHitos = firma(nuevo.fases); }
    set(nuevo);
    scrollTo(0, 0);
  };
  const terminar = async () => {
    const e = validar(3, s, codigos);
    setErrores(e);
    if (Object.keys(e).length) { avisar('Hay hitos sin fecha plan.', 'error'); return; }
    setCreando(true);
    try {
      const p = await crear(s, catalogos);
      await borrarBorrador(CLAVE);
      celebrar();
      avisar(`¡Proyecto ${p.codigo} creado! Ya tiene sus fases, hitos y checklist AWP.`);
      ir('/p/' + p.id);
    } catch (err) {
      setCreando(false);
      avisar(`${err.message} ${err.ayuda || ''}`, 'error');
    }
  };

  const Paso = [PasoDatos, PasoFases, PasoRoles, PasoHitos][s.paso];
  return html`<main class="asistente">
    <nav class="migas"><a href="#/portafolio">Portafolio</a><${Ic} n="chevron-right" style="width:14px" /><span>Nuevo proyecto</span></nav>
    <div class="titulo-pantalla"><div><h1>Nuevo proyecto</h1><p>Cuatro pasos. Tu avance se guarda solo: puedes cerrar y continuar después, incluso desde otro dispositivo.</p></div></div>
    ${recuperable && html`<div class="aviso aviso-info" style="margin-bottom:14px;align-items:center;flex-wrap:wrap"><${Ic} n="history" />
      <div style="flex:1">Tienes un proyecto a medio crear: <b>${recuperable.datos.codigo || ''} ${recuperable.datos.nombre || ''}</b>. ¿Quieres continuarlo?</div>
      <button class="btn btn-chico btn-primario" onClick=${() => { setS(recuperable); setRecuperable(null); }}>Continuar</button>
      <button class="btn btn-chico" onClick=${() => { borrarBorrador(CLAVE); setRecuperable(null); }}>Empezar de nuevo</button></div>`}
    <div class="pasos-horizontales" role="list">${PASOS.map(([t, i], k) => html`<div role="listitem" class=${'ph' + (k === s.paso ? ' actual' : '') + (k < s.paso ? ' hecho' : '')} onClick=${() => k < s.paso && irPaso(k)}>
      <span class="n">${k < s.paso ? html`<${Ic} n="check" />` : k + 1}</span><${Ic} n=${i} />${t}</div>`)}</div>
    <div class="tarjeta">
      <${Paso} s=${s} set=${set} e=${errores} roles=${catalogos.roles} />
      ${s.paso === 3 && html`<${Resumen} s=${s} />`}
      <div class="pie-form">
        <span class="autoguardado"><${Ic} n="save" />${guardado ? 'Borrador guardado ' + hace(guardado) : 'Se guarda automáticamente'}</span>
        <div class="der">
          ${s.paso > 0 ? html`<button class="btn" onClick=${() => irPaso(s.paso - 1)}><${Ic} n="chevron-left" />Anterior</button>` : html`<a class="btn" href="#/portafolio">Cancelar</a>`}
          ${s.paso < 3 ? html`<button class="btn btn-primario" onClick=${() => irPaso(s.paso + 1)}>Siguiente<${Ic} n="chevron-right" /></button>`
            : html`<button class="btn btn-primario" onClick=${terminar} disabled=${creando}>${creando ? html`<span class="girador" style="width:16px;height:16px"></span>` : html`<${Ic} n="rocket" />`}Crear proyecto</button>`}
        </div>
      </div>
    </div>
  </main>`;
}
