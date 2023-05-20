const CANVAS_SIZE = 800;
const TILE_SIZE = 10;
const CHANCE_TO_START_ALIVE = 0.4;

let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');

// Initialize a 2D array
let cells = new Array(CANVAS_SIZE / TILE_SIZE);
for(let i = 0; i < cells.length; i++) {
    cells[i] = new Array(CANVAS_SIZE / TILE_SIZE);
}

function initialize() {
    for(let x = 0; x < cells.length; x++) {
        for(let y = 0; y < cells[0].length; y++) {
            cells[x][y] = Math.random() < CHANCE_TO_START_ALIVE ? 1 : 0;
        }
    }
}

function doSimulationStep() {
    let newCells = JSON.parse(JSON.stringify(cells)); // Copy the array

    for(let x = 0; x < cells.length; x++) {
        for(let y = 0; y < cells[0].length; y++) {
            let aliveNeighbours = countAliveNeighbours(x, y);

            if(cells[x][y]) {
                if(aliveNeighbours < 2 || aliveNeighbours > 3) {
                    newCells[x][y] = 0;
                } else {
                    newCells[x][y] = 1;
                }
            } else {
                if(aliveNeighbours == 3) {
                    newCells[x][y] = 1;
                }
            }
        }
    }

    cells = newCells;
}

function countAliveNeighbours(x, y) {
    let count = 0;
    for(let i = -1; i < 2; i++) {
        for(let j = -1; j < 2; j++) {
            let neighbourX = x + i;
            let neighbourY = y + j;

            if(i == 0 && j == 0) {
                // Do nothing for the current cell
            } else if(neighbourX < 0 || neighbourY < 0 || neighbourX >= cells.length || neighbourY >= cells[0].length) {
                count++;
            } else if(cells[neighbourX][neighbourY]) {
                count++;
            }
        }
    }

    return count;
}

function drawCells() {
    context.fillStyle = 'black';
    context.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    context.fillStyle = 'white';

    for(let x = 0; x < cells.length; x++) {
        for(let y = 0; y < cells[0].length; y++) {
            if(cells[x][y]) {
                context.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
            }
        }
    }
}

function update() {
    doSimulationStep();
    drawCells();
    requestAnimationFrame(update);
}

initialize();
update();
