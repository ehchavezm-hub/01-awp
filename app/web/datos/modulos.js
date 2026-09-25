// Módulos del proyecto: ícono, ayuda contextual, recursos relacionados y etapa
// de construcción en que se habilitan (ver app/DISENO.md, sección 12).
export const MODULOS = [
  {
    id: 'resumen', nombre: 'Resumen', icono: 'gauge', etapa: 2, grupo: 'Proyecto',
    ayuda: {
      que: 'El dashboard del proyecto: cuánto avanzó la implementación de AWP, qué hitos vienen y qué hacer a continuación.',
      ejemplo: 'Anillos por etapa del ciclo de vida: FEL 100 %, Ingeniería 80 %, Construcción 45 %.',
      consejo: 'Empieza cada semana por «Tu próximo paso»: resume lo más urgente según el avance del proyecto.',
    },
    recursos: ['Plan_Implementacion_AWP.docx'], presentacion: '13',
  },
  {
    id: 'fases', nombre: 'Fases', icono: 'layers', etapa: 2, grupo: 'Proyecto',
    ayuda: {
      que: 'Las fases del proyecto (Fase 1, 2, 3…) con sus fechas, estado y plazos de liberación de IWP. Todo lo que registres se vincula a una fase.',
      ejemplo: 'Fase 2 · Instalación principal · M8–M30 · IWP iniciado 12 semanas antes de su ejecución.',
      consejo: 'La Fase 1 conviene como piloto: plazos más cortos y metas de KPI más bajas; luego se escalan con lo aprendido.',
    },
    recursos: ['Plan_Implementacion_AWP.docx', 'Informe_Cierre_Fase_AWP.docx'], presentacion: '4',
  },
  {
    id: 'avance', nombre: 'Avance AWP', icono: 'list-checks', etapa: 2, grupo: 'Proyecto',
    ayuda: {
      que: 'El checklist de implementación del kit: 30 actividades AWP agrupadas por etapa del ciclo de vida. El % de avance se calcula solo.',
      ejemplo: 'FEL-04 · Desarrollar el Path of Construction en talleres de planificación interactiva.',
      consejo: 'Marca «No aplica» solo con una razón en el comentario: así el % refleja la realidad del proyecto.',
    },
    recursos: ['Plan_Implementacion_AWP.docx'], presentacion: '4',
  },
  {
    id: 'hitos', nombre: 'Hitos', icono: 'flag', etapa: 2, grupo: 'Proyecto',
    ayuda: {
      que: 'Los hitos AWP H0–H10 de cada fase, con fecha plan, fecha real y la evidencia que los respalda.',
      ejemplo: 'H7 · Primer IWP liberado: IWP sin restricciones y con checklist firmado, entregado al capataz.',
      consejo: 'Un hito se cumple cuando existe la evidencia, no cuando «casi está». Anota la evidencia al marcarlo.',
    },
    recursos: ['Plan_Implementacion_AWP.docx'], presentacion: '4',
  },
  { id: 'paquetes', nombre: 'Paquetes', icono: 'package', etapa: 3, grupo: 'Planificación', recursos: ['Seguimiento_Paquetes.xlsx', 'Definicion_CWA.xlsx', 'Plantilla_CWP.docx', 'Plantilla_EWP.docx', 'Plantilla_IWP.docx'], presentacion: '2' },
  { id: 'poc', nombre: 'Path of Construction', icono: 'route', etapa: 3, grupo: 'Planificación', recursos: ['Path_of_Construction.xlsx', 'Acta_Taller_Path_of_Construction.docx'], presentacion: '4' },
  { id: 'restricciones', nombre: 'Restricciones', icono: 'octagon-alert', etapa: 3, grupo: 'Ejecución', recursos: ['Registro_Restricciones.xlsx', 'Procedimiento_Gestion_Restricciones.docx'], presentacion: '6' },
  { id: 'liberacion', nombre: 'Liberación de IWP', icono: 'badge-check', etapa: 3, grupo: 'Ejecución', recursos: ['Programa_Liberacion_IWP.xlsx', 'Checklist_Liberacion_IWP.xlsx'], presentacion: '6' },
  { id: 'lookahead', nombre: 'Lookahead', icono: 'calendar-range', etapa: 3, grupo: 'Ejecución', recursos: ['Lookahead_3_Semanas.xlsx'], presentacion: '6' },
  { id: 'roles', nombre: 'Roles y RACI', icono: 'users', etapa: 4, grupo: 'Control', recursos: ['Matriz_Roles_RACI.xlsx', 'Perfiles_Puesto_AWP.docx'], presentacion: '9' },
  { id: 'riesgos', nombre: 'Riesgos', icono: 'shield-alert', etapa: 4, grupo: 'Control', recursos: ['Registro_Riesgos.xlsx'], presentacion: '12' },
  { id: 'lecciones', nombre: 'Lecciones', icono: 'lightbulb', etapa: 4, grupo: 'Control', recursos: ['Registro_Lecciones_Aprendidas.xlsx'], presentacion: '12' },
  { id: 'kpi', nombre: 'KPI', icono: 'gauge', etapa: 4, grupo: 'Control', recursos: ['Tablero_KPI.xlsx'], presentacion: '10' },
  { id: 'documentos', nombre: 'Documentos', icono: 'file-text', etapa: 5, grupo: 'Control', recursos: ['Procedimiento_Gestion_Restricciones.docx', 'Informe_Cierre_Fase_AWP.docx'], presentacion: null },
];

export const ETAPA_ACTUAL = 2;
export const disponible = m => m.etapa <= ETAPA_ACTUAL;
