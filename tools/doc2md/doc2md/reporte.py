"""Informe de verificación en Markdown."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .verificar import Resultado

_MAX_PALABRAS = 40


def _lista(contador: Counter) -> str:
    items = [f"`{p}`" + (f" ×{n}" if n > 1 else "") for p, n in contador.most_common(_MAX_PALABRAS)]
    resto = len(contador) - _MAX_PALABRAS
    if resto > 0:
        items.append(f"… y {resto} más")
    return ", ".join(items)


def _estado(r: Resultado, umbral: float) -> str:
    if r.aprobado(umbral):
        return "✅ OK"
    if r.ocr:
        return "⚠ OCR: revisar"
    if r.sin_referencia:
        return "⚠ Sin texto de referencia: revisar"
    return "❌ REVISAR"


def escribir(
    ruta: Path,
    origen: Path,
    salida_md: Path,
    resultados: list[Resultado],
    umbral: float,
    avisos: list[str],
) -> bool:
    """Escribe el informe y devuelve True si todas las unidades quedaron aprobadas."""
    aprobadas = [r for r in resultados if r.aprobado(umbral)]
    todo_ok = len(aprobadas) == len(resultados)
    total_ref = sum(r.total_referencia for r in resultados)
    total_falt = sum(sum(r.faltantes.values()) for r in resultados)
    total_sobr = sum(sum(r.sobrantes.values()) for r in resultados)
    cobertura = 1 - total_falt / total_ref if total_ref else 1.0

    lineas = [
        f"# Informe de verificación: {origen.name}",
        "",
        f"- Markdown generado: `{salida_md.name}`",
        f"- Unidades verificadas: {len(resultados)} · aprobadas: {len(aprobadas)}",
        f"- Palabras en el original: {total_ref} · faltantes: {total_falt} · sobrantes: {total_sobr}",
        f"- Cobertura global: {cobertura:.2%} (umbral por unidad: {umbral:.2%})",
        f"- Resultado: {'✅ FIEL al original según la verificación' if todo_ok else '❌ REQUIERE REVISIÓN MANUAL en las unidades marcadas'}",
        "",
        "> La verificación compara las palabras del Markdown con el texto extraído del original",
        "> por un camino independiente de la conversión. **Sobrantes** = palabras que no están en",
        "> el original (nunca deberían existir). **Faltantes** = palabras del original ausentes en",
        "> el Markdown. No detecta errores de formato (negritas, niveles de título, celdas de",
        "> tabla desplazadas): para eso, revisa visualmente las unidades con baja similitud de orden.",
        "",
    ]
    if avisos:
        lineas += ["## Avisos", ""] + [f"- {a}" for a in avisos] + [""]

    lineas += [
        "## Resumen",
        "",
        "| Unidad | Estado | Palabras | Cobertura | Faltantes | Sobrantes | Similitud de orden |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in resultados:
        lineas.append(
            f"| {r.etiqueta} | {_estado(r, umbral)} | {r.total_referencia} | {r.cobertura:.2%} "
            f"| {sum(r.faltantes.values())} | {sum(r.sobrantes.values())} | {r.similitud_orden:.2%} |"
        )
    lineas.append("")

    detalles = [r for r in resultados if not r.aprobado(umbral) or r.excluidas or r.notas]
    if detalles:
        lineas += ["## Detalle", ""]
    for r in detalles:
        lineas += [f"### {r.etiqueta} — {_estado(r, umbral)}", ""]
        lineas += [f"- {n}" for n in r.notas]
        if r.faltantes:
            lineas.append(f"- **Faltantes:** {_lista(r.faltantes)}")
        if r.sobrantes:
            lineas.append(f"- **Sobrantes:** {_lista(r.sobrantes)}")
        if r.excluidas:
            lineas.append(f"- Omitido como encabezado/pie de página: {_lista(r.excluidas)}")
        if r.unidas_por_guion:
            lineas.append(f"- Palabras unidas por guion de fin de línea: {len(r.unidas_por_guion)}")
        lineas.append("")

    ruta.write_text("\n".join(lineas), encoding="utf-8")
    return todo_ok
