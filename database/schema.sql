-- Disability Intelligence Platform - Database Schema
-- PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Beneficiaries table
CREATE TABLE beneficiaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unique_id VARCHAR(50) UNIQUE NOT NULL,
    child_name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    disability_type VARCHAR(255),
    disability_degree VARCHAR(50),
    village VARCHAR(255),
    gram_panchayat VARCHAR(255),
    block VARCHAR(255),
    district VARCHAR(255),
    state VARCHAR(100) DEFAULT 'Bihar',
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Functional assessments table
CREATE TABLE functional_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    beneficiary_id UUID REFERENCES beneficiaries(id) ON DELETE CASCADE,
    domain VARCHAR(100),
    score INTEGER,
    max_score INTEGER DEFAULT 100,
    assessment_date DATE,
    assessor VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Severity assessments table
CREATE TABLE severity_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    beneficiary_id UUID REFERENCES beneficiaries(id) ON DELETE CASCADE,
    original_degree VARCHAR(50),
    inferred_level VARCHAR(50),
    severity_score DECIMAL(5,2),
    confidence DECIMAL(5,2),
    severity_factors TEXT,
    severity_reasoning TEXT,
    severity_recommendations TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Welfare recommendations table
CREATE TABLE welfare_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    beneficiary_id UUID REFERENCES beneficiaries(id) ON DELETE CASCADE,
    scheme_name VARCHAR(255),
    scheme_category VARCHAR(100),
    eligibility_status VARCHAR(50),
    has_required_documents BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Villages table
CREATE TABLE villages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    gram_panchayat VARCHAR(255),
    block VARCHAR(255),
    district VARCHAR(255),
    state VARCHAR(100) DEFAULT 'Bihar',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    beneficiary_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Intervention zones table
CREATE TABLE intervention_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_name VARCHAR(255) NOT NULL,
    zone_code VARCHAR(50),
    beneficiary_count INTEGER,
    priority_score DECIMAL(5,2),
    recommended_interventions TEXT,
    estimated_cost DECIMAL(12,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Insights table
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_id VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100),
    title VARCHAR(500),
    description TEXT,
    evidence TEXT,
    impact_score DECIMAL(5,2),
    confidence DECIMAL(5,2),
    urgency VARCHAR(20),
    affected_count INTEGER,
    location VARCHAR(255),
    recommendations TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Field visits table
CREATE TABLE field_visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    beneficiary_id UUID REFERENCES beneficiaries(id) ON DELETE SET NULL,
    village_id UUID REFERENCES villages(id) ON DELETE SET NULL,
    scheduled_date DATE,
    visit_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resource needs table
CREATE TABLE resource_needs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(100),
    quantity_needed INTEGER,
    current_available INTEGER DEFAULT 0,
    priority VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Upload logs table
CREATE TABLE upload_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename VARCHAR(255),
    file_size BIGINT,
    records_processed INTEGER,
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_beneficiaries_village ON beneficiaries(village);
CREATE INDEX idx_beneficiaries_disability ON beneficiaries(disability_type);
CREATE INDEX idx_beneficiaries_severity ON beneficiaries(disability_degree);
CREATE INDEX idx_assessments_beneficiary ON functional_assessments(beneficiary_id);
CREATE INDEX idx_severity_beneficiary ON severity_assessments(beneficiary_id);
CREATE INDEX idx_insights_urgency ON ai_insights(urgency);
CREATE INDEX idx_insights_category ON ai_insights(category);
CREATE INDEX idx_visits_date ON field_visits(scheduled_date);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_beneficiaries_updated_at
    BEFORE UPDATE ON beneficiaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();