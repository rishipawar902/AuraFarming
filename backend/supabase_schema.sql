-- AuraFarming Database Schema
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

-- Enable Row Level Security (recommended for production)
ALTER TABLE farmers ENABLE ROW LEVEL SECURITY;
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for farmers (they can only access their own data)
CREATE POLICY "Farmers can view own profile" ON farmers
    FOR SELECT USING (auth.uid() = id::uuid);

CREATE POLICY "Farmers can update own profile" ON farmers
    FOR UPDATE USING (auth.uid() = id::uuid);

-- Create policies for farms
CREATE POLICY "Farmers can view own farms" ON farms
    FOR ALL USING (farmer_id IN (SELECT id FROM farmers WHERE auth.uid() = id::uuid));

-- Create policies for recommendations
CREATE POLICY "Farmers can view own recommendations" ON recommendations
    FOR ALL USING (farm_id IN (SELECT id FROM farms WHERE farmer_id IN (SELECT id FROM farmers WHERE auth.uid() = id::uuid)));

-- Create policies for crops history
CREATE POLICY "Farmers can view own crops history" ON crops_history
    FOR ALL USING (farm_id IN (SELECT id FROM farms WHERE farmer_id IN (SELECT id FROM farmers WHERE auth.uid() = id::uuid)));

-- Insert some demo data (optional)
INSERT INTO farmers (id, name, phone, password, language) VALUES 
('demo-farmer-123', 'Demo Farmer', '9876543210', 'hashed_password_demo', 'english')
ON CONFLICT (phone) DO NOTHING;

INSERT INTO farms (id, farmer_id, name, location, soil_type, irrigation_method, field_size) VALUES 
('demo-farm-456', 'demo-farmer-123', 'Demo Farm', 
'{"latitude": 23.3441, "longitude": 85.3096, "district": "Ranchi", "village": "Demo Village"}', 
'loam', 'drip', 2.5)
ON CONFLICT (id) DO NOTHING;