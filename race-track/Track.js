class Track {
    constructor(canvas) {
        this.pan = {
            x: 0,
            y: 0
        };
        this.path = [];
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");

        this.squareSize = 500;
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
            revert: true
        };

        this.zoomLevel = 0.5;
        this.maxSquareSize = 300;

        //this.drawGrid();
    }

    drawGrid() {
        ctx.strokeStyle = 'darkGreen';
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

    setTrack(x, y) {
        this.grid[x][y] = true;
    }

    drawTrack() {
        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                if (this.grid[x][y]) {
                    ctx.fillStyle = "darkgray";
                    ctx.strokeStyle = 'darkgray';

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
                    let neighborCount = 0;
                    for (let neighbor of neighbors) {
                        if (
                            neighbor.x >= 0 &&
                            neighbor.x < this.gridWidth &&
                            neighbor.y >= 0 &&
                            neighbor.y < this.gridHeight &&
                            this.grid[neighbor.x][neighbor.y]
                        ) {
                            neighborCount++;
                        }
                    }

                    if (neighborCount == 2) {
                        const top = this.grid[neighbors[3].x][neighbors[3].y];
                        const bottom = this.grid[neighbors[2].x][neighbors[2].y];
                        const left = this.grid[neighbors[1].x][neighbors[1].y];
                        const right = this.grid[neighbors[0].x][neighbors[0].y];

                        ctx.beginPath();
                        if (right && bottom) {
                            ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize, this.squareSize, Math.PI, 1.5 * Math.PI, false);
                            ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize);
                            ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                        } else if (left && bottom) {
                            ctx.arc(x * this.squareSize, y * this.squareSize + this.squareSize, this.squareSize, 1.5 * Math.PI, 2 * Math.PI, false);
                            ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                            ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                        } else if (right && top) {
                            ctx.arc(x * this.squareSize + this.squareSize, y * this.squareSize, this.squareSize, Math.PI / 2, Math.PI, false);
                            ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize);
                            ctx.lineTo(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize);
                        } else if (left && top) {
                            ctx.arc(x * this.squareSize, y * this.squareSize, this.squareSize, 0, Math.PI / 2, false);
                            ctx.lineTo(x * this.squareSize, y * this.squareSize + this.squareSize);
                            ctx.lineTo(x * this.squareSize, y * this.squareSize);
                        } else {
                            ctx.rect(x * this.squareSize, y * this.squareSize, this.squareSize, this.squareSize);
                        }
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

    getTrackGeometry() {
        let geometry = {
            lines: [],
            arcs: []
        };

        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
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
                    let neighborCount = 0;
                    for (let neighbor of neighbors) {
                        if (
                            neighbor.x >= 0 &&
                            neighbor.x < this.gridWidth &&
                            neighbor.y >= 0 &&
                            neighbor.y < this.gridHeight &&
                            this.grid[neighbor.x][neighbor.y]
                        ) {
                            neighborCount++;
                        }
                    }

                    if (neighborCount == 2) {
                        const top = this.grid[neighbors[3].x][neighbors[3].y];
                        const bottom = this.grid[neighbors[2].x][neighbors[2].y];
                        const left = this.grid[neighbors[1].x][neighbors[1].y];
                        const right = this.grid[neighbors[0].x][neighbors[0].y];
                        if (top && bottom) { // Vertical
                            geometry.lines.push({
                                p1: new Vector(x * this.squareSize, y * this.squareSize),
                                p2: new Vector(x * this.squareSize, y * this.squareSize + this.squareSize)
                            });
                            geometry.lines.push({
                                p1: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize),
                                p2: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize)
                            });
                        } else if (left && right) { // Horizontal
                            geometry.lines.push({
                                p1: new Vector(x * this.squareSize, y * this.squareSize),
                                p2: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize)
                            });
                            geometry.lines.push({
                                p1: new Vector(x * this.squareSize, y * this.squareSize + this.squareSize),
                                p2: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize)
                            });
                        } else if (top && left) { // Top left corner
                            geometry.arcs.push({
                                center: new Vector(x * this.squareSize, y * this.squareSize),
                                radius: this.squareSize,
                                startAngle: 0,
                                endAngle: Math.PI / 2,
                                anticlockwise: false
                            });
                        } else if (top && right) { // Top right corner
                            geometry.arcs.push({
                                center: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize),
                                radius: this.squareSize,
                                startAngle: Math.PI / 2,
                                endAngle: Math.PI,
                                anticlockwise: false
                            });
                        } else if (bottom && left) { // Bottom left corner
                            geometry.arcs.push({
                                center: new Vector(x * this.squareSize, y * this.squareSize + this.squareSize),
                                radius: this.squareSize,
                                startAngle: 1.5 * Math.PI,
                                endAngle: 2 * Math.PI,
                                anticlockwise: false
                            });
                        } else if (bottom && right) { // Bottom right corner
                            geometry.arcs.push({
                                center: new Vector(x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize),
                                radius: this.squareSize,
                                startAngle: Math.PI,
                                endAngle: 1.5 * Math.PI,
                                anticlockwise: false
                            });
                        }
                    }
                }
            }
        }

        return geometry;
    }




    drawTrackGeometry(geometry, ctx) {
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 10;
        ctx.fillStyle = 'black';

        ctx.beginPath();
        for (let i = 0; i < geometry.lines.length; i++) {
            const {
                p1,
                p2
            } = geometry.lines[i];
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
        }
        ctx.stroke();

        for (let i = 0; i < geometry.arcs.length; i++) {
            const {
                center,
                radius,
                startAngle,
                endAngle,
                anticlockwise
            } = geometry.arcs[i];
            ctx.beginPath();
            ctx.arc(center.x, center.y, radius, startAngle, endAngle, anticlockwise);
            ctx.stroke();
        }
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

    panEvent(event) {
        event.preventDefault();
        this.pan.x += event.movementX;
        this.pan.y += event.movementY;
        this.redraw();
    }

    zoom(event) {
        event.preventDefault();
        const scaleFactor = 1.1;
        const zoomFactor = event.deltaY < 0 ? scaleFactor : 1 / scaleFactor;
        this.zoomLevel *= zoomFactor;

        this.redraw();
    }

    redraw() {
        if (!this.redraw.debounced) {
            this.redraw.debounced = true;
            setTimeout(() => {
                this.redraw.debounced = false;
                // The code that needs to be debounced goes here:

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.save();
                ctx.translate(this.pan.x, this.pan.y);
                ctx.scale(this.zoomLevel, this.zoomLevel);
                this.drawGrid();
                this.drawTrack();
                let trackGeometry = this.getTrackGeometry();
                this.drawTrackGeometry(trackGeometry, ctx);
                let carIndex = 0;
                for (let redCar of redCars) {
                    if (!redCar.neuralNetwork.isDead && redCar.neuralNetwork == geneticAlgorithm.bestIndividual)
                        redCar.drawLaserSensors(ctx);
                    redCar.draw(ctx);
                    for (let laserSensor of redCar.laserSensors) {
                        let intersection = laserSensor.calculateTrackIntersection(trackGeometry);
                        laserSensor.intersectionInfo = intersection;
                        if (carIndex == 0)
                            drawIntersectionPoint(ctx, intersection);
                    }
                    // Check for collisions walls
                    let intersect = redCar.calculateIntersectionWithTrack(trackGeometry);
                    if (intersect.objectType) {
                        intersect.objectType = "other"
                        drawIntersectionPoint(ctx, intersect)
                    }
                    carIndex++;
                }

                ctx.restore();

            }, 1000 / 60);
        }
    }

    redrawNormal() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(this.pan.x, this.pan.y);
        ctx.scale(this.zoomLevel, this.zoomLevel);
        this.drawGrid();
        this.drawTrack();
        let geometry = this.getTrackGeometry();
        this.drawTrackGeometry(geometry, ctx);
        let carIndex = 0;
        for (let redCar of redCars) {
            if (carIndex == 0)
                redCar.drawLaserSensors(ctx);
            redCar.draw(ctx);
            for (let laserSensor of redCar.laserSensors) {
                let intersection = laserSensor.calculateTrackIntersection(geometry);
                laserSensor.intersectionInfo = intersection;
                if (carIndex == 0)
                    drawIntersectionPoint(ctx, intersection);
            }
            carIndex++;;
        }

        ctx.restore();
    }




    getTrackPath() {
        const visited = new Array(this.gridWidth).fill(null).map(() => new Array(this.gridHeight).fill(false));
        let path = [];

        let visit = (x, y, dir) => {
            visited[x][y] = true;

            const cellPos = {
                x,
                y
            };
            if (!dir) {
                dir = this.getTrackDirectionSimple({
                    x,
                    y
                });
                if (dir == "horizontal" && startPoint.revert)
                    dir = "right";
                else if (dir == "horizontal" && !startPoint.revert)
                    dir = "left";
                else if (dir == "vertical" && startPoint.revert)
                    dir = "down";
                else if (dir == "vertical" && !startPoint.revert)
                    dir = "up";
            }

            let cellDir = dir;
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
                    if (neighbor.x === x + 1 && neighbor.y === y + 1) {
                        neighborDir = "upleft";
                        0
                    } else if (neighbor.x === x - 1) {
                        neighborDir = "left";
                    } else if (neighbor.x === x + 1) {
                        neighborDir = "right";
                    } else if (neighbor.y === y - 1) {
                        neighborDir = "up";
                    } else if (neighbor.y === y + 1) {
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
        const trackPath = this.getTrackPath();
        const trackCellCount = this.grid.flat().filter(cell => cell).length;

        if (trackPath.length !== trackCellCount) {
            return false;
        }

        const firstCell = trackPath[0];
        const lastCell = trackPath[trackPath.length - 1];
        const neighbors = [{
                x: lastCell.pos.x + 1,
                y: lastCell.pos.y
            },
            {
                x: lastCell.pos.x - 1,
                y: lastCell.pos.y
            },
            {
                x: lastCell.pos.x,
                y: lastCell.pos.y + 1
            },
            {
                x: lastCell.pos.x,
                y: lastCell.pos.y - 1
            },
        ];

        return neighbors.some(neighbor => neighbor.x === firstCell.pos.x && neighbor.y === firstCell.pos.y);
    }

    getTrackDirection(pos) {
        let path = this.path;

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
                        car.angle = direction === 'right' ? 180 : direction === 'up' ? 90 : direction === 'left' ? 0 : 270;
                        car.color = 'red'
                    }
                }
            }
        }
    }


    drawMultipleArrowheads(ctx, fromX, fromY, toX, toY, headLength, headWidth, numArrowheads, reverseDirection) {
        const dx = toX - fromX;
        const dy = toY - fromY;
        const angle = Math.atan2(dy, dx);
        const halfHeadWidthAngle = Math.atan2(headWidth / 2, headLength);
        const length = Math.sqrt(dx * dx + dy * dy);
        const step = length / (numArrowheads);

        const direction = reverseDirection ? -1 : 1;

        for (let i = 1; i <= numArrowheads; i++) {
            const arrowX = fromX + i * step * Math.cos(angle);
            const arrowY = fromY + i * step * Math.sin(angle);

            ctx.beginPath();
            ctx.moveTo(arrowX, arrowY);
            ctx.lineTo(arrowX - direction * headLength * Math.cos(angle - halfHeadWidthAngle), arrowY - direction * headLength * Math.sin(angle - halfHeadWidthAngle));
            ctx.moveTo(arrowX, arrowY);
            ctx.lineTo(arrowX - direction * headLength * Math.cos(angle + halfHeadWidthAngle), arrowY - direction * headLength * Math.sin(angle + halfHeadWidthAngle));
            ctx.stroke();
        }
    }


    drawMultipleArrowheadsOnArc(ctx, centerX, centerY, radius, startAngle, endAngle, headLength, headWidth, numArrowheads, counterClockwise) {
        const angleDifference = counterClockwise ? startAngle - endAngle : endAngle - startAngle;
        const angleStep = angleDifference / (numArrowheads);
        const halfHeadWidthAngle = Math.atan2(headWidth / 2, headLength);

        for (let i = 0; i <= numArrowheads; i++) {
            const currentAngle = counterClockwise ? startAngle - i * angleStep : startAngle + i * angleStep;
            const arrowX = centerX + radius * Math.cos(currentAngle);
            const arrowY = centerY + radius * Math.sin(currentAngle);

            const angle = currentAngle + (counterClockwise ? -Math.PI / 2 : Math.PI / 2);

            ctx.beginPath();
            ctx.moveTo(arrowX, arrowY);
            ctx.lineTo(arrowX - headLength * Math.cos(angle - halfHeadWidthAngle), arrowY - headLength * Math.sin(angle - halfHeadWidthAngle));
            ctx.moveTo(arrowX, arrowY);
            ctx.lineTo(arrowX - headLength * Math.cos(angle + halfHeadWidthAngle), arrowY - headLength * Math.sin(angle + halfHeadWidthAngle));
            ctx.stroke();
        }
    }


    drawDashedLines() {
        ctx.strokeStyle = '#FF0';
        ctx.lineWidth = 5;
        //ctx.setLineDash([50, 50]);

        const arrowHeadLength = 20;
        const arrowHeadWidth = 15;
        const numArrowheads = 8;
        const numArrowheadsArc = 6;
        for (let path of this.path) {
            let x = path.pos.x;
            let y = path.pos.y;
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
            let neighborCount = 0;
            for (let neighbor of neighbors) {
                if (
                    neighbor.x >= 0 &&
                    neighbor.x < this.gridWidth &&
                    neighbor.y >= 0 &&
                    neighbor.y < this.gridHeight &&
                    this.grid[neighbor.x][neighbor.y]
                ) {
                    neighborCount++;
                }
            }

            if (neighborCount == 2) {
                const top = this.grid[neighbors[3].x][neighbors[3].y];
                const bottom = this.grid[neighbors[2].x][neighbors[2].y];
                const left = this.grid[neighbors[1].x][neighbors[1].y];
                const right = this.grid[neighbors[0].x][neighbors[0].y];

                ctx.beginPath();
                ctx.stroke();
                if (top && bottom) {
                    let reverse = path.dir == 'up';
                    this.drawMultipleArrowheads(ctx, x * this.squareSize + this.squareSize / 2, y * this.squareSize, x * this.squareSize + this.squareSize / 2, (y + 1) * this.squareSize, arrowHeadLength, arrowHeadWidth, numArrowheads, reverse);
                } else if (left && right) {
                    let reverse = path.dir == 'left';
                    this.drawMultipleArrowheads(ctx, x * this.squareSize, y * this.squareSize + this.squareSize / 2, (x + 1) * this.squareSize, y * this.squareSize + this.squareSize / 2, arrowHeadLength, arrowHeadWidth, numArrowheads, reverse);
                } else if (top && left) {
                    let clockwise = path.dir == 'right';
                    this.drawMultipleArrowheadsOnArc(ctx, x * this.squareSize, y * this.squareSize, this.squareSize / 2, 0, Math.PI / 2, arrowHeadLength, arrowHeadWidth, numArrowheadsArc, clockwise);
                } else if (top && right) {
                    let clockwise = path.dir == 'down';
                    this.drawMultipleArrowheadsOnArc(ctx, x * this.squareSize + this.squareSize, y * this.squareSize, this.squareSize / 2, Math.PI / 2, Math.PI, arrowHeadLength, arrowHeadWidth, numArrowheadsArc, clockwise);
                } else if (bottom && left) {
                    let clockwise = path.dir == 'up';
                    this.drawMultipleArrowheadsOnArc(ctx, x * this.squareSize, y * this.squareSize + this.squareSize, this.squareSize / 2, 1.5 * Math.PI, 2 * Math.PI, arrowHeadLength, arrowHeadWidth, numArrowheadsArc, clockwise);
                } else if (bottom && right) {
                    let clockwise = path.dir == 'left';
                    this.drawMultipleArrowheadsOnArc(ctx, x * this.squareSize + this.squareSize, y * this.squareSize + this.squareSize, this.squareSize / 2, Math.PI, 1.5 * Math.PI, arrowHeadLength, arrowHeadWidth, numArrowheadsArc, clockwise);
                }
            }
            ctx.stroke();
        }
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
            track.path = track.getTrackPath();
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
            x: Math.floor(((event.clientX - rect.left - this.pan.x) / this.zoomLevel) / this.squareSize),
            y: Math.floor(((event.clientY - rect.top - this.pan.y) / this.zoomLevel) / this.squareSize),
        };
    }

    clearTrack() {
        for (let x = 0; x < this.gridWidth; x++) {
            for (let y = 0; y < this.gridHeight; y++) {
                this.grid[x][y] = false;
            }
        }
        this.startPoint = {
            x: 0,
            y: 0,
            dir: "",
            revert: true
        };
        //this.drawGrid();
    }


    findNearestCheckpoint(vehiclePosition, checkpoints) {
        let nearestCheckpoint = null;
        let nearestDistance = Number.MAX_VALUE;
        let nearestIndex;

        let index = 0;
        for (let checkpoint of checkpoints) {
            let distance = vehiclePosition.distanceTo(new Vector(checkpoint.pos.x, checkpoint.pos.y).multiply(this.squareSize));

            if (distance < nearestDistance) {
                nearestCheckpoint = checkpoint;
                nearestDistance = distance;
                nearestIndex = index;
            }
            index++;
        }

        return nearestIndex;
    }

    calculateCompletionPercentage(car) {
        const path = this.getTrackPath();
        let carPosition = new Vector(car.x, car.y);
        let distanceCovered = 0;
        let checkpointIndex = this.findNearestCheckpoint(carPosition, path);
        let checkpointDistance = 0;
        let totalDistance = 0;

        // Calculate distance covered and total distance
        for (let i = 0; i < path.length - 1; i++) {
            const current = new Vector(path[i].pos.x * this.squareSize + this.squareSize / 2, path[i].pos.y * this.squareSize + this.squareSize / 2);
            const next = new Vector(path[i + 1].pos.x * this.squareSize + this.squareSize / 2, path[i + 1].pos.y * this.squareSize + this.squareSize / 2);
            const distance = next.subtract(current).length();
            totalDistance += distance;
            if (i >= checkpointIndex) {
                checkpointDistance += distance;
            }
        }

        // Calculate distance from car to next checkpoint
        const checkpointPos = new Vector(path[checkpointIndex].pos.x * this.squareSize + this.squareSize / 2, path[checkpointIndex].pos.y * this.squareSize + this.squareSize / 2);
        const nextCheckpointIndex = (checkpointIndex + 1) % path.length;
        const nextCheckpointPos = new Vector(path[nextCheckpointIndex].pos.x * this.squareSize + this.squareSize / 2, path[nextCheckpointIndex].pos.y * this.squareSize + this.squareSize / 2);
        const distanceToCheckpoint = checkpointPos.subtract(carPosition).length();
        const distanceToNextCheckpoint = distanceToCheckpoint + nextCheckpointPos.subtract(checkpointPos).length();


        distanceCovered += totalDistance - checkpointDistance + (this.squareSize - distanceToCheckpoint) - this.squareSize;

        // Calculate completion percentage
        let completionPercentage = distanceCovered / totalDistance;
        completionPercentage = Math.min(Math.max(completionPercentage, 0), 1);

        return completionPercentage;
    }


}