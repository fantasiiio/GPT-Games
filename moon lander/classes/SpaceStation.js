class SpaceStation {
    constructor(x, y, width, height, dockingWidth, dockingHeight, angle) {
        this.angle = angle;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.dockingWidth = dockingWidth;
        this.dockingHeight = dockingHeight;
        this.dockPosition = new Vector(this.x + this.width / 2, this.y - this.dockingHeight);

        this.dockAlignment = new Vector(Math.cos(angle-Math.PI/2), Math.sin(angle-Math.PI/2));

        this.polygon = Polygon.createRectangle(this.x, this.y, this.width, this.height);
        let center = this.polygon.calculateCenter();
        let rotatedPosition = this.rotatePoint(this.dockPosition, center, angle);
        this.dockPosition = new Vector(rotatedPosition.x, rotatedPosition.y);
        this.polygon.rotate(angle, center);
        this.rigidBody = new RigidBody(this.x, this.y, this.width, this.height, 1);
        this.rigidBody.center = center;
        this.docked
    }
    // Update the space station position and rotation
    updateDockPosition() {
        
        this.dockAlignment = new Vector(Math.cos(this.angle-Math.PI/2), Math.sin(this.angle-Math.PI/2));

        this.x = position.x;
        this.y = position.y;
        this.dockPosition.x = this.x + this.width / 2;
        this.dockPosition.y = this.y - this.dockingHeight;
        this.polygon = Polygon.createRectangle(this.x, this.y, this.width, this.height);
        let center = this.polygon.calculateCenter();
        let rotatedPosition = this.rotatePoint(this.dockPosition, center, this.angle);
        this.dockPosition = new Vector(rotatedPosition.x, rotatedPosition.y);
        this.polygon.rotate(this.angle, center);
        this.rigidBody.center = center;
    }

    rotatePoint(point, center, angle) {
        const rotatedX = center.x + (point.x - center.x) * Math.cos(angle) - (point.y - center.y) * Math.sin(angle);
        const rotatedY = center.y + (point.x - center.x) * Math.sin(angle) + (point.y - center.y) * Math.cos(angle);
        return {
            x: rotatedX,
            y: rotatedY
        };
    }

    draw() {
        ctx.save();
        ctx.translate(this.x + this.width / 2, this.y + this.height / 2); // Translate to the center of the space station
        ctx.rotate(this.angle); // Rotate by the specified angle
        ctx.fillStyle = 'gray';
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height); // Draw the space station body
        const dockingX = -this.dockingWidth / 2;
        const dockingY = -this.height / 2 - this.dockingHeight;
        ctx.fillStyle = 'white';
        ctx.fillRect(dockingX, dockingY, this.dockingWidth, this.dockingHeight); // Draw the docking port
        ctx.restore();
    }


}