// Proyectos de ejemplo de USD 50 M, 100 M y 200 M para conocer la aplicación con datos.
// Se crean con la sesión del usuario (RLS: queda como propietario) y con es_ejemplo = true.
// Todas las fechas son relativas al día en que se cargan, para que los estados
// (hitos cumplidos, paquetes en ejecución, restricciones por vencer) sean coherentes.
import { sb, q, traducirError, registrarInstantanea } from './db.js';
import { crear, proponerHitos } from '../vistas/asistente.js';
import { hoyISO, sumarDias, dias } from './fechas.js';

const PLAZOS_F2 = [12, 10, 8, 4, 2], PLAZOS = [8, 6, 5, 3, 2];

export const EJEMPLOS = [
  {
    codigo: 'EJ-PTA', nombre: 'Planta de tratamiento de agua potable (ejemplo)', presupuesto: 50e6,
    tipo: 'Infraestructura', cliente: 'Empresa regional de agua (cliente de ejemplo)', ubicacion: 'Lima, Perú',
    responsable: 'Jorge Vargas', meses: 24, inicioHace: 15, estado: 'En ejecución',
    descripcion: 'Proyecto de ejemplo de USD 50 M: planta de 1,5 m³/s con captación, línea de impulsión de 6 km, decantadores, filtros, reservorios y sala eléctrica. Contrato EPC a suma alzada. ≈ 940 000 HH directas; pico de 380 trabajadores.',
    fases: [
      { nombre: 'Captación, línea de impulsión y reservorios', alcance: 'Obras civiles de captación, cámara de bombeo, 6 km de tubería DN 900 y reservorios R1 y R2.', ini: 0.5, fin: 13, madurez: 2, plazos: PLAZOS, backlog: 2, hh: 380000, pico: 250 },
      { nombre: 'Planta de tratamiento y electromecánica', alcance: 'Decantadores, filtros, edificio químico, sala eléctrica, montaje electromecánico y pruebas.', ini: 5, fin: 24, madurez: 3, plazos: [10, 8, 6, 3, 2], backlog: 2, hh: 560000, pico: 380 },
    ],
    actividades: { FEL: [8, 0], ING: [5, 1], PRO: [4, 1], CON: [4, 2], COM: [1, 1] },
    atrasados: { 2: 1 }, planificadores: 8,
    cwa: [
      ['CWA-1.01', 1, 'Captación y cámara de bombeo', 'CIV, MEC, ELE', 120000, 1, null, 'Bocatoma, desarenador y cámara de bombeo'],
      ['CWA-1.02', 1, 'Línea de impulsión', 'TUB, CIV', 140000, 2, 'CWA-1.01', 'Tramos 1 a 3, 6 km hasta la planta'],
      ['CWA-1.03', 1, 'Reservorios', 'CIV', 120000, 2, 'CWA-1.01', 'Reservorios R1 y R2 de 10 000 m³'],
      ['CWA-2.02', 2, 'Sala eléctrica y control', 'CIV, ELE, INS', 90000, 1, null, 'Sala eléctrica, transformadores y sala de control'],
      ['CWA-2.01', 2, 'Decantadores y filtros', 'CIV, EST, TUB, MEC', 330000, 2, 'CWA-2.02', 'Ejes A–F del área de proceso'],
      ['CWA-2.03', 2, 'Edificio químico y oficinas', 'CIV, ARQ, MEC', 140000, 3, 'CWA-2.01', 'Almacén de químicos, dosificación y oficinas'],
    ],
    cwp: [
      ['CWP-1.01-CIV-01', 'Obras civiles de captación y cámara de bombeo', 'CIV', 60000, 3, 16, null, 'Captación', 'Primer frente: habilita el bombeo para la prueba hidráulica de la línea.'],
      ['CWP-1.02-TUB-01', 'Tubería de impulsión DN 900, tramos 1 a 3', 'TUB', 90000, 4.5, 30, null, 'Agua cruda', 'Frente lineal independiente; se ejecuta en paralelo con la captación.'],
      ['CWP-1.03-CIV-01', 'Reservorios R1 y R2', 'CIV', 80000, 6, 28, null, 'Almacenamiento', 'Debe estar listo para recibir agua tratada en las pruebas de la Fase 2.'],
      ['CWP-2.02-ELE-01', 'Sala eléctrica, transformadores y tableros', 'ELE', 45000, 9, 24, null, 'Distribución eléctrica', 'Energización temprana para probar bombas y filtros.'],
      ['CWP-2.01-CIV-01', 'Cimentaciones de decantadores y filtros', 'CIV', 120000, 9, 22, null, 'Estructura de proceso', 'Primer frente de la planta; libera el montaje electromecánico.'],
      ['CWP-2.01-MEC-01', 'Montaje de equipos de filtración', 'MEC', 70000, 15, 20, 'CWP-2.01-CIV-01', 'Filtración', 'Requiere cimentaciones terminadas y equipos en obra (RAS).'],
      ['CWP-2.01-TUB-01', 'Tuberías de proceso de decantadores y filtros', 'TUB', 90000, 16, 24, 'CWP-2.01-CIV-01', 'Agua tratada', 'Tuberías sobre estructuras terminadas, por módulo.'],
      ['CWP-2.03-ARQ-01', 'Edificio químico y oficinas', 'ARQ', 40000, 17, 20, null, 'Dosificación química', 'Edificio independiente; su entrega temprana permite la dosificación en las pruebas.'],
    ],
    restricciones: [
      ['CWP-2.01-MEC-01', 'Materiales', 'Llegada de los paneles de filtración importados', 'PRO', -20, 10, 'Liberada'],
      ['CWP-2.01-MEC-01', 'Andamios', 'Andamios certificados para el montaje en altura de los filtros', 'SUP', -12, 5, 'En gestión'],
      ['CWP-2.01-TUB-01', 'Ingeniería', 'Planos IFC de tuberías del módulo 2 con la revisión de constructabilidad', 'ING', -10, 12, 'Abierta'],
      ['CWP-2.01-TUB-01', 'Materiales', 'Válvulas mariposa DN 600 con tag (PWP-2.01-TUB-01)', 'PRO', -8, 20, 'En gestión'],
      ['CWP-2.03-ARQ-01', 'Permisos', 'Licencia de edificación del edificio químico', 'CLI', -30, 4, 'Abierta'],
      ['CWP-2.03-ARQ-01', 'HSE', 'Plan de izaje del tanque de hipoclorito', 'HSE', -6, 25, 'Abierta'],
    ],
    riesgos: [[3, 3, 'En tratamiento'], [3, 3, 'En tratamiento'], [4, 3, 'Abierto'], [2, 4, 'En tratamiento'], [2, 3, 'Cerrado'], [3, 4, 'En tratamiento']],
  },
  {
    codigo: 'EJ-MIN', nombre: 'Ampliación de planta concentradora (ejemplo)', presupuesto: 100e6,
    tipo: 'Minería', cliente: 'Compañía minera (cliente de ejemplo)', ubicacion: 'Arequipa, Perú',
    responsable: 'Rosa Salas', meses: 30, inicioHace: 8, estado: 'En ejecución',
    descripcion: 'Proyecto de ejemplo de USD 100 M: ampliación de 40 000 a 60 000 t/d con chancado secundario, molino de bolas, celdas de flotación, espesadores y relaves. Contrato EPCM. ≈ 1,9 M HH directas; pico de 900 trabajadores.',
    fases: [
      { nombre: 'Obras tempranas, plataformas y accesos', alcance: 'Movimiento de tierras, vías, campamento, redes enterradas y bancos de ductos.', ini: 0.5, fin: 11, madurez: 2, plazos: PLAZOS, backlog: 2, hh: 420000, pico: 300 },
      { nombre: 'Molienda y flotación', alcance: 'Subestación, molino de bolas, celdas de flotación, chancado secundario y sala eléctrica.', ini: 4, fin: 26, madurez: 3, plazos: PLAZOS_F2, backlog: 2, hh: 1100000, pico: 650 },
      { nombre: 'Espesadores, relaves y servicios', alcance: 'Espesadores, sistema de relaves, agua recuperada y conexiones con la planta existente.', ini: 12, fin: 30, madurez: 4, plazos: PLAZOS, backlog: 3, hh: 380000, pico: 250 },
    ],
    actividades: { FEL: [7, 1], ING: [3, 2], PRO: [2, 2], CON: [2, 2], COM: [0, 1] },
    atrasados: { 1: 1, 2: 1 }, planificadores: 5,
    cwa: [
      ['CWA-1.01', 1, 'Plataformas y movimiento de tierras', 'CIV', 180000, 1, null, 'Plataformas de molienda y flotación'],
      ['CWA-1.02', 1, 'Accesos y campamento', 'CIV, ARQ, ELE', 120000, 1, null, 'Vía de acceso, campamento de 600 camas y patio de acopio'],
      ['CWA-1.03', 1, 'Redes enterradas', 'TUB, ELE', 120000, 2, 'CWA-1.01', 'Redes de agua, relaves enterrados y bancos de ductos'],
      ['CWA-2.03', 2, 'Subestación y sala eléctrica', 'CIV, ELE, INS', 160000, 1, 'CWA-1.03', 'Subestación 220 kV y sala eléctrica de molienda'],
      ['CWA-2.01', 2, 'Molienda', 'Todas', 520000, 2, 'CWA-2.03', 'Molino de bolas, chancado secundario y fajas'],
      ['CWA-2.02', 2, 'Flotación', 'Todas', 420000, 3, 'CWA-2.01', 'Celdas de flotación rougher y cleaner'],
      ['CWA-3.01', 3, 'Espesadores', 'CIV, EST, MEC', 200000, 1, null, 'Espesadores de relaves y de concentrado'],
      ['CWA-3.02', 3, 'Relaves y agua recuperada', 'TUB, MEC', 180000, 2, 'CWA-3.01', 'Líneas de relaves y estación de agua recuperada'],
    ],
    cwp: [
      ['CWP-1.01-CIV-01', 'Plataforma de molienda', 'CIV', 90000, 2.5, 18, null, 'Plataformas', 'Libera la huella del molino para la Fase 2.'],
      ['CWP-1.02-CIV-01', 'Vías de acceso y campamento', 'CIV', 60000, 3, 20, null, 'Instalaciones temporales', 'Acceso y alojamiento para el pico de la Fase 2.'],
      ['CWP-1.03-TUB-01', 'Redes de agua y relaves enterradas', 'TUB', 50000, 7, 16, 'CWP-1.01-CIV-01', 'Agua de proceso', 'Redes enterradas antes de cimentaciones para evitar interferencias.'],
      ['CWP-1.03-ELE-01', 'Bancos de ductos eléctricos', 'ELE', 40000, 7.5, 14, 'CWP-1.01-CIV-01', 'Energía', 'Alimenta la futura subestación de 220 kV.'],
      ['CWP-2.01-CIV-01', 'Cimentación del molino de bolas', 'CIV', 110000, 10, 22, 'CWP-1.01-CIV-01', 'Molienda', 'Camino crítico: el molino es el equipo de mayor plazo.'],
      ['CWP-2.03-ELE-01', 'Subestación 220 kV y sala eléctrica', 'ELE', 70000, 11, 30, 'CWP-1.03-ELE-01', 'Distribución eléctrica', 'Energización temprana para las pruebas de molienda.'],
      ['CWP-3.01-CIV-01', 'Cimentación de espesadores', 'CIV', 80000, 14, 20, null, 'Espesamiento', 'Frente independiente de la Fase 3.'],
      ['CWP-2.01-MEC-01', 'Montaje del molino de bolas', 'MEC', 90000, 16, 26, 'CWP-2.01-CIV-01', 'Molienda', 'Requiere cimentación curada y el molino en obra (RAS).'],
    ],
    restricciones: [
      ['CWP-1.03-TUB-01', 'Permisos', 'Permiso de excavación en la zona de relaves existente', 'CLI', -25, -6, 'Abierta'],
      ['CWP-1.03-TUB-01', 'Materiales', 'Tubería HDPE de 24" para relaves (PWP-1.03-TUB-01)', 'PRO', -30, -8, 'Liberada'],
      ['CWP-1.03-ELE-01', 'Trabajos predecesores', 'Entrega de la plataforma norte por el CWP-1.01-CIV-01', 'CON', -40, -20, 'Liberada'],
      ['CWP-1.03-ELE-01', 'Mano de obra', 'Cuadrilla de electricistas del subcontratista', 'SUB', -10, 6, 'En gestión'],
      ['CWP-2.01-CIV-01', 'Ingeniería', 'Planos IFC de la cimentación del molino con cargas del proveedor', 'ING', -15, 18, 'En gestión'],
      ['CWP-2.01-CIV-01', 'Documentación del proveedor', 'Planos certificados del molino de bolas', 'PRO', -20, 12, 'Abierta'],
      ['CWP-2.01-CIV-01', 'Equipos de construcción', 'Grúa de 250 t para los pernos de anclaje', 'CON', -5, 30, 'Abierta'],
    ],
    riesgos: [[4, 4, 'En tratamiento'], [4, 4, 'Abierto'], [3, 4, 'En tratamiento'], [3, 3, 'Abierto'], [4, 3, 'Abierto'], [2, 3, 'En tratamiento']],
  },
  {
    codigo: 'EJ-HOS', nombre: 'Hospital regional de alta complejidad (ejemplo)', presupuesto: 200e6,
    tipo: 'Hospitalario', cliente: 'Gobierno regional (cliente de ejemplo)', ubicacion: 'Piura, Perú',
    responsable: 'Miguel Torres', meses: 36, inicioHace: 3, estado: 'En ejecución',
    descripcion: 'Proyecto de ejemplo de USD 200 M: hospital de 450 camas con 4 bloques asistenciales (emergencia, centro quirúrgico y UCI, hospitalización, consulta externa), central de energía y obras exteriores. Diseño y construcción. ≈ 3,6 M HH directas; pico de 1 500 trabajadores.',
    fases: [
      { nombre: 'Obras tempranas, cimentaciones y central de energía', alcance: 'Movimiento de tierras, muros, redes exteriores enterradas, subestación y central de energía.', ini: 1, fin: 14, madurez: 2, plazos: PLAZOS, backlog: 2, hh: 900000, pico: 500 },
      { nombre: 'Bloques asistenciales', alcance: 'Estructura, arquitectura e instalaciones de los bloques A a D.', ini: 6, fin: 30, madurez: 3, plazos: PLAZOS_F2, backlog: 2, hh: 2200000, pico: 1100 },
      { nombre: 'Equipamiento, obras exteriores y puesta en marcha', alcance: 'Equipamiento médico, obras exteriores, pruebas integrales y entrega por sistemas.', ini: 20, fin: 36, madurez: 4, plazos: PLAZOS, backlog: 3, hh: 500000, pico: 300 },
    ],
    actividades: { FEL: [4, 1], ING: [1, 1], PRO: [0, 0], CON: [0, 0], COM: [1, 0] },
    atrasados: { 1: 1 }, planificadores: 1,
    cwa: [
      ['CWA-1.01', 1, 'Movimiento de tierras y muros', 'CIV', 260000, 1, null, 'Todo el terreno: cortes, rellenos y muros de contención'],
      ['CWA-1.02', 1, 'Central de energía y subestación', 'CIV, EST, ELE, MEC', 280000, 2, 'CWA-1.01', 'Subestación, grupos electrógenos, chillers y calderos'],
      ['CWA-1.03', 1, 'Redes exteriores enterradas', 'TUB, ELE', 180000, 2, 'CWA-1.01', 'Agua, desagüe, gases medicinales y bancos de ductos'],
      ['CWA-2.01', 2, 'Bloque A · Emergencia', 'Todas', 480000, 1, 'CWA-1.02', 'Ejes 1–8'],
      ['CWA-2.02', 2, 'Bloque B · Centro quirúrgico y UCI', 'Todas', 520000, 2, 'CWA-2.01', 'Ejes 9–16'],
      ['CWA-2.03', 2, 'Bloque C · Hospitalización', 'Todas', 700000, 3, 'CWA-2.01', 'Torre de hospitalización, 8 niveles'],
      ['CWA-2.04', 2, 'Bloque D · Consulta externa', 'Todas', 400000, 4, 'CWA-2.03', 'Ejes 17–24'],
      ['CWA-3.01', 3, 'Obras exteriores', 'CIV, ELE', 200000, 1, null, 'Pavimentos, estacionamientos, cercos e iluminación'],
      ['CWA-3.02', 3, 'Equipamiento médico', 'MEC, ELE, INS', 300000, 2, null, 'Equipos de imágenes, esterilización y mobiliario clínico'],
    ],
    cwp: [], restricciones: [],
    riesgos: [[3, 5, 'Abierto'], [4, 4, 'Abierto'], [3, 3, 'Abierto'], [3, 4, 'Abierto'], [4, 3, 'Abierto'], [3, 3, 'Abierto']],
  },
];

// Riesgos del kit adaptados (se asignan P e I por proyecto).
const RIESGOS = [
  ['R01', 'Todas las fases', 'Planificación temprana (FEL)', 'Organización y liderazgo', 'Falta de patrocinio del cliente; AWP percibido como «papeleo adicional».', 'Beneficios de AWP no comunicados.', 'Abandono parcial del proceso.', 'Plan firmado por el cliente; Comité AWP mensual; comunicar resultados de la Fase 1.', 'CHA'],
  ['R02', 'Fase 2', 'Ingeniería', 'Procesos', 'Ingeniería no entrega EWP en la secuencia del PoC.', 'Planificación por disciplina y no por CWP.', 'CWP sin planos IFC; backlog insuficiente.', 'Fechas de EWP del PoC en el contrato; K01; revisión quincenal del plan de liberación.', 'ING'],
  ['R03', 'Fase 2', 'Construcción', 'Personas y competencias', 'Falta de planificadores de frente de trabajo con experiencia.', 'Mercado laboral competido.', 'IWP de baja calidad; restricciones no detectadas.', 'Formar planificadores en la Fase 1; reclutamiento anticipado; formación de 40 h.', 'CHA'],
  ['R04', 'Fases 1 y 2', 'Procura', 'Herramientas e información', 'Procura no sigue los materiales por CWP/IWP.', 'Órdenes de compra sin código de CWP.', 'No se sabe qué IWP tiene material completo.', 'PWP por CWP; código de CWP en órdenes de compra; reporte semanal de disponibilidad.', 'PRO'],
  ['R08', 'Fase 2', 'Construcción', 'Procesos', 'Backlog insuficiente por ingeniería o procura detrás del PoC.', 'Atrasos de EWP y PWP.', 'Cuadrillas sin trabajo liberado.', 'Backlog proyectado a 8 semanas; alertas tempranas; trabajo de «plan B».', 'CON'],
  ['R09', 'Fases 2 y 3', 'Construcción', 'Interfaces entre fases', 'Conflictos de recursos e interfaces entre fases superpuestas.', 'Grúas, accesos y almacenes compartidos.', 'Interferencias y demoras en ambas fases.', 'Registro único de restricciones; lookahead conjunto; tablero de recursos compartidos.', 'CON'],
];

const NOMBRES = {
  CLI: 'Patricia Luna', GP: null, CHA: 'Ana Rojas', LWF: 'Luis Díaz', WFP: 'Pedro Soto', ING: 'Rosa Quispe', PRO: 'Martín Flores', MAT: 'Carmen Ríos',
  CON: 'Carla Paz', SUP: 'Julio Mendoza', CTR: 'Lucía Ramos', IM: 'Diego Castro', HSE: 'Sofía Herrera', CAL: 'Andrés Medina', COM: 'Elena Vega', SUB: 'Montajes del Sur (ejemplo)',
};
const OTROS_WFP = ['Raúl Chávez', 'Marco Aguilar', 'Silvia Paredes', 'Óscar Núñez', 'Teresa Campos', 'Hugo Salazar', 'Gloria Espinoza', 'Iván Gutiérrez'];
const ORG = { CLI: 'Cliente', GP: 'Contratista', SUB: 'Subcontratista' };
const RESPONSABLE_ETAPA = { FEL: 'CHA', ING: 'ING', PRO: 'PRO', CON: 'LWF', COM: 'COM' };
// Días entre la fecha plan y la real: la mayoría a tiempo, algunos con atraso.
const RETRASOS = [-3, 0, -5, 4, -1, 0, -2, 9, 0, -4];

// Lunes de la semana de una fecha ISO.
const lunes = iso => { const [a, m, d] = iso.split('-').map(Number); const f = new Date(Date.UTC(a, m - 1, d)); const dw = (f.getUTCDay() + 6) % 7; f.setUTCDate(f.getUTCDate() - dw); return f.toISOString().slice(0, 10); };
const min = (a, b) => (a < b ? a : b);

export async function proyectosEjemploExistentes() {
  return q(sb.from('proyectos').select('id, codigo, es_ejemplo').eq('es_ejemplo', true));
}

// Crea los proyectos de ejemplo que aún no existan. «aviso(texto)» informa el avance.
export async function cargarEjemplos(catalogos, aviso = () => {}) {
  const hoy = hoyISO();
  const existentes = new Set((await q(sb.from('proyectos').select('codigo'))).map(p => p.codigo));
  const creados = [];
  for (const ej of EJEMPLOS) {
    if (existentes.has(ej.codigo)) { aviso(`${ej.codigo} ya existe: se omite.`); continue; }
    aviso(`Creando ${ej.nombre}…`);
    const inicio = sumarDias(hoy, -Math.round(ej.inicioHace * 30.44));
    const mes = m => sumarDias(inicio, Math.round(m * 30.44));
    const datos = { codigo: ej.codigo, nombre: ej.nombre, cliente: ej.cliente, ubicacion: ej.ubicacion, tipo: ej.tipo, presupuesto_usd: ej.presupuesto,
      fecha_inicio: inicio, fecha_fin: mes(ej.meses), responsable: ej.responsable, estado: ej.estado, descripcion: ej.descripcion };
    const fases = ej.fases.map((f, i) => {
      const fi = mes(f.ini), ff = mes(f.fin);
      return { numero: i + 1, nombre: f.nombre, alcance: f.alcance, estado: ff < hoy ? 'Cerrada' : fi <= hoy ? 'En ejecución' : 'Planificada',
        fecha_inicio: fi, fecha_fin: ff, madurez_objetivo: f.madurez, sem_iwp_iniciado: f.plazos[0], sem_identificadas: f.plazos[1], sem_asignadas: f.plazos[2],
        sem_levantadas: f.plazos[3], sem_liberacion: f.plazos[4], backlog_meta_sem: f.backlog };
    });
    const personas = Object.fromEntries(Object.entries(NOMBRES).map(([rol, n]) => [rol, { nombre: rol === 'GP' ? ej.responsable : n, organizacion: ORG[rol] || 'Contratista' }]));
    const hitos = proponerHitos(datos, fases, catalogos.hitos);
    const p = await crear({ datos, fases, personas, hitos, es_ejemplo: true }, catalogos);
    try {
      await completar(p, ej, fases, catalogos, hoy, mes, aviso);
    } catch (e) {
      await borrarProyecto(p.id).catch(() => {});
      throw traducirError(e);
    }
    creados.push(p);
  }
  return creados;
}

async function completar(p, ej, fasesPlan, catalogos, hoy, mes, aviso) {
  const fases = await q(sb.from('fases').select('id, numero').eq('proyecto_id', p.id));
  const idFase = Object.fromEntries(fases.map(f => [f.numero, f.id]));
  // Fases: horas y pico de personal
  await Promise.all(ej.fases.map((f, i) => q(sb.from('fases').update({ hh_estimadas: f.hh, pico_personal: f.pico }).eq('id', idFase[i + 1]))));
  // Planificadores adicionales (1 por cada 50 trabajadores cuando la obra ya está en marcha)
  const extra = OTROS_WFP.slice(0, Math.max(0, ej.planificadores - 1)).map(n => ({ proyecto_id: p.id, rol_codigo: 'WFP', nombre: n, organizacion: 'Contratista' }));
  if (extra.length) await q(sb.from('personas').insert(extra));

  // Checklist AWP: las primeras N completadas y las M siguientes en curso, por etapa
  aviso(`${ej.codigo}: checklist de implementación…`);
  const acts = await q(sb.from('avance_actividades').select('id, actividad').eq('proyecto_id', p.id));
  const plan = catalogos.actividades.slice().sort((a, b) => a.codigo.localeCompare(b.codigo));
  const cambios = [];
  for (const [etapa, [nc, ne]] of Object.entries(ej.actividades)) {
    const lista = plan.filter(a => a.codigo.startsWith(etapa + '-'));
    lista.forEach((a, k) => {
      const fila = acts.find(x => x.actividad === a.codigo);
      if (!fila || k >= nc + ne) return;
      const hecha = k < nc;
      const fecha = min(sumarDias(p.fecha_inicio, Math.round(dias(p.fecha_inicio, hoy) * (k + 1) / (nc + ne + 1))), hoy);
      cambios.push(q(sb.from('avance_actividades').update({
        estado: hecha ? 'Completada' : 'En curso', responsable_rol: RESPONSABLE_ETAPA[etapa],
        fecha_real: hecha ? fecha : null, evidencia: hecha ? (a.plantilla ? `${a.plantilla} aprobado` : 'Acta en la carpeta AWP del proyecto') : null,
      }).eq('id', fila.id)));
    });
  }
  await Promise.all(cambios);

  // Hitos: los vencidos se cumplen (con evidencia), salvo los que el ejemplo deja atrasados
  aviso(`${ej.codigo}: hitos H0–H10…`);
  const hitos = await q(sb.from('hitos').select('id, fase_id, codigo, fecha_plan, evidencia').eq('proyecto_id', p.id));
  const numFase = Object.fromEntries(fases.map(f => [f.id, f.numero]));
  const dejar = new Set();
  for (const [n, cant] of Object.entries(ej.atrasados)) {
    hitos.filter(h => numFase[h.fase_id] === Number(n) && h.fecha_plan < hoy).sort((a, b) => b.fecha_plan.localeCompare(a.fecha_plan)).slice(0, cant).forEach(h => dejar.add(h.id));
  }
  await Promise.all(hitos.map((h, i) => {
    if (h.fecha_plan < hoy && !dejar.has(h.id)) {
      return q(sb.from('hitos').update({ estado: 'Cumplido', fecha_real: min(sumarDias(h.fecha_plan, RETRASOS[i % RETRASOS.length]), hoy), comentario: 'Evidencia: ' + (h.evidencia || 'acta firmada') }).eq('id', h.id));
    }
    if (dejar.has(h.id) || (h.fecha_plan >= hoy && h.fecha_plan <= sumarDias(hoy, 30))) return q(sb.from('hitos').update({ estado: 'En curso' }).eq('id', h.id));
    return null;
  }));

  // CWA
  aviso(`${ej.codigo}: áreas (CWA), paquetes y restricciones…`);
  const cwaIns = await q(sb.from('cwa').insert(ej.cwa.map(([codigo, fase, nombre, disc, hh, sec, , limites]) => {
    const fp = fasesPlan[fase - 1];
    return { proyecto_id: p.id, fase_id: idFase[fase], codigo, nombre, limites, disciplinas: disc, hh_estimadas: hh, secuencia: sec,
      fecha_inicio: fp.fecha_inicio, fecha_fin: fp.fecha_fin, responsable_rol: 'CON', cumple_criterios: true,
      estado: fp.fecha_inicio <= hoy ? 'Aprobado' : 'En desarrollo' };
  })).select('id, codigo'));
  const idCwa = Object.fromEntries(cwaIns.map(c => [c.codigo, c.id]));
  await Promise.all(ej.cwa.filter(c => c[6]).map(c => q(sb.from('cwa').update({ predecesora_id: idCwa[c[6]] }).eq('id', idCwa[c[0]]))));

  // CWP con su EWP, PWP e IWP (estados según la fecha de hoy)
  if (ej.cwp.length) {
    const filasCwp = ej.cwp.map(([codigo, desc, dis, hh, m, sem, , sistema, just], k) => {
      const ini = mes(m), fin = sumarDias(ini, sem * 7), emision = sumarDias(ini, -70);
      const estado = fin < hoy ? 'Cerrado' : ini <= hoy ? 'En ejecución' : emision <= hoy ? 'Liberado' : 'Aprobado';
      const avance = estado === 'Cerrado' ? 100 : estado === 'En ejecución' ? Math.round(100 * dias(ini, hoy) / (sem * 7)) : 0;
      const fase = Number(codigo.slice(4, 5));
      return { proyecto_id: p.id, fase_id: idFase[fase], tipo: 'CWP', codigo, descripcion: desc, disciplina: dis, cwa_id: idCwa[codigo.replace('CWP-', 'CWA-').slice(0, 8)],
        sistema, responsable_rol: 'CON', estado, inicio_plan: ini, fin_plan: fin, inicio_real: estado === 'Cerrado' || estado === 'En ejecución' ? ini : null,
        fin_real: estado === 'Cerrado' ? min(sumarDias(fin, RETRASOS[k % RETRASOS.length]), hoy) : null, avance, hh_estimadas: hh,
        hh_reales: Math.round(hh * avance / 100 * 1.04), secuencia_poc: k + 1, duracion_semanas: sem, justificacion_poc: just };
    });
    const cwps = await q(sb.from('paquetes').insert(filasCwp).select('id, codigo, cwa_id, fase_id, inicio_plan, fin_plan, estado, hh_estimadas, disciplina'));
    const idCwp = Object.fromEntries(cwps.map(c => [c.codigo, c]));
    await Promise.all(ej.cwp.filter(c => c[6]).map(c => q(sb.from('paquetes').update({ predecesor_id: idCwp[c[6]].id }).eq('id', idCwp[c[0]].id))));
    // EWP y PWP (uno por CWP) e IWP de los CWP liberados o en ejecución
    const hijos = [];
    for (const c of cwps) {
      const suf = c.codigo.slice(4), ewpFin = sumarDias(c.inicio_plan, -91), ewpIni = sumarDias(ewpFin, -112), ras = sumarDias(c.inicio_plan, -10);
      const est = (a, b) => (b < hoy ? 'Cerrado' : a <= hoy ? 'En desarrollo' : 'Planificado');
      hijos.push({ proyecto_id: p.id, fase_id: c.fase_id, tipo: 'EWP', codigo: 'EWP-' + suf, descripcion: 'Ingeniería de ' + c.codigo, disciplina: c.disciplina, cwa_id: c.cwa_id, cwp_id: c.id,
        responsable_rol: 'ING', estado: est(ewpIni, ewpFin), inicio_plan: ewpIni, fin_plan: ewpFin, avance: ewpFin < hoy ? 100 : ewpIni <= hoy ? Math.round(100 * dias(ewpIni, hoy) / dias(ewpIni, ewpFin)) : 0,
        fin_real: ewpFin < hoy ? ewpFin : null });
      const pwpEst = ras < hoy ? 'Cerrado' : ewpFin <= hoy ? 'En ejecución' : 'Planificado';
      hijos.push({ proyecto_id: p.id, fase_id: c.fase_id, tipo: 'PWP', codigo: 'PWP-' + suf, descripcion: 'Materiales y equipos de ' + c.codigo, disciplina: c.disciplina, cwa_id: c.cwa_id, cwp_id: c.id,
        responsable_rol: 'PRO', estado: pwpEst, inicio_plan: ewpFin, fin_plan: ras, avance: pwpEst === 'Cerrado' ? 100 : pwpEst === 'En ejecución' ? Math.round(100 * dias(ewpFin, hoy) / Math.max(1, dias(ewpFin, ras))) : 0,
        fin_real: pwpEst === 'Cerrado' ? ras : null });
      if (c.estado === 'En ejecución' || c.estado === 'Liberado') {
        for (let k = 0; k < 5; k++) {
          const ii = sumarDias(c.inicio_plan, k * 7), fi = sumarDias(ii, 5);
          const e = fi < hoy ? 'Cerrado' : ii <= hoy ? 'En ejecución' : sumarDias(ii, -14) <= hoy ? 'Liberado' : 'Planificado';
          hijos.push({ proyecto_id: p.id, fase_id: c.fase_id, tipo: 'IWP', codigo: `IWP-${suf}-${String(k + 1).padStart(3, '0')}`, descripcion: `Frente ${k + 1} de ${c.codigo}`,
            disciplina: c.disciplina, cwa_id: c.cwa_id, cwp_id: c.id, responsable_rol: 'WFP', estado: e, inicio_plan: ii, fin_plan: fi,
            inicio_real: e === 'Cerrado' || e === 'En ejecución' ? ii : null, fin_real: e === 'Cerrado' ? fi : null, avance: e === 'Cerrado' ? 100 : e === 'En ejecución' ? 50 : 0,
            hh_estimadas: 320 + (k * 70) % 280, cuadrilla: `Cuadrilla ${c.disciplina}-${k + 1}`, liberacion_real: e === 'Planificado' ? null : sumarDias(ii, -14) });
        }
      }
    }
    await q(sb.from('paquetes').insert(hijos));
    // Restricciones
    if (ej.restricciones.length) {
      await q(sb.from('restricciones').insert(ej.restricciones.map(([cwp, tipo, desc, rol, dIdent, dReq, estado], k) => ({
        proyecto_id: p.id, fase_id: idCwp[cwp].fase_id, codigo: 'R-' + String(k + 1).padStart(4, '0'), cwp_id: idCwp[cwp].id, tipo, descripcion: desc,
        responsable_rol: rol, fecha_identificada: sumarDias(hoy, dIdent), fecha_requerida: sumarDias(hoy, dReq), estado,
        fecha_liberacion: estado === 'Liberada' ? min(sumarDias(hoy, dReq - 2), hoy) : null,
      }))));
    }
  }

  // Riesgos
  aviso(`${ej.codigo}: riesgos…`);
  await q(sb.from('riesgos').insert(RIESGOS.map(([codigo, alcance, etapa, cat, desc, causa, cons, mit, rol], k) => {
    const [pr, im, estado] = ej.riesgos[k];
    return { proyecto_id: p.id, codigo, alcance_fases: ej.fases.length < 3 && alcance.includes('3') ? 'Todas las fases' : alcance, etapa, categoria: cat, descripcion: desc, causa, consecuencia: cons,
      probabilidad: pr, impacto: im, mitigacion: mit, responsable_rol: rol, fecha_revision: sumarDias(hoy, 14 + 7 * k), estado,
      probabilidad_residual: Math.max(1, pr - 1), impacto_residual: Math.max(1, im - 1) };
  })));

  // Tendencia: fotos semanales hasta la semana pasada; la actual la toma registrar_instantanea
  aviso(`${ej.codigo}: tendencia semanal…`);
  // Igual que registrar_instantanea: promedio del % de cada etapa del ciclo de vida.
  const porEtapa = Object.entries(ej.actividades).map(([et, [c, e]]) => 100 * (c + 0.5 * e) / plan.filter(a => a.codigo.startsWith(et + '-')).length);
  const actual = Math.round(10 * porEtapa.reduce((a, v) => a + v, 0) / porEtapa.length) / 10;
  const semanas = Math.min(16, Math.floor(dias(p.fecha_inicio, hoy) / 7));
  const fotos = [];
  for (let w = semanas; w >= 1; w--) {
    const valor = Math.max(0, Math.round(10 * actual * (1 - w / (semanas + 2))) / 10);
    fotos.push({ proyecto_id: p.id, semana: lunes(sumarDias(hoy, -7 * w)), indicadores: { avance_awp: valor } });
  }
  if (fotos.length) await q(sb.from('instantaneas').insert(fotos));
  await registrarInstantanea(p.id);
}

// Borra un proyecto en orden (restricciones → IWP/EWP/PWP → CWP → CWA → proyecto) para respetar las claves foráneas.
export async function borrarProyecto(id) {
  await q(sb.from('restricciones').delete().eq('proyecto_id', id));
  await q(sb.from('paquetes').delete().eq('proyecto_id', id).neq('tipo', 'CWP'));
  await q(sb.from('paquetes').delete().eq('proyecto_id', id));
  await q(sb.from('cwa').delete().eq('proyecto_id', id));
  await q(sb.from('proyectos').delete().eq('id', id));
}

export async function quitarEjemplos(aviso = () => {}) {
  const lista = await proyectosEjemploExistentes();
  for (const p of lista) { aviso(`Quitando ${p.codigo}…`); await borrarProyecto(p.id); }
  return lista.length;
}
