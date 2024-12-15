const net = require('net');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const os = require('os');

// Get local IP address
function getLocalIP() {
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return '127.0.0.1';
}

// Create readline interface
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Server implementation
function startServer(port) {
    const server = net.createServer((socket) => {
        console.log('Client connected:', socket.remoteAddress);

        socket.on('data', (data) => {
            const command = data.toString().trim();
            
            if (command === 'LIST') {
                // Send list of files in current directory
                fs.readdir('.', (err, files) => {
                    if (err) {
                        socket.write('ERROR: ' + err.message);
                    } else {
                        socket.write('FILES:' + files.join(','));
                    }
                });
            } else if (command.startsWith('GET ')) {
                // Handle file download request
                const filename = command.slice(4);
                if (fs.existsSync(filename)) {
                    const fileStream = fs.createReadStream(filename);
                    socket.write('START:' + filename);
                    fileStream.pipe(socket);
                } else {
                    socket.write('ERROR: File not found');
                }
            }
        });

        socket.on('error', (err) => {
            console.log('Socket error:', err.message);
        });

        socket.on('end', () => {
            console.log('Client disconnected');
        });
    });

    server.listen(port, () => {
        console.log(`Server listening on ${getLocalIP()}:${port}`);
    });

    server.on('error', (err) => {
        console.log('Server error:', err.message);
    });
}

// Client implementation
function startClient(serverIP, serverPort) {
    const client = new net.Socket();

    client.connect(serverPort, serverIP, () => {
        console.log('Connected to server');
        showClientMenu(client);
    });

    client.on('data', (data) => {
        const response = data.toString();
        if (response.startsWith('FILES:')) {
            // Display list of files
            const files = response.slice(6).split(',');
            console.log('\nAvailable files:');
            files.forEach((file, index) => {
                console.log(`${index + 1}. ${file}`);
            });
            showClientMenu(client);
        } else if (response.startsWith('START:')) {
            // Handle file download
            const filename = response.slice(6);
            const writeStream = fs.createWriteStream('downloaded_' + filename);
            client.pipe(writeStream);
            console.log(`\nDownloading ${filename}...`);
        } else if (response.startsWith('ERROR:')) {
            console.log('\nError:', response.slice(6));
            showClientMenu(client);
        }
    });

    client.on('error', (err) => {
        console.log('Client error:', err.message);
    });
}

function showClientMenu(client) {
    console.log('\nClient Menu:');
    console.log('1. List files');
    console.log('2. Download file');
    console.log('3. Exit');
    
    rl.question('Select an option: ', (answer) => {
        switch(answer) {
            case '1':
                client.write('LIST');
                break;
            case '2':
                rl.question('Enter filename to download: ', (filename) => {
                    client.write('GET ' + filename);
                });
                break;
            case '3':
                client.end();
                rl.close();
                process.exit(0);
                break;
            default:
                console.log('Invalid option');
                showClientMenu(client);
        }
    });
}

// Main menu
console.log('FTP Application Menu:');
console.log('1. Start Server');
console.log('2. Start Client');

rl.question('Select mode (1/2): ', (mode) => {
    if (mode === '1') {
        rl.question('Enter port number: ', (port) => {
            startServer(parseInt(port));
        });
    } else if (mode === '2') {
        rl.question('Enter server IP: ', (ip) => {
            rl.question('Enter server port: ', (port) => {
                startClient(ip, parseInt(port));
            });
        });
    } else {
        console.log('Invalid option');
        rl.close();
    }
});
