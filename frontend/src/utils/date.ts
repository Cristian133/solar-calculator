export function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

/** Formatea un instante (ISO, en UT) en la hora local del lugar
 * consultado — no la del navegador, que puede ser una zona horaria
 * distinta a la del lugar. */
export function formatTime(iso: string, timezone: string): string {
  return new Date(iso).toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: timezone,
  })
}
