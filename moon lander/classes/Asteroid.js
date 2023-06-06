class Asteroid {
    constructor(center, radius) {
        this.vertices = [];
        this.radius = radius;
        this.numSubdivisions = 2;
        this.polygon = this.generateRandomAsteroidPolygon(radius, this.numSubdivisions)
        let rectangle = this.polygon.createRectangleFromPolygon()
        this.rigidBody = new RigidBody(center.x, center.y, rectangle.width, rectangle.height, 1);

    }

    getPolygon() {
        const polygon = new Polygon();
        for (let i = 0; i < this.vertices.length; i++) {
            let vertex = {
                x: this.vertices[i].x + this.rigidBody.position.x,
                y: this.vertices[i].y + this.rigidBody.position.y
            }
            this.rotatePoint(vertex, this.rigidBody.position, this.rigidBody.angle)
            polygon.vertices.push(vertex);
        }
        this.polygon = polygon;
        this.rigidBody.center = this.polygon.calculateCenter();
    }

    rotatePoint(point, center, angle) {
        const rotatedX = center.x + (point.x - center.x) * Math.cos(angle) - (point.y - center.y) * Math.sin(angle);
        const rotatedY = center.y + (point.x - center.x) * Math.sin(angle) + (point.y - center.y) * Math.cos(angle);
        return {
            x: rotatedX,
            y: rotatedY
        };
    }

    // Move and rotate the asteroid
    // update() {
    //     for (let i = 0; i < this.vertices.length; i++) {
    //         this.vertices[i] = this.rotatePoint(this.vertices[i], this.rigidBody.position, this.rigidBody.angle);
    //     }
    // }



    draw() {
        if (this.vertices.length < 3) {
            return;
        }
        ctx.save();
        ctx.translate(this.rigidBody.position.x, this.rigidBody.position.y);
        ctx.rotate(this.rigidBody.angle);

        ctx.fillStyle = "gray";
        ctx.lineWidth = 5;
        ctx.strokeStyle = "darkGray";
        ctx.beginPath();
        ctx.moveTo(this.vertices[0].x, this.vertices[0].y);
        for (let i = 1; i < this.vertices.length; i++) {
            ctx.lineTo(this.vertices[i].x, this.vertices[i].y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.restore();
    }


    generateRandomAsteroidPolygon() {
        const initialPoints = this.generateInitialPoints();
        let polygon = new Polygon(initialPoints);

        for (let i = 0; i < this.numSubdivisions; i++) {
            polygon = this.subdividePolygon(polygon);
        }

        this.vertices = polygon.vertices;
        return polygon;
    }

    generateInitialPoints() {
        const numPoints = Math.floor(Math.random() * 4) + 5;
        const points = [];

        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * Math.PI * 2;
            const distance = (Math.random() + 0.5) * this.radius;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            points.push(new Vector(x, y));
        }

        return points;
    }

    subdividePolygon(polygon) {
        const subdivisions = [];
        const numPoints = polygon.vertices.length;

        for (let i = 0; i < numPoints; i++) {
            const currentPoint = polygon.vertices[i];
            const nextPoint = polygon.vertices[(i + 1) % numPoints];

            const midPoint = currentPoint.add(nextPoint).multiply(0.5);
            const randomOffset = this.getRandomOffset();
            const newPoint = midPoint.add(randomOffset);

            subdivisions.push(currentPoint, newPoint);
        }

        return new Polygon(subdivisions);
    }

    getRandomOffset() {
        const minOffset = -this.radius * 0.1;
        const maxOffset = this.radius * 0.1;
        const offsetX = Math.random() * (maxOffset - minOffset) + minOffset;
        const offsetY = Math.random() * (maxOffset - minOffset) + minOffset;
        return new Vector(offsetX, offsetY);
    }

}
