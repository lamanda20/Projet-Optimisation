"use client"

import { useMemo } from "react"
import type { Entity, Assignment } from "./carpool-visualizer"
import { Car, MapPin } from "lucide-react"

type BipartiteGraphProps = {
  drivers: Entity[]
  riders: Entity[]
  assignments: Assignment[]
  costMatrix: number[][]
}

export function BipartiteGraph({ drivers, riders, assignments, costMatrix }: BipartiteGraphProps) {
  const height = Math.max(drivers.length, riders.length) * 80 + 60
  const width = 600

  const driverPositions = useMemo(() => {
    return drivers.map((d, i) => ({
      id: d.id,
      label: d.label,
      x: 80,
      y: 50 + i * 80,
    }))
  }, [drivers])

  const riderPositions = useMemo(() => {
    return riders.map((r, i) => ({
      id: r.id,
      label: r.label,
      x: width - 80,
      y: 50 + i * 80,
    }))
  }, [riders])

  const isAssigned = (driverId: string, riderId: string) =>
    assignments.some((a) => a.driverId === driverId && a.riderId === riderId)

  return (
    <div className="overflow-x-auto">
      <svg width={width} height={height} className="mx-auto">
        {/* All possible edges */}
        {driverPositions.map((dp, di) =>
          riderPositions.map((rp, ri) => {
            const assigned = isAssigned(dp.id, rp.id)
            return (
              <g key={`${dp.id}-${rp.id}`}>
                <line
                  x1={dp.x + 24}
                  y1={dp.y}
                  x2={rp.x - 24}
                  y2={rp.y}
                  stroke={assigned ? "var(--primary)" : "var(--border)"}
                  strokeWidth={assigned ? 3 : 1}
                  strokeDasharray={assigned ? "none" : "4,4"}
                  className={assigned ? "animate-pulse" : "opacity-40"}
                />
                <text
                  x={(dp.x + rp.x) / 2}
                  y={(dp.y + rp.y) / 2 - 6}
                  fill={assigned ? "var(--primary)" : "var(--muted-foreground)"}
                  fontSize={12}
                  textAnchor="middle"
                  className="font-mono"
                >
                  {costMatrix[di]?.[ri] ?? "?"}
                </text>
              </g>
            )
          }),
        )}

        {/* Driver nodes */}
        {driverPositions.map((dp) => (
          <g key={dp.id}>
            <circle cx={dp.x} cy={dp.y} r={24} fill="var(--background)" stroke="var(--driver)" strokeWidth={2} />
            <foreignObject x={dp.x - 12} y={dp.y - 12} width={24} height={24}>
              <div className="flex h-full w-full items-center justify-center">
                <Car className="h-5 w-5 text-driver" />
              </div>
            </foreignObject>
            <text x={dp.x - 40} y={dp.y + 4} fill="var(--driver)" fontSize={14} fontWeight={600} textAnchor="end">
              {dp.label}
            </text>
          </g>
        ))}

        {/* Rider nodes */}
        {riderPositions.map((rp) => (
          <g key={rp.id}>
            <circle cx={rp.x} cy={rp.y} r={24} fill="var(--background)" stroke="var(--rider)" strokeWidth={2} />
            <foreignObject x={rp.x - 12} y={rp.y - 12} width={24} height={24}>
              <div className="flex h-full w-full items-center justify-center">
                <MapPin className="h-5 w-5 text-rider" />
              </div>
            </foreignObject>
            <text x={rp.x + 40} y={rp.y + 4} fill="var(--rider)" fontSize={14} fontWeight={600} textAnchor="start">
              {rp.label}
            </text>
          </g>
        ))}

        {/* Labels */}
        <text x={80} y={20} fill="var(--muted-foreground)" fontSize={12} textAnchor="middle">
          Drivers
        </text>
        <text x={width - 80} y={20} fill="var(--muted-foreground)" fontSize={12} textAnchor="middle">
          Riders
        </text>
      </svg>
    </div>
  )
}
