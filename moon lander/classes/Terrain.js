class Terrain {
    constructor(width, height, mountainResolution, mountainHeightFactor, maxYOffset) {
        this.width = width;
        this.height = height;
        this.mountainResolution = mountainResolution;
        this.mountainHeightFactor = mountainHeightFactor;
        this.maxYOffset = maxYOffset;
        // Array to hold terrain points
        this.terrainPoints = [];
    }

    getY(x) {
        const y = (1 + Noise.perlin2(x * mountainResolution, 0)) * (canvas.height * mountainHeightFactor) + (canvas
            .height * maxYOffset);
        if (x >= platform.x && x <= platform.x + platform.width) {
            return platform.y;
        }
        return y;
    }

    isCollidingWithMountains(x, y) {
        // Logic to check collision goes here
        // For example, we can check if the given point is below the terrain:
        return y >= this.getY(x);
    }

    generateTerrain() {
        // Logic to generate terrain goes here
        // Here we generate random terrain:
        let y = this.height / 2;
        for (let x = 0; x < this.width; x++) {
            this.terrainPoints[x] = this.getY(x);
        }
    }

    draw(ctx) {
        // Drawing logic goes here
        // For example, we can draw the terrain:
        ctx.beginPath();
        ctx.moveTo(0, this.terrainPoints[0]);
        for (let x = 1; x < this.width; x++) {
            ctx.lineTo(x, this.terrainPoints[x]);
        }
        ctx.lineTo(this.width, this.height);
        ctx.lineTo(0, this.height);
        ctx.closePath();
        ctx.fillStyle = "brown";
        ctx.fill();
    }

    getTerrainSlope(posX) {
        const x = Math.round(posX);
        const currentY = this.terrainPoints[x];
        const previousY = this.terrainPoints[x - 1] || currentY; // If no previous point, use the current point
        const nextY = this.terrainPoints[x + 1] || currentY; // If no next point, use the current point
        const slope = (nextY - previousY) / (x + 1 - (x - 1));
        return slope;
      }    
}