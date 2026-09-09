"""Motor de cálculo astronómico: puro, sin dependencias de FastAPI.

Módulos (ver docs/plan_tecnico.md, sección 4):

- time.py: Día Juliano, siglos julianos (T), manejo de zona horaria. Hecho.
- coordinates.py: posición solar (Meeus, cap. 25, método de baja precisión).
  Hecho.
- horizontal.py: transformación ecuatorial -> horizontal (azimut/altitud).
  Pendiente.
- events.py: orto, tránsito y ocaso (Meeus, cap. 15). Hecho.
- refraction.py: refracción atmosférica (Meeus, cap. 16). Pendiente.
- irradiance.py: irradiancia de cielo despejado (fuente de respaldo, no
  Meeus). Pendiente.
"""
