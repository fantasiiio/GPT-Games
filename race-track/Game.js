const canvas = document.getElementById('track-editor');
const ctx = canvas.getContext('2d');
const track = new Track(canvas);

let isPanning = false;
let drawing = false;
let erasing = false;


const startPoint = {
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


canvas.width = divCanvas.clientWidth;
canvas.height = divCanvas.clientHeight;

//divCanvas.clientWidth
let currentTool = 'run';

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

document.addEventListener('DOMContentLoaded', function () {

    const numRedCars = 1;
    let keyPressed = {};

    // Create red cars
    for (let i = 0; i < numRedCars; i++) {
        const neuralNetwork = new NeuralNetwork(8, 4, 2);
        const redCar = new Car(canvas.width / 2, canvas.height / 2, 80, 40, 'red', 180, neuralNetwork);
        track.placeCarAtStartPos({
            x: 0,
            y: 0
        });

        redCars.push(redCar);
    }

    track.loadTrack();

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
        for (let redCar of redCars) {
            //redCar.applyNeuralNetwork();
            redCar.update(trackGeometry);

            let completionPct = track.calculateCompletionPercentage(redCar)
            drawText(ctx, "completion: " + (completionPct*100).toFixed(1), 10, 30)
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