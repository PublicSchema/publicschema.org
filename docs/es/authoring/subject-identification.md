# Patrones de identificación del sujeto

Los registros de perfil (FunctioningProfile y SocioEconomicProfile en PublicSchema, además de subtipos humanitarios como AnthropometricProfile, FoodSecurityProfile y DwellingDamageProfile publicados en un esquema hermano) referencian a su sujeto mediante la propiedad `subject`. Tres patrones cubren el rango de escenarios de identificación en la recolección en campo.

## Patrón 1: Referencia

El sujeto es un registro Person o Group que ya existe en el sistema. El formulario almacena una referencia (identificador o URI).

**Cuándo usarlo:** encuestas vinculadas al registro, visitas de seguimiento, cualquier contexto donde los sujetos están pre-inscritos.

## Patrón 2: En línea

El sujeto se describe directamente en el registro de perfil con suficiente información de identificación para vincular posteriormente (nombre, fecha de nacimiento, ubicación). No se requiere un registro Person preexistente.

**Cuándo usarlo:** tamizaje comunitario, primer contacto de registro, recolección móvil en áreas sin inscripción previa.

## Patrón 3: Anónimo

El sujeto no se identifica. El perfil captura datos de observación sin vincularlos a un individuo nombrado.

**Cuándo usarlo:** encuestas a nivel poblacional (DHS, MICS, SMART), investigación, cualquier contexto donde la identificación individual no es necesaria.

## Elección del patrón

| Contexto | Patrón | Notas |
|---|---|---|
| Visita de seguimiento en un programa | Referencia | El sujeto debe existir antes de abrir el formulario |
| Tamizaje comunitario MUAC | En línea | Crear registro Person a partir de datos en línea después del tamizaje |
| Encuesta nutricional SMART | Anónimo | Sin seguimiento individual; los datos se agregan |
| Encuesta de registro de hogares | Referencia o En línea | Depende de si el hogar fue pre-registrado |
