class CaveGenerator {
    constructor(width, height, fillProbability, birthLimit, deathLimit, steps) {
        this.width = width;
        this.height = height;
        this.fillProbability = fillProbability;
        this.birthLimit = birthLimit;
        this.deathLimit = deathLimit;
        this.steps = steps;
    }

    generateMap() {
        let map = this.createRandomMap();

        for (let i = 0; i < this.steps; i++) {
            map = this.doSimulationStep(map);
        }

        return map;
    }

    createRandomMap() {
        let map = new Array(this.height);
        for (let y = 0; y < this.height; y++) {
            map[y] = new Array(this.width);
            for (let x = 0; x < this.width; x++) {
                map[y][x] = Math.random() < this.fillProbability ? 1 : 0;
            }
        }
        return map;
    }

    doSimulationStep(map) {
        let newMap = new Array(this.height);
        for (let y = 0; y < map.length; y++) {
            newMap[y] = new Array(this.width);
            for (let x = 0; x < map[0].length; x++) {
                let nbs = this.countAliveNeighbors(map, x, y);
                if (map[y][x] === 1) {
                    newMap[y][x] = nbs < this.deathLimit ? 0 : 1;
                } else {
                    newMap[y][x] = nbs > this.birthLimit ? 1 : 0;
                }
            }
        }
        return newMap;
    }

    countAliveNeighbors(map, x, y) {
        let count = 0;
        for (let i = -1; i < 2; i++) {
            for (let j = -1; j < 2; j++) {
                let neighbourX = x + i;
                let neighbourY = y + j;
                if (i === 0 && j === 0) {
                    // Do nothing for the center cell.
                } else if (neighbourX < 0 || neighbourY < 0 || neighbourX >= this.width || neighbourY >= this.height) {
                    // Count out-of-bounds as alive.
                    count = count + 1;
                } else if (map[neighbourY][neighbourX] === 1) {
                    // Count alive cells.
                    count = count + 1;
                }
            }
        }
        return count;
    }


    
}


function drawCave(context, map, cellSize) {
    // Clear the canvas before drawing.
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);

    // Set colors for the cave and free space.
    const colors = {
        '1': '#000', // Color for the cave walls.
        '0': '#fff'  // Color for the free space.
    };

    for (let y = 0; y < map.length; y++) {
        for (let x = 0; x < map[0].length; x++) {
            context.fillStyle = colors[map[y][x]];
            context.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }
}

const canvas = document.getElementById('cavernCanvas');
const context = canvas.getContext('2d');

let generator = new CaveGenerator(800, 600, 0.4, 4, 3, 1);
let map = generator.generateMap();
drawCave(context, map, 1);