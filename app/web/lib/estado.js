// Estado global mínimo: sesión, perfil, catálogos y avisos (toast).
import { useEffect, useState } from '../vendor/preact-htm.js';

const estado = { sesion: undefined, perfil: null, catalogos: null, toast: null, modal: null };
const oyentes = new Set();

export function obtener() { return estado; }
export function actualizar(cambios) { Object.assign(estado, cambios); oyentes.forEach(f => f({ ...estado })); }
export function useEstado() {
  const [e, setE] = useState({ ...estado });
  useEffect(() => { oyentes.add(setE); return () => oyentes.delete(setE); }, []);
  return e;
}

let tt;
export function avisar(texto, tipo = 'ok') {
  actualizar({ toast: { texto, tipo, id: Date.now() } });
  clearTimeout(tt);
  tt = setTimeout(() => actualizar({ toast: null }), tipo === 'error' ? 6000 : 3200);
}
export function avisarError(e) { avisar(e?.ayuda ? `${e.message} ${e.ayuda}` : (e?.message || String(e)), 'error'); }

// Confirmación antes de acciones que no se pueden deshacer.
export function confirmar({ titulo, texto, boton = 'Confirmar', peligro = false }) {
  return new Promise(resolver => actualizar({ modal: { titulo, texto, boton, peligro, resolver } }));
}
