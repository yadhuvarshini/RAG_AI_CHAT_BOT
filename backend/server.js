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

//to handle the file upload logic using multer
const uploadRoutes = require('./routes/upload');
//to create ws 
const setupWebSocket = require('./ws/socket');

dotenv.config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// WebSocket setup
setupWebSocket(wss);

// Middleware
app.use(express.json());

//public accessiblity to uploads folder
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Routes
app.use('/api/upload', uploadRoutes);

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});