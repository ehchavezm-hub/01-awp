"""Aplicación local: una página en el navegador donde se arrastran los PDF y EPUB.

Todo ocurre en esta computadora: el servidor solo escucha en 127.0.0.1 y los
archivos no salen de ella. Se inicia con `python -m doc2md.app`.
"""

from __future__ import annotations

import io
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
import webbrowser
import zipfile
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import urlopen

from .conversion import FORMATOS, Opciones, Resumen, convertir

PUERTO = 8765
_MAX_BYTES = 2 * 1024**3
_BLOQUE = 1024 * 1024
_CARACTERES_INVALIDOS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _nombre_seguro(nombre: str) -> str:
    nombre = _CARACTERES_INVALIDOS.sub("_", Path(nombre.replace("\\", "/")).name).strip(" .")
    return nombre or "documento"


def _abrir_en_sistema(ruta: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(ruta)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(ruta)])
    else:
        subprocess.Popen(["xdg-open", str(ruta)])


def _contar_unidades(origen: Path) -> int | None:
    try:
        if origen.suffix.lower() == ".pdf":
            import pypdfium2 as pdfium

            pdf = pdfium.PdfDocument(origen)
            try:
                return len(pdf)
            finally:
                pdf.close()
        from .epub import capitulos

        with zipfile.ZipFile(origen) as z:
            return len(capitulos(z))
    except Exception:
        return None


@dataclass
class Trabajo:
    id: str
    nombre: str
    entrada: Path
    salida: Path
    opciones: Opciones
    estado: str = "cola"  # cola | convirtiendo | listo | error
    unidades: int | None = None
    inicio: float | None = None
    fin: float | None = None
    error: str = ""
    resumen: Resumen | None = field(default=None, repr=False)

    def a_json(self) -> dict:
        datos = {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": "pdf" if self.nombre.lower().endswith(".pdf") else "epub",
            "estado": self.estado,
            "unidades": self.unidades,
            "segundos": round((self.fin or time.time()) - self.inicio) if self.inicio else 0,
            "error": self.error,
            "carpeta": str(self.salida),
        }
        r = self.resumen
        if r:
            datos.update(
                ok=r.ok,
                total=len(r.resultados),
                aprobadas=len(r.resultados) - len(r.por_revisar),
                cobertura=r.cobertura,
                revisar=[
                    {
                        "etiqueta": u.etiqueta,
                        "faltantes": sum(u.faltantes.values()),
                        "sobrantes": sum(u.sobrantes.values()),
                        "ocr": u.ocr or u.sin_referencia,
                    }
                    for u in r.por_revisar[:200]
                ],
                avisos=r.avisos,
            )
        return datos


class Cola:
    """Convierte los archivos de a uno (Docling usa toda la CPU)."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.trabajos: dict[str, Trabajo] = {}
        self._cola: queue.Queue[Trabajo] = queue.Queue()
        self._lock = threading.Lock()
        threading.Thread(target=self._procesar, daemon=True).start()

    def agregar(self, nombre: str, entrada: Path, opciones: Opciones) -> Trabajo:
        stem = Path(nombre).stem
        salida = self.base / stem
        with self._lock:
            en_uso = {t.salida for t in self.trabajos.values() if t.estado in ("cola", "convirtiendo")}
            n = 2
            while salida in en_uso:
                salida = self.base / f"{stem} ({n})"
                n += 1
            t = Trabajo(uuid.uuid4().hex[:12], nombre, entrada, salida, opciones)
            self.trabajos[t.id] = t
        t.unidades = _contar_unidades(entrada)
        self._cola.put(t)
        return t

    def lista(self) -> list[dict]:
        with self._lock:
            return [t.a_json() for t in self.trabajos.values()]

    def quitar(self, id_: str) -> bool:
        with self._lock:
            t = self.trabajos.get(id_)
            if t is None or t.estado in ("cola", "convirtiendo"):
                return False
            del self.trabajos[id_]
            return True

    def _procesar(self) -> None:
        while True:
            t = self._cola.get()
            t.estado, t.inicio = "convirtiendo", time.time()
            print(f"Convirtiendo {t.nombre}…", flush=True)
            try:
                if t.salida.exists():
                    shutil.rmtree(t.salida)
                t.resumen = convertir(t.entrada, t.salida, t.opciones)
                t.estado = "listo"
                print(f"  {'OK' if t.resumen.ok else 'REVISAR'}: {t.salida}", flush=True)
            except Exception as e:
                traceback.print_exc()
                t.estado, t.error = "error", str(e) or type(e).__name__
                if t.salida.exists() and not any(t.salida.iterdir()):
                    t.salida.rmdir()
            finally:
                t.fin = time.time()
                shutil.rmtree(t.entrada.parent, ignore_errors=True)


class Manejador(BaseHTTPRequestHandler):
    cola: Cola
    entrada: Path

    def log_message(self, *args) -> None:  # sin registro de cada petición
        pass

    def _enviar(self, codigo: int, cuerpo: bytes, tipo: str, extra: dict | None = None) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, datos, codigo: int = 200) -> None:
        self._enviar(codigo, json.dumps(datos, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def _trabajo(self, q: dict) -> Trabajo | None:
        t = self.cola.trabajos.get(q.get("id", [""])[0])
        return t if t and t.estado == "listo" and t.resumen else None

    def do_GET(self) -> None:
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/":
            self._enviar(200, PAGINA.encode(), "text/html; charset=utf-8")
        elif url.path == "/api/estado":
            self._json({"app": "doc2md"})
        elif url.path == "/api/trabajos":
            self._json(self.cola.lista())
        elif url.path == "/api/ver":
            t = self._trabajo(q)
            if not t:
                return self._json({"error": "no encontrado"}, 404)
            ruta = t.resumen.informe if q.get("que", [""])[0] == "informe" else t.resumen.markdown
            self._enviar(200, ruta.read_bytes(), "text/plain; charset=utf-8")
        elif url.path == "/api/zip":
            t = self._trabajo(q)
            if not t:
                return self._json({"error": "no encontrado"}, 404)
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(t.salida.rglob("*")):
                    if f.is_file():
                        z.write(f, f.relative_to(t.salida))
            nombre = f"{t.salida.name}.zip"
            self._enviar(200, buf.getvalue(), "application/zip", {
                "Content-Disposition": f"attachment; filename*=UTF-8''{_url(nombre)}"
            })
        else:
            self._json({"error": "no encontrado"}, 404)

    def do_POST(self) -> None:
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/api/subir":
            return self._subir(q)
        if url.path == "/api/abrir":
            t = self._trabajo(q)
            destino = t.salida if t else self.cola.base
            destino.mkdir(parents=True, exist_ok=True)
            try:
                _abrir_en_sistema(destino)
            except Exception as e:
                return self._json({"error": str(e)}, 500)
            return self._json({"ok": True})
        if url.path == "/api/quitar":
            return self._json({"ok": self.cola.quitar(q.get("id", [""])[0])})
        self._json({"error": "no encontrado"}, 404)

    def _subir(self, q: dict) -> None:
        nombre = _nombre_seguro(unquote(self.headers.get("X-Nombre", "")))
        if Path(nombre).suffix.lower() not in FORMATOS:
            return self._json({"error": f"{nombre}: solo se aceptan archivos PDF o EPUB"}, 400)
        tam = int(self.headers.get("Content-Length") or 0)
        if not 0 < tam <= _MAX_BYTES:
            return self._json({"error": f"{nombre}: archivo vacío o demasiado grande"}, 400)

        carpeta = self.entrada / uuid.uuid4().hex
        carpeta.mkdir(parents=True)
        destino = carpeta / nombre
        restante = tam
        with open(destino, "wb") as f:
            while restante:
                bloque = self.rfile.read(min(_BLOQUE, restante))
                if not bloque:
                    break
                f.write(bloque)
                restante -= len(bloque)
        if restante:
            shutil.rmtree(carpeta, ignore_errors=True)
            return self._json({"error": f"{nombre}: la subida se interrumpió"}, 400)

        opciones = Opciones(
            ocr=q.get("ocr", ["auto"])[0] if q.get("ocr", ["auto"])[0] in ("auto", "siempre", "nunca") else "auto",
            conservar_encabezados=q.get("encabezados", ["0"])[0] == "1",
        )
        t = self.cola.agregar(nombre, destino, opciones)
        self._json(t.a_json())


def _url(texto: str) -> str:
    from urllib.parse import quote

    return quote(texto)


def _ya_abierta(puerto: int) -> bool:
    try:
        with urlopen(f"http://127.0.0.1:{puerto}/api/estado", timeout=1) as r:
            return json.load(r).get("app") == "doc2md"
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="doc2md.app", description="Aplicación local de doc2md")
    p.add_argument("--resultados", type=Path, default=Path(__file__).resolve().parent.parent / "resultados")
    p.add_argument("--puerto", type=int, default=PUERTO)
    p.add_argument("--sin-navegador", action="store_true")
    args = p.parse_args(argv)

    if _ya_abierta(args.puerto):
        print("doc2md ya estaba abierto; lo muestro en el navegador.")
        if not args.sin_navegador:
            webbrowser.open(f"http://127.0.0.1:{args.puerto}/")
        return 0

    base = args.resultados.resolve()
    entrada = base / ".entrada"
    shutil.rmtree(entrada, ignore_errors=True)
    entrada.mkdir(parents=True, exist_ok=True)

    Manejador.cola = Cola(base)
    Manejador.entrada = entrada
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Manejador)
    except OSError:
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
    direccion = f"http://127.0.0.1:{servidor.server_address[1]}/"

    print("=" * 60)
    print(" doc2md está abierto en tu navegador:")
    print(f"   {direccion}")
    print(f" Resultados en: {base}")
    print(" Deja esta ventana abierta mientras lo uses.")
    print(" Para cerrarlo, cierra esta ventana.")
    print("=" * 60, flush=True)
    if not args.sin_navegador:
        threading.Timer(0.5, webbrowser.open, [direccion]).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


PAGINA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>doc2md</title>
<style>
:root {
  --fondo: #f6f5f2; --panel: #ffffff; --texto: #1d1d1b; --suave: #6b6a66; --borde: #dedcd6;
  --acento: #2f5bd3; --acento-suave: #e8eefc; --ok: #1f7a4d; --ok-suave: #e3f3ea;
  --alerta: #a35b00; --alerta-suave: #fbeedb; --error: #b3261e; --error-suave: #fbe4e2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --fondo: #161614; --panel: #201f1d; --texto: #ecebe7; --suave: #a3a19b; --borde: #3a3935;
    --acento: #8aa8ff; --acento-suave: #232c45; --ok: #6fd3a0; --ok-suave: #1b3027;
    --alerta: #f0b563; --alerta-suave: #3a2c17; --error: #ff8a80; --error-suave: #3d1f1d;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fondo); color: var(--texto);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 32px 16px 64px; }
header { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
h1 { font-size: 26px; margin: 0; letter-spacing: -0.01em; }
.sub { color: var(--suave); margin: 4px 0 24px; }
button, .boton { font: inherit; font-size: 14px; border: 1px solid var(--borde); background: var(--panel);
  color: var(--texto); padding: 6px 12px; border-radius: 8px; cursor: pointer; text-decoration: none; }
button:hover, .boton:hover { border-color: var(--acento); color: var(--acento); }
.zona { border: 2px dashed var(--borde); border-radius: 16px; background: var(--panel);
  padding: 48px 16px; text-align: center; transition: .15s; cursor: pointer; }
.zona.encima { border-color: var(--acento); background: var(--acento-suave); }
.zona strong { display: block; font-size: 19px; margin-bottom: 6px; }
.zona span { color: var(--suave); }
.icono { font-size: 40px; line-height: 1; margin-bottom: 12px; }
details { margin: 12px 0 0; color: var(--suave); font-size: 14px; }
details label { display: inline-flex; gap: 6px; align-items: center; margin: 8px 16px 0 0; }
select { font: inherit; }
#lista { margin-top: 28px; display: grid; gap: 12px; }
.tarjeta { background: var(--panel); border: 1px solid var(--borde); border-radius: 12px; padding: 14px 16px; }
.fila { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.nombre { font-weight: 600; flex: 1; min-width: 0; overflow-wrap: anywhere; }
.estado { font-size: 13px; padding: 2px 10px; border-radius: 99px; white-space: nowrap; }
.e-cola, .e-subiendo { background: var(--acento-suave); color: var(--acento); }
.e-convirtiendo { background: var(--acento-suave); color: var(--acento); }
.e-ok { background: var(--ok-suave); color: var(--ok); }
.e-revisar { background: var(--alerta-suave); color: var(--alerta); }
.e-error { background: var(--error-suave); color: var(--error); }
.detalle { color: var(--suave); font-size: 14px; margin-top: 6px; }
.acciones { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.barra { height: 4px; background: var(--acento-suave); border-radius: 4px; overflow: hidden; margin-top: 10px; }
.barra i { display: block; height: 100%; background: var(--acento); width: 0; transition: width .2s; }
.barra.indef i { width: 30%; animation: ir 1.4s ease-in-out infinite; }
@keyframes ir { from { transform: translateX(-100%); } to { transform: translateX(340%); } }
ul.revisar { margin: 8px 0 0; padding-left: 20px; font-size: 14px; max-height: 180px; overflow: auto; }
.vacio { color: var(--suave); text-align: center; margin-top: 28px; }
footer { margin-top: 40px; color: var(--suave); font-size: 13px; }
</style>
</head>
<body>
<main>
  <header>
    <h1>doc2md</h1>
    <button id="carpeta" type="button">📂 Abrir carpeta de resultados</button>
  </header>
  <p class="sub">PDF y EPUB a Markdown, con verificación página por página contra el original.</p>

  <div class="zona" id="zona" tabindex="0" role="button" aria-label="Elegir archivos PDF o EPUB">
    <div class="icono">⬇</div>
    <strong>Arrastra aquí tus PDF o EPUB</strong>
    <span>o haz clic para elegirlos</span>
    <input id="archivos" type="file" accept=".pdf,.epub" multiple hidden>
  </div>

  <details>
    <summary>Opciones</summary>
    <label>OCR (páginas escaneadas)
      <select id="ocr">
        <option value="auto" selected>Automático</option>
        <option value="siempre">Siempre (todo el documento)</option>
        <option value="nunca">Nunca</option>
      </select>
    </label>
    <label><input type="checkbox" id="encabezados"> Conservar encabezados y pies de página</label>
  </details>

  <div id="lista"></div>
  <p class="vacio" id="vacio">Todavía no hay archivos. Se convierten de a uno, en el orden en que los agregues.</p>

  <footer>Todo se procesa en esta computadora; nada se sube a internet. Para cerrar doc2md, cierra la ventana negra.</footer>
</main>
<script>
const $ = (s) => document.querySelector(s);
const subiendo = new Map();

function fmtTiempo(s) {
  const m = Math.floor(s / 60), r = s % 60;
  return m ? `${m} min ${String(r).padStart(2, "0")} s` : `${r} s`;
}
function esc(t) {
  return String(t).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function unidad(t, n) {
  return t.tipo === "pdf" ? (n === 1 ? "página" : "páginas") : (n === 1 ? "capítulo" : "capítulos");
}
function verificadas(t) {
  return t.tipo === "pdf" ? "verificadas" : "verificados";
}

function subir(archivo) {
  const clave = Math.random().toString(36).slice(2);
  const nombre = archivo.name;
  if (!/\.(pdf|epub)$/i.test(nombre)) {
    subiendo.set(clave, { nombre, error: "Solo se aceptan archivos PDF o EPUB." });
    return pintar();
  }
  const q = new URLSearchParams({ ocr: $("#ocr").value, encabezados: $("#encabezados").checked ? "1" : "0" });
  const xhr = new XMLHttpRequest();
  subiendo.set(clave, { nombre, avance: 0 });
  xhr.upload.onprogress = (e) => { if (e.lengthComputable) { subiendo.get(clave).avance = e.loaded / e.total; pintar(); } };
  xhr.onload = () => {
    if (xhr.status === 200) subiendo.delete(clave);
    else subiendo.set(clave, { nombre, error: (JSON.parse(xhr.responseText || "{}").error) || "No se pudo subir." });
    actualizar();
  };
  xhr.onerror = () => { subiendo.set(clave, { nombre, error: "No se pudo conectar con doc2md. ¿Cerraste la ventana negra?" }); pintar(); };
  xhr.open("POST", "/api/subir?" + q);
  xhr.setRequestHeader("X-Nombre", encodeURIComponent(nombre));
  xhr.send(archivo);
  pintar();
}

let trabajos = [];
async function actualizar() {
  try { trabajos = await (await fetch("/api/trabajos")).json(); } catch { }
  pintar();
}

function tarjetaSubida(s, clave) {
  if (s.error) return `<div class="tarjeta"><div class="fila"><span class="nombre">${esc(s.nombre)}</span>
    <span class="estado e-error">Error</span><button data-descartar="${clave}">Quitar</button></div>
    <div class="detalle">${esc(s.error)}</div></div>`;
  return `<div class="tarjeta"><div class="fila"><span class="nombre">${esc(s.nombre)}</span>
    <span class="estado e-subiendo">Cargando ${Math.round(s.avance * 100)} %</span></div>
    <div class="barra"><i style="width:${s.avance * 100}%"></i></div></div>`;
}

function tarjeta(t) {
  const partes = t.unidades ? `${t.unidades} ${unidad(t, t.unidades)}` : "";
  let estado, detalle = "", extra = "", acciones = "";
  if (t.estado === "cola") {
    estado = `<span class="estado e-cola">En espera</span>`;
    detalle = [partes, "empieza cuando termine el anterior"].filter(Boolean).join(" · ");
  } else if (t.estado === "convirtiendo") {
    estado = `<span class="estado e-convirtiendo">Convirtiendo…</span>`;
    detalle = [partes, fmtTiempo(t.segundos)].filter(Boolean).join(" · ") + ". Un libro largo puede tardar bastante; no cierres la ventana negra.";
    extra = `<div class="barra indef"><i></i></div>`;
  } else if (t.estado === "error") {
    estado = `<span class="estado e-error">Error</span>`;
    detalle = esc(t.error);
    acciones = `<button data-quitar="${t.id}">Quitar de la lista</button>`;
  } else {
    const u = unidad(t, t.total);
    if (t.ok) {
      estado = `<span class="estado e-ok">✓ Fiel al original</span>`;
      detalle = `${t.aprobadas} de ${t.total} ${u} ${verificadas(t)} · cobertura ${(t.cobertura * 100).toFixed(2)} % · ${fmtTiempo(t.segundos)}`;
    } else {
      estado = `<span class="estado e-revisar">Revisar ${t.total - t.aprobadas} ${unidad(t, t.total - t.aprobadas)}</span>`;
      detalle = `${t.aprobadas} de ${t.total} ${u} ${verificadas(t)} · cobertura ${(t.cobertura * 100).toFixed(2)} % · ${fmtTiempo(t.segundos)}`;
      extra = `<ul class="revisar">` + t.revisar.map((r) => `<li>${esc(r.etiqueta)}: ` +
        (r.ocr ? "pasó por OCR, compárala con el original" :
          [r.faltantes ? (r.faltantes === 1 ? "falta 1 palabra" : `faltan ${r.faltantes} palabras`) : "",
           r.sobrantes ? (r.sobrantes === 1 ? "sobra 1 palabra" : `sobran ${r.sobrantes} palabras`) : ""].filter(Boolean).join(", ")) +
        `</li>`).join("") + `</ul>`;
    }
    if (t.avisos && t.avisos.length) extra += `<div class="detalle">⚠ ${t.avisos.map(esc).join("<br>⚠ ")}</div>`;
    acciones = `<a class="boton" href="/api/ver?id=${t.id}&que=md" target="_blank">Ver Markdown</a>
      <a class="boton" href="/api/ver?id=${t.id}&que=informe" target="_blank">Ver informe</a>
      <a class="boton" href="/api/zip?id=${t.id}">Descargar .zip</a>
      <button data-abrir="${t.id}">📂 Abrir carpeta</button>
      <button data-quitar="${t.id}">Quitar de la lista</button>`;
  }
  return `<div class="tarjeta"><div class="fila"><span class="nombre">${esc(t.nombre)}</span>${estado}</div>
    ${detalle ? `<div class="detalle">${detalle}</div>` : ""}${extra}
    ${acciones ? `<div class="acciones">${acciones}</div>` : ""}</div>`;
}

function pintar() {
  const html = [...subiendo].map(([k, s]) => tarjetaSubida(s, k)).join("") + [...trabajos].reverse().map(tarjeta).join("");
  $("#lista").innerHTML = html;
  $("#vacio").hidden = !!html;
}

$("#lista").addEventListener("click", async (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  if (b.dataset.abrir) fetch("/api/abrir?id=" + b.dataset.abrir, { method: "POST" });
  if (b.dataset.quitar) { await fetch("/api/quitar?id=" + b.dataset.quitar, { method: "POST" }); actualizar(); }
  if (b.dataset.descartar) { subiendo.delete(b.dataset.descartar); pintar(); }
});
$("#carpeta").onclick = () => fetch("/api/abrir", { method: "POST" });

const zona = $("#zona");
zona.onclick = () => $("#archivos").click();
zona.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("#archivos").click(); } };
$("#archivos").onchange = (e) => { [...e.target.files].forEach(subir); e.target.value = ""; };
["dragenter", "dragover"].forEach((ev) => document.addEventListener(ev, (e) => { e.preventDefault(); zona.classList.add("encima"); }));
["dragleave", "drop"].forEach((ev) => document.addEventListener(ev, (e) => {
  e.preventDefault();
  if (ev === "drop" || !e.relatedTarget) zona.classList.remove("encima");
}));
document.addEventListener("drop", (e) => [...e.dataTransfer.files].forEach(subir));

actualizar();
setInterval(actualizar, 1000);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
