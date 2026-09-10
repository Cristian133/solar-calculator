import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TooltipContentProps } from 'recharts'
import type { AnnualSunResponse } from '../../api/types'

interface ChartPoint {
  date: string
  dayLengthHours: number | null
}

function formatShortDate(iso: string): string {
  const [, month, day] = iso.split('-')
  return `${day}/${month}`
}

function CustomTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload as ChartPoint
  if (point.dayLengthHours == null) return null

  return (
    <div
      style={{
        background: 'var(--surface-1)',
        border: '1px solid var(--border)',
        borderRadius: '0.375rem',
        padding: '0.5rem 0.75rem',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
      }}
    >
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
        {formatShortDate(point.date)}
      </div>
      <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
        {point.dayLengthHours.toFixed(2)} h de sol
      </div>
    </div>
  )
}

/** Evolución anual de las horas de sol (punto 2), vía GET /sol/anual. Serie
 * única: sin leyenda (el título ya dice qué se muestra). Marca el día más
 * largo y el más corto del año (los solsticios) — la única etiqueta directa
 * que vale la pena, el resto queda en el tooltip. */
export function AnnualDayLengthChart({ data }: { data: AnnualSunResponse }) {
  const points: ChartPoint[] = data.days.map((day) => ({
    date: day.date,
    dayLengthHours: day.day_length_hours,
  }))

  const withValue = points.filter((p): p is { date: string; dayLengthHours: number } =>
    p.dayLengthHours != null,
  )
  const longest = withValue.reduce(
    (max, p) => (p.dayLengthHours > (max?.dayLengthHours ?? -Infinity) ? p : max),
    undefined as ChartPoint | undefined,
  )
  const shortest = withValue.reduce(
    (min, p) => (p.dayLengthHours < (min?.dayLengthHours ?? Infinity) ? p : min),
    undefined as ChartPoint | undefined,
  )

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={points} margin={{ top: 16, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--gridline)" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={formatShortDate}
          interval={29}
          stroke="var(--axis)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
        />
        <YAxis
          width={40}
          domain={[0, 24]}
          ticks={[0, 6, 12, 18, 24]}
          stroke="var(--axis)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          label={{
            value: 'horas de sol',
            angle: -90,
            position: 'insideLeft',
            fill: 'var(--text-muted)',
            fontSize: 12,
          }}
        />
        <Tooltip content={CustomTooltip} />
        <Area
          type="monotone"
          dataKey="dayLengthHours"
          stroke="var(--series-1)"
          strokeWidth={2}
          strokeLinecap="round"
          fill="var(--series-1)"
          fillOpacity={0.1}
          dot={false}
          activeDot={{ r: 4, fill: 'var(--series-1)', stroke: 'var(--surface-1)', strokeWidth: 2 }}
          connectNulls={false}
          isAnimationActive={false}
        />
        {longest && (
          <ReferenceDot
            x={longest.date}
            y={longest.dayLengthHours ?? undefined}
            r={4}
            fill="var(--series-1)"
            stroke="var(--surface-1)"
            strokeWidth={2}
            label={{
              value: 'día más largo',
              position: 'top',
              fill: 'var(--text-secondary)',
              fontSize: 11,
            }}
          />
        )}
        {shortest && (
          <ReferenceDot
            x={shortest.date}
            y={shortest.dayLengthHours ?? undefined}
            r={4}
            fill="var(--series-1)"
            stroke="var(--surface-1)"
            strokeWidth={2}
            label={{
              value: 'día más corto',
              position: 'bottom',
              fill: 'var(--text-secondary)',
              fontSize: 11,
            }}
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  )
}
