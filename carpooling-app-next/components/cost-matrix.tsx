"use client"

import type { Entity, Assignment } from "./carpool-visualizer"
import type { HungarianStep } from "@/lib/hungarian"
import { cn } from "@/lib/utils"

type CostMatrixProps = {
  drivers: Entity[]
  riders: Entity[]
  costMatrix: number[][]
  assignments: Assignment[]
  currentStep?: HungarianStep
}

export function CostMatrix({ drivers, riders, costMatrix, assignments, currentStep }: CostMatrixProps) {
  const isAssigned = (driverIdx: number, riderIdx: number) => {
    const driver = drivers[driverIdx]
    const rider = riders[riderIdx]
    if (!driver || !rider) return false
    return assignments.some((a) => a.driverId === driver.id && a.riderId === rider.id)
  }

  const displayMatrix = currentStep?.matrix ?? costMatrix

  return (
    <div className="overflow-x-auto">
      <table className="mx-auto border-collapse">
        <thead>
          <tr>
            <th className="p-2"></th>
            {riders.map((r) => (
              <th key={r.id} className="min-w-[60px] p-2 text-center text-sm font-semibold text-rider">
                {r.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {drivers.map((d, di) => (
            <tr key={d.id}>
              <td className="p-2 text-sm font-semibold text-driver">{d.label}</td>
              {riders.map((r, ri) => {
                const assigned = isAssigned(di, ri)
                const highlighted = currentStep?.highlighted?.some(([row, col]) => row === di && col === ri)
                return (
                  <td
                    key={r.id}
                    className={cn(
                      "border border-border p-2 text-center font-mono text-sm transition-all",
                      assigned && "bg-primary text-primary-foreground font-bold",
                      highlighted && !assigned && "bg-accent text-accent-foreground",
                      !assigned && !highlighted && "bg-secondary",
                    )}
                  >
                    {displayMatrix[di]?.[ri] ?? "—"}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {currentStep && (
        <p className="mt-4 text-center text-sm text-muted-foreground">
          Step {currentStep.step}: {currentStep.description}
        </p>
      )}
    </div>
  )
}
