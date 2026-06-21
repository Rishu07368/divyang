const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// List of government schemes
const SCHEMES = [
  {
    name: "Disability Pension Scheme",
    agency: "Central Government",
    description: "Monthly pension for persons with severe disabilities",
    benefits: ["₹300-500 per month", "Direct bank transfer"],
    eligibility: { disability_degree: ["SEVERE", "CRITICAL"], age_min: 18 },
    category: "financial"
  },
  {
    name: "ADIP (Assistance to Disabled Persons)",
    agency: "Ministry of Social Justice",
    description: "Free distribution of aids and appliances",
    benefits: ["Free wheelchairs", "Crutches", "Hearing aids", "Artificial limbs"],
    eligibility: { disability_degree: ["MILD", "MODERATE", "SEVERE", "CRITICAL"] },
    category: "assistive"
  },
  {
    name: "Scholarship for Students with Disabilities",
    agency: "Central Government",
    description: "Pre-matric and post-matric scholarships",
    benefits: ["₹500-1200 per month (pre-matric)", "₹750-1600 per month (post-matric)"],
    eligibility: { disability_degree: ["MILD", "MODERATE", "SEVERE", "CRITICAL"], age_max: 40 },
    category: "education"
  },
  {
    name: "Pradhan Mantri Disability Pension",
    agency: "Central Government",
    description: "Direct benefit transfer for persons with severe disabilities",
    benefits: ["₹300-500 per month", "Direct bank transfer"],
    eligibility: { disability_degree: ["SEVERE", "CRITICAL"], age_min: 18, age_max: 79 },
    category: "financial"
  },
  {
    name: "UP Disability Pension",
    agency: "Uttar Pradesh Government",
    description: "State-funded monthly pension for persons with disabilities",
    benefits: ["₹500-1000 per month", "Quarterly payment"],
    eligibility: { disability_degree: ["SEVERE", "CRITICAL"], state: "Uttar Pradesh" },
    category: "financial"
  },
  {
    name: "UP Free Education Scheme",
    agency: "Uttar Pradesh Government",
    description: "Free education from class 1 to PhD",
    benefits: ["Free education", "Free books", "Free uniform", "Scholarship for higher studies"],
    eligibility: { disability_degree: ["MILD", "MODERATE", "SEVERE", "CRITICAL"], age_max: 35 },
    category: "education"
  },
  {
    name: "Health Insurance (Ayushman Bharat)",
    agency: "Ayushman Bharat - Central",
    description: "Free health coverage under PMJAY",
    benefits: ["₹5 lakh coverage per family", "Cashless treatment"],
    eligibility: { all: true },
    category: "healthcare"
  }
];

// Get all schemes
router.get('/schemes', (req, res) => {
  res.json({
    success: true,
    count: SCHEMES.length,
    data: SCHEMES
  });
});

// Get schemes by category
router.get('/schemes/:category', (req, res) => {
  const { category } = req.params;
  const filtered = SCHEMES.filter(s => s.category === category);
  
  res.json({
    success: true,
    count: filtered.length,
    data: filtered
  });
});

// Get welfare recommendations
router.get('/recommendations', (req, res) => {
  try {
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/welfare_recommendations.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Welfare recommendations not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const recommendations = [];
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      recommendations.push(row);
    }

    res.json({
      success: true,
      count: recommendations.length,
      data: recommendations
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get recommendations for a specific beneficiary
router.get('/recommendations/:id', (req, res) => {
  try {
    const { id } = req.params;
    const dataPath = path.join(__dirname, '../../../frontend/public/data/processed/welfare_recommendations.csv');
    
    if (!fs.existsSync(dataPath)) {
      return res.status(404).json({
        success: false,
        error: 'Welfare recommendations not found'
      });
    }

    const csv = fs.readFileSync(dataPath, 'utf8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    let recommendation = null;
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      if (row.unique_id === id || row.Unique_ID === id) {
        recommendation = row;
        break;
      }
    }

    if (!recommendation) {
      return res.status(404).json({
        success: false,
        error: 'Recommendation not found'
      });
    }

    // Get matching schemes for this beneficiary
    const matchingSchemes = SCHEMES.filter(scheme => {
      if (scheme.eligibility.all) return true;
      if (scheme.eligibility.disability_degree && 
          scheme.eligibility.disability_degree.includes(recommendation.disability_degree?.toUpperCase())) {
        return true;
      }
      return false;
    });

    res.json({
      success: true,
      beneficiary: recommendation,
      eligible_schemes: matchingSchemes
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;