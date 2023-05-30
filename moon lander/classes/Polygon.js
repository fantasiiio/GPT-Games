class Polygon {
    constructor(points) {
        this.vertices = [];
        if (!points) return;
        for (let i = 0; i < points.length; i++) {
            const point = points[i];
            const vertex = new Vector(point.x, point.y);
            this.vertices.push(vertex);
        }
    }

    static createRectangle(x, y, width, height) {
        const points = [{
                x,
                y
            },
            {
                x: x + width,
                y
            },
            {
                x: x + width,
                y: y + height
            },
            {
                x,
                y: y + height
            }
        ];

        return new Polygon(points);
    }

    rotate(angle, center) {
        for (let i = 0; i < this.vertices.length; i++) {
            this.vertices[i] = this.rotatePoint(this.vertices[i], center, angle);
        }
    }

    rotatePoint(point, center, angle) {
        const rotatedX = center.x + (point.x - center.x) * Math.cos(angle) - (point.y - center.y) * Math.sin(angle);
        const rotatedY = center.y + (point.x - center.x) * Math.sin(angle) + (point.y - center.y) * Math.cos(angle);
        return {
            x: rotatedX,
            y: rotatedY
        };
    }

    calculateCenter() {
        let center = new Vector(0, 0);
        for (let i = 0; i < this.vertices.length; i++) {
            center = center.add(this.vertices[i]);
        }
        center = center.multiply(1 / this.vertices.length);
        return center;
    }

    sortVertices() {
        const center = this.calculateCenter();
        const vertices = this.vertices.slice();
        vertices.sort((a, b) => {
            const angleA = Math.atan2(a.y - center.y, a.x - center.x);
            const angleB = Math.atan2(b.y - center.y, b.x - center.x);
            if (angleA < angleB) return -1;
            if (angleA > angleB) return 1;
            return 0;
        });
        this.vertices = vertices;
    }

    area() {
        let area = 0;
        for (let i = 0; i < this.vertices.length; i++) {
            const vertex1 = this.vertices[i];
            const vertex2 = i === this.vertices.length - 1 ? this.vertices[0] : this.vertices[i + 1];
            area += vertex1.x * vertex2.y - vertex1.y * vertex2.x;
        }
        return Math.abs(area) / 2;
    }

    draw() {
        if (this.vertices.length < 3) {
            return;
        }
        ctx.strokeStyle = "blue";
        ctx.beginPath();
        ctx.moveTo(this.vertices[0].x, this.vertices[0].y);
        for (let i = 1; i < this.vertices.length; i++) {
            ctx.lineTo(this.vertices[i].x, this.vertices[i].y);
        }
        ctx.closePath();
        ctx.stroke();
    }

    clip(otherPolygon) {
        let outputList = this.vertices;
        let cp1, cp2, s, e;
        for (let j = 0; j < otherPolygon.vertices.length; j++) {
            const inputList = outputList;
            outputList = [];
            cp1 = otherPolygon.vertices[j];
            cp2 = j === otherPolygon.vertices.length - 1 ? otherPolygon.vertices[0] : otherPolygon.vertices[j + 1];
            for (let i = 0; i < inputList.length; i++) {
                s = inputList[i];
                e = i === inputList.length - 1 ? inputList[0] : inputList[i + 1];
                if (this.inside(s, cp1, cp2)) {
                    if (!this.inside(e, cp1, cp2)) {
                        outputList.push(this.intersection(cp1, cp2, s, e));
                    }
                    outputList.push(s);
                } else if (this.inside(e, cp1, cp2)) {
                    outputList.push(this.intersection(cp1, cp2, s, e));
                }
            }
        }
        return new Polygon(outputList);
    }

    // Returns the nearest intersection points between this and line
    getNearestRayIntersection(ray, includeLastSegment = true) {
        let nearestPoint = null;
        let nearestDistance = Infinity;

        const lastVertexIndex = includeLastSegment ? this.vertices.length : this.vertices.length - 1;

        for (let i = 0; i < lastVertexIndex; i++) {
            const p1 = this.vertices[i];
            const p2 = i === this.vertices.length - 1 ? this.vertices[0] : this.vertices[i + 1];
            const intersection = IntersectionUtil.lineIntersection(p1, p2, ray.start, ray.end);

            if (intersection) {
                const distance = intersection.point.distanceTo(ray.start);

                if (distance < nearestDistance) {
                    nearestPoint = intersection;
                    nearestDistance = distance;
                }
            }
        }

        return nearestPoint;
    }


    //
    inside(point, cp1, cp2) {
        return (cp2.x - cp1.x) * (point.y - cp1.y) > (cp2.y - cp1.y) * (point.x - cp1.x);
    }

    intersection(cp1, cp2, s, e) {
        const dc = new Vector(cp1.x - cp2.x, cp1.y - cp2.y);
        const dp = new Vector(s.x - e.x, s.y - e.y);
        const n1 = cp1.x * cp2.y - cp1.y * cp2.x;
        const n2 = s.x * e.y - s.y * e.x;
        const n3 = 1.0 / (dc.x * dp.y - dc.y * dp.x);
        return new Vector((n1 * dp.x - n2 * dc.x) * n3, (n1 * dp.y - n2 * dc.y) * n3);
    }

    // Returns the nearest intersection point between this and poly2
    getNearestIntersection(poly2, includeLastSegment = true) {
        let nearestPoint = null;
        let nearestDistance = Infinity;

        const lastVertexIndex = includeLastSegment ? this.vertices.length : this.vertices.length - 1;

        for (let i = 0; i < lastVertexIndex; i++) {
            // Iterate through each edge of this
            for (let i = 0; i < this.vertices.length; i++) {
                const p1 = this.vertices[i];
                const p2 = i === this.vertices.length - 1 ? this.vertices[0] : this.vertices[i + 1];

                // Iterate through each edge of poly2
                for (let j = 0; j < poly2.vertices.length; j++) {
                    const p3 = poly2.vertices[j];
                    const p4 = j === poly2.vertices.length - 1 ? poly2.vertices[0] : poly2.vertices[j + 1];

                    // Find the intersection point between the two edges
                    const intersection = IntersectionUtil.lineIntersection(p1, p2, p3, p4);

                    // If there is an intersection
                    if (intersection) {
                        // Calculate the distance between the intersection point and this
                        const distance = intersection.point.distanceTo(p1);

                        // Update the nearest point and distance if necessary
                        if (distance < nearestDistance) {
                            nearestPoint = intersection;
                            nearestDistance = distance;
                        }
                    }
                }
            }
        }

        return nearestPoint;
    }


    createRectangleFromPolygon() {
        let minX = Number.MAX_VALUE;
        let minY = Number.MAX_VALUE;
        let maxX = Number.MIN_VALUE;
        let maxY = Number.MIN_VALUE;

        // Find the minimum and maximum coordinates
        for (const point of this.vertices) {
            minX = Math.min(minX, point.x);
            minY = Math.min(minY, point.y);
            maxX = Math.max(maxX, point.x);
            maxY = Math.max(maxY, point.y);
        }

        // Calculate the width and height of the rectangle
        const width = maxX - minX;
        const height = maxY - minY;

        // Create and return the rectangle
        const rectangle = {
            x: minX,
            y: minY,
            width: width,
            height: height,
        };

        return rectangle;
    }

    isPointInside(point) {
        const vertices = this.vertices;
        let inside = false;
        for (let i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
            const xi = vertices[i].x;
            const yi = vertices[i].y;
            const xj = vertices[j].x;
            const yj = vertices[j].y;

            const intersect =
                yi > point.y !== yj > point.y &&
                point.x < ((xj - xi) * (point.y - yi)) / (yj - yi) + xi;

            if (intersect) inside = !inside;
        }

        return inside;
    }

}