const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// Get all beneficiaries
router.get('/', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/basic_info.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Beneficiary data not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const beneficiaries = [];
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      beneficiaries.push(row);
    }

    res.json({
      success: true,
      count: beneficiaries.length,
      data: beneficiaries
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get beneficiary by ID
router.get('/:id', (req, res) => {
  try {
    const { id } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/merged.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Beneficiary data not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    let beneficiary = null;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      if (row.unique_id === id || row.Unique_ID === id) {
        beneficiary = row;
        break;
      }
    }

    if (!beneficiary) {
      return res.status(404).json({
        success: false,
        error: 'Beneficiary not found'
      });
    }

    res.json({
      success: true,
      data: beneficiary
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Search beneficiaries
router.get('/search/:query', (req, res) => {
  try {
    const { query } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/basic_info.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Beneficiary data not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const results = [];
    const searchLower = query.toLowerCase();
    
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      
      // Search in name, village, unique_id
      const name = (row.child_name || row['Child name'] || '').toLowerCase();
      const village = (row.village || '').toLowerCase();
      const uid = (row.unique_id || row.Unique_ID || '').toLowerCase();
      
      if (name.includes(searchLower) || village.includes(searchLower) || uid.includes(searchLower)) {
        results.push(row);
      }
    }

    res.json({
      success: true,
      query,
      count: results.length,
      data: results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get severity assessments
router.get('/severity/all', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/severity_assessments.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Severity data not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const assessments = [];
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      assessments.push(row);
    }

    res.json({
      success: true,
      count: assessments.length,
      data: assessments
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;