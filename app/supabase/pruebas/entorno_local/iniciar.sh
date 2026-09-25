#!/usr/bin/env bash
# Levanta un entorno local que imita Supabase para probar la aplicación:
# PostgreSQL (con imitacion_supabase.sql + esquema.sql), PostgREST y servidor.mjs.
# Requisitos: PostgreSQL 15+ (initdb, pg_ctl, psql), el binario `postgrest`
# (https://github.com/PostgREST/postgrest/releases) y Node.js.
# Uso: POSTGREST_BIN=/ruta/postgrest PG_BIN=/usr/lib/postgresql/16/bin bash iniciar.sh
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$AQUI/../../../.." && pwd)"
DATOS="${DATOS:-/tmp/awp_entorno}"
PG_BIN="${PG_BIN:-/usr/lib/postgresql/16/bin}"
PUERTO_PG="${PUERTO_PG:-5433}"
SECRETO="clave-de-prueba-local-de-al-menos-32-caracteres"
USUARIOS='[{"id":"11111111-1111-1111-1111-111111111111","email":"yo@correo.com","clave":"clave-prueba-1"},{"id":"22222222-2222-2222-2222-222222222222","email":"otro@correo.com","clave":"clave-prueba-2"}]'

mkdir -p "$DATOS"
# PostgreSQL no se ejecuta como administrador (root): se usa el usuario postgres.
COMO_PG=""
if [ "$(id -u)" = 0 ]; then chown postgres "$DATOS"; COMO_PG="su postgres -s /bin/bash -c"; fi
correr_pg() { if [ -n "$COMO_PG" ]; then $COMO_PG "$*"; else bash -c "$*"; fi; }
if [ ! -d "$DATOS/pg" ]; then
  correr_pg "$PG_BIN/initdb -D $DATOS/pg -U postgres -A trust >/dev/null"
fi
correr_pg "$PG_BIN/pg_ctl -D $DATOS/pg -o '-p $PUERTO_PG -k $DATOS' -l $DATOS/pg.log start >/dev/null" || true
sleep 1
pkill -f "postgrest $DATOS/postgrest.conf" 2>/dev/null || true
PSQL="psql -h $DATOS -p $PUERTO_PG -U postgres -v ON_ERROR_STOP=1 -q"
$PSQL -c "drop database if exists awp with (force)" -c "create database awp"
$PSQL -d awp -f "$REPO/app/supabase/pruebas/imitacion_supabase.sql"
$PSQL -d awp -f "$REPO/app/supabase/esquema.sql"

cat > "$DATOS/postgrest.conf" <<CONF
db-uri = "postgres://authenticator@localhost:$PUERTO_PG/awp?host=$DATOS"
db-schemas = "public"
db-anon-role = "anon"
jwt-secret = "$SECRETO"
server-port = 3001
CONF
nohup "${POSTGREST_BIN:-postgrest}" "$DATOS/postgrest.conf" > "$DATOS/postgrest.log" 2>&1 &
pkill -f "entorno_local/servidor.mjs" 2>/dev/null || true
JWT_SECRETO="$SECRETO" USUARIOS="$USUARIOS" RAIZ="$REPO" nohup node "$AQUI/servidor.mjs" > "$DATOS/servidor.log" 2>&1 &
sleep 2
echo "Aplicación: http://localhost:8080/01-awp/app/  (usuario: yo@correo.com / clave-prueba-1)"
