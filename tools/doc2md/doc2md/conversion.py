"""Conversión de un archivo con su informe; la usan la línea de comandos y la aplicación."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import reporte
from .verificar import Resultado

FORMATOS = (".pdf", ".epub")


@dataclass
class Opciones:
    umbral: float = 0.995
    ocr: str = "auto"
    idiomas: list[str] = field(default_factory=lambda: ["spa", "eng"])
    conservar_encabezados: bool = False
    modelos: Path | None = None


@dataclass
class Resumen:
    origen: Path
    markdown: Path
    imagenes: Path
    informe: Path
    resultados: list[Resultado]
    avisos: list[str]
    umbral: float

    @property
    def ok(self) -> bool:
        return not self.por_revisar

    @property
    def por_revisar(self) -> list[Resultado]:
        return [r for r in self.resultados if not r.aprobado(self.umbral)]

    @property
    def cobertura(self) -> float:
        total = sum(r.total_referencia for r in self.resultados)
        faltan = sum(sum(r.faltantes.values()) for r in self.resultados)
        return 1 - faltan / total if total else 1.0


def convertir(origen: Path, salida: Path, opciones: Opciones) -> Resumen:
    """Convierte `origen` y deja en `salida` el .md, sus imágenes y el informe."""
    nombre = origen.stem
    salida.mkdir(parents=True, exist_ok=True)
    salida_md = salida / f"{nombre}.md"
    dir_imagenes = salida / f"{nombre}_imagenes"
    ruta_informe = salida / f"{nombre}.reporte.md"

    tipo = origen.suffix.lower()
    if tipo == ".pdf":
        from . import pdf

        md, resultados, avisos = pdf.convertir(
            origen, salida_md, dir_imagenes,
            ocr=opciones.ocr,
            idiomas=opciones.idiomas,
            conservar_encabezados=opciones.conservar_encabezados,
            modelos=opciones.modelos,
        )
    elif tipo == ".epub":
        from . import epub

        md, resultados, avisos = epub.convertir(origen, salida_md, dir_imagenes)
    else:
        raise ValueError(f"Formato no soportado: {origen.suffix} (solo .pdf y .epub)")

    salida_md.write_text(md, encoding="utf-8")
    if dir_imagenes.exists() and not any(dir_imagenes.iterdir()):
        dir_imagenes.rmdir()
    reporte.escribir(ruta_informe, origen, salida_md, resultados, opciones.umbral, avisos)
    return Resumen(origen, salida_md, dir_imagenes, ruta_informe, resultados, avisos, opciones.umbral)
