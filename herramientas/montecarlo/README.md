# Análisis cuantitativo de riesgos — Simulación Montecarlo (Excel con macro) · v3

| Archivo | Qué es |
|---|---|
| `MonteCarlo_Riesgos.xlsm` | **Entregable.** Libro con la macro incrustada y **abierta** (sin contraseña ni bloqueo), 11 hojas en español y 4 botones. |
| `MonteCarlo.bas` | Respaldo del módulo (Alt+F11 › Archivo › Importar). `ThisWorkbook` y las hojas no llevan código, por eso no hay `.cls`. |
| `Trazabilidad_Metodologia.md` | Requisitos M1–M17 de los `.md` y dónde quedó implementado cada uno. |
| `Informe_Verificacion.md` | Tabla de mapeo de `Ejemplo.xlsm`, paleta aplicada y resultados de todas las comprobaciones. |
| `build_xlsm.py`, `vba_project.py`, `datos_riesgos.py`, `contenido.py` | Regeneran el libro: `python3 build_xlsm.py` (requiere `xlsxwriter` y `openpyxl`). |
| `entrada/` | `Ejemplo.xlsm` (base de riesgos) y `plantilla_ppt.pptx` (paleta Bloomberg). |
| `pruebas/` | Pruebas automáticas: ejecución del VBA en LibreOffice, referencia numpy y verificador estático. |

## Uso

1. Abra el `.xlsm` y pulse **Habilitar contenido**. Si Windows bloquea las macros de un archivo descargado: clic derecho › Propiedades › **Desbloquear**.
2. En **PARAMETROS** reemplace el costo base (S/ 200 M) y el plazo base (730 días), que son **supuestos**.
3. Valide con cada dueño las **estimaciones preliminares** de R-01…R-32 (ESTADO = «ESTIMADO – VALIDAR»).
4. **✔ VALIDAR DATOS** → **▶ CORRER SIMULACIÓN**. **＋ AGREGAR DIMENSIÓN** crea una dimensión nueva sin tocar el código.

## Cómo se genera la macro sin Excel

`vba_project.py` escribe el `vbaProject.bin` según MS-OVBA: solo código fuente, sin p-code (`_VBA_PROJECT` versión 0xFFFF y `MODULEOFFSET = 0`). Excel compila el código al abrir el libro, en 32 o 64 bits.
Los campos de protección CMG, DPB y GC se **cifran con la clave del ID del proyecto** (suma de los bytes del ID, módulo 256). En la v1 se habían copiado de otro proyecto; por eso Excel dejó `Ejemplo.xlsm` «bloqueado para visualización». Corregido en la v3 y verificado descifrando los tres campos.

Para repetir las pruebas: `python3 build_xlsm.py --test && cd pruebas && python3 verificar_v3_dist.py && python3 verificar_v3_modelo.py`.
