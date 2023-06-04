class Enemy extends Lander {
    constructor(x, y, angle, populationIndex) {
        super(x, y, populationIndex);
        this.angle = 0;
        this.angularVelocity = 0;
        this.isEnemy = true;
        this.fireTime = 200;
        this.fireTimer = 0;
        this.neuralNetwork = {isDead : false};
        this.rigidBody.angle = angle;
    }

    update(player){
        if(!this.neuralNetwork.isDead)
            this.superBasicAI(player.rigidBody.position);
        this.updateLander();
    }

    rotateToAngle(playerPosition) {
        let deltaPosition = playerPosition.subtract(this.rigidBody.position);
        this.rigidBody.angle = Math.PI-deltaPosition.angle();
    }

    superBasicAI(playerPosition) {
        this.rotateToAngle(playerPosition);
        if (this.fireTimer >= this.fireTime) {
            this.fireLaser();
            this.fireTimer = 0;
        }
        this.fireTimer++;
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