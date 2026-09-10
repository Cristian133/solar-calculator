import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { DateProvider } from './context/DateContext'
import { LocationProvider } from './context/LocationContext'
import './styles/theme.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <LocationProvider>
        <DateProvider>
          <App />
        </DateProvider>
      </LocationProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
