// «Tu próximo paso», insignias, borradores y recorrido guiado.
import { html, useEffect, useState } from '../vendor/preact-htm.js';
import { sb, q } from './db.js';
import { actualizar, avisar, obtener, useEstado } from './estado.js';
import { fmt, dias, sumarDias } from './fechas.js';
import { Ic, celebrar } from './ui.js';

// ---------------------------------------------------------------- próximo paso
// Reglas en orden de prioridad: se muestra la primera que se cumple.
export function proximoPaso({ proyecto, fases, personas, actividades, hitos, catalogos, corte }) {
  const base = `#/p/${proyecto.id}`;
  if (!fases.length) return { titulo: 'Agrega las fases del proyecto', texto: 'Todo lo que registres (paquetes, restricciones, hitos) se vincula a una fase. Empieza por definirlas.', boton: 'Agregar fases', ir: base + '/fases', icono: 'layers' };
  const rolesAsignados = new Set(personas.filter(p => p.activo).map(p => p.rol_codigo));
  if (!rolesAsignados.has('CHA')) return { titulo: 'Designa al AWP Champion', texto: 'Es el primer nombramiento del plan (hito H0) y debe ser a tiempo completo: lidera la implementación, forma al equipo y consolida los KPI.', boton: 'Asignar roles', ir: base + '/editar?pestana=equipo', icono: 'users' };
  const faseDe = id => fases.find(f => f.id === id);
  const pendientes = hitos.filter(h => !['Cumplido', 'No aplica'].includes(h.estado));
  const atrasados = pendientes.filter(h => h.fecha_plan && h.fecha_plan < corte).sort((a, b) => a.fecha_plan.localeCompare(b.fecha_plan));
  if (atrasados.length) {
    const h = atrasados[0], f = faseDe(h.fase_id);
    return { titulo: `Revisa el hito ${h.codigo} · ${h.nombre}${f ? ' de la Fase ' + f.numero : ''}`, texto: `Debía cumplirse el ${fmt(h.fecha_plan)} (hace ${dias(h.fecha_plan, corte)} días). Registra la evidencia si ya se cumplió o actualiza su fecha plan.${atrasados.length > 1 ? ` Hay ${atrasados.length} hitos atrasados.` : ''}`, boton: 'Ver hitos', ir: base + '/hitos?filtro=atrasados', icono: 'flag', estado: 'critico' };
  }
  const porEtapa = catalogos.etapas.map(e => ({ etapa: e, acts: actividades.filter(a => a.cat?.etapa === e.nombre && a.estado !== 'No aplica') }));
  for (const { etapa, acts } of porEtapa) {
    const siguiente = acts.find(a => a.estado === 'En curso') || acts.find(a => a.estado === 'Pendiente');
    if (siguiente) {
      const hechas = acts.filter(a => a.estado === 'Completada').length;
      return { titulo: `${siguiente.estado === 'En curso' ? 'Termina' : 'Sigue con'}: ${siguiente.cat.nombre}`, texto: `${siguiente.cat.descripcion} Etapa «${etapa.nombre}»: ${hechas} de ${acts.length} actividades completadas.`, boton: 'Ir al checklist', ir: `${base}/avance?etapa=${etapa.codigo}`, icono: 'list-checks' };
    }
  }
  const proximos = pendientes.filter(h => h.fecha_plan && h.fecha_plan <= sumarDias(corte, 30)).sort((a, b) => a.fecha_plan.localeCompare(b.fecha_plan));
  if (proximos.length) {
    const h = proximos[0];
    return { titulo: `Prepara la evidencia del hito ${h.codigo} · ${h.nombre}`, texto: `Vence el ${fmt(h.fecha_plan)}. Criterio: ${h.criterio || 'ver el plan de implementación'}.`, boton: 'Ver hitos', ir: base + '/hitos', icono: 'flag', estado: 'atencion' };
  }
  return { titulo: '¡Todo al día!', texto: 'No hay hitos atrasados ni actividades pendientes en el checklist. Revisa los próximos hitos y mantén los datos actualizados cada semana.', boton: 'Ver hitos', ir: base + '/hitos', icono: 'party-popper', estado: 'ok' };
}

// ---------------------------------------------------------------- insignias
export const INSIGNIAS = [
  { codigo: 'primer-paso', nombre: 'Primer paso', icono: 'flag', como: 'Crea el proyecto con sus fases.' },
  { codigo: 'equipo-formado', nombre: 'Equipo formado', icono: 'users', como: 'Asigna AWP Champion, Líder de WFP y Gerente de Construcción.' },
  { codigo: 'etapa-FEL', nombre: 'FEL completa', icono: 'award', como: 'Completa las actividades de planificación temprana.' },
  { codigo: 'areas-definidas', nombre: 'Áreas definidas', icono: 'map', como: 'Cumple el hito H1 (CWA definidas) en alguna fase.' },
  { codigo: 'ruta-trazada', nombre: 'Ruta trazada', icono: 'route', como: 'Cumple el hito H2 (Path of Construction aprobado).' },
  { codigo: 'paquetes-alineados', nombre: 'Paquetes alineados', icono: 'package', como: 'Cumple el hito H3 (CWP, EWP y PWP definidos).' },
  { codigo: 'etapa-ING', nombre: 'Ingeniería completa', icono: 'pencil-ruler', como: 'Completa las actividades de ingeniería.' },
  { codigo: 'primer-iwp', nombre: 'Primer IWP liberado', icono: 'badge-check', como: 'Cumple el hito H7.' },
  { codigo: 'backlog-estable', nombre: 'Backlog estable', icono: 'calendar-range', como: 'Cumple el hito H8.' },
  { codigo: 'etapa-CON', nombre: 'Construcción completa', icono: 'hard-hat', como: 'Completa las actividades de construcción.' },
  { codigo: 'fase-cerrada', nombre: 'Fase cerrada', icono: 'graduation-cap', como: 'Cumple el hito H10 (cierre AWP de la fase).' },
  { codigo: 'implementacion-completa', nombre: 'AWP implementado', icono: 'rocket', como: 'Completa las 5 etapas del checklist.' },
];
const HITO_INSIGNIA = { H1: 'areas-definidas', H2: 'ruta-trazada', H3: 'paquetes-alineados', H7: 'primer-iwp', H8: 'backlog-estable', H10: 'fase-cerrada' };

// Calcula qué insignias corresponden, guarda las nuevas y celebra.
export async function revisarInsignias({ proyecto, fases, personas, actividades, hitos, catalogos, obtenidas }) {
  const merecidas = new Set();
  if (fases.length) merecidas.add('primer-paso');
  const roles = new Set(personas.filter(p => p.activo).map(p => p.rol_codigo));
  if (['CHA', 'LWF', 'CON'].every(r => roles.has(r))) merecidas.add('equipo-formado');
  let etapasCompletas = 0;
  for (const e of catalogos.etapas) {
    const acts = actividades.filter(a => a.cat?.etapa === e.nombre && a.estado !== 'No aplica');
    if (acts.length && acts.every(a => a.estado === 'Completada')) { etapasCompletas++; merecidas.add('etapa-' + e.codigo); }
  }
  if (etapasCompletas === catalogos.etapas.length) merecidas.add('implementacion-completa');
  hitos.filter(h => h.estado === 'Cumplido' && HITO_INSIGNIA[h.codigo]).forEach(h => merecidas.add(HITO_INSIGNIA[h.codigo]));
  const yaTiene = new Set(obtenidas.map(i => i.codigo));
  const nuevas = [...merecidas].filter(c => !yaTiene.has(c) && INSIGNIAS.some(i => i.codigo === c));
  if (!nuevas.length) return obtenidas;
  try {
    const filas = await q(sb.from('insignias').insert(nuevas.map(codigo => ({ proyecto_id: proyecto.id, codigo }))).select());
    const nombres = nuevas.map(c => INSIGNIAS.find(i => i.codigo === c).nombre);
    if (obtenidas.length || nuevas.length) { celebrar(); avisar(`¡Nueva insignia${nuevas.length > 1 ? 's' : ''}! ${nombres.join(' · ')}`); }
    return obtenidas.concat(filas);
  } catch (e) { return obtenidas; }
}

// ---------------------------------------------------------------- borradores
// Se guardan en el navegador al instante y en Supabase (tabla borradores) para
// continuarlos desde otro dispositivo.
const CLAVE_LOCAL = c => 'awp-borrador-' + c;
export async function leerBorrador(clave) {
  let local = null;
  try { local = JSON.parse(localStorage.getItem(CLAVE_LOCAL(clave)) || 'null'); } catch (e) {}
  try {
    const remoto = await q(sb.from('borradores').select('contenido, actualizado_en').eq('clave', clave).maybeSingle());
    if (remoto && (!local || remoto.actualizado_en > local.guardado)) return remoto.contenido;
  } catch (e) {}
  return local?.datos || null;
}
let temporizador;
export function guardarBorrador(clave, datos, proyectoId = null) {
  const guardado = new Date().toISOString();
  try { localStorage.setItem(CLAVE_LOCAL(clave), JSON.stringify({ datos, guardado })); } catch (e) {}
  clearTimeout(temporizador);
  temporizador = setTimeout(async () => {
    const usuario = obtener().sesion?.user?.id;
    if (!usuario) return;
    try { await q(sb.from('borradores').upsert({ usuario_id: usuario, clave, proyecto_id: proyectoId, contenido: datos, actualizado_en: new Date().toISOString() })); } catch (e) {}
  }, 1500);
  return guardado;
}
export async function borrarBorrador(clave) {
  clearTimeout(temporizador);
  try { localStorage.removeItem(CLAVE_LOCAL(clave)); } catch (e) {}
  try { await q(sb.from('borradores').delete().eq('clave', clave)); } catch (e) {}
}

// ---------------------------------------------------------------- recorrido guiado
const PASOS_TOUR = [
  { sel: '[data-tour="marca"]', icono: 'sparkles', titulo: '¡Bienvenido a tu guía de AWP!', texto: 'Esta aplicación te acompaña a implementar Advanced Work Packaging en tus proyectos. Te muestro lo principal en un minuto.' },
  { sel: '[data-tour="portafolio"]', icono: 'layout-grid', titulo: 'Tu portafolio', texto: 'Aquí verás todos tus proyectos, con el % de implementación AWP, los hitos atrasados y el próximo hito de cada uno.' },
  { sel: '[data-tour="nuevo"]', icono: 'plus', titulo: 'Crea un proyecto paso a paso', texto: 'Un asistente de 4 pasos (datos, fases, roles e hitos) arma el proyecto con el checklist AWP y los hitos del kit ya cargados.' },
  { sel: '[data-tour="recursos"]', icono: 'library', titulo: 'Recursos del kit', texto: 'Todas las plantillas Word y Excel, el plan de implementación y la presentación de capacitación, siempre a mano.' },
  { sel: '[data-tour="tema"]', icono: 'moon', titulo: 'Modo claro u oscuro', texto: 'Cámbialo cuando quieras; la aplicación también se adapta al celular.' },
  { sel: '[data-tour="ayuda"]', icono: 'circle-help', titulo: 'Ayuda siempre disponible', texto: 'Repite este recorrido desde aquí. Dentro de cada módulo verás «¿Qué es esto y para qué sirve?» y las siglas subrayadas se explican al tocarlas.' },
];
export function iniciarTour() { actualizar({ tour: 0 }); }
async function marcarTourVisto() {
  const u = obtener().sesion?.user?.id;
  if (!u) return;
  try { await q(sb.from('perfiles').upsert({ id: u, tour_visto: true })); } catch (e) {}
  try { localStorage.setItem('awp-tour-visto', '1'); } catch (e) {}
}
export function Tour() {
  const { tour } = useEstado();
  const [pos, setPos] = useState(null);
  const visibles = PASOS_TOUR.filter(p => { const el = document.querySelector(p.sel); return el && el.offsetParent !== null; });
  const paso = tour != null ? visibles[tour] : null;
  useEffect(() => {
    document.querySelectorAll('.resaltado-tour').forEach(e => e.classList.remove('resaltado-tour'));
    if (!paso) { setPos(null); return; }
    const el = document.querySelector(paso.sel);
    el.scrollIntoView({ block: 'center' }); el.classList.add('resaltado-tour');
    const r = el.getBoundingClientRect();
    const abajo = r.bottom + 220 < innerHeight;
    setPos({ top: abajo ? r.bottom + 12 : Math.max(12, r.top - 200), left: Math.max(12, Math.min(r.left, innerWidth - 342)) });
  }, [tour, paso?.sel]);
  // Si la pantalla aún no termina de cargar, se reintenta en un momento.
  const [, reintentar] = useState(0);
  useEffect(() => { if (tour != null && !visibles.length) { const t = setTimeout(() => reintentar(n => n + 1), 300); return () => clearTimeout(t); } });
  if (tour == null || !visibles.length) return null;
  if (!paso) { actualizar({ tour: null }); marcarTourVisto(); return null; }
  const cerrar = () => { document.querySelectorAll('.resaltado-tour').forEach(e => e.classList.remove('resaltado-tour')); actualizar({ tour: null }); marcarTourVisto(); };
  return pos && html`<div class="tour-caja" role="dialog" aria-live="polite" style=${`top:${pos.top}px;left:${pos.left}px`}>
    <h4><${Ic} n=${paso.icono} />${paso.titulo}</h4><p>${paso.texto}</p>
    <div class="pie"><span class="puntos">${visibles.map((_, i) => html`<i class=${i === tour ? 'on' : ''} />`)}</span>
      <button class="btn btn-chico" onClick=${cerrar}>Saltar</button>
      <button class="btn btn-chico btn-primario" onClick=${() => tour === visibles.length - 1 ? cerrar() || avisar('¡Listo! Puedes repetir el recorrido desde el botón de ayuda (?).') : actualizar({ tour: tour + 1 })}>${tour === visibles.length - 1 ? 'Terminar' : 'Siguiente'}</button></div>
  </div>`;
}
