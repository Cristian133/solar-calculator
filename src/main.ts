import './style.css'
import * as SunCalc from 'suncalc'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const form = document.querySelector<HTMLFormElement>('#coords-form')!
const latInput = document.querySelector<HTMLInputElement>('#lat')!
const lngInput = document.querySelector<HTMLInputElement>('#lng')!
const sunriseEl = document.querySelector<HTMLSpanElement>('#sunrise')!
const sunsetEl = document.querySelector<HTMLSpanElement>('#sunset')!
const sunriseCanvas = document.querySelector<HTMLCanvasElement>('#sunrise-chart')!
const sunsetCanvas = document.querySelector<HTMLCanvasElement>('#sunset-chart')!
const cityForm = document.querySelector<HTMLFormElement>('#city-form')!
const cityInput = document.querySelector<HTMLInputElement>('#city')!
const cityResultsEl = document.querySelector<HTMLUListElement>('#city-results')!

let sunriseChart: Chart | null = null
let sunsetChart: Chart | null = null

interface GeocodingResult {
  name: string
  latitude: number
  longitude: number
  country: string
  admin1?: string
}

function formatTime(date: Date | null): string {
  if (!date) return 'N/D (día o noche polar)'
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function toDecimalHours(date: Date | null): number | null {
  if (!date) return null
  return date.getHours() + date.getMinutes() / 60
}

function formatDecimalHours(value: number | null): string {
  if (value === null) return 'N/D'
  const hours = Math.floor(value)
  const minutes = Math.round((value - hours) * 60)
  return `${hours}:${minutes.toString().padStart(2, '0')}`
}

function updateToday(lat: number, lng: number) {
  const times = SunCalc.getTimes(new Date(), lat, lng)
  sunriseEl.textContent = formatTime(times.sunrise)
  sunsetEl.textContent = formatTime(times.sunset)
}

function buildYearSeries(lat: number, lng: number) {
  const year = new Date().getFullYear()
  const labels: string[] = []
  const sunrise: (number | null)[] = []
  const sunset: (number | null)[] = []

  const date = new Date(year, 0, 1)
  while (date.getFullYear() === year) {
    const times = SunCalc.getTimes(date, lat, lng)
    labels.push(date.toLocaleDateString([], { day: '2-digit', month: 'short' }))
    sunrise.push(toDecimalHours(times.sunrise))
    sunset.push(toDecimalHours(times.sunset))
    date.setDate(date.getDate() + 1)
  }

  return { labels, sunrise, sunset }
}

function axisRange(values: (number | null)[]) {
  const numbers = values.filter((value): value is number => value !== null)
  return { min: Math.floor(Math.min(...numbers) - 0.5), max: Math.ceil(Math.max(...numbers) + 0.5) }
}

function renderSeriesChart(
  canvas: HTMLCanvasElement,
  existing: Chart | null,
  labels: string[],
  data: (number | null)[],
  label: string,
  color: string,
) {
  const { min, max } = axisRange(data)

  existing?.destroy()
  return new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{ label, data, borderColor: color, pointRadius: 0 }],
    },
    options: {
      animation: false,
      scales: {
        x: { ticks: { maxTicksLimit: 12 } },
        y: {
          min,
          max,
          ticks: { callback: (value) => formatDecimalHours(value as number) },
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${formatDecimalHours(context.parsed.y)}`,
          },
        },
      },
    },
  })
}

function renderChart(lat: number, lng: number) {
  const { labels, sunrise, sunset } = buildYearSeries(lat, lng)
  sunsetChart = renderSeriesChart(sunsetCanvas, sunsetChart, labels, sunset, 'Puesta del sol', '#4a67d6')
  sunriseChart = renderSeriesChart(sunriseCanvas, sunriseChart, labels, sunrise, 'Salida del sol', '#f5a623')
}

function update() {
  const lat = latInput.valueAsNumber
  const lng = lngInput.valueAsNumber
  updateToday(lat, lng)
  renderChart(lat, lng)
}

async function searchCity(name: string): Promise<GeocodingResult[]> {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(name)}&count=5&language=es`
  const response = await fetch(url)
  if (!response.ok) throw new Error('No se pudo buscar la ciudad')
  const data = await response.json()
  return data.results ?? []
}

function renderCityResults(results: GeocodingResult[]) {
  cityResultsEl.innerHTML = ''

  if (results.length === 0) {
    cityResultsEl.hidden = true
    return
  }

  for (const result of results) {
    const li = document.createElement('li')
    const location = [result.admin1, result.country].filter(Boolean).join(', ')
    li.textContent = location ? `${result.name} (${location})` : result.name
    li.addEventListener('click', () => {
      latInput.value = result.latitude.toFixed(4)
      lngInput.value = result.longitude.toFixed(4)
      cityResultsEl.hidden = true
      cityInput.value = result.name
      update()
    })
    cityResultsEl.appendChild(li)
  }

  cityResultsEl.hidden = false
}

cityForm.addEventListener('submit', async (event) => {
  event.preventDefault()
  const name = cityInput.value.trim()
  if (!name) return

  try {
    const results = await searchCity(name)
    renderCityResults(results)
  } catch (error) {
    console.error(error)
    cityResultsEl.hidden = true
  }
})

form.addEventListener('submit', (event) => {
  event.preventDefault()
  update()
})

update()
