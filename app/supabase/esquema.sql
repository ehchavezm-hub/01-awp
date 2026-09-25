-- ==========================================================================
-- ESQUEMA DE LA APLICACIÓN AWP PARA SUPABASE
-- ==========================================================================
-- Archivo generado por app/supabase/generar_esquema.py a partir de
-- estructura.sql y de los catálogos del kit de implementación. No lo edite
-- a mano: cambie estructura.sql o los datos del kit y vuelva a generarlo.
--
-- Cómo usarlo: Supabase > SQL Editor > New query > pegar todo > Run.
-- Debe ejecutarse una sola vez, en un proyecto de Supabase vacío.
-- No contiene datos de proyectos: solo estructura, seguridad y catálogos
-- públicos del kit.


-- ==========================================================================
-- ESTRUCTURA
-- ==========================================================================
-- Convenciones
--  * Todas las tablas de datos de proyecto tienen proyecto_id y, cuando
--    corresponde, fase_id. Las claves foráneas compuestas (x_id, proyecto_id)
--    impiden mezclar registros de proyectos distintos.
--  * Los valores de las listas (estados, tipos, fases…) son los mismos del
--    kit de implementación (implementacion/scripts/datos_proyecto.py).
--  * Los porcentajes se guardan de 0 a 100.
--  * Columnas de control en todas las tablas: creado_en, creado_por,
--    actualizado_en, actualizado_por (las llenan los triggers).


-- --------------------------------------------------------------------------
-- 1. Perfiles de usuario y preferencias
-- --------------------------------------------------------------------------
create table public.perfiles (
  id              uuid primary key references auth.users (id) on delete cascade,
  nombre          text,
  tour_visto      boolean not null default false,
  preferencias    jsonb not null default '{}'::jsonb,
  creado_en       timestamptz not null default now(),
  actualizado_en  timestamptz not null default now()
);
comment on table public.perfiles is 'Datos del usuario: nombre, recorrido guiado visto y preferencias (tema, filtros).';

-- --------------------------------------------------------------------------
-- 2. Catálogos del kit (comunes a todos los proyectos, solo lectura)
-- --------------------------------------------------------------------------
create table public.cat_etapas (
  codigo  text primary key,
  nombre  text not null unique,
  orden   smallint not null
);

create table public.cat_roles (
  codigo            text primary key,
  nombre            text not null unique,
  responsabilidades text,
  orden             smallint not null
);

create table public.cat_disciplinas (
  codigo  text primary key,
  nombre  text not null
);

create table public.cat_tipos_restriccion (
  nombre                text primary key,
  ejemplos              text,
  responsable_habitual  text,
  anticipacion_semanas  smallint
);

create table public.cat_causas_no_cumplimiento (
  nombre  text primary key,
  orden   smallint not null
);

create table public.cat_kpi (
  codigo   text primary key,
  nombre   text not null,
  formula  text not null,
  unidad   text not null,
  sentido  text not null check (sentido in ('≥', '≤')),
  meta_f1  numeric not null,
  meta_f2  numeric not null,
  meta_f3  numeric not null,
  tipo     text not null check (tipo in ('Proceso', 'Resultado'))
);

create table public.cat_hitos (
  codigo    text primary key,
  nombre    text not null,
  criterio  text not null,
  evidencia text,
  aprueba   text,
  orden     smallint not null
);

create table public.cat_actividades_awp (
  codigo       text primary key,
  etapa        text not null references public.cat_etapas (nombre),
  orden        smallint not null,
  nombre       text not null,
  descripcion  text,
  hito         text references public.cat_hitos (codigo),
  plantilla    text
);
comment on table public.cat_actividades_awp is 'Checklist de implementación AWP por etapa del ciclo de vida (plan de implementación, sección Etapas).';

create table public.cat_criterios_liberacion (
  numero     smallint primary key,
  categoria  text not null,
  criterio   text not null,
  rol        text not null
);

create table public.cat_criterios_cwa (
  numero       smallint primary key,
  criterio     text not null,
  descripcion  text not null
);

create table public.cat_actividades_raci (
  orden         smallint primary key,
  etapa         text not null references public.cat_etapas (nombre),
  actividad     text not null,
  fase          text not null,
  asignaciones  jsonb not null
);

-- --------------------------------------------------------------------------
-- 3. Proyectos, miembros y fases
-- --------------------------------------------------------------------------
create table public.proyectos (
  id              uuid primary key default gen_random_uuid(),
  codigo          text not null,
  nombre          text not null,
  cliente         text,
  ubicacion       text,
  tipo            text,
  descripcion     text,
  fecha_inicio    date,
  fecha_fin       date,
  responsable     text,
  estado          text not null default 'Planificado'
                  check (estado in ('Planificado', 'En ejecución', 'En pausa', 'Cerrado')),
  archivado       boolean not null default false,
  es_ejemplo      boolean not null default false,
  fecha_corte     date,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  constraint proyectos_fechas check (fecha_fin is null or fecha_inicio is null or fecha_fin >= fecha_inicio),
  constraint proyectos_codigo_no_vacio check (length(trim(codigo)) > 0)
);
comment on column public.proyectos.fecha_corte is 'Fecha de corte para calcular atrasos. Vacía = fecha de hoy. El proyecto de ejemplo usa una fecha fija.';

create table public.proyecto_miembros (
  proyecto_id  uuid not null references public.proyectos (id) on delete cascade,
  usuario_id   uuid not null references auth.users (id) on delete cascade,
  rol_acceso   text not null check (rol_acceso in ('propietario', 'editor', 'lector')),
  creado_en    timestamptz not null default now(),
  primary key (proyecto_id, usuario_id)
);
comment on table public.proyecto_miembros is 'Quién puede ver (lector) o editar (editor, propietario) cada proyecto.';

create table public.invitaciones (
  id           uuid primary key default gen_random_uuid(),
  proyecto_id  uuid not null references public.proyectos (id) on delete cascade,
  correo       text not null,
  rol_acceso   text not null check (rol_acceso in ('editor', 'lector')),
  aceptada_en  timestamptz,
  creado_en    timestamptz not null default now(),
  creado_por   uuid default auth.uid() references auth.users (id) on delete set null,
  unique (proyecto_id, correo)
);
comment on table public.invitaciones is 'Preparada para invitar a otras personas a un proyecto (uso futuro).';

create table public.fases (
  id                  uuid primary key default gen_random_uuid(),
  proyecto_id         uuid not null references public.proyectos (id) on delete cascade,
  numero              smallint not null check (numero > 0),
  nombre              text not null,
  alcance             text,
  fecha_inicio        date,
  fecha_fin           date,
  estado              text not null default 'Planificada'
                      check (estado in ('Planificada', 'En ejecución', 'Cerrada')),
  madurez_objetivo    smallint check (madurez_objetivo between 1 and 5),
  hh_estimadas        numeric check (hh_estimadas >= 0),
  pico_personal       integer check (pico_personal >= 0),
  -- Plazos de liberación de IWP (semanas antes del inicio de ejecución)
  sem_iwp_iniciado    smallint not null default 8,
  sem_identificadas   smallint not null default 6,
  sem_asignadas       smallint not null default 5,
  sem_levantadas      smallint not null default 3,
  sem_liberacion      smallint not null default 2,
  backlog_meta_sem    numeric not null default 2,
  creado_en           timestamptz not null default now(),
  creado_por          uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en      timestamptz not null default now(),
  actualizado_por     uuid references auth.users (id) on delete set null,
  unique (proyecto_id, numero),
  unique (id, proyecto_id),
  constraint fases_fechas check (fecha_fin is null or fecha_inicio is null or fecha_fin >= fecha_inicio),
  constraint fases_plazos check (sem_iwp_iniciado >= sem_identificadas and sem_identificadas >= sem_asignadas
                                 and sem_asignadas >= sem_levantadas and sem_levantadas >= sem_liberacion)
);

create table public.personas (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  nombre          text not null,
  rol_codigo      text references public.cat_roles (codigo),
  organizacion    text,
  correo          text,
  telefono        text,
  activo          boolean not null default true,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  unique (id, proyecto_id)
);
comment on table public.personas is 'Equipo del proyecto y el rol AWP de cada persona (paso «Roles» del asistente).';

-- --------------------------------------------------------------------------
-- 4. Avance de la implementación AWP e hitos
-- --------------------------------------------------------------------------
create table public.avance_actividades (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  fase_id         uuid,
  actividad       text not null references public.cat_actividades_awp (codigo),
  estado          text not null default 'Pendiente'
                  check (estado in ('Pendiente', 'En curso', 'Completada', 'No aplica')),
  responsable_rol text references public.cat_roles (codigo),
  fecha_objetivo  date,
  fecha_real      date,
  evidencia       text,
  comentario      text,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade
);
create unique index avance_actividades_unica
  on public.avance_actividades (proyecto_id, coalesce(fase_id, '00000000-0000-0000-0000-000000000000'::uuid), actividad);

create table public.hitos (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  fase_id         uuid,
  codigo          text not null,
  nombre          text not null,
  criterio        text,
  evidencia       text,
  aprueba         text,
  fecha_plan      date,
  fecha_real      date,
  estado          text not null default 'Pendiente'
                  check (estado in ('Pendiente', 'En curso', 'Cumplido', 'No aplica')),
  comentario      text,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade,
  constraint hitos_real_si_cumplido check (estado <> 'Cumplido' or fecha_real is not null)
);
create unique index hitos_unico
  on public.hitos (proyecto_id, coalesce(fase_id, '00000000-0000-0000-0000-000000000000'::uuid), codigo);

-- --------------------------------------------------------------------------
-- 5. Paquetes: CWA y CWP / EWP / PWP / IWP
-- --------------------------------------------------------------------------
create table public.cwa (
  id                uuid primary key default gen_random_uuid(),
  proyecto_id       uuid not null references public.proyectos (id) on delete cascade,
  fase_id           uuid not null,
  codigo            text not null check (codigo ~ '^CWA-[0-9]+\.[0-9]{2}$'),
  nombre            text not null,
  limites           text,
  disciplinas       text,
  hh_estimadas      numeric check (hh_estimadas >= 0),
  secuencia         smallint,
  predecesora_id    uuid,
  n_cwp_previstos   smallint check (n_cwp_previstos >= 0),
  fecha_inicio      date,
  fecha_fin         date,
  responsable_rol   text references public.cat_roles (codigo),
  estado            text not null default 'Planificado'
                    check (estado in ('Planificado', 'En desarrollo', 'En revisión', 'Aprobado', 'Liberado', 'En ejecución', 'Cerrado', 'Suspendido')),
  cumple_criterios  boolean,
  criterios         jsonb not null default '{}'::jsonb,
  observaciones     text,
  creado_en         timestamptz not null default now(),
  creado_por        uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en    timestamptz not null default now(),
  actualizado_por   uuid references auth.users (id) on delete set null,
  unique (proyecto_id, codigo),
  unique (id, proyecto_id),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete restrict,
  foreign key (predecesora_id, proyecto_id) references public.cwa (id, proyecto_id) on delete set null (predecesora_id),
  constraint cwa_fechas check (fecha_fin is null or fecha_inicio is null or fecha_fin >= fecha_inicio),
  constraint cwa_no_se_precede check (predecesora_id is null or predecesora_id <> id)
);

create table public.paquetes (
  id                    uuid primary key default gen_random_uuid(),
  proyecto_id           uuid not null references public.proyectos (id) on delete cascade,
  fase_id               uuid not null,
  tipo                  text not null check (tipo in ('CWP', 'EWP', 'PWP', 'IWP')),
  codigo                text not null,
  descripcion           text not null,
  disciplina            text references public.cat_disciplinas (codigo),
  cwa_id                uuid not null,
  cwp_id                uuid,             -- CWP padre (EWP, PWP e IWP)
  sistema               text,
  responsable_rol       text references public.cat_roles (codigo),
  responsable_persona   uuid,
  estado                text not null default 'Planificado'
                        check (estado in ('Planificado', 'En desarrollo', 'En revisión', 'Aprobado', 'Liberado', 'En ejecución', 'Cerrado', 'Suspendido')),
  inicio_plan           date,
  fin_plan              date,
  inicio_real           date,
  fin_real              date,
  avance                numeric not null default 0 check (avance between 0 and 100),
  hh_estimadas          numeric check (hh_estimadas >= 0),
  hh_reales             numeric check (hh_reales >= 0),
  -- Path of Construction (CWP)
  secuencia_poc         smallint,
  predecesor_id         uuid,
  duracion_semanas      numeric check (duracion_semanas > 0),
  justificacion_poc     text,
  -- Programa de liberación (IWP)
  cuadrilla             text,
  liberacion_real       date,
  -- Contenido de las plantillas Word (IWP, CWP, EWP) por secciones
  documento             jsonb not null default '{}'::jsonb,
  observaciones         text,
  creado_en             timestamptz not null default now(),
  creado_por            uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en        timestamptz not null default now(),
  actualizado_por       uuid references auth.users (id) on delete set null,
  unique (proyecto_id, codigo),
  unique (id, proyecto_id),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete restrict,
  foreign key (cwa_id, proyecto_id) references public.cwa (id, proyecto_id) on delete restrict,
  foreign key (cwp_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete restrict,
  foreign key (predecesor_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete set null (predecesor_id),
  foreign key (responsable_persona, proyecto_id) references public.personas (id, proyecto_id) on delete set null (responsable_persona),
  constraint paquetes_codigo_formato check (
    (tipo = 'IWP' and codigo ~ '^IWP-[0-9]+\.[0-9]{2}-[A-Z]{3}-[0-9]{2}-[0-9]{3}$') or
    (tipo <> 'IWP' and codigo ~ ('^' || tipo || '-[0-9]+\.[0-9]{2}-[A-Z]{3}-[0-9]{2}$'))),
  constraint paquetes_padre check ((tipo = 'CWP' and cwp_id is null) or (tipo <> 'CWP' and cwp_id is not null)),
  constraint paquetes_fechas_plan check (fin_plan is null or inicio_plan is null or fin_plan >= inicio_plan),
  constraint paquetes_fechas_real check (fin_real is null or inicio_real is null or fin_real >= inicio_real),
  constraint paquetes_no_se_precede check (predecesor_id is null or predecesor_id <> id)
);
create index paquetes_cwp on public.paquetes (cwp_id);
create index paquetes_cwa on public.paquetes (cwa_id);

-- --------------------------------------------------------------------------
-- 6. Restricciones, liberación de IWP y lookahead
-- --------------------------------------------------------------------------
create table public.restricciones (
  id                    uuid primary key default gen_random_uuid(),
  proyecto_id           uuid not null references public.proyectos (id) on delete cascade,
  fase_id               uuid not null,
  codigo                text not null check (codigo ~ '^R-[0-9]{4,}$'),
  cwp_id                uuid not null,
  iwp_id                uuid,
  tipo                  text not null references public.cat_tipos_restriccion (nombre),
  descripcion           text not null,
  responsable_rol       text not null references public.cat_roles (codigo),
  responsable_persona   uuid,
  responsable_nombre    text,
  fecha_identificada    date not null default current_date,
  fecha_requerida       date,
  fecha_liberacion      date,
  estado                text not null default 'Abierta'
                        check (estado in ('Abierta', 'En gestión', 'Liberada', 'Cancelada')),
  evidencia             text,
  observaciones         text,
  creado_en             timestamptz not null default now(),
  creado_por            uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en        timestamptz not null default now(),
  actualizado_por       uuid references auth.users (id) on delete set null,
  unique (proyecto_id, codigo),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete restrict,
  foreign key (cwp_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete restrict,
  foreign key (iwp_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete set null (iwp_id),
  foreign key (responsable_persona, proyecto_id) references public.personas (id, proyecto_id) on delete set null (responsable_persona),
  constraint restricciones_requerida check (fecha_requerida is null or fecha_requerida >= fecha_identificada),
  constraint restricciones_liberacion check (
    (estado = 'Liberada' and fecha_liberacion is not null and fecha_liberacion >= fecha_identificada) or
    (estado <> 'Liberada' and fecha_liberacion is null))
);
create index restricciones_iwp on public.restricciones (iwp_id);
create index restricciones_cwp on public.restricciones (cwp_id);

create table public.liberaciones_iwp (
  id                  uuid primary key default gen_random_uuid(),
  proyecto_id         uuid not null references public.proyectos (id) on delete cascade,
  iwp_id              uuid not null,
  fecha_revision      date not null default current_date,
  planificador        text,
  -- [{numero, aplica: bool, cumple: 'Sí'|'No'|'Pendiente'|'No aplica', evidencia, rol, observaciones}]
  criterios           jsonb not null default '[]'::jsonb,
  liberado_por_rol    text references public.cat_roles (codigo),
  fecha_liberacion    date,
  observaciones       text,
  creado_en           timestamptz not null default now(),
  creado_por          uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en      timestamptz not null default now(),
  actualizado_por     uuid references auth.users (id) on delete set null,
  foreign key (iwp_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete cascade,
  constraint liberaciones_fecha check (fecha_liberacion is null or fecha_liberacion >= fecha_revision)
);

create table public.lookahead (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  semana_inicio   date not null check (extract(isodow from semana_inicio) = 1),
  notas           text,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  unique (proyecto_id, semana_inicio),
  unique (id, proyecto_id)
);
comment on column public.lookahead.semana_inicio is 'Lunes de la semana 1 del lookahead.';

create table public.lookahead_items (
  id                  uuid primary key default gen_random_uuid(),
  proyecto_id         uuid not null references public.proyectos (id) on delete cascade,
  lookahead_id        uuid not null,
  iwp_id              uuid not null,
  responsables        text,
  personas_cuadrilla  smallint check (personas_cuadrilla >= 0),
  hh                  numeric check (hh >= 0),
  recursos_criticos   text,
  -- 18 caracteres (3 semanas × lunes a sábado): 'X' = día programado, '-' = libre
  dias                text not null default '------------------' check (dias ~ '^[X-]{18}$'),
  completado_s1       boolean,
  causa               text references public.cat_causas_no_cumplimiento (nombre),
  creado_en           timestamptz not null default now(),
  creado_por          uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en      timestamptz not null default now(),
  actualizado_por     uuid references auth.users (id) on delete set null,
  unique (lookahead_id, iwp_id),
  foreign key (lookahead_id, proyecto_id) references public.lookahead (id, proyecto_id) on delete cascade,
  foreign key (iwp_id, proyecto_id) references public.paquetes (id, proyecto_id) on delete cascade,
  constraint lookahead_causa check (completado_s1 is distinct from false or causa is not null)
);

-- --------------------------------------------------------------------------
-- 7. Roles (RACI), riesgos, lecciones y KPI
-- --------------------------------------------------------------------------
create table public.raci (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  orden           smallint not null,
  etapa           text not null references public.cat_etapas (nombre),
  actividad       text not null,
  fase            text not null default 'Todas las fases'
                  check (fase in ('Fase 1', 'Fase 2', 'Fase 3', 'Fases 1 y 2', 'Fases 2 y 3', 'Todas las fases')),
  -- {"CLI": "A", "GP": "R", ...} con valores R, A, C o I
  asignaciones    jsonb not null default '{}'::jsonb,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null
);

create table public.riesgos (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  codigo          text not null,
  alcance_fases   text not null default 'Todas las fases'
                  check (alcance_fases in ('Fase 1', 'Fase 2', 'Fase 3', 'Fases 1 y 2', 'Fases 2 y 3', 'Todas las fases')),
  fase_id         uuid,
  etapa           text references public.cat_etapas (nombre),
  categoria       text check (categoria in ('Organización y liderazgo', 'Personas y competencias', 'Procesos', 'Contratos',
                                            'Herramientas e información', 'Interfaces entre fases', 'Medición')),
  descripcion     text not null,
  causa           text,
  consecuencia    text,
  probabilidad    smallint not null check (probabilidad between 1 and 5),
  impacto         smallint not null check (impacto between 1 and 5),
  mitigacion      text,
  responsable_rol text references public.cat_roles (codigo),
  fecha_revision  date,
  estado          text not null default 'Abierto'
                  check (estado in ('Abierto', 'En tratamiento', 'Cerrado', 'Materializado')),
  probabilidad_residual smallint check (probabilidad_residual between 1 and 5),
  impacto_residual      smallint check (impacto_residual between 1 and 5),
  observaciones   text,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  unique (proyecto_id, codigo),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete set null (fase_id)
);

create table public.lecciones (
  id                  uuid primary key default gen_random_uuid(),
  proyecto_id         uuid not null references public.proyectos (id) on delete cascade,
  codigo              text not null,
  fase_origen_id      uuid,
  fase_aplicacion_id  uuid,
  etapa               text references public.cat_etapas (nombre),
  categoria           text check (categoria in ('Definición de paquetes', 'Path of Construction', 'Restricciones', 'Materiales',
                                                'Ingeniería', 'Herramientas e información', 'Organización y roles', 'HSE',
                                                'Calidad', 'Comisionamiento', 'Interfaces entre fases')),
  tipo                text check (tipo in ('Positiva', 'Negativa')),
  evento              text not null,
  causa_raiz          text,
  impacto             text check (impacto in ('Alto', 'Medio', 'Bajo')),
  leccion             text not null,
  accion              text,
  documento_afectado  text,
  responsable_rol     text references public.cat_roles (codigo),
  fecha_compromiso    date,
  estado              text not null default 'Registrada'
                      check (estado in ('Registrada', 'En análisis', 'Aprobada', 'Implementada', 'Verificada', 'Descartada')),
  verificacion        text,
  creado_en           timestamptz not null default now(),
  creado_por          uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en      timestamptz not null default now(),
  actualizado_por     uuid references auth.users (id) on delete set null,
  unique (proyecto_id, codigo),
  foreign key (fase_origen_id, proyecto_id) references public.fases (id, proyecto_id) on delete set null (fase_origen_id),
  foreign key (fase_aplicacion_id, proyecto_id) references public.fases (id, proyecto_id) on delete set null (fase_aplicacion_id)
);

create table public.kpi_semanal (
  id                  uuid primary key default gen_random_uuid(),
  proyecto_id         uuid not null references public.proyectos (id) on delete cascade,
  fase_id             uuid not null,
  semana              date not null check (extract(isodow from semana) = 1),
  iwp_planificados    numeric check (iwp_planificados >= 0),
  iwp_completados     numeric check (iwp_completados >= 0),
  iwp_liberados       numeric check (iwp_liberados >= 0),
  iwp_sin_restr       numeric check (iwp_sin_restr >= 0),
  iwp_mat_100         numeric check (iwp_mat_100 >= 0),
  iwp_entregados      numeric check (iwp_entregados >= 0),
  iwp_devueltos       numeric check (iwp_devueltos >= 0),
  hh_backlog          numeric check (hh_backlog >= 0),
  hh_ejecutadas       numeric check (hh_ejecutadas >= 0),
  restr_liberadas     numeric check (restr_liberadas >= 0),
  restr_a_tiempo      numeric check (restr_a_tiempo >= 0),
  restr_vencidas      numeric check (restr_vencidas >= 0),
  restr_dias_atraso   numeric check (restr_dias_atraso >= 0),
  ewp_vencidos        numeric check (ewp_vencidos >= 0),
  ewp_a_tiempo        numeric check (ewp_a_tiempo >= 0),
  hh_ganadas          numeric check (hh_ganadas >= 0),
  hh_gastadas         numeric check (hh_gastadas >= 0),
  hh_retrabajo        numeric check (hh_retrabajo >= 0),
  trabajadores        numeric check (trabajadores >= 0),
  planificadores      numeric check (planificadores >= 0),
  tool_time           numeric check (tool_time between 0 and 100),
  valor_ganado        numeric check (valor_ganado >= 0),
  valor_planificado   numeric check (valor_planificado >= 0),
  creado_en           timestamptz not null default now(),
  creado_por          uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en      timestamptz not null default now(),
  actualizado_por     uuid references auth.users (id) on delete set null,
  unique (proyecto_id, fase_id, semana),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade,
  constraint kpi_coherencia check (
    (iwp_completados is null or iwp_planificados is null or iwp_completados <= iwp_planificados) and
    (iwp_sin_restr is null or iwp_liberados is null or iwp_sin_restr <= iwp_liberados) and
    (iwp_mat_100 is null or iwp_liberados is null or iwp_mat_100 <= iwp_liberados) and
    (iwp_devueltos is null or iwp_entregados is null or iwp_devueltos <= iwp_entregados) and
    (restr_a_tiempo is null or restr_liberadas is null or restr_a_tiempo <= restr_liberadas) and
    (ewp_a_tiempo is null or ewp_vencidos is null or ewp_a_tiempo <= ewp_vencidos))
);

create table public.kpi_metas (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  fase_id         uuid not null,
  kpi             text not null references public.cat_kpi (codigo),
  meta            numeric not null,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  unique (fase_id, kpi),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade
);
comment on table public.kpi_metas is 'Metas propias de una fase. Si no hay fila, se usa la meta del catálogo (cat_kpi).';

-- --------------------------------------------------------------------------
-- 8. Documentos basados en plantillas Word
-- --------------------------------------------------------------------------
create table public.documentos (
  id              uuid primary key default gen_random_uuid(),
  proyecto_id     uuid not null references public.proyectos (id) on delete cascade,
  fase_id         uuid,
  tipo            text not null check (tipo in ('ACTA_POC', 'INFORME_CIERRE', 'PROCEDIMIENTO_RESTRICCIONES', 'PERFILES_PUESTO')),
  titulo          text not null,
  revision        text not null default '0',
  estado          text not null default 'Borrador' check (estado in ('Borrador', 'En revisión', 'Aprobado')),
  contenido       jsonb not null default '{}'::jsonb,
  aprobado_por    text,
  fecha_aprobacion date,
  creado_en       timestamptz not null default now(),
  creado_por      uuid default auth.uid() references auth.users (id) on delete set null,
  actualizado_en  timestamptz not null default now(),
  actualizado_por uuid references auth.users (id) on delete set null,
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete set null (fase_id)
);
comment on table public.documentos is 'Acta del taller de PoC, informe de cierre de fase, procedimiento de restricciones y perfiles de puesto. IWP, CWP y EWP guardan su documento en paquetes.documento.';

-- --------------------------------------------------------------------------
-- 9. Progreso, borradores, historial y auditoría
-- --------------------------------------------------------------------------
create table public.insignias (
  id           uuid primary key default gen_random_uuid(),
  proyecto_id  uuid not null references public.proyectos (id) on delete cascade,
  fase_id      uuid,
  codigo       text not null,
  obtenida_en  timestamptz not null default now(),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade
);
create unique index insignias_unica
  on public.insignias (proyecto_id, coalesce(fase_id, '00000000-0000-0000-0000-000000000000'::uuid), codigo);

create table public.borradores (
  usuario_id      uuid not null default auth.uid() references auth.users (id) on delete cascade,
  clave           text not null,
  proyecto_id     uuid references public.proyectos (id) on delete cascade,
  contenido       jsonb not null,
  actualizado_en  timestamptz not null default now(),
  primary key (usuario_id, clave)
);
comment on table public.borradores is 'Borradores de formularios largos, para continuarlos desde otro dispositivo.';

create table public.historial (
  id               bigint generated always as identity primary key,
  proyecto_id      uuid not null references public.proyectos (id) on delete cascade,
  fase_id          uuid,
  tabla            text not null,
  registro_id      uuid not null,
  codigo           text,
  campo            text not null,
  valor_anterior   text,
  valor_nuevo      text,
  fecha            timestamptz not null default now(),
  usuario_id       uuid references auth.users (id) on delete set null
);
create index historial_proyecto_fecha on public.historial (proyecto_id, fecha);
comment on table public.historial is 'Cambios de estado y de avance (se llena solo). Sirve para las tendencias de los dashboards.';

create table public.instantaneas (
  id            bigint generated always as identity primary key,
  proyecto_id   uuid not null references public.proyectos (id) on delete cascade,
  fase_id       uuid,
  semana        date not null check (extract(isodow from semana) = 1),
  indicadores   jsonb not null,
  tomada_en     timestamptz not null default now(),
  foreign key (fase_id, proyecto_id) references public.fases (id, proyecto_id) on delete cascade
);
create unique index instantaneas_semana
  on public.instantaneas (proyecto_id, coalesce(fase_id, '00000000-0000-0000-0000-000000000000'::uuid), semana);
comment on table public.instantaneas is 'Fotografía semanal de los indicadores de cada proyecto y fase (tendencias).';

create table public.auditoria (
  id           bigint generated always as identity primary key,
  proyecto_id  uuid,
  tabla        text not null,
  registro_id  text,
  accion       text not null check (accion in ('INSERT', 'UPDATE', 'DELETE')),
  cambios      jsonb,
  fecha        timestamptz not null default now(),
  usuario_id   uuid
);
create index auditoria_proyecto_fecha on public.auditoria (proyecto_id, fecha);
comment on table public.auditoria is 'Quién cambió qué y cuándo, en todas las tablas de proyecto (se llena sola).';

-- ==========================================================================
-- FUNCIONES DE PERMISOS
-- ==========================================================================
-- security definer: consultan proyecto_miembros sin quedar bloqueadas por su
-- propia política (evita recursión). No exponen datos: solo devuelven sí/no.

create or replace function public.es_miembro(p_proyecto uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.proyecto_miembros m
                 where m.proyecto_id = p_proyecto and m.usuario_id = auth.uid());
$$;

create or replace function public.puede_editar(p_proyecto uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.proyecto_miembros m
                 where m.proyecto_id = p_proyecto and m.usuario_id = auth.uid()
                   and m.rol_acceso in ('propietario', 'editor'));
$$;

create or replace function public.es_propietario(p_proyecto uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.proyecto_miembros m
                 where m.proyecto_id = p_proyecto and m.usuario_id = auth.uid()
                   and m.rol_acceso = 'propietario');
$$;

-- ==========================================================================
-- TRIGGERS
-- ==========================================================================

-- Quién y cuándo creó o modificó cada registro (no se puede falsificar desde la app).
create or replace function public.fn_control_cambios()
returns trigger language plpgsql set search_path = public as $$
begin
  if tg_op = 'INSERT' then
    new.creado_en := now();
    new.creado_por := auth.uid();
    new.actualizado_en := now();
    new.actualizado_por := auth.uid();
  else
    new.creado_en := old.creado_en;
    new.creado_por := old.creado_por;
    new.actualizado_en := now();
    new.actualizado_por := auth.uid();
  end if;
  return new;
end;
$$;

-- El creador de un proyecto queda como propietario.
create or replace function public.fn_proyecto_propietario()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is not null then
    insert into public.proyecto_miembros (proyecto_id, usuario_id, rol_acceso)
    values (new.id, auth.uid(), 'propietario')
    on conflict do nothing;
  end if;
  return new;
end;
$$;

-- Auditoría: guarda el registro (alta/baja) o solo los campos cambiados.
create or replace function public.fn_auditoria()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  v_nuevo jsonb := case when tg_op <> 'DELETE' then to_jsonb(new) end;
  v_viejo jsonb := case when tg_op <> 'INSERT' then to_jsonb(old) end;
  v_cambios jsonb;
  v_proyecto uuid;
begin
  if tg_op = 'UPDATE' then
    select jsonb_object_agg(k, jsonb_build_object('antes', v_viejo -> k, 'despues', v_nuevo -> k))
      into v_cambios
      from jsonb_object_keys(v_nuevo) k
     where k not in ('actualizado_en', 'actualizado_por')
       and (v_viejo -> k) is distinct from (v_nuevo -> k);
    if v_cambios is null then
      return new;
    end if;
  else
    v_cambios := coalesce(v_nuevo, v_viejo);
  end if;
  v_proyecto := coalesce(v_nuevo ->> 'proyecto_id', v_viejo ->> 'proyecto_id',
                         case when tg_table_name = 'proyectos' then coalesce(v_nuevo ->> 'id', v_viejo ->> 'id') end)::uuid;
  -- Al borrar un proyecto completo no se audita cada fila hija.
  if tg_op = 'DELETE' and tg_table_name <> 'proyectos'
     and not exists (select 1 from public.proyectos where id = v_proyecto) then
    return old;
  end if;
  insert into public.auditoria (proyecto_id, tabla, registro_id, accion, cambios, usuario_id)
  values (case when tg_op = 'DELETE' and tg_table_name = 'proyectos' then null else v_proyecto end,
          tg_table_name, coalesce(v_nuevo ->> 'id', v_viejo ->> 'id'), tg_op, v_cambios, auth.uid());
  return coalesce(new, old);
end;
$$;

-- Historial de estado y avance: los campos a seguir se pasan como argumentos.
create or replace function public.fn_historial()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  v_campo text;
  v_nuevo jsonb := to_jsonb(new);
  v_viejo jsonb := case when tg_op = 'UPDATE' then to_jsonb(old) end;
begin
  foreach v_campo in array tg_argv loop
    if tg_op = 'INSERT' or (v_viejo ->> v_campo) is distinct from (v_nuevo ->> v_campo) then
      insert into public.historial (proyecto_id, fase_id, tabla, registro_id, codigo, campo,
                                    valor_anterior, valor_nuevo, usuario_id)
      values (coalesce((v_nuevo ->> 'proyecto_id')::uuid, (v_nuevo ->> 'id')::uuid),
              nullif(v_nuevo ->> 'fase_id', '')::uuid,
              tg_table_name, (v_nuevo ->> 'id')::uuid, v_nuevo ->> 'codigo', v_campo,
              v_viejo ->> v_campo, v_nuevo ->> v_campo, auth.uid());
    end if;
  end loop;
  return new;
end;
$$;

-- Reglas de la jerarquía de paquetes que no caben en un CHECK.
create or replace function public.fn_validar_paquete()
returns trigger language plpgsql set search_path = public as $$
declare
  v_padre record;
  v_cwa record;
begin
  select codigo, fase_id into v_cwa from public.cwa where id = new.cwa_id;
  if new.fase_id <> v_cwa.fase_id then
    raise exception 'El paquete % debe estar en la misma fase que su CWA %.', new.codigo, v_cwa.codigo
      using hint = 'Elija la CWA de la fase correcta o cambie la fase del paquete.';
  end if;
  if substr(new.codigo, 5, 4) <> substr(v_cwa.codigo, 5, 4) then
    raise exception 'El código % no corresponde a la CWA %.', new.codigo, v_cwa.codigo
      using hint = 'Los dígitos después del tipo deben coincidir con la CWA (por ejemplo, CWP-2.01-… para CWA-2.01).';
  end if;
  if new.cwp_id is not null then
    select tipo, codigo, cwa_id into v_padre from public.paquetes where id = new.cwp_id;
    if v_padre.tipo <> 'CWP' then
      raise exception 'El paquete padre de % debe ser un CWP.', new.codigo;
    end if;
    if v_padre.cwa_id <> new.cwa_id then
      raise exception '% debe pertenecer a la misma CWA que su CWP %.', new.codigo, v_padre.codigo;
    end if;
    if substr(new.codigo, 5, 11) <> substr(v_padre.codigo, 5, 11) then
      raise exception 'El código % no corresponde a su CWP %.', new.codigo, v_padre.codigo
        using hint = 'EWP, PWP e IWP usan el mismo sufijo que su CWP (por ejemplo, EWP-2.01-EST-01 para CWP-2.01-EST-01).';
    end if;
  end if;
  return new;
end;
$$;

-- Una restricción se asocia a un IWP de su mismo CWP.
create or replace function public.fn_validar_restriccion()
returns trigger language plpgsql set search_path = public as $$
declare
  v_iwp record;
  v_cwp record;
begin
  select tipo, fase_id into v_cwp from public.paquetes where id = new.cwp_id;
  if v_cwp.tipo <> 'CWP' then
    raise exception 'La restricción % debe asociarse a un CWP.', new.codigo;
  end if;
  new.fase_id := v_cwp.fase_id;
  if new.iwp_id is not null then
    select tipo, cwp_id into v_iwp from public.paquetes where id = new.iwp_id;
    if v_iwp.tipo <> 'IWP' or v_iwp.cwp_id <> new.cwp_id then
      raise exception 'El IWP de la restricción % debe pertenecer al CWP elegido.', new.codigo;
    end if;
  end if;
  return new;
end;
$$;

create trigger proyectos_propietario after insert on public.proyectos
  for each row execute function public.fn_proyecto_propietario();
create trigger paquetes_validar before insert or update on public.paquetes
  for each row execute function public.fn_validar_paquete();
create trigger restricciones_validar before insert or update on public.restricciones
  for each row execute function public.fn_validar_restriccion();

-- Control de cambios y auditoría en todas las tablas de proyecto.
do $$
declare
  t text;
begin
  foreach t in array array['proyectos', 'fases', 'personas', 'avance_actividades', 'hitos', 'cwa', 'paquetes',
                           'restricciones', 'liberaciones_iwp', 'lookahead', 'lookahead_items', 'raci', 'riesgos',
                           'lecciones', 'kpi_semanal', 'kpi_metas', 'documentos'] loop
    execute format('create trigger %I before insert or update on public.%I
                    for each row execute function public.fn_control_cambios()', t || '_control', t);
    execute format('create trigger %I after insert or update or delete on public.%I
                    for each row execute function public.fn_auditoria()', t || '_auditoria', t);
  end loop;
end;
$$;

-- Historial de estado y avance.
create trigger proyectos_historial after insert or update on public.proyectos
  for each row execute function public.fn_historial('estado');
create trigger fases_historial after insert or update on public.fases
  for each row execute function public.fn_historial('estado');
create trigger avance_historial after insert or update on public.avance_actividades
  for each row execute function public.fn_historial('estado');
create trigger hitos_historial after insert or update on public.hitos
  for each row execute function public.fn_historial('estado', 'fecha_plan', 'fecha_real');
create trigger cwa_historial after insert or update on public.cwa
  for each row execute function public.fn_historial('estado');
create trigger paquetes_historial after insert or update on public.paquetes
  for each row execute function public.fn_historial('estado', 'avance');
create trigger restricciones_historial after insert or update on public.restricciones
  for each row execute function public.fn_historial('estado');
create trigger riesgos_historial after insert or update on public.riesgos
  for each row execute function public.fn_historial('estado', 'probabilidad', 'impacto');
create trigger lecciones_historial after insert or update on public.lecciones
  for each row execute function public.fn_historial('estado');

-- ==========================================================================
-- VISTAS CON CAMPOS CALCULADOS (mismas fórmulas que las plantillas Excel)
-- ==========================================================================
-- security_invoker: la vista respeta el RLS de quien consulta.

create or replace function public.fecha_corte(p_proyecto uuid)
returns date language sql stable set search_path = public as $$
  select coalesce((select fecha_corte from public.proyectos where id = p_proyecto), current_date);
$$;

create view public.v_restricciones with (security_invoker = true) as
select r.*,
       case when r.fecha_requerida is null then null
            when r.estado = 'Cancelada' then 0
            when r.estado = 'Liberada' then greatest(0, r.fecha_liberacion - r.fecha_requerida)
            else greatest(0, public.fecha_corte(r.proyecto_id) - r.fecha_requerida) end as dias_atraso,
       case when r.estado = 'Cancelada' then 'Cancelada'
            when r.estado = 'Liberada' then
              case when r.fecha_requerida is not null and r.fecha_liberacion > r.fecha_requerida
                   then 'Liberada con atraso' else 'Liberada a tiempo' end
            when r.fecha_requerida is null then 'Sin fecha requerida'
            when public.fecha_corte(r.proyecto_id) > r.fecha_requerida then 'Vencida'
            when r.fecha_requerida - public.fecha_corte(r.proyecto_id) <= 7 then 'Por vencer'
            else 'En plazo' end as situacion
  from public.restricciones r;

create view public.v_paquetes with (security_invoker = true) as
with abiertas as (
  select cwp_id, iwp_id, count(*) as n
    from public.restricciones
   where estado in ('Abierta', 'En gestión')
   group by cwp_id, iwp_id
), base as (
  select p.*,
         public.fecha_corte(p.proyecto_id) as corte,
         case when p.tipo = 'IWP' then (select coalesce(sum(n), 0) from abiertas a where a.iwp_id = p.id)
              when p.tipo = 'CWP' then (select coalesce(sum(n), 0) from abiertas a where a.cwp_id = p.id)
              else (select coalesce(sum(n), 0) from abiertas a where a.cwp_id = p.cwp_id) end as restricciones_abiertas
    from public.paquetes p
)
select b.*,
       case when b.fin_plan is null then null
            when b.fin_real is not null then greatest(0, b.fin_real - b.fin_plan)
            when b.corte > b.fin_plan and b.estado <> 'Cerrado' then b.corte - b.fin_plan
            else 0 end as dias_atraso,
       case when b.estado = 'Cerrado' then
              case when b.fin_real is not null and b.fin_plan is not null and b.fin_real > b.fin_plan
                   then 'Cerrado con atraso' else 'Cerrado' end
            when b.fin_plan is not null and b.corte > b.fin_plan then 'Atrasado'
            when b.inicio_real is null and b.inicio_plan is not null and b.corte > b.inicio_plan then 'Inicio atrasado'
            else 'En plazo' end as situacion
  from base b;

create view public.v_iwp_liberacion with (security_invoker = true) as
select p.id, p.proyecto_id, p.fase_id, p.codigo, p.cwp_id, p.descripcion, p.cuadrilla, p.hh_estimadas,
       p.estado, p.inicio_plan, p.liberacion_real,
       p.inicio_plan - 7 * f.sem_iwp_iniciado  as f_iwp_iniciado,
       p.inicio_plan - 7 * f.sem_identificadas as f_identificadas,
       p.inicio_plan - 7 * f.sem_asignadas     as f_asignadas,
       p.inicio_plan - 7 * f.sem_levantadas    as f_levantadas,
       p.inicio_plan - 7 * f.sem_liberacion    as f_liberacion_objetivo,
       case when p.inicio_plan is null then null
            when p.liberacion_real is not null then greatest(0, p.liberacion_real - (p.inicio_plan - 7 * f.sem_liberacion))
            else greatest(0, public.fecha_corte(p.proyecto_id) - (p.inicio_plan - 7 * f.sem_liberacion)) end as dias_atraso_liberacion,
       case when p.inicio_plan is null then null
            when p.liberacion_real is not null then
              case when p.liberacion_real > p.inicio_plan - 7 * f.sem_liberacion
                   then 'Liberado con atraso' else 'Liberado a tiempo' end
            when public.fecha_corte(p.proyecto_id) > p.inicio_plan - 7 * f.sem_liberacion then 'Vencido sin liberar'
            when (p.inicio_plan - 7 * f.sem_liberacion) - public.fecha_corte(p.proyecto_id) <= 14 then 'Próximo a liberar'
            else 'En plazo' end as situacion
  from public.paquetes p
  join public.fases f on f.id = p.fase_id
 where p.tipo = 'IWP';

create view public.v_riesgos with (security_invoker = true) as
select r.*,
       r.probabilidad * r.impacto as nivel,
       case when r.probabilidad * r.impacto >= 12 then 'Alto'
            when r.probabilidad * r.impacto >= 6 then 'Medio' else 'Bajo' end as clasificacion,
       r.probabilidad_residual * r.impacto_residual as nivel_residual,
       case when r.probabilidad_residual is null or r.impacto_residual is null then null
            when r.probabilidad_residual * r.impacto_residual >= 12 then 'Alto'
            when r.probabilidad_residual * r.impacto_residual >= 6 then 'Medio' else 'Bajo' end as clasificacion_residual
  from public.riesgos r;

create view public.v_lecciones with (security_invoker = true) as
select l.*,
       case when l.estado in ('Implementada', 'Verificada', 'Descartada') or l.fecha_compromiso is null then null
            else l.fecha_compromiso - public.fecha_corte(l.proyecto_id) end as dias_para_vencer,
       case when l.estado in ('Implementada', 'Verificada', 'Descartada') then 'Cerrada'
            when l.fecha_compromiso is null then 'Sin fecha'
            when l.fecha_compromiso < public.fecha_corte(l.proyecto_id) then 'Vencida'
            when l.fecha_compromiso - public.fecha_corte(l.proyecto_id) <= 15 then 'Por vencer'
            else 'En plazo' end as situacion
  from public.lecciones l;

create view public.v_raci with (security_invoker = true) as
select r.*,
       (select count(*) from jsonb_each_text(r.asignaciones) e where e.value = 'A') as n_a,
       (select count(*) from jsonb_each_text(r.asignaciones) e where e.value = 'R') as n_r,
       case when (select count(*) from jsonb_each_text(r.asignaciones) e where e.value = 'A') <> 1
            then 'Revisar: debe haber una sola A'
            when (select count(*) from jsonb_each_text(r.asignaciones) e where e.value = 'R') = 0
            then 'OK (A ejecuta)' else 'OK' end as verificacion
  from public.raci r;

-- % de avance de la implementación AWP por etapa (las actividades «No aplica» no cuentan).
create view public.v_avance_etapas with (security_invoker = true) as
select a.proyecto_id, a.fase_id, c.etapa, e.orden,
       count(*) filter (where a.estado <> 'No aplica') as actividades,
       count(*) filter (where a.estado = 'Completada') as completadas,
       count(*) filter (where a.estado = 'En curso') as en_curso,
       round(100.0 * (count(*) filter (where a.estado = 'Completada')
                      + 0.5 * count(*) filter (where a.estado = 'En curso'))
             / nullif(count(*) filter (where a.estado <> 'No aplica'), 0), 1) as porcentaje
  from public.avance_actividades a
  join public.cat_actividades_awp c on c.codigo = a.actividad
  join public.cat_etapas e on e.nombre = c.etapa
 group by a.proyecto_id, a.fase_id, c.etapa, e.orden;

-- ==========================================================================
-- FOTOGRAFÍA SEMANAL DE INDICADORES
-- ==========================================================================
-- La aplicación la llama al abrir un proyecto (una vez por semana basta; si se
-- repite, actualiza la de la semana). Respeta el RLS de quien la llama.
create or replace function public.registrar_instantanea(p_proyecto uuid)
returns void language plpgsql security invoker set search_path = public as $$
declare
  v_semana date := date_trunc('week', current_date)::date;
  v_fase record;
  v_ind jsonb;
begin
  if not public.puede_editar(p_proyecto) then
    raise exception 'No tiene permiso para actualizar este proyecto.';
  end if;
  for v_fase in select null::uuid as id union all select id from public.fases where proyecto_id = p_proyecto loop
    select jsonb_build_object(
      'avance_awp', (select round(avg(porcentaje), 1) from public.v_avance_etapas
                      where proyecto_id = p_proyecto and (v_fase.id is null or fase_id = v_fase.id)),
      'restricciones_abiertas', (select count(*) from public.restricciones where proyecto_id = p_proyecto
                                   and (v_fase.id is null or fase_id = v_fase.id) and estado in ('Abierta', 'En gestión')),
      'restricciones_vencidas', (select count(*) from public.v_restricciones where proyecto_id = p_proyecto
                                   and (v_fase.id is null or fase_id = v_fase.id) and situacion = 'Vencida'),
      'restricciones_liberadas', (select count(*) from public.restricciones where proyecto_id = p_proyecto
                                   and (v_fase.id is null or fase_id = v_fase.id) and estado = 'Liberada'),
      'paquetes', (select coalesce(jsonb_object_agg(tipo, n), '{}') from (
                     select tipo, count(*) n from public.paquetes where proyecto_id = p_proyecto
                        and (v_fase.id is null or fase_id = v_fase.id) group by tipo) x),
      'paquetes_atrasados', (select count(*) from public.v_paquetes where proyecto_id = p_proyecto
                               and (v_fase.id is null or fase_id = v_fase.id) and situacion in ('Atrasado', 'Inicio atrasado')),
      'iwp_liberados', (select count(*) from public.paquetes where proyecto_id = p_proyecto and tipo = 'IWP'
                          and (v_fase.id is null or fase_id = v_fase.id) and estado = 'Liberado'),
      'hh_backlog', (select coalesce(sum(hh_estimadas), 0) from public.paquetes where proyecto_id = p_proyecto
                       and tipo = 'IWP' and (v_fase.id is null or fase_id = v_fase.id) and estado = 'Liberado'),
      'riesgos_altos', (select count(*) from public.v_riesgos where proyecto_id = p_proyecto
                          and (v_fase.id is null or fase_id = v_fase.id or fase_id is null)
                          and clasificacion = 'Alto' and estado not in ('Cerrado')),
      'hitos_atrasados', (select count(*) from public.hitos where proyecto_id = p_proyecto
                            and (v_fase.id is null or fase_id = v_fase.id) and estado not in ('Cumplido', 'No aplica')
                            and fecha_plan < public.fecha_corte(p_proyecto)),
      'lecciones_abiertas', (select count(*) from public.lecciones where proyecto_id = p_proyecto
                               and (v_fase.id is null or fase_origen_id = v_fase.id)
                               and estado not in ('Implementada', 'Verificada', 'Descartada'))
    ) into v_ind;
    insert into public.instantaneas (proyecto_id, fase_id, semana, indicadores)
    values (p_proyecto, v_fase.id, v_semana, v_ind)
    on conflict (proyecto_id, coalesce(fase_id, '00000000-0000-0000-0000-000000000000'::uuid), semana)
    do update set indicadores = excluded.indicadores, tomada_en = now();
  end loop;
end;
$$;

-- Aceptar una invitación (uso futuro): la persona invitada inicia sesión con
-- el correo invitado y queda como miembro del proyecto.
create or replace function public.aceptar_invitaciones()
returns integer language plpgsql security definer set search_path = public as $$
declare
  v_n integer;
begin
  with pendientes as (
    update public.invitaciones i set aceptada_en = now()
     where lower(i.correo) = lower(auth.jwt() ->> 'email') and i.aceptada_en is null
     returning i.proyecto_id, i.rol_acceso
  )
  insert into public.proyecto_miembros (proyecto_id, usuario_id, rol_acceso)
  select proyecto_id, auth.uid(), rol_acceso from pendientes
  on conflict (proyecto_id, usuario_id) do nothing;
  get diagnostics v_n = row_count;
  return v_n;
end;
$$;

-- ==========================================================================
-- ROW LEVEL SECURITY
-- ==========================================================================
-- Regla general: solo usuarios autenticados. Cada uno ve los proyectos de los
-- que es miembro; editores y propietarios los modifican; solo el propietario
-- borra proyectos y gestiona miembros e invitaciones.

do $$
declare
  t text;
begin
  -- Tablas con proyecto_id: leer = miembro; escribir = editor o propietario.
  foreach t in array array['fases', 'personas', 'avance_actividades', 'hitos', 'cwa', 'paquetes', 'restricciones',
                           'liberaciones_iwp', 'lookahead', 'lookahead_items', 'raci', 'riesgos', 'lecciones',
                           'kpi_semanal', 'kpi_metas', 'documentos', 'insignias'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select to authenticated using (public.es_miembro(proyecto_id))',
                   t || '_leer', t);
    execute format('create policy %I on public.%I for insert to authenticated with check (public.puede_editar(proyecto_id))',
                   t || '_crear', t);
    execute format('create policy %I on public.%I for update to authenticated using (public.puede_editar(proyecto_id)) with check (public.puede_editar(proyecto_id))',
                   t || '_editar', t);
    execute format('create policy %I on public.%I for delete to authenticated using (public.puede_editar(proyecto_id))',
                   t || '_borrar', t);
  end loop;

  -- Catálogos: lectura para usuarios autenticados; nadie los modifica desde la app.
  foreach t in array array['cat_etapas', 'cat_roles', 'cat_disciplinas', 'cat_tipos_restriccion',
                           'cat_causas_no_cumplimiento', 'cat_kpi', 'cat_hitos', 'cat_actividades_awp',
                           'cat_criterios_liberacion', 'cat_criterios_cwa', 'cat_actividades_raci'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy %I on public.%I for select to authenticated using (true)', t || '_leer', t);
  end loop;
end;
$$;

alter table public.proyectos enable row level security;
-- El creador también puede leerlo: así la app recibe el proyecto recién creado
-- (la membresía de propietario la agrega un trigger justo después).
create policy proyectos_leer on public.proyectos for select to authenticated
  using (public.es_miembro(id) or creado_por = auth.uid());
create policy proyectos_crear on public.proyectos for insert to authenticated
  with check (auth.uid() is not null);
create policy proyectos_editar on public.proyectos for update to authenticated
  using (public.puede_editar(id)) with check (public.puede_editar(id));
create policy proyectos_borrar on public.proyectos for delete to authenticated
  using (public.es_propietario(id));

alter table public.proyecto_miembros enable row level security;
create policy miembros_leer on public.proyecto_miembros for select to authenticated
  using (public.es_miembro(proyecto_id));
create policy miembros_crear on public.proyecto_miembros for insert to authenticated
  with check (public.es_propietario(proyecto_id));
create policy miembros_editar on public.proyecto_miembros for update to authenticated
  using (public.es_propietario(proyecto_id)) with check (public.es_propietario(proyecto_id));
create policy miembros_borrar on public.proyecto_miembros for delete to authenticated
  using (public.es_propietario(proyecto_id) and usuario_id <> auth.uid());

alter table public.invitaciones enable row level security;
create policy invitaciones_propietario on public.invitaciones for all to authenticated
  using (public.es_propietario(proyecto_id)) with check (public.es_propietario(proyecto_id));

alter table public.perfiles enable row level security;
create policy perfiles_propio on public.perfiles for all to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

alter table public.borradores enable row level security;
create policy borradores_propios on public.borradores for all to authenticated
  using (usuario_id = auth.uid()
         and (proyecto_id is null or public.es_miembro(proyecto_id)))
  with check (usuario_id = auth.uid()
              and (proyecto_id is null or public.es_miembro(proyecto_id)));

-- Historial, instantáneas y auditoría: solo lectura para los miembros; los
-- llenan los triggers y la función registrar_instantanea.
alter table public.historial enable row level security;
create policy historial_leer on public.historial for select to authenticated
  using (public.es_miembro(proyecto_id));

alter table public.instantaneas enable row level security;
create policy instantaneas_leer on public.instantaneas for select to authenticated
  using (public.es_miembro(proyecto_id));
create policy instantaneas_crear on public.instantaneas for insert to authenticated
  with check (public.puede_editar(proyecto_id));
create policy instantaneas_editar on public.instantaneas for update to authenticated
  using (public.puede_editar(proyecto_id)) with check (public.puede_editar(proyecto_id));

alter table public.auditoria enable row level security;
create policy auditoria_leer on public.auditoria for select to authenticated
  using (proyecto_id is not null and public.es_miembro(proyecto_id));

-- ==========================================================================
-- PERMISOS DE LOS ROLES DE SUPABASE
-- ==========================================================================
-- anon (visitante sin sesión) no accede a ninguna tabla ni función.
-- authenticated (usuario con sesión) accede, siempre filtrado por el RLS.
revoke all on all tables in schema public from anon;
revoke all on all sequences in schema public from anon;
revoke execute on all functions in schema public from anon, public;

grant select, insert, update, delete on all tables in schema public to authenticated;
revoke insert, update, delete on public.historial, public.auditoria from authenticated;
revoke insert, update, delete on public.cat_etapas, public.cat_roles, public.cat_disciplinas, public.cat_tipos_restriccion,
  public.cat_causas_no_cumplimiento, public.cat_kpi, public.cat_hitos, public.cat_actividades_awp,
  public.cat_criterios_liberacion, public.cat_criterios_cwa, public.cat_actividades_raci from authenticated;
grant usage on all sequences in schema public to authenticated;
grant execute on function public.es_miembro(uuid), public.puede_editar(uuid), public.es_propietario(uuid),
  public.fecha_corte(uuid), public.registrar_instantanea(uuid), public.aceptar_invitaciones() to authenticated;

-- Las tablas que se creen en el futuro tampoco quedan abiertas a anon.
alter default privileges in schema public revoke all on tables from anon;
alter default privileges in schema public revoke execute on functions from anon, public;


-- ==========================================================================
-- CATÁLOGOS DEL KIT
-- ==========================================================================

insert into public.cat_etapas (codigo, nombre, orden) values
  ('FEL', 'Planificación temprana (FEL)', 1),
  ('ING', 'Ingeniería', 2),
  ('PRO', 'Procura', 3),
  ('CON', 'Construcción', 4),
  ('COM', 'Comisionamiento', 5);

insert into public.cat_roles (codigo, nombre, responsabilidades, orden) values
  ('CLI', 'Gerente del proyecto del cliente', 'Patrocina AWP; aprueba el plan, el PoC y los hitos; exige requisitos AWP en los contratos; participa en las revisiones mensuales de KPI.', 1),
  ('GP', 'Gerente de Proyecto', 'Responsable final de la implementación; asigna recursos; resuelve restricciones escaladas; integra AWP en el plan de ejecución.', 2),
  ('CHA', 'AWP Champion', 'Lidera la implementación; define estrategia, procedimientos y plantillas; forma al equipo; facilita los talleres de PoC; audita el proceso; consolida KPI y lecciones.', 3),
  ('LWF', 'Líder de WFP', 'Coordina a los planificadores; dirige la reunión semanal de restricciones; controla el backlog y la liberación de IWP; consolida el reporte semanal de WFP.', 4),
  ('WFP', 'Planificador de frente de trabajo', 'Divide los CWP en IWP; identifica y sigue restricciones; arma y libera los IWP; recibe los IWP terminados y registra avance y causas de no cumplimiento.', 5),
  ('ING', 'Líder de Ingeniería', 'Planifica y emite los EWP en la secuencia del PoC; mantiene el modelo 3D con atributos AWP; responde RFI; participa en revisiones de constructabilidad.', 6),
  ('PRO', 'Líder de Procura', 'Estructura los PWP; asegura fechas RAS alineadas; informa el estado de materiales por CWP/IWP; gestiona la documentación del proveedor.', 7),
  ('MAT', 'Gestor de materiales', 'Recibe, almacena, reserva y despacha materiales por IWP; confirma disponibilidad antes de la liberación.', 8),
  ('CON', 'Gerente de Construcción', 'Lidera el PoC; aprueba CWP; decide la secuencia de ejecución; controla fechas plan/real de paquetes; prioriza restricciones críticas.', 9),
  ('SUP', 'Superintendente / capataz general', 'Selecciona IWP del backlog para el lookahead; ejecuta los IWP con sus capataces; informa avance y problemas en campo.', 10),
  ('CTR', 'Controles del proyecto', 'Integra CWP (nivel 3) e IWP (nivel 5) en el cronograma; mide avance y productividad; calcula los KPI.', 11),
  ('IM', 'Coordinador de gestión de información', 'Define la codificación y los atributos; integra modelo 3D, cronograma, materiales y documentos; administra el software de WFP.', 12),
  ('HSE', 'Líder de HSE', 'Incorpora análisis de riesgos (JHA) y permisos en CWP e IWP; valida los requisitos de seguridad antes de liberar.', 13),
  ('CAL', 'Líder de calidad (QA/QC)', 'Incluye ITP y registros de inspección en CWP e IWP; verifica el cierre de calidad de cada IWP.', 14),
  ('COM', 'Líder de comisionamiento', 'Define sistemas y secuencia de puesta en marcha; relaciona IWP con sistemas; prepara SWP y TOP.', 15),
  ('SUB', 'Subcontratista de especialidad', 'Aplica el proceso AWP en su alcance; aporta planificadores según contrato; cumple el lookahead y reporta avance por IWP.', 16);

insert into public.cat_disciplinas (codigo, nombre) values
  ('CIV', 'Civil'),
  ('EST', 'Estructuras'),
  ('ARQ', 'Arquitectura'),
  ('MEC', 'Mecánica'),
  ('TUB', 'Tuberías'),
  ('ELE', 'Eléctrica'),
  ('INS', 'Instrumentación y control'),
  ('VAR', 'Varias disciplinas');

insert into public.cat_tipos_restriccion (nombre, ejemplos, responsable_habitual, anticipacion_semanas) values
  ('Ingeniería', 'Plano no emitido IFC, RFI abierta, revisión pendiente', 'Líder de Ingeniería', 4),
  ('Materiales', 'Material no recibido, no conforme o no reservado', 'Líder de Procura / Gestor de materiales', 4),
  ('Equipos de construcción', 'Grúa, plataforma elevadora o equipo pesado no disponible', 'Gerente de Construcción', 3),
  ('Permisos', 'Permiso de trabajo, excavación, trabajo en caliente, licencia municipal', 'Líder de HSE', 3),
  ('Mano de obra', 'Cuadrilla o especialista no disponible, acreditaciones', 'Superintendente', 2),
  ('Andamios', 'Andamio no solicitado, no montado o no inspeccionado', 'Superintendente', 3),
  ('Acceso / interferencias', 'Frente ocupado por otra cuadrilla, vía cerrada', 'Gerente de Construcción', 2),
  ('Trabajos predecesores', 'Trabajo previo no terminado o no liberado por calidad', 'Superintendente', 1),
  ('Calidad', 'ITP no aprobado, procedimiento de soldadura no calificado', 'Líder de calidad', 2),
  ('HSE', 'JHA no aprobado, plan de izaje pendiente', 'Líder de HSE', 2),
  ('Documentación del proveedor', 'Planos certificados o manual de montaje pendientes', 'Líder de Procura', 4),
  ('Interfaz entre fases', 'Entrega de área o conexión pendiente de otra fase', 'AWP Champion', 6);

insert into public.cat_causas_no_cumplimiento (nombre, orden) values
  ('Ingeniería', 1),
  ('Materiales', 2),
  ('Equipos de construcción', 3),
  ('Permisos', 4),
  ('Mano de obra', 5),
  ('Andamios', 6),
  ('Acceso / interferencias', 7),
  ('Trabajos predecesores', 8),
  ('Calidad', 9),
  ('HSE', 10),
  ('Documentación del proveedor', 11),
  ('Interfaz entre fases', 12),
  ('Clima', 13),
  ('Cambio de prioridad', 14),
  ('Productividad menor a la prevista', 15),
  ('Otro', 16);

insert into public.cat_kpi (codigo, nombre, formula, unidad, sentido, meta_f1, meta_f2, meta_f3, tipo) values
  ('K01', 'EWP emitidos a tiempo', 'EWP emitidos IFC a tiempo ÷ EWP con fecha requerida vencida', '%', '≥', 0.8, 0.9, 0.95, 'Proceso'),
  ('K02', 'Materiales disponibles al liberar', 'IWP liberados con 100 % de materiales ÷ IWP liberados', '%', '≥', 0.9, 0.95, 0.98, 'Proceso'),
  ('K03', 'IWP liberados sin restricciones', 'IWP liberados sin restricciones abiertas ÷ IWP liberados', '%', '≥', 0.85, 0.95, 0.98, 'Proceso'),
  ('K04', 'Backlog de IWP liberados', 'HH de IWP liberados no iniciados ÷ HH ejecutadas por semana', 'semanas', '≥', 2, 2, 3, 'Proceso'),
  ('K05', 'Restricciones liberadas a tiempo', 'Restricciones liberadas a tiempo ÷ restricciones liberadas', '%', '≥', 0.8, 0.9, 0.95, 'Proceso'),
  ('K06', 'Atraso promedio de restricciones', 'Suma de días de atraso ÷ N.° de restricciones vencidas', 'días', '≤', 7, 5, 3, 'Proceso'),
  ('K07', 'Cobertura de planificadores', 'Trabajadores directos ÷ planificadores', 'trab./planif.', '≤', 55, 50, 50, 'Proceso'),
  ('K08', 'Porcentaje de plan cumplido (PPC)', 'IWP completados según plan ÷ IWP planificados', '%', '≥', 0.75, 0.8, 0.85, 'Resultado'),
  ('K09', 'IWP devueltos', 'IWP devueltos de campo ÷ IWP entregados a campo', '%', '≤', 0.08, 0.05, 0.03, 'Resultado'),
  ('K10', 'Factor de productividad', 'HH ganadas ÷ HH gastadas', 'índice', '≥', 0.95, 1.0, 1.05, 'Resultado'),
  ('K11', 'Tiempo productivo (tool time)', 'Tiempo en trabajo directo ÷ tiempo observado', '%', '≥', 0.4, 0.44, 0.46, 'Resultado'),
  ('K12', 'Retrabajo', 'HH de retrabajo ÷ HH gastadas', '%', '≤', 0.04, 0.03, 0.02, 'Resultado'),
  ('K13', 'SPI de construcción', 'Valor ganado ÷ valor planificado', 'índice', '≥', 0.95, 0.98, 1.0, 'Resultado');

insert into public.cat_hitos (codigo, nombre, criterio, evidencia, aprueba, orden) values
  ('H0', 'Estrategia AWP aprobada (programa)', 'Plan de implementación AWP firmado; AWP Champion designado; nivel de madurez objetivo por fase definido.', 'Plan firmado, acta de designación', 'Cliente', 1),
  ('H1', 'CWA definidas', '100 % del alcance de la fase asignado a CWA sin superposiciones; CWA con límites en plano y código.', 'Plano de CWA, plantilla Definicion_CWA', 'AWP Champion', 2),
  ('H2', 'Path of Construction aprobado', 'Secuencia de CWA y CWP acordada en taller IPP con construcción, ingeniería, procura y comisionamiento; PoC congelado.', 'Acta del taller, plantilla Path_of_Construction', 'Cliente y Gerente de Construcción', 3),
  ('H3', 'CWP, EWP y PWP definidos', 'Lista completa de CWP con su EWP y PWP asociados; fechas requeridas calculadas desde el PoC; plan de liberación publicado.', 'Seguimiento_Paquetes con fechas plan', 'AWP Champion', 4),
  ('H4', 'Requisitos AWP en contratos', 'Cláusulas AWP incluidas en contratos y subcontratos de la fase (niveles 3 y 5, planificadores, reportes).', 'Contratos firmados', 'Gerente de Proyecto', 5),
  ('H5', 'Primer EWP emitido IFC en secuencia', 'El EWP del primer CWP del PoC está emitido IFC completo, antes de su fecha requerida.', 'Transmittal de ingeniería', 'Líder de Ingeniería', 6),
  ('H6', 'Primer CWP emitido a construcción', 'CWP completo según la plantilla, con materiales asegurados (PWP) y aprobado.', 'Plantilla de CWP firmada', 'Gerente de Construcción', 7),
  ('H7', 'Primer IWP liberado', 'IWP sin restricciones abiertas, con checklist de liberación firmado, entregado al capataz.', 'Checklist de liberación, registro de restricciones', 'Líder de WFP', 8),
  ('H8', 'Backlog estable', 'Backlog de IWP liberados igual o mayor a la meta de la fase durante 4 semanas seguidas.', 'Tablero de KPI', 'Gerente de Construcción', 9),
  ('H9', 'Primer sistema o área entregado', 'Primer SWP o acta de entrega de área completa, con documentación.', 'Acta de entrega / SWP', 'Líder de comisionamiento', 10),
  ('H10', 'Cierre AWP de la fase', 'Informe de cierre AWP y registro de lecciones aprendidas aprobados y comunicados a la fase siguiente.', 'Informe de cierre, registro de lecciones', 'AWP Champion y Cliente', 11);

insert into public.cat_actividades_awp (codigo, etapa, orden, nombre, descripcion, hito, plantilla) values
  ('FEL-01', 'Planificación temprana (FEL)', 1, 'Designar al AWP Champion', 'Designar al AWP Champion y formar el equipo AWP (cliente y contratista).', 'H0', 'Perfiles_Puesto_AWP.docx'),
  ('FEL-02', 'Planificación temprana (FEL)', 2, 'Evaluar la escala de AWP', 'Evaluar la escala de AWP que conviene al proyecto (modelo de AWP escalable de la COAA) y definir el nivel de madurez objetivo por fase.', null, 'Registro_Riesgos.xlsx'),
  ('FEL-03', 'Planificación temprana (FEL)', 3, 'Dividir el proyecto en CWA', 'Dividir el proyecto en CWA siguiendo límites físicos y lógicos (ver la plantilla Definicion_CWA.xlsx).', 'H1', 'Definicion_CWA.xlsx'),
  ('FEL-04', 'Planificación temprana (FEL)', 4, 'Desarrollar el Path of Construction (PoC)', 'Desarrollar el Path of Construction (PoC) en talleres de planificación interactiva (IPP) con construcción, ingeniería, procura, comisionamiento y el cliente. El PoC se desarrolla en FEL 2 y se congela en FEL 3.', 'H2', 'Path_of_Construction.xlsx'),
  ('FEL-05', 'Planificación temprana (FEL)', 5, 'Elaborar la lista preliminar de CWP', 'Elaborar la lista preliminar de CWP y el plan de liberación CWP/EWP/PWP (qué paquete se necesita y cuándo).', 'H3', 'Seguimiento_Paquetes.xlsx'),
  ('FEL-06', 'Planificación temprana (FEL)', 6, 'Definir la estructura de desglose del trabajo (WBS)', 'Definir la estructura de desglose del trabajo (WBS) y la codificación común de paquetes para todas las disciplinas y sistemas de información.', null, 'Seguimiento_Paquetes.xlsx'),
  ('FEL-07', 'Planificación temprana (FEL)', 7, 'Incluir los requisitos AWP en los contratos', 'Incluir los requisitos AWP en los contratos cronograma de nivel 3 por CWP y de nivel 5 por IWP, dotación de planificadores, entrega de EWP por paquete, reportes.', 'H4', 'Matriz_Roles_RACI.xlsx'),
  ('FEL-08', 'Planificación temprana (FEL)', 8, 'Definir los requisitos de gestión de la información', 'Definir los requisitos de gestión de la información modelo 3D, atributos, integración con cronograma y materiales.', null, null),
  ('ING-01', 'Ingeniería', 1, 'Planificar la ingeniería por EWP', 'Planificar la ingeniería por EWP cada uno ligado a un único CWP y con una fecha requerida calculada hacia atrás desde el inicio del CWP (Path of Engineering).', null, 'Plantilla_EWP.docx'),
  ('ING-02', 'Ingeniería', 2, 'Priorizar los EWP según el PoC', 'Priorizar los EWP según el PoC primero los que alimentan los CWP tempranos y las compras de largo plazo.', null, null),
  ('ING-03', 'Ingeniería', 3, 'Emitir los EWP completos', 'Emitir los EWP completos planos IFC, especificaciones, listas de materiales (MTO) y datos del proveedor necesarios para construir.', 'H5', 'Plantilla_EWP.docx'),
  ('ING-04', 'Ingeniería', 4, 'Mantener el modelo 3D con atributos', 'Mantener el modelo 3D con atributos (código de CWA, CWP e IWP; estado de ingeniería; estado de materiales) para que los planificadores puedan armar los IWP.', null, null),
  ('ING-05', 'Ingeniería', 5, 'Revisiones de constructabilidad', 'Revisiones de constructabilidad con construcción antes de la emisión IFC.', null, null),
  ('ING-06', 'Ingeniería', 6, 'Gestionar las RFI', 'Gestionar las RFI como restricciones de ingeniería en el registro de restricciones.', null, null),
  ('PRO-01', 'Procura', 1, 'Estructurar las compras en PWP', 'Estructurar las compras en PWP alineados con los CWP (materiales a granel, materiales identificados con tag y equipos).', null, 'Seguimiento_Paquetes.xlsx'),
  ('PRO-02', 'Procura', 2, 'Fijar fechas requeridas en obra (RAS)', 'Fijar fechas requeridas en obra (RAS) a partir del PoC y del plan de liberación de CWP, no del avance de ingeniería.', null, null),
  ('PRO-03', 'Procura', 3, 'Seguir el estado de materiales por CWP e IWP', 'Seguir el estado de materiales por CWP e IWP comprado, en fabricación, en tránsito, recibido, disponible para despacho.', null, 'Seguimiento_Paquetes.xlsx'),
  ('PRO-04', 'Procura', 4, 'Reservar materiales para IWP', 'Reservar materiales para IWP y preparar entregas por paquete (bag and tag) cuando el IWP entra al lookahead de 3 semanas.', null, null),
  ('PRO-05', 'Procura', 5, 'Gestionar la documentación del proveedor', 'Gestionar la documentación del proveedor que construcción necesita (planos certificados, manuales, certificados de calidad).', null, null),
  ('CON-01', 'Construcción', 1, 'Emitir los CWP', 'Emitir los CWP con alcance, planos, cantidades, horas estimadas, secuencia, riesgos de seguridad y requisitos de calidad.', 'H6', 'Plantilla_CWP.docx'),
  ('CON-02', 'Construcción', 2, 'Dividir los CWP en IWP', 'Dividir los CWP en IWP (una cuadrilla, un capataz, alrededor de una semana de trabajo) dentro de una ventana de planificación de unas 12 semanas.', null, 'Plantilla_IWP.docx'),
  ('CON-03', 'Construcción', 3, 'Identificar, asignar y levantar restricciones', 'Identificar, asignar y levantar restricciones de cada IWP con el registro de restricciones y la reunión semanal de restricciones.', null, 'Registro_Restricciones.xlsx'),
  ('CON-04', 'Construcción', 4, 'Liberar a campo solo IWP sin restricciones', 'Liberar a campo solo IWP sin restricciones y mantener un backlog de 2 a 4 semanas de IWP listos, con trabajo de "plan B".', 'H7', 'Checklist_Liberacion_IWP.xlsx'),
  ('CON-05', 'Construcción', 5, 'Planificar con el lookahead de 3 semanas', 'Planificar con el lookahead de 3 semanas y el plan semanal; los superintendentes seleccionan IWP del backlog.', null, 'Lookahead_3_Semanas.xlsx'),
  ('CON-06', 'Construcción', 6, 'Registrar avance, horas y causas de no cumplimiento', 'Registrar avance, horas y causas de no cumplimiento por IWP y cerrar cada IWP con su documentación de calidad.', null, null),
  ('CON-07', 'Construcción', 7, 'Medir los KPI', 'Medir los KPI (PPC, restricciones, backlog, tool time, productividad) y reportarlos cada semana.', null, 'Tablero_KPI.xlsx'),
  ('COM-01', 'Comisionamiento', 1, 'Definir los sistemas y subsistemas', 'Definir los sistemas y subsistemas y su secuencia de puesta en marcha desde la planificación temprana, para que el PoC termine en sistemas completos.', null, null),
  ('COM-02', 'Comisionamiento', 2, 'Relacionar IWP y sistemas', 'Relacionar IWP y sistemas cada IWP indica a qué sistema pertenece, para saber qué falta para completar cada uno.', null, null),
  ('COM-03', 'Comisionamiento', 3, 'Preparar los paquetes de sistema (SWP) y de entrega (TOP)', 'Preparar los paquetes de sistema (SWP) y de entrega (TOP) con registros de inspección y pruebas (ITR), listas de pendientes y dossiers.', 'H9', null),
  ('COM-04', 'Comisionamiento', 4, 'Cerrar la fase', 'Cerrar la fase con el informe de cierre AWP y el registro de lecciones aprendidas para la fase siguiente.', 'H10', 'Informe_Cierre_Fase_AWP.docx');

insert into public.cat_criterios_liberacion (numero, categoria, criterio, rol) values
  (1, 'Documentos', 'Planos y documentos IFC vigentes incluidos en el IWP', 'Líder de Ingeniería'),
  (2, 'Documentos', 'Sin RFI abiertas que afecten al alcance del IWP', 'Líder de Ingeniería'),
  (3, 'Documentos', 'Vistas 3D, isométricos o croquis del alcance incluidos', 'Planificador de frente de trabajo'),
  (4, 'Documentos', 'Cantidades y HH estimadas verificadas (300 a 600 HH)', 'Planificador de frente de trabajo'),
  (5, 'Materiales', '100 % de materiales recibidos en almacén', 'Gestor de materiales'),
  (6, 'Materiales', 'Materiales inspeccionados y conformes', 'Líder de calidad (QA/QC)'),
  (7, 'Materiales', 'Materiales reservados para el IWP (y preparados por paquete si aplica)', 'Gestor de materiales'),
  (8, 'Materiales', 'Documentación del proveedor disponible (planos certificados, manuales)', 'Líder de Procura'),
  (9, 'Recursos', 'Cuadrilla y capataz asignados y acreditados', 'Superintendente / capataz general'),
  (10, 'Recursos', 'Equipos y grúas confirmados para las fechas', 'Gerente de Construcción'),
  (11, 'Recursos', 'Andamios montados e inspeccionados (o solicitados con fecha confirmada)', 'Superintendente / capataz general'),
  (12, 'Recursos', 'Herramientas y consumibles disponibles', 'Superintendente / capataz general'),
  (13, 'Frente de trabajo', 'Trabajos predecesores terminados y aceptados por calidad', 'Superintendente / capataz general'),
  (14, 'Frente de trabajo', 'Frente de trabajo libre de interferencias con otras cuadrillas o fases', 'Gerente de Construcción'),
  (15, 'HSE', 'JHA elaborado y aprobado', 'Líder de HSE'),
  (16, 'HSE', 'Permisos de trabajo identificados (excavación, altura, caliente, izaje)', 'Líder de HSE'),
  (17, 'HSE', 'Plan de izaje aprobado (si aplica)', 'Líder de HSE'),
  (18, 'Calidad', 'ITP y formatos de inspección incluidos', 'Líder de calidad (QA/QC)'),
  (19, 'Calidad', 'Procedimientos de trabajo aprobados (soldadura, concreto, pruebas)', 'Líder de calidad (QA/QC)'),
  (20, 'Registro', 'Todas las restricciones del IWP liberadas o canceladas en el registro', 'Líder de WFP'),
  (21, 'Registro', 'IWP incluido en el cronograma de nivel 5 y con sistema asignado', 'Controles del proyecto'),
  (22, 'Aprobación', 'Revisado por el planificador de frente de trabajo', 'Planificador de frente de trabajo'),
  (23, 'Aprobación', 'Revisado por el superintendente', 'Superintendente / capataz general'),
  (24, 'Aprobación', 'Aprobado para liberación por el Líder de WFP', 'Líder de WFP');

insert into public.cat_criterios_cwa (numero, criterio, descripcion) values
  (1, 'Límites', 'Tiene límites físicos o lógicos claros, dibujados en un plano de CWA y sin superposición con otras CWA.'),
  (2, 'Fase', 'Pertenece a una sola fase del proyecto.'),
  (3, 'Secuencia', 'Permite construir en una secuencia lógica que termina en sistemas o áreas entregables.'),
  (4, 'Tamaño', 'Su tamaño permite dividirla en CWP de una disciplina y menos de 40 000 HH.'),
  (5, 'Accesos', 'Considera accesos, zonas de acopio, grúas y rutas de izaje.'),
  (6, 'Interfaces', 'Identifica las interfaces con CWA vecinas y con otras fases (entregas de área, conexiones).'),
  (7, 'Sistemas', 'Identifica los sistemas de comisionamiento que atraviesan la CWA.'),
  (8, 'Modularización', 'Evalúa si parte del alcance se prefabrica o modulariza.'),
  (9, 'Código', 'Tiene código único según la codificación del kit y está cargada en el modelo 3D y el cronograma.'),
  (10, 'Aprobación', 'Fue revisada por construcción, ingeniería, procura y comisionamiento y aprobada por el AWP Champion.');

insert into public.cat_actividades_raci (orden, etapa, actividad, fase, asignaciones) values
  (1, 'Planificación temprana (FEL)', 'Aprobar la estrategia y el plan de implementación AWP', 'Todas las fases', '{"CLI": "A", "GP": "R", "CHA": "R", "CON": "C", "ING": "C", "PRO": "C", "CTR": "C", "COM": "I"}'::jsonb),
  (2, 'Planificación temprana (FEL)', 'Designar al AWP Champion y al equipo AWP', 'Todas las fases', '{"CLI": "C", "GP": "A", "CHA": "I", "CON": "C"}'::jsonb),
  (3, 'Planificación temprana (FEL)', 'Evaluar la escala de AWP y definir el nivel de madurez por fase', 'Todas las fases', '{"CLI": "C", "GP": "A", "CHA": "R", "CON": "C", "CTR": "C"}'::jsonb),
  (4, 'Planificación temprana (FEL)', 'Definir las CWA de la fase', 'Todas las fases', '{"CLI": "C", "CHA": "A", "CON": "R", "ING": "C", "COM": "C", "CTR": "C", "IM": "I"}'::jsonb),
  (5, 'Planificación temprana (FEL)', 'Desarrollar el Path of Construction en talleres IPP', 'Todas las fases', '{"CLI": "C", "CHA": "R", "CON": "A", "ING": "C", "PRO": "C", "COM": "C", "CTR": "C", "HSE": "C", "LWF": "C"}'::jsonb),
  (6, 'Planificación temprana (FEL)', 'Elaborar el plan de liberación CWP/EWP/PWP', 'Todas las fases', '{"CHA": "A", "CON": "R", "ING": "R", "PRO": "R", "CTR": "R", "LWF": "C"}'::jsonb),
  (7, 'Planificación temprana (FEL)', 'Definir la WBS y la codificación de paquetes', 'Todas las fases', '{"CHA": "A", "IM": "R", "CTR": "R", "ING": "C", "PRO": "C", "CON": "C"}'::jsonb),
  (8, 'Planificación temprana (FEL)', 'Incluir los requisitos AWP en contratos y subcontratos', 'Todas las fases', '{"CLI": "C", "GP": "A", "CHA": "C", "PRO": "R", "SUB": "I"}'::jsonb),
  (9, 'Planificación temprana (FEL)', 'Definir los requisitos de gestión de la información y del modelo 3D', 'Todas las fases', '{"CHA": "A", "IM": "R", "ING": "C", "CTR": "C", "PRO": "C"}'::jsonb),
  (10, 'Planificación temprana (FEL)', 'Implementar el software de WFP integrado con modelo, cronograma y materiales', 'Fase 2', '{"CHA": "A", "IM": "R", "LWF": "C", "ING": "C", "PRO": "C", "CTR": "C"}'::jsonb),
  (11, 'Ingeniería', 'Planificar la ingeniería por EWP según el PoC', 'Todas las fases', '{"ING": "A", "CTR": "R", "CON": "C", "CHA": "C"}'::jsonb),
  (12, 'Ingeniería', 'Emitir EWP completos (IFC y MTO) en la secuencia del PoC', 'Todas las fases', '{"ING": "A", "CON": "I", "PRO": "I", "LWF": "I", "CHA": "I"}'::jsonb),
  (13, 'Ingeniería', 'Mantener el modelo 3D con atributos AWP', 'Todas las fases', '{"IM": "A", "ING": "R", "LWF": "C", "WFP": "I"}'::jsonb),
  (14, 'Ingeniería', 'Revisar la constructabilidad antes de la emisión IFC', 'Todas las fases', '{"ING": "A", "CON": "R", "SUP": "C", "HSE": "C", "CAL": "C"}'::jsonb),
  (15, 'Ingeniería', 'Responder las RFI', 'Todas las fases', '{"ING": "A", "WFP": "C", "LWF": "I", "CON": "I"}'::jsonb),
  (16, 'Procura', 'Estructurar las compras en PWP por CWP', 'Todas las fases', '{"PRO": "A", "ING": "C", "CON": "C", "MAT": "C", "CHA": "C"}'::jsonb),
  (17, 'Procura', 'Alinear las fechas RAS con el PoC', 'Todas las fases', '{"PRO": "A", "CTR": "R", "CON": "C", "ING": "C"}'::jsonb),
  (18, 'Procura', 'Informar el estado de materiales por CWP e IWP', 'Todas las fases', '{"PRO": "A", "MAT": "R", "LWF": "I", "WFP": "I"}'::jsonb),
  (19, 'Procura', 'Reservar y despachar materiales por IWP', 'Todas las fases', '{"MAT": "A", "WFP": "C", "SUP": "I", "PRO": "C"}'::jsonb),
  (20, 'Procura', 'Gestionar la documentación del proveedor', 'Todas las fases', '{"PRO": "A", "ING": "C", "CAL": "C", "COM": "C"}'::jsonb),
  (21, 'Construcción', 'Emitir los CWP', 'Todas las fases', '{"CON": "A", "LWF": "R", "ING": "C", "PRO": "C", "HSE": "C", "CAL": "C", "CTR": "C"}'::jsonb),
  (22, 'Construcción', 'Dividir los CWP en IWP', 'Todas las fases', '{"LWF": "A", "WFP": "R", "SUP": "C", "CTR": "I"}'::jsonb),
  (23, 'Construcción', 'Identificar y registrar restricciones', 'Todas las fases', '{"LWF": "A", "WFP": "R", "SUP": "C", "SUB": "R"}'::jsonb),
  (24, 'Construcción', 'Levantar las restricciones asignadas', 'Todas las fases', '{"LWF": "A", "ING": "R", "PRO": "R", "MAT": "R", "HSE": "R", "SUP": "R"}'::jsonb),
  (25, 'Construcción', 'Dirigir la reunión semanal de restricciones', 'Todas las fases', '{"LWF": "A", "CON": "C", "WFP": "C", "ING": "C", "PRO": "C", "SUP": "C"}'::jsonb),
  (26, 'Construcción', 'Liberar IWP con el checklist de liberación', 'Todas las fases', '{"LWF": "A", "WFP": "R", "SUP": "C", "HSE": "C", "CAL": "C", "MAT": "C"}'::jsonb),
  (27, 'Construcción', 'Seleccionar IWP del backlog (lookahead de 3 semanas)', 'Todas las fases', '{"CON": "A", "SUP": "R", "LWF": "C", "SUB": "C"}'::jsonb),
  (28, 'Construcción', 'Ejecutar el IWP en campo', 'Todas las fases', '{"SUP": "A", "SUB": "R", "WFP": "I", "CAL": "C", "HSE": "C"}'::jsonb),
  (29, 'Construcción', 'Cerrar el IWP (avance, HH, calidad)', 'Todas las fases', '{"LWF": "A", "WFP": "R", "SUP": "R", "CAL": "R", "CTR": "I"}'::jsonb),
  (30, 'Construcción', 'Calcular y reportar los KPI', 'Todas las fases', '{"CHA": "A", "CTR": "R", "LWF": "R", "GP": "I", "CLI": "I"}'::jsonb),
  (31, 'Construcción', 'Gestionar las interfaces entre fases superpuestas', 'Fases 2 y 3', '{"CHA": "A", "CON": "R", "ING": "C", "COM": "C", "CTR": "C"}'::jsonb),
  (32, 'Construcción', 'Auditar el proceso AWP', 'Todas las fases', '{"CHA": "A", "LWF": "C", "CON": "C", "GP": "I", "CLI": "I"}'::jsonb),
  (33, 'Comisionamiento', 'Definir los sistemas y la secuencia de puesta en marcha', 'Todas las fases', '{"COM": "A", "ING": "R", "CON": "C", "CHA": "C", "CLI": "C"}'::jsonb),
  (34, 'Comisionamiento', 'Relacionar los IWP con los sistemas', 'Todas las fases', '{"COM": "A", "LWF": "R", "IM": "R", "WFP": "C"}'::jsonb),
  (35, 'Comisionamiento', 'Preparar los SWP y TOP', 'Todas las fases', '{"COM": "A", "CAL": "R", "CON": "C", "SUP": "C", "CLI": "I"}'::jsonb),
  (36, 'Comisionamiento', 'Capturar y transferir lecciones aprendidas', 'Todas las fases', '{"CHA": "A", "LWF": "R", "GP": "C", "CLI": "I", "ING": "C", "PRO": "C", "CON": "C", "COM": "C"}'::jsonb),
  (37, 'Comisionamiento', 'Elaborar el informe de cierre AWP de la fase', 'Todas las fases', '{"CHA": "A", "CTR": "C", "LWF": "C", "GP": "C", "CLI": "I"}'::jsonb);
