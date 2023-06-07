let drawingMode = 'symmetric'; // Values can be 'normal' or 'symmetric'

// Get the canvas element and its 2D drawing context
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
// Translate the context to the center of the canvas
ctx.translate(canvas.width / 2, canvas.height / 2);


// Variables to track the drawing state
let isDrawing = false;
let startCoordinates = {
    x: 0,
    y: 0
};
let endCoordinates = {
    x: 0,
    y: 0
};

// Array to store the geometries (lines)
const geometries = [];

// Set the initial drawing mode
let mode = 'stroke';

// Grid size and snapping flag
const gridSize = 10;
let snapToGrid = true;

// Variables for select rectangle
let isSelecting = false;
let selectStart = {
    x: 0,
    y: 0
};
let selectEnd = {
    x: 0,
    y: 0
};

// Function to draw the two big lines crossing at the point (0,0)
function drawAxisLines() {
    // Draw vertical line
    ctx.beginPath();
    ctx.moveTo(0, -canvas.height / 2);
    ctx.lineTo(0, canvas.height / 2);
    ctx.stroke();

    // Draw horizontal line
    ctx.beginPath();
    ctx.moveTo(-canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, 0);
    ctx.stroke();
}

// Now you can draw your axis lines
drawAxisLines();


// Function to handle the line drawing
// Function to handle the line drawing
function drawLine(startX, startY, endX, endY) {
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    if (mode === 'stroke') {
        ctx.stroke();
    } else if (mode === 'fill') {
        ctx.fill();
    }

    // If drawingMode is symmetric, draw the symmetric line
    if (drawingMode === 'symmetric') {
        ctx.beginPath();
        ctx.moveTo(-startX, startY);
        ctx.lineTo(-endX, endY);
        if (mode === 'stroke') {
            ctx.stroke();
        } else if (mode === 'fill') {
            ctx.fill();
        }
    }
}

// Function to draw all the stored lines
function drawGeometries() {
    geometries.forEach(geometry => {
        drawLine(geometry.start.x, geometry.start.y, geometry.end.x, geometry.end.y);
    });
}

// Function to draw the grid points
function drawGrid() {
    ctx.fillStyle = '#ccc'; // Grid point color

    for (let x = -canvas.width / 2; x < canvas.width / 2; x += gridSize) {
        for (let y = -canvas.height / 2; y < canvas.height / 2; y += gridSize) {
            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}
drawGrid();

// Function to handle mouse down event
function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const offsetX = e.clientX - rect.left - canvas.width / 2; // Adjust for the translated context
    const offsetY = e.clientY - rect.top - canvas.height / 2; // Adjust for the translated context


    if (isDrawing) return;

    if (!isSelecting) {
        startCoordinates.x = offsetX;
        startCoordinates.y = offsetY;

        if (snapToGrid) {
            startCoordinates.x = Math.round(startCoordinates.x / gridSize) * gridSize;
            startCoordinates.y = Math.round(startCoordinates.y / gridSize) * gridSize;
        }

        isDrawing = true;
    } else {
        selectStart.x = offsetX;
        selectStart.y = offsetY;
    }
}

// Function to handle mouse move event
function handleMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const offsetX = e.clientX - rect.left - canvas.width / 2; // Adjust for the translated context
    const offsetY = e.clientY - rect.top - canvas.height / 2; // Adjust for the translated context


    if (!isDrawing && !isSelecting) return;

    if (isDrawing) {
        endCoordinates.x = offsetX;
        endCoordinates.y = offsetY;

        if (snapToGrid) {
            endCoordinates.x = Math.round(endCoordinates.x / gridSize) * gridSize;
            endCoordinates.y = Math.round(endCoordinates.y / gridSize) * gridSize;
        }

        ctx.clearRect(-(canvas.width / 2), -(canvas.height / 2), canvas.width , canvas.height); // Clear the canvas
        drawGrid(); // Draw the grid points
        drawAxisLines(); // Draw the axis lines
        drawGeometries(); // Redraw the stored lines
        drawLine(startCoordinates.x, startCoordinates.y, endCoordinates.x, endCoordinates.y);
    } else if (isSelecting) {
        selectEnd.x = offsetX;
        selectEnd.y = offsetY;
        ctx.clearRect(-(canvas.width / 2), -(canvas.height / 2), canvas.width , canvas.height); // Clear the canvas
        drawGrid(); // Draw the grid points
        drawAxisLines(); // Draw the axis lines
        drawGeometries(); // Redraw the stored lines
        drawSelectRectangle();
    }
}

// Function to handle mouse up event
function handleMouseUp(e) {
    const rect = canvas.getBoundingClientRect();
    const offsetX = e.clientX - rect.left - canvas.width / 2; // Adjust for the translated context
    const offsetY = e.clientY - rect.top - canvas.height / 2; // Adjust for the translated context

    if (isDrawing) {
        endCoordinates.x = offsetX;
        endCoordinates.y = offsetY;

        if (snapToGrid) {
            endCoordinates.x = Math.round(endCoordinates.x / gridSize) * gridSize;
            endCoordinates.y = Math.round(endCoordinates.y / gridSize) * gridSize;
        }

        ctx.clearRect(-(canvas.width / 2), -(canvas.height / 2), canvas.width , canvas.height); // Clear the canvas
        drawGrid(); // Draw the grid points
        drawAxisLines(); // Draw the axis lines
        drawGeometries(); // Redraw the stored lines
        drawLine(startCoordinates.x, startCoordinates.y, endCoordinates.x, endCoordinates.y);


        if (Math.abs(endCoordinates.x - startCoordinates.x) > 0 || Math.abs(endCoordinates.y - startCoordinates.y) > 0) {
            geometries.push({
                start: {
                    x: startCoordinates.x,
                    y: startCoordinates.y
                },
                end: {
                    x: endCoordinates.x,
                    y: endCoordinates.y
                },
            });
            if (drawingMode === 'symmetric') {
                geometries.push({
                    start: {
                        x: -startCoordinates.x,
                        y: startCoordinates.y
                    },
                    end: {
                        x: -endCoordinates.x,
                        y: endCoordinates.y
                    },
                });
            }            
            console.log('Geometries:', geometries);
        } else {
            endCoordinates = endCoordinates;
        }

        isDrawing = false;
    } else if (isSelecting) {
        selectEnd.x = offsetX;
        selectEnd.y = offsetY;
        ctx.clearRect(-(canvas.width / 2), -(canvas.height / 2), canvas.width , canvas.height); // Clear the canvas
        drawGrid(); // Draw the grid points
        drawAxisLines(); // Draw the axis lines
        drawGeometries(); // Redraw the stored lines
        drawSelectRectangle();

        // Perform selection logic here using the selectStart and selectEnd coordinates
        // You can check which geometries intersect with the select rectangle and perform any desired actions
        const selectedGeometries = getSelectedGeometries(selectStart, selectEnd);
        console.log('Selected Geometries:', selectedGeometries);

        isSelecting = false;
    }
}

// Function to draw the select rectangle
function drawSelectRectangle() {
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.rect(selectStart.x, selectStart.y, selectEnd.x - selectStart.x, selectEnd.y - selectStart.y);
    ctx.stroke();
}

// Function to toggle grid snap
function toggleGridSnap() {
    snapToGrid = !snapToGrid;
}

// Attach event listeners to the canvas
canvas.addEventListener('mousedown', handleMouseDown);
canvas.addEventListener('mousemove', handleMouseMove);
canvas.addEventListener('mouseup', handleMouseUp);

// Attach event listener to the grid snap button
const gridSnapButton = document.getElementById('gridSnapButton');
gridSnapButton.addEventListener('click', toggleGridSnap);

const lineTool = document.getElementById('lineTool');
const rectangleTool = document.getElementById('rectangleTool');

const selectTool = document.getElementById('selectTool');
lineTool.addEventListener('click', () => {
    isSelecting = false;
    isDrawing = true;
    drawingMode = 'line';
});

rectangleTool.addEventListener('click', () => {
    isSelecting = false;
    isDrawing = true;
    drawingMode = 'rectangle';
});


selectTool.addEventListener('click', () => {
    isSelecting = !isSelecting;
});
// Helper function to get selected geometries
function getSelectedGeometries(start, end) {
    const selected = [];
    geometries.forEach(geometry => {
        if (
            geometry.start.x >= start.x &&
            geometry.start.y >= start.y &&
            geometry.end.x <= end.x &&
            geometry.end.y <= end.y
        ) {
            selected.push(geometry);
        }
    });
    return selected;
}