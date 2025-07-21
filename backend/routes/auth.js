// backend/routes/auth.js (Node.js Auth with JWT)
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const mongoose = require('mongoose');
const { MongoClient } = require('mongodb');
require('dotenv').config();

const router = express.Router();

const MONGO_URI = process.env.MONGO_DB_URI;
const SECRET_KEY = process.env.SECRET_KEY;

const client = new MongoClient(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  tls: true, // optional, but okay to include
});

let usersCollection;

(async () => {
  try {
    await client.connect();
    const db = client.db(); // Uses default DB from URI
    usersCollection = db.collection('users');
  } catch (e) {
    console.error('MongoDB connection error:', e);
  }
})();

// Signup
router.post('/signup', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: 'All fields required' });
    }

    const existing = await usersCollection.findOne({ email });
    if (existing) return res.status(400).json({ error: 'Email already exists' });

    const hashedPassword = await bcrypt.hash(password, 10);
    await usersCollection.insertOne({ username, email, hashed_password: hashedPassword });

    const token = jwt.sign({ sub: email }, SECRET_KEY, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ error: 'Signup failed' });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await usersCollection.findOne({ email });
    if (!user) return res.status(400).json({ error: 'Invalid credentials' });

    const isValid = await bcrypt.compare(password, user.hashed_password);
    if (!isValid) return res.status(400).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ sub: email }, SECRET_KEY, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Login failed' });
  }
});

module.exports = router;