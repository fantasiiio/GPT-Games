class NeuralNetwork2 {
    constructor(nodesPerLayer) {
        // nodesPerLayer is an array like [inputNodes, hiddenNodes1, hiddenNodes2, ..., outputNodes]
        this.nodesPerLayer = nodesPerLayer;
        this.numLayers = nodesPerLayer.length;
        this.learningRate = 0.1;
        this.weights = new Array(this.numLayers - 1);
        this.biases = new Array(this.numLayers - 1);

        for (let i = 0; i < this.numLayers - 1; i++) {
            this.weights[i] = new Matrix(nodesPerLayer[i + 1], nodesPerLayer[i]);
            this.weights[i].randomize();
            this.biases[i] = new Matrix(nodesPerLayer[i + 1], 1);
            this.biases[i].randomize();
        }

        this.isDead = false;
        this.currentFitness = 0;
    }

    // Fisher-Yates Shuffle Algorithm to shuffle indices
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    trainBatch(inputArrays, targetArrays) {
        // Randomly shuffle the data
        let shuffledIndices = [...Array(inputArrays.length).keys()];
        shuffledIndices = this.shuffleArray(shuffledIndices);

        for (let i = 0; i < inputArrays.length; i++) {
            // Select a random instance
            let idx = shuffledIndices[i];
            let inputArray = inputArrays[idx];
            let targetArray = targetArrays[idx];

            // Convert input and target arrays to matrices
            let inputs = Matrix.fromArray(inputArray);
            let targets = Matrix.fromArray(targetArray);

            // Array to hold output of each layer
            let layerOutputs = [inputs];
            // Array to hold gradients of each layer
            let gradients = [];

            // Feed forward
            for (let j = 0; j < this.numLayers - 1; j++) {
                let layerInput = layerOutputs[j];
                let layerOutput = Matrix.multiply(this.weights[j], layerInput);
                layerOutput.add(this.biases[j]);
                layerOutput.map(this.sigmoid);
                layerOutputs.push(layerOutput);
            }

            // Calculate output layer errors
            let outputErrors = Matrix.subtract(targets, layerOutputs[this.numLayers - 1]);

            // Backpropagation
            for (let j = this.numLayers - 2; j >= 0; j--) {
                let layerOutputsTransposed = Matrix.transpose(layerOutputs[j]);
                let layerWeightsDeltas = Matrix.multiply(outputErrors, layerOutputsTransposed);

                // Adjust weights and biases
                this.weights[j].add(layerWeightsDeltas);
                this.biases[j].add(outputErrors);

                // Calculate next layer errors if not at input layer
                if (j > 0) {
                    let weightsTransposed = Matrix.transpose(this.weights[j]);
                    outputErrors = Matrix.multiply(weightsTransposed, outputErrors);

                    // Calculate layer gradients
                    let layerGradients = Matrix.map(layerOutputs[j], this.sigmoidDerivative);
                    layerGradients.multiply(outputErrors);
                    layerGradients.multiply(this.learningRate);
                    gradients[j] = layerGradients;
                }
            }
        }
    }



    predict(inputArray) {
        let inputs = Matrix.fromArray(inputArray);
        let layerOutputs = [inputs];

        for (let i = 0; i < this.numLayers - 1; i++) {
            let weights = this.weights[i];
            let biases = this.biases[i];

            let layerInput = layerOutputs[i];
            let layerOutput = Matrix.multiply(weights, layerInput);
            layerOutput.add(biases);
            layerOutput.map(this.sigmoid);
            layerOutputs.push(layerOutput);
        }
        let outputs = layerOutputs[this.numLayers - 1].toArray();
        return outputs;
    }



    sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }

    sigmoidDerivative(y) {
        // y is assumed to be the sigmoid function already applied to x
        return y * (1 - y);
    }

    crossover(partner) {
        const child = new NeuralNetwork2(this.nodesPerLayer);

        function multiPointCrossover(parent1Matrix, parent2Matrix) {
            const rows = parent1Matrix.rows;
            const cols = parent1Matrix.cols;
            const newMatrix = new Matrix(rows, cols);

            const crossoverPoints = [Math.floor(rows / 3), Math.floor(2 * rows / 3)];

            for (let i = 0; i < rows; i++) {
                for (let j = 0; j < cols; j++) {
                    if (i < crossoverPoints[0] || (i >= crossoverPoints[1] && i < rows)) {
                        newMatrix.data[i][j] = parent1Matrix.data[i][j];
                    } else {
                        newMatrix.data[i][j] = parent2Matrix.data[i][j];
                    }
                }
            }
            return newMatrix;
        }

        child.weights = this.weights.map((weightMatrix, layerIndex) =>
            multiPointCrossover(weightMatrix, partner.weights[layerIndex]));
        child.biases = this.biases.map((biasMatrix, layerIndex) =>
            multiPointCrossover(biasMatrix, partner.biases[layerIndex]));

        return child;
    }



    mutate(mutationRate) {
        function gaussianRandom() {
            let u = 0,
                v = 0;
            while (u === 0) u = Math.random(); // Converting [0,1) to (0,1)
            while (v === 0) v = Math.random();
            return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        }

        function mutateGene(gene) {
            if (Math.random() < mutationRate) {
                const mutationStrength = 0.5;
                return gene + gaussianRandom() * mutationStrength;
            } else {
                return gene;
            }
        }

        this.weights = this.weights.map(weightMatrix =>
            weightMatrix.map(mutateGene));
        this.biases = this.biases.map(biasMatrix =>
            biasMatrix.map(mutateGene));
    }


    addInputNeuron() {
        // Increase the number of input nodes by 1
        this.nodesPerLayer[0] += 1;

        // Create a new weight matrix for the new input neuron
        const newNeuronWeights = new Matrix(this.nodesPerLayer[1], 1);
        newNeuronWeights.randomize();
        newNeuronWeights.multiply(0.1); // Initialize new neuron weights with low values

        // Add the new neuron weights to the first layer weights
        this.weights[0] = Matrix.appendColumn(this.weights[0], newNeuronWeights);

        // Create a new bias for the new input neuron
        const newNeuronBias = new Matrix(1, 1);
        newNeuronBias.randomize();
        newNeuronBias.multiply(0.1); // Initialize new neuron bias with a low value

        // Add the new neuron bias to the first layer biases
        this.biases[0] = Matrix.appendRow(this.biases[0], newNeuronBias);
    }

}