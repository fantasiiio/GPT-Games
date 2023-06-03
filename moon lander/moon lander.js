const canvas = document.getElementById('gameCanvas');


const ctx = canvas.getContext('2d');

let enableManualControl = false;
let useSpaceStation = true;
let landers = [];
let targets = [];
let asteroids = [];
let walls = [];
let asteroidsCount = 0;
let targetCount = 2;
let cycleTargets = false;
const populationCount = enableManualControl ? 1 : 100;
let targetRadius = 200;
let numRadarRays = 5;
let startingTimeBonus = 2000;
let frameCount = 0;
let geneticAlgorithm = null;
const deathTimer = Number.MAX_VALUE;
const gravity = 0.0;
const maxThrustPower = 0.1;
const maxSideThrustPower = 0.05;
const landingSpeed = 1;
const maxAngularVelocity = 0.1;
const maxRotationAccel = 0.002;
const FuelConsumption_thrust = 0.25;
const FuelConsumption_rotate = 0.25;


let score = 0;
let zoomLevel = 0.25;


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
const resourceRadius = 10;
const resourceAmount = 50;
const resourceRefuelAmount = 25;
const audioContext = new(window.AudioContext || window.webkitAudioContext)();
const thrustSound = new Audio('thrust.mp3');
//thrustSound.play();
const refuelSound = new Audio('boost-100537.mp3');

// Create gas tanks array
let resources = [];
let drawingMode = false;
let drawing = false;

const saveGenerationBtn = document.getElementById('saveGenerationBtn');
const skipGenerationBtn = document.getElementById('skipGenerationBtn');
const stopShipBtn = document.getElementById('stopShipBtn');
const numberOfTargets = document.getElementById('numberOfTargets');
const numberOfStarship = document.getElementById('numberOfStarship');
const drawBtn = document.getElementById('drawBtn');

numberOfTargets.value = targetCount;
numberOfStarship.value = populationCount;

numberOfStarship.addEventListener('change', () => {
    populationCount = numberOfStarship.value;
})

numberOfTargets.addEventListener('change', () => {
    targetCount = numberOfTargets.value;
    generateTargets();
})

drawBtn.addEventListener('click', () => {
    drawingMode = true;
});

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
        resourceAmount,
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
        resourceAmount = settings.resourceAmount;
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


function drawResources(resourceCounts) {
    ctx.save();
    for (const [index, resource] of resources.entries()) {
        ctx.beginPath();

        ctx.arc(resource.x, resource.y, resourceRadius, 0, 2 * Math.PI);
        ctx.fillStyle = "#03C03C";
        ctx.fill();
        ctx.stroke();

        // If this resource has been harvested, display the count
        if (resourceCounts[index] !== undefined) {
            ctx.font = "10px Arial";
            ctx.fillStyle = "black";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(resourceCounts[index].toString(), resource.x, resource.y);
        }
    }
    ctx.restore();
}

function clearCanvas(canvas, context, color) {
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
}
let terrain = new Terrain(canvas.width / zoomLevel, canvas.height / zoomLevel, mountainResolution, mountainHeightFactor, maxYOffset);
terrain.generateTerrain();

let spaceStation = new SpaceStation(canvas.width / zoomLevel / 2, canvas.height / zoomLevel / 2 + 1000, 200, 200, 100, 10, 0);

function getNeuralNetworksFromLanders() {
    let neuralNetworks = [];
    for (let lander of landers) {
        neuralNetworks.push(lander.neuralNetwork);
    }
    return neuralNetworks;
}

function addNeuralNetworkToLanders(name) {
    for (let lander of landers) {
        lander.addNeuralNetwork(new NeuralNetwork2([inputSize, hiddenSize, outputSize]), name);
    }
}

const inputSize = 8 + numRadarRays;
const hiddenSize = 10;
const outputSize = 3;

// Init Genetic Algorithm
function initGeneticAlgorithm() {
    //const populationSize = 50;

    const mutationRate = 0.1;
    const maxGenerations = 1000;
    const inputs = []; // Vous pouvez ajouter des données d'entrée spécifiques ici
    const expectedOutputs = []; // Vous pouvez ajouter des sorties attendues spécifiques ici
    let population = getNeuralNetworksFromLanders();
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

    for (let i = 0; i < positionsCount - 1; i++) {
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
        let asteroid = new Asteroid(position, Math.random() * 200 + 100);
        asteroids.push(asteroid);
    }
}

function generateTargets() {
    let positions = generateObjectPositions(targetCount);
    targets = positions || [];
}

let populationCreated = false;

function restart(newPopulation) {
    populationCreated = false;
    //generateAsteroids();
    for (let i = 0; i < newPopulation.length; i++) {
        landers[i].neuralNetwork = newPopulation[i];
        landers[i].resetLander();
        //landers[i].rigidBody.angle = Math.PI/2;
        //landers[i].rigidBody.velocity = new Vector(10, 0);
    }
    changeAllTarget();
    populationCreated = true;
}



generateTargets();
generateAsteroids();


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
    } else if (drawing) {
        walls[walls.length - 1].push(mousePosition)
    }

});

function changeAllTarget(position) {
    for (let lander of landers) {
        if (targets.length > 0)
            lander.target = targets[0];
        else if (useSpaceStation)
            lander.target = spaceStation.dockPosition;
        else
            lander.target = new Vector(canvas.width / zoomLevel / 2, canvas.height / zoomLevel - 50);
    }
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
            if (asteroids[i].polygon.isPointInside(mousePosition)) {
                asteroidFound = asteroids[i];
                return;
            }
        }

        if (drawingMode) {
            walls.push([])
            drawing = true;
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
    drawing = false;
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

//geneticAlgorithm.loadPopulation()


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

function drawLines(listOfPoints, color = 'white') {
    ctx.lineWidth = 5;
    for (let points of listOfPoints) {
        if (points.length < 2) continue; // If less than 2 points, no line can be drawn

        ctx.beginPath(); // Begin the drawing path
        ctx.moveTo(points[0].x, points[0].y); // Move to the first point

        // Loop through each point in the current list
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y); // Draw a line to the next point
        }

        ctx.strokeStyle = color; // Set the color of the line
        ctx.stroke(); // Apply the line stroke
    }
}

function getCheckedItemCount(network) {
    const checkedItemCount = {
        fitness: 0,
        inputs: 0,
        hiddenLayers: 0,
        outputs: 0
    };

    network.fitness.forEach((item) => {
        if (item.checked) {
            checkedItemCount.fitness++;
        }
    });

    network.inputs.forEach((item) => {
        if (item) {
            checkedItemCount.inputs++;
        }
    });

    network.hiddenLayers.forEach((item) => {
        if (item) {
            checkedItemCount.hiddenLayers++;
        }
    });

    network.outputs.forEach((item) => {
        if (item) {
            checkedItemCount.outputs++;
        }
    });

    return checkedItemCount;
}

function checkNodesPerLayer(individualData, config) {
    const nodesPerLayer = individualData.nodesPerLayer;
    const inputsCount = config.inputs.reduce((sum, input) => sum + (input.checked ? input.inputCount : 0), 0);
    const hiddenLayersCount = config.hiddenLayers.length;
    const outputs = config.outputs;
    const outputsCount = outputs.filter((output) => output.checked).length;

    if (nodesPerLayer.length !== hiddenLayersCount + 2) {
        return false; // Number of layers doesn't match
    }

    if (nodesPerLayer[0] !== inputsCount) {
        return false; // Number of input neurons doesn't match
    }

    if (nodesPerLayer[nodesPerLayer.length - 1] !== outputsCount) {
        return false; // Number of output neurons doesn't match
    }

    for (let i = 1; i <= hiddenLayersCount; i++) {
        if (nodesPerLayer[i] != config.hiddenLayers[i - 1]) {
            return false; // Number of neurons in hidden layers doesn't match
        }
    }

    return true; // All checks passed
}


function getMatchingNodesPerLayer(config) {
    const inputsCount = config.inputs.length;
    const hiddenLayersCount = config.hiddenLayers.length;
    const outputsCount = config.outputs.length;

    const nodesPerLayer = [inputsCount];
    for (let i = 0; i < hiddenLayersCount; i++) {
        nodesPerLayer.push(config.hiddenLayers[i].defaultValue);
    }
    nodesPerLayer.push(outputsCount);

    return nodesPerLayer;
}


let nnConfigs = {};

function loadLanders() {
    const config = JSON.parse(localStorage.getItem('nnConfig'));

    if (config && config.networks) {
        nnConfigs.length = 0;
        let networkCount = 0;

        config.networks.forEach((network) => {
            // networkCount++;
            // let nnConfig = {
            //     id: networkCount,
            //     inputs: [],
            //     hiddenLayers: [],
            //     outputs: [],
            //     fitness: [],
            //     name: network.name,
            //     isDefault: network.isDefault || false
            // };

            // network.fitness.forEach((fitness, index) => {
            //     let newValue = {
            //         value: network.fitness[index].checked,
            //         multiplyFactor: network.fitness[index].multiplyFactor
            //     }
            //     nnConfig.fitness.push(newValue);
            // });

            // for (let i = 0; i < network.inputs.length; i++) {
            //     nnConfig.inputs.push({
            //         value: network.inputs[i].checked,
            //         inputCount: network.inputs[i].inputCount
            //     });
            // }
            // for (let i = 0; i < network.hiddenLayers.length; i++) {
            //     nnConfig.hiddenLayers.push({
            //         value: network.hiddenLayers[i]
            //     });
            // }
            // for (let i = 0; i < network.outputs.length; i++) {
            //     nnConfig.outputs.push({
            //         value: network.outputs[i].checked
            //     });
            // }

            nnConfigs[network.name] = network;

            let key = Object.keys(localStorage).find(key => key == 'NeuralNetwork_' + network.name);
            let populationData = JSON.parse(localStorage.getItem(key));
            if (populationData) {
                // For each saved individual, load the individual's data into the corresponding Lander
                populationData.forEach((individualData, i) => {
                    let lander = landers[i];
                    if (!lander)
                        lander = new Lander(canvas.width / 2 / zoomLevel, canvas.height / 2 / zoomLevel, i);

                    Object.setPrototypeOf(individualData, NeuralNetwork2.prototype);

                    if (!checkNodesPerLayer(individualData, network)) {
                        console.error('The number of nodes per layer in the saved NeuralNetwork does not match the number of nodes per layer in the config.');
                        return false;
                    }
                    // Add the loaded NeuralNetwork to the Lander
                    lander.addNeuralNetwork(individualData, network.name);
                    if (!landers[i])
                        landers.push(lander);

                    // Convert weights and biases back to Matrix objects
                    individualData.weights = individualData.weights.map(weightMatrix => Matrix.map(weightMatrix, x => x));
                    individualData.biases = individualData.biases.map(biasMatrix => Matrix.map(biasMatrix, x => x));
                });
            } else {
                for (let i = 0; i < populationCount; i++) {
                    let nodesPerLayer = getMatchingNodesPerLayer(network);
                    let lander = landers[i];
                    if (!lander)
                        lander = new Lander(canvas.width / 2 / zoomLevel, canvas.height / 2 / zoomLevel, i);

                    lander.addNeuralNetwork(new NeuralNetwork2(nodesPerLayer), name);
                    if (!landers[i])
                        landers.push(lander);
                }

            }
            if(network.isDefault)
                SetLandersNeuralNetwork(network.name);
        });
    }

    return true;
}


function SetLandersNeuralNetwork(name) {
    for (let i = 0; i < populationCount; i++) {
        landers[i].setActiveNeuralNetwork(name);
    }
}

if (!loadLanders()) {
    for (let i = 0; i < populationCount; i++) {
        const lander = new Lander(canvas.width / 2 / zoomLevel, canvas.height / 2 / zoomLevel, i);
        landers.push(lander);
    }
}


changeAllTarget();

geneticAlgorithm = initGeneticAlgorithm(populationCount);
geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
    restart(newPopulation);
}
geneticAlgorithm.run(bestIndividual => {
    console.log("L'algorithme g\xE9n\xE9tique a terminé. Meilleur individu : ", bestIndividual);
});



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
            if (useSpaceStation)
                spaceStation.draw();

            let harvestedResources = countHarvestedResources()
            drawResources(harvestedResources);
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
                    lander.checkChangeAction();
                    if (lander.checkTargetReached(lander.target)) {
                        if (targets.length > 1 && !lander.harvesting) {
                            // if(targets.length > 1)
                            //      lander.neuralNetwork.currentFitness += 5000;
                            lander.targetIndex++;
                            if (cycleTargets) {
                                lander.targetIndex %= targets.length;
                            } else {
                                if (lander.targetIndex >= targets.length) {
                                    lander.targetIndex = targets.length - 1;
                                }
                            }
                            lander.changeTarget(targets[lander.targetIndex]);
                        }
                    }


                    lander.updateLander(asteroids);
                    if (index == 0 && enableManualControl) {
                        updateLanderManually(lander);
                    } else {
                        lander.applyNeuralNetwork(lander.target); // Update the neural network input
                    }

                    if (!lander.neuralNetwork.isDead) {
                        // inputArrays.push(lander.lastSpaceshipStates);
                        // targetArrays.push(lander.spaceshipStates.slice(0, lander.spaceshipStates.length - 2));

                        lander.calculateFitness()
                        lander.harvestResource(terrain); // Check if the lander is refueling
                        lander.checkLanding();
                        if (useSpaceStation)
                            lander.checkDocking();
                    }
                    lander.drawLander();
                    for (let i = 0; i < asteroidsCount; i++) {
                        lander.handleCollision(asteroids[i]);
                    }
                } else {
                    lander.calculateFitness()
                    lander.drawLander();
                }
                index++;
            }

            //predictionModel.trainBatch(inputArrays, targetArrays);

            for (let i = 0; i < targetCount; i++) {
                drawTarget(targets[i], targetRadius, i);
            }
            //spaceStation.polygon.draw();
            drawLines(walls);

            //drawFuelBar();
            drawScore();
            ctx.restore();
            frameCount++;
            requestAnimationFrame(gameLoop);
        }, 1);
    }

    for (let key in keysPressed) {
        delete keysPressed[key];
    }
}

function countHarvestedResources() {
    let harvestedResourceCounts = {};

    for (let i = 0; i < landers.length; i++) {
        const lander = landers[i];

        for (let j = 0; j < lander.harvestedResources.length; j++) {
            const resourceIndex = lander.harvestedResources[j];

            if (harvestedResourceCounts[resourceIndex] === undefined) {
                harvestedResourceCounts[resourceIndex] = 1;
            } else {
                harvestedResourceCounts[resourceIndex]++;
            }
        }
    }

    return harvestedResourceCounts;
}

function getRandomPositionInsideCircle(centerX, centerY, radius) {
    // Generate a random radius within the circle
    const randomRadius = Math.random() * radius;

    // Generate a random angle
    const angle = Math.random() * 2 * Math.PI;

    // Calculate the random position inside the circle
    const x = centerX + randomRadius * Math.cos(angle);
    const y = centerY + randomRadius * Math.sin(angle);

    return {
        x,
        y
    };
}

for (let i = 0; i < resourceAmount; i++) {
    resources.push(getRandomPositionInsideCircle(0, 0, 500))
}
gameLoop();