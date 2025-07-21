// utils/forwardToFastAPI.js
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

async function forwardToFastAPI(filePath, token, chat_id) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('chat_id', chat_id);

  console.log("Forwarding to FastAPI with token:", token); // Debug log

  try {
    const response = await axios.post('http://localhost:8000/process', form, {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      },
      timeout: 30000
    });
    return response.data;
  } catch (error) {
    console.error('Forwarding error:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers
    });
    throw error;
  }
}

module.exports = forwardToFastAPI;

