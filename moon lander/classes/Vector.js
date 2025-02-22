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

    cross(vector) {
        return this.x * vector.y - this.y * vector.x;
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

    div(scalar) {
        return new Vector(this.x / scalar, this.y / scalar);
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

    static distance(v1, other) {
        const dx = v1.x - other.x;
        const dy = v1.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    angle() {
        return Math.atan2(this.x, this.y);
    }

    angle2() {
        var r = Math.sqrt(this.x * this.x + this.y * this.y);
        return {
            cos_angle: this.x / r,
            sin_angle: this.y / r
        };
    }

    static angleBetweenVectors(vector1, vector2) {
        const dotProduct = vector1.dot(vector2);
        const magnitudeProduct = vector1.length() * vector2.length();
        const angleInRadians = Math.acos(dotProduct / magnitudeProduct);
        return angleInRadians;
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