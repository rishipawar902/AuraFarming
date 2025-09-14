-- AuraFarming Database Schema (Simplified)
-- Run this in Supabase SQL Editor

-- Create farmers table
CREATE TABLE IF NOT EXISTS farmers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    language VARCHAR(20) DEFAULT 'english',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create farms table
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID REFERENCES farmers(id) ON DELETE CASCADE,
    name VARCHAR(100),
    location JSONB NOT NULL,
    soil_type VARCHAR(50) NOT NULL,
    irrigation_method VARCHAR(50) NOT NULL,
    field_size DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    crops JSONB NOT NULL,
    model_confidence DECIMAL(5,4),
    season VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create crops history table
CREATE TABLE IF NOT EXISTS crops_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    crop VARCHAR(50) NOT NULL,
    planting_date DATE,
    harvest_date DATE,
    yield_amount DECIMAL(10,2),
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES farmers(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert some demo data (optional)
INSERT INTO farmers (name, phone, password, language) VALUES 
('Demo Farmer', '9876543210', 'hashed_password_demo', 'english')
ON CONFLICT (phone) DO NOTHING;

-- Get the farmer ID for the farm insert
-- Note: You'll need to run this separately after the farmer is created
-- INSERT INTO farms (farmer_id, name, location, soil_type, irrigation_method, field_size) 
-- SELECT id, 'Demo Farm', 
-- '{"latitude": 23.3441, "longitude": 85.3096, "district": "Ranchi", "village": "Demo Village"}', 
-- 'loam', 'drip', 2.5
-- FROM farmers WHERE phone = '9876543210';