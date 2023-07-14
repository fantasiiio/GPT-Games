class PPOAgent {
    constructor(nodesPerLayer) {
        this.currentFitness = 0;
        this.nodesPerLayer = nodesPerLayer;
        this.actionSize = nodesPerLayer[nodesPerLayer.length - 1];

        // Hyperparameters
        this.gamma = 0.99;
        this.lambda = 0.95;
        this.epsilon = 0.2;
        this.entropyCoeff = 0.01;
        this.actorLR = 2e-4;
        this.criticLR = 1e-3;
        this.maxGradNorm = 0.5;

        // Actor and critic networks
        nodesPerLayer[nodesPerLayer.length - 1] = 2 * this.actionSize;
        this.actor = new NeuralNetwork2(nodesPerLayer);

        nodesPerLayer[nodesPerLayer.length - 1] = this.actionSize;
        nodesPerLayer[nodesPerLayer.length - 1] = 1;
        this.critic = new NeuralNetwork2(nodesPerLayer);

        // Optimizers
        this.actorOptimizer = new AdamOptimizer(this.actor.parameters(), this.actorLR);
        this.criticOptimizer = new AdamOptimizer(this.critic.parameters(), this.criticLR);
    }

    sample(arr, size) {
        let indices = [];
        while (indices.length < size) {
            let index = Math.floor(Math.random() * arr.length);
            if (!indices.includes(index)) indices.push(index);
        }
        return indices.map(i => arr[i]);
    }

    getAction(state) {
        // Actor predicts action 
        const action = this.actor.predictStds(state);
        return action;
    }



    calculateMean(array) {
        const sum = array.reduce((a, b) => a + b, 0);
        const mean = sum / array.length;
        return mean;
    }

    train2(episode) {
        // Get experiences from episode
        let states = [];
        let actions = [];
        let rewards = [];
        let nextStates = [];
        let dones = [];
        let values = [];
        for (let step of episode) {
            states.push(step.state);
            actions.push(step.action);
            rewards.push(step.reward);
            nextStates.push(step.nextState);
            dones.push(step.done);

            // Critic predicts state value 
            const value = this.critic.predict(step.state)[0][0];
            values.push(value);
        }
        // Critic predicts state values

        // Compute advantages and targets
        const [advantages, targets] = this.estimateAdvantages(
            states, rewards, nextStates, values, dones
        );

        // Normalize advantages
        const meanAdv = advantages.reduce((a, b) => a + b) / advantages.length;
        const stdAdv = Math.sqrt(
            advantages.reduce((a, b) => a + Math.pow(b - meanAdv, 2)) / advantages.length
        );
        const normalizedAdv = advantages.map(adv => (adv - meanAdv) / stdAdv);

        // Compute log probabilities of chosen actions
        const logProbs = this.computeLogProbs(states, actions);

        // Calculate mean of entropy of policy
        const entropy = -this.calculateMean(logProbs);

        // Compute surrogate loss for the actor
        const surrogateLoss = this.computeSurrogateLoss(logProbs, normalizedAdv, entropy);

        // Compute gradients for critic using backward function
        const criticGradients = this.critic.backward(values, targets);

        // Compute gradients for actor using backward function
        const actorGradients = this.actor.backwardScalar(logProbs, surrogateLoss);

        // Update actor
        this.actorOptimizer.zeroGrad();
        this.actorOptimizer.update(actorGradients);

        // Update critic
        this.criticOptimizer.update(criticGradients);

        // Update critic a few more times
        for (let i = 0; i < 4; i++) {
            this.criticOptimizer.update(criticGradients);
        }
    }

    train(episode) {
        // Get experiences from episode
        let states = [];
        let actions = [];
        let rewards = [];
        let nextStates = [];
        let dones = [];
        let values = [];
    
        for (let step of episode) {
            states.push(step.state);
            actions.push(step.action);
            rewards.push(step.reward);
            nextStates.push(step.nextState);
            dones.push(step.done ? 1.0 : 0.0);
    
            // Critic predicts state value
            const value = this.critic.predict(step.state)[0][0];
            values.push(value);
        }
    
        // Compute advantages and targets
        const [advantages, targets] = this.estimateAdvantages(
            states, rewards, nextStates, values, dones
        );
    
        // Normalize advantages
        const meanAdv = this.calculateMean(advantages);
        let sum = 0;
        for (let i = 0; i < advantages.length; i++) {
            sum += Math.pow(advantages[i] - meanAdv, 2);
        }
    
        const stdAdv = Math.sqrt(sum / advantages.length);
        const normalizedAdv = advantages.map(adv => (adv - meanAdv) / stdAdv);
    
        // Compute log probabilities of chosen actions
        const logProbs = this.computeLogProbs(states, actions);
    
        // Calculate mean of entropy of policy
        const entropy = -this.calculateMean(logProbs);
    
        // Compute surrogate loss for the actor
        const surrogateLoss = this.computeSurrogateLoss(logProbs, normalizedAdv, entropy);
    
        // Compute gradients for critic using backward function
        const criticLoss = this.calculateCriticLoss(values, targets);
        this.critic.computeGradients(criticLoss);
    
        // Compute gradients for actor using backward function
        const actorLoss = surrogateLoss;
        this.actor.computeGradients(actorLoss);
    
        // Apply gradients for both critic and actor
        for (let paramInfo of this.critic.getParameters()) {
            let layer = paramInfo.layer;
            this.criticOptimizer.applyGradients(layer.weightsGrads, layer.biasGrads);
        }
    
        for (let paramInfo of this.actor.getParameters()) {
            let layer = paramInfo.layer;
            this.actorOptimizer.applyGradients(layer.weightsGrads, layer.biasGrads);
        }
    
        // Update critic a few more times
        for (let i = 0; i < 4; i++) {
            for (let paramInfo of this.critic.getParameters()) {
                let layer = paramInfo.layer;
                this.criticOptimizer.applyGradients(layer.weightsGrads, layer.biasGrads);
            }
        }
    }
    

    calculateCriticLoss(values, targets) {
        const squaredErrors = values.map((value, idx) => Math.pow(value - targets[idx], 2));
        const criticLoss = this.calculateMean(squaredErrors);
        return criticLoss;
    }

    estimateAdvantages(states, rewards, nextStates, values, dones) {
        const numSteps = states.length;

        // Initialize arrays for advantages and targets
        const advantages = new Array(numSteps);
        const targets = new Array(numSteps);

        for (let t = 0; t < numSteps; t++) {
            const reward = rewards[t];
            const nextState = nextStates[t];
            const value = values[t];
            const done = dones[t];

            // Estimate value of next state
            const nextValue = this.critic.predict(nextState);

            // Calculate advantage and target
            if (done) {
                advantages[t] = reward - value;
                targets[t] = reward;
            } else {
                advantages[t] = reward + this.gamma * nextValue - value;
                targets[t] = reward + this.gamma * nextValue;
            }
        }

        return [advantages, targets];
    }


    computeLogProbs(states, actions) {
        const numSteps = states.length;

        let logProbs = new Array(numSteps);

        for (let i = 0; i < numSteps; i++) {
            const state = states[i];
            const action = actions[i];

            // Actor predicts Gaussian means and std devs
            const [means, stds] = this.actor.predictStds(state);

            // Compute log probability of chosen action
            let logProb = 0;
            for (let j = 0; j < this.actionSize; j++) {
                const actionValue = action[j];
                logProb -= 0.5 * Math.log(2 * Math.PI * stds[j] * stds[j]) +
                    (actionValue - means[j]) * (actionValue - means[j]) / (2 * stds[j] * stds[j]);
            }

            logProbs[i] = logProb;
        }

        return logProbs;
    }



    computeSurrogateLoss(logProbs, advantages, entropy) {
        // Compute surrogate losses
        const surrogate1 = logProbs.map((lp, idx) => lp * advantages[idx]);
        const surrogate2 = logProbs.map((lp, idx) =>
            Math.max(Math.min(lp, 1 + this.epsilon), 1 - this.epsilon) * advantages[idx]
        );

        const surrogate1Sum = surrogate1.reduce((acc, val) => acc + val, 0);
        const surrogate2Sum = surrogate2.reduce((acc, val) => acc + val, 0);

        let surrogate = Math.min(surrogate1Sum, surrogate2Sum);

        // Add entropy regularization
        let loss = -surrogate / logProbs.length - this.entropyCoeff * entropy;

        return loss;
    }
}

function zeros(size) {
    return Array(size).fill(0);
}


class AdamOptimizer {
    constructor(parameters, learningRate = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8) {
        this.parameters = parameters;
        this.learningRate = learningRate;
        this.beta1 = beta1;
        this.beta2 = beta2;
        this.epsilon = epsilon;

        // Initialize moment estimates and squared moment estimates to zero
        this.m = []
        this.v = []

        for (let param of parameters) {
            this.m.push({
                weights: new Matrix(param.weights.rows, param.weights.cols),
                bias: new Matrix(param.bias.rows, param.bias.cols)
            });
        
            this.v.push({
                weights: new Matrix(param.weights.rows, param.weights.cols),
                bias: new Matrix(param.bias.rows, param.bias.cols)
            });
        }        

        this.t = 0; // Iteration count
    }

    computeGradients(X, Y) {
        // Forward pass
        let output = this.forward(X);
    
        // Calculate initial gradient
        let gradient = this.lossFunction.gradient(Y, output);
    
        let parameters = this.getParameters();
    
        // Reverse loop through the layers
        for (let i = parameters.length - 1; i >= 0; i--) {
            let paramInfo = parameters[i];
            let layer = paramInfo.layer;
            
            // Calculate gradients for weights and bias
            if (paramInfo.paramType === "weights") {
                layer.weightsGrads = Matrix.multiply(gradient, layer.prevActivations.transpose());
            } else { // if paramInfo.paramType === "bias"
                layer.biasGrads = gradient;
            }
    
            // Calculate gradient for the next layer
            gradient = Matrix.multiply(layer.weights.transpose(), gradient);
        }
    }
    



    applyGradients(grads) {
        this.t++; // Increment the iteration count

        // Perform Adam update for each parameter
        for (let i = 0; i < this.parameters.length; i++) {
            let param = this.parameters[i];
            let gradient = grads[i];

            // Compute bias-corrected first moment estimate
            this.m[i] = this.beta1 * this.m[i] + (1 - this.beta1) * gradient;

            // Compute bias-corrected second raw moment estimate
            this.v[i] = this.beta2 * this.v[i] + (1 - this.beta2) * gradient * gradient;

            // Compute bias-corrected estimates
            let mHat = this.m[i] / (1 - Math.pow(this.beta1, this.t));
            let vHat = this.v[i] / (1 - Math.pow(this.beta2, this.t));

            // Update parameters
            params[i] = param - this.learningRate * mHat / (Math.sqrt(vHat) + this.epsilon);
        }
    }
}

class Episode {
    constructor(state, action, reward, nextState, done) {
        this.state = state;
        this.action = action;
        this.reward = reward;
        this.nextState = nextState;
        this.done = done;
    }

    add(state, action, reward, nextState, done) {
        this.state = state;
        this.action = action;
        this.reward = reward;
        this.nextState = nextState;
        this.done = done;
    }
}