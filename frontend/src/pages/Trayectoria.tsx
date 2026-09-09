import { useEffect, useState } from 'react'
import { ApiError, getTrajectory } from '../api/client'
import type { TrajectoryResponse } from '../api/types'
import { useLocation } from '../context/LocationContext'
import { useDate } from '../context/DateContext'
import { SunPathChart } from '../components/charts/SunPathChart'

/** Trayectoria/posición del sol (punto 3), como gráfico polar. */
export default function Trayectoria() {
  const { location } = useLocation()
  const { date } = useDate()
  const [data, setData] = useState<TrajectoryResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!location) return
    setError(null)
    getTrajectory({ latitude: location.latitude, longitude: location.longitude, date })
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : 'No se pudo calcular la trayectoria.')
      })
  }, [location, date])

  if (!location) return null

  return (
    <div>
      <h1 style={{ marginBottom: '0.25rem' }}>Trayectoria solar</h1>
      <p style={{ color: 'var(--text-secondary)', marginTop: 0 }}>{location.displayName}</p>
      <p style={{ margin: '0 0 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Posición del sol a lo largo del día: el centro es el cenit (90° de altitud), el borde es
        el horizonte. Pasá el mouse sobre la curva para ver hora, altitud y dirección.
      </p>

      {error && <p style={{ color: 'var(--series-2)' }}>{error}</p>}
      {data && <SunPathChart data={data} timezone={location.timezone} />}
    </div>
  )
}
