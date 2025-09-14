-- Insert Demo Data into Supabase
-- Run this in Supabase SQL Editor after creating the tables

-- Insert demo farmer
INSERT INTO farmers (id, name, phone, password, language, created_at) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440000',
    'Demo Farmer',
    '9876543210',
    '$2b$12$LQv3c1yqBkVXK47k7rJAiOX9.5pJVtNQjQQkjp6z1zQJ8QzV8QzV8',
    'english',
    NOW()
);

-- Insert demo farm
INSERT INTO farms (id, farmer_id, name, location, soil_type, irrigation_method, field_size, created_at) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440000',
    'Demo Farm',
    '{"latitude": 23.3441, "longitude": 85.3096, "district": "Ranchi", "village": "Demo Village"}',
    'loam',
    'drip',
    2.5,
    NOW()
);

-- Insert some demo crop recommendations
INSERT INTO recommendations (id, farm_id, crops, model_confidence, season, created_at) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440001',
    '[
        {"crop": "Rice", "confidence": 0.85, "expected_yield": 25.5, "reasons": ["Suitable soil type", "Good water availability"]},
        {"crop": "Wheat", "confidence": 0.78, "expected_yield": 18.2, "reasons": ["Winter season crop", "Market demand high"]},
        {"crop": "Maize", "confidence": 0.72, "expected_yield": 22.8, "reasons": ["Good soil nutrition", "Weather favorable"]}
    ]',
    0.85,
    'Kharif',
    NOW()
);

-- Insert some crop history
INSERT INTO crops_history (id, farm_id, crop, planting_date, harvest_date, yield_amount, quality_score, created_at) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440003',
    '550e8400-e29b-41d4-a716-446655440001',
    'Rice',
    '2024-06-15',
    '2024-11-20',
    24.5,
    4.2,
    NOW()
),
(
    '550e8400-e29b-41d4-a716-446655440004',
    '550e8400-e29b-41d4-a716-446655440001',
    'Wheat',
    '2023-12-01',
    '2024-04-15',
    16.8,
    3.9,
    NOW()
);

-- Insert audit log
INSERT INTO audit_logs (id, user_id, action, details, timestamp) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440005',
    '550e8400-e29b-41d4-a716-446655440000',
    'farm_profile_created',
    '{"farm_id": "550e8400-e29b-41d4-a716-446655440001", "action": "created farm profile"}',
    NOW()
);

-- Verify the data was inserted
SELECT 'Farmers' as table_name, COUNT(*) as count FROM farmers
UNION ALL
SELECT 'Farms' as table_name, COUNT(*) as count FROM farms
UNION ALL
SELECT 'Recommendations' as table_name, COUNT(*) as count FROM recommendations
UNION ALL
SELECT 'Crops History' as table_name, COUNT(*) as count FROM crops_history
UNION ALL
SELECT 'Audit Logs' as table_name, COUNT(*) as count FROM audit_logs;