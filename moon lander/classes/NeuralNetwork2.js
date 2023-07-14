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
        this.layerOutputs = [];
        this.isDead = false;
        this.currentFitness = 0;
        this.generationNumber = 1;
    }

    parameters() {
        const params = [];

        // Add weights and biases for each layer 
        for (let i = 0; i < this.numLayers - 1; i++) {
            params.push(this.weights[i].concat(this.biases[i]))
        }

        return params;
    }
    
    predict(inputArray) {
        let inputs = Matrix.fromArray(inputArray);
        this.layerOutputs = [inputs];

        for (let i = 0; i < this.numLayers - 1; i++) {
            let weights = this.weights[i];
            let biases = this.biases[i];

            let layerInput = this.layerOutputs[i];
            let layerOutput = Matrix.multiply(weights, layerInput);
            layerOutput.add(biases);
            if (i == this.numLayers - 2 && this.nodesPerLayer[this.nodesPerLayer.length - 1] > 1){
                // Apply softmax on the final layer if there is more than 1 node
                let outputArray = Matrix.transpose(layerOutput).getRow(0).data;
                let softmaxOutput = softmax(outputArray);
                layerOutput = Matrix.fromArray([softmaxOutput]);  // convert it back to Matrix
            } else {
                layerOutput.map(this.softplus);
            }
            this.layerOutputs.push(layerOutput);
        }
        return Matrix.transpose(this.layerOutputs[this.numLayers - 1]).getRow(0).data;
    }

    softmax(arr) {
        // Calculate the exponentials
        const exps = arr.map(val => Math.exp(val));
    
        // Calculate the sum of the exponentials
        const sum = exps.reduce((a, b) => a + b, 0);
    
        // Return the softmax values (each value divided by the sum of all values)
        return exps.map(val => val / sum);
    }
    

    softplus(x) {
        if (x instanceof Matrix) {
            let result = new Matrix(x.rows, x.cols);
            for (let i = 0; i < x.rows; i++) {
                for (let j = 0; j < x.cols; j++) {
                    result.data[i][j] = Math.log(1 + Math.exp(x.data[i][j]))
                }
            }
            return result;
        } else {
            return Math.log(1 + Math.exp(x));
        }
    }

    sigmoid(x) {
        if (x instanceof Matrix) {
            let result = new Matrix(x.rows, x.cols);
            for (let i = 0; i < x.rows; i++) {
                for (let j = 0; j < x.cols; j++) {
                    result.data[i][j] = 1 / (1 + Math.exp(-x.data[i][j]));
                }
            }
            return result;
        } else {
            return 1 / (1 + Math.exp(-x));
        }
    }

    sigmoidPrime(x) {
        const sigmoidX = this.sigmoid(x);
        if (sigmoidX instanceof Matrix) {
            let result = new Matrix(sigmoidX.rows, sigmoidX.cols);
            for (let i = 0; i < sigmoidX.rows; i++) {
                for (let j = 0; j < sigmoidX.cols; j++) {
                    result.data[i][j] = sigmoidX.data[i][j] * (1 - sigmoidX.data[i][j]);
                }
            }
            return result;
        } else {
            return sigmoidX * (1 - sigmoidX);
        }
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



}