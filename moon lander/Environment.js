class Environment {
    constructor() {
        this.showRender = true;
        // Canvas elements
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Environment settings
        this.enableManualControl = false;
        this.useSpaceStation = false;
        this.landers = [];
        this.ppoLander = null;
        this.targets = [];
        this.asteroids = [];
        this.walls = [];
        this.spaceStations = [];
        this.asteroidsCount = 0;
        this.showfirstN = 0;
        this.targetCount = 1;
        this.cycleTargets = true;
        this.targetRadius = 200;

        // Neural network settings
        this.populationCount = this.enableManualControl ? 1 : 100;
        this.numRadarRays = 5;
        this.startingTimeBonus = 0;

        // Physics settings
        this.gravity = 0.0;
        this.maxThrustPower = 0.1;
        this.maxSideThrustPower = 0.05;
        this.landingSpeed = 1;
        this.maxAngularVelocity = 0.1;
        this.maxRotationAccel = 0.002;
        this.FuelConsumption_thrust = 0.25;
        this.FuelConsumption_rotate = 0.25;
        this.FuelConsumption_sideThrust = 0.25 * 0.5;
        this.maxDistance = 2000;
        this.nnConfigs = {};
        this.resourcesSpots = [];

    }

    generateObjectPositions(positionsCount, minDistance = 500, maxDistance = 5000) {
        let positions = [];

        if (positionsCount == 0)
            return;
        // Add first positions
        let center = {
            position: {
                x: (200 + Math.random() * (this.canvas.width / zoomLevel - 200)),
                y: (200 + Math.random() * (this.canvas.height / zoomLevel / 3 * 2 - 200))
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

    generateAsteroids() {
        this.asteroids = [];
        const asteroidPositions = this.generateObjectPositions(this.asteroidsCount);
        asteroidPositions.forEach(pos => {
            const asteroid = new Asteroid(pos); // Create new asteroid object
            this.asteroids.push(asteroid);
        });
    }

    generateTargets() {
        this.targets = [];
        const targetPositions = this.generateObjectPositions(this.targetCount);
        targetPositions.forEach(pos => {
            this.targets.push({
                ...pos,
                velocity: new Vector(0, 0),
                startAngle: 0
            });
        });
    }

    restart(newPopulation) {
        if (newPopulation) {
            this.landers = newPopulation.map(nn => new Lander(nn));
        } else {
            this.landers.forEach(lander => lander.reset());
        }
    }

    changeAllTarget(position) {
        this.landers.forEach(lander => {
            lander.target = position;
        });
    }

    killAll() {
        this.landers.forEach(lander => lander.kill());
    }

    getNeuralNetworksFromLanders() {
        return this.landers.map(lander => lander.neuralNetwork);
    }

    addNeuralNetworkToLanders(name) {
        const nn = new NeuralNetwork();
        this.landers.forEach(lander => lander.addNeuralNetwork(nn, name));
    }

    addEnemyToLanders() {
        this.landers.forEach(lander => {
            lander.addEnemy(new Enemy());
        });
    }

    drawResources(resourceCounts) {
        this.ctx.save();
        this.resourcesSpots.forEach((spot, spotIndex) => {
            spot.resources.forEach((resource, resourceIndex) => {
                this.ctx.beginPath();
                this.ctx.arc(resource.x + spot.x, resource.y + spot.y, spot.resourceRadius, 0, 2 * Math.PI);
                this.ctx.fillStyle = '#03C03C';
                this.ctx.fill();
                this.ctx.stroke();

                // Draw resource count if harvested
                if (resourceCounts[spotIndex] && resourceCounts[spotIndex][resourceIndex]) {
                    this.ctx.font = '10px Arial';
                    this.ctx.fillStyle = 'black';
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(resourceCounts[spotIndex][resourceIndex], resource.x + spot.x, resource.y + spot.y);
                }
            });
        });
        this.ctx.restore();
    }

    countHarvestedResources() {
        const harvestedResources = {};
        for (let spotIndex in this.ppoLander.harvestedResources) {
            const resources = this.ppoLander.harvestedResources[spotIndex];
            for (let i = 0; i < resources.length; i++) {
                const resourceIndex = resources[i];
                if (!harvestedResources[spotIndex]) harvestedResources[spotIndex] = {};
                if (!harvestedResources[spotIndex][resourceIndex]) {
                    harvestedResources[spotIndex][resourceIndex] = 1;
                } else {
                    harvestedResources[spotIndex][resourceIndex]++;
                }
            }
        }
        return harvestedResources;
    }

    clearCanvas(canvas, context, color) {
        context.fillStyle = color;
        context.fillRect(0, 0, canvas.width, canvas.height);
    }

    updateLanderManually(lander) {
        if (this.keys['ArrowLeft']) lander.rigidBody.angularVelocity -= this.maxRotationAccel;
        if (this.keys['ArrowRight']) lander.rigidBody.angularVelocity += this.maxRotationAccel;
        if (!this.keys['ArrowLeft'] && !this.keys['ArrowRight']) lander.rigidBody.angularVelocity = 0;
        if (this.keys['ArrowUp']) lander.thrust = this.maxThrustPower;
        if (this.keys['ArrowDown']) lander.thrust = -this.maxThrustPower;
        if (!this.keys['ArrowUp'] && !this.keys['ArrowDown']) lander.thrust = 0;
        if (this.keys['Space']) lander.fireLaser();
    }

    drawScore() {
        this.ctx.fillStyle = 'black';
        this.ctx.font = '14px Arial';
        this.ctx.fillText('Score: ' + this.score, this.canvas.width - 100, 20);
    }

    drawText(text, x, y, textAlign = 'left') {
        this.ctx.font = '40px Arial';
        this.ctx.fillStyle = 'white';
        this.ctx.textAlign = textAlign || 'left';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(text, x, y);
    }

    drawTarget(target, size, index) {
        this.drawText(index, target.position.x, target.position.y, index == 'Start' ? 'center' : 'left');
        this.ctx.beginPath();
        this.ctx.arc(target.position.x, target.position.y, size - 50, 0, 2 * Math.PI);
        this.ctx.strokeStyle = 'white';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        if (index == 'Start') this.drawArrow(target.position.x, target.position.y, target.startAngle - Math.PI / 2, size);
    }

    drawArrow(fromX, fromY, angle, length) {
        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.translate(fromX, fromY);
        this.ctx.rotate(angle);
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(length, 0);
        this.ctx.lineTo(length - 20, -20);
        this.ctx.moveTo(length, 0);
        this.ctx.lineTo(length - 20, 20);
        this.ctx.restore();
        this.ctx.stroke();
    }

    zoom(event) {
        event.preventDefault();
        const scaleFactor = 1.1;
        const zoomFactor = event.deltaY < 0 ? scaleFactor : 1 / scaleFactor;
        const mousePosBefore = new Vector(event.clientX / zoomLevel - pan.x, event.clientY / zoomLevel - pan.y);
        zoomLevel *= zoomFactor;
        const mousePosAfter = new Vector(event.clientX / zoomLevel - pan.x, event.clientY / zoomLevel - pan.y);
        pan.x = pan.x + mousePosAfter.x - mousePosBefore.x;
        pan.y = pan.y + mousePosAfter.y - mousePosBefore.y;
    }

    panEvent(event) {
        event.preventDefault();
        pan.x += event.movementX / zoomLevel;
        pan.y += event.movementY / zoomLevel;
    }

    drawFuelBar() {
        const fuelBarHeight = 20;
        const fuelBarWidth = 100;
        const fuelBarPadding = 10;
        const fuelBarX = fuelBarPadding;
        const fuelBarY = fuelBarPadding;
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(fuelBarX, fuelBarY, fuelBarWidth, fuelBarHeight);
        this.ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
        const fuelProgressWidth = (this.landers[0].fuel / 100) * fuelBarWidth;
        this.ctx.fillRect(fuelBarX, fuelBarY, fuelProgressWidth, fuelBarHeight);
        this.ctx.fillStyle = 'white';
        this.ctx.font = '14px Arial';
        this.ctx.fillText('Fuel', fuelBarX + fuelBarWidth / 2 - 10, fuelBarY + 14);
    }

    playThrustSound() {
        if (!this.thrustSound.isPlaying) {
            this.thrustSound.isPlaying = true;
            this.thrustSound.currentTime = 0;
            //this.thrustSound.play();
        }
    }

    stopThrustSound() {
        this.thrustSound.isPlaying = false;
        this.thrustSound.currentTime = 0;
        this.thrustSound.pause();
    }

    playRefuelSound() {
        this.refuelSound.currentTime = 0;
        //this.refuelSound.play();
    }

    drawPoint(point) {
        let color;
        color = 'white';
        this.ctx.beginPath();
        this.ctx.arc(point.x, point.y, 10, 0, 2 * Math.PI, false);
        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.closePath();
    }

    drawLines(points, color = 'white') {
        this.ctx.lineWidth = 5;
        for (let pointList of points) {
            if (pointList.length < 2) continue;
            this.ctx.beginPath();
            this.ctx.moveTo(pointList[0].x, pointList[0].y);
            for (let i = 1; i < pointList.length; i++) {
                this.ctx.lineTo(pointList[i].x, pointList[i].y);
            }
            this.ctx.strokeStyle = color;
            this.ctx.stroke();
        }
    }

    getCheckedItemCount(network) {
        const checkedItemCount = {
            fitness: 0,
            inputs: 0,
            hiddenLayers: 0,
            outputs: 0
        };
        network.fitness.forEach(item => {
            if (item.checked) checkedItemCount.fitness++;
        });
        network.inputs.forEach(item => {
            if (item) checkedItemCount.inputs++;
        });
        network.hiddenLayers.forEach(item => {
            if (item) checkedItemCount.hiddenLayers++;
        });
        network.outputs.forEach(item => {
            if (item) checkedItemCount.outputs++;
        });
        return checkedItemCount;
    }

    checkNodesPerLayer(individualData, config) {
        const nodesPerLayer = individualData.nodesPerLayer;
        const inputsCount = config.inputs.reduce((sum, input) => sum + (input.checked ? input.inputCount : 0), 0);
        const hiddenLayersCount = config.hiddenLayers.length;
        const outputs = config.outputs;
        const outputsCount = outputs.filter(output => output.checked).length;
        if (nodesPerLayer.length !== hiddenLayersCount + 2) return false;
        if (nodesPerLayer[0] !== inputsCount) return false;
        if (nodesPerLayer[nodesPerLayer.length - 1] !== outputsCount) return false;
        for (let i = 1; i <= hiddenLayersCount; i++) {
            if (nodesPerLayer[i] != config.hiddenLayers[i - 1]) return false;
        }
        return true;
    }

    getMatchingNodesPerLayer(config) {
        const inputsCount = config.inputs.reduce((sum, input) => sum + (input.checked ? input.inputCount : 0), 0);
        const hiddenLayersCount = config.hiddenLayers.length;
        const outputs = config.outputs;
        const outputsCount = outputs.filter(output => output.checked).length;
        const nodesPerLayer = [inputsCount];
        for (let i = 0; i < hiddenLayersCount; i++) {
            nodesPerLayer.push(Number(config.hiddenLayers[i]));
        }
        nodesPerLayer.push(outputsCount);
        return nodesPerLayer;
    }

    getSceneNames() {
        let list = [];
        for (const [key, value] of Object.entries(localStorage)) {
            if (key.startsWith('scene_')) {
                list.push(key.replace('scene_', ''));
            }
        }
        return list;
    }

    loadSceneNames() {
        let scenes = this.getSceneNames();
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

    loadLandersGA() {
        const config = JSON.parse(localStorage.getItem('nnConfig'));
        if (config && config.networks) {
            config.networks.forEach(network => {
                this.nnConfigs[network.name] = network;
                for (let fitnessOnEvent of network.fitnessOnEvents) {
                    network.fitnessOnEvents[fitnessOnEvent.name] = fitnessOnEvent.value;
                }
                let fileIndex = GeneticAlgorithm.getMaxFileIndex(network.name);
                let fileName = 'NeuralNetwork_' + network.name + "_" + fileIndex;
                let populationData = JSON.parse(localStorage.getItem(fileName));
                if (populationData) {
                    populationData.forEach((individualData, i) => {
                        let lander = this.landers[i];
                        if (!lander) lander = new Lander(this.targets[0].position.x, this.targets[0].position.y + 1, i, this.targets[0].startAngle);
                        Object.setPrototypeOf(individualData, NeuralNetwork2.prototype);
                        if (!this.checkNodesPerLayer(individualData, network)) {
                            console.error('The number of nodes per layer in the saved NeuralNetwork does not match the number of nodes per layer in the config.');
                            return false;
                        }
                        lander.addNeuralNetwork(individualData, network.name);
                        if (!this.landers[i]) this.landers.push(lander);
                        individualData.weights = individualData.weights.map(weightMatrix => Matrix.map(weightMatrix, x => x));
                        individualData.biases = individualData.biases.map(biasMatrix => Matrix.map(biasMatrix, x => x));
                    });
                } else {
                    for (let i = 0; i < this.populationCount; i++) {
                        let nodesPerLayer = this.getMatchingNodesPerLayer(network);
                        let lander = this.landers[i];
                        if (!lander) lander = new Lander(this.targets[0].position.x, this.targets[0].position.y + 1, i, this.targets[0].startAngle);
                        lander.addNeuralNetwork(new NeuralNetwork2(nodesPerLayer), network.name);
                        if (!this.landers[i]) this.landers.push(lander);
                    }
                }
                if (network.isDefault) this.setLandersNeuralNetwork(network.name);
            });
        }
        return true;
    }

    getMaxFileIndex(actionName, startsWith = 'NeuralNetwork_') {
        let maxIndex = -1;
        for (const [key, value] of Object.entries(localStorage)) {
            if (key.startsWith(startsWith + actionName + '_')) {
                let index = parseInt(key.replace(startsWith + actionName + '_', ''));
                if (index > maxIndex) {
                    maxIndex = index;
                }
            }
        }
        return Number(maxIndex);
    }

    loadppoLander() {
        const config = JSON.parse(localStorage.getItem('nnConfig'));
        if (config && config.networks) {
            config.networks.forEach(network => {
                this.nnConfigs[network.name] = network;
                for (let fitnessOnEvent of network.fitnessOnEvents) {
                    network.fitnessOnEvents[fitnessOnEvent.name] = fitnessOnEvent.value;
                }
                let fileIndex = this.getMaxFileIndex(network.name, "PPO_");
                let fileName = 'PPO_' + network.name + "_" + fileIndex;
                let populationData; // = JSON.parse(localStorage.getItem(fileName));
                if (populationData) {
                    Object.setPrototypeOf(individualData, PPOAgent.prototype);
                    if (!this.checkNodesPerLayer(individualData, network)) {
                        console.error('The number of nodes per layer in the saved NeuralNetwork does not match the number of nodes per layer in the config.');
                        return false;
                    }
                    if (!this.ppoLander) this.ppoLander = new Lander(this.targets[0].position.x, this.targets[0].position.y + 1, i, this.targets[0].startAngle);
                    this.ppoLander.addPPOAgent(individualData, network.name);
                    if (!this.landers[i]) this.landers.push(this.ppoLander);
                    individualData.weights = individualData.weights.map(weightMatrix => Matrix.map(weightMatrix, x => x));
                    individualData.biases = individualData.biases.map(biasMatrix => Matrix.map(biasMatrix, x => x));
                } else {
                    let nodesPerLayer = this.getMatchingNodesPerLayer(network);
                    if (!this.ppoLander) this.ppoLander = new Lander(this.targets[0].position.x, this.targets[0].position.y + 1, 1, this.targets[0].startAngle);
                    let spaceConfig = {
                        actionSpace: {
                            'class': 'Box',
                            'shape': [nodesPerLayer[nodesPerLayer.length - 1]]
                        },
                        observationSpace: {
                            'shape': [nodesPerLayer[0]]
                        }
                    }
                    //this.ppoLander.addPPOAgent(new PPO(this, spaceConfig), network.name);
                    this.ppoLander.addPPOAgent(new PPO(nodesPerLayer[0], nodesPerLayer[nodesPerLayer.length - 1]), network.name);
                }
                if (network.isDefault)
                    this.ppoLander.setActivePPOAgent(network.name);
                // this.setLandersNeuralNetwork(network.name);
            });
        }
        return true;
    }

    setLandersNeuralNetwork(name) {
        for (let i = 0; i < this.populationCount; i++) {
            this.landers[i].setActiveNeuralNetwork(name);
        }
    }

    changeAllTarget(position) {
        this.landers.forEach(lander => {
            lander.target = position;
        });
    }

    killAll() {
        this.landers.forEach(lander => lander.kill());
    }

    restart(newPopulation) {
        if (newPopulation) {
            for (let i = 0; i < newPopulation.length; i++) {
                this.landers[i].neuralNetwork = newPopulation[i];
                this.landers[i].reset();
            }
        } else {
            for (let i = 0; i < this.landers.length; i++) {
                this.landers[i].reset();
            }
        }
    }

    reset() {
        return this.ppoLander.step();
    }


    async step(action) {
        let stepData = [0, 0, 0]
        if (this.showRender) {
            // Clear canvas
            this.clearCanvas(this.canvas, this.ctx, '#03002e');

            // Set up canvas transform
            this.ctx.save();
            this.ctx.scale(zoomLevel, zoomLevel);
            this.ctx.translate(pan.x, pan.y);

            // Draw space stations
            this.spaceStations.forEach(spaceStation => spaceStation.draw());

            // Get harvested resource counts
            const harvestedResources = this.countHarvestedResources();
            // Draw resources
            this.drawResources(harvestedResources);
        }



        // Update and draw asteroids
        this.asteroids.forEach(asteroid => {
            asteroid.update();
            asteroid.getPolygon();
            if (this.showRender)
                asteroid.draw();
        });

        // Get ppoLander (first lander)

        // Update and draw ppoLander
        if (!this.ppoLander.ppoAgent.isDead) {
            this.ppoLander.checkTargetModes();
            this.ppoLander.checkTargets();
            if (this.enableManualControl)
                this.updateLanderManually(this.ppoLander);
            else
                stepData = this.ppoLander.step(action);

            if (this.showRender)
                this.ppoLander.drawLander();
            this.ppoLander.checkDocking();
            this.ppoLander.handleCollision();
        } else {
            this.ppoLander.update();
            this.ppoLander.calculateFitness();
        }

        // Draw targets
        this.targets.forEach((target, i) => this.drawTarget(target, this.targetRadius, i));

        // Draw walls
        if (this.showRender)
            this.drawLines(this.walls);

        // Draw score
        if (this.showRender)
            this.drawScore();

        // Restore canvas
        if (this.showRender)
            this.ctx.restore();

        // Increment frame count
        this.frameCount++;

        await new Promise(resolve => setTimeout(resolve, 1));

        return stepData;
    }

}