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

// const canvas = document.getElementById('parking');
// const ctx = canvas.getContext('2d');
// const parkingLot = new ParkingLot(100, 60, 100, 6, 10);

function initGeneticAlgorithm(populationSize) {
    //const populationSize = 50;
    const inputSize = 8;
    const hiddenSize = 4;
    const outputSize = 2;
    const mutationRate = 0.1;
    const maxGenerations = 100;
    const inputs = []; // Vous pouvez ajouter des données d'entrée spécifiques ici
    const expectedOutputs = []; // Vous pouvez ajouter des sorties attendues spécifiques ici
    let population = [];
    for (let i = 0; i < populationSize; i++) {
        const neuralNetwork = new NeuralNetwork(8, 4, 2);
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

function updateTrack(event) {
    if (!mouseDown)
        return;

    const pos = track.getMousePosition(event);

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

    if (currentTool == "run")
        return;

    if (event.button != 0) {
        return;
    }
    const pos = track.getMousePosition(event);

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
    geneticAlgorithm.bestIndividual.saveGenes();
    alert("saved")
});

loadBestNeuralNetworkBtn.addEventListener('click', () => {
    redCars.length = 1;
    let individual = new NeuralNetwork();
    individual.loadGenes();
    restart([individual])
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
});

loadTrackBtn.addEventListener('click', () => {
    track.loadTrack();
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
        redCars[i].neuralNetwork = geneticAlgorithm.population[i];
        redCars[i].neuralNetwork.isDead = false;
        redCars[i].reset();
        track.placeCarAtStartPos(redCars[i]);
    }
}

document.addEventListener('DOMContentLoaded', function () {

    //track.loadTrack();
    track.generateClosedTrack();
    startPoint = track.selectStartPoint();
    track.path = track.getTrackPath();        


    const numRedCars = 50;
    let keyPressed = {};
    geneticAlgorithm = initGeneticAlgorithm(numRedCars);
    geneticAlgorithm.onNewGenerationCreatedFn = (newPopulation) => {
        restart(newPopulation);
    }

    // Create red cars
    for (let i = 0; i < geneticAlgorithm.population.length; i++) {
        const redCar = new Car(canvas.width / 2, canvas.height / 2, 80, 40, 'red', 180, geneticAlgorithm.population[i], track.squareSize);
        redCar.reset();
        track.placeCarAtStartPos(redCar);
        redCars.push(redCar);
    }

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
        let trackGeometry = track.getTrackGeometry();
        handleKeypress();
        let index = 0;
        for (let redCar of redCars) {
            redCar.applyNeuralNetwork();
            redCar.update(trackGeometry, track);
            for (let laserSensor of redCar.laserSensors) {
                let intersection = laserSensor.calculateTrackIntersection(trackGeometry);
                laserSensor.intersectionInfo = intersection;
            }

            let completionPct = track.calculateCompletionPercentage(redCar)
            redCar.updateCheckpoint();            
            redCar.neuralNetwork.currentFitness = completionPct;
            if (redCar.neuralNetwork.isCompleted) {
                const slowTime = track.path.length * 1000 * track.lapToWin; // 1 second per square in the path
                let timeBonus = slowTime - redCar.timeTakenToCompleteTrack;
                redCar.neuralNetwork.currentFitness = timeBonus;
            }


            if (redCar.neuralNetwork == geneticAlgorithm.bestIndividual){
                drawText(ctx, "completion: " + (completionPct * 100).toFixed(1), 10, 30)
                // track.pan.x = canvas.width / 2 - redCar.x;
                // track.pan.y = canvas.height / 2 - redCar.y;
            }
            index++;
        }

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