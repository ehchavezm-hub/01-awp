# 🌐 Diplomacia Global

Buscador **muy fácil de usar** de noticias, estudios académicos (*papers*) y libros sobre
diplomacia, relaciones internacionales y geopolítica.
Está pensado para personas mayores y para quien no tiene mucha experiencia con la tecnología:
letra grande, alto contraste, botones amplios y todo a un máximo de dos clics.

---

## ✨ Qué puede hacer

| Función | Cómo se usa |
|---|---|
| 🔍 **Buscar** | Escriba un tema, país o autor en la caja grande y pulse **Buscar**. No importan mayúsculas ni tildes, y entiende español e inglés («ONU» = «United Nations»). |
| 🎙️ **Buscar hablando** | Pulse el botón del micrófono y diga lo que busca (Chrome, Edge o Safari). |
| 🏷️ **Filtros** | Botones grandes: *Todos*, *Noticias*, *Papers / Investigaciones*, *Libros*. |
| 🔗 **Visitar enlace original** | Abre la fuente oficial en una pestaña nueva. |
| ⬇️ **Descargar documento** | Solo en documentos de acceso libre. Un clic y aparece «¡Descarga iniciada con éxito!». |
| 💬 **Compartir por WhatsApp** | Envía el título y el enlace a un familiar o amigo. |
| 🔠 **A+ / A−** | Agranda o achica toda la letra (se recuerda para la próxima visita). |
| 📚 **Mi biblioteca** | Busca **dentro** de sus propios libros (.md o .txt) y muestra el párrafo y el capítulo. |

### De dónde salen los datos

| Fuente | Qué aporta | ¿Necesita internet? |
|---|---|---|
| **Catálogo local** (`public/datos/catalogo.js`) | Libros clásicos y actuales, papers fundamentales, tratados de la ONU (PDF) y noticias **de ejemplo** | No |
| **Noticias ONU (RSS)** | Titulares reales y recientes, en español | Sí |
| **Crossref** (API gratuita) | Millones de artículos académicos reales | Sí |
| **Mi biblioteca** (carpeta `biblioteca/`) | Fragmentos de sus propios libros | No |

> Si internet falla, la aplicación **nunca queda en blanco**: muestra el catálogo local y un aviso amable.
> Las tarjetas marcadas **«Contenido de ejemplo»** son textos de demostración, no noticias reales;
> desaparecen en cuanto llegan titulares reales de Noticias ONU.

---

## 🚀 Cómo probarla en su computadora (paso a paso)

### Opción A — La más rápida (sin instalar nada)

1. Abra la carpeta `diplomacia-global/public/`.
2. Haga **doble clic** en el archivo `index.html`.
3. Se abrirá en su navegador. ¡Listo!

En este modo funciona con el **catálogo de demostración** (sin noticias reales, sin búsqueda
dentro de sus libros). Para tener todo, use la opción B.

### Opción B — Completa, con servidor (recomendada)

**Paso 1. Instale Node.js** (solo la primera vez)

1. Entre en <https://nodejs.org>.
2. Descargue la versión que dice **LTS** (la recomendada).
3. Abra el archivo descargado y pulse **Siguiente** hasta terminar.

**Paso 2. Abra una "terminal" en la carpeta del proyecto**

- **Windows:** abra la carpeta `diplomacia-global` en el Explorador de archivos, haga clic en la
  barra de direcciones (arriba), escriba `cmd` y pulse **Enter**.
- **Mac:** abra la aplicación **Terminal**, escriba `cd ` (con un espacio al final), arrastre la
  carpeta `diplomacia-global` a la ventana y pulse **Enter**.
- **Linux:** clic derecho dentro de la carpeta → **Abrir en una terminal**.

Para comprobar que Node.js quedó instalado, escriba esto y pulse **Enter**:

```bash
node --version
```

Debe aparecer un número como `v22.x.x` (sirve cualquier versión 18 o superior).

**Paso 3. Encienda la aplicación**

```bash
npm start
```

Verá este mensaje:

```
  ✅ Diplomacia Global está funcionando.
  👉 Abra su navegador en: http://localhost:3000
```

**Paso 4. Ábrala en el navegador**

Escriba `http://localhost:3000` en la barra de direcciones de Chrome, Edge, Firefox o Safari.

**Paso 5. Para apagarla**

Vuelva a la terminal y pulse **Ctrl + C**.

> 💡 No hace falta ejecutar `npm install` para usar la aplicación: no depende de ningún paquete externo.

### ¿Sin internet?

```bash
npm run sin-internet
```

Usa solo el catálogo local y su biblioteca, sin intentar conectarse a Noticias ONU ni Crossref.

### ¿El puerto 3000 está ocupado?

- **Mac / Linux:** `PUERTO=8080 npm start`
- **Windows (cmd):** `set PUERTO=8080 && npm start`

Luego abra `http://localhost:8080`.

---

## 📚 Buscar dentro de sus propios libros

1. Copie sus libros en formato `.md` o `.txt` dentro de la carpeta `biblioteca/`.
2. (Opcional) Añada su título, autor y año en `biblioteca/libros.json`. Ya vienen configurados
   *Diplomacia* (Henry Kissinger) y *Diplomacy: Theory and Practice* (G. R. Berridge).
3. Encienda la aplicación con `npm start` y busque, por ejemplo, «Richelieu» o «Guerra Fría».

Verá tarjetas **«📘 Libro · Fragmento de mi biblioteca»** con el párrafo, el capítulo y la ubicación
aproximada dentro del libro.

> 🔒 Sus libros **no se suben a GitHub** (la carpeta está excluida en `.gitignore`) y la aplicación
> nunca los ofrece para descargar: solo muestra fragmentos breves en su propia computadora.

---

## 🗂️ Estructura de archivos

```
diplomacia-global/
├── README.md                     ← Este archivo
├── package.json                  ← Comandos: npm start, npm test, npm run css
├── servidor.js                   ← Servidor web (Node.js, sin dependencias)
├── tailwind.config.js            ← Colores y fuente de Tailwind CSS
├── estilos-fuente/
│   └── tailwind.css              ← Entrada de Tailwind (solo para regenerar el CSS)
├── servidor/
│   ├── config.js                 ← Ajustes: puerto, fuentes en vivo, feeds RSS…
│   ├── buscador.js               ← Combina todas las fuentes, quita duplicados y ordena
│   └── fuentes/                  ← Un archivo por cada origen de datos
│       ├── catalogo-local.js
│       ├── noticias-rss.js       ← Noticias ONU (y cualquier otro feed RSS)
│       ├── crossref.js           ← Papers académicos reales
│       ├── biblioteca-personal.js← Búsqueda dentro de sus libros
│       └── utilidades.js
├── public/                       ← Lo que ve la persona usuaria
│   ├── index.html                ← Página única con las 4 pestañas
│   ├── css/
│   │   ├── tailwind.css          ← Tailwind ya compilado (no requiere internet)
│   │   └── estilos.css           ← Estilos de accesibilidad propios
│   ├── datos/catalogo.js         ← Catálogo de demostración (editable)
│   ├── img/icono.svg
│   └── js/
│       ├── motor-busqueda.js     ← Búsqueda sin tildes, con sinónimos (navegador y servidor)
│       ├── servicio-datos.js     ← Pide datos al servidor o usa el catálogo local
│       ├── interfaz.js           ← Dibuja las tarjetas y los avisos
│       ├── voz.js                ← Búsqueda por voz
│       └── app.js                ← Une todo: menú, filtros, letra, ayuda
├── biblioteca/                   ← Sus libros (.md / .txt), privados
│   ├── LEEME.md
│   └── libros.json
└── pruebas/
    └── pruebas.test.js           ← 18 pruebas automáticas (npm test)
```

---

## 🔌 Cómo conectar una base de datos o API real

Cada fuente es un archivo pequeño en `servidor/fuentes/` con la misma forma:

```js
module.exports = {
  nombre: 'Mi fuente',
  tipos: ['paper'],                          // 'noticia', 'paper' y/o 'libro'
  async buscar(consulta) {
    // Consulte su API o base de datos y devuelva documentos con este formato:
    return [{
      id: 'unico-123', tipo: 'paper',
      titulo: '…', resumen: '…', autor: '…', fuente: '…', fecha: '2026-01-31',
      enlace: 'https://…',
      descarga: null                         // o { url, formato: 'PDF', nombreArchivo }
    }];
  }
};
```

Después, agréguela a la lista `FUENTES_EN_VIVO` en `servidor/buscador.js`. Si la fuente falla o
tarda más de 5 segundos, la aplicación sigue funcionando con las demás.

**Ideas de fuentes:** OpenAlex (<https://openalex.org>, gratuita), feeds RSS de medios
internacionales (añádalos en `config.feedsNoticias`), Open Library para libros.
Google Scholar no ofrece una API pública oficial.

### Ajustes disponibles (variables de entorno)

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `PUERTO` | Puerto del servidor | `3000` |
| `FUENTES_EN_VIVO` | `no` para no usar internet | `si` |
| `TIEMPO_ESPERA_SEG` | Espera máxima a una fuente externa | `5` |
| `CACHE_MINUTOS` | Minutos que se recuerdan las respuestas externas | `15` |
| `CORREO_CROSSREF` | Su correo, que Crossref recomienda incluir | *(vacío)* |
| `CARPETA_BIBLIOTECA` | Otra carpeta para sus libros | `biblioteca/` |

---

## ♿ Accesibilidad (WCAG 2.1 AA)

- Texto base de **18 px**, ampliable hasta 27 px con **A+**. Títulos de tarjeta de ~29 px.
- Contraste de **14,9:1** en el texto principal (azul marino `#0b2545` sobre marfil `#fdfbf5`);
  todos los botones y etiquetas superan **7:1**.
- Botones y enlaces de **56 px** de alto como mínimo (se comprobó que ninguno baja de 44 px, en
  escritorio ni en celular).
- Iconos **siempre acompañados de texto**.
- Contorno de foco ámbar de 4 px para quien navega con teclado; enlace «Saltar al contenido».
- Resultados y avisos anunciados a lectores de pantalla (`aria-live`); al cambiar de pestaña, el
  foco pasa al título de la sección.
- Filtros hechos con botones de opción reales (se manejan con el teclado y el lector de pantalla).
- Respeta «reducir movimiento» del sistema y el modo de alto contraste de Windows.
- Fuente **Atkinson Hyperlegible**, creada para personas con baja visión (si no hay internet, se usa Verdana).
- Sin desplazamiento horizontal en celulares (probado a 390 px de ancho).

---

## 🧪 Para desarrolladores

```bash
npm test          # 18 pruebas: catálogo, motor de búsqueda, fuentes, servidor y descargas
npm install       # solo si va a cambiar clases de Tailwind…
npm run css       # …y regenerar public/css/tailwind.css
```

**Seguridad:** el servidor no sirve archivos fuera de `public/`; la ruta de descarga solo acepta
documentos del catálogo o resultados ya mostrados (no es un proxy abierto); todo el texto
externo se inserta con `textContent`, nunca como HTML.

**Pendiente de comprobar con conexión:** los conectores de Noticias ONU y Crossref se probaron
con datos simulados. El entorno donde se construyó no tenía acceso a internet, así que tampoco
se comprobaron los enlaces externos del catálogo (Gutenberg, ONU, DOI). Conviene revisarlos una
vez con `npm start`.
