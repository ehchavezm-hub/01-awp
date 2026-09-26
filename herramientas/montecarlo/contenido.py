"""Textos del libro: catálogo de distribuciones, INICIO, GUIA y TEORIA."""

# ---------------------------------------------------------------------------
# Catálogo (tblDistribuciones): nombre, P1, P2, P3, P4, cuándo usar, ejemplo de obra
# ---------------------------------------------------------------------------
CATALOGO = [
    ("CONSTANTE", "Valor", "", "", "",
     "El impacto se conoce con certeza si el riesgo ocurre.",
     "Multa fija de S/ 250 000 si se incumple un hito."),
    ("UNIFORME", "Mínimo", "Máximo", "", "",
     "Solo se conoce un rango; ningún valor es más probable que otro.",
     "Demora de 10 a 40 días en un permiso municipal, sin valor típico."),
    ("TRIANGULAR", "Mínimo", "Moda (más probable)", "Máximo", "",
     "Se conocen mínimo, más probable y máximo; da bastante peso a los extremos.",
     "Retraso en aprobación de submittals: 10 / 20 / 45 días."),
    ("TRIGEN", "Valor bajo", "Moda", "Valor alto", "% bajo (ej. 10)",
     "El experto da valores que «rara vez» se superan (P10 / P90) en vez de extremos absolutos.",
     "«Rara vez menos de 5 días, lo normal 12, rara vez más de 30» → 5 / 12 / 30 / 10."),
    ("PERT", "Mínimo", "Moda (más probable)", "Máximo", "",
     "Recomendada para tres puntos: más peso en la moda que la triangular (Beta-PERT, λ = 4).",
     "Sobrecosto por reprocesos: 0,8 / 2,5 / 6,0 millones S/."),
    ("PERT_MODIFICADA", "Mínimo", "Moda", "Máximo", "Gamma (4 = PERT)",
     "Como PERT pero ajustando la confianza en la moda: gamma alto = más concentrada.",
     "Moda muy confiable: gamma = 8; poco confiable: gamma = 2."),
    ("BETA_GENERAL", "Alfa", "Beta", "Mínimo", "Máximo",
     "Forma flexible entre un mínimo y un máximo cuando se ajusta a datos históricos.",
     "Porcentaje de desperdicio de concreto ajustado a obras anteriores."),
    ("NORMAL", "Media", "Desviación estándar", "", "",
     "Variación simétrica alrededor de un promedio; puede dar valores negativos (oportunidades).",
     "Variación de precios de acero: media 50 000, desviación 25 000."),
    ("NORMAL_TRUNCADA", "Media", "Desviación estándar", "Mínimo", "Máximo",
     "Normal pero limitada a un rango físico (sin negativos o con tope contractual).",
     "Ajuste de precios con tope contractual de ±5 %."),
    ("LOGNORMAL", "Media", "Desviación estándar", "", "",
     "Costos o duraciones sesgados a la derecha, nunca negativos, con cola larga.",
     "Costo de reparación de fisuras en viviendas vecinas."),
    ("GAMMA", "Forma", "Escala", "", "",
     "Sesgada a la derecha, positiva; media = forma × escala.",
     "Horas-hombre de rediseño cuando hay datos de proyectos similares."),
    ("EXPONENCIAL", "Media", "", "", "",
     "Tiempos entre eventos o impactos con muchos casos pequeños y pocos grandes. P1 es la MEDIA.",
     "Días de paralización por evento aleatorio, media 10 días."),
    ("WEIBULL", "Forma (k)", "Escala (λ)", "", "",
     "Tiempos de falla o duración de equipos; forma < 1 = fallas tempranas, > 1 = desgaste.",
     "Días fuera de servicio de una grúa torre."),
    ("GUMBEL", "Ubicación", "Escala", "", "",
     "Valores extremos (el máximo de muchos eventos): lluvias, crecidas, picos de demanda.",
     "Lluvia máxima anual que detiene trabajos de excavación."),
    ("LOGISTICA", "Media", "Escala", "", "",
     "Parecida a la normal pero con colas algo más pesadas.",
     "Variación de productividad diaria de una cuadrilla."),
    ("PARETO", "Forma (> 1)", "Mínimo", "", "",
     "Colas muy pesadas: pocos casos muy grandes (reclamos, siniestros). Forma > 1 para que exista la media.",
     "Monto de un reclamo de terceros: mínimo 100 000, forma 2,5."),
    ("POISSON", "Media (λ)", "", "", "",
     "Número de eventos en el periodo cuando pueden ocurrir varias veces.",
     "Número de no conformidades (NCR) al mes, media 3."),
    ("BINOMIAL", "n (ensayos)", "p (probabilidad)", "", "",
     "Número de «fallas» en n intentos independientes con probabilidad p.",
     "Cuántos de 40 submittals serán rechazados si p = 0,15."),
    ("DISCRETA_UNIFORME", "Mínimo (entero)", "Máximo (entero)", "", "",
     "Un entero entre mínimo y máximo, todos igual de probables.",
     "Número de grúas indisponibles: 0 a 2."),
    ("DISCRETA", "Valores «v1;v2;…»", "Probabilidades «p1;p2;…»", "", "",
     "Pocos escenarios con probabilidad conocida. Las probabilidades deben sumar 1.",
     "Penalidad: «0;150000;400000» con «0,6;0,3;0,1»."),
]

LISTA_MENU = ["(vacío)"] + [c[0] for c in CATALOGO]


def ayuda(c):
    partes = ["P%d=%s" % (k + 1, c[k + 1]) for k in range(4) if c[k + 1]]
    return " · ".join(partes)


# ---------------------------------------------------------------------------
# INICIO
# ---------------------------------------------------------------------------
HOJAS = [
    ("INICIO", "Esta hoja: propósito, pasos de uso, resumen del método y limitaciones."),
    ("GUIA", "Guía práctica de distribuciones para no especialistas y catálogo de las 20 disponibles (fuente de los menús)."),
    ("PARAMETROS", "Configuración, dimensiones de impacto (tblDimensiones), escalas de la matriz (tblEscalas), "
                   "registro de riesgos (tblRiesgos) y botones. Celdas ámbar claro = editables."),
    ("RESULTADOS", "Resumen por dimensión, percentiles P0–P100, estadísticas, VME, reservas (contingencia y gestión), "
                   "precisión de la simulación, correlación lograda y advertencias."),
    ("CURVA_S", "Curva S (probabilidad acumulada) con marcas P50 y del nivel elegido, e histograma de cada dimensión."),
    ("TORNADO", "Sensibilidad: Spearman, contribución a la varianza y swing de cada riesgo, por dimensión."),
    ("RANGOS", "Mínimo, P10, P25, P50, P75, P90, máximo, promedio y VME de cada riesgo y de los totales."),
    ("MATRIZ_PI", "Matriz probabilidad–impacto 5×5 general y por dimensión, con la clasificación de cada riesgo."),
    ("COMPARACION", "Antes vs. después de las respuestas (PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL, COSTO_RESPUESTA)."),
    ("SIMULACION", "Datos de las primeras 5 000 iteraciones (totales y cada riesgo)."),
    ("TEORIA", "Toda la teoría usada para construir la herramienta, con su bibliografía."),
]

PASOS = [
    "Pulse «Habilitar contenido». Si Windows bloquea las macros de un archivo descargado: clic derecho en el archivo › "
    "Propiedades › marque «Desbloquear». La macro está abierta: con Alt+F11 puede ver y editar el código.",
    "En PARAMETROS reemplace el costo base (S/ 200 M) y el plazo base (730 días) SUPUESTOS por los valores del contrato; "
    "revise iteraciones, semilla, nivel de confianza y % de reserva de gestión.",
    "Valide con cada dueño de riesgo las ESTIMACIONES PRELIMINARES de R-01…R-32 (ESTADO = «ESTIMADO – VALIDAR») y cambie "
    "el ESTADO a «CUANTIFICADO». Los riesgos EJEMPLO están inactivos (ACTIVO = NO).",
    "Para cada riesgo elija la distribución de cada dimensión con la hoja GUIA; la columna AYUDA_ indica qué va en P1…P4. "
    "Deje vacía la distribución de las dimensiones que el riesgo no afecta.",
    "Opcional: registre la respuesta (ESTRATEGIA, PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL, COSTO_RESPUESTA) y los grupos de "
    "correlación (GRUPO_CORRELACION, RHO_GRUPO).",
    "Pulse «✔ VALIDAR DATOS» (errores en rojo, advertencias en ámbar) y luego «▶ CORRER SIMULACIÓN».",
    "Lea RESULTADOS (reserva recomendada al nivel de confianza), CURVA_S, TORNADO, MATRIZ_PI y COMPARACION.",
    "Para analizar otra dimensión (calidad, SSOMA, etc.) pulse «＋ AGREGAR DIMENSIÓN»: se crean sus columnas sin tocar el código.",
]

METODO_RESUMEN = [
    ("Riesgo (M1)", "Evento o condición incierta que, si ocurre, afecta los objetivos: AMENAZA si los perjudica, "
                    "OPORTUNIDAD si los favorece (PMI)."),
    ("Evento de riesgo (M3)", "En cada iteración el riesgo ocurre con su PROBABILIDAD; si ocurre, se muestrea su impacto en "
                              "TODAS las dimensiones que afecta con el mismo evento (Vose)."),
    ("Oportunidades (M4)", "Se ingresan con parámetros positivos; el modelo les aplica signo negativo."),
    ("Dimensiones", "COSTO (S/), PLAZO (días), INGENIERÍA DE DISEÑO (HH), INGENIERÍA DE CAMPO (HH) y las que agregue el usuario. "
                    "Cada una se suma por separado."),
    ("Reservas (M7)", "Reserva para contingencias = percentil del nivel de confianza (80 % por defecto) del impacto de los "
                      "riesgos conocidos. Reserva de gestión = % de la base para trabajo no previsto (no se simula)."),
    ("Correlación (M8)", "Riesgos del mismo GRUPO_CORRELACION se mueven juntos (Iman–Conover con un factor común)."),
    ("Generador (M9)", "MRG32k3a de L'Ecuyer, período ≈ 3,1 × 10^57; misma semilla = mismos resultados."),
    ("Precisión (M10)", "Intervalos de confianza de la media y del percentil elegido; iteraciones sugeridas para ±1 %."),
    ("Sensibilidad (M11)", "Tornado por correlación de rangos (Spearman), contribución a la varianza y swing."),
    ("VME (M6)", "Valor monetario esperado = probabilidad × impacto medio; su suma se contrasta con la media simulada."),
    ("Matriz P-I (M13)", "5×5 con umbrales editables (razón ~3 entre niveles) en tblEscalas."),
    ("Antes/después (M12)", "Se simulan ambos escenarios con los mismos números aleatorios para medir el beneficio neto."),
]

LIMITACIONES = [
    "Los impactos de PLAZO se SUMAN: supuesto conservador de que todos los riesgos afectan la ruta crítica; no se modela "
    "la lógica de red del cronograma (Vose 19.2).",
    "Los riesgos son independientes salvo los que comparten GRUPO_CORRELACION. Con probabilidades < 1 hay muchos ceros "
    "(empates) y la correlación lograda es menor que la objetivo; RESULTADOS muestra ambas.",
    "NORMAL y LOGISTICA pueden dar valores negativos (oportunidades dentro del riesgo): no se truncan a 0. Use "
    "NORMAL_TRUNCADA si no deben existir negativos.",
    "Las dimensiones en HH no se convierten a soles; si ese costo ya está en COSTO_P*, no lo sume de nuevo (doble conteo).",
    "Las estimaciones de R-01…R-32 son PRELIMINARES (base supuesta S/ 200 M, 730 días) y deben validarse.",
    "Técnicas evaluadas y no aplicadas (hipercubo latino, Subset Simulation, MCMC, etc.): ver TEORIA, sección 12.",
]

# ---------------------------------------------------------------------------
# GUIA
# ---------------------------------------------------------------------------
GUIA_QUE_ES = [
    "Una distribución describe lo que NO sabemos con exactitud: qué valores son posibles y cuáles son más probables. "
    "En vez de decir «el sobrecosto será S/ 600 000», decimos «estará entre 200 000 y 1 400 000, lo más probable 600 000».",
    "En cada riesgo hay DOS preguntas distintas, y van en lugares distintos:",
    "   1) ¿Ocurre o no ocurre? → columna PROBABILIDAD (ej. 0,55 = 55 % de chance de que la Supervisión demore las aprobaciones).",
    "   2) Si ocurre, ¿cuánto cuesta o demora? → la DISTRIBUCIÓN de cada dimensión (ej. PLAZO TRIANGULAR 10 / 20 / 45 días).",
    "Ejemplo R-11 (demoras de aprobación de la Supervisión): PROBABILIDAD 0,55; COSTO PERT 200 000 / 600 000 / 1 400 000; "
    "PLAZO TRIANGULAR 10 / 20 / 45 días. En el 45 % de las iteraciones el riesgo no ocurre e impacta 0.",
]
GUIA_ARBOL = [
    ("Solo conozco un rango, sin valor más probable", "UNIFORME"),
    ("Conozco mínimo, más probable y máximo", "PERT (recomendada) o TRIANGULAR"),
    ("El experto dice «rara vez baja de X o pasa de Y»", "TRIGEN (P10 / moda / P90)"),
    ("Tengo promedio y dispersión simétrica (datos históricos)", "NORMAL (o NORMAL_TRUNCADA si hay límites)"),
    ("Costos o duraciones sesgados a la derecha, nunca negativos", "LOGNORMAL o GAMMA"),
    ("Cuento eventos (accidentes, NCR, RFI) en el periodo", "POISSON o BINOMIAL"),
    ("Pocos escenarios con probabilidad conocida", "DISCRETA"),
    ("El valor es seguro si el riesgo ocurre", "CONSTANTE"),
    ("Colas extremas (reclamos grandes, eventos raros)", "PARETO, GUMBEL o LOGNORMAL"),
]
GUIA_PREGUNTAS = [
    "1. «Si todo sale bien, ¿cuál es el MÍNIMO razonable del impacto?» (pregunte primero los extremos para evitar el anclaje).",
    "2. «Si todo sale mal, ¿cuál es el MÁXIMO razonable?» (sin catástrofes absurdas; si hay dudas, use TRIGEN con P10/P90).",
    "3. «¿Cuál es el valor MÁS PROBABLE?» (la moda, no el promedio). Luego pregunte la PROBABILIDAD de que el riesgo ocurra.",
    "Registre de dónde sale cada número (experto, histórico, cotización) en NOTAS. Fuente: Vose, cap. 14 (elicitación de expertos).",
]
GUIA_ERRORES = [
    "Meter la probabilidad dentro del impacto (ej. poner el 30 % del costo): la probabilidad va SOLO en PROBABILIDAD.",
    "Usar el peor caso como moda: la moda es el valor más frecuente, no el más temido.",
    "Mezclar unidades: soles vs. miles de soles, días hábiles vs. calendario, HH vs. días-hombre.",
    "Duplicar un impacto: poner las HH valorizadas en COSTO y además en ING_DISENO/ING_CAMPO.",
    "Mínimo > moda o moda > máximo (la validación lo marca en rojo).",
    "Poner probabilidad 1 a un evento que puede no ocurrir; o > 0,5 a algo casi seguro (mejor incluirlo en la línea base).",
]

# ---------------------------------------------------------------------------
# TEORIA: (titulo, [parrafos])
# ---------------------------------------------------------------------------
TEORIA = [
    ("1. Gestión de riesgos: definiciones y proceso", [
        "Riesgo: evento o condición incierta que, si se produce, tiene un efecto positivo o negativo en uno o más objetivos. "
        "Los riesgos negativos son AMENAZAS y los positivos OPORTUNIDADES. [PMI-E 1 y 2.1]",
        "Riesgo individual vs. riesgo general: el individual es cada evento del registro; el general es el efecto de toda la "
        "incertidumbre sobre el proyecto. El análisis cuantitativo estima el riesgo general. [PMI-E 2.1.1, 4.5.1]",
        "Reserva para contingencias: tiempo o dinero en la línea base para riesgos CONOCIDOS con respuesta activa. Reserva de "
        "gestión: tiempo o dinero adicional a la línea base para trabajo NO previsto dentro del alcance. [PMI-E Glosario]",
        "Riesgo residual: el que queda tras implementar la respuesta. Riesgo secundario: el que surge por la respuesta. [PMI-E Glosario]",
        "Proceso: planificar, identificar, análisis cualitativo, análisis cuantitativo, planificar e implementar respuestas, "
        "monitorear. Apetito al riesgo: grado de incertidumbre que la organización acepta; umbral: variación aceptable "
        "alrededor de un objetivo. [PMI-E 2.1.5, 2.1.6, 4]",
        "Estrategias de respuesta. Amenazas: escalar, evitar, transferir, mitigar, aceptar. Oportunidades: escalar, explotar, "
        "compartir, mejorar, aceptar. [PMI-E 4.6]",
        "Registro de riesgos: nombre, descripción, causa, impulsores, probabilidad e impacto, dueño, respuesta y estado. [Vose 1.6]",
    ]),
    ("2. Simulación Montecarlo", [
        "Se generan N escenarios (iteraciones). En cada uno se muestrean todas las variables inciertas y se calcula el resultado; "
        "el conjunto de resultados aproxima su distribución de probabilidad. [PMI-E X6.4.6; Vose 4.2.4; Stevens 1–2]",
        "Ley de los grandes números: el promedio de las iteraciones converge a la media verdadera. Teorema central del límite: "
        "el error de la media es aproximadamente normal con desviación σ/√N. [Kroese-H, apéndice; Stevens 2]",
        "Consecuencia práctica: para reducir el error a la décima parte hay que multiplicar las iteraciones por 100. [Stevens 2.4]",
        "Un percentil Pxx es el valor que no se supera en el xx % de las iteraciones: P80 = 80 % de confianza de no superarlo.",
    ]),
    ("3. Números aleatorios", [
        "Los generadores congruenciales producen una secuencia determinista que parece aleatoria; su calidad depende del período "
        "y de la uniformidad en varias dimensiones. [Kroese-H cap. 1]",
        "Rnd() de VBA es un congruencial de 24 bits: período ≈ 16,7 millones. Una simulación de 100 000 iteraciones × 37 riesgos × "
        "varios números por muestra supera ese período y repetiría la secuencia. Por eso NO se usa.",
        "Se usa MRG32k3a de L'Ecuyer (recomendado en Kroese-H 1.3): dos recurrencias de orden 3, "
        "x(n) = (1 403 580·x(n−2) − 810 728·x(n−3)) mod 4 294 967 087 y "
        "y(n) = (527 612·y(n−1) − 1 370 589·y(n−3)) mod 4 294 944 443; u(n) = ((x(n) − y(n)) mod m1) / (m1 + 1). "
        "Período ≈ 3,1 × 10^57. Todas las operaciones son exactas en Double (< 2^53).",
        "Semilla: con un número en Semilla la simulación es reproducible; vacía, se toma del reloj.",
    ]),
    ("4. Generación de variables aleatorias y catálogo", [
        "Transformada inversa: si U ~ Uniforme(0,1), X = F⁻¹(U) tiene distribución F (triangular, uniforme, exponencial, "
        "Weibull, Gumbel, logística, Pareto, normal truncada, discretas). [Kroese-H cap. 3]",
        "Aceptación-rechazo: se proponen valores y se aceptan con cierta probabilidad (Gamma de Marsaglia–Tsang). [Kroese-H cap. 3]",
        "Normal: Box–Muller, Z = √(−2 ln U1)·cos(2π U2). Φ⁻¹ por el algoritmo de Acklam (error < 1,2 × 10⁻⁹).",
        "Beta(α, β) = X / (X + Y) con X ~ Gamma(α), Y ~ Gamma(β). PERT = Beta con α = 1 + λ(moda − mín)/(máx − mín), "
        "β = 1 + λ(máx − moda)/(máx − mín), λ = 4; media PERT = (mín + 4·moda + máx) / 6. [Vose parte II]",
        "Fórmulas de media: UNIFORME (a+b)/2 · TRIANGULAR (a+m+b)/3 · NORMAL μ · LOGNORMAL m (parametrizada por media m y "
        "desviación s de la variable: σ² = ln(1 + s²/m²), μ = ln m − σ²/2) · GAMMA k·θ · EXPONENCIAL media · WEIBULL "
        "λ·Γ(1 + 1/k) · GUMBEL μ + 0,5772·β · LOGISTICA μ · PARETO α·xm/(α−1) · POISSON λ · BINOMIAL n·p · "
        "DISCRETA Σ v·p · NORMAL_TRUNCADA μ + σ(φ(a*) − φ(b*))/(Φ(b*) − Φ(a*)).",
        "TRIGEN: triangular cuyos percentiles P(%bajo) y P(100 − %bajo) coinciden con los valores bajo y alto dados; el mínimo y "
        "el máximo se resuelven numéricamente. [Vose]",
        "POISSON: Knuth para λ < 30; PTRS de Hörmann para λ ≥ 30. BINOMIAL: suma de Bernoulli para n ≤ 50; si no, inversión con "
        "recurrencia (aproximación normal solo si la probabilidad de 0 no es representable).",
    ]),
    ("5. Modelo de evento de riesgo", [
        "Cada riesgo es un evento: Bernoulli(p) × impacto. La MISMA ocurrencia dispara todas sus dimensiones en esa iteración, "
        "y en la sensibilidad el riesgo se trata como una sola variable (ocurrencia + impacto). [Vose 5.3.7]",
        "Oportunidades: el mismo modelo con signo negativo. Si la probabilidad supera 50 %, conviene incluir el evento en la "
        "línea base y modelar su no ocurrencia como oportunidad. [Vose cap. 1]",
        "Total por dimensión en cada iteración = suma de los impactos de los riesgos activos.",
    ]),
    ("6. Correlación", [
        "Pearson mide relación lineal; Spearman (correlación de rangos) mide relación monótona y no depende de la forma de las "
        "distribuciones. [Vose 13.2]",
        "Iman–Conover: se generan puntajes normales con la correlación deseada y se reordenan las muestras de cada riesgo para "
        "que sus rangos sigan a los puntajes; las distribuciones marginales no cambian. [Vose 13.2.4]",
        "Modelo de un factor por grupo: S = √r·W + √(1−r)·E, con W común al grupo. La matriz resultante siempre es válida "
        "(semidefinida positiva). La correlación de rango objetivo ρ se convierte a normal con r = 2·sen(π·ρ/6).",
        "Con probabilidades < 1 muchos valores son 0 (empates) y la correlación de rango lograda es menor que la objetivo.",
    ]),
    ("7. Estadísticos de salida", [
        "Percentiles con interpolación lineal, igual que PERCENTIL.INC: posición h = (N − 1)·p + 1.",
        "Media, desviación estándar (N − 1), coeficiente de variación = desviación / |media|.",
        "IC 95 % de la media: media ± 1,96·σ/√N. IC 95 % del percentil p: valores ordenados en las posiciones "
        "N·p ± 1,96·√(N·p·(1−p)). Iteraciones sugeridas para ±1 %: N·(semiancho relativo / 0,01)². [Vose cap. 7; Kroese-H]",
    ]),
    ("8. Reservas y valor monetario esperado", [
        "a) Reserva para contingencias = P(nivel de confianza) del impacto simulado de los riesgos conocidos. [PMI-E X6.4.1]",
        "b) Variante Vose: presupuesto al valor esperado (base + media) y contingencia = P(nivel) − media; el directorio elige "
        "el nivel (80–85 % es usual). [Vose 19.1]",
        "c) Reserva de gestión = % de la base; cubre lo no identificado y no se simula. d) Presupuesto recomendado = base + a + c.",
        "VME = probabilidad × impacto (medio). La suma de los VME de todos los riesgos debe coincidir con la media simulada. "
        "[PMI-E X6.4.4]",
    ]),
    ("9. Sensibilidad (tornado)", [
        "Para cada riesgo: correlación de Spearman entre su impacto y el total; contribución a la varianza = ρ²/Σρ²; swing = "
        "media del total cuando el riesgo está en su 10 % superior − media cuando está en su 10 % inferior. [Vose 5.3.7]",
        "El tornado ordena los riesgos por swing: los de arriba son los que más conviene gestionar o investigar.",
    ]),
    ("10. Matriz probabilidad–impacto", [
        "Escala de 5 niveles para probabilidad e impacto; conviene que cada nivel sea ~3 veces el anterior. [Vose tabla 1.1; "
        "PMI-E X6.3.5, X6.4.3]",
        "Nivel de impacto del riesgo = mayor nivel entre sus dimensiones (impacto medio si ocurre). Puntaje = nivel P × nivel I; "
        "verde ≤ 4, ámbar 5–12, rojo ≥ 15.",
    ]),
    ("11. Antes / después de las respuestas", [
        "Escenario después: probabilidad residual y factor de impacto residual para cada riesgo con respuesta, más el costo de "
        "las respuestas (determinístico). [PMI-E 4.6; Vose 1.3–1.4]",
        "Se usan los MISMOS números aleatorios en ambos escenarios (números aleatorios comunes): la diferencia se debe solo a "
        "las respuestas. Beneficio neto = reserva antes − reserva después (incluye el costo de las respuestas).",
    ]),
    ("12. Limitaciones y técnicas no aplicadas", [
        "Plazo por suma (sin lógica de red del cronograma). [Vose 19.2]",
        "Hipercubo latino: mejora poco con muchas distribuciones y exige inversas de la CDF incompatibles con Gamma por rechazo. "
        "[Vose 4.4.3]",
        "Subset Simulation: diseñada para probabilidades de falla muy pequeñas (eventos raros), no es el caso. [Au y Wang]",
        "MCMC: para inferencia bayesiana, no se necesita en este modelo. [Robert y Casella]",
        "Reducción de varianza de finanzas (variables de control, antitéticas): la precisión se controla con N. [Glasserman]",
        "Asignación de contingencia por partida: aplica a partidas de costo, no a eventos. [Vose 19.1]",
        "Law y Kelton: el archivo .md solo contiene imágenes, sin texto utilizable.",
    ]),
    ("13. Bibliografía (archivos .md de MD.zip)", [
        "[PMI-E] PMI. El Estándar para la Gestión de Riesgos en Portafolios, Programas y Proyectos (español).",
        "[PMI-G] PMI. Risk Management in Portfolios, Programs, and Projects: A Practice Guide.",
        "[Vose] Vose, D. Risk Analysis: A Quantitative Guide, 3.ª ed. Wiley.",
        "[Kroese-H] Kroese, D. P.; Taimre, T.; Botev, Z. I. Handbook of Monte Carlo Methods. Wiley.",
        "[Kroese-S] Kroese, D. P.; Taimre, T.; Botev, Z. I.; Rubinstein, R. Y. Simulation and the Monte Carlo Method — manual de soluciones.",
        "[Stevens] Stevens, A. Monte-Carlo Simulation: An Introduction for Engineers and Scientists.",
        "[Glasserman] Glasserman, P. Monte Carlo Methods in Financial Engineering. Springer.",
        "[Robert y Casella] Robert, C. P.; Casella, G. Monte Carlo Statistical Methods, 2.ª ed. Springer.",
        "[Au y Wang] Au, S.-K.; Wang, Y. Engineering Risk Assessment with Subset Simulation. Wiley.",
        "[Law y Kelton] Law, A. M.; Kelton, W. D. Simulation Modeling and Analysis (sin texto en el .md).",
    ]),
]
