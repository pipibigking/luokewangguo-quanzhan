<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId = 0

interface Particle {
    x: number
    y: number
    vx: number
    vy: number
    size: number
    baseAngle: number
    orbitRadius: number
    orbitSpeed: number
    spin: number
    imgIndex: number
}

const ballImages = [
    '/images/balls/暗星球.png',
    '/images/balls/变幻球.png',
    '/images/balls/捕光球.png',
    '/images/balls/调温球.png',
    '/images/balls/光合球.png',
    '/images/balls/国王球.png',
    '/images/balls/好战球.png',
    '/images/balls/绝缘球.png',
    '/images/balls/可可果球.png',
    '/images/balls/美妙球.png',
    '/images/balls/淘沙球.png',
    '/images/balls/网兜球.png',
    '/images/balls/织梦棱镜球.png'
]

function initParticles() {
    const canvas = canvasRef.value
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
        const parent = canvas.parentElement
        if (parent) {
            canvas.width = parent.offsetWidth
            canvas.height = parent.offsetHeight
        }
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const loadedImages: HTMLImageElement[] = []
    let imagesLoaded = 0

    ballImages.forEach((src, index) => {
        const img = new Image()
        img.crossOrigin = 'anonymous'
        img.onload = () => {
            imagesLoaded++
            if (imagesLoaded === ballImages.length) {
                startAnimation()
            }
        }
        img.onerror = () => {
            console.warn(`精灵球图片加载失败: ${src}`)
            imagesLoaded++
            if (imagesLoaded === ballImages.length) {
                startAnimation()
            }
        }
        img.src = src
        loadedImages[index] = img
    })

    function startAnimation() {
        const particles: Particle[] = []
        const particleCount = 50

        for (let i = 0; i < particleCount; i++) {
            const angle = Math.random() * Math.PI * 2
            const radius = Math.random() * 0.3 + 0.1
            
            particles.push({
                x: Math.random() * (canvas?.width || 0),
                y: Math.random() * (canvas?.height || 0),
                vx: 0,
                vy: 0,
                size: Math.random() * 35 + 15,
                baseAngle: angle,
                orbitRadius: radius,
                orbitSpeed: (Math.random() * 0.002 + 0.001) * (Math.random() > 0.5 ? 1 : -1),
                spin: (Math.random() - 0.5) * 0.001,
                imgIndex: Math.floor(Math.random() * 13)
            })
        }

        let mouseX = -9999
        let mouseY = -9999
        let isMouseOverCanvas = false

        const handleMouseMove = (e: MouseEvent) => {
            const rect = canvas?.getBoundingClientRect()
            if (!rect) return
            
            const x = e.clientX - rect.left
            const y = e.clientY - rect.top
            
            if (x >= 0 && x <= (canvas?.width || 0) && y >= 0 && y <= (canvas?.height || 0)) {
                mouseX = x
                mouseY = y
                isMouseOverCanvas = true
            } else {
                isMouseOverCanvas = false
            }
        }

        const handleMouseLeave = () => {
            isMouseOverCanvas = false
        }

        window.addEventListener('mousemove', handleMouseMove)
        canvas?.addEventListener('mouseleave', handleMouseLeave)

        function animate() {
            if (!ctx || !canvas) return
            ctx.clearRect(0, 0, canvas.width, canvas.height)

            for (const p of particles) {
                p.baseAngle += p.orbitSpeed

                const orbitX = Math.cos(p.baseAngle) * p.orbitRadius
                const orbitY = Math.sin(p.baseAngle) * p.orbitRadius

                p.x += orbitX
                p.y += orbitY

                if (isMouseOverCanvas) {
                    const dx = mouseX - p.x
                    const dy = mouseY - p.y
                    const dist = Math.sqrt(dx * dx + dy * dy)

                    if (dist < 350 && dist > 20) {
                        const force = (350 - dist) / 350
                        const attractionStrength = 0.05
                        p.vx += (dx / dist) * force * attractionStrength
                        p.vy += (dy / dist) * force * attractionStrength
                    }
                }

                p.vx *= 0.95
                p.vy *= 0.95

                p.x += p.vx
                p.y += p.vy

                if (p.x < -p.size) {
                    p.x = canvas.width + p.size
                    p.baseAngle = Math.random() * Math.PI * 2
                }
                if (p.x > canvas.width + p.size) {
                    p.x = -p.size
                    p.baseAngle = Math.random() * Math.PI * 2
                }
                if (p.y < -p.size) {
                    p.y = canvas.height + p.size
                    p.baseAngle = Math.random() * Math.PI * 2
                }
                if (p.y > canvas.height + p.size) {
                    p.y = -p.size
                    p.baseAngle = Math.random() * Math.PI * 2
                }

                p.baseAngle += p.spin

                const img = loadedImages[p.imgIndex]
                if (img && img.complete && img.naturalWidth > 0) {
                    ctx.save()
                    ctx.globalAlpha = 1.0
                    ctx.translate(p.x, p.y)
                    ctx.rotate(p.baseAngle * 0.1)

                    const drawSize = p.size

                    ctx.drawImage(
                        img,
                        -drawSize / 2,
                        -drawSize / 2,
                        drawSize,
                        drawSize
                    )
                    ctx.restore()
                }
            }

            animationId = requestAnimationFrame(animate)
        }

        animate()

        return () => {
            window.removeEventListener('resize', resizeCanvas)
            window.removeEventListener('mousemove', handleMouseMove)
            canvas?.removeEventListener('mouseleave', handleMouseLeave)
            cancelAnimationFrame(animationId)
        }
    }

    return () => {
        window.removeEventListener('resize', () => {})
        cancelAnimationFrame(animationId)
    }
}

onMounted(() => {
    const cleanup = initParticles()
    onUnmounted(() => {
        if (cleanup) cleanup()
    })
})
</script>

<template>
    <canvas ref="canvasRef" class="header-particles-canvas"></canvas>
</template>

<style scoped>
.header-particles-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: auto;
    z-index: 1;
}
</style>
