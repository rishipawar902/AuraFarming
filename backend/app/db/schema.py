"""
Database schema creation script for Supabase.
This file contains SQL commands to create the database schema.
"""

# SQL commands to create tables in Supabase
CREATE_TABLES_SQL = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Farmers table
CREATE TABLE IF NOT EXISTS farmers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Farms table
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_id UUID NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    location JSONB NOT NULL,
    soil_type TEXT NOT NULL,
    irrigation_method TEXT NOT NULL,
    field_size DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crops history table
CREATE TABLE IF NOT EXISTS crops_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    season TEXT NOT NULL,
    crop TEXT NOT NULL,
    yield_per_acre DECIMAL(10,2),
    year INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    recommended_crops JSONB,
    rotation_plan JSONB,
    sustainability_score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table for federated learning
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    update_hash TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    previous_hash TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers(phone);
CREATE INDEX IF NOT EXISTS idx_farms_farmer_id ON farms(farmer_id);
CREATE INDEX IF NOT EXISTS idx_crops_history_farm_id ON crops_history(farm_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_farm_id ON recommendations(farm_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_round ON audit_logs(round_number);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_farmers_updated_at BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farms_updated_at BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE farmers ENABLE ROW LEVEL SECURITY;
ALTER TABLE farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

-- Policy for farmers to access their own data
CREATE POLICY "Farmers can view own data" ON farmers
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Farmers can update own data" ON farmers
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Policy for farms
CREATE POLICY "Farmers can view own farms" ON farms
    FOR ALL USING (farmer_id::text = auth.uid()::text);

-- Policy for crops history
CREATE POLICY "Farmers can manage own crop history" ON crops_history
    FOR ALL USING (
        farm_id IN (
            SELECT id FROM farms WHERE farmer_id::text = auth.uid()::text
        )
    );

-- Policy for recommendations
CREATE POLICY "Farmers can view own recommendations" ON recommendations
    FOR SELECT USING (
        farm_id IN (
            SELECT id FROM farms WHERE farmer_id::text = auth.uid()::text
        )
    );

-- Public read access for audit logs (transparency)
CREATE POLICY "Public can view audit logs" ON audit_logs
    FOR SELECT USING (true);
"""

# Sample data insertion
SAMPLE_DATA_SQL = """
-- Insert sample districts data (for reference)
INSERT INTO districts (name, state) VALUES 
    ('Ranchi', 'Jharkhand'),
    ('Dhanbad', 'Jharkhand'),
    ('Bokaro', 'Jharkhand'),
    ('Deoghar', 'Jharkhand'),
    ('East Singhbhum', 'Jharkhand'),
    ('West Singhbhum', 'Jharkhand'),
    ('Hazaribagh', 'Jharkhand'),
    ('Giridih', 'Jharkhand'),
    ('Palamu', 'Jharkhand'),
    ('Chatra', 'Jharkhand')
ON CONFLICT DO NOTHING;

-- Insert sample crops data
INSERT INTO crops (name, category, season, water_requirement) VALUES 
    ('Rice', 'Cereal', 'Kharif', 'High'),
    ('Wheat', 'Cereal', 'Rabi', 'Medium'),
    ('Maize', 'Cereal', 'Kharif', 'Medium'),
    ('Arhar', 'Pulse', 'Kharif', 'Low'),
    ('Moong', 'Pulse', 'Kharif', 'Low'),
    ('Groundnut', 'Oilseed', 'Kharif', 'Medium'),
    ('Potato', 'Vegetable', 'Rabi', 'High'),
    ('Sugarcane', 'Cash Crop', 'Annual', 'High')
ON CONFLICT DO NOTHING;

-- Insert sample market data
INSERT INTO markets (name, district, type) VALUES 
    ('Ranchi Mandi', 'Ranchi', 'Primary'),
    ('Dhanbad Market', 'Dhanbad', 'Primary'),
    ('Bokaro Agricultural Market', 'Bokaro', 'Primary')
ON CONFLICT DO NOTHING;
"""

if __name__ == "__main__":
    print("Database Schema for AuraFarming - SIH 2025")
    print("=" * 50)
    print("\nTo set up the database:")
    print("1. Copy the SQL commands above")
    print("2. Execute them in your Supabase SQL editor")
    print("3. Ensure all tables are created successfully")
    print("4. Verify RLS policies are active")
    print("\nTables to be created:")
    print("- farmers")
    print("- farms") 
    print("- crops_history")
    print("- recommendations")
    print("- audit_logs")
    print("\nIndexes and triggers will be created automatically.")