export function createParticleBurst(button: HTMLElement, color = '#06b6d4') {
    const rect = button.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    const particleCount = 18

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('span')
        particle.style.cssText = `
            position: fixed;
            width: ${4 + Math.random() * 4}px;
            height: ${4 + Math.random() * 4}px;
            border-radius: 50%;
            background: ${color};
            pointer-events: none;
            z-index: 99999;
            left: ${centerX}px;
            top: ${centerY}px;
        `
        document.body.appendChild(particle)

        const angle = (Math.PI * 2 * i) / particleCount + (Math.random() - 0.5) * 0.5
        const distance = 40 + Math.random() * 60
        const dx = Math.cos(angle) * distance
        const dy = Math.sin(angle) * distance
        const duration = 500 + Math.random() * 300

        particle.animate([
            {
                transform: 'translate(0, 0) scale(1)',
                opacity: 1
            },
            {
                transform: `translate(${dx}px, ${dy}px) scale(0)`,
                opacity: 0
            }
        ], {
            duration,
            easing: 'cubic-bezier(0, 0.9, 0.57, 1)',
            fill: 'forwards'
        }).onfinish = () => particle.remove()
    }
}
