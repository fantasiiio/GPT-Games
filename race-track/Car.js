class Car extends Rectangle {
    constructor(x, y, width, height, color, angle, neuralNetwork, gridSize) {
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
        this.timeOnSameGridSquare = 0;
        this.gridSize = gridSize;
        this.lastCheckpointIndex = 0;
        this.timeTakenToCompleteTrack = 0;
        this.completionTime = 0;
        this.startTime = 0;
        this.lapCount = 0;
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

    update(trackGeometry, track) {
        this.velocity += this.acceleration;
        this.velocity *= 0.99; // Friction


        this.oldX = this.x;
        this.oldY = this.y;

        this.x += this.velocity * Math.cos(this.angle * Math.PI / 180);
        this.y += this.velocity * Math.sin(this.angle * Math.PI / 180);

        // Calculate wheel angle based on velocity and steering angle
        this.wheelAngle = this.Steering.angle * Math.PI / 180;

        const dx = this.x - this.oldX;
        const dy = this.y - this.oldY;

        // Calculate new angle based on steering angle and velocity
        if (Math.abs(this.Steering.angle) > 0 && Math.abs(this.velocity) > 0) {
            const radius = Math.sqrt(dx * dx + dy * dy) / Math.sin(this.Steering.angle * Math.PI / 180);
            const angleDelta = Math.abs(this.velocity) * this.velocity * Math.PI / (180 * radius);

            this.angle += angleDelta * 180 / Math.PI;
        }

        // check if Die
        let intersect = this.calculateIntersectionWithTrack(trackGeometry);
        if (intersect.objectType) {
            this.die();
        }

        this.checkpointIndex = track.findNearestCheckpoint(new Vector(this.x, this.y), track.path);

        if (this.velocity < 0)
            this.die();

        this.updateLaserSensors();
    }

    updateCheckpoint() {
        if (this.checkpointIndex == this.lastCheckpointIndex) {
            this.timeOnSameGridSquare++;
            if (this.timeOnSameGridSquare >= 60 * 5) {
                this.die();
            }
        } else {
            this.timeOnSameGridSquare = 0;
            this.lastCheckpointIndex = this.checkpointIndex;
        }
    }

    win = function () {
        this.completionTime = new Date().getTime();
        // Calculate the time taken to complete the track
        this.timeTakenToCompleteTrack = this.completionTime - this.startTime;
        this.color = 'green'
        this.neuralNetwork.isCompleted = true;
    }

    die() {
        this.x = this.oldX;
        this.y = this.oldY;
        this.velocity = 0;
        this.acceleration = 0;
        this.Steering.angle = 0;
        this.neuralNetwork.isDead = true;
        this.color = 'gray'
    }


    reset(x, y, angle = 0) {
        this.startTime = new Date().getTime();
        this.timeOnSameGridSquare = 0;
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.velocity = 0;
        this.acceleration = 0;
        this.Steering.angle = 0;
        this.wheelAngle = 0;
        this.speed = 0;
        this.color = 'red'
    }

    updateLaserSensors() {
        const center = new Vector(this.x, this.y);
        for (let laser of this.laserSensors) {
            laser.updateOrigin(center, this.angle * Math.PI / 180);
            laser.endPoint = laser.calculateEndPoint();
        }
    }

    applyNeuralNetwork() {
        if (this.neuralNetwork.isDead)
            return;
        const inputs = this.laserSensors.map(sensor => (sensor.intersectionInfo || {}).distance / 1000 || 0);
        const [acceleration, steering] = this.neuralNetwork.apply(inputs);
        this.acceleration = (acceleration - 0.5) * 2 * 0.1;
        this.Steering.angle = (steering - 0.5) * 2 * 30;
    }

}