class MultiBuffer {
    constructor() {
        this.buffers = {
            observationBuffer: [],
            actionBuffer: [],
            advantageBuffer: [],
            returnBuffer: [],
            logprobabilityBuffer: [],
            rewardsBuffer: [],
            valueBuffer: []
        };
    }

    standardizeRewards(rewards) {
        rewards = rewards || this.buffers.rewardsBuffer
        const mean = rewards.reduce((a, b) => a + b) / rewards.length;
        const std = Math.sqrt(rewards.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / rewards.length);
        return rewards.map(x => (x - mean) / std);
    }

    add(data) {
        for (let key in data) {
            if (this.buffers[key] !== undefined) {
                this.buffers[key].push(data[key]);
            }
        }
    }

    getBatches(batch_size) {
        let batches = {
            observationBuffer: [],
            actionBuffer: [],
            advantageBuffer: [],
            returnBuffer: [],
            logprobabilityBuffer: [],
            rewardsBuffer: [],
            valueBuffer: []
        };

        for (let key in this.buffers) {
            for (let i = 0; i < this.buffers[key].length; i += batch_size) {
                batches[key].push(this.buffers[key].slice(i, i + batch_size));
            }
        }

        return batches;
    }

    shuffle() {
        // Generate a list of indices and shuffle it
        const indices = tf.util.createShuffledIndices(this.buffers.observationBuffer.length);
        
        for (let key in this.buffers) {
            let oldBuffer = this.buffers[key];
            let newBuffer = new Array(oldBuffer.length);
            
            // Reassign each element to its new (shuffled) index
            for (let i = 0; i < indices.length; i++) {
                newBuffer[i] = oldBuffer[indices[i]];
            }
            
            // Replace the old buffer with the new (shuffled) buffer
            this.buffers[key] = newBuffer;
        }
    }

    reset() {
        // Iterate over each buffer and reset it
        for (let key in this.buffers) {
            this.buffers[key].length = 0;
        }
    }
    
}
