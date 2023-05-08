class Steering {
    constructor(maxAngle) {
        this.angle = 0;
        this.velocity = 0;
        this.acceleration = 0;
        this.maxAngle = maxAngle;
    }

    update(velocity) {
        if(Math.abs(this.angle) < this.maxAngle)
            this.angle += velocity;
    }

    reset(){
        this.angle = 0;
    }
}


class IntersectionUtil {
    constructor() {}

    static lineIntersection(p1, p2, lineStart, lineEnd) {
        let x1 = p1.x;
        let y1 = p1.y;
        let x2 = p2.x;
        let y2 = p2.y;
        let x3 = lineStart.x;
        let y3 = lineStart.y;
        let x4 = lineEnd.x;
        let y4 = lineEnd.y;

        let denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);

        if (denominator === 0) {
            return null;
        }

        let t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator;
        let u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator;

        if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
            let intersectionPoint = new Vector(x1 + t * (x2 - x1), y1 + t * (y2 - y1));
            let distance = p1.distanceTo(intersectionPoint);
            return {
                point: intersectionPoint,
                distance: distance
            };
        }

        return null;
    }


    static lineArcIntersection(p1, p2, center, radius, startAngle, endAngle) {

        function isWithinArc(point) {
            let angle = point.subtract(center).angle();
            if (angle < 0)
                angle += 2 * Math.PI;
            if (startAngle <= endAngle) {
                return angle >= startAngle && angle <= endAngle;
            } else {
                return angle >= startAngle || angle <= endAngle;
            }
        }

        let d = p2.subtract(p1);
        let f = p1.subtract(center);

        let a = d.dot(d);
        let b = 2 * f.dot(d);
        let c = f.dot(f) - radius * radius;

        let discriminant = b * b - 4 * a * c;

        if (discriminant < 0) {
            return null;
        }

        let t1 = (-b + Math.sqrt(discriminant)) / (2 * a);
        let t2 = (-b - Math.sqrt(discriminant)) / (2 * a);

        let intersectPoints = [];

        if (t1 >= 0 && t1 <= 1) {
            let p = p1.add(d.multiply(t1));
            if (isWithinArc(p)) {
                let distance = p1.distanceTo(p);
                intersectPoints.push({
                    point: p,
                    distance
                });
            }

        }

        if (t2 >= 0 && t2 <= 1) {
            let p = p1.add(d.multiply(t2));
            if (isWithinArc(p)) {
                let distance = p1.distanceTo(p);
                intersectPoints.push({
                    point: p,
                    distance
                });
            }
        }

        if (intersectPoints.length > 0) {
            // Find the closest intersection point to the start of the line
            let closestIntersection = null;
            let closestDistance = Infinity;

            for (let i = 0; i < intersectPoints.length; i++) {
                const intersection = intersectPoints[i];
                const distance = intersection.point.subtract(p1).length();
                if (distance < closestDistance) {
                    closestIntersection = intersection;
                    closestDistance = distance;
                }
            }

            return closestIntersection;
        }

        return null;
    }

}


class Polygon {
    constructor(points) {
        this.vertices = [];
        for (let i = 0; i < points.length; i++) {
            const point = points[i];
            const vertex = new Vector(point.x, point.y);
            this.vertices.push(vertex);
        }
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

    draw(context) {
        if (this.vertices.length < 3) {
            return;
        }
        context.strokeStyle = "blue";
        context.beginPath();
        context.moveTo(this.vertices[0].x, this.vertices[0].y);
        for (let i = 1; i < this.vertices.length; i++) {
            context.lineTo(this.vertices[i].x, this.vertices[i].y);
        }
        context.closePath();
        context.stroke();
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
}

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


class ParkingLot {
    constructor(offsetX, spaceWidth, spaceHeight, numSpaces, lineWidth) {
        this.offsetX = offsetX;
        this.spaceWidth = spaceWidth;
        this.spaceHeight = spaceHeight;
        this.numSpaces = numSpaces;
        this.width = spaceWidth * numSpaces;
        this.height = spaceHeight;
        this.lineWidth = lineWidth;
    }

    drawParkingLot(ctx) {
        // Draw parking lot
        ctx.fillStyle = 'gray';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;


        const numCols = 6;
        const parkingSpaceWidth = 60;
        const parkingSpaceHeight = 100;
        const spaceBetweenCols = 10;
        const spaceBetweenRows = canvas.height - 2 * this.spaceHeight;

        // Dessiner les places de parking avec des lignes jaunes
        ctx.strokeStyle = 'yellow';
        ctx.lineWidth = this.lineWidth;
        ctx.fillStyle = 'yellow';
        for (let row = 0; row < 2; row++) {
            for (let col = 0; col < numCols + 1; col++) {
                const x = col * (this.spaceWidth + this.lineWidth) - this.lineWidth;
                const y = row * (this.spaceHeight + spaceBetweenRows);
                ctx.fillRect(this.offsetX + x, y, this.lineWidth, this.spaceHeight);

            }
        }

        // for (let i = 1; i < this.numSpaces; i++) {
        //     ctx.beginPath();
        //     ctx.moveTo(this.x + (this.spaceWidth + this.lineWidth) * i, this.y);
        //     ctx.lineTo(this.x + (this.spaceWidth + this.lineWidth) * i, this.y + this.height);
        //     ctx.stroke();
        // }
    }

    draw(ctx) {


        // Draw parking lot
        ctx.fillStyle = 'gray';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw parking spaces
        ctx.fillStyle = 'dark-gray';
        const numCols = 6;
        const parkingSpaceWidth = 60;
        const parkingSpaceHeight = 100;
        const spaceBetweenCols = 10;
        const spaceBetweenRows = canvas.height - 2 * parkingSpaceHeight;


        // Draw spaces between parking spaces
        ctx.fillStyle = 'yellow';
        for (let row = 0; row < 2; row++) {
            for (let col = 0; col < numCols - 1; col++) {
                const x = col * (parkingSpaceWidth + spaceBetweenCols) + parkingSpaceWidth;
                const y = row * (parkingSpaceHeight + spaceBetweenRows);
                ctx.fillRect(x, y, spaceBetweenCols, parkingSpaceHeight);
            }
        }
    }


    checkCarInParkingSpace(car) {
        const carCorners = car.corners();
        for (const parkingSpace of this.parkingSpaces) {
            const spaceCorners = parkingSpace.corners();
            let cornersInSpace = 0;

            for (const carCorner of carCorners) {
                if (
                    carCorner.x >= spaceCorners[0].x &&
                    carCorner.x <= spaceCorners[2].x &&
                    carCorner.y >= spaceCorners[0].y &&
                    carCorner.y <= spaceCorners[2].y
                ) {
                    cornersInSpace++;
                }
            }

            if (cornersInSpace === 4) {
                return true;
            }
        }

        return false;
    }
}

function distanceBetweenPoints(x1, y1, x2, y2) {
    const deltaX = x2 - x1;
    const deltaY = y2 - y1;
    return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
}

class LaserSensor {
    constructor(origin, direction, offsetAngle = 0) {
        this.origin = origin;
        this.direction = direction;
        this.offsetAngle = offsetAngle;
        this.angle = 0;
        this.detectedObjects = [];
        this.intersectionInfo = {
            distance: 0,
            intersection: null
        };
        this.length = 1000;
        this.origin = origin;
        this.endPoint = this.calculateEndPoint();
    }

    calculateEndPoint() {
        let x = this.origin.x + this.length * Math.cos(this.angle + this.offsetAngle);
        let y = this.origin.y + this.length * Math.sin(this.angle + this.offsetAngle);
        return new Vector(x, y);
    }

    calculateIntersection(rectangles) {
        let closestIntersection = null;
        let closestDistance = this.length;
        let closestObjectType = null;

        for (const rect of rectangles) {
            const corners = rect.corners();
            for (let i = 0; i < corners.length; i++) {
                const startCorner = corners[i];
                const endCorner = corners[(i + 1) % corners.length];
                const intersection = this.calculateLineIntersection(startCorner, endCorner);
                if (intersection) {
                    const distance = distanceBetweenPoints(this.origin.x, this.origin.y, intersection.point.x, intersection.point.y);
                    if (distance < closestDistance) {
                        closestIntersection = intersection;
                        closestDistance = distance;
                        closestObjectType = rect.objectType;
                    }
                }
            }
        }

        return {
            intersection: closestIntersection,
            distance: closestDistance,
            objectType: closestObjectType
        };
    }

    updateIntersectionInfo(rectangles, maxLength = 1000) {
        let shortestDistance = maxLength;
        let closestIntersection = null;
        const endPoint = new Vector(this.origin.x + this.direction.x * maxLength, this.origin.y + this.direction.y * maxLength);

        rectangles.forEach(rectangle => {
            const corners = rectangle.corners();
            for (let i = 0; i < corners.length; i++) {
                const p1 = corners[i];
                const p2 = corners[(i + 1) % corners.length];
                const intersection = Vector.intersection(this.origin, endPoint, p1, p2);

                if (intersection) {
                    const distance = this.origin.subtract(intersection).length();
                    if (distance < shortestDistance) {
                        shortestDistance = distance;
                        closestIntersection = intersection;
                    }
                }
            }
        });

        this.intersectionInfo.distance = shortestDistance;
        this.intersectionInfo.intersection = closestIntersection;
    }

    updateOrigin(newOrigin, angle) {
        this.origin = newOrigin;
        this.direction = this.rotateDirection(angle);
    }

    rotateDirection(angle) {
        this.angle = angle;
        const sensorAngle = this.angle + this.offsetAngle;
        return new Vector(Math.cos(sensorAngle), Math.sin(sensorAngle));
    }

    draw(ctx) {
        ctx.save();
        ctx.strokeStyle = 'white';
        ctx.beginPath();
        ctx.moveTo(this.origin.x, this.origin.y);
        ctx.lineTo(this.endPoint.x, this.endPoint.y);
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.restore();
    }


    drawClosestIntersection(ctx) {
        if (this.intersectionInfo.intersection) {
            ctx.save();
            ctx.beginPath();
            ctx.arc(this.intersectionInfo.intersection.x, this.intersectionInfo.intersection.y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = 'red';
            ctx.fill();
            ctx.restore();
        }
    }

    detectObject(distance, objectType) {
        this.detectedObjects.push({
            distance,
            objectType
        });
    }

    clearDetectedObjects() {
        this.detectedObjects = [];
    }



    calculateTrackIntersection(trackGeometry) {
        let closestIntersection = null;
        let closestDistance = this.length;
        let closestObjectType = null;

        // Check for intersections with lines
        for (const line of trackGeometry.lines) {
            const intersection = IntersectionUtil.lineIntersection(this.origin, this.endPoint, line.p1, line.p2);
            if (intersection) {
                const distance = this.origin.distanceTo(intersection.point);
                if (distance < closestDistance) {
                    closestIntersection = intersection;
                    closestDistance = distance;
                    closestObjectType = 'line';
                }
            }
        }

        // Check for intersections with arcs
        for (const arc of trackGeometry.arcs) {
            let intersection = IntersectionUtil.lineArcIntersection(this.origin, this.endPoint, arc.center, arc.radius, arc.startAngle, arc.endAngle);
            if (intersection) {
                const distance = this.origin.distanceTo(intersection.point);
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
}

function drawIntersectionPoint(ctx, detectedObject) {
    if (!detectedObject.intersection)
        return;
    let color;
    if (detectedObject.objectType === 'arc') {
        color = 'lightblue';
    } else if (detectedObject.objectType === 'line') {
        color = 'lightblue';
    } else {
        color = 'white';
    }

    ctx.beginPath();
    ctx.arc(detectedObject.intersection.point.x, detectedObject.intersection.point.y, 10, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.closePath();
}

class Vector {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    add(other) {
        return new Vector(this.x + other.x, this.y + other.y);
    }

    subtract(other) {
        return new Vector(this.x - other.x, this.y - other.y);
    }

    dot(other) {
        return this.x * other.x + this.y * other.y;
    }

    length() {
        return Math.sqrt(this.dot(this));
    }

    normalize() {
        const len = this.length();
        return new Vector(this.x / len, this.y / len);
    }

    project(other) {
        const scale = this.dot(other) / other.dot(other);
        return other.multiply(scale);
    }

    multiply(scalar) {
        return new Vector(this.x * scalar, this.y * scalar);
    }

    perpendicular() {
        return new Vector(-this.y, this.x);
    }
    equals(other) {
        return this.x == other.x && this.y == other.y;
    }

    distanceTo(other) {
        const dx = this.x - other.x;
        const dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    angle() {
        return Math.atan2(this.y, this.x);
    }
}

Vector.intersection = function (p1, p2, p3, p4) {
    const d = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x);
    if (d === 0) return null;

    const t = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / d;
    const u = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / d;

    if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
        return new Vector(p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y));
    }

    return null;
};


class Goal extends Rectangle {
    constructor(x, y, width, height) {
        super(x, y, width, height);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.objectType = 'goal';
    }

    draw(ctx) {
        ctx.save();
        ctx.fillStyle = "#00FF00";
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.restore();
    }

    drawPercentageCovered(ctx, pct) {
        // Draw the percentage covered text
        ctx.font = '20px Arial';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pct.toFixed(0), this.x + this.width / 2, this.y + this.height / 2);
    }
}


class Car extends Rectangle {
    constructor(x, y, width, height, color, angle, neuralNetwork) {
        super(x, y, width, height);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.angle = angle;
        this.velocity = 0;
        this.acceleration = 0;
        this.wheelAngle = 0;
        this.speed = 0;
        this.laserSensors = [];
        this.createLaserSensors();
        this.objectType = `${color}Car`;
        this.neuralNetwork = neuralNetwork;
        this.Steering = new Steering(20);
    }



    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle * Math.PI / 180);

        // Draw the car body
        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);

        // Draw tires
        ctx.fillStyle = 'black';
        const tireWidth = 20;
        const tireHeight = 5;
        const tireOffsetX = 5;
        const tireOffsetY = -5;

        // Rear left tire
        ctx.save();
        ctx.translate(-this.width / 2 + tireOffsetX + tireWidth / 2, -this.height / 2 + tireOffsetY + tireHeight / 2);
        ctx.fillRect(-tireWidth / 2, -tireHeight / 2, tireWidth, tireHeight);
        ctx.restore();

        // Front Left tire
        ctx.save();
        ctx.translate(this.width / 2 - tireWidth - tireOffsetX + tireWidth / 2, -this.height / 2 + tireOffsetY + tireHeight / 2);
        ctx.rotate(this.wheelAngle);
        ctx.fillRect(-tireWidth / 2, -tireHeight / 2, tireWidth, tireHeight);
        ctx.restore();

        // Rear Right tire
        ctx.save();
        ctx.translate(-this.width / 2 + tireOffsetX + tireWidth / 2, this.height / 2 - tireHeight - tireOffsetY + tireHeight / 2);
        ctx.fillRect(-tireWidth / 2, -tireHeight / 2, tireWidth, tireHeight);
        ctx.restore();

        // Front right tire
        ctx.save();
        ctx.translate(this.width / 2 - tireWidth - tireOffsetX + tireWidth / 2, this.height / 2 - tireHeight - tireOffsetY + tireHeight / 2);
        ctx.rotate(this.wheelAngle);
        ctx.fillRect(-tireWidth / 2, -tireHeight / 2, tireWidth, tireHeight);
        ctx.restore();

        // Draw front lights
        ctx.fillStyle = 'yellow';
        const lightWidth = 5;
        const lightHeight = 10;
        const lightOffsetX = this.width / 2 - 5;
        const lightOffsetY = (this.height - lightHeight) / 2;
        // Left front light
        ctx.fillRect(lightOffsetX, -lightOffsetY, lightWidth, lightHeight);
        // Right front light
        ctx.fillRect(lightOffsetX, lightOffsetY - lightHeight, lightWidth, lightHeight);

        ctx.restore();

    }

    createLaserSensors() {
        const numSensors = 8;
        const center = new Vector(this.x + this.width / 2, this.y + this.height / 2);

        for (let i = 0; i < numSensors; i++) {
            const sensorAngle = (i * 360 / numSensors) * Math.PI / 180;
            this.laserSensors.push(new LaserSensor(center, 0, sensorAngle));
        }
    }

    drawLaserSensors(ctx, maxLength) {
        for (let sensor of this.laserSensors) {
            sensor.draw(ctx, maxLength);
        }
    }



    checkCollisionWithParkedCars(parkedCars) {
        for (const parkedCar of parkedCars) {
            if (this.calculateIntersectionArea(parkedCar)) {
                this.neuralNetwork.isDead = true;
                return true;
            }
        }
        return false;
    }

    checkScreenCollision(canvasWidth, canvasHeight) {
        const corners = this.corners();

        for (let corner of corners) {
            if (corner.x < 0 || corner.y < 0 || corner.x > canvasWidth || corner.y > canvasHeight) {
                this.neuralNetwork.isDead = true;
                return true;
            }
        }

        return false;
    }

    update(trackGeometry) {
        this.velocity += this.acceleration;
        this.velocity *= 0.99; // Friction

        const oldX = this.x;
        const oldY = this.y;

        this.x += this.velocity * Math.cos(this.angle * Math.PI / 180);
        this.y += this.velocity * Math.sin(this.angle * Math.PI / 180);

        // Calculate wheel angle based on velocity and steering angle
        this.wheelAngle = this.Steering.angle * Math.PI / 180;

        const dx = this.x - oldX;
        const dy = this.y - oldY;

        // Calculate new angle based on steering angle and velocity
        if (Math.abs(this.Steering.angle) > 0 && Math.abs(this.velocity) > 0) {
            const radius = Math.sqrt(dx * dx + dy * dy) / Math.sin(this.Steering.angle * Math.PI / 180);
            const angleDelta = Math.abs(this.velocity) * this.velocity * Math.PI / (180 * radius);

            this.angle += angleDelta * 180 / Math.PI;
        }

        //     // Undo the movement if there is a collision
        let intersect = this.calculateIntersectionWithTrack(trackGeometry);
        if (intersect.objectType) {
            this.x = oldX;
            this.y = oldY;
            this.velocity = 0;
            this.acceleration = 0;
            this.Steering.angle = 0;
            this.neuralNetwork.isDead = true;
        }

        this.updateLaserSensors();
    }

    reset(x, y, angle = 0) {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.velocity = 0;
        this.acceleration = 0;
        this.Steering.angle = 0;
        this.wheelAngle = 0;
        this.speed = 0;
    }

    updateLaserSensors() {
        const center = new Vector(this.x, this.y);
        for (let laser of this.laserSensors) {
            laser.updateOrigin(center, this.angle * Math.PI / 180);
            laser.endPoint = laser.calculateEndPoint();
        }
    }

    updateControls() {
        if (this.neuralNetwork.isDead)
            return;
        const inputs = this.laserSensors.map(sensor => (sensor.intersectionInfo || {}).distance / 1000 || 0);
        const [acceleration, steering] = this.neuralNetwork.apply(inputs);
        this.acceleration = (acceleration - 0.5) * 2 * 0.1;
        this.Steering.angle = (steering - 0.5) * 2 * 30;
    }

}



function restartGame() {
    const initialX = canvas.width - 80;
    const initialY = (canvas.height - 40) / 2;
    const initialAngle = 180;

    redCar.reset(initialX, initialY, initialAngle);
}
let redCars = [];

// const canvas = document.getElementById('parking');
// const ctx = canvas.getContext('2d');
// const parkingLot = new ParkingLot(100, 60, 100, 6, 10);

function initGeneticAlgorithm(population) {
    const populationSize = 50;
    const inputSize = 8;
    const hiddenSize = 4;
    const outputSize = 2;
    const mutationRate = 0.1;
    const maxGenerations = 100;
    const inputs = []; // Vous pouvez ajouter des données d'entrée spécifiques ici
    const expectedOutputs = []; // Vous pouvez ajouter des sorties attendues spécifiques ici

    const ga = new GeneticAlgorithm(
        population,
        inputSize,
        hiddenSize,
        outputSize,
        mutationRate,
        maxGenerations,
        inputs,
        expectedOutputs
    );

    return ga;
}

/*
document.addEventListener('DOMContentLoaded', function () {

    const parkingSpaceWidth = 60;
    const parkingSpaceHeight = 100;
    const spaceBetweenCols = 10;
    const spaceBetweenRows = canvas.height - 2 * parkingSpaceHeight;

    //drawParkingLot(ctx, canvas);


    // Draw parked cars
    const numCols = 6;
    const parkedCars = [];
    const numCars = 4;
    const occupiedSpaces = [];

    // Draw parked cars
    for (let i = 0; i < numCars; i++) {
        let x = Math.floor(Math.random() * numCols);
        let y = Math.floor(Math.random() * 2);

        while (occupiedSpaces.some(s => s[0] === x && s[1] === y)) {
            x = Math.floor(Math.random() * numCols);
            y = Math.floor(Math.random() * 2);
        }

        parkedCars.push(new Car(x, y, 80, 40, 'blue', y % 2 == 1 ? 90 : 270));
        occupiedSpaces.push([x, y]);
    }

    parkedCars.forEach(car => {
        const x = car.x * (parkingSpaceWidth + spaceBetweenCols) + (parkingSpaceWidth - car.width) / 2;
        const y = car.y * (parkingSpaceHeight + spaceBetweenRows) + (parkingSpaceHeight - car.height) / 2;
        car.x = parkingLot.offsetX + x;
        car.y = y;
        car.draw(ctx);
    });

    // Choose a random empty parking space for the goal
    let goalX = null;
    let goalY = null;
    let foundEmptySpace = false;
    let numIterations = 0;
    const maxIterations = numCols * 2;

    while (!foundEmptySpace && numIterations < maxIterations) {
        numIterations++;
        goalX = Math.floor(Math.random() * numCols);
        goalY = Math.floor(Math.random() * 2);
        foundEmptySpace = !occupiedSpaces.some(s => s[0] === goalX && s[1] === goalY);
    }

    if (!foundEmptySpace) {
        // All parking spaces are occupied, so use the last space for the goal
        goalX = numCols - 1;
        goalY = 1;
    }

    // Draw the goal
    const goalWidth = parkingSpaceWidth;
    const goalHeight = parkingSpaceHeight;
    const goalXPos = parkingLot.offsetX + goalX * (parkingSpaceWidth + spaceBetweenCols) + (parkingSpaceWidth - goalWidth) / 2;
    const goalYPos = goalY * (parkingSpaceHeight + spaceBetweenRows) + (parkingSpaceHeight - goalHeight) / 2;
    const goal = new Goal(goalXPos, goalYPos, goalWidth, goalHeight, 'green');
    goal.draw(ctx);

    // Create red cars
    for (let i = 0; i < numCars; i++) {
        const neuralNetwork = new NeuralNetwork(8, 4, 2);
        const redCar = new Car(canvas.width - 120, (canvas.height - 40) / 2, 80, 40, 'red', 180, neuralNetwork);
        redCar.draw(ctx);
        redCars.push(redCar);
    }

    let population = redCars.map(car => car.neuralNetwork);
    const geneticAlgorithm = initGeneticAlgorithm(population);


    geneticAlgorithm.run(bestIndividual => {
        console.log("L'algorithme génétique a terminé. Meilleur individu : ", bestIndividual);
    });

    function gameLoop() {
        // Effacer le canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Redessiner le parking
        parkingLot.drawParkingLot(ctx);

        ctx.fillStyle = 'green';
        ctx.fillRect(goalXPos, goalYPos, goalWidth, goalHeight);

        parkedCars.forEach(car => {
            car.draw(ctx);
        });

        for (let redCar of redCars) {


            redCar.updateControls();

            // Mettre à jour la position de la voiture rouge
            const prevX = redCar.x;
            const prevY = redCar.y;
            const prevWidth = redCar.width;
            const prevHeight = redCar.height;
            const prevAngle = redCar.angle;

            redCar.update(parkedCars, goal);

            // Effacer la position précédente de la voiture rouge
            ctx.save();
            ctx.translate(prevX + prevWidth / 2, prevY + prevHeight / 2);
            ctx.rotate(prevAngle * Math.PI / 180);
            ctx.clearRect(-prevWidth / 2, -prevHeight / 2, prevWidth, prevHeight);
            ctx.restore();
            redCar.draw(ctx);


            let objects = parkedCars.concat([goal]);

            for (let laserSensor of redCar.laserSensors) {
                let detectedObjects = laserSensor.calculateIntersection(objects);
                laserSensor.drawIntersectionPoint(ctx, detectedObjects);
            }
            // Redessiner la voiture rouge à sa nouvelle position
            redCar.drawLaserSensors(ctx);
            redCar.draw(ctx);

            let percentageCovered = redCar.percentageCoveredBy(goal);
            goal.drawPercentageCovered(ctx, percentageCovered);

            if (percentageCovered >= 100 && Math.abs(redCar.velocity) < 0.1) {
                restartGame();
            }
        }
        requestAnimationFrame(gameLoop);
    }

    gameLoop();

    // Event listeners for keyboard input
    document.addEventListener('keydown', (event) => {
        const key = event.key;

        switch (key) {
            case 'ArrowUp':
                redCars[0].acceleration = 0.1;
                break;
            case 'ArrowDown':
                redCars[0].acceleration = -0.1;
                break;
            case 'ArrowLeft':
                redCars[0].steeringAngle = -30;
                break;
            case 'ArrowRight':
                redCars[0].steeringAngle = 30;
                break;
            case 'r':
            case 'R':
                restartGame();
                break;
        }
    });

    document.addEventListener('keyup', (event) => {
        const key = event.key;

        if (key === 'ArrowUp' || key === 'ArrowDown') {
            redCars[0].acceleration = 0;
        } else if (key === 'ArrowLeft' || key === 'ArrowRight') {
            redCars[0].steeringAngle = 0;
        }
    });
});*/