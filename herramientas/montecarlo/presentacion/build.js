// Presentación: guía de uso de la macro Montecarlo, con énfasis en distribuciones.
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const sim = JSON.parse(fs.readFileSync(__dirname + "/sim.json", "utf8"));

// ---------- Paleta Bloomberg (plantilla_ppt.pptx) ----------
const C = {
  negro: "000000", ambar: "FFA028", blanco: "FFFFFF", gris: "333333", grisM: "6B6B6B",
  grisC: "EDEDED", tinte: "FFF0D6", tinte2: "FFF7EB", naranja: "FF6600", azul: "0068FF",
  verde: "00C805", rojo: "FF433D", teal: "4AF6C3", ambarP: "CC7A00", panel: "2A2A2A",
};
const F = "Arial";
const W = 13.333, H = 7.5, M = 0.6;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Guía de uso — Simulación Montecarlo de riesgos";
pres.author = "Análisis de riesgos";

// ---------- Matemática para las curvas ----------
function lgamma(x) {
  const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x);
  x -= 1; let a = c[0]; const t = x + g + 0.5;
  for (let i = 1; i < g + 2; i++) a += c[i] / (x + i);
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}
const pdf = {
  tri: (a, m, b) => x => x < a || x > b ? 0 : x <= m ? 2 * (x - a) / ((b - a) * (m - a)) : 2 * (b - x) / ((b - a) * (b - m)),
  beta: (al, be, a, b) => x => {
    if (x <= a || x >= b) return 0; const z = (x - a) / (b - a);
    return Math.exp((al - 1) * Math.log(z) + (be - 1) * Math.log(1 - z) - (lgamma(al) + lgamma(be) - lgamma(al + be))) / (b - a);
  },
  pertG: (a, m, b, g) => pdf.beta(1 + g * (m - a) / (b - a), 1 + g * (b - m) / (b - a), a, b),
  unif: (a, b) => x => x < a || x > b ? 0 : 1 / (b - a),
  normal: (mu, s) => x => Math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * Math.sqrt(2 * Math.PI)),
  logistic: (mu, s) => x => { const e = Math.exp(-(x - mu) / s); return e / (s * (1 + e) ** 2); },
  lognormal: (mean, sd) => { const s2 = Math.log(1 + (sd / mean) ** 2), mu = Math.log(mean) - s2 / 2, s = Math.sqrt(s2);
    return x => x <= 0 ? 0 : Math.exp(-((Math.log(x) - mu) ** 2) / (2 * s2)) / (x * s * Math.sqrt(2 * Math.PI)); },
  gamma: (k, th) => x => x <= 0 ? 0 : Math.exp((k - 1) * Math.log(x) - x / th - lgamma(k) - k * Math.log(th)),
  expo: (mean) => x => x < 0 ? 0 : Math.exp(-x / mean) / mean,
  weibull: (k, l) => x => x < 0 ? 0 : (k / l) * (x / l) ** (k - 1) * Math.exp(-((x / l) ** k)),
  gumbel: (mu, b) => x => { const z = (x - mu) / b; return Math.exp(-(z + Math.exp(-z))) / b; },
  pareto: (a, xm) => x => x < xm ? 0 : a * xm ** a / x ** (a + 1),
};
function grid(a, b, n) { const xs = []; for (let i = 0; i <= n; i++) xs.push(a + (b - a) * i / n); return xs; }
function r3(v) { return Math.round(v * 1e5) / 1e5; }
// TRIGEN: extremos a partir de P10 / moda / P90
function trigen(lo, m, hi, p) {
  let a = lo - 1, b = hi + 1;
  for (let i = 0; i < 200; i++) { a = lo - Math.sqrt(p * (b - a) * (m - a)); b = hi + Math.sqrt(p * (b - a) * (b - m)); }
  return [a, b];
}

// ---------- Helpers de diseño ----------
const notas = {};
function txt(s, t, o) { s.addText(t, Object.assign({ fontFace: F, isTextBox: true, color: C.negro, fontSize: 14, valign: "top", margin: 0 }, o)); }
function titulo(s, tag, t, sub) {
  txt(s, tag.toUpperCase(), { x: M, y: 0.38, w: 9, h: 0.3, fontSize: 11, bold: true, color: C.ambarP, charSpacing: 2 });
  txt(s, t, { x: M, y: 0.68, w: W - 2 * M, h: 0.75, fontSize: 30, bold: true, valign: "middle" });
  if (sub) txt(s, sub, { x: M, y: 1.42, w: W - 2 * M, h: 0.45, fontSize: 15, color: C.gris });
}
function nueva(tag, t, sub) { const s = pres.addSlide(); s.background = { color: C.blanco }; titulo(s, tag, t, sub); return s; }
function oscura() { const s = pres.addSlide(); s.background = { color: C.negro }; return s; }
function circulo(s, x, y, d, n, fill, col) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill || C.ambar }, line: { color: fill || C.ambar } });
  txt(s, String(n), { x, y, w: d, h: d, align: "center", valign: "middle", bold: true, fontSize: d > 0.6 ? 20 : 14, color: col || C.negro });
}
function tarjeta(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.tinte2 }, line: { color: fill || C.tinte2 } });
}
function pie(s, t) { txt(s, t, { x: M, y: H - 0.5, w: W - 2 * M, h: 0.3, fontSize: 10, color: C.grisM, italic: true }); }
function bullets(s, items, o) {
  s.addText(items.map((it, i) => ({ text: it, options: { bullet: true, breakLine: i < items.length - 1 } })),
    Object.assign({ fontFace: F, isTextBox: true, fontSize: 15, color: C.negro, paraSpaceAfter: 8, valign: "top", margin: 0 }, o));
}
// Gráfico de curvas (dispersión con líneas) — cada serie con su propia rejilla X común
function curvas(s, xs, series, o) {
  let mx = 0; series.forEach(se => xs.forEach(x => { const v = se.f(x); if (isFinite(v) && v > mx) mx = v; }));
  const data = [{ name: "X", values: xs.map(r3) }].concat(series.map(se => ({ name: se.name, values: xs.map(x => { const v = se.f(x); return r3(isFinite(v) ? v / mx : 0); }) })));
  s.addChart(pres.charts.SCATTER, data, Object.assign({
    lineSize: 2.5, lineDataSymbol: "none", chartColors: series.map(se => se.color),
    showLegend: series.length > 1, legendPos: "b", legendFontSize: 11, legendFontFace: F,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    catAxisLabelColor: C.gris, catAxisLabelFontSize: 11, catAxisLabelFontFace: F, catAxisLineColor: C.grisM,
    valAxisMinVal: 0, catAxisMinVal: xs[0], catAxisMaxVal: xs[xs.length - 1],
    showCatAxisTitle: !!o.ejeX, catAxisTitle: o.ejeX || "", catAxisTitleFontSize: 11, catAxisTitleColor: C.gris,
    showTitle: !!o.titulo, title: o.titulo || "", titleFontSize: 13, titleFontFace: F, titleColor: C.negro,
  }, o.extra || {}, { x: o.x, y: o.y, w: o.w, h: o.h }));
}
function barras(s, labels, vals, color, o) {
  s.addChart(pres.charts.BAR, [{ name: o.nombre || "Probabilidad", labels, values: vals }], Object.assign({
    barDir: "col", chartColors: [color], barGapWidthPct: 40, showLegend: false,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    catAxisLabelColor: C.gris, catAxisLabelFontSize: 11, catAxisLabelFontFace: F,
    showValue: !!o.valores, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: C.gris,
    dataLabelFormatCode: o.fmt || "0%",
    showTitle: !!o.titulo, title: o.titulo || "", titleFontSize: 13, titleFontFace: F, titleColor: C.negro,
    showCatAxisTitle: !!o.ejeX, catAxisTitle: o.ejeX || "", catAxisTitleFontSize: 11, catAxisTitleColor: C.gris,
  }, { x: o.x, y: o.y, w: o.w, h: o.h }));
}
function tabla(s, filas, o) {
  const cab = filas[0].map(t => ({ text: t, options: { bold: true, color: C.ambar, fill: { color: C.negro }, fontSize: o.fsCab || 12 } }));
  const cuerpo = filas.slice(1).map((f, i) => f.map((t, j) => ({ text: t, options: {
    fill: { color: i % 2 ? C.tinte2 : C.blanco }, fontSize: o.fs || 12, bold: j === 0 && o.primeraNegrita } })));
  s.addTable([cab].concat(cuerpo), { x: o.x, y: o.y, w: o.w, colW: o.colW, fontFace: F, color: C.negro,
    border: { type: "solid", pt: 0.5, color: "BFBFBF" }, valign: "middle", margin: [3, 6, 3, 6], rowH: o.rowH });
}
function N(v) { return v.toLocaleString("es-PE", { maximumFractionDigits: 0 }); }

// =====================================================================
// 1. Portada
let s = oscura();
txt(s, "ANÁLISIS CUANTITATIVO DE RIESGOS", { x: M, y: 1.5, w: 11, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Simulación Montecarlo en Excel", { x: M, y: 2.0, w: 12, h: 1.0, fontSize: 44, bold: true, color: C.blanco });
txt(s, "Guía de uso de la macro, con énfasis en cómo elegir y llenar las distribuciones", { x: M, y: 3.05, w: 11, h: 0.6, fontSize: 20, color: C.grisC });
txt(s, "MonteCarlo_Riesgos.xlsm  ·  costo · plazo · ingeniería de diseño · ingeniería de campo", { x: M, y: 5.9, w: 11, h: 0.4, fontSize: 13, color: C.ambar });
// motivo: curva PERT a la derecha
circulo(s, 11.3, 1.45, 0.9, "∿", C.ambar, C.negro);
s.addNotes("Presentación para capacitar a quienes llenan el registro de riesgos y corren la macro. La parte central (secciones 2 a 4) explica las distribuciones, que es lo más difícil de entender.");

// 2. Agenda
s = nueva("Contenido", "Qué veremos");
const agenda = [
  ["Qué hace la herramienta", "El flujo completo, de los riesgos a la contingencia"],
  ["La idea de distribución", "Probabilidad vs. impacto; qué hace la macro en cada escenario"],
  ["Cómo elegir la distribución", "Árbol de decisión y lo que dice el experto"],
  ["Las 20 distribuciones", "Por familias, con ejemplos de obra y qué va en P1…P4"],
  ["Casos especiales", "Dimensiones, oportunidades, respuestas y correlación"],
  ["Ejecutar e interpretar", "Botones, validación, curva S, tornado y contingencia"],
];
agenda.forEach((a, i) => {
  const col = i % 2, fila = Math.floor(i / 2), x = M + col * 6.2, y = 2.0 + fila * 1.6;
  circulo(s, x, y, 0.7, i + 1);
  txt(s, a[0], { x: x + 0.95, y: y, w: 5, h: 0.4, fontSize: 18, bold: true });
  txt(s, a[1], { x: x + 0.95, y: y + 0.42, w: 5, h: 0.6, fontSize: 14, color: C.gris });
});
s.addNotes("Las secciones 2, 3 y 4 son el núcleo: sin entender qué es una distribución, el resto de la herramienta es una caja negra.");

// 3. Qué hace
s = nueva("1 · La herramienta", "De un registro de riesgos a una contingencia justificada");
const flujo = [
  ["Registro", "32 riesgos con probabilidad e impactos (hoja PARAMETROS)"],
  ["Distribuciones", "Cada impacto se describe como un rango, no como un número"],
  ["10 000 escenarios", "La macro «juega» el proyecto miles de veces"],
  ["Curva S", "Probabilidad de no superar cada monto o plazo"],
  ["Contingencia", "Se elige el nivel (P80) y se lee la reserva"],
];
flujo.forEach((f, i) => {
  const x = M + i * 2.46, y = 2.3;
  tarjeta(s, x, y, 2.2, 2.6, i === 2 ? C.negro : C.tinte2);
  circulo(s, x + 0.2, y + 0.2, 0.55, i + 1, C.ambar);
  txt(s, f[0], { x: x + 0.2, y: y + 0.9, w: 1.9, h: 0.45, fontSize: 15, bold: true, color: i === 2 ? C.ambar : C.negro });
  txt(s, f[1], { x: x + 0.2, y: y + 1.45, w: 1.85, h: 1.1, fontSize: 12.5, color: i === 2 ? C.blanco : C.gris });
  if (i < 4) txt(s, "›", { x: x + 2.2, y: y + 1.0, w: 0.26, h: 0.5, fontSize: 28, bold: true, color: C.ambar, align: "center" });
});
txt(s, "En cada escenario la macro decide si cada riesgo ocurre y, si ocurre, cuánto impacta. Sumando los riesgos obtiene un total; repitiendo miles de veces obtiene la forma completa de lo que puede pasar.",
  { x: M, y: 5.3, w: W - 2 * M, h: 0.9, fontSize: 16 });
s.addNotes("La ventaja frente a sumar valores fijos: no todos los riesgos ocurren a la vez; la simulación refleja esa combinación de forma natural y entrega probabilidades, no un solo número.");

// 4. Hojas
s = nueva("1 · La herramienta", "Las 11 hojas del libro");
const hojas = [
  ["INICIO", "Propósito, pasos y limitaciones"], ["GUIA", "Distribuciones para no especialistas"],
  ["PARAMETROS", "Configuración, dimensiones y registro de riesgos"], ["RESULTADOS", "Estadísticas, reservas y precisión"],
  ["CURVA_S", "Probabilidad acumulada e histograma"], ["TORNADO", "Riesgos que más mueven el total"],
  ["RANGOS", "P10…P90 y VME por riesgo"], ["MATRIZ_PI", "Matriz probabilidad–impacto 5×5"],
  ["COMPARACION", "Antes vs. después de las respuestas"], ["SIMULACION", "Primeras 5 000 iteraciones"],
  ["TEORIA", "Toda la teoría y la bibliografía"],
];
hojas.forEach((h, i) => {
  const col = i % 4, fila = Math.floor(i / 4), x = M + col * 3.05, y = 2.0 + fila * 1.6;
  const entrada = h[0] === "PARAMETROS";
  tarjeta(s, x, y, 2.85, 1.35, entrada ? C.ambar : C.tinte2);
  txt(s, h[0], { x: x + 0.2, y: y + 0.18, w: 2.5, h: 0.4, fontSize: 16, bold: true });
  txt(s, h[1], { x: x + 0.2, y: y + 0.6, w: 2.5, h: 0.65, fontSize: 12.5, color: C.gris });
});
tarjeta(s, M + 3 * 3.05, 2.0 + 2 * 1.6, 2.85, 1.35, C.blanco);
txt(s, "En ámbar: la única hoja donde se ingresan datos. Las demás las escribe la macro.", { x: M + 3 * 3.05 + 0.1, y: 2.0 + 2 * 1.6 + 0.15, w: 2.7, h: 1.1, fontSize: 12, italic: true, color: C.gris });
s.addNotes("Solo se edita PARAMETROS. Las hojas de resultados se borran y reescriben en cada corrida.");

// 5. Pasos
s = nueva("1 · La herramienta", "Flujo de uso en 6 pasos");
const pasos = [
  ["Habilitar macros", "Abrir el .xlsm › «Habilitar contenido». Si Windows lo bloquea: clic derecho › Propiedades › Desbloquear."],
  ["Configurar", "PARAMETROS: costo base, plazo base, iteraciones (10 000), semilla, nivel de confianza (80 %), reserva de gestión."],
  ["Registrar riesgos", "Una fila por riesgo: probabilidad y, para cada dimensión que afecte, su distribución y P1…P4."],
  ["Validar", "Botón ✔ VALIDAR DATOS: rojo = error que impide correr; ámbar = advertencia a revisar."],
  ["Simular", "Botón ▶ CORRER SIMULACIÓN. 10 000 iteraciones tardan del orden de un minuto."],
  ["Interpretar", "RESULTADOS y CURVA_S para la contingencia; TORNADO para saber dónde actuar."],
];
pasos.forEach((p, i) => {
  const y = 2.0 + i * 0.82;
  circulo(s, M, y, 0.55, i + 1);
  txt(s, p[0], { x: M + 0.8, y: y + 0.08, w: 2.6, h: 0.45, fontSize: 16, bold: true });
  txt(s, p[1], { x: M + 3.5, y: y + 0.08, w: 8.6, h: 0.7, fontSize: 14, color: C.gris });
});
s.addNotes("El paso 3 es donde se decide la calidad del resultado: las secciones siguientes explican cómo llenarlo.");

// 6. Divisor
s = oscura();
txt(s, "PARTE 2", { x: M, y: 2.4, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "La idea de distribución", { x: M, y: 2.85, w: 12, h: 0.9, fontSize: 40, bold: true, color: C.blanco });
txt(s, "Lo más importante de la herramienta — y lo más difícil de entender", { x: M, y: 3.8, w: 12, h: 0.5, fontSize: 18, color: C.grisC });

// 7. Un número vs un rango
s = nueva("2 · La idea", "De un número a un rango", "Una distribución describe lo que NO sabemos con exactitud: qué valores son posibles y cuáles son más probables.");
tarjeta(s, M, 2.15, 4.3, 4.3, C.grisC);
txt(s, "Estimado tradicional", { x: M + 0.3, y: 2.35, w: 3.8, h: 0.4, fontSize: 15, bold: true, color: C.gris });
txt(s, "S/ 600 000", { x: M + 0.3, y: 2.9, w: 3.8, h: 0.9, fontSize: 40, bold: true });
txt(s, "Un solo número. No dice qué tan seguro es, ni cuánto podría llegar a costar si sale mal.", { x: M + 0.3, y: 3.95, w: 3.8, h: 1.2, fontSize: 14, color: C.gris });
txt(s, "Falsa precisión: el costo real casi nunca será exactamente ese.", { x: M + 0.3, y: 5.3, w: 3.8, h: 0.9, fontSize: 13, italic: true, color: C.rojo });
const xsP = grid(150, 1500, 135);
curvas(s, xsP, [{ name: "PERT 200 000 / 600 000 / 1 400 000", f: pdf.pertG(200, 600, 1400, 4), color: C.naranja }],
  { x: 5.3, y: 2.1, w: 7.4, h: 3.7, titulo: "Estimado con distribución: PERT 200 000 / 600 000 / 1 400 000", ejeX: "Sobrecosto (miles de S/)",
    extra: { catAxisMajorUnit: 200 } });
txt(s, "Mínimo 200 000 · lo más probable 600 000 · máximo 1 400 000. La altura de la curva indica qué valores salen más a menudo.",
  { x: 5.3, y: 5.9, w: 7.4, h: 0.7, fontSize: 14 });
s.addNotes("No es más trabajo que dar un número: basta con tres (mínimo, más probable, máximo). Ganamos poder decir con qué probabilidad no se supera cada monto.");

// 8. Dos preguntas
s = nueva("2 · La idea", "Cada riesgo responde DOS preguntas distintas", "Van en columnas distintas y nunca se mezclan.");
[[M, "1", "¿Ocurre o no ocurre?", "Columna PROBABILIDAD", "Un número entre 0 y 1.", "0,55 = 55 % de chance de que la Supervisión demore las aprobaciones.", C.azul],
 [6.9, "2", "Si ocurre, ¿cuánto impacta?", "Columnas DIST_<dimensión> y P1…P4", "Una distribución por cada dimensión que el riesgo afecte.", "COSTO PERT 200 000 / 600 000 / 1 400 000\nPLAZO TRIANGULAR 10 / 20 / 45 días", C.naranja]]
  .forEach(([x, n, q, col, desc, ej, color]) => {
    tarjeta(s, x, 2.15, 5.8, 3.9, C.tinte2);
    circulo(s, x + 0.3, 2.4, 0.7, n, color, C.blanco);
    txt(s, q, { x: x + 1.2, y: 2.45, w: 4.4, h: 0.6, fontSize: 20, bold: true, valign: "middle" });
    txt(s, col, { x: x + 0.3, y: 3.35, w: 5.2, h: 0.4, fontSize: 15, bold: true, color: C.ambarP });
    txt(s, desc, { x: x + 0.3, y: 3.8, w: 5.2, h: 0.5, fontSize: 14 });
    txt(s, "Ejemplo R-11: " + ej, { x: x + 0.3, y: 4.4, w: 5.2, h: 1.4, fontSize: 14, color: C.gris });
  });
txt(s, "Error típico: «multiplicar» la probabilidad por el impacto al ingresar los datos. La macro ya lo hace en cada escenario; el impacto se ingresa COMPLETO, como si el riesgo ocurriera.",
  { x: M, y: 6.2, w: W - 2 * M, h: 0.7, fontSize: 14, bold: true, color: C.rojo });
s.addNotes("En el 45 % de las iteraciones R-11 no ocurre y aporta 0. En el 55 % restante aporta un valor sacado de su distribución. Por eso el impacto se escribe completo.");

// 9. Qué hace la macro en cada iteración
s = nueva("2 · La idea", "Qué hace la macro en cada escenario", "Ejemplo con R-05 (demora en aprobación de UMAS): probabilidad 0,45; afecta costo, plazo e ingeniería de diseño.");
tabla(s, [
  ["Iteración", "Sorteo (0–1)", "¿Ocurre? (< 0,45)", "Costo (PERT)", "Plazo (TRIANGULAR)", "Ing. diseño (TRIANGULAR)"],
  ["1", "0,31", "Sí", "S/ 612 000", "34 días", "350 HH"],
  ["2", "0,72", "No", "0", "0", "0"],
  ["3", "0,08", "Sí", "S/ 455 000", "22 días", "260 HH"],
  ["4", "0,90", "No", "0", "0", "0"],
  ["…", "…", "…", "…", "…", "…"],
  ["10 000", "0,44", "Sí", "S/ 981 000", "51 días", "540 HH"],
], { x: M, y: 2.2, w: 8.1, colW: [1.1, 1.2, 1.5, 1.4, 1.4, 1.5], rowH: 0.42, fs: 13, primeraNegrita: true });
tarjeta(s, 9.1, 2.2, 3.6, 3.5, C.negro);
txt(s, "Reglas clave", { x: 9.35, y: 2.4, w: 3.2, h: 0.4, fontSize: 16, bold: true, color: C.ambar });
bullets(s, ["Un solo sorteo decide la ocurrencia para TODAS las dimensiones del riesgo.",
  "Si ocurre, cada dimensión saca su propio valor de su distribución.",
  "El total de la iteración es la suma de todos los riesgos."], { x: 9.35, y: 2.9, w: 3.2, h: 2.7, fontSize: 13, color: C.blanco });
txt(s, "Valores ilustrativos. Al final hay 10 000 totales por dimensión: con ellos se construyen la curva S, el tornado y la contingencia.",
  { x: M, y: 5.6, w: 8.1, h: 0.8, fontSize: 14, color: C.gris });
s.addNotes("Si el riesgo ocurre, cuesta y demora a la vez: la macro no puede producir un escenario con costo pero sin retraso para el mismo evento.");

// 10. Densidad vs acumulada
s = nueva("2 · La idea", "Dos formas de leer una distribución", "La misma información, vista como «qué tan frecuente» (densidad) o como «probabilidad de no superar» (acumulada).");
curvas(s, xsP, [{ name: "Densidad", f: pdf.pertG(200, 600, 1400, 4), color: C.naranja }],
  { x: M, y: 2.1, w: 6.0, h: 3.6, titulo: "Densidad: dónde se concentran los valores", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 200 } });
// acumulada numérica
const fP = pdf.pertG(200, 600, 1400, 4); let acc = 0; const cdf = [];
xsP.forEach((x, i) => { if (i > 0) acc += (fP(x) + fP(xsP[i - 1])) / 2 * (x - xsP[i - 1]); cdf.push(acc); });
s.addChart(pres.charts.SCATTER, [{ name: "X", values: xsP.map(r3) }, { name: "Acumulada", values: cdf.map(v => Math.round(v * 1000) / 10) }], {
  x: 6.8, y: 2.1, w: 6.0, h: 3.6, lineSize: 2.5, lineDataSymbol: "none", chartColors: [C.azul], showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20, valAxisLabelFontSize: 11, valAxisLabelColor: C.gris,
  showValAxisTitle: true, valAxisTitle: "% acumulado", valAxisTitleFontSize: 11, valAxisTitleColor: C.gris,
  showCatAxisTitle: true, catAxisTitle: "Miles de S/", catAxisTitleFontSize: 11, catAxisTitleColor: C.gris,
  valGridLine: { color: "E0E0E0", size: 0.5 }, catGridLine: { style: "none" }, catAxisMajorUnit: 200,
  catAxisMinVal: xsP[0], catAxisMaxVal: xsP[xsP.length - 1], catAxisLabelFontSize: 11, catAxisLabelColor: C.gris,
  showTitle: true, title: "Acumulada (curva S): P10, P50, P80…", titleFontSize: 13, titleFontFace: F });
const pq = q => { for (let i = 0; i < cdf.length; i++) if (cdf[i] >= q) return xsP[i] * 1000; };
txt(s, `P50 ≈ S/ ${N(Math.round(pq(0.5) / 1000) * 1000)}: mitad de los casos por debajo.   P80 ≈ S/ ${N(Math.round(pq(0.8) / 1000) * 1000)}: 80 % de los casos por debajo.`,
  { x: M, y: 5.85, w: W - 2 * M, h: 0.5, fontSize: 15, bold: true });
txt(s, "La curva S es la que se usa para fijar la contingencia (parte 6).", { x: M, y: 6.35, w: W - 2 * M, h: 0.4, fontSize: 13, color: C.gris });
s.addNotes("Densidad: la altura indica frecuencia relativa. Acumulada: para cada valor, qué fracción de los escenarios queda por debajo. El P80 se lee donde la curva cruza 80 %.");

// 11. Min, moda, media
const a0 = 10, m0 = 20, b0 = 45;
s = nueva("2 · La idea", "Mínimo, moda, media y máximo no son lo mismo", `Ejemplo: retraso en aprobación de submittals, ${a0} / ${m0} / ${b0} días.`);
const xsT = grid(5, 50, 90);
curvas(s, xsT, [{ name: "PERT", f: pdf.pertG(a0, m0, b0, 4), color: C.naranja }],
  { x: M, y: 2.1, w: 7.2, h: 4.2, ejeX: "Días de retraso", extra: { catAxisMajorUnit: 5 } });
const defs = [
  ["Mínimo (P1)", `${a0} días`, "Lo mejor razonable, no lo imposible."],
  ["Moda (P2)", `${m0} días`, "El valor MÁS FRECUENTE: la cima de la curva."],
  ["Media", `${((a0 + 4 * m0 + b0) / 6).toFixed(1)} días`, "El promedio. Con cola a la derecha, es mayor que la moda."],
  ["Máximo (P3)", `${b0} días`, "Lo peor razonable, sin catástrofes absurdas."],
];
defs.forEach((d, i) => {
  const y = 2.15 + i * 1.05;
  tarjeta(s, 8.1, y, 4.6, 0.92, i === 1 ? C.tinte : C.tinte2);
  txt(s, d[0], { x: 8.3, y: y + 0.1, w: 2.2, h: 0.35, fontSize: 14, bold: true });
  txt(s, d[1], { x: 10.6, y: y + 0.1, w: 1.9, h: 0.35, fontSize: 14, bold: true, color: C.ambarP, align: "right" });
  txt(s, d[2], { x: 8.3, y: y + 0.47, w: 4.2, h: 0.4, fontSize: 12, color: C.gris });
});
txt(s, "La moda es lo que ocurre «normalmente», no el peor caso ni el promedio.", { x: 8.1, y: 6.4, w: 4.6, h: 0.5, fontSize: 13, italic: true });
s.addNotes("Error frecuente: poner como moda el valor más temido. La media de PERT = (mín + 4·moda + máx)/6.");

// 12. Divisor
s = oscura();
txt(s, "PARTE 3", { x: M, y: 2.4, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Cómo elegir la distribución", { x: M, y: 2.85, w: 12, h: 0.9, fontSize: 40, bold: true, color: C.blanco });
txt(s, "Se elige según LO QUE SABEMOS del impacto, no según lo que «suena» más técnico", { x: M, y: 3.8, w: 12, h: 0.5, fontSize: 18, color: C.grisC });

// 13. Árbol de decisión
s = nueva("3 · Elegir", "Árbol de decisión: ¿qué sé del impacto?");
const arbol = [
  ["El valor es seguro si el riesgo ocurre", "CONSTANTE"],
  ["Solo conozco un rango, sin valor más probable", "UNIFORME"],
  ["Conozco mínimo, más probable y máximo", "PERT (recomendada) o TRIANGULAR"],
  ["El experto dice «rara vez baja de X o pasa de Y»", "TRIGEN"],
  ["Pocos escenarios con probabilidad conocida", "DISCRETA"],
  ["Promedio y dispersión simétrica (datos históricos)", "NORMAL / NORMAL_TRUNCADA"],
  ["Sesgado a la derecha, nunca negativo, con datos", "LOGNORMAL o GAMMA"],
  ["Cuento eventos en el periodo", "POISSON o BINOMIAL"],
  ["Colas extremas: reclamos grandes, eventos raros", "PARETO, GUMBEL o LOGNORMAL"],
];
arbol.forEach((a, i) => {
  const y = 1.75 + i * 0.58;
  tarjeta(s, M, y, 7.0, 0.48, i % 2 ? C.tinte2 : C.grisC);
  txt(s, a[0], { x: M + 0.2, y, w: 6.7, h: 0.48, fontSize: 14, valign: "middle" });
  txt(s, "›", { x: M + 7.05, y, w: 0.4, h: 0.48, fontSize: 22, bold: true, color: C.ambar, align: "center", valign: "middle" });
  const principal = i <= 4;
  tarjeta(s, M + 7.5, y, 4.6, 0.48, principal ? C.ambar : C.negro);
  txt(s, a[1], { x: M + 7.7, y, w: 4.3, h: 0.48, fontSize: 14, bold: true, valign: "middle", color: principal ? C.negro : C.ambar });
});
pie(s, "En ámbar: las que cubren la mayoría de los riesgos de obra estimados por juicio experto. En negro: cuando hay datos históricos o casos particulares.");
s.addNotes("En la práctica, más del 90 % de los riesgos de un registro de obra se modelan con PERT o TRIANGULAR porque se estiman con expertos. Las demás se usan cuando hay datos o un comportamiento particular.");

// 14. Frase del experto -> distribución
s = nueva("3 · Elegir", "Traducir lo que dice el experto", "La forma en que la persona describe el impacto ya indica la distribución.");
const frases = [
  ["«Si pasa, la multa es S/ 250 000, fija.»", "CONSTANTE", "P1 = 250 000"],
  ["«Entre 10 y 40 días, cualquiera; no sé cuál es típico.»", "UNIFORME", "10 / 40"],
  ["«Normalmente 20 días; como mínimo 10 y como máximo 45.»", "PERT", "10 / 20 / 45"],
  ["«Rara vez menos de 5, lo normal 12, rara vez más de 30.»", "TRIGEN", "5 / 12 / 30 / 10"],
  ["«60 % nada, 30 % S/ 150 000, 10 % S/ 400 000.»", "DISCRETA", "«0;150000;400000» / «0,6;0,3;0,1»"],
  ["«Unas 3 no conformidades al mes, a veces más.»", "POISSON", "P1 = 3"],
  ["«En obras anteriores: promedio 50 000, ±25 000.»", "NORMAL", "50 000 / 25 000"],
];
tabla(s, [["Lo que dice el experto", "Distribución", "P1 / P2 / P3 / P4"]].concat(frases),
  { x: M, y: 2.1, w: W - 2 * M, colW: [6.4, 2.3, 3.43], rowH: 0.5, fs: 14, fsCab: 13 });
s.addNotes("Escuchar las palabras: «más o menos», «normalmente», «lo típico» = moda; «rara vez» = percentil (TRIGEN); «cualquiera» = uniforme; «escenarios» = discreta.");

// 15. Tres preguntas
s = nueva("3 · Elegir", "Cómo preguntar al experto: 3 preguntas en este orden", "Primero los extremos, después el valor típico: así se evita que la primera cifra «ancle» a las demás (Vose, cap. 14).");
[["«Si todo sale bien, ¿cuál es el MÍNIMO razonable del impacto?»", "P1"],
 ["«Si todo sale mal, ¿cuál es el MÁXIMO razonable?» (sin catástrofes absurdas)", "P3"],
 ["«¿Cuál es el valor MÁS PROBABLE?» (lo que pasa normalmente)", "P2"]].forEach((p, i) => {
  const y = 2.25 + i * 1.15;
  circulo(s, M, y, 0.75, i + 1);
  txt(s, p[0], { x: M + 1.0, y: y + 0.05, w: 8.6, h: 0.7, fontSize: 17, valign: "middle" });
  tarjeta(s, 10.3, y + 0.08, 2.4, 0.6, C.negro);
  txt(s, "→ " + p[1], { x: 10.3, y: y + 0.08, w: 2.4, h: 0.6, fontSize: 16, bold: true, color: C.ambar, align: "center", valign: "middle" });
});
tarjeta(s, M, 5.8, W - 2 * M, 0.95, C.tinte);
txt(s, "Después pregunte la PROBABILIDAD de que el riesgo ocurra. Si el experto duda de los extremos, use TRIGEN y pida valores que «rara vez» se superan. Anote la fuente de cada número en NOTAS.",
  { x: M + 0.25, y: 5.88, w: W - 2 * M - 0.5, h: 0.8, fontSize: 14, valign: "middle" });
s.addNotes("Las personas tienden a subestimar la incertidumbre: los extremos que dan suelen ser demasiado estrechos. Por eso TRIGEN es útil: pide percentiles, no extremos absolutos.");

// 16. Divisor
s = oscura();
txt(s, "PARTE 4", { x: M, y: 2.4, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Las 20 distribuciones, por familias", { x: M, y: 2.85, w: 12, h: 0.9, fontSize: 40, bold: true, color: C.blanco });
txt(s, "Todas están en el menú de cada columna DIST_. Para cada una: cuándo usarla, qué va en P1…P4 y un ejemplo de obra.", { x: M, y: 3.8, w: 12, h: 0.8, fontSize: 18, color: C.grisC });

// 17. Tres puntos: TRIANGULAR vs PERT vs TRIGEN
s = nueva("4 · Familia «tres puntos»", "TRIANGULAR, PERT y TRIGEN", `Las tres usan mínimo / moda / máximo. Con los mismos datos (${a0} / ${m0} / ${b0} días) dan resultados distintos.`);
const [tgA, tgB] = trigen(a0, m0, b0, 0.10);
const xs3 = grid(-10, 70, 160);
curvas(s, xs3, [
  { name: "TRIANGULAR", f: pdf.tri(a0, m0, b0), color: C.azul },
  { name: "PERT", f: pdf.pertG(a0, m0, b0, 4), color: C.naranja },
  { name: "TRIGEN (10 y 45 como P10 y P90)", f: pdf.tri(tgA, m0, tgB), color: C.gris },
], { x: M, y: 2.1, w: 6.9, h: 4.4, ejeX: "Días", extra: { catAxisMajorUnit: 10 } });
tabla(s, [
  ["", "P1", "P2", "P3", "P4", "Media"],
  ["TRIANGULAR", "Mín.", "Moda", "Máx.", "—", ((a0 + m0 + b0) / 3).toFixed(1)],
  ["PERT", "Mín.", "Moda", "Máx.", "—", ((a0 + 4 * m0 + b0) / 6).toFixed(1)],
  ["TRIGEN", "Bajo", "Moda", "Alto", "% (10)", ((tgA + m0 + tgB) / 3).toFixed(1)],
], { x: 7.75, y: 2.15, w: 4.95, colW: [1.35, 0.6, 0.7, 0.6, 0.8, 0.9], rowH: 0.38, fs: 12, primeraNegrita: true });
bullets(s, [
  "PERT (recomendada): concentra el peso cerca de la moda; es la opción por defecto.",
  "TRIANGULAR: da más peso a los extremos → más conservadora (media mayor).",
  `TRIGEN: el experto da valores que «rara vez» se superan; la macro calcula los extremos reales (aquí ≈ ${tgA.toFixed(1)} y ${tgB.toFixed(1)}).`,
], { x: 7.75, y: 3.85, w: 4.95, h: 2.9, fontSize: 13 });
s.addNotes("Con 10/20/45: media triangular 25 días, PERT 22,5 días. TRIGEN amplía el rango porque el 10 % de los casos queda por debajo de 10 y otro 10 % por encima de 45.");

// 18. PERT_MODIFICADA y BETA_GENERAL
s = nueva("4 · Controlar la forma", "PERT_MODIFICADA y BETA_GENERAL", "Cuando además del rango se sabe qué tan concentrados están los valores.");
curvas(s, xsT, [
  { name: "γ = 2 (moda poco confiable)", f: pdf.pertG(a0, m0, b0, 2), color: C.azul },
  { name: "γ = 4 (= PERT)", f: pdf.pertG(a0, m0, b0, 4), color: C.naranja },
  { name: "γ = 8 (moda muy confiable)", f: pdf.pertG(a0, m0, b0, 8), color: C.negro },
], { x: M, y: 2.1, w: 6.2, h: 3.9, titulo: `PERT_MODIFICADA ${a0} / ${m0} / ${b0} / γ`, ejeX: "Días", extra: { catAxisMajorUnit: 5 } });
curvas(s, grid(0, 10, 100), [
  { name: "α=2, β=5", f: pdf.beta(2, 5, 0, 10), color: C.naranja },
  { name: "α=5, β=2", f: pdf.beta(5, 2, 0, 10), color: C.azul },
  { name: "α=β=2", f: pdf.beta(2, 2, 0, 10), color: C.gris },
], { x: 6.9, y: 2.1, w: 5.8, h: 3.9, titulo: "BETA_GENERAL α / β / 0 / 10", ejeX: "% de desperdicio", extra: { catAxisMajorUnit: 2 } });
txt(s, "PERT_MODIFICADA — P1 mín., P2 moda, P3 máx., P4 γ (4 = PERT). Úsela si el experto está muy seguro (γ 6–10) o poco seguro (γ 1–3) del valor típico.",
  { x: M, y: 6.1, w: 6.1, h: 0.9, fontSize: 13 });
txt(s, "BETA_GENERAL — P1 α, P2 β, P3 mín., P4 máx. Para ajustar a datos históricos acotados (ej. % de desperdicio de concreto de obras anteriores).",
  { x: 6.9, y: 6.1, w: 5.8, h: 0.9, fontSize: 13 });
s.addNotes("Si no hay datos ni una razón clara, quédese con PERT. BETA_GENERAL requiere estimar α y β, normalmente con una herramienta de ajuste estadístico.");

// 19. Simples: CONSTANTE, UNIFORME, DISCRETA, DISCRETA_UNIFORME
s = nueva("4 · Familia «simples»", "Cuatro distribuciones simples", "CONSTANTE, UNIFORME, DISCRETA y DISCRETA_UNIFORME: no requieren moda ni dispersión.");
const simples = [
  ["CONSTANTE", "P1 = valor", "El impacto es seguro si el riesgo ocurre.", "Multa fija de S/ 250 000 por incumplir un hito."],
  ["UNIFORME", "P1 mín. · P2 máx.", "Solo hay un rango; ningún valor es más probable.", "Permiso municipal: demora de 10 a 40 días."],
  ["DISCRETA", "P1 «v1;v2;…» · P2 «p1;p2;…»", "Pocos escenarios con probabilidad conocida (deben sumar 1).", "Penalidad «0;150000;400000» con «0,6;0,3;0,1»."],
  ["DISCRETA_UNIFORME", "P1 mín. · P2 máx. (enteros)", "Un entero entre dos límites, todos igual de probables.", "Grúas indisponibles: 0 a 2."],
];
simples.forEach((c, i) => {
  const x = M + (i % 2) * 3.1, y = 2.05 + Math.floor(i / 2) * 2.4;
  tarjeta(s, x, y, 2.95, 2.25, C.tinte2);
  txt(s, c[0], { x: x + 0.18, y: y + 0.15, w: 2.6, h: 0.35, fontSize: 14, bold: true });
  txt(s, c[1], { x: x + 0.18, y: y + 0.52, w: 2.6, h: 0.45, fontSize: 11.5, bold: true, color: C.ambarP });
  txt(s, c[2], { x: x + 0.18, y: y + 0.98, w: 2.6, h: 0.65, fontSize: 12 });
  txt(s, c[3], { x: x + 0.18, y: y + 1.65, w: 2.6, h: 0.7, fontSize: 11.5, italic: true, color: C.gris });
});
barras(s, ["S/ 0", "S/ 150 000", "S/ 400 000"], [0.6, 0.3, 0.1], C.naranja,
  { x: 6.9, y: 2.05, w: 5.8, h: 2.25, titulo: "DISCRETA: penalidad por escenarios", valores: true });
curvas(s, grid(0, 50, 100), [{ name: "UNIFORME 10 / 40", f: pdf.unif(10, 40), color: C.azul }],
  { x: 6.9, y: 4.4, w: 5.8, h: 2.1, titulo: "UNIFORME 10 / 40 días: todos igual de probables", ejeX: "Días", extra: { catAxisMajorUnit: 10 } });
pie(s, "DISCRETA: los valores y las probabilidades se escriben separados por «;» y en el mismo orden.");
s.addNotes("Con DISCRETA el valor 0 es un escenario válido además de la probabilidad del riesgo: por ejemplo, el riesgo ocurre pero la penalidad no se aplica.");

// 20. Simétricas
s = nueva("4 · Familia «simétricas»", "NORMAL, NORMAL_TRUNCADA y LOGISTICA", "Variación pareja alrededor de un promedio. Útiles con datos históricos; con juicio experto prefiera PERT.");
curvas(s, grid(-40, 140, 180), [
  { name: "NORMAL 50 000 / 25 000", f: pdf.normal(50, 25), color: C.naranja },
  { name: "LOGISTICA 50 000 / 13 800 (misma dispersión)", f: pdf.logistic(50, 25 * Math.sqrt(3) / Math.PI), color: C.azul },
], { x: M, y: 2.1, w: 7.0, h: 4.3, ejeX: "Variación de precio del acero (miles de S/)", extra: { catAxisMajorUnit: 20 } });
const sim3 = [
  ["NORMAL", "P1 media · P2 desviación", "Puede dar valores negativos: útil para variaciones que pueden ser a favor."],
  ["NORMAL_TRUNCADA", "P1 media · P2 desv. · P3 mín. · P4 máx.", "Igual, pero dentro de límites físicos o contractuales (ej. tope ±5 %)."],
  ["LOGISTICA", "P1 media · P2 escala", "Parecida a la normal, con colas algo más pesadas. Desviación = escala × 1,81."],
];
sim3.forEach((c, i) => {
  const y = 2.1 + i * 1.45;
  tarjeta(s, 7.9, y, 4.8, 1.3, C.tinte2);
  txt(s, c[0], { x: 8.1, y: y + 0.12, w: 4.4, h: 0.35, fontSize: 14, bold: true });
  txt(s, c[1], { x: 8.1, y: y + 0.45, w: 4.4, h: 0.3, fontSize: 11.5, bold: true, color: C.ambarP });
  txt(s, c[2], { x: 8.1, y: y + 0.77, w: 4.4, h: 0.5, fontSize: 12 });
});
s.addNotes("Regla práctica: 68 % de los valores caen a ±1 desviación de la media y 95 % a ±2. Si un valor negativo no tiene sentido físico, use NORMAL_TRUNCADA con mínimo 0.");

// 21. Sesgadas
s = nueva("4 · Familia «sesgadas a la derecha»", "LOGNORMAL, GAMMA, WEIBULL y EXPONENCIAL", "Nunca negativas, con muchos casos pequeños y algunos muy grandes. Todas con media ≈ 10 en el gráfico.");
curvas(s, grid(0, 40, 160), [
  { name: "LOGNORMAL 10 / 6", f: pdf.lognormal(10, 6), color: C.naranja },
  { name: "GAMMA 3 / 3,33", f: pdf.gamma(3, 10 / 3), color: C.azul },
  { name: "WEIBULL 2 / 11,3", f: pdf.weibull(2, 11.28), color: C.gris },
  { name: "EXPONENCIAL 10", f: pdf.expo(10), color: C.negro },
], { x: M, y: 2.1, w: 6.9, h: 4.4, ejeX: "Días (o S/, HH…)", extra: { catAxisMajorUnit: 5 } });
tabla(s, [
  ["Distribución", "P1", "P2", "Ejemplo"],
  ["LOGNORMAL", "Media", "Desv.", "Reparación de fisuras en vecinos"],
  ["GAMMA", "Forma", "Escala", "HH de rediseño (media = forma × escala)"],
  ["WEIBULL", "Forma k", "Escala λ", "Días de grúa fuera de servicio"],
  ["EXPONENCIAL", "Media", "—", "Días de paralización por evento"],
], { x: 7.75, y: 2.15, w: 4.95, colW: [1.35, 0.75, 0.75, 2.1], rowH: 0.5, fs: 11.5, primeraNegrita: true });
txt(s, "Ojo: en EXPONENCIAL, P1 es la MEDIA (no la tasa). En WEIBULL, forma < 1 = fallas tempranas; > 1 = desgaste.",
  { x: 7.75, y: 5.0, w: 4.95, h: 0.9, fontSize: 13, bold: true, color: C.ambarP });
s.addNotes("Se usan sobre todo cuando hay datos para ajustar. LOGNORMAL se parametriza con media y desviación de los valores reales (no del logaritmo).");

// 22. Extremos
s = nueva("4 · Familia «colas extremas»", "GUMBEL y PARETO", "Para eventos donde lo raro puede ser enorme: reclamos, siniestros, lluvias máximas.");
curvas(s, grid(0, 60, 150), [{ name: "GUMBEL 15 / 6", f: pdf.gumbel(15, 6), color: C.azul }],
  { x: M, y: 2.1, w: 6.0, h: 3.6, titulo: "GUMBEL 15 / 6: días perdidos por lluvia máxima", ejeX: "Días", extra: { catAxisMajorUnit: 10 } });
curvas(s, grid(0, 800, 400), [{ name: "PARETO 2,5 / 100 000", f: pdf.pareto(2.5, 100), color: C.rojo }],
  { x: 6.8, y: 2.1, w: 5.9, h: 3.6, titulo: "PARETO 2,5 / 100 000: monto de un reclamo", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 100 } });
txt(s, "GUMBEL — P1 ubicación · P2 escala. El «máximo de muchos eventos» (el peor aguacero del año).", { x: M, y: 5.85, w: 6.0, h: 0.8, fontSize: 13 });
txt(s, "PARETO — P1 forma (> 1) · P2 mínimo. Pocos casos muy grandes; con forma ≤ 2 la dispersión es enorme.", { x: 6.8, y: 5.85, w: 5.9, h: 0.8, fontSize: 13 });
s.addNotes("Estas distribuciones dominan el P90–P99. Úselas solo si el comportamiento extremo es real, porque pueden inflar la contingencia.");

// 23. Conteos
s = nueva("4 · Familia «conteos»", "POISSON y BINOMIAL", "Entregan un número entero de eventos. El valor sorteado es el impacto, en la unidad de la dimensión.");
const pois = [], lp = [], lam = 3; let pk = Math.exp(-lam);
for (let k = 0; k <= 9; k++) { lp.push(String(k)); pois.push(Math.round(pk * 1000) / 1000); pk = pk * lam / (k + 1); }
barras(s, lp, pois, C.azul, { x: M, y: 2.1, w: 6.0, h: 3.4, titulo: "POISSON media 3: eventos en el periodo", valores: true, ejeX: "Número de eventos" });
const bin = [], lb = []; const nB = 40, pB = 0.15;
const comb = (n, k) => Math.exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1));
for (let k = 0; k <= 14; k++) { lb.push(String(k)); bin.push(Math.round(comb(nB, k) * pB ** k * (1 - pB) ** (nB - k) * 1000) / 1000); }
barras(s, lb, bin, C.naranja, { x: 6.8, y: 2.1, w: 5.9, h: 3.4, titulo: "BINOMIAL 40 / 0,15: submittals rechazados", ejeX: "Rechazos de 40" });
tarjeta(s, M, 5.7, W - 2 * M, 1.1, C.tinte);
txt(s, "Úselas cuando la unidad de la dimensión SEA el conteo: por ejemplo, días perdidos = número de días de lluvia fuerte, o una dimensión nueva «NCR» agregada con ＋ AGREGAR DIMENSIÓN. Si cada evento cuesta S/ X, modele el costo total con PERT, porque la macro no multiplica conteo × costo.",
  { x: M + 0.25, y: 5.78, w: W - 2 * M - 0.5, h: 0.95, fontSize: 13.5, valign: "middle" });
s.addNotes("POISSON: P1 media de eventos. BINOMIAL: P1 número de intentos n, P2 probabilidad p de cada uno.");

// 24-25. Catálogo completo
const catalogo = [
  ["CONSTANTE", "Valor", "", "", "", "Impacto conocido con certeza"],
  ["UNIFORME", "Mínimo", "Máximo", "", "", "Solo un rango, sin valor típico"],
  ["TRIANGULAR", "Mínimo", "Moda", "Máximo", "", "Tres puntos, conservadora"],
  ["TRIGEN", "Valor bajo", "Moda", "Valor alto", "% bajo (10)", "Tres puntos como P10 / P90"],
  ["PERT", "Mínimo", "Moda", "Máximo", "", "Tres puntos (recomendada)"],
  ["PERT_MODIFICADA", "Mínimo", "Moda", "Máximo", "γ (4 = PERT)", "PERT con confianza ajustable"],
  ["BETA_GENERAL", "α", "β", "Mínimo", "Máximo", "Ajuste a datos con límites"],
  ["NORMAL", "Media", "Desv. estándar", "", "", "Simétrica; admite negativos"],
  ["NORMAL_TRUNCADA", "Media", "Desv. estándar", "Mínimo", "Máximo", "Normal con límites"],
  ["LOGNORMAL", "Media", "Desv. estándar", "", "", "Sesgada, positiva, cola larga"],
  ["GAMMA", "Forma", "Escala", "", "", "Sesgada, positiva"],
  ["EXPONENCIAL", "Media", "", "", "", "Muchos pequeños, pocos grandes"],
  ["WEIBULL", "Forma k", "Escala λ", "", "", "Fallas y duración de equipos"],
  ["GUMBEL", "Ubicación", "Escala", "", "", "Máximos: lluvias, crecidas"],
  ["LOGISTICA", "Media", "Escala", "", "", "Como normal, colas más pesadas"],
  ["PARETO", "Forma (> 1)", "Mínimo", "", "", "Colas muy pesadas: reclamos"],
  ["POISSON", "Media λ", "", "", "", "Número de eventos en el periodo"],
  ["BINOMIAL", "n (ensayos)", "p", "", "", "Fallas en n intentos"],
  ["DISCRETA_UNIFORME", "Mín. (entero)", "Máx. (entero)", "", "", "Entero equiprobable"],
  ["DISCRETA", "«v1;v2;…»", "«p1;p2;…»", "", "", "Escenarios con probabilidad"],
];
[[0, 10], [10, 20]].forEach(([i0, i1], k) => {
  s = nueva("4 · Resumen", `Catálogo: qué va en P1…P4 (${k + 1} de 2)`, "Las mismas definiciones aparecen en la columna AYUDA_ del registro y en la hoja GUIA.");
  tabla(s, [["Distribución", "P1", "P2", "P3", "P4", "Cuándo usarla"]].concat(catalogo.slice(i0, i1)),
    { x: M, y: 2.05, w: W - 2 * M, colW: [2.4, 1.6, 1.6, 1.4, 1.5, 3.63], rowH: 0.42, fs: 13, fsCab: 13, primeraNegrita: true });
  s.addNotes("P1…P4 vacíos donde la distribución no los usa. La validación marca en rojo parámetros faltantes o incoherentes (mín. > moda, desviación ≤ 0, probabilidades que no suman 1…).");
});

// 26. Divisor
s = oscura();
txt(s, "PARTE 5", { x: M, y: 2.4, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Casos especiales al llenar el registro", { x: M, y: 2.85, w: 12, h: 0.9, fontSize: 40, bold: true, color: C.blanco });
txt(s, "Varias dimensiones, oportunidades, respuestas y correlación", { x: M, y: 3.8, w: 12, h: 0.5, fontSize: 18, color: C.grisC });

// 27. Dimensiones
s = nueva("5 · Dimensiones", "Una distribución por cada dimensión que el riesgo afecte", "Se deja la distribución VACÍA en las dimensiones que el riesgo no toca. Ejemplos tomados del registro (estimaciones preliminares).");
const dims = [
  ["COSTO", "S/", C.naranja, "R-01 Consumo de contingencia", "PERT 1 500 000 / 4 000 000 / 9 000 000", "Sobrecostos directos: material, mano de obra, penalidades."],
  ["PLAZO", "días", C.azul, "R-05 Demora aprobación UMAS", "TRIANGULAR 15 / 30 / 60", "Días de retraso. La macro los SUMA: supuesto conservador."],
  ["ING_DISENO", "HH", C.ambarP, "R-05 Demora aprobación UMAS", "TRIANGULAR 120 / 300 / 600", "Horas-hombre adicionales de ingeniería de diseño (rediseño, RFI)."],
  ["ING_CAMPO", "HH", C.panel, "R-06 NC en tarrajeo y solaqueo", "TRIANGULAR 200 / 500 / 1 200", "Horas-hombre de ingeniería de campo (supervisión, reprocesos)."],
];
dims.forEach((d, i) => {
  const x = M + i * 3.07;
  tarjeta(s, x, 2.2, 2.9, 4.1, C.tinte2);
  circulo(s, x + 0.2, 2.4, 0.6, d[1], d[2], C.blanco);
  txt(s, d[0], { x: x + 0.95, y: 2.45, w: 1.9, h: 0.5, fontSize: 16, bold: true, valign: "middle" });
  txt(s, d[5], { x: x + 0.2, y: 3.2, w: 2.55, h: 1.1, fontSize: 12.5 });
  txt(s, d[3], { x: x + 0.2, y: 4.45, w: 2.55, h: 0.6, fontSize: 12, bold: true, color: C.gris });
  txt(s, d[4], { x: x + 0.2, y: 5.1, w: 2.55, h: 0.9, fontSize: 12.5, bold: true, color: C.ambarP });
});
txt(s, "No duplicar: si las HH ya están valorizadas dentro de COSTO, no las ingrese además en ING_DISENO / ING_CAMPO (o viceversa). ＋ AGREGAR DIMENSIÓN crea otras (calidad, SSOMA…) sin tocar el código.",
  { x: M, y: 6.45, w: W - 2 * M, h: 0.7, fontSize: 13, bold: true });
s.addNotes("R-05 afecta tres dimensiones a la vez: cuando ocurre, las tres reciben impacto en la misma iteración.");

// 28. Oportunidades y respuestas
s = nueva("5 · Oportunidades y respuestas", "Oportunidades y riesgo residual");
tarjeta(s, M, 1.75, 5.9, 4.9, C.tinte2);
circulo(s, M + 0.25, 1.95, 0.6, "+", C.verde, C.negro);
txt(s, "Oportunidades", { x: M + 1.05, y: 2.0, w: 4.5, h: 0.5, fontSize: 18, bold: true, valign: "middle" });
bullets(s, ["TIPO = OPORTUNIDAD.", "Los parámetros se ingresan POSITIVOS (ahorro de 100 000 a 300 000).",
  "La macro les aplica signo negativo: reducen el total.", "Se marcan en verde en TORNADO, RANGOS y MATRIZ_PI."],
  { x: M + 0.3, y: 2.8, w: 5.3, h: 3.6, fontSize: 14 });
tarjeta(s, 6.8, 1.75, 5.9, 4.9, C.tinte2);
circulo(s, 7.05, 1.95, 0.6, "↓", C.azul, C.blanco);
txt(s, "Respuestas (escenario «después»)", { x: 7.85, y: 2.0, w: 4.7, h: 0.5, fontSize: 18, bold: true, valign: "middle" });
tabla(s, [["Columna", "Qué significa"],
  ["ESTRATEGIA", "Evitar, mitigar, transferir, aceptar… (PMI)"],
  ["PROB_RESIDUAL", "Probabilidad tras la respuesta"],
  ["FACTOR_IMPACTO_RESIDUAL", "0,5 = el impacto baja a la mitad"],
  ["COSTO_RESPUESTA", "Lo que cuesta implementar la respuesta (S/)"]],
  { x: 7.1, y: 2.8, w: 5.3, colW: [2.4, 2.9], rowH: 0.48, fs: 12, primeraNegrita: true });
txt(s, "La distribución NO se reescribe: el factor la escala. COMPARACION muestra antes vs. después con los mismos números aleatorios.",
  { x: 7.1, y: 5.35, w: 5.3, h: 1.1, fontSize: 13, color: C.gris });
s.addNotes("La respuesta conviene si la reducción del P80 (o de la media) supera su costo. Con números aleatorios comunes, la diferencia se debe solo a la respuesta, no al azar.");

// 29. Correlación
s = nueva("5 · Correlación", "Riesgos que se mueven juntos", "Si una misma causa agrava varios riesgos, deben simularse correlacionados.");
bullets(s, [
  "GRUPO_CORRELACION: nombre común a los riesgos relacionados (ej. APROBACIONES, CALIDAD, CONTRACTUAL).",
  "RHO_GRUPO: intensidad entre 0 y 1. Guía: 0,3 débil · 0,5 moderada · 0,7 fuerte.",
  "Efecto: cuando uno sale alto, los demás del grupo tienden a salir altos. La media no cambia, pero el P80 y el P90 suben.",
  "Ignorar una correlación real subestima la contingencia.",
  "RESULTADOS muestra la correlación objetivo vs. lograda. Con probabilidades < 1 la lograda es menor, porque muchos escenarios valen 0.",
], { x: M, y: 2.2, w: 6.8, h: 4.5, fontSize: 15 });
tabla(s, [["Grupo", "ρ objetivo", "ρ lograda"],
  ["CONTRACTUAL", "0,50", "0,41"], ["SOBRECONSUMO", "0,40", "0,34"], ["APROBACIONES", "0,50", "0,45"],
  ["CALIDAD", "0,40", "0,30"], ["INGENIERIA", "0,50", "0,44"], ["EXTENSION_PLAZO", "0,60", "0,50"]],
  { x: 7.9, y: 2.25, w: 4.8, colW: [2.2, 1.3, 1.3], rowH: 0.45, fs: 13, primeraNegrita: true });
pie(s, "Método Iman–Conover con un factor común por grupo (Vose 13.2). Valores de una corrida de prueba con las estimaciones preliminares.");
s.addNotes("La correlación no cambia la probabilidad ni la distribución de cada riesgo, solo cómo se combinan los valores altos y bajos.");

// 30. Errores frecuentes
s = nueva("5 · Checklist", "Errores frecuentes al llenar distribuciones");
const errores = [
  ["Probabilidad dentro del impacto", "Poner el 30 % del costo como impacto. La probabilidad va SOLO en PROBABILIDAD."],
  ["Peor caso como moda", "La moda es lo más frecuente, no lo más temido."],
  ["Mezclar unidades", "Soles vs. miles de soles; días hábiles vs. calendario; HH vs. días-hombre."],
  ["Duplicar impactos", "HH valorizadas en COSTO y además en ING_DISENO / ING_CAMPO."],
  ["Orden incoherente", "Mínimo > moda o moda > máximo: la validación lo marca en rojo."],
  ["Probabilidad mal usada", "1 a un evento que puede no ocurrir; > 0,5 a algo casi seguro (mejor en la línea base)."],
];
errores.forEach((e, i) => {
  const x = M + (i % 2) * 6.15, y = 1.75 + Math.floor(i / 2) * 1.7;
  tarjeta(s, x, y, 5.95, 1.5, C.tinte2);
  circulo(s, x + 0.2, y + 0.2, 0.5, "✕", C.rojo, C.negro);
  txt(s, e[0], { x: x + 0.9, y: y + 0.22, w: 4.9, h: 0.45, fontSize: 15, bold: true, valign: "middle" });
  txt(s, e[1], { x: x + 0.9, y: y + 0.72, w: 4.9, h: 0.7, fontSize: 13, color: C.gris });
});
s.addNotes("La validación detecta los errores de forma (orden, faltantes), pero no los de concepto (unidades, duplicados). Esos dependen de quien llena el registro.");

// 31. Divisor
s = oscura();
txt(s, "PARTE 6", { x: M, y: 2.4, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Ejecutar e interpretar", { x: M, y: 2.85, w: 12, h: 0.9, fontSize: 40, bold: true, color: C.blanco });
txt(s, "Botones, validación y cómo leer los resultados", { x: M, y: 3.8, w: 12, h: 0.5, fontSize: 18, color: C.grisC });

// 32. Botones y validación
s = nueva("6 · Ejecutar", "Botones y validación");
const botones = [
  ["▶ CORRER SIMULACIÓN", "Valida, simula y escribe todas las hojas de resultados."],
  ["✔ VALIDAR DATOS", "Revisa el registro sin simular y marca las celdas con problemas."],
  ["✕ LIMPIAR RESULTADOS", "Borra las hojas de salida (no toca PARAMETROS)."],
  ["＋ AGREGAR DIMENSIÓN", "Crea una dimensión nueva: columnas DIST_, P1…P4 y AYUDA_."],
];
botones.forEach((b, i) => {
  const y = 1.8 + i * 1.05;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: 3.6, h: 0.75, rectRadius: 0.1, fill: { color: C.negro }, line: { color: C.negro } });
  txt(s, b[0], { x: M, y, w: 3.6, h: 0.75, fontSize: 14, bold: true, color: C.ambar, align: "center", valign: "middle" });
  txt(s, b[1], { x: M + 3.85, y, w: 4.0, h: 0.75, fontSize: 13, valign: "middle" });
});
tarjeta(s, 8.8, 1.8, 3.9, 1.95, C.rojo);
txt(s, "ROJO = error", { x: 9.0, y: 1.95, w: 3.5, h: 0.4, fontSize: 16, bold: true });
txt(s, "Impide correr: parámetro faltante, mín. > moda, probabilidad fuera de 0–1, texto donde va número…", { x: 9.0, y: 2.4, w: 3.5, h: 1.3, fontSize: 12.5 });
tarjeta(s, 8.8, 3.95, 3.9, 1.95, "FFB020");
txt(s, "ÁMBAR = advertencia", { x: 9.0, y: 4.1, w: 3.5, h: 0.4, fontSize: 16, bold: true });
txt(s, "Permite correr, pero revise: probabilidad > 0,5, riesgo sin impacto, estimado por validar…", { x: 9.0, y: 4.55, w: 3.5, h: 1.3, fontSize: 12.5 });
txt(s, "Si aparece un aviso ámbar «No se pudo crear el gráfico», los números siguen siendo válidos; envíe una captura del aviso para corregirlo.",
  { x: M, y: 6.25, w: W - 2 * M, h: 0.6, fontSize: 13, italic: true, color: C.gris });
s.addNotes("Filas con ACTIVO = NO se ignoran. Los 5 riesgos EJEMPLO de la versión 1 están desactivados.");

// 33. Curva S y contingencia
s = nueva("6 · Interpretar", "Curva S y contingencia", "La reserva para contingencias es el P(nivel) del impacto total de los riesgos. Con nivel 80 %: el P80.");
const pctLabels = [], pctVals = [];
sim.pct.forEach((v, i) => { pctLabels.push(v / 1e6); pctVals.push(i * 5); });
s.addChart(pres.charts.SCATTER, [{ name: "X", values: pctLabels.map(r3) }, { name: "Costo", values: pctVals }], {
  x: M, y: 2.1, w: 7.0, h: 4.5, lineSize: 3, lineDataSymbol: "none", chartColors: [C.naranja], showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20, showValAxisTitle: true, valAxisTitle: "% acumulado", valAxisTitleFontSize: 11, valAxisTitleColor: C.gris, valAxisLabelColor: C.gris, valAxisLabelFontSize: 11,
  valGridLine: { color: "E0E0E0", size: 0.5 }, catGridLine: { style: "none" }, catAxisMinVal: 0, catAxisMaxVal: 45, catAxisMajorUnit: 5,
  catAxisLabelColor: C.gris, catAxisLabelFontSize: 11, showCatAxisTitle: true, catAxisTitle: "Impacto total de los riesgos en costo (millones S/)",
  catAxisTitleFontSize: 11, catAxisTitleColor: C.gris, showTitle: true, title: "Curva S — costo", titleFontSize: 13, titleFontFace: F });
const kpis = [["P50", "15,7 M", "Mitad de los escenarios por debajo"], ["P80", "21,3 M", "Reserva para contingencias (10,7 % de la base)"], ["P90", "24,7 M", "Nivel más exigente: +3,3 M"]];
kpis.forEach((k, i) => {
  const y = 2.1 + i * 1.3;
  tarjeta(s, 7.9, y, 4.8, 1.15, i === 1 ? C.ambar : C.tinte2);
  txt(s, k[0], { x: 8.1, y: y + 0.1, w: 1.0, h: 0.9, fontSize: 18, bold: true, valign: "middle" });
  txt(s, "S/ " + k[1], { x: 9.0, y: y + 0.05, w: 3.5, h: 0.55, fontSize: 24, bold: true });
  txt(s, k[2], { x: 9.0, y: y + 0.62, w: 3.6, h: 0.45, fontSize: 12, color: C.gris });
});
txt(s, "Presupuesto recomendado = base + contingencia + reserva de gestión = 200 + 21,3 + 0 = S/ 221,3 M",
  { x: 7.9, y: 6.05, w: 4.8, h: 0.7, fontSize: 13, bold: true });
pie(s, "Cifras de una corrida de prueba con estimaciones preliminares y base supuesta de S/ 200 M. No sumar los P80 de cada riesgo: la contingencia es el P80 del TOTAL.");
s.addNotes("Variante de Vose: presupuestar la media (≈ S/ 16,2 M) como partida de riesgos y el colchón P80 − media (≈ S/ 5,1 M) como contingencia. El total es el mismo.");

// 34. Otras hojas
s = nueva("6 · Interpretar", "Qué pregunta responde cada hoja de resultados");
const preg = [
  ["RESULTADOS", "¿Cuánta reserva necesito y qué tan precisa es la simulación?"],
  ["CURVA_S", "¿Con qué probabilidad no supero cada monto o plazo?"],
  ["TORNADO", "¿Qué riesgos mueven más el total? → dónde enfocar las respuestas"],
  ["RANGOS", "¿Cuál es el P10…P90 y el VME de cada riesgo?"],
  ["MATRIZ_PI", "¿Cómo se ven los riesgos en la matriz probabilidad–impacto?"],
  ["COMPARACION", "¿Cuánto baja el P80 si aplico las respuestas, y compensa su costo?"],
];
preg.forEach((p, i) => {
  const y = 1.8 + i * 0.83;
  tarjeta(s, M, y, 3.0, 0.68, C.negro);
  txt(s, p[0], { x: M, y, w: 3.0, h: 0.68, fontSize: 15, bold: true, color: C.ambar, align: "center", valign: "middle" });
  txt(s, p[1], { x: M + 3.3, y, w: 8.8, h: 0.68, fontSize: 15, valign: "middle" });
});
pie(s, "Precisión: si RESULTADOS indica «Insuficiente» en el intervalo del P80, aumente las iteraciones.");
s.addNotes("El tornado usa correlación de rangos (Spearman) y el «swing»: cuánto cambia el total cuando el riesgo está en su 10 % alto vs. su 10 % bajo.");

// 35. Cierre
s = oscura();
txt(s, "ANTES DE PRESENTAR RESULTADOS", { x: M, y: 0.9, w: 11, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Checklist final", { x: M, y: 1.35, w: 11, h: 0.8, fontSize: 36, bold: true, color: C.blanco });
const check = [
  "Costo base y plazo base reemplazados por los del contrato (hoy son supuestos).",
  "Cada estimación «ESTIMADO – VALIDAR» revisada con el dueño del riesgo; fuente anotada en NOTAS.",
  "Distribución elegida según lo que se sabe (árbol de decisión); PERT por defecto.",
  "Probabilidad separada del impacto; unidades revisadas; sin impactos duplicados.",
  "Correlación definida para los riesgos con causa común.",
  "Validación sin errores rojos; advertencias ámbar revisadas.",
  "Precisión «Suficiente» en RESULTADOS.",
];
check.forEach((c, i) => {
  const y = 2.45 + i * 0.63;
  circulo(s, M, y, 0.42, "✓", C.ambar, C.negro);
  txt(s, c, { x: M + 0.65, y: y - 0.02, w: 11.5, h: 0.5, fontSize: 16, color: C.blanco, valign: "middle" });
});
s.addNotes("La herramienta es tan buena como los datos: el trabajo de fondo es la elicitación de distribuciones con los dueños de los riesgos.");

pres.writeFile({ fileName: process.argv[2] || "Guia_Uso_MonteCarlo.pptx" }).then(f => console.log("OK", f));
