class PID {
    constructor(Kp = 0, Ki = 0, Kd = 0) {
        this.Kp = Kp;
        this.Ki = Ki;
        this.Kd = Kd;
        this.previousError = 0;
        this.integral = 0;
        this.K_u
        this.T_u;
    }

    compute(input, setpoint) {
        const error = setpoint - input;

        // Proportional term
        const P = this.Kp * error;

        // Integral term
        this.integral += error;
        const I = this.Ki * this.integral;

        // Derivative term
        const derivative = error - this.previousError;
        const D = this.Kd * derivative;

        // Save error for next iteration
        this.previousError = error;

        return P + I + D;
    }

    setTuningParams(Kp, Ki, Kd) {
        this.Kp = Kp;
        this.Ki = Ki;
        this.Kd = Kd;
    }

}


class PIDAutotuner {
    constructor() {
        this.Kp = 1;
        this.Ki = 0;
        this.Kd = 0;
        this.pid = new PID();
        this.targetInputValue = 0;
        this.minOutput = 0;
        this.maxOutput = 0;
        this.znMode = 'default';
        this.cycles = 0;
        this.oscillateCount = 0;
        this.oscillationInterval = 0;
        this.tLow = 0;
        this.tHigh = 0;
        this.t1 = 0;
        this.t2 = 0;
        this.amplitudeTolerance = 0.1; // Adjust this as needed
        this.intervalTolerance = 10; // Adjust this as needed        
    }

    setTargetInputValue(target) {
        this.targetInputValue = target;
    }

    setOutputRange(min, max) {
        this.minOutput = min;
        this.maxOutput = max;
    }

    setZNMode(zn) {
        this.znMode = zn;
    }

    setTuningCycles(tuneCycles) {
        this.cycles = tuneCycles;
    }

    startTuningLoop() {
        this.oscillateCount = 0;
        this.output = true;
        this.outputValue = this.maxOutput;
        this.t1 = this.t2 = 0;
        this.microseconds = this.tHigh = this.tLow = 0;
        this.max = -Number.MAX_SAFE_INTEGER;
        this.min = Number.MAX_SAFE_INTEGER;
        this.pAverage = this.iAverage = this.dAverage = 0;
        this.Ki = 0;
        this.Kd = 0;
        this.oscillateCount = 0;
    }

    isAmplitudeConstant() {
        const currentAmplitude = this.max - this.min;
        if (this.previousAmplitude === null) {
            this.previousAmplitude = currentAmplitude;
            return true;
        }

        const amplitudeDifference = Math.abs(this.previousAmplitude - currentAmplitude);
        return amplitudeDifference <= this.amplitudeTolerance;
    }

    getIsIntervalConstant() {
        if (!this.previousOscillationInterval && this.previousOscillationInterval !== 0) {
            this.previousOscillationInterval = this.oscillationInterval;
            return true;
        }

        const intervalDifference = Math.abs(this.previousOscillationInterval - this.oscillationInterval);
        return intervalDifference <= this.intervalTolerance;
    }

    getIntervalDelta() {
        if (!this.previousOscillationInterval && this.previousOscillationInterval !== 0) {
            this.previousOscillationInterval = this.oscillationInterval;
            return true;
        }

        const intervalDifference = Math.abs(this.previousOscillationInterval - this.oscillationInterval);
        return intervalDifference;
    }    

    getOscillation(input, frame) {
        this.max = Math.max(this.max, input);
        this.min = Math.min(this.min, input);
        let isNewOscillation = false;
        

        if (this.output && input > this.targetInputValue) {
            this.output = false;
            this.outputValue = this.minOutput;
            this.t1 = frame;
            this.tHigh = this.t1 - this.t2;
            this.max = this.targetInputValue;
        }

        if (!this.output && input < this.targetInputValue) {
            this.output = true;
            this.outputValue = this.maxOutput;
            this.t2 = frame;
            this.tLow = this.t2 - this.t1;

            this.oscillationInterval = this.tLow + this.tHigh;
            this.oscillateCount++;
            isNewOscillation = true;

            this.isIntervalConstant = this.getIsIntervalConstant()
            if (!this.isIntervalConstant) {
                // Reset the count if oscillation is not constant
                this.oscillateCount = 0;
            }
            this.intervalDelta = this.getIntervalDelta();
            this.previousAmplitude = this.max - this.min;
            this.previousOscillationInterval = this.oscillationInterval;
        }

        return {
            intervalDelta: this.intervalDelta,
            oscillationInterval: this.oscillationInterval,
            oscillateCount: this.oscillateCount,
            isConstantAmplitude: this.isAmplitudeConstant(),
            isConstantInterval: this.isIntervalConstant,
            isNewOscillation: isNewOscillation
        };
    }

    getKp() {
        return this.Kp;
    }

    setKp(newKp) {
        this.Kp = newKp;
    }

    getKi() {
        return this.Ki;
    }

    setKi(newKi) {
        this.Ki = newKi;
    }

    getKd() {
        return this.Kd;
    }

    setKd(newKd) {
        this.Kd = newKd;
    }

    isFinished() {
        return this.oscillateCount >= this.cycles;
    }

    getCycle() {
        return this.oscillateCount;
    }
}


let pid = new PID(0.1,0.002,0.1);
let position = 0;
let velocity = 0;
let acceleration = 0;

let dataLogs = []

function logData(value) {
    dataLogs.push(value);
}

for (let i = 0; i < 1000; i++) {
    acceleration = pid.compute(position, 10);
    velocity += acceleration;
    position += velocity;
    logData(position);
}

console.log(JSON.stringify(dataLogs))
