class Lander {
    constructor(x, y, populationIndex, angle) {
        this.retartPosition = {
            x,
            y
        };
        this.populationIndex = populationIndex;
        this.thrust = 0;
        this.sideThrust = 0;
        this.angularAcceleration = 0;
        this.successfulLanding = false;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
        this.currentTime = 0;
        this.docked = false;
        this.cumulRotationPenaltyFactor = 0;
        this.frameCount = 0;
        this.target = null;
        this.targetIndex = -1;
        this.rigidBody = new RigidBody(x, y, 50, 50);
        this.rigidBody.angle = angle || 0;
        this.polygons = this.getLanderPolygons();
        let area = 0;
        this.fitnessMultiplier = 1;
        for (let polygon of this.polygons) {
            area += polygon.area();
        }
        this.rigidBody.mass = area / 1000;
        this.rigidBody.calculateMomentOfInertia();
        this.timeBonus = startingTimeBonus;
        //this.neuralNetwork.currentFitness = startingTimeBonus;
        this.neuralNetworks = {}; // Array to store multiple neural networks indexed by name
        this.currentActionName = "";

        this.harvestCapacity = 1000;
        this.harvestedResources = {};

        this.lasers = [];
        this.laserSpeed = 20;
        this.laserLifeTime = 100;
        this.laserCooldown = 0;
        this.laserCooldownTime = 50;
        this.laserEnergyCost = 20;
        this.laserLength = 30;
        this.laserDamage = 10;

        this.energyLevel = 100;
        this.energyRegainRate = 0.1;
        this.healthLevel = 100;

        this.shieldEnergyCost = 30;
        this.shieldCoolDown = 100;
        this.shieldActivatingTime = 200;
        this.shieldActive = false;
        this.shieldCooldownTimer = 0;
        this.shieldActivationTimer = 0;

        this.fuelConsumption = 0;
        this.fuelCapacity = 1000;
        this.fuelLevel = this.fuelCapacity;
        this.enemies = [];
        this.target = null;
        //this.enemies.push(new Enemy());
        this.chooseTargetMode = "nextTarget", "nearestTarget", "nearestEnemy", "nearestResource", "nearestAsteroid", "spaceStation"
    }

    setTarget(target) {
        this.target = target;
        this.changeTarget();
    }

    setTargetEnemy(enemy) {
        this.target = {
            position: enemy.rigidBody.position,
            velocity: enemy.rigidBody.velocity,
            targetType: "enemy"
        };
        this.changeTarget();
    }

    setTargetResource(resourceSpot) {
        let resource = resourceSpot.spot.resources[resourceSpot.resourceIndex];
        this.target = {
            position: {
                x: resource.position.x + resourceSpot.spot.position.x,
                y: resource.position.y + resourceSpot.spot.position.y
            },
            velocity: new Vector(0, 0),
            targetType: "resource"
        };
        this.changeTarget();
    }

    setTargetLaser(laser) {
        this.target = {
            position: laser.position,
            velocity: laser.velocity,
            targetType: "laser"
        };
        this.changeTarget();
    }

    setTargetSpaceStation(spaceStation) {
        this.target = {
            position: spaceStation.position,
            velocity: spaceStation.velocity,
            targetType: "spaceStation"
        };
        this.changeTarget();
    }

    addEnemy(enemy) {
        enemy.enemies.push(this);
        this.enemies.push(enemy);
    }

    activateShield() {
        if (this.energyLevel >= this.shieldEnergyCost && !this.shieldActive && this.shieldCooldownTimer === 0) {
            this.shieldActive = true;
            this.shieldActivationTimer = this.shieldActivatingTime;
            this.energyLevel -= this.shieldEnergyCost;
        }
    }

    updateShield() {
        if (this.shieldActive) {
            this.shieldActivationTimer--;

            if (this.shieldActivationTimer === 0) {
                this.shieldActive = false;
                this.shieldCooldownTimer = this.shieldCoolDown;
            }
        } else if (this.shieldCooldownTimer > 0) {
            this.shieldCooldownTimer--;
        }
    }

    fireLaser() {
        if (this.energyLevel < this.laserEnergyCost || this.laserCooldownTimer > 0) {
            return; // Cannot fire laser due to insufficient energy or cooldown in progress
        }
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        this.energyLevel -= this.laserEnergyCost;
        const laser = {
            position: new Vector(this.rigidBody.position.x, this.rigidBody.position.y),
            end: new Vector(this.rigidBody.position.x - facingDirection.x * this.laserLength, this.rigidBody.position.y - facingDirection.y * this.laserLength),
            direction: facingDirection,
            velocity: facingDirection.multiply(this.laserSpeed),
            life: 0,
        };

        this.lasers.push(laser);
        this.laserCooldownTimer = this.laserCooldownTime; // Start the cooldown timer
    }


    removeLaser(index) {
        this.lasers.splice(index, 1);
    }

    setActiveNeuralNetwork(name) {
        this.neuralNetwork = this.neuralNetworks[name];
        if (geneticAlgorithm)
            geneticAlgorithm.population[this.populationIndex] = this.neuralNetwork;
        this.currentActionName = name;
    }

    // Method to add a neural network
    addNeuralNetwork(network, name) {
        this.neuralNetworks[name] = network;
    }

    // Method to get a neural network for a specific task
    getNeuralNetwork(name) {
        return this.neuralNetworks[name];
    }

    isCollidingWithMountains(terrain) {
        return false;
        const x = this.rigidBody.position.x;
        const y = this.rigidBody.position.y + 25;
        return y >= terrain.getY(x);
    }

    getLastTargetDistance() {
        let lastTarget = targets[targets.length - 1];
        const distanceVector = new Vector(lastTarget.position.x - this.rigidBody.position.x, lastTarget.position.y - this.rigidBody.position.y);
        return distanceVector.length();
    }

    checkChangeAction() {
        if (this.targetIndex == targets.length - 1) {
            let lastTargetDistance = this.getLastTargetDistance();
            if (lastTargetDistance < 1000) {
                this.setActiveNeuralNetwork("stop");
            }
        }
    }

    updateLasers() {
        for (let i = this.lasers.length - 1; i >= 0; i--) {
            const laser = this.lasers[i];
            laser.life++;
            if (laser.life > this.laserLifeTime) {
                this.lasers.splice(i, 1);
            }
            laser.position = laser.position.add(laser.velocity)
            laser.end = laser.position.subtract(laser.direction.multiply(this.laserLength));
        }
    }

    updateEnemies() {
        for (let enemy of this.enemies) {
            enemy.update(this);
            enemy.handleCollision();
        }
    }

    updateLander() {
        if (!this.isEnemy)
            this.updateEnemies();

        // Update the cooldown timer
        if (this.laserCooldownTimer > 0) {
            this.laserCooldownTimer--;
        }


        // fuel consumption is calculated based on the thrust and angular acceleration
        this.fuelConsumption = 0;
        this.fuelConsumption += FuelConsumption_thrust * (this.thrust / maxThrustPower);
        this.fuelConsumption += FuelConsumption_rotate * (Math.abs(this.angularAcceleration) / maxRotationAccel);
        this.fuelConsumption += FuelConsumption_sideThrust * (this.sideThrust / maxSideThrustPower);
        this.fuelLevel -= this.fuelConsumption;
        if (this.fuelLevel < 0)
            this.fuelLevel = 0;

        if (this.fuelLevel > 0) {
            let force = new Vector(this.thrust * Math.sin(this.rigidBody.angle), gravity - (this.thrust * Math.cos(this.rigidBody.angle)));
            let sideForce = new Vector(this.sideThrust * Math.sin(this.rigidBody.angle + Math.PI / 2), gravity - (this.sideThrust * Math.cos(this.rigidBody.angle + Math.PI / 2)));
            this.rigidBody.applyForce(force);
            this.rigidBody.applyForce(sideForce);
            this.rigidBody.applyTorque(this.angularAcceleration);
        } else { // No fuel left
            this.thrust = 0;
            this.sideThrust = 0;
            this.angularAcceleration = 0;
        }
        this.rigidBody.update();

        this.lastSpaceshipStates = this.spaceshipStates;
        if (!this.neuralNetwork.isDead)
            this.spaceshipStates = this.calculateStates(this.target, asteroids);
        //this.spaceshipStates = [...this.spaceshipStates, this.thrust, this.angularAcceleration]
        if (!this.lastSpaceshipStates)
            this.lastSpaceshipStates = this.spaceshipStates;

        this.updateLasers();

        this.updateShield();

        if (!this.shieldActive && this.energyLevel < 100) {
            this.energyLevel += this.energyRegainRate;
        }

        if (this.healthLevel <= 0 && !this.neuralNetwork.isDead) {
            this.die();
            this.explosion = new Explosion(this.rigidBody.position.x, this.rigidBody.position.y, ctx);
        }
        if (this.explosion) {
            this.explosion.update();
            if (this.explosion.isDone()) {}
        }
    }

    resetLander() {
        this.rigidBody.position.x = targets[0].position.x;
        this.rigidBody.position.y = targets[0].position.y + 1;
        this.rigidBody.velocity.x = 0;
        this.rigidBody.velocity.y = 0;
        this.rigidBody.angularVelocity = 0;
        this.rigidBody.angle = targets[0].startAngle || 0;

        this.thrust = 0;
        this.fuelConsumption = 0;
        this.successfulLanding = false;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
        this.currentTime = 0;
        this.docked = false;
        this.cumulRotationPenaltyFactor = 0;
        this.frameCount = 0;
        this.target = null;
        this.targetIndex = -1;
        this.neuralNetwork.currentFitness = startingTimeBonus;
        this.fitnessMultiplier = 1;
        this.timeBonus = startingTimeBonus;
        this.harvestCount = 0;
        this.harvestedResources = {};
        for (let name in this.neuralNetworks)
            this.neuralNetworks[name].isDead = false;

        this.energyLevel = 100;
        this.fuelLevel = this.fuelCapacity;
        this.healthLevel = 100;
        this.setTarget(targets[0]);
    }

    changeTarget() {
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTimeReached = 0;
    }

    drawLasers() {
        ctx.strokeStyle = "red";
        ctx.lineWidth = 5;

        for (let i = 0; i < this.lasers.length; i++) {
            const laser = this.lasers[i];

            ctx.beginPath();
            ctx.moveTo(laser.position.x, laser.position.y);
            ctx.lineTo(laser.end.x, laser.end.y);
            ctx.stroke();
        }
    }

    drawBars() {
        // Draw Health bar
        ctx.save();
        ctx.translate(this.rigidBody.position.x + 50, this.rigidBody.position.y - 50);
        ctx.strokeStyle = 'white';
        ctx.strokeRect(0, 0, 10, 100); // Total health bar
        ctx.fillStyle = 'green';
        ctx.fillRect(0, 100, 10, -this.healthLevel); // Current health

        // Draw Energy bar
        ctx.translate(15, 0); // Move 15 units right from health bar
        ctx.strokeStyle = 'white';
        ctx.strokeRect(0, 0, 10, 100); // Total energy bar
        ctx.fillStyle = '#E275AD';
        ctx.fillRect(0, 100, 10, -this.energyLevel); // Current energy

        // Draw Energy bar
        ctx.translate(15, 0); // Move 15 units right from Energy bar
        ctx.strokeStyle = 'white';
        ctx.strokeRect(0, 0, 10, 100); // Total energy bar
        ctx.fillStyle = 'yellow';
        ctx.fillRect(0, 100, 10, -(this.fuelLevel / this.fuelCapacity) * 100); // Current energy

        ctx.restore();


    }


    getResourcesCount() {
        let count = 0;
        let obj = this.harvestedResources
        for (let key in obj) {
            if (obj.hasOwnProperty(key) && Array.isArray(obj[key])) {
                count += obj[key].length;
            }
        }
        return count;
    }

    drawLander() {
        if (!this.isEnemy) {
            for (let enemy of this.enemies) {
                enemy.drawLander();
            }
        }

        if (this.explosion) {
            return;
        }

        ctx.save();
        ctx.translate(this.rigidBody.position.x, this.rigidBody.position.y);

        let rocketColor = 'silver';
        if (this.isEnemy)
            rocketColor = '#CB9EFB';

        if (this.neuralNetwork.positionNumber) {
            if (this.neuralNetwork.positionNumber <= 10)
                ctx.fillStyle = 'yellow';
            else
                ctx.fillStyle = 'white';

            ctx.font = '40px Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(this.neuralNetwork.positionNumber + "(" + this.neuralNetwork.currentFitness.toFixed() + ")", 100, -30);

            ctx.moveTo(0, 15);
            ctx.font = '20px Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            if (this.currentActionName == "harvest")
                ctx.fillText(this.currentActionName + " (" + this.getResourcesCount() + ")", 100, 15);
            else
                ctx.fillText(this.currentActionName, 100, 15);

            ctx.moveTo(0, -15);
            ctx.font = '20px Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(this.chooseTargetMode, 100, 40);

            //ctx.fillText(this.neuralNetwork.positionNumber, 50, 0);
        }

        ctx.rotate(this.rigidBody.angle);

        // Draw this body
        ctx.beginPath();
        ctx.moveTo(-15, 15);
        ctx.quadraticCurveTo(-15, -15, 0, -30);
        ctx.quadraticCurveTo(15, -15, 15, 15);
        ctx.closePath();
        ctx.fillStyle = rocketColor;
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
        ctx.fillStyle = rocketColor;
        ctx.fill();
        ctx.strokeStyle = 'gray';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(15, 15);
        ctx.quadraticCurveTo(25, 10, 25, 30);
        ctx.lineTo(15, 30);
        ctx.closePath();
        ctx.fillStyle = rocketColor;
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
        } else if (this.thrust < 0) {
            const thrusterHeight = 30;
            const adjustedThrusterHeight = thrusterHeight * (this.thrust / maxThrustPower);
            ctx.beginPath();
            ctx.moveTo(-5, -25);
            ctx.lineTo(0, -25 + adjustedThrusterHeight);
            ctx.lineTo(5, -25);
            ctx.closePath();
            ctx.fillStyle = 'red';
            ctx.fill();
            ctx.strokeStyle = 'red';
            ctx.stroke();
        }

        // Draw rotation thruster
        if (this.angularAcceleration < 0) {
            const thrusterWidth = 20;
            const adjustedThrusterWidth = thrusterWidth * (this.angularAcceleration / maxRotationAccel);
            ctx.beginPath();
            ctx.moveTo(-25, 30); // Starting point is at the end of the left wing
            ctx.lineTo(-25 + adjustedThrusterWidth, 25);
            ctx.lineTo(-25, 20);
            ctx.closePath();
            ctx.fillStyle = 'red'; // Choose a different color to distinguish side thrusters
            ctx.fill();
            ctx.strokeStyle = 'red';
            ctx.stroke();
        } else if (this.angularAcceleration > 0) {
            const thrusterWidth = 20;
            const adjustedThrusterWidth = thrusterWidth * (this.angularAcceleration / maxRotationAccel);
            ctx.beginPath();
            ctx.moveTo(25, 30); // Starting point is at the end of the right wing
            ctx.lineTo(25 + adjustedThrusterWidth, 25);
            ctx.lineTo(25, 20);
            ctx.closePath();
            ctx.fillStyle = 'red'; // Choose a different color to distinguish side thrusters
            ctx.fill();
            ctx.strokeStyle = 'red';
            ctx.stroke();
        }


        // Draw side thruster
        if (this.sideThrust > 0) {
            const thrusterWidth = 30;
            const adjustedThrusterWidth = thrusterWidth * (this.sideThrust / maxThrustPower);
            ctx.beginPath();
            ctx.moveTo(-15, 15);
            ctx.lineTo(-15 - adjustedThrusterWidth, 10);
            ctx.lineTo(-15, 5);
            ctx.closePath();
            ctx.fillStyle = '#03C03C'; // Choose a different color to distinguish side thrusters
            ctx.fill();
            ctx.strokeStyle = '#03C03C';
            ctx.stroke();
        } else if (this.sideThrust < 0) {
            const thrusterWidth = 30;
            const adjustedThrusterWidth = thrusterWidth * (this.sideThrust / maxThrustPower);
            ctx.beginPath();
            ctx.moveTo(15, 15);
            ctx.lineTo(15 - adjustedThrusterWidth, 10);
            ctx.lineTo(15, 5);
            ctx.closePath();
            ctx.fillStyle = '#03C03C'; // Choose a different color to distinguish side thrusters
            ctx.fill();
            ctx.strokeStyle = '#03C03C';
            ctx.stroke();
        }

        if (this.shieldActive) {
            // Draw shield
            ctx.beginPath();
            ctx.arc(0, 0, 50, 0, 2 * Math.PI);
            ctx.strokeStyle = 'lightblue';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.stroke();
            ctx.closePath();
        }

        ctx.restore();

        this.drawBars();
        this.drawLasers();
    }



    isLanderOutOfScreen() {
        return false;
        // return (
        //     isNaN(this.rigidBody.position.x) || // Check if lander is not a number
        //     isNaN(this.rigidBody.position.y) || // Check if lander is not a number
        //     this.rigidBody.position.x < 0 || // Check if lander is left of the screen
        //     this.rigidBody.position.x > canvas.width / zoomLevel || // Check if lander is right of the screen
        //     this.rigidBody.position.y < 0 || // Check if lander is above the screen
        //     this.rigidBody.position.y > canvas.height / zoomLevel // Check if lander is below the screen
        // );
    }
    die() {
        this.rigidBody.velocityX = 0;
        this.rigidBody.velocityY = 0;
        this.rigidBody.angularVelocity = 0;
        this.thrust = 0;
        this.sideThrust = 0;
        this.angularAcceleration = 0;
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

    getNearestResourceSpotIndex() {
        let nearestresourcesSpot = null;
        let nearestDistance = Infinity;
        for (let resourcesSpot of resourcesSpots) {
            let dx = this.rigidBody.position.x - resourcesSpot.position.x;
            let dy = this.rigidBody.position.y - resourcesSpot.position.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < nearestDistance) {
                nearestDistance = distance;
                nearestresourcesSpot = resourcesSpot;
            }
        }
        return resourcesSpots.indexOf(nearestresourcesSpot);
    }

    harvestResource() {
        let closestResourceIndex = null;
        let minDistance = Number.MAX_SAFE_INTEGER;

        let nearestresourcesSpotIndex = this.getNearestResourceSpotIndex();
        let nearestresourcesSpot = resourcesSpots[nearestresourcesSpotIndex];
        if (!nearestresourcesSpot)
            return null;
        for (let i = 0; i < nearestresourcesSpot.resources.length; i++) {
            const resource = nearestresourcesSpot.resources[i];
            const dx = this.rigidBody.position.x - (resource.position.x + nearestresourcesSpot.position.x);
            const dy = this.rigidBody.position.y - (resource.position.y + nearestresourcesSpot.position.y);
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (!this.harvestedResources[nearestresourcesSpotIndex])
                this.harvestedResources[nearestresourcesSpotIndex] = [];

            let resources = this.harvestedResources[nearestresourcesSpotIndex];

            if (distance < nearestresourcesSpot.resourceRadius + 25) {
                if (resources.length < this.harvestCapacity && !resources.includes(i)) {
                    resources.push(i);
                    this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnResourceHarvested"]);
                    if (this.target && this.target.position == resource.position)
                        this.target = null;
                }
            }

            // If this resource is closer than the current closest resource, update closestResourceIndex and minDistance
            if (distance < minDistance && !resources.includes(i)) {
                minDistance = distance;
                closestResourceIndex = i;
                this.nearestResource = resource;
            }
        }

        return {
            spot: nearestresourcesSpot,
            resourceIndex: closestResourceIndex
        };
    }

    nextTarget() {
        if (this.targetReached || !this.target) {
            this.targetIndex++;
            if (cycleTargets) {
                this.targetIndex %= targets.length;
            } else {
                if (this.targetIndex >= targets.length) {
                    this.targetIndex = targets.length - 1;
                }
            }
            this.setTarget(targets[this.targetIndex]);
        }
    }

    checkTargetReached() {
        const target = this.target;
        if (!target)
            return true;
        const distanceVector = new Vector(target.position.x - this.rigidBody.position.x, target.position.y - this.rigidBody.position.y);
        let targetReached = distanceVector.length() < targetRadius;
        if (targetReached && !this.targetReached) {
            if (this.startTimeReached == 0)
                this.startTimeReached = performance.now();

            this.timeToReachTarget = performance.now() - this.startTimeReached;
            if (this.timeToReachTarget > 20 && targets.length > 1) {
                this.targetReached = true;
                this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnTargetReached"]);
                this.target = null;
                //nextTarget();
            }
        } else if (!targetReached) {
            this.startTimeReached = 0;
        }

        return this.targetReached;
    }

    checkTargetModes() {
        if (!this.target)
            return;
        // Check if target is activated (within radius) and if so, change the action to the target action
        const distanceVector = new Vector(this.target.position.x - this.rigidBody.position.x, this.target.position.y - this.rigidBody.position.y);
        let targetActivated = distanceVector.length() < (this.target.activateRadius || 1000);
        if (targetActivated) {
            let resetTarget = false;
            if (this.target.targetMode && this.chooseTargetMode != this.target.targetMode) {
                this.chooseTargetMode = this.target.targetMode;
                resetTarget = true;
            }
            if (this.target.action && this.currentActionName != this.target.action)
                this.setActiveNeuralNetwork(this.target.action);

            if (resetTarget) {
                // Reset target
                this.targetIndex = -1;
                this.target = null;
            }

        }
    }

    checkTargets() {
        if (this.chooseTargetMode == "spaceStation")
            this.target = spaceStation.dockPosition;
        else if (this.chooseTargetMode == "nextTarget") {
            if (this.checkTargetReached()) {
                this.nextTarget();
            }
        } else if (this.chooseTargetMode == "nearestEnemy") {
            if (!this.target) {
                let enemy = this.getNearestEnemy();
                this.target = enemy.rigidBody.position;
            }
        } else if (this.chooseTargetMode == "nearestResource") {
            let closestResource = this.harvestResource();
            if (closestResource) {
                this.setTargetResource(closestResource)
            }
        }
    }

    wrapAroundAngle(angle) {
        while (angle < -Math.PI) angle += 2 * Math.PI;
        while (angle > Math.PI) angle -= 2 * Math.PI;
        return angle;
    }

    calculatePredictionError(predictionModel) {
        // Get the model's prediction for the next state
        let predictedNextState = predictionModel.predict(this.lastSpaceshipStates);

        // Calculate the difference between the predicted and actual next states
        let predictionError = [];
        for (let i = 0; i < predictedNextState.length; i++) {
            predictionError[i] = this.spaceshipStates[i] - predictedNextState[i];
        }

        // Calculate the mean squared error
        let mse = 0;
        for (let error of predictionError) {
            mse += error * error;
        }
        mse /= predictionError.length;

        return mse;
    }

    // function that check if trajectory line is intersecting with target
    checkTrajectoryIntersectTarget(target) {
        const trajectoryLine = {
            start: this.rigidBody.position,
            end: this.rigidBody.position.add(this.rigidBody.velocity.normalize().multiply(10000)) // multiply by 10000 to extend the line
        };
        const targetCircle = {
            center: new Vector(target.position.x, target.position.y),
            radius: targetRadius
        };
        const intersection = IntersectionUtil.lineCircleIntersection(trajectoryLine.start, trajectoryLine.end, targetCircle.center, targetCircle.radius);
        return intersection;
    }

    calculateFitness_race(target, predictionModel) {
        if (!target)
            return;
        this.frameCount++;

        if (!this.targetReached) {
            if (this.frameCount > startingTimeBonus)
                this.timeBonus--; // time bonus is reduced by 1 more if target is not reached before startingTimeBonus
            this.timeBonus--;
        }
        // Calculate the vector pointing from the spaceship to the target
        let distanceVector = new Vector(target.position.x - this.rigidBody.position.x, target.position.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate distance fitness based on the normalized distance to the target
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / maxDistance);

        // Normalize the distance vector
        let distanceVectorNormal = new Vector(distanceVector.x, distanceVector.y).normalize();

        let velocityDotProduct = 0;
        let velocityScore;
        let facingDotProduct;
        let facingReward = 0;
        let trajectoryBonus = 0;
        if (this.rigidBody.velocity.length() == 0) {
            velocityScore = 0;
        } else {
            // Check if the spaceship is moving toward the target
            velocityDotProduct = this.rigidBody.velocity.normalize().dot(distanceVectorNormal);
            velocityScore = velocityDotProduct;

            if (this.checkTrajectoryIntersectTarget(target))
                trajectoryBonus = 2;

            // Check if the spaceship is facing the target
            facingDotProduct = facingDirection.dot(distanceVectorNormal);
            facingReward = facingDotProduct;
        }

        // Calculate rotation penalty based on the spaceship's angular velocity
        const rotationPenaltyFactor = Math.abs(this.rigidBody.angularVelocity) / maxAngularVelocity;

        // Calculate thrust penalty based on the spaceship's thrust
        let thrustPenaltyFactor = Math.abs(this.thrust) / maxThrustPower;
        if (this.targetReached)
            thrustPenaltyFactor *= 10;

        // Update the current fitness of the neural network by combining various factors
        this.neuralNetwork.currentFitness += (distanceFitness + facingReward * 5 + velocityScore) - (rotationPenaltyFactor * 5 + thrustPenaltyFactor * 0.2);
    }

    distanceFromLineToPoint(lineStart, lineEnd, point) {
        const {
            x: x1,
            y: y1
        } = lineStart;
        const {
            x: x2,
            y: y2
        } = lineEnd;
        const {
            x: x0,
            y: y0
        } = point;

        const numerator = Math.abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1));
        const denominator = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);

        return numerator / denominator;
    }


    checkDocking() {
        return false;
        if (this.docked)
            return;
        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));
        let angleDelta = Vector.angleBetweenVectors(facingDirection, spaceStation.dockAlignment)

        if (this.rigidBody.position.distanceTo(spaceStation.dockPosition) < 50 && angleDelta < 5 * (Math.PI / 180) && this.rigidBody.velocity.length() < 1) {
            this.rigidBody.position = spaceStation.dockPosition.add(spaceStation.dockAlignment.multiply(30));
            this.rigidBody.angle = spaceStation.dockAlignment.angle() + Math.PI;
            this.docked = true;
            this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnDocked"]);
            this.die();
        }
    }

    calculateFitness_docking() {
        this.frameCount++;

        // if (!this.targetReached) {
        //     if (this.frameCount > startingTimeBonus)
        //         this.neuralNetwork.currentFitness--; // time bonus is reduced by 1 more if target is not reached before startingTimeBonus
        //     this.neuralNetwork.currentFitness--;
        // }

        // Calculate the vector pointing from the spaceship to the target
        let distanceVector = new Vector(spaceStation.dockPosition.x - this.rigidBody.position.x, spaceStation.dockPosition.y - this.rigidBody.position.y);

        // Calculate distance fitness based on the normalized distance to the target
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / maxDistance);


        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate rotation penalty based on the spaceship's angular velocity
        const rotationPenaltyFactor = Math.abs(this.rigidBody.angularVelocity) / maxAngularVelocity;

        // Calculate the alignment with the docking port (dot product)
        let angleAlignmentScore = spaceStation.dockAlignment.dot(facingDirection);
        let positionAlignmentPenality = this.distanceFromLineToPoint(spaceStation.dockPosition, spaceStation.dockPosition.add(spaceStation.dockAlignment), this.rigidBody.position) / 1000;

        // Get the spaceship's speed
        let speed = this.rigidBody.velocity.length();

        // Calculate the fitness
        this.neuralNetwork.currentFitness += distanceFitness + angleAlignmentScore - (rotationPenaltyFactor * 5 + positionAlignmentPenality * 2 + speed * 0.1);
    }

    calculateFitness_stop() {
        let target = this.target;
        if (!target)
            return;
        this.frameCount++;

        if (!this.targetReached) {
            if (this.frameCount > startingTimeBonus)
                this.timeBonus--; // time bonus is reduced by 1 more if target is not reached before startingTimeBonus
            this.timeBonus--;
        }
        // Calculate the vector pointing from the spaceship to the target
        let distanceVector = new Vector(target.position.x - this.rigidBody.position.x, target.position.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate distance fitness based on the normalized distance to the target
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / maxDistance);

        // Normalize the distance vector
        let distanceVectorNormal = new Vector(distanceVector.x, distanceVector.y).normalize();

        let velocityDotProduct = 0;
        let velocityScore;
        let facingDotProduct;
        let facingReward = 0;
        let trajectoryBonus = 0;
        if (this.rigidBody.velocity.length() == 0) {
            velocityScore = 0;
        } else {
            // Check if the spaceship is moving toward the target
            velocityDotProduct = this.rigidBody.velocity.normalize().dot(distanceVectorNormal);
            velocityScore = velocityDotProduct;

            if (this.checkTrajectoryIntersectTarget(target))
                trajectoryBonus = 2;

            // Check if the spaceship is facing the target
            facingDotProduct = facingDirection.dot(distanceVectorNormal);
            facingReward = facingDotProduct;
        }

        // Calculate rotation penalty based on the spaceship's angular velocity
        const rotationPenaltyFactor = Math.abs(this.rigidBody.angularVelocity) / maxAngularVelocity;

        // Calculate thrust penalty based on the spaceship's thrust
        let thrustScore = 1 - Math.abs(this.thrust) / maxThrustPower;
        let speedScore = 0;
        if (this.targetReached) {
            speedScore = Math.max(1 - this.rigidBody.velocity.length() / 10, 1);
        }


        // Update the current fitness of the neural network by combining various factors
        this.neuralNetwork.currentFitness += (distanceFitness * 4 + facingReward * 5 + velocityScore + speedScore + thrustScore) - (rotationPenaltyFactor * 5);
    }

    calculateFitness() {
        if (enableManualControl)
            return;

        let fitness = 0;

        let fitnessInputs = nnConfigs[this.currentActionName].fitness;
        let inputIndex = 1;

        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));
        let distanceVector = new Vector(this.target.position.x - this.rigidBody.position.x, this.target.position.y - this.rigidBody.position.y);
        let distanceVectorNormal = new Vector(distanceVector.x, distanceVector.y).normalize();

        for (let input of fitnessInputs) {
            if (!input.checked) {
                inputIndex++;
                continue;
            }
            let value;

            switch (inputIndex++) {
                case 1:
                    value = Math.max(0, 1 - distanceVector.length() / maxDistance);
                    break;
                case 2:
                    value = facingDirection.dot(distanceVectorNormal);
                    break;
                case 3:
                    if (this.rigidBody.velocity.length() == 0)
                        value = 0;
                    else
                        value = this.rigidBody.velocity.normalize().dot(distanceVectorNormal);
                    break;
                case 4:
                    value = Math.abs(this.rigidBody.angularVelocity) / maxAngularVelocity;
                    break;
                case 5:
                    value = Math.abs(this.thrust) / maxThrustPower;
                    break;
                case 6:
                    if (this.targetReached) {
                        value = Math.max(1 - this.rigidBody.velocity.length() / 10, 1);
                    } else
                        value = 0;
                    break;
                case 7:
                    value = 1 - Math.abs(this.thrust) / maxThrustPower;
                    break;
                case 8:
                    value = spaceStation.dockAlignment.dot(facingDirection);
                    break;
                case 9:
                    value = 1 - this.distanceFromLineToPoint(spaceStation.dockPosition, spaceStation.dockPosition.add(spaceStation.dockAlignment), this.rigidBody.position) / 1000;
                    break;
                case 10:
                    value = this.rigidBody.velocity.length();
                    break;
                case 11:
                    value = this.fuelLevel / this.fuelCapacity;
                    break;
                default:
                    break;
            }

            fitness += value * input.multiplyFactor;
        };

        this.neuralNetwork.currentFitness += fitness;
    }


    // calculate the rate of change of θ
    compute_dtheta_dt(x, y, vx, vy) {
        // compute distance from origin
        var r = Math.sqrt(x * x + y * y);

        // compute unit tangential vector
        var unit_tangential_vector = {
            x: -y / r,
            y: x / r
        };

        // compute dθ/dt
        var dtheta_dt = vx * unit_tangential_vector.x + vy * unit_tangential_vector.y;

        return dtheta_dt;
    }

    // calculate the rate of change of r
    compute_dr_dt(x, y, vx, vy) {
        // compute distance from origin
        var r = Math.sqrt(x * x + y * y);

        // compute unit radial vector
        var unit_radial_vector = {
            x: x / r,
            y: y / r
        };

        // compute dr/dt
        var dr_dt = vx * unit_radial_vector.x + vy * unit_radial_vector.y;

        return dr_dt;
    }

    // Function to calculate velocity in polar coordinates
    velocityInPolarCoordinates(r, dr_dt, dtheta_dt) {
        var v_r = dr_dt; // radial velocity
        var v_theta = r * dtheta_dt; // tangential velocity
        return {
            v_r: v_r,
            v_theta: v_theta
        };
    }

    calculateCosSinAngle(vector1, vector2) {
        const dotProduct = vector1.dot(vector2);
        const magnitudeProduct = vector1.length() * vector2.length();

        const cosAngle = dotProduct / magnitudeProduct;
        const sinAngle = vector1.cross(vector2) / magnitudeProduct;

        return {
            cos_angle: cosAngle,
            sin_angle: sinAngle
        };
    }
    // function that cast Cast 5 rays in 180 degree arc in front of the spaceship and returns an array of distances to the nearest asteroids
    getRayDistances(asteroids, walls, numRays = numRadarRays, rayAngle = Math.PI, rayLength = 1000) {
        const rayDistances = [];

        for (let i = 0; i < numRays; i++) {
            // Calculate the angle of the spaceship's body
            let bodyAngle = this.rigidBody.angle;
            bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;
            // Calculate the current ray
            const angle = bodyAngle - rayAngle / 2 + (rayAngle / (numRays - 1)) * i;
            const rayDirection = new Vector(Math.cos(angle), Math.sin(angle));
            const ray = {
                start: this.rigidBody.position,
                end: this.rigidBody.position.add(rayDirection.multiply(rayLength))
            };
            let minDistance = Infinity;

            for (let asteroid of asteroids) {
                const intersection = asteroid.polygon.getNearestRayIntersection(ray);
                if (intersection) {
                    //drawPoint(intersection.point);
                    const distance = this.rigidBody.position.distanceTo(intersection.point);

                    if (distance < minDistance) {
                        minDistance = distance;
                    }
                }
            }

            // Check for intersections with walls
            for (let wall of walls) {
                const wallPolygon = new Polygon(wall);
                const intersection = wallPolygon.getNearestRayIntersection(ray, false);
                if (intersection) {
                    drawPoint(intersection.point);
                    const distance = this.rigidBody.position.distanceTo(intersection.point);
                    if (distance < minDistance) {
                        minDistance = distance;
                    }
                }
            }

            if (minDistance == Infinity) {
                minDistance = rayLength;
            }

            rayDistances.push(minDistance / rayLength);
        }

        return rayDistances;
    }

    calculateStates2(target, asteroids) {
        if (this.neuralNetwork.isDead)
            return;

        // Calculate the vector pointing from the spaceship to the target
        const deltaTarget = new Vector(target.position.x - this.rigidBody.position.x, target.position.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;
        const headingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate the cosine and sine of the angle between the spaceship's heading and the target direction
        const targetAngle = this.calculateCosSinAngle(deltaTarget, headingDirection);


        let r = Math.max(1, deltaTarget.length() / maxDistance);

        // Calculate the velocity in polar coordinates relative to the target
        const dr_dt = this.compute_dr_dt(-deltaTarget.x, -deltaTarget.y, this.rigidBody.velocity.x, this.rigidBody.velocity.y);
        const dtheta_dt = this.compute_dtheta_dt(-deltaTarget.x, -deltaTarget.y, this.rigidBody.velocity.x, this.rigidBody.velocity.y);
        const velocity = this.velocityInPolarCoordinates(r, dr_dt, dtheta_dt);

        // Find the nearest asteroid and calculate the angle and distance to it
        let radar = this.getRayDistances(asteroids, walls, numRadarRays);

        // Gather the spaceship states including position, velocity, target information, and asteroid information
        const spaceshipStates = [
            Math.cos(this.rigidBody.angle), // x-component of spaceship's body angle
            Math.sin(this.rigidBody.angle), // y-component of spaceship's body angle
            this.rigidBody.angularVelocity / maxAngularVelocity, // normalized angular velocity
            r, // normalized target distance
            velocity.v_r, // radial velocity
            velocity.v_theta, // angular velocity
            targetAngle.cos_angle, // cosine of angle between heading and target direction
            targetAngle.sin_angle, // sine of angle between heading and target direction
            ...radar, // normalized distances to nearest asteroids
            projectileAngle.cos_angle, // cosine of angle between heading and projectile direction
            projectileAngle.sin_angle, // sine of angle between heading and projectile direction
            projectileDistance, // normalized distance to nearest projectile
            projectile.v_r, // radial velocity of nearest projectile
            projectile.v_theta, // angular velocity of nearest projectile
        ];

        return spaceshipStates;
    }

    getNearestLaserInfo() {
        let nearestLaser = null;
        let minDistance = Infinity;
        let laserDirection = null;

        for (let enemy of this.enemies) {
            // Find nearest laser
            for (let laser of enemy.lasers) {
                // Calculate the distance from both endpoints of the laser to the spaceship, use the minimum of the two
                let dx1 = this.rigidBody.position.x - laser.position.x;
                let dy1 = this.rigidBody.position.y - laser.position.y;
                let distance1 = Math.sqrt(dx1 * dx1 + dy1 * dy1);

                let dx2 = this.rigidBody.position.x - laser.end.x;
                let dy2 = this.rigidBody.position.y - laser.end.x;
                let distance2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

                let distance = Math.min(distance1, distance2);
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestLaser = laser;
                    laserDirection = new Vector(dx1, dy1).normalize();
                }
            }
        }

        if (!nearestLaser) {
            return null; // No lasers found
        }

        return nearestLaser;


    }

    getNearestEnemy() {
        let nearestEnemy = null;
        let nearestDistance = Infinity;
        for (let enemy of enemies) {
            if (enemy.isDead)
                continue;
            let dx = this.rigidBody.position.x - enemy.rigidBody.position.x;
            let dy = this.rigidBody.position.y - enemy.rigidBody.position.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < nearestDistance) {
                nearestDistance = distance;
                nearestEnemy = enemy;
            }
        }
        return nearestEnemy;
    }

    getTargetedEnemy() {
        for (let enemy of this.enemies) {
            if (enemy.rigidBody.position == this.target.position)
                return enemy;
        }
        return null;
    }

    calculateStates(target, asteroids) {
        if (this.neuralNetwork.isDead)
            return;

        const spaceshipStates = [];

        if (enableManualControl)
            return spaceshipStates;

        const bodyAngle = this.wrapAroundAngle(this.rigidBody.angle) + Math.PI / 2 * 3;
        const headingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        let inputs = nnConfigs[this.currentActionName].inputs;
        let inputIndex = 1;
        for (const input of inputs) {
            if (!input.checked) {
                inputIndex++;
                continue;
            }
            switch (inputIndex++) {
                case 1: // spaceship's angle + Angular velocity (x3)
                    spaceshipStates.push(
                        headingDirection.x,
                        headingDirection.y,
                        this.rigidBody.angularVelocity / maxAngularVelocity
                    );
                    break;
                case 2: // target info (distance, polar velocity, target angle) (x5)

                    if (!target) {
                        spaceshipStates.push(0, 0, 0, 0, 0);
                        break;
                    }
                    // Calculate the vector pointing from the spaceship tors the target
                    let deltaTarget = new Vector(target.position.x - this.rigidBody.position.x, target.position.y - this.rigidBody.position.y);

                    // Calculate the cosine and sine of the angle between the spaceship's heading and the target direction
                    let targetAngle = this.calculateCosSinAngle(deltaTarget, headingDirection);

                    // Store the initial target distance for normalization and calculate normalized target distance
                    let targetDistance = Math.max(1, deltaTarget.length() / maxDistance);

                    // Calculate the velocity in polar coordinates relative to the target
                    const dr_dt = this.compute_dr_dt(-deltaTarget.x, -deltaTarget.y, target.velocity.x - this.rigidBody.velocity.x, target.velocity.y - this.rigidBody.velocity.y);
                    const dtheta_dt = this.compute_dtheta_dt(-deltaTarget.x, -deltaTarget.y, target.velocity.x - this.rigidBody.velocity.x, target.velocity.y - this.rigidBody.velocity.y);
                    let velocity = this.velocityInPolarCoordinates(targetDistance, dr_dt, dtheta_dt);

                    spaceshipStates.push(
                        targetDistance,
                        velocity.v_r,
                        velocity.v_theta,
                        targetAngle.cos_angle,
                        targetAngle.sin_angle
                    );
                    break;
                case 3: // Asteroids Radar Rays ( x5)
                    // Find the nearest asteroid and calculate the angle and distance to it
                    let radar = this.getRayDistances(asteroids, walls, numRadarRays);

                    spaceshipStates.push(...radar);
                    break;
                case 4: // Asteroids Radar Nearest ( x3)
                    let nearestAsteroidPoint = this.getNearestAsteroidPoint(asteroids);
                    let distanceToNearestAsteroid = this.rigidBody.position.distanceTo(nearestAsteroidPoint);
                    let angleToNearestAsteroid = this.calculateCosSinAngle(this.rigidBody.position, nearestAsteroidPoint);
                    spaceshipStates.push(
                        distanceToNearestAsteroid,
                        angleToNearestAsteroid.cos_angle,
                        angleToNearestAsteroid.sin_angle
                    );
                    break;
                case 5: // Nearest Laser Info (distance, polar velocity, angle) (x5)
                    const nearestLaser = this.getNearestLaserInfo();

                    if (nearestLaser) {
                        // Calculate the cosine and sine of the angle between the spaceship's heading and the laser direction
                        const laserAngle = this.calculateCosSinAngle(laserDirection, headingDirection);

                        // Calculate the relative position and velocity to the nearest laser
                        const deltaLaser = new Vector(nearestLaser.position.x - this.rigidBody.position.x, nearestLaser.position.y - this.rigidBody.position.y);
                        const deltaVelocity = new Vector(nearestLaser.velocity.x - this.rigidBody.velocity.x, nearestLaser.velocity.y - this.rigidBody.velocity.y);
                        const laserDistance = deltaLaser.length();
                        const laser_dr_dt = this.compute_dr_dt(-deltaLaser.x, -deltaLaser.y, deltaVelocity.x, deltaVelocity.y);
                        const laser_dtheta_dt = this.compute_dtheta_dt(-deltaLaser.x, -deltaLaser.y, deltaVelocity.x, deltaVelocity.y);
                        const laser_velocity = this.velocityInPolarCoordinates(laserDistance, laser_dr_dt, laser_dtheta_dt);

                        // Gather the spaceship states including position, velocity, target information, asteroid information, and projectile information
                        spaceshipStates.push(
                            laserAngle.cos_angle,
                            laserAngle.sin_angle,
                            laserDistance,
                            laser_velocity.v_r,
                            laser_velocity.v_theta
                        );
                    } else {
                        spaceshipStates.push(0, 0, 1, 0, 0);
                    }
                    break;
                case 6:
                    break;
                case 7:
                    spaceshipStates.push(this.fuelLevel);
                    break;
                case 8:
                    spaceshipStates.push(this.healthLevel);
                    break;
                case 9:
                    spaceshipStates.push(this.energyLevel);
                    break;
                case 10: // targeted enemy info (health, shield) (x2)
                    let enemy = this.getTargetedEnemy();
                    if (enemy) {
                        spaceshipStates.push(
                            enemy.healthLevel,
                            enemy.shieldActive
                        )
                    } else {
                        spaceshipStates.push(0, 0);
                    }
                    break;
                case 11: // Sheild Status (isActive, CooldownTimer, ActivationTimer) (x3)
                    spaceshipStates.push(
                        this.shieldActive,
                        this.shieldCooldownTimer / this.shieldCoolDown,
                        this.shieldActivationTimer / this.shieldActivatingTime
                    );
                    break;
            }
        }

        return spaceshipStates;
    }


    applyNeuralNetwork() {
        if (this.neuralNetwork.isDead)
            return;

        let inputs = this.spaceshipStates;
        const outputValues = this.neuralNetwork.predict(inputs);

        let outputs = nnConfigs[this.currentActionName].outputs;
        let outputIndex = 1;
        outputs.forEach((output, index) => {
            if (!output.checked) {
                outputIndex++;
                return;
            }

            let value = (outputValues[index] - 0.5) * 2; // transform from range [0, 1] to [-1, 1]
            switch (outputIndex++) {
                case 1:
                    value *= maxThrustPower; // additional transform specific to thrust
                    this.thrust = value;
                    break;
                case 2:
                    value *= maxRotationAccel; // additional transform specific to angularAcceleration
                    this.angularAcceleration = value;
                    break;
                case 3:
                    value *= maxSideThrustPower; // additional transform specific to sideThrust
                    this.sideThrust = value;
                    break;
                case 4:
                    // Assuming value is used to determine if fire is active
                    this.isFireActive = value > 0; // threshold for activating fire can be adjusted
                    break;
                case 5:
                    // Assuming value is used to determine if shield is active
                    this.shieldActive = value > 0; // threshold for activating shield can be adjusted
                    break;
                default:
                    break;
            }
        });

        let now = performance.now();
        if (!this.startTime)
            this.startTime = now;

        let deltaTime = now - this.startTime;
        if (deltaTime > deathTimer) {
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

    handleCollision() {
        // Get the polygons of the lander and asteroid
        const landerPolygons = this.getLanderPolygons();

        for (let enemy of this.enemies) {
            for (let i = 0; i < enemy.lasers.length; i++) {
                const laser = enemy.lasers[i];

                nearestPoint = IntersectionUtil.lineCircleIntersection({
                    start: laser.position,
                    end: laser.end
                }, this.rigidBody.position, 50);

                if (nearestPoint) {
                    if (this.rigidBody.position == enemy.target.position)
                        enemy.target = null;
                    enemy.removeLaser(i);
                    this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnGotShieldHit"]);
                    enemy.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnHitEnemyShield"]);
                    this.healthLevel -= this.laserDamage;
                }
            }
        }
        // Check for intersection between each pair of polygons
        for (const landerPolygon of landerPolygons) {
            let nearestPoint;
            for (let i = 0; i < asteroids.length; i++) {
                let asteroid = asteroids[i];
                const asteroidPolygon = asteroids[i].polygon;
                nearestPoint = landerPolygon.getNearestIntersection(asteroidPolygon);

                if (nearestPoint) {
                    this.rigidBody.resolveCollision(asteroid.rigidBody);
                    this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnCollisionAsteroid"]);
                    //this.neuralNetwork.currentFitness -= 1000;
                }
            }

            for (let enemy of this.enemies) {
                for (let i = 0; i < enemy.lasers.length; i++) {
                    const laser = enemy.lasers[i];
                    nearestPoint = landerPolygon.getNearestRayIntersection({
                        start: laser.position,
                        end: laser.end
                    });
                    if (nearestPoint) {
                        if (this.rigidBody.position == enemy.target.position)
                            enemy.target = null;
                        enemy.removeLaser(i);
                        this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnGotHit"]);
                        enemy.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnHitEnemy"]);
                        this.healthLevel -= this.laserDamage;
                    }
                }
            }

            // Check for intersection with walls
            for (const wall of walls) {
                const wallPolygon = new Polygon(wall);
                //let center = wallPolygon.calculateCenter();
                //let rectangle = wallPolygon.createRectangleFromPolygon()
                //let wallRigidBody = new RigidBody(center.x, center.y, rectangle.width, rectangle.height, 1);
                //wallRigidBody.center = center;

                //const nearestPoint = wallPolygon.getNearestIntersection(landerPolygon);

                if (nearestPoint) {
                    this.rigidBody.resolveCollision(asteroid.rigidBody);
                    //this.neuralNetwork.currentFitness -= 1000;
                }
            }
            if (useSpaceStation) {
                nearestPoint = spaceStation.polygon.getNearestIntersection(landerPolygon);
                if (nearestPoint) {
                    this.rigidBody.resolveCollision(spaceStation.rigidBody);
                    this.neuralNetwork.currentFitness += Number(nnConfigs[this.currentActionName].fitnessOnEvents["OnCollisionSpaceStation"]);
                }
            }
        }

    }

    // For navigation
    getNearestAsteroidPoint(asteroids) {
        let nearestPoint = null;
        let minDistance = Infinity;

        for (let asteroid of asteroids) {
            for (let i = 0; i < asteroid.polygon.vertices.length; i++) {
                const asteroidPoint = asteroid.polygon.vertices[i];
                let position = new Vector(this.rigidBody.position.x, this.rigidBody.position.y);
                const distance = position.distanceTo(asteroidPoint);

                if (distance < minDistance) {
                    minDistance = distance;
                    nearestPoint = asteroidPoint;
                }
            }
        }

        return nearestPoint;
    }


}