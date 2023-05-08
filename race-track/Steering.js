class Steering {
    constructor(maxAngle) {
        this.angle = 0;
        this.velocity = 0;
        this.acceleration = 0;
        this.maxAngle = maxAngle;
    }

    update(velocity) {
        if(Math.abs(this.angle) < this.maxAngle)
            this.angle += velocity;
    }

    reset(){
        this.angle = 0;
    }
}


