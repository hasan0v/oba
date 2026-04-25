-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id VARCHAR(100) UNIQUE NOT NULL,
    name_az VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    description_az TEXT,
    ingredients JSONB NOT NULL,
    instructions_az TEXT NOT NULL,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    servings INTEGER,
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    tags TEXT[],
    image_url TEXT,
    embedding vector(768), -- Gemini embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create recipe categories table
CREATE TABLE IF NOT EXISTS recipe_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id VARCHAR(100) UNIQUE NOT NULL,
    name_az VARCHAR(255) NOT NULL,
    name_en VARCHAR(255)
);

-- Add embedding column to products table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'embedding'
    ) THEN
        ALTER TABLE products ADD COLUMN embedding vector(768);
    END IF;
END $$;

-- Create semantic search function for products
CREATE OR REPLACE FUNCTION search_products_semantic(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    description TEXT,
    price DECIMAL,
    category VARCHAR,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.description,
        p.price,
        p.category,
        1 - (p.embedding <=> query_embedding) AS similarity
    FROM products p
    WHERE p.embedding IS NOT NULL
    AND 1 - (p.embedding <=> query_embedding) > match_threshold
    ORDER BY p.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create semantic search function for recipes
CREATE OR REPLACE FUNCTION search_recipes_semantic(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    recipe_id VARCHAR,
    name_az VARCHAR,
    category VARCHAR,
    description_az TEXT,
    ingredients JSONB,
    instructions_az TEXT,
    difficulty VARCHAR,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.recipe_id,
        r.name_az,
        r.category,
        r.description_az,
        r.ingredients,
        r.instructions_az,
        r.difficulty,
        1 - (r.embedding <=> query_embedding) AS similarity
    FROM recipes r
    WHERE r.embedding IS NOT NULL
    AND 1 - (r.embedding <=> query_embedding) > match_threshold
    ORDER BY r.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create combined semantic search function
CREATE OR REPLACE FUNCTION search_all_semantic(
    query_embedding vector(768),
    search_type VARCHAR DEFAULT 'all', -- 'products', 'recipes', 'all'
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    item_type VARCHAR,
    item_id UUID,
    name VARCHAR,
    description TEXT,
    category VARCHAR,
    extra_data JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH product_results AS (
        SELECT 
            'product'::VARCHAR AS item_type,
            p.id AS item_id,
            p.name::VARCHAR,
            p.description::TEXT,
            p.category::VARCHAR,
            jsonb_build_object(
                'price', p.price,
                'image_url', p.image_url,
                'stock_quantity', p.stock_quantity
            ) AS extra_data,
            1 - (p.embedding <=> query_embedding) AS similarity
        FROM products p
        WHERE p.embedding IS NOT NULL
        AND (search_type = 'all' OR search_type = 'products')
        AND 1 - (p.embedding <=> query_embedding) > match_threshold
    ),
    recipe_results AS (
        SELECT 
            'recipe'::VARCHAR AS item_type,
            r.id AS item_id,
            r.name_az::VARCHAR AS name,
            r.description_az::TEXT AS description,
            r.category::VARCHAR,
            jsonb_build_object(
                'ingredients', r.ingredients,
                'instructions', r.instructions_az,
                'prep_time', r.prep_time_minutes,
                'cook_time', r.cook_time_minutes,
                'difficulty', r.difficulty,
                'tags', r.tags
            ) AS extra_data,
            1 - (r.embedding <=> query_embedding) AS similarity
        FROM recipes r
        WHERE r.embedding IS NOT NULL
        AND (search_type = 'all' OR search_type = 'recipes')
        AND 1 - (r.embedding <=> query_embedding) > match_threshold
    )
    SELECT * FROM product_results
    UNION ALL
    SELECT * FROM recipe_results
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Create indexes for faster search
CREATE INDEX IF NOT EXISTS idx_products_embedding ON products 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_recipes_embedding ON recipes 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create index on recipe tags for filtering
CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes USING GIN (tags);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_recipes_updated_at
    BEFORE UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_categories ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read access to recipes"
    ON recipes FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Allow public read access to recipe_categories"
    ON recipe_categories FOR SELECT
    TO public
    USING (true);

-- Grant permissions
GRANT SELECT ON recipes TO anon, authenticated;
GRANT SELECT ON recipe_categories TO anon, authenticated;
