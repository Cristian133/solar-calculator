# Calculadora Solar

Aplicación web para calcular y visualizar fenómenos solares (horas de sol,
trayectoria del sol, mediodía solar, irradiancia recibida) a partir de la
latitud/longitud del observador y la fecha del año. Pensada como base
escalable para etapas futuras (eclipses, calendario lunar, mareas teóricas,
meteorología).

**Estado actual: solo esqueleto de proyecto, sin lógica de cálculo
implementada todavía.** Ver [`docs/plan_tecnico.md`](docs/plan_tecnico.md)
para el plan completo (arquitectura, módulos, fórmulas por feature, backlog).

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python), numpy para cálculos vectorizados |
| Frontend | React + TypeScript + Vite |
| Infra | Docker Compose |

## Getting Started

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Estructura

```
solar-calculator/
├── docs/               # plan técnico y brief original del proyecto
├── backend/            # FastAPI + motor de cálculo astronómico
└── frontend/           # React + TypeScript + Vite
```

Ver `docs/plan_tecnico.md`, sección 3, para el detalle de `backend/app/solar/`
(el motor de cálculo, agnóstico de framework) y su mapeo a fórmulas
concretas.

## Fuentes

Los algoritmos astronómicos se basan en *Astronomical Algorithms* (2nd ed.) y
*(More) Mathematical Astronomy Morsels* de Jean Meeus, con *Fundamentals of
Celestial Mechanics* (Danby), *Methods of Astrodynamics* (Vallado) y el
*Explanatory Supplement to the Astronomical Almanac* como referencias de
respaldo.
