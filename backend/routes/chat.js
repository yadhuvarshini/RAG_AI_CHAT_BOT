// POST /api/chat
const express = require('express');
const axios = require('axios');
const router = express.Router();

router.post('/', async (req, res) => {
  const { chat_name } = req.body;
  const token = req.headers.authorization;

  if (!token) {
    return res.status(401).json({ error: 'Token missing' });
  }

  try {
    const response = await axios.post('http://127.0.0.1:8000/chat', new URLSearchParams({ chat_name }), {
      headers: {
        'Authorization': token,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.response?.data?.detail || 'Chat creation failed' });
  }
});

// GET /api/chats
router.get('/all', async (req, res) => {
  const token = req.headers.authorization;

  if (!token) {
    return res.status(401).json({ error: 'Token missing' });
  }

  try {
    const response = await axios.get('http://127.0.0.1:8000/chats', {
      headers: { Authorization: token }
    });
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.response?.data?.detail || 'Failed to fetch chats' });
  }
});

// GET /api/chat-summary/:chat_id
router.get('/summary/:chat_id', async (req, res) => {
  const { chat_id } = req.params;

  try {
    const response = await axios.get(`http://127.0.0.1:8000/chat_summary/${chat_id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch summary' });
  }
});

module.exports = router;