import { NavLink, Outlet } from 'react-router-dom'
import { LocationSearch } from './LocationSearch'
import { useLocation } from '../context/LocationContext'
import { useDate } from '../context/DateContext'

const NAV_ITEMS = [
  { to: '/', label: 'Horas de sol' },
  { to: '/trayectoria', label: 'Trayectoria' },
  { to: '/mediodia', label: 'Mediodía' },
  { to: '/irradiancia', label: 'Irradiancia' },
]

export function Layout() {
  const { location } = useLocation()
  const { date, setDate } = useDate()

  return (
    <div style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          borderBottom: '1px solid var(--gridline)',
          background: 'var(--surface-1)',
          padding: '0.75rem 1rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '1rem',
        }}
      >
        <strong style={{ fontSize: '1.1rem' }}>☀️ Calculadora Solar</strong>

        <nav style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              style={({ isActive }) => ({
                padding: '0.4rem 0.75rem',
                borderRadius: '0.375rem',
                textDecoration: 'none',
                color: isActive ? '#fff' : 'var(--text-primary)',
                background: isActive ? 'var(--series-1)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
              })}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Fecha</span>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              style={{
                padding: '0.4rem 0.5rem',
                borderRadius: '0.375rem',
                border: '1px solid var(--axis)',
                background: 'var(--surface-1)',
                color: 'var(--text-primary)',
              }}
            />
          </label>
          <LocationSearch />
        </div>
      </header>

      <main style={{ flex: 1, padding: '1.5rem 1rem', maxWidth: '64rem', width: '100%', margin: '0 auto' }}>
        {location ? (
          <Outlet />
        ) : (
          <p style={{ color: 'var(--text-secondary)' }}>
            Buscá una ubicación arriba para empezar (ej. "Buenos Aires, Argentina").
          </p>
        )}
      </main>
    </div>
  )
}
