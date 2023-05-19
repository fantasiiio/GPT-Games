class NeuralNetwork {
    constructor(inputSize, hiddenSize, outputSize) {
        this.inputLayer = Array.from({
            length: inputSize * hiddenSize
        }, () => NeuralNetwork.random());
        this.hiddenLayer = Array.from({
            length: hiddenSize * outputSize
        }, () => NeuralNetwork.random());
        this.biasHidden = Array.from({
            length: hiddenSize
        }, () => NeuralNetwork.random());
        this.biasOutput = Array.from({
            length: outputSize
        }, () => NeuralNetwork.random());
        this.isDead = false;
        this.currentFitness = 0;
    }

    static random() {
        return Math.random() * 2 - 1;
    }

    static sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }

    apply(input) {
        const inputSize = input.length;
        const hiddenSize = this.biasHidden.length;
        const outputSize = this.biasOutput.length;

        const hidden = Array(hiddenSize).fill(0);
        const output = Array(outputSize).fill(0);
        if(this.isDead)
            return output;
            
        for (let h = 0; h < hiddenSize; h++) {
            for (let i = 0; i < inputSize; i++) {
                hidden[h] += input[i] * this.inputLayer[h * inputSize + i];
            }
            hidden[h] = NeuralNetwork.sigmoid(hidden[h] + this.biasHidden[h]);
        }

        for (let o = 0; o < outputSize; o++) {
            for (let h = 0; h < hiddenSize; h++) {
                output[o] += hidden[h] * this.hiddenLayer[o * hiddenSize + h];
            }
            output[o] = NeuralNetwork.sigmoid(output[o] + this.biasOutput[o]);
        }

        return output;
    }


    crossover(partner) {
        const child = new NeuralNetwork(this.inputSize, this.hiddenSize, this.outputSize);

        function uniformCrossover(parent1Genes, parent2Genes) {
            return parent1Genes.map((gene, index) => {
                return Math.random() < 0.5 ? gene : parent2Genes[index];
            });
        }

        child.inputLayer = uniformCrossover(this.inputLayer, partner.inputLayer);
        child.hiddenLayer = uniformCrossover(this.hiddenLayer, partner.hiddenLayer);
        child.biasHidden = uniformCrossover(this.biasHidden, partner.biasHidden);
        child.biasOutput = uniformCrossover(this.biasOutput, partner.biasOutput);

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
                const mutationStrength = 0.5; // Adjust this value to control the magnitude of mutation
                return gene + gaussianRandom() * mutationStrength;
            } else {
                return gene;
            }
        }

        this.inputLayer = this.inputLayer.map(mutateGene);
        this.hiddenLayer = this.hiddenLayer.map(mutateGene);
        this.biasHidden = this.biasHidden.map(mutateGene);
        this.biasOutput = this.biasOutput.map(mutateGene);
    }

    saveGenes() {
        const genes = {
            inputLayer: this.inputLayer,
            hiddenLayer: this.hiddenLayer,
            biasHidden: this.biasHidden,
            biasOutput: this.biasOutput
        };

        const json = JSON.stringify(genes);
        localStorage.setItem('neuralNetworkGenes', json);
    }

    loadGenes() {
        const json = localStorage.getItem('neuralNetworkGenes');
        if (json) {
            const genes = JSON.parse(json);
            this.inputLayer = genes.inputLayer;
            this.hiddenLayer = genes.hiddenLayer;
            this.biasHidden = genes.biasHidden;
            this.biasOutput = genes.biasOutput;
        } else {
            console.error('No saved genes found in localStorage.');
        }
    }
}

