class Gene {
    static random() {
        return Math.random() * 2 - 1;
    }
}

class NeuralNetwork {
    constructor(inputSize, hiddenSize, outputSize) {
        this.inputLayer = Array.from({
            length: inputSize * hiddenSize
        }, () => Gene.random());
        this.hiddenLayer = Array.from({
            length: hiddenSize * outputSize
        }, () => Gene.random());
        this.biasHidden = Array.from({
            length: hiddenSize
        }, () => Gene.random());
        this.biasOutput = Array.from({
            length: outputSize
        }, () => Gene.random());
        this.isDead = false;
        this.currentFitness = 0;
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
                const mutationStrength = 0.1; // Adjust this value to control the magnitude of mutation
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

class GeneticAlgorithm {
    constructor(population, inputSize, hiddenSize, outputSize, mutationRate, maxGenerations,
        expectedOutputs) {
        this.populationSize = population.length;
        this.population = population;
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        this.mutationRate = mutationRate;
        this.maxGenerations = maxGenerations;
        this.expectedOutputs = expectedOutputs;
    }

    allIndividualsDead() {
        return this.population.every(neuralNetwork => neuralNetwork.isDead);
    }

    run(callback) {

        const runGeneration = (generation) => {
            if (generation >= this.maxGenerations) {
                callback(this.population);
                return;
            }

            const checkPopulation = () => {
                if (this.allIndividualsDead()) {
                    this.population.sort((a, b) => b.currentFitness - a.currentFitness);
                    console.log(`Génération ${generation}: Meilleure fitness = ${this.population[0].currentFitness}`);

                    this.population = this.createNewGeneration();
                    runGeneration(generation + 1);
                } else {
                    requestAnimationFrame(checkPopulation);
                }
            };

            requestAnimationFrame(checkPopulation);
        };

        runGeneration(0);
    }



    selectParents() {
        let selectOne = () => {
            const tournamentSize = 3; // Adjust this value to control the selection pressure
            const selected = [];
            for (let i = 0; i < tournamentSize; i++) {
                const randomIndex = Math.floor(Math.random() * this.population.length);
                selected.push(this.population[randomIndex]);
            }
            return selected.sort((a, b) => b.currentFitness - a.currentFitness)[0];
        }

        const parent1 = selectOne();
        const parent2 = selectOne();

        return [parent1, parent2];
    }


    createNewGeneration() {
        const newGeneration = [];
        for (let i = 0; i < this.population.length; i++) {
            const parents = this.selectParents();
            const childNetwork = parents[0].crossover(parents[1]);
            childNetwork.mutate(this.mutationRate);
            newGeneration.push(childNetwork);
        }
        return newGeneration;
    }

}

function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    NeuralNetwork.loadGenes(file, (neuralNetwork) => {
        // Use the loaded neural network
        console.log('Loaded neural network:', neuralNetwork);
    });
}

// // Exemple d'utilisation
// const populationSize = 100;
// const inputSize = 5;
// const hiddenSize = 5;
// const outputSize = 1;
// const mutationRate = 0.1;
// const maxGenerations = 50;
// const inputs = [
//     [0],
//     [0.5],
//     [1],
//     [1.5],
//     [2]
// ];
// const expectedOutputs = [0];

// const geneticAlgorithm = new GeneticAlgorithm(populationSize, inputSize, hiddenSize, outputSize,
//     mutationRate,
//     maxGenerations, inputs, expectedOutputs);

// geneticAlgorithm.run((bestNeuralNetwork) => {
//     console.log('Meilleur réseau de neurones:', bestNeuralNetwork);
//     const simulatedOutputs = bestNeuralNetwork.simulate(inputs);
//     console.log('Fitness:', fitness(simulatedOutputs, expectedOutputs));
// });