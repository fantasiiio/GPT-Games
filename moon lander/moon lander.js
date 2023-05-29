const canvas = document.getElementById('gameCanvas');


const ctx = canvas.getContext('2d');

let enableManualControl = false;
let landers = [];
let targets = [];
let asteroids = [];
let asteroidsCount = 10;
let targetCount = 1
const populationCount = enableManualControl ? 1 : 100;
let targetRadius = 200;
let numRadarRays = 5;

const mountainResolution = 0.005;
const mountainHeightFactor = 0.4;
const maxYOffset = 3.5;
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

const saveGenerationBtn = document.getElementById('saveGenerationBtn');
const skipGenerationBtn = document.getElementById('skipGenerationBtn');
const stopShipBtn = document.getElementById('stopShipBtn');
const numberOfTargets = document.getElementById('numberOfTargets');
const numberOfStarship = document.getElementById('numberOfStarship');

numberOfTargets.value = targetCount;
numberOfStarship.value = populationCount;

numberOfStarship.addEventListener('change', () => {
    populationCount = numberOfStarship.value;
})

numberOfTargets.addEventListener('change', () => {
    targetCount = numberOfTargets.value;
    generateTargets();
})
saveGenerationBtn.addEventListener('click', () => {
    geneticAlgorithm.savePopulation()
    alert("saved")
});

skipGenerationBtn.addEventListener('click', () => {
    killAll();
});

stopShipBtn.addEventListener('click', () => {
    landers[0].rigidBody.velocity = new Vector(0, 0);
    landers[0].rigidBody.angularVelocity = 0;
});

const deathTimer = Number.MAX_SAFE_INTEGER;
const gravity = 0.0;
const maxThrustPower = 0.1;
const maxSideThrustPower = 0.05;
const landingSpeed = 1;
const maxAngularVelocity = 0.1;
const maxRotationAccel = 0.002;
const FuelConsumption_thrust = 0.25;
const FuelConsumption_rotate = 0.05;
let score = 0;
let zoomLevel = 0.25;

let platform = {
    x: (Math.random() * (canvas.width - 200) + 100) / zoomLevel,
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


function saveSettings() {
    localStorage.setItem('moonLanderSettings', JSON.stringify({
        mountainResolution,
        mountainHeightFactor,
        maxYOffset,
        gasTankAmount,
        targetCount,
        populationCount,
        deathTimer,
        gravity,
        maxThrustPower,
        landingSpeed,
        maxAngularVelocity,
        maxRotationAccel,
        FuelConsumption_thrust,
        FuelConsumption_rotate,
        zoomLevel
    }));
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('moonLanderSettings'));
    if (settings) {
        mountainResolution = settings.mountainResolution;
        mountainHeightFactor = settings.mountainHeightFactor;
        maxYOffset = settings.maxYOffset;
        gasTankAmount = settings.gasTankAmount;
        targetCount = settings.targetCount;
        populationCount = settings.populationCount;
        deathTimer = settings.deathTimer;
        gravity = settings.gravity;
        maxThrustPower = settings.maxThrustPower;
        landingSpeed = settings.landingSpeed;
        maxAngularVelocity = settings.maxAngularVelocity;
        maxRotationAccel = settings.maxRotationAccel;
        FuelConsumption_thrust = settings.FuelConsumption_thrust;
        FuelConsumption_rotate = settings.FuelConsumption_rotate;
        zoomLevel = settings.zoomLevel;
    }
}

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
let terrain = new Terrain(canvas.width / zoomLevel, canvas.height / zoomLevel, mountainResolution, mountainHeightFactor, maxYOffset);
terrain.generateTerrain();

// Init Genetic Algorithm
function initGeneticAlgorithm(populationSize) {
    //const populationSize = 50;
    const inputSize = 8 + numRadarRays;
    const hiddenSize = 6;
    const outputSize = 2;
    const mutationRate = 0.1;
    const maxGenerations = 1000;
    const inputs = []; // Vous pouvez ajouter des données d'entrée spécifiques ici
    const expectedOutputs = []; // Vous pouvez ajouter des sorties attendues spécifiques ici
    let population = [];
    for (let i = 0; i < populationSize; i++) {
        const neuralNetwork = new NeuralNetwork2([inputSize, hiddenSize, outputSize]);
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



function generateObjectPositions(positionsCount, minDistance = 500, maxDistance = 5000) {
    let positions = [];

    if (positionsCount == 0)
        return;
    // Add first positions
    let center = new Vector(200 + Math.random() * (canvas.width / zoomLevel - 200), 200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
    positions.push(new Vector(center.x, center.y));

    for (let i = 0; i < positionsCount-1; i++) {
        let newPositions = null;

        // Try up to 100 times to find a valid position for a new positions.
        // If it can't find a valid position after 100 tries, it breaks out of the loop to prevent freezing your application.
        for (let tries = 0; tries < 100; tries++) {
            let theta = Math.random() * 2 * Math.PI; // Random angle
            let distance = minDistance + Math.random() * (maxDistance - minDistance); // Random distance within min and max

            // Calculate new position based on a random existing positions
            let randomExistingPositions = positions[Math.floor(Math.random() * positions.length)];
            let newX = randomExistingPositions.x + distance * Math.cos(theta);
            let newY = randomExistingPositions.y + distance * Math.sin(theta);

            let isTooCloseToExistingPositions = positions.some(positions => {
                let dx = positions.x - newX;
                let dy = positions.y - newY;
                return Math.sqrt(dx * dx + dy * dy) < minDistance; // Check distance to each existing positions
            });

            if (!isTooCloseToExistingPositions && newX >= 200 && newX <= (canvas.width / zoomLevel - 200) && newY >= 200 && newY <= (canvas.height / zoomLevel / 3 * 2 - 200)) {
                let center = new Vector(200 + Math.random() * (canvas.width / zoomLevel - 200), 200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
                newPositions = new Vector(center.x, center.y);
                break; // If a valid position is found, break out of the loop
            }
        }

        // If a valid position was found, add new positions
        if (newPositions !== null) {
            positions.push(newPositions);
        }
    }

    return positions;
}


function generateAsteroids() {
    if (asteroidsCount == 0)
        return;

    asteroids.length = 0;
    let positions = generateObjectPositions(asteroidsCount);
    for (let position of positions) {
        let asteroid = new Asteroid(position, Math.random()*400+ 100);
        asteroids.push(asteroid);
    }
}

function generateTargets() {
    let positions = generateObjectPositions(targetCount);
    targets = positions;
    // targets = [{x: canvas.width / 2 / zoomLevel, y: canvas.height / 4 / zoomLevel}];
}

let populationCreated = false;

function restart(newPopulation) {
    populationCreated = false;
    //generateTargets();
    //generateAsteroids();
    for (let i = 0; i < newPopulation.length; i++) {
        landers[i].neuralNetwork = newPopulation[i];
        landers[i].neuralNetwork.isDead = false;
        landers[i].resetLander();
    }
    populationCreated = true;
}

let geneticAlgorithm = initGeneticAlgorithm(populationCount);
geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
    restart(newPopulation);
}
geneticAlgorithm.run(bestIndividual => {
    console.log("L'algorithme g\xE9n\xE9tique a terminé. Meilleur individu : ", bestIndividual);
});



for (let i = 0; i < populationCount; i++) {
    const lander = new Lander(canvas.width / 2 / zoomLevel, canvas.height / 2 / zoomLevel, geneticAlgorithm.population[i]);
    landers.push(lander);
}



canvas.addEventListener('mousemove', (event) => {
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.clientX) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.clientY) / zoomLevel - pan.y - 30;
    if (targetFound) {
        targetFound.x = mousePosition.x;
        targetFound.y = mousePosition.y;
    } else if (asteroidFound) {
        asteroidFound.rigidBody.position.x = mousePosition.x;
        asteroidFound.rigidBody.position.y = mousePosition.y;
    } else if (panning) {
        panEvent(event);
    }

});

function changeAllTarget(mousePosition) {
    for (let lander of landers) {
        lander.target = null;
    }
    targets[0] = {
        x: mousePosition.x / zoomLevel,
        y: mousePosition.y / zoomLevel
    };
}

function killAll() {
    for (let lander of landers) {
        lander.die()
    }
}

let targetFound = null;
let asteroidFound = null;
let panning = false;

canvas.addEventListener('mousedown', (event) => {
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.clientX) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.clientY) / zoomLevel - pan.y - 30;
    if (event.button == 1) {
        panning = true;
    } else if (event.button == 0) {
        // check if the mouse is in a target circle
        targetFound = null;
        for (let i = 0; i < targetCount; i++) {
            let distance = Math.sqrt(Math.pow(targets[i].x - mousePosition.x, 2) + Math.pow(targets[i].y - mousePosition.y, 2));
            if (distance < targetRadius) {
                targetFound = targets[i];
                return;
            }
        }

        asteroidFound = null;
        for (let i = 0; i < asteroidsCount; i++) {
            if(asteroids[i].polygon.isPointInside(mousePosition)){
                asteroidFound = asteroids[i];
                return;
            }
        }

    }
    //changeAllTarget(mousePosition);
});

canvas.addEventListener('mouseup', (event) => {
    targetFound = null;
    asteroidFound = null;
    lastCursorX = null;
    lastCursorY = null;
    panning = false;
});


let lastCursorX = null;
let lastCursorY = null;
let pan = {
    x: 0,
    y: 0
};

function panEvent(event) {
    event.preventDefault()

    pan.x += event.movementX / zoomLevel;
    pan.y += event.movementY / zoomLevel;
}

function zoom(event) {
    event.preventDefault();

    const scaleFactor = 1.1;
    const zoomFactor = event.deltaY < 0 ? scaleFactor : 1 / scaleFactor;

    const mousePosBefore = new Vector(event.clientX / zoomLevel - pan.x, event.clientY / zoomLevel - pan.y);
    zoomLevel *= zoomFactor;
    const mousePosAfter = new Vector(event.clientX / zoomLevel - pan.x, event.clientY / zoomLevel - pan.y);
    
    pan.x = pan.x + mousePosAfter.x - mousePosBefore.x;
    pan.y = pan.y + mousePosAfter.y - mousePosBefore.y;
}

// Add an event listener for the wheel event
canvas.addEventListener('wheel', (event) => {
    event.preventDefault(); // Prevent the default scrolling behavior
    zoom(event);
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
    // ctx.beginPath();
    // ctx.moveTo(position.x - crossLength, position.y);
    // ctx.lineTo(position.x + crossLength, position.y);
    // ctx.moveTo(position.x, position.y - crossLength);
    // ctx.lineTo(position.x, position.y + crossLength);
    // ctx.strokeStyle = 'white';
    // ctx.lineWidth = 2;
    // ctx.stroke();

    drawText(index + 1, position.x, position.y); // Draw target index

    // Draw circle
    ctx.beginPath();
    ctx.arc(position.x, position.y, size - 50, 0, 2 * Math.PI);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();
}
generateTargets();
generateAsteroids();

function updateLanderManually(lander) {

    if (keys['ArrowLeft']) {
        lander.rigidBody.angularVelocity -= maxRotationAccel;
    }
    if (keys['ArrowRight']) {
        lander.rigidBody.angularVelocity += maxRotationAccel;
    }
    if (!keys['ArrowLeft'] && !keys['ArrowRight']) {
        //lander.rigidBody.angularVelocity = 0;
    }
    if (keys['ArrowUp']) {
        lander.thrust = maxThrustPower;
    } else {
        lander.thrust = 0;
    }
}

//let predictionModel = new NeuralNetwork2([10, 8, 8]);
function drawPoint(point) {
    let color;
    color = 'white';

    ctx.beginPath();
    ctx.arc(point.x, point.y, 10, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.closePath();
}

function gameLoop() {
    if (!gameLoop.debounced) {
        gameLoop.debounced = true;
        setTimeout(() => {
            gameLoop.debounced = false;

            if (!populationCreated)
                requestAnimationFrame(gameLoop);

            if (keysPressed["KeyS"])
                geneticAlgorithm.savePopulation();
            //ctx.clearRect(0, 0, canvas.width, canvas.height);
            clearCanvas(canvas, ctx, '#03002e');
            ctx.save();
            ctx.scale(zoomLevel, zoomLevel);
            ctx.translate(pan.x, pan.y);
            terrain.draw(ctx);
            drawGasTanks(); // Draw the gas tanks on the mountain
            for (let i = 0; i < asteroidsCount; i++) {
                asteroids[i].rigidBody.update();
                asteroids[i].getPolygon();
                asteroids[i].draw();
            }
            let index = 0;
            let inputArrays = [];
            let targetArrays = [];
            for (let lander of landers) {
                if (!lander.neuralNetwork.isDead) {
                    if (!lander.target || lander.checkTargetReached(lander.target)) {
                         if (!lander.target || targets.length > 1) {
                            if(targets.length > 1)
                                lander.neuralNetwork.currentFitness += 5000;
                            lander.changeTarget(targets[lander.targetIndex++]);
                            lander.targetIndex %= targets.length;
                        }
                    }

                    lander.updateLander(asteroids);
                    if (index == 0 && enableManualControl) {
                        updateLanderManually(lander);
                    } else {
                        lander.applyNeuralNetwork(lander.target); // Update the neural network input
                    }

                    if (!lander.landed) {


                        inputArrays.push(lander.lastSpaceshipStates);
                        targetArrays.push(lander.spaceshipStates.slice(0, lander.spaceshipStates.length - 2));

                        lander.calculateFitness(lander.target, null)
                        lander.refuelLander(terrain); // Check if the lander is refueling
                        lander.checkLanding();
                    }
                    lander.drawLander();
                    for (let i = 0; i < asteroidsCount; i++) {
                        lander.handleAsteroidCollision(asteroids[i]);
                    }
                }
                index++;
            }

            //predictionModel.trainBatch(inputArrays, targetArrays);

            for (let i = 0; i < targetCount; i++) {
                drawTarget(targets[i], targetRadius, i);
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