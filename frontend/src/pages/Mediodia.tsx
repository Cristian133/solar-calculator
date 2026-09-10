import { useEffect, useState } from 'react'
import { ApiError, getSolarNoon } from '../api/client'
import type { SolarNoonResponse } from '../api/types'
import { useLocation } from '../context/LocationContext'
import { useDate } from '../context/DateContext'
import { formatTime } from '../utils/date'
import { compassLabel } from '../utils/compass'
import { Compass } from '../components/Compass'

/** Mediodía solar + inclinación (punto 4). */
export default function Mediodia() {
  const { location } = useLocation()
  const { date } = useDate()
  const [noon, setNoon] = useState<SolarNoonResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!location) return
    setError(null)
    getSolarNoon({ latitude: location.latitude, longitude: location.longitude, date })
      .then(setNoon)
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : 'No se pudo calcular el mediodía solar.')
      })
  }, [location, date])

  if (!location) return null

  return (
    <div>
      <h1 style={{ marginBottom: '0.25rem' }}>Mediodía solar</h1>
      <p style={{ color: 'var(--text-secondary)', marginTop: 0 }}>{location.displayName}</p>
      <p style={{ margin: '0 0 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Horarios en hora local del lugar ({location.timezone})
      </p>

      {error && <p style={{ color: 'var(--series-2)' }}>{error}</p>}

      {noon && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2.5rem', alignItems: 'center' }}>
          <dl style={{ display: 'grid', gap: '1.25rem', margin: 0 }}>
            <div>
              <dt style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Hora del mediodía solar
              </dt>
              <dd style={{ margin: 0, fontSize: '2rem', fontWeight: 600 }}>
                {formatTime(noon.transit, location.timezone)}
              </dd>
            </div>
            <div style={{ display: 'flex', gap: '2rem' }}>
              <div>
                <dt style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Altitud del sol</dt>
                <dd style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
                  {noon.altitude_deg.toFixed(1)}°
                </dd>
              </div>
              <div>
                <dt style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Altitud aparente
                </dt>
                <dd style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
                  {noon.apparent_altitude_deg.toFixed(1)}°
                </dd>
              </div>
            </div>
            <div>
              <dt style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Dirección del sol</dt>
              <dd style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
                {noon.azimuth_deg.toFixed(0)}° ({compassLabel(noon.azimuth_deg)})
              </dd>
            </div>
          </dl>

          <Compass azimuthDeg={noon.azimuth_deg} />
        </div>
      )}
    </div>
  )
}
