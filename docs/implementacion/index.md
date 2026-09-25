# Plan de implementación de AWP

!!! info "Sobre este plan"
    Este plan forma parte del **kit de implementación de AWP** del repositorio. Se aplica a un **proyecto tipo** de construcción ejecutado en tres fases y se apoya en los documentos fuente publicados en esta web. El mismo contenido está disponible como documento Word en la página [Plantillas descargables](plantillas.md).

## Convenciones del plan

Para evitar confusiones, en todo el kit se usan siempre dos términos distintos:

| Término | Significado | Valores |
|---|---|---|
| **Fase del proyecto** | Cada una de las partes en que se divide la ejecución del proyecto tipo. Pueden superponerse en el tiempo. | Fase 1, Fase 2 y Fase 3 |
| **Etapa del ciclo de vida** | Cada etapa por la que pasa el trabajo de una fase, desde la definición hasta la entrega. | Planificación temprana (FEL), ingeniería, procura, construcción y comisionamiento |

Cada fase del proyecto recorre todas las etapas del ciclo de vida. Por eso el plan explica primero **qué se hace en cada etapa** y después **cómo se aplica en cada fase**.

Las siglas técnicas se mantienen en inglés (AWP, CWA, CWP, EWP, PWP, IWP, WFP, PoC, etc.). Su significado aparece al pasar el ratón sobre ellas y en el [glosario](../referencia/glosario.md).

## Objetivo

Implementar **Advanced Work Packaging (AWP)** en el proyecto tipo para que la **secuencia de construcción dirija** la ingeniería, la procura y la ejecución en campo, de modo que cada cuadrilla reciba paquetes de trabajo **libres de restricciones** y la productividad mejore de forma medible de una fase a la siguiente.

Objetivos específicos:

1. Definir las áreas de trabajo (CWA) y el Path of Construction de cada fase antes de iniciar la ingeniería de detalle.
2. Alinear los paquetes de ingeniería (EWP) y de procura (PWP) con los paquetes de construcción (CWP), en el orden que requiere construcción.
3. Liberar a campo solo IWP sin restricciones abiertas, con un backlog de 2 a 4 semanas de trabajo listo.
4. Medir con los mismos indicadores en las tres fases y usar las lecciones aprendidas de cada fase para mejorar la siguiente.
5. Dejar al equipo del proyecto con procedimientos, plantillas y roles AWP que puedan reutilizarse en otros proyectos.

## Alcance

El plan cubre:

- Las **tres fases del proyecto** tipo y sus interfaces.
- Las **cinco etapas del ciclo de vida**: planificación temprana (FEL), ingeniería, procura, construcción y comisionamiento.
- A todos los participantes: cliente, contratista principal (ingeniería, procura y construcción), proveedores y subcontratistas.
- Los tres procesos de AWP descritos por Insight-AWP: **AWP** (alineación de paquetes), **Workface Planning** (WFP, planificación del frente de trabajo) e **Information Management** (IM, gestión de la información).

No cubre la selección comercial de software ni el diseño detallado del modelo 3D, que se tratan en el [procedimiento 2.0 de gestión de la información](../procedimientos/2-information-management.md).

## Beneficios esperados

Las fuentes del repositorio coinciden en los beneficios de AWP cuando se aplica de forma completa:

| Beneficio | Valor de referencia | Fuente |
|---|---|---|
| Productividad en campo | Hasta **+25 %** | CII (RT-272 y RT-319), guías de inicio rápido |
| Costo total instalado (TIC) | Cerca de **−10 %** | CII, Omega 365 |
| Tiempo productivo (*tool time*) | De **37 %** a **46–47 %** de la jornada | Introducción y marco educativo del CII, curso 2023 |
| Previsibilidad | Mejor cumplimiento del cronograma (SPI) y del costo (CPI) | Marco educativo del CII |
| Seguridad y calidad | Menos improvisación en campo y menos retrabajo | Education Primer, AWP y Lean Construction |

Para el proyecto tipo se fijan metas **progresivas**, porque la primera fase es también la fase de aprendizaje:

| Indicador | Línea base (sin AWP) | Meta Fase 1 | Meta Fase 2 | Meta Fase 3 |
|---|---|---|---|---|
| Tiempo productivo (*tool time*) | 37 % | 40 % | 44 % | 46 % |
| Mejora del factor de productividad | — | +5 % | +12 % | +18 % |
| IWP liberados sin restricciones | — | ≥ 85 % | ≥ 95 % | ≥ 98 % |

El detalle de todos los indicadores está en [Indicadores (KPI)](kpi.md).

## Estructura del plan

| Sección | Contenido |
|---|---|
| [Proyecto tipo y sus fases](proyecto-tipo.md) | Supuestos del caso: alcance, disciplinas, organización, duración y relación entre fases. |
| [Etapas del ciclo de vida](etapas-ciclo-de-vida.md) | Actividades AWP en cada etapa, de FEL a comisionamiento. |
| [Aplicación por fase del proyecto](aplicacion-por-fase.md) | Qué se implementa en cada fase, cómo se escala y cómo se gestionan las interfaces. |
| [Hitos por fase](hitos.md) | Hitos clave y criterios de cumplimiento. |
| [Organización y roles](organizacion.md) | Roles AWP y responsabilidades. |
| [Flujo de paquetes](flujo-paquetes.md) | CWA → CWP → EWP / PWP → IWP con ejemplos del proyecto tipo. |
| [Restricciones y liberación de IWP](restricciones-liberacion.md) | Gestión de restricciones y proceso de liberación. |
| [Riesgos de implementación](riesgos.md) | Riesgos, probabilidad, impacto, mitigación y responsable. |
| [Indicadores (KPI)](kpi.md) | Indicadores comparables entre fases. |
| [Lecciones aprendidas entre fases](lecciones-aprendidas.md) | Cómo se capturan y transfieren las lecciones. |
| [Cronograma de implementación](cronograma.md) | Cronograma resumido por fase. |
| [Referencias](referencias.md) | Documentos fuente del repositorio. |
| [Plantillas descargables](plantillas.md) | Plantillas Excel y Word del kit. |
