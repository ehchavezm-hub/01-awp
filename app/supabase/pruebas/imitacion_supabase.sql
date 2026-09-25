-- Imitación mínima de Supabase para pruebas locales.
do $$ begin create role anon nologin; exception when duplicate_object then null; end $$;
do $$ begin create role authenticated nologin; exception when duplicate_object then null; end $$;
create schema auth;
create table auth.users (id uuid primary key, email text);
create function auth.uid() returns uuid language sql stable as
  $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
create function auth.jwt() returns jsonb language sql stable as
  $$ select coalesce(nullif(current_setting('request.jwt.claims', true), ''), '{}')::jsonb $$;
grant usage on schema auth to anon, authenticated;
grant usage on schema public to anon, authenticated;
grant execute on function auth.uid(), auth.jwt() to anon, authenticated;
insert into auth.users values ('11111111-1111-1111-1111-111111111111', 'yo@correo.com'),
                              ('22222222-2222-2222-2222-222222222222', 'otro@correo.com');
