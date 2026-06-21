const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');

// Import routes
const uploadRoutes = require('./routes/upload');
const analyticsRoutes = require('./routes/analytics');
const beneficiaryRoutes = require('./routes/beneficiaries');
const welfareRoutes = require('./routes/welfare');
const insightsRoutes = require('./routes/insights');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static files for generated data
app.use('/data', express.static(path.join(__dirname, '../../frontend/public/data')));

// API Routes
app.use('/api/upload', uploadRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/beneficiaries', beneficiaryRoutes);
app.use('/api/welfare', welfareRoutes);
app.use('/api/insights', insightsRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// API Documentation
app.get('/api', (req, res) => {
  res.json({
    name: 'Disability Intelligence Platform API',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      upload: '/api/upload',
      analytics: '/api/analytics',
      beneficiaries: '/api/beneficiaries',
      welfare: '/api/welfare',
      insights: '/api/insights'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.message);
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal Server Error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Route not found'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║     Disability Intelligence Platform - Backend API      ║
╠══════════════════════════════════════════════════════════╣
║  Server running on http://localhost:${PORT}               ║
║                                                          ║
║  Endpoints:                                              ║
║  • GET  /api/health      - Health check                ║
║  • POST /api/upload      - Upload Excel file           ║
║  • GET  /api/analytics  - Dashboard data              ║
║  • GET  /api/beneficiaries - Beneficiary data          ║
║  • GET  /api/welfare     - Welfare recommendations     ║
║  • GET  /api/insights   - AI-generated insights       ║
╚══════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
