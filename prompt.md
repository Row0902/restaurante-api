# prompt.md — Registro de desarrollo asistido por IA

> Proyecto: Restaurante API (refactor monolito → Clean Architecture)
> Autor: [tu nombre] · Herramienta: OpenCode + gentle-ai (perfil `gentleman`)
>
> Copiá este archivo a la raíz del repo como `prompt.md` y completalo a medida que avanzás.
> Una entrada por cada interacción con la IA. Lo que más puntúa: prompts atómicos + cómo
> corregiste cuando la IA se equivocó.

---

## Plantilla por interacción (copiá este bloque para cada prompt)

### [Fase / paso] — título corto

**Prompt enviado:**
```
(texto exacto que le escribí a la IA)
```

**Resultado / qué funcionó:**
- ...

**Qué NO funcionó:**
- ...

**Iteración / corrección:**
- Reformulé así: `...` → y entonces ...

---

## Ejemplo (borrar antes de entregar)

### Fase 2 — Diseño de la estructura objetivo

**Prompt enviado:**
```
Diseñá la estructura de archivos objetivo para llevar este monolito a Clean
Architecture (api → services → repositories → core), respetando las 15 reglas de
AGENTS.md. Mostrame solo el árbol de archivos, sin código.
```

**Resultado / qué funcionó:**
- Propuso bien las 4 capas y separó schemas de modelos.

**Qué NO funcionó:**
- Puso varias clases en `models.py`, violando la regla 3 (1 clase por archivo).

**Iteración / corrección:**
- Reformulé: "Separá cada modelo SQLModel en su propio archivo, nombre = clase en
  snake_case, según la regla 3 de AGENTS.md." → corrigió la estructura.
