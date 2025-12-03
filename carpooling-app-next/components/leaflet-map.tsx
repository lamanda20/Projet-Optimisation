"use client"

import { useEffect, useRef, useState } from "react"
import type { Passenger, RouteStop } from "@/lib/routing-algorithm"

interface LeafletMapProps {
  driver: { position: [number, number]; capacity: number } | null
  passengers: Passenger[]
  pendingPickup: [number, number] | null
  route: RouteStop[]
  roadCoordinates: [number, number][]
  assignedPassengers: Passenger[]
  mode: "driver" | "pickup" | "destination" | null
  isAnimating: boolean
  animatedPosition: [number, number] | null
  currentStopIndex: number
  setDriver: (driver: { position: [number, number]; capacity: number } | null) => void
  capacity: number
}

// Marrakech bounds
const MARRAKECH_CENTER: [number, number] = [31.6295, -7.9811]
const MARRAKECH_BOUNDS = {
  north: 31.68,
  south: 31.58,
  east: -7.92,
  west: -8.05,
}

declare global {
  interface Window {
    L: any
  }
}

export default function LeafletMap({
  driver,
  passengers,
  pendingPickup,
  route,
  roadCoordinates,
  mode,
  isAnimating,
  animatedPosition,
  currentStopIndex,
  setDriver,
  capacity,
}: LeafletMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])
  const polylineRef = useRef<any>(null)
  const animatedMarkerRef = useRef<any>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // ... existing code for loading Leaflet ...
  useEffect(() => {
    if (typeof window === "undefined") return

    if (window.L) {
      setIsLoaded(true)
      return
    }

    const link = document.createElement("link")
    link.rel = "stylesheet"
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    document.head.appendChild(link)

    const script = document.createElement("script")
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    script.onload = () => {
      setIsLoaded(true)
    }
    document.head.appendChild(script)
  }, [])

  // ... existing code for initializing map ...
  useEffect(() => {
    if (!isLoaded || !mapRef.current || mapInstanceRef.current) return

    const L = window.L
    const map = L.map(mapRef.current).setView(MARRAKECH_CENTER, 13)

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map)

    map.on("click", (e: any) => {
      const { lat, lng } = e.latlng
      if (
        lat >= MARRAKECH_BOUNDS.south &&
        lat <= MARRAKECH_BOUNDS.north &&
        lng >= MARRAKECH_BOUNDS.west &&
        lng <= MARRAKECH_BOUNDS.east
      ) {
        window.dispatchEvent(new CustomEvent("map-click", { detail: { lat, lng } }))
      }
    })

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [isLoaded])

  // ... existing code for drag and drop ...
  useEffect(() => {
    if (!mapRef.current || !mapInstanceRef.current) return

    const mapEl = mapRef.current
    const map = mapInstanceRef.current

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault()
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = "copy"
      }
    }

    const handleDrop = (e: DragEvent) => {
      e.preventDefault()
      const data = e.dataTransfer?.getData("text/plain")

      if (data === "driver" && map) {
        const rect = mapEl.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        const point = map.containerPointToLatLng([x, y])
        const lat = point.lat
        const lng = point.lng

        if (
          lat >= MARRAKECH_BOUNDS.south &&
          lat <= MARRAKECH_BOUNDS.north &&
          lng >= MARRAKECH_BOUNDS.west &&
          lng <= MARRAKECH_BOUNDS.east
        ) {
          setDriver({ position: [lat, lng], capacity })
        }
      }
    }

    mapEl.addEventListener("dragover", handleDragOver)
    mapEl.addEventListener("drop", handleDrop)

    return () => {
      mapEl.removeEventListener("dragover", handleDragOver)
      mapEl.removeEventListener("drop", handleDrop)
    }
  }, [isLoaded, setDriver, capacity])

  // ... existing code for markers ...
  useEffect(() => {
    if (!isLoaded || !mapInstanceRef.current) return

    const L = window.L
    const map = mapInstanceRef.current

    markersRef.current.forEach((m) => map.removeLayer(m))
    markersRef.current = []

    const createIcon = (color: string, emoji: string) => {
      return L.divIcon({
        className: "custom-marker",
        html: `<div style="
          background: ${color};
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          font-size: 16px;
        ">${emoji}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      })
    }

    if (driver) {
      const marker = L.marker(driver.position, {
        icon: createIcon("#0d9488", "🚗"),
        draggable: true,
      })
        .addTo(map)
        .bindPopup(`<strong>Driver</strong><br/>Capacity: ${driver.capacity} passengers`)

      marker.on("dragend", (e: any) => {
        const { lat, lng } = e.target.getLatLng()
        if (
          lat >= MARRAKECH_BOUNDS.south &&
          lat <= MARRAKECH_BOUNDS.north &&
          lng >= MARRAKECH_BOUNDS.west &&
          lng <= MARRAKECH_BOUNDS.east
        ) {
          setDriver({ position: [lat, lng], capacity })
        } else {
          marker.setLatLng(driver.position)
        }
      })

      markersRef.current.push(marker)
    }

    if (pendingPickup) {
      const marker = L.marker(pendingPickup, { icon: createIcon("#22c55e", "📍") })
        .addTo(map)
        .bindPopup("Pending pickup - click destination")
      markersRef.current.push(marker)
    }

    passengers.forEach((p) => {
      const pickupMarker = L.marker(p.pickup, { icon: createIcon("#22c55e", "📍") })
        .addTo(map)
        .bindPopup(`<strong>${p.name}</strong> - Pickup`)
      markersRef.current.push(pickupMarker)

      const destMarker = L.marker(p.destination, { icon: createIcon("#ef4444", "🎯") })
        .addTo(map)
        .bindPopup(`<strong>${p.name}</strong> - Destination`)
      markersRef.current.push(destMarker)
    })
  }, [isLoaded, driver, passengers, pendingPickup, setDriver, capacity])

  useEffect(() => {
    if (!isLoaded || !mapInstanceRef.current) return

    const L = window.L
    const map = mapInstanceRef.current

    if (polylineRef.current) {
      map.removeLayer(polylineRef.current)
      polylineRef.current = null
    }

    // Use roadCoordinates if available, otherwise fall back to route positions
    const pathCoords = roadCoordinates.length > 0 ? roadCoordinates : route.map((r) => r.position)

    if (pathCoords.length > 1) {
      polylineRef.current = L.polyline(pathCoords, {
        color: "#0ea5e9",
        weight: 5,
        opacity: 0.9,
        lineJoin: "round",
        lineCap: "round",
      }).addTo(map)
    }
  }, [isLoaded, route, roadCoordinates, isAnimating])

  // ... existing code for animated marker ...
  useEffect(() => {
    if (!isLoaded || !mapInstanceRef.current) return

    const L = window.L
    const map = mapInstanceRef.current

    if (animatedMarkerRef.current) {
      map.removeLayer(animatedMarkerRef.current)
      animatedMarkerRef.current = null
    }

    if (animatedPosition) {
      const carIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="
          background: #0ea5e9;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 3px solid white;
          box-shadow: 0 2px 12px rgba(14,165,233,0.5);
          font-size: 20px;
          animation: pulse 1s infinite;
        ">🚙</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      })

      let popupContent = "En route..."
      if (currentStopIndex < route.length - 1 && route[currentStopIndex + 1]) {
        const nextStop = route[currentStopIndex + 1]
        if (nextStop.type === "pickup") {
          popupContent = `Heading to pick up ${nextStop.passengerName}`
        } else if (nextStop.type === "dropoff") {
          popupContent = `Heading to drop off ${nextStop.passengerName}`
        }
      }

      animatedMarkerRef.current = L.marker(animatedPosition, { icon: carIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindPopup(popupContent)
    }
  }, [isLoaded, animatedPosition, currentStopIndex, route])

  if (!isLoaded) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-secondary">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-muted-foreground">Loading map...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        .leaflet-container {
          background: #1a1a2e;
        }
      `}</style>
      <div ref={mapRef} className="h-full w-full" />
    </>
  )
}
