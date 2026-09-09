import { useEffect, useRef, useState } from 'react'
import { searchLocation } from '../api/geocoding'
import type { GeocodingResult } from '../api/geocoding'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { useLocation } from '../context/LocationContext'

/** Buscador de dirección (Nominatim/OpenStreetMap) que resuelve a
 * latitud/longitud. La ubicación elegida queda compartida (ver
 * `LocationContext`) para todas las páginas. */
export function LocationSearch() {
  const { location, setLocation } = useLocation()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<GeocodingResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const debouncedQuery = useDebouncedValue(query, 400)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (debouncedQuery.trim().length < 3) {
      setResults([])
      return
    }

    const controller = new AbortController()
    setIsLoading(true)
    setError(null)

    searchLocation(debouncedQuery, controller.signal)
      .then((found) => {
        setResults(found)
        setIsOpen(true)
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === 'AbortError') return
        setError('No se pudo buscar la dirección. Probá de nuevo.')
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [debouncedQuery])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function handleSelect(result: GeocodingResult) {
    setLocation(result)
    setQuery('')
    setResults([])
    setIsOpen(false)
  }

  return (
    <div ref={containerRef} style={{ position: 'relative', minWidth: '16rem' }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setIsOpen(true)}
        placeholder={location ? location.displayName : 'Buscar una ciudad o dirección…'}
        aria-label="Buscar ubicación"
        style={{
          width: '100%',
          padding: '0.5rem 0.75rem',
          borderRadius: '0.375rem',
          border: `1px solid var(--axis)`,
          background: 'var(--surface-1)',
          color: 'var(--text-primary)',
        }}
      />

      {isOpen && (isLoading || error || results.length > 0) && (
        <ul
          role="listbox"
          style={{
            position: 'absolute',
            zIndex: 10,
            top: 'calc(100% + 0.25rem)',
            left: 0,
            right: 0,
            margin: 0,
            padding: '0.25rem',
            listStyle: 'none',
            background: 'var(--surface-1)',
            border: `1px solid var(--border)`,
            borderRadius: '0.375rem',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
            maxHeight: '16rem',
            overflowY: 'auto',
          }}
        >
          {isLoading && (
            <li style={{ padding: '0.5rem 0.75rem', color: 'var(--text-muted)' }}>Buscando…</li>
          )}
          {error && (
            <li style={{ padding: '0.5rem 0.75rem', color: 'var(--text-secondary)' }}>{error}</li>
          )}
          {!isLoading &&
            !error &&
            results.map((result) => (
              <li key={`${result.latitude},${result.longitude}`}>
                <button
                  type="button"
                  onClick={() => handleSelect(result)}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '0.5rem 0.75rem',
                    border: 'none',
                    background: 'transparent',
                    color: 'var(--text-primary)',
                    borderRadius: '0.25rem',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--gridline)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  {result.displayName}
                </button>
              </li>
            ))}
        </ul>
      )}

      <p style={{ margin: '0.25rem 0 0', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
        Datos de{' '}
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">
          OpenStreetMap
        </a>
      </p>
    </div>
  )
}
