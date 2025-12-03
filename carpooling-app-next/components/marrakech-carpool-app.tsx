"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import dynamic from "next/dynamic"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Car, User, Navigation, Play, RotateCcw, Trash2, Target, Loader2 } from "lucide-react"
import { type Passenger, type Driver, type RouteStop, solveAssignment } from "@/lib/routing-algorithm"

const LeafletMap = dynamic(() => import("./leaflet-map"), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-secondary">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
        <p className="text-muted-foreground">Loading map...</p>
      </div>
    </div>
  ),
})

type PlacementMode = "pickup" | "destination" | null

export default function MarrakechCarpoolApp() {
  const [driver, setDriver] = useState<Driver | null>(null)
  const [passengers, setPassengers] = useState<Passenger[]>([])
  const [capacity, setCapacity] = useState(4)
  const [mode, setMode] = useState<PlacementMode>(null)
  const [pendingPickup, setPendingPickup] = useState<[number, number] | null>(null)
  const [route, setRoute] = useState<RouteStop[]>([])
  const [roadCoordinates, setRoadCoordinates] = useState<[number, number][]>([])
  const [segmentIndices, setSegmentIndices] = useState<number[]>([])
  const [assignedPassengers, setAssignedPassengers] = useState<Passenger[]>([])
  const [totalDistance, setTotalDistance] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [animatedPosition, setAnimatedPosition] = useState<[number, number] | null>(null)
  const [currentStopIndex, setCurrentStopIndex] = useState(0)
  const [isSolved, setIsSolved] = useState(false)
  const [isSolving, setIsSolving] = useState(false)
  const animationRef = useRef<number | null>(null)

  useEffect(() => {
    const handleMapClick = (e: CustomEvent<{ lat: number; lng: number }>) => {
      const { lat, lng } = e.detail

      if (mode === "pickup") {
        setPendingPickup([lat, lng])
        setMode("destination")
      } else if (mode === "destination" && pendingPickup) {
        const newPassenger: Passenger = {
          id: `p-${Date.now()}`,
          pickup: pendingPickup,
          destination: [lat, lng],
          name: `Passenger ${passengers.length + 1}`,
        }
        setPassengers((prev) => [...prev, newPassenger])
        setPendingPickup(null)
        setMode(null)
        setIsSolved(false)
        setRoute([])
        setRoadCoordinates([])
      }
    }

    window.addEventListener("map-click", handleMapClick as EventListener)
    return () => window.removeEventListener("map-click", handleMapClick as EventListener)
  }, [mode, pendingPickup, passengers.length])

  const handleSetDriver = (newDriver: Driver | null) => {
    setDriver(newDriver)
    setIsSolved(false)
    setRoute([])
    setRoadCoordinates([])
  }

  const handleSolve = async () => {
    if (!driver || passengers.length === 0) return

    setIsSolving(true)
    try {
      const driverWithCapacity = { ...driver, capacity }
      const result = await solveAssignment(driverWithCapacity, passengers)
      setRoute(result.route)
      setRoadCoordinates(result.roadCoordinates)
      setSegmentIndices(result.segmentIndices)
      setAssignedPassengers(result.assignedPassengers)
      setTotalDistance(result.totalDistance)
      setIsSolved(true)
      setCurrentStopIndex(0)
    } catch (error) {
      console.error("Failed to solve assignment:", error)
    } finally {
      setIsSolving(false)
    }
  }

  const handleAnimate = () => {
    if (roadCoordinates.length < 2) return

    setIsAnimating(true)
    setCurrentStopIndex(0)
    animateAlongRoad()
  }

  const animateAlongRoad = () => {
    if (roadCoordinates.length < 2) return

    let coordIndex = 0
    const totalCoords = roadCoordinates.length
    const speed = 50 // milliseconds per coordinate point

    const animate = () => {
      if (coordIndex >= totalCoords) {
        setIsAnimating(false)
        setAnimatedPosition(null)
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current)
        }
        return
      }

      setAnimatedPosition(roadCoordinates[coordIndex])

      // Update current stop index based on segment indices
      for (let i = segmentIndices.length - 1; i >= 0; i--) {
        if (coordIndex >= segmentIndices[i]) {
          setCurrentStopIndex(i)
          break
        }
      }

      coordIndex++

      setTimeout(() => {
        animationRef.current = requestAnimationFrame(animate)
      }, speed)
    }

    animationRef.current = requestAnimationFrame(animate)
  }

  const handleReset = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
    setDriver(null)
    setPassengers([])
    setRoute([])
    setRoadCoordinates([])
    setSegmentIndices([])
    setAssignedPassengers([])
    setTotalDistance(0)
    setMode(null)
    setPendingPickup(null)
    setIsAnimating(false)
    setAnimatedPosition(null)
    setIsSolved(false)
    setCurrentStopIndex(0)
  }

  const removePassenger = (id: string) => {
    setPassengers((prev) => prev.filter((p) => p.id !== id))
    setIsSolved(false)
    setRoute([])
    setRoadCoordinates([])
  }

  const getModeLabel = () => {
    switch (mode) {
      case "pickup":
        return "Click on the map to set pickup location"
      case "destination":
        return "Click on the map to set destination"
      default:
        return driver ? "Drag the car to reposition, or add passengers" : "Drag the car onto the map to place driver"
    }
  }

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData("text/plain", "driver")
    e.dataTransfer.effectAllowed = "copy"
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-80 bg-card border-r border-border p-4 flex flex-col gap-4 overflow-y-auto">
        <div className="flex items-center gap-2">
          <Car className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold text-foreground">Marrakech Carpool</h1>
        </div>

        {/* Mode indicator */}
        <Card className="bg-secondary/50">
          <CardContent className="p-3">
            <p className="text-sm text-muted-foreground">{getModeLabel()}</p>
          </CardContent>
        </Card>

        {/* Driver Section */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Car className="h-4 w-4" />
              Driver
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div
              draggable={!isAnimating}
              onDragStart={handleDragStart}
              className={`
                flex items-center justify-center gap-2 p-4 rounded-lg border-2 border-dashed 
                ${driver ? "border-primary/50 bg-primary/10" : "border-muted-foreground/30 bg-secondary/50"}
                ${!isAnimating ? "cursor-grab hover:border-primary hover:bg-primary/20 active:cursor-grabbing" : "opacity-50"}
                transition-colors
              `}
            >
              <div className="w-12 h-12 rounded-full bg-teal-600 flex items-center justify-center text-2xl shadow-lg">
                🚗
              </div>
              <div className="text-sm">
                <p className="font-medium">{driver ? "Driver placed" : "Drag me"}</p>
                <p className="text-muted-foreground text-xs">{driver ? "Drag on map to move" : "Drop on the map"}</p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Capacity: {capacity} passengers</label>
              <Slider
                value={[capacity]}
                onValueChange={(v) => {
                  setCapacity(v[0])
                  if (driver) {
                    setDriver({ ...driver, capacity: v[0] })
                  }
                }}
                min={1}
                max={6}
                step={1}
                disabled={isAnimating}
              />
            </div>

            {driver && (
              <Badge variant="secondary" className="w-full justify-center">
                Driver is on the map
              </Badge>
            )}
          </CardContent>
        </Card>

        {/* Passengers Section */}
        <Card className="flex-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <User className="h-4 w-4" />
              Passengers ({passengers.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              variant={mode === "pickup" || mode === "destination" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("pickup")}
              disabled={isAnimating}
            >
              <User className="h-4 w-4 mr-2" />
              Add Passenger
            </Button>

            {pendingPickup && (
              <Badge variant="outline" className="w-full justify-center text-green-500 border-green-500">
                Now click destination on map
              </Badge>
            )}

            <div className="space-y-2 max-h-48 overflow-y-auto">
              {passengers.map((p) => (
                <div
                  key={p.id}
                  className={`flex items-center justify-between p-2 rounded-md text-sm ${
                    assignedPassengers.some((ap) => ap.id === p.id)
                      ? "bg-primary/20 border border-primary/40"
                      : "bg-secondary/50"
                  }`}
                >
                  <span>{p.name}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => removePassenger(p.id)}
                    disabled={isAnimating}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Controls */}
        <div className="space-y-2">
          <Button
            className="w-full"
            onClick={handleSolve}
            disabled={!driver || passengers.length === 0 || isAnimating || isSolving}
          >
            {isSolving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Computing route...
              </>
            ) : (
              <>
                <Target className="h-4 w-4 mr-2" />
                Solve Assignment
              </>
            )}
          </Button>

          <Button className="w-full" variant="secondary" onClick={handleAnimate} disabled={!isSolved || isAnimating}>
            <Play className="h-4 w-4 mr-2" />
            {isAnimating ? "Animating..." : "Animate Route"}
          </Button>

          <Button className="w-full bg-transparent" variant="outline" onClick={handleReset} disabled={isAnimating}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </div>

        {/* Stats */}
        {isSolved && (
          <Card className="bg-primary/10 border-primary/30">
            <CardContent className="p-3 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Distance:</span>
                <span className="font-mono font-bold">{totalDistance.toFixed(2)} km</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Assigned:</span>
                <span className="font-mono font-bold">
                  {assignedPassengers.length}/{passengers.length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Stops:</span>
                <span className="font-mono font-bold">{route.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Road Points:</span>
                <span className="font-mono font-bold">{roadCoordinates.length}</span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        <LeafletMap
          driver={driver}
          passengers={passengers}
          pendingPickup={pendingPickup}
          route={route}
          roadCoordinates={roadCoordinates}
          assignedPassengers={assignedPassengers}
          mode={mode}
          isAnimating={isAnimating}
          animatedPosition={animatedPosition}
          currentStopIndex={currentStopIndex}
          setDriver={handleSetDriver}
          capacity={capacity}
        />

        {/* Route info overlay */}
        {isAnimating && currentStopIndex < route.length && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-card/95 backdrop-blur px-4 py-2 rounded-lg border border-border shadow-lg z-[1000]">
            <div className="flex items-center gap-2">
              <Navigation className="h-4 w-4 text-primary animate-pulse" />
              <span className="text-sm font-medium">
                {currentStopIndex === 0
                  ? "Starting from driver location"
                  : route[currentStopIndex]?.type === "pickup"
                    ? `Picked up ${route[currentStopIndex]?.passengerName}`
                    : `Dropped off ${route[currentStopIndex]?.passengerName}`}
              </span>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 right-4 bg-card/95 backdrop-blur p-3 rounded-lg border border-border z-[1000]">
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-teal-600" />
              <span>Driver</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500" />
              <span>Pickup</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500" />
              <span>Destination</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-1 bg-sky-500 rounded" />
              <span>Road Route</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
