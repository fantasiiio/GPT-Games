let env = new Environment();

let asteroidFound = null;
let targetFound = null;
let zoomLevel = 0.25;
let pan = {
    x: 0,
    y: 0
};
let panning = false;
let drawingMode = false;
let drawing = false;

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



removeresourcesSpotBtn.addEventListener('click', (event) => {
    if (resourcesSpotFound) {
        let index = env.resourcesSpots.indexOf(resourcesSpotFound);
        env.resourcesSpots.splice(index, 1);
        resourcesSpotFound = null;
    }
});


document.getElementById('spaceStationDockMaxSpeed').addEventListener('change', (event) => {
    spaceStationFound.maxDockingSpeed = Number(document.getElementById('spaceStationDockMaxSpeed').value);
})

document.getElementById('showfirstN').addEventListener('change', (event) => {
    showfirstN = Number(document.getElementById('showfirstN').value);
})

document.getElementById('enableManualControlChk').addEventListener('change', (event) => {
    enableManualControl = document.getElementById('enableManualControlChk').checked;
    if (enableManualControl) {
        landers[0].resetLander()
    }
});


deathTimeoutInput.addEventListener('change', (event) => {
    env.deathTimer = Number(deathTimeoutInput.value) * 1000;
});

deathTimeoutInput.value = env.deathTimer / 1000;

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

resourcesSpotResourceRadius.addEventListener('change', (event) => {
    resourcesSpotFound.resourceRadius = Number(resourcesSpotResourceRadius.value);
});


resourcesSpotRadius.addEventListener('change', (event) => {
    resourcesSpotFound.radius = Number(resourcesSpotRadius.value);
    updateenv.resourcesSpots(resourcesSpotFound)
});

resourcesSpotNumResources.addEventListener('change', (event) => {
    resourcesSpotFound.numResources = Number(resourcesSpotNumResources.value);
    updateenv.resourcesSpots(resourcesSpotFound)
});

resourcesSpotModeSelect.addEventListener('change', (event) => {
    resourcesSpotFound.targetMode = resourcesSpotModeSelect.value;
});
resourcesSpotAction.addEventListener('change', (event) => {
    resourcesSpotFound.action = resourcesSpotAction.value;
});

spaceStationWidthInput.addEventListener('change', (event) => {
    if (spaceStationFound) {
        let index = env.spaceStations.indexOf(spaceStationFound)
        let spaceStation = env.spaceStations[index];
        let newWidth = Number(spaceStationWidthInput.value);
        env.spaceStations[index] = new SpaceStation(spaceStation.x, spaceStation.y, newWidth, spaceStation.height, spaceStation.dockingWidth, spaceStation.dockingHeight, spaceStation.angle);
        spaceStationFound = env.spaceStations[index];
    }

});

spaceStationHeightInput.addEventListener('change', (event) => {

});

addResourcesSpotBtn.addEventListener('click', () => {
    let spot = addResourcesSpot(env.canvas.width / 2, env.canvas.height / 2, 500, 50);
    showresourcesSpotProperties(spot);
});


addSpaceStationBtn.addEventListener('click', () => {
    spaceStation = new SpaceStation(env.canvas.width / zoomLevel / 2, env.canvas.height / zoomLevel / 2 + 1000, 200, 200, 100, 10, 0);
    showSpaceStationProperties(spaceStation);
    env.spaceStations.push(spaceStation);
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
    angleDisplay.textContent = (angle * (180 / Math.PI)).toFixed(1);
    angleDisplay.value = (angle * (180 / Math.PI)).toFixed(1);
}

//updateAngleDisplay();



//updateKnobPosition();


function saveScene() {
    let scene = {
        targets: env.targets,
        asteroids: env.asteroids,
        walls: walls,
        resourcesSpots: env.resourcesSpots,
        spaceStations: env.spaceStations,
        useSpaceStation: useSpaceStation,
        deathTimer: env.deathTimer,
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


function loadScene(sceneName) {
    sceneSelect.value = sceneName;
    let scene = JSON.parse(localStorage.getItem('scene_' + sceneName));
    env.targets = scene.targets;
    env.asteroids = scene.asteroids;
    walls = scene.walls;
    env.resourcesSpots = scene.resourcesSpots || [];
    for (let spaceStation of scene.env.spaceStations) {
        env.spaceStations.push(new SpaceStation(spaceStation.x, spaceStation.y, spaceStation.width, spaceStation.height, spaceStation.dockingWidth, spaceStation.dockingHeight, spaceStation.angle));
        copyNonObjectProperties(env.spaceStations[env.spaceStations.length - 1], spaceStation)
    }
    env.deathTimer = scene.deathTimer || 30000;
    deathTimeoutInput.value = env.deathTimer / 1000;
    useSpaceStation = scene.useSpaceStation
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
            x: env.canvas.width / zoomLevel / 2,
            y: env.canvas.height / zoomLevel / 2,
            angle: 0
        },
        50,
    );
    env.asteroids.push(asteroid);
    asteroidFound = asteroid;
    showAsteroidProperties(asteroid);
});

removeTargetBtn.addEventListener('click', () => {
    if (currentTarget && env.targets.length > 1) {
        let index = env.targets.indexOf(currentTarget);
        env.targets.splice(index, 1);
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
            x: env.canvas.width / zoomLevel / 2,
            y: env.canvas.height / zoomLevel / 2
        },
        velocity: new Vector(0, 0),
    };
    env.targets.push(target);
    showTargetProperties(target);
});

drawBtn.addEventListener('click', () => {
    drawingMode = true;
});

saveGenerationBtn.addEventListener('click', () => {
    //geneticAlgorithm.savePopulation(landers[0].currentActionName)

    alert("saved")
    PPOLander.saveGenetics()
});

skipGenerationBtn.addEventListener('click', () => {
    //killAll();
    PPOLander.die()
});

stopShipBtn.addEventListener('click', () => {
    landers[0].rigidBody.velocity = new Vector(0, 0);
    landers[0].rigidBody.angularVelocity = 0;
});


const keys = {};
const keysPressed = {};

document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
    keysPressed[e.code] = true;
});

document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});


env.canvas.addEventListener('mousemove', (event) => {
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.clientX) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.clientY) / zoomLevel - pan.y - 30;
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

// Add an event listener for the wheel event
env.canvas.addEventListener('wheel', (event) => {
    event.preventDefault(); // Prevent the default scrolling behavior
    env.zoom(event);
});

function panEvent(event) {
    event.preventDefault()

    pan.x += event.movementX / zoomLevel;
    pan.y += event.movementY / zoomLevel;
}

env.canvas.addEventListener('mousedown', (event) => {
    let rect = env.canvas.getBoundingClientRect();
    let mousePosition = new Vector(0, 0);
    mousePosition.x = (event.clientX - rect.left) / zoomLevel - pan.x - 30;
    mousePosition.y = (event.clientY - rect.top) / zoomLevel - pan.y - 30;
    if (event.button == 1) {
        panning = true;
    } else if (event.buttons == 1) {
        // resourcesSpot
        resourcesSpotFound = null;
        for (let i = 0; i < env.resourcesSpots.length; i++) {
            let distance = Math.sqrt(Math.pow(env.resourcesSpots[i].position.x - mousePosition.x, 2) + Math.pow(env.resourcesSpots[i].position.y - mousePosition.y, 2));
            if (distance < env.resourcesSpots[i].radius) {
                resourcesSpotFound = env.resourcesSpots[i];
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
        for (let i = 0; i < env.spaceStations.length; i++) {
            let distance = Math.sqrt(Math.pow(env.spaceStations[i].x - mousePosition.x, 2) + Math.pow(env.spaceStations[i].y - mousePosition.y, 2));
            if (distance < env.spaceStations[i].width) {
                spaceStationFound = env.spaceStations[i];
                break;
            }
        }

        if (spaceStationFound) {
            showSpaceStationProperties(spaceStationFound);
        } else {
            // Hide space station properties if not found (similar to the asteroidPropertiesTable)
            document.getElementById('spaceStationPropertiesTable').style.display = 'none';
        }

        // Target
        targetFound = null;
        for (let i = 0; i < env.targets.length; i++) {
            let distance = Math.sqrt(Math.pow(env.targets[i].position.x - mousePosition.x, 2) + Math.pow(env.targets[i].position.y - mousePosition.y, 2));
            if (distance < env.targetRadius) {
                targetFound = env.targets[i];
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
        for (let i = 0; i < env.asteroids.length; i++) {
            if (env.asteroids[i].polygon.isPointInside(mousePosition)) {
                asteroidFound = env.asteroids[i];
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
    targetActivateRadiusInput.value = target.activateRadius || 1000;
    targetModeSelect.value = target.targetMode;
    targetActionSelect.value = target.action;
    targetPropertiesDiv.style.display = 'block';
    document.getElementById('startAngleRow').style.display = target == env.targets[0] ? 'table-row' : 'none';
    document.getElementById('targetName').innerHTML = target == env.targets[0] ? 'Start' : 'Target ' + (env.targets.indexOf(target));
}

env.canvas.addEventListener('mouseup', (event) => {
    lastCursorX = null;
    lastCursorY = null;
    panning = false;
    drawing = false;
});

function main() {
    env.generateTargets();
    env.loadppoLander();
    env.loadSceneNames();
    env.ppoLander.ppoAgent.trainPPO(env);
}