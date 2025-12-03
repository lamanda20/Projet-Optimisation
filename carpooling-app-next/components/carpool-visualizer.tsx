"use client"

import { useState, useCallback } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CityGrid } from "@/components/city-grid"
import { BipartiteGraph } from "@/components/bipartite-graph"
import { CostMatrix } from "@/components/cost-matrix"
import { AlgorithmSteps } from "@/components/algorithm-steps"
import { hungarianAlgorithm, type HungarianStep } from "@/lib/hungarian"
import { Car, MapPin, Play, RotateCcw, Plus, Trash2 } from "lucide-react"

export type Entity = {
  id: string
  x: number
  y: number
  label: string
}

export type Assignment = {
  driverId: string
  riderId: string
  cost: number
}

const GRID_SIZE = 10

function generateId() {
  return Math.random().toString(36).substring(2, 9)
}

export function CarpoolVisualizer() {
  const [drivers, setDrivers] = useState<Entity[]>([
    { id: "d1", x: 1, y: 2, label: "D1" },
    { id: "d2", x: 3, y: 7, label: "D2" },
    { id: "d3", x: 8, y: 3, label: "D3" },
  ])

  const [riders, setRiders] = useState<Entity[]>([
    { id: "r1", x: 5, y: 1, label: "R1" },
    { id: "r2", x: 2, y: 5, label: "R2" },
    { id: "r3", x: 7, y: 8, label: "R3" },
  ])

  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [algorithmSteps, setAlgorithmSteps] = useState<HungarianStep[]>([])
  const [currentStep, setCurrentStep] = useState(-1)
  const [isAnimating, setIsAnimating] = useState(false)

  const calculateCost = useCallback((d: Entity, r: Entity) => {
    return Math.abs(d.x - r.x) + Math.abs(d.y - r.y)
  }, [])

  const costMatrix = drivers.map((d) => riders.map((r) => calculateCost(d, r)))

  const totalCost = assignments.reduce((sum, a) => sum + a.cost, 0)

  const handleDragDriver = useCallback((id: string, x: number, y: number) => {
    setDrivers((prev) => prev.map((d) => (d.id === id ? { ...d, x, y } : d)))
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [])

  const handleDragRider = useCallback((id: string, x: number, y: number) => {
    setRiders((prev) => prev.map((r) => (r.id === id ? { ...r, x, y } : r)))
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [])

  const addDriver = useCallback(() => {
    const newId = generateId()
    const label = `D${drivers.length + 1}`
    setDrivers((prev) => [
      ...prev,
      { id: newId, x: Math.floor(Math.random() * GRID_SIZE), y: Math.floor(Math.random() * GRID_SIZE), label },
    ])
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [drivers.length])

  const addRider = useCallback(() => {
    const newId = generateId()
    const label = `R${riders.length + 1}`
    setRiders((prev) => [
      ...prev,
      { id: newId, x: Math.floor(Math.random() * GRID_SIZE), y: Math.floor(Math.random() * GRID_SIZE), label },
    ])
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [riders.length])

  const removeDriver = useCallback((id: string) => {
    setDrivers((prev) => prev.filter((d) => d.id !== id))
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [])

  const removeRider = useCallback((id: string) => {
    setRiders((prev) => prev.filter((r) => r.id !== id))
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
  }, [])

  const runAlgorithm = useCallback(() => {
    if (drivers.length === 0 || riders.length === 0) return

    const { assignments: result, steps } = hungarianAlgorithm(costMatrix, drivers, riders)
    setAlgorithmSteps(steps)
    setCurrentStep(0)
    setIsAnimating(true)

    let step = 0
    const interval = setInterval(() => {
      step++
      if (step >= steps.length) {
        clearInterval(interval)
        setAssignments(result)
        setCurrentStep(steps.length - 1)
        setIsAnimating(false)
      } else {
        setCurrentStep(step)
      }
    }, 800)
  }, [costMatrix, drivers, riders])

  const reset = useCallback(() => {
    setAssignments([])
    setAlgorithmSteps([])
    setCurrentStep(-1)
    setIsAnimating(false)
  }, [])

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Carpooling Assignment Problem</h1>
          <p className="text-sm text-muted-foreground">
            Visualize the Hungarian Algorithm for optimal driver-rider matching
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={runAlgorithm} disabled={isAnimating || drivers.length === 0 || riders.length === 0}>
            <Play className="mr-2 h-4 w-4" />
            Solve
          </Button>
          <Button variant="outline" onClick={reset} disabled={isAnimating}>
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset
          </Button>
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="md:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Car className="h-4 w-4 text-driver" />
              Drivers
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {drivers.map((d) => (
              <div key={d.id} className="flex items-center justify-between rounded-md bg-secondary px-3 py-2 text-sm">
                <span className="font-medium text-driver">{d.label}</span>
                <span className="text-muted-foreground">
                  ({d.x}, {d.y})
                </span>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeDriver(d.id)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
            <Button variant="outline" size="sm" className="w-full bg-transparent" onClick={addDriver}>
              <Plus className="mr-2 h-3 w-3" />
              Add Driver
            </Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <MapPin className="h-4 w-4 text-rider" />
              Riders
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {riders.map((r) => (
              <div key={r.id} className="flex items-center justify-between rounded-md bg-secondary px-3 py-2 text-sm">
                <span className="font-medium text-rider">{r.label}</span>
                <span className="text-muted-foreground">
                  ({r.x}, {r.y})
                </span>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeRider(r.id)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
            <Button variant="outline" size="sm" className="w-full bg-transparent" onClick={addRider}>
              <Plus className="mr-2 h-3 w-3" />
              Add Rider
            </Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-lg bg-secondary p-3 text-center">
                <p className="text-2xl font-bold text-driver">{drivers.length}</p>
                <p className="text-xs text-muted-foreground">Drivers</p>
              </div>
              <div className="rounded-lg bg-secondary p-3 text-center">
                <p className="text-2xl font-bold text-rider">{riders.length}</p>
                <p className="text-xs text-muted-foreground">Riders</p>
              </div>
              <div className="rounded-lg bg-secondary p-3 text-center">
                <p className="text-2xl font-bold text-primary">{assignments.length > 0 ? totalCost : "—"}</p>
                <p className="text-xs text-muted-foreground">Total Cost</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="city" className="w-full">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:grid-cols-none lg:flex">
          <TabsTrigger value="city">City Map</TabsTrigger>
          <TabsTrigger value="bipartite">Bipartite Graph</TabsTrigger>
          <TabsTrigger value="matrix">Cost Matrix</TabsTrigger>
        </TabsList>

        <TabsContent value="city" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>City Grid View</CardTitle>
              <CardDescription>
                Drag drivers and riders to reposition them. Cost is calculated using Manhattan distance.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CityGrid
                drivers={drivers}
                riders={riders}
                assignments={assignments}
                gridSize={GRID_SIZE}
                onDragDriver={handleDragDriver}
                onDragRider={handleDragRider}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bipartite" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Bipartite Graph View</CardTitle>
              <CardDescription>
                Shows all possible connections between drivers and riders with edge weights.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <BipartiteGraph drivers={drivers} riders={riders} assignments={assignments} costMatrix={costMatrix} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="matrix" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Cost Matrix</CardTitle>
              <CardDescription>
                The cost matrix showing Manhattan distance between each driver-rider pair.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CostMatrix
                drivers={drivers}
                riders={riders}
                costMatrix={costMatrix}
                assignments={assignments}
                currentStep={currentStep >= 0 ? algorithmSteps[currentStep] : undefined}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {algorithmSteps.length > 0 && <AlgorithmSteps steps={algorithmSteps} currentStep={currentStep} />}
    </div>
  )
}
