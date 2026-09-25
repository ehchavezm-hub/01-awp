"""Publica en la web los archivos descargables del kit de implementación.

Los archivos .xlsx y .docx viven en implementacion/ (fuera de docs/) para que
sean fáciles de encontrar en el repositorio. Este hook los añade a la web en
implementacion/descargas/, de modo que las páginas puedan enlazarlos.
"""

from pathlib import Path

from mkdocs.structure.files import File

EXTENSIONES = {".xlsx", ".docx"}
RAIZ = Path(__file__).resolve().parent.parent / "implementacion"
DESTINO = "implementacion/descargas"


def on_files(files, config):
    for archivo in sorted(RAIZ.rglob("*")):
        if archivo.suffix.lower() not in EXTENSIONES or archivo.name.startswith("~$"):
            continue
        # Todos los descargables quedan en una sola carpeta de la web.
        files.append(
            File.generated(config, f"{DESTINO}/{archivo.name}", abs_src_path=str(archivo))
        )
    return files
