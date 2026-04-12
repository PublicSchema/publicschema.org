# Principios de diseño

## 1. Semántico, no estructural

Los conceptos tienen significado. Una Persona (Person) no es un conjunto de campos; es una entidad con nombre y una definición escrita para practicantes del dominio. El problema de interoperabilidad radica en la divergencia de vocabulario: los sistemas usan nombres diferentes para las mismas entidades del mundo real, y cuando esos nombres codifican decisiones semánticas distintas, las correspondencias entre ellos pierden información. PublicSchema provee definiciones compartidas que hacen explícitas las equivalencias y preservan el significado a través de los sistemas.

## 2. Descriptivo, no normativo

Nada es obligatorio. Los sistemas adoptan los conceptos, propiedades y vocabularios que les aplican. PublicSchema describe cómo se ven los datos de prestación en todos los sistemas; no impone qué debe recopilar ningún sistema.

## 3. Basado en evidencia e incremental

Los datos de convergencia impulsan las prioridades. Una propiedad presente en 6 de 6 sistemas vale la pena estandarizar antes que una presente en 2 de 6. Comience con lo que está confirmado y extiéndalo cuando la adopción revele una necesidad genuina.

## 4. Lenguaje sencillo para practicantes

Las definiciones están escritas para responsables de políticas y gestores de programas, no para desarrolladores. "Los estados del ciclo de vida de una inscripción en un programa" es preferible a "una enumeración de códigos de estado aplicables a la entidad de registro de personas beneficiarias".

## Véase también

- [Diseño de esquema](../schema-design/): nomenclatura, alcance y modelado
- [Diseño de vocabulario](../vocabulary-design/): conjuntos de valores controlados y correspondencias de sistemas
- [Versionado y madurez](../versioning-and-maturity/): garantías de estabilidad y reglas de evolución
- [Divulgación selectiva](../selective-disclosure/): diseño de privacidad para credenciales
