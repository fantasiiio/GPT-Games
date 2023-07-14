class AdamOptimizer {
    constructor(learningRate, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8) {
        this.learningRate = learningRate;
        this.beta1 = beta1;
        this.beta2 = beta2;
        this.epsilon = epsilon;
        this.m = 0;
        this.v = 0;
        this.t = 0;
    }

    getGradients(parameters, lossFunction) {
        let gradients = {}
        for (let param in parameters) {
            let originalParam = parameters[param]
            parameters[param] = originalParam + this.epsilon
            let loss1 = lossFunction(parameters)

            parameters[param] = originalParam - this.epsilon
            let loss2 = lossFunction(parameters)

            gradients[param] = (loss1 - loss2) / (2 * this.epsilon)
            parameters[param] = originalParam // reset
        }
        return gradients
    }

    minimize(parameters, lossFunction) {
        let gradients = this.getGradients(parameters, lossFunction) 
        
        this.t += 1
        let beta1Pow = Math.pow(this.beta1, this.t)
        let beta2Pow = Math.pow(this.beta2, this.t)
    
        for (let param in parameters) {
          this.m[param] = this.beta1 * this.m[param] + (1 - this.beta1) * gradients[param]  
          this.v[param] = this.beta2 * this.v[param] + (1 - this.beta2) * gradients[param] ** 2 
    
          let mHat = this.m[param] / (1 - beta1Pow)
          let vHat = this.v[param] / (1 - beta2Pow)
    
          parameters[param] -= this.learningRate * mHat / (Math.sqrt(vHat) + this.epsilon)
        }
      }    
}