# Metodología

## Por qué existe esta página

PublicSchema formula afirmaciones sobre el significado de los datos de prestación de servicios públicos. Esas afirmaciones deben ser dignas de confianza. La confianza depende de comprender cómo se construye el esquema, qué se acelera con herramientas y qué se revisa por humanos. Esta página documenta ambos aspectos.

## Qué sintetiza PublicSchema

El modelo de referencia es el resultado de una amplia revisión de literatura, un análisis sistemático de sistemas de prestación de código abierto y una alineación con estándares internacionales.

Las fuentes incluyen:

- **Sistemas de código abierto**: openIMIS (seguro social de salud), OpenSPP (protección social), OpenCRVS (registro civil), SEMIC (interoperabilidad semántica de la UE), GovStack (bloques de construcción de gobierno digital). Los scripts de descarga y conversión de cada uno residen en `external/`.
- **Estándares internacionales**: ISO (3166 países, 4217 monedas, 639-3 idiomas, 15924 escrituras, 5218 códigos de sexo), FHIR R4, regiones UN M49, niveles educativos ISCED, credenciales verificables del W3C, SD-JWT VC.
- **Iniciativas de dominio**: DCI (Digital Convergence Initiative) para el intercambio de datos de protección social, EU Core Person Vocabulary, CPSV-AP y HSDS/Open Referral para catálogos de servicios, ILO y World Bank ASPIRE para indicadores.
- **Literatura**: literatura académica y gris sobre prestación de protección social, identidad y modelos de datos de servicios públicos.

## Dónde aporta la IA

La IA acelera la investigación y la redacción:

- **Lectura a escala.** Comparar modelos de datos entre seis o más sistemas, decenas de estándares y una amplia base de literatura sería un trabajo lento para un equipo pequeño.
- **Identificación de patrones y divergencias.** Detectar dónde los sistemas coinciden en el significado, dónde divergen y dónde existen vacíos.
- **Primeros borradores.** Primeras versiones de definiciones, listas de propiedades, conjuntos de valores de vocabulario y correspondencias entre sistemas. Los borradores son puntos de partida para la revisión humana, no el resultado final.

## Qué deciden los humanos

Cada definición de concepto, propiedad, entrada de vocabulario y correspondencia entre sistemas es revisada por un humano antes de publicarse:

- **Definiciones.** Reescritas para lograr claridad en lenguaje sencillo. Las definiciones son el producto, no un subproducto.
- **Correspondencias.** Revisadas contra los esquemas y la documentación fuente. Cada correspondencia lleva un nivel de confianza y un comentario que señala la incertidumbre.
- **Decisiones de diseño.** Las decisiones arquitectónicas (supertipos abstractos, separación entre observación y puntuación, espacios de nombres por dominio) se registran como Architecture Decision Records en `decisions/`. Cada ADR plantea la pregunta, las opciones consideradas y la justificación de la decisión.
- **Áreas sensibles.** Los temas que requieren experiencia en el dominio (definiciones legales, categorías protegidas, variaciones culturales) reciben revisión adicional antes de salir del estado borrador.

## Capas de verificación

Las afirmaciones son verificables, no solo enunciadas:

- **Indicadores de madurez.** Cada concepto, propiedad y valor de vocabulario lleva un nivel de madurez: borrador, uso experimental o normativo. Véase [Versionado y madurez](../versioning-and-maturity/). El contenido borrador está explícitamente marcado para que los lectores sepan qué sigue abierto.
- **Registros de decisiones públicos.** Toda decisión arquitectónica no trivial cuenta con un ADR en `decisions/` que documenta lo considerado y el porqué.
- **Pruebas automatizadas.** La canalización de construcción valida la estructura YAML, la integridad referencial, la completitud de las traducciones, los invariantes del grafo RDF, la exactitud de los exports y la precisión de las correspondencias contra las enumeraciones externas. Las pruebas residen en `tests/`.
- **Código abierto de extremo a extremo.** Las fuentes YAML, los scripts de construcción, los esquemas externos convertidos, las pruebas y el sitio son todos públicos. Cualquier persona puede reproducir la construcción, auditar una correspondencia o proponer un cambio.
- **Retroalimentación de la comunidad.** La retroalimentación de expertos en el dominio e implementadores de sistemas orienta lo que avanza de borrador a uso experimental y luego a normativo.

## Para qué no se usa la IA

- Aceptar contribuciones sin revisión humana.
- Promover conceptos a madurez normativa. Los compromisos de estabilidad los asumen los humanos.
- Decisiones que requieren juicio experto: definiciones legales, clasificaciones de categorías protegidas, variaciones culturales, sensibilidad de datos.
- Pasar por alto la retroalimentación de la comunidad o las preocupaciones de los adoptantes.

## Límites conocidos

- Partes del esquema siguen en madurez borrador y esperan explícitamente revisión por expertos. Están señaladas individualmente en cada página de concepto, propiedad y vocabulario.
- Algunas correspondencias entre sistemas se redactaron a partir de documentación pública en lugar de experiencia práctica con el sistema. Se busca activamente retroalimentación de los implementadores.
- La cobertura bibliográfica mejora de forma iterativa.

Si algo parece incorrecto, por favor abra una incidencia o proponga un cambio.

## Véase también

- [Principios de diseño](../design-principles/) -- la filosofía que sigue el esquema
- [Versionado y madurez](../versioning-and-maturity/) -- cómo se gana la estabilidad
- [Diseño del esquema](../schema-design/) -- reglas de nombrado, delimitación y modelado
