# Guía: preparar Supabase para la aplicación AWP

Tiempo estimado: **15 a 20 minutos**. No necesitas instalar nada: todo se hace desde el navegador.

Supabase es el servicio que guardará los datos de tus proyectos (una base de datos PostgreSQL) y controlará el inicio de sesión. El plan gratuito es suficiente.

> Los nombres de los botones pueden variar un poco, porque Supabase actualiza su panel. Si no encuentras uno, busca el texto entre paréntesis o usa el buscador del panel.

---

## Paso 1. Crear la cuenta

1. Entra a **https://supabase.com** y pulsa **Start your project** (o **Sign up**).
2. Elige **Continue with GitHub** (usa la misma cuenta de GitHub del repositorio) o regístrate con tu correo y una contraseña.
3. Si te lo pide, confirma tu correo desde el mensaje que te llega.

## Paso 2. Crear el proyecto

1. En el panel, pulsa **New project**.
2. Si te pide una **organización**, crea una con tu nombre (plan **Free**).
3. Completa:
   - **Project name:** `awp-app`
   - **Database password:** pulsa **Generate a password** y **guárdala en un lugar seguro** (no la necesitaré, pero te servirá si algún día hay que restaurar la base de datos).
   - **Region:** la más cercana a ti, por ejemplo **South America (São Paulo)**.
   - **Plan:** Free.
4. Pulsa **Create new project** y espera 1 a 2 minutos hasta que el panel diga que el proyecto está listo.

## Paso 3. Ejecutar el script de la base de datos

El script crea las tablas, las reglas de seguridad y los catálogos del kit. **No contiene datos de proyectos.**

1. Abre el script en GitHub:
   **https://github.com/ehchavezm-hub/01-awp/blob/main/app/supabase/esquema.sql**
   (mientras el pull request no esté fusionado, abre el enlace del pull request y busca el archivo `app/supabase/esquema.sql`).
2. Pulsa el botón **Copy raw file** (ícono de dos hojas, arriba a la derecha del archivo) para copiar todo el contenido.
3. En Supabase, en el menú de la izquierda, entra a **SQL Editor** (ícono `>_`).
4. Pulsa **New query** (o **+**), pega el contenido (Ctrl+V; en Mac, Cmd+V) y pulsa **Run** (o Ctrl+Enter).
5. Si aparece un aviso sobre una **operación destructiva** o sobre **RLS**, confirma con **Run this query**. Es normal: el script revoca permisos para que nadie sin sesión acceda.
6. Resultado esperado: **«Success. No rows returned»**.

**Comprobar que salió bien:**

- En **Table Editor** deben aparecer unas 36 tablas (por ejemplo, `proyectos`, `fases`, `paquetes`, `restricciones`, `cat_kpi`).
- Abre la tabla `cat_kpi`: debe tener 13 filas (K01 a K13).
- En **Authentication → Policies** (o **Database → Policies**), cada tabla debe decir **RLS enabled**.

**Si aparece un error:** copia el mensaje y envíamelo. No vuelvas a ejecutar el script en el mismo proyecto (daría errores de «ya existe»); si hiciera falta empezar de cero, lo más simple es borrar el proyecto de Supabase (**Project Settings → General → Delete project**) y crear otro.

## Paso 4. Crear tu usuario

1. Menú izquierdo: **Authentication → Users**.
2. Pulsa **Add user → Create new user**.
3. Escribe tu **correo** y una **contraseña** segura (la usarás para entrar a la aplicación).
4. Marca **Auto Confirm User** (así no tienes que confirmar por correo).
5. Pulsa **Create user**.

## Paso 5. Cerrar el registro a otras personas

La aplicación es tuya. Para que nadie más pueda crearse una cuenta:

1. **Authentication → Sign In / Providers** (en algunos paneles: **Authentication → Providers → Email** o **Authentication → Settings**).
2. Desactiva **Allow new users to sign up** (permitir que nuevos usuarios se registren) y pulsa **Save**.
3. Deja **activado** el proveedor **Email** (es el que usarás para entrar con correo y contraseña).

Aunque alguien lograra registrarse, las reglas de seguridad le impedirían ver tus proyectos; este paso es una protección adicional. Más adelante, si quieres invitar a otras personas, podrás crear sus usuarios desde **Add user**.

## Paso 6. Configurar la dirección de la aplicación

Sirve para que los enlaces de «recuperar contraseña» lleven a la aplicación.

1. **Authentication → URL Configuration**.
2. **Site URL:** `https://ehchavezm-hub.github.io/01-awp/app/`
3. En **Redirect URLs**, pulsa **Add URL** y agrega la misma dirección: `https://ehchavezm-hub.github.io/01-awp/app/`
4. Pulsa **Save**.

## Paso 7. Copiar los dos datos que necesito

1. Ve a **Project Settings** (ícono de engranaje) → **Data API** o **API**.
2. Copia estos dos datos:

| Dato | Dónde está | Ejemplo |
|---|---|---|
| **Project URL** | «Project URL» | `https://abcdefghijkl.supabase.co` |
| **anon key** (clave pública) | «Project API keys» → **anon · public** (en paneles nuevos: **API Keys → Publishable key**) | `eyJhbGciOi…` o `sb_publishable_…` |

3. **Envíamelos en el chat.** Ambos son públicos por diseño: la aplicación los incluye en su código y la seguridad la dan las reglas de la base de datos (Row Level Security).

> ⚠️ **Nunca compartas la clave `service_role`** (o **Secret key**). Esa clave salta todas las reglas de seguridad. No la necesito y no debe aparecer en ningún archivo ni mensaje.

---

## Bueno saber

- **Pausa por inactividad:** en el plan gratuito, si nadie usa el proyecto durante 7 días, Supabase lo pausa. Tus datos no se pierden: entra a **https://supabase.com/dashboard**, abre el proyecto y pulsa **Restore project**. Tarda unos minutos.
- **Copias de seguridad:** el plan gratuito no guarda copias descargables. La aplicación permitirá exportar cada módulo a Excel y un reporte completo en PDF; conviene hacerlo al cerrar cada fase.
- **Límites del plan gratuito:** 500 MB de base de datos (sobra para cientos de proyectos) y 50 000 usuarios activos al mes.
- **Qué datos ve Supabase:** solo los que registres en la aplicación. El repositorio de GitHub (que es público) no contiene ningún dato de tus proyectos.

## Lista final

- [ ] Proyecto `awp-app` creado.
- [ ] Script `esquema.sql` ejecutado con «Success».
- [ ] Mi usuario creado con **Auto Confirm User**.
- [ ] Registro de nuevos usuarios desactivado.
- [ ] Site URL y Redirect URL configuradas.
- [ ] **Project URL** y **anon key** enviadas en el chat.
