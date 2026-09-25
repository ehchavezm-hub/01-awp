"""Genera presentacion/implementacion_awp.pptx (122 láminas) sobre plantilla_ppt.pptx.

Uso:  python presentacion/generar_presentacion.py
Requiere: python-pptx y Pillow (y las fuentes Liberation para la verificación de ajuste de texto).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from awp import contenido_a  # noqa: E402
from awp.diseno import AVISOS, Mazo  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "implementacion_awp.pptx"


def main():
    d = Mazo()
    modulos = [contenido_a.m0, contenido_a.m1, contenido_a.m2, contenido_a.m3, contenido_a.m4]
    try:
        from awp import contenido_b, contenido_c
        modulos += [contenido_b.m5, contenido_b.m6, contenido_b.m7, contenido_b.m8,
                    contenido_c.m9, contenido_c.m10, contenido_c.m11, contenido_c.m12, contenido_c.m13]
    except ImportError:
        pass
    for m in modulos:
        m(d)
    d.guardar(SALIDA, "Implementar AWP: guía práctica fase por fase")
    print(f"Guardado: {SALIDA} ({d.n} láminas)")
    for a in AVISOS:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
