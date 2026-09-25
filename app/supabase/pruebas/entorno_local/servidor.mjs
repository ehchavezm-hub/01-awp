// Servidor de pruebas que imita Supabase para probar la aplicación sin internet.
//  * /auth/v1/...  → inicio de sesión de prueba (emite tokens JWT como Supabase Auth)
//  * /rest/v1/...  → reenvía a PostgREST (el mismo motor de la API de Supabase)
//  * /01-awp/app/  → la aplicación (app/web) y /01-awp/ → la web MkDocs construida (site/)
// Uso: ver iniciar.sh. Solo para pruebas locales: no usar en producción.
import http from 'node:http';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const PUERTO = Number(process.env.PUERTO || 8080);
const POSTGREST = process.env.POSTGREST || 'http://127.0.0.1:3001';
const SECRETO = process.env.JWT_SECRETO;
const RAIZ = path.resolve(process.env.RAIZ || '.');
const USUARIOS = JSON.parse(process.env.USUARIOS || '[]'); // [{id, email, clave}]

const b64 = b => Buffer.from(b).toString('base64url');
function firmar(usuario) {
  const ahora = Math.floor(Date.now() / 1000);
  const carga = { sub: usuario.id, email: usuario.email, role: 'authenticated', aud: 'authenticated', iat: ahora, exp: ahora + 3600 };
  const base = b64(JSON.stringify({ alg: 'HS256', typ: 'JWT' })) + '.' + b64(JSON.stringify(carga));
  return base + '.' + crypto.createHmac('sha256', SECRETO).update(base).digest('base64url');
}
function leerToken(req) {
  const t = (req.headers.authorization || '').replace(/^Bearer /, '').split('.');
  if (t.length !== 3) return null;
  const firma = crypto.createHmac('sha256', SECRETO).update(t[0] + '.' + t[1]).digest('base64url');
  if (firma !== t[2]) return null;
  return JSON.parse(Buffer.from(t[1], 'base64url'));
}
const datosUsuario = u => ({ id: u.id, email: u.email, aud: 'authenticated', role: 'authenticated', app_metadata: { provider: 'email' }, user_metadata: {}, created_at: '2026-01-01T00:00:00Z' });
function sesion(u) {
  return { access_token: firmar(u), token_type: 'bearer', expires_in: 3600, expires_at: Math.floor(Date.now() / 1000) + 3600, refresh_token: 'r-' + u.id, user: datosUsuario(u) };
}
const json = (res, codigo, obj) => { res.writeHead(codigo, { 'content-type': 'application/json', 'access-control-allow-origin': '*' }); res.end(JSON.stringify(obj)); };
const cuerpo = req => new Promise(r => { let d = ''; req.on('data', c => d += c); req.on('end', () => r(d)); });

async function auth(req, res, url) {
  const ruta = url.pathname.replace('/auth/v1', '');
  if (ruta === '/token') {
    const b = JSON.parse(await cuerpo(req) || '{}');
    const tipo = url.searchParams.get('grant_type');
    let u;
    if (tipo === 'password') u = USUARIOS.find(x => x.email === b.email && x.clave === b.password);
    if (tipo === 'refresh_token') u = USUARIOS.find(x => 'r-' + x.id === b.refresh_token);
    if (!u) return json(res, 400, { error: 'invalid_grant', error_description: 'Invalid login credentials', code: 'invalid_credentials', msg: 'Invalid login credentials' });
    return json(res, 200, sesion(u));
  }
  if (ruta === '/user') {
    const t = leerToken(req);
    const u = t && USUARIOS.find(x => x.id === t.sub);
    if (!u) return json(res, 401, { msg: 'Invalid token' });
    if (req.method === 'PUT') { const b = JSON.parse(await cuerpo(req) || '{}'); if (b.password) u.clave = b.password; }
    return json(res, 200, datosUsuario(u));
  }
  if (ruta === '/logout') { res.writeHead(204); return res.end(); }
  if (ruta === '/recover') return json(res, 200, {});
  return json(res, 404, { msg: 'No implementado en el servidor de pruebas: ' + ruta });
}

function proxy(req, res, url) {
  const destino = new URL(url.pathname.replace('/rest/v1', '') + url.search, POSTGREST);
  const cabeceras = { ...req.headers, host: destino.host };
  const t = leerToken(req);
  if (!t) delete cabeceras.authorization; // clave pública → rol anon
  const p = http.request(destino, { method: req.method, headers: cabeceras }, r => { res.writeHead(r.statusCode, r.headers); r.pipe(res); });
  p.on('error', e => json(res, 502, { message: e.message }));
  req.pipe(p);
}

const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', '.webmanifest': 'application/manifest+json' };
function estatico(req, res, url) {
  let rel = decodeURIComponent(url.pathname);
  let base;
  if (rel.startsWith('/01-awp/app/') && !rel.startsWith('/01-awp/app/maqueta')) { base = path.join(RAIZ, 'app/web'); rel = rel.slice('/01-awp/app/'.length); }
  else if (rel.startsWith('/01-awp/')) { base = path.join(RAIZ, 'site'); rel = rel.slice('/01-awp/'.length); }
  else { res.writeHead(302, { location: '/01-awp/app/' }); return res.end(); }
  let f = path.join(base, rel);
  if (!f.startsWith(base)) { res.writeHead(403); return res.end(); }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('No encontrado'); }
  res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' });
  fs.createReadStream(f).pipe(res);
}

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (req.method === 'OPTIONS') { res.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' }); return res.end(); }
  try {
    if (url.pathname.startsWith('/auth/v1')) return await auth(req, res, url);
    if (url.pathname.startsWith('/rest/v1')) return proxy(req, res, url);
    return estatico(req, res, url);
  } catch (e) { json(res, 500, { message: e.message }); }
}).listen(PUERTO, () => console.log(`Servidor de pruebas en http://localhost:${PUERTO}/01-awp/app/`));
