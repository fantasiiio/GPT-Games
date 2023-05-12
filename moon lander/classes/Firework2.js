class Firework2 {
    constructor(x, y, color, ctx) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.ctx = ctx;
        this.particles = [];
        this.gravity = 0.03;
        this.init();
    }

    init() {
        for (let i = 0; i < 50; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 2 + 1;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            this.particles.push({
                x: this.x,
                y: this.y,
                vx,
                vy,
                life: 1,
                size: Math.random() * 5 + 3,
                color: `hsl(${Math.random() * 360}, 100%, 50%)`
            });
        }
    }

    update() {
        for (const particle of this.particles) {
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(
                particle.x,
                particle.y,
                particle.size * particle.life,
                0,
                Math.PI * 2
            );
            this.ctx.fill();

            particle.x += particle.vx;
            particle.y += particle.vy;

            particle.vy += this.gravity;
            particle.life -= 0.015;

            if (particle.life <= 0) {
                particle.life = 0;
            }
        }

        this.particles = this.particles.filter(p => p.life > 0);
    }

    draw() {
        for (const particle of this.particles) {
            this.ctx.fillStyle = `rgba(${this.color}, ${particle.life})`;
            this.ctx.fillRect(particle.x, particle.y, 2, 2);
        }
    }

    isDone() {
        return this.particles.length === 0;
    }
}

