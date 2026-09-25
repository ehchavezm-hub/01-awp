"""Genera app/web/lib/iconos.js con los íconos Lucide que usa la aplicación.

Uso (con el paquete lucide-static descargado con `npm pack lucide-static`):
    python app/herramientas/generar_iconos.py <carpeta>/package/icons

Para agregar un ícono, súmalo a ICONOS y vuelve a ejecutar el script.
Licencia de los íconos: ISC (app/web/vendor/LICENCIA-lucide.txt).
"""

import re
import sys
from pathlib import Path

ICONOS = """
layout-grid building-2 layers list-checks flag map package pencil-ruler truck hard-hat route
octagon-alert badge-check calendar-range users shield-alert lightbulb gauge file-text library
circle-help sparkles plus search sun moon download file-spreadsheet presentation chevron-right
chevron-left chevron-down check circle-alert clock filter image arrow-right award graduation-cap
x menu save info triangle-alert log-out file pencil trash-2 archive archive-restore eye eye-off
lock mail key-round user settings history rocket party-popper circle-check-big circle-dashed
circle-dot circle arrow-left external-link book-open list calendar map-pin briefcase target
refresh-cw ellipsis-vertical house printer
""".split()

carpeta = Path(sys.argv[1])
simbolos = []
for nombre in ICONOS:
    svg = (carpeta / f"{nombre}.svg").read_text(encoding="utf-8")
    cuerpo = re.sub(r"\s+", " ", re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)).strip()
    simbolos.append(f'<symbol id="i-{nombre}" viewBox="0 0 24 24">{cuerpo}</symbol>')
salida = Path(__file__).resolve().parents[1] / "web" / "lib" / "iconos.js"
salida.write_text(
    "// Generado por app/herramientas/generar_iconos.py. Íconos Lucide (licencia ISC).\n"
    "export const SPRITE = `<svg xmlns=\"http://www.w3.org/2000/svg\" style=\"display:none\">"
    + "".join(simbolos) + "</svg>`;\n",
    encoding="utf-8",
)
print(f"{len(simbolos)} íconos en {salida}")
