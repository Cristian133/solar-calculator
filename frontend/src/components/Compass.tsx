const SIZE = 160
const CENTER = SIZE / 2
const RADIUS = CENTER - 24

const CARDINAL_POINTS = [
  { deg: 0, label: 'N' },
  { deg: 90, label: 'E' },
  { deg: 180, label: 'S' },
  { deg: 270, label: 'O' },
]

/** Rosa de los vientos simple: marca la dirección del sol (azimut, 0°=N
 * en sentido horario) como un rumbo desde el centro. */
export function Compass({ azimuthDeg }: { azimuthDeg: number }) {
  const rad = (azimuthDeg * Math.PI) / 180
  const x = CENTER + RADIUS * Math.sin(rad)
  const y = CENTER - RADIUS * Math.cos(rad)

  return (
    <svg
      width={SIZE}
      height={SIZE}
      viewBox={`0 0 ${SIZE} ${SIZE}`}
      role="img"
      aria-label={`Azimut del sol: ${azimuthDeg.toFixed(0)}°`}
    >
      <circle cx={CENTER} cy={CENTER} r={RADIUS} fill="none" stroke="var(--gridline)" strokeWidth={1} />

      {CARDINAL_POINTS.map(({ deg, label }) => {
        const pointRad = (deg * Math.PI) / 180
        const edgeX = CENTER + RADIUS * Math.sin(pointRad)
        const edgeY = CENTER - RADIUS * Math.cos(pointRad)
        const labelX = CENTER + (RADIUS + 14) * Math.sin(pointRad)
        const labelY = CENTER - (RADIUS + 14) * Math.cos(pointRad)
        return (
          <g key={deg}>
            <line x1={CENTER} y1={CENTER} x2={edgeX} y2={edgeY} stroke="var(--gridline)" strokeWidth={1} />
            <text
              x={labelX}
              y={labelY}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={12}
              fill="var(--text-secondary)"
            >
              {label}
            </text>
          </g>
        )
      })}

      <line x1={CENTER} y1={CENTER} x2={x} y2={y} stroke="var(--series-1)" strokeWidth={2} strokeLinecap="round" />
      <circle cx={x} cy={y} r={5} fill="var(--series-1)" stroke="var(--surface-1)" strokeWidth={2} />
    </svg>
  )
}
