const canvas = document.getElementById('gameCanvas');


const ctx = canvas.getContext('2d');

const mountainResolution = 0.005;
const mountainHeightFactor = 0.4;
const maxYOffset = 1.5;
let fireworksV1 = [];
let fireworks = [];
let explosion = null;

let fireworkCounter = 0;
const fireworkInterval = 100;
//let successfulLanding = false;
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




const gravity = 0.01;
const maxThrustPower = 0.05;
const landingSpeed = 1;
const maxAngularVelocity = 0.1;
const maxRotationAccel = 0.05;
const FuelConsumption_thrust = 0.25;
const FuelConsumption_rotate = 0.05;
let score = 0;
let zoomLevel = 0.5;

let platform = {
    x: Math.random() * (canvas.width - 200) + 100,
    y: canvas.height / zoomLevel - 50,
    width: 200,
    height: 10
};


const keys = {};
const keysPressed = {};

document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
    keysPressed[e.code] = true;
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
    const fuelProgressWidth = (landers[0].fuel / 100) * fuelBarWidth;
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
    //thrustSound.play();
}

function stopThrustSound() {
    thrustSound.isPlaying = false;
    thrustSound.currentTime = 0;
    thrustSound.pause();
}

function playRefuelSound() {
    refuelSound.currentTime = 0;
    //refuelSound.play();
}

let firework = null;


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

function clearCanvas(canvas, context, color) {
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
}
let terrain = new Terrain(canvas.width * 2, canvas.height * 2, mountainResolution, mountainHeightFactor, maxYOffset);
terrain.generateTerrain();

// Init Genetic Algorithm
function initGeneticAlgorithm(populationSize) {
    //const populationSize = 50;
    const inputSize = 8;
    const hiddenSize = 5;
    const outputSize = 2;
    const mutationRate = 0.1;
    const maxGenerations = 1000;
    const inputs = []; // Vous pouvez ajouter des données d'entrée spécifiques ici
    const expectedOutputs = []; // Vous pouvez ajouter des sorties attendues spécifiques ici
    let population = [];
    for (let i = 0; i < populationSize; i++) {
        const neuralNetwork = new NeuralNetwork(inputSize, hiddenSize, outputSize);
        population.push(neuralNetwork);
    }
    const ga = new GeneticAlgorithm(
        population,
        inputSize,
        hiddenSize,
        outputSize,
        mutationRate,
        maxGenerations,
        inputs,
        expectedOutputs
    );

    return ga;
}
let landers = [];
let targets = [];
let asteroids = [];
let asteroidsCount = 10;
let targetCount = 1;

function generateTargets() {
    targets.length = 0;
    let center = new Vector(200 + Math.random() * (canvas.width / zoomLevel - 200), 200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
    targets.push(center);
}

function generateAsteroids(minDistance = 500, maxDistance = 5000) {
    asteroids.length = 0;
    const minRadius = 100;
    const maxRadius = 100;
    // Add first asteroid
    let center = new Vector(200 + Math.random() * (canvas.width / zoomLevel - 200), 200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
    asteroids.push(new Asteroid(center, minRadius, maxRadius, 5 + Math.random()*5));

    for (let i = 0; i < asteroidsCount; i++) {
        let newAsteroid = null;

        // Try up to 100 times to find a valid position for a new asteroid.
        // If it can't find a valid position after 100 tries, it breaks out of the loop to prevent freezing your application.
        for (let tries = 0; tries < 100; tries++) {
            let theta = Math.random() * 2 * Math.PI; // Random angle
            let distance = minDistance + Math.random() * (maxDistance - minDistance); // Random distance within min and max

            // Calculate new position based on a random existing asteroid
            let randomExistingAsteroid = asteroids[Math.floor(Math.random() * asteroids.length)];
            let newX = randomExistingAsteroid.rigidBody.position.x + distance * Math.cos(theta);
            let newY = randomExistingAsteroid.rigidBody.position.y + distance * Math.sin(theta);

            let isTooCloseToExistingAsteroid = asteroids.some(asteroid => {
                let dx = asteroid.rigidBody.position.x - newX;
                let dy = asteroid.rigidBody.position.y - newY;
                return Math.sqrt(dx * dx + dy * dy) < minDistance; // Check distance to each existing asteroid
            });

            if (!isTooCloseToExistingAsteroid && newX >= 200 && newX <= (canvas.width / zoomLevel - 200) && newY >= 200 && newY <= (canvas.height / zoomLevel / 3 * 2 - 200)) {
                let center = new Vector(200 + Math.random() * (canvas.width / zoomLevel - 200), 200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
                newAsteroid = new Asteroid(center, minRadius, maxRadius, 5 + Math.random()*5);
                break; // If a valid position is found, break out of the loop
            }
        }

        // If a valid position was found, add new asteroid
        if (newAsteroid !== null) {
            asteroids.push(newAsteroid);
        }
    }

    asteroidsCount = asteroids.length;
}

let populationCreated = false;

function restart(newPopulation) {
    populationCreated = false;
    generateTargets();
    generateAsteroids();
    for (let i = 0; i < newPopulation.length; i++) {
        landers[i].neuralNetwork = newPopulation[i];
        landers[i].neuralNetwork.isDead = false;
        landers[i].resetLander();
    }
    populationCreated = true;
}

const populationCount = 100;
let geneticAlgorithm = initGeneticAlgorithm(populationCount);
geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
    restart(newPopulation);
}
geneticAlgorithm.run(bestIndividual => {
    console.log("L'algorithme g\xE9n\xE9tique a terminé. Meilleur individu : ", bestIndividual);
});



for (let i = 0; i < populationCount; i++) {
    const lander = new Lander(canvas.width / 2, 50, geneticAlgorithm.population[i]);
    landers.push(lander);
}

let mousePosition = new Vector(0, 0);

canvas.addEventListener('mousemove', (event) => {
    mousePosition.x = event.clientX;
    mousePosition.y = event.clientY;
});

function changeAllTarget(mousePosition) {
    for (let lander of landers) {
        lander.target = new Vector(mousePosition.x, mousePosition.y);
    }
}

function killAll() {
    for (let lander of landers) {
        lander.die()
    }
}
canvas.addEventListener('mousedown', (event) => {
    mousePosition.x = event.clientX / zoomLevel;
    mousePosition.y = event.clientY / zoomLevel;
    //changeAllTarget(mousePosition);
});


geneticAlgorithm.loadPopulation()


function drawText(text, x, y) {
    ctx.font = '40px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
}

function drawTarget(position, size, index) {
    const crossLength = size / 2;

    // Draw cross lines
    ctx.beginPath();
    ctx.moveTo(position.x - crossLength, position.y);
    ctx.lineTo(position.x + crossLength, position.y);
    ctx.moveTo(position.x, position.y - crossLength);
    ctx.lineTo(position.x, position.y + crossLength);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();

    //drawText(index + 1, position.x, position.y); // Draw target index

    // Draw circle
    ctx.beginPath();
    ctx.arc(position.x, position.y, size, 0, 2 * Math.PI);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function gameLoop() {
    if (!gameLoop.debounced) {
        gameLoop.debounced = true;
        setTimeout(() => {
            gameLoop.debounced = false;

            if (!populationCreated)
                requestAnimationFrame(gameLoop);

            if (keysPressed["s"])
                geneticAlgorithm.savePopulation();
            if (keysPressed["Enter"])
                killAll();
            //ctx.clearRect(0, 0, canvas.width, canvas.height);
            clearCanvas(canvas, ctx, '#03002e');
            ctx.save();
            ctx.scale(zoomLevel, zoomLevel);
            terrain.draw(ctx);
            drawGasTanks(); // Draw the gas tanks on the mountain
            for (let i = 0; i < asteroidsCount; i++) {
                asteroids[i].rigidBody.update();
                asteroids[i].getPolygon();
                asteroids[i].draw();
            }

            for (let lander of landers) {
                if (!lander.neuralNetwork.isDead) {
                    if (!lander.target || lander.checkTargetReached(lander.target)) {
                        lander.changeTarget(targets[lander.targetIndex]);
                        if (lander.targetIndex < targets.length-1)
                            lander.targetIndex++;
                    }
                    lander.calculateFitness(lander.target)
                    lander.applyNeuralNetwork(lander.target); // Update the neural network input 

                    if (!lander.landed) {
                        lander.updateLander();
                        lander.refuelLander(terrain); // Check if the lander is refueling
                        lander.checkLanding();
                    }
                    lander.drawLander();
                    for (let i = 0; i < asteroidsCount; i++) {
                        lander.handleAsteroidCollision(asteroids[i]);
                    }
                }
            }

            for (let i = 0; i < targetCount; i++) {
                drawTarget(targets[i], 50, i);
            }

            drawFuelBar();
            drawScore();
            ctx.restore();
            requestAnimationFrame(gameLoop);
        }, 1);
    }

    for (let key in keysPressed) {
        delete keysPressed[key];
    }
}



for (let i = 0; i < gasTankAmount; i++) {
    const x = Math.random() * (canvas.width - gasTankRadius * 2) + gasTankRadius;
    const y = terrain.getY(x) - gasTankRadius - 10; // Add a -10 offset to move the gas tank above the mountain surface
    gasTanks.push({
        x,
        y
    });
}
gameLoop();