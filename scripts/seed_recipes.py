#!/usr/bin/env python3
"""
Seed recipes data to Supabase database
Run this after applying the migration
"""

import json
import os
import sys
from supabase import create_client, Client

# Load environment variables - Set these before running!
# You can also pass as command line args: python seed_recipes.py <url> <key>
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

def load_recipes():
    """Load recipes from JSON file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'recipes_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def seed_categories(supabase: Client, categories: list):
    """Seed recipe categories"""
    print("Seeding recipe categories...")
    
    for category in categories:
        try:
            data = {
                'category_id': category['id'],
                'name_az': category['name_az'],
                'name_en': category.get('name_en')
            }
            supabase.table('recipe_categories').upsert(data, on_conflict='category_id').execute()
            print(f"  ✓ {category['name_az']}")
        except Exception as e:
            print(f"  ✗ Error seeding category {category['id']}: {e}")

def seed_recipes(supabase: Client, recipes: list):
    """Seed recipes"""
    print("\nSeeding recipes...")
    
    for recipe in recipes:
        try:
            data = {
                'recipe_id': recipe['id'],
                'name_az': recipe['name_az'],
                'name_en': recipe.get('name_en'),
                'category': recipe['category'],
                'description_az': recipe.get('description_az'),
                'ingredients': recipe['ingredients'],
                'instructions_az': recipe['instructions_az'],
                'prep_time_minutes': recipe.get('prep_time_minutes'),
                'cook_time_minutes': recipe.get('cook_time_minutes'),
                'servings': recipe.get('servings'),
                'difficulty': recipe.get('difficulty'),
                'tags': recipe.get('tags', []),
                'image_url': recipe.get('image_url')
            }
            supabase.table('recipes').upsert(data, on_conflict='recipe_id').execute()
            print(f"  ✓ {recipe['name_az']}")
        except Exception as e:
            print(f"  ✗ Error seeding recipe {recipe['id']}: {e}")

def main():
    global SUPABASE_URL, SUPABASE_SERVICE_KEY
    
    # Check for command line args
    if len(sys.argv) >= 3:
        SUPABASE_URL = sys.argv[1]
        SUPABASE_SERVICE_KEY = sys.argv[2]
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Error: Supabase credentials required!")
        print("Usage: python seed_recipes.py <SUPABASE_URL> <SERVICE_KEY>")
        print("Or set environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY")
        sys.exit(1)
    
    # Initialize Supabase client
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Load data
    data = load_recipes()
    
    # Seed categories first
    seed_categories(supabase, data['categories'])
    
    # Seed recipes
    seed_recipes(supabase, data['recipes'])
    
    print("\n✅ Seeding complete!")
    print(f"   Categories: {len(data['categories'])}")
    print(f"   Recipes: {len(data['recipes'])}")

if __name__ == "__main__":
    main()
