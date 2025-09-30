'use client'

import { useEffect, useRef } from 'react'

interface EvalData {
  move: number
  eval: number
  mate?: number | null
  mistake: string
}

interface EvalGraphProps {
  data: EvalData[]
  currentMove?: number
}

export default function EvalGraph({ data, currentMove = 0 }: EvalGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || data.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * window.devicePixelRatio
    canvas.height = rect.height * window.devicePixelRatio
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Set up dimensions
    const padding = 20
    const width = rect.width - padding * 2
    const height = rect.height - padding * 2
    const centerY = height / 2

    // Draw axes
    ctx.strokeStyle = '#e2e8f0'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding, height + padding)
    ctx.lineTo(width + padding, height + padding)
    ctx.stroke()

    // Draw center line (0 evaluation)
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(padding, centerY + padding)
    ctx.lineTo(width + padding, centerY + padding)
    ctx.stroke()

    if (data.length === 0) return

    // Calculate step size
    const stepX = width / Math.max(data.length - 1, 1)

    // Normalize evaluation values to fit in the graph
    const maxEval = Math.max(...data.map(d => Math.abs(d.eval)), 500)
    const scaleY = centerY / maxEval

    // Draw evaluation line
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 2
    ctx.beginPath()

    data.forEach((point, index) => {
      const x = padding + index * stepX
      const y = centerY + padding - (point.eval * scaleY)
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    data.forEach((point, index) => {
      const x = padding + index * stepX
      const y = centerY + padding - (point.eval * scaleY)
      
      // Color based on mistake type
      let color = '#3b82f6'
      if (point.mistake === 'blunder') color = '#ef4444'
      else if (point.mistake === 'mistake') color = '#f97316'
      else if (point.mistake === 'inacc') color = '#eab308'
      
      // Highlight current move
      if (index === currentMove - 1) {
        ctx.fillStyle = '#1d4ed8'
        ctx.beginPath()
        ctx.arc(x, y, 6, 0, 2 * Math.PI)
        ctx.fill()
      } else {
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fill()
      }
    })

    // Draw move numbers
    ctx.fillStyle = '#64748b'
    ctx.font = '12px Inter'
    ctx.textAlign = 'center'
    
    data.forEach((point, index) => {
      const x = padding + index * stepX
      ctx.fillText(point.move.toString(), x, height + padding + 15)
    })

    // Draw evaluation labels
    ctx.fillStyle = '#64748b'
    ctx.font = '10px Inter'
    ctx.textAlign = 'right'
    
    // +5.0
    ctx.fillText('+5.0', padding - 5, centerY + padding - (500 * scaleY))
    // 0.0
    ctx.fillText('0.0', padding - 5, centerY + padding)
    // -5.0
    ctx.fillText('-5.0', padding - 5, centerY + padding - (-500 * scaleY))

  }, [data, currentMove])

  return (
    <div className="eval-graph">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ width: '100%', height: '200px' }}
      />
    </div>
  )
}

