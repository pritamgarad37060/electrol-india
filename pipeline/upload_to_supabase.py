"""
Upload Lok Sabha Members and Positions to Supabase Database via REST API.
Splits data into chunks of 100 rows for rock-solid reliability.
"""
import os, sys, json, time
from pathlib import Path
from dotenv import load_dotenv

PROJ_ROOT = Path(__file__).parent.parent
load_dotenv(PROJ_ROOT / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be in .env")
    sys.exit(1)

try:
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase client init error: {e}")
    sys.exit(1)

JSON_PATH = PROJ_ROOT / 'data' / 'ls_members.json'
if not JSON_PATH.exists():
    print(f"Data file not found: {JSON_PATH}")
    sys.exit(1)

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    members = json.load(f)

print(f"Loaded {len(members)} members.")

# 1. Prepare members batch
members_rows = []
positions_rows = []

for m in members:
    members_rows.append({
        'member_id': m['id'],
        'full_name': m['name'],
        'first_name': m['first_name'],
        'last_name': m['last_name'],
        'constituency': m['constituency'],
        'matched_pc': m['matched_pc'],
        'state': m['state'],
        'party_name': m['party'],
        'party_code': m['party_code'],
        'member_status': m['status'],
        'gender': m['gender'],
        'date_of_birth': m['dob'],
        'age': m['age'],
        'marital_status': m['marital_status'],
        'birth_place': m['birth_place'],
        'father_name': m['father'],
        'mother_name': m['mother'],
        'spouse_name': m['spouse'],
        'sons': m['sons'],
        'daughters': m['daughters'],
        'qualification': m['qualification'],
        'education': m['education'],
        'profession': m['profession'],
        'other_profession': m['other_profession'],
        'email': m['email'],
        'personal_phone': m['phone'],
        'delhi_phone': m['delhi_phone'],
        'present_address': m['present_address'],
        'permanent_address': m['permanent_address'],
        'photo_url': m['photo_url'],
        'facebook_url': (m.get('social') or {}).get('facebook'),
        'twitter_url': (m.get('social') or {}).get('twitter'),
        'instagram_url': (m.get('social') or {}).get('instagram'),
        'linkedin_url': (m.get('social') or {}).get('linkedin'),
        'lok_sabha_terms': m['terms'],
        'number_of_terms': m['num_terms'],
        'oath_video_url': (m.get('video') or {}).get('direct_url'),
        'oath_video_search_url': (m.get('video') or {}).get('search_url'),
        'oath_video_status': (m.get('video') or {}).get('status'),
        'source_profile_url': m['source_profile'],
        'source_positions_url': m['source_positions']
    })

    for p in m.get('positions', []):
        positions_rows.append({
            'member_id': m['id'],
            'member_name': m['name'],
            'period': p['period'],
            'position_held': p['position'],
            'source_profile_url': p['source']
        })

print(f"Total Members Rows: {len(members_rows)}")
print(f"Total Positions Rows: {len(positions_rows)}")

# Upsert members in chunks
print("\n[1/2] Upserting ls_members...")
chunk_size = 50
for i in range(0, len(members_rows), chunk_size):
    chunk = members_rows[i:i+chunk_size]
    try:
        sb.table('ls_members').upsert(chunk, on_conflict='member_id').execute()
        print(f"  Upserted members {i+1} to {min(i+chunk_size, len(members_rows))}")
    except Exception as e:
        print(f"  Error at chunk {i}: {e}")

# Insert positions in chunks
print("\n[2/2] Inserting ls_member_positions...")
for i in range(0, len(positions_rows), 100):
    chunk = positions_rows[i:i+100]
    try:
        sb.table('ls_member_positions').insert(chunk).execute()
        print(f"  Inserted positions {i+1} to {min(i+100, len(positions_rows))}")
    except Exception as e:
        print(f"  Error at chunk {i}: {e}")

print("\nFinished!")
