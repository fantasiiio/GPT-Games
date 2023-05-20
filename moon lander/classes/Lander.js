class Lander {
    constructor(x, y, neuralNetwork = null) {
        this.thrust = 0;
        this.maxFuel = 1000;
        this.fuel = this.maxFuel;
        this.neuralNetwork = neuralNetwork;
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
        this.rigidBody = new RigidBody(x / zoomLevel, y / zoomLevel, 50, 50);
        this.polygons = this.getLanderPolygons();
        let area = 0;
        for(let polygon of this.polygons){
            area += polygon.area();
        }
        this.rigidBody.mass = area / 1000;    
        this.rigidBody.calculateMomentOfInertia();
    }



    isCollidingWithMountains(terrain) {
        const x = this.rigidBody.position.x;
        const y = this.rigidBody.position.y + 25;
        return y >= terrain.getY(x);
    }

    updateLander() {
        this.fuel -= FuelConsumption_thrust * this.thrust;
        let force = new Vector(this.thrust * Math.sin(this.rigidBody.angle), gravity - (this.thrust * Math.cos(this.rigidBody.angle)));
        this.rigidBody.applyForce(force);
        this.rigidBody.update(force);
    }

    resetLander() {
        this.rigidBody.position.x = canvas.width / 2 / zoomLevel;
        this.rigidBody.position.y = 50;
        this.rigidBody.angle = 0;
        this.rigidBody.velocity.x = 0;
        this.rigidBody.velocity.y = 0;
        this.rigidBody.angularVelocity = 0;
        this.thrust = 0;
        this.fuel = this.maxFuel;
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
        ctx.translate(this.rigidBody.position.x, this.rigidBody.position.y);
        ctx.rotate(this.rigidBody.angle);

        // Draw this body
        ctx.beginPath();
        ctx.moveTo(-15, 15);
        ctx.quadraticCurveTo(-15, -15, 0, -30);
        ctx.quadraticCurveTo(15, -15, 15, 15);
        ctx.closePath();
        ctx.fillStyle = 'silver';
        ctx.fill();
        ctx.strokeStyle = 'gray';
        ctx.stroke();


        // Draw this windows
        ctx.beginPath();
        ctx.arc(0, -5, 6, 0, 2 * Math.PI);
        ctx.fillStyle = 'black';
        ctx.fill();
        ctx.stroke();

        // Draw this wings
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

        // Draw this thruster
        if (this.thrust > 0) {
            const thrusterHeight = 30;
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
            isNaN(this.rigidBody.position.x) || // Check if lander is not a number
            isNaN(this.rigidBody.position.y) || // Check if lander is not a number
            this.rigidBody.position.x < 0 || // Check if lander is left of the screen
            this.rigidBody.position.x > canvas.width / zoomLevel || // Check if lander is right of the screen
            this.rigidBody.position.y < 0 || // Check if lander is above the screen
            this.rigidBody.position.y > canvas.height / zoomLevel // Check if lander is below the screen
        );
    }
    die() {
        this.landed = true;
        this.velocityX = 0;
        this.velocityY = 0;
        this.neuralNetwork.isDead = true;
    }

    checkLanding() {
        const x = this.rigidBody.position.x;
        const y = this.rigidBody.position.y;
        if (this.isLanderOutOfScreen()) {
            this.die();
        } else {
            if (this.isCollidingWithMountains(terrain)) {
                let checkAngle = (this.rigidBody.angle + Math.PI / 2) % (2 * Math.PI);
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
            const dx = this.rigidBody.position.x - gasTank.x;
            const dy = this.rigidBody.position.y - gasTank.y;
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

        const distanceVector = new Vector(target.x - this.rigidBody.position.x, target.y - this.rigidBody.position.y);
        let targetReached = distanceVector.length() < 100;
        if (targetReached && !this.targetReached) {
            if (this.startTimeReached == 0)
                this.startTimeReached = performance.now();

            this.timeToReachTarget = performance.now() - this.startTimeReached;
            if (this.timeToReachTarget > 3000) {
                this.targetReached = true;
            }
        } else if (!targetReached) {
            this.startTimeReached = 0;
        }

        return this.targetReached;
    }

    calculateFitness(target) {
        if (!target)
            return;
        this.frameCount++;

        const distanceVector = new Vector(target.x - this.rigidBody.position.x, target.y - this.rigidBody.position.y);

        const distanceFitness = (1000 - distanceVector.length()) / 1000;

        const rotationPenaltyFactor = Math.abs(this.rigidBody.angularVelocity) / maxAngularVelocity; // Apply penalty based on rotation speed

        this.neuralNetwork.currentFitness += distanceFitness - (rotationPenaltyFactor) * 0.8;
    }

    applyNeuralNetwork(target) {
        if (this.neuralNetwork.isDead)
            return;


        const spaceshipState = [this.rigidBody.position.x / canvas.width, (canvas.height - this.rigidBody.position.y) / canvas.height, this.rigidBody.angle % (Math.PI * 2), this.rigidBody.velocity.x,  this.rigidBody.velocity.y];


        const distanceVector = new Vector((target.x - this.rigidBody.position.x) / canvas.width, (target.y - this.rigidBody.position.y) / canvas.height);
        const targetAngle = distanceVector.angle();

        const inputs = [...spaceshipState, distanceVector.length(), targetAngle.cos_angle, targetAngle.sin_angle];

        const [thrust, rotationAccel] = this.neuralNetwork.apply(inputs);
        this.rigidBody.applyTorque((rotationAccel - 0.5) * 2 * maxRotationAccel);
        this.thrust = thrust * maxThrustPower;


        let now = performance.now();
        if (!this.startTime)
            this.startTime = now;

            
        this.startTimeReached = 0;
        let deltaTime = now - this.startTime;
        if (deltaTime > 30000) {
            this.die();
        }
    }

    // getNearestMountainDistance(terrain) {
    //     const distanceArray = [];
    //     for (let x = 0; x < terrain.width; x++) {
    //         const y = terrain.getY(x);
    //         const distance = Math.sqrt((this.rigidBody.position.x - x) ** 2 + (this.rigidBody.position.y - y) ** 2);
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

            const distance = Math.abs(mid - this.rigidBody.position.x);

            if (distance < nearestDistance) {
                nearestIndex = mid;
                nearestDistance = distance;
            }

            if (mid < this.rigidBody.position.x) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        const nearestPoint = terrain.terrainPoints[nearestIndex];

        return nearestPoint;
    }



    getTerrainSlope(terrain) {
        const x = Math.round(this.rigidBody.position.x);
        const slope = terrain.getTerrainSlope(x);
        return slope;
    }

    getPlatformDistance(platform) {
        const dx = platform.x - this.rigidBody.position.x;
        const dy = platform.y - this.rigidBody.position.y;
        const distance = Math.sqrt(dx ** 2 + dy ** 2);
        return distance;
    }

    getPlatformAngle(platform) {
        const dx = platform.x - this.rigidBody.position.x;
        const dy = platform.y - this.rigidBody.position.y;
        const angle = Math.atan2(dy, dx);
        return angle;
    }

    getDescentSpeed() {
        const descentSpeed = this.velocityY;
        return descentSpeed;
    }

    getLanderPolygons() {
        let polygons = [];

        const center = {
            x: this.rigidBody.position.x,
            y: this.rigidBody.position.y
        };
        const angle = this.rigidBody.angle;

        const bodyVertices = [{
                x: this.rigidBody.position.x - 15,
                y: this.rigidBody.position.y + 15
            },
            {
                x: this.rigidBody.position.x,
                y: this.rigidBody.position.y - 30
            },
            {
                x: this.rigidBody.position.x + 15,
                y: this.rigidBody.position.y + 15
            }
        ];
        const rotatedBodyVertices = bodyVertices.map(vertex => this.rotatePoint(vertex, center, angle));
        polygons.push(new Polygon(rotatedBodyVertices));

        const leftWingVertices = [{
                x: this.rigidBody.position.x - 15,
                y: this.rigidBody.position.y + 15
            },
            {
                x: this.rigidBody.position.x - 25,
                y: this.rigidBody.position.y + 10
            },
            {
                x: this.rigidBody.position.x - 25,
                y: this.rigidBody.position.y + 30
            },
            {
                x: this.rigidBody.position.x - 15,
                y: this.rigidBody.position.y + 30
            }
        ];
        const rotatedLeftWingVertices = leftWingVertices.map(vertex => this.rotatePoint(vertex, center, angle));
        polygons.push(new Polygon(rotatedLeftWingVertices));

        const rightWingVertices = [{
                x: this.rigidBody.position.x + 15,
                y: this.rigidBody.position.y + 15
            },
            {
                x: this.rigidBody.position.x + 25,
                y: this.rigidBody.position.y + 10
            },
            {
                x: this.rigidBody.position.x + 25,
                y: this.rigidBody.position.y + 30
            },
            {
                x: this.rigidBody.position.x + 15,
                y: this.rigidBody.position.y + 30
            }
        ];
        const rotatedRightWingVertices = rightWingVertices.map(vertex => this.rotatePoint(vertex, center, angle));
        polygons.push(new Polygon(rotatedRightWingVertices));

        return polygons;
    }

    rotatePoint(point, center, angle) {
        const rotatedX = center.x + (point.x - center.x) * Math.cos(angle) - (point.y - center.y) * Math.sin(angle);
        const rotatedY = center.y + (point.x - center.x) * Math.sin(angle) + (point.y - center.y) * Math.cos(angle);
        return {
            x: rotatedX,
            y: rotatedY
        };
    }

    handleAsteroidCollision(asteroid) {
        // Get the polygons of the lander and asteroid
        const landerPolygons = this.getLanderPolygons();

        // Check for intersection between each pair of polygons
        for (const landerPolygon of landerPolygons) {
            const nearestPoint = landerPolygon.getNearestIntersection(asteroid.polygon);

            if (nearestPoint) {
                this.rigidBody.resolveCollision(asteroid.rigidBody);
            }
        }
    }

    // For navigation
    getNearestAsteroidPoint(asteroid) {
        let nearestPoint = null;
        let minDistance = Infinity;


        for (let i = 0; i < asteroid.vertices.length; i++) {
            const asteroidPoint = asteroid.vertices[i];
            let position = new Vector(this.rigidBody.position.x, this.rigidBody.position.y);
            const distance = position.distanceTo(asteroidPoint);

            if (distance < minDistance) {
                minDistance = distance;
                nearestPoint = asteroidPoint;
            }
        }

        return nearestPoint;
    }
    

}