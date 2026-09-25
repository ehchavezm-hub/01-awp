// Conexión con Supabase y utilidades de datos.
import { CONFIG } from '../config.js';

export const sb = window.supabase.createClient(CONFIG.supabaseUrl, CONFIG.supabaseClave, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, storageKey: 'awp-sesion' },
});

// Mensajes claros para las restricciones de la base de datos (nombre → texto).
const RESTRICCIONES = {
  proyectos_fechas: 'La fecha de fin del proyecto no puede ser anterior a la de inicio. Revisa las dos fechas.',
  proyectos_codigo_no_vacio: 'El código del proyecto es obligatorio. Usa algo corto, por ejemplo «PTN».',
  fases_fechas: 'La fecha de fin de la fase no puede ser anterior a la de inicio.',
  fases_plazos: 'Los plazos de liberación deben ir de mayor a menor: IWP iniciado ≥ identificadas ≥ asignadas ≥ levantadas ≥ liberación.',
  fases_proyecto_id_numero_key: 'Ya existe una fase con ese número en el proyecto. Usa otro número.',
  hitos_real_si_cumplido: 'Para marcar el hito como cumplido, indica la fecha real en que se cumplió.',
  hitos_unico: 'Ese hito ya existe en esta fase.',
  avance_actividades_unica: 'Esa actividad ya está registrada.',
  cwa_proyecto_id_codigo_key: 'Ya existe una CWA con ese código en el proyecto.',
  paquetes_proyecto_id_codigo_key: 'Ya existe un paquete con ese código en el proyecto.',
  restricciones_proyecto_id_codigo_key: 'Ya existe una restricción con ese código en el proyecto.',
};

export class ErrorAmigable extends Error {
  constructor(mensaje, ayuda, original) {
    super(mensaje);
    this.ayuda = ayuda;
    this.original = original;
  }
}

export function traducirError(e) {
  if (e instanceof ErrorAmigable) return e;
  const texto = `${e?.message || ''} ${e?.details || ''}`;
  const nombre = Object.keys(RESTRICCIONES).find(k => texto.includes(k));
  if (nombre) return new ErrorAmigable(RESTRICCIONES[nombre], null, e);
  switch (e?.code) {
    case '23505': return new ErrorAmigable('Ya existe un registro con esos datos (por ejemplo, el mismo código).', 'Cambia el código o edita el registro existente.', e);
    case '23503': return new ErrorAmigable('No se puede completar porque hay registros relacionados.', 'Por ejemplo, una fase con CWA no se puede borrar: primero mueve o borra sus CWA.', e);
    case '23514': return new ErrorAmigable('Algún dato no cumple las reglas del kit AWP.', 'Revisa fechas y valores de las listas.', e);
    case '23502': return new ErrorAmigable('Falta un dato obligatorio.', 'Completa los campos marcados con *.', e);
    case '42501': return new ErrorAmigable('No tienes permiso para hacer esto en este proyecto.', 'Si deberías tenerlo, pide al propietario del proyecto que te dé acceso de editor.', e);
    case 'P0001': return new ErrorAmigable(e.message, e.hint, e);
    case 'PGRST301':
    case 'PGRST303': return new ErrorAmigable('Tu sesión expiró.', 'Vuelve a iniciar sesión.', e);
  }
  if (/Failed to fetch|NetworkError|Load failed/i.test(texto)) {
    return new ErrorAmigable('No hay conexión con el servidor.', 'Revisa tu internet. Si el problema sigue, el proyecto de Supabase podría estar en pausa: ábrelo en supabase.com y pulsa «Restore project».', e);
  }
  return new ErrorAmigable('Algo salió mal al guardar o leer los datos.', e?.message, e);
}

// Ejecuta una consulta de supabase-js y devuelve los datos o lanza un ErrorAmigable.
export async function q(consulta) {
  const { data, error } = await consulta;
  if (error) throw traducirError(error);
  return data;
}

// Catálogos del kit (solo lectura), cargados una vez por sesión.
let catalogos = null;
export async function cargarCatalogos() {
  if (catalogos) return catalogos;
  const [etapas, roles, hitos, actividades, kpi, raci, tipos] = await Promise.all([
    q(sb.from('cat_etapas').select('*').order('orden')),
    q(sb.from('cat_roles').select('*').order('orden')),
    q(sb.from('cat_hitos').select('*').order('orden')),
    q(sb.from('cat_actividades_awp').select('*').order('codigo')),
    q(sb.from('cat_kpi').select('*').order('codigo')),
    q(sb.from('cat_actividades_raci').select('*').order('orden')),
    q(sb.from('cat_tipos_restriccion').select('*')),
  ]);
  const ordenEtapa = Object.fromEntries(etapas.map(e => [e.nombre, e.orden]));
  actividades.sort((a, b) => ordenEtapa[a.etapa] - ordenEtapa[b.etapa] || a.orden - b.orden);
  catalogos = { etapas, roles, hitos, actividades, kpi, raci, tipos, rol: Object.fromEntries(roles.map(r => [r.codigo, r])) };
  return catalogos;
}
export function limpiarCatalogos() { catalogos = null; }

// Registra la fotografía semanal de indicadores (para las tendencias).
export async function registrarInstantanea(proyectoId) {
  try { await q(sb.rpc('registrar_instantanea', { p_proyecto: proyectoId })); } catch (e) { /* no bloquea la pantalla */ }
}
