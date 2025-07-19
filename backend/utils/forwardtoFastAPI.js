// utils/forwardToFastAPI.js
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

async function forwardToFastAPI(filePath, token) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));

  const res = await axios.post('http://127.0.0.1:8000/process', form, {
    headers: form.getHeaders(),
    headers: {
      accessiblityuthorization: ` Bearer ${token}`
    }
  });

  return res.data;
}

module.exports = forwardToFastAPI;