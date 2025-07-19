// routes/auth.js

const express = require('express');
const axios = require('axios');
const router = express.Router();

// Signup route
router.post('/signup', async (req, res) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/auth/signup', req.body);
    res.json(response.data);
  } catch (err) {
    console.error('Signup error:', err.message);
    res.status(500).json({ error: 'Signup failed' });
  }
});

// Login route
router.post('/login', async (req, res) => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', req.body.username);
    formData.append('password', req.body.password);
    console.log('Username:', req.body.username);
    console.log('Password:', req.body.password);

    const response = await axios.post('http://127.0.0.1:8000/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    console.log('FastAPI response:', response.data);
    res.json(response.data);
    console.log('Login Sucess')
  } catch (err) {
    console.error('Full error:', err.response?.data || err.message);
    res.status(401).json({ error: 'Login failed' });
  }
});

module.exports = router;