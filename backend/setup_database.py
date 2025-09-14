"""
Supabase database schema creation script.
Run this script to create the necessary tables for AuraFarming.
"""

from supabase import create_client, Client
from app.core.config import settings
import json

def create_database_schema():
    """Create database schema in Supabase."""
    
    # Initialize Supabase client
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role key for admin operations
    )
    
    print("Creating database schema...")
    
    # Note: In Supabase, you typically create tables using the SQL editor or migrations
    # This script shows the table structures you need to create manually
    
    table_schemas = {
        "farmers": """
        CREATE TABLE IF NOT EXISTS farmers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            language VARCHAR(20) DEFAULT 'english',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        "farms": """
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
        """,
        
        "recommendations": """
        CREATE TABLE IF NOT EXISTS recommendations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
            crops JSONB NOT NULL,
            model_confidence DECIMAL(5,4),
            season VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        "crops_history": """
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
        """,
        
        "audit_logs": """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES farmers(id),
            action VARCHAR(100) NOT NULL,
            details JSONB,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    }
    
    print("Database schema definitions:")
    for table_name, schema in table_schemas.items():
        print(f"\n--- {table_name.upper()} TABLE ---")
        print(schema)
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste each table schema above")
    print("4. Run each schema one by one")
    print("5. Enable Row Level Security (RLS) if needed")
    print("="*60)
    
    return table_schemas

def test_connection():
    """Test Supabase connection."""
    try:
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        
        # Try a simple query to test connection
        # This will fail if tables don't exist, but will test the connection
        result = supabase.table("farmers").select("count", count="exact").execute()
        print(f"✅ Connection successful! Farmer count: {result.count}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("Please check your Supabase URL and API keys in the .env file")
        return False

if __name__ == "__main__":
    print("AuraFarming Supabase Setup")
    print("=" * 40)
    
    # Test connection first
    if test_connection():
        print("\n✅ Supabase connection is working!")
    else:
        print("\n❌ Please fix Supabase connection before proceeding")
        
    # Show schema
    create_database_schema()