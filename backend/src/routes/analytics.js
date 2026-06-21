const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// Get dashboard data
router.get('/dashboard', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/dashboard_data.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Dashboard data not found. Please upload a dataset first.'
      });
    }

    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    res.json({
      success: true,
      data
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get summary statistics
router.get('/summary', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/dashboard_data.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Dashboard data not found'
      });
    }

    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    res.json({
      success: true,
      data: {
        total_beneficiaries: data.summary.total_beneficiaries,
        villages_covered: Object.keys(data.village_distribution).length,
        disability_types: Object.keys(data.disability_distribution).length,
        severity_distribution: data.severity_distribution,
        key_metrics: data.key_metrics
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get distribution data
router.get('/distribution/:type', (req, res) => {
  try {
    const { type } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/dashboard_data.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Dashboard data not found'
      });
    }

    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    const distributions = {
      disability: data.disability_distribution,
      severity: data.severity_distribution,
      gender: data.summary.by_gender,
      age_group: data.summary.by_age_group,
      social_status: data.summary.by_social_status,
      village: data.village_distribution
    };

    if (!distributions[type]) {
      return res.status(400).json({
        success: false,
        error: 'Invalid distribution type'
      });
    }

    res.json({
      success: true,
      data: distributions[type]
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get resource needs
router.get('/resources', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/dashboard_data.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Dashboard data not found'
      });
    }

    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    res.json({
      success: true,
      data: data.resource_needs
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;