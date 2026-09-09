import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

export interface SelectedLocation {
  displayName: string
  latitude: number
  longitude: number
}

interface LocationContextValue {
  location: SelectedLocation | null
  setLocation: (location: SelectedLocation) => void
}

const STORAGE_KEY = 'calculadora-solar:location'

const LocationContext = createContext<LocationContextValue | null>(null)

function readStoredLocation(): SelectedLocation | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as SelectedLocation) : null
  } catch {
    return null // localStorage puede fallar (modo privado, etc.) — sin ubicación guardada
  }
}

/** Ubicación elegida por el usuario, compartida entre todas las páginas y
 * persistida en localStorage (conveniencia de este navegador, no un
 * backend — ver skill de capacidades de artifacts si algún día hiciera
 * falta compartir entre dispositivos). */
export function LocationProvider({ children }: { children: ReactNode }) {
  const [location, setLocationState] = useState<SelectedLocation | null>(readStoredLocation)

  useEffect(() => {
    if (!location) return
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(location))
    } catch {
      // Sin persistencia si localStorage no está disponible; la sesión
      // sigue funcionando igual con el estado en memoria.
    }
  }, [location])

  return (
    <LocationContext.Provider value={{ location, setLocation: setLocationState }}>
      {children}
    </LocationContext.Provider>
  )
}

export function useLocation(): LocationContextValue {
  const context = useContext(LocationContext)
  if (!context) {
    throw new Error('useLocation debe usarse dentro de <LocationProvider>')
  }
  return context
}
