"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { HungarianStep } from "@/lib/hungarian"
import { cn } from "@/lib/utils"
import { CheckCircle2, Circle } from "lucide-react"

type AlgorithmStepsProps = {
  steps: HungarianStep[]
  currentStep: number
}

export function AlgorithmSteps({ steps, currentStep }: AlgorithmStepsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Hungarian Algorithm Steps</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {steps.map((step, idx) => (
            <div
              key={step.step}
              className={cn(
                "flex items-start gap-3 rounded-lg p-3 transition-all",
                idx === currentStep && "bg-primary/10 border border-primary",
                idx < currentStep && "opacity-60",
              )}
            >
              {idx <= currentStep ? (
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
              ) : (
                <Circle className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
              )}
              <div>
                <p className="text-sm font-medium">Step {step.step}</p>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
