// Proyecto: carga de datos, navegación por módulos y dashboard (resumen).
import { html, useEffect, useState, useCallback } from '../vendor/preact-htm.js';
import { sb, q, registrarInstantanea } from '../lib/db.js';
import { obtener, avisarError, useEstado } from '../lib/estado.js';
import { Ic, Chip, Anillo, Vacio, AyudaModulo, Contexto, colorEstado, Termino } from '../lib/ui.js';
import { BarrasH, LineaTiempo, Tendencia, estadoHito } from '../lib/graficos.js';
import { fmt, hace, dias } from '../lib/fechas.js';
import { corteDe, atrasados, proximos, metaALaFecha, semaforo, TEXTO_SEMAFORO, avancePorEtapa, porcentajeTotal } from '../lib/metricas.js';
import { proximoPaso, revisarInsignias, INSIGNIAS } from '../lib/guia.js';
import { MODULOS, disponible } from '../datos/modulos.js';
import { VistaFases } from './fases.js';
import { VistaAvance } from './avance.js';
import { VistaHitos } from './hitos.js';
import { VistaEditar } from './editar.js';

export const COLOR_FASE = n => ['var(--f1)', 'var(--f2)', 'var(--f3)'][(n - 1) % 3];
const NOMBRE_TABLA = { proyectos: 'el proyecto', fases: 'una fase', personas: 'el equipo', avance_actividades: 'el checklist AWP', hitos: 'un hito', raci: 'la matriz RACI', cwa: 'una CWA', paquetes: 'un paquete', restricciones: 'una restricción', riesgos: 'un riesgo', lecciones: 'una lección', kpi_semanal: 'los KPI', documentos: 'un documento' };
const ACCION = { INSERT: 'creó', UPDATE: 'actualizó', DELETE: 'borró' };

async function cargarProyecto(id, catalogos) {
  const [proyecto, fases, personas, avance, hitos, insignias, instantaneas, auditoria, miembro] = await Promise.all([
    q(sb.from('proyectos').select('*').eq('id', id).maybeSingle()),
    q(sb.from('fases').select('*').eq('proyecto_id', id).order('numero')),
    q(sb.from('personas').select('*').eq('proyecto_id', id).order('creado_en')),
    q(sb.from('avance_actividades').select('*').eq('proyecto_id', id)),
    q(sb.from('hitos').select('*').eq('proyecto_id', id)),
    q(sb.from('insignias').select('*').eq('proyecto_id', id)),
    q(sb.from('instantaneas').select('semana, fase_id, indicadores').eq('proyecto_id', id).is('fase_id', null).order('semana')),
    q(sb.from('auditoria').select('tabla, accion, fecha, usuario_id, cambios').eq('proyecto_id', id).order('fecha', { ascending: false }).limit(12)),
    q(sb.from('proyecto_miembros').select('rol_acceso').eq('proyecto_id', id).eq('usuario_id', obtener().sesion.user.id).maybeSingle()),
  ]);
  if (!proyecto) return null;
  const cat = Object.fromEntries(catalogos.actividades.map(a => [a.codigo, a]));
  const actividades = avance.map(a => ({ ...a, cat: cat[a.actividad] })).sort((a, b) => a.actividad.localeCompare(b.actividad));
  const ordenHito = Object.fromEntries(catalogos.hitos.map(h => [h.codigo, h.orden]));
  const faseNum = Object.fromEntries(fases.map(f => [f.id, f.numero]));
  hitos.sort((a, b) => (faseNum[a.fase_id] || 0) - (faseNum[b.fase_id] || 0) || ordenHito[a.codigo] - ordenHito[b.codigo]);
  return { proyecto, fases, personas, actividades, hitos, insignias, instantaneas, auditoria, rol: miembro?.rol_acceso || 'lector', corte: corteDe(proyecto) };
}

// ---------------------------------------------------------------- navegación lateral
function Lateral({ p, actual }) {
  const grupos = [...new Set(MODULOS.map(m => m.grupo))];
  return html`<nav class="lateral" aria-label="Módulos del proyecto">
    ${grupos.map(g => html`<div class="grupo">${g}</div>${MODULOS.filter(m => m.grupo === g).map(m => {
      const ok = disponible(m);
      const href = `#/p/${p.id}${m.id === 'resumen' ? '' : '/' + m.id}`;
      return html`<a href=${ok ? href : undefined} class=${ok ? '' : 'pronto'} aria-current=${actual === m.id ? 'page' : null} aria-disabled=${!ok}
        title=${ok ? m.nombre : `Se habilita en la Etapa ${m.etapa}`}><${Ic} n=${m.icono} />${m.nombre}${!ok && html`<small>Etapa ${m.etapa}</small>`}</a>`;
    })}`)}
  </nav>`;
}

// ---------------------------------------------------------------- dashboard
function Resumen({ d, catalogos, recargar }) {
  const { proyecto: p, fases, personas, actividades, hitos, corte } = d;
  const [faseFiltro, setFaseFiltro] = useState('');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const paso = proximoPaso({ ...d, catalogos });
  const etapas = avancePorEtapa(actividades, catalogos.etapas);
  const total = porcentajeTotal(actividades);
  const completas = etapas.filter(e => e.total && e.pct >= 100).map(e => e.etapa.nombre);
  const menor = etapas.filter(e => e.total).sort((a, b) => a.pct - b.pct)[0];
  const tituloEtapas = `La implementación va en ${Math.round(total)} %` + (completas.length ? `: ${completas.length === 1 ? completas[0] : completas.length + ' etapas'} completa${completas.length > 1 ? 's' : ''}` : '') + (menor && menor.pct < 100 ? `; ${menor.etapa.nombre.toLowerCase()} al ${Math.round(menor.pct)} %` : '');

  const hitosF = hitos.filter(h => (!faseFiltro || h.fase_id === faseFiltro) && (!desde || (h.fecha_plan || '') >= desde) && (!hasta || (h.fecha_plan || '') <= hasta));
  const nombreFase = id => { const f = fases.find(x => x.id === id); return f ? `Fase ${f.numero}` : 'Programa'; };
  const listaTiempo = hitosF.map(h => ({ ...h, fase: nombreFase(h.fase_id) }));
  const atr = atrasados(hitosF, corte), prox = proximos(hitosF, corte, 30);

  const porFase = fases.map(f => {
    const hs = hitos.filter(h => h.fase_id === f.id && h.estado !== 'No aplica');
    const cumplidos = hs.filter(h => h.estado === 'Cumplido').length;
    return { f, pct: hs.length ? 100 * cumplidos / hs.length : 0, meta: metaALaFecha(hs, corte), cumplidos, total: hs.length };
  });
  const faseRezagada = porFase.filter(x => x.meta != null).sort((a, b) => (a.pct - a.meta) - (b.pct - b.meta))[0];
  const tituloFases = !porFase.length ? 'Avance por fase' : faseRezagada && faseRezagada.pct < faseRezagada.meta - 5
    ? `La Fase ${faseRezagada.f.numero} va ${Math.round(faseRezagada.meta - faseRezagada.pct)} puntos por detrás de sus hitos planificados`
    : 'Las fases cumplen sus hitos al ritmo planificado';
  const tituloHitos = atr.length ? `${atr.length} hito${atr.length > 1 ? 's' : ''} atrasado${atr.length > 1 ? 's' : ''}; ${prox.length} vence${prox.length === 1 ? '' : 'n'} en los próximos 30 días`
    : prox.length ? `Sin hitos atrasados; ${prox.length} vence${prox.length === 1 ? '' : 'n'} en los próximos 30 días` : 'Sin hitos atrasados ni próximos a vencer';

  const tendencia = d.instantaneas.filter(i => i.indicadores?.avance_awp != null).map(i => ({ fecha: i.semana, valor: Number(i.indicadores.avance_awp) }));
  const deltaTend = tendencia.length > 1 ? tendencia.at(-1).valor - tendencia[0].valor : null;
  const obtenidas = new Set(d.insignias.map(i => i.codigo));
  const yo = obtener().sesion.user.id;

  return html`
    <div class=${'proximo-paso'} data-tour="proximo-paso" style=${paso.estado === 'critico' ? 'border-color:var(--critico)' : ''}>
      <div class="burbuja" style=${paso.estado ? `background:${colorEstado(paso.estado)}` : ''}><${Ic} n=${paso.icono || 'sparkles'} cls="ic ic-lg" /></div>
      <div><h2>Tu próximo paso: ${paso.titulo}</h2><p>${paso.texto}</p></div>
      <a class="btn btn-primario" href=${paso.ir}>${paso.boton}<${Ic} n="arrow-right" /></a>
    </div>

    <button class="btn btn-filtros-movil" onClick=${e => e.currentTarget.nextElementSibling.classList.toggle('abiertos')}><${Ic} n="filter" />Filtros</button>
    <div class="filtros">
      <label>Fase<select value=${faseFiltro} onChange=${e => setFaseFiltro(e.target.value)}><option value="">Todas</option>${fases.map(f => html`<option value=${f.id}>Fase ${f.numero} · ${f.nombre}</option>`)}</select></label>
      <label>Hitos desde<input type="date" value=${desde} onInput=${e => setDesde(e.target.value)} /></label>
      <label>Hasta<input type="date" value=${hasta} onInput=${e => setHasta(e.target.value)} /></label>
      ${(faseFiltro || desde || hasta) && html`<button class="btn btn-chico" onClick=${() => { setFaseFiltro(''); setDesde(''); setHasta(''); }}><${Ic} n="x" />Limpiar</button>`}
    </div>

    <div class="rejilla r-21">
      <div class="tarjeta">
        <h2>${tituloEtapas}</h2>
        <p class="leer">Cómo leerlo: cada anillo es el % del checklist AWP completado en esa <${Termino} t="Etapa del ciclo de vida">etapa del ciclo de vida<//> (las actividades en curso cuentan la mitad). Toca un anillo para ver sus actividades.</p>
        <div class="etapas">${etapas.map(e => html`<a class="etapa" href=${`#/p/${p.id}/avance?etapa=${e.etapa.codigo}`} style="text-decoration:none;color:inherit">
          <${Anillo} pct=${e.pct} tam=${72} /><div class="nombre">${e.etapa.nombre}</div><div class="det">${e.completadas} de ${e.total} actividades</div></a>`)}</div>
      </div>
      <div class="tarjeta">
        <h2>${tituloFases}</h2>
        <p class="leer">Cómo leerlo: % de hitos cumplidos de cada fase; la línea discontinua es el % que ya debería estar cumplido según sus fechas plan.</p>
        ${porFase.length ? html`<${BarrasH} aria="Avance por fase" etiquetaAncho=${70} datos=${porFase.map(x => ({ etq: 'Fase ' + x.f.numero, valor: x.pct, meta: x.meta, color: COLOR_FASE(x.f.numero), tip: `${x.cumplidos} de ${x.total} hitos cumplidos${x.meta != null ? ` · esperado ${Math.round(x.meta)} %` : ''}` }))} />
          <div class="leyenda">${porFase.map(x => html`<span><i style=${'background:' + COLOR_FASE(x.f.numero)}></i>Fase ${x.f.numero}</span>`)}<span><i class="linea-meta"></i>Esperado a la fecha</span></div>`
          : html`<${Vacio} ilustracion="fases" titulo="Sin fases" texto="Agrega las fases para ver su avance."><a class="btn btn-chico" href=${`#/p/${p.id}/fases`}>Agregar fases</a><//>`}
      </div>
    </div>

    <div class="tarjeta" style="margin-top:16px">
      <h2>${tituloHitos}</h2>
      <p class="leer">Cómo leerlo: círculo vacío = fecha plan; círculo lleno = fecha real (verde a tiempo, rojo con atraso); rombo = pendiente (ámbar a tiempo, rojo atrasado). Toca un hito para verlo en detalle.</p>
      <${LineaTiempo} hitos=${listaTiempo} corte=${corte} onClick=${h => location.hash = `#/p/${p.id}/hitos?hito=${h.id}`} />
      <div class="leyenda">${listaTiempo.filter(h => h.fecha_plan).slice(0, 14).map(h => html`<span><${Chip} estado=${estadoHito(h, corte)}>${h.codigo}<//> ${h.nombre}${faseFiltro ? '' : ' · ' + h.fase}</span>`)}${listaTiempo.length > 14 && html`<a href=${`#/p/${p.id}/hitos`}>y ${listaTiempo.length - 14} más…</a>`}</div>
    </div>

    <div class="rejilla r-3" style="margin-top:16px">
      <div class="tarjeta">
        <h2>${atr.length ? `${atr.length} hito${atr.length > 1 ? 's' : ''} atrasado${atr.length > 1 ? 's' : ''}` : 'Ningún hito atrasado'}</h2>
        <p class="leer">Hitos pendientes cuya fecha plan ya pasó. Toca uno para registrar su evidencia o replanificarlo.</p>
        ${atr.length ? html`<ul class="lista">${atr.slice(0, 6).map(h => html`<li onClick=${() => location.hash = `#/p/${p.id}/hitos?hito=${h.id}`}><span style="color:var(--critico)"><${Ic} n="circle-alert" /></span>
          <div class="t"><b>${h.codigo} ${h.nombre}</b><small>${nombreFase(h.fase_id)} · plan ${fmt(h.fecha_plan)}</small></div><${Chip} estado="critico">${dias(h.fecha_plan, corte)} días<//></li>`)}</ul>`
          : html`<p style="color:var(--ok-texto);margin:0"><${Ic} n="circle-check-big" /> Todo al día.</p>`}
      </div>
      <div class="tarjeta">
        <h2>Próximos hitos (30 días)</h2>
        <p class="leer">Prepara con tiempo la evidencia que exige cada criterio.</p>
        ${prox.length ? html`<ul class="lista">${prox.slice(0, 6).map(h => html`<li onClick=${() => location.hash = `#/p/${p.id}/hitos?hito=${h.id}`}><span style="color:var(--atencion)"><${Ic} n="flag" /></span>
          <div class="t"><b>${h.codigo} ${h.nombre}</b><small>${nombreFase(h.fase_id)} · ${fmt(h.fecha_plan)}</small></div><${Chip} estado="atencion">en ${dias(corte, h.fecha_plan)} días<//></li>`)}</ul>`
          : html`<p style="color:var(--texto-2);margin:0">No hay hitos en los próximos 30 días.</p>`}
      </div>
      <div class="tarjeta">
        <h2>${deltaTend == null ? 'Evolución de la implementación' : deltaTend >= 0 ? `La implementación subió ${Math.round(deltaTend)} puntos` : `La implementación bajó ${Math.round(-deltaTend)} puntos`}</h2>
        <p class="leer">Cómo leerlo: % de implementación AWP en la foto semanal de cada lunes${tendencia.length > 1 ? `, desde el ${fmt(tendencia[0].fecha)}` : ''}.</p>
        <${Tendencia} puntos=${tendencia} sufijo=" %" aria="Evolución del % de implementación AWP" />
      </div>
    </div>

    <div class="rejilla r-2" style="margin-top:16px">
      <div class="tarjeta">
        <h2>Insignias del proyecto</h2>
        <p class="leer">Se obtienen al cumplir hitos y completar etapas. ${obtenidas.size} de ${INSIGNIAS.length}.</p>
        <div class="insignias">${INSIGNIAS.map(i => html`<div class=${'insignia' + (obtenidas.has(i.codigo) ? '' : ' bloqueada')} title=${obtenidas.has(i.codigo) ? 'Obtenida' : 'Cómo obtenerla: ' + i.como}>
          <span class="medalla"><${Ic} n=${i.icono} cls="ic ic-lg" /></span>${i.nombre}</div>`)}</div>
      </div>
      <div class="tarjeta">
        <h2>Actividad reciente</h2>
        <p class="leer">Quién cambió qué y cuándo (registro automático).</p>
        ${d.auditoria.length ? html`<ul class="lista actividad-reciente">${d.auditoria.slice(0, 8).map(a => html`<li style="cursor:default">
          <span style="color:var(--texto-3)"><${Ic} n=${a.accion === 'DELETE' ? 'trash-2' : a.accion === 'INSERT' ? 'plus' : 'pencil'} /></span>
          <div class="t"><b style="font-weight:400">${a.usuario_id === yo ? 'Tú' : 'Otro usuario'} ${ACCION[a.accion]} ${NOMBRE_TABLA[a.tabla] || a.tabla}${a.accion === 'UPDATE' && a.cambios?.estado ? `: estado «${a.cambios.estado.despues}»` : ''}</b><small>${hace(a.fecha)}</small></div></li>`)}</ul>`
          : html`<p style="color:var(--texto-2);margin:0">Aún no hay cambios registrados.</p>`}
      </div>
    </div>

    <h2 class="seccion-titulo">Módulos del proyecto</h2>
    <div class="modulos-proyecto">${MODULOS.filter(m => m.id !== 'resumen').map(m => disponible(m)
      ? html`<a class="modulo-p" href=${`#/p/${p.id}/${m.id}`}><span class="ic-caja"><${Ic} n=${m.icono} /></span><span><b>${m.nombre}</b><small>Disponible</small></span></a>`
      : html`<div class="modulo-p pronto"><span class="ic-caja"><${Ic} n=${m.icono} /></span><span><b>${m.nombre}</b><small>Se habilita en la Etapa ${m.etapa}</small></span></div>`)}</div>`;
}

function Pronto({ modulo }) {
  return html`<div class="tarjeta"><${Vacio} titulo=${`${modulo.nombre}: próximamente`} texto=${`Este módulo se construye en la Etapa ${modulo.etapa} de la aplicación. Mientras tanto puedes usar su plantilla del kit.`}><//>
    <${Contexto} modulo=${modulo} /></div>`;
}

export function VistaProyecto({ id, ruta }) {
  const { catalogos } = useEstado();
  const [d, setD] = useState(null);
  const [noExiste, setNoExiste] = useState(false);
  const recargar = useCallback(async () => {
    try {
      const datos = await cargarProyecto(id, catalogos);
      if (!datos) { setNoExiste(true); return; }
      datos.insignias = await revisarInsignias({ ...datos, catalogos, obtenidas: datos.insignias });
      setD(datos);
    } catch (e) { avisarError(e); }
  }, [id]);
  useEffect(() => {
    try { localStorage.setItem('awp-ultimo-proyecto', id); } catch (e) {}
    registrarInstantanea(id).finally(recargar);
  }, [id]);

  if (noExiste) return html`<main><div class="tarjeta"><${Vacio} titulo="No encontramos este proyecto" texto="Puede que se haya borrado o que no tengas acceso a él."><a class="btn btn-primario" href="#/portafolio">Ir al portafolio</a><//></div></main>`;
  if (!d) return html`<main><div class="cargando-inicial"><span class="girador"></span>Cargando el proyecto…</div></main>`;

  const sub = ruta.partes[2] || 'resumen';
  const modulo = MODULOS.find(m => m.id === sub);
  const p = d.proyecto;
  const faseActual = d.fases.find(f => f.estado === 'En ejecución');
  const est = semaforo({ hitos: d.hitos, corte: d.corte });
  const puedeEditar = d.rol !== 'lector';

  let contenido;
  if (sub === 'editar') contenido = html`<${VistaEditar} d=${d} recargar=${recargar} params=${ruta.params} />`;
  else if (!modulo) contenido = html`<${Vacio} titulo="Esta sección no existe" texto="Elige un módulo en el menú." />`;
  else if (!disponible(modulo)) contenido = html`<${Pronto} modulo=${modulo} />`;
  else {
    const V = { resumen: Resumen, fases: VistaFases, avance: VistaAvance, hitos: VistaHitos }[sub];
    contenido = html`<${AyudaModulo} modulo=${modulo} /><${Contexto} modulo=${modulo} /><${V} d=${d} catalogos=${catalogos} recargar=${recargar} params=${ruta.params} puedeEditar=${puedeEditar} />`;
  }

  return html`<main>
    <nav class="migas"><a href="#/portafolio">Portafolio</a><${Ic} n="chevron-right" style="width:14px" /><a href=${'#/p/' + p.id}>${p.codigo}</a>
      ${sub !== 'resumen' && html`<${Ic} n="chevron-right" style="width:14px" /><span>${sub === 'editar' ? 'Editar proyecto' : modulo?.nombre}</span>`}</nav>
    <div class="titulo-pantalla">
      <div><h1>${p.nombre}</h1>
        <p>${p.codigo}${p.cliente ? ' · Cliente: ' + p.cliente : ''}${p.ubicacion ? ' · ' + p.ubicacion : ''}
          ${faseActual && html` · <span class="chip chip-fase" style=${'background:' + COLOR_FASE(faseActual.numero)}>Fase ${faseActual.numero} en ejecución</span>`}
          ${' '}<${Chip} estado=${est}>${TEXTO_SEMAFORO[est]}<//>${p.archivado ? html` <${Chip} estado="neutro" icono="archive">Archivado<//>` : ''}</p></div>
      ${puedeEditar && sub !== 'editar' && html`<div class="acciones"><a class="btn" href=${`#/p/${p.id}/editar`}><${Ic} n="settings" />Editar proyecto</a></div>`}
    </div>
    <div class="con-lateral"><${Lateral} p=${p} actual=${sub} /><div style="min-width:0">${contenido}</div></div>
  </main>`;
}
