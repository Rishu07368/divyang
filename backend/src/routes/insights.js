const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// Get all insights
router.get('/', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/ai_insights.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Insights data not found'
      });
    }

    const insights = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    res.json({
      success: true,
      count: insights.length,
      data: insights
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get insights by urgency
router.get('/urgency/:level', (req, res) => {
  try {
    const { level } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/ai_insights.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Insights data not found'
      });
    }

    const insights = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const filtered = insights.filter(i => i.urgency.toUpperCase() === level.toUpperCase());
    
    res.json({
      success: true,
      count: filtered.length,
      urgency: level.toUpperCase(),
      data: filtered
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get insights by category
router.get('/category/:category', (req, res) => {
  try {
    const { category } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/ai_insights.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Insights data not found'
      });
    }

    const insights = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const filtered = insights.filter(i => 
      i.category.toLowerCase().includes(category.toLowerCase())
    );
    
    res.json({
      success: true,
      count: filtered.length,
      category,
      data: filtered
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get insights summary
router.get('/summary', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/ai_insights.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Insights data not found'
      });
    }

    const insights = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    // Calculate summary
    const byUrgency = {};
    const byCategory = {};
    let totalAffected = 0;
    let avgImpact = 0;
    
    insights.forEach(insight => {
      byUrgency[insight.urgency] = (byUrgency[insight.urgency] || 0) + 1;
      byCategory[insight.category] = (byCategory[insight.category] || 0) + 1;
      totalAffected += insight.affected_count;
      avgImpact += insight.impact_score;
    });
    
    avgImpact = insights.length > 0 ? (avgImpact / insights.length).toFixed(1) : 0;
    
    res.json({
      success: true,
      summary: {
        total_insights: insights.length,
        by_urgency: byUrgency,
        by_category: byCategory,
        total_affected: totalAffected,
        average_impact: parseFloat(avgImpact),
        critical_count: byUrgency['CRITICAL'] || 0,
        high_count: byUrgency['HIGH'] || 0
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get high priority insights (CRITICAL and HIGH)
router.get('/priority', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/ai_insights.json');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Insights data not found'
      });
    }

    const insights = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    const priority = insights.filter(i => 
      i.urgency === 'CRITICAL' || i.urgency === 'HIGH'
    ).sort((a, b) => {
      if (a.urgency === 'CRITICAL' && b.urgency !== 'CRITICAL') return -1;
      if (b.urgency === 'CRITICAL' && a.urgency !== 'CRITICAL') return 1;
      return b.impact_score - a.impact_score;
    });
    
    res.json({
      success: true,
      count: priority.length,
      data: priority
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;