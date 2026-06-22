#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://keleythlzrtmvoetixcl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlbGV5dGhsenJ0bXZvZXRpeGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTE3OTMyMywiZXhwIjoyMDg0NzU1MzIzfQ.AtEPGg_hVYzJOjwPLaOdRkozemgiLL8ILCp9v2OOxV4"

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check recipes with embeddings
result = client.table('recipes').select('name_az, embedding').limit(5).execute()
print("=== Recipes ===")
for r in result.data:
    emb = r.get('embedding')
    has_emb = emb is not None and len(emb) > 0 if isinstance(emb, (list, str)) else bool(emb)
    print(f"  {r['name_az']}: embedding={'YES' if has_emb else 'NO'}")

# Check products with embeddings  
result2 = client.table('products').select('name, embedding').limit(5).execute()
print("\n=== Products ===")
for p in result2.data:
    emb = p.get('embedding')
    has_emb = emb is not None and len(emb) > 0 if isinstance(emb, (list, str)) else bool(emb)
    print(f"  {p['name']}: embedding={'YES' if has_emb else 'NO'}")
