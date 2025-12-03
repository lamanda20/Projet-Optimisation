"use client"

import dynamic from "next/dynamic"

const MarrakechCarpoolApp = dynamic(() => import("@/components/marrakech-carpool-app"), { ssr: false })

export default function Page() {
  return (
    <main className="min-h-screen bg-background">
      <MarrakechCarpoolApp />
    </main>
  )
}
