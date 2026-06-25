import { useEffect, useRef } from "react"

function rgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export default function PlexusBackground({ sand, sage, olive, bark }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    let animationId
    let particles = []

    const config = {
      areaPerParticle: 12000,
      minCount: 65,
      maxCount: 110,
      linkDist: 158,
      maxLinks: 5,
      lineOpacity: 0.28,
      nodeOpacity: 0.72,
      speed: 0.16,
      margin: 24,
    }

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }

    function init() {
      const w = window.innerWidth
      const h = window.innerHeight
      const n = Math.max(
        config.minCount,
        Math.min(config.maxCount, Math.floor((w * h) / config.areaPerParticle))
      )
      particles = Array.from({ length: n }, () => ({
        x: config.margin + Math.random() * (w - config.margin * 2),
        y: config.margin + Math.random() * (h - config.margin * 2),
        vx: (Math.random() - 0.5) * config.speed,
        vy: (Math.random() - 0.5) * config.speed,
        r: 1.3 + Math.random() * 1.5,
      }))
    }

    function move(p, w, h) {
      p.x += p.vx
      p.y += p.vy
      if (p.x < config.margin || p.x > w - config.margin) {
        p.vx *= -1
        p.x = Math.max(config.margin, Math.min(w - config.margin, p.x))
      }
      if (p.y < config.margin || p.y > h - config.margin) {
        p.vy *= -1
        p.y = Math.max(config.margin, Math.min(h - config.margin, p.y))
      }
    }

    function linksFor(i) {
      const a = particles[i]
      const found = []
      for (let j = 0; j < particles.length; j++) {
        if (j === i) continue
        const b = particles[j]
        const d = Math.hypot(a.x - b.x, a.y - b.y)
        if (d < config.linkDist) found.push({ j, d })
      }
      found.sort((x, y) => x.d - y.d)
      return found.slice(0, config.maxLinks)
    }

    function draw() {
      const w = window.innerWidth
      const h = window.innerHeight

      ctx.fillStyle = sand
      ctx.fillRect(0, 0, w, h)

      for (const p of particles) move(p, w, h)

      const drawn = new Set()
      ctx.lineCap = "round"

      for (let i = 0; i < particles.length; i++) {
        const a = particles[i]
        for (const { j, d } of linksFor(i)) {
          const key = i < j ? `${i}-${j}` : `${j}-${i}`
          if (drawn.has(key)) continue
          drawn.add(key)
          const b = particles[j]
          const alpha = (1 - d / config.linkDist) * config.lineOpacity
          ctx.strokeStyle = rgba(sage, alpha)
          ctx.lineWidth = 0.8
          ctx.beginPath()
          ctx.moveTo(a.x, a.y)
          ctx.lineTo(b.x, b.y)
          ctx.stroke()
        }
      }

      for (const p of particles) {
        ctx.fillStyle = rgba(olive, config.nodeOpacity)
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fill()
      }

      animationId = requestAnimationFrame(draw)
    }

    function onResize() {
      resize()
      init()
    }

    resize()
    init()
    animationId = requestAnimationFrame(draw)
    window.addEventListener("resize", onResize)
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener("resize", onResize)
    }
  }, [sand, sage, olive, bark])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
      aria-hidden="true"
    />
  )
}
