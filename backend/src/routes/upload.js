const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);
const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../../../analytics/uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, `irp-data-${uniqueSuffix}.xlsx`);
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ];
    if (allowedTypes.includes(file.mimetype) || file.originalname.endsWith('.xlsx') || file.originalname.endsWith('.xls')) {
      cb(null, true);
    } else {
      cb(new Error('Only Excel files (.xlsx, .xls) are allowed'));
    }
  }
});

// Upload and process endpoint
router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded'
      });
    }

    const filePath = req.file.path;
    console.log('File uploaded:', filePath);

    // Run analytics pipeline
    const analyticsDir = path.join(__dirname, '../../../analytics');
    const outputDir = path.join(__dirname, '../../../frontend/public/data');

    // Update the run_analytics.py to accept file path as argument
    // For now, copy the uploaded file to the expected location
    const targetPath = path.join(analyticsDir, 'IRP_data.xlsx');
    fs.copyFileSync(filePath, targetPath);

    // Run the analytics pipeline
    try {
      await execAsync(`cd ${analyticsDir} && python run_analytics.py`, { timeout: 120000 });
      console.log('Analytics pipeline completed');
    } catch (execError) {
      console.error('Analytics pipeline error:', execError.message);
      // Continue even if analytics fails - data might already exist
    }

    // Read generated dashboard data
    const dashboardPath = path.join(outputDir, 'dashboard_data.json');
    let dashboardData = null;
    if (fs.existsSync(dashboardPath)) {
      dashboardData = JSON.parse(fs.readFileSync(dashboardPath, 'utf8'));
    }

    res.json({
      success: true,
      message: 'File processed successfully',
      records_processed: dashboardData?.summary?.total_beneficiaries || 0,
      file: req.file.originalname,
      data_path: '/data/dashboard_data.json'
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get upload status
router.get('/status', (req, res) => {
  const uploadsDir = path.join(__dirname, '../../../analytics/uploads');
  const outputDir = path.join(__dirname, '../../../frontend/public/data');
  
  const files = fs.existsSync(uploadsDir) 
    ? fs.readdirSync(uploadsDir).map(f => ({
        name: f,
        size: fs.statSync(path.join(uploadsDir, f)).size,
        uploaded: fs.statSync(path.join(uploadsDir, f)).mtime
      }))
    : [];

  const hasDashboard = fs.existsSync(path.join(outputDir, 'dashboard_data.json'));

  res.json({
    success: true,
    uploaded_files: files,
    has_analytics_data: hasDashboard
  });
});

module.exports = router;
