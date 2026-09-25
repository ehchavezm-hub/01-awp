# Análisis de riesgos — Simulación Montecarlo (Excel con macro)

| Archivo | Qué es |
|---|---|
| `MonteCarlo_Riesgos.xlsm` | **Entregable.** Libro con el proyecto VBA incrustado (`xl/vbaProject.bin`) y 3 botones en PARAMETROS. |
| `MonteCarlo.bas` | Respaldo del módulo (Alt+F11 › Archivo › Importar). `ThisWorkbook` no lleva código, por eso no hay `.cls`. |
| `build_xlsm.py`, `vba_project.py` | Regeneran el `.xlsm` desde el `.bas` (`python3 build_xlsm.py`). Requiere `xlsxwriter`. |
| `pruebas/` | Verificación automática (LibreOffice headless + numpy) y chequeo estático del VBA. |

## Uso
1. Abrir el `.xlsm` y **Habilitar contenido**. Si Windows bloquea las macros de un archivo descargado:
   clic derecho › Propiedades › marcar **Desbloquear**.
2. PARAMETROS: costo/plazo base (opcional), iteraciones, semilla (vacía = aleatoria) y tabla `tblRiesgos`.
3. **✔ VALIDAR DATOS** → **▶ CORRER SIMULACIÓN**. **✖ LIMPIAR RESULTADOS** vacía las hojas de salida.

El proyecto VBA se guarda **sin p-code** (solo código fuente, MS-OVBA `_VBA_PROJECT` versión 0xFFFF):
Excel lo compila al abrir, en 32 o 64 bits y en cualquier idioma.

## Verificación realizada
| Comprobación | Resultado |
|---|---|
| olevba extrae el módulo completo; descompresión idéntica byte a byte al `.bas` | ✅ |
| Código fuente 100 % ASCII (tildes vía `U("ó")` → `ChrW`) | ✅ 0 bytes > 127 |
| `Type`/`Const` antes del primer procedimiento; ningún `Array()` en arreglo tipado; sin variables sin declarar (`pruebas/lint_vba.py`, probado con errores sembrados) | ✅ |
| Nombres `CostoBase`, `PlazoBase`, `Iteraciones`, `Semilla`; tabla `tblRiesgos`; CodeNames `sh*` | ✅ |
| 3 botones con `OnAction` → `RunMonteCarlo`, `ValidarDatos`, `ClearResults` | ✅ |
| Motor VBA ejecutado en LibreOffice, semilla 12345, N = 10,000 vs numpy N = 1,000,000: P50/P80/P90 y medias de costo y plazo | ✅ todas dentro de ±1 % (criterio ±3 %) |
| 7 distribuciones (200,000 muestras) vs media y desviación teóricas | ✅ dentro de ±0.3 % |
| Misma semilla → resultados idénticos; otra semilla → distintos | ✅ |
| Casos borde: Mín = Máx, fila inactiva, filas vacías, probabilidad 0 y 1 | ✅ sin errores |
| Validación: 6 tipos de error detectados y marcados en rojo; filas inactivas ignoradas | ✅ |
| Escritura de RESULTADOS, CURVA_S (tablas), TORNADO, RANGOS, SIMULACION | ✅ (en LibreOffice) |

**No verificable en este entorno (requiere Excel):** la creación de gráficos (LibreOffice no implementa
`SeriesCollection.NewSeries`) y la lectura por `ListObjects` (LibreOffice no los implementa; el parser sí se
probó pasándole el rango de la tabla). Ese código usa solo miembros estándar del modelo de objetos de Excel.
Si algo falla al primer uso, el mensaje de error indica la etapa y el riesgo/fila.

Para repetir las pruebas: `python3 build_xlsm.py --test && cd pruebas && python3 verificar.py`.
