class Explosion {
    constructor(x, y, ctx) {
        this.x = x;
        this.y = y;
        this.ctx = ctx;
        this.pieces = [];
        this.gravity = 0.03;
        this.init();
    }

    init() {
        for (let i = 0; i < 20; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 3 + 1;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            const angularVelocity = Math.random() * 2 - 1;

            const width = Math.random() * 10 + 5;
            const height = Math.random() * 10 + 5;

            this.pieces.push({
                x: this.x,
                y: this.y,
                vx,
                vy,
                life: 5,
                width,
                height,
                rotation: 0,
                angularVelocity,
                color: 'darkgray'
            });
        }
    }

    update() {
        for (const piece of this.pieces) {
            this.ctx.fillStyle = piece.color;
            this.ctx.strokeStyle = 'black';
            this.ctx.save();
            this.ctx.translate(piece.x, piece.y);
            this.ctx.rotate((piece.rotation * Math.PI));
            this.ctx.rect(-piece.width / 2, -piece.height / 2, piece.width, piece.height);
            this.ctx.fill();
            this.ctx.stroke();
            this.ctx.restore();

            piece.x += piece.vx;
            piece.y += piece.vy;

            piece.vy += this.gravity;
            piece.life -= 0.015;

            piece.rotation += piece.angularVelocity;

            if (piece.life <= 0) {
                piece.life = 0;
            }
        }

        this.pieces = this.pieces.filter(p => p.life > 0);
    }

    isDone() {
        return this.pieces.length === 0;
    }
}