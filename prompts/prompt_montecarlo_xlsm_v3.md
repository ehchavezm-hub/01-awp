# Prompt v3: Herramienta de Riesgos Montecarlo en Excel (.xlsm con macro incluida)

> Versión 3 (26/09/2026). Parte de la v2 y aplica las 6 notas prioritarias del usuario:
> (1) usar `Ejemplo.xlsm` como guía, (2) cuantificar los 32 riesgos para poder ejecutar la macro,
> (3) dejar el análisis abierto a más dimensiones (ingeniería de diseño y de campo),
> (4) explicar las distribuciones para usuarios no especialistas, (5) todas las distribuciones en
> los menús y (6) una hoja con toda la teoría. Supuestos de escala confirmados por el usuario:
> costo de obra S/ 120–300 M (se usa **S/ 200 M**, editable) y plazo de **24 meses (730 días)**.
> Copia el bloque de abajo y adjunta `Ejemplo.xlsm`, `plantilla_ppt.pptx` y `MD.zip`.

---

```text
ROL
Eres un desarrollador senior de Excel/VBA y analista cuantitativo de riesgos de proyectos de
construcción. Tu entregable es UN archivo Excel habilitado para macros (.xlsm) con el proyecto
VBA DENTRO del archivo (xl/vbaProject.bin), listo para abrir en Excel 2016/365 (Windows,
configuración regional Perú / español), habilitar macros y presionar un botón. Además entregas
como respaldo el módulo exportado MonteCarlo.bas (y ThisWorkbook.cls si lo usas).

OBJETIVO
Herramienta de análisis cuantitativo de riesgos por simulación Montecarlo para obras de
construcción, con DIMENSIONES DE IMPACTO CONFIGURABLES: por defecto COSTO (S/), PLAZO (días),
INGENIERÍA DE DISEÑO (HH) e INGENIERÍA DE CAMPO (HH), y cualquier otra que el usuario agregue.
Para amenazas y oportunidades entrega: percentiles P0–P100, reservas al nivel de confianza
elegido, curva S, tornado, rangos por riesgo, matriz probabilidad-impacto y comparación
antes/después de las respuestas. Incluye una guía de distribuciones para no especialistas y
una hoja con toda la teoría.

ARCHIVOS DE ENTRADA (adjuntos)
- Ejemplo.xlsm        -> GUÍA de diseño y base de riesgos (ver 0.1).
- plantilla_ppt.pptx  -> paleta de colores (lámina única "BLOOMBERG — Paleta de colores oficial").
- MD.zip              -> 10 archivos .md con la base metodológica (ver 0.3).
Si falta alguno, detente y pídemelo. Los ÚNICOS valores que no provienen de los adjuntos son
las estimaciones del ANEXO A, que ya vienen dadas en este prompt: úsalas tal cual. No inventes
otros riesgos, valores, colores ni método.

======================================================================
0. DATOS DE ENTRADA (verifícalos, no los reinterpretes)
======================================================================
0.1 Ejemplo.xlsm COMO GUÍA (nota prioritaria 1)
Ejemplo.xlsm es la versión 1 de esta herramienta, ya ejecutada con éxito en Excel real:
compiló, corrió 100 000 iteraciones y generó 6 gráficos. Tómala como GUÍA y conserva lo que
funcionó:
- Distribución de hojas y bloques: título en B2, subtítulo en B3, tablas desde la columna B,
  configuración arriba en PARAMETROS, tabla de riesgos debajo, guía de parámetros al final.
- Tipos de gráfico que ya funcionaron en Excel: curva S como dispersión XY suavizada con líneas
  punteadas P50/P80 y etiqueta; histograma de columnas con separación 10; tornado de barras
  horizontales con superposición 100 y orden invertido.
- Mensajes, etapas del manejo de errores y estructura de RESULTADOS (percentiles,
  estadísticas, contingencias), CURVA_S, TORNADO, RANGOS y SIMULACION.
Lo que NO debes copiar: su proyecto VBA (está "bloqueado para visualización", ver R10), sus
colores (paleta anterior) ni el uso de Rnd().
Datos: tblRiesgos B11:N61. Filas 12–16 = 5 riesgos DEMOSTRATIVOS cuantificados; filas 17–48 =
32 riesgos REALES que solo traen el texto (ANEXO A). Costo base, plazo base y semilla vacíos;
iteraciones = 100 000.

[DECISIÓN D1, actualizada]: cargar 37 riesgos:
  * R-01 … R-32 con ACTIVO = "SI", ESTADO = "ESTIMADO – VALIDAR" y los valores del ANEXO A.
    En NOTAS: "Estimación preliminar del analista con costo base supuesto S/ 200 M y plazo
    730 días; validar con el dueño del riesgo". Nota prioritaria 2.
  * EJ-1 … EJ-5 (los 5 demostrativos) con ACTIVO = "NO", ESTADO = "EJEMPLO". Se conservan
    como referencia y para las pruebas.
- Normalización: recortar espacios y unir espacios dobles. Si el texto contiene " - Debido a"
  (15 de 32), copiar lo posterior a "Debido a" en CAUSA; el texto completo queda en NOMBRE.
- Configuración inicial: CostoBase = 200 000 000; PlazoBase = 730; Iteraciones = 10 000;
  Semilla = 12345; NivelConfianza = 0,80; ReservaGestionPct = 0 %. En INICIO y en PARAMETROS,
  indicar que CostoBase y PlazoBase son SUPUESTOS a reemplazar por los valores del contrato.
- Entregar TABLA DE MAPEO origen -> destino -> transformación y el conteo 37 = 37.

0.2 PALETA DE COLORES (plantilla_ppt.pptx: paleta Bloomberg). Sin cambios respecto de la v2:
  ROL                              FONDO      TEXTO      CONTRASTE  VALOR LONG VBA (fondo)
  Banda de título de hoja          #000000    #FFA028    10.3:1     0
  Encabezado de tabla              #000000    #FFA028    10.3:1     0
  Subtítulo / notas                #FFFFFF    #333333    12.6:1     16777215
  Fila alterna (derivado*)         #FFF7EB    #000000    19.8:1     15464447
  Celda de entrada (derivado*)     #FFF0D6    #000000    18.7:1     14086399
  Celda de salida (derivado*)      #EDEDED    #000000    17.9:1     15592941
  Resaltado P10                    #4AF6C3    #000000    15.3:1     12842570
  Resaltado P50                    #FFB020    #000000    11.5:1     2142463
  Resaltado P80 / nivel elegido    #FFA028    #000000    10.3:1     2662655
  Resaltado P90                    #FB8B1E    #000000     8.8:1     2001915
  Error de validación              #FF433D    #000000     6.1:1     4015103
  Advertencia de validación        #FFB020    #000000    11.5:1     2142463
  Oportunidad (marca en tabla)     #00C805    #000000     9.3:1     378880
  Estimado – validar (marca)       #FFF0D6 con borde #CC7A00 y texto #000000
  Bordes finos                     #333333                           3355443
  Tornado 10 % inferior / superior #00C805 / #FF433D
  Botones                          #000000    #FFA028    10.3:1
  Series por dimensión, en orden: 1 COSTO #FF6600 · 2 PLAZO #0068FF · 3 ING_DISENO #CC7A00 ·
  4 ING_CAMPO #2A2A2A · 5.ª y 6.ª: #FF6600 y #0068FF con línea punteada.
  Referencias en curvas S: P50 #333333 punteada; P(nivel) #FF433D punteada.
  (*) Tinte claro de un color de la paleta (la paleta no trae neutros claros); repórtalo así.
Combinaciones PROHIBIDAS: texto blanco sobre #FF433D (3.4:1) o #FF6600 (2.9:1); texto
#A0A0A0, #CC7A00 o #D4890A sobre blanco. No debe quedar ningún color de la v1 (RGB(15,110,86),
#0F6E56, 5664271).

0.3 METODOLOGÍA (MD.zip). Fuentes: [PMI-E] estándar PMI de gestión de riesgos (español),
[PMI-G] guía práctica PMI, [VOSE] Risk Analysis 3.ª ed., [KROESE-H] Handbook of Monte Carlo
Methods, [KROESE-S] Simulation and the Monte Carlo Method (solucionario), [STEVENS] Monte-Carlo
Simulation, [GLASS] Glasserman, [RC] Robert y Casella, [AU] Au y Wang (Subset Simulation),
[LK] Law y Kelton (solo imágenes, sin texto: "Sin contenido utilizable").
Requisitos M1–M15 de la v2, con los ajustes de la v3 (todos van a Trazabilidad_Metodologia.md):
  M1  Definiciones [PMI-E 2.1, Glosario]: riesgo, amenaza, oportunidad, riesgo individual y
      general, reserva para contingencias (riesgos conocidos), reserva de gestión (trabajo no
      previsto), riesgo residual y secundario.
  M2  Registro de riesgos [VOSE 1.6; PMI-E 4.3]: TIPO, CATEGORIA, CAUSA, DUENO DEL RIESGO,
      ESTRATEGIA (amenazas: ESCALAR, EVITAR, TRANSFERIR, MITIGAR, ACEPTAR; oportunidades:
      ESCALAR, EXPLOTAR, COMPARTIR, MEJORAR, ACEPTAR), ESTADO.
  M3  Evento de riesgo = Bernoulli(p) × impacto [VOSE 5.3.7]: una sola variable por riesgo y
      dimensión en la sensibilidad. La MISMA ocurrencia dispara todas las dimensiones del
      riesgo en esa iteración.
  M4  Oportunidades [PMI-E 2.1.2; VOSE]: parámetros positivos; el modelo aplica signo negativo.
  M5  Probabilidad > 50 % [VOSE cap. 1]: advertencia (no error).
  M6  VME por riesgo y dimensión [PMI-E X6.4.4] = p × media condicionada del impacto; la suma
      debe coincidir con la media simulada (± 2 %).
  M7  Reservas por dimensión [PMI-E Glosario y X6.4.1; VOSE 19.1]: a) reserva para
      contingencias = P(NivelConfianza) del impacto; b) variante Vose: valor esperado +
      (P(nivel) − media); c) reserva de gestión = ReservaGestionPct × base (solo COSTO, y en
      otras dimensiones si el usuario la activa en tblDimensiones); d) presupuesto
      recomendado = base + a) + c).
  M8  Correlación por grupos [PMI-E 4.5; VOSE cap. 13]: GRUPO_CORRELACION y RHO_GRUPO (0–0,95).
      Iman–Conover con un factor común por grupo. Se reordena el vector completo del evento
      (todas sus dimensiones juntas) usando como clave la primera dimensión con impacto.
      Reportar la correlación de rango lograda vs. objetivo.
  M9  Generador MRG32k3a [KROESE-H cap. 1] en lugar de Rnd(), en aritmética Double, con
      semilla reproducible. Validar contra los valores publicados.
  M10 Precisión [VOSE cap. 7; STEVENS cap. 2; KROESE-H]: error estándar e IC 95 % de la
      media; IC 95 % del percentil del nivel por estadísticos de orden; iteraciones sugeridas
      para ± 1 %.
  M11 Sensibilidad [VOSE 5.3.7]: Spearman, contribución a la varianza (rho²/Σrho²), swing.
  M12 Antes/después de la respuesta [PMI-E 4.6; VOSE 1.3–1.4]: PROB_RESIDUAL,
      FACTOR_IMPACTO_RESIDUAL (0–1, se aplica a TODAS las dimensiones del riesgo) y
      COSTO_RESPUESTA (S/, se suma al COSTO "después"). Misma semilla en ambos escenarios.
  M13 Matriz probabilidad–impacto 5×5 [PMI-E X6.3.5 y X6.4.3; VOSE tabla 1.1]: tblEscalas
      con umbrales de probabilidad y de impacto POR DIMENSIÓN (razón ~3 entre niveles). El
      nivel de impacto del riesgo es el MAYOR entre sus dimensiones; mostrar también la matriz
      de cada dimensión.
  M14 Agregación [VOSE 19.2]: suma por dimensión. Para PLAZO es un supuesto conservador
      (todo sobre la ruta crítica), sin lógica de red: declararlo como limitación. Para las
      dimensiones en HH, advertir que no deben convertirse a S/ y sumarse al COSTO si ese
      costo ya está en C_P* (evitar doble conteo).
  M15 No implementado, con motivo: hipercubo latino [VOSE 4.4.3], Subset Simulation [AU],
      MCMC [RC], reducción de varianza financiera [GLASS], asignación de contingencia por
      partida [VOSE 19.1], [LK] sin texto.
  M16 NUEVO. Selección y parametrización de distribuciones para no especialistas [VOSE cap. 9 y
      14, elicitación de expertos; VOSE cap. 1 "incertidumbre vs. evento"]: guía práctica en
      la hoja GUIA (sección 1).
  M17 NUEVO. Catálogo completo de distribuciones [VOSE parte II; KROESE-H "Random variable
      generation" y "Probability distributions"; KROESE-S cap. 2]: sección 3.
Prioridad: en lo METODOLÓGICO prevalecen los .md; en lo TÉCNICO (R1–R15) prevalece este
prompt. Si un .md trae un requisito aplicable que no está aquí, impleméntalo y regístralo.

======================================================================
1. ESTRUCTURA DEL LIBRO
======================================================================
Hojas en este orden: INICIO, GUIA, PARAMETROS, RESULTADOS, CURVA_S, TORNADO, RANGOS, MATRIZ_PI,
COMPARACION, SIMULACION, TEORIA.
CodeNames: hjInicio, hjGuia, hjParametros, hjResultados, hjCurvaS, hjTornado, hjRangos,
hjMatriz, hjComparacion, hjSimulacion, hjTeoria. El VBA usa SIEMPRE los CodeNames.
Todas las hojas: cuadrícula oculta, banda de título negra con texto ámbar, Calibri.

INICIO: propósito; descripción de cada hoja; pasos de uso (1–8: revisar supuestos de base,
validar las estimaciones del ANEXO A con cada dueño, elegir distribuciones con la GUIA,
validar, correr, leer resultados, comparar antes/después, agregar dimensiones); resumen de
METODOLOGÍA (M1–M17); limitaciones; aviso destacado: "Los 32 riesgos traen ESTIMACIONES
PRELIMINARES (ESTADO = ESTIMADO – VALIDAR)".

GUIA (notas prioritarias 4 y 5). Hoja de consulta para usuarios no especialistas:
 1) ¿Qué es una distribución? Explicación en lenguaje llano: "no sabemos el valor exacto;
    describimos qué valores son posibles y cuáles son más probables". Diferencia clave entre
    PROBABILIDAD DE OCURRENCIA (¿pasa o no pasa?, va en PROBABILIDAD) e INCERTIDUMBRE DEL
    IMPACTO (si pasa, ¿cuánto cuesta o demora?, va en la distribución). Ejemplo con R-11.
 2) Árbol de decisión "¿qué sé del impacto?":
    - Solo un rango, sin valor más probable ............... UNIFORME
    - Mínimo, más probable y máximo ....................... PERT (recomendada) o TRIANGULAR
    - Opiniones del tipo "rara vez baja de X o pasa de Y" ... TRIGEN (P10 / moda / P90)
    - Promedio y dispersión simétrica (datos históricos) ... NORMAL
    - Costos o duraciones sesgados a la derecha, nunca < 0 .. LOGNORMAL o GAMMA
    - Número de eventos (accidentes, NCR, RFI) en el periodo  POISSON o BINOMIAL
    - Pocos escenarios con probabilidad conocida ........... DISCRETA
    - Valor seguro .......................................... CONSTANTE
    - Colas extremas (reclamos grandes, eventos raros) ...... PARETO, GUMBEL o LOGNORMAL
 3) Cómo preguntar al experto (3 preguntas de elicitación, VOSE cap. 14): "¿cuál es el
    impacto más probable?", "¿cuál es el mínimo razonable si todo sale bien?", "¿cuál es el
    máximo razonable si todo sale mal (sin catástrofes absurdas)?". Preguntar primero los
    extremos para evitar el anclaje en la moda.
 4) Cómo llenar C_P1…C_P4, T_P1…T_P4 y demás: tabla por distribución con el significado de
    cada parámetro, en la unidad de la dimensión, y un ejemplo numérico de obra.
 5) Errores frecuentes: poner la probabilidad dentro del impacto; usar el peor caso como moda;
    mezclar unidades (miles vs. soles, días hábiles vs. calendario); duplicar un mismo impacto
    en COSTO y en HH valorizadas; poner mín > moda.
 6) Gráficos estáticos de la forma de cada distribución (curvas de densidad generadas al
    construir el libro con datos tabulados en la misma hoja).
 7) tblDistribuciones (catálogo de la sección 3): DISTRIBUCION | P1 | P2 | P3 | P4 | CUANDO USAR
    | EJEMPLO. Es la FUENTE de las listas desplegables (nombre definido ListaDistribuciones) y
    de la ayuda en PARAMETROS.

PARAMETROS
- Configuración (nombres definidos): CostoBase, PlazoBase, Iteraciones, Semilla,
  NivelConfianza, ReservaGestionPct.
- tblDimensiones (nota prioritaria 3): CLAVE | NOMBRE | UNIDAD | BASE | FORMATO | ACTIVA (SI/NO)
  | RESERVA_GESTION (SI/NO) | COLOR. Filas iniciales:
    COSTO      | Costo                    | S/   | =CostoBase | #,##0   | SI | SI | #FF6600
    PLAZO      | Plazo                    | días | =PlazoBase | #,##0.0 | SI | NO | #0068FF
    ING_DISENO | Ingeniería de diseño     | HH   | (vacío)    | #,##0   | SI | NO | #CC7A00
    ING_CAMPO  | Ingeniería de campo      | HH   | (vacío)    | #,##0   | SI | NO | #2A2A2A
  Máximo 6 dimensiones. La CLAVE es ASCII, en mayúsculas y sin espacios.
- tblEscalas (M13): NIVEL 1–5 | DESCRIPCION (Muy baja … Muy alta) | PROB_MAX | un umbral de
  impacto máximo por dimensión (columna IMP_<CLAVE>). Valores iniciales (razón ~3, escala del
  proyecto): PROB_MAX 0,10 / 0,30 / 0,50 / 0,70 / 1,00; IMP_COSTO 200 000 / 600 000 /
  1 800 000 / 5 400 000 / sin tope; IMP_PLAZO 5 / 15 / 45 / 120 / sin tope; IMP_ING_DISENO
  y IMP_ING_CAMPO 100 / 300 / 900 / 2 700 / sin tope.
- tblRiesgos (ListObject). Columnas comunes: ID | NOMBRE DEL RIESGO | TIPO | CATEGORIA | CAUSA |
  DUENO DEL RIESGO | ESTADO | ACTIVO | PROBABILIDAD | GRUPO_CORRELACION | RHO_GRUPO |
  ESTRATEGIA | PROB_RESIDUAL | FACTOR_IMPACTO_RESIDUAL | COSTO_RESPUESTA | NOTAS.
  Por CADA dimensión de tblDimensiones, 5 columnas con nombre fijo:
  DIST_<CLAVE> | <CLAVE>_P1 | <CLAVE>_P2 | <CLAVE>_P3 | <CLAVE>_P4
  (p.ej. DIST_COSTO, COSTO_P1 … COSTO_P4; DIST_ING_CAMPO, ING_CAMPO_P1 …).
  * El VBA lee TODO por el texto del encabezado y descubre las dimensiones desde
    tblDimensiones: agregar una dimensión NO requiere tocar el código.
  * Por cada dimensión, una columna de ayuda AYUDA_<CLAVE> con fórmula INDEX/MATCH (no XLOOKUP,
    por compatibilidad con 2016) contra tblDistribuciones que muestre, p.ej.,
    "P1=Mínimo · P2=Moda · P3=Máximo". Escribir las fórmulas con .Formula (sintaxis inglesa).
  * Listas: TIPO, ACTIVO, ESTADO (EJEMPLO, ESTIMADO – VALIDAR, CUANTIFICADO, PENDIENTE DE
    CUANTIFICAR, CERRADO), ESTRATEGIA (M2), DIST_* = ListaDistribuciones (las 20 de la
    sección 3, más "(vacío)" = no afecta esa dimensión). Mensaje de entrada en cada DIST_*:
    "Elija la distribución; vea la hoja GUIA".
  * NOMBRE DEL RIESGO con ajuste de texto y ancho ~60.
- Botones como FORMAS (rectángulo redondeado, fondo #000000, texto #FFA028, negrita) con
  OnAction:
    "▶ CORRER SIMULACIÓN"   -> EjecutarSimulacion
    "✔ VALIDAR DATOS"       -> ValidarDatos
    "✖ LIMPIAR RESULTADOS"  -> LimpiarResultados
    "＋ AGREGAR DIMENSIÓN"  -> AgregarDimension (pide CLAVE, nombre, unidad y formato; agrega
                              la fila en tblDimensiones, las 5 columnas y la de ayuda en
                              tblRiesgos, y la columna IMP_<CLAVE> en tblEscalas)
  Si se crean desde VBA, los símbolos se construyen con ChrW (▶ 9654, ✔ 10004, ✖ 10006,
  ＋ 65291).
Hojas de salida: no se borran ni se recrean; se limpian (Cells.Clear y ChartObjects) y se
reescriben. Con N dimensiones activas, cada hoja repite su bloque por dimensión, en el orden
de tblDimensiones.

TEORIA (nota prioritaria 6). Toda la teoría usada, con la fuente de cada punto:
 1. Gestión de riesgos: definiciones M1, proceso PMI (planificar, identificar, análisis
    cualitativo y cuantitativo, respuesta, implementación, monitoreo), apetito y umbral.
 2. Simulación Montecarlo: idea, ley de los grandes números, teorema central del límite,
    error proporcional a 1/√N, cómo leer iteraciones y percentiles.
 3. Números aleatorios: generadores congruenciales, por qué no se usa Rnd() (período ~2^24),
    algoritmo MRG32k3a (recurrencias, módulos, multiplicadores) y semilla.
 4. Generación de variables: transformada inversa, aceptación-rechazo, Box–Muller,
    Marsaglia–Tsang para Gamma, Beta como cociente de Gammas. Fórmula de cada una de las 20
    distribuciones: parámetros, media, varianza y método de generación.
 5. Modelo de evento de riesgo: Bernoulli × impacto, oportunidades con signo negativo,
    agregación por dimensión y sus supuestos.
 6. Correlación: Pearson vs. Spearman, Iman–Conover, modelo de un factor por grupo y por qué
    siempre es una matriz válida.
 7. Estadísticos de salida: percentiles (interpolación igual que PERCENTIL.INC), media,
    desviación, CV, IC 95 % de la media y del percentil.
 8. Reservas: contingencia vs. gestión, nivel de confianza, variante Vose y VME.
 9. Sensibilidad: tornado, Spearman, contribución a la varianza, swing.
 10. Matriz probabilidad-impacto y escalas.
 11. Antes/después de la respuesta, riesgo residual y beneficio neto.
 12. Limitaciones y técnicas no aplicadas (M14, M15).
 13. Bibliografía: los 10 .md con título, autores y la sección citada.
Fórmulas en texto legible (p.ej. "media PERT = (mín + 4·moda + máx) / 6"). No uses objetos de
ecuación.

======================================================================
2. REGLAS OBLIGATORIAS DEL CÓDIGO VBA
======================================================================
R1. Código fuente 100 % ASCII, comentarios incluidos (página de códigos 1252). Tildes desde VBA
    con U("Simulaci\u00F3n") (convierte \uXXXX con ChrW) o ChrW directo.
R2. Option Explicit; todas las variables declaradas.
R3. Type, Const y variables de módulo antes del primer Sub/Function.
R4. Toda variable que reciba Array(...) es Variant.
R5. Long para filas, contadores e índices.
R6. On Error GoTo en EjecutarSimulacion; restaurar siempre ScreenUpdating, Calculation,
    EnableEvents y StatusBar; MsgBox en español con número, descripción, etapa, riesgo/fila y
    dimensión.
R7. Arrays en memoria y un solo volcado Range.Value = array. Objetivo: 10 000 iteraciones ×
    37 riesgos × 4 dimensiones en < 20 s sin el escenario "después"; reporta el tiempo real.
    Memoria: si N × riesgos × dimensiones supera 20 millones de valores, avisar y sugerir
    menos iteraciones.
R8. Sin referencias externas, ActiveX ni Analysis ToolPak; sin constantes mso* (valor numérico
    con comentario). Debe compilar con Depuración > Compilar VBAProject.
R9. 32 y 64 bits (sin Declare; PtrSafe solo si fuera imprescindible).
R10. MACRO ABIERTA, SIN CLAVE: proyecto sin contraseña ni "bloqueado para visualización";
    CMG/DPB/GC CIFRADOS con la clave del ID del proyecto (MS-OVBA 2.4.3: suma de los bytes del
    texto del ID, módulo 256). Nunca copiarlos de otro proyecto: eso hizo que Excel dejara
    Ejemplo.xlsm "bloqueado para visualización" (GC = 00, CMG = 05). Valores descifrados
    obligatorios: CMG = 00000000, DPB = 00, GC = FF. Sin protección de hojas ni de libro, y
    sin hojas ocultas.
R11. Todo en español: textos, gráficos, botones, mensajes, nombres definidos, macros,
    procedimientos, variables, comentarios y propiedades del archivo (idioma es-PE).
    Excepciones: .Formula en inglés y NumberFormat con códigos ingleses. Fechas
    "dd/mm/yyyy hh:mm".
R12. tblRiesgos, tblDimensiones, tblEscalas y tblDistribuciones se leen por encabezado.
R13. Colores como Const Long por rol (tabla 0.2), sin RGB() en Const y sin colores sueltos.
    Los colores de las dimensiones se leen de tblDimensiones.
R14. Macros públicas SOLO: EjecutarSimulacion, ValidarDatos, LimpiarResultados,
    AgregarDimension y la función ValidarParametros() As Boolean.
R15. Distribuciones centralizadas: una función Muestra(codigo, p1, p2, p3, p4) y una tabla
    interna de metadatos (nombre, n.º de parámetros, validaciones) coherente con
    tblDistribuciones. Agregar una distribución = agregarla a ambos sitios.

======================================================================
3. CATÁLOGO DE DISTRIBUCIONES (nota prioritaria 5): las 20 en todos los menús
======================================================================
  NOMBRE            P1            P2             P3            P4             GENERACIÓN
  CONSTANTE         valor         –              –             –              directo
  UNIFORME          mínimo        máximo         –             –              inversa
  TRIANGULAR        mínimo        moda           máximo        –              inversa
  TRIGEN            valor bajo    moda           valor alto    % bajo (10)    triangular cuyos percentiles P4 y 100−P4 son P1 y P3 (VOSE)
  PERT              mínimo        moda           máximo        –              Beta(1+4·(m−a)/(b−a), 1+4·(b−m)/(b−a))
  PERT_MODIFICADA   mínimo        moda           máximo        gamma (4)      Beta con λ = P4
  BETA_GENERAL      alfa          beta           mínimo        máximo         X/(X+Y), Gamma
  NORMAL            media         desv. est.     –             –              Box–Muller
  NORMAL_TRUNCADA   media         desv. est.     mínimo        máximo         inversa con Φ y Φ⁻¹ (Acklam)
  LOGNORMAL         media         desv. est.     –             –              exp(Normal) con parámetros de la variable
  GAMMA             forma         escala         –             –              Marsaglia–Tsang
  EXPONENCIAL       media         –              –             –              inversa
  WEIBULL           forma         escala         –             –              inversa
  GUMBEL            ubicación     escala         –             –              inversa (valores extremos)
  LOGISTICA         media         escala         –             –              inversa
  PARETO            forma         mínimo         –             –              inversa (colas pesadas)
  POISSON           media (λ)     –              –             –              Knuth si λ < 30; si no, transformada con corrección
  BINOMIAL          n             p              –             –              suma de Bernoulli si n ≤ 50; si no, inversa
  DISCRETA_UNIFORME mínimo        máximo         –             –              entero uniforme
  DISCRETA          valores "v1;v2;…" probs "p1;p2;…" –       –              inversa sobre la acumulada (probs suman 1 ± 0,001)
Validaciones: parámetros requeridos numéricos (salvo DISCRETA, que usa texto); mín ≤ moda ≤ máx;
desviaciones, escalas, formas y medias > 0 donde corresponda; 0 < % bajo < 50 en TRIGEN;
0 ≤ p ≤ 1 y n entero ≥ 1 en BINOMIAL; en NORMAL_TRUNCADA, mín < máx y P(mín < X < máx) > 0,001.
Constantes permitidas (mín = máx). Todas las distribuciones con prueba de media y desviación
contra la teoría (sección 5).

======================================================================
4. LÓGICA Y SALIDAS
======================================================================
- ValidarParametros(): restablece colores; valida solo ACTIVO = SI y todas sus dimensiones.
  Errores según la sección 3, más RHO_GRUPO 0–0,95, PROB_RESIDUAL 0–1, FACTOR 0–1,
  COSTO_RESPUESTA ≥ 0, NivelConfianza 0,50–0,95, iteraciones 1 000–100 000, tblEscalas
  creciente y CLAVE de dimensión única. Advertencias (no detienen): p > 0,5; riesgos
  "ESTIMADO – VALIDAR" (conteo); riesgos PENDIENTES; EJEMPLO activos.
- EjecutarSimulacion(): validar -> leer dimensiones y riesgos -> MRG32k3a -> por iteración y
  riesgo: una ocurrencia; si ocurre, una muestra por cada dimensión con distribución; signo
  negativo para oportunidades -> Iman–Conover por grupo -> totales por dimensión ->
  escenario "después" con la misma semilla -> percentiles -> hojas y gráficos -> MsgBox
  final con P50 y P(nivel) de cada dimensión y la reserva recomendada -> activar RESULTADOS.
- RESULTADOS: por dimensión, percentiles P0…P100, estadísticas, VME vs. media, reservas
  (M7), precisión (M10). Tabla resumen al inicio: una fila por dimensión con base, P50,
  P(nivel), reserva y % sobre la base.
- CURVA_S: por dimensión, tabla 0–100 % cada 5 %, curva S y histograma de 20 clases.
- TORNADO: por dimensión, tabla ordenada y gráfico (verde/rojo); oportunidades marcadas.
- RANGOS: una fila por riesgo y dimensión (TIPO, prob., frecuencia observada, mín., P10,
  P25, P50, P75, P90, máx., promedio, VME) y totales por dimensión.
- MATRIZ_PI: matriz general (mayor nivel entre dimensiones) y una matriz por dimensión.
- COMPARACION: por dimensión, antes vs. después, beneficio neto y curvas S superpuestas.
- SIMULACION: primeras min(N, 5 000) iteraciones: ITER, totales por dimensión y columnas por
  riesgo y dimensión.
- Formato: colores de 0.2; formato numérico de cada dimensión según tblDimensiones; paneles
  inmovilizados; nada protegido.

======================================================================
5. ENTREGA Y AUTOVERIFICACIÓN
======================================================================
Entrega: a) MonteCarlo_Riesgos.xlsm; b) MonteCarlo.bas (+ .cls si aplica);
c) Trazabilidad_Metodologia.md (M1–M17); d) informe breve: mapeo (0.1), paleta aplicada
(0.2) y lista de verificación.
Si generas el archivo sin Excel: vbaProject.bin conforme a MS-OVBA (solo código fuente,
_VBA_PROJECT versión 0xFFFF, MODULEOFFSET = 0) y CMG/DPB/GC cifrados con la clave del ID; o
Excel vía COM (VBComponents.Import y FileFormat = 52).
Comprobaciones (reporta cada una):
  [ ] olevba extrae los módulos y coinciden byte a byte con el .bas; 0 bytes > 127; Type y
      Const arriba; sin variables sin declarar; ningún Array() en arreglo tipado.
  [ ] R10: CMG/DPB/GC descifrados = 00000000 / 00 / FF, con la clave del ID.
  [ ] R11: ninguna cadena visible en inglés (lista de cadenas revisada).
  [ ] Tablas y nombres definidos existen; lectura por encabezado probada moviendo columnas.
  [ ] tblRiesgos: 37 filas (32 ESTIMADO – VALIDAR activas + 5 EJEMPLO inactivas); valores del
      ANEXO A cargados sin cambios (comparar 5 filas); CAUSA en las 15 filas con "Debido a".
  [ ] AgregarDimension crea una 5.ª dimensión (p.ej. CALIDAD, "NCR", #,##0) y la simulación
      la procesa sin tocar el código.
  [ ] Las 20 distribuciones: media y desviación de 200 000 muestras dentro de ± 1 % (± 2 %
      en PARETO con forma > 3) de la teoría; DISCRETA y POISSON reproducen sus
      probabilidades.
  [ ] MRG32k3a reproduce los valores publicados; misma semilla = mismos resultados.
  [ ] Pruebas con los 5 EJEMPLO activados (independientes, semilla 12345, N = 10 000):
      P50/P80 dentro de ± 3 % de numpy (costo ≈ 67 400 / 133 000; plazo ≈ 52,3 / 73,1).
  [ ] Base real (ANEXO A), N = 400 000 en numpy con la misma lógica (costo PERT, plazo
      TRIANGULAR, HH TRIANGULAR/PERT). Referencia calculada al preparar este prompt, sin
      correlación / con correlación:
        COSTO     media ≈ 16,31 M / 16,32 M · P50 ≈ 16,11 M / 15,87 M · P80 ≈ 20,14 M / 21,47 M
        PLAZO     media ≈ 85 / 85 d        · P50 ≈ 81 / 82 d        · P80 ≈ 116 / 122 d
        ING_DISEÑO media ≈ 2 708 / 2 710 HH · P80 ≈ 3 867 / 4 258 HH
        ING_CAMPO media ≈ 1 290 / 1 290 HH · P80 ≈ 1 965 / 1 999 HH
      La macro (N = 10 000, semilla 12345) debe quedar dentro de ± 3 % en P50 y P80 y de
      ± 2 % en las medias. Con correlación, P80 COSTO > P80 sin correlación.
  [ ] Correlación: rango lograda = objetivo ± 0,05 en cada grupo.
  [ ] Oportunidad: cambiar un riesgo a OPORTUNIDAD reduce la media en 2 × su VME (± 2 %).
  [ ] Antes/después: con PROB_RESIDUAL = 0 en todos, el P80 "después" del COSTO = suma de
      COSTO_RESPUESTA y el de las demás dimensiones = 0.
  [ ] VME total ≈ media simulada (± 2 %) en cada dimensión.
  [ ] Casos borde sin error: mín = máx, fila vacía, probabilidad 0 y 1, columna reordenada,
      dimensión desactivada, riesgo sin ninguna dimensión (error claro), solo EJEMPLO
      inactivos (mensaje "no hay riesgos activos").
Si algo falla, corrígelo antes de entregar.

======================================================================
ANEXO A – 32 RIESGOS REALES CON ESTIMACIÓN PRELIMINAR (nota prioritaria 2)
======================================================================
Supuestos: obra de edificación hospitalaria o institucional en Lima (hay llamado de
enfermeras, UMAS, muro anclado y vecinos), costo base S/ 200 M y plazo 730 días.
Montos en S/. COSTO = PERT(mín; moda; máx) y PLAZO = TRIANGULAR(mín; moda; máx) en días, salvo
que se indique otra cosa; HH = horas-hombre (TRI = TRIANGULAR). Todos: TIPO = AMENAZA,
ACTIVO = SI, ESTADO = ESTIMADO – VALIDAR.
Grupos de correlación (RHO_GRUPO): CONTRACTUAL 0,5 · APROBACIONES 0,5 · CALIDAD 0,4 ·
INGENIERIA 0,5 · EXTENSION_PLAZO 0,6 · SOBRECONSUMO 0,4. Vacío = independiente.
ID   | CATEGORIA     | GRUPO           | PROB | COSTO (mín; moda; máx)          | PLAZO días     | ING_DISENO HH         | ING_CAMPO HH
R-01 | CONTRACTUAL   | CONTRACTUAL     | 0,40 | 1 500 000; 4 000 000; 9 000 000 | –              | –                     | –
R-02 | CONTRACTUAL   | CONTRACTUAL     | 0,50 |   300 000;   800 000; 1 800 000 | –              | TRI 80; 200; 400      | –
R-03 | PRODUCCION    | SOBRECONSUMO    | 0,60 |   400 000; 1 000 000; 2 200 000 | –              | –                     | –
R-04 | COSTOS        | –               | 0,50 |   800 000; 2 000 000; 4 500 000 | –              | –                     | –
R-05 | APROBACIONES  | APROBACIONES    | 0,45 |   200 000;   500 000; 1 200 000 | 15; 30; 60     | TRI 120; 300; 600     | –
R-06 | CALIDAD       | CALIDAD         | 0,35 |   150 000;   400 000;   900 000 | 3; 7; 15       | –                     | TRI 200; 500; 1 200
R-07 | CALIDAD       | CALIDAD         | 0,30 |   100 000;   300 000;   700 000 | 2; 5; 12       | –                     | TRI 150; 400; 900
R-08 | CALIDAD       | CALIDAD         | 0,30 |   100 000;   350 000;   800 000 | –              | –                     | TRI 150; 350; 800
R-09 | SSOMA         | –               | 0,08 |   300 000; 1 200 000; 4 000 000 | 5; 15; 45      | –                     | –
R-10 | CONTRACTUAL   | CONTRACTUAL     | 0,40 |   200 000;   600 000; 1 500 000 | –              | –                     | –
R-11 | APROBACIONES  | APROBACIONES    | 0,55 |   200 000;   600 000; 1 400 000 | 10; 20; 45     | –                     | –
R-12 | TERCEROS      | –               | 0,25 |   300 000; 1 000 000; 3 500 000 | 0; 7; 30       | –                     | TRI 100; 300; 800
R-13 | APROBACIONES  | APROBACIONES    | 0,50 |   100 000;   400 000; 1 000 000 | 5; 15; 35      | –                     | –
R-14 | INGENIERIA    | INGENIERIA      | 0,65 |   800 000; 2 500 000; 6 000 000 | 10; 25; 60     | PERT 500; 1 500; 4 000| PERT 300; 900; 2 500
R-15 | TERCEROS      | –               | 0,30 |   150 000;   400 000;   900 000 | –              | –                     | –
R-16 | PERMISOS      | –               | 0,12 |   500 000; 1 800 000; 5 000 000 | 15; 45; 120    | TRI 200; 500; 1 200   | –
R-17 | CONTRACTUAL   | CONTRACTUAL     | 0,40 |   300 000;   900 000; 2 000 000 | –              | –                     | –
R-18 | CONTRACTUAL   | CONTRACTUAL     | 0,45 |   400 000; 1 200 000; 2 800 000 | –              | –                     | –
R-19 | CONTRACTUAL   | CONTRACTUAL     | 0,40 |   200 000;   500 000; 1 200 000 | –              | –                     | –
R-20 | CONTRACTUAL   | EXTENSION_PLAZO | 0,35 |   800 000; 2 500 000; 6 000 000 | –              | –                     | –
R-21 | INGENIERIA    | INGENIERIA      | 0,55 |   500 000; 1 500 000; 3 500 000 | 5; 12; 30      | PERT 400; 1 000; 2 500| –
R-22 | INGENIERIA    | INGENIERIA      | 0,45 |   300 000;   900 000; 2 200 000 | –              | PERT 300; 700; 1 800  | –
R-23 | INGENIERIA    | INGENIERIA      | 0,40 |   200 000;   600 000; 1 500 000 | –              | PERT 200; 500; 1 200  | –
R-24 | COSTOS        | –               | 0,90 | TRIANGULAR 300 000; 500 000; 800 000 | –         | –                     | –
R-25 | COSTOS        | –               | 0,50 |   200 000;   600 000; 1 400 000 | –              | –                     | –
R-26 | COSTOS        | EXTENSION_PLAZO | 0,40 | 1 000 000; 3 000 000; 7 000 000 | –              | –                     | –
R-27 | COSTOS        | EXTENSION_PLAZO | 0,40 |   400 000; 1 200 000; 3 000 000 | –              | –                     | –
R-28 | PRODUCCION    | SOBRECONSUMO    | 0,50 |   300 000;   800 000; 1 800 000 | –              | –                     | –
R-29 | PRODUCCION    | SOBRECONSUMO    | 0,45 |   200 000;   500 000; 1 200 000 | –              | –                     | –
R-30 | PRODUCCION    | SOBRECONSUMO    | 0,40 |   100 000;   300 000;   700 000 | –              | –                     | –
R-31 | PRODUCCION    | SOBRECONSUMO    | 0,50 |   300 000;   900 000; 2 000 000 | –              | –                     | –
R-32 | PRODUCCION    | SOBRECONSUMO    | 0,50 |   200 000;   600 000; 1 500 000 | –              | –                     | –
Notas de la estimación (copiarlas en NOTAS de cada fila afectada):
  R-03 (0,60) y R-11 (0,55) superan 50 %: se conservan como riesgos y activan la advertencia M5.
  R-24 (0,90), "ya realizados", es casi seguro: la advertencia M5 sugiere pasarlo a la línea
  base.
  R-17…R-20 ("Mayor costo - Reconocimiento de …") quedan como AMENAZA con NOTAS = "Confirmar
  si es oportunidad (reconocimiento del cliente)". [DECISIÓN D2]
  R-09 y R-16 son de baja probabilidad y alto impacto: por eso dominan la cola del plazo.

TEXTO LITERAL DE LOS 32 RIESGOS (NOMBRE DEL RIESGO; espacios normalizados)
R-01 Consumo total de contingencia y afectación utilidad de Cosapi - Debido a que el Cliente no acepta el acuerdo de cuentas de control dejando la posibilidad de que la cuantificación del balance se realice partida a partida y no por cuentas de control que consideramos era el acuerdo, por lo que habrian muchos más sobrecostos (+) afectando directamente la utilidad.
R-02 Afectación utilidad de Cosapi - Debido a no reconocimiento de adicional por drywall y verificación de framming
R-03 Costos desestimados - Debido a mayor desperdicio de concreto / acero / conectores / otros
R-04 Costos desestimados - Mayores costos indirectos dentro del plazo contractual
R-05 Demora en la aprobación de fabricación y suministro de UMAS - Debido al retraso en la verificación acustica correspondiente a las UMAS para proceder a la orden de fabricación, cuya responsabilidad indica el Cliente le correspondía al proyectista mecánico (Cosapi Ingeniería).
R-06 Costos desestimados - Debido a no conformidades por la ejecución de tarrajeos y solaqueos
R-07 Costos desestimados - Debido a no conformidades en la ejecución de los contrapisos
R-08 Costos desestimados - Debido a no conformidades corrientes debiles/inst ACI-IIEE
R-09 Paralización de obra - Debido a infracciones muy graves / accidente de trabajo
R-10 Consumo total de contingencia y afectación utilidad de Cosapi - Debido a no reconocimiento de adicional Puertas / Cerrajeria
R-11 Retraso en la ejecución de obra por demoras de las aprobaciones de la Supervisión - Debido a retrasos en la aprobación de Submittals (bloquetas / EEMM Ascensores)
R-12 Aparición de fisuras, grietas en viviendas vecinas, con su consecuente reclamos de vecinos - Debido a asentamientos diferenciales propios de la reconsolidación del terreno, durante la excavación,ejecución del muro anclado, y posterior al destensado del muro anclado
R-13 Retraso en la ejecución de nuestros trabajos por demoras en las liberaciones - Debido a que la Supervisión no quiere realizar las liberaciones indicando que debe estar presentes los ingenieros de calidad / de producción
R-14 Reprocesos y/o atrasos en la ejecución que generan mayores costos que no quiera asumir como Orden de cambio - Debido a no tener un ingeniería terminada, la cual continúa actualizándose
R-15 Cambiar todas las ventanas de los vecinos a ventanas antiruidos, - Debido a las quejas de los vecinos por los ruidos de la obra superior a los decibeles permitidos
R-16 Paralizacion de obra por no contar con licencia actualizada - Debido a diferencias sustanciales entre proyecto aprobado municipal y proyecto de construcción que requieran actualización de licencia.
R-17 Mayor costo - Reconocimiento de adicionales de Cosapi Ingenieria
R-18 Mayor costo - Reconocimiento de mayores costos por incremento de staff a fecha contractual
R-19 Mayor costo - Reconocimiento de orden de cambio denegados (conectores de cabeza, colgajos)
R-20 Mayor costo - Reconocimiento de mayores costos por ampliacion de plazo
R-21 Costos desestimados - Deficiencias en ingenieria MEPS desarrollada por COSAPI (llamado enfermeras, acustico UMAS, antisismico, valvula de cortes, otros)
R-22 Costos desestimados - Deficiencias en ingenieria MEPS desarrollada por COSAPI (soportes no estructurales y estructura drywall)
R-23 Costos desestimados - Deficiencias en ingenieria MEPS desarrollada por COSAPI (proyeccion)
R-24 Costos desestimados - Mayores recursos por obras provisionales ya realizados
R-25 Costos desestimados - Mayores recursos por obras provisionales proyectados
R-26 Costos desestimados - Mayores costos indirectos en la extensión del plazo
R-27 Costos desestimados - Mayores costos indirectos de subcontratistas por extension de plazo
R-28 Costos desestimados - Sobreconsumo de acero
R-29 Costos desestimados - Sobreconsumo de recursos en la ejecución de drywall
R-30 Costos desestimados - Sobreconsumo de recursos en la ejecución de bloquetas
R-31 Costos desestimados - Sobreconsumo de recursos por SSOMA, elementos horizontales concreto encofrado, HVAC, empaste pintura
R-32 Costos desestimados - Sobreconsumo de recursos varios
```

---

## Cambios respecto de la v2 (notas prioritarias)

| Nota | Cómo quedó |
|---|---|
| 1. Ejemplo.xlsm como guía | 0.1 dice qué conservar de la v1, que ya funcionó en Excel (diseño, gráficos, mensajes), y qué no copiar (el VBA bloqueado, los colores y `Rnd()`). |
| 2. Completar los 32 riesgos | Anexo A: probabilidad, costo, plazo y HH de los 32 riesgos, más categoría y grupo de correlación. Base supuesta S/ 200 M y 730 días. Los riesgos quedan activos y marcados «ESTIMADO – VALIDAR». Verifiqué la coherencia con numpy: impacto medio de 8,2 % de la base y P80 de 10,1 %. |
| 3. Más dimensiones | `tblDimensiones` + columnas `DIST_<CLAVE>`/`<CLAVE>_P1..P4`. Vienen ING_DISENO e ING_CAMPO (HH) y el botón «Agregar dimensión», sin tocar el código. |
| 4. Explicar las distribuciones | Hoja GUIA: diferencia entre probabilidad e impacto, árbol de decisión, 3 preguntas al experto, significado de cada parámetro, errores frecuentes, gráficos de forma y ayuda automática junto a cada fila. |
| 5. Todas las distribuciones en los menús | Catálogo de 20 distribuciones con parámetros, validaciones y método de generación; la lista sale de `tblDistribuciones`. |
| 6. Hoja de teoría | Hoja TEORIA con 13 secciones y la bibliografía de los 10 `.md`. |
