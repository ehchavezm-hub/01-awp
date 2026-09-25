"""Publica en la web los archivos descargables del kit de implementación.

Los archivos .xlsx y .docx viven en implementacion/ (fuera de docs/) para que
sean fáciles de encontrar en el repositorio. Este hook los añade a la web en
implementacion/descargas/, de modo que las páginas puedan enlazarlos.

La presentación (presentacion/*.pptx) se publica en su misma ruta,
presentacion/, cuando existe en el repositorio.
"""

from pathlib import Path

from mkdocs.structure.files import File

EXTENSIONES = {".xlsx", ".docx"}
RAIZ = Path(__file__).resolve().parent.parent / "implementacion"
DESTINO = "implementacion/descargas"
PRESENTACIONES = Path(__file__).resolve().parent.parent / "presentacion"


def on_files(files, config):
    for archivo in sorted(RAIZ.rglob("*")):
        if archivo.suffix.lower() not in EXTENSIONES or archivo.name.startswith("~$"):
            continue
        # Todos los descargables quedan en una sola carpeta de la web.
        files.append(
            File.generated(config, f"{DESTINO}/{archivo.name}", abs_src_path=str(archivo))
        )
    if PRESENTACIONES.is_dir():
        for archivo in sorted(PRESENTACIONES.glob("*.pptx")):
            files.append(
                File.generated(config, f"presentacion/{archivo.name}", abs_src_path=str(archivo))
            )
    return files
