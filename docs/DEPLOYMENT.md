# Deployment Guide

## Disability Intelligence Platform - Deployment Guide

## Option 1: Static Dashboard Deployment (Recommended)

### Prerequisites
- Python 3.8+ for analytics
- Web browser for viewing dashboard
- Optional: Simple HTTP server

### Steps

1. **Install Analytics Dependencies**
```bash
cd /workspace/project/analytics
pip install -r requirements.txt
```

2. **Run Analytics Pipeline**
```bash
python run_analytics.py
```

3. **Serve Dashboard**
```bash
# Using Python's built-in server
cd /workspace/project/frontend/public
python -m http.server 8000

# Or using Node.js serve
npx serve .
```

4. **Access Dashboard**
Open browser to: http://localhost:8000

## Option 2: Full Stack Deployment

### Backend Setup

1. **Install Node.js Dependencies**
```bash
cd backend
npm install
```

2. **Set Environment Variables**
```bash
export DATABASE_URL=postgresql://user:pass@localhost/disability_db
export PORT=3000
```

3. **Start Backend**
```bash
npm start
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

## Option 3: Docker Deployment

### Dockerfile Example
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY analytics/ /app/analytics/
RUN pip install -r analytics/requirements.txt

CMD ["python", "analytics/run_analytics.py"]
```

### Build and Run
```bash
docker build -t disability-intelligence .
docker run -v /path/to/data:/data disability-intelligence
```

## Production Considerations

### Security
- Secure API endpoints with authentication
- Use HTTPS in production
- Implement role-based access control
- Sanitize all user inputs

### Scalability
- Use Redis for caching frequent queries
- Implement database indexing
- Use CDN for static assets
- Consider Kubernetes for auto-scaling

### Monitoring
- Set up logging (e.g., ELK stack)
- Implement health check endpoints
- Monitor error rates and latencies
- Set up alerts for critical issues

## Data Updates

### Manual Update
```bash
cd /workspace/project/analytics
python run_analytics.py
```

### Automated Update (Cron)
```bash
# Run daily at 2 AM
0 2 * * * cd /workspace/project && python analytics/run_analytics.py >> /var/log/analytics.log 2>&1
```

## Troubleshooting

### Analytics Pipeline Fails
1. Check Excel file format
2. Verify all required sheets exist
3. Check for data quality issues
4. Review logs in `/workspace/project/analytics/`

### Maps Not Loading
1. Ensure geo coordinates are available
2. Check browser console for errors
3. Verify internet connection for map tiles

### Dashboard Shows No Data
1. Run analytics pipeline first
2. Check browser console for fetch errors
3. Verify `dashboard_data.json` exists

## Support

For issues or questions:
1. Check the documentation in `/workspace/project/docs/`
2. Review the Architecture document
3. Check the Data Quality Report