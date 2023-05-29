class NeuralNetwork {
    constructor(inputSize, hiddenSizes, outputSize) {
        this.layers = [];
        this.bias = [];
        let previousSize = inputSize;
        this.inputSize = inputSize;
        this.hiddenSizes = hiddenSizes;
        this.outputSize = outputSize;

        // Create hidden layers and their biases
        for (let hiddenSize of hiddenSizes) {
            this.layers.push(Array.from({
                length: previousSize * hiddenSize
            }, () => NeuralNetwork.random()));
            this.bias.push(Array.from({
                length: hiddenSize
            }, () => NeuralNetwork.random()));
            previousSize = hiddenSize;
        }

        // Create output layer and its bias
        this.layers.push(Array.from({
            length: previousSize * outputSize
        }, () => NeuralNetwork.random()));
        this.bias.push(Array.from({
            length: outputSize
        }, () => NeuralNetwork.random()));

        this.isDead = false;
        this.currentFitness = 0;
    }

    static random() {
        return Math.random() * 2 - 1;
    }

    static sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }

    predict(input) {
        let values = input;
        for (let layerIndex = 0; layerIndex < this.layers.length; layerIndex++) {
            const layer = this.layers[layerIndex];
            const bias = this.bias[layerIndex];
            const nextValues = Array(bias.length).fill(0);

            for (let neuronIndex = 0; neuronIndex < bias.length; neuronIndex++) {
                for (let valueIndex = 0; valueIndex < values.length; valueIndex++) {
                    nextValues[neuronIndex] += values[valueIndex] * layer[neuronIndex * values.length + valueIndex];
                }
                nextValues[neuronIndex] = NeuralNetwork.sigmoid(nextValues[neuronIndex] + bias[neuronIndex]);
            }

            values = nextValues;
        }

        return values;
    }

    crossover(partner) {
        const child = new NeuralNetwork(this.inputSize, this.hiddenSizes, this.outputSize);

        function multiPointCrossover(parent1Genes, parent2Genes) {
            let newGenes = [];
            let crossoverPoints = [Math.floor(parent1Genes.length / 3), Math.floor(2 * parent1Genes.length / 3)];

            for (let i = 0; i < parent1Genes.length; i++) {
                if (i < crossoverPoints[0] || (i >= crossoverPoints[1] && i < parent1Genes.length)) {
                    newGenes.push(parent1Genes[i]);
                } else {
                    newGenes.push(parent2Genes[i]);
                }
            }
            return newGenes;
        }

        child.layers = this.layers.map((layer, layerIndex) =>
            multiPointCrossover(layer, partner.layers[layerIndex]));
        child.bias = this.bias.map((biasLayer, layerIndex) =>
            multiPointCrossover(biasLayer, partner.bias[layerIndex]));

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

        this.layers = this.layers.map(layer => layer.map(mutateGene));
        this.bias = this.bias.map(layer => layer.map(mutateGene));
    }

    saveGenes() {
        const genes = {
            layers: this.layers,
            bias: this.bias
        };

        const json = JSON.stringify(genes);
        localStorage.setItem('neuralNetworkGenes', json);
    }

    loadGenes() {
        const json = localStorage.getItem('neuralNetworkGenes');
        if (json) {
            const genes = JSON.parse(json);
            this.layers = genes.layers;
            this.bias = genes.bias;
        } else {
            console.error('No saved genes found in localStorage.');
        }
    }

    addInputNeuron() {
        // Increase input size by 1
        this.inputSize += 1;

        // Initialize new neuron weights with low values
        const newNeuronWeights = Array.from({
                length: this.hiddenSizes[0]
            }, () =>
            NeuralNetwork.random() * 0.1
        );

        // Insert new neuron weights into the first layer
        this.layers[0] = [
            ...this.layers[0],
            ...newNeuronWeights
        ];

        // Initialize new neuron bias with a low value
        const newNeuronBias = NeuralNetwork.random() * 0.1;

        // Insert new neuron bias into the first layer bias
        this.bias[0].push(newNeuronBias);

        // Adjust subsequent layers to accommodate the new neuron
        for (let i = 1; i < this.layers.length; i++) {
            const layerSize = this.layers[i].length / this.layers[i - 1].length;
            const newLayerWeights = Array.from({
                    length: layerSize
                }, () =>
                NeuralNetwork.random() * 0.1
            );
            this.layers[i] = [
                ...this.layers[i],
                ...newLayerWeights
            ];
            this.bias[i].push(NeuralNetwork.random() * 0.1);
        }
    }


}