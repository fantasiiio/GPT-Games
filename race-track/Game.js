const canvas = document.getElementById('track-editor');
const ctx = canvas.getContext('2d');
const track = new Track(canvas);

let isPanning = false;
let drawing = false;
let erasing = false;


let startPoint = {
    x: 0,
    y: 0,
    dir: ""
};

// Add an event listener for the wheel event
canvas.addEventListener('wheel', (event) => {
    event.preventDefault(); // Prevent the default scrolling behavior
    track.zoom(event);
});

function drawText(ctx, text, x, y) {
    ctx.font = '40px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
}



function restartGame() {
    const initialX = canvas.width - 80;
    const initialY = (canvas.height - 40) / 2;
    const initialAngle = 180;

    redCar.reset(initialX, initialY, initialAngle);
}
let redCars = [];


function updateTrack(event) {
    if (!mouseDown)
        return;

    const pos = track.getMouseSquarePos(event);

    if (currentTool === 'draw') {
        track.setTrack(pos.x, pos.y);
    } else if (currentTool === 'erase') {
        track.clearSquare(pos.x, pos.y);
    }

    track.path = track.getTrackPath();
}

let mouseDown = false;
canvas.addEventListener('mousedown', (event) => {
    if (event.button == 1) {
        isPanning = true;
        event.preventDefault();
    }

    if (currentTool == "run"){
        track.getMousePos(event);
        return;
    }

    if (event.button != 0) {
        return;
    }
    const pos = track.getMouseSquarePos(event);

    if (drawTrackBtn.checked) {
        drawing = true;

        if (track.grid[pos.x][pos.y]) {
            startPoint.x = pos.x;
            startPoint.y = pos.y;
            startPoint.dir = track.getTrackDirection(startPoint);
            for (let redCar of redCars) {
                track.placeCarAtStartPos(redCar);
            }
        }
        track.setTrack(pos.x, pos.y);
    } else if (eraseTrackBtn.checked) {
        drawing = true;
        track.clearSquare(pos.x, pos.y);
    }
    mouseDown = true;
});

canvas.addEventListener('mouseup', (event) => {
    isPanning = false;
    if (currentTool == "run")
        return;
    mouseDown = false;
});
canvas.addEventListener('mousemove', (event) => {
    if (isPanning) {
        track.panEvent(event);
    }

    if (currentTool == "run")
        return;
    updateTrack(event);
});

//track.drawGrid();


// Toolbar buttons
const saveTrackBtn = document.getElementById('saveTrackBtn');
const loadTrackBtn = document.getElementById('loadTrackBtn');
const validateTrackBtn = document.getElementById('validateTrackBtn');
const clearTrackBtn = document.getElementById('clearTrackBtn');
const runBtn = document.getElementById('runBtn');
const drawTrackBtn = document.getElementById('drawTrackBtn');
const eraseTrackBtn = document.getElementById('eraseTrackBtn');
const buttonContents = document.getElementsByClassName('button-content');
const divCanvas = document.getElementById('divCanvas');
const runLbl = document.getElementById('runLbl');
const saveBestNeuralNetworkBtn = document.getElementById('saveBestNeuralNetworkBtn');
const loadBestNeuralNetworkBtn = document.getElementById('loadBestNeuralNetworkBtn');


canvas.width = divCanvas.clientWidth;
canvas.height = divCanvas.clientHeight;

//divCanvas.clientWidth
let currentTool = 'run';

saveBestNeuralNetworkBtn.addEventListener('click', () => {
    geneticAlgorithm.savePopulation()
    alert("saved")
});

loadBestNeuralNetworkBtn.addEventListener('click', () => {
    geneticAlgorithm.loadPopulation()
});

clearTrackBtn.addEventListener('click', () => {
    track.clearTrack();
});

drawTrackBtn.addEventListener('change', () => {
    if (drawTrackBtn.checked) {
        currentTool = 'draw';
    }
});

eraseTrackBtn.addEventListener('change', () => {
    if (eraseTrackBtn.checked) {
        currentTool = 'erase';
    }
});

saveTrackBtn.addEventListener('click', () => {
    track.saveTrack();
    geneticAlgorithm.savePopulation()
});

loadTrackBtn.addEventListener('click', () => {
    track.loadTrack();
    geneticAlgorithm.loadPopulation()
});

validateTrackBtn.addEventListener('click', () => {
    if (track.isTrackClosed()) {
        alert('Piste fermée');
    } else {
        alert('Piste non-fermée');
    }
});


runBtn.addEventListener('click', () => {
    if (runBtn.checked) {
        currentTool = 'run';
        runLbl.focus();
    }
});


addEventListener("resize", (event) => {
    const divCanvas = document.getElementById('divCanvas');

    canvas.width = divCanvas.clientWidth;
    canvas.height = divCanvas.clientHeight;
});

var population;
var geneticAlgorithm;

function restart(newPopulation) {
    for (let i = 0; i < newPopulation.length; i++) {
        redCars[i].neuralNetwork = newPopulation[i];
        redCars[i].neuralNetwork.isDead = false;
        redCars[i].reset();
        track.placeCarAtStartPos(redCars[i]);
    }
}

document.addEventListener('DOMContentLoaded', function () {

    const numRedCars = 50;
    let keyPressed = {};
    geneticAlgorithm = initGeneticAlgorithm(numRedCars);
    geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
        restart(newPopulation);
    }

    if (track.loadTrack()) {
        // Create red cars
        for (let i = 0; i < geneticAlgorithm.population.length; i++) {
            const redCar = new Car(canvas.width / 2, canvas.height / 2, 80, 40, 'red', 180, geneticAlgorithm.population[i], track.squareSize);
            redCar.reset();
            track.placeCarAtStartPos(redCar);
            redCars.push(redCar);
        }
        geneticAlgorithm.loadPopulation()
    } else {
        track.generateClosedTrack();
        startPoint = track.selectStartPoint();
        track.path = track.getTrackPath();

        // Create red cars
        for (let i = 0; i < geneticAlgorithm.population.length; i++) {
            const redCar = new Car(canvas.width / 2, canvas.height / 2, 80, 40, 'red', 180, geneticAlgorithm.population[i], track.squareSize);
            redCar.reset();
            track.placeCarAtStartPos(redCar);
            redCars.push(redCar);
        }

    }

    track.buildQuadTree();

    population = redCars.map(car => car.neuralNetwork);


    geneticAlgorithm.run(bestIndividual => {
        console.log("L'algorithme génétique a terminé. Meilleur individu : ", bestIndividual);
    });

    function handleKeypress() {
        if (currentTool != "run")
            return;

        if (keyPressed['ArrowUp'])
            redCars[0].acceleration = 0.1;
        else if (keyPressed['ArrowDown'])
            redCars[0].acceleration = -0.1;
        else
            redCars[0].acceleration = 0;

        if (keyPressed['ArrowLeft'])
            redCars[0].Steering.update(-0.5);
        else if (keyPressed['ArrowRight'])
            redCars[0].Steering.update(0.5);
        else
            redCars[0].Steering.reset();

        if (keyPressed['r'])
            restartGame();
    }

    function gameLoop() {
        handleKeypress();
        // Redessiner tout
        track.redraw();

        requestAnimationFrame(gameLoop);
    }

    gameLoop();


    // Event listeners for keyboard input
    document.addEventListener('keydown', (event) => {
        const key = event.key;
        keyPressed[key] = true;
    });

    document.addEventListener('keyup', (event) => {
        const key = event.key;
        keyPressed[key] = false;
    });
});