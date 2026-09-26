# Informe de verificación — MonteCarlo_Riesgos.xlsm v3

Libro generado con `python3 build_xlsm.py` según `prompts/prompt_montecarlo_xlsm_v3.md`. El VBA se probó ejecutándolo en LibreOffice headless (`pruebas/run_lo.py`) y se contrastó con una referencia independiente en numpy (`pruebas/referencia_numpy.py`).

## 1. Mapeo de `Ejemplo.xlsm` → `tblRiesgos`

Origen: `entrada/Ejemplo.xlsm`, tabla `tblRiesgos` (B11:N61). Se leyeron **37 filas = 37 cargadas**: 32 riesgos del proyecto (filas 17–48) y 5 ejemplos de la v1 (filas 12–16).

| Columna de origen | Columna destino | Regla |
|---|---|---|
| ID (vacío en R-01…R-32; 1–5 en ejemplos) | ID | R-01…R-32 según el orden de las filas 17–48; EJ-1…EJ-5 para las filas 12–16 |
| NOMBRE DEL RIESGO | NOMBRE DEL RIESGO | Espacios recortados y espacios dobles unidos; el texto no cambia |
| NOMBRE DEL RIESGO (tras « - Debido a») | CAUSA | Texto posterior a «Debido a/al» (**15 filas**) |
| ACTIVO (SI/NO) | ACTIVO | R-01…R-32 = SI (estimados); EJ = NO (decisión D1) |
| PROBABILIDAD (0-1) | PROBABILIDAD | EJ: igual al origen; R: ANEXO A (en el origen está vacía) |
| DIST_COSTO, C_P1…C_P3 | DIST_COSTO, COSTO_P1…COSTO_P3 | EJ: igual al origen; R: ANEXO A |
| DIST_PLAZO, T_P1…T_P3 | DIST_PLAZO, PLAZO_P1…PLAZO_P3 | EJ: igual al origen; R: ANEXO A |
| — | DIST_ING_DISENO…, DIST_ING_CAMPO… | Dimensiones nuevas; R: ANEXO A |
| NOTAS | NOTAS | EJ: «EJEMPLO – desactivar…»; R: nota de estimación preliminar |
| — | TIPO, CATEGORIA, ESTADO, GRUPO_CORRELACION, RHO_GRUPO | ANEXO A (TIPO = AMENAZA; ESTADO = «ESTIMADO – VALIDAR» o «EJEMPLO») |

**Decisión D2 pendiente:** R-17…R-20 se cargaron como AMENAZA. Si alguno es una oportunidad, basta con cambiar TIPO a OPORTUNIDAD; el modelo le aplica signo negativo.

## 2. Paleta aplicada (plantilla_ppt.pptx, Bloomberg)

| Rol | Fondo | Texto | Contraste |
|---|---|---|---|
| Banda de título y encabezado de tabla | #000000 | #FFA028 | 10.3:1 |
| Subtítulo y notas | #FFFFFF | #333333 | 12.6:1 |
| Fila alterna (tinte derivado*) | #FFF7EB | #000000 | 19.8:1 |
| Celda de entrada (tinte derivado*) | #FFF0D6 | #000000 | 18.7:1 |
| Celda de salida (tinte derivado*) | #EDEDED | #000000 | 17.9:1 |
| P10 / P50 / P80 (nivel) / P90 | #4AF6C3 / #FFB020 / #FFA028 / #FB8B1E | #000000 | ≥ 8.8:1 |
| Error de validación | #FF433D | #000000 | 6.1:1 |
| Advertencia de validación | #FFB020 | #000000 | 11.5:1 |
| Oportunidad | #00C805 | #000000 | 9.3:1 |
| Estimado – validar | #FFF0D6, borde #CC7A00 | #000000 | 18.7:1 |
| Botones | #000000 | #FFA028 | 10.3:1 |
| Series: COSTO / PLAZO / ING_DISENO / ING_CAMPO | #FF6600 / #0068FF / #CC7A00 / #2A2A2A | — | — |

(*) La paleta no trae neutros claros, así que estos fondos son tintes claros de sus colores.

Verificación: se revisaron todos los estilos del libro y del código VBA. Solo hay colores de esta tabla, no queda ninguno de la v1 y no se usa ninguna combinación prohibida. También se revisó el render a PDF de INICIO, GUIA y PARAMETROS.

## 3. Lista de comprobación

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Macro abierta: CMG, DPB y GC descifrados con la clave del ID del proyecto (217) | CMG = 00000000, DPB = 00, GC = FF → **sin contraseña ni bloqueo** |
| 2 | Sin hojas protegidas ni ocultas | OK |
| 3 | Código de `vbaProject.bin` (olevba) idéntico a `MonteCarlo.bas`; ASCII puro (0 bytes > 127) | OK |
| 4 | Verificador estático `lint_vba.py` (orden de declaraciones, Array, identificadores no declarados, locales que ocultan procedimientos, texto \u fuera de U()) | Sin hallazgos |
| 5 | Generador MRG32k3a: VBA frente a Python | Coincide a 1e-15 |
| 6 | 20 distribuciones (N = 60 000): media y desviación frente a las teóricas | Error ≤ 0.7 % en la media y ≤ 0.6 % en la desviación; TRIGEN: P(X<5) = P(X>30) = 0.1000 |
| 7 | Modelo frente a numpy: casos EJEMPLOS, REAL independiente y REAL correlacionado | Diferencia ≤ 1.03 %. REAL: costo P50 15.74 M, P80 21.34 M, P90 24.66 M; plazo P80 121.7 d; ING_DISENO P80 4 260 HH; ING_CAMPO P80 1 995 HH |
| 8 | VME frente a la media simulada | Diferencia ≤ 0.5 % |
| 9 | Reproducibilidad | Misma semilla → mismo resultado; otra semilla → resultado distinto |
| 10 | Correlación: prueba en memoria | 0.606 frente a 0.6 objetivo |
| 10b | Correlación: grupos reales | Lograda < objetivo por los empates en 0 con p < 1: CONTRACTUAL 0.41/0.5, SOBRECONSUMO 0.34/0.4, APROBACIONES 0.45/0.5, CALIDAD 0.30/0.4, INGENIERIA 0.44/0.5, EXTENSION_PLAZO 0.50/0.6. RESULTADOS lo informa |
| 11 | Oportunidades | Signo negativo: DIF 79.80 frente a 80 |
| 12 | Escenario «después» con impacto constante | P80 = mín = máx = 3 000 |
| 13 | Casos borde (N mínimo, sin riesgos activos, p = 0 y 1, parámetros límite) | OK |
| 14 | 5.ª dimensión (CALIDAD) procesada sin cambiar el código | OK (ND = 5) |
| 15 | ValidarDatos | Detecta 7 errores reales con marca roja; ignora la fila inactiva; muestra las advertencias en ámbar |
| 16 | Hojas de salida (RESULTADOS, CURVA_S, TORNADO, RANGOS, MATRIZ_PI, COMPARACION, SIMULACION) | Escritas y coherentes. Reserva para contingencias S/ 21.34 M (11 % de la base); precisión «Suficiente»; en COMPARACION la respuesta de prueba (S/ 450 000) baja el P80 en 1.87 M |

## 4. Pendiente de probar en Excel real

LibreOffice no puede probar estos puntos, que dependen de Excel:

- Creación de gráficos (curva S, histograma, tornado). Los de la v1, hechos con el mismo método, funcionaron en Excel.
- Lectura de las tablas como ListObjects. En LibreOffice se probó con rangos equivalentes y la ruta de lectura es la misma.
- `AgregarDimension`: agrega columnas a tblRiesgos, tblDimensiones y tblEscalas.
- Los 4 botones (formas con macro asignada).

Si alguno falla, anote el mensaje de error y la línea resaltada en el editor VBA.

## 5. Supuestos a validar

- Costo base S/ 200 M y plazo base de 730 días: son **supuestos**, reemplácelos en PARAMETROS.
- Las estimaciones de R-01…R-32 son **preliminares** (ESTADO = «ESTIMADO – VALIDAR»), no son datos del proyecto.
