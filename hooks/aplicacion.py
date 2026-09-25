"""Publica la aplicación AWP en la web, en /app/.

El código vive en app/web/ (la aplicación) y app/maqueta/ (maqueta de diseño),
fuera de docs/. Este hook los agrega tal cual al sitio: app/web/x → /app/x y
app/maqueta/x → /app/maqueta/x. No se publican app/DISENO.md ni app/supabase/.
"""

from pathlib import Path

from mkdocs.structure.files import File

APP = Path(__file__).resolve().parent.parent / "app"
CARPETAS = {"web": "app", "maqueta": "app/maqueta"}


def on_files(files, config):
    for origen, destino in CARPETAS.items():
        carpeta = APP / origen
        if not carpeta.is_dir():
            continue
        for archivo in sorted(carpeta.rglob("*")):
            if archivo.is_dir() or archivo.name.startswith("."):
                continue
            ruta = f"{destino}/{archivo.relative_to(carpeta).as_posix()}"
            files.append(File.generated(config, ruta, abs_src_path=str(archivo)))
    return files
