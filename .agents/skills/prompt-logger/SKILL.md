---
name: prompt-logger
description: |
  Estandariza la documentación compacta de interacciones con IA en prompt.md.
  Registra milestones, decisiones, validaciones, correcciones y resultados relevantes
  para la evaluación del curso, evitando transcripciones extensas o repetitivas.
  No documenta microacciones, logs completos ni cambios sin valor evaluativo.
version: 1.0.0
---

# Prompt Logger

Esta skill estandariza la documentación de interacciones con IA en `prompt.md`.

Su función no es transcribir toda la conversación.
Su función es **registrar evidencia evaluable, compacta y verificable** sobre el uso de IA durante el desarrollo.

---

## Objetivo

Asegurar que cada interacción relevante con IA:

* quede documentada de forma breve y útil;
* evidencie el prompt utilizado;
* muestre qué funcionó y qué no funcionó;
* registre decisiones técnicas o de alcance;
* incluya validaciones ejecutadas cuando existan;
* no convierta `prompt.md` en una transcripción extensa;
* aporte valor directo a la rúbrica del curso.

---

## Principio rector

**Documentar evidencia de criterio, no volumen de conversación.**

`prompt.md` debe demostrar cómo se usó la IA para planificar, iterar, corregir y validar el trabajo.
No debe convertirse en un historial completo de cada mensaje, comando o salida de terminal.

---

## No usar cuando

No usar esta skill en estos casos:

1. microacciones sin impacto evaluativo;
2. comandos exploratorios menores;
3. salidas de terminal sin conclusión relevante;
4. cambios cosméticos;
5. ajustes triviales que no afectan arquitectura, pruebas, funcionalidad o decisiones;
6. prompts repetidos sin nuevo aprendizaje;
7. debugging sin resultado útil;
8. modificaciones ya suficientemente documentadas en una entrada previa;
9. acciones automáticas que no requirieron criterio humano;
10. cambios que no aportan evidencia para la rúbrica del curso.

Si existe duda razonable entre documentar o no, esta skill debe preferir **no documentar** hasta que el valor evaluativo sea claro.

---

## Modelo documental

Esta skill opera sobre un único documento principal:

1. **prompt.md**
   Bitácora evaluativa de interacciones con IA.

El documento debe registrar:

* prompts relevantes;
* objetivos de cada interacción;
* resultados obtenidos;
* errores o límites detectados;
* correcciones aplicadas;
* decisiones tomadas;
* comandos de validación y resultados resumidos.

---

## Modo de operación obligatorio

Esta skill puede actualizar `prompt.md` solo en estos casos:

1. cuando el usuario lo solicite explícitamente;
2. cuando el prompt del milestone incluya una instrucción clara de documentar al finalizar;
3. cuando se complete una etapa relevante y exista valor evaluativo claro.

Si la documentación no fue solicitada explícitamente, la skill debe primero proponer la entrada y pedir confirmación.

La skill siempre debe:

1. identificar si la interacción tiene valor evaluativo;
2. clasificar el tipo de interacción;
3. redactar una entrada compacta;
4. evitar repetición de contexto ya documentado;
5. registrar validaciones solo de forma resumida;
6. no inventar prompts, resultados, archivos, comandos ni decisiones;
7. no hacer commits automáticamente.

---

## Flujo obligatorio

### Paso 1: determinar si debe documentarse

Antes de actualizar `prompt.md`, la skill debe responder internamente estas preguntas:

1. ¿La interacción corresponde a un milestone?
2. ¿Se tomó una decisión técnica o de alcance?
3. ¿Se modificaron archivos relevantes?
4. ¿Se agregaron o ajustaron tests?
5. ¿Se ejecutaron validaciones importantes?
6. ¿Hubo error, corrección o iteración significativa?
7. ¿La entrada ayudará a evidenciar creatividad, eficacia, calidad o corrección?
8. ¿La información ya está documentada suficientemente?

Si la interacción no deja evidencia útil para evaluación, no debe registrarse.

---

### Paso 2: clasificar la interacción

La skill debe clasificar la interacción en una o varias de estas categorías:

* diagnóstico
* planificación
* milestone
* refactor
* pruebas
* corrección
* validación
* documentación
* decisión de alcance
* cierre de calidad

No debe usar categorías innecesarias.

---

### Paso 3: determinar el nivel de detalle

La skill debe elegir uno de estos niveles:

* **mínimo:** entrada de 5 a 8 líneas para acciones simples;
* **normal:** entrada de 8 a 15 líneas para milestones o cambios relevantes;
* **ampliado:** entrada de hasta 25 líneas solo si hubo error importante, corrección compleja o decisión arquitectónica relevante.

La regla general es usar nivel **normal**.

---

### Paso 4: actualizar prompt.md

Al actualizar `prompt.md`, la skill debe:

1. leer la última interacción documentada;
2. continuar la numeración;
3. agregar la nueva entrada al final;
4. mantener formato consistente;
5. no reescribir entradas anteriores salvo solicitud expresa;
6. no insertar logs extensos;
7. no duplicar README.md, AGENT.md ni contexto base;
8. indicar si no hubo archivos modificados.

---

## Salida esperada

Después de aplicar la skill, la respuesta al usuario debe incluir:

1. número de interacción agregada;
2. título breve de la entrada;
3. resumen de lo registrado;
4. advertencia breve si quedó algo pendiente de validar.

No debe pegar todo el contenido de `prompt.md` salvo que el usuario lo pida.

---

## Formato obligatorio para prompt.md

Usar este formato o uno equivalente con el mismo nivel de brevedad:

```markdown
## Interacción X - Milestone N: Título breve

Tipo: [categoría]
Alcance: [diagnóstico / implementación / corrección / validación / documentación]
Archivos: [lista breve o "sin cambios de archivos"]

Prompt:
[prompt real enviado o síntesis fiel si fue demasiado largo]

Resultado:
[1–3 líneas]

Qué funcionó:
[1–2 líneas]

Qué no funcionó / corrección:
[1–2 líneas o "No aplica"]

Validación:
[comandos y resultados resumidos, o "No ejecutada en esta interacción"]

Decisión:
[1 línea]
```

---

## Reglas de oro

### 1. No transcribir conversaciones completas

La skill no debe copiar diálogos extensos, razonamientos internos ni salidas completas de herramientas.

Debe registrar una síntesis fiel y evaluable.

---

### 2. No repetir contexto base

Si el README.md, AGENT.md, reglas de arquitectura o alcance ya fueron documentados en una interacción anterior, no deben repetirse.

Usar referencias breves como:

* “según contexto base”;
* “respetando AGENT.md”;
* “manteniendo el alcance aprobado”;
* “según milestones definidos”.

---

### 3. Documentar iteración real

La skill debe mostrar cuando hubo corrección o ajuste.

Ejemplos:

* La IA propuso implementar base de datos, pero se corrigió el alcance para mantener repositorios en memoria.
* La primera solución mezcló lógica HTTP en services y se pidió moverla a api.
* La cobertura quedó bajo 80% y se pidió agregar tests específicos.
* Ruff detectó errores y se corrigieron.

Si no hubo error, debe indicarse brevemente:

* “No aplica”.
* “No se detectaron fallos en esta interacción”.

---

### 4. Registrar validaciones de forma resumida

No copiar salidas completas de terminal.

Preferir:

* `pytest -v`: 12 passed.
* `pytest --cov=src`: cobertura 84%.
* `ruff check src test`: sin errores.
* `ty check src test`: sin errores.
* `git status --short`: limpio.

Si una validación falló:

* indicar comando;
* resumir el fallo;
* registrar corrección o pendiente.

---

### 5. Mantener trazabilidad mínima

Cuando existan, incluir:

* archivos creados o modificados;
* comandos ejecutados;
* resultado de pruebas;
* decisión tomada;
* milestone asociado.

Si no existen, no inventarlos.

---

### 6. No sobredocumentar

No registrar cada micro-prompt.

Agrupar en una sola entrada cuando varias interacciones cortas pertenezcan al mismo objetivo.

Ejemplo:

* No crear 5 entradas para corregir 5 errores menores de Ruff.
* Crear una entrada: “Corrección de lint y formato”.

---

### 7. No sustituir criterio humano

La skill puede proponer o escribir una entrada compacta, pero debe reflejar fielmente lo ocurrido.

Si falta información, debe preguntar antes de documentar.

---

## Criterios de evaluación que debe proteger

Toda entrada debe aportar evidencia para al menos uno de estos criterios:

1. **Creatividad en los prompts:** descomposición del problema en pasos manejables.
2. **Eficacia de las indicaciones:** claridad, restricciones, ejemplos y contexto.
3. **Calidad del código final:** arquitectura, tests, lint, tipos y cobertura.
4. **Iteración y corrección:** detección de errores de IA y ajuste del rumbo.

Si una entrada no aporta a ninguno de esos criterios, probablemente no debe documentarse.

---

## Especificación por tipo de interacción

### Diagnóstico

Registrar cuando se analice el estado del proyecto o se identifiquen deudas relevantes.

Debe incluir:

* qué se pidió analizar;
* principales hallazgos;
* decisión tomada;
* si hubo o no modificación de archivos.

---

### Planificación

Registrar cuando se definan milestones, alcance, estrategia de refactorización o reparto de trabajo.

Debe incluir:

* objetivo de la planificación;
* milestones o estrategia resumida;
* restricciones aprobadas;
* decisiones de alcance.

---

### Milestone

Registrar cuando se complete una etapa de trabajo.

Debe incluir:

* milestone asociado;
* archivos modificados;
* resultado funcional o técnico;
* validaciones ejecutadas;
* errores o correcciones relevantes.

---

### Pruebas

Registrar cuando se creen, ajusten o ejecuten tests significativos.

Debe incluir:

* tipo de test: unitario, integración, caracterización o cobertura;
* capa afectada;
* resultado resumido;
* decisión derivada.

---

### Corrección

Registrar cuando se detecte y corrija un error importante.

Debe incluir:

* fallo detectado;
* causa resumida;
* corrección aplicada;
* validación posterior.

---

### Validación

Registrar cuando se cierre una etapa con pruebas, cobertura, linting o type checking.

Debe incluir:

* comandos ejecutados;
* resultados resumidos;
* pendientes, si existen.

---

### Decisión de alcance

Registrar cuando se acepte o rechace ampliar el alcance.

Debe incluir:

* propuesta considerada;
* decisión tomada;
* justificación breve.

---

## Antipatrones prohibidos

La skill NO debe:

* escribir entradas largas sin necesidad;
* repetir listas completas de reglas del proyecto;
* duplicar README.md o AGENT.md;
* copiar logs completos;
* inventar resultados de comandos;
* inventar archivos modificados;
* registrar microacciones irrelevantes;
* convertir `prompt.md` en diario personal;
* documentar cada mensaje de la IA;
* ocultar fallos reales;
* afirmar que una validación pasó si no se ejecutó;
* modificar código productivo;
* hacer commits;
* cambiar el alcance aprobado.

---

## Comportamiento esperado

La skill debe:

* clasificar antes de documentar;
* resumir antes que transcribir;
* registrar evidencia antes que narrativa;
* proteger la legibilidad de `prompt.md`;
* diferenciar resultados de decisiones;
* evidenciar iteración y criterio humano;
* detenerse si falta información esencial;
* mantener el documento útil para revisión docente.

---

## Ejemplo de interacción esperada

### Entrada del usuario

Usa prompt-logger para documentar el cierre del Milestone 0. Se agregaron tests de caracterización para health, menú y órdenes. `pytest -v` pasó con 9 tests.

### Respuesta esperada de la skill

Se agregará una entrada compacta en `prompt.md`:

```markdown
## Interacción 4 - Milestone 0: Tests de caracterización

Tipo: pruebas
Alcance: validación inicial
Archivos: test/integration/test_menu.py, test/integration/test_ordenes.py

Prompt:
Crear tests de caracterización para congelar el comportamiento observable del monolito antes de refactorizar.

Resultado:
Se agregaron pruebas para health, menú y órdenes, incluyendo creación de platos y cálculo de total.

Qué funcionó:
Los tests permitieron fijar el contrato observable antes de mover lógica fuera de main.py.

Qué no funcionó / corrección:
No aplica.

Validación:
`pytest -v`: 9 passed.

Decisión:
Continuar con extracción de dominio manteniendo comportamiento observable cubierto.
```

---

## Regla final

Si documentar no ayuda a demostrar criterio, iteración o validación, no se documenta.

Esta skill existe para mantener `prompt.md` como evidencia evaluativa clara, no para producir una montaña de texto.
