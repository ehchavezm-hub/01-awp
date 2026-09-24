# Cómo agregar documentos

Esta web se genera con [MkDocs](https://www.mkdocs.org/) y el tema [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) a partir de la carpeta `docs/` del repositorio. Cada vez que se sube un cambio a la rama `main`, GitHub la vuelve a publicar sola en unos minutos.

## Estructura del repositorio

```text
01-awp/
├── *.md                     ← archivos originales (no se tocan)
├── docs/                    ← contenido de la web
│   ├── index.md             ← página de inicio
│   ├── introduccion/
│   ├── guias/
│   ├── procedimientos/
│   ├── formacion/
│   ├── referencia/          ← glosario y siglas del CII
│   ├── comparaciones/
│   └── acerca/
├── includes/abreviaturas.md ← siglas que muestran su significado al pasar el ratón
├── mkdocs.yml               ← configuración y menú lateral
└── .github/workflows/publicar-web.yml ← publicación automática
```

## Agregar un documento nuevo

1. **Copia el archivo `.md`** en la carpeta de `docs/` del tema que corresponda. Usa un nombre corto, en minúsculas y sin espacios ni tildes; por ejemplo, `docs/formacion/taller-awp-2026.md`.
2. **Pon un título en la primera línea** con un solo `#`:

    ```markdown
    # Taller de AWP 2026
    ```

    Si el documento ya tiene otros títulos con `#`, cámbialos a `##` para que haya un único título principal.

3. **Agrégalo al menú** en `mkdocs.yml`, dentro de la sección `nav:` que corresponda:

    ```yaml
      - Formación (CII):
          - Introducción a AWP (CII): formacion/education-primer.md
          - Taller de AWP 2026: formacion/taller-awp-2026.md   # ← línea nueva
    ```

    El texto antes de `:` es lo que se ve en el menú lateral. La ruta se escribe sin `docs/`.

4. **Sube los cambios a `main`** (con un commit desde GitHub o desde tu equipo). La publicación se ve en la pestaña **Actions** del repositorio y tarda de 1 a 3 minutos.

!!! tip "Crear un tema nuevo"
    Si el documento no encaja en ningún tema, crea una carpeta nueva dentro de `docs/` y añade un grupo nuevo en `nav:` con el mismo formato que los demás.

!!! warning "Si el menú no incluye el documento"
    La web se construye en modo estricto: si un archivo de `docs/` no está en `nav:`, o si un enlace apunta a una página que no existe, la publicación falla y la web anterior sigue en línea. El error aparece en la pestaña **Actions**.

## Documentos en inglés

Las páginas de esta web se publican en español. Si el documento nuevo está en inglés:

- Traduce **solo la copia** que está en `docs/`; el archivo original de la raíz no se modifica.
- Mantén las siglas técnicas en inglés (AWP, CWP, IWP, EWP, IFC, RFI…). La primera vez que aparezca cada una en el documento, añade entre paréntesis su nombre completo en inglés y en español; por ejemplo: CWP (*Construction Work Package*, paquete de trabajo de construcción).
- Usa la terminología del [glosario](../referencia/glosario.md), en especial su tabla de equivalencias, para que todos los documentos digan lo mismo de la misma forma.
- Si el documento cita textualmente a otra organización (por ejemplo, una definición del CII), tradúcela también e indica que es una traducción.
- Indica en el recuadro “Documento fuente” del inicio de la página que es una traducción y de qué archivo proviene.

## Agregar siglas al glosario

- Para que una sigla muestre su significado al pasar el ratón en todas las páginas, añade una línea en `includes/abreviaturas.md`:

    ```markdown
    *[SIGLA]: Significado de la sigla
    ```

- Para que aparezca en la página del glosario, añade una fila a la tabla que corresponda en `docs/referencia/glosario.md`.

## Consejos de formato

- Deja una **línea en blanco** antes y después de cada tabla y de cada lista, o no se verán bien.
- Los saltos de línea simples se respetan (útil para textos copiados de PDF).
- Para enlazar otra página de la web, usa la ruta relativa al archivo, por ejemplo `[glosario](../referencia/glosario.md)`.

## Revisar la web en tu equipo (opcional)

Con Python instalado:

```bash
pip install -r requirements.txt
mkdocs serve
```

La web se abre en <http://127.0.0.1:8000> y se actualiza sola al guardar cambios. Para comprobar que no hay errores ni enlaces rotos, igual que hace GitHub:

```bash
mkdocs build --strict
```
