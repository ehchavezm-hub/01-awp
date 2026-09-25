// Inicio de sesión, recuperación y cambio de contraseña.
import { html, useState } from '../vendor/preact-htm.js';
import { sb } from '../lib/db.js';
import { actualizar, avisar } from '../lib/estado.js';
import { Ic, Campo } from '../lib/ui.js';
import { ir } from '../lib/rutas.js';

const correoValido = c => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c);

function Lado() {
  return html`<section class="entrar-lado">
    <${Ic} n="package" cls="ic" style="width:40px;height:40px" />
    <h1>Tu guía para implementar AWP en cada proyecto</h1>
    <p>Registra y sigue la implementación de Advanced Work Packaging en todos tus proyectos, con el mismo kit, las mismas plantillas y los mismos KPI.</p>
    <ul>
      <li><${Ic} n="list-checks" />Checklist AWP por etapa del ciclo de vida, de FEL a comisionamiento.</li>
      <li><${Ic} n="flag" />Hitos H0–H10 por fase, con línea de tiempo plan vs. real.</li>
      <li><${Ic} n="sparkles" />«Tu próximo paso»: qué hacer ahora según el avance.</li>
      <li><${Ic} n="library" />Plantillas, plan y capacitación siempre a mano.</li>
    </ul>
  </section>`;
}

export function VistaEntrar({ ruta }) {
  const [modo, setModo] = useState('entrar');
  const [correo, setCorreo] = useState('');
  const [clave, setClave] = useState('');
  const [ver, setVer] = useState(false);
  const [errores, setErrores] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const entrar = async e => {
    e.preventDefault();
    const err = {};
    if (!correoValido(correo)) err.correo = 'Escribe un correo válido, por ejemplo nombre@empresa.com.';
    if (modo === 'entrar' && !clave) err.clave = 'Escribe tu contraseña.';
    setErrores(err); setMensaje(null);
    if (Object.keys(err).length) return;
    setEnviando(true);
    if (modo === 'entrar') {
      const { error } = await sb.auth.signInWithPassword({ email: correo.trim(), password: clave });
      setEnviando(false);
      if (error) {
        const credenciales = /invalid|credentials/i.test(error.message);
        setMensaje({ tipo: 'error', texto: credenciales ? 'El correo o la contraseña no coinciden.' : 'No se pudo iniciar sesión.', ayuda: credenciales ? 'Revisa mayúsculas y el correo. Si no recuerdas la contraseña, usa «¿Olvidaste tu contraseña?».' : error.message });
        return;
      }
      ir(ruta.params.volver || '/portafolio');
    } else {
      const { error } = await sb.auth.resetPasswordForEmail(correo.trim(), { redirectTo: location.href.split('#')[0] });
      setEnviando(false);
      setMensaje(error ? { tipo: 'error', texto: 'No se pudo enviar el correo.', ayuda: error.message }
        : { tipo: 'ok', texto: 'Listo. Si el correo está registrado, te llegará un enlace para crear una contraseña nueva.', ayuda: 'Revisa también la carpeta de correo no deseado.' });
    }
  };

  return html`<main class="entrar" style="max-width:none;padding:0">
    <${Lado} />
    <section class="entrar-form">
      <form onSubmit=${entrar} novalidate>
        <h2>${modo === 'entrar' ? 'Iniciar sesión' : 'Recuperar contraseña'}</h2>
        <p style="margin:0;color:var(--texto-2)">${modo === 'entrar' ? 'Entra con el correo y la contraseña de tu usuario.' : 'Te enviaremos un enlace para crear una contraseña nueva.'}</p>
        ${mensaje && html`<div class=${'aviso ' + (mensaje.tipo === 'error' ? 'aviso-error' : 'aviso-ok')} role="alert"><${Ic} n=${mensaje.tipo === 'error' ? 'circle-alert' : 'check'} /><div><b>${mensaje.texto}</b>${mensaje.ayuda && html`<br />${mensaje.ayuda}`}</div></div>`}
        <${Campo} etiqueta="Correo" error=${errores.correo}>
          <input type="email" autocomplete="username" value=${correo} onInput=${e => setCorreo(e.target.value)} placeholder="nombre@empresa.com" />
        <//>
        ${modo === 'entrar' && html`<${Campo} etiqueta="Contraseña" error=${errores.clave}>
          <div style="position:relative">
            <input type=${ver ? 'text' : 'password'} autocomplete="current-password" value=${clave} onInput=${e => setClave(e.target.value)} style="width:100%;padding-right:40px" />
            <button type="button" class="btn-ic" style="position:absolute;right:4px;top:3px;color:var(--texto-2)" onClick=${() => setVer(!ver)} aria-label=${ver ? 'Ocultar contraseña' : 'Mostrar contraseña'}><${Ic} n=${ver ? 'eye-off' : 'eye'} /></button>
          </div>
        <//>`}
        <button class="btn btn-primario" type="submit" disabled=${enviando} style="justify-content:center;padding:10px">
          ${enviando ? html`<span class="girador" style="width:16px;height:16px"></span>` : html`<${Ic} n=${modo === 'entrar' ? 'arrow-right' : 'mail'} />`}
          ${modo === 'entrar' ? 'Entrar' : 'Enviar enlace'}</button>
        <button type="button" class="enlace-boton" style="align-self:flex-start" onClick=${() => { setModo(modo === 'entrar' ? 'recuperar' : 'entrar'); setMensaje(null); setErrores({}); }}>
          ${modo === 'entrar' ? '¿Olvidaste tu contraseña?' : 'Volver a iniciar sesión'}</button>
        <div class="aviso aviso-info"><${Ic} n="library" /><div>Sin iniciar sesión puedes ver los <a href="#/recursos">recursos del kit</a>: plantillas, plan y capacitación.</div></div>
      </form>
    </section>
  </main>`;
}

export function VistaNuevaClave() {
  const [clave, setClave] = useState('');
  const [repite, setRepite] = useState('');
  const [errores, setErrores] = useState({});
  const [enviando, setEnviando] = useState(false);
  const guardar = async e => {
    e.preventDefault();
    const err = {};
    if (clave.length < 8) err.clave = 'Usa al menos 8 caracteres, mezclando letras y números.';
    if (repite !== clave) err.repite = 'Las dos contraseñas no coinciden. Escríbelas de nuevo.';
    setErrores(err);
    if (Object.keys(err).length) return;
    setEnviando(true);
    const { error } = await sb.auth.updateUser({ password: clave });
    setEnviando(false);
    if (error) { setErrores({ clave: 'No se pudo cambiar la contraseña: ' + error.message }); return; }
    actualizar({ recuperando: false });
    avisar('¡Listo! Tu contraseña nueva ya está activa.');
    ir('/portafolio');
  };
  return html`<main class="entrar" style="max-width:none;padding:0"><${Lado} />
    <section class="entrar-form"><form onSubmit=${guardar} novalidate>
      <h2>Crea tu contraseña nueva</h2>
      <${Campo} etiqueta="Contraseña nueva" error=${errores.clave} ayuda="Al menos 8 caracteres."><input type="password" autocomplete="new-password" value=${clave} onInput=${e => setClave(e.target.value)} /><//>
      <${Campo} etiqueta="Repite la contraseña" error=${errores.repite}><input type="password" autocomplete="new-password" value=${repite} onInput=${e => setRepite(e.target.value)} /><//>
      <button class="btn btn-primario" type="submit" disabled=${enviando} style="justify-content:center;padding:10px"><${Ic} n="key-round" />Guardar contraseña</button>
    </form></section></main>`;
}
