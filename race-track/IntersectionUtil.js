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

        static getArcPoints(arcCenter, arcRadius, arcStartAngle, arcEndAngle, numPoints = 10) {
            const points = [];
            const angleDelta = Math.abs(arcEndAngle - arcStartAngle);
            const angleStep = angleDelta / (numPoints - 1);

            for (let pointIndex = 0; pointIndex < numPoints; pointIndex++) {
                let angle;
                if (arcStartAngle > arcEndAngle)
                    angle = arcEndAngle + angleStep * pointIndex;
                else
                    angle = arcStartAngle - angleStep * pointIndex;
                const x = arcCenter.x + arcRadius * Math.cos(angle * Math.PI / 180);
                const y = arcCenter.y + arcRadius * Math.sin(angle * Math.PI / 180);
                points.push({
                    x,
                    y
                });
            }

            return points;
        }

    }