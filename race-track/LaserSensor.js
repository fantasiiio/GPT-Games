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

