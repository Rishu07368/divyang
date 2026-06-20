# User Manual - Disability Intelligence Platform

## Introduction

The Disability Intelligence Platform is designed to help NGOs, schools, rehabilitation centers, and welfare offices analyze disability data and make informed decisions.

## Getting Started

### 1. Dashboard Overview

The dashboard consists of 6 main sections:
- **Dashboard**: Overview statistics and charts
- **Maps**: Interactive GIS visualizations
- **Analytics**: Detailed analysis and metrics
- **Welfare**: Scheme recommendations
- **Insights**: AI-generated recommendations
- **Planning**: Resource allocation and schedules

### 2. Understanding the Dashboard

#### Statistics Cards
- **Total Beneficiaries**: Total number of children in the system
- **Villages Covered**: Geographic coverage
- **High Priority Cases**: Number of severe/critical cases
- **Welfare Eligible**: Total scheme eligibility matches

#### Charts
- **Disability Distribution**: Pie chart showing types of disabilities
- **Severity Distribution**: Bar chart showing severity levels
- **Gender Distribution**: Pie chart by gender
- **Age Group Distribution**: Bar chart by age groups

### 3. Using the Maps

#### Beneficiary Map
- Each marker represents a beneficiary location
- Marker size indicates concentration
- Color indicates severity (green=mild, red=severe)

#### Heatmap
- Shows density of high-severity cases
- Red areas indicate concentrations of need

#### Village Summary
- Aggregated statistics per village
- Circle size indicates total beneficiaries

### 4. Welfare Recommendations

Each beneficiary is matched with eligible government schemes:

| Scheme Type | Description |
|-------------|-------------|
| Financial | Pension, grants, scholarships |
| Education | Free education, scholarships |
| Healthcare | Ayushman cards, health insurance |
| Assistive | Wheelchairs, hearing aids |
| Transport | Concessions, travel assistance |

### 5. AI Insights

The platform automatically generates insights:

| Priority | Meaning | Action Timeline |
|----------|---------|----------------|
| CRITICAL | Immediate attention required | Within 24 hours |
| HIGH | Urgent but not critical | Within 1 week |
| MEDIUM | Schedule for next visit | Within 1 month |
| LOW | Can be addressed later | When convenient |

### 6. Planning Tools

#### Intervention Zones
- Areas grouped by geographic proximity
- Priority scores based on beneficiary needs
- Resource requirements per zone

#### Camp Locations
- Recommended locations for rehabilitation camps
- Team composition suggestions
- Services needed at each location

#### Weekly Schedules
- Optimized field worker routes
- Daily visit plans
- Estimated travel times

## Common Tasks

### Finding a Specific Beneficiary
1. Navigate to the **Welfare** tab
2. Search by name or ID
3. View scheme eligibility

### Identifying High-Risk Cases
1. Go to **Insights** tab
2. Filter by CRITICAL or HIGH priority
3. Review recommendations

### Planning a Field Visit
1. Go to **Planning** tab
2. Review priority zones
3. Check weekly schedules
4. Note village details

### Checking Welfare Eligibility
1. Go to **Welfare** tab
2. Find the beneficiary
3. View their eligible schemes
4. Note required documents

## Tips

- **Refresh Data**: Run analytics pipeline to update data
- **Export**: Use browser print to PDF any view
- **Maps**: Click markers for detailed information
- **Charts**: Hover for exact values

## Need Help?

Contact your system administrator or refer to the Architecture documentation.