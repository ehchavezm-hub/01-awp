# doc2md: PDF y EPUB a Markdown, fiel al original

Convierte PDF y EPUB a Markdown con [Docling](https://github.com/docling-project/docling)
y **verifica** el resultado palabra por palabra contra el original. Así sabes
exactamente qué páginas quedaron fieles y cuáles hay que revisar a mano.

## Principios

- **Sin IA generativa.** Docling usa modelos solo para reconocer la estructura
  (títulos, columnas, tablas). El texto se copia de la capa de texto del PDF, sin
  reescribirlo, y el de las celdas de tabla también sale del PDF.
- **Nada se adivina.** Lo que no se puede verificar (páginas escaneadas pasadas
  por OCR) se marca para revisión y nunca se da por bueno.
- **Trazabilidad.** Cada página (`<!-- página N -->`) o capítulo
  (`<!-- capítulo N: ruta -->`) queda marcado en el Markdown.
- **Imágenes locales.** Se guardan en `<nombre>_imagenes/` con rutas relativas.
- **Encabezados y pies de página.** Se omiten del cuerpo, pero cada palabra
  omitida queda listada en el informe. Con `--conservar-encabezados` se mantienen.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r tools/doc2md/requirements.txt
```

Para PDF escaneados conviene instalar también [Tesseract](https://github.com/tesseract-ocr/tesseract)
con los idiomas español e inglés (`spa`, `eng`). Sin Tesseract se usa RapidOCR,
que reconoce peor los acentos y la ñ.

La primera conversión de un PDF descarga los modelos de Docling desde
`huggingface.co`. Para trabajar sin internet, descárgalos una vez con
`docling-tools models download` y pasa la carpeta con `--modelos`.

## Uso

```bash
cd tools/doc2md
python -m doc2md ruta/libro.epub ruta/documento.pdf -o ../../md
```

Por cada archivo se genera:

| Archivo | Contenido |
|---|---|
| `<nombre>.md` | El Markdown |
| `<nombre>_imagenes/` | Las imágenes extraídas |
| `<nombre>.reporte.md` | El informe de verificación |

El comando termina con código 0 si todo quedó verificado y 1 si hay algo que revisar.

### Opciones

| Opción | Efecto |
|---|---|
| `--umbral 0.995` | Cobertura mínima para aprobar una página o capítulo |
| `--ocr auto\|siempre\|nunca` | `auto`: OCR solo en páginas sin capa de texto |
| `--idiomas spa,eng` | Idiomas de Tesseract |
| `--conservar-encabezados` | No omitir encabezados ni pies de página |
| `--modelos CARPETA` | Modelos de Docling descargados (sin internet) |
| `-v` | Mostrar el registro de Docling |

## Cómo se verifica

1. Se extrae el texto del original por un camino **independiente** de Docling:
   pdfium para PDF y el texto visible de cada XHTML para EPUB.
2. Se comparan las palabras de cada página o capítulo con las del Markdown,
   sin tener en cuenta la sintaxis Markdown y normalizando ligaduras (ﬁ → fi)
   y guiones de fin de línea.
3. Se informa:
   - **Faltantes:** palabras del original que no están en el Markdown.
   - **Sobrantes:** palabras del Markdown que no están en el original. Nunca
     deberían existir, así que cualquier sobrante reprueba la unidad.
   - **Similitud de orden:** dato orientativo. En PDFs con columnas o tablas el
     orden de lectura no es único, por eso no reprueba.

Una unidad se aprueba solo si su cobertura es mayor o igual al umbral, no tiene
sobrantes y no pasó por OCR.

**Límite:** la verificación comprueba el *texto*, no el *formato*. Si un nivel
de título, una negrita o una celda desplazada dentro de una tabla está mal, no
lo detecta. Revisa visualmente las unidades con baja similitud de orden y las
tablas complejas.

## Pruebas

```bash
cd tools/doc2md
python -m pytest -q tests
```
