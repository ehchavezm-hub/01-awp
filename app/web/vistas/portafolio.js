// Portafolio: todos los proyectos en tarjetas, gráfico comparativo y tabla.
import { html, useEffect, useMemo, useState } from '../vendor/preact-htm.js';
import { sb, q } from '../lib/db.js';
import { avisarError } from '../lib/estado.js';
import { Ic, Chip, Anillo, Vacio, colorEstado } from '../lib/ui.js';
import { BarrasH } from '../lib/graficos.js';
import { fmt } from '../lib/fechas.js';
import { avanceAWP, atrasados, proximos, corteDe, semaforo, metaALaFecha, TEXTO_SEMAFORO } from '../lib/metricas.js';
import { ir } from '../lib/rutas.js';

const ESTADOS = ['Planificado', 'En ejecución', 'En pausa', 'Cerrado'];

async function cargar() {
  const [proyectos, fases, avance, hitos, vencidas, riesgos] = await Promise.all([
    q(sb.from('proyectos').select('*').order('creado_en', { ascending: false })),
    q(sb.from('fases').select('id, proyecto_id, numero, nombre, estado, fecha_inicio, fecha_fin')),
    q(sb.from('v_avance_etapas').select('*')),
    q(sb.from('hitos').select('id, proyecto_id, fase_id, codigo, nombre, fecha_plan, fecha_real, estado')),
    q(sb.from('v_restricciones').select('proyecto_id').eq('situacion', 'Vencida')),
    q(sb.from('v_riesgos').select('proyecto_id, estado').eq('clasificacion', 'Alto')),
  ]);
  return proyectos.map(p => {
    const corte = corteDe(p);
    const hs = hitos.filter(h => h.proyecto_id === p.id);
    const fs = fases.filter(f => f.proyecto_id === p.id).sort((a, b) => a.numero - b.numero);
    const nVencidas = vencidas.filter(v => v.proyecto_id === p.id).length;
    return {
      ...p, corte, fases: fs,
      awp: avanceAWP(avance.filter(a => a.proyecto_id === p.id)),
      meta: metaALaFecha(hs, corte),
      atrasados: atrasados(hs, corte).length,
      proximo: proximos(hs, corte, 3650)[0],
      vencidas: nVencidas,
      riesgos: riesgos.filter(r => r.proyecto_id === p.id && r.estado !== 'Cerrado').length,
      faseActual: fs.find(f => f.estado === 'En ejecución') || fs.find(f => f.estado === 'Planificada'),
      semaforo: semaforo({ hitos: hs, corte, vencidas: nVencidas }),
    };
  });
}

const COLOR_FASE = n => ['var(--f1)', 'var(--f2)', 'var(--f3)'][(n - 1) % 3];

function TarjetaProyecto({ p }) {
  return html`<article class="tarjeta proyecto" onClick=${() => ir('/p/' + p.id)} tabindex="0" onKeyDown=${e => e.key === 'Enter' && ir('/p/' + p.id)} role="link" aria-label=${'Abrir ' + p.nombre}>
    <div class="proyecto-cab"><${Anillo} pct=${p.awp} tam=${58} grosor=${6} color=${colorEstado(p.semaforo)} />
      <div style="min-width:0"><h3>${p.nombre}</h3><div class="cod">${p.codigo}${p.faseActual && html` · <span class="chip chip-fase" style=${`background:${COLOR_FASE(p.faseActual.numero)};padding:0 8px;font-size:11.5px`}>Fase ${p.faseActual.numero}</span>`}${p.archivado && ' · Archivado'}</div></div></div>
    <div style="display:flex;gap:6px;flex-wrap:wrap"><${Chip} estado=${p.semaforo}>${TEXTO_SEMAFORO[p.semaforo]}<//><${Chip} estado="neutro" icono="briefcase">${p.estado}<//></div>
    <div class="mini num">
      <div class=${p.atrasados ? 'rojo' : ''}><b>${p.atrasados}</b>hitos atrasados</div>
      <div class=${p.vencidas ? 'rojo' : ''}><b>${p.vencidas}</b>restricciones vencidas</div>
      <div><b>${p.riesgos}</b>riesgos altos</div>
    </div>
    <div class="proximo"><${Ic} n="flag" /><span>${p.proximo ? `${p.proximo.codigo} ${p.proximo.nombre} · ${fmt(p.proximo.fecha_plan)}` : 'Sin hitos pendientes'}</span></div>
  </article>`;
}

export function VistaPortafolio() {
  const [datos, setDatos] = useState(null);
  const [f, setF] = useState({ buscar: '', estado: '', tipo: '', responsable: '', archivados: false, fase: '' });
  useEffect(() => { cargar().then(setDatos).catch(e => { avisarError(e); setDatos([]); }); }, []);
  const cambiar = (k, v) => setF({ ...f, [k]: v });

  const lista = useMemo(() => (datos || []).filter(p =>
    (f.archivados || !p.archivado) && (!f.estado || p.estado === f.estado) && (!f.tipo || p.tipo === f.tipo) &&
    (!f.responsable || p.responsable === f.responsable) && (!f.fase || p.faseActual?.numero === Number(f.fase)) &&
    (!f.buscar || [p.codigo, p.nombre, p.cliente, p.ubicacion].join(' ').toLowerCase().includes(f.buscar.toLowerCase()))), [datos, f]);

  if (!datos) return html`<main><div class="cargando-inicial"><span class="girador"></span>Cargando tus proyectos…</div></main>`;

  const activos = lista.filter(p => p.estado !== 'Cerrado');
  const prom = lista.length ? lista.reduce((a, p) => a + p.awp, 0) / lista.length : 0;
  const totAtrasados = lista.reduce((a, p) => a + p.atrasados, 0);
  const totVencidas = lista.reduce((a, p) => a + p.vencidas, 0);
  const totRiesgos = lista.reduce((a, p) => a + p.riesgos, 0);
  const tipos = [...new Set(datos.map(p => p.tipo).filter(Boolean))];
  const responsables = [...new Set(datos.map(p => p.responsable).filter(Boolean))];

  // Conclusión del gráfico comparativo.
  const conMeta = lista.filter(p => p.meta != null);
  const peor = conMeta.slice().sort((a, b) => (a.awp - a.meta) - (b.awp - b.meta))[0];
  const titulo = !conMeta.length ? 'Implementación AWP por proyecto'
    : peor.awp < peor.meta - 10 ? `${peor.nombre} va ${Math.round(peor.meta - peor.awp)} puntos por detrás de lo esperado a la fecha`
    : 'Todos los proyectos van cerca o por encima del avance esperado a la fecha';

  return html`<main>
    <div class="titulo-pantalla">
      <div><h1>Tu portafolio AWP</h1><p>${activos.length} proyecto${activos.length === 1 ? '' : 's'} activo${activos.length === 1 ? '' : 's'}${datos.length ? '' : ' · empieza creando el primero'}</p></div>
      <div class="acciones"><a class="btn btn-primario" href="#/proyectos/nuevo" data-tour="nuevo"><${Ic} n="plus" />Nuevo proyecto</a></div>
    </div>

    ${!datos.length ? html`<div class="tarjeta"><${Vacio} ilustracion="proyectos" titulo="Aún no tienes proyectos"
        texto="Un proyecto reúne sus fases, el checklist de implementación AWP, los hitos H0–H10 y, más adelante, paquetes, restricciones, riesgos y KPI. El asistente te guía en 4 pasos.">
        <a class="btn btn-primario" href="#/proyectos/nuevo"><${Ic} n="rocket" />Crear mi primer proyecto</a>
        <a class="btn" href="#/recursos"><${Ic} n="library" />Ver los recursos del kit</a><//></div>` : html`

    <button class="btn btn-filtros-movil" onClick=${e => e.currentTarget.nextElementSibling.classList.toggle('abiertos')}><${Ic} n="filter" />Filtros</button>
    <div class="filtros">
      <label style="flex:1;min-width:180px">Buscar<input value=${f.buscar} onInput=${e => cambiar('buscar', e.target.value)} placeholder="Código, nombre, cliente…" style="width:100%" /></label>
      <label>Estado<select value=${f.estado} onChange=${e => cambiar('estado', e.target.value)}><option value="">Todos</option>${ESTADOS.map(s => html`<option value=${s}>${s}</option>`)}</select></label>
      <label>Fase actual<select value=${f.fase} onChange=${e => cambiar('fase', e.target.value)}><option value="">Todas</option>${[1, 2, 3, 4, 5].map(n => html`<option value=${n}>Fase ${n}</option>`)}</select></label>
      ${tipos.length > 0 && html`<label>Tipo<select value=${f.tipo} onChange=${e => cambiar('tipo', e.target.value)}><option value="">Todos</option>${tipos.map(t => html`<option value=${t}>${t}</option>`)}</select></label>`}
      ${responsables.length > 0 && html`<label>Responsable<select value=${f.responsable} onChange=${e => cambiar('responsable', e.target.value)}><option value="">Todos</option>${responsables.map(t => html`<option value=${t}>${t}</option>`)}</select></label>`}
      <label style="flex-direction:row;align-items:center;gap:6px;align-self:flex-end;padding-bottom:6px"><input type="checkbox" checked=${f.archivados} onChange=${e => cambiar('archivados', e.target.checked)} style="min-width:0" />Ver archivados</label>
    </div>

    <div class="rejilla r-5 estadisticas">
      <div class="tarjeta estadistica"><span class="etq"><${Ic} n="building-2" />Proyectos activos</span><span class="valor num">${activos.length}</span><span class="delta">${lista.length - activos.length} cerrados</span></div>
      <div class="tarjeta estadistica"><span class="etq"><${Ic} n="list-checks" />Implementación AWP</span><span class="valor num">${Math.round(prom)} %</span><span class="delta">promedio de los proyectos</span></div>
      <div class="tarjeta estadistica"><span class="etq"><${Ic} n="flag" />Hitos atrasados</span><span class="valor num" style=${totAtrasados ? 'color:var(--critico-texto)' : ''}>${totAtrasados}</span><span class="delta">${lista.reduce((a, p) => a + (p.proximo ? 1 : 0), 0)} proyectos con hitos pendientes</span></div>
      <div class="tarjeta estadistica"><span class="etq"><${Ic} n="octagon-alert" />Restricciones vencidas</span><span class="valor num" style=${totVencidas ? 'color:var(--critico-texto)' : ''}>${totVencidas}</span><span class="delta">se registran desde la Etapa 3</span></div>
      <div class="tarjeta estadistica"><span class="etq"><${Ic} n="shield-alert" />Riesgos altos</span><span class="valor num">${totRiesgos}</span><span class="delta">se registran desde la Etapa 4</span></div>
    </div>

    <h2 class="seccion-titulo">Proyectos (${lista.length})</h2>
    ${lista.length ? html`<div class="rejilla r-4">${lista.map(p => html`<${TarjetaProyecto} p=${p} />`)}</div>`
      : html`<div class="tarjeta"><${Vacio} titulo="Ningún proyecto coincide con los filtros" texto="Cambia o limpia los filtros para ver tus proyectos."><button class="btn" onClick=${() => setF({ buscar: '', estado: '', tipo: '', responsable: '', archivados: false, fase: '' })}><${Ic} n="x" />Limpiar filtros</button><//></div>`}

    ${lista.length > 0 && html`<h2 class="seccion-titulo">Comparación entre proyectos</h2>
    <div class="rejilla r-21">
      <div class="tarjeta">
        <h2>${titulo}</h2>
        <p class="leer">Cómo leerlo: cada barra es el % del checklist AWP completado; la línea discontinua es el avance esperado a la fecha (% de hitos cuya fecha plan ya pasó). Toca una barra para abrir el proyecto.</p>
        <${BarrasH} aria="Implementación AWP por proyecto" datos=${lista.map(p => ({ etq: p.nombre, valor: p.awp, meta: p.meta, color: colorEstado(p.semaforo), tip: `Implementación ${Math.round(p.awp)} %${p.meta != null ? ` · esperado ${Math.round(p.meta)} %` : ''}`, onClick: () => ir('/p/' + p.id) }))} />
        <div class="leyenda"><span><i style="background:var(--ok)"></i>Al día</span><span><i style="background:var(--atencion)"></i>Atención</span><span><i style="background:var(--critico)"></i>Requiere acción</span><span><i class="linea-meta"></i>Esperado a la fecha</span></div>
      </div>
      <div class="tarjeta">
        <h2>Resumen comparativo</h2>
        <p class="leer">Semáforo: rojo con 2 o más hitos atrasados o restricciones vencidas; ámbar con 1 atrasado o un hito que vence en 7 días.</p>
        <div class="tabla-env"><table class="tabla-movil num"><thead><tr><th>Proyecto</th><th>AWP</th><th>Atrasados</th><th>Estado</th></tr></thead>
          <tbody>${lista.map(p => html`<tr onClick=${() => ir('/p/' + p.id)}>
            <td data-etq="Proyecto"><b>${p.codigo}</b><br /><small style="color:var(--texto-2)">${p.nombre}</small></td>
            <td data-etq="AWP"><div style="display:flex;gap:8px;align-items:center;white-space:nowrap"><div class="barra-mini"><i style=${`width:${p.awp}%;background:${colorEstado(p.semaforo)}`}></i></div>${Math.round(p.awp)} %</div></td>
            <td data-etq="Hitos atrasados">${p.atrasados}</td>
            <td data-etq="Estado"><${Chip} estado=${p.semaforo}>${TEXTO_SEMAFORO[p.semaforo]}<//></td></tr>`)}</tbody></table></div>
      </div>
    </div>`}`}
  </main>`;
}
