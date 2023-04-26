const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

class Car {
    constructor(x, y, angle) {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.speed = 0;
        this.driftFactor = 0.98;
    }

    update() {
        const velocityX = Math.cos(this.angle) * this.speed;
        const velocityY = Math.sin(this.angle) * this.speed;

        this.x += velocityX;
        this.y += velocityY;
    }

    draw() {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.fillStyle = 'red';
        ctx.fillRect(-25, -12, 50, 25);

        // Draw the front bumper
        ctx.fillStyle = 'black';
        ctx.fillRect(22, -14, 3, 29);

        // Draw the wheels
        ctx.fillStyle = 'blue';
        ctx.fillRect(-20, -17, 12, 4); // Front left wheel
        ctx.fillRect(8, -17, 12, 4);   // Front right wheel
        ctx.fillRect(-20, 14, 12, 4);  // Rear left wheel
        ctx.fillRect(8, 14, 12, 4);    // Rear right wheel

        ctx.restore();
    }

    isDrifting() {
        const driftThreshold = 2;
        return Math.abs(this.lateralSpeed) > driftThreshold;
    }
}

const car = new Car(canvas.width / 2, canvas.height / 2, 0);

function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    car.update();
    car.draw();

     {
        ctx.font = '30px Arial';
        ctx.fillStyle = 'black';
        ctx.fillText('dérapage: ' + Math.abs(car.lateralSpeed), canvas.width / 2 - 50, canvas.height / 2 - 20);
    }

    requestAnimationFrame(gameLoop);
}

gameLoop();

let isArrowLeftPressed = false;
let isArrowRightPressed = false;
let isArrowUpDownPressed = false;

document.addEventListener('keydown', (event) => {
    const key = event.key;
    const rotationSpeed = 0.1;
    const acceleration = 0.5;

    if (key === 'ArrowLeft') {
        isArrowLeftPressed = true;
    } else if (key === 'ArrowRight') {
        isArrowRightPressed = true;
    } else if (key === 'ArrowUp') {
        car.speed += acceleration;
        isArrowUpDownPressed = true;
    } else if (key === 'ArrowDown') {
        car.speed -= acceleration;
        isArrowUpDownPressed = true;
    }

    if (isArrowLeftPressed && isArrowUpDownPressed) {
        car.angle -= rotationSpeed;
        car.speed *= car.driftFactor;
    }

    if (isArrowRightPressed && isArrowUpDownPressed) {
        car.angle += rotationSpeed;
        car.speed *= car.driftFactor;
    }
});

document.addEventListener('keyup', (event) => {
    const key = event.key;

    if (key === 'ArrowLeft') {
        isArrowLeftPressed = false;
    } else if (key === 'ArrowRight') {
        isArrowRightPressed = false;
    } else if (key === 'ArrowUp' || key === 'ArrowDown') {
        isArrowUpDownPressed = false;
    }
});






