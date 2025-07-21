// routes/upload.js
const express = require('express');
// for file upload and storage
const multer = require('multer');
const path = require('path');
const fs = require('fs/promises');


// to forward the file to FastAPI
const forwardToFastAPI = require('../utils/forwardToFastAPI');
const router = express.Router();

// Set up multer
const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => {
    const filename = Date.now() + path.extname(file.originalname);
    cb(null, filename);
  }
});
const upload = multer({ storage });

router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;
    const authHeader = req.headers.authorization;
    const chat_id = req.body.chat_id;
    

    if (!authHeader || !authHeader.startsWith('Bearer')){
      return res.status(401).json({error: 'Unauthorized. Token missing or Invalid'})
    }

    if (!chat_id) {
      return res.status(400).json({ error: 'chat_id is required' });
    }

    const token = authHeader.split(' ')[1];
    const response = await forwardToFastAPI(filePath,token,chat_id);

    await fs.unlink(filePath);

    res.json({ success: true, fastApiResponse: response });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error processing file' });
  }
});

module.exports = router;