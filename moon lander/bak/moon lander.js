class Explosion {
    constructor(x, y, ctx) {
        this.x = x;
        this.y = y;
        this.ctx = ctx;
        this.pieces = [];
        this.gravity = 0.03;
        this.init();
    }

    init() {
        for (let i = 0; i < 20; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 3 + 1;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            const rotationSpeed = Math.random() * 2 - 1;

            const width = Math.random() * 10 + 5;
            const height = Math.random() * 10 + 5;

            this.pieces.push({
                x: this.x,
                y: this.y,
                vx,
                vy,
                life: 5,
                width,
                height,
                rotation: 0,
                rotationSpeed,
                color:'darkgray'
            });
        }
    }

    update() {
        for (const piece of this.pieces) {
            this.ctx.fillStyle = piece.color;
            this.ctx.strokeStyle = 'black';
            this.ctx.save();
            this.ctx.translate(piece.x, piece.y);
            this.ctx.rotate((piece.rotation * Math.PI) / 180);
            this.ctx.rect(-piece.width / 2, -piece.height / 2, piece.width, piece.height);
            this.ctx.fill();
            this.ctx.stroke();                    
            this.ctx.restore();

            piece.x += piece.vx;
            piece.y += piece.vy;

            piece.vy += this.gravity;
            piece.life -= 0.015;

            piece.rotation += piece.rotationSpeed;

            if (piece.life <= 0) {
                piece.life = 0;
            }
        }

        this.pieces = this.pieces.filter(p => p.life > 0);
    }

    isDone() {
        return this.pieces.length === 0;
    }
}

class Firework2 {
    constructor(x, y, color, ctx) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.ctx = ctx;
        this.particles = [];
        this.gravity = 0.03;
        this.init();
    }

    init() {
        for (let i = 0; i < 50; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 2 + 1;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            this.particles.push({
                x: this.x,
                y: this.y,
                vx,
                vy,
                life: 1,
                size: Math.random() * 5 + 3,
                color: `hsl(${Math.random() * 360}, 100%, 50%)`
            });
        }
    }

    update() {
        for (const particle of this.particles) {
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(
                particle.x,
                particle.y,
                particle.size * particle.life,
                0,
                Math.PI * 2
            );
            this.ctx.fill();

            particle.x += particle.vx;
            particle.y += particle.vy;

            particle.vy += this.gravity;
            particle.life -= 0.015;

            if (particle.life <= 0) {
                particle.life = 0;
            }
        }

        this.particles = this.particles.filter(p => p.life > 0);
    }

    draw() {
        for (const particle of this.particles) {
            this.ctx.fillStyle = `rgba(${this.color}, ${particle.life})`;
            this.ctx.fillRect(particle.x, particle.y, 2, 2);
        }
    }

    isDone() {
        return this.particles.length === 0;
    }
}

class Firework {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.rays = [];
        this.numRays = 10;
        this.colors = ['red', 'yellow', 'blue', 'green', 'purple'];
        this.life = 100; // Duration of the firework animation

        for (let i = 0; i < this.numRays; i++) {
            const angle = (2 * Math.PI / this.numRays) * i;
            const randomColor = this.colors[Math.floor(Math.random() * this.colors.length)];
            this.rays.push({
                x: this.x,
                y: this.y,
                angle: angle,
                length: 0,
                color: randomColor,
            });
        }
    }

    update() {
        if (this.life > 0) {
            this.life--;
            for (let ray of this.rays) {
                ray.length += 2;
            }
        }
    }

    draw() {
        if (this.life <= 0) return;

        ctx.save();

        for (let ray of this.rays) {
            const x = this.x + ray.length * Math.cos(ray.angle);
            const y = this.y + ray.length * Math.sin(ray.angle);

            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(x, y);
            ctx.strokeStyle = ray.color;
            ctx.lineWidth = 2;
            ctx.stroke();
        }
        ctx.restore();
    }
}


let Noise = {
    rand_vect: function () {
        let theta = Math.random() * 2 * Math.PI;
        return {
            x: Math.cos(theta),
            y: Math.sin(theta)
        };
    },
    dot_prod_grid: function (x, y, vx, vy) {
        let g_vect;
        let d_vect = {
            x: x - vx,
            y: y - vy
        };
        if (this.gradients[[vx, vy]]) {
            g_vect = this.gradients[[vx, vy]];
        } else {
            g_vect = this.rand_vect();
            this.gradients[[vx, vy]] = g_vect;
        }
        return d_vect.x * g_vect.x + d_vect.y * g_vect.y;
    },
    smootherstep: function (x) {
        return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3;
    },
    interp: function (x, a, b) {
        return a + this.smootherstep(x) * (b - a);
    },
    seed: function () {
        this.gradients = {};
        this.memory = {};
    },
    perlin2: function (x, y) {
        if (this.memory.hasOwnProperty([x, y]))
            return this.memory[[x, y]];
        let xf = Math.floor(x);
        let yf = Math.floor(y);
        //interpolate
        let tl = this.dot_prod_grid(x, y, xf, yf);
        let tr = this.dot_prod_grid(x, y, xf + 1, yf);
        let bl = this.dot_prod_grid(x, y, xf, yf + 1);
        let br = this.dot_prod_grid(x, y, xf + 1, yf + 1);
        let xt = this.interp(x - xf, tl, tr);
        let xb = this.interp(x - xf, bl, br);
        let v = this.interp(y - yf, xt, xb);
        this.memory[[x, y]] = v;
        return v;
    }
}
Noise.seed();

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const mountainResolution = 0.005;
const mountainHeightFactor = 0.4;
const maxYOffset = 0.4;
let fireworksV1 = [];
let fireworks = [];
let explosion = null;

let fireworkCounter = 0;
const fireworkInterval = 100;
let successfulLanding = false;
let landed = false;
// Add gas tank properties
const gasTankRadius = 10;
const gasTankColor = 'rgba(0, 255, 0, 0.5)';
const gasTankAmount = 5;
const gasTankRefuelAmount = 25;
const audioContext = new(window.AudioContext || window.webkitAudioContext)();
const thrustSound = new Audio('thrust.mp3');
//thrustSound.play();
const refuelSound = new Audio('boost-100537.mp3');

// Create gas tanks array
let gasTanks = [];


let lander = {
    x: canvas.width / 2,
    y: 50,
    angle: 0,
    velocityX: 0,
    velocityY: 0,
    thrust: 0,
    rotationSpeed: 0,
    fuel: 100
};

const gravity = 0.01;
const thrustPower = 0.05;
const rotationSpeed = 1;
const landingSpeed = 1;
const FuelConsumption_thrust = 0.25;
const FuelConsumption_rotate = 0.05;
let score = 0;

let platform = {
    x: Math.random() * (canvas.width - 200) + 100,
    y: canvas.height - 50,
    width: 200,
    height: 10
};

function getY(x) {
    const y = (1 + Noise.perlin2(x * mountainResolution, 0)) * (canvas.height * mountainHeightFactor) + (canvas
        .height * maxYOffset);
    if (x >= platform.x && x <= platform.x + platform.width) {
        return platform.y;
    }
    return y;
}


function isCollidingWithMountains() {
    const x = lander.x;
    const y = lander.y + 25;
    return y >= getY(x);
}

function generateTerrain() {
    ctx.beginPath();
    ctx.moveTo(0, getY(0));
    for (let x = 1; x < canvas.width; x++) {
        ctx.lineTo(x, getY(x));
    }
    ctx.lineTo(canvas.width, canvas.height);
    ctx.lineTo(0, canvas.height);
    ctx.closePath();
    ctx.fillStyle = 'darkgray';
    ctx.fill();
}

const keys = {};

document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
});

document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});


function drawFuelBar() {
    const fuelBarHeight = 20;
    const fuelBarWidth = 100;
    const fuelBarPadding = 10;
    const fuelBarX = fuelBarPadding;
    const fuelBarY = fuelBarPadding;

    // Draw the fuel bar background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(fuelBarX, fuelBarY, fuelBarWidth, fuelBarHeight);

    // Draw the fuel bar progress
    ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
    const fuelProgressWidth = (lander.fuel / 100) * fuelBarWidth;
    ctx.fillRect(fuelBarX, fuelBarY, fuelProgressWidth, fuelBarHeight);

    // Draw the fuel bar text
    ctx.fillStyle = 'white';
    ctx.font = '14px Arial';
    ctx.fillText('Fuel', fuelBarX + fuelBarWidth / 2 - 10, fuelBarY + 14);
}

function drawScore() {
    ctx.fillStyle = 'black';
    ctx.font = '14px Arial';
    ctx.fillText('Score: ' + score, canvas.width - 100, 20);
}

function playThrustSound() {
    if (thrustSound.isPlaying)
        return;
    thrustSound.isPlaying = true;
    thrustSound.currentTime = 0;
    thrustSound.play();
}

function stopThrustSound() {
    thrustSound.isPlaying = false;
    thrustSound.currentTime = 0;
    thrustSound.pause();
}

function playRefuelSound() {
    refuelSound.currentTime = 0;
    refuelSound.play();
}

function updateLander() {

    if (keys['ArrowLeft'] && lander.fuel > 0) {
        lander.rotationSpeed = -rotationSpeed;
        lander.fuel -= FuelConsumption_rotate;
    }
    if (keys['ArrowRight'] && lander.fuel > 0) {
        lander.rotationSpeed = rotationSpeed;
        lander.fuel -= FuelConsumption_rotate;
    }
    if (!keys['ArrowLeft'] && !keys['ArrowRight']) {
        lander.rotationSpeed = 0;
    }
    if (keys['ArrowUp'] && lander.fuel > 0) {
        score += FuelConsumption_thrust;
        lander.thrust = thrustPower;
        lander.fuel -= FuelConsumption_thrust;
        playThrustSound();
    } else {
        lander.thrust = 0;
        stopThrustSound();
    }

    lander.angle += lander.rotationSpeed;
    lander.velocityX += lander.thrust * Math.sin(lander.angle * Math.PI / 180);
    lander.velocityY += gravity - (lander.thrust * Math.cos(lander.angle * Math.PI / 180));
    lander.x += lander.velocityX;
    lander.y += lander.velocityY;
}

function drawFireworks() {
    const fireworkColors = ['red', 'yellow', 'blue', 'green', 'purple'];
    const fireworkRadius = 50;
    const numRays = 10;

    const centerX = platform.x + platform.width / 2;
    const centerY = platform.y - fireworkRadius;

    for (let i = 0; i < numRays; i++) {
        const angle = (2 * Math.PI / numRays) * i;
        const x = centerX + fireworkRadius * Math.cos(angle);
        const y = centerY + fireworkRadius * Math.sin(angle);

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = fireworkColors[i % fireworkColors.length];
        ctx.lineWidth = 2;
        ctx.stroke();
    }
}

let firework = null;


function resetLander() {
    lander.x = canvas.width / 2;
    lander.y = 50;
    lander.angle = 0;
    lander.velocityX = 0;
    lander.velocityY = 0;
    lander.thrust = 0;
    lander.rotationSpeed = 0;
    lander.fuel = 100;
    score = 0;
    platform.x = Math.random() * (canvas.width - 200) + 100;
    platform.y = getY(platform.x);
    keys['ArrowUp'] = false; // Reset the up arrow key state
    keys['ArrowRight'] = false;
    keys['ArrowLeft'] = false
}


function drawLander() {
    ctx.save();
    ctx.translate(lander.x, lander.y);
    ctx.rotate(lander.angle * Math.PI / 180);

    // Draw spaceship body
    ctx.beginPath();
    ctx.moveTo(-15, 15);
    ctx.quadraticCurveTo(-15, -15, 0, -30);
    ctx.quadraticCurveTo(15, -15, 15, 15);
    ctx.closePath();
    ctx.fillStyle = 'silver';
    ctx.fill();
    ctx.strokeStyle = 'black';
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
    ctx.strokeStyle = 'black';
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(15, 15);
    ctx.quadraticCurveTo(25, 10, 25, 30);
    ctx.lineTo(15, 30);
    ctx.closePath();
    ctx.fillStyle = 'silver';
    ctx.fill();
    ctx.strokeStyle = 'black';
    ctx.stroke();

    // Draw spaceship thruster
    if (lander.thrust > 0) {
        ctx.beginPath();
        ctx.moveTo(-5, 20);
        ctx.lineTo(0, 30);
        ctx.lineTo(5, 20);
        ctx.closePath();
        ctx.fillStyle = 'red';
        ctx.fill();
        ctx.strokeStyle = 'black';
        ctx.stroke();
    }
    ctx.restore();
}

function checkLanding() {
    const x = lander.x;
    const y = lander.y + 25;
    const platformRange = y >= platform.y && x >= platform.x - 25 && x <= platform.x + platform.width - 25;
    if (isCollidingWithMountains()) {
        let checkAngle = (lander.angle + 180) % 360;
        if (platformRange && lander.velocityY < landingSpeed && Math.abs(180 - checkAngle) < 10) {
            landed = true;
            successfulLanding = true;
            lander.velocityX = 0;
            lander.velocityY = 0;
            lander.rotationSpeed = 0;
        } else {
            landed = true;
            successfulLanding = false;
            lander.velocityX = 0;
            lander.velocityY = 0;
            lander.rotationSpeed = 0;
            if (explosion === null) {
                explosion = new Explosion(lander.x, lander.y, ctx);
            }
        }
        fireworkCounter = fireworkInterval - 1;

    }
}

function drawGasTanks() {
    ctx.save();
    for (const gasTank of gasTanks) {
        ctx.beginPath();
        ctx.arc(gasTank.x, gasTank.y, gasTankRadius, 0, 2 * Math.PI);
        ctx.fillStyle = gasTankColor;
        ctx.fill();
        ctx.stroke();
    }
    ctx.restore();
}

function refuelLander() {
    for (let i = 0; i < gasTanks.length; i++) {
        const gasTank = gasTanks[i];
        const dx = lander.x - gasTank.x;
        const dy = lander.y - gasTank.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < gasTankRadius + 25) {
            lander.fuel += gasTankRefuelAmount;
            if (lander.fuel > 100) lander.fuel = 100;
            gasTanks.splice(i, 1);
            i--;

            // Add a new gas tank to the mountain
            const x = Math.random() * (canvas.width - gasTankRadius * 2) + gasTankRadius;
            const y = getY(x) - gasTankRadius;
            gasTanks.push({
                x,
                y
            });
            playRefuelSound();
            score += 100;
        }
    }
}

function clearCanvas(canvas, context, color) {
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
}

function gameLoop() {
    //ctx.clearRect(0, 0, canvas.width, canvas.height);
    clearCanvas(canvas, ctx, 'black');
    generateTerrain();
    drawGasTanks(); // Draw the gas tanks on the mountain
    if (!landed) {
        updateLander();
        refuelLander(); // Check if the lander is refueling
        drawLander();
        checkLanding();
    } else {
        if (successfulLanding) {
            drawLander();
            if (Math.random() < 0.03) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                fireworks.push(new Firework2(x, y, color, ctx));
            }

            for (const firework of fireworks) {
                firework.update();
                firework.draw();
            }

            fireworks = fireworks.filter(fw => !fw.isDone());
        } else {
            if (explosion !== null) {
                explosion.update();
                if (explosion.isDone()) {
                    resetLander();
                    explosion = null;
                    landed = false;
                    successfulLanding = false;
                }
            }
            // for (let i = 0; i < fireworksV1.length; i++) {
            //     const firework = fireworksV1[i];
            //     firework.update();
            //     firework.draw();
            //     if (firework.life <= 0) {
            //         fireworksV1.splice(i, 1);
            //         i--;
            //     }
            // }

            // fireworkCounter++;
            // if (fireworkCounter % fireworkInterval === 0) {
            //     fireworksV1.push(new Firework(lander.x, lander.y));
            // }
        }
    }
    drawFuelBar();
    drawScore();
    requestAnimationFrame(gameLoop);
}

for (let i = 0; i < gasTankAmount; i++) {
    const x = Math.random() * (canvas.width - gasTankRadius * 2) + gasTankRadius;
    const y = getY(x) - gasTankRadius - 10; // Add a -10 offset to move the gas tank above the mountain surface
    gasTanks.push({
        x,
        y
    });
}
gameLoop();