class Relay {
    constructor(amplitude) {
        this.amplitude = amplitude;
        this.state = 1; // 1 or -1
    }

    step(y) {
        this.state = y >= this.amplitude ? -1 : (y <= -this.amplitude ? 1 : this.state);
        return this.amplitude * this.state;
    }
}

class FirstOrderProcess {
    constructor(K, tau) {
        this.K = K;
        this.tau = tau;
        this.y = 0;
    }

    step(u, dt) {
        const dy = (-this.y + this.K * u) * dt / this.tau;
        this.y += dy;
        return this.y;
    }
}


class FirstOrderProcess2 {
    constructor(K, tau) {
        this.K = K;
        this.tau = tau;
        this.y = 0;
    }

    step(u) {
        const dy = (-this.y + this.K * u) / this.tau;
        this.y += dy;
        return this.y;
    }
}

class IMCController {
    constructor(Km, tauM, tauC) {
        this.Km = Km;
        this.tauM = tauM;
        this.yM = 0;
        this.yPrev = 0;
        this.tauC = tauC;
    }

    step(r, y) {
        const e = r - y;
        this.yM += (e + (this.yPrev - this.yM) / this.tauM) * this.tauC;
        this.yPrev = this.yM;
        return this.Km * this.yM;
    }
}


function relayFeedbackTest(process, relay, dt, steps) {
    let y = 0;
    let oscPeriods = [];
    let lastSwitchTime = -2 * dt; // Initial value for switch
    let lastState = relay.state;

    for (let i = 0; i < steps; i++) {
        let u = relay.step(y);
        if (lastState !== relay.state) {
            oscPeriods.push((i - lastSwitchTime) * dt);
            lastSwitchTime = i;
            lastState = relay.state;
        }
        y = process.step(u, dt);
    }

    // Average over found periods
    const Pu = oscPeriods.reduce((acc, val) => acc + val, 0) / oscPeriods.length;

    return {
        Ku: 4 * relay.amplitude / (Math.PI * (process.y / process.K)),
        Pu: Pu
    };
}

function estimateProcessParameters(Ku, Pu) {
    return {
        Kp: 0.9 * Ku,
        tau: Pu / (3 * Math.PI)
    };
}

let dataLogs = []

function logData(value) {
    dataLogs.push(value);
}

// Parameters
const dt = 0.3;
const steps = 1000;

// Process for relay feedback test
const process = new FirstOrderProcess(2, 3);
const relay = new Relay(1);

const results = relayFeedbackTest(process, relay, dt, steps);
const params = estimateProcessParameters(results.Ku, results.Pu);

const imc = new IMCController(params.Kp, params.tau, 1.5);

process.y = 0;
// Test IMC
let y = 0;
for (let i = 0; i < steps; i++) {
    const u = imc.step(1, y); // Step reference to 1
    y = process.step(u, dt);
    logData(`${y}`);
}

console.log(JSON.stringify(dataLogs))