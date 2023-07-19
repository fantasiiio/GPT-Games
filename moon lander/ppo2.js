class PPO {
    constructor(
        observationDimensions,
        numActions,
        hiddenSizes = [32, 32],
        clipRatio = 0.2,
        policyLearningRate = 3e-5,
        valueFunctionLearningRate = 1e-5,
        trainPolicyIterations = 50,
        trainValueIterations = 50,
        targetKl = 0.1,
        miniBatchSize = 64
    ) {
        this.multiBuffer = new MultiBuffer();
        this.observationDimensions = observationDimensions;
        this.numActions = numActions;
        this.hiddenSizes = hiddenSizes;
        this.clipRatio = clipRatio;
        this.policyLearningRate = policyLearningRate;
        this.valueFunctionLearningRate = valueFunctionLearningRate;
        this.trainPolicyIterations = trainPolicyIterations;
        this.trainValueIterations = trainValueIterations;
        this.targetKl = targetKl;
        this.miniBatchSize = miniBatchSize;

        // Initialize the actor and the critic as tf.Model
        const observationInput = tf.input({
            shape: [this.observationDimensions]
        });
        this.actor = this.mlp(observationInput, [...this.hiddenSizes, this.numActions], 'sigmoid', 'sigmoid');

        this.critic = this.mlp(observationInput, [...this.hiddenSizes, 1], 'sigmoid', null);


        // Initialize the policy and the value function optimizers
        this.policyOptimizer = tf.train.adam(this.policyLearningRate);
        this.valueOptimizer = tf.train.adam(this.valueFunctionLearningRate);

        // Add metrics logs
        this.policyLossLog = [];
        this.valueLossLog = [];
        this.klDivergenceLog = [];
        this.totalRewardLog = [];
    }

    mlp(x, sizes, activation = 'tanh', outputActivation = null) {
        // Build a feedforward neural network
        let output = x;

        // Use the first n-1 sizes for the shared layers
        for (let i = 0; i < sizes.length - 1; i++) {
            output = tf.layers.dense({
                units: sizes[i],
                activation: activation
            }).apply(output);
        }

        // For the final layer, have two separate dense layers for the mean and standard deviation
        const mean = tf.layers.dense({
            units: sizes[sizes.length - 1],
            activation: outputActivation
        }).apply(output);

        const stdDev = tf.layers.dense({
            units: sizes[sizes.length - 1],
            activation: 'softplus' // Ensure standard deviation is positive
        }).apply(output);

        return tf.model({
            inputs: x,
            outputs: [mean, stdDev]
        });
    }

    logprobabilities(mean, stdDev, action) {
        action = tf.tensor2d(action);

        const variance = stdDev.square();
        const logStd = stdDev.log();

        const exponent = action.sub(mean).square().div(variance.mul(2)).neg();
        const logCoefficient = logStd.mul(2).add(tf.log(Math.PI * 2).div(-2));

        const logprobabilities = exponent.sub(logCoefficient);

        return logprobabilities;
    }

    sampleAction(observation) {
        // Add batch dimension
        observation = tf.expandDims(observation, 0);

        // Get mean and std dev from policy network
        let res = this.actor.predict(observation);
        const mean = res[0];
        const stdDev = res[1];

        // Sample from Gaussian distribution
        const action = mean.add(stdDev.mul(tf.randomNormal(mean.shape)));

        // Remove batch dimension and return action and logits
        return [res, action.squeeze().arraySync()]; // arraySync() to get the JavaScript array from the tensor
    }

    gaussianPolicyLoss(states, actions, advantages) {
        const [means, stds] = this.actor.predict(tf.tensor2d(states));
        const actionLogProb = this.gaussianLogProb(means, stds, tf.tensor2d(actions));

        // Ensure advantages is a 2D tensor matching shape of actionLogProb
        advantages = tf.reshape(tf.tensor1d(advantages), [-1, 1]);

        // Calculate the loss as the mean of the element-wise product of -actionLogProb and advantages
        const loss = tf.mean(tf.mul(actionLogProb, tf.neg(advantages)));
        return loss;
    }

    gaussianLogProb(means, stds, values) {
        const var1 = stds.square();
        const logProb = values.sub(means).square().div(var1.mul(2)).neg().sub(var1.log().mul(Math.PI * 2).div(2));

        return logProb;
    }


    // Function to zip arrays
    zip(arrays) {
        return arrays[0].map((_, i) => arrays.map(array => array[i]));
    }

    async trainPolicy(observationBuffer, actionBuffer, logprobabilityBuffer, advantageBuffer) {
        // Compute Gaussian policy loss
        const computePolicyLoss = () => {
            return this.gaussianPolicyLoss(observationBuffer, actionBuffer, advantageBuffer);
        };
        // Compute and apply gradients
        const grads = tf.grads(computePolicyLoss);
        this.policyOptimizer.applyGradients(grads);

        // Run actions through updated policy network
        const newPolicyParams = this.actor.predict(tf.tensor2d(observationBuffer));
        const newMean = newPolicyParams[0];
        const newStdDev = newPolicyParams[1];

        // Compute log probabilities under new policy
        const newLogProbabilities = this.logprobabilities(newMean, newStdDev, actionBuffer);

        // Compute KL divergence between old and new policy
        const kl = tf.tensor2d(logprobabilityBuffer).sub(newLogProbabilities);

        // Log policy loss and KL divergence
        this.policyLossLog.push(computePolicyLoss().dataSync()[0]);
        this.klDivergenceLog.push(tf.sum(kl).dataSync()[0]);
        return tf.sum(kl);
    }


    async trainValueFunction(observationBuffer, returnBuffer) {
        const computeValueLoss = () => {
            const value = this.critic.predict(tf.tensor2d(observationBuffer));
            const predictedValues = value[0].squeeze(); // Assuming the value tensor has a single dimension
            returnBuffer = tf.tensor1d(returnBuffer);
            return tf.mean(tf.square(tf.sub(returnBuffer, predictedValues)));
        };

        const grads = tf.grads(computeValueLoss);

        this.valueOptimizer.applyGradients(grads);
        // Log value loss
        this.valueLossLog.push(computeValueLoss().dataSync()[0]);
    }

    async train(observationBuffer, actionBuffer, advantageBuffer, returnBuffer, logprobabilityBuffer) {
        // Train the policy and the value function
        // Update the policy and implement early stopping using KL divergence
        for (let i = 0; i < this.trainPolicyIterations; i++) {
            const kl = await this.trainPolicy(observationBuffer, actionBuffer, logprobabilityBuffer, advantageBuffer);
            if (kl.dataSync()[0] > 1.5 * this.targetKl) {
                // Early Stopping
                break;
            }
        }

        // Update the value function
        for (let i = 0; i < this.trainValueIterations; i++) {
            await this.trainValueFunction(observationBuffer, returnBuffer);
        }
    }

    async getAction(observation) {
        // Generate an action and return its value and log-probability
        const output = this.actor.predict(tf.tensor2d([observation]));
        const mean = output[0];
        const stdDev = output[1];

        // Sample action from the Gaussian distribution
        const action = mean.add(stdDev.mul(tf.randomNormal(mean.shape)));

        // Get the value of the action from the critic network
        const valueT = this.critic.predict(tf.tensor2d([observation]));

        // Compute the log-probability of the action
        const logprobabilityT = this.gaussianLogProb(mean, stdDev, action);

        // Convert tensors to JavaScript values
        const actionValue = action;
        const value = valueT[0];
        const logprobability = logprobabilityT;


        return [actionValue, value, logprobability];
    }

    async save(path) {
        // Save the trained model to a file.
        await this.actor.save('file://' + path + '_actor');
        await this.critic.save('file://' + path + '_critic');
    }

    async load(path) {
        // Load a previously trained model from a file.
        this.actor = await tf.loadLayersModel('file://' + path + '_actor/model.json');
        this.critic = await tf.loadLayersModel('file://' + path + '_critic/model.json');
    }

    computeAdvantages(rewards, values, gamma = 0.99, lambda = 0.97) {
        // Compute TD residuals
        let deltas = [];
        for (let i = 0; i < rewards.length - 1; i++) {
            deltas.push(rewards[i] + gamma * values[i + 1] - values[i]);
        }
        // Compute GAE advantages
        let advantages = new Array(rewards.length).fill(0.0);
        for (let t = rewards.length - 2; t >= 0; t--) {
            advantages[t] = deltas[t] + gamma * lambda * advantages[t + 1];
        }
        return advantages;
    }

    async trainPPO(env, epochs = 1000, stepsPerEpoch = 1000) {
        let csvLog = 'epoch,policyLoss,valueLoss,klDivergence,totalReward\n'; // Header for csv file

        for (let epoch = 0; epoch < epochs; epoch++) {
            let obs = env.reset();
            let totalReward = 0; // Initialize total reward for the epoch
            for (let step = 0; step < stepsPerEpoch; step++) {
                let [act, val, logp] = await this.getAction(obs);
                let result = await env.step(act.dataSync());
                let [obs2, rew, done] = result;
                totalReward += rew; // Add reward to total reward

                if (done) {
                    obs = env.reset();
                } else {
                    obs = obs2;
                }

                this.multiBuffer.add({
                    observationBuffer: obs,
                    actionBuffer: act.arraySync()[0],
                    valueBuffer: val.arraySync()[0],
                    rewardsBuffer: rew,
                    logprobabilityBuffer: logp.arraySync()[0]
                });
            }

            this.multiBuffer.standardizeRewards();
            this.totalRewardLog.push(totalReward); // Log total reward

            // Compute the returns
            let returnBuf = [];
            let g = 0;
            const gamma = 0.99; // set the discount factor as per your requirement
            for (let i = this.multiBuffer.buffers.rewardsBuffer.length - 1; i >= 0; i--) {
                g = this.multiBuffer.buffers.rewardsBuffer[i] + gamma * g;
                returnBuf[i] = g;
                this.multiBuffer.add({
                    returnBuffer: g,
                });
            }

            // Compute advantage estimates
            this.multiBuffer.buffers.advantageBuffer = this.computeAdvantages(this.multiBuffer.buffers.rewardsBuffer, this.multiBuffer.buffers.valueBuffer);

            this.multiBuffer.shuffle();
            let miniBatches = this.multiBuffer.getBatches(this.miniBatchSize);
            for (let i = 0; i < miniBatches.actionBuffer.length; i++) {
                let obsBuf = miniBatches.observationBuffer[i];
                let actBuf = miniBatches.actionBuffer[i];
                let advBuf = miniBatches.advantageBuffer[i];
                let returnBuf = miniBatches.returnBuffer[i];
                let logpBuf = miniBatches.logprobabilityBuffer[i];
                await this.train(obsBuf, actBuf, advBuf, returnBuf, logpBuf);
            }
            this.multiBuffer.reset();
            // Append metrics for this epoch to the csv string
            csvLog += `${epoch},${this.policyLossLog[this.policyLossLog.length - 1]},${this.valueLossLog[this.valueLossLog.length - 1]},${this.klDivergenceLog[this.klDivergenceLog.length - 1]},${this.totalRewardLog[this.totalRewardLog.length - 1]}\n`;
            this.valueLossLog.length = 0;
            this.valueLossLog.length = 0;
            this.klDivergenceLog.length = 0;
            // Log the csv string at the end of each epoch
            console.log(csvLog);

        }
    }
}