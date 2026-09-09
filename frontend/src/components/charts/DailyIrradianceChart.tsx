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
import type { IrradianceResponse } from '../../api/types'
import { formatTime } from '../../utils/date'

interface ChartPoint {
  time: string
  power: number
}

function CustomTooltip({
  active,
  payload,
  timezone,
}: TooltipContentProps & { timezone: string }) {
  if (!active || !payload?.length) return null
  const point = payload[0].payload as ChartPoint

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
        {formatTime(point.time, timezone)}
      </div>
      <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
        {point.power.toFixed(0)} W/m²
      </div>
    </div>
  )
}

/** Irradiancia solar (cielo despejado) a lo largo de un día (punto 5).
 * Serie única: sin leyenda. Marca el pico de potencia (mediodía solar)
 * como única etiqueta directa. */
export function DailyIrradianceChart({
  data,
  timezone,
}: {
  data: IrradianceResponse
  timezone: string
}) {
  const points: ChartPoint[] = data.samples.map((s) => ({ time: s.time, power: s.power_w_per_m2 }))
  const peak = points.reduce((max, p) => (p.power > max.power ? p : max), points[0])

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={points} margin={{ top: 16, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--gridline)" vertical={false} />
        <XAxis
          dataKey="time"
          tickFormatter={(t: string) => formatTime(t, timezone)}
          interval={Math.max(Math.floor(points.length / 8) - 1, 0)}
          stroke="var(--axis)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
        />
        <YAxis
          width={48}
          domain={[0, 'auto']}
          stroke="var(--axis)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          label={{
            value: 'W/m²',
            angle: -90,
            position: 'insideLeft',
            fill: 'var(--text-muted)',
            fontSize: 12,
          }}
        />
        <Tooltip content={(props) => <CustomTooltip {...props} timezone={timezone} />} />
        <Area
          type="monotone"
          dataKey="power"
          stroke="var(--series-1)"
          strokeWidth={2}
          strokeLinecap="round"
          fill="var(--series-1)"
          fillOpacity={0.1}
          dot={false}
          activeDot={{ r: 4, fill: 'var(--series-1)', stroke: 'var(--surface-1)', strokeWidth: 2 }}
          isAnimationActive={false}
        />
        {peak.power > 0 && (
          <ReferenceDot
            x={peak.time}
            y={peak.power}
            r={4}
            fill="var(--series-1)"
            stroke="var(--surface-1)"
            strokeWidth={2}
            label={{
              value: `${peak.power.toFixed(0)} W/m² máx.`,
              position: 'top',
              fill: 'var(--text-secondary)',
              fontSize: 11,
            }}
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  )
}
