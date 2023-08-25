class MaxSizeList {
    constructor(maxSize) {
        this.maxSize = maxSize;
        this.data = [];
    }

    // Add an item to the list
    add(item) {
        if (this.data.length >= this.maxSize) {
            this.data.shift();  // Remove the oldest item
        }
        this.data.push(item);
    }

    // Get the list items
    getItems() {
        return this.data;
    }

    // Get the size of the list
    size() {
        return this.data.length;
    }
}


class Enemy extends Lander {
    constructor(x, y, angle, populationIndex) {
        super(x, y, populationIndex);
        this.angle = 0;
        this.angularVelocity = 0;
        this.isEnemy = true;
        this.fireTime = 200;
        this.fireTimer = 0;
        this.neuralNetwork = {
            isDead: true
        };
        this.rigidBody.angle = angle;
        this.startPosx = this.rigidBody.position.x;
        this.pid = new PID(0.0025,0,0.1);
        this.isTuning = false;
        this.stepCount = 0;
        this.checkOscillationInterval = 100;
        this.pidTuned = false;
        this.targetPosition = 0;
        this.systemModel = null;

        this.destinationPosition = this.rigidBody.position.x + this.targetPosition;
        this.relativePosition = this.destinationPosition - this.rigidBody.position.x;
        this.lastPositionList = new MaxSizeList(1000);
        this.side = 1;  // Initialize side
        this.previousSteady = false;  // To track the state in the previous frame
        this.startPosx = this.rigidBody.position.x;
        this.rigidBody.mass = 1;
    }

    isSteady(outputData, windowSize = 10, threshold = 0.01) {
        if(outputData.length < windowSize)
            return false;
        // Get the most recent data based on windowSize
        const recentData = outputData.slice(-windowSize);
    
        // Calculate the mean of the recent data
        const mean = recentData.reduce((acc, val) => acc + val, 0) / windowSize;
    
        // Calculate the variance of the recent data
        const variance = recentData.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / windowSize;
    
        // Check if the variance is below the threshold
        return variance < threshold;
    }


    
    checkAndToggleSide(outputData) {
        const steady = this.isSteady(outputData);
        let switchSide = false;
        if (steady && !this.previousSteady) {
            this.side *= -1;
            switchSide = true;
        }
    
        this.previousSteady = steady;
        return switchSide;
    }    

    update(player) {
        this.stepCount++;
        this.targetPosition = this.side * 500;
        let relativePosition = this.rigidBody.position.x - this.startPosx;
        let output = this.pid.compute(relativePosition, this.targetPosition);
        this.sideThrust = -output;
        this.sideThrust = Math.max(-maxSideThrustPower, Math.min(maxSideThrustPower, this.sideThrust));
        this.updateLander();
        relativePosition = this.rigidBody.position.x - this.startPosx;
        this.lastPositionList.add(relativePosition);
        if(this.checkAndToggleSide(this.lastPositionList.getItems())){
            this.startPosx = this.rigidBody.position.x;
        }
        // if(this.stepCount == 500){
        //     console.log(JSON.stringify(this.lastPositionList.getItems()))
        // }
    }


    currentMicros() {
        return performance.now() * 1000; // Convert milliseconds to microseconds
    }

    rotateToAngle(playerPosition) {
        let deltaPosition = playerPosition.subtract(this.rigidBody.position);
        this.rigidBody.angle = Math.PI - deltaPosition.angle();
    }

    superBasicAI(playerPosition) {

    }

    circlePattern(deltaTime) {
        const speed = 100;
        const radius = 200;
        const centerX = 400;
        const centerY = 300;
        const angle = this.time * speed / radius;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        this.position.x = x;
        this.position.y = y;
        this.time += deltaTime;
    }

    basicAI(player, deltaTime) {
        const direction = new Vector(player.position.x - this.position.x, player.position.y - this.position.y);
        direction.normalize();
        const speed = 200;
        this.velocity.x = direction.x * speed;
        this.velocity.y = direction.y * speed;
        this.position.x += this.velocity.x * deltaTime;
        this.position.y += this.velocity.y * deltaTime;
        this.attackTimer += deltaTime;
        if (this.attackTimer >= 3) {
            this.attack();
            this.attackTimer = 0;
        }
    }

    controlledMovementPattern(deltaTime) {
        const maxSpeed = 200;
        const acceleration = 100;
        const deceleration = 200;
        const targetX = 500;
        const distance = targetX - this.position.x;
        const movementDirection = Math.sign(distance);
        const accel = movementDirection * acceleration;
        const decel = -Math.sign(this.velocity.x) * deceleration;
        this.velocity.x += accel * deltaTime;
        if (Math.abs(this.velocity.x) > maxSpeed) {
            this.velocity.x = movementDirection * maxSpeed;
        }
        if ((distance < 0 && this.velocity.x > 0) || (distance > 0 && this.velocity.x < 0)) {
            this.velocity.x += decel * deltaTime;
        }
        this.position.x += this.velocity.x * deltaTime;
    }
}