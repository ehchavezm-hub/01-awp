# Prompt: Herramienta de Riesgos Montecarlo en Excel (.xlsm con macro incluida)

> Copia todo lo que está dentro del bloque de abajo y pégalo en la herramienta de IA.
> Está escrito para evitar los errores del archivo anterior (`montecarlo_mc2.xlsm`), que se listan al final.

---

```text
ROL
Eres un desarrollador senior de Excel/VBA y analista de riesgos de proyectos de construcción.
Tu entregable es UN archivo Excel habilitado para macros (.xlsm) que contenga el proyecto VBA
DENTRO del archivo (xl/vbaProject.bin), listo para abrir en Excel 2016/365 (Windows, configuración
regional Perú / español), habilitar macros y presionar un botón. No me entregues solo el código:
el código debe estar incrustado en el .xlsm. Además, entrega como respaldo el módulo exportado
MonteCarlo.bas (y el .cls de ThisWorkbook si lo usas).

OBJETIVO
Herramienta de análisis cuantitativo de riesgos por simulación Montecarlo para obras de
construcción: impacto en COSTO (S/) y en PLAZO (días), con percentiles P0–P100, contingencias
P50/P80/P90, curva S, diagrama tornado y tabla de rangos por riesgo.

======================================================================
1. ESTRUCTURA DEL LIBRO (nombres de hoja EXACTOS, en MAYÚSCULAS)
======================================================================
Hojas en este orden: INICIO, PARAMETROS, RESULTADOS, CURVA_S, TORNADO, RANGOS, SIMULACION.
- Los nombres de hoja NO llevan tildes, eñes, espacios ni emojis (el código VBA los referencia).
- El texto visible dentro de las celdas SÍ puede llevar tildes (se escribe desde Python/openpyxl,
  no desde VBA).
- En VBA referencia las hojas por su CodeName (shInicio, shParam, shRes, shCurva, shTornado,
  shRangos, shSim) y NO por el nombre de pestaña, para que el código siga funcionando aunque el
  usuario renombre una pestaña. Asigna esos CodeName al crear el vbaProject.

INICIO
- Título, descripción de cada hoja, pasos de uso (1–6) y tabla de distribuciones disponibles con
  sus parámetros (igual que la guía de la hoja PARAMETROS).

PARAMETROS
- Celda D5: "Costo base del proyecto (S/)" (opcional, numérico).
- Celda D6: "Plazo base del proyecto (días)" (opcional, numérico).
- Celda D7: "Número de iteraciones" = 10000 (validación: entero entre 1000 y 100000).
- Celda D8: "Semilla aleatoria" (vacío = aleatoria; número = resultados reproducibles).
- Defínelos además como NOMBRES DEFINIDOS: CostoBase, PlazoBase, Iteraciones, Semilla. El VBA
  debe leer SIEMPRE por nombre definido (Range("Iteraciones")), nunca por dirección fija.
- Tabla de riesgos como TABLA DE EXCEL (ListObject) llamada tblRiesgos, encabezado en la fila 11,
  datos desde la fila 12, con estas columnas:
    ID | NOMBRE DEL RIESGO | ACTIVO (SI/NO) | PROBABILIDAD (0–1) |
    DIST_COSTO | C_P1 | C_P2 | C_P3 |
    DIST_PLAZO | T_P1 | T_P2 | T_P3 |
    NOTAS
  * Cada riesgo puede impactar costo, plazo o ambos: si DIST_COSTO está vacío no afecta costo;
    si DIST_PLAZO está vacío no afecta plazo. (Esto reemplaza el antiguo "TIPO = AMBOS", que
    multiplicaba mal el costo por un parámetro.)
  * PROBABILIDAD = probabilidad de ocurrencia del riesgo (evento discreto). Si es 1, el riesgo
    siempre ocurre (incertidumbre). Si ocurre, costo y plazo se muestrean en la MISMA iteración
    (el mismo evento dispara ambos impactos).
  * Validación de datos (listas) en DIST_COSTO y DIST_PLAZO:
    TRIANGULAR, PERT, NORMAL, UNIFORME, LOGNORMAL, EXPONENCIAL, WEIBULL.
  * ACTIVO: lista SI/NO. Celdas de entrada en amarillo claro; fórmulas/salidas en gris.
- Ejemplos precargados (5 riesgos):
    1 Ingeniería en desarrollo (90 entregables) | SI | 1.0 | — | | | | TRIANGULAR | 7 | 14 | 28
    2 Alza de precios de materiales            | SI | 1.0 | NORMAL | 50000 | 25000 | | — | | |
    3 Condiciones geotécnicas imprevistas      | SI | 0.35 | PERT | 30000 | 80000 | 200000 | PERT | 10 | 25 | 60
    4 Huelga o paralización                    | SI | 0.20 | — | | | | TRIANGULAR | 5 | 15 | 45
    5 Demora en permisos y aprobaciones        | SI | 1.0 | — | | | | UNIFORME | 10 | 40 |
- Guía de parámetros por distribución (debajo de la tabla o a la derecha):
    TRIANGULAR  P1=Mín, P2=Moda, P3=Máx
    PERT        P1=Mín, P2=Moda, P3=Máx (Beta-PERT, lambda=4)
    NORMAL      P1=Media, P2=Desv.Est.
    UNIFORME    P1=Mín, P2=Máx
    LOGNORMAL   P1=Media, P2=Desv.Est. (de la variable, no del logaritmo)
    EXPONENCIAL P1=Media (NO lambda; lambda = 1/P1)
    WEIBULL     P1=Forma (k), P2=Escala (lambda)
- Tres BOTONES (Form Controls, no ActiveX) asignados a macros:
    "▶ CORRER SIMULACIÓN"  -> RunMonteCarlo
    "✔ VALIDAR DATOS"      -> ValidarParametros
    "✖ LIMPIAR RESULTADOS" -> ClearResults
  Los botones DEBEN existir físicamente en la hoja (drawing + vmlDrawing / ctrlProps) y estar
  vinculados a la macro. Si tu herramienta no puede crear botones, crea en ThisWorkbook un
  Workbook_Open que los genere si no existen (Shapes.AddFormControl / Buttons.Add con .OnAction).

Hojas de salida (RESULTADOS, CURVA_S, TORNADO, RANGOS, SIMULACION): NO se borran ni se recrean;
la macro solo limpia su contenido (Cells.Clear y borra ChartObjects) y vuelve a escribir.

======================================================================
2. REGLAS OBLIGATORIAS DEL CÓDIGO VBA (causas de fallo del archivo anterior)
======================================================================
R1. CÓDIGO FUENTE 100% ASCII. Ni tildes, ni ñ, ni "—", ni "✅", ni caracteres de caja (═ ─) en
    el código, comentarios incluidos. El proyecto VBA usa codepage 1252; si lo escribes en UTF-8
    aparece texto corrupto ("PARÃ�METROS") y las hojas no se encuentran (error 9).
    Para mostrar texto con tildes desde VBA usa ChrW(): p.ej. "Simulaci" & ChrW(243) & "n",
    o una función auxiliar U("Simulación") que convierta secuencias \uXXXX con ChrW.
R2. Option Explicit en todos los módulos. TODAS las variables declaradas (el anterior usaba
    "cht" sin declarar -> error de compilación).
R3. Las declaraciones Type, Const y Private/Public a nivel de módulo van ARRIBA, antes del primer
    Sub/Function (el anterior declaraba "Type RiskData" a mitad del módulo -> error de compilación).
R4. Array() devuelve Variant: cualquier variable que reciba Array(...) debe declararse As Variant
    (el anterior hacía "Dim pcts() As Integer: pcts = Array(...)" -> error "no coinciden los tipos").
R5. Usa Long (no Integer) para filas, contadores e índices.
R6. Manejo de errores: On Error GoTo ErrHandler en RunMonteCarlo; en ErrHandler y en la salida
    normal SIEMPRE restaurar ScreenUpdating, Calculation, EnableEvents y StatusBar, y mostrar
    MsgBox con Err.Number, Err.Description y el riesgo/fila que causó el problema.
R7. Rendimiento: guardar las muestras en arrays en memoria y volcar a hoja con UNA asignación
    Range.Value = array (nada de escribir celda por celda en bucles de miles de filas).
    10,000 iteraciones x 20 riesgos debe tardar menos de ~10 s.
R8. Nada de dependencias externas: sin referencias a librerías adicionales, sin ActiveX,
    sin Analysis ToolPak. Debe compilar con Depurar > Compilar VBAProject sin errores.
R9. Compatibilidad 32 y 64 bits (no uses Declare; si fuera imprescindible, PtrSafe).

======================================================================
3. LÓGICA DE LA SIMULACIÓN
======================================================================
Módulo estándar "MonteCarlo" con, como mínimo:

- ValidarParametros() As Boolean
  Revisa cada fila ACTIVA de tblRiesgos y marca en rojo la celda con error + lista de errores en
  MsgBox. Reglas: nombre no vacío; 0 <= PROBABILIDAD <= 1; al menos una distribución (costo o
  plazo); parámetros numéricos; TRIANGULAR/PERT: Mín <= Moda <= Máx y Mín < Máx; UNIFORME:
  Mín < Máx; NORMAL/LOGNORMAL: Desv.Est. > 0; LOGNORMAL: Media > 0; EXPONENCIAL: Media > 0;
  WEIBULL: Forma > 0 y Escala > 0. Iteraciones entre 1000 y 100000.
  RunMonteCarlo llama a ValidarParametros primero y se detiene si hay errores.

- RunMonteCarlo()
  1. Validar. 2. Leer riesgos activos desde tblRiesgos (ListObject.DataBodyRange a un array).
  3. Semilla: si Semilla tiene valor -> Rnd(-1): Randomize Semilla; si no -> Randomize.
  4. Para i = 1..N y para cada riesgo j:
       ocurre = (Rnd() < Prob_j)
       si ocurre: c_ij = Muestra(DIST_COSTO_j) ; t_ij = Muestra(DIST_PLAZO_j)  (0 si no hay dist.)
       si no ocurre: c_ij = 0 ; t_ij = 0
     Guardar la matriz completa c(i,j) y t(i,j) (se necesita para rangos y tornado).
     TotalCosto(i) = suma_j c(i,j) ; TotalPlazo(i) = suma_j t(i,j).
     NO truncar a 0 los valores negativos de NORMAL (una oportunidad puede ser negativa);
     sí documentarlo en la hoja INICIO.
  5. StatusBar con % de avance cada 5% y DoEvents.
  6. Ordenar (QuickSort iterativo o recursivo sobre copia) y calcular percentiles con
     interpolación lineal (mismo criterio que PERCENTIL.INC de Excel).
  7. Escribir todas las hojas de salida y crear gráficos. 8. MsgBox final con iteraciones,
     riesgos, tiempo, P50 y P80 de costo y plazo. Activar hoja RESULTADOS.

- Generadores (todos con Rnd(), sin WorksheetFunction dentro del bucle):
    TRIANGULAR: inversa de la CDF; si Máx = Mín devolver Mín (evitar división por cero).
    PERT: Beta-PERT con alpha = 1 + 4*(Moda-Mín)/(Máx-Mín), beta = 1 + 4*(Máx-Moda)/(Máx-Mín);
          Beta muestreada como X/(X+Y) con X~Gamma(alpha), Y~Gamma(beta) usando el método de
          Marsaglia–Tsang. (NO usar el método de Jöhnk con 200 intentos y fallback a la media:
          el archivo anterior sesgaba los resultados por eso.)
    NORMAL: Box–Muller (u1 > 0).
    UNIFORME: Mín + Rnd*(Máx-Mín).
    LOGNORMAL: sigma_ln = Sqr(Log(1 + (sd/m)^2)); mu_ln = Log(m) - sigma_ln^2/2; Exp(Normal).
    EXPONENCIAL: -Media * Log(1 - u), u en [0,1).
    WEIBULL: Escala * (-Log(1 - u))^(1/Forma).

======================================================================
4. HOJAS DE SALIDA (lo que debe escribir la macro)
======================================================================
RESULTADOS
- Encabezado con fecha/hora de la corrida, N iteraciones, semilla usada, N riesgos.
- Tabla P0, P5, P10, P20, ..., P90, P95, P100 para: Impacto Costo, Impacto Plazo y, si hay
  CostoBase/PlazoBase, Costo Total (base + impacto) y Plazo Total. Resaltar P10, P50, P80, P90.
- Estadísticas: media, desviación estándar, coeficiente de variación, mínimo, máximo,
  probabilidad de impacto = 0.
- Contingencias recomendadas: P50, P80 y P90 para costo (S/) y plazo (días) en COLUMNAS
  separadas y bien etiquetadas; si hay base, además "Contingencia = Pxx − Media" y % sobre base.

CURVA_S
- Tabla de probabilidad acumulada de 0% a 100% cada 5% con valor de costo y de plazo.
- Dos gráficos XY Dispersión con líneas suavizadas (xlXYScatterSmoothNoMarkers), NO gráfico de
  líneas: eje X = valor (S/ o días), eje Y = probabilidad acumulada 0–100%.
  Líneas de referencia o etiquetas en P50 y P80. Además un histograma de frecuencias (20 clases)
  para costo y otro para plazo, con su tabla de clases.

TORNADO
- Por riesgo: impacto medio en costo y en plazo, y sensibilidad = coeficiente de correlación de
  rango (Spearman) o, en su defecto, de Pearson entre c(:,j) y TotalCosto (y t(:,j) vs
  TotalPlazo). Incluir también "swing" = P90 − P10 del total condicionado.
- Tabla ORDENADA de mayor a menor contribución (dos tablas: costo y plazo).
- Dos gráficos de barras horizontales (xlBarClustered) ordenados con el mayor arriba
  (ReversePlotOrder en el eje de categorías), uno para costo y otro para plazo, sin incluir
  riesgos con contribución 0.

RANGOS
- Una fila POR CADA RIESGO (no solo totales) y por dimensión (Costo / Plazo):
  RIESGO | DIMENSIÓN | UNIDAD | PROB. OCURRENCIA | MÍNIMO | P10 | P25 | P50 | P75 | P90 | MÁXIMO | PROMEDIO
  Calculado sobre las N muestras de ese riesgo. PROMEDIO debe ser la media real (el anterior
  ponía P50 en la columna PROMEDIO).
- Al final, filas TOTAL COSTO y TOTAL PLAZO.

SIMULACION
- Primeras min(N, 5000) iteraciones: ITER | TOTAL COSTO | TOTAL PLAZO | columnas por riesgo
  (C_Riesgo1, T_Riesgo1, ...). Volcado en un solo bloque de array.

Formato general: fuente Calibri 10–11, encabezados con fondo verde oscuro RGB(15,110,86) y texto
blanco, filas alternas, bordes finos gris, formato "#,##0" para S/ y "#,##0.0" para días,
paneles inmovilizados bajo encabezados, ancho de columnas ajustado. Proteger nada (sin
contraseñas).

======================================================================
5. ENTREGA Y AUTOVERIFICACIÓN (obligatorio antes de entregarme el archivo)
======================================================================
Entrega:
  a) MonteCarlo_Riesgos.xlsm (con vbaProject.bin incrustado y botones funcionando).
  b) MonteCarlo.bas y ThisWorkbook.cls exportados (respaldo para importar con Alt+F11 >
     Archivo > Importar si el .xlsm se abriera sin macros).
  c) Una breve lista de verificación de lo que comprobaste.

Si generas el archivo con Python (openpyxl / XlsxWriter) recuerda que esas librerías NO pueden
crear un vbaProject.bin desde texto. Usa un método real para compilar el proyecto VBA dentro del
archivo (por ejemplo, Excel vía COM/xlwings: wb.VBProject.VBComponents.Import("MonteCarlo.bas")
y guardar como .xlsm con FileFormat=52; o una plantilla .xlsm con vbaProject.bin válido), y
asigna los CodeName de hojas coherentes con el código.

Comprobaciones mínimas (reporta el resultado de cada una):
  [ ] olevba (oletools) extrae el módulo MonteCarlo completo y sin texto corrupto.
  [ ] El código fuente del VBA no contiene ningún carácter fuera de ASCII (bytes > 127).
  [ ] Todas las declaraciones Type/Const están antes del primer procedimiento.
  [ ] Ninguna variable sin declarar (Option Explicit) y ningún Array() asignado a un array tipado.
  [ ] Los nombres CostoBase, PlazoBase, Iteraciones, Semilla y la tabla tblRiesgos existen.
  [ ] Los tres botones existen en PARAMETROS y su OnAction apunta a macros existentes.
  [ ] Con los 5 riesgos de ejemplo, semilla = 12345 y N = 10000, reporta P50 y P80 de costo y
      plazo, y compáralos contra una simulación equivalente en Python (numpy) con la misma
      lógica: deben coincidir dentro de ±3%.
  [ ] Casos borde: un riesgo con Mín = Máx, un riesgo inactivo, una fila vacía en la tabla,
      probabilidad 0 y probabilidad 1; ninguno debe provocar error.
Si alguna comprobación falla, corrígela antes de entregar; no me entregues un archivo que no
hayas verificado.
```

---

## Errores detectados en `montecarlo_mc2.xlsm` (por qué no funcionaba)

| # | Problema en el archivo anterior | Efecto | Regla del prompt que lo evita |
|---|---|---|---|
| 1 | El código VBA se grabó en UTF‑8 con tildes/emojis → `"PARÃ�METROS"`, `"SIMULACIÃ“N"` | `Sheets(HOJA_PARAM)` no encuentra la hoja → error 9 al iniciar | R1 (código ASCII) + nombres de hoja sin tildes + CodeName |
| 2 | `Type RiskData` declarado a mitad del módulo, después de `Sub RunMonteCarlo` | Error de compilación: el módulo no corre | R3 |
| 3 | `Dim pcts() As Integer: pcts = Array(...)` (también `labels`, `stats_c`, etc.) | Error "No coinciden los tipos" | R4 |
| 4 | `cht` sin declarar en `CreateTornadoChart` con `Option Explicit` | Error de compilación | R2 |
| 5 | Lee iteraciones de `C4`, pero el valor está en `D6` | Siempre usa 1000 iteraciones | Nombres definidos |
| 6 | `FILA_INICIO = 8` es la fila de encabezados | El encabezado se lee como un riesgo | `tblRiesgos` (ListObject) |
| 7 | No hay botón en la hoja PARÁMETROS (no existe drawing) | No hay forma de lanzar la macro desde la hoja | Botones Form Control obligatorios |
| 8 | Tipo `AMBOS`: costo = valor × P3 | Impacto en costo sin sentido | Distribución separada para costo y plazo |
| 9 | PERT con método de Jöhnk + fallback a la media tras 200 intentos | Resultados sesgados hacia la media | Marsaglia–Tsang |
| 10 | Curva S como gráfico de línea con ejes invertidos | La curva S no se lee correctamente | XY dispersión, X = valor, Y = probabilidad |
| 11 | Tornado sin ordenar y solo con medias | No es un tornado real | Correlación/swing, ordenado |
| 12 | RANGOS solo muestra totales y la columna PROMEDIO usa P50 | Falta el rango por riesgo; promedio incorrecto | Fila por riesgo y media real |
| 13 | Escritura celda por celda con formato en bucles | Lento | R7 (volcado por arrays) |
| 14 | Triangular con Mín = Máx divide entre cero | Error en tiempo de ejecución | Validación + caso borde |
