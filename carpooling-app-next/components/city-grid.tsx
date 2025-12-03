"use client"

import type React from "react"

import { useRef, useCallback, useState, useEffect } from "react"
import type { Entity, Assignment } from "./carpool-visualizer"
import { Car, MapPin } from "lucide-react"

type CityGridProps = {
  drivers: Entity[]
  riders: Entity[]
  assignments: Assignment[]
  gridSize: number
  onDragDriver: (id: string, x: number, y: number) => void
  onDragRider: (id: string, x: number, y: number) => void
}

export function CityGrid({ drivers, riders, assignments, gridSize, onDragDriver, onDragRider }: CityGridProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dragging, setDragging] = useState<{ type: "driver" | "rider"; id: string } | null>(null)
  const [cellSize, setCellSize] = useState(50)

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const width = containerRef.current.clientWidth
        setCellSize(Math.floor((width - 40) / gridSize))
      }
    }
    updateSize()
    window.addEventListener("resize", updateSize)
    return () => window.removeEventListener("resize", updateSize)
  }, [gridSize])

  const handleMouseDown = useCallback(
    (type: "driver" | "rider", id: string) => (e: React.MouseEvent) => {
      e.preventDefault()
      setDragging({ type, id })
    },
    [],
  )

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!dragging || !containerRef.current) return

      const rect = containerRef.current.getBoundingClientRect()
      const x = Math.max(0, Math.min(gridSize - 1, Math.floor((e.clientX - rect.left - 20) / cellSize)))
      const y = Math.max(0, Math.min(gridSize - 1, Math.floor((e.clientY - rect.top - 20) / cellSize)))

      if (dragging.type === "driver") {
        onDragDriver(dragging.id, x, y)
      } else {
        onDragRider(dragging.id, x, y)
      }
    },
    [dragging, cellSize, gridSize, onDragDriver, onDragRider],
  )

  const handleMouseUp = useCallback(() => {
    setDragging(null)
  }, [])

  const getAssignmentForDriver = (driverId: string) => assignments.find((a) => a.driverId === driverId)

  return (
    <div
      ref={containerRef}
      className="relative select-none overflow-hidden rounded-lg bg-secondary p-5"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Grid lines */}
      <svg width={cellSize * gridSize} height={cellSize * gridSize} className="absolute left-5 top-5">
        {/* Vertical lines */}
        {Array.from({ length: gridSize + 1 }).map((_, i) => (
          <line
            key={`v-${i}`}
            x1={i * cellSize}
            y1={0}
            x2={i * cellSize}
            y2={cellSize * gridSize}
            stroke="var(--grid-line)"
            strokeWidth={1}
          />
        ))}
        {/* Horizontal lines */}
        {Array.from({ length: gridSize + 1 }).map((_, i) => (
          <line
            key={`h-${i}`}
            x1={0}
            y1={i * cellSize}
            x2={cellSize * gridSize}
            y2={i * cellSize}
            stroke="var(--grid-line)"
            strokeWidth={1}
          />
        ))}

        {/* Assignment lines */}
        {assignments.map((assignment) => {
          const driver = drivers.find((d) => d.id === assignment.driverId)
          const rider = riders.find((r) => r.id === assignment.riderId)
          if (!driver || !rider) return null

          return (
            <line
              key={`${assignment.driverId}-${assignment.riderId}`}
              x1={driver.x * cellSize + cellSize / 2}
              y1={driver.y * cellSize + cellSize / 2}
              x2={rider.x * cellSize + cellSize / 2}
              y2={rider.y * cellSize + cellSize / 2}
              stroke="var(--primary)"
              strokeWidth={3}
              strokeDasharray="8,4"
              className="animate-pulse"
            />
          )
        })}
      </svg>

      {/* Entities */}
      <div className="relative" style={{ width: cellSize * gridSize, height: cellSize * gridSize }}>
        {/* Drivers */}
        {drivers.map((driver) => {
          const isAssigned = !!getAssignmentForDriver(driver.id)
          return (
            <div
              key={driver.id}
              className={`absolute flex cursor-grab items-center justify-center rounded-full border-2 transition-shadow ${
                isAssigned ? "border-primary shadow-lg shadow-primary/30" : "border-driver"
              } bg-background`}
              style={{
                left: driver.x * cellSize + cellSize / 2 - 18,
                top: driver.y * cellSize + cellSize / 2 - 18,
                width: 36,
                height: 36,
              }}
              onMouseDown={handleMouseDown("driver", driver.id)}
            >
              <Car className="h-5 w-5 text-driver" />
              <span className="absolute -bottom-5 text-xs font-medium text-driver">{driver.label}</span>
            </div>
          )
        })}

        {/* Riders */}
        {riders.map((rider) => {
          const isAssigned = assignments.some((a) => a.riderId === rider.id)
          return (
            <div
              key={rider.id}
              className={`absolute flex cursor-grab items-center justify-center rounded-full border-2 transition-shadow ${
                isAssigned ? "border-primary shadow-lg shadow-primary/30" : "border-rider"
              } bg-background`}
              style={{
                left: rider.x * cellSize + cellSize / 2 - 18,
                top: rider.y * cellSize + cellSize / 2 - 18,
                width: 36,
                height: 36,
              }}
              onMouseDown={handleMouseDown("rider", rider.id)}
            >
              <MapPin className="h-5 w-5 text-rider" />
              <span className="absolute -bottom-5 text-xs font-medium text-rider">{rider.label}</span>
            </div>
          )
        })}
      </div>

      {/* Coordinates legend */}
      <div className="absolute bottom-1 left-5 flex gap-2 text-xs text-muted-foreground">
        {Array.from({ length: gridSize }).map((_, i) => (
          <span key={i} style={{ width: cellSize }} className="text-center">
            {i}
          </span>
        ))}
      </div>
      <div className="absolute left-1 top-5 flex flex-col gap-0 text-xs text-muted-foreground">
        {Array.from({ length: gridSize }).map((_, i) => (
          <span key={i} style={{ height: cellSize }} className="flex items-center">
            {i}
          </span>
        ))}
      </div>
    </div>
  )
}
