// server.js
//setting up express server with websocket for real time communication
const express = require('express');
//for methods like post, get, we use post to send the question to fastapi and get to receive the answer
const http = require('http');
//for realtime communication inside this we use fastapi doing logi part
const WebSocket = require('ws');
//for file upload and storage
const path = require('path');
//for environment variables
const dotenv = require('dotenv');
//for cors
const cors = require('cors');

//to handle the file upload logic using multer
const uploadRoutes = require('./routes/upload');
//to create ws 
const setupWebSocket = require('./ws/socket');

const authRoutes = require('./routes/auth');

const chatRoutes = require('./routes/chat');

dotenv.config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// WebSocket setup
setupWebSocket(wss);

// CORS options
const corsOptions = {
  origin: ['http://localhost:5173', 'http://localhost:8000', 'http://localhost:8501', 'http://localhost:5500'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
app.options('*', cors(corsOptions)); // preflight support

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

//public accessiblity to uploads folder
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Error handling middleware
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    return res.status(400).json({
      error: 'File upload error',
      details: err.message
    });
  }
  next(err);
});

// Routes
app.use('/api/upload', uploadRoutes);

app.use('/auth', authRoutes);

app.use('/api/chat', chatRoutes); // handles /chat, /chats/all, /summary/:chat_id

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});