import os, sys, re, json
import pandas as pd
from pathlib import Path

EXCEL_PATH = r"C:\Users\prita\Documents\Codex\2026-10-12\https-sansad-in-ls-members-here\outputs\Lok_Sabha_All_Members_SQL_Import_With_Search_Links.xlsx"
PROJ_ROOT = Path(r"c:\Users\prita\Downloads\files\india-elections\india-elections")

print("=" * 60)
print("  LOK SABHA MEMBERS & POSITIONS PIPELINE")
print("=" * 60)

# 1. Load Excel
print("[1/5] Loading Excel sheets...")
df_members = pd.read_excel(EXCEL_PATH, sheet_name="Members")
df_positions = pd.read_excel(EXCEL_PATH, sheet_name="Positions")
print(f"  Loaded {len(df_members)} members and {len(df_positions)} positions.")

# 2. Constituency Alias Map for 100% exact match with Lok Sabha 2024 database
ALIAS_MAP = {
    ("bahraich", "uttar pradesh"): "Bahraich",
    ("kurnool", "andhra pradesh"): "Kurnoolu",
    ("andaman and nicobar islands", "andaman and nicobar islands"): "Andaman & Nicobar Islands",
    ("hatkanangle", "maharashtra"): "Hatkanangale",
    ("anantapur", "andhra pradesh"): "Ananthapur",
    ("narasaraopet", "andhra pradesh"): "Narsaraopet",
    ("tirupati", "andhra pradesh"): "Thirupathi",
    ("surat", "gujarat"): "Surat",
    ("daman and diu", "dadra and nagar haveli and daman and diu"): "Daman & Diu",
    ("hardwar", "uttarakhand"): "Haridwar",
    ("dadra and nagar haveli", "dadra and nagar haveli and daman and diu"): "Dadra & Nagar Haveli",
    ("pataliputra", "bihar"): "Patliputra",
    ("darrang udalguri", "assam"): "Darrang-Udalguri",
    ("gadchiroli-chimur", "maharashtra"): "Gadchiroli - Chimur",
    ("bhandara-gondiya", "maharashtra"): "Bhandara - Gondiya"
}

def clean_val(v):
    if pd.isna(v):
        return None
    s = str(v).strip()
    return s if s != "" and s.lower() != "nan" else None

# Group positions by member_id
print("[2/5] Grouping positions by member...")
pos_by_member = {}
for _, r in df_positions.iterrows():
    mid = int(r["member_id"])
    if mid not in pos_by_member:
        pos_by_member[mid] = []
    pos_by_member[mid].append({
        "period": clean_val(r.get("period")),
        "position": clean_val(r.get("position_held")),
        "source": clean_val(r.get("source_profile_url"))
    })

# 3. Format members list
print("[3/5] Processing members...")
members_list = []
for _, r in df_members.iterrows():
    mid = int(r["member_id"])
    constituency_raw = clean_val(r.get("constituency")) or ""
    state_raw = clean_val(r.get("state")) or ""
    
    # Resolve constituency alias
    key = (constituency_raw.lower().strip(), state_raw.lower().strip())
    matched_pc = ALIAS_MAP.get(key, constituency_raw)
    
    # Process oath video
    direct_video = clean_val(r.get("oath_video_url"))
    search_video = clean_val(r.get("oath_video_search_url"))
    video_status = clean_val(r.get("oath_video_status")) or ("direct" if direct_video else "search")
    
    # Extract youtube id if direct
    yt_id = None
    if direct_video:
        m = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", direct_video)
        if m:
            yt_id = m.group(1)

    m_obj = {
        "id": mid,
        "name": clean_val(r.get("full_name")),
        "first_name": clean_val(r.get("first_name")),
        "last_name": clean_val(r.get("last_name")),
        "constituency": constituency_raw,
        "matched_pc": matched_pc,
        "state": state_raw,
        "party": clean_val(r.get("party_name")),
        "party_code": clean_val(r.get("party_code")),
        "status": clean_val(r.get("member_status")) or "Sitting",
        "gender": clean_val(r.get("gender")),
        "dob": clean_val(r.get("date_of_birth")),
        "age": int(r["age"]) if pd.notna(r.get("age")) and str(r.get("age")).isdigit() else None,
        "marital_status": clean_val(r.get("marital_status")),
        "birth_place": clean_val(r.get("birth_place")),
        "father": clean_val(r.get("father_name")),
        "mother": clean_val(r.get("mother_name")),
        "spouse": clean_val(r.get("spouse_name")),
        "sons": int(r["sons"]) if pd.notna(r.get("sons")) and str(r.get("sons")).isdigit() else 0,
        "daughters": int(r["daughters"]) if pd.notna(r.get("daughters")) and str(r.get("daughters")).isdigit() else 0,
        "qualification": clean_val(r.get("qualification")),
        "education": clean_val(r.get("education")),
        "profession": clean_val(r.get("profession")),
        "other_profession": clean_val(r.get("other_profession")),
        "email": clean_val(r.get("email")),
        "phone": clean_val(r.get("personal_phone")),
        "delhi_phone": clean_val(r.get("delhi_phone")),
        "present_address": clean_val(r.get("present_address")),
        "permanent_address": clean_val(r.get("permanent_address")),
        "photo_url": clean_val(r.get("photo_url")),
        "social": {
            "facebook": clean_val(r.get("facebook_url")),
            "twitter": clean_val(r.get("twitter_url")),
            "instagram": clean_val(r.get("instagram_url")),
            "pinterest": clean_val(r.get("pinterest_url")),
            "linkedin": clean_val(r.get("linkedin_url")),
        },
        "social_activities": clean_val(r.get("other_social_activities")),
        "interests": clean_val(r.get("interests")),
        "hobbies": clean_val(r.get("hobbies")),
        "sports": clean_val(r.get("sports")),
        "books": clean_val(r.get("books_published")),
        "countries_visited": clean_val(r.get("countries_visited")),
        "terms": clean_val(r.get("lok_sabha_terms")),
        "num_terms": int(r["number_of_terms"]) if pd.notna(r.get("number_of_terms")) and str(r.get("number_of_terms")).isdigit() else 1,
        "video": {
            "direct_url": direct_video,
            "search_url": search_video,
            "status": video_status,
            "yt_id": yt_id
        },
        "source_profile": clean_val(r.get("source_profile_url")),
        "source_positions": clean_val(r.get("source_positions_url")),
        "positions": pos_by_member.get(mid, [])
    }
    members_list.append(m_obj)

print(f"  Processed {len(members_list)} full member dossiers.")

# 4. Save JSON and JS files
print("[4/5] Writing web datasets (JSON & JS)...")
json_path = PROJ_ROOT / "data" / "ls_members.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(members_list, f, ensure_ascii=False, indent=2)
print(f"  Saved JSON: {json_path} ({os.path.getsize(json_path):,} bytes)")

# Write client-side JS bundle
js_path = PROJ_ROOT / "js" / "data-ls-members.js"
with open(js_path, "w", encoding="utf-8") as f:
    f.write("/* Electrol India — Lok Sabha 18th Members Complete Dataset */\n")
    f.write("window.LS_MEMBERS = ")
    json.dump(members_list, f, ensure_ascii=False)
    f.write(";\n")
print(f"  Saved JS: {js_path} ({os.path.getsize(js_path):,} bytes)")

# 5. Generate Supabase SQL scripts
print("[5/5] Generating Supabase SQL migration & insert scripts...")
sql_schema = """-- ============================================================
-- Electrol India — Lok Sabha Members & Positions Schema
-- ============================================================
CREATE TABLE IF NOT EXISTS ls_members (
  member_id            INTEGER PRIMARY KEY,
  full_name            TEXT NOT NULL,
  first_name           TEXT,
  last_name            TEXT,
  constituency         TEXT,
  matched_pc           TEXT,
  state                TEXT,
  party_name           TEXT,
  party_code           TEXT,
  member_status        TEXT DEFAULT 'Sitting',
  gender               TEXT,
  date_of_birth        DATE,
  age                  INTEGER,
  marital_status       TEXT,
  birth_place          TEXT,
  father_name          TEXT,
  mother_name          TEXT,
  spouse_name          TEXT,
  sons                 INTEGER DEFAULT 0,
  daughters            INTEGER DEFAULT 0,
  qualification        TEXT,
  education            TEXT,
  profession           TEXT,
  other_profession     TEXT,
  email                TEXT,
  personal_phone       TEXT,
  delhi_phone          TEXT,
  present_address      TEXT,
  permanent_address    TEXT,
  photo_url            TEXT,
  facebook_url         TEXT,
  twitter_url          TEXT,
  instagram_url        TEXT,
  pinterest_url        TEXT,
  linkedin_url         TEXT,
  other_social_activities TEXT,
  interests            TEXT,
  hobbies              TEXT,
  sports               TEXT,
  books_published      TEXT,
  countries_visited    TEXT,
  lok_sabha_terms      TEXT,
  number_of_terms      INTEGER DEFAULT 1,
  oath_video_url       TEXT,
  oath_video_search_url TEXT,
  oath_video_status    TEXT,
  source_profile_url   TEXT,
  source_positions_url TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ls_member_positions (
  id                   BIGSERIAL PRIMARY KEY,
  member_id            INTEGER REFERENCES ls_members(member_id) ON DELETE CASCADE,
  member_name          TEXT,
  period               TEXT,
  position_held        TEXT,
  source_profile_url   TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ls_members_pc ON ls_members(matched_pc);
CREATE INDEX IF NOT EXISTS idx_ls_members_state ON ls_members(state);
CREATE INDEX IF NOT EXISTS idx_ls_members_party ON ls_members(party_code);
CREATE INDEX IF NOT EXISTS idx_ls_member_pos_mid ON ls_member_positions(member_id);

-- Enable RLS
ALTER TABLE ls_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE ls_member_positions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read ls_members" ON ls_members FOR SELECT USING (true);
CREATE POLICY "Public read ls_member_positions" ON ls_member_positions FOR SELECT USING (true);
"""

with open(PROJ_ROOT / "supabase_ls_members.sql", "w", encoding="utf-8") as f:
    f.write(sql_schema)

print(f"  Created schema file: supabase_ls_members.sql")

def sql_esc(val):
    if val is None or pd.isna(val):
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"

def num_esc(val):
    if val is None or pd.isna(val) or not str(val).isdigit():
        return "NULL"
    return str(int(val))

sql_inserts = [sql_schema, "\n-- DATA INSERTS\nBEGIN;\n"]
for m in members_list:
    line = f"""INSERT INTO ls_members (
  member_id, full_name, first_name, last_name, constituency, matched_pc, state,
  party_name, party_code, member_status, gender, date_of_birth, age,
  marital_status, birth_place, father_name, mother_name, spouse_name,
  sons, daughters, qualification, education, profession, other_profession,
  email, personal_phone, delhi_phone, present_address, permanent_address,
  photo_url, facebook_url, twitter_url, instagram_url, linkedin_url,
  lok_sabha_terms, number_of_terms, oath_video_url, oath_video_search_url,
  oath_video_status, source_profile_url, source_positions_url
) VALUES (
  {m['id']}, {sql_esc(m['name'])}, {sql_esc(m['first_name'])}, {sql_esc(m['last_name'])},
  {sql_esc(m['constituency'])}, {sql_esc(m['matched_pc'])}, {sql_esc(m['state'])},
  {sql_esc(m['party'])}, {sql_esc(m['party_code'])}, {sql_esc(m['status'])},
  {sql_esc(m['gender'])}, {sql_esc(m['dob'])}, {num_esc(m['age'])},
  {sql_esc(m['marital_status'])}, {sql_esc(m['birth_place'])}, {sql_esc(m['father'])},
  {sql_esc(m['mother'])}, {sql_esc(m['spouse'])}, {m['sons']}, {m['daughters']},
  {sql_esc(m['qualification'])}, {sql_esc(m['education'])}, {sql_esc(m['profession'])},
  {sql_esc(m['other_profession'])}, {sql_esc(m['email'])}, {sql_esc(m['phone'])},
  {sql_esc(m['delhi_phone'])}, {sql_esc(m['present_address'])}, {sql_esc(m['permanent_address'])},
  {sql_esc(m['photo_url'])}, {sql_esc(m['social']['facebook'])}, {sql_esc(m['social']['twitter'])},
  {sql_esc(m['social']['instagram'])}, {sql_esc(m['social']['linkedin'])},
  {sql_esc(m['terms'])}, {m['num_terms']}, {sql_esc(m['video']['direct_url'])},
  {sql_esc(m['video']['search_url'])}, {sql_esc(m['video']['status'])},
  {sql_esc(m['source_profile'])}, {sql_esc(m['source_positions'])}
) ON CONFLICT (member_id) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  photo_url = EXCLUDED.photo_url,
  email = EXCLUDED.email,
  personal_phone = EXCLUDED.personal_phone,
  updated_at = NOW();\n"""
    sql_inserts.append(line)

# Add positions inserts
for mid, p_list in pos_by_member.items():
    for p in p_list:
        pos_line = f"""INSERT INTO ls_member_positions (member_id, period, position_held, source_profile_url) VALUES ({mid}, {sql_esc(p['period'])}, {sql_esc(p['position'])}, {sql_esc(p['source'])});\n"""
        sql_inserts.append(pos_line)

sql_inserts.append("COMMIT;\n")

insert_file_path = PROJ_ROOT / "supabase_ls_members_data.sql"
with open(insert_file_path, "w", encoding="utf-8") as f:
    f.writelines(sql_inserts)

print(f"  Saved SQL data migration: {insert_file_path} ({os.path.getsize(insert_file_path):,} bytes)")
print("Done!")
