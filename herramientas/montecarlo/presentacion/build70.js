// Guía extendida (70 láminas) de la macro Montecarlo. Cada lámina lleva su narración
// (notas del orador), que también se exporta a narracion.json para el video.
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const sim = JSON.parse(fs.readFileSync(__dirname + "/sim.json", "utf8"));

const C = {
  negro: "000000", ambar: "FFA028", blanco: "FFFFFF", gris: "333333", grisM: "6B6B6B",
  grisC: "EDEDED", tinte: "FFF0D6", tinte2: "FFF7EB", naranja: "FF6600", azul: "0068FF",
  verde: "00C805", rojo: "FF433D", teal: "4AF6C3", ambarP: "CC7A00", panel: "2A2A2A", amarillo: "FFB020",
};
const F = "Arial";
const W = 13.333, H = 7.5, M = 0.6;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Guía extendida — Simulación Montecarlo de riesgos";

// ---------- Matemática ----------
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
  truncN: (mu, s, a, b) => x => x < a || x > b ? 0 : Math.exp(-0.5 * ((x - mu) / s) ** 2),
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
function trigen(lo, m, hi, p) {
  let a = lo - 1, b = hi + 1;
  for (let i = 0; i < 300; i++) { a = lo - Math.sqrt(p * (b - a) * (m - a)); b = hi + Math.sqrt(p * (b - a) * (b - m)); }
  return [a, b];
}
// media y percentiles numéricos de una densidad
function stats(f, a, b) {
  const n = 20000, h = (b - a) / n; let tot = 0, mu = 0; const cdf = [0];
  for (let i = 1; i <= n; i++) { const x0 = a + (i - 1) * h, x1 = a + i * h; const v0 = f(x0), v1 = f(x1);
    const ar = (isFinite(v0) ? v0 : 0) / 2 * h + (isFinite(v1) ? v1 : 0) / 2 * h; tot += ar; mu += ar * (x0 + x1) / 2; cdf.push(tot); }
  return { media: mu / tot, q: p => { for (let i = 0; i <= n; i++) if (cdf[i] / tot >= p) return a + i * h; return b; } };
}
const fmt = (v, d = 0) => { const s = Math.abs(v).toFixed(d).split("."); const ent = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return (v < 0 ? "−" : "") + ent + (d > 0 ? "," + s[1] : ""); };

// ---------- Diseño ----------
const narr = [];
let num = 0;
function txt(s, t, o) { s.addText(t, Object.assign({ fontFace: F, isTextBox: true, color: C.negro, fontSize: 14, valign: "top", margin: 0 }, o)); }
function numero(s, oscuro) { txt(s, String(num), { x: W - 1.1, y: H - 0.45, w: 0.6, h: 0.3, fontSize: 10, color: oscuro ? C.grisM : C.grisM, align: "right" }); }
function nueva(tag, t, sub) {
  const s = pres.addSlide(); s.background = { color: C.blanco }; num++;
  txt(s, tag.toUpperCase(), { x: M, y: 0.35, w: 10, h: 0.3, fontSize: 11, bold: true, color: C.ambarP, charSpacing: 2 });
  txt(s, t, { x: M, y: 0.62, w: W - 2 * M, h: 0.72, fontSize: 28, bold: true, valign: "middle" });
  if (sub) txt(s, sub, { x: M, y: 1.36, w: W - 2 * M, h: 0.62, fontSize: 14.5, color: C.gris });
  numero(s); return s;
}
function oscura() { const s = pres.addSlide(); s.background = { color: C.negro }; num++; numero(s, true); return s; }
function divisor(parte, t, sub, lista) {
  const s = oscura();
  txt(s, parte, { x: M, y: 1.6, w: 6, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
  txt(s, t, { x: M, y: 2.05, w: 12, h: 0.9, fontSize: 38, bold: true, color: C.blanco });
  txt(s, sub, { x: M, y: 3.0, w: 11.5, h: 0.8, fontSize: 17, color: C.grisC });
  if (lista) lista.forEach((l, i) => {
    circulo(s, M, 4.1 + i * 0.52, 0.36, i + 1, C.ambar, C.negro);
    txt(s, l, { x: M + 0.55, y: 4.1 + i * 0.52, w: 11, h: 0.36, fontSize: 14, color: C.blanco, valign: "middle" });
  });
  return s;
}
function circulo(s, x, y, d, n, fill, col) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill || C.ambar }, line: { color: fill || C.ambar } });
  txt(s, String(n), { x, y, w: d, h: d, align: "center", valign: "middle", bold: true, fontSize: d > 0.6 ? 18 : (d > 0.45 ? 13 : 11), color: col || C.negro });
}
function tarjeta(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.tinte2 }, line: { color: fill || C.tinte2 } });
}
function caja(s, x, y, w, h, titulo, cuerpo, o) {
  o = o || {}; tarjeta(s, x, y, w, h, o.fill || C.tinte2);
  const col = o.oscuro ? C.blanco : C.negro;
  txt(s, titulo, { x: x + 0.2, y: y + 0.14, w: w - 0.4, h: 0.38, fontSize: o.ft || 15, bold: true, color: o.oscuro ? C.ambar : (o.colT || C.negro) });
  txt(s, cuerpo, { x: x + 0.2, y: y + 0.55, w: w - 0.4, h: h - 0.65, fontSize: o.fs || 13, color: o.oscuro ? C.grisC : (o.colC || C.gris) });
}
function pie(s, t) { txt(s, t, { x: M, y: H - 0.5, w: W - 2 * M - 0.8, h: 0.35, fontSize: 10, color: C.grisM, italic: true }); }
function bullets(s, items, o) {
  s.addText(items.map((it, i) => ({ text: it, options: { bullet: true, breakLine: i < items.length - 1 } })),
    Object.assign({ fontFace: F, isTextBox: true, fontSize: 14, color: C.negro, paraSpaceAfter: 7, valign: "top", margin: 0 }, o));
}
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
function narrar(s, texto) { s.addNotes(texto); narr.push({ lamina: num, texto }); }

// =====================================================================
// PARTE 0 — Introducción
let s = oscura();
txt(s, "ANÁLISIS CUANTITATIVO DE RIESGOS", { x: M, y: 1.4, w: 11, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Simulación Montecarlo en Excel", { x: M, y: 1.9, w: 12, h: 1.0, fontSize: 44, bold: true, color: C.blanco });
txt(s, "Guía extendida de uso de la macro MonteCarlo_Riesgos.xlsm", { x: M, y: 2.95, w: 11, h: 0.5, fontSize: 22, color: C.grisC });
txt(s, "Con énfasis en la parte conceptual: qué es una distribución, cómo se elige y cómo se llena cada una de las 20 disponibles.", { x: M, y: 3.6, w: 10.5, h: 0.9, fontSize: 16, color: C.grisC });
txt(s, "Costo · Plazo · Ingeniería de diseño · Ingeniería de campo", { x: M, y: 5.9, w: 11, h: 0.4, fontSize: 14, color: C.ambar });
narrar(s, "Bienvenidos. En esta guía vamos a aprender a usar la herramienta de simulación Montecarlo para el análisis cuantitativo de riesgos del proyecto. La herramienta es un libro de Excel con una macro incluida, y permite estimar la contingencia de costo, de plazo y de horas hombre de ingeniería a partir del registro de riesgos. Pondremos especial atención en la parte conceptual, que es la más difícil: qué es una distribución de probabilidad, cómo se elige la adecuada para cada riesgo y qué número va en cada casilla.");

s = nueva("Introducción", "Qué podrá hacer al terminar esta guía", "La guía está pensada para quien llena el registro de riesgos y para quien presenta los resultados. No se necesita formación en estadística.");
[["Entender", "Qué es una distribución, por qué reemplaza a un número fijo y cómo la usa la macro en cada escenario."],
 ["Elegir", "La distribución adecuada para cada impacto según la información disponible, con un árbol de decisión."],
 ["Llenar", "Las columnas PROBABILIDAD, DIST_ y P1…P4 de las 20 distribuciones, con ejemplos de obra."],
 ["Ejecutar", "Validar los datos, correr la simulación y resolver los mensajes de error y advertencia."],
 ["Interpretar", "La curva S, el tornado y la tabla de reservas para proponer una contingencia justificada."],
 ["Mejorar", "Evaluar respuestas a los riesgos y ver cuánto reducen la contingencia frente a su costo."]].forEach((c, i) => {
  const x = M + (i % 3) * 4.1, y = 2.2 + Math.floor(i / 3) * 2.35;
  tarjeta(s, x, y, 3.9, 2.15, i === 0 ? C.tinte : C.tinte2);
  circulo(s, x + 0.2, y + 0.2, 0.55, i + 1);
  txt(s, c[0], { x: x + 0.95, y: y + 0.22, w: 2.8, h: 0.5, fontSize: 18, bold: true, valign: "middle" });
  txt(s, c[1], { x: x + 0.2, y: y + 0.9, w: 3.5, h: 1.15, fontSize: 13.5, color: C.gris });
});
narrar(s, "Al terminar, usted podrá hacer seis cosas. Primero, entender qué es una distribución y por qué es mejor que un número fijo. Segundo, elegir la distribución adecuada para cada impacto. Tercero, llenar correctamente la probabilidad y los parámetros pe uno a pe cuatro de las veinte distribuciones disponibles. Cuarto, validar y correr la simulación. Quinto, interpretar la curva S, el tornado y la tabla de reservas. Y sexto, evaluar si las respuestas a los riesgos valen lo que cuestan. No se necesita formación previa en estadística: cada concepto se explica con ejemplos de obra.");

s = nueva("Introducción", "Contenido de la guía");
const partes = [
  ["Conceptos de riesgo", "Amenaza, oportunidad, reservas, valor monetario esperado y la idea de simulación."],
  ["La herramienta", "Hojas del libro, configuración, dimensiones y columnas del registro."],
  ["La idea de distribución", "Probabilidad vs. impacto, qué hace la macro, cómo leer una distribución."],
  ["Cómo elegir", "Árbol de decisión, lenguaje del experto, elicitación, sesgos y datos históricos."],
  ["Las 20 distribuciones", "Una lámina por distribución: cuándo, parámetros, ejemplo y cuidados."],
  ["Casos especiales", "Dimensiones, oportunidades, respuestas, correlación y errores frecuentes."],
  ["Ejecutar e interpretar", "Validación, resultados, curva S, contingencia, tornado y comparación."],
];
partes.forEach((p, i) => {
  const y = 1.75 + i * 0.73;
  circulo(s, M, y, 0.55, i + 1, i === 2 || i === 3 || i === 4 ? C.ambar : C.grisC);
  txt(s, p[0], { x: M + 0.8, y: y + 0.02, w: 3.6, h: 0.5, fontSize: 17, bold: true, valign: "middle" });
  txt(s, p[1], { x: M + 4.5, y: y + 0.02, w: 7.6, h: 0.5, fontSize: 14, color: C.gris, valign: "middle" });
});
pie(s, "En ámbar: las partes conceptuales sobre distribuciones, que concentran la mayor parte de la guía.");
narrar(s, "La guía tiene siete partes. Empezamos con los conceptos de riesgo que usa la herramienta. Luego recorremos el libro de Excel y sus columnas. Las partes tres, cuatro y cinco, marcadas en ámbar, son el núcleo: la idea de distribución, cómo elegirla, y una lámina dedicada a cada una de las veinte distribuciones. Después vemos casos especiales, como oportunidades, respuestas y correlación. Y cerramos con la ejecución de la macro y la interpretación de los resultados, incluida la contingencia.");

s = nueva("Introducción", "¿Por qué simular y no sumar?", "Los métodos tradicionales de contingencia tienen problemas que la simulación resuelve.");
caja(s, M, 2.2, 3.85, 3.2, "Porcentaje fijo", "«Pongamos 10 % de contingencia.» No se relaciona con los riesgos reales del proyecto y no se puede defender ante el cliente o la gerencia.", { fill: C.grisC });
caja(s, M + 4.05, 2.2, 3.85, 3.2, "Suma de peores casos", "Sumar el máximo de cada riesgo supone que TODOS ocurren y en su peor versión a la vez. La cifra resulta exagerada e improbable.", { fill: C.grisC });
caja(s, M + 8.1, 2.2, 3.85, 3.2, "Suma de valores esperados", "Sumar probabilidad × impacto da el promedio, pero no dice cuánto margen hace falta para cubrir el 80 % de los casos.", { fill: C.grisC });
tarjeta(s, M, 5.6, W - 2 * M, 1.1, C.negro);
txt(s, "La simulación combina los riesgos como ocurren en la realidad (algunos sí, otros no, con impactos variables) y entrega la probabilidad de no superar cada monto. Así la contingencia se elige con un nivel de confianza explícito.",
  { x: M + 0.3, y: 5.7, w: W - 2 * M - 0.6, h: 0.9, fontSize: 14.5, color: C.blanco, valign: "middle" });
narrar(s, "¿Por qué simular y no simplemente sumar? Hay tres prácticas comunes con problemas. El porcentaje fijo, por ejemplo diez por ciento, no se relaciona con los riesgos reales y es difícil de defender. La suma de peores casos supone que todos los riesgos ocurren a la vez y en su peor versión, lo que da una cifra exagerada. Y la suma de valores esperados da el promedio, pero no dice cuánto margen se necesita para estar cubiertos con cierta seguridad. La simulación combina los riesgos como ocurren en la realidad y entrega la probabilidad de no superar cada monto.");

// PARTE 1 — Conceptos
s = divisor("PARTE 1", "Conceptos de riesgo", "El vocabulario del Estándar del PMI que usa la herramienta.",
  ["Amenazas y oportunidades", "Reservas para contingencias y de gestión", "Valor monetario esperado", "Qué es una simulación Montecarlo"]);
narrar(s, "Parte uno: conceptos de riesgo. Repasamos el vocabulario del estándar del PMI que usa la herramienta: amenazas y oportunidades, las dos reservas, el valor monetario esperado y la idea de la simulación Montecarlo.");

s = nueva("1 · Conceptos", "Riesgo: amenaza u oportunidad", "Un riesgo es un evento o condición incierta que, si ocurre, afecta al menos un objetivo del proyecto (PMI).");
caja(s, M, 2.2, 5.9, 2.4, "Amenaza (efecto negativo)", "Aumenta el costo, alarga el plazo o consume horas hombre adicionales.\nEjemplo: demora en la aprobación de planos por la Supervisión; no conformidades en tarrajeo.", { fill: C.tinte });
caja(s, M + 6.15, 2.2, 5.9, 2.4, "Oportunidad (efecto positivo)", "Reduce el costo o el plazo si ocurre.\nEjemplo: el proveedor adelanta la entrega de acero; se aprueba una ingeniería de valor.", { fill: C.tinte2 });
caja(s, M, 4.85, 5.9, 1.9, "Riesgo individual", "Cada fila del registro. Tiene causa, probabilidad, impacto y dueño.", { fill: C.grisC });
caja(s, M + 6.15, 4.85, 5.9, 1.9, "Riesgo general del proyecto", "El efecto combinado de toda la incertidumbre. Es lo que mide la simulación: la curva S del total.", { fill: C.grisC });
narrar(s, "Según el PMI, un riesgo es un evento o condición incierta que, si ocurre, afecta al menos un objetivo del proyecto. Puede ser una amenaza, que aumenta el costo o el plazo, o una oportunidad, que los reduce. Además, conviene distinguir el riesgo individual, que es cada fila del registro, del riesgo general del proyecto, que es el efecto combinado de toda la incertidumbre. La simulación mide precisamente ese riesgo general: su resultado principal es la curva S del total.");

s = nueva("1 · Conceptos", "Dos reservas distintas", "El presupuesto se arma por capas. La herramienta calcula la segunda y aplica la tercera como porcentaje.");
const capas = [["Línea base", "Costo y plazo del contrato sin riesgos (S/ 200 M y 730 días, supuestos).", C.grisC, 3.1],
  ["Reserva para contingencias", "Para los riesgos IDENTIFICADOS del registro. Se calcula con la simulación: el P80 del impacto total.", C.ambar, 1.6],
  ["Reserva de gestión", "Para lo NO previsto. No se simula: es un % de la base definido por la organización.", C.negro, 1.1]];
let yC = 5.9;
capas.forEach((c, i) => {
  const h = c[3] * 0.62; yC -= h;
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: yC, w: 4.2, h, fill: { color: c[2] }, line: { color: C.blanco, width: 2 } });
  txt(s, c[0], { x: M + 0.2, y: yC, w: 3.8, h, fontSize: 15, bold: true, valign: "middle", color: i === 2 ? C.ambar : C.negro });
  txt(s, c[1], { x: 5.2, y: yC + 0.05, w: 7.5, h: h - 0.05, fontSize: 14, valign: "middle" });
});
txt(s, "Presupuesto recomendado = línea base + reserva para contingencias + reserva de gestión", { x: M, y: 6.15, w: W - 2 * M, h: 0.45, fontSize: 15, bold: true });
narrar(s, "El presupuesto se construye por capas. Abajo está la línea base, que es el costo y el plazo del contrato sin considerar riesgos. Encima va la reserva para contingencias, que cubre los riesgos identificados en el registro. Esta es la que calcula la simulación, normalmente como el percentil ochenta del impacto total. Y arriba va la reserva de gestión, para lo no previsto, que no se simula porque por definición no conocemos esos riesgos: se fija como un porcentaje de la base. La suma de las tres capas es el presupuesto recomendado.");

s = nueva("1 · Conceptos", "Valor monetario esperado (VME)", "VME = probabilidad × impacto medio. Es el «costo promedio» de un riesgo si el proyecto se repitiera muchas veces.");
tabla(s, [["Riesgo", "Probabilidad", "Impacto medio", "VME"],
  ["R-11 Demora de aprobaciones", "0,55", "S/ 666 667", "S/ 366 667"],
  ["R-06 NC en tarrajeo", "0,35", "S/ 441 667", "S/ 154 583"],
  ["Oportunidad: entrega adelantada", "0,30", "− S/ 200 000", "− S/ 60 000"],
  ["Total", "", "", "S/ 461 250"]], { x: M, y: 2.2, w: 7.2, colW: [2.9, 1.3, 1.5, 1.5], rowH: 0.5, fs: 13, primeraNegrita: true });
caja(s, 8.1, 2.2, 4.6, 2.2, "Para qué sirve", "Ordenar riesgos por importancia y comprobar la simulación: la media simulada debe parecerse al VME total (RESULTADOS lo compara).");
caja(s, 8.1, 4.6, 4.6, 2.1, "Lo que NO dice", "Cuánto margen se necesita. El VME es un promedio: la mitad de las veces el proyecto lo supera. Por eso la contingencia se lee en la curva S.", { fill: C.tinte });
pie(s, "Impacto medio de PERT = (mínimo + 4 × moda + máximo) / 6. Ejemplo R-11: (200 000 + 4 × 600 000 + 1 400 000) / 6 = 666 667.");
narrar(s, "El valor monetario esperado, o VME, es la probabilidad por el impacto medio. Por ejemplo, si la demora de aprobaciones tiene cincuenta y cinco por ciento de probabilidad y un impacto medio de unos seiscientos sesenta y siete mil soles, su VME es de unos trescientos sesenta y siete mil soles. En las oportunidades el VME es negativo, porque reduce el total. El VME sirve para ordenar riesgos y para comprobar la simulación, pero no dice cuánto margen hace falta: es un promedio, y el proyecto lo supera en muchos casos. Por eso la contingencia se lee en la curva S.");

s = nueva("1 · Conceptos", "Qué es una simulación Montecarlo", "Se «juega» el proyecto miles de veces con dados cargados según las estimaciones, y se observa qué pasa.");
const conv = []; const labs = [];
[100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000].forEach(n => { labs.push(fmt(n)); conv.push(Math.round(1.96 * 0.6 / Math.sqrt(n) * 1000) / 10); });
barras(s, labs, conv, C.azul, { x: M, y: 2.2, w: 6.4, h: 4.0, titulo: "Error típico de la media (±%) según el número de iteraciones", valores: true, fmt: "0.0", ejeX: "Iteraciones" });
bullets(s, ["Cada iteración es un proyecto posible: se sortea qué riesgos ocurren y cuánto impactan.",
  "Con 10 000 iteraciones hay 10 000 totales posibles: su distribución es el resultado.",
  "El error baja con la raíz de N: para reducirlo a la mitad hacen falta 4 veces más iteraciones.",
  "La macro usa un generador de alta calidad (MRG32k3a) y una semilla: con la misma semilla se obtiene exactamente el mismo resultado."],
  { x: 7.3, y: 2.25, w: 5.4, h: 4.3, fontSize: 14 });
narrar(s, "Una simulación Montecarlo consiste en jugar el proyecto miles de veces. En cada iteración, la computadora sortea qué riesgos ocurren y cuánto impactan, según las estimaciones del registro. Con diez mil iteraciones obtenemos diez mil totales posibles, y su distribución es el resultado. La precisión mejora con la raíz cuadrada del número de iteraciones: para reducir el error a la mitad se necesitan cuatro veces más iteraciones. El gráfico muestra cómo el error baja rápidamente al principio y luego cada vez más lento. La macro usa un generador de números aleatorios de alta calidad y una semilla, de modo que con la misma semilla el resultado es reproducible.");

// PARTE 2 — Herramienta
s = divisor("PARTE 2", "La herramienta", "Cómo está organizado el libro y qué va en cada columna.",
  ["Flujo general y hojas", "Configuración y dimensiones", "Columnas del registro de riesgos"]);
narrar(s, "Parte dos: la herramienta. Veamos cómo está organizado el libro de Excel y qué información va en cada columna.");

s = nueva("2 · Herramienta", "Flujo general de trabajo");
const flujo = [["Registro", "Riesgos con probabilidad e impactos en PARAMETROS."], ["Distribuciones", "Cada impacto como rango, no como número."],
  ["Validación", "La macro revisa datos y marca errores."], ["10 000 escenarios", "Se juega el proyecto miles de veces."],
  ["Resultados", "Curva S, tornado, rangos, matriz."], ["Contingencia", "Se elige el nivel y se lee la reserva."]];
flujo.forEach((f, i) => {
  const x = M + i * 2.05, y = 1.9;
  tarjeta(s, x, y, 1.85, 2.5, i === 1 ? C.negro : C.tinte2);
  circulo(s, x + 0.18, y + 0.18, 0.5, i + 1);
  txt(s, f[0], { x: x + 0.15, y: y + 0.8, w: 1.6, h: 0.5, fontSize: 14, bold: true, color: i === 1 ? C.ambar : C.negro });
  txt(s, f[1], { x: x + 0.15, y: y + 1.3, w: 1.6, h: 1.1, fontSize: 12, color: i === 1 ? C.blanco : C.gris });
});
caja(s, M, 4.7, 5.9, 2.0, "Lo que hace usted", "Llenar el registro (pasos 1 y 2), pulsar los botones y leer los resultados. La calidad del resultado depende casi por completo de los pasos 1 y 2.", { fill: C.tinte });
caja(s, M + 6.15, 4.7, 5.9, 2.0, "Lo que hace la macro", "Valida, simula, calcula percentiles, sensibilidad, reservas y precisión, y escribe todas las hojas de resultados con sus gráficos.");
narrar(s, "El flujo tiene seis pasos. Usted registra los riesgos y describe cada impacto con una distribución. Luego la macro valida los datos, juega diez mil escenarios, escribe los resultados y calcula la contingencia al nivel elegido. Su trabajo está en los dos primeros pasos y en la lectura final. Y es importante saber que la calidad del resultado depende casi por completo de esos dos primeros pasos: la macro calcula bien, pero no puede corregir una estimación mal planteada.");

s = nueva("2 · Herramienta", "Las 11 hojas del libro", "Solo se ingresan datos en PARAMETROS. Las hojas de resultados se borran y reescriben en cada corrida.");
const hojas = [["INICIO", "Propósito, pasos, método y limitaciones."], ["GUIA", "Distribuciones para no especialistas: árbol, preguntas, catálogo y gráficos."],
  ["PARAMETROS", "Configuración, dimensiones, escalas y registro de riesgos."], ["RESULTADOS", "Estadísticas, reservas, precisión, advertencias y correlación lograda."],
  ["CURVA_S", "Probabilidad acumulada e histograma por dimensión."], ["TORNADO", "Riesgos ordenados por su influencia en el total."],
  ["RANGOS", "Mínimo, P10…P90, máximo, promedio y VME por riesgo."], ["MATRIZ_PI", "Matriz probabilidad–impacto 5×5 general y por dimensión."],
  ["COMPARACION", "Antes vs. después de las respuestas y beneficio neto."], ["SIMULACION", "Detalle de las primeras 5 000 iteraciones."],
  ["TEORIA", "Toda la teoría usada, con bibliografía."]];
hojas.forEach((h, i) => {
  const col = i % 4, fila = Math.floor(i / 4), x = M + col * 3.05, y = 2.15 + fila * 1.55;
  tarjeta(s, x, y, 2.85, 1.38, h[0] === "PARAMETROS" ? C.ambar : C.tinte2);
  txt(s, h[0], { x: x + 0.18, y: y + 0.14, w: 2.5, h: 0.36, fontSize: 15, bold: true });
  txt(s, h[1], { x: x + 0.18, y: y + 0.52, w: 2.5, h: 0.8, fontSize: 11.5, color: C.gris });
});
narrar(s, "El libro tiene once hojas. INICIO explica el propósito y los pasos. GUIA es la ayuda sobre distribuciones para no especialistas. PARAMETROS, en ámbar, es la única hoja donde se ingresan datos. Las demás las escribe la macro: RESULTADOS con las reservas, CURVA S, TORNADO, RANGOS, la matriz de probabilidad e impacto, COMPARACION de antes y después, el detalle de la SIMULACION y la hoja TEORIA con toda la base conceptual y la bibliografía.");

s = nueva("2 · Herramienta", "PARAMETROS: la zona de configuración", "Seis celdas con nombre que controlan toda la corrida.");
tabla(s, [["Celda", "Valor inicial", "Qué significa y cómo decidirlo"],
  ["Costo base (S/)", "200 000 000", "SUPUESTO. Reemplácelo por el costo del contrato; sirve para expresar la contingencia como % y para la reserva de gestión."],
  ["Plazo base (días)", "730", "SUPUESTO (24 meses). Reemplácelo por el plazo contractual."],
  ["Iteraciones", "10 000", "Entre 1 000 y 100 000. 10 000 es un buen equilibrio; suba si la precisión sale «Insuficiente»."],
  ["Semilla", "12345", "Número que fija los sorteos: misma semilla = mismos resultados. Vacía = resultados distintos en cada corrida."],
  ["Nivel de confianza", "80 %", "Entre 50 % y 95 %. Define la reserva (P80). Es una decisión de la empresa según su apetito de riesgo."],
  ["Reserva de gestión", "0 %", "Porcentaje de la base para lo no previsto. Solo se aplica a las dimensiones marcadas RESERVA_GESTION = SI."]],
  { x: M, y: 2.1, w: W - 2 * M, colW: [2.3, 1.6, 8.23], rowH: 0.58, fs: 13, primeraNegrita: true });
narrar(s, "En la parte superior de PARAMETROS hay seis celdas de configuración. El costo base y el plazo base vienen con valores supuestos de doscientos millones de soles y setecientos treinta días: deben reemplazarse por los del contrato. Las iteraciones, por defecto diez mil, controlan la precisión. La semilla permite repetir exactamente los mismos resultados; si se deja vacía, cada corrida será distinta. El nivel de confianza, ochenta por ciento por defecto, define la reserva para contingencias y es una decisión de la empresa. Y la reserva de gestión es un porcentaje de la base para lo no previsto.");

s = nueva("2 · Herramienta", "Tabla de dimensiones (tblDimensiones)", "Una dimensión es un tipo de impacto que se simula por separado: costo, plazo, horas hombre de diseño y de campo.");
tabla(s, [["CLAVE", "NOMBRE", "UNIDAD", "BASE", "ACTIVA", "RESERVA_GESTION", "COLOR"],
  ["COSTO", "Costo", "S/", "200 000 000", "SI", "SI", "#FF6600"],
  ["PLAZO", "Plazo", "días", "730", "SI", "NO", "#0068FF"],
  ["ING_DISENO", "Ingeniería de diseño", "HH", "—", "SI", "NO", "#CC7A00"],
  ["ING_CAMPO", "Ingeniería de campo", "HH", "—", "SI", "NO", "#2A2A2A"]],
  { x: M, y: 2.2, w: W - 2 * M, colW: [1.8, 2.6, 1.1, 1.9, 1.2, 2.1, 1.43], rowH: 0.45, fs: 13, primeraNegrita: true });
bullets(s, ["Cada dimensión tiene sus propias columnas en el registro: DIST_<CLAVE>, <CLAVE>_P1…P4 y AYUDA_<CLAVE>.",
  "ACTIVA = NO excluye la dimensión de la corrida sin borrar datos.",
  "Las dimensiones no se suman entre sí: cada una tiene su curva S y su reserva, en su propia unidad.",
  "Quedan 2 filas libres: el botón ＋ AGREGAR DIMENSIÓN crea, por ejemplo, CALIDAD o SSOMA con todas sus columnas."],
  { x: M, y: 4.65, w: W - 2 * M, h: 2.2, fontSize: 14 });
narrar(s, "La tabla de dimensiones define los tipos de impacto. Vienen cuatro: costo en soles, plazo en días, e ingeniería de diseño e ingeniería de campo en horas hombre. Cada dimensión tiene sus propias columnas en el registro de riesgos. Es importante entender que las dimensiones no se suman entre sí: cada una tiene su propia curva S y su propia reserva, en su propia unidad. Si necesita otra dimensión, como calidad o seguridad, el botón agregar dimensión la crea con todas sus columnas, sin tocar el código.");

s = nueva("2 · Herramienta", "Registro de riesgos: columnas de identificación", "Describen el riesgo. No entran al cálculo, salvo TIPO y ACTIVO, pero son esenciales para gestionarlo.");
tabla(s, [["Columna", "Qué va", "Ejemplo"],
  ["ID", "Código único", "R-05"],
  ["NOMBRE DEL RIESGO", "Evento, con su causa", "Demora en la aprobación de fabricación de UMAS - Debido al retraso en la verificación acústica…"],
  ["TIPO", "AMENAZA u OPORTUNIDAD", "AMENAZA (la oportunidad resta del total)"],
  ["CATEGORIA", "Agrupación para reportes", "APROBACIONES"],
  ["CAUSA", "Texto tras «Debido a»", "retraso en la verificación acústica…"],
  ["DUEÑO / ESTRATEGIA", "Responsable y respuesta PMI", "Ingeniería · MITIGAR"],
  ["ESTADO / ACTIVO", "Situación y si se simula", "ESTIMADO – VALIDAR · SI"]],
  { x: M, y: 2.15, w: W - 2 * M, colW: [2.6, 3.0, 6.53], rowH: 0.52, fs: 13, primeraNegrita: true });
narrar(s, "Las primeras columnas del registro identifican el riesgo: su código, su nombre con la causa, el tipo, la categoría, la causa, el dueño, la estrategia de respuesta y el estado. De ellas, solo dos entran al cálculo. TIPO, porque las oportunidades restan del total. Y ACTIVO, porque las filas con ACTIVO igual a NO se ignoran. Los treinta y dos riesgos del proyecto tienen estado estimado por validar: sus números son preliminares y deben revisarse con cada dueño.");

s = nueva("2 · Herramienta", "Registro de riesgos: columnas de cuantificación", "Aquí está el corazón del modelo. Las partes 3 a 5 de esta guía explican cómo llenarlas.");
[["PROBABILIDAD", "0 a 1. Chance de que el riesgo ocurra.", C.azul],
 ["DIST_COSTO", "Nombre de la distribución (menú de 20).", C.naranja],
 ["COSTO_P1…P4", "Parámetros de esa distribución.", C.naranja],
 ["AYUDA_COSTO", "Se llena solo: dice qué va en P1…P4.", C.grisM]].forEach((c, i) => {
  const x = M + i * 3.07;
  tarjeta(s, x, 2.15, 2.9, 1.7, C.tinte2);
  s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: 2.3, w: 0.3, h: 0.3, fill: { color: c[2] }, line: { color: c[2] } });
  txt(s, c[0], { x: x + 0.6, y: 2.27, w: 2.2, h: 0.36, fontSize: 14, bold: true });
  txt(s, c[1], { x: x + 0.2, y: 2.8, w: 2.55, h: 0.95, fontSize: 13, color: C.gris });
});
txt(s, "El mismo bloque DIST_ / P1…P4 / AYUDA_ se repite para PLAZO, ING_DISENO e ING_CAMPO. Si la distribución queda vacía, el riesgo no afecta esa dimensión.",
  { x: M, y: 4.05, w: W - 2 * M, h: 0.6, fontSize: 14, bold: true });
caja(s, M, 4.85, 5.9, 1.85, "Correlación", "GRUPO_CORRELACION y RHO_GRUPO: riesgos con causa común que tienden a salir altos juntos (parte 6).");
caja(s, M + 6.15, 4.85, 5.9, 1.85, "Respuesta", "PROB_RESIDUAL, FACTOR_IMPACTO_RESIDUAL y COSTO_RESPUESTA: el escenario «después» de aplicar la respuesta (parte 6).");
narrar(s, "Las columnas de cuantificación son el corazón del modelo. PROBABILIDAD es un número entre cero y uno. Luego, para cada dimensión, hay un bloque de columnas: DIST, con el nombre de la distribución elegida de un menú de veinte; pe uno a pe cuatro, con sus parámetros; y AYUDA, que se llena sola y dice qué va en cada parámetro. Si la distribución de una dimensión se deja vacía, el riesgo no afecta esa dimensión. Al final hay columnas para correlación y para evaluar respuestas, que veremos en la parte seis.");

// PARTE 3 — Distribución
s = divisor("PARTE 3", "La idea de distribución", "Lo más importante de la herramienta — y lo más difícil de entender. Vamos paso a paso.",
  ["De un número a un rango", "Probabilidad e impacto: dos preguntas", "Qué hace la macro en cada escenario", "Cómo leer una distribución"]);
narrar(s, "Parte tres: la idea de distribución. Esta es la parte más importante y también la más difícil de entender, así que iremos paso a paso, siempre con ejemplos de obra.");

const xsP = grid(150, 1500, 270);
s = nueva("3 · La idea", "De un número a un rango", "Una distribución describe lo que NO sabemos con exactitud: qué valores son posibles y cuáles son más probables.");
tarjeta(s, M, 2.2, 4.3, 4.4, C.grisC);
txt(s, "Estimado tradicional", { x: M + 0.3, y: 2.4, w: 3.8, h: 0.4, fontSize: 15, bold: true, color: C.gris });
txt(s, "S/ 600 000", { x: M + 0.3, y: 2.9, w: 3.8, h: 0.9, fontSize: 40, bold: true });
txt(s, "Un solo número. No dice qué tan seguro es, ni cuánto podría costar si sale mal. Da una falsa sensación de precisión: el costo real casi nunca será exactamente ese.",
  { x: M + 0.3, y: 3.95, w: 3.8, h: 2.4, fontSize: 14, color: C.gris });
curvas(s, xsP, [{ name: "PERT", f: pdf.pertG(200, 600, 1400, 4), color: C.naranja }],
  { x: 5.3, y: 2.15, w: 7.4, h: 3.5, titulo: "Estimado con distribución PERT: 200 / 600 / 1 400 miles de S/", ejeX: "Sobrecosto (miles de S/)", extra: { catAxisMajorUnit: 200 } });
txt(s, "Con tres números (mínimo 200 000, más probable 600 000, máximo 1 400 000) se describe todo el rango. La altura de la curva indica qué valores salen más a menudo: cerca de 600 000 es frecuente; cerca de 1 400 000 es raro pero posible.",
  { x: 5.3, y: 5.75, w: 7.4, h: 1.0, fontSize: 13.5 });
narrar(s, "Empecemos con la idea central. Tradicionalmente decimos: el sobrecosto será de seiscientos mil soles. Es un solo número, que no dice qué tan seguros estamos ni cuánto podría costar si las cosas salen mal. Una distribución describe lo que no sabemos: qué valores son posibles y cuáles son más probables. Con tres números, mínimo doscientos mil, más probable seiscientos mil y máximo un millón cuatrocientos mil, describimos todo el rango. La altura de la curva indica qué tan frecuente es cada valor: cerca de seiscientos mil es frecuente, y cerca del máximo es raro, pero posible.");

s = nueva("3 · La idea", "Qué representa una distribución", "No es un capricho estadístico: es la forma honesta de registrar lo que sabemos y lo que no.");
caja(s, M, 2.15, 3.85, 2.3, "Refleja conocimiento", "Un rango ancho significa que sabemos poco; un rango estrecho, que sabemos mucho. Ambos son válidos si son honestos.", { fill: C.tinte });
caja(s, M + 4.05, 2.15, 3.85, 2.3, "Se puede actualizar", "Cuando llega información (una cotización, un avance de obra), el rango se ajusta y se vuelve a simular.");
caja(s, M + 8.1, 2.15, 3.85, 2.3, "Se puede defender", "Cada número tiene una fuente: experto, histórico o cotización. Se anota en NOTAS.");
curvas(s, grid(0, 60, 240), [
  { name: "Sabemos poco: 10 / 25 / 55", f: pdf.pertG(10, 25, 55, 4), color: C.azul },
  { name: "Sabemos mucho: 20 / 25 / 32", f: pdf.pertG(20, 25, 32, 4), color: C.naranja }],
  { x: M, y: 4.6, w: W - 2 * M, h: 2.3, ejeX: "Días de retraso", extra: { catAxisMajorUnit: 5 } });
narrar(s, "¿Qué representa una distribución? Representa nuestro conocimiento. Si sabemos poco, el rango es ancho; si sabemos mucho, es estrecho. Ambos son válidos si son honestos. En el gráfico, la curva azul describe un retraso sobre el que sabemos poco, entre diez y cincuenta y cinco días, y la naranja uno que conocemos bien, entre veinte y treinta y dos días. La distribución se puede actualizar cuando llega información nueva, y se puede defender, porque cada número tiene una fuente que se anota en la columna de notas.");

s = nueva("3 · La idea", "Cada riesgo responde DOS preguntas distintas", "Van en columnas distintas y nunca se mezclan.");
[[M, "1", "¿Ocurre o no ocurre?", "Columna PROBABILIDAD", "Un número entre 0 y 1. Se aplica UNA sola vez al riesgo, para todas sus dimensiones.", "0,55 = 55 % de chance de que la Supervisión demore las aprobaciones.", C.azul],
 [6.9, "2", "Si ocurre, ¿cuánto impacta?", "Columnas DIST_ y P1…P4", "Una distribución por cada dimensión afectada. Describe el impacto COMPLETO, suponiendo que el riesgo ya ocurrió.", "COSTO PERT 200 000 / 600 000 / 1 400 000 · PLAZO TRIANGULAR 10 / 20 / 45 días.", C.naranja]]
  .forEach(([x, n, q, col, desc, ej, color]) => {
    tarjeta(s, x, 2.1, 5.8, 3.9, C.tinte2);
    circulo(s, x + 0.3, 2.3, 0.7, n, color, C.blanco);
    txt(s, q, { x: x + 1.2, y: 2.35, w: 4.4, h: 0.6, fontSize: 20, bold: true, valign: "middle" });
    txt(s, col, { x: x + 0.3, y: 3.2, w: 5.2, h: 0.4, fontSize: 15, bold: true, color: C.ambarP });
    txt(s, desc, { x: x + 0.3, y: 3.65, w: 5.2, h: 1.0, fontSize: 14 });
    txt(s, "Ejemplo R-11: " + ej, { x: x + 0.3, y: 4.75, w: 5.2, h: 1.1, fontSize: 13.5, color: C.gris });
  });
tarjeta(s, M, 6.15, W - 2 * M, 0.75, C.rojo);
txt(s, "Error típico: multiplicar la probabilidad por el impacto al ingresar los datos. La macro ya lo hace en cada escenario: el impacto se ingresa completo.",
  { x: M + 0.25, y: 6.15, w: W - 2 * M - 0.5, h: 0.75, fontSize: 14, bold: true, valign: "middle" });
narrar(s, "Cada riesgo responde dos preguntas distintas, y van en columnas distintas. La primera: ¿ocurre o no ocurre? Va en la columna probabilidad, como un número entre cero y uno. La segunda: si ocurre, ¿cuánto impacta? Va en la distribución de cada dimensión, y describe el impacto completo, suponiendo que el riesgo ya ocurrió. El error más común es multiplicar la probabilidad por el impacto al ingresar los datos. No lo haga: la macro ya lo hace en cada escenario. Si usted lo multiplica, el riesgo quedaría contado dos veces a la baja.");

s = nueva("3 · La idea", "Cómo estimar la probabilidad", "La probabilidad es la chance de que el evento ocurra durante el proyecto, una sola vez. Se puede partir de una escala verbal.");
tabla(s, [["Expresión", "Probabilidad", "Referencia"],
  ["Muy improbable", "0,05 – 0,10", "Ocurrió en muy pocos proyectos similares"],
  ["Poco probable", "0,10 – 0,30", "Ocurre a veces"],
  ["Tan probable como no", "0,30 – 0,50", "Ocurre en la mitad de los proyectos"],
  ["Probable", "0,50 – 0,70", "Suele ocurrir: evalúe incluirlo en la base"],
  ["Casi seguro", "> 0,70", "Mejor presupuestarlo en la línea base"]],
  { x: M, y: 2.2, w: 7.0, colW: [2.4, 1.6, 3.0], rowH: 0.52, fs: 13, primeraNegrita: true });
bullets(s, ["Use la frecuencia histórica cuando exista: 3 de 10 obras similares = 0,30.",
  "No ponga 0 (el riesgo no existe: desactívelo) ni 1 si puede no ocurrir.",
  "Si es > 0,50, la macro lo advierte en ámbar: el PMI sugiere incluir el evento en la línea base y dejar en el registro solo la variación.",
  "La probabilidad es por riesgo, no por dimensión: el mismo sorteo decide el costo y el plazo."],
  { x: 7.9, y: 2.25, w: 4.8, h: 4.5, fontSize: 13.5 });
narrar(s, "¿Cómo estimamos la probabilidad? Se puede partir de una escala verbal: muy improbable, entre cinco y diez por ciento; poco probable, hasta treinta; tan probable como no, hasta cincuenta; probable, hasta setenta; y casi seguro, por encima. Si hay datos históricos, úselos: si ocurrió en tres de diez obras similares, la probabilidad es cero coma tres. No ponga cero; si el riesgo no existe, desactívelo. Y si la probabilidad supera cincuenta por ciento, la macro lo advierte: conviene incluir el evento en la línea base. Recuerde que la probabilidad es una sola por riesgo, para todas sus dimensiones.");

s = nueva("3 · La idea", "Qué hace la macro en cada escenario", "Ejemplo con R-05 (demora en aprobación de UMAS): probabilidad 0,45; afecta costo, plazo e ingeniería de diseño.");
tabla(s, [["Iteración", "Sorteo (0–1)", "¿Ocurre? (< 0,45)", "Costo (PERT)", "Plazo (TRIANG.)", "Ing. diseño (TRIANG.)"],
  ["1", "0,31", "Sí", "S/ 612 000", "34 días", "350 HH"], ["2", "0,72", "No", "0", "0", "0"],
  ["3", "0,08", "Sí", "S/ 455 000", "22 días", "260 HH"], ["4", "0,90", "No", "0", "0", "0"],
  ["…", "…", "…", "…", "…", "…"], ["10 000", "0,44", "Sí", "S/ 981 000", "51 días", "540 HH"]],
  { x: M, y: 2.2, w: 8.1, colW: [1.1, 1.2, 1.5, 1.4, 1.4, 1.5], rowH: 0.45, fs: 13, primeraNegrita: true });
tarjeta(s, 9.1, 2.2, 3.6, 4.5, C.negro);
txt(s, "Tres pasos por riesgo", { x: 9.35, y: 2.4, w: 3.2, h: 0.4, fontSize: 16, bold: true, color: C.ambar });
bullets(s, ["Sortea un número entre 0 y 1. Si es menor que la probabilidad, el riesgo ocurre.",
  "Si ocurre, saca un valor de cada distribución (costo, plazo, HH).",
  "Si no ocurre, aporta 0 a todas las dimensiones.",
  "Suma todos los riesgos: ese es el total de la iteración."], { x: 9.35, y: 2.9, w: 3.2, h: 3.7, fontSize: 13, color: C.blanco });
txt(s, "Valores ilustrativos. En unas 4 500 de las 10 000 iteraciones R-05 ocurre; en las demás aporta 0.", { x: M, y: 5.55, w: 8.1, h: 0.8, fontSize: 13.5, color: C.gris });
narrar(s, "Veamos qué hace la macro en cada escenario, con el riesgo R cero cinco, que tiene probabilidad cero coma cuarenta y cinco. En cada iteración sortea un número entre cero y uno. Si sale menor que cero coma cuarenta y cinco, el riesgo ocurre, y entonces saca un valor de cada una de sus distribuciones: costo, plazo y horas hombre. Si el sorteo sale mayor, el riesgo no ocurre y aporta cero. Luego suma todos los riesgos para obtener el total de esa iteración. Como resultado, en unas cuatro mil quinientas de las diez mil iteraciones el riesgo ocurre, y en las demás aporta cero.");

s = nueva("3 · La idea", "Una ocurrencia, varias dimensiones", "Si el riesgo ocurre, impacta a la vez en todas las dimensiones donde tiene distribución.");
tarjeta(s, M, 2.3, 3.4, 3.0, C.negro);
txt(s, "R-05 ocurre", { x: M + 0.25, y: 2.5, w: 3.0, h: 0.5, fontSize: 20, bold: true, color: C.ambar });
txt(s, "Un solo sorteo con probabilidad 0,45 para todo el riesgo.", { x: M + 0.25, y: 3.1, w: 3.0, h: 1.2, fontSize: 14, color: C.blanco });
[["COSTO", "PERT 200 000 / 500 000 / 1 200 000", C.naranja], ["PLAZO", "TRIANGULAR 15 / 30 / 60 días", C.azul],
 ["ING_DISENO", "TRIANGULAR 120 / 300 / 600 HH", C.ambarP], ["ING_CAMPO", "(vacía) → no afecta", C.grisC]].forEach((d, i) => {
  const y = 2.0 + i * 0.95;
  txt(s, "›", { x: 4.15, y, w: 0.5, h: 0.75, fontSize: 30, bold: true, color: C.ambar, align: "center", valign: "middle" });
  tarjeta(s, 4.75, y, 7.95, 0.75, C.tinte2);
  s.addShape(pres.shapes.OVAL, { x: 4.95, y: y + 0.22, w: 0.32, h: 0.32, fill: { color: d[2] }, line: { color: d[2] } });
  txt(s, d[0], { x: 5.45, y, w: 2.2, h: 0.75, fontSize: 15, bold: true, valign: "middle" });
  txt(s, d[1], { x: 7.7, y, w: 4.9, h: 0.75, fontSize: 14, valign: "middle" });
});
txt(s, "Por eso la macro nunca produce un escenario donde R-05 cueste dinero pero no retrase la obra: ambos efectos vienen del mismo evento. Los valores dentro de cada dimensión se sortean por separado.",
  { x: M, y: 5.95, w: W - 2 * M, h: 0.9, fontSize: 14 });
narrar(s, "Un punto clave: si el riesgo ocurre, impacta a la vez en todas las dimensiones donde tiene distribución. R cero cinco tiene distribución en costo, plazo e ingeniería de diseño, y la de ingeniería de campo está vacía, así que no la afecta. Como la ocurrencia es un solo sorteo, la macro nunca produce un escenario donde el riesgo cueste dinero pero no retrase la obra. Lo que sí se sortea por separado es el valor dentro de cada dimensión: puede salir un costo alto con un retraso moderado, por ejemplo.");

s = nueva("3 · La idea", "De 10 000 escenarios a un resultado", "Sumando los 32 riesgos en cada iteración se obtienen 10 000 totales. Su histograma es la distribución del riesgo general.");
const hl = [], hv = [];
sim.hist.forEach((v, i) => { hl.push(fmt((sim.edges[i] + sim.edges[i + 1]) / 2e6, 0)); hv.push(v); });
barras(s, hl, hv, C.naranja, { x: M, y: 2.15, w: 7.6, h: 4.3, titulo: "Histograma del impacto total en costo (10 000 iteraciones)", ejeX: "Millones de S/", nombre: "Iteraciones" });
bullets(s, ["Cada barra cuenta cuántas iteraciones cayeron en ese rango.",
  "El centro está cerca de S/ 16 M: lo más frecuente.",
  "Casi nunca sale 0 (algún riesgo casi siempre ocurre) ni más de S/ 35 M (tendrían que ocurrir casi todos en su peor versión).",
  "La suma de los máximos de todos los riesgos superaría ampliamente lo que muestra el histograma: por eso no se suman peores casos."],
  { x: 8.5, y: 2.2, w: 4.2, h: 4.5, fontSize: 13.5 });
narrar(s, "Cuando la macro suma los treinta y dos riesgos en cada iteración, obtiene diez mil totales. El histograma muestra cuántas iteraciones cayeron en cada rango. El centro está cerca de dieciséis millones de soles, que es lo más frecuente. Casi nunca sale cero, porque algún riesgo casi siempre ocurre, y casi nunca pasa de treinta y cinco millones, porque tendrían que ocurrir casi todos en su peor versión. Fíjese que la suma de los máximos de todos los riesgos sería mucho mayor: por eso no se suman peores casos.");

s = nueva("3 · La idea", "Leer una distribución (1): la densidad", "La curva de densidad muestra DÓNDE se concentran los valores. El área bajo la curva entre dos puntos es la probabilidad de ese tramo.");
const fP = pdf.pertG(200, 600, 1400, 4), stP = stats(fP, 200, 1400);
curvas(s, xsP, [{ name: "Densidad", f: fP, color: C.naranja }], { x: M, y: 2.2, w: 7.3, h: 4.3, ejeX: "Sobrecosto (miles de S/)", extra: { catAxisMajorUnit: 200 } });
caja(s, 8.2, 2.2, 4.5, 1.35, "La cima es la moda", "El valor más frecuente: 600 000.");
caja(s, 8.2, 3.7, 4.5, 1.35, "La cola derecha", "Valores altos poco frecuentes pero posibles, hasta 1 400 000.");
caja(s, 8.2, 5.2, 4.5, 1.35, "El área = probabilidad", `P(entre 400 000 y 800 000) ≈ ${Math.round((stats(fP, 200, 800).media, 0) || 0)}${""}`.replace(/.*/, "Entre 400 000 y 800 000 cae aproximadamente el " + Math.round(100 * (function () { const f = fP; let a = 0; for (let x = 400; x < 800; x += 0.5) a += f(x) * 0.5; return a; })()) + " % de los casos."));
narrar(s, "Hay dos formas de leer una distribución. La primera es la densidad. La curva muestra dónde se concentran los valores. La cima es la moda, el valor más frecuente, aquí seiscientos mil soles. La cola derecha son los valores altos, poco frecuentes pero posibles. Y un concepto importante: el área bajo la curva entre dos puntos es la probabilidad de ese tramo. Por ejemplo, entre cuatrocientos mil y ochocientos mil cae más de la mitad de los casos. La altura por sí sola no es una probabilidad; lo es el área.");

s = nueva("3 · La idea", "Leer una distribución (2): la acumulada y los percentiles", "La curva acumulada (curva S) responde: ¿con qué probabilidad NO se supera cada valor?");
let acc = 0; const cdf = [];
xsP.forEach((x, i) => { if (i > 0) acc += (fP(x) + fP(xsP[i - 1])) / 2 * (x - xsP[i - 1]); cdf.push(acc); });
s.addChart(pres.charts.SCATTER, [{ name: "X", values: xsP.map(r3) }, { name: "Acumulada", values: cdf.map(v => Math.round(v * 1000) / 10) }], {
  x: M, y: 2.2, w: 7.3, h: 4.3, lineSize: 3, lineDataSymbol: "none", chartColors: [C.azul], showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20, valAxisLabelFontSize: 11, valAxisLabelColor: C.gris,
  showValAxisTitle: true, valAxisTitle: "% acumulado", valAxisTitleFontSize: 11, valAxisTitleColor: C.gris,
  showCatAxisTitle: true, catAxisTitle: "Sobrecosto (miles de S/)", catAxisTitleFontSize: 11, catAxisTitleColor: C.gris,
  valGridLine: { color: "E0E0E0", size: 0.5 }, catGridLine: { style: "none" }, catAxisMajorUnit: 200,
  catAxisMinVal: 150, catAxisMaxVal: 1500, catAxisLabelFontSize: 11, catAxisLabelColor: C.gris });
tabla(s, [["Percentil", "Valor", "Se lee así"],
  ["P10", "S/ " + fmt(Math.round(stP.q(0.1)) * 1000), "Solo 10 % de los casos por debajo"],
  ["P50", "S/ " + fmt(Math.round(stP.q(0.5)) * 1000), "Mitad y mitad (mediana)"],
  ["P80", "S/ " + fmt(Math.round(stP.q(0.8)) * 1000), "80 % de los casos por debajo"],
  ["P90", "S/ " + fmt(Math.round(stP.q(0.9)) * 1000), "Solo 10 % de los casos por encima"]],
  { x: 8.2, y: 2.25, w: 4.5, colW: [1.0, 1.5, 2.0], rowH: 0.5, fs: 12.5, primeraNegrita: true });
txt(s, "La reserva para contingencias se lee exactamente así, pero sobre la curva S del TOTAL (parte 7).", { x: 8.2, y: 5.0, w: 4.5, h: 1.2, fontSize: 14, bold: true });
narrar(s, "La segunda forma de leer una distribución es la curva acumulada, también llamada curva S. Para cada valor, indica qué porcentaje de los casos queda por debajo. De ahí salen los percentiles. El percentil diez es el valor que solo el diez por ciento de los casos no alcanza. El percentil cincuenta, o mediana, deja la mitad de cada lado. Y el percentil ochenta es el valor que no se supera en el ochenta por ciento de los casos. Esta es exactamente la lectura que usaremos para la contingencia, pero sobre la curva S del total del proyecto.");

s = nueva("3 · La idea", "Mínimo, moda, mediana, media y máximo", "Cinco valores que se confunden a menudo. Ejemplo: retraso en aprobación de submittals, PERT 10 / 20 / 45 días.");
const fS = pdf.pertG(10, 20, 45, 4), stS = stats(fS, 10, 45);
curvas(s, grid(5, 50, 180), [{ name: "PERT", f: fS, color: C.naranja }], { x: M, y: 2.2, w: 6.9, h: 4.4, ejeX: "Días de retraso", extra: { catAxisMajorUnit: 5 } });
[["Mínimo (P1)", "10 días", "Lo mejor razonable. No lo imposible."],
 ["Moda (P2)", "20 días", "Lo MÁS FRECUENTE: la cima de la curva."],
 ["Mediana (P50)", fmt(stS.q(0.5), 1) + " días", "Mitad de los casos por debajo."],
 ["Media", fmt(stS.media, 1) + " días", "El promedio: con cola derecha, mayor que la moda."],
 ["Máximo (P3)", "45 días", "Lo peor razonable, sin catástrofes absurdas."]].forEach((d, i) => {
  const y = 2.2 + i * 0.9;
  tarjeta(s, 7.8, y, 4.9, 0.8, i === 1 ? C.tinte : C.tinte2);
  txt(s, d[0], { x: 8.0, y: y + 0.08, w: 2.3, h: 0.33, fontSize: 14, bold: true });
  txt(s, d[1], { x: 10.6, y: y + 0.08, w: 1.9, h: 0.33, fontSize: 14, bold: true, color: C.ambarP, align: "right" });
  txt(s, d[2], { x: 8.0, y: y + 0.43, w: 4.5, h: 0.33, fontSize: 12, color: C.gris });
});
narrar(s, "Cinco valores que se confunden a menudo. El mínimo es lo mejor razonable, no lo imposible. La moda es el valor más frecuente, la cima de la curva, aquí veinte días. La mediana deja la mitad de los casos de cada lado. La media es el promedio. Cuando la distribución tiene una cola hacia la derecha, como casi todos los sobrecostos y retrasos, la media es mayor que la moda: aquí veintidós coma cinco días frente a veinte. Y el máximo es lo peor razonable. En las distribuciones de tres puntos, el experto da la moda, no la media.");

s = nueva("3 · La idea", "Tres rasgos de la forma: centro, ancho y sesgo", "Al elegir una distribución, en realidad se eligen estos tres rasgos.");
const xs3 = grid(0, 60, 240);
curvas(s, xs3, [{ name: "Centro 20", f: pdf.pertG(10, 20, 30, 4), color: C.azul }, { name: "Centro 35", f: pdf.pertG(25, 35, 45, 4), color: C.naranja }],
  { x: M, y: 2.2, w: 3.9, h: 3.1, titulo: "Centro: dónde está", extra: { catAxisMajorUnit: 10, showLegend: false } });
curvas(s, xs3, [{ name: "Estrecho", f: pdf.pertG(24, 30, 36, 4), color: C.azul }, { name: "Ancho", f: pdf.pertG(10, 30, 50, 4), color: C.naranja }],
  { x: M + 4.1, y: 2.2, w: 3.9, h: 3.1, titulo: "Ancho: cuánta incertidumbre", extra: { catAxisMajorUnit: 10, showLegend: false } });
curvas(s, xs3, [{ name: "Simétrico", f: pdf.pertG(10, 30, 50, 4), color: C.azul }, { name: "Sesgo derecha", f: pdf.pertG(10, 18, 55, 4), color: C.naranja }],
  { x: M + 8.2, y: 2.2, w: 3.9, h: 3.1, titulo: "Sesgo: hacia dónde la cola", extra: { catAxisMajorUnit: 10, showLegend: false } });
txt(s, "Centro: la moda o la media. Define el valor típico.", { x: M, y: 5.45, w: 3.9, h: 0.9, fontSize: 13 });
txt(s, "Ancho: distancia entre mínimo y máximo (o la desviación). Define cuánta contingencia hará falta.", { x: M + 4.1, y: 5.45, w: 3.9, h: 1.0, fontSize: 13 });
txt(s, "Sesgo: en obra casi siempre a la derecha: salir mal cuesta más de lo que ahorra salir bien.", { x: M + 8.2, y: 5.45, w: 3.9, h: 1.0, fontSize: 13 });
narrar(s, "Al elegir una distribución, en realidad elegimos tres rasgos de su forma. El centro, que es el valor típico. El ancho, que es la cantidad de incertidumbre, y que determina en buena parte cuánta contingencia hará falta. Y el sesgo, que indica hacia dónde se extiende la cola. En obra, los impactos casi siempre tienen sesgo a la derecha: cuando las cosas salen mal, cuestan mucho más de lo que se ahorra cuando salen bien. Por eso las distribuciones asimétricas, como PERT, son tan usadas.");

// PARTE 4 — Elegir
s = divisor("PARTE 4", "Cómo elegir la distribución", "Se elige según LO QUE SABEMOS del impacto, no según lo que suena más técnico.",
  ["Juicio experto o datos", "Árbol de decisión", "Lo que dice el experto", "Preguntas, sesgos y datos históricos"]);
narrar(s, "Parte cuatro: cómo elegir la distribución. La regla principal es sencilla: se elige según lo que sabemos del impacto, no según lo que suena más técnico.");

s = nueva("4 · Elegir", "Principio: elegir según la información disponible", "La fuente de la información decide la familia de distribuciones.");
caja(s, M, 2.15, 5.9, 4.3, "Juicio experto (lo más común en obra)", "No hay datos suficientes; se consulta a quien conoce el tema.\n\n• Tres puntos: PERT (por defecto), TRIANGULAR, TRIGEN.\n• Solo un rango: UNIFORME.\n• Escenarios: DISCRETA.\n• Valor fijo: CONSTANTE.\n\nMás del 90 % de un registro típico de obra se modela así.", { fill: C.tinte, fs: 14 });
caja(s, M + 6.15, 2.15, 5.9, 4.3, "Datos históricos (cuando existen)", "Hay registros de obras anteriores, series de precios o de fallas.\n\n• Simétricos: NORMAL, LOGISTICA.\n• Sesgados positivos: LOGNORMAL, GAMMA, WEIBULL, EXPONENCIAL.\n• Extremos: GUMBEL, PARETO.\n• Conteos: POISSON, BINOMIAL.\n\nSe estiman media y desviación (o forma y escala) de los datos.", { fs: 14 });
pie(s, "Regla práctica: si duda, use PERT con mínimo, más probable y máximo. Es robusta, fácil de explicar y la recomienda la bibliografía (Vose).");
narrar(s, "El principio es elegir según la información disponible. Si la fuente es el juicio de un experto, que es lo más común en obra, se usan distribuciones que el experto pueda describir con palabras: tres puntos con PERT, TRIANGULAR o TRIGEN; un rango con UNIFORME; escenarios con DISCRETA; o un valor fijo con CONSTANTE. Si hay datos históricos, se pueden usar distribuciones que se ajustan a datos, como normal, lognormal o gamma. Y la regla práctica: si duda, use PERT. Es robusta, fácil de explicar y es la que recomienda la bibliografía.");

s = nueva("4 · Elegir", "Árbol de decisión: ¿qué sé del impacto?");
const arbol = [["El valor es seguro si el riesgo ocurre", "CONSTANTE"], ["Solo conozco un rango, sin valor más probable", "UNIFORME"],
  ["Conozco mínimo, más probable y máximo", "PERT (recomendada) o TRIANGULAR"], ["El experto dice «rara vez baja de X o pasa de Y»", "TRIGEN"],
  ["Pocos escenarios con probabilidad conocida", "DISCRETA"], ["Promedio y dispersión simétrica (datos)", "NORMAL / NORMAL_TRUNCADA / LOGISTICA"],
  ["Sesgado a la derecha, nunca negativo (datos)", "LOGNORMAL, GAMMA, WEIBULL"], ["Tiempos entre eventos o muchos casos pequeños", "EXPONENCIAL"],
  ["Cuento eventos en el periodo", "POISSON, BINOMIAL, DISCRETA_UNIFORME"], ["Colas extremas: reclamos, eventos raros", "PARETO, GUMBEL"]];
arbol.forEach((a, i) => {
  const y = 1.6 + i * 0.54;
  tarjeta(s, M, y, 7.0, 0.46, i % 2 ? C.tinte2 : C.grisC);
  txt(s, a[0], { x: M + 0.2, y, w: 6.7, h: 0.46, fontSize: 13.5, valign: "middle" });
  txt(s, "›", { x: M + 7.05, y, w: 0.4, h: 0.46, fontSize: 22, bold: true, color: C.ambar, align: "center", valign: "middle" });
  const p = i <= 4; tarjeta(s, M + 7.5, y, 4.6, 0.46, p ? C.ambar : C.negro);
  txt(s, a[1], { x: M + 7.7, y, w: 4.3, h: 0.46, fontSize: 13, bold: true, valign: "middle", color: p ? C.negro : C.ambar });
});
pie(s, "Ámbar: juicio experto. Negro: con datos o casos particulares. El mismo árbol está en la hoja GUIA.");
narrar(s, "Este árbol de decisión resume la elección. Pregúntese qué sabe del impacto. Si el valor es seguro, use constante. Si solo conoce un rango, uniforme. Si conoce mínimo, más probable y máximo, PERT o triangular. Si el experto habla de valores que rara vez se superan, TRIGEN. Si hay pocos escenarios con probabilidad conocida, discreta. Las cinco primeras, en ámbar, cubren el juicio experto. Las de abajo, en negro, se usan con datos o en casos particulares: simétricas, sesgadas, tiempos entre eventos, conteos y colas extremas.");

s = nueva("4 · Elegir", "Traducir lo que dice el experto", "Las palabras que usa la persona ya indican la distribución. Escuche con atención.");
tabla(s, [["Lo que dice el experto", "Palabra clave", "Distribución", "P1 / P2 / P3 / P4"],
  ["«Si pasa, la multa es S/ 250 000, fija.»", "fija", "CONSTANTE", "250 000"],
  ["«Entre 10 y 40 días, cualquiera; no sé cuál es típico.»", "cualquiera", "UNIFORME", "10 / 40"],
  ["«Normalmente 20 días; mínimo 10, máximo 45.»", "normalmente", "PERT", "10 / 20 / 45"],
  ["«Rara vez menos de 10, lo normal 15, rara vez más de 35.»", "rara vez", "TRIGEN", "10 / 15 / 35 / 10"],
  ["«60 % nada, 30 % S/ 150 000, 10 % S/ 400 000.»", "escenarios", "DISCRETA", "«0;150000;400000» / «0,6;0,3;0,1»"],
  ["«Unos 4 días de lluvia fuerte por temporada.»", "cuántos eventos", "POISSON", "4"],
  ["«En obras anteriores: promedio 50 000, ±25 000.»", "promedio ±", "NORMAL", "50 000 / 25 000"],
  ["«Muy seguro de que serán 20 días, entre 10 y 45.»", "muy seguro", "PERT_MODIFICADA", "10 / 20 / 45 / 8"]],
  { x: M, y: 2.1, w: W - 2 * M, colW: [5.2, 1.8, 2.2, 2.93], rowH: 0.5, fs: 13, fsCab: 13 });
narrar(s, "Las palabras que usa el experto ya indican la distribución. Si dice fija, es constante. Si dice cualquiera dentro de un rango, uniforme. Si dice normalmente, o lo típico, está dando la moda: PERT. Si dice rara vez, está dando percentiles, no extremos absolutos: TRIGEN. Si habla de escenarios con porcentajes, discreta. Si cuenta eventos, Poisson. Si da un promedio con más o menos, normal. Y si dice que está muy seguro del valor típico, PERT modificada con un gamma alto. Escuche con atención y anote las palabras exactas en notas.");

s = nueva("4 · Elegir", "Cómo preguntar al experto: 3 preguntas en este orden", "Primero los extremos, después el valor típico: así se evita que la primera cifra «ancle» a las demás.");
[["«Si todo sale bien, ¿cuál es el MÍNIMO razonable del impacto?»", "P1", "Pida que piense en un caso favorable real, no en «cero»."],
 ["«Si todo sale mal, ¿cuál es el MÁXIMO razonable?»", "P3", "Sin catástrofes absurdas; pida un ejemplo que lo justifique."],
 ["«¿Cuál es el valor MÁS PROBABLE?»", "P2", "Lo que pasa normalmente. No el promedio ni el más temido."]].forEach((p, i) => {
  const y = 2.2 + i * 1.2;
  circulo(s, M, y, 0.75, i + 1);
  txt(s, p[0], { x: M + 1.0, y: y - 0.02, w: 8.6, h: 0.5, fontSize: 17, bold: true, valign: "middle" });
  txt(s, p[2], { x: M + 1.0, y: y + 0.48, w: 8.6, h: 0.45, fontSize: 13.5, color: C.gris });
  tarjeta(s, 10.3, y + 0.08, 2.4, 0.6, C.negro);
  txt(s, "→ " + p[1], { x: 10.3, y: y + 0.08, w: 2.4, h: 0.6, fontSize: 16, bold: true, color: C.ambar, align: "center", valign: "middle" });
});
tarjeta(s, M, 5.85, W - 2 * M, 0.95, C.tinte);
txt(s, "4.ª pregunta: la PROBABILIDAD de que ocurra. 5.ª: ¿qué otros riesgos se moverían junto con este? (correlación). Anote la fuente de cada número en NOTAS.",
  { x: M + 0.25, y: 5.9, w: W - 2 * M - 0.5, h: 0.85, fontSize: 14, valign: "middle" });
narrar(s, "Para obtener los tres puntos, pregunte en este orden. Primero el mínimo razonable: si todo sale bien, ¿cuánto sería el impacto? Segundo el máximo razonable: si todo sale mal, sin catástrofes absurdas. Y recién tercero el valor más probable. Se pregunta primero por los extremos para evitar el anclaje: si el experto dice primero el valor típico, luego tiende a dar extremos demasiado cercanos a él. Después pregunte la probabilidad, y por último qué otros riesgos se moverían junto con este, lo que nos servirá para la correlación.");

s = nueva("4 · Elegir", "Sesgos del experto y cómo contrarrestarlos", "Las personas, incluso los expertos, suelen subestimar la incertidumbre.");
[["Exceso de confianza", "Rangos demasiado estrechos. Contramedida: pida un caso real en que se superó el máximo; si existe, amplíe el rango o use TRIGEN."],
 ["Anclaje", "La primera cifra condiciona las demás. Contramedida: pregunte extremos antes que el valor típico."],
 ["Disponibilidad", "Se sobrevalora lo reciente o dramático. Contramedida: contraste con registros de varias obras, no solo la última."],
 ["Optimismo", "Mínimos y modas demasiado favorables. Contramedida: pregunte a más de una persona y a quien no es responsable del resultado."],
 ["Confundir moda y peor caso", "Se da como moda el valor temido. Contramedida: pregunte «¿qué pasa normalmente?»."],
 ["Doble conteo", "El mismo impacto en dos riesgos o en dos dimensiones. Contramedida: revise causas y unidades."]].forEach((c, i) => {
  const x = M + (i % 2) * 6.15, y = 2.1 + Math.floor(i / 2) * 1.6;
  caja(s, x, y, 5.95, 1.45, c[0], c[1], { fs: 13 });
});
narrar(s, "Incluso los expertos tienen sesgos. El más importante es el exceso de confianza: dan rangos demasiado estrechos. Para contrarrestarlo, pida un caso real en que se superó el máximo; si existe, amplíe el rango o use TRIGEN. El anclaje se evita preguntando primero los extremos. La disponibilidad hace sobrevalorar lo reciente, así que contraste con varias obras. El optimismo se reduce consultando a más de una persona. Y cuide dos errores prácticos: confundir la moda con el peor caso, y contar dos veces el mismo impacto.");

s = nueva("4 · Elegir", "Cuando hay datos históricos", "Con 15 o más observaciones de obras comparables se puede ajustar una distribución a los datos.");
[["1", "Reúna los datos", "Impactos reales de obras similares, en la misma unidad y actualizados (por ejemplo, a soles de hoy)."],
 ["2", "Mire la forma", "Haga un histograma en Excel: ¿simétrico?, ¿cola a la derecha?, ¿valores extremos aislados?"],
 ["3", "Calcule parámetros", "PROMEDIO y DESVEST para NORMAL o LOGNORMAL; forma = media² / var y escala = var / media para GAMMA."],
 ["4", "Revise los extremos", "Compare el P5 y el P95 de la distribución con el mínimo y el máximo observados."],
 ["5", "Documente", "Anote la fuente, el número de datos y el ajuste en NOTAS."]].forEach((p, i) => {
  const y = 2.1 + i * 0.9;
  circulo(s, M, y, 0.55, p[0]);
  txt(s, p[1], { x: M + 0.8, y: y + 0.05, w: 2.8, h: 0.45, fontSize: 15, bold: true, valign: "middle" });
  txt(s, p[2], { x: M + 3.7, y: y + 0.05, w: 8.4, h: 0.75, fontSize: 13.5, color: C.gris });
});
pie(s, "Con pocos datos (menos de 15), prefiera PERT usando el mínimo, el valor más frecuente y el máximo observados, ampliados con criterio experto.");
narrar(s, "Cuando hay datos históricos, digamos quince o más observaciones de obras comparables, se puede ajustar una distribución. Primero reúna los datos en la misma unidad y actualizados. Segundo, haga un histograma para ver la forma: si es simétrico, si tiene cola a la derecha, si hay extremos aislados. Tercero, calcule los parámetros: promedio y desviación estándar para la normal o la lognormal, o forma y escala para la gamma. Cuarto, compare los extremos de la distribución con los observados. Y quinto, documente. Con pocos datos, es mejor usar PERT con criterio experto.");

// PARTE 5 — Las 20 distribuciones
s = divisor("PARTE 5", "Las 20 distribuciones", "Una lámina por distribución: cuándo usarla, qué va en P1…P4, un ejemplo de obra con su lectura y los cuidados.",
  ["Simples y de tres puntos", "Control de forma", "Simétricas y sesgadas", "Extremos, conteos y escenarios"]);
narrar(s, "Parte cinco: las veinte distribuciones. Dedicamos una lámina a cada una. En cada lámina verá cuándo usarla, qué va en cada parámetro, un ejemplo de obra con su lectura, y los cuidados que hay que tener.");

s = nueva("5 · Mapa", "Mapa de las 20 distribuciones por familias", "Todas están en el menú de cada columna DIST_. Las de juicio experto son las más usadas.");
const fam = [
  ["Simples", "CONSTANTE · UNIFORME · DISCRETA · DISCRETA_UNIFORME", "Valor fijo, rango o escenarios.", C.tinte],
  ["Tres puntos", "TRIANGULAR · PERT · TRIGEN", "Mínimo, más probable y máximo (o P10 / P90).", C.ambar],
  ["Control de forma", "PERT_MODIFICADA · BETA_GENERAL", "Rango con concentración ajustable.", C.tinte],
  ["Simétricas", "NORMAL · NORMAL_TRUNCADA · LOGISTICA", "Variación pareja alrededor de un promedio.", C.tinte2],
  ["Sesgadas positivas", "LOGNORMAL · GAMMA · WEIBULL · EXPONENCIAL", "Nunca negativas, cola derecha.", C.tinte2],
  ["Extremos", "GUMBEL · PARETO", "Lo raro puede ser enorme.", C.tinte2],
  ["Conteos", "POISSON · BINOMIAL", "Número de eventos.", C.tinte2]];
fam.forEach((f, i) => {
  const y = 2.15 + i * 0.66;
  tarjeta(s, M, y, W - 2 * M, 0.56, f[3]);
  txt(s, f[0], { x: M + 0.2, y, w: 2.5, h: 0.56, fontSize: 14.5, bold: true, valign: "middle" });
  txt(s, f[1], { x: M + 2.8, y, w: 5.6, h: 0.56, fontSize: 13.5, bold: true, color: C.ambarP === f[3] ? C.negro : C.gris, valign: "middle" });
  txt(s, f[2], { x: M + 8.5, y, w: 3.5, h: 0.56, fontSize: 13, valign: "middle" });
});
narrar(s, "Este mapa agrupa las veinte distribuciones en siete familias. Las simples: constante, uniforme, discreta y discreta uniforme. Las de tres puntos: triangular, PERT y TRIGEN, que son las más usadas. Las de control de forma: PERT modificada y beta general. Las simétricas: normal, normal truncada y logística. Las sesgadas positivas: lognormal, gamma, Weibull y exponencial. Las de extremos: Gumbel y Pareto. Y las de conteo: Poisson y binomial. Veamos cada una.");

// Plantilla de lámina de distribución
function lamDist(o) {
  const s = nueva("5 · " + o.familia, o.nombre, o.idea);
  if (o.bars) barras(s, o.bars.l, o.bars.v, o.color || C.naranja, { x: M, y: 2.15, w: 6.3, h: 3.4, titulo: o.tituloG, valores: true, ejeX: o.ejeX, fmt: o.fmtBar });
  else curvas(s, o.xs, o.series, { x: M, y: 2.15, w: 6.3, h: 3.4, titulo: o.tituloG, ejeX: o.ejeX, extra: o.extra || {} });
  tarjeta(s, M, 5.7, 6.3, 1.2, C.negro);
  txt(s, "Lectura del ejemplo", { x: M + 0.2, y: 5.78, w: 5.9, h: 0.3, fontSize: 12, bold: true, color: C.ambar });
  txt(s, o.lectura, { x: M + 0.2, y: 6.1, w: 5.9, h: 0.75, fontSize: 12.5, color: C.blanco });
  txt(s, "Cuándo usarla", { x: 7.2, y: 2.15, w: 5.5, h: 0.3, fontSize: 13, bold: true, color: C.ambarP });
  txt(s, o.cuando, { x: 7.2, y: 2.45, w: 5.5, h: 1.05, fontSize: 13 });
  const filas = [["Parám.", "Qué va", "Ejemplo"]].concat(o.params);
  tabla(s, filas, { x: 7.2, y: 3.55, w: 5.5, colW: [0.85, 3.0, 1.65], rowH: 0.36, fs: 11.5, fsCab: 11.5, primeraNegrita: true });
  const yc = 3.55 + 0.36 * filas.length + 0.15;
  tarjeta(s, 7.2, yc, 5.5, 6.9 - yc, C.tinte);
  txt(s, "Cuidado", { x: 7.4, y: yc + 0.08, w: 5.1, h: 0.3, fontSize: 12.5, bold: true, color: C.rojo });
  txt(s, o.cuidado, { x: 7.4, y: yc + 0.4, w: 5.1, h: 6.9 - yc - 0.45, fontSize: 12 });
  narrar(s, o.narr);
}
function lect(f, a, b, unidad, esc) {
  const st = stats(f, a, b); esc = esc || 1;
  return { media: st.media * esc, p50: st.q(0.5) * esc, p80: st.q(0.8) * esc, p10: st.q(0.1) * esc, p90: st.q(0.9) * esc };
}

// CONSTANTE
lamDist({ familia: "Simples", nombre: "CONSTANTE", idea: "El impacto es un valor conocido con certeza SI el riesgo ocurre. La incertidumbre está solo en si ocurre o no.",
  bars: { l: ["No ocurre (70 %)", "Ocurre (30 %)"], v: [0, 250000] }, color: C.naranja, tituloG: "Aporte al total: 0 o S/ 250 000", ejeX: "Escenario", fmtBar: "#,##0",
  cuando: "Multas, penalidades o costos contractuales de monto fijo; una tasa o licencia de precio conocido.",
  params: [["P1", "Valor del impacto", "250 000"], ["P2–P4", "(vacío)", "—"]],
  lectura: "Multa fija por incumplir un hito, probabilidad 0,30. En el 30 % de las iteraciones aporta S/ 250 000; en el 70 %, cero. VME = S/ 75 000.",
  cuidado: "Si el monto puede variar (por ejemplo, depende de los días de atraso), no es constante: use PERT o TRIANGULAR. La probabilidad va en su columna, no dentro de P1.",
  narr: "La distribución constante es la más simple. Se usa cuando el impacto es un valor conocido con certeza si el riesgo ocurre, como una multa fija por incumplir un hito. Solo lleva un parámetro, pe uno, el valor. Toda la incertidumbre está en si el riesgo ocurre o no. Por ejemplo, una multa de doscientos cincuenta mil soles con probabilidad de treinta por ciento aporta doscientos cincuenta mil en el treinta por ciento de las iteraciones, y cero en las demás. Cuidado: si el monto depende de algo variable, como los días de atraso, ya no es constante.",
});
// UNIFORME
lamDist({ familia: "Simples", nombre: "UNIFORME", idea: "Todos los valores entre un mínimo y un máximo son igual de probables.",
  xs: grid(0, 50, 200), series: [{ name: "UNIFORME 10 / 40", f: pdf.unif(10, 40), color: C.azul }], tituloG: "UNIFORME 10 / 40 días", ejeX: "Días", extra: { catAxisMajorUnit: 10 },
  cuando: "Solo se conoce un rango y NO hay un valor más probable. Es la opción de «máxima ignorancia» dentro de límites.",
  params: [["P1", "Mínimo", "10"], ["P2", "Máximo", "40"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Demora de un permiso municipal: media 25 días, P80 = 34 días. Cualquier valor entre 10 y 40 sale con la misma frecuencia.",
  cuidado: "Si el experto sí tiene una idea del valor típico, use PERT: la uniforme da mucho peso a los extremos y suele inflar la contingencia.",
  narr: "La distribución uniforme asigna la misma probabilidad a todos los valores entre un mínimo y un máximo. Se usa cuando solo conocemos un rango y no hay un valor más probable. Lleva dos parámetros: pe uno, el mínimo, y pe dos, el máximo. Por ejemplo, la demora de un permiso municipal entre diez y cuarenta días: la media es veinticinco días y el percentil ochenta, treinta y cuatro. Cuidado: si el experto sí tiene una idea del valor típico, use PERT, porque la uniforme da mucho peso a los extremos y suele inflar la contingencia.",
});
// TRIANGULAR
const lT = lect(pdf.tri(10, 20, 45), 10, 45);
lamDist({ familia: "Tres puntos", nombre: "TRIANGULAR", idea: "Mínimo, más probable y máximo unidos por líneas rectas. Sencilla y fácil de explicar.",
  xs: grid(5, 50, 180), series: [{ name: "TRIANGULAR 10 / 20 / 45", f: pdf.tri(10, 20, 45), color: C.azul }], tituloG: "TRIANGULAR 10 / 20 / 45 días", ejeX: "Días", extra: { catAxisMajorUnit: 5 },
  cuando: "El experto da tres puntos y se quiere una estimación algo conservadora, o se necesita explicarla de forma muy simple.",
  params: [["P1", "Mínimo", "10"], ["P2", "Moda (más probable)", "20"], ["P3", "Máximo", "45"], ["P4", "(vacío)", "—"]],
  lectura: `Retraso en aprobación de submittals: media = (10 + 20 + 45) / 3 = ${fmt(lT.media, 1)} días; P80 = ${fmt(lT.p80, 1)} días.`,
  cuidado: "Da bastante peso a los extremos: con una cola larga, su media sube más que la de PERT. Debe cumplirse mínimo ≤ moda ≤ máximo (si no, la validación lo marca en rojo).",
  narr: "La distribución triangular une el mínimo, el valor más probable y el máximo con líneas rectas. Es sencilla y fácil de explicar. Lleva tres parámetros: mínimo, moda y máximo. Por ejemplo, el retraso en la aprobación de submittals con diez, veinte y cuarenta y cinco días. Su media es la suma de los tres dividida entre tres: veinticinco días, y su percentil ochenta es de unos treinta y un días. Cuidado: la triangular da bastante peso a los extremos, así que su media sube más que la de PERT cuando la cola es larga. Y siempre debe cumplirse que el mínimo sea menor o igual que la moda, y la moda menor o igual que el máximo.",
});
// PERT
const lPe = lect(pdf.pertG(800, 2500, 6000, 4), 800, 6000);
lamDist({ familia: "Tres puntos", nombre: "PERT (recomendada)", idea: "Los mismos tres puntos que la triangular, pero con una curva suave que concentra más peso cerca de la moda.",
  xs: grid(500, 6500, 240), series: [{ name: "PERT", f: pdf.pertG(800, 2500, 6000, 4), color: C.naranja }], tituloG: "PERT 800 / 2 500 / 6 000 miles de S/", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 1000 },
  cuando: "La opción por defecto para cualquier impacto estimado por un experto con mínimo, más probable y máximo. Costo, plazo y HH.",
  params: [["P1", "Mínimo", "800 000"], ["P2", "Moda (más probable)", "2 500 000"], ["P3", "Máximo", "6 000 000"], ["P4", "(vacío)", "—"]],
  lectura: `Sobrecosto por reprocesos: media = (mín + 4·moda + máx) / 6 = S/ ${fmt(lPe.media / 1000, 2)} M; P80 = S/ ${fmt(lPe.p80 / 1000, 2)} M.`,
  cuidado: "La moda es lo más frecuente, no el peor caso. Si el experto está muy seguro o muy inseguro de la moda, considere PERT_MODIFICADA.",
  narr: "PERT es la distribución recomendada. Usa los mismos tres puntos que la triangular, pero con una curva suave que concentra más peso cerca del valor más probable. Es la opción por defecto para cualquier impacto de costo, plazo u horas hombre estimado por un experto. Por ejemplo, un sobrecosto por reprocesos con mínimo ochocientos mil soles, más probable dos millones y medio, y máximo seis millones. Su media se calcula como el mínimo más cuatro veces la moda más el máximo, todo dividido entre seis: dos coma ocho millones. Recuerde: la moda es lo más frecuente, no el peor caso.",
});
// TRI vs PERT
s = nueva("5 · Tres puntos", "TRIANGULAR frente a PERT con los mismos datos", "Mismo mínimo, moda y máximo (10 / 20 / 45 días). La diferencia está en cuánto peso dan a los extremos.");
const lP2 = lect(pdf.pertG(10, 20, 45, 4), 10, 45);
curvas(s, grid(5, 50, 180), [{ name: "TRIANGULAR", f: pdf.tri(10, 20, 45), color: C.azul }, { name: "PERT", f: pdf.pertG(10, 20, 45, 4), color: C.naranja }],
  { x: M, y: 2.15, w: 6.6, h: 4.5, ejeX: "Días de retraso", extra: { catAxisMajorUnit: 5 } });
tabla(s, [["", "TRIANGULAR", "PERT", "Diferencia"],
  ["Media", fmt(lT.media, 1), fmt(lP2.media, 1), fmt(lT.media - lP2.media, 1) + " días"],
  ["P50", fmt(lT.p50, 1), fmt(lP2.p50, 1), fmt(lT.p50 - lP2.p50, 1) + " días"],
  ["P80", fmt(lT.p80, 1), fmt(lP2.p80, 1), fmt(lT.p80 - lP2.p80, 1) + " días"],
  ["P90", fmt(lT.p90, 1), fmt(lP2.p90, 1), fmt(lT.p90 - lP2.p90, 1) + " días"]],
  { x: 7.5, y: 2.2, w: 5.2, colW: [1.1, 1.4, 1.2, 1.5], rowH: 0.45, fs: 13, primeraNegrita: true });
bullets(s, ["La triangular es más conservadora: con los mismos datos, su P80 es mayor.",
  "PERT refleja mejor que los extremos son raros.",
  "Elija una y úsela de forma consistente en todo el registro; no la cambie para «ajustar» el resultado."],
  { x: 7.5, y: 4.65, w: 5.2, h: 2.2, fontSize: 13.5 });
narrar(s, "Comparemos la triangular y PERT con los mismos datos: diez, veinte y cuarenta y cinco días. La curva azul, triangular, tiene más área en los extremos; la naranja, PERT, se concentra cerca de la moda. Por eso, con los mismos tres números, la triangular da una media y un percentil ochenta mayores: es más conservadora. PERT refleja mejor que los extremos son raros. Lo importante es elegir una y usarla de forma consistente en todo el registro, y nunca cambiarla para ajustar el resultado a lo que uno quiere ver.");

// TRIGEN
const [tgA, tgB] = trigen(10, 15, 35, 0.1);
lamDist({ familia: "Tres puntos", nombre: "TRIGEN", idea: "Triangular construida a partir de valores que «rara vez» se superan (percentiles), no de extremos absolutos.",
  xs: grid(0, 50, 200), series: [{ name: "TRIGEN 10 / 15 / 35 / 10", f: pdf.tri(tgA, 15, tgB), color: C.naranja }, { name: "TRIANGULAR 10 / 15 / 35", f: pdf.tri(10, 15, 35), color: C.gris }],
  tituloG: "TRIGEN 10 / 15 / 35 / 10 frente a TRIANGULAR 10 / 15 / 35", ejeX: "Días", extra: { catAxisMajorUnit: 10 },
  cuando: "El experto no se atreve a dar extremos absolutos pero sí dice «rara vez menos de X, rara vez más de Y». Corrige el exceso de confianza.",
  params: [["P1", "Valor bajo (percentil P4)", "10"], ["P2", "Moda", "15"], ["P3", "Valor alto (percentil 100 − P4)", "35"], ["P4", "% en cada cola", "10"]],
  lectura: `Demora de una licencia: el 10 % de los casos queda por debajo de 10 días y otro 10 % por encima de 35. La macro calcula los extremos reales: ≈ ${fmt(tgA, 1)} y ${fmt(tgB, 1)} días.`,
  cuidado: "Si el valor bajo calculado resulta negativo y el impacto no puede serlo, reduzca P4 (por ejemplo a 5) o use PERT. La validación avisa si no se puede resolver.",
  narr: "TRIGEN es una triangular que se construye con valores que rara vez se superan, en lugar de extremos absolutos. Es muy útil porque corrige el exceso de confianza del experto. Lleva cuatro parámetros: el valor bajo, la moda, el valor alto, y en pe cuatro el porcentaje de casos que queda en cada cola, típicamente diez. Por ejemplo: rara vez menos de diez días, lo normal quince, rara vez más de treinta y cinco. La macro calcula los extremos reales, que resultan más amplios, como muestra la curva naranja frente a la gris. Cuidado: si el mínimo calculado sale negativo y el impacto no puede serlo, reduzca el porcentaje o use PERT.",
});
// PERT_MODIFICADA
lamDist({ familia: "Control de forma", nombre: "PERT_MODIFICADA", idea: "Como PERT, con un cuarto parámetro γ que controla cuánto se concentran los valores alrededor de la moda.",
  xs: grid(5, 50, 180), series: [{ name: "γ = 2", f: pdf.pertG(10, 20, 45, 2), color: C.azul }, { name: "γ = 4 (PERT)", f: pdf.pertG(10, 20, 45, 4), color: C.naranja }, { name: "γ = 8", f: pdf.pertG(10, 20, 45, 8), color: C.negro }],
  tituloG: "PERT_MODIFICADA 10 / 20 / 45 / γ", ejeX: "Días", extra: { catAxisMajorUnit: 5 },
  cuando: "El experto está muy seguro del valor típico (γ 6–10) o poco seguro (γ 1–3), pero mantiene los mismos extremos.",
  params: [["P1", "Mínimo", "10"], ["P2", "Moda", "20"], ["P3", "Máximo", "45"], ["P4", "γ (4 = PERT)", "8"]],
  lectura: `Con γ = 8 la media baja a ${fmt(lect(pdf.pertG(10, 20, 45, 8), 10, 45).media, 1)} días y el P80 a ${fmt(lect(pdf.pertG(10, 20, 45, 8), 10, 45).p80, 1)}; con γ = 2 suben a ${fmt(lect(pdf.pertG(10, 20, 45, 2), 10, 45).media, 1)} y ${fmt(lect(pdf.pertG(10, 20, 45, 2), 10, 45).p80, 1)} días.`,
  cuidado: "γ debe ser mayor que 0. Sin una razón clara para cambiarlo, deje γ = 4 (es decir, use PERT).",
  narr: "La PERT modificada agrega un cuarto parámetro, gamma, que controla cuánto se concentran los valores alrededor de la moda. Con gamma igual a cuatro es idéntica a PERT. Con gamma alto, por ejemplo ocho, la curva se vuelve más puntiaguda: el experto está muy seguro del valor típico. Con gamma bajo, por ejemplo dos, se aplana: está poco seguro. Los extremos no cambian. En el ejemplo, con gamma ocho el percentil ochenta baja, y con gamma dos sube. Si no hay una razón clara, deje gamma igual a cuatro.",
});
// BETA_GENERAL
const lB = lect(pdf.beta(2, 5, 0, 700), 0, 700);
lamDist({ familia: "Control de forma", nombre: "BETA_GENERAL", idea: "Forma muy flexible entre un mínimo y un máximo, definida por dos parámetros de forma α y β.",
  xs: grid(0, 700, 280), series: [{ name: "α=2, β=5", f: pdf.beta(2, 5, 0, 700), color: C.naranja }, { name: "α=5, β=2", f: pdf.beta(5, 2, 0, 700), color: C.azul }, { name: "α=β=2", f: pdf.beta(2, 2, 0, 700), color: C.gris }],
  tituloG: "BETA_GENERAL α / β / 0 / 700 miles de S/", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 100 },
  cuando: "Hay datos históricos acotados (por ejemplo, % de desperdicio) y se ajustan α y β con una herramienta estadística.",
  params: [["P1", "α (forma izquierda)", "2"], ["P2", "β (forma derecha)", "5"], ["P3", "Mínimo", "0"], ["P4", "Máximo", "700 000"]],
  lectura: `Sobrecosto por desperdicio de concreto con α = 2, β = 5: media = mín + (máx − mín)·α/(α+β) = S/ ${fmt(lB.media * 1000)}; P80 = S/ ${fmt(Math.round(lB.p80) * 1000)}.`,
  cuidado: "α y β no son intuitivos: sin datos, prefiera PERT (que es una beta con α y β calculados desde los tres puntos). α < β = sesgo a la derecha.",
  narr: "La beta general es una forma muy flexible entre un mínimo y un máximo, definida por dos parámetros de forma, alfa y beta. Si alfa es menor que beta, la cola va hacia la derecha; si es mayor, hacia la izquierda; si son iguales, es simétrica. Lleva cuatro parámetros: alfa, beta, mínimo y máximo. Se usa cuando hay datos históricos acotados, como el porcentaje de desperdicio de concreto, y se ajustan alfa y beta con una herramienta estadística. Sin datos, es mejor PERT, que en realidad es una beta cuyos alfa y beta se calculan a partir de los tres puntos.",
});
// NORMAL
lamDist({ familia: "Simétricas", nombre: "NORMAL", idea: "La campana: variación simétrica alrededor de un promedio. Admite valores negativos.",
  xs: grid(-40, 140, 240), series: [{ name: "NORMAL 50 / 25", f: pdf.normal(50, 25), color: C.naranja }], tituloG: "NORMAL media 50 000, desviación 25 000", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 20 },
  cuando: "Variaciones de precios o cantidades con datos, que pueden ir a favor o en contra. También sumas de muchos efectos pequeños.",
  params: [["P1", "Media", "50 000"], ["P2", "Desviación estándar (> 0)", "25 000"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Variación del precio del acero: 68 % de los casos entre 25 000 y 75 000; 95 % entre 0 y 100 000. P80 ≈ 71 000. Hay 2 % de casos negativos (ahorro).",
  cuidado: "Si un valor negativo no tiene sentido físico (días, HH), use NORMAL_TRUNCADA con mínimo 0 o una sesgada positiva. La desviación no es el máximo.",
  narr: "La distribución normal es la conocida campana. Describe una variación simétrica alrededor de un promedio, y admite valores negativos. Lleva dos parámetros: la media y la desviación estándar. Una regla útil: el sesenta y ocho por ciento de los casos cae a una desviación de la media, y el noventa y cinco por ciento a dos desviaciones. Por ejemplo, la variación del precio del acero con media cincuenta mil soles y desviación veinticinco mil. Cuidado: si un valor negativo no tiene sentido, como en días u horas hombre, use la normal truncada o una distribución sesgada positiva.",
});
// NORMAL_TRUNCADA
lamDist({ familia: "Simétricas", nombre: "NORMAL_TRUNCADA", idea: "Una normal recortada entre un mínimo y un máximo: los valores fuera del rango no pueden salir.",
  xs: grid(-800, 800, 320), series: [{ name: "NORMAL_TRUNCADA 0 / 400 / −600 / 600", f: pdf.truncN(0, 400, -600, 600), color: C.azul }, { name: "NORMAL sin recorte", f: x => pdf.normal(0, 400)(x) * 400 * Math.sqrt(2 * Math.PI), color: C.grisC }],
  tituloG: "Ajuste de precios con tope contractual ±600 miles de S/", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 200 },
  cuando: "Variación simétrica con límites físicos o contractuales: topes de reajuste, cantidades que no pueden ser negativas.",
  params: [["P1", "Media (antes del recorte)", "0"], ["P2", "Desviación (antes del recorte)", "400 000"], ["P3", "Mínimo", "−600 000"], ["P4", "Máximo", "600 000"]],
  lectura: "Reajuste de un subcontrato de S/ 12 M con tope de ±5 %: nunca supera ±S/ 600 000; la media se mantiene en 0 porque el recorte es simétrico.",
  cuidado: "Si el recorte es asimétrico, la media real cambia respecto de P1. El rango debe contener la media; mínimo < máximo.",
  narr: "La normal truncada es una normal recortada entre un mínimo y un máximo. Los valores fuera del rango no pueden salir. Lleva cuatro parámetros: media y desviación antes del recorte, mínimo y máximo. Se usa cuando hay límites físicos o contractuales. Por ejemplo, el reajuste de precios de un subcontrato de doce millones con un tope contractual de más o menos cinco por ciento: el impacto nunca supera seiscientos mil soles en ninguna dirección. Cuidado: si el recorte es asimétrico, la media real cambia respecto del parámetro pe uno.",
});
// LOGISTICA
lamDist({ familia: "Simétricas", nombre: "LOGISTICA", idea: "Parecida a la normal, simétrica, pero con colas algo más pesadas: los extremos son un poco más frecuentes.",
  xs: grid(-5, 25, 240), series: [{ name: "LOGISTICA 10 / 2", f: pdf.logistic(10, 2), color: C.naranja }, { name: "NORMAL 10 / 3,63 (misma desviación)", f: pdf.normal(10, 2 * Math.PI / Math.sqrt(3)), color: C.azul }],
  tituloG: "LOGISTICA 10 / 2 frente a NORMAL equivalente", ejeX: "Días", extra: { catAxisMajorUnit: 5 },
  cuando: "Datos simétricos donde se observan más extremos de los que la normal predice, por ejemplo productividad diaria de cuadrillas.",
  params: [["P1", "Media", "10"], ["P2", "Escala (> 0)", "2"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Días perdidos por baja productividad: media 10, desviación = escala × 1,81 = 3,6 días. P80 ≈ 12,8 días.",
  cuidado: "P2 es la ESCALA, no la desviación: desviación = escala × π / √3. Admite negativos, como la normal.",
  narr: "La distribución logística se parece a la normal: es simétrica alrededor de la media, pero tiene colas algo más pesadas, es decir, los extremos son un poco más frecuentes. Lleva dos parámetros: la media y la escala. Cuidado: la escala no es la desviación estándar; la desviación es la escala multiplicada por uno coma ochenta y uno. Se usa con datos simétricos donde se observan más extremos de los que la normal predice, por ejemplo la productividad diaria de las cuadrillas.",
});
// LOGNORMAL
const lLN = lect(pdf.lognormal(120, 90), 0, 1500);
lamDist({ familia: "Sesgadas positivas", nombre: "LOGNORMAL", idea: "Nunca negativa, con cola larga a la derecha. Típica de costos y duraciones reales.",
  xs: grid(0, 600, 300), series: [{ name: "LOGNORMAL 120 / 90", f: pdf.lognormal(120, 90), color: C.naranja }], tituloG: "LOGNORMAL media 120 000, desviación 90 000", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 100 },
  cuando: "Costos o duraciones positivos con datos, donde unos pocos casos son mucho mayores que el resto.",
  params: [["P1", "Media (de los valores reales)", "120 000"], ["P2", "Desviación estándar", "90 000"], ["P3–P4", "(vacío)", "—"]],
  lectura: `Reparación de fisuras en viviendas vecinas: moda ≈ S/ 57 000, mediana S/ ${fmt(Math.round(lLN.p50) * 1000)}, media S/ 120 000, P80 S/ ${fmt(Math.round(lLN.p80) * 1000)}.`,
  cuidado: "P1 y P2 son la media y la desviación de los valores reales, no de su logaritmo. Con desviación alta frente a la media, la cola crece mucho.",
  narr: "La lognormal nunca es negativa y tiene una cola larga hacia la derecha. Es típica de costos y duraciones reales, donde unos pocos casos son mucho mayores que el resto. Lleva dos parámetros: la media y la desviación estándar de los valores reales, no de su logaritmo. Por ejemplo, la reparación de fisuras en viviendas vecinas con media ciento veinte mil soles y desviación noventa mil. Fíjese que la moda, la mediana y la media son muy distintas: la mayoría de los casos son moderados, pero algunos son muy caros.",
});
// GAMMA
lamDist({ familia: "Sesgadas positivas", nombre: "GAMMA", idea: "Positiva y sesgada a la derecha. Su forma va de exponencial (forma 1) a casi normal (forma alta).",
  xs: grid(0, 1000, 300), series: [{ name: "forma 3, escala 100", f: pdf.gamma(3, 100), color: C.naranja }, { name: "forma 1,5, escala 200", f: pdf.gamma(1.5, 200), color: C.azul }, { name: "forma 9, escala 33,3", f: pdf.gamma(9, 33.33), color: C.gris }],
  tituloG: "GAMMA con media 300 HH y distintas formas", ejeX: "Horas hombre", extra: { catAxisMajorUnit: 200 },
  cuando: "Horas hombre, duraciones o costos positivos con datos de proyectos similares.",
  params: [["P1", "Forma (> 0)", "3"], ["P2", "Escala (> 0)", "100"], ["P3–P4", "(vacío)", "—"]],
  lectura: `HH de rediseño: media = forma × escala = 300 HH; desviación = √forma × escala = 173 HH; P80 ≈ ${fmt(lect(pdf.gamma(3, 100), 0, 3000).p80)} HH.`,
  cuidado: "Con datos: forma = media² / varianza; escala = varianza / media. Forma baja = más sesgo y cola más larga.",
  narr: "La gamma es positiva y sesgada a la derecha. Su forma cambia con el parámetro forma: con forma uno es una exponencial, y con forma alta se parece a una normal. Lleva dos parámetros: forma y escala. La media es forma por escala. Por ejemplo, horas hombre de rediseño con forma tres y escala cien: media de trescientas horas hombre. En el gráfico, las tres curvas tienen la misma media pero distinta forma. Si tiene datos, la forma es la media al cuadrado dividida entre la varianza, y la escala es la varianza dividida entre la media.",
});
// EXPONENCIAL
lamDist({ familia: "Sesgadas positivas", nombre: "EXPONENCIAL", idea: "Muchos valores pequeños y pocos grandes. La más probable es cerca de cero.",
  xs: grid(0, 50, 200), series: [{ name: "EXPONENCIAL media 10", f: pdf.expo(10), color: C.naranja }], tituloG: "EXPONENCIAL media 10 días", ejeX: "Días", extra: { catAxisMajorUnit: 5 },
  cuando: "Duración de eventos aleatorios o tiempos entre fallas cuando lo típico es poco y ocasionalmente mucho.",
  params: [["P1", "MEDIA (no la tasa)", "10"], ["P2–P4", "(vacío)", "—"]],
  lectura: "Días de paralización por un evento aleatorio: mediana 6,9 días, media 10, P80 = 16,1 días, P90 = 23 días.",
  cuidado: "P1 es la MEDIA. En otros programas se pide la tasa (1 / media): no las confunda. Desviación = media, así que la incertidumbre es alta.",
  narr: "La exponencial describe situaciones con muchos valores pequeños y pocos grandes; el valor más probable está cerca de cero. Lleva un solo parámetro, y es muy importante: en esta herramienta pe uno es la media, no la tasa. En otros programas se pide la tasa, que es uno dividido entre la media, así que no las confunda. Por ejemplo, días de paralización por un evento aleatorio con media diez días: la mediana es de unos siete días, pero el percentil noventa llega a veintitrés. Su desviación es igual a su media, lo que indica una incertidumbre alta.",
});
// WEIBULL
lamDist({ familia: "Sesgadas positivas", nombre: "WEIBULL", idea: "La distribución de los tiempos de falla y de duración de equipos. La forma indica el tipo de falla.",
  xs: grid(0, 30, 240), series: [{ name: "forma 0,8", f: pdf.weibull(0.8, 8), color: C.azul }, { name: "forma 1,5", f: pdf.weibull(1.5, 8), color: C.naranja }, { name: "forma 3", f: pdf.weibull(3, 8), color: C.gris }],
  tituloG: "WEIBULL escala 8 con distintas formas", ejeX: "Días", extra: { catAxisMajorUnit: 5 },
  cuando: "Días fuera de servicio de equipos (grúa torre, bombas), vida de componentes, con datos de mantenimiento.",
  params: [["P1", "Forma k (> 0)", "1,5"], ["P2", "Escala λ (> 0)", "8"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Grúa torre fuera de servicio con k = 1,5 y λ = 8: media ≈ 7,2 días, P80 ≈ 11,4 días.",
  cuidado: "k < 1: fallas tempranas (defectos de instalación). k = 1: exponencial. k > 1: desgaste. La escala es aproximadamente el P63.",
  narr: "La Weibull es la distribución clásica de tiempos de falla y duración de equipos. Lleva dos parámetros: forma k y escala lambda. La forma indica el tipo de falla: menor que uno significa fallas tempranas, como defectos de instalación; igual a uno es una exponencial; y mayor que uno indica desgaste. Por ejemplo, los días que una grúa torre queda fuera de servicio, con forma uno coma cinco y escala ocho: media de unos siete días y percentil ochenta de unos once. Se usa cuando hay datos de mantenimiento.",
});
// GUMBEL
lamDist({ familia: "Extremos", nombre: "GUMBEL", idea: "La distribución del MÁXIMO de muchos eventos: el peor aguacero del año, la crecida máxima.",
  xs: grid(0, 60, 240), series: [{ name: "GUMBEL 15 / 6", f: pdf.gumbel(15, 6), color: C.azul }], tituloG: "GUMBEL ubicación 15, escala 6", ejeX: "Días", extra: { catAxisMajorUnit: 10 },
  cuando: "Impactos que dependen de un valor extremo: lluvias máximas, crecidas, picos de demanda o de viento.",
  params: [["P1", "Ubicación (moda)", "15"], ["P2", "Escala (> 0)", "6"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Días perdidos por la lluvia máxima de la temporada: moda 15, media = 15 + 0,577 × 6 = 18,5 días, P80 ≈ 24 días, P90 ≈ 28,5 días.",
  cuidado: "Admite valores negativos si la escala es grande frente a la ubicación. Úsela solo si el impacto depende de un máximo.",
  narr: "La Gumbel es la distribución del máximo de muchos eventos: por ejemplo, el peor aguacero del año o la crecida máxima de un río. Lleva dos parámetros: la ubicación, que es la moda, y la escala. Se usa cuando el impacto depende de un valor extremo. Por ejemplo, los días perdidos por la lluvia máxima de la temporada, con ubicación quince y escala seis: la moda es quince días, la media unos dieciocho y medio, y el percentil noventa casi veintinueve. Úsela solo si el impacto depende realmente de un máximo.",
});
// PARETO
lamDist({ familia: "Extremos", nombre: "PARETO", idea: "Colas muy pesadas: la mayoría de los casos son cercanos al mínimo, pero unos pocos son enormes.",
  xs: grid(0, 800, 400), series: [{ name: "PARETO 2,5 / 100", f: pdf.pareto(2.5, 100), color: C.rojo }], tituloG: "PARETO forma 2,5, mínimo 100 000", ejeX: "Miles de S/", extra: { catAxisMajorUnit: 100 },
  cuando: "Montos de reclamos de terceros, siniestros o litigios, donde el caso extremo domina.",
  params: [["P1", "Forma (> 1)", "2,5"], ["P2", "Mínimo (> 0)", "100 000"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Monto de un reclamo: media = forma × mín / (forma − 1) = S/ 166 667; mediana S/ 132 000; P90 S/ 251 000; P99 S/ 631 000.",
  cuidado: "Forma ≤ 1: la media no existe (la validación lo impide). Forma ≤ 2: dispersión enorme. Puede dominar el P90–P99 y la contingencia.",
  narr: "La Pareto tiene colas muy pesadas: la mayoría de los casos están cerca del mínimo, pero unos pocos son enormes. Lleva dos parámetros: la forma, que debe ser mayor que uno, y el mínimo. Se usa para montos de reclamos de terceros, siniestros o litigios. Por ejemplo, un reclamo con mínimo cien mil soles y forma dos coma cinco: la mediana es de unos ciento treinta mil, pero el percentil noventa y nueve supera los seiscientos mil. Cuidado: con forma baja la dispersión es enorme y puede dominar la contingencia; úsela solo si ese comportamiento es real.",
});
// POISSON
const pois = [], lp = []; let pk = Math.exp(-4);
for (let k = 0; k <= 11; k++) { lp.push(String(k)); pois.push(Math.round(pk * 1000) / 1000); pk = pk * 4 / (k + 1); }
lamDist({ familia: "Conteos", nombre: "POISSON", idea: "Número de eventos que ocurren en un periodo cuando pueden ocurrir varias veces, de forma independiente.",
  bars: { l: lp, v: pois }, color: C.azul, tituloG: "POISSON media 4: días de lluvia fuerte", ejeX: "Número de eventos",
  cuando: "Cuando la unidad de la dimensión ES el conteo: días perdidos por lluvia, número de NCR en una dimensión nueva «NCR».",
  params: [["P1", "Media λ (> 0)", "4"], ["P2–P4", "(vacío)", "—"]],
  lectura: "Días de lluvia fuerte que paralizan vaciados: media 4 días, 2 % de temporadas sin ninguno, P80 = 6 días, P90 = 7 días.",
  cuidado: "El valor sorteado es el impacto, en la unidad de la dimensión: la macro no multiplica conteo × costo. Si cada evento cuesta S/ X, modele el costo total con PERT.",
  narr: "La Poisson cuenta el número de eventos que ocurren en un periodo, cuando pueden ocurrir varias veces de forma independiente. Lleva un solo parámetro, la media. Por ejemplo, los días de lluvia fuerte que paralizan vaciados en una temporada, con media cuatro: el percentil ochenta es de seis días. Un cuidado importante: el valor sorteado es el impacto, en la unidad de la dimensión. La macro no multiplica el conteo por un costo. Así que úsela cuando la unidad sea el conteo, como días, y si cada evento cuesta una cantidad de soles, modele el costo total con PERT.",
});
// BINOMIAL
const bin = [], lb = [];
const comb = (n, k) => Math.exp(lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1));
for (let k = 0; k <= 9; k++) { lb.push(String(k)); bin.push(Math.round(comb(20, k) * 0.15 ** k * 0.85 ** (20 - k) * 1000) / 1000); }
lamDist({ familia: "Conteos", nombre: "BINOMIAL", idea: "Cuántos «fracasos» hay en n intentos independientes, cada uno con la misma probabilidad p.",
  bars: { l: lb, v: bin }, color: C.naranja, tituloG: "BINOMIAL n = 20, p = 0,15", ejeX: "Vaciados postergados",
  cuando: "Hay un número conocido de intentos (vaciados, ensayos, submittals) y cada uno puede fallar con cierta probabilidad.",
  params: [["P1", "n: número de intentos (entero)", "20"], ["P2", "p: probabilidad de cada uno", "0,15"], ["P3–P4", "(vacío)", "—"]],
  lectura: "20 vaciados en temporada, cada uno con 15 % de postergarse 1 día: media = n × p = 3 días; P80 = 4 días; P90 = 5 días.",
  cuidado: "Igual que POISSON: el resultado es un conteo en la unidad de la dimensión. p va entre 0 y 1 y n debe ser entero positivo.",
  narr: "La binomial cuenta cuántos fracasos hay en un número conocido de intentos independientes, cada uno con la misma probabilidad. Lleva dos parámetros: n, el número de intentos, y p, la probabilidad de cada uno. Por ejemplo, veinte vaciados programados en temporada de lluvias, cada uno con quince por ciento de probabilidad de postergarse un día: la media es n por p, tres días, y el percentil ochenta, cuatro días. Como en la Poisson, el resultado es un conteo en la unidad de la dimensión.",
});
// DISCRETA_UNIFORME
lamDist({ familia: "Conteos", nombre: "DISCRETA_UNIFORME", idea: "Un número entero entre un mínimo y un máximo, todos igual de probables.",
  bars: { l: ["0", "1", "2", "3"], v: [0.25, 0.25, 0.25, 0.25] }, color: C.azul, tituloG: "DISCRETA_UNIFORME 0 / 3", ejeX: "Días",
  cuando: "Pocos valores enteros posibles, sin preferencia por ninguno: días de paro, número de equipos indisponibles.",
  params: [["P1", "Mínimo (entero)", "0"], ["P2", "Máximo (entero)", "3"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Días adicionales de paro regional: 0, 1, 2 o 3 días, cada uno con 25 %. Media 1,5 días; P80 = 3 días.",
  cuidado: "Solo enteros. Si algunos valores son más probables que otros, use DISCRETA con sus probabilidades.",
  narr: "La discreta uniforme sortea un número entero entre un mínimo y un máximo, todos igual de probables. Lleva dos parámetros enteros: mínimo y máximo. Por ejemplo, los días adicionales de paro regional, que pueden ser cero, uno, dos o tres, cada uno con veinticinco por ciento de probabilidad. La media es uno coma cinco días. Si algunos valores son más probables que otros, use la discreta con sus propias probabilidades, que vemos a continuación.",
});
// DISCRETA
lamDist({ familia: "Escenarios", nombre: "DISCRETA", idea: "Pocos escenarios posibles, cada uno con su probabilidad. Las probabilidades deben sumar 1.",
  bars: { l: ["S/ 0", "S/ 150 000", "S/ 400 000"], v: [0.6, 0.3, 0.1] }, color: C.naranja, tituloG: "DISCRETA: penalidad por escenarios", ejeX: "Escenario",
  cuando: "El experto describe escenarios concretos: «nada», «penalidad parcial», «penalidad total», con sus probabilidades.",
  params: [["P1", "Valores separados por «;»", "0;150000;400000"], ["P2", "Probabilidades separadas por «;»", "0,6;0,3;0,1"], ["P3–P4", "(vacío)", "—"]],
  lectura: "Penalidad si el riesgo ocurre: 60 % no se aplica, 30 % parcial, 10 % total. Media = 0×0,6 + 150 000×0,3 + 400 000×0,1 = S/ 85 000.",
  cuidado: "Mismo orden y misma cantidad de valores y probabilidades; deben sumar 1 (la validación lo revisa). El 0 aquí es un escenario, además de la probabilidad del riesgo.",
  narr: "La distribución discreta describe pocos escenarios posibles, cada uno con su probabilidad. Lleva dos parámetros de texto: en pe uno los valores separados por punto y coma, y en pe dos las probabilidades, en el mismo orden, también separadas por punto y coma. Deben sumar uno. Por ejemplo, una penalidad que, si el riesgo ocurre, puede no aplicarse, con sesenta por ciento; aplicarse parcialmente, ciento cincuenta mil soles, con treinta por ciento; o totalmente, cuatrocientos mil, con diez por ciento. La media es ochenta y cinco mil soles. Note que el cero aquí es un escenario adicional a la probabilidad del riesgo.",
});

// PARTE 6 — Casos especiales
s = divisor("PARTE 6", "Casos especiales al llenar el registro", "Situaciones que generan dudas frecuentes.",
  ["Dimensiones y unidades", "Oportunidades", "Respuestas y riesgo residual", "Correlación y errores frecuentes"]);
narrar(s, "Parte seis: casos especiales al llenar el registro. Veremos cómo manejar varias dimensiones y sus unidades, las oportunidades, las respuestas y el riesgo residual, la correlación, y los errores más frecuentes.");

s = nueva("6 · Dimensiones", "Una distribución por dimensión, en su unidad", "Cada dimensión se llena de forma independiente. Ejemplos del registro (estimaciones preliminares).");
[["COSTO", "S/", C.naranja, "R-01 Consumo de contingencia", "PERT 1 500 000 / 4 000 000 / 9 000 000", "Sobrecostos directos: material, mano de obra, equipos, penalidades."],
 ["PLAZO", "días", C.azul, "R-05 Demora aprobación UMAS", "TRIANGULAR 15 / 30 / 60", "Días de retraso. La macro los SUMA entre riesgos: supuesto conservador."],
 ["ING_DISENO", "HH", C.ambarP, "R-05 Demora aprobación UMAS", "TRIANGULAR 120 / 300 / 600", "Horas hombre adicionales de diseño: rediseños, RFI, revisiones."],
 ["ING_CAMPO", "HH", C.panel, "R-06 NC en tarrajeo y solaqueo", "TRIANGULAR 200 / 500 / 1 200", "Horas hombre de ingeniería de campo: supervisión, reprocesos, control."]].forEach((d, i) => {
  const x = M + i * 3.07;
  tarjeta(s, x, 2.15, 2.9, 3.6, C.tinte2);
  circulo(s, x + 0.2, 2.3, 0.6, d[1], d[2], C.blanco);
  txt(s, d[0], { x: x + 0.95, y: 2.35, w: 1.9, h: 0.5, fontSize: 15, bold: true, valign: "middle" });
  txt(s, d[5], { x: x + 0.2, y: 3.05, w: 2.55, h: 1.1, fontSize: 12.5 });
  txt(s, d[3], { x: x + 0.2, y: 4.2, w: 2.55, h: 0.55, fontSize: 12, bold: true, color: C.gris });
  txt(s, d[4], { x: x + 0.2, y: 4.8, w: 2.55, h: 0.85, fontSize: 12.5, bold: true, color: C.ambarP });
});
tarjeta(s, M, 5.95, W - 2 * M, 0.95, C.tinte);
txt(s, "No duplicar: si las HH ya están valorizadas dentro del COSTO del riesgo, no las ingrese además en ING_DISENO / ING_CAMPO, o hágalo sabiendo que son indicadores de carga, no de dinero. Revise unidades: soles (no miles), días calendario, HH (no días hombre).",
  { x: M + 0.25, y: 6.0, w: W - 2 * M - 0.5, h: 0.85, fontSize: 13, valign: "middle" });
narrar(s, "Cada dimensión se llena de forma independiente, en su propia unidad. El costo en soles, no en miles. El plazo en días calendario. Y la ingeniería de diseño y de campo en horas hombre, no en días hombre. Un riesgo puede usar distribuciones distintas en cada dimensión, por ejemplo PERT en costo y triangular en plazo. Y un cuidado importante: no duplicar. Si las horas hombre ya están valorizadas dentro del costo del riesgo, no las ingrese además como dinero en otra parte; las dimensiones de horas hombre sirven para medir la carga de trabajo de ingeniería.");

s = nueva("6 · Oportunidades", "Oportunidades", "Riesgos con efecto positivo: reducen el costo o el plazo si ocurren.");
caja(s, M, 2.15, 5.9, 4.6, "Cómo se ingresan", "1. TIPO = OPORTUNIDAD.\n2. PROBABILIDAD como cualquier riesgo.\n3. La distribución con parámetros POSITIVOS: el ahorro de 100 000 a 300 000 se escribe PERT 100 000 / 180 000 / 300 000.\n4. La macro les aplica signo negativo: restan del total en cada iteración en que ocurren.", { fill: C.tinte, fs: 14 });
caja(s, M + 6.15, 2.15, 5.9, 4.6, "Ejemplo y efecto", "Proveedor adelanta la entrega de acero: probabilidad 0,30; PLAZO TRIANGULAR 3 / 5 / 10 días de ahorro.\n\nEn el 30 % de las iteraciones el plazo total baja entre 3 y 10 días. VME = −1,8 días.\n\nSe marcan en verde en TORNADO, RANGOS y MATRIZ_PI. Aparecen con barras hacia la izquierda en el tornado.", { fs: 14 });
narrar(s, "Las oportunidades son riesgos con efecto positivo. Se ingresan con tipo igual a oportunidad, su probabilidad, y una distribución con parámetros positivos: el ahorro se escribe como un número positivo. La macro les aplica el signo negativo, de modo que restan del total en cada iteración en que ocurren. Por ejemplo, que el proveedor adelante la entrega del acero, con probabilidad de treinta por ciento y un ahorro de tres a diez días. Las oportunidades se marcan en verde en las hojas de resultados.");

s = nueva("6 · Respuestas", "Respuestas y riesgo residual", "La herramienta simula dos escenarios con los mismos números aleatorios: antes y después de las respuestas.");
tabla(s, [["Columna", "Qué significa", "Ejemplo R-14"],
  ["ESTRATEGIA", "Evitar, mitigar, transferir, aceptar (amenazas); explotar, mejorar, compartir (oportunidades)", "MITIGAR"],
  ["PROB_RESIDUAL", "Probabilidad después de la respuesta (vacía = igual)", "0,20 (antes 0,40)"],
  ["FACTOR_IMPACTO_RESIDUAL", "Multiplica el impacto: 0,5 = la mitad (vacío = 1)", "0,5"],
  ["COSTO_RESPUESTA", "Lo que cuesta implementar la respuesta, en S/", "300 000"]],
  { x: M, y: 2.15, w: W - 2 * M, colW: [3.0, 6.6, 2.53], rowH: 0.55, fs: 13, primeraNegrita: true });
bullets(s, ["La distribución NO se reescribe: el factor la escala proporcionalmente.",
  "Con números aleatorios comunes, la diferencia entre antes y después se debe solo a la respuesta, no al azar.",
  "La respuesta conviene si la reducción del P80 (o de la media) supera su costo. COMPARACION muestra ese beneficio neto."],
  { x: M, y: 5.2, w: W - 2 * M, h: 1.7, fontSize: 14 });
narrar(s, "La herramienta permite evaluar respuestas. Para cada riesgo se indica la estrategia, la probabilidad residual después de la respuesta, un factor que multiplica el impacto, por ejemplo cero coma cinco si el impacto baja a la mitad, y el costo de implementar la respuesta. La distribución no se reescribe: el factor la escala. La macro simula antes y después con los mismos números aleatorios, de modo que la diferencia se debe solo a la respuesta. Y la respuesta conviene si la reducción del percentil ochenta supera su costo; la hoja comparación muestra ese beneficio neto.");

s = nueva("6 · Correlación", "Riesgos que se mueven juntos", "Si una misma causa agrava varios riesgos, deben simularse correlacionados.");
bullets(s, ["GRUPO_CORRELACION: el mismo nombre en los riesgos relacionados (APROBACIONES, CALIDAD, CONTRACTUAL…).",
  "RHO_GRUPO: intensidad entre 0 y 1. Guía: 0,3 débil · 0,5 moderada · 0,7 fuerte.",
  "Efecto: cuando uno sale alto, los otros del grupo tienden a salir altos. La media no cambia, pero el P80 y el P90 suben.",
  "Ignorar una correlación real subestima la contingencia.",
  "La correlación lograda es menor que la objetivo porque en muchas iteraciones algún riesgo no ocurre (vale 0)."],
  { x: M, y: 2.2, w: 6.8, h: 4.6, fontSize: 14 });
tabla(s, [["Grupo", "ρ objetivo", "ρ lograda"],
  ["CONTRACTUAL", "0,50", "0,41"], ["SOBRECONSUMO", "0,40", "0,34"], ["APROBACIONES", "0,50", "0,45"],
  ["CALIDAD", "0,40", "0,30"], ["INGENIERIA", "0,50", "0,44"], ["EXTENSION_PLAZO", "0,60", "0,50"]],
  { x: 7.9, y: 2.25, w: 4.8, colW: [2.2, 1.3, 1.3], rowH: 0.45, fs: 13, primeraNegrita: true });
pie(s, "Método Iman–Conover con un factor común por grupo (Vose 13.2). Valores de una corrida de prueba con las estimaciones preliminares.");
narrar(s, "Algunos riesgos se mueven juntos porque comparten una causa. Por ejemplo, si la Supervisión es lenta, se demoran varias aprobaciones a la vez. Para reflejarlo, se pone el mismo nombre de grupo en la columna grupo de correlación, y la intensidad en rho grupo, entre cero y uno: cero coma tres es débil, cero coma cinco moderada y cero coma siete fuerte. La correlación no cambia la media, pero sube el percentil ochenta y el noventa. Ignorar una correlación real subestima la contingencia. La hoja resultados muestra la correlación objetivo y la lograda, que es algo menor porque en muchas iteraciones algún riesgo no ocurre.");

s = nueva("6 · Checklist", "Errores frecuentes al llenar distribuciones", "La validación detecta errores de forma; los de concepto dependen de quien llena el registro.");
[["Probabilidad dentro del impacto", "Poner el 30 % del costo como impacto. La probabilidad va SOLO en PROBABILIDAD."],
 ["Peor caso como moda", "La moda es lo más frecuente, no lo más temido."],
 ["Mezclar unidades", "Soles vs. miles; días hábiles vs. calendario; HH vs. días hombre."],
 ["Duplicar impactos", "El mismo efecto en dos riesgos o en dos dimensiones."],
 ["Orden incoherente", "Mínimo > moda o moda > máximo: la validación lo marca en rojo."],
 ["Probabilidad mal usada", "1 a algo que puede no ocurrir; > 0,5 a algo casi seguro (mejor en la línea base)."],
 ["Rangos demasiado estrechos", "Exceso de confianza: amplíe o use TRIGEN."],
 ["Parámetro equivocado", "Escala en vez de desviación (LOGISTICA); tasa en vez de media (EXPONENCIAL)."]].forEach((e, i) => {
  const x = M + (i % 2) * 6.15, y = 2.15 + Math.floor(i / 2) * 1.18;
  tarjeta(s, x, y, 5.95, 1.05, C.tinte2);
  circulo(s, x + 0.18, y + 0.25, 0.5, "✕", C.rojo, C.negro);
  txt(s, e[0], { x: x + 0.85, y: y + 0.1, w: 5.0, h: 0.38, fontSize: 14, bold: true });
  txt(s, e[1], { x: x + 0.85, y: y + 0.5, w: 5.0, h: 0.5, fontSize: 12.5, color: C.gris });
});
narrar(s, "Estos son los errores más frecuentes. Meter la probabilidad dentro del impacto. Poner el peor caso como moda. Mezclar unidades, como soles con miles de soles. Duplicar impactos. Dar un orden incoherente entre mínimo, moda y máximo. Usar mal la probabilidad. Dar rangos demasiado estrechos por exceso de confianza. Y confundir parámetros, como la escala con la desviación en la logística, o la tasa con la media en la exponencial. La validación detecta los errores de forma, pero los de concepto dependen de quien llena el registro.");

// PARTE 7 — Ejecutar e interpretar
s = divisor("PARTE 7", "Ejecutar e interpretar", "Validación, corrida y lectura de resultados para proponer la contingencia.",
  ["Validar y correr", "RESULTADOS: reservas y precisión", "Curva S y contingencia", "Tornado, rangos, matriz y comparación"]);
narrar(s, "Parte siete: ejecutar e interpretar. Veremos cómo validar y correr la simulación, y cómo leer los resultados para proponer una contingencia justificada.");

s = nueva("7 · Ejecutar", "Validar y correr la simulación", "Cuatro botones en PARAMETROS. Habilite las macros al abrir el archivo.");
[["▶ CORRER SIMULACIÓN", "Valida, simula y escribe todas las hojas de resultados."], ["✔ VALIDAR DATOS", "Revisa el registro sin simular y marca las celdas con problemas."],
 ["✕ LIMPIAR RESULTADOS", "Borra las hojas de salida (no toca PARAMETROS)."], ["＋ AGREGAR DIMENSIÓN", "Crea una dimensión nueva con todas sus columnas."]].forEach((b, i) => {
  const y = 2.1 + i * 1.0;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: 3.6, h: 0.75, rectRadius: 0.1, fill: { color: C.negro }, line: { color: C.negro } });
  txt(s, b[0], { x: M, y, w: 3.6, h: 0.75, fontSize: 14, bold: true, color: C.ambar, align: "center", valign: "middle" });
  txt(s, b[1], { x: M + 3.85, y, w: 4.0, h: 0.75, fontSize: 13, valign: "middle" });
});
caja(s, 8.8, 2.1, 3.9, 1.95, "ROJO = error", "Impide correr: parámetro faltante, mínimo > moda, probabilidad fuera de 0–1, texto en vez de número.", { fill: C.rojo, colC: C.negro });
caja(s, 8.8, 4.2, 3.9, 1.95, "ÁMBAR = advertencia", "Permite correr, pero revise: probabilidad > 0,5, riesgo sin impacto, estimado por validar.", { fill: C.amarillo, colC: C.negro });
txt(s, "Al terminar, un mensaje resume iteraciones, riesgos activos, semilla, tiempo y el P50 y P80 de cada dimensión. Si un gráfico no se crea, queda un aviso ámbar: los números siguen siendo válidos.",
  { x: M, y: 6.25, w: W - 2 * M, h: 0.65, fontSize: 13, italic: true, color: C.gris });
narrar(s, "Para ejecutar, abra el archivo y habilite las macros. En la hoja parámetros hay cuatro botones. Validar datos revisa el registro sin simular: marca en rojo los errores que impiden correr, como un parámetro faltante o un mínimo mayor que la moda, y en ámbar las advertencias, que permiten correr pero conviene revisar. Correr simulación valida, simula y escribe todas las hojas. Limpiar resultados borra las hojas de salida. Y agregar dimensión crea una nueva. Al terminar, un mensaje resume la corrida y muestra el percentil cincuenta y el ochenta de cada dimensión.");

s = nueva("7 · Interpretar", "RESULTADOS: reservas y precisión", "Un bloque por dimensión. Así se lee el de COSTO (corrida de prueba con estimaciones preliminares).");
tabla(s, [["Fila", "Valor", "Qué significa"],
  ["Media (valor esperado)", "≈ S/ 16,2 M", "Promedio del impacto de los riesgos"],
  ["VME total", "S/ 16,3 M", "Σ probabilidad × impacto medio; debe parecerse a la media"],
  ["a) Reserva para contingencias (P80)", "S/ 21,3 M", "La contingencia al nivel elegido (10,7 % de la base)"],
  ["b) Contingencia sobre la media (P80 − media)", "≈ S/ 5,1 M", "Variante de Vose: el colchón por encima del promedio"],
  ["c) Reserva de gestión", "S/ 0", "% × base (hoy 0 %)"],
  ["d) Presupuesto recomendado", "S/ 221,3 M", "Base + a + c"],
  ["IC 95 % del P80 / precisión", "± ≈ 1 %", "«Suficiente»: no hace falta subir iteraciones"]],
  { x: M, y: 2.1, w: W - 2 * M, colW: [4.4, 2.0, 5.73], rowH: 0.52, fs: 13, primeraNegrita: true });
narrar(s, "La hoja resultados tiene un bloque por dimensión. En costo, con los datos de prueba, la media del impacto de los riesgos es de unos dieciséis millones de soles, muy parecida al valor monetario esperado total, lo que confirma que la simulación es coherente. La fila a es la reserva para contingencias al percentil ochenta: veintiún coma tres millones, el diez coma siete por ciento de la base. La fila b muestra la variante de Vose: presupuestar la media y un colchón de unos cinco millones por encima. La fila c es la reserva de gestión, y la d el presupuesto recomendado. Al final, la precisión indica si las iteraciones fueron suficientes.");

s = nueva("7 · Interpretar", "Curva S y contingencia", "La reserva para contingencias es el P(nivel) del impacto TOTAL de los riesgos. Con nivel 80 %: el P80.");
const pctL = [], pctV = [];
sim.pct.forEach((v, i) => { pctL.push(v / 1e6); pctV.push(i * 5); });
s.addChart(pres.charts.SCATTER, [{ name: "X", values: pctL.map(r3) }, { name: "Costo", values: pctV }], {
  x: M, y: 2.1, w: 7.0, h: 4.6, lineSize: 3, lineDataSymbol: "none", chartColors: [C.naranja], showLegend: false,
  valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20, showValAxisTitle: true, valAxisTitle: "% acumulado", valAxisTitleFontSize: 11, valAxisTitleColor: C.gris,
  valAxisLabelColor: C.gris, valAxisLabelFontSize: 11, valGridLine: { color: "E0E0E0", size: 0.5 }, catGridLine: { style: "none" },
  catAxisMinVal: 0, catAxisMaxVal: 45, catAxisMajorUnit: 5, catAxisLabelColor: C.gris, catAxisLabelFontSize: 11,
  showCatAxisTitle: true, catAxisTitle: "Impacto total de los riesgos en costo (millones de S/)", catAxisTitleFontSize: 11, catAxisTitleColor: C.gris,
  showTitle: true, title: "Curva S — costo", titleFontSize: 13, titleFontFace: F });
[["P50", "15,7 M", "Mitad de los escenarios por debajo"], ["P80", "21,3 M", "Reserva para contingencias"], ["P90", "24,7 M", "Nivel exigente: +3,3 M"]].forEach((k, i) => {
  const y = 2.1 + i * 1.25;
  tarjeta(s, 7.9, y, 4.8, 1.1, i === 1 ? C.ambar : C.tinte2);
  txt(s, k[0], { x: 8.1, y: y + 0.1, w: 1.0, h: 0.9, fontSize: 18, bold: true, valign: "middle" });
  txt(s, "S/ " + k[1], { x: 9.0, y: y + 0.05, w: 3.5, h: 0.55, fontSize: 24, bold: true });
  txt(s, k[2], { x: 9.0, y: y + 0.62, w: 3.6, h: 0.4, fontSize: 12, color: C.gris });
});
txt(s, "No sume los P80 de cada riesgo: la contingencia es el P80 del TOTAL. Plazo: P80 ≈ 122 días (suma de retrasos: supuesto conservador; contrastar con el cronograma).",
  { x: 7.9, y: 5.95, w: 4.8, h: 0.95, fontSize: 12.5, bold: true });
narrar(s, "La curva S del costo muestra, para cada monto, la probabilidad de no superarlo. La contingencia se lee en el nivel elegido. Con ochenta por ciento, el percentil ochenta es de veintiún coma tres millones de soles. El percentil cincuenta es de quince coma siete, y el noventa de veinticuatro coma siete: pasar de ochenta a noventa por ciento de confianza cuesta unos tres coma tres millones más. Dos advertencias. No sume los percentiles ochenta de cada riesgo: la contingencia es el percentil ochenta del total. Y en plazo, la macro suma los retrasos de todos los riesgos, lo que es conservador: contrástelo con el cronograma.");

s = nueva("7 · Interpretar", "Tornado, rangos, matriz y comparación", "Las demás hojas responden preguntas de gestión, no solo de presupuesto.");
[["TORNADO", "¿Qué riesgos mueven más el total?", "Ordena por «swing»: cuánto cambia el total cuando el riesgo está en su 10 % alto frente a su 10 % bajo. Los primeros son donde conviene invertir en respuestas."],
 ["RANGOS", "¿Cuánto aporta cada riesgo?", "Mínimo, P10…P90, máximo, promedio y VME de cada riesgo en cada dimensión, incluidos los escenarios en que no ocurre."],
 ["MATRIZ_PI", "¿Cómo se ve el registro en la matriz?", "Ubica cada riesgo en la matriz probabilidad–impacto 5×5 con las escalas de tblEscalas: útil para reportes cualitativos."],
 ["COMPARACION", "¿Valen la pena las respuestas?", "Curvas S antes y después, reducción del P80 y beneficio neto frente al costo de las respuestas."]].forEach((c, i) => {
  const x = M + (i % 2) * 6.15, y = 2.1 + Math.floor(i / 2) * 2.4;
  tarjeta(s, x, y, 5.95, 2.2, C.tinte2);
  tarjeta(s, x + 0.2, y + 0.2, 2.2, 0.5, C.negro);
  txt(s, c[0], { x: x + 0.2, y: y + 0.2, w: 2.2, h: 0.5, fontSize: 13.5, bold: true, color: C.ambar, align: "center", valign: "middle" });
  txt(s, c[1], { x: x + 2.55, y: y + 0.2, w: 3.3, h: 0.5, fontSize: 13.5, bold: true, valign: "middle" });
  txt(s, c[2], { x: x + 0.2, y: y + 0.85, w: 5.55, h: 1.3, fontSize: 13, color: C.gris });
});
narrar(s, "Las demás hojas responden preguntas de gestión. El tornado ordena los riesgos según cuánto mueven el total: los primeros son donde conviene invertir en respuestas. Rangos muestra el aporte de cada riesgo con sus percentiles y su valor monetario esperado. La matriz de probabilidad e impacto ubica cada riesgo en una cuadrícula de cinco por cinco, útil para reportes cualitativos. Y comparación muestra las curvas S antes y después de las respuestas, cuánto baja el percentil ochenta y si el beneficio supera el costo de las respuestas.");

s = oscura();
txt(s, "ANTES DE PRESENTAR RESULTADOS", { x: M, y: 0.8, w: 11, h: 0.4, fontSize: 14, bold: true, color: C.ambar, charSpacing: 3 });
txt(s, "Checklist final", { x: M, y: 1.25, w: 11, h: 0.8, fontSize: 36, bold: true, color: C.blanco });
["Costo base y plazo base reemplazados por los del contrato (hoy son supuestos).",
 "Cada estimación «ESTIMADO – VALIDAR» revisada con el dueño del riesgo; fuente anotada en NOTAS.",
 "Distribución elegida según lo que se sabe (árbol de decisión); PERT por defecto.",
 "Probabilidad separada del impacto; unidades revisadas; sin impactos duplicados.",
 "Oportunidades con parámetros positivos y TIPO = OPORTUNIDAD.",
 "Correlación definida para los riesgos con causa común.",
 "Validación sin errores rojos; advertencias ámbar revisadas.",
 "Precisión «Suficiente»; contingencia leída en el P(nivel) del TOTAL."].forEach((c, i) => {
  const y = 2.3 + i * 0.58;
  circulo(s, M, y, 0.4, "✓", C.ambar, C.negro);
  txt(s, c, { x: M + 0.65, y: y - 0.03, w: 11.5, h: 0.46, fontSize: 15.5, color: C.blanco, valign: "middle" });
});
narrar(s, "Terminamos con un checklist antes de presentar resultados. Reemplace el costo y el plazo base por los del contrato. Revise cada estimación con su dueño y anote la fuente. Elija la distribución según lo que se sabe, con PERT por defecto. Separe la probabilidad del impacto, revise unidades y evite duplicados. Ingrese las oportunidades con parámetros positivos. Defina la correlación de los riesgos con causa común. Corrija los errores rojos y revise las advertencias. Y confirme que la precisión sea suficiente y que la contingencia se lea en el percentil del total. Muchas gracias.");

fs.writeFileSync(__dirname + "/narracion.json", JSON.stringify(narr, null, 1));
console.log("Láminas:", num, "Narraciones:", narr.length);
pres.writeFile({ fileName: process.argv[2] || "Guia_Extendida_MonteCarlo.pptx" }).then(f => console.log("OK", f));
