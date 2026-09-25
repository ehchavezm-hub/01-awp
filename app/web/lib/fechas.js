// Fechas en formato local (dd/mm/aaaa) y cálculos simples en días.
export const hoyISO = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
export function aFecha(iso) { if (!iso) return null; const [a, m, d] = iso.slice(0, 10).split('-').map(Number); return new Date(a, m - 1, d); }
export function aISO(f) { if (!f) return null; return `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, '0')}-${String(f.getDate()).padStart(2, '0')}`; }
export function fmt(iso) { if (!iso) return '—'; const [a, m, d] = iso.slice(0, 10).split('-'); return `${d}/${m}/${a}`; }
export function fmtCorta(iso) { if (!iso) return '—'; const f = aFecha(iso); return f.toLocaleDateString('es', { day: '2-digit', month: 'short' }).replace('.', ''); }
export function dias(desde, hasta) { return Math.round((aFecha(hasta) - aFecha(desde)) / 86400000); }
export function sumarDias(iso, n) { const f = aFecha(iso); f.setDate(f.getDate() + n); return aISO(f); }
export function sumarMeses(iso, n) { const f = aFecha(iso); f.setMonth(f.getMonth() + n); return aISO(f); }
export function interpolar(desde, hasta, t) { return sumarDias(desde, Math.round(dias(desde, hasta) * t)); }
export function hace(ts) {
  const s = (Date.now() - new Date(ts).getTime()) / 1000;
  if (s < 60) return 'hace un momento';
  if (s < 3600) return `hace ${Math.round(s / 60)} min`;
  if (s < 86400) return `hace ${Math.round(s / 3600)} h`;
  if (s < 86400 * 30) return `hace ${Math.round(s / 86400)} días`;
  return 'el ' + fmt(new Date(ts).toISOString());
}
