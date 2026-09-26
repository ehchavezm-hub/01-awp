"""Interfaz de línea de comandos de doc2md."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .conversion import Opciones, convertir


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="doc2md",
        description=(
            "Convierte PDF y EPUB a Markdown con Docling y verifica, palabra por palabra, "
            "que el resultado sea fiel al original."
        ),
    )
    p.add_argument("archivos", nargs="+", type=Path, help="Archivos .pdf o .epub")
    p.add_argument("-o", "--salida", type=Path, default=Path("md"), help="Carpeta de salida (por defecto: md/)")
    p.add_argument(
        "--umbral", type=float, default=0.995,
        help="Cobertura mínima por página o capítulo para aprobarla (0-1, por defecto 0.995)",
    )
    p.add_argument(
        "--ocr", choices=["auto", "siempre", "nunca"], default="auto",
        help="auto: OCR solo si hay páginas escaneadas (por defecto); siempre: OCR de página completa; nunca",
    )
    p.add_argument("--idiomas", default="spa,eng", help="Idiomas de Tesseract para OCR (por defecto: spa,eng)")
    p.add_argument(
        "--conservar-encabezados", action="store_true",
        help="Mantener encabezados y pies de página en el Markdown (por defecto se omiten y se listan en el informe)",
    )
    p.add_argument("--modelos", type=Path, help="Carpeta con los modelos de Docling descargados (uso sin internet)")
    p.add_argument("-v", "--detallado", action="store_true", help="Mostrar el registro de Docling")
    return p.parse_args(argv)


def convertir_archivo(origen: Path, args: argparse.Namespace) -> bool:
    opciones = Opciones(
        umbral=args.umbral,
        ocr=args.ocr,
        idiomas=[i.strip() for i in args.idiomas.split(",") if i.strip()],
        conservar_encabezados=args.conservar_encabezados,
        modelos=args.modelos,
    )
    r = convertir(origen, args.salida, opciones)
    revisar = [u.etiqueta for u in r.por_revisar]
    print(f"{'OK     ' if r.ok else 'REVISAR'}  {origen.name} -> {r.markdown}")
    if revisar:
        print(f"         {len(revisar)} de {len(r.resultados)} por revisar: {', '.join(revisar[:10])}"
              + (" …" if len(revisar) > 10 else ""))
    print(f"         informe: {r.informe}")
    return r.ok


def main(argv: list[str] | None = None) -> int:
    args = _argumentos(argv)
    logging.basicConfig(level=logging.INFO if args.detallado else logging.ERROR)
    if not 0 <= args.umbral <= 1:
        print("--umbral debe estar entre 0 y 1", file=sys.stderr)
        return 2

    todos_ok = True
    for origen in args.archivos:
        if not origen.is_file():
            print(f"ERROR    no existe: {origen}", file=sys.stderr)
            todos_ok = False
            continue
        try:
            todos_ok &= convertir_archivo(origen, args)
        except Exception as e:  # un archivo que falla no detiene a los demás
            print(f"ERROR    {origen.name}: {e}", file=sys.stderr)
            todos_ok = False
    # 0 = todo verificado; 1 = hay algo que revisar o que falló.
    return 0 if todos_ok else 1
