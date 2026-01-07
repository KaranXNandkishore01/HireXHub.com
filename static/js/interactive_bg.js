/**
 * Interactive Particle Network Background
 * Features:
 * - Responsive canvas resizing
 * - Particles that react to mouse position
 * - Connections between nearby particles
 * - Theme awareness (Dark/Light mode support)
 */

class ParticleNetwork {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };

        // Configuration
        this.config = {
            particleCount: 100, // Will be adjusted based on screen size
            connectionDistance: 120,
            baseSpeed: 0.8,
            colors: {
                dark: {
                    particle: 'rgba(102, 126, 234, 0.8)', // Light Blue
                    line: 'rgba(102, 126, 234, 0.2)'
                },
                light: {
                    particle: 'rgba(100, 100, 100, 0.5)', // Dark Grey
                    line: 'rgba(0, 0, 0, 0.05)'
                }
            }
        };

        this.init();
    }

    init() {
        this.resize();
        this.createParticles();
        this.addEventListeners();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;

        // Adjust particle count implementation for mobile/desktop
        const area = this.canvas.width * this.canvas.height;
        this.config.particleCount = Math.floor(area / 15000); // 1 particle per 15000px²
    }

    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.config.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.config.baseSpeed,
                vy: (Math.random() - 0.5) * this.config.baseSpeed,
                size: Math.random() * 2 + 1
            });
        }
    }

    addEventListeners() {
        window.addEventListener('resize', () => {
            this.resize();
            this.createParticles();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.x;
            this.mouse.y = e.y;
        });

        window.addEventListener('mouseout', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }

    getThemeColors() {
        // Check for bootstrap theme attribute on html tag
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        return isDark ? this.config.colors.dark : this.config.colors.light;
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const colors = this.getThemeColors();

        // Update and draw particles
        for (let i = 0; i < this.particles.length; i++) {
            let p = this.particles[i];

            // Movement
            p.x += p.vx;
            p.y += p.vy;

            // Bounce off edges
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            // Mouse Interaction (Antimagnetic / Repulsion)
            if (this.mouse.x != null) {
                let dx = p.x - this.mouse.x;
                let dy = p.y - this.mouse.y;
                let distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.mouse.radius) {
                    // Calculate repulsion force (stronger when closer)
                    const forceDirectionX = dx / distance;
                    const forceDirectionY = dy / distance;
                    const force = (this.mouse.radius - distance) / this.mouse.radius;

                    // Move particle AWAY from mouse
                    // Multiplier determines strength of 'magnetic field'
                    const repulsionStrength = 5;
                    const directionX = forceDirectionX * force * repulsionStrength;
                    const directionY = forceDirectionY * force * repulsionStrength;

                    p.x += directionX;
                    p.y += directionY;
                }
            }

            // Draw Particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = colors.particle;
            this.ctx.fill();

            // Connections (Between particles only)
            for (let j = i; j < this.particles.length; j++) {
                let p2 = this.particles[j];
                let dx = p.x - p2.x;
                let dy = p.y - p2.y;
                let distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.config.connectionDistance) {
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = colors.line;
                    this.ctx.lineWidth = 1;
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    new ParticleNetwork('interactive-bg');
});
