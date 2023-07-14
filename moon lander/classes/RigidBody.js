class RigidBody {
    constructor(x, y, width, height, mass) {
        this.position = new Vector(x, y);
        this.velocity = new Vector(0, 0);
        this.width = width;
        this.height = height;
        this.mass = mass;
        this.restitution = 0.1; // coefficient of restitution
        this.angularVelocity = 0;
        this.angle = 0;
        this.calculateMomentOfInertia()
    }

    calculateMomentOfInertia() {
        this.momentOfInertia = (1 / 12) * this.mass * (this.width * this.width + this.height * this.height); // assuming rectangular shape    
    }

    applyForce(force) {
        this.velocity.x += force.x / this.mass;
        this.velocity.y += force.y / this.mass;
    }

    // Method to apply an angular force (torque) to the object (angular acceleration = torque / mass)
    applyTorque(torque) {
        this.angularVelocity += torque / this.mass;
    }

    // Method to update the object's position and rotation based on its velocity and angular velocity
    update() {
        if (this.angularVelocity > env.maxAngularVelocity) {
            this.angularVelocity = env.maxAngularVelocity;
        } else if (this.angularVelocity < -env.maxAngularVelocity) {
            this.angularVelocity = -env.maxAngularVelocity;
        }
        // Update the position based on the velocity
        this.position = this.position.add(this.velocity);

        // Update the angle based on the angular velocity
        this.angle += this.angularVelocity;
    }

    applyImpulse(impulse, contactVector) {
        // Apply linear impulse to the velocity based on mass
        this.velocity = this.velocity.add(impulse.multiply(1 / this.mass));

        // Apply angular impulse
        const angularImpulse =
            (contactVector.x * impulse.y - contactVector.y * impulse.x) /
            this.momentOfInertia;
        this.angularVelocity += angularImpulse;
    }

    // Check if this rigid body collides with another rigid body
    collidesWith(other) {
        return (
            this.position.x < other.position.x + other.width &&
            this.position.x + this.width > other.position.x &&
            this.position.y < other.position.y + other.height &&
            this.position.y + this.height > other.position.y
        );
    }

    resolveCollision(other) {
        // Calculate relative velocity
        const relativeVelocity = this.velocity.subtract(other.velocity);

        // Calculate relative velocity along the collision normal
        const collisionNormal = other.position.subtract(this.position).normalize();

        const velocityAlongNormal = relativeVelocity.dot(collisionNormal);

        // If the relative velocity is separating, no further action is needed
        // if (velocityAlongNormal > 0) {
        //     return;
        // }

        // Calculate the impulse scalar
        const impulseScalar =
            (-1 * (1 + this.restitution) * velocityAlongNormal) /
            (1 / this.mass + 1 / other.mass);

        // Calculate impulse
        const impulse = collisionNormal.multiply(impulseScalar);

        // Calculate contact vector
        const contactVector = other.center            
            .subtract(this.position)
            .perpendicular();

        // Apply impulses
        this.applyImpulse(impulse, contactVector);
        //other.applyImpulse(impulse.multiply(-1), contactVector);

        // Separate the bodies to resolve overlap
        const overlap = Math.min(
            this.width + other.width - Math.abs(this.position.x - other.position.x),
            this.height + other.height - Math.abs(this.position.y - other.position.y)
        );

        const separationVector = collisionNormal.multiply(1);

        this.position = this.position.subtract(separationVector);
        //other.position = other.position.add(separationVector);
    }
}

// // Create two rigid bodies
// const body1 = new RigidBody(0, 0, 50, 50, 1);
// const body2 = new RigidBody(60, 0, 50, 50, 1);

// // Move body1 to the right
// body1.velocity = new Vector(1, 0);

// // Simulate the update loop
// function updateLoop() {
//     // Update the positions of the rigid bodies
//     body1.update();
//     body2.update();

//     // Check for collisions
//     if (body1.collidesWith(body2)) {
//         body1.resolveCollision(body2);
//         console.log("Collision detected!");
//         // Handle the collision here (e.g., change velocities, resolve overlap)
//     }

//     // Repeat the update loop
//     requestAnimationFrame(updateLoop);
// }

// // Start the update loop
// updateLoop();