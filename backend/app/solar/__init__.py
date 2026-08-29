"""Motor de cálculo astronómico: puro, sin dependencias de FastAPI.

Módulos planificados (ver docs/plan_tecnico.md, sección 4) — todavía no
implementados:

- time.py: Día Juliano, siglos julianos (T), manejo de zona horaria.
- coordinates.py: posición solar (Meeus, cap. 25, método de baja precisión).
- horizontal.py: transformación ecuatorial -> horizontal (azimut/altitud).
- events.py: orto, tránsito y ocaso (Meeus, cap. 15).
- refraction.py: refracción atmosférica (Meeus, cap. 16).
- irradiance.py: irradiancia de cielo despejado (fuente de respaldo, no Meeus).
"""
