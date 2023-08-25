const canvas = document.getElementById('gameCanvas');


const ctx = canvas.getContext('2d');

let isSimulationRunning = false;
let enableManualControl = false;
let enableAutoTunePID = true;
let IncreaseP = false;
let GetZieglerNichols = false;
let landers = [];
let targets = [];
let asteroids = [];
let walls = [];
let spaceStations = [];
let asteroidsCount = 0;
let showfirstN = 0; //0 = all

let targetCount = 1;
let cycleTargets = true;
let targetRadius = 200;

let scenes = [];
const populationCount = enableManualControl ? 1 : 100;
let numRadarRays = 5;
let startingTimeBonus = 2000;
let frameCount = 0;
let geneticAlgorithm = null;
let deathTimer = 60000; //Number.MAX_VALUE;
const gravity = 0.0;
const maxThrustPower = 0.1;
const maxSideThrustPower = 0.1;
const landingSpeed = 1;
const maxAngularVelocity = 0.1;
const maxRotationAccel = 0.002;
const FuelConsumption_thrust = 0.25;
const FuelConsumption_rotate = 0.25;
const FuelConsumption_sideThrust = 0.25 * 0.5;
const maxDistance = 2000;

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
const resourceAmount = 500;
const resourceRefuelAmount = 25;
const audioContext = new(window.AudioContext || window.webkitAudioContext)();
const thrustSound = new Audio('thrust.mp3');
//thrustSound.play();
const refuelSound = new Audio('boost-100537.mp3');

// Create gas tanks array
let drawingMode = false;
let drawing = false;

let targetFound = null;
let asteroidFound = null;
let panning = false;
let spaceStationFound = null;


const saveGenerationBtn = document.getElementById('saveGenerationBtn');
const skipGenerationBtn = document.getElementById('skipGenerationBtn');
const stopShipBtn = document.getElementById('stopShipBtn');
const addTargetBtn = document.getElementById('addTargetBtn');
const drawBtn = document.getElementById('drawBtn');
const targetPropertiesDiv = document.getElementById('targetProperties');
const targetActivateRadiusInput = document.getElementById('targetActivateRadius');
const targetModeSelect = document.getElementById('targetMode');
const targetActionSelect = document.getElementById('targetAction');
const removeTargetBtn = document.getElementById('removeTargetBtn');
let asteroidRadiusInput = document.getElementById('asteroidRadiusInput');
let asteroidNumSubdivisionsInput = document.getElementById('asteroidNumSubdivisionsInput');
const addAsteroidBtn = document.getElementById('addAsteroidBtn');
const regenerateAsteroidBtn = document.getElementById('regenerateAsteroidBtn');
const saveSceneBtn = document.getElementById('saveSceneBtn');
const sceneSelect = document.getElementById('sceneSelect');
const addSceneBtn = document.getElementById('addSceneBtn');
const sceneNameInput = document.getElementById('sceneName');
let slider = document.getElementById('circle-slider');
let handle = document.getElementById('handle');

let spaceStationActivateRadius = document.getElementById('spaceStationActivateRadius');
let spaceStationEnterMode = document.getElementById('spaceStationEnterMode');
let spaceStationEnterAction = document.getElementById('spaceStationEnterAction');
let spaceStationExitMode = document.getElementById('spaceStationExitMode');
let spaceStationExitAction = document.getElementById('spaceStationExitAction');

const addSpaceStationBtn = document.getElementById('addSpaceStationBtn');
const spaceStationWidthInput = document.getElementById('spaceStationWidthInput');
const spaceStationHeightInput = document.getElementById('spaceStationHeightInput');

let addResourcesSpotBtn = document.getElementById('addResourcesSpotBtn');
let removeresourcesSpotBtn = document.getElementById('removeresourcesSpotBtn');
let resourcesSpotRadius = document.getElementById('resourcesSpotRadius');
let resourcesSpotNumResources = document.getElementById('resourcesSpotNumResources');
let resourcesSpotModeSelect = document.getElementById('resourcesSpotModeSelect');
let resourcesSpotAction = document.getElementById('resourcesSpotAction');
let resourcesSpotResourceRadius = document.getElementById('resourcesSpotResourceRadius');

let deathTimeoutInput = document.getElementById('deathTimeoutInput');


document.getElementById('IncreasePBtn').addEventListener('click', (event) => {
    IncreaseP = true;
})

document.getElementById('GetZieglerNicholsBtn').addEventListener('click', (event) => {
    GetZieglerNichols = true;
})



document.getElementById('makeDefaultSceneBtn').addEventListener('click', (event) => {
    localStorage.setItem('sceneDefault', sceneSelect.value);
})

document.getElementById('addEnemyBtn').addEventListener('click', (event) => {
    addEnemyToLanders();
})

document.getElementById('resetSceneBtn').addEventListener('click', (event) => {
    resetScene();
})


document.getElementById('playButton').addEventListener('click', (event) => {
    isSimulationRunning = true;
})

document.getElementById('stopButton').addEventListener('click', (event) => {
    isSimulationRunning = false;
})

removeresourcesSpotBtn.addEventListener('click', (event) => {
    if (resourcesSpotFound) {
        let index = resourcesSpots.indexOf(resourcesSpotFound);
        resourcesSpots.splice(index, 1);
        resourcesSpotFound = null;
    }
});


document.getElementById('spaceStationDockMaxSpeed').addEventListener('change', (event) => {
    spaceStationFound.maxDockingSpeed = Number(document.getElementById('spaceStationDockMaxSpeed').value);
})

document.getElementById('showfirstN').addEventListener('change', (event) => {
    showfirstN = Number(document.getElementById('showfirstN').value);
})

document.getElementById('enableAutoTunePIDChk').addEventListener('change', (event) => {
    enableAutoTunePID = document.getElementById('enableAutoTunePIDChk').checked;
});

document.getElementById('enableManualControlChk').addEventListener('change', (event) => {
    enableManualControl = document.getElementById('enableManualControlChk').checked;
    if (enableManualControl) {
        landers[0].resetLander()
    }
});


deathTimeoutInput.addEventListener('change', (event) => {
    deathTimer = Number(deathTimeoutInput.value) * 1000;
});

deathTimeoutInput.value = deathTimer / 1000;

spaceStationActivateRadius.addEventListener('change', (event) => {
    spaceStationFound.activateRadius = parseFloat(spaceStationActivateRadius.value);
});

spaceStationEnterMode.addEventListener('change', (event) => {
    spaceStationFound.mode = spaceStationEnterMode.value;
});

spaceStationEnterAction.addEventListener('change', (event) => {
    spaceStationFound.action = spaceStationEnterAction.value;
});

spaceStationExitMode.addEventListener('change', (event) => {
    spaceStationFound.exitMode = spaceStationExitMode.value;
});

spaceStationExitAction.addEventListener('change', (event) => {
    spaceStationFound.exitAction = spaceStationExitAction.value;
});

removeresourcesSpotBtn.addEventListener('click', (event) => {
    if (resourcesSpotFound) {
        let index = resourcesSpots.indexOf(resourcesSpotFound);
        resourcesSpots.splice(index, 1);
        resourcesSpotFound = null;
    }
});

resourcesSpotResourceRadius.addEventListener('change', (event) => {
    resourcesSpotFound.resourceRadius = Number(resourcesSpotResourceRadius.value);
});


resourcesSpotRadius.addEventListener('change', (event) => {
    resourcesSpotFound.radius = Number(resourcesSpotRadius.value);
    updateResourcesSpots(resourcesSpotFound)
});

resourcesSpotNumResources.addEventListener('change', (event) => {
    resourcesSpotFound.numResources = Number(resourcesSpotNumResources.value);
    updateResourcesSpots(resourcesSpotFound)
});

resourcesSpotModeSelect.addEventListener('change', (event) => {
    resourcesSpotFound.targetMode = resourcesSpotModeSelect.value;
});
resourcesSpotAction.addEventListener('change', (event) => {
    resourcesSpotFound.action = resourcesSpotAction.value;
});

spaceStationWidthInput.addEventListener('change', (event) => {
    if (spaceStationFound) {
        let index = spaceStations.indexOf(spaceStationFound)
        let spaceStation = spaceStations[index];
        let newWidth = Number(spaceStationWidthInput.value);
        spaceStations[index] = new SpaceStation(spaceStation.x, spaceStation.y, newWidth, spaceStation.height, spaceStation.dockingWidth, spaceStation.dockingHeight, spaceStation.angle);
        spaceStationFound = spaceStations[index];
    }

});

spaceStationHeightInput.addEventListener('change', (event) => {

});

addResourcesSpotBtn.addEventListener('click', () => {
    let spot = addResourcesSpot(canvas.width / 2, canvas.height / 2, 500, 50);
    showresourcesSpotProperties(spot);
});


addSpaceStationBtn.addEventListener('click', () => {
    spaceStation = new SpaceStation(canvas.width / zoomLevel / 2, canvas.height / zoomLevel / 2 + 1000, 200, 200, 100, 10, 0);
    showSpaceStationProperties(spaceStation);
    spaceStations.push(spaceStation);
});

let mouseDown = false;
let circleCenter;
let lastAngle;
let radius = 40;
let center = {
    x: radius + 10,
    y: radius + 10
};
let angleSliderSize = 2 * radius + 20;
const snapInterval = Math.PI / 4; // Change this to adjust snap interval

const spaceStationSvg = document.querySelector("#spaceStationSvg");
spaceStationSvg.setAttribute('width', angleSliderSize);
spaceStationSvg.setAttribute('height', angleSliderSize);
const spaceStationMainCircle = document.querySelector("#spaceStationMainCircle");
spaceStationMainCircle.setAttribute('cx', angleSliderSize / 2);
spaceStationMainCircle.setAttribute('cy', angleSliderSize / 2);
spaceStationMainCircle.setAttribute("r", radius);

const asteroidSvg = document.querySelector("#asteroidSvg");
asteroidSvg.setAttribute('width', angleSliderSize);
asteroidSvg.setAttribute('height', angleSliderSize);
const asteroidMainCircle = document.querySelector("#asteroidMainCircle");
asteroidMainCircle.setAttribute('cx', angleSliderSize / 2);
asteroidMainCircle.setAttribute('cy', angleSliderSize / 2);
asteroidMainCircle.setAttribute("r", radius);

const startSvg = document.querySelector("#startSvg");
startSvg.setAttribute('width', angleSliderSize);
startSvg.setAttribute('height', angleSliderSize);
const startMainCircle = document.querySelector("#startMainCircle");
startMainCircle.setAttribute('cx', angleSliderSize / 2);
startMainCircle.setAttribute('cy', angleSliderSize / 2);
startMainCircle.setAttribute("r", radius);

const spaceStationDockSvg = document.querySelector("#spaceStationDockSvg");
spaceStationDockSvg.setAttribute('width', angleSliderSize);
spaceStationDockSvg.setAttribute('height', angleSliderSize);
const spaceStationDockMainCircle = document.querySelector("#spaceStationDockMainCircle");
spaceStationDockMainCircle.setAttribute('cx', angleSliderSize / 2);
spaceStationDockMainCircle.setAttribute('cy', angleSliderSize / 2);
spaceStationDockMainCircle.setAttribute("r", radius);
document.getElementById('spaceStationDockAngleDisplay').addEventListener('change', (event) => {
    spaceStationFound.maxDockingAngle = Number(event.target.value) * Math.PI / 180;
    updateKnobPosition(spaceStationFound.maxDockingAngle, "spaceStationDock");
    updateAngleDisplay(spaceStationFound.maxDockingAngle, "spaceStationDock");
})
let isMouseDown = false;

spaceStationDockKnob.addEventListener("mousedown", function (e) {
    isMouseDown = true;
});

spaceStationDockSvg.addEventListener("mouseup", function (e) {
    isMouseDown = false;
});

spaceStationDockSvg.addEventListener("mousemove", function (e) {
    if (!isMouseDown) return;
    let angle = onAngleSliderMouseMove(e, "spaceStationDock");

    let spaceStation = spaceStationFound;
    spaceStation.maxDockingAngle = angle
    updateAngleDisplay(spaceStationFound.maxDockingAngle, "spaceStationDock");
});

spaceStationKnob.addEventListener("mousedown", function (e) {
    isMouseDown = true;
});

spaceStationSvg.addEventListener("mouseup", function (e) {
    isMouseDown = false;
});

spaceStationSvg.addEventListener("mousemove", function (e) {
    if (!isMouseDown) return;
    let angle = onAngleSliderMouseMove(e, "spaceStation");

    spaceStationFound.angle = angle
    spaceStationFound.updateDockPosition();
});


asteroidKnob.addEventListener("mousedown", function (e) {
    isMouseDown = true;
});

asteroidSvg.addEventListener("mouseup", function (e) {
    isMouseDown = false;
});

asteroidSvg.addEventListener("mousemove", function (e) {
    if (!isMouseDown) return;
    let angle = onAngleSliderMouseMove(e, "asteroid");

    let asteroid = asteroidFound;
    asteroid.rigidBody.angle = angle
});


startKnob.addEventListener("mousedown", function (e) {
    isMouseDown = true;
});

startSvg.addEventListener("mouseup", function (e) {
    isMouseDown = false;
});

startSvg.addEventListener("mousemove", function (e) {
    if (!isMouseDown) return;
    let angle = onAngleSliderMouseMove(e, "start");

    let start = targetFound;
    start.startAngle = angle
});

function onAngleSliderMouseMove(e, controlName) {
    let svg = document.querySelector("#" + controlName + "Svg");
    let rect = svg.getBoundingClientRect();
    let x = e.clientX - rect.left - center.x;
    let y = e.clientY - rect.top - center.y;

    let angle = Math.atan2(y, x);
    angle = angle + Math.PI / 2;

    let chk = document.querySelector("#" + controlName + "SnapCheckbox");
    if (chk.checked)
        angle = Math.round(angle / snapInterval) * snapInterval;

    updateKnobPosition(angle, controlName);
    updateAngleDisplay(angle, controlName);
    return angle;
}

function updateKnobPosition(angle, controlName) {
    angle = angle || 0;
    angle = angle - Math.PI / 2;
    let knob = document.querySelector("#" + controlName + "Knob");
    knob.setAttribute("cx", center.x + Math.cos(angle) * radius);
    knob.setAttribute("cy", center.y + Math.sin(angle) * radius);
}

function updateAngleDisplay(angle, controlName) {
    angle = angle || 0;
    let angleDisplay = document.querySelector("#" + controlName + "AngleDisplay");
    angleDisplay.value = (angle * (180 / Math.PI)).toFixed(1);
}

//updateAngleDisplay();



//updateKnobPosition();


function saveScene() {
    let scene = {
        targets: targets,
        asteroids: asteroids,
        walls: walls,
        resourcesSpots: resourcesSpots,
        spaceStations: spaceStations,
        deathTimer: deathTimer,
        numEnemies: landers[landers.length - 1].enemies.count,
    }
    maxIndex = 0;

    localStorage.setItem('scene_' + sceneSelect.value, JSON.stringify(scene));
}

function copyNonObjectProperties(target, source) {
    for (let key in source) {
        // Check if the property is not an object and exists in the source object
        if (typeof source[key] !== 'object' && source.hasOwnProperty(key)) {
            target[key] = source[key];
        }
    }
}

function resetScene() {
    targets = [];
    generateTargets();
    changeAllTarget();
    asteroids = [];
    walls = [];
    resourcesSpots = [];
    spaceStations = [];
    // create an option
    let option = document.createElement('option');
    option.value = "New Scene";
    option.text = "New Scene";
    option.selected = true;
    sceneSelect.appendChild(option);

    restart();
}

function loadScene(sceneName) {
    sceneSelect.value = sceneName;
    let scene = JSON.parse(localStorage.getItem('scene_' + sceneName));
    targets = scene.targets;
    asteroids = scene.asteroids;
    walls = scene.walls;
    resourcesSpots = scene.resourcesSpots || [];
    for (let spaceStation of scene.spaceStations) {
        spaceStations.push(new SpaceStation(spaceStation.x, spaceStation.y, spaceStation.width, spaceStation.height, spaceStation.dockingWidth, spaceStation.dockingHeight, spaceStation.angle));
        copyNonObjectProperties(spaceStations[spaceStations.length - 1], spaceStation)
    }
    numEnemies = scene.numEnemies || 0;
    for(let lander of landers){
        lander.resetLander();
    }
    for (let i = 0; i < numEnemies; i++) {
        addEnemyToLanders();
    }
    addEnemyToLanders();
    deathTimer = scene.deathTimer || 30000;
    deathTimeoutInput.value = deathTimer / 1000;
    restart();
}

sceneSelect.addEventListener('change', (event) => {
    loadScene(sceneSelect.value)
});

asteroidRadiusInput.addEventListener('change', (event) => {
    if (asteroidFound) {
        asteroidFound.radius = parseFloat(event.target.value);
        asteroidFound.generateRandomAsteroidPolygon();
    }
});

asteroidNumSubdivisionsInput.addEventListener('change', (event) => {
    if (asteroidFound) {
        asteroidFound.numSubdivisions = parseInt(event.target.value);
        asteroidFound.generateRandomAsteroidPolygon();
    }
});



let currentTarget = null;

addSceneBtn.addEventListener('click', () => {
    let sceneName = sceneNameInput.value;
    scenes.push({
        name: sceneName
    });

    let option = document.createElement('option');
    option.value = sceneName;
    option.text = sceneName;
    option.selected = true;
    sceneSelect.appendChild(option);
});

saveSceneBtn.addEventListener('click', () => {
    saveScene()
});

regenerateAsteroidBtn.addEventListener('click', () => {
    if (asteroidFound) {
        asteroidFound.generateRandomAsteroidPolygon();
    }
});

addAsteroidBtn.addEventListener('click', () => {
    let asteroid = new Asteroid({
            x: canvas.width / zoomLevel / 2,
            y: canvas.height / zoomLevel / 2,
            angle: 0
        },
        50,
    );
    asteroids.push(asteroid);
    asteroidFound = asteroid;
    showAsteroidProperties(asteroid);
});

removeTargetBtn.addEventListener('click', () => {
    if (currentTarget && targets.length > 1) {
        let index = targets.indexOf(currentTarget);
        targets.splice(index, 1);
        currentTarget = null;
    }
});

// Set up onChange listeners to update currentTarget dynamically
targetActivateRadiusInput.addEventListener('input', () => {
    if (currentTarget) {
        currentTarget.activateRadius = parseFloat(targetActivateRadiusInput.value);
    }
});

targetModeSelect.addEventListener('change', () => {
    if (currentTarget) {
        currentTarget.targetMode = targetModeSelect.value;
    }
});

targetActionSelect.addEventListener('change', () => {
    if (currentTarget) {
        currentTarget.action = targetActionSelect.value;
    }
});

addTargetBtn.addEventListener('click', () => {
    let target = {
        position: {
            x: canvas.width / zoomLevel / 2,
            y: canvas.height / zoomLevel / 2
        },
        velocity: new Vector(0, 0),
    };
    targets.push(target);
    showTargetProperties(target);
});

drawBtn.addEventListener('click', () => {
    drawingMode = true;
});

saveGenerationBtn.addEventListener('click', () => {
    geneticAlgorithm.savePopulation(landers[0].currentActionName)
    alert("saved")
});

skipGenerationBtn.addEventListener('click', () => {
    killAll();
});

stopShipBtn.addEventListener('click', () => {
    landers[0].enemies[0].rigidBody.velocity = new Vector(0, 0);
    landers[0].enemies[0].rigidBody.angularVelocity = 0;
    landers[0].enemies[0].rigidBody.position.x = landers[0].rigidBody.position.x;
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
let resourcesSpots = [];


function drawResources(resourceCounts) {
    ctx.save();
    let resourcesSpotIndex = 0;
    for (let resourcesSpot of resourcesSpots) {
        for (const [index, resource] of resourcesSpot.resources.entries()) {
            ctx.beginPath();

            ctx.arc(resource.position.x + resourcesSpot.position.x, resource.position.y + resourcesSpot.position.y, resourcesSpot.resourceRadius || 10, 0, 2 * Math.PI);
            ctx.fillStyle = "#03C03C";
            ctx.fill();
            ctx.stroke();

            // If this resource has been harvested, display the count
            if (resourceCounts[resourcesSpotIndex] && resourceCounts[resourcesSpotIndex][index]) {
                ctx.font = "10px Arial";
                ctx.fillStyle = "black";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(resourceCounts[resourcesSpotIndex][index].toString(), resource.position.x + resourcesSpot.position.x, resource.position.y + resourcesSpot.position.y);
            }
        }
        resourcesSpotIndex++;
    }
    ctx.restore();
}

function clearCanvas(canvas, context, color) {
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);
}
//let terrain = new Terrain(canvas.width / zoomLevel, canvas.height / zoomLevel, mountainResolution, mountainHeightFactor, maxYOffset);
//terrain.generateTerrain();


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

function addEnemyToLanders() {
    for (let lander of landers) {
        lander.addEnemy(new Enemy(lander.rigidBody.position.x, lander.rigidBody.position.y - 1000, Math.PI));
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
    let center = {
        position: {
            x: (200 + Math.random() * (canvas.width / zoomLevel - 200)),
            y: (200 + Math.random() * (canvas.height / zoomLevel / 3 * 2 - 200))
        }
    }
    positions.push({
        position: new Vector(center.position.x, center.position.y)
    });

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
                newPositions = {
                    position: {
                        x: center.position.x,
                        y: center.position.y
                    }
                };
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
    targets = (positions || []).map((position) => {
        position.velocity = new Vector(0, 0)
        position.startAngle = 0;
        return position
    });
}


function restart(newPopulation) {
    if (newPopulation) {
        for (let i = 0; i < newPopulation.length; i++) {
            landers[i].neuralNetwork = newPopulation[i];
            landers[i].resetLander();
        }
    } else {
        for (let i = 0; i < landers.length; i++) {
            landers[i].resetLander();
        }
    }
}

function changeAllTarget(position) {
    for (let lander of landers) {
        if (targets.length > 0)
            lander.target = targets[0];
        else if (spaceStations.length > 0)
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

//generateTargets();
//generateAsteroids();

canvas.addEventListener('mousemove', (event) => {
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.offsetX) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.offsetY) / zoomLevel - pan.y - 30;
    if (event.buttons == 1) {
        if (targetFound) {
            targetFound.position.x = mousePosition.x;
            targetFound.position.y = mousePosition.y;
        } else if (asteroidFound) {
            asteroidFound.rigidBody.position.x = mousePosition.x;
            asteroidFound.rigidBody.position.y = mousePosition.y;
        } else if (drawing) {
            walls[walls.length - 1].push(mousePosition)
        } else if (spaceStationFound) {
            spaceStationFound.x = mousePosition.x - spaceStationFound.width / 2;
            spaceStationFound.y = mousePosition.y - spaceStationFound.height / 2;
            spaceStationFound.updateDockPosition();
        } else if (resourcesSpotFound) {
            resourcesSpotFound.position.x = mousePosition.x;
            resourcesSpotFound.position.y = mousePosition.y;
        }
    } else if (event.buttons == 4) {
        if (panning) {
            panEvent(event);
        }
    }
});


canvas.addEventListener('mousedown', (event) => {
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.offsetX) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.offsetY) / zoomLevel - pan.y - 30;
    if (event.button == 1) {
        panning = true;
    } else if (event.buttons == 1) {
        // resourcesSpot
        resourcesSpotFound = null;
        for (let i = 0; i < resourcesSpots.length; i++) {
            let distance = Math.sqrt(Math.pow(resourcesSpots[i].position.x - mousePosition.x, 2) + Math.pow(resourcesSpots[i].position.y - mousePosition.y, 2));
            if (distance < resourcesSpots[i].radius) {
                resourcesSpotFound = resourcesSpots[i];
                break;
            }
        }

        if (resourcesSpotFound) {
            currentresourcesSpot = resourcesSpotFound;
            showresourcesSpotProperties(resourcesSpotFound);
        } else {
            resourcesSpotProperties.style.display = 'none';
        }

        // Space station
        spaceStationFound = null;
        for (let i = 0; i < spaceStations.length; i++) {
            let distance = Math.sqrt(Math.pow(spaceStations[i].x - mousePosition.x, 2) + Math.pow(spaceStations[i].y - mousePosition.y, 2));
            if (distance < spaceStations[i].width) {
                spaceStationFound = spaceStations[i];
                break;
            }
        }

        if (spaceStationFound) {
            showSpaceStationProperties(spaceStationFound);
            updateKnobPosition(spaceStationFound.angle, 'spaceStation');
            updateAngleDisplay(spaceStationFound.angle, 'spaceStation');
        } else {
            // Hide space station properties if not found (similar to the asteroidPropertiesTable)
            document.getElementById('spaceStationPropertiesTable').style.display = 'none';
        }

        // Target
        targetFound = null;
        for (let i = 0; i < targets.length; i++) {
            let distance = Math.sqrt(Math.pow(targets[i].position.x - mousePosition.x, 2) + Math.pow(targets[i].position.y - mousePosition.y, 2));
            if (distance < targetRadius) {
                targetFound = targets[i];
                break;
            }
        }

        if (targetFound) {
            currentTarget = targetFound;
            showTargetProperties(targetFound);
            updateKnobPosition(targetFound.startAngle || 0, 'start');
            updateAngleDisplay(targetFound.startAngle || 0, 'start');
        } else {
            targetPropertiesDiv.style.display = 'none';
        }

        // Asteroid
        asteroidFound = null;
        for (let i = 0; i < asteroids.length; i++) {
            if (asteroids[i].polygon.isPointInside(mousePosition)) {
                asteroidFound = asteroids[i];
                break;
            }
        }

        if (asteroidFound) {
            showAsteroidProperties(asteroidFound);
            updateKnobPosition(asteroidFound.rigidBody.angle, 'asteroid');
            updateAngleDisplay(asteroidFound.rigidBody.angle, 'asteroid');
        } else {
            document.getElementById('asteroidPropertiesTable').style.display = 'none';
        }

        if (drawingMode) {
            walls.push([])
            drawing = true;
        }

    }
    //changeAllTarget(mousePosition);
});

function showresourcesSpotProperties(resourcesSpot) {
    document.getElementById('resourcesSpotProperties').style.display = 'block';
    resourcesSpotRadius.value = resourcesSpot.radius;
    resourcesSpotNumResources.value = resourcesSpot.numResources;
    resourcesSpotResourceRadius.value = resourcesSpot.resourceRadius;

    resourcesSpotModeSelect.value = resourcesSpot.targetMode;
    resourcesSpotAction.value = resourcesSpot.action;
    document.getElementById('resourcesSpotName').innerHTML = 'Resources Spot ' + (resourcesSpots.indexOf(resourcesSpot) + 1);

}

function showSpaceStationProperties(spaceStation) {
    document.getElementById('spaceStationPropertiesTable').style.display = 'block';
    document.getElementById('spaceStationDockMaxSpeed').value = spaceStation.maxDockingSpeed;

    spaceStationWidthInput.value = spaceStation.width;
    spaceStationHeightInput.value = spaceStation.height;
    spaceStationEnterMode.value = spaceStation.mode;
    spaceStationEnterAction.value = spaceStation.action;
    spaceStationExitMode.value = spaceStation.exitMode;
    spaceStationExitAction.value = spaceStation.exitAction;
    spaceStationActivateRadius.value = spaceStation.activateRadius;

    updateKnobPosition(spaceStationFound.angle, 'spaceStation');
    updateAngleDisplay(spaceStationFound.angle, 'spaceStation');
    updateKnobPosition(spaceStationFound.maxDockingAngle, 'spaceStationDock');
    updateAngleDisplay(spaceStationFound.maxDockingAngle, 'spaceStationDock');

}

function showAsteroidProperties(asteroid) {
    document.getElementById('asteroidPropertiesTable').style.display = 'block';
    asteroidRadiusInput.value = asteroid.radius;
    asteroidNumSubdivisionsInput.value = asteroid.numSubdivisions;
}

function showTargetProperties(target) {
    targetActivateRadiusInput.value = target.activateRadius;
    targetModeSelect.value = target.targetMode;
    targetActionSelect.value = target.action;
    targetPropertiesDiv.style.display = 'block';
    document.getElementById('startAngleRow').style.display = target == targets[0] ? 'table-row' : 'none';
    document.getElementById('targetName').innerHTML = target == targets[0] ? 'Start' : 'Target ' + (targets.indexOf(target));
}

canvas.addEventListener('mouseup', (event) => {
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

    const mousePosBefore = new Vector(event.offsetX / zoomLevel - pan.x, event.offsetY / zoomLevel - pan.y);
    zoomLevel *= zoomFactor;
    const mousePosAfter = new Vector(event.offsetX / zoomLevel - pan.x, event.offsetY / zoomLevel - pan.y);

    pan.x = pan.x + mousePosAfter.x - mousePosBefore.x;
    pan.y = pan.y + mousePosAfter.y - mousePosBefore.y;
}

// Add an event listener for the wheel event
canvas.addEventListener('wheel', (event) => {
    event.preventDefault(); // Prevent the default scrolling behavior
    zoom(event);
});

//geneticAlgorithm.loadPopulation()


function drawText(text, x, y, textAlign = 'left') {
    ctx.font = '40px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = textAlign || 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
}

function drawTarget(target, size, index) {
    if (index == 0)
        index = 'Start';

    drawText(index, target.position.x, target.position.y, index == "Start" ? "center" : "left"); // Draw target index

    // Draw circle
    ctx.beginPath();
    ctx.arc(target.position.x, target.position.y, size - 50, 0, 2 * Math.PI);
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

    if (keys['KeyQ']) {
        lander.sideThrust = -maxSideThrustPower;
    }
    if (keys['KeyE']) {
        lander.sideThrust = maxSideThrustPower;
    }

    if (keys['ArrowUp']) {
        lander.thrust = maxThrustPower;
    }
    if (keys['ArrowDown']) {
        lander.thrust = -maxThrustPower;
    }
    if (!keys['ArrowUp'] && !keys['ArrowDown']) {
        lander.thrust = 0;
    }
    if (keys['Space']) {
        lander.fireLaser();
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
    const inputsCount = config.inputs.reduce((sum, input) => sum + (input.checked ? input.inputCount : 0), 0);
    const hiddenLayersCount = config.hiddenLayers.length;
    const outputs = config.outputs;
    const outputsCount = outputs.filter((output) => output.checked).length;

    const nodesPerLayer = [inputsCount];
    for (let i = 0; i < hiddenLayersCount; i++) {
        nodesPerLayer.push(Number(config.hiddenLayers[i]));
    }
    nodesPerLayer.push(outputsCount);

    return nodesPerLayer;
}

function getSceneNames() {
    let list = [];
    for (const [key, value] of Object.entries(localStorage)) {
        if (key.startsWith('scene_')) {
            list.push(key.replace('scene_', ''));
        }
    }
    return list;
}

function loadSceneNames() {
    let scenes = getSceneNames();

    let option = document.createElement('option');
    option.value = "";
    option.text = "";
    sceneSelect.appendChild(option);

    for (let scene of scenes) {
        let option = document.createElement('option');
        option.value = scene;
        option.text = scene;
        sceneSelect.appendChild(option);
    }
}

let nnConfigs = {};
loadSceneNames();

function loadLanders() {
    const config = JSON.parse(localStorage.getItem('nnConfig'));

    if (config && config.networks) {

        config.networks.forEach((network) => {
            nnConfigs[network.name] = network;

            for (let fitnessOnEvent of network.fitnessOnEvents) {
                network.fitnessOnEvents[fitnessOnEvent.name] = fitnessOnEvent.value;
            }
            let fileIndex = GeneticAlgorithm.getMaxFileIndex(network.name);
            let fileName = 'NeuralNetwork_' + network.name + "_" + fileIndex;

            let populationData = JSON.parse(localStorage.getItem(fileName));
            if (populationData) {
                // For each saved individual, load the individual's data into the corresponding Lander
                populationData.forEach((individualData, i) => {
                    let lander = landers[i];
                    if (!lander)
                        lander = new Lander(0,0,0);

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
                        lander = new Lander(0,0,0);

                    lander.addNeuralNetwork(new NeuralNetwork2(nodesPerLayer), network.name);
                    if (!landers[i])
                        landers.push(lander);
                }

            }
            if (network.isDefault)
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
    // If the NeuralNetworks could not be loaded, create new ones
    for (let i = 0; i < populationCount; i++) {
        const lander = new Lander(targets[0].position.x, targets[0].position.y + 1, i, targets[0].startAngle);
        landers.push(lander);
    }
    addNeuralNetworkToLanders('travel');
    SetLandersNeuralNetwork('travel');
    addEnemyToLanders();
}

function createOptions(control) {
    // Create and append the 'Don't change' option
    let defaultOption = document.createElement('option');
    defaultOption.value = "";
    defaultOption.text = "Don't change";
    control.appendChild(defaultOption);

    // Fill action options dynamically
    for (let action in nnConfigs) {
        let option = document.createElement('option');
        option.value = action;
        option.text = action;
        control.appendChild(option);
    }
}

createOptions(targetActionSelect)
createOptions(resourcesSpotAction)
createOptions(spaceStationEnterAction)
createOptions(spaceStationExitAction)


//changeAllTarget();
if (!enableManualControl) {
    geneticAlgorithm = initGeneticAlgorithm(populationCount);
    geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
        restart(newPopulation);
    }
    geneticAlgorithm.run(bestIndividual => {
        console.log("L'algorithme g\xE9n\xE9tique a terminé. Meilleur individu : ", bestIndividual);
    });
}

let sceneDefault = localStorage.getItem('sceneDefault');
if(sceneDefault)
    loadScene(sceneDefault)

function gameLoop() {
    if (!gameLoop.debounced) {
        gameLoop.debounced = true;
        setTimeout(() => {
            // if(!isSimulationRunning){
            //     requestAnimationFrame(gameLoop);            
            //     return;
            // }
            gameLoop.debounced = false;
            clearCanvas(canvas, ctx, '#03002e');
            ctx.save();
            ctx.scale(zoomLevel, zoomLevel);
            ctx.translate(pan.x, pan.y);
            for (let spaceStation of spaceStations)
                spaceStation.draw();

            let harvestedResources = countHarvestedResources()
            drawResources(harvestedResources);
            for (let i = 0; i < asteroids.length; i++) {
                asteroids[i].rigidBody.update();
                asteroids[i].getPolygon();
                asteroids[i].draw();
            }
            let index = 0;
            for (let lander of landers) {
                if (enableManualControl && index > 0)
                    continue;
                let showIt = true;
                if (showfirstN && lander.neuralNetwork.positionNumber > showfirstN)
                    showIt = false;
                // if(!lander.neuralNetwork.isBest)
                //     continue;
                if (!lander.neuralNetwork.isDead) {
                    lander.checkDocking();
                    lander.checkTargetModes();
                    lander.checkTargets();

                    if (isSimulationRunning)
                        lander.updateLander();
                    lander.drawLander();
                    if (index == 0 && enableManualControl)
                        updateLanderManually(lander);
                    else
                    if (isSimulationRunning)
                        lander.applyNeuralNetwork(lander.target); // Update the neural network input                    

                    lander.calculateFitness()
                    lander.handleCollision();
                } else {
                    lander.updateLander();
                    lander.calculateFitness()
                }
                index++;
            }

            //predictionModel.trainBatch(inputArrays, targetArrays);
            for (let i = 0; i < targets.length; i++) {
                drawTarget(targets[i], targetRadius, i);
            }
            drawLines(walls);
            drawScore();
            ctx.restore();
            frameCount++;
            requestAnimationFrame(gameLoop);

        });
    }

    for (let key in keysPressed) {
        delete keysPressed[key];
    }
}

function countHarvestedResources() {
    let harvestedResourceCounts = {};

    for (let i = 0; i < landers.length; i++) {
        const lander = landers[i];

        for (let resourcesSpotIndex in lander.harvestedResources) {
            const resourceArray = lander.harvestedResources[resourcesSpotIndex];

            for (let k = 0; k < resourceArray.length; k++) {
                const resourceIndex = resourceArray[k];
                if (!harvestedResourceCounts[resourcesSpotIndex])
                    harvestedResourceCounts[resourcesSpotIndex] = {};
                if (harvestedResourceCounts[resourcesSpotIndex][resourceIndex] === undefined) {
                    harvestedResourceCounts[resourcesSpotIndex][resourceIndex] = 1;
                } else {
                    harvestedResourceCounts[resourcesSpotIndex][resourceIndex]++;
                }
            }
        }
    }

    return harvestedResourceCounts;
}


function getRandomPositionInsideCircle(radius) {
    // Generate a random angle
    const angle = Math.random() * 2 * Math.PI;

    // Calculate a random radius within the circle using the square root of a random value between 0 and 1
    const randomRadius = radius * Math.sqrt(Math.random());

    // Calculate the random position inside the circle
    const x = randomRadius * Math.cos(angle);
    const y = randomRadius * Math.sin(angle);

    return {
        position: new Vector(x, y)
    };
}

function updateResourcesSpots(resourceSpot) {
    resourceSpot.resources = [];
    for (let i = 0; i < resourceSpot.numResources; i++) {
        resourceSpot.resources.push(getRandomPositionInsideCircle(resourceSpot.radius))
    }
}

function addResourcesSpot(x, y, radius, numResources) {
    let spot = {
        position: new Vector(x, y),
        radius: radius,
        resources: [],
        numResources,
        resourceRadius: 10
    }
    resourcesSpots.push(spot);
    for (let i = 0; i < numResources; i++) {
        spot.resources.push(getRandomPositionInsideCircle(radius))
    }
    return spot;
}

gameLoop();