class PPOAlgorithm {
    constructor() {
        this.stepTurboMode = false;
        this.stepDebounced = this.stepDebounced.bind(this);
        this.stepTurbo = this.stepTurbo.bind(this);
        this.step = this.step.bind(this);
        this.run = this.run.bind(this);
        this.stepNumber = 0;
        this.episode = [];
    }

    stepDebounced() {
        if (!this.stepDebounced.debounced) {
            this.stepDebounced.debounced = true;
            setTimeout(() => {
                this.stepDebounced.debounced = false;
                this.step();
                // Recursively call next step 
                if (this.stepTurboMode)
                    requestAnimationFrame(this.stepTurbo);
                else
                    requestAnimationFrame(this.stepDebounced);
            });
        }
    }

    stepTurbo() {
        const interval = setInterval(() => {
            if (this.stepTurboMode)
                this.step();
            else {
                clearInterval(interval);
                requestAnimationFrame(this.stepDebounced);
            }
        }, 1);
    }

    sampleNormalDistribution(mean, std) {
        let u = Math.random();
        let v = Math.random();
        let x = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
        return mean + std * x;
    }

    step() {
        // Get action from the actor
        let output = this.agent.getAction(this.state);
        let means = output[0];
        let stds = output[1];
        
        let actions = [];
        for(let i = 0; i < this.agent.actionSize; i++) {
            actions[i] = this.sampleNormalDistribution(means[i], stds[i]);
        }
        // Take a step in the environment
        let [nextState, reward, done] = this.environment.step(actions);
    
        // Add experience to episode
        this.episode.push(new Episode(this.state, actions, reward, nextState, done));
    
        // Add to total reward
        this.totalReward = reward;
    
        if (done || this.stepNumber >= this.maxStepsPerEpisode) { // Episode done
            this.agent.train(this.episode);
    
            // Start new episode
            this.episode.length = 0;
            this.state = this.environment.ppoLander.resetLander();
            this.totalReward = 0;
            this.maxStepsPerEpisode = Math.min(this.maxStepsPerEpisode * 1.1, 1000); // Increase max steps
        } else {
            this.state = nextState; // Continue episode
        }
        this.stepNumber++;
    }
    

    run(environment) {
        // Save as properties so they can be accessed in other methods
        this.agent = environment.ppoLander.ppoAgent;
        this.environment = environment;
        this.state = this.environment.ppoLander.resetLander();
        this.totalReward = 0;
        this.maxStepsPerEpisode = 100; // Max steps per episode

        // Begin animation loop 
        requestAnimationFrame(this.stepDebounced);
    }
}

let ppo = new PPOAlgorithm();
ppo.run(env);