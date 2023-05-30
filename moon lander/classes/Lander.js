class Lander {
    constructor(x, y, neuralNetwork = null) {
        this.retartPosition = {
            x,
            y
        };
        this.thrust = 0;
        this.sideThrust = 0;
        this.angularAcceleration = 0;
        this.fuelConsumption = 0;
        //this.neuralNetwork = neuralNetwork;
        this.successfulLanding = false;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTime = 0;
        this.currentTime = 0;
        this.docked = false;
        this.cumulRotationPenaltyFactor = 0;
        this.frameCount = 0;
        this.target = null;
        this.targetIndex = 0;
        this.rigidBody = new RigidBody(x, y, 50, 50);
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
    }

    setActiveNeuralNetwork(name) {
        this.neuralNetwork = this.neuralNetworks[name];
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
        const distanceVector = new Vector(lastTarget.x - this.rigidBody.position.x, lastTarget.y - this.rigidBody.position.y);
        return distanceVector.length();
    }

    checkChangeAction() {
        if (this.targetIndex == targets.length - 1) {
            let lastTargetDistance = this.getLastTargetDistance();
            if (lastTargetDistance < 1000)
                this.setActiveNeuralNetwork("stop");
        }
    }

    updateLander(asteroids) {
        // fuel consumption is calculated based on the thrust and angular acceleration
        this.fuelConsumption = 0;
        this.fuelConsumption += FuelConsumption_thrust * (this.thrust / maxThrustPower);
        this.fuelConsumption += FuelConsumption_rotate * (Math.abs(this.angularAcceleration) / maxRotationAccel);
        let force = new Vector(this.thrust * Math.sin(this.rigidBody.angle), gravity - (this.thrust * Math.cos(this.rigidBody.angle)));
        let sideForce = new Vector(this.sideThrust * Math.sin(this.rigidBody.angle + Math.PI / 2), gravity - (this.sideThrust * Math.cos(this.rigidBody.angle + Math.PI / 2)));
        this.rigidBody.applyForce(force);
        this.rigidBody.applyForce(sideForce);
        this.rigidBody.applyTorque(this.angularAcceleration);
        this.rigidBody.update();

        this.lastSpaceshipStates = this.spaceshipStates;
        this.spaceshipStates = this.calculateStates(this.target, asteroids);
        //this.spaceshipStates = [...this.spaceshipStates, this.thrust, this.angularAcceleration]
        if (!this.lastSpaceshipStates)
            this.lastSpaceshipStates = this.spaceshipStates;
    }

    resetLander() {
        this.rigidBody.position.x = this.retartPosition.x;
        this.rigidBody.position.y = this.retartPosition.y;
        this.rigidBody.angle = 0;
        this.rigidBody.velocity.x = 0;
        this.rigidBody.velocity.y = 0;
        this.rigidBody.angularVelocity = 0;
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
        this.targetIndex = 0;
        this.neuralNetwork.currentFitness = startingTimeBonus;
        this.fitnessMultiplier = 1;
        this.startDistance = 0;
        this.timeBonus = startingTimeBonus;
    }

    changeTarget(target) {
        this.target = target;
        this.targetReached = false;
        this.timeToReachTarget = 0;
        this.startTimeReached = 0;
    }

    drawLander() {
        ctx.save();
        ctx.translate(this.rigidBody.position.x, this.rigidBody.position.y);

        if (this.neuralNetwork.positionNumber) {
            if (this.neuralNetwork.positionNumber <= 10)
                ctx.fillStyle = 'yellow';
            else
                ctx.fillStyle = 'white';

            ctx.font = '40px Arial';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(this.neuralNetwork.positionNumber + "(" + this.neuralNetwork.currentFitness.toFixed() + ")", 50, 0);
            //ctx.fillText(this.neuralNetwork.positionNumber, 50, 0);
        }

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
        ctx.restore();
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
        let targetReached = distanceVector.length() < targetRadius;
        if (targetReached && !this.targetReached) {
            if (this.startTimeReached == 0)
                this.startTimeReached = performance.now();

            this.timeToReachTarget = performance.now() - this.startTimeReached;
            if (this.timeToReachTarget > 20) {
                this.targetReached = true;
                this.neuralNetwork.currentFitness += 15000;
            }
        } else if (!targetReached) {
            this.startTimeReached = 0;
        }

        return this.targetReached;
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
            center: new Vector(target.x, target.y),
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
        let distanceVector = new Vector(target.x - this.rigidBody.position.x, target.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate distance fitness based on the normalized distance to the target
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / this.startDistance);

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
            this.neuralNetwork.currentFitness += 10000;
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
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / this.startDistance);


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

    calculateFitness(target) {
        if (!target)
            return;
        this.frameCount++;

        if (!this.targetReached) {
            if (this.frameCount > startingTimeBonus)
                this.timeBonus--; // time bonus is reduced by 1 more if target is not reached before startingTimeBonus
            this.timeBonus--;
        }
        // Calculate the vector pointing from the spaceship to the target
        let distanceVector = new Vector(target.x - this.rigidBody.position.x, target.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;

        // Calculate the facing direction of the spaceship
        const facingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate distance fitness based on the normalized distance to the target
        let distanceFitness = Math.max(0, 1 - distanceVector.length() / this.startDistance);

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

    calculateStates(target, asteroids) {
        if (this.neuralNetwork.isDead)
            return;

        // Calculate the vector pointing from the spaceship to the target
        const deltaTarget = new Vector(target.x - this.rigidBody.position.x, target.y - this.rigidBody.position.y);

        // Calculate the angle of the spaceship's body
        let bodyAngle = this.rigidBody.angle;
        bodyAngle = this.wrapAroundAngle(bodyAngle) + Math.PI / 2 * 3;
        const headingDirection = new Vector(Math.cos(bodyAngle), Math.sin(bodyAngle));

        // Calculate the cosine and sine of the angle between the spaceship's heading and the target direction
        const targetAngle = this.calculateCosSinAngle(deltaTarget, headingDirection);


        let r;
        if (this.startDistance)
            r = deltaTarget.length() / this.startDistance;
        else
            r = 1;

        // Store the initial target distance for normalization
        if (!this.startDistance)
            this.startDistance = deltaTarget.length();

        // Calculate the velocity in polar coordinates
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
            ...radar // normalized distances to nearest asteroids
        ];

        return spaceshipStates;
    }



    applyNeuralNetwork() {

        let inputs = this.spaceshipStates;
        const [thrust, angularAcceleration, sideThrust] = this.neuralNetwork.predict(inputs);

        // Update thrustDirection based on the new orientation
        this.angularAcceleration = (angularAcceleration - 0.5) * 2 * maxRotationAccel;
        this.thrust = (thrust - 0.5) * 2 * maxThrustPower;
        this.sideThrust = (sideThrust - 0.5) * 2 * maxSideThrustPower;
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

    handleCollision(asteroid) {
        // Get the polygons of the lander and asteroid
        const landerPolygons = this.getLanderPolygons();

        // Check for intersection between each pair of polygons
        for (const landerPolygon of landerPolygons) {
            let nearestPoint = landerPolygon.getNearestIntersection(asteroid.polygon);

            if (nearestPoint) {
                this.rigidBody.resolveCollision(asteroid.rigidBody);
                //this.neuralNetwork.currentFitness -= 1000;
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
                    this.neuralNetwork.currentFitness -= 100;
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