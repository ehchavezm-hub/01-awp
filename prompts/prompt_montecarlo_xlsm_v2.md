# Prompt v2: Herramienta de Riesgos Montecarlo en Excel (.xlsm con macro incluida)

> Versión 2 (26/09/2026). Incorpora: base de riesgos de `Ejemplo.xlsm`, paleta Bloomberg de
> `plantilla_ppt.pptx`, macro abierta sin clave, todo en español, y la metodología de los 10 `.md`
> de `MD.zip`. Copia el bloque de abajo y adjunta los tres archivos al pegarlo.
> Las decisiones marcadas como **[DECISIÓN]** tienen un valor por defecto; cámbialo si quieres otro.

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
construcción: impacto en COSTO (S/) y en PLAZO (días) de amenazas y oportunidades, con
percentiles P0–P100, reserva para contingencias al nivel de confianza elegido, curva S,
tornado, rangos por riesgo, matriz probabilidad-impacto y comparación antes/después de las
respuestas.

ARCHIVOS DE ENTRADA (adjuntos)
- Ejemplo.xlsm        -> base de riesgos del proyecto (hoja PARAMETROS, tabla tblRiesgos).
- plantilla_ppt.pptx  -> paleta de colores (lámina única "BLOOMBERG — Paleta de colores oficial").
- MD.zip              -> 10 archivos .md con la base metodológica (lista en la sección 0.3).
Si falta alguno, detente y pídemelo. No inventes riesgos, valores, colores ni método.

======================================================================
0. DATOS YA EXTRAÍDOS DE LOS ADJUNTOS (verifícalos, no los reinterpretes)
======================================================================
0.1 BASE DE RIESGOS (Ejemplo.xlsm, hoja PARAMETROS, tblRiesgos B11:N61)
- Filas 12–16: 5 riesgos DEMOSTRATIVOS completamente cuantificados (los de la versión anterior):
    1 Ingeniería en desarrollo (90 entregables) | SI | 1    | —      |       |       |        | TRIANGULAR | 7  | 14 | 28
    2 Alza de precios de materiales            | SI | 1    | NORMAL | 50000 | 25000 |        | —          |    |    |
    3 Condiciones geotécnicas imprevistas      | SI | 0.35 | PERT   | 30000 | 80000 | 200000 | PERT       | 10 | 25 | 60
    4 Huelga o paralización                    | SI | 0.20 | —      |       |       |        | TRIANGULAR | 5  | 15 | 45
    5 Demora en permisos y aprobaciones        | SI | 1    | —      |       |       |        | UNIFORME   | 10 | 40 |
- Filas 17–48: 32 riesgos REALES del proyecto (lista literal en el ANEXO A). SOLO traen el texto
  del riesgo en la columna NOMBRE; NO traen probabilidad, distribución ni parámetros.
- Costo base, plazo base y semilla están vacíos; iteraciones = 100000.
- El archivo NO trae más columnas, comentarios, filas ni columnas ocultas.

[DECISIÓN D1 – por defecto]: cargar los 37 riesgos así:
  * Los 32 reales con ACTIVO = "NO" y ESTADO = "PENDIENTE DE CUANTIFICAR". Nunca inventes su
    probabilidad, distribución ni parámetros: los completa el usuario.
  * Los 5 demostrativos con ACTIVO = "SI", ESTADO = "EJEMPLO" y NOTAS que empiecen con
    "EJEMPLO – desactivar al cargar datos reales", para que la herramienta se pueda probar de
    inmediato. Sus ID serán EJ-1 … EJ-5; los reales R-01 … R-32 en el orden del ANEXO A.
  * ValidarParametros NO debe dar error por filas con ACTIVO = "NO" sin cuantificar; sí debe
    avisar (advertencia, no error) cuántos riesgos siguen PENDIENTES.
- Normalización (sin cambiar el sentido del texto): recortar espacios, unir espacios dobles.
  Si el texto contiene " - Debido a" (15 de los 32), copia la parte posterior a "Debido a" en la
  columna CAUSA y deja el texto completo en NOMBRE DEL RIESGO.
- NO copies el código VBA de Ejemplo.xlsm ni su proyecto VBA (está marcado como "bloqueado para
  visualización", ver R10); solo los datos.
- Entrega una TABLA DE MAPEO (columna origen -> destino -> transformación) y el conteo
  leídos vs. cargados (37 = 37).

0.2 PALETA DE COLORES (plantilla_ppt.pptx: paleta Bloomberg)
Colores de la lámina (HEX · nombre en la lámina · uso indicado):
  #000000 Negro Bloomberg (fondo principal) · #FFFFFF Blanco · #FFA028 Sunshade Amber (acento de
  marca) · #FF6600 Bloomberg Orange · #FB8B1E Amber Cálido (gráficas) · #FFB020 Amber Medio
  (KPI) · #D4890A Amber Oscuro · #CC7A00 Amber Profundo · #0D0D0D / #1A1A1A / #2A2A2A paneles ·
  #333333 Separador (bordes, divisores) · #00C805 Verde Up (positivo) · #4AF6C3 Teal Datos ·
  #FF433D Rojo Down (negativo, riesgo, alerta) · #0068FF Azul Links · #A0A0A0 Gris Texto.
Asignación OBLIGATORIA en Excel (contraste medido según WCAG; mínimo 4.5:1):
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
  Bordes finos                     #333333 (líneas)                  3355443
  Serie COSTO (líneas y barras)    #FF6600                           26367
  Serie PLAZO (líneas y barras)    #0068FF                           16738304
  Línea de referencia P50          #333333 punteada
  Línea de referencia P80/nivel    #FF433D punteada
  Tornado: 10% inferior / superior #00C805 / #FF433D
  Botones                          #000000    #FFA028    10.3:1
  (*) Derivado = tinte claro de un color de la paleta (Amber o Gris) para fondos de celda;
      la paleta no trae neutros claros. Repórtalo así en el informe.
Combinaciones PROHIBIDAS por contraste insuficiente: texto blanco sobre #FF433D (3.4:1) o sobre
#FF6600 (2.9:1); texto #A0A0A0 (2.6:1), #CC7A00 (3.3:1) o #D4890A (2.8:1) sobre blanco.
Esta paleta reemplaza TODOS los colores anteriores: no debe quedar RGB(15,110,86), #0F6E56,
5664271 ni ningún verde/azul de la versión 1.

0.3 METODOLOGÍA (MD.zip): fuentes y requisitos que DEBES implementar
Fuentes (10 .md). Úsalas y cita la sección en la trazabilidad:
  [PMI-E]  thestandardforriskmgmt-spa (El Estándar para la Gestión de Riesgos en Portafolios,
           Programas y Proyectos, PMI, en español)
  [PMI-G]  riskmanagementpracticeguide (Risk Management in Portfolios, Programs and Projects:
           A Practice Guide, PMI)
  [VOSE]   risk-analysis-a-quantitative-guide (D. Vose, 3.ª ed.)
  [KROESE-H] handbook-of-monte-carlo-methods (Kroese, Taimre, Botev)
  [KROESE-S] simulation-and-the-monte-carlo-method-solutions-manual (Kroese, Taimre, ...)
  [STEVENS] monte-carlo-simulation-an-introduction-for-engineers-and-scientists
  [GLASS]  Monte Carlo Methods in Financial Engineering (Glasserman)
  [RC]     monte-carlo-statistical-methods (Robert y Casella)
  [AU]     engineering-risk-assessment-with-subset-simulation (Au y Wang)
  [LK]     Simulation Modelling and Analysis (Law y Kelton): el .md SOLO contiene enlaces a
           imágenes, sin texto extraíble. Regístralo como "Sin contenido utilizable".
Requisitos (implementa TODOS; cada uno va a la matriz de trazabilidad con su ID):
  M1  Definiciones [PMI-E 2.1, Glosario]: riesgo = evento o condición incierta con efecto
      positivo (OPORTUNIDAD) o negativo (AMENAZA); riesgo individual vs. riesgo general;
      reserva para contingencias = tiempo o dinero en la línea base para riesgos CONOCIDOS;
      reserva de gestión = adicional a la línea base para trabajo NO previsto; riesgo residual y
      secundario. Van en la sección METODOLOGÍA de INICIO y en el glosario.
  M2  Registro de riesgos [VOSE 1.6; PMI-E 4.3]: además de las columnas de cálculo, tblRiesgos
      incluye TIPO (AMENAZA/OPORTUNIDAD), CATEGORIA, CAUSA, DUENO DEL RIESGO, ESTRATEGIA DE
      RESPUESTA, ESTADO. Listas de ESTRATEGIA según PMI-E: amenazas = ESCALAR, EVITAR,
      TRANSFERIR, MITIGAR, ACEPTAR; oportunidades = ESCALAR, EXPLOTAR, COMPARTIR, MEJORAR,
      ACEPTAR.
  M3  Evento de riesgo = Bernoulli(p) × impacto [VOSE 1.x y 5.3.7]: el riesgo j es UNA sola
      variable (ocurrencia + impacto) en el análisis de sensibilidad (no se separan), tal como
      hace el tornado actual con c(:,j).
  M4  Oportunidades [PMI-E 2.1.2; VOSE 1.x]: si TIPO = OPORTUNIDAD, el usuario ingresa
      parámetros POSITIVOS y el modelo aplica signo negativo al impacto (reduce costo/plazo).
  M5  Probabilidad > 50 % [VOSE 1.x]: ADVERTENCIA (no error) "considere incluirlo en la línea
      base y modelar como oportunidad que no ocurra".
  M6  Valor monetario esperado [PMI-E X6.4.4]: VME_j = Prob_j × media del impacto dado que
      ocurre. Columna calculada por la macro en RANGOS y total VME en RESULTADOS; comprobar
      que la suma de VME ≈ media simulada del impacto (diferencia < 2 %) y mostrarlo.
  M7  Reserva para contingencias [PMI-E Glosario, X6.4.1; VOSE 19.1]: nombre definido
      NivelConfianza (por defecto 0,80; lista 0,50–0,95). Mostrar:
        a) Reserva para contingencias = P(NivelConfianza) del impacto simulado
           (= costo total al nivel − costo base).
        b) Variante Vose: presupuesto al valor esperado + (P(nivel) − media).
        c) Reserva de gestión = % ingresado por el usuario (nombre ReservaGestionPct, por
           defecto 0 %) × costo base. No se simula y se muestra aparte.
        d) Presupuesto recomendado = costo base + a) + c). Lo mismo para plazo.
      Mantener también la tabla P50/P80/P90.
  M8  Correlación entre riesgos [PMI-E 4.5 "interrelaciones"; VOSE cap. 13]: columnas
      GRUPO_CORRELACION (texto; vacío = independiente) y RHO_GRUPO (0 a 0,95, correlación de
      rango objetivo dentro del grupo). Implementar Iman–Conover: por grupo, puntajes normales
      S_ij = sqrt(rho)·W_i + sqrt(1−rho)·E_ij, y reordenar las muestras simuladas del riesgo j
      según el rango de S(:,j). Se reordena el PAR (costo, plazo) del mismo evento para no
      romper su vínculo. Con un factor por grupo la matriz es siempre semidefinida positiva:
      no se necesita Cholesky. Reportar la correlación de rango lograda vs. objetivo.
  M9  Generador de números aleatorios [KROESE-H cap. 1]: NO usar Rnd() de VBA (su período es
      de ~16,7 millones de números, insuficiente para 100 000 iteraciones × decenas de riesgos
      × varios números por muestra). Implementar MRG32k3a de L'Ecuyer en VBA con aritmética
      Double (exacta hasta 2^53), semilla reproducible desde el nombre Semilla y semilla
      aleatoria con Timer si está vacío. Validar contra los primeros valores publicados de
      MRG32k3a con semilla por defecto (12345 × 6).
  M10 Precisión de la simulación [VOSE cap. 7; STEVENS cap. 2; KROESE-H "Statistical analysis
      of simulation data"]: el error baja con 1/sqrt(N). En RESULTADOS, sección "Precisión":
      error estándar e IC 95 % de la media; IC 95 % del percentil del nivel elegido por
      estadísticos de orden (rangos N·p ± 1,96·sqrt(N·p·(1−p))); iteraciones sugeridas para un
      error relativo de 1 % en el percentil del nivel elegido. Advertencia si el IC supera ±1 %.
  M11 Sensibilidad [VOSE 5.3.7]: tornado por correlación de rango de Spearman + contribución a
      la varianza (rho²/Σrho²) + swing (media del total con el riesgo en su 10 % superior −
      en su 10 % inferior). Se mantiene lo de la versión 1.
  M12 Antes/después de la respuesta [PMI-E 4.6 y Glosario "riesgo residual"; VOSE 1.3–1.4]:
      columnas PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL (0–1, multiplica el impacto) y
      COSTO_RESPUESTA (S/, determinístico, se suma al escenario "después"). Vacías = igual al
      "antes" y costo 0. La macro simula ambos escenarios con la MISMA semilla y crea la hoja
      COMPARACION: tabla P10/P50/P80/P90/media antes vs. después, diferencia, beneficio neto
      = reducción de la reserva − costo de respuestas, y curvas S superpuestas.
  M13 Matriz probabilidad–impacto 5×5 [PMI-E X6.3.5 y X6.4.3; VOSE tabla 1.1]: umbrales
      editables en PARAMETROS (tabla tblEscalas: nivel 1–5, prob. máxima, impacto costo máx.,
      impacto plazo máx.; valores iniciales con razón ~3 entre niveles, como recomienda VOSE).
      Hoja MATRIZ_PI con conteo e ID de riesgos por celda, calculada con la probabilidad y el
      impacto medio condicionado de cada riesgo; colores de la paleta (verde, ámbar, rojo).
  M14 Agregación del plazo [VOSE 19.2]: se SUMAN los impactos en días (supuesto conservador:
      todos sobre la ruta crítica). Documentarlo en INICIO como limitación, porque no se modela
      la lógica de red del cronograma.
  M15 Técnicas evaluadas y NO implementadas (registrarlas como "No aplica" con su motivo):
      muestreo por hipercubo latino [VOSE 4.4.3: poca mejora con muchas distribuciones; exige
      inversas de la CDF incompatibles con Gamma por rechazo]; Subset Simulation [AU: eventos
      raros de falla, no es el caso]; MCMC [RC]; reducción de varianza financiera [GLASS];
      asignación de contingencia por partida [VOSE 19.1: aplica a partidas de costo, no a
      eventos]; [LK] sin texto.
Reglas de prioridad: en lo METODOLÓGICO prevalecen los .md sobre este prompt; en lo TÉCNICO
(reglas R1–R14, estructura, compatibilidad) prevalece este prompt. Si encuentras en los .md un
requisito aplicable que no esté en M1–M15, impleméntalo y agrégalo a la trazabilidad.
Entrega Trazabilidad_Metodologia.md con: ID | fuente y sección | requisito | implementación
(hoja / columna / procedimiento VBA) | estado (Implementado / Parcial / No aplica + motivo).

======================================================================
1. ESTRUCTURA DEL LIBRO (nombres de hoja EXACTOS)
======================================================================
Hojas en este orden: INICIO, PARAMETROS, RESULTADOS, CURVA_S, TORNADO, RANGOS, MATRIZ_PI,
COMPARACION, SIMULACION.
- Nombres de hoja en MAYÚSCULAS, sin tildes, eñes, espacios ni emojis.
- CodeName en español (asígnalos al crear el vbaProject): hjInicio, hjParametros,
  hjResultados, hjCurvaS, hjTornado, hjRangos, hjMatriz, hjComparacion, hjSimulacion. El VBA
  referencia las hojas SIEMPRE por CodeName.
- Todas las hojas: cuadrícula oculta, banda de título negra con texto ámbar, fuente Calibri.

INICIO: título; descripción de cada hoja; pasos de uso (1–7, incluido "completar los riesgos
PENDIENTES y desactivar los EJEMPLO"); guía de distribuciones; sección METODOLOGÍA (M1–M15 en
lenguaje claro); glosario (M1); limitaciones (M14, independencia salvo grupos M8, negativos de
NORMAL = oportunidades, no se truncan).

PARAMETROS
- Configuración (nombres definidos; el VBA lee SIEMPRE por nombre, nunca por dirección):
    CostoBase (S/, opcional) · PlazoBase (días, opcional) · Iteraciones (entero 1 000–100 000,
    valor inicial 10 000) · Semilla (vacío = aleatoria) · NivelConfianza (0,80) ·
    ReservaGestionPct (0 %).
- tblEscalas (M13) al lado de la configuración.
- tblRiesgos (ListObject), encabezado en la fila de tu diseño, con columnas:
    ID | NOMBRE DEL RIESGO | TIPO | CATEGORIA | CAUSA | DUENO DEL RIESGO | ESTADO | ACTIVO |
    PROBABILIDAD | DIST_COSTO | C_P1 | C_P2 | C_P3 | DIST_PLAZO | T_P1 | T_P2 | T_P3 |
    GRUPO_CORRELACION | RHO_GRUPO | ESTRATEGIA | PROB_RESIDUAL | FACTOR_IMPACTO_RESIDUAL |
    COSTO_RESPUESTA | NOTAS
  * El VBA ubica cada columna por el TEXTO DEL ENCABEZADO (ListColumns("PROBABILIDAD").Index),
    nunca por posición. Si falta una columna obligatoria, lo indica en el mensaje de error.
  * Listas: TIPO (AMENAZA, OPORTUNIDAD); ACTIVO (SI, NO); ESTADO (EJEMPLO, PENDIENTE DE
    CUANTIFICAR, CUANTIFICADO, CERRADO); DIST_* (TRIANGULAR, PERT, NORMAL, UNIFORME,
    LOGNORMAL, EXPONENCIAL, WEIBULL); ESTRATEGIA (M2).
  * NOMBRE DEL RIESGO con ajuste de texto y ancho ~60; filas con alto automático.
- Guía de parámetros por distribución (igual que v1).
- Tres BOTONES como FORMAS (rectángulo redondeado, fondo #000000, texto #FFA028 en negrita)
  con OnAction (macro="[0]!Macro" en el drawing, o Workbook_Open que las cree si no existen).
  Los controles de formulario no admiten color, por eso se usan formas:
    "▶ CORRER SIMULACIÓN"  -> EjecutarSimulacion
    "✔ VALIDAR DATOS"      -> ValidarDatos (Sub que llama a la función ValidarParametros)
    "✖ LIMPIAR RESULTADOS" -> LimpiarResultados
  Si las creas desde VBA, los símbolos y tildes se construyen con ChrW (▶ = ChrW(9654),
  ✔ = ChrW(10004), ✖ = ChrW(10006)).
Hojas de salida: NO se borran ni se recrean; solo se limpian (Cells.Clear y ChartObjects) y se
vuelven a escribir.

======================================================================
2. REGLAS OBLIGATORIAS DEL CÓDIGO VBA
======================================================================
R1. CÓDIGO FUENTE 100 % ASCII (comentarios incluidos). El proyecto usa la página de códigos
    1252. Texto con tildes desde VBA: función U("Simulaci\u00F3n") que convierte \uXXXX con
    ChrW, o ChrW directo.
R2. Option Explicit en todos los módulos; todas las variables declaradas.
R3. Type, Const y variables de módulo ARRIBA, antes del primer Sub/Function.
R4. Toda variable que reciba Array(...) se declara As Variant.
R5. Long (no Integer) para filas, contadores e índices.
R6. On Error GoTo en EjecutarSimulacion; en la salida normal y en el manejador restaurar
    ScreenUpdating, Calculation, EnableEvents y StatusBar; MsgBox en español con número,
    descripción, etapa y riesgo/fila.
R7. Muestras en arrays y volcado con UNA asignación Range.Value = array. Tiempo objetivo:
    10 000 iteraciones × 20 riesgos activos < 10 s, sin contar el escenario "después"; reporta
    el tiempo real.
R8. Sin referencias externas, ActiveX ni Analysis ToolPak. Evita constantes mso* (usa el valor
    numérico con comentario, p.ej. 4 'msoLineDash). Debe compilar sin errores con
    Depuración > Compilar VBAProject.
R9. 32 y 64 bits (sin Declare; si fuera imprescindible, PtrSafe).
R10. MACRO ABIERTA, SIN CLAVE NI PROTECCIÓN:
    - Proyecto VBA sin contraseña y SIN "Bloquear proyecto para visualización": con Alt+F11
      se deben ver y editar todos los módulos.
    - CMG, DPB y GC del stream PROJECT se CIFRAN con la clave derivada del ID del proyecto
      (MS-OVBA 2.4.3: clave = suma de los bytes del texto de ID mod 256). NUNCA copies
      CMG/DPB/GC de otro proyecto: si la clave no coincide con el ID, Excel toma el proyecto
      como protegido y al guardar lo marca "bloqueado para visualización". Esto ya ocurrió
      con Ejemplo.xlsm (su GC descifra a 00 = bloqueado; CMG = 05).
    - Valores descifrados obligatorios: CMG = 00000000 (sin protección), DPB = 00 (sin
      contraseña), GC = FF (visible).
    - Sin protección de hojas, libro ni estructura; sin hojas ocultas ni xlVeryHidden.
R11. TODO EN ESPAÑOL: celdas, encabezados, títulos, ejes, leyendas, botones, MsgBox, InputBox,
    StatusBar, validaciones, nombres definidos, nombres de macros, procedimientos, variables y
    constantes (sin tildes ni ñ: "Dueno", "Anio"), comentarios y propiedades del archivo
    (título, asunto, idioma es-PE). Excepción técnica: fórmulas desde VBA con .Formula
    (inglés; no .FormulaLocal) y NumberFormat con códigos ingleses ("#,##0", "0.0%").
    Fechas "dd/mm/yyyy hh:mm" (en VBA usa "mm" para minutos tras "hh").
R12. tblRiesgos y tblEscalas se leen por nombre de encabezado.
R13. Colores centralizados: una Const Long por rol de la tabla 0.2 (p.ej.
    Private Const COLOR_ENCABEZADO As Long = 0 ' #000000 encabezado). Sin RGB() en Const y
    sin colores sueltos en el código.
R14. Macros públicas: EjecutarSimulacion, ValidarDatos, ValidarParametros (Function As
    Boolean), LimpiarResultados. Ninguna otra Sub pública sin argumentos, para que no
    aparezcan en la lista de macros.

======================================================================
3. LÓGICA DE LA SIMULACIÓN
======================================================================
- ValidarParametros(): restablece primero el color de entrada; valida SOLO filas ACTIVO = SI.
  Errores: nombre vacío; probabilidad fuera de 0–1; ninguna distribución; parámetros no
  numéricos; TRIANGULAR/PERT Mín ≤ Moda ≤ Máx; UNIFORME Mín ≤ Máx; NORMAL/LOGNORMAL
  Desv.Est. > 0; LOGNORMAL y EXPONENCIAL media > 0; WEIBULL forma y escala > 0; RHO_GRUPO en
  0–0,95; PROB_RESIDUAL en 0–1; FACTOR_IMPACTO_RESIDUAL en 0–1; COSTO_RESPUESTA ≥ 0;
  NivelConfianza en 0,50–0,95; iteraciones 1 000–100 000; tblEscalas creciente.
  Advertencias (no detienen): probabilidad > 0,5 (M5); riesgos PENDIENTES (D1); ESTADO =
  EJEMPLO activos. Mín = Moda = Máx se acepta como valor constante.
- EjecutarSimulacion(): validar -> leer por encabezados -> semilla MRG32k3a (M9) -> para cada
  iteración i y riesgo activo j: ocurre = U < p_j; si ocurre, c_ij y t_ij de sus
  distribuciones (0 si no hay); signo negativo si OPORTUNIDAD (M4) -> correlación Iman–Conover
  por grupo (M8) -> totales por iteración -> escenario "después" con la misma semilla (M12) ->
  ordenar y calcular percentiles (interpolación lineal, igual que PERCENTIL.INC) -> escribir
  hojas y gráficos -> MsgBox final (iteraciones, riesgos activos, pendientes, tiempo, P50 y
  P(nivel) de costo y plazo, reserva recomendada) -> activar RESULTADOS.
- Generadores (con el MRG32k3a, sin WorksheetFunction en el bucle): TRIANGULAR (inversa de la
  CDF; Máx = Mín -> Mín); PERT (Beta-PERT λ=4: alfa = 1 + 4(Moda−Mín)/(Máx−Mín), beta =
  1 + 4(Máx−Moda)/(Máx−Mín), Beta = X/(X+Y) con Gamma de Marsaglia–Tsang; Máx = Mín -> Mín);
  NORMAL (Box–Muller); UNIFORME; LOGNORMAL (media y desv. de la variable); EXPONENCIAL
  (P1 = media); WEIBULL (forma, escala).
- LimpiarResultados(): pide confirmación, limpia las hojas de salida y restablece colores.

======================================================================
4. HOJAS DE SALIDA
======================================================================
RESULTADOS: encabezado (fecha, iteraciones, semilla, activos, pendientes, nivel de confianza);
percentiles P0, P5, P10, P20…P90, P95, P100 de impacto costo y plazo (y totales con base);
estadísticas (media, desv. est., CV, mín., máx., prob. de impacto 0); VME total vs. media (M6);
RESERVAS (M7 a–d); PRECISIÓN (M10); resaltados P10/P50/P80/P90 con la paleta.
CURVA_S: tabla 0–100 % cada 5 %; curvas S de costo y plazo (dispersión XY suavizada) con líneas
P50 y P(nivel); histogramas de 20 clases con su tabla.
TORNADO: dos tablas ordenadas (costo, plazo) con impacto medio, Spearman, contribución, swing,
Δ inferior/superior; dos gráficos de barras horizontales (mayor arriba) en verde/rojo de la
paleta; oportunidades identificadas.
RANGOS: una fila por riesgo y dimensión con TIPO, prob., frecuencia observada, mínimo, P10,
P25, P50, P75, P90, máximo, promedio, VME; filas TOTAL COSTO y TOTAL PLAZO.
MATRIZ_PI (M13) y COMPARACION (M12).
SIMULACION: primeras min(N, 5 000) iteraciones (ITER, totales, columnas por riesgo) en un solo
bloque.
Formato: Calibri 10–11; colores SOLO de la tabla 0.2; bordes #333333 finos; "#,##0" para S/,
"#,##0.0" para días, "0.0%" para probabilidades; paneles inmovilizados; nada protegido.

======================================================================
5. ENTREGA Y AUTOVERIFICACIÓN (obligatorio antes de entregar)
======================================================================
Entrega: a) MonteCarlo_Riesgos.xlsm; b) MonteCarlo.bas (+ ThisWorkbook.cls si tiene código);
c) Trazabilidad_Metodologia.md; d) informe breve con tabla de mapeo (0.1), tabla de paleta
aplicada (0.2) y lista de verificación.
Si generas el archivo sin Excel (Python), recuerda que openpyxl/XlsxWriter no compilan VBA:
escribe el vbaProject.bin conforme a MS-OVBA (solo código fuente, sin p-code: _VBA_PROJECT
versión 0xFFFF y MODULEOFFSET = 0), con CMG/DPB/GC cifrados con la clave del ID (R10); o usa
Excel vía COM (VBProject.VBComponents.Import y FileFormat = 52).

Comprobaciones (reporta cada resultado):
  [ ] olevba extrae todos los módulos y el texto coincide byte a byte con el .bas.
  [ ] 0 bytes > 127 en el código; Type/Const antes del primer procedimiento; sin variables sin
      declarar; ningún Array() en un arreglo tipado (verificador estático probado con errores
      sembrados).
  [ ] R10: CMG/DPB/GC descifrados = 00000000 / 00 / FF y clave = clave del ID; sin protección
      de hojas ni libro; sin hojas ocultas.
  [ ] R11: ningún texto visible, mensaje, título de gráfico, botón o nombre de macro en inglés
      (lista de todas las cadenas del código revisada).
  [ ] Nombres definidos y tablas tblRiesgos / tblEscalas existen; lectura por encabezado
      probada moviendo una columna de lugar.
  [ ] tblRiesgos tiene 37 filas: 5 EJEMPLO activas + 32 PENDIENTES inactivas; 3 filas
      comparadas origen vs. destino; CAUSA extraída en las 15 filas con "Debido a".
  [ ] Colores = tabla 0.2 (búsqueda de 5664271 / 15,110,86 / 0F6E56 sin resultados).
  [ ] Cada M1–M15 figura en la trazabilidad con estado.
  [ ] Botones (formas) con OnAction a macros existentes.
  [ ] MRG32k3a reproduce los valores de referencia publicados; misma semilla = mismos
      resultados.
  [ ] Con los 5 EJEMPLO, semilla 12345, N = 10 000 e independencia: P50 y P80 de costo y
      plazo dentro de ±3 % de numpy con la misma lógica. Valores de referencia (numpy,
      N = 1 000 000): costo P50 ≈ 67 400, P80 ≈ 133 000, P90 ≈ 163 900; plazo P50 ≈ 52,3,
      P80 ≈ 73,1, P90 ≈ 83,4 días. La versión 1, ejecutada en Excel con N = 100 000, dio
      67 790 / 133 436 y 52,4 / 73,1.
  [ ] Correlación: grupo de 2 riesgos con rho = 0,6 -> correlación de rango lograda 0,6 ± 0,05.
  [ ] Oportunidad: un riesgo OPORTUNIDAD reduce la media en prob × impacto medio (± 2 %).
  [ ] Escenario "después": con PROB_RESIDUAL = 0 en todos, el P80 "después" = suma de
      COSTO_RESPUESTA.
  [ ] VME total ≈ media simulada (± 2 %).
  [ ] Casos borde sin error: Mín = Máx, fila inactiva, fila vacía, probabilidad 0 y 1, columna
      reordenada, tabla solo con PENDIENTES (mensaje claro: "no hay riesgos activos").
Si algo falla, corrígelo antes de entregar. No entregues un archivo sin verificar.

ANEXO A – 32 RIESGOS REALES (Ejemplo.xlsm, filas 17–48; texto literal, espacios normalizados)
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
TIPO de R-01…R-32: AMENAZA por defecto, con ESTADO = PENDIENTE DE CUANTIFICAR. [DECISIÓN D2]
R-17…R-20 ("Mayor costo - Reconocimiento de …") pueden ser OPORTUNIDADES si significan que el
cliente reconoce el mayor costo. Márcalas AMENAZA con NOTAS = "Confirmar si es oportunidad"
salvo que el usuario indique otra cosa.
```

---

## Qué cambió respecto de la versión 1

| Criterio pedido | Cómo quedó en el prompt |
|---|---|
| Base de riesgos de `Ejemplo.xlsm` | 32 riesgos reales listados literalmente (Anexo A). Llegan sin cuantificar, así que se cargan como PENDIENTES sin inventar valores. Los 5 de ejemplo quedan activos y marcados EJEMPLO (D1). |
| Paleta de `plantilla_ppt` | Paleta Bloomberg con un rol para cada color y el contraste medido. Se prohíben las combinaciones que no llegan a 4.5:1. |
| Macro abierta sin clave | R10 corrige la causa real de que no pudieras ver la macro: CMG/DPB/GC estaban cifrados con la clave de otro proyecto. Se exige comprobar los valores descifrados. |
| Todo en español | R11 cubre hojas, CodeNames, macros, variables, gráficos, mensajes y propiedades del archivo. |
| Método según los `.md` | M1–M15, cada uno con su fuente (PMI, Vose, Kroese, Stevens…). Los que no aplican quedan registrados con su motivo. |
