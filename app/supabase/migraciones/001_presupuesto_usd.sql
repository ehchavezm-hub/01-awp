-- Migración 001 · Presupuesto del proyecto en USD
-- Para bases creadas con una versión anterior de esquema.sql (Etapas 1 y 2).
-- Cómo aplicarla: Supabase → SQL Editor → New query → pegar este texto → Run.
-- Es segura de repetir: si la columna ya existe, no hace nada.

alter table public.proyectos
  add column if not exists presupuesto_usd numeric
  constraint proyectos_presupuesto_positivo check (presupuesto_usd >= 0);

comment on column public.proyectos.presupuesto_usd is 'Presupuesto (costo total instalado) del proyecto en USD.';

-- Avisa a la API de Supabase que el esquema cambió.
notify pgrst, 'reload schema';
