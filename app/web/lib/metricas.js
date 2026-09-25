// Indicadores comunes al portafolio y al proyecto.
import { hoyISO, sumarDias } from './fechas.js';

export const corteDe = p => p.fecha_corte || hoyISO();

// % de implementación AWP: actividades completadas (+ ½ de las en curso) sobre
// las aplicables, igual que la vista v_avance_etapas.
export function avanceAWP(filas) {
  const total = filas.reduce((a, f) => a + Number(f.actividades), 0);
  if (!total) return 0;
  const hecho = filas.reduce((a, f) => a + Number(f.completadas) + 0.5 * Number(f.en_curso), 0);
  return 100 * hecho / total;
}

export const pendiente = h => !['Cumplido', 'No aplica'].includes(h.estado);
export const atrasados = (hitos, corte) => hitos.filter(h => pendiente(h) && h.fecha_plan && h.fecha_plan < corte);
export const proximos = (hitos, corte, n = 30) => hitos.filter(h => pendiente(h) && h.fecha_plan && h.fecha_plan >= corte && h.fecha_plan <= sumarDias(corte, n)).sort((a, b) => a.fecha_plan.localeCompare(b.fecha_plan));

// Meta a la fecha: % de hitos cuya fecha plan ya pasó (avance esperado).
export function metaALaFecha(hitos, corte) {
  const aplicables = hitos.filter(h => h.estado !== 'No aplica' && h.fecha_plan);
  if (!aplicables.length) return null;
  return 100 * aplicables.filter(h => h.fecha_plan <= corte).length / aplicables.length;
}

// Semáforo del proyecto: rojo con 2 o más hitos atrasados o restricciones
// vencidas; ámbar con 1 hito atrasado o un hito que vence en 7 días; verde si no.
export function semaforo({ hitos, corte, vencidas = 0 }) {
  const n = atrasados(hitos, corte).length;
  if (n >= 2 || vencidas > 0) return 'critico';
  if (n === 1 || proximos(hitos, corte, 7).length) return 'atencion';
  return 'ok';
}
export const TEXTO_SEMAFORO = { ok: 'Al día', atencion: 'Atención', critico: 'Requiere acción' };

// % total del checklist AWP (las actividades en curso cuentan la mitad).
export function porcentajeTotal(actividades) {
  const aplic = actividades.filter(a => a.estado !== 'No aplica');
  if (!aplic.length) return 0;
  return 100 * (aplic.filter(a => a.estado === 'Completada').length + 0.5 * aplic.filter(a => a.estado === 'En curso').length) / aplic.length;
}

// % por etapa del ciclo de vida a partir del checklist.
export function avancePorEtapa(actividades, etapas) {
  return etapas.map(e => {
    const acts = actividades.filter(a => a.cat?.etapa === e.nombre && a.estado !== 'No aplica');
    const hecho = acts.filter(a => a.estado === 'Completada').length + 0.5 * acts.filter(a => a.estado === 'En curso').length;
    return { etapa: e, total: acts.length, completadas: acts.filter(a => a.estado === 'Completada').length, pct: acts.length ? 100 * hecho / acts.length : 0 };
  });
}

