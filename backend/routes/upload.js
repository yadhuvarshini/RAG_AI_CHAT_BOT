// routes/upload.js
const express = require('express');
// for file upload and storage
const multer = require('multer');
const path = require('path');

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
    const filePath = req.file.path;
    const response = await forwardToFastAPI(filePath);
    res.json({ success: true, fastApiResponse: response });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error processing file' });
  }
});

module.exports = router;