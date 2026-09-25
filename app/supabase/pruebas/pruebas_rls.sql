\set ON_ERROR_STOP 0
\echo '=== 1. Visitante anónimo: no debe ver nada'
set role anon;
select count(*) from public.proyectos;
select count(*) from public.cat_kpi;
reset role;

\echo '=== 2. Usuario A crea un proyecto completo'
set role authenticated;
set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
insert into proyectos (codigo, nombre, fecha_corte) values ('PT', 'Proyecto tipo', '2028-06-15') returning codigo, creado_por is not null as con_autor;
select rol_acceso from proyecto_miembros;
insert into fases (proyecto_id, numero, nombre, sem_iwp_iniciado, sem_identificadas, sem_asignadas, sem_levantadas, sem_liberacion)
  select id, 2, 'Instalación principal', 12, 10, 8, 4, 2 from proyectos;
insert into cwa (proyecto_id, fase_id, codigo, nombre) select p.id, f.id, 'CWA-2.01', 'Bloque A' from proyectos p join fases f on f.proyecto_id = p.id;
insert into paquetes (proyecto_id, fase_id, tipo, codigo, descripcion, disciplina, cwa_id, inicio_plan, fin_plan)
  select p.id, f.id, 'CWP', 'CWP-2.01-EST-01', 'Estructura bloque A', 'EST', c.id, '2028-04-25', '2028-08-21'
  from proyectos p join fases f on f.proyecto_id = p.id join cwa c on c.proyecto_id = p.id;
insert into paquetes (proyecto_id, fase_id, tipo, codigo, descripcion, disciplina, cwa_id, cwp_id, inicio_plan, fin_plan, hh_estimadas)
  select proyecto_id, fase_id, 'IWP', 'IWP-2.01-EST-01-001', 'Columnas nivel 1', 'EST', cwa_id, id, '2028-04-25', '2028-04-30', 420
  from paquetes where codigo = 'CWP-2.01-EST-01';
insert into restricciones (proyecto_id, codigo, cwp_id, iwp_id, tipo, descripcion, responsable_rol, fecha_identificada, fecha_requerida)
  select c.proyecto_id, 'R-0005', c.id, i.id, 'Equipos de construcción', 'Grúa de 100 t', 'CON', '2028-02-20', '2028-04-11'
  from paquetes c join paquetes i on i.cwp_id = c.id where c.codigo = 'CWP-2.01-EST-01';
select codigo, dias_atraso, situacion, fase_id is not null as fase_copiada from v_restricciones;
select codigo, restricciones_abiertas, dias_atraso, situacion from v_paquetes order by codigo;
select codigo, f_liberacion_objetivo, situacion from v_iwp_liberacion;
update paquetes set estado = 'En desarrollo', avance = 10 where codigo = 'IWP-2.01-EST-01-001';
insert into avance_actividades (proyecto_id, actividad, estado) select id, 'FEL-01', 'Completada' from proyectos;
insert into avance_actividades (proyecto_id, actividad, estado) select id, 'FEL-02', 'En curso' from proyectos;
select etapa, porcentaje from v_avance_etapas;
select registrar_instantanea(id) from proyectos;
select fase_id is null as global, indicadores->>'restricciones_vencidas' vencidas, indicadores->'paquetes' paquetes from instantaneas order by 1;
select tabla, campo, valor_anterior, valor_nuevo from historial where tabla = 'paquetes' order by id;
select tabla, accion, count(*) from auditoria group by 1, 2 order by 1, 2;

\echo '=== 3. Reglas de datos (deben fallar con mensaje claro)'
insert into paquetes (proyecto_id, fase_id, tipo, codigo, descripcion, cwa_id, cwp_id)
  select proyecto_id, fase_id, 'EWP', 'EWP-2.01-TUB-01', 'Sufijo distinto', cwa_id, id from paquetes where codigo = 'CWP-2.01-EST-01';
insert into paquetes (proyecto_id, fase_id, tipo, codigo, descripcion, cwa_id) select proyecto_id, fase_id, 'CWP', 'CWP-21-EST-01', 'Código mal', cwa_id from paquetes where codigo = 'CWP-2.01-EST-01';
update restricciones set estado = 'Liberada';
update paquetes set inicio_plan = '2028-05-01', fin_plan = '2028-04-01' where codigo = 'CWP-2.01-EST-01';
insert into auditoria (tabla, accion) values ('x', 'INSERT');
update perfiles set nombre = 'x';

\echo '=== 4. Usuario B no ve ni toca el proyecto de A'
set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
select count(*) as proyectos_visibles from proyectos;
select count(*) as restricciones_visibles from v_restricciones;
select count(*) as auditoria_visible from auditoria;
update paquetes set avance = 99;
select count(*) as sin_cambios from paquetes;
insert into fases (proyecto_id, numero, nombre) select id, 9, 'intruso' from (select '00000000-0000-0000-0000-000000000000'::uuid id) x;
\echo '--- B intenta agregarse como miembro del proyecto de A'
reset role;
select id as proyecto_a from proyectos \gset
set role authenticated;
set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
insert into proyecto_miembros values (:'proyecto_a', '22222222-2222-2222-2222-222222222222', 'editor');
insert into fases (proyecto_id, numero, nombre) values (:'proyecto_a', 9, 'intruso');

\echo '=== 5. A invita a B como lector; B acepta y solo puede leer'
set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
insert into invitaciones (proyecto_id, correo, rol_acceso) values (:'proyecto_a', 'otro@correo.com', 'lector');
set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222';
set request.jwt.claims = '{"email": "otro@correo.com"}';
select aceptar_invitaciones() as aceptadas;
select count(*) as ahora_ve from proyectos;
update paquetes set avance = 50 where codigo = 'IWP-2.01-EST-01-001';
select avance as sigue_en_10 from paquetes where codigo = 'IWP-2.01-EST-01-001';
delete from proyectos;
select count(*) as no_puede_borrar from proyectos;

\echo '=== 6. A borra su proyecto (se borra todo en cascada)'
set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111';
delete from proyectos;
reset role;
select (select count(*) from paquetes) paquetes, (select count(*) from historial) historial, (select count(*) from auditoria where tabla='proyectos' and accion='DELETE') borrado_auditado;
