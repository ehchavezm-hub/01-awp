# Trazabilidad metodológica — Herramienta Montecarlo v3

Fuentes (archivos `.md` de `MD.zip`): **[PMI-E]** El Estándar para la Gestión de Riesgos en Portafolios, Programas y Proyectos (PMI, español) · **[PMI-G]** Risk Management in Portfolios, Programs, and Projects: A Practice Guide (PMI) · **[Vose]** Risk Analysis: A Quantitative Guide, 3.ª ed. · **[Kroese-H]** Handbook of Monte Carlo Methods · **[Kroese-S]** Simulation and the Monte Carlo Method (manual de soluciones) · **[Stevens]** Monte-Carlo Simulation: An Introduction for Engineers and Scientists · **[Glasserman]** Monte Carlo Methods in Financial Engineering · **[RC]** Robert y Casella, Monte Carlo Statistical Methods · **[Au]** Au y Wang, Engineering Risk Assessment with Subset Simulation · **[LK]** Law y Kelton, Simulation Modeling and Analysis.

Procedimientos VBA del módulo `MonteCarlo`; hojas y columnas del libro `MonteCarlo_Riesgos.xlsm`.

| ID | Fuente y sección | Requisito | Implementación (hoja / columna / procedimiento) | Estado |
|---|---|---|---|---|
| M1 | PMI-E 1, 2.1.1–2.1.3; Glosario | Riesgo = evento o condición incierta con efecto positivo (oportunidad) o negativo (amenaza); riesgo individual vs. general; reserva para contingencias (riesgos conocidos) vs. reserva de gestión (no previsto); riesgo residual y secundario | INICIO › «Metodología»; TEORIA §1; RESULTADOS › resumen y reservas | Implementado |
| M2 | Vose 1.6; PMI-E 4.3, 4.6 | Registro de riesgos con causa, dueño, estrategia, estado; estrategias PMI para amenazas y oportunidades | tblRiesgos: TIPO, CATEGORIA, CAUSA, DUENO DEL RIESGO, ESTRATEGIA (lista PMI), ESTADO | Implementado |
| M3 | Vose 1 («risk event»), 5.3.7 | Evento de riesgo = Bernoulli(p) × impacto, tratado como UNA variable en la sensibilidad; la misma ocurrencia dispara todas las dimensiones | `NucleoSimulacion` (una ocurrencia por riesgo e iteración para todas las dimensiones); `CalcularSensibilidad` usa `gM(:, r, d)` completo | Implementado |
| M4 | PMI-E 2.1.2; Vose 1 | Oportunidades con efecto positivo | TIPO = OPORTUNIDAD → `Signo = −1` en `LeerModeloDe`; marcadas en verde en TORNADO, RANGOS y MATRIZ_PI | Implementado |
| M5 | Vose 1 («probability in excess of 50 %») | Si p > 50 %, considerar incluir el evento en la línea base | Advertencia en `LeerModeloDe` y celda ámbar; listada en RESULTADOS | Implementado |
| M6 | PMI-E X6.4.4 | VME = probabilidad × impacto | `VME(r, d)` con la media teórica `DistMediaTeorica`; columna VME en RANGOS; VME total y su diferencia con la media simulada en RESULTADOS | Implementado |
| M7 | PMI-E Glosario, X6.4.1; Vose 19.1 | Reserva para contingencias con el nivel de confianza; variante de Vose (valor esperado + contingencia); reserva de gestión separada | Nombres NivelConfianza y ReservaGestionPct; RESULTADOS a) P(nivel), b) base + media y P(nivel) − media, c) % × base (dimensiones con RESERVA_GESTION = SI), d) presupuesto recomendado | Implementado |
| M8 | PMI-E 4.5 («interrelaciones», «correlación entre riesgos»); Vose 13.2, 13.2.4 | Correlación entre riesgos por rangos; matriz válida | GRUPO_CORRELACION y RHO_GRUPO; `AplicarCorrelacion` (Iman–Conover, un factor por grupo, r = 2·sen(πρ/6)); tabla «objetivo vs. lograda» en RESULTADOS | Implementado. Con p < 1 los ceros (empates) reducen la correlación lograda; se informa |
| M9 | Kroese-H cap. 1 (generadores; MRG32k3a recomendado) | Generador de calidad con período suficiente | `Aleatorio` (MRG32k3a en Double), `SembrarGenerador`, `FijarEstadoGenerador`; sin `Rnd()` | Implementado |
| M10 | Vose cap. 7; Stevens cap. 2; Kroese-H «Statistical analysis of simulation data» | Error ∝ 1/√N; precisión de media y percentiles; iteraciones necesarias | RESULTADOS › «Precisión»: error estándar, IC 95 % de la media, IC 95 % del P(nivel) por estadísticos de orden, iteraciones sugeridas para ±1 %, advertencia | Implementado |
| M11 | Vose 5.3.7 | Tornado por correlación de rangos (Spearman) | TORNADO: Spearman, contribución a la varianza, swing; gráfico de barras | Implementado |
| M12 | PMI-E 4.6, Glosario (riesgo residual); Vose 1.3–1.4 | Evaluar respuestas: riesgo residual y costo de la respuesta | PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL, COSTO_RESPUESTA; escenario «después» con números aleatorios comunes; hoja COMPARACION | Implementado |
| M13 | PMI-E X6.3.5, X6.4.3; Vose tabla 1.1 | Matriz probabilidad–impacto con escalas definidas (razón ~3) | tblEscalas (PROB_MAX, IMP_<DIM>); hoja MATRIZ_PI (general y por dimensión); `EscribirMatriz` | Implementado |
| M14 | Vose 19.2 | El plazo real depende de la lógica de red del cronograma | Suma por dimensión (supuesto conservador); declarado en INICIO › Limitaciones y TEORIA §12 | Parcial (limitación documentada) |
| M15 | Vose 4.4.3; Au; RC; Glasserman; Vose 19.1; LK | Técnicas evaluadas | Hipercubo latino, Subset Simulation, MCMC, reducción de varianza financiera y asignación de contingencia por partida: **no aplican** (motivos en TEORIA §12). LK: el `.md` solo contiene imágenes | No aplica |
| M16 | Vose cap. 9 y 14 (elicitación); Vose cap. 1 | Elección y parametrización de distribuciones para no especialistas | Hoja GUIA: probabilidad vs. impacto, árbol de decisión, 3 preguntas, catálogo, errores frecuentes, gráficos de forma; columnas AYUDA_ en tblRiesgos | Implementado |
| M17 | Vose parte II; Kroese-H caps. 3–4; Kroese-S cap. 2 | Catálogo completo de distribuciones y su generación | 20 distribuciones en `Muestra` y la lista ListaDistribuciones; validaciones en `ValidarDistribucion`; fórmulas en TEORIA §4 | Implementado |
| A1 | PMI-E X6.4.6 | La simulación entrega un rango de estimados y el nivel de confianza (curva S) | CURVA_S con marcas P50 y P(nivel) | Implementado (adicional) |
| A2 | PMI-E 2.1.5–2.1.6 | Apetito y umbral de riesgo | NivelConfianza como umbral de la organización; explicado en TEORIA §1 | Implementado (adicional) |
| A3 | PMI-G (guía práctica, mismos conceptos que PMI-E en inglés) | Coherencia de términos | Se usaron los términos en español de PMI-E | Implementado |

## Notas

- Los 32 riesgos del proyecto (R-01…R-32) llevan **estimaciones preliminares** (ANEXO A del prompt v3; costo base supuesto S/ 200 M y plazo de 730 días) con ESTADO = «ESTIMADO – VALIDAR». No son datos del proyecto.
- Law y Kelton: el archivo `Simulation Modelling and Analysis (...).pdf.md` contiene solo enlaces a imágenes; no se extrajo ningún requisito.
