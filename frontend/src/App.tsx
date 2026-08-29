import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/**
 * Placeholder de arranque: solo confirma que el frontend puede hablar con
 * el backend. Las páginas reales (una por feature, ver docs/plan_tecnico.md
 * sección 5) todavía no están implementadas.
 */
export default function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ok' | 'error'>('checking')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => (res.ok ? setBackendStatus('ok') : setBackendStatus('error')))
      .catch(() => setBackendStatus('error'))
  }, [])

  return (
    <main style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>Calculadora Solar</h1>
      <p>Proyecto en construcción — ver docs/plan_tecnico.md para el plan.</p>
      <p>Backend: {backendStatus}</p>
    </main>
  )
}
