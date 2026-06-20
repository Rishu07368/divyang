# Disability Intelligence Platform

A comprehensive data analytics platform for disability welfare programs in India.

## Overview

This platform transforms raw IRP (Individual Rehabilitation Plan) data from NGOs, schools, and welfare offices into actionable intelligence for decision-making.

## Features

- **Disability Analytics**: Comprehensive analysis of disability types, severity, and distribution
- **Severity Assessment**: Intelligent severity scoring based on functional assessments
- **GIS Mapping**: Interactive maps showing beneficiary locations and severity heatmaps
- **Welfare Recommendations**: Matching beneficiaries with eligible government schemes
- **Resource Allocation**: Optimized intervention zone planning
- **Field Worker Intelligence**: Route optimization and visit planning
- **AI Insights**: Automated detection of high-risk populations and service gaps

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+ (optional for full stack)
- PostgreSQL (optional for database)

### 1. Install Dependencies
```bash
cd analytics
pip install -r requirements.txt
```

### 2. Run Analytics Pipeline
```bash
python run_analytics.py
```

### 3. View Dashboard
Open `frontend/public/index.html` in a browser, or serve it with any HTTP server.

## Project Structure

```
disability-intelligence-platform/
├── analytics/              # Python analytics engine
│   ├── data_processor.py   # Excel data ingestion
│   ├── severity_engine.py # Severity assessment
│   ├── gis_engine.py      # GIS mapping
│   ├── welfare_engine.py    # Scheme recommendations
│   ├── resource_allocation.py  # Resource planning
│   ├── field_worker_intelligence.py  # Route optimization
│   ├── ai_insights.py      # AI-generated insights
│   └── run_analytics.py     # Main pipeline
├── frontend/
│   └── public/
│       ├── index.html      # Dashboard UI
│       └── data/           # Generated analytics data
├── database/               # Database schemas
├── docs/                   # Documentation
└── ARCHITECTURE.md         # System architecture
```

## Data Format

The platform expects IRP (Individual Rehabilitation Plan) data in Excel format with the following sheets:
- Basic Info: Child demographics and family information
- Functional Assessment: Multi-domain functional evaluation
- Education Schemes Referral: School and education support
- IRP Goals: Rehabilitation goals and priorities
- Intervention Plan: Service interventions

## Generated Outputs

After running the pipeline:
- `processed/*.csv` - Cleaned and standardized data
- `processed/severity_assessments.csv` - Severity scores for all beneficiaries
- `processed/welfare_recommendations.csv` - Scheme eligibility
- `maps/*.html` - Interactive maps
- `reports/ai_insights_report.txt` - AI-generated insights
- `dashboard_data.json` - Dashboard data

## API (Optional)

For full API functionality:
```bash
cd backend
npm install
npm start
```

## License

MIT License - See LICENSE file for details