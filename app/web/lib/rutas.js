// Rutas con «#» (GitHub Pages solo sirve archivos estáticos).
export function leerRuta() {
  const [camino, consulta = ''] = (location.hash.slice(1) || '/portafolio').split('?');
  return { partes: camino.split('/').filter(Boolean), params: Object.fromEntries(new URLSearchParams(consulta)) };
}
export const ir = destino => { location.hash = destino.startsWith('#') ? destino : '#' + destino; };
