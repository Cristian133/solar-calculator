import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import HorasDeSol from './pages/HorasDeSol'
import Trayectoria from './pages/Trayectoria'
import Mediodia from './pages/Mediodia'
import Irradiancia from './pages/Irradiancia'

/** Una ruta por feature del plan técnico (sección 5): horas de sol
 * (puntos 1+2), trayectoria (punto 3), mediodía (punto 4), irradiancia
 * (punto 5). `Layout` comparte la navegación, la ubicación y la fecha. */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HorasDeSol />} />
        <Route path="trayectoria" element={<Trayectoria />} />
        <Route path="mediodia" element={<Mediodia />} />
        <Route path="irradiancia" element={<Irradiancia />} />
      </Route>
    </Routes>
  )
}
