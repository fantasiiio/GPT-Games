class GeneticAlgorithm {
    constructor(population, inputSize, hiddenSize, outputSize, mutationRate, maxGenerations,
        expectedOutputs, onNewGenerationCreatedFn) {
        this.populationSize = population.length;
        this.population = population;
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        this.mutationRate = mutationRate;
        this.maxGenerations = maxGenerations;
        this.expectedOutputs = expectedOutputs;
        this.onNewGenerationCreatedFn = onNewGenerationCreatedFn;
        this.bestIndividual = null;
    }

    allIndividualsDead() {
        return this.population.every(neuralNetwork => neuralNetwork.isDead || neuralNetwork.isCompleted);
    }

    run(callback) {

        const runGeneration = (generation) => {
            if (generation >= this.maxGenerations) {
                callback(this.population);
                return;
            }

            const checkPopulation = () => {
                // find best population based on it's currentFitness that is not dead
                this.bestIndividual = null;
                for (let i = 0; i < this.population.length; i++) {
                    const neuralNetwork = this.population[i];
                    neuralNetwork.isBest = false;
                    if (!neuralNetwork.isDead) {
                        if(neuralNetwork.currentFitness > ((this.bestIndividual || {}).currentFitness || 0)) {
                            this.bestIndividual = neuralNetwork;
                        }
                    }
                }                   
                if(this.bestIndividual)
                    this.bestIndividual.isBest = true;
                
                if (this.allIndividualsDead()) {
                    this.population.sort((a, b) => b.currentFitness - a.currentFitness);
                    console.log(`Génération ${generation}: Meilleure fitness = ${this.population[0].currentFitness}`);

                    this.population = this.createNewGeneration();
                    this.onNewGenerationCreatedFn(this.population);
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
                const randomIndex = Math.floor(Math.random() * Math.max(10, this.population.length * 0.1));
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