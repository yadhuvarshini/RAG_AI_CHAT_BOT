// ws/socket.js
function setupWebSocket(wss) {
  wss.on('connection', (ws) => {
    console.log('Client connected');

    ws.on('message', async (message) => {
      console.log('Received:', message);

      // TODO: call FastAPI with the message content
      // e.g., send question from chat to FastAPI
      ws.send(JSON.stringify({ answer: 'Mock answer from backend for: ' + message }));
    });

    ws.on('close', () => {
      console.log('Client disconnected');
    });
  });
}

module.exports = setupWebSocket;