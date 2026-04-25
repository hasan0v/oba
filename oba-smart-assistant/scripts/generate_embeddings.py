#!/usr/bin/env python3
"""
Generate embeddings for recipes and products using Google Gemini
Run this after seeding recipes to enable semantic search
"""

import json
import os
import sys
import time
import requests
from supabase import create_client, Client

# Gemini API settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBEDDING_MODEL}:embedContent"

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


def generate_embedding(text: str) -> list:
    """Generate embedding using Gemini API"""
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    
    payload = {
        "model": f"models/{EMBEDDING_MODEL}",
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    response = requests.post(EMBEDDING_URL, headers=headers, params=params, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"Embedding API error: {response.status_code} - {response.text}")
    
    data = response.json()
    return data["embedding"]["values"]


def create_recipe_text(recipe: dict) -> str:
    """Create searchable text from recipe"""
    parts = [
        recipe.get('name_az', ''),
        recipe.get('name_en', ''),
        recipe.get('category', ''),
        recipe.get('description_az', ''),
    ]
    
    # Add ingredients
    ingredients = recipe.get('ingredients', [])
    if isinstance(ingredients, list):
        for ing in ingredients:
            if isinstance(ing, dict):
                parts.append(ing.get('item', ''))
            else:
                parts.append(str(ing))
    
    # Add tags
    tags = recipe.get('tags', [])
    if tags:
        parts.extend(tags)
    
    return ' '.join(filter(None, parts))


def create_product_text(product: dict) -> str:
    """Create searchable text from product"""
    parts = [
        product.get('name', ''),
        product.get('description', ''),
        product.get('category', ''),
    ]
    return ' '.join(filter(None, parts))


def generate_recipe_embeddings(supabase: Client):
    """Generate embeddings for all recipes"""
    print("\n📚 Generating recipe embeddings...")
    
    # Get all recipes without embeddings
    result = supabase.table('recipes').select('id, recipe_id, name_az, name_en, category, description_az, ingredients, tags').is_('embedding', 'null').execute()
    recipes = result.data
    
    if not recipes:
        print("  All recipes already have embeddings!")
        return 0
    
    print(f"  Found {len(recipes)} recipes without embeddings")
    
    success_count = 0
    for i, recipe in enumerate(recipes):
        try:
            # Create text for embedding
            text = create_recipe_text(recipe)
            
            # Generate embedding
            embedding = generate_embedding(text)
            
            # Update recipe with embedding
            supabase.table('recipes').update({
                'embedding': embedding
            }).eq('id', recipe['id']).execute()
            
            print(f"  ✓ [{i+1}/{len(recipes)}] {recipe['name_az']}")
            success_count += 1
            
            # Rate limiting - Gemini has 60 requests/minute for free tier
            time.sleep(1.1)
            
        except Exception as e:
            print(f"  ✗ [{i+1}/{len(recipes)}] {recipe['name_az']}: {e}")
    
    return success_count


def generate_product_embeddings(supabase: Client):
    """Generate embeddings for all products"""
    print("\n🛒 Generating product embeddings...")
    
    # Get all products without embeddings
    result = supabase.table('products').select('id, name, description, category').is_('embedding', 'null').execute()
    products = result.data
    
    if not products:
        print("  All products already have embeddings!")
        return 0
    
    print(f"  Found {len(products)} products without embeddings")
    
    success_count = 0
    for i, product in enumerate(products):
        try:
            # Create text for embedding
            text = create_product_text(product)
            
            # Generate embedding
            embedding = generate_embedding(text)
            
            # Update product with embedding
            supabase.table('products').update({
                'embedding': embedding
            }).eq('id', product['id']).execute()
            
            print(f"  ✓ [{i+1}/{len(products)}] {product['name']}")
            success_count += 1
            
            # Rate limiting
            time.sleep(1.1)
            
        except Exception as e:
            print(f"  ✗ [{i+1}/{len(products)}] {product['name']}: {e}")
    
    return success_count


def main():
    global SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY
    
    # Check for command line args
    if len(sys.argv) >= 4:
        SUPABASE_URL = sys.argv[1]
        SUPABASE_SERVICE_KEY = sys.argv[2]
        GEMINI_API_KEY = sys.argv[3]
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not GEMINI_API_KEY:
        print("❌ Error: All credentials required!")
        print("Usage: python generate_embeddings.py <SUPABASE_URL> <SERVICE_KEY> <GEMINI_API_KEY>")
        print("Or set environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY")
        sys.exit(1)
    
    # Initialize Supabase client
    print("🔌 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Generate embeddings
    recipe_count = generate_recipe_embeddings(supabase)
    product_count = generate_product_embeddings(supabase)
    
    print("\n" + "="*50)
    print("✅ Embedding generation complete!")
    print(f"   Recipes: {recipe_count}")
    print(f"   Products: {product_count}")


if __name__ == "__main__":
    main()
