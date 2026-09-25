// Configuración pública de la aplicación.
// La URL y la clave «publishable» de Supabase son públicas por diseño: la
// seguridad la dan las reglas Row Level Security de la base de datos.
// Nunca pongas aquí la clave secreta (service_role / secret key).
const SUPABASE = {
  url: 'https://lowiiqbbtpdhtaezgixk.supabase.co',
  clave: 'sb_publishable_-GiXbpFqv9c7aIP32bF94g_kf7Nvf1v',
};

// En el entorno de pruebas local (app/supabase/pruebas/entorno_local) la app
// usa el servidor de pruebas que imita Supabase.
const LOCAL = ['localhost', '127.0.0.1'].includes(location.hostname);

export const CONFIG = {
  supabaseUrl: LOCAL ? location.origin : SUPABASE.url,
  supabaseClave: LOCAL ? 'clave-publica-de-prueba' : SUPABASE.clave,
  // Raíz de la web de consulta (la app vive en /01-awp/app/).
  web: new URL('../', location.href).href,
  local: LOCAL,
};
