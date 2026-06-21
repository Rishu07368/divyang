# Disability Intelligence Platform - Backend

Node.js/Express backend API for the Disability Intelligence Platform.

## Features

- RESTful API for analytics data
- File upload and processing
- Beneficiary data management
- Welfare scheme recommendations
- AI insights endpoints
- Health check endpoints

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express.js
- **File Processing**: Multer, xlsx
- **Database**: PostgreSQL (optional)
- **Logging**: Morgan

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Python 3.8+ (for analytics pipeline)

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev

# Or for production
npm start
```

The API will be available at [http://localhost:3001](http://localhost:3001).

## API Endpoints

### Health Check
```
GET /api/health
```

### Upload Data
```
POST /api/upload
```
Upload an Excel (.xlsx) file for processing.

### Analytics
```
GET /api/analytics/dashboard    - Get dashboard data
GET /api/analytics/summary      - Get summary statistics
GET /api/analytics/distribution/:type - Get distribution data
GET /api/analytics/resources     - Get resource needs
```

### Beneficiaries
```
GET /api/beneficiaries          - Get all beneficiaries
GET /api/beneficiaries/:id       - Get beneficiary by ID
GET /api/beneficiaries/search/:query - Search beneficiaries
GET /api/beneficiaries/severity/all - Get all severity assessments
```

### Welfare
```
GET /api/welfare/schemes              - List all schemes
GET /api/welfare/schemes/:category    - Schemes by category
GET /api/welfare/recommendations      - Get all recommendations
GET /api/welfare/recommendations/:id  - Get recommendations for beneficiary
```

### Insights
```
GET /api/insights               - Get all insights
GET /api/insights/summary       - Get insights summary
GET /api/insights/priority      - Get high-priority insights
GET /api/insights/urgency/:level - Get by urgency level
GET /api/insights/category/:cat - Get by category
```

## Project Structure

```
backend/
├── src/
│   ├── index.js          # Main entry point
│   ├── routes/           # API routes
│   │   ├── upload.js
│   │   ├── analytics.js
│   │   ├── beneficiaries.js
│   │   ├── welfare.js
│   │   └── insights.js
│   ├── services/         # Business logic
│   ├── middleware/       # Express middleware
│   └── config/           # Configuration
├── package.json
└── .env.example
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `3001` |
| `NODE_ENV` | Environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `52428800` |
| `CORS_ORIGIN` | Allowed CORS origin | `http://localhost:3000` |

## Response Format

All API responses follow this format:

### Success
```json
{
  "success": true,
  "data": { ... },
  "count": 100
}
```

### Error
```json
{
  "success": false,
  "error": "Error message"
}
```