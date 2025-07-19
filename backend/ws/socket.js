const axios = require('axios')

function setupWebSocket(wss) {
  wss.on('connection', (ws) => {
    console.log('Client connected');

    ws.on('message', async (message) => {
      console.log('Received:', message);
      const question = message.toString().trim();
      console.log('Question:', question);

      try {
        
        const res = await axios.post('http://127.0.0.1:8000/ask', new URLSearchParams({question}), {
            headers: {
                'content-type':'application/x-www-form-urlencoded'
            }
        });

        const geminiAnswer = res.data.gemini_answer || "No answer from gemini";

        ws.send(JSON.stringify({ 
            type: 'answer',
            question,
            answer: geminiAnswer
        }));

      } catch(err) {
        console.log("fastapi error", err.message);
        ws.send(JSON.stringify({
          type: 'error',
          message: err && err.message ? err.message : 'unknown error'
        }));
      }
    });

    ws.on('close', () => {
      console.log('Client disconnected');
    });
  });
}

module.exports = setupWebSocket;