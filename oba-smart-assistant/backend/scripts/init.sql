-- OBA Smart Assistant - Database Initialization Script
-- This script runs automatically when PostgreSQL container starts

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_tier AS ENUM ('bronze', 'silver', 'gold', 'platinum');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE complaint_status AS ENUM ('pending', 'in_progress', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE complaint_priority AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (will be created by SQLAlchemy, but defined here for reference)
-- CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
-- CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
-- CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oba_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oba_user;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'OBA Database initialized successfully at %', NOW();
END $$;
