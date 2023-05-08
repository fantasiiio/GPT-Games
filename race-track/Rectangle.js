class Rectangle {
    constructor(x, y, width, height, angle = 0) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.angle = angle;
    }

    corners() {
        const halfWidth = this.width / 2;
        const halfHeight = this.height / 2;

        const topLeft = new Vector(this.x - halfWidth, this.y - halfHeight);
        const topRight = new Vector(this.x + halfWidth, this.y - halfHeight);
        const bottomLeft = new Vector(this.x - halfWidth, this.y + halfHeight);
        const bottomRight = new Vector(this.x + halfWidth, this.y + halfHeight);
        const corners = [topLeft, topRight, bottomRight, bottomLeft];
        const center = new Vector(this.x, this.y);

        for (let i = 0; i < corners.length; i++) {
            corners[i] = this.rotatePoint(corners[i], center, this.angle * Math.PI / 180);
        }
        return corners;
    }

    rotatePoint(point, center, angle) {
        const s = Math.sin(angle);
        const c = Math.cos(angle);
        const translatedX = point.x - center.x;
        const translatedY = point.y - center.y;
        const rotatedX = translatedX * c - translatedY * s;
        const rotatedY = translatedX * s + translatedY * c;
        return new Vector(rotatedX + center.x, rotatedY + center.y);
    }

    percentageCoveredBy(rect) {
        const intersectionArea = this.calculateIntersectionArea(rect);
        const rect1Area = this.width * this.height;
        return (intersectionArea / rect1Area) * 100;
    }

    getPolygon() {
        const corners = this.corners();
        const polygon = new Polygon(corners);
        return polygon;
    }

    calculateIntersectionArea(rect) {
        const poly1 = this.getPolygon();
        const poly2 = rect.getPolygon();
        const intersection = poly1.clip(poly2);
        const area = intersection.area();
        return area;
    }

    calculateIntersectionWithTrack(trackGeometry) {
        let closestIntersection = null;
        let closestDistance = Infinity;
        let closestObjectType = null;

        // Check for intersections with lines
        for (const line of trackGeometry.lines) {
            const intersection = this.calculateLineIntersection(line);
            if (intersection) {
                const distance = this.corners().reduce((minDistance, corner) => {
                    const dist = corner.distanceTo(intersection.point);
                    return Math.min(minDistance, dist);
                }, Infinity);
                if (distance < closestDistance) {
                    closestIntersection = intersection;
                    closestDistance = distance;
                    closestObjectType = 'line';
                }
            }
        }

        // Check for intersections with arcs
        for (const arc of trackGeometry.arcs) {
            const intersection = this.calculateArcIntersection(arc);
            if (intersection) {
                const distance = this.corners().reduce((minDistance, corner) => {
                    const dist = corner.distanceTo(intersection.point);
                    return Math.min(minDistance, dist);
                }, Infinity);
                if (distance < closestDistance) {
                    closestIntersection = intersection;
                    closestDistance = distance;
                    closestObjectType = 'arc';
                }
            }
        }

        return {
            intersection: closestIntersection,
            distance: closestDistance,
            objectType: closestObjectType
        };
    }

    calculateArcIntersection(arc) {
        const corners = this.corners();
        for (let i = 0; i < corners.length; i++) {
            const startCorner = corners[i];
            const endCorner = corners[(i + 1) % corners.length];
            const intersection = IntersectionUtil.lineArcIntersection(startCorner, endCorner, arc.center, arc.radius, arc.startAngle, arc.endAngle);
            if (intersection) {
                return intersection;
            }
        }
        return null;
    }

    calculateLineIntersection(line) {
        const corners = this.corners();
        for (let i = 0; i < corners.length; i++) {
            const startCorner = corners[i];
            const endCorner = corners[(i + 1) % corners.length];
            const intersection = IntersectionUtil.lineIntersection(startCorner, endCorner, line.p1, line.p2);
            if (intersection) {
                return intersection;
            }
        }
        return null;
    }
}


