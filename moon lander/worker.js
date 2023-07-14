self.addEventListener('message', function(e) {
    const data = e.data;
    switch (data.cmd) {
        case 'start':
            const result = trainPolicy(data.observation, data.action, data.logprobability, data.advantage);
            self.postMessage(result);
            break;
        default:
            self.postMessage('Unknown command');
    };
}, false);