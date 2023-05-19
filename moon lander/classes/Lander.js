class Lander {
    constructor(x, y, neuralNetwork = null) {
        this.x = x;
        this.y = y;
        this.angle = 0;
        this.velocityX = 0;
        this.velocityY = 0;
        this.thrust = 0;
        this.rotationSpeed = 0;
        this.maxFuel = 1000;
        this.fuel = this.maxFuel;
        this.neuralNetwork = neuralNetwork;
        this.rotationAccel = 0;
        this.successfulLanding = false;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
        this.currentTime = 0;
        this.landed = false;
        this.cumulRotationPenaltyFactor = 0;
        this.frameCount = 0;
        this.target = null;
        this.targetIndex = 0;
    }

    isCollidingWithMountains(terrain) {
        const x = this.x;
        const y = this.y + 25;
        return y >= terrain.getY(x);
    }

    updateLander() {
        this.fuel -= FuelConsumption_thrust * this.thrust;
        this.rotationSpeed += this.rotationAccel;
        if (this.rotationSpeed > maxRotationSpeed) {
            this.rotationSpeed = maxRotationSpeed;
        } else if (this.rotationSpeed < -maxRotationSpeed) {
            this.rotationSpeed = -maxRotationSpeed;
        }
        this.angle += this.rotationSpeed;
        this.velocityX += this.thrust * Math.sin(this.angle);
        this.velocityY += gravity - (this.thrust * Math.cos(this.angle));
        this.x += this.velocityX;
        this.y += this.velocityY;
    }

    resetLander() {
        this.x = canvas.width / 2;
        this.y = 50;
        this.angle = 0;
        this.velocityX = 0;
        this.velocityY = 0;
        this.thrust = 0;
        this.rotationSpeed = 0;
        this.fuel = this.maxFuel;
        this.rotationAccel = 0;
        this.successfulLanding = false;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
        this.currentTime = 0;
        this.landed = false;
        this.cumulRotationPenaltyFactor = 0;
        this.frameCount = 0;
        this.target = null;
        this.targetIndex = 0;
    }

    changeTarget(target) {
        this.target = target;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
    }


    drawLander() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        // Draw spaceship body
        ctx.beginPath();
        ctx.moveTo(-15, 15);
        ctx.quadraticCurveTo(-15, -15, 0, -30);
        ctx.quadraticCurveTo(15, -15, 15, 15);
        ctx.closePath();
        ctx.fillStyle = 'silver';
        ctx.fill();
        ctx.strokeStyle = 'gray';
        ctx.stroke();


        // Draw spaceship windows
        ctx.beginPath();
        ctx.arc(0, -5, 6, 0, 2 * Math.PI);
        ctx.fillStyle = 'black';
        ctx.fill();
        ctx.stroke();

        // Draw spaceship wings
        ctx.beginPath();
        ctx.moveTo(-15, 15);
        ctx.quadraticCurveTo(-25, 10, -25, 30);
        ctx.lineTo(-15, 30);
        ctx.closePath();
        ctx.fillStyle = 'silver';
        ctx.fill();
        ctx.strokeStyle = 'gray';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(15, 15);
        ctx.quadraticCurveTo(25, 10, 25, 30);
        ctx.lineTo(15, 30);
        ctx.closePath();
        ctx.fillStyle = 'silver';
        ctx.fill();
        ctx.strokeStyle = 'gray';
        ctx.stroke();

        // Draw spaceship thruster
        if (this.thrust > 0) {
            const thrusterHeight = 15;
            const adjustedThrusterHeight = thrusterHeight * (this.thrust / maxThrustPower);
            ctx.beginPath();
            ctx.moveTo(-5, 15);
            ctx.lineTo(0, 15 + adjustedThrusterHeight);
            ctx.lineTo(5, 15);
            ctx.closePath();
            ctx.fillStyle = 'red';
            ctx.fill();
            ctx.strokeStyle = 'red';
            ctx.stroke();
        }
        ctx.restore();
    }

    isLanderOutOfScreen() {
        return (
            isNaN(this.x) || // Check if lander is not a number
            isNaN(this.y) || // Check if lander is not a number
            this.x < 0 || // Check if lander is left of the screen
            this.x > canvas.width / zoomLevel || // Check if lander is right of the screen
            this.y < 0 || // Check if lander is above the screen
            this.y > canvas.height / zoomLevel // Check if lander is below the screen
        );
    }
    die() {
        this.landed = true;
        this.velocityX = 0;
        this.velocityY = 0;
        this.rotationSpeed = 0;
        this.neuralNetwork.isDead = true;
    }

    checkLanding() {
        const x = this.x;
        const y = this.y;
        if (this.isLanderOutOfScreen()) {
            this.die();
        } else {
            if (this.isCollidingWithMountains(terrain)) {
                let checkAngle = (this.angle + Math.PI / 2) % (2 * Math.PI);
                const platformRange = y >= platform.y && x >= platform.x && x <= platform.x + platform.width;
                if (platformRange && this.velocityY < landingSpeed && Math.abs(Math.PI / 2 - checkAngle) < 10) {
                    this.successfulLanding = true;
                } else {
                    this.successfulLanding = false;
                }
                this.die();
            }
        }
    }

    refuelLander(terrain) {
        for (let i = 0; i < gasTanks.length; i++) {
            const gasTank = gasTanks[i];
            const dx = this.x - gasTank.x;
            const dy = this.y - gasTank.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < gasTankRadius + 25) {
                this.fuel += gasTankRefuelAmount;
                if (this.fuel > 100) this.fuel = 100;
                gasTanks.splice(i, 1);
                i--;

                // Add a new gas tank to the mountain
                const x = Math.random() * (canvas.width - gasTankRadius * 2) + gasTankRadius;
                const y = terrain.getY(x) - gasTankRadius;
                gasTanks.push({
                    x,
                    y
                });
                playRefuelSound();
            }
        }
    }

    checkTargetReached(target) {

        const distanceVector = new Vector(target.x - this.x, target.y - this.y);
        let targetReached = distanceVector.length() < 100;
        if (targetReached && !this.targetReached) {
            if (this.startTime == 0)
                this.startTime = performance.now();

            this.timeToReachTarget = performance.now() - this.startTime;
            if (this.timeToReachTarget > 3000) {
                this.targetReached = true;
            }
        } else if (!targetReached) {
            this.startTime = 0;
        }

        return this.targetReached;
    }

    calculateFitness(target) {
        if (!target)
            return;
        this.frameCount++;

        const distanceVector = new Vector(target.x - this.x, target.y - this.y);

        const distanceFitness = (1000 - distanceVector.length()) / 1000;

        const rotationPenaltyFactor = Math.abs(this.rotationSpeed) / maxRotationSpeed; // Apply penalty based on rotation speed

        this.neuralNetwork.currentFitness += distanceFitness - (rotationPenaltyFactor) * 0.8;
    }

    applyNeuralNetwork(target) {
        if (this.neuralNetwork.isDead)
            return;


        const spaceshipState = [this.x / canvas.width, (canvas.height - this.y) / canvas.height, this.angle % (Math.PI * 2), this.velocityX, this.velocityY];


        const distanceVector = new Vector((target.x - this.x) / canvas.width, (target.y - this.y) / canvas.height);
        const targetAngle = distanceVector.angle();

        const inputs = [...spaceshipState, distanceVector.length(), targetAngle.cos_angle, targetAngle.sin_angle];

        const [thrust, rotationAccel] = this.neuralNetwork.apply(inputs);
        this.rotationAccel = (rotationAccel - 0.5) * 2 * maxRotationAccel;
        this.thrust = thrust * maxThrustPower;


        let now = performance.now();
        if (!this.startTime)
            this.startTime = now;
        let deltaTime = now - this.startTime;
        // if (deltaTime > 30000) {
        //     this.die();
        // }
    }

    // getNearestMountainDistance(terrain) {
    //     const distanceArray = [];
    //     for (let x = 0; x < terrain.width; x++) {
    //         const y = terrain.getY(x);
    //         const distance = Math.sqrt((this.x - x) ** 2 + (this.y - y) ** 2);
    //         distanceArray.push(distance);
    //     }
    //     const nearestDistance = Math.min(...distanceArray);
    //     return nearestDistance;
    // }

    getNearestMountainDistance(terrain) {
        let left = 0;
        let right = terrain.terrainPoints.length - 1;
        let nearestIndex = -1;
        let nearestDistance = Number.POSITIVE_INFINITY;

        while (left <= right) {
            const mid = Math.floor((left + right) / 2);

            const distance = Math.abs(mid - this.x);

            if (distance < nearestDistance) {
                nearestIndex = mid;
                nearestDistance = distance;
            }

            if (mid < this.x) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        const nearestPoint = terrain.terrainPoints[nearestIndex];

        return nearestPoint;
    }



    getTerrainSlope(terrain) {
        const x = Math.round(this.x);
        const slope = terrain.getTerrainSlope(x);
        return slope;
    }

    getPlatformDistance(platform) {
        const dx = platform.x - this.x;
        const dy = platform.y - this.y;
        const distance = Math.sqrt(dx ** 2 + dy ** 2);
        return distance;
    }

    getPlatformAngle(platform) {
        const dx = platform.x - this.x;
        const dy = platform.y - this.y;
        const angle = Math.atan2(dy, dx);
        return angle;
    }

    getDescentSpeed() {
        const descentSpeed = this.velocityY;
        return descentSpeed;
    }

}