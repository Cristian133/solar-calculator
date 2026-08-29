# Calculadora Solar — Plan Técnico

Estado: **plan aprobado, sin implementación iniciada.**

## 1. Decisiones tomadas

| Decisión | Elegido | Motivo |
|---|---|---|
| Backend | Python (FastAPI) | Ecosistema científico maduro (numpy, astropy, skyfield). Consistente con `satellite-tracker`. |
| Frontend | React + TypeScript + Vite | Ecosistema de gráficos amplio (Plotly.js/Recharts/D3). Consistente con `satellite-tracker`. |
| Motor de cálculo | Python + `numpy` para vectorizar rangos (año completo, grillas) | Las fórmulas son cerradas, no iterativas ni de alto costo — un core en Rust/C sería optimización prematura. Se revisita solo si el profiling muestra un cuello de botella real (candidato futuro: grillas globales de eclipses en etapa 2). |
| Infra dev | Docker Compose | Consistente con `satellite-tracker`. Sin Postgres/Redis por ahora: la etapa 1 es *stateless* (cálculo puro sin persistencia). Se suma si etapa 3 lo requiere (cache de datos meteorológicos). |
| Precisión astronómica | Método de baja precisión de Meeus (*Astronomical Algorithms* cap. 25, error < 0.01°) | Más que suficiente para el caso de uso; VSOP87 añade complejidad de tablas sin beneficio práctico. |
| Alcance punto 5 (potencia solar) | Modelo teórico de cielo despejado (irradiancia extraterrestre + atenuación atmosférica por masa de aire) | Autocontenido, no depende de fuentes de datos externas ni adelanta la etapa 3. |
| "Mareas" (etapa 2) | Fuerzas de marea teóricas (posición relativa Sol-Luna-Tierra) | Es astronomía, encaja en el motor ya construido. Las mareas oceánicas reales (altura de marea costera) son oceanografía aplicada — dominio distinto, fuera de alcance salvo que se redefina explícitamente más adelante. |
| Mobile | Pospuesto | Web responsive alcanza por ahora; se evalúa app nativa/PWA cuando la web esté funcional. |

## 2. Fuentes de referencia

Fuente primaria (dominio de trabajo cotidiano — **no de dominio público**, uso privado de referencia para implementar código propio, ver nota de copyright abajo):

- `~/Documentos/Jean Meuss/Jean Meuss - Astronomical Algorithms 2ed.pdf`
- `~/Documentos/Jean Meuss/Jean Meuss - Mathematical Astronomy Morsels.pdf`
- `~/Documentos/Jean Meuss/Jean Meuss - More Mathematical Astronomy Morsels.pdf`
- Extracto ya elaborado: `guias-del-sol-jean-meeus.md` (solo temas del Sol — **no cubre Luna ni calendario**, ver Sección 6).

Fuentes de respaldo, para lo que Meeus no cubre (irradiancia/radiometría, refracción atmosférica detallada, mareas teóricas si se necesita mayor rigor):

- `~/Documentos/Danby, J. M. A. - Fundamentals of Celestial Mechanics, 2nd Edition.pdf`
- `~/Documentos/Davis Vallado - Methods of Astrodynamics.pdf`
- `~/Documentos/Explanatory Supplement Astronomical Almanac.pdf`

**Nota de copyright**: estos libros no son de dominio público (términos de vida+70 años vigentes). Los algoritmos/fórmulas en sí no son objeto de copyright; lo que no debe reproducirse textualmente en artefactos públicos (repo público, documentación publicada) es la prosa/tablas compiladas de los libros. Uso interno como referencia técnica: sin problema.

## 3. Estructura de carpetas propuesta

```
calculadora_solar/
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── solar/                  # motor de cálculo astronómico (puro, sin framework)
│   │   │   ├── time.py             # JD, T (siglos julianos), manejo de zona horaria
│   │   │   ├── coordinates.py      # posición solar: L0, M, C, longitud verdadera, RA/dec (Meeus cap. 25)
│   │   │   ├── horizontal.py       # transformación ecuatorial → horizontal (azimut/altitud)
│   │   │   ├── events.py           # orto, tránsito, ocaso (Meeus cap. 15)
│   │   │   ├── refraction.py       # refracción atmosférica (Meeus cap. 16)
│   │   │   └── irradiance.py       # irradiancia extraterrestre + masa de aire (fuente de respaldo, no Meeus)
│   │   ├── api/                    # routers FastAPI, uno por punto/feature
│   │   └── schemas/                # modelos Pydantic (request/response)
│   └── tests/                      # tests unitarios del motor, con casos de referencia del propio libro de Meeus
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── api/                    # cliente HTTP tipado
        ├── pages/                  # una por punto: HorasDeSol, SunPath, Mediodia, Irradiancia
        └── components/charts/      # componentes de gráficos reutilizables
```

`app/solar/` es el módulo clave: agnóstico de FastAPI, testeable de forma aislada, y es el que crece en etapas 2 y 3 sin tocar el resto.

## 4. Motor de cálculo — Etapa 1

Todos los ángulos en grados salvo que se indique lo contrario; conversión a radianes solo en el borde de las funciones trigonométricas.

### 4.1 `time.py`
- Fecha calendario → Día Juliano (JD) → siglos julianos desde J2000.0 (T).
- Manejo explícito de zona horaria del observador (input) vs. UT interno de cálculo — **crítico y fácil de hacer mal**; toda la app calcula en UT y convierte a hora local solo en la capa de presentación.

### 4.2 `coordinates.py` — posición solar (Meeus cap. 25, método de baja precisión)
- Longitud media ($L_0$), anomalía media ($M$), excentricidad orbital ($e$), ecuación del centro ($C$).
- Longitud verdadera del Sol ($\odot = L_0 + C$).
- Oblicuidad de la eclíptica ($\epsilon$) → ascensión recta ($\alpha$) y declinación ($\delta$).

### 4.3 `horizontal.py` — transformación a coordenadas horizontales
- Ángulo horario ($H$) a partir de $\alpha$, tiempo sidéreo local y longitud del observador.
- Altitud ($h$) y azimut ($A$) a partir de $H$, $\delta$, latitud ($\varphi$) — fórmulas estándar de transformación ecuatorial→horizontal (no exclusivas del cap. 25, son de la parte general de transformación de coordenadas del libro).
- Base directa de los **puntos 3 y 4** (trayectoria del sol, azimut de salida, altitud a mediodía).

### 4.4 `events.py` — orto, tránsito, ocaso (Meeus cap. 15)
- Altitud estándar $h_0 = -0.833°$ para orto/ocaso aparente.
- Algoritmo iterativo de Meeus para las horas exactas de salida, tránsito (mediodía solar) y puesta en UT.
- Base directa de los **puntos 1, 2 y 4** (horas de sol, evolución anual, hora del mediodía).

### 4.5 `refraction.py` — refracción atmosférica (Meeus cap. 16, a incorporar; no estaba en el extracto actual)
- Corrección de altitud aparente vs. verdadera cerca del horizonte. Afecta precisión de orto/ocaso.

### 4.6 `irradiance.py` — potencia solar recibida (fuente de respaldo, Meeus no lo cubre)
- Irradiancia extraterrestre (constante solar ajustada por distancia Tierra-Sol, ya tenemos $R$ del cap. 25).
- Atenuación atmosférica por masa de aire (modelo tipo Kasten-Young) en función de la altitud solar $h$.
- Integración a lo largo del día → energía por m² (punto 5), asumiendo cielo despejado.

## 5. Endpoints / features — Etapa 1

| # | Feature | Endpoint (borrador) | Módulos usados |
|---|---|---|---|
| 1 | Horas de sol en un día | `GET /sol/dia` | time, coordinates, events |
| 2 | Evolución anual de horas de sol | `GET /sol/anual` (vectorizado con numpy sobre 365 días) | + refraction |
| 3 | Trayectoria/posición de salida del sol (gráfico polar) | `GET /sol/trayectoria` | + horizontal |
| 4 | Mediodía solar + inclinación | `GET /sol/mediodia` | events, horizontal |
| 5 | Potencia recibida por m² | `GET /sol/irradiancia` | + irradiance |

## 6. Etapa 2 — trabajo previo necesario

El extracto `guias-del-sol-jean-meeus.md` está enfocado **solo en el Sol**. Para eclipses ya hay material extenso y bien cubierto. Pero **calendario lunar y Pascuas requieren una extracción nueva** de capítulos que hoy no están en ese documento:

- Posición de la Luna (cap. 47), fracción iluminada/fase (cap. 48-49) — calendario lunar.
- Cálculo de la fecha de Pascua (cap. 8) y capítulos de calendarios (cap. 7).
- Mareas teóricas: no hay capítulo dedicado exclusivo en Meeus; se apoyaría en la posición Sol-Luna ya calculada más teoría de marea gravitatoria de Danby/Vallado.

Acción sugerida cuando lleguemos a esa etapa: repetir el proceso de extracción de algoritmos (como hiciste con el Sol) para estos capítulos antes de planificar el detalle técnico de la etapa 2.

## 7. Etapa 3 — meteorología

Fuera del alcance de los libros disponibles: requiere integración con fuentes de datos externas (ej. Open-Meteo, NASA POWER) para series históricas de lluvia/nubosidad. Es trabajo de integración de datos, no de cálculo astronómico — se planifica en detalle cuando se llegue a esa etapa.

## 8. Backlog sugerido — orden de implementación Etapa 1

1. `time.py` + tests con casos de ejemplo verificados a mano/con el libro.
2. `coordinates.py` (posición solar) + tests contra ejemplos numéricos de Meeus cap. 25.
3. `events.py` (orto/tránsito/ocaso) → cierra el punto 1.
4. Endpoint + gráfica del punto 2 (vectorizado con numpy sobre el año).
5. `horizontal.py` → cierra puntos 3 y 4.
6. Gráfica polar del punto 3.
7. `refraction.py` (mejora de precisión sobre lo ya construido).
8. `irradiance.py` → cierra punto 5.
9. Revisión de estructura para confirmar que agregar etapa 2 no requiere tocar `app/solar/` existente, solo sumar módulos nuevos.

## 9. Convenciones de desarrollo

Espejo de `satellite-tracker`: pre-commit (lint + tests), CI en push, Ruff para Python, ESLint + Google TS style guide para el frontend (via skill `typescript-google-implement`).

## 10. Riesgos / pendientes abiertos

- Validar el manejo de zona horaria / horario de verano antes de construir la UI (afecta puntos 1, 2 y 4).
- Definir cómo se ingresa la ubicación (lat/lon manual vs. buscador de dirección) — no bloquea el motor de cálculo, sí a la UI.
- El modelo de irradiancia de cielo despejado (punto 5) no tiene aún una fórmula concreta seleccionada de una fuente específica — pendiente de elegir entre Danby/Vallado/Explanatory Supplement u otra referencia estándar (ej. ASHRAE clear-sky) al momento de implementar ese módulo.
