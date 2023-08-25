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
        this.generationCount = 0;
    }

    allIndividualsDead() {
        return this.population.every(neuralNetwork => neuralNetwork.isDead || neuralNetwork.isCompleted);
    }

    run(callback) {

        const runGeneration = (generation) => {
            this.generationCount = generation;
            if (generation >= this.maxGenerations) {
                callback(this.population);
                return;
            }

            const checkPopulation = () => {
                if(!isSimulationRunning){
                    requestAnimationFrame(checkPopulation);  
                    return;
                }          

                let copyArray = [...this.population];
                copyArray.sort((a, b) => b.currentFitness - a.currentFitness);
                
                this.bestIndividual = null;
                for (let i = 0; i < copyArray.length; i++) {
                    const neuralNetwork = copyArray[i];
                    neuralNetwork.positionNumber = i + 1;
                    if (i == 0) {
                        this.bestIndividual = neuralNetwork;
                        neuralNetwork.isBest = true;
                    } else {
                        neuralNetwork.isBest = false;
                    }
                }

                if (!this.restart && !this.bestSolutionFound) {
                    if (this.allIndividualsDead()) {
                        //this.savePopulation();
                        console.log(`G\xE9n\xE9ration ${this.generationCount}: Meilleure fitness = ${this.bestIndividual.currentFitness}`);

                        this.population = this.createNewGeneration();
                        this.onNewGenerationCreatedFn(this.population);
                        runGeneration(this.generationCount + 1);
                    } else {
                        requestAnimationFrame(checkPopulation);
                    }
                } else {
                    this.restart = false;
                    requestAnimationFrame(checkPopulation);
                }

            };
            requestAnimationFrame(checkPopulation);
        };

        runGeneration(0);
    }



    selectParents() {
        let selectOne = () => {
            const tournamentSize = 5; // Adjust this value to control the selection pressure
            const selected = [];
            for (let i = 0; i < tournamentSize; i++) {
                const randomIndex = Math.floor(Math.random() * this.population.length - 1);
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
        if (this.population.length < 3)
            return this.population;

        for (let i = 0; i < this.population.length; i++) {
            const parents = this.selectParents();
            const childNetwork = parents[0].crossover(parents[1]);
            childNetwork.mutate(this.mutationRate);
            newGeneration.push(childNetwork);
        }
        return newGeneration;
    }

    static getMaxFileIndex(actionName){
        let maxIndex = -1;
        for (const [key, value] of Object.entries(localStorage)) {
            if (key.startsWith('NeuralNetwork_' + actionName + '_')) {
                let index = parseInt(key.replace('NeuralNetwork_' + actionName + '_', ''));
                if (index > maxIndex) {
                    maxIndex = index;
                }
            }
        }  
        return Number(maxIndex);      
    }

    savePopulation(actionName) {
        //localStorage.setItem('bestSolutionFound', confirm('Est-ce que l\'\xC9volution est termin\xE9e?'));
        const json = JSON.stringify(this.population);
        let maxIndex = GeneticAlgorithm.getMaxFileIndex(actionName);
        localStorage.setItem('NeuralNetwork_' + actionName + '_' + (maxIndex+1), json);
    }

    loadPopulation2() {
        let generationJson;
        let maxGenerationNumber = 0;

        if (generationJson && confirm('Charger la population?')) {
            this.generationCount = maxGenerationNumber;


            this.restart = true;
            this.bestSolutionFound = localStorage.getItem('bestSolutionFound') === 'true';
            const population = JSON.parse(generationJson);
            for (let i = 0; i < Math.min(population.length, this.population.length); i++) {
                Object.assign(this.population[i], population[i]);

                this.population[i].weights = this.population[i].weights.map(weightMatrix => Matrix.map(weightMatrix, x => x));
                this.population[i].biases = this.population[i].biases.map(biasMatrix => Matrix.map(biasMatrix, x => x));
                // this.population[i].addInputNeuron();
                // this.population[i].addInputNeuron();
                // this.population[i].addInputNeuron();
            }
            this.onNewGenerationCreatedFn(this.population);
        }
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