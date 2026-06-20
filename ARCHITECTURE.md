# Disability Intelligence Platform - Architecture Document

## Repository Inventory

### Current State
- **Repository**: Empty Git repository at `/workspace/project`
- **Primary Dataset**: `IRP_ash&alam (5).xlsx` - IRP (Individual Rehabilitation Plan) assessment data

### Excel Workbook Structure

| Sheet | Rows | Columns | Purpose |
|-------|------|---------|---------|
| 00_Code_Lists | 58 | 6 | Reference codes, difficulty scales, dropdown values |
| 01_Basic_Info | 197 | 33 | Child demographics, family info, location, contact |
| 02_Functional_Assessment | 197 | 21 | Functional domains: movement, self-care, communication, etc. |
| 03_Education_Schemes_Referral | 197 | 12 | School enrollment, schemes, referrals |
| 04_IRP_Goals | 197 | 21 | Family/child priorities, short/medium/long-term goals |
| 05_Intervention_Plan | 197 | 12 | Intervention fields, aims, responsible persons |
| 06_Home_Centre_Program | 289 | 15 | Daily tasks, positioning, exercises, strategies |
| 07_Progress_Notes | 289 | 9 | Progress tracking, plan changes |
| 08_Signatures | 197 | 12 | Multi-disciplinary team sign-offs |

## Dataset Relationship Map

```
CHILDREN (01_Basic_Info)
    │
    ├── FUNCTIONAL_ASSESSMENT (02) [1:1 by Unique ID]
    │       └── Movement, Learning, Communication, etc.
    │
    ├── EDUCATION_SCHEMES (03) [1:1 by Unique ID]
    │       └── School type, enrollment status, referral info
    │
    ├── IRP_GOALS (04) [1:1 by Unique ID]
    │       └── Family priorities, Child priorities
    │       └── Short/Medium/Long-term rehabilitation goals
    │
    ├── INTERVENTION_PLANS (05) [1:N by Unique ID]
    │       └── Multiple interventions per child
    │
    ├── HOME_CENTRE_PROGRAM (06) [1:N by Unique ID]
    │       └── Daily tasks, exercises, strategies
    │
    ├── PROGRESS_NOTES (07) [1:N by Unique ID]
    │       └── Follow-up progress tracking
    │
    └── SIGNATURES (08) [1:1 by Unique ID]
            └── CBR Worker, Physiotherapist, Special Educator, Speech Therapist
```

## Entity Relationships

### Primary Entities
1. **Child/Beneficiary** - Core entity with 197 records
2. **Family** - Associated with children
3. **Village/Location** - Geographic hierarchy
4. **Disability** - Type and degree
5. **Assessment** - Functional evaluation
6. **Goal** - Rehabilitation targets
7. **Intervention** - Treatment plans
8. **Service Provider** - CBR Workers, Therapists, Educators

## Data Quality Assessment (Pre-Audit)

### Known Issues
- Header rows with Hindi text in first data row
- Missing values across all sheets (5-60%)
- Duplicate rows in intervention/notes sheets
- Some columns with inconsistent data (phone numbers)
- Block information missing for ~22 records

### Completeness by Sheet
| Sheet | Estimated Data Quality |
|-------|----------------------|
| 01_Basic_Info | ~75% complete |
| 02_Functional_Assessment | ~70% complete |
| 03_Education_Schemes | ~50% complete |
| 04_IRP_Goals | ~60% complete |
| 05-08 | ~20-40% complete (follow-up data) |

## System Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  Next.js 14 + React 18 + TypeScript + TailwindCSS + Recharts   │
│  Leaflet Maps, D3.js Charts, Radix UI Components               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND                                   │
│  Node.js + Express + TypeScript                                 │
│  REST API + WebSocket for real-time updates                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYTICS ENGINE                             │
│  Python + Pandas + GeoPandas + Scikit-Learn                     │
│  ML Models, Severity Inference, Welfare Recommendations         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE                                   │
│  PostgreSQL with PostGIS extension                              │
│  TimescaleDB for time-series data                               │
└─────────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
disability-intelligence-platform/
├── frontend/                    # Next.js application
│   ├── app/                     # App router pages
│   ├── components/              # React components
│   │   ├── dashboard/           # Dashboard widgets
│   │   ├── maps/                # GIS components
│   │   ├── charts/              # Analytics charts
│   │   └── forms/               # Data entry forms
│   ├── lib/                     # Utilities
│   └── public/                  # Static assets
│
├── backend/                     # Node.js API
│   ├── src/
│   │   ├── controllers/         # Route handlers
│   │   ├── services/            # Business logic
│   │   ├── models/              # Data models
│   │   ├── routes/              # API routes
│   │   └── middleware/          # Express middleware
│   └── package.json
│
├── analytics/                   # Python ML engine
│   ├── data/                    # Data processing
│   ├── models/                  # ML model definitions
│   ├── scripts/                 # ETL pipelines
│   └── notebooks/               # Analysis notebooks
│
├── database/                    # PostgreSQL schema
│   ├── migrations/              # Alembic migrations
│   └── seeds/                   # Reference data
│
└── docs/                        # Documentation
    ├── user-manual.md
    ├── admin-manual.md
    └── deployment-guide.md
```

## API Design

### Core Endpoints

#### Beneficiaries
- `GET /api/beneficiaries` - List all beneficiaries
- `GET /api/beneficiaries/:id` - Get beneficiary details
- `POST /api/beneficiaries` - Create beneficiary
- `PUT /api/beneficiaries/:id` - Update beneficiary

#### Analytics
- `GET /api/analytics/summary` - Dashboard summary stats
- `GET /api/analytics/disabilities` - Disability distribution
- `GET /api/analytics/geographic` - Geographic aggregations
- `GET /api/analytics/trends` - Time-series trends

#### Intelligence
- `GET /api/intelligence/severity` - Severity assessment
- `GET /api/intelligence/recommendations` - Welfare schemes
- `GET /api/intelligence/allocations` - Resource allocation
- `GET /api/intelligence/insights` - AI-generated insights

#### Maps
- `GET /api/maps/beneficiaries` - GeoJSON beneficiary data
- `GET /api/maps/clusters` - Cluster analysis results
- `GET /api/maps/heatmaps` - Density heatmap data

## Implementation Roadmap

### Phase 1: Foundation (Milestones 1-3)
- [ ] Milestone 1: Project Setup
- [ ] Milestone 2: Data Ingestion Pipeline
- [ ] Milestone 3: Basic API & Dashboard

### Phase 2: Core Intelligence (Milestones 4-6)
- [ ] Milestone 4: Disability Intelligence Engine
- [ ] Milestone 5: Severity Engine
- [ ] Milestone 6: GIS Mapping

### Phase 3: Advanced Analytics (Milestones 7-9)
- [ ] Milestone 7: Analytics Suite
- [ ] Milestone 8: Welfare Recommendations
- [ ] Milestone 9: Resource Allocation

### Phase 4: Field Operations (Milestones 10-11)
- [ ] Milestone 10: Field Worker Intelligence
- [ ] Milestone 11: AI Insights

### Phase 5: Deployment (Milestone 12)
- [ ] Milestone 12: Production Deployment

## Geographic Coverage

Based on dataset analysis:
- **State**: Uttar Pradesh (inferred)
- **Districts**: Bahraich (inferred)
- **Blocks**: Brahmpur
- **Villages**: Hariyar, Bahabar, others
- **Gram Panchayats**: Hariyar, Lalapur, Bahapur

## Disability Types Identified
1. Speech and Language
2. Muscular Dystrophy
3. Intellectual Disability
4. Cerebral Palsy
5. Hearing Impairment
6. Visual Impairment
7. Multiple Disabilities

## Severity Levels
- Mild
- Moderate
- Severe
- Critical (to be inferred)

## Next Steps
1. Initialize project structure
2. Set up development environment
3. Implement data ingestion
4. Build core APIs
5. Create dashboard