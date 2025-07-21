const axios = require('axios');
const FormData = require('form-data');

function setupWebSocket(wss) {
  wss.on('connection', (ws) => {
    console.log('✅ Client connected');

    ws.on('message', async (message) => {
      console.log('📩 Received message:', message.toString());
      let fullAnswer = ''; // Moved inside message handler

      try {
        const parsed = JSON.parse(message.toString());
        const { question, token, chat_id } = parsed;

        const form = new FormData();
        form.append('question', question);
        form.append('chat_id', chat_id);

        const headers = {
          ...form.getHeaders(),
          Authorization: `Bearer ${token}`
        };

        console.log('🚀 Sending to FastAPI:', { question });
        const res = await axios.post('http://127.0.0.1:8000/ask', form, {
          headers,
          responseType: 'stream'
        });

        res.data.on('data', (chunk) => {
          try {
            const data = JSON.parse(chunk.toString());
            console.log('📥 Received chunk:', data); // Debug each chunk
            
            if (data.content) {
              fullAnswer += data.content;
              ws.send(JSON.stringify({
                type: 'partial',
                chunk: data.content,
                debug: `Chunk ${Date.now()}` // For debugging
              }));
            }
          } catch (e) {
            console.error('❌ Chunk parse error:', e);
          }
        });

        res.data.on('end', () => {
          console.log('🏁 Stream complete. Full answer:', fullAnswer);
          ws.send(JSON.stringify({
            type: 'complete',
            question: question,
            answer: fullAnswer,
            debug: `Complete ${Date.now()}`
          }));
        });

        res.data.on('error', (err) => {
          console.error('🔴 Stream error:', err);
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Stream error'
          }));
        });

      } catch (err) {
        console.error('💥 Main error:', err);
        ws.send(JSON.stringify({
          type: 'error',
          message: err.message,
          stack: err.stack // For debugging
        }));
      }
    });

    ws.on('close', () => {
      console.log('❌ Client disconnected');
    });
  });
}

module.exports = setupWebSocket;