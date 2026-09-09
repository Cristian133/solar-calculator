import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import HorasDeSol from './pages/HorasDeSol'
import { ComingSoon } from './pages/ComingSoon'

/** Una ruta por feature del plan técnico (sección 5): horas de sol
 * (puntos 1+2), trayectoria (punto 3), mediodía (punto 4), irradiancia
 * (punto 5). `Layout` comparte la navegación y el buscador de ubicación. */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HorasDeSol />} />
        <Route path="trayectoria" element={<ComingSoon title="Trayectoria solar" />} />
        <Route path="mediodia" element={<ComingSoon title="Mediodía solar" />} />
        <Route path="irradiancia" element={<ComingSoon title="Irradiancia" />} />
      </Route>
    </Routes>
  )
}
