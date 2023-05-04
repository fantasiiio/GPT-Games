class Track {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");

        this.squareSize = 200;
        this.gridWidth = 30;
        this.gridHeight = 30;
        this.gridSize = this.squareSize * this.gridWidth;

        this.grid = new Array(this.gridWidth)
            .fill(null)
            .map(() => new Array(this.gridHeight).fill(false));

        this.startPoint = {
            x: 0,
            y: 0,
            dir: "",
        };

        this.zoomLevel = 0.5;
        this.maxSquareSize = 300;

        this.drawGrid();
    }

    drawGrid() {
        ctx.strokeStyle = '#ccc';
        for (let i = 0; i <= this.gridWidth; i++) {
            ctx.beginPath();
            ctx.moveTo(i * this.squareSize, 0);
            ctx.lineTo(i * this.squareSize, this.gridSize);
            ctx.stroke();
        }

        for (let j = 0; j <= this.gridHeight; j++) {
            ctx.beginPath();
            ctx.moveTo(0, j * this.squareSize);
            ctx.lineTo(this.gridSize, j * this.squareSize);
            ctx.stroke();
        }
    }

    drawTrack(x, y) {
        //ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.grid[x][y] = true;
        this.drawGrid();

        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                if (this.grid[x][y]) {
                    ctx.fillStyle = "darkgray";
                    ctx.strokeStyle = 'darkgray';

                    let isBottomRightCorner = x > 0 && y > 0 && this.grid[x - 1][y] && this.grid[x][y - 1];
                    let isBottomLeftCorner = x < this.gridWidth - 1 && y > 0 && this.grid[x + 1][y] && this.grid[x][y - 1];
                    let isTopRightCorner = x > 0 && y < this.gridHeight - 1 && this.grid[x - 1][y] && this.grid[x][y + 1];
                    let isTopLeftCorner = x < this.gridWidth - 1 && y < this.gridHeight - 1 && this.grid[x + 1][y] && this.grid[x][y + 1];

                    ctx.beginPath();
                    if (isTopLeftCorner) {
                        ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize, this.squareSize, Math.PI, 1.5 * Math.PI, false);
                        ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize);
                        ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                    } else if (isTopRightCorner) {
                        ctx.arc(x * this.squareSize, y * this.squareSize + this.squareSize, this.squareSize, 1.5 * Math.PI, 2 * Math.PI, false);
                        ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                        ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                    } else if (isBottomLeftCorner) {
                        ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize, this.squareSize, Math.PI / 2, Math.PI, false);
                        ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize);
                        ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize);
                    } else if (isBottomRightCorner) {
                        ctx.arc(x * this.squareSize, y * this.squareSize, this.squareSize, 0, Math.PI / 2, false);
                        ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                        ctx.lineTo(x * this.squareSize, y * this.squareSize);
                    } else {
                        ctx.rect(x * this.squareSize, y * this.squareSize, this.squareSize, this.squareSize);
                    }
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                }
            }
        }
        this.drawDashedLines();

    }

    clearSquare(x, y) {
        this.grid[x][y] = false;
        ctx.fillStyle = '#FFF';
        ctx.strokeStyle = '#ccc';
        ctx.fillRect(x * this.squareSize, y * this.squareSize, this.squareSize, this.squareSize);
        ctx.strokeRect(x * this.squareSize, y * this.squareSize, this.squareSize, this.squareSize);

        // Redraw the this.grid lines for the cleared square
        ctx.beginPath();
        ctx.moveTo(x * this.squareSize, y * this.squareSize);
        ctx.lineTo(x * this.squareSize, (y + 1) * this.squareSize);
        ctx.moveTo(x * this.squareSize, y * this.squareSize);
        ctx.lineTo((x + 1) * this.squareSize, y * this.squareSize);
        ctx.stroke();
    }

    zoom(event) {
        const scaleFactor = 1.1;
        const zoomFactor = event.deltaY < 0 ? scaleFactor : 1 / scaleFactor;
        this.zoomLevel *= zoomFactor;
        this.redraw();
    }

    redraw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(this.zoomLevel, this.zoomLevel);
        this.drawGrid();
        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                if (this.grid[x][y]) {
                    this.drawTrack(x, y);
                }
            }
        }

        for (let redCar of redCars) {
            redCar.draw(ctx);
        }
        ctx.restore();
    }


    getTrackPath() {
        const visited = new Array(this.gridWidth).fill(null).map(() => new Array(this.gridHeight).fill(false));
        let path = [];

        let visit = (x, y, dir)=> {
            visited[x][y] = true;

            const cellPos = {
                x,
                y
            };
            let cellDir = dir || this.getTrackDirectionSimple({
                x,
                y
            });
            path.push({
                pos: cellPos,
                dir: cellDir
            });

            const neighbors = [{
                    x: x + 1,
                    y
                },
                {
                    x: x - 1,
                    y
                },
                {
                    x,
                    y: y + 1
                },
                {
                    x,
                    y: y - 1
                },
            ];

            for (let neighbor of neighbors) {
                if (
                    neighbor.x >= 0 &&
                    neighbor.x < this.gridWidth &&
                    neighbor.y >= 0 &&
                    neighbor.y < this.gridHeight &&
                    !visited[neighbor.x][neighbor.y] &&
                    this.grid[neighbor.x][neighbor.y]
                ) {
                    //const neighborPos = { x: neighbor.x, y: neighbor.y };
                    let neighborDir;
                    if (neighbor.x === x + 1) {
                        neighborDir = "left";
                    } else if (neighbor.x === x - 1) {
                        neighborDir = "right";
                    } else if (neighbor.y === y + 1) {
                        neighborDir = "up";
                    } else if (neighbor.y === y - 1) {
                        neighborDir = "down";
                    }

                    visit(neighbor.x, neighbor.y, neighborDir);
                }
            }
        }

        visit(startPoint.x, startPoint.y);
        return path;
    }


    isTrackClosed() {
        let path2 = this.getTrackPath();

        if (path2.length < 4) {
            return false;
        }

        const first = path2[0];
        const last = path2[path2.length - 1];

        return first.pos.x === last.pos.x && first.pos.y === last.pos.y;
    }

    getTrackDirection(pos) {
        let path = this.getTrackPath();

        for (let i = 0; i < path.length; i++) {
            if (path[i].pos.x === pos.x && path[i].pos.y === pos.y) {
                return path[i].dir;
            }
        }

        return null;
    }

    getTrackDirectionSimple(pos) {
        const {
            x,
            y
        } = pos;

        if (this.grid[x][y]) {
            const neighbors = [{
                    x: x + 1,
                    y
                },
                {
                    x: x - 1,
                    y
                },
                {
                    x,
                    y: y + 1
                },
                {
                    x,
                    y: y - 1
                },
            ];

            const validNeighbors = neighbors.filter(
                (neighbor) =>
                neighbor.x >= 0 && neighbor.x < this.gridWidth && neighbor.y >= 0 && neighbor.y < this.gridHeight && this.grid[neighbor.x][neighbor.y]
            );

            if (validNeighbors.length === 1) {
                const neighbor = validNeighbors[0];

                if (neighbor.x === x + 1) {
                    return 'right';
                } else if (neighbor.x === x - 1) {
                    return 'left';
                } else if (neighbor.y === y + 1) {
                    return 'down';
                } else if (neighbor.y === y - 1) {
                    return 'up';
                }
            } else if (validNeighbors.length === 2) {
                const neighbor1 = validNeighbors[0];
                const neighbor2 = validNeighbors[1];

                if (neighbor1.y === neighbor2.y) {
                    if (neighbor1.x === x + 1) {
                        return 'horizontal';
                    } else if (neighbor1.x === x - 1) {
                        return 'horizontal';
                    }
                } else if (neighbor1.x === neighbor2.x) {
                    if (neighbor1.y === y + 1) {
                        return 'vertical';
                    } else if (neighbor1.y === y - 1) {
                        return 'vertical';
                    }
                } else if (
                    (neighbor1.x === x + 1 && neighbor2.y === y - 1) ||
                    (neighbor2.x === x + 1 && neighbor1.y === y - 1)
                ) {
                    return 'bottomright';
                } else if (
                    (neighbor1.x === x + 1 && neighbor2.y === y + 1) ||
                    (neighbor2.x === x + 1 && neighbor1.y === y + 1)
                ) {
                    return 'topright';
                } else if (
                    (neighbor1.x === x - 1 && neighbor2.y === y - 1) ||
                    (neighbor2.x === x - 1 && neighbor1.y === y - 1)
                ) {
                    return 'bottomleft';
                } else if (
                    (neighbor1.x === x - 1 && neighbor2.y === y + 1) ||
                    (neighbor2.x === x - 1 && neighbor1.y === y + 1)
                ) {
                    return 'topleft';
                }
            }
        }

        return '';
    }


    placeCarAtStartPos(car) {
        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                if (this.grid[x][y]) {
                    if (x === startPoint.x && y === startPoint.y) {
                        car.x = x * this.squareSize + this.squareSize / 2;
                        car.y = y * this.squareSize + this.squareSize / 2;
                        let direction = this.getTrackDirection({
                            x,
                            y
                        });
                        car.angle = direction === "horizontal" ? 0 : 90;
                    }
                }
            }
        }
    }


    drawDashedLines() {
        ctx.strokeStyle = '#FF0';
        ctx.lineWidth = 5;
        ctx.setLineDash([50, 50]);

        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                if (this.grid[x][y]) {
                    const top = this.grid[x][y - 1];
                    const bottom = this.grid[x][y + 1];
                    const left = this.grid[x - 1][y];
                    const right = this.grid[x + 1][y];

                    ctx.beginPath();

                    if (top && bottom) {
                        ctx.moveTo(x * this.squareSize + this.squareSize / 2, y * this.squareSize);
                        ctx.lineTo(x * this.squareSize + this.squareSize / 2, (y + 1) * this.squareSize);
                    } else if (left && right) {
                        ctx.moveTo(x * this.squareSize, y * this.squareSize + this.squareSize / 2);
                        ctx.lineTo((x + 1) * this.squareSize, y * this.squareSize + this.squareSize / 2);
                    } else if (top && left) {
                        ctx.arc(x * this.squareSize, y * this.squareSize, this.squareSize / 2, 0, Math.PI / 2, false);
                    } else if (top && right) {
                        ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize, this.squareSize / 2, Math.PI / 2, Math.PI, false);
                    } else if (bottom && left) {
                        ctx.arc(x * this.squareSize, y * this.squareSize + this.squareSize, this.squareSize / 2, 1.5 * Math.PI, 2 * Math.PI, false);
                    } else if (bottom && right) {
                        ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize, this.squareSize / 2, Math.PI, 1.5 * Math.PI, false);
                    }

                    ctx.stroke();
                }
            }
        }

        ctx.setLineDash([]); // Reset the line dash to solid
        ctx.lineWidth = 1; // Reset the lineWidth to 1
    }

    saveTrack() {
        const data = {
            grid: this.grid,
            startPoint,
        };

        localStorage.setItem('track', JSON.stringify(data));
    }

    loadTrack() {
        const savedTrack = localStorage.getItem('track');
        if (savedTrack) {
            const savedData = JSON.parse(savedTrack);
            this.grid = savedData.grid;
            startPoint.x = savedData.startPoint.x;
            startPoint.y = savedData.startPoint.y;
            this.redraw();
            for (let redCar of redCars) {
                this.placeCarAtStartPos(redCar);
            }
            console.log('Piste chargée');
        } else {
            console.log('Aucune piste sauvegardée');
        }
    }

    getMousePosition(event) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: Math.floor(((event.clientX - rect.left) / this.zoomLevel) / this.squareSize),
            y: Math.floor(((event.clientY - rect.top) / this.zoomLevel) / this.squareSize),
        };
    }    
}

const canvas = document.getElementById('track-editor');
const ctx = canvas.getContext('2d');
const track = new Track(canvas);


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


function updateTrack() {
    if (!mouseDown)
        return;
    const pos = track.getMousePosition(event);

    if (currentTool === 'draw') {
        track.drawTrack(pos.x, pos.y);
    } else if (currentTool === 'erase') {
        track.clearSquare(pos.x, pos.y);
    }
}

let mouseDown = false;
canvas.addEventListener('mousedown', (event) => {
    if (currentTool == "run")
        return;
    const pos = track.getMousePosition(event);

    if (drawTrackBtn.checked) {
        drawing = true;

        if (track.grid[pos.x][pos.y]) {
            startPoint.x = pos.x;
            startPoint.y = pos.y;
            startPoint.dir = getTrackDirection(startPoint);
            for (let redCar of redCars) {
                track.placeCarAtStartPos(redCar);
            }
        }
        track.drawTrack(pos.x, pos.y);
    } else if (eraseTrackBtn.checked) {
        drawing = true;
        track.clearSquare(pos.x, pos.y);
    }
    mouseDown = true;
});

canvas.addEventListener('mouseup', (event) => {
    if (currentTool == "run")
        return;
    mouseDown = false;
});
canvas.addEventListener('mousemove', (event) => {
    if (currentTool == "run")
        return;
    updateTrack();
});

track.drawGrid();


// Toolbar buttons
const saveTrackBtn = document.getElementById('saveTrackBtn');
const loadTrackBtn = document.getElementById('loadTrackBtn');
const validateTrackBtn = document.getElementById('validateTrackBtn');
const editCheckpointsBtn = document.getElementById('editCheckpointsBtn');
const runBtn = document.getElementById('runBtn');
const drawTrackBtn = document.getElementById('drawTrackBtn');
const eraseTrackBtn = document.getElementById('eraseTrackBtn');
const buttonContents = document.getElementsByClassName('button-content');
const divCanvas = document.getElementById('divCanvas');

canvas.width = divCanvas.clientWidth;
canvas.height = divCanvas.clientHeight;

//divCanvas.clientWidth
let currentTool = 'run';

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
    if (isTrackClosed()) {
        alert('Piste fermée');
    } else {
        alert('Piste non-fermée');
    }
});


editCheckpointsBtn.addEventListener('click', () => {
    console.log('Modifier les points de contrôle');
    // Implement the functionality for editing checkpoints
});


runBtn.addEventListener('click', () => {
    currentTool = 'run';
});


addEventListener("resize", (event) => {
    const divCanvas = document.getElementById('divCanvas');

    canvas.width = divCanvas.clientWidth;
    canvas.height = divCanvas.clientHeight;
});

document.addEventListener('DOMContentLoaded', function () {

    const numRedCars = 1;
    // Create red cars
    for (let i = 0; i < numRedCars; i++) {
        //const neuralNetwork = new NeuralNetwork(8, 4, 2);
        const redCar = new Car(canvas.width / 2, canvas.height / 2, 80, 40, 'red', 180, null);
        track.placeCarAtStartPos({
            x: 0,
            y: 0
        });
        redCar.draw(ctx);
        redCars.push(redCar);
    }

    track.loadTrack();

    function gameLoop() {
        for (let redCar of redCars) {


            //redCar.updateControls();

            // Mettre à jour la position de la voiture rouge
            const prevX = redCar.x;
            const prevY = redCar.y;
            const prevWidth = redCar.width;
            const prevHeight = redCar.height;
            const prevAngle = redCar.angle;

            redCar.update();

            // Effacer la position précédente de la voiture rouge
            ctx.save();
            ctx.translate(prevX + prevWidth / 2, prevY + prevHeight / 2);
            ctx.rotate(prevAngle * Math.PI / 180);
            ctx.clearRect(-prevWidth / 2, -prevHeight / 2, prevWidth, prevHeight);
            ctx.restore();
            redCar.draw(ctx);

        }

        // Redessiner tout
        track.redraw();


        requestAnimationFrame(gameLoop);
    }

    gameLoop();

    // Event listeners for keyboard input
    document.addEventListener('keydown', (event) => {
        if (!currentTool == "run")
            return;
        const key = event.key;

        switch (key) {
            case 'ArrowUp':
                redCars[0].acceleration = 0.1;
                break;
            case 'ArrowDown':
                redCars[0].acceleration = -0.1;
                break;
            case 'ArrowLeft':
                redCars[0].steeringAngle = -30;
                break;
            case 'ArrowRight':
                redCars[0].steeringAngle = 30;
                break;
            case 'r':
            case 'R':
                restartGame();
                break;
        }
    });

    document.addEventListener('keyup', (event) => {
        if (!currentTool == "run")
            return;
        const key = event.key;

        if (key === 'ArrowUp' || key === 'ArrowDown') {
            redCars[0].acceleration = 0;
        } else if (key === 'ArrowLeft' || key === 'ArrowRight') {
            redCars[0].steeringAngle = 0;
        }
    });
});