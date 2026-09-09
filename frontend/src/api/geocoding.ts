/**
 * Buscador de direcciones vía Nominatim (OpenStreetMap) — gratuito, sin
 * API key. Uso liviano (búsqueda interactiva de un solo usuario), acorde
 * a su política de uso: https://operations.osmfoundation.org/policies/nominatim/
 * Igual, atribuir "datos de OpenStreetMap" donde se muestren resultados.
 */

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

export interface GeocodingResult {
  displayName: string
  latitude: number
  longitude: number
}

export async function searchLocation(
  query: string,
  signal?: AbortSignal,
): Promise<GeocodingResult[]> {
  if (query.trim().length < 3) return []

  const params = new URLSearchParams({
    q: query,
    format: 'jsonv2',
    limit: '5',
  })
  const response = await fetch(`${NOMINATIM_URL}?${params}`, { signal })
  if (!response.ok) {
    throw new Error(`Nominatim: ${response.statusText}`)
  }

  const results = (await response.json()) as { display_name: string; lat: string; lon: string }[]
  return results.map((r) => ({
    displayName: r.display_name,
    latitude: Number(r.lat),
    longitude: Number(r.lon),
  }))
}
