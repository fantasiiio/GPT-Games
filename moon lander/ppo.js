// Check if node
if (typeof module === 'object' && module.exports) {
    var tf = require('@tensorflow/tfjs')
}

function log() {
    console.log('[PPO]', ...arguments)
}

class BaseCallback {
    constructor() {
        this.nCalls = 0
    }

    _onStep(alg) {
        return true
    }
    onStep(alg) {
        this.nCalls += 1
        return this._onStep(alg)
    }

    _onTrainingStart(alg) {}
    onTrainingStart(alg) {
        this._onTrainingStart(alg)
    }

    _onTrainingEnd(alg) {}
    onTrainingEnd(alg) {
        this._onTrainingEnd(alg)
    }

    _onRolloutStart(alg) {}
    onRolloutStart(alg) {
        this._onRolloutStart(alg)
    }

    _onRolloutEnd(alg) {}
    onRolloutEnd(alg) {
        this._onRolloutEnd(alg)
    }
}

class FunctionalCallback extends BaseCallback {
    constructor(callback) {
        super()
        this.callback = callback
    }

    _onStep(alg) {
        if (this.callback) {
            return this.callback(alg)
        }
        return true
    }
}

class DictCallback extends BaseCallback {
    constructor(callback) {
        super()
        this.callback = callback
    }

    _onStep(alg) {
        if (this.callback && this.callback.onStep) {
            return this.callback.onStep(alg)
        }
        return true
    }

    _onTrainingStart(alg) {
        if (this.callback && this.callback.onTrainingStart) {
            this.callback.onTrainingStart(alg)
        }
    }

    _onTrainingEnd(alg) {
        if (this.callback && this.callback.onTrainingEnd) {
            this.callback.onTrainingEnd(alg)
        }
    }

    _onRolloutStart(alg) {
        if (this.callback && this.callback.onRolloutStart) {
            this.callback.onRolloutStart(alg)
        }
    }

    _onRolloutEnd(alg) {
        if (this.callback && this.callback.onRolloutEnd) {
            this.callback.onRolloutEnd(alg)
        }
    }
}

class Buffer {
    constructor(bufferConfig) {
        const bufferConfigDefault = {
            gamma: 0.99,
            lam: 0.95
        }
        this.bufferConfig = Object.assign({}, bufferConfigDefault, bufferConfig)
        this.gamma = this.bufferConfig.gamma
        this.lam = this.bufferConfig.lam
        this.reset()
    }

    add(observation, action, reward, value, logprobability, predsScale) {
        this.observationBuffer.push(observation.slice(0))
        this.actionBuffer.push(action)
        this.rewardBuffer.push(reward)
        this.valueBuffer.push(value)
        this.logprobabilityBuffer.push(logprobability)
        this.predsScaleBuffer.push(predsScale)
        this.pointer += 1
    }

    discountedCumulativeSums(arr, coeff) {
        let res = []
        let s = 0
        arr.reverse().forEach(v => {
            s = v + s * coeff
            res.push(s)
        })
        return res.reverse()
    }

    finishTrajectory(lastValue) {
        const rewards = this.rewardBuffer
            .slice(this.trajectoryStartIndex, this.pointer)
            .concat(lastValue * this.gamma)
        const values = this.valueBuffer
            .slice(this.trajectoryStartIndex, this.pointer)
            .concat(lastValue)
        const deltas = rewards
            .slice(0, -1)
            .map((reward, ri) => reward - (values[ri] - this.gamma * values[ri + 1]))
        this.advantageBuffer = this.advantageBuffer
            .concat(this.discountedCumulativeSums(deltas, this.gamma * this.lam))
        this.returnBuffer = this.returnBuffer
            .concat(this.discountedCumulativeSums(rewards, this.gamma).slice(0, -1))
        this.trajectoryStartIndex = this.pointer
        //ET CELLE-CI ?
    }

    get() {
        const [advantageMean, advantageStd] = tf.tidy(() => [
            tf.mean(this.advantageBuffer).arraySync(),
            tf.moments(this.advantageBuffer).variance.sqrt().arraySync()
        ])

        this.advantageBuffer = this.advantageBuffer
            .map(advantage => (advantage - advantageMean) / advantageStd)

        return [
            this.observationBuffer,
            this.actionBuffer,
            this.advantageBuffer,
            this.returnBuffer,
            this.logprobabilityBuffer
        ]
    }

    reset() {
        this.observationBuffer = []
        this.actionBuffer = []
        this.advantageBuffer = []
        this.rewardBuffer = []
        this.returnBuffer = []
        this.valueBuffer = []
        this.logprobabilityBuffer = []
        this.predsScaleBuffer = []
        this.trajectoryStartIndex = 0
        this.pointer = 0
    }

}

let id = 1;

class PPO {
    constructor(env, spaceConfig, config) {
        const configDefault = {
            nSteps: 1024,
            nEpochs: 50,
            policyLearningRate: 1e-5,
            valueLearningRate: 1e-5,
            clipRatio: 0.2,
            targetKL: 0.01,
            useSDE: false, // TODO: State Dependent Exploration (gSDE)
            netArch: {
                'pi': [7],
                'vf': [7]
            },
            activation: 'sigmoid',
            verbose: 1
        }
        this.ema = new LossEMA(0.95)
        this.config = Object.assign({}, configDefault, config)
        this.spaceConfig = spaceConfig;
        this.rewards = [];
        this.losses = [];

        // Prepare network architecture
        if (Array.isArray(this.config.netArch)) {
            this.config.netArch = {
                'pi': this.config.netArch,
                'vf': this.config.netArch
            }
        }

        // Initialize logger
        this.log = (...args) => {
            if (this.config.verbose > 0) {
                console.log('[PPO]', ...args)
            }
        }

        // Initialize environment
        this.env = env
        if ((this.spaceConfig.actionSpace.class == 'Discrete') && !this.spaceConfig.actionSpace.dtype) {
            this.spaceConfig.actionSpace.dtype = 'int32'
        } else if ((this.spaceConfig.actionSpace.class == 'Box') && !this.spaceConfig.actionSpace.dtype) {
            this.spaceConfig.actionSpace.dtype = 'float32'
        }

        // Initialize counters
        this.numTimesteps = 0
        this.lastObservation = null

        // Initialize buffer
        this.buffer = new Buffer(config)

        // Initialize models for actor and critic
        this.actor = this.createActor()
        this.critic = this.createCritic()

        // Initialize logStd (for continuous action space)
        if (this.spaceConfig.actionSpace.class == 'Box') {
            this.logStd = tf.variable(tf.zeros([this.spaceConfig.actionSpace.shape[0]]), true, 'logStd' + id++)
        }

        // Initialize optimizers
        this.optPolicy = tf.train.adam(this.config.policyLearningRate)
        this.optValue = tf.train.adam(this.config.valueLearningRate)
    }

    createActor() {
        const input = tf.layers.input({
            shape: this.spaceConfig.observationSpace.shape
        })
        let l = input
        this.config.netArch.pi.forEach((units, i) => {
            l = tf.layers.dense({
                units,
                activation: this.config.activation
            }).apply(l)
        })

        l = tf.layers.dense({
            units: this.spaceConfig.actionSpace.shape[0],
            activation: this.config.activation
            // kernelInitializer: 'glorotNormal'
        }).apply(l)

        return tf.model({
            inputs: input,
            outputs: l
        })
    }

    createCritic() {
        // Initialize critic
        const input = tf.layers.input({
            shape: this.spaceConfig.observationSpace.shape
        })
        let l = input
        this.config.netArch.vf.forEach((units, i) => {
            l = tf.layers.dense({
                units: units,
                activation: this.config.activation
            }).apply(l)
        })
        l = tf.layers.dense({
            units: 1,
            activation: 'linear'
        }).apply(l)
        return tf.model({
            inputs: input,
            outputs: l
        })
    }

    sampleAction(observationT) {
        return tf.tidy(() => {
            const preds = tf.squeeze(this.actor.predict(observationT), 0)
            let action
            let noiseScale
            let predsScale;

            noiseScale = tf.exp(this.logStd);
            const randomNoise = tf.mul(
                tf.sigmoid(tf.randomStandardNormal([this.spaceConfig.actionSpace.shape[0]])),
                noiseScale
            );
            predsScale = tf.sub(1, noiseScale);
            const policyAction = tf.mul(preds, predsScale);
            action = tf.add(randomNoise, policyAction);

            return [preds, action, predsScale]
        })
    }


    logProbCategorical(logits, x) {
        return tf.tidy(() => {
            const numActions = logits.shape[logits.shape.length - 1]
            const logprobabilitiesAll = tf.logSoftmax(logits)
            return tf.sum(
                tf.mul(tf.oneHot(x, numActions), logprobabilitiesAll),
                logprobabilitiesAll.shape.length - 1
            )
        })
    }

    logProbNormal(loc, scale, x) {
        return tf.tidy(() => {
            const logUnnormalized = tf.mul(
                -0.5,
                tf.square(
                    tf.sub(
                        tf.div(x, scale),
                        tf.div(loc, scale)
                    )
                )
            )
            const logNormalization = tf.add(
                tf.scalar(0.5 * Math.log(2.0 * Math.PI)),
                tf.log(scale)
            )
            return tf.sum(
                tf.sub(logUnnormalized, logNormalization),
                logUnnormalized.shape.length - 1
            )
        })
    }

    logProb(preds, actions) {
        // Preds can be logits or means
        if (this.spaceConfig.actionSpace.class == 'Discrete') {
            return this.logProbCategorical(preds, actions)
        } else if (this.spaceConfig.actionSpace.class == 'Box') {
            return this.logProbNormal(preds, tf.exp(this.logStd), actions)
        }
    }

    predict(observation, deterministic = false) {
        return this.actor.predict(observation)
    }

    trainPolicy(observationBufferT, actionBufferT, logprobabilityBufferT, advantageBufferT) {
        const optFunc = () => {
            const predsT = this.actor.predict(observationBufferT) // -> Logits or means
            const diffT = tf.sub(
                this.logProb(predsT, actionBufferT),
                logprobabilityBufferT
            )
            const ratioT = tf.exp(diffT)
            const minAdvantageT = tf.where(
                tf.greater(advantageBufferT, 0),
                tf.mul(tf.add(1, this.config.clipRatio), advantageBufferT),
                tf.mul(tf.sub(1, this.config.clipRatio), advantageBufferT)
            )
            const policyLoss = tf.neg(tf.mean(
                tf.minimum(tf.mul(ratioT, advantageBufferT), minAdvantageT)
            ))
            this.ema.update(policyLoss.arraySync())
            return policyLoss
        }

        return tf.tidy(() => {
            const {
                values,
                grads
            } = this.optPolicy.computeGradients(optFunc)
            this.optPolicy.applyGradients(grads)
            const kl = tf.mean(tf.sub(
                logprobabilityBufferT,
                this.logProb(this.actor.predict(observationBufferT), actionBufferT)
            ))
            return kl.arraySync()
        })
    }

    trainValue(observationBufferT, returnBufferT) {
        const optFunc = () => {
            const valuesPredT = this.critic.predict(observationBufferT)
            return tf.losses.meanSquaredError(returnBufferT, valuesPredT)
        }

        tf.tidy(() => {
            const {
                values,
                grads
            } = this.optValue.computeGradients(optFunc)
            this.optValue.applyGradients(grads)
        })
    }

    _initCallback(callback) {
        // Function, not class
        if (typeof callback === 'function') {
            if (callback.prototype.constructor === undefined) {
                return new FunctionalCallback(callback)
            }
            return callback
        }
        if (typeof callback === 'object') {
            return new DictCallback(callback)
        }
        return new BaseCallback()
    }

    async collectRollouts(callback) {
        if (this.lastObservation === null) {
            this.lastObservation = this.env.reset()
        }

        this.buffer.reset()
        callback.onRolloutStart(this)

        await this.stepLoop(callback)

        callback.onRolloutEnd(this)
    }


    async stepLoop(callback) {
        let step = 0;
        let allNoiseScales = [];

        return new Promise((resolve) => {
            const maxSteps = this.config.nSteps; // replace with your maximum step count

            let intervalId = setInterval(async () => {
                // Predict action, value and logprob from last observation
                const [preds, action, value, logprobability, predsScale] = tf.tidy(() => {
                    const lastObservationT = tf.tensor([this.lastObservation])
                    const [predsT, actionT, predsScaleT] = this.sampleAction(lastObservationT)
                    const valueT = this.critic.predict(lastObservationT)
                    const logprobabilityT = this.logProb(predsT, actionT)
                    return [
                        predsT.arraySync(),
                        actionT.arraySync(),
                        valueT.arraySync()[0][0],
                        logprobabilityT.arraySync(),
                        predsScaleT.arraySync()
                    ]
                })

                // Rescale for continuous action space
                //let clippedAction = action
                // if (this.spaceConfig.actionSpace.class == 'Box') {
                //     let h = this.spaceConfig.actionSpace.high
                //     let l = this.spaceConfig.actionSpace.low
                //     if (typeof h === 'number' && typeof l === 'number') {
                //         clippedAction = action.map(a => {
                //             return Math.min(Math.max(a, l), h)
                //         })
                //     }
                // }

                // Take action in environment
                const [newObservation, reward, done] = await this.env.step(action)

                // Update global timestep counter
                this.numTimesteps += 1

                callback.onStep(this)

                this.buffer.add(
                    this.lastObservation,
                    action,
                    reward,
                    value,
                    logprobability,
                    predsScale
                )

                this.lastObservation = newObservation

                if (done || step === this.config.nSteps - 1) {
                    const lastValue = done ?
                        0 :
                        tf.tidy(() => this.critic.predict(tf.tensor([newObservation])).arraySync())[0][0]
                    this.buffer.finishTrajectory(lastValue)
                    console.log("Reward:" + this.buffer.rewardBuffer[this.buffer.rewardBuffer.length - 1]);
                    let avgArr = tf.mean(this.buffer.predsScaleBuffer).arraySync()

                    console.log("Predictions Scale:" + JSON.stringify(avgArr));

                    this.lastObservation = this.env.reset()
                }
                step++;

                if (step >= maxSteps) {
                    clearInterval(intervalId);
                    resolve(true);
                }
            }, 0);
        });
    }

    async train(config) {
        // Get values from the buffer
        const [
            observationBuffer,
            actionBuffer,
            advantageBuffer,
            returnBuffer,
            logprobabilityBuffer,
        ] = this.buffer.get()

        const [
            observationBufferT,
            actionBufferT,
            advantageBufferT,
            returnBufferT,
            logprobabilityBufferT
        ] = tf.tidy(() => [
            tf.tensor(observationBuffer),
            tf.tensor(actionBuffer, null, this.spaceConfig.actionSpace.dtype),
            tf.tensor(advantageBuffer),
            tf.tensor(returnBuffer).reshape([-1, 1]),
            tf.tensor(logprobabilityBuffer)
        ])

        for (let i = 0; i < this.config.nEpochs; i++) {
            const kl = this.trainPolicy(observationBufferT, actionBufferT, logprobabilityBufferT, advantageBufferT)
            this.losses.push(kl);
            if (kl > 1.5 * this.config.targetKL) {
                break
            }
        }

        console.log("Loss:" + this.ema.get())
        this.ema.ema = 0;

        for (let i = 0; i < this.config.nEpochs; i++) {
            this.trainValue(observationBufferT, returnBufferT)
        }

        tf.dispose([
            observationBufferT,
            actionBufferT,
            advantageBufferT,
            returnBufferT,
            logprobabilityBufferT
        ])
    }

    async trainPPO(learnConfig) {
        const learnConfigDefault = {
            'logInterval': 1,
            'callback': null
        }
        let {
            logInterval,
            callback
        } = Object.assign({}, learnConfigDefault, learnConfig)

        callback = this._initCallback(callback)

        let iteration = 0

        callback.onTrainingStart(this)

        while (true) {
            iteration += 1
            console.log(`Iteration: ${iteration}`)
            await this.collectRollouts(callback)
            this.train()
        }
    }

}

// Exponentially weighted moving average

class LossEMA {
    constructor(decay = 0.5) {
        this.decay = decay
        this.ema = 0
    }

    update(loss) {
        if (this.ema === 0) {
            this.ema = loss
        } else {
            this.ema = this.decay * this.ema + (1 - this.decay) * loss
        }
    }

    get() {
        return this.ema
    }
}

class PPOAlgorithm {
    constructor(newPPO) {
        this.ppo = newPPO
        this.ppoChanged = false
    }
    changePPO(newPPO) {
        this.ppo = newPPO
    }

    async runSimulation(totalTimesteps) {
        let observation = this.ppo.env.reset();

        for (let t = 0; t < totalTimesteps; t++) {
            let action = this.ppo.predict(observation);
            let [newObservation, reward, done] = await this.ppo.env.step(action);
            observation = newObservation;

            if (done) {
                observation = this.ppo.env.reset();
            }
        }
    }
}

if (typeof module === 'object' && module.exports) {
    module.exports = PPO
}