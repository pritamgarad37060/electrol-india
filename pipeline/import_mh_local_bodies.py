"""
Process Maharashtra Municipal Corporations & Municipal Councils Excel files.
Generates:
1. data/elections/mh_corporations.json
2. data/elections/mh_councils.json
3. js/data-mh-local-bodies.js
4. supabase_mh_local_bodies.sql & supabase_mh_local_bodies_data.sql
"""
import os, sys, re, json
from pathlib import Path
import pandas as pd

PROJ_ROOT = Path(r"c:\Users\prita\Downloads\files\india-elections\india-elections")
CORPS_FILE = PROJ_ROOT / "data" / "mh_corps.xlsx"
COUNCILS_FILE = PROJ_ROOT / "data" / "mh_councils.xlsx"

print("=" * 60)
print("  MAHARASHTRA LOCAL BODIES DATA PIPELINE")
print("=" * 60)

# Helper to clean strings
def clean_str(v):
    if pd.isna(v): return ""
    s = str(v).strip()
    return "" if s.lower() == "nan" else s

# Clean party names to standard codes
PARTY_MAP = {
    'bharatiya janata party': 'BJP',
    'bjp': 'BJP',
    'indian national congress': 'INC',
    'congress': 'INC',
    'shiv sena': 'SHS',
    'shivsena': 'SHS',
    'shiv sena (ubt)': 'SHSUBT',
    'shiv sena (uddhav balasaheb thackrey)': 'SHSUBT',
    'nationalist congress party': 'NCP',
    'nationalist congress party (sp)': 'NCPSP',
    'nationalist congress party - sharadchandra pawar': 'NCPSP',
    'all india majlis-e-ittehadul muslimeen': 'AIMIM',
    'all india majlis-e-ittehadul muslimeen (aimim)': 'AIMIM',
    'all india majlis-e-ittehadul muslimeen ': 'AIMIM',
    'all india majlis-e-ittehadul muslimeen  ': 'AIMIM',
    'maharashtra navnirman sena': 'MNS',
    'bahujan vikas aghadi': 'BVA',
    'vanchit bahujan aaghadi': 'VBA',
    'vanchit bahujan aghadi': 'VBA',
    'aam aadmi party': 'AAP',
    'independent': 'IND',
    'none of the above': 'NOTA',
    'nota': 'NOTA'
}

def get_party_code(raw):
    clean = clean_str(raw).lower()
    return PARTY_MAP.get(clean, clean_str(raw))

# ─────────────────────────────────────────────────────────────
# 1. PROCESS MUNICIPAL CORPORATIONS
# ─────────────────────────────────────────────────────────────
print("\n[1/4] Processing Municipal Corporations...")
df_corps_meta = pd.read_excel(CORPS_FILE, sheet_name="Corporations")
df_corps_cand = pd.read_excel(CORPS_FILE, sheet_name="Candidates_2026")

# Group candidates by Corporation
corp_cands_grouped = {}
for _, r in df_corps_cand.iterrows():
    c_name = clean_str(r.get("Municipal_Corporation"))
    if not c_name: continue
    if c_name not in corp_cands_grouped:
        corp_cands_grouped[c_name] = []
    
    votes = int(r["Votes"]) if pd.notna(r.get("Votes")) and str(r.get("Votes")).replace('.','',1).isdigit() else 0
    share = float(r["Vote_Share_Pct"]) if pd.notna(r.get("Vote_Share_Pct")) else 0.0
    is_win = bool(r.get("Winner") is True or clean_str(r.get("Status")).lower() == "winner")
    
    corp_cands_grouped[c_name].append({
        "ward": int(r["Ward"]) if pd.notna(r.get("Ward")) and str(r.get("Ward")).isdigit() else clean_str(r.get("Ward")),
        "seat": clean_str(r.get("Seat")),
        "candidate": clean_str(r.get("Candidate")),
        "party": clean_str(r.get("Political_Party")),
        "party_code": get_party_code(r.get("Political_Party")),
        "votes": votes,
        "vote_share": round(share, 2),
        "status": clean_str(r.get("Status")),
        "winner": is_win,
        "reservation": clean_str(r.get("Ward_Reservation")),
        "source": clean_str(r.get("Source_URL"))
    })

corps_list = []
corp_id = 1
for _, r in df_corps_meta.iterrows():
    raw_name = clean_str(r["Municipal_Corporation"])
    # Clean display name: e.g. "Nagpur Municipal Corporation (NMC) 2026" -> "Nagpur Municipal Corporation"
    display_name = re.sub(r'\s*\b2026\b|\s*–\s*All Wards|\s*-\s*All Wards', '', raw_name).strip()
    
    # Extract short code like BMC, PMC, NMC
    m_code = re.search(r'\(([A-Z]{3,5})\)', display_name)
    short_code = m_code.group(1) if m_code else display_name.split()[0][:4].upper()
    
    cands = corp_cands_grouped.get(raw_name, [])
    
    # Calculate party seat tallies (winners)
    party_seats = {}
    party_votes = {}
    wards_set = set()
    total_winners = 0
    for cd in cands:
        p = cd["party_code"]
        wards_set.add(cd["ward"])
        party_votes[p] = party_votes.get(p, 0) + cd["votes"]
        if cd["winner"]:
            party_seats[p] = party_seats.get(p, 0) + 1
            total_winners += 1
            
    sorted_party_seats = sorted(party_seats.items(), key=lambda x: x[1], reverse=True)
    leading_party = sorted_party_seats[0][0] if sorted_party_seats else "–"
    
    pop_tot = int(r["Total_Population"]) if pd.notna(r.get("Total_Population")) and str(r.get("Total_Population")).isdigit() else None
    pop_sc = int(r["SC_Population"]) if pd.notna(r.get("SC_Population")) and str(r.get("SC_Population")).isdigit() else None
    pop_st = int(r["ST_Population"]) if pd.notna(r.get("ST_Population")) and str(r.get("ST_Population")).isdigit() else None

    corps_list.append({
        "id": corp_id,
        "raw_name": raw_name,
        "name": display_name,
        "short_code": short_code,
        "year": 2026,
        "population": {
            "total": pop_tot,
            "sc": pop_sc,
            "st": pop_st
        },
        "wards_count": len(wards_set) if wards_set else int(clean_str(r.get("Ward_Pages_2026")) or 0),
        "total_seats": total_winners if total_winners else len(cands),
        "candidates_count": len(cands),
        "party_seats": sorted_party_seats,
        "leading_party": leading_party,
        "source": clean_str(r.get("Source_URL")),
        "candidates": cands
    })
    corp_id += 1

print(f"  Processed {len(corps_list)} Municipal Corporations with {sum(len(c['candidates']) for c in corps_list)} candidates.")

# ─────────────────────────────────────────────────────────────
# 2. PROCESS MUNICIPAL COUNCILS
# ─────────────────────────────────────────────────────────────
print("\n[2/4] Processing Municipal Councils (2025)...")
df_councils_meta = pd.read_excel(COUNCILS_FILE, sheet_name="Municipal_Councils")
df_councils_cand = pd.read_excel(COUNCILS_FILE, sheet_name="Candidate_Results")

councils_cands_grouped = {}
for _, r in df_councils_cand.iterrows():
    cn_name = clean_str(r.get("Council"))
    if not cn_name: continue
    if cn_name not in councils_cands_grouped:
        councils_cands_grouped[cn_name] = []
        
    votes = int(r["Votes"]) if pd.notna(r.get("Votes")) and str(r.get("Votes")).replace('.','',1).isdigit() else 0
    share = float(r["Vote_Share_Pct"]) if pd.notna(r.get("Vote_Share_Pct")) else 0.0
    is_win = bool(r.get("Winner") is True or clean_str(r.get("Status")).lower() == "winner")
    
    councils_cands_grouped[cn_name].append({
        "post_type": clean_str(r.get("Post_Type")), # 'President' or 'Councillor'
        "ward": int(r["Ward"]) if pd.notna(r.get("Ward")) and str(r.get("Ward")).isdigit() else clean_str(r.get("Ward")),
        "seat": clean_str(r.get("Seat")),
        "candidate": clean_str(r.get("Candidate")),
        "party": clean_str(r.get("Party")),
        "party_code": get_party_code(r.get("Party")),
        "votes": votes,
        "vote_share": round(share, 2),
        "status": clean_str(r.get("Status")),
        "winner": is_win,
        "source": clean_str(r.get("Source_URL"))
    })

councils_list = []
council_id = 1
for _, r in df_councils_meta.iterrows():
    raw_name = clean_str(r["Council"])
    display_name = re.sub(r'^(Municipal Council|Nagar Panchayat)\s*', '', raw_name).strip()
    
    cands = councils_cands_grouped.get(raw_name, [])
    
    # Find directly elected president
    presidents = [c for c in cands if c["post_type"].lower() == "president"]
    pres_winner = next((c for c in presidents if c["winner"]), None)
    if not pres_winner and presidents:
        # Sort by votes
        pres_winner = sorted(presidents, key=lambda x: x["votes"], reverse=True)[0]
    
    councillors = [c for c in cands if c["post_type"].lower() == "councillor"]
    
    councillor_party_seats = {}
    wards_set = set()
    for cd in councillors:
        wards_set.add(cd["ward"])
        if cd["winner"]:
            p = cd["party_code"]
            councillor_party_seats[p] = councillor_party_seats.get(p, 0) + 1
            
    sorted_seats = sorted(councillor_party_seats.items(), key=lambda x: x[1], reverse=True)
    leading_party = sorted_seats[0][0] if sorted_seats else (pres_winner["party_code"] if pres_winner else "–")
    
    councils_list.append({
        "id": council_id,
        "raw_name": raw_name,
        "name": display_name or raw_name,
        "year": 2025,
        "wards_count": len(wards_set) if wards_set else int(clean_str(r.get("Ward_Result_Pages")) or 0),
        "total_councillor_seats": sum(councillor_party_seats.values()),
        "president": {
            "winner_name": pres_winner["candidate"] if pres_winner else None,
            "party": pres_winner["party"] if pres_winner else None,
            "party_code": pres_winner["party_code"] if pres_winner else None,
            "votes": pres_winner["votes"] if pres_winner else None,
            "vote_share": pres_winner["vote_share"] if pres_winner else None
        } if pres_winner else None,
        "councillor_seats": sorted_seats,
        "leading_party": leading_party,
        "candidates_count": len(cands),
        "source": clean_str(r.get("Council_URL")),
        "candidates": cands
    })
    council_id += 1

print(f"  Processed {len(councils_list)} Municipal Councils with {sum(len(c['candidates']) for c in councils_list)} candidates.")

# ─────────────────────────────────────────────────────────────
# 3. SAVE JSON DATASETS & JS BUNDLE
# ─────────────────────────────────────────────────────────────
print("\n[3/4] Exporting Web Datasets...")
data_dir = PROJ_ROOT / "data" / "elections"
data_dir.mkdir(parents=True, exist_ok=True)

# Save corporations JSON
with open(data_dir / "mh_corporations.json", "w", encoding="utf-8") as f:
    json.dump(corps_list, f, ensure_ascii=False)
print(f"  Saved: data/elections/mh_corporations.json")

# Save councils JSON
with open(data_dir / "mh_councils.json", "w", encoding="utf-8") as f:
    json.dump(councils_list, f, ensure_ascii=False)
print(f"  Saved: data/elections/mh_councils.json")

# Write lightweight client JS bundle containing summaries (without huge candidate arrays for speed)
# Detailed candidates can be loaded on demand or included in full
corps_summary = []
for c in corps_list:
    item = dict(c)
    item["candidates"] = item["candidates"][:30] # Top candidates or keep full if needed
    corps_summary.append(item)

councils_summary = []
for c in councils_list:
    item = dict(c)
    item["candidates"] = item["candidates"][:30]
    councils_summary.append(item)

js_bundle_path = PROJ_ROOT / "js" / "data-mh-local-bodies.js"
with open(js_bundle_path, "w", encoding="utf-8") as f:
    f.write("/* Maharashtra Urban Local Bodies: 29 Corporations & 224 Councils */\n")
    f.write("window.MH_CORPORATIONS = ")
    json.dump(corps_list, f, ensure_ascii=False)
    f.write(";\n")
    f.write("window.MH_COUNCILS = ")
    json.dump(councils_list, f, ensure_ascii=False)
    f.write(";\n")
print(f"  Saved: js/data-mh-local-bodies.js ({os.path.getsize(js_bundle_path):,} bytes)")

# ─────────────────────────────────────────────────────────────
# 4. GENERATE SUPABASE SQL SCRIPTS
# ─────────────────────────────────────────────────────────────
print("\n[4/4] Generating Supabase SQL Schemas & Migrations...")
sql_schema = """-- ============================================================
-- Electrol India — Maharashtra Municipal Corporations & Councils Schema
-- ============================================================
CREATE TABLE IF NOT EXISTS mh_municipal_corporations (
  id                   SERIAL PRIMARY KEY,
  name                 TEXT NOT NULL,
  short_code           TEXT,
  election_year        INTEGER DEFAULT 2026,
  total_population     BIGINT,
  sc_population        BIGINT,
  st_population        BIGINT,
  total_wards          INTEGER,
  total_seats          INTEGER,
  leading_party        TEXT,
  source_url           TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mh_corporation_candidates (
  id                   BIGSERIAL PRIMARY KEY,
  corp_id              INTEGER REFERENCES mh_municipal_corporations(id) ON DELETE CASCADE,
  corp_name            TEXT,
  election_year        INTEGER DEFAULT 2026,
  ward                 TEXT,
  seat                 TEXT,
  candidate_name       TEXT NOT NULL,
  political_party      TEXT,
  party_code           TEXT,
  votes                INTEGER DEFAULT 0,
  vote_share_pct       NUMERIC(5,2),
  status               TEXT,
  is_winner            BOOLEAN DEFAULT FALSE,
  ward_reservation     TEXT,
  source_url           TEXT
);

CREATE TABLE IF NOT EXISTS mh_municipal_councils (
  id                   SERIAL PRIMARY KEY,
  name                 TEXT NOT NULL,
  election_year        INTEGER DEFAULT 2025,
  local_body_type      TEXT DEFAULT 'Municipal Council',
  total_wards          INTEGER,
  total_councillors    INTEGER,
  president_winner_name TEXT,
  president_party      TEXT,
  president_votes      INTEGER,
  leading_party        TEXT,
  source_url           TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mh_council_candidates (
  id                   BIGSERIAL PRIMARY KEY,
  council_id           INTEGER REFERENCES mh_municipal_councils(id) ON DELETE CASCADE,
  council_name         TEXT,
  election_year        INTEGER DEFAULT 2025,
  post_type            TEXT,
  ward                 TEXT,
  seat                 TEXT,
  candidate_name       TEXT NOT NULL,
  political_party      TEXT,
  party_code           TEXT,
  votes                INTEGER DEFAULT 0,
  vote_share_pct       NUMERIC(5,2),
  status               TEXT,
  is_winner            BOOLEAN DEFAULT FALSE,
  source_url           TEXT
);

-- Indexes for lightning fast queries
CREATE INDEX IF NOT EXISTS idx_mh_corp_cands_cid ON mh_corporation_candidates(corp_id);
CREATE INDEX IF NOT EXISTS idx_mh_corp_cands_party ON mh_corporation_candidates(party_code);
CREATE INDEX IF NOT EXISTS idx_mh_council_cands_cid ON mh_council_candidates(council_id);
CREATE INDEX IF NOT EXISTS idx_mh_council_cands_post ON mh_council_candidates(post_type);

-- RLS Policies
ALTER TABLE mh_municipal_corporations ENABLE ROW LEVEL SECURITY;
ALTER TABLE mh_corporation_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE mh_municipal_councils ENABLE ROW LEVEL SECURITY;
ALTER TABLE mh_council_candidates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read mh_corps" ON mh_municipal_corporations FOR SELECT USING (true);
CREATE POLICY "Public read mh_corp_cands" ON mh_corporation_candidates FOR SELECT USING (true);
CREATE POLICY "Public read mh_councils" ON mh_municipal_councils FOR SELECT USING (true);
CREATE POLICY "Public read mh_council_cands" ON mh_council_candidates FOR SELECT USING (true);
"""

with open(PROJ_ROOT / "supabase_mh_local_bodies.sql", "w", encoding="utf-8") as f:
    f.write(sql_schema)
print("  Saved schema: supabase_mh_local_bodies.sql")

def sql_e(v):
    if v is None or pd.isna(v): return "NULL"
    return "'" + str(v).replace("'", "''") + "'"

def sql_n(v):
    if v is None or pd.isna(v): return "NULL"
    try:
        return str(int(v))
    except:
        return "NULL"

def sql_f(v):
    if v is None or pd.isna(v): return "NULL"
    try:
        return str(float(v))
    except:
        return "NULL"

sql_inserts = [sql_schema, "\nBEGIN;\n"]

for c in corps_list:
    line = f"""INSERT INTO mh_municipal_corporations (id, name, short_code, election_year, total_population, sc_population, st_population, total_wards, total_seats, leading_party, source_url) VALUES ({c['id']}, {sql_e(c['name'])}, {sql_e(c['short_code'])}, 2026, {sql_n(c['population']['total'])}, {sql_n(c['population']['sc'])}, {sql_n(c['population']['st'])}, {c['wards_count']}, {c['total_seats']}, {sql_e(c['leading_party'])}, {sql_e(c['source'])});\n"""
    sql_inserts.append(line)

for c in councils_list:
    pres = c.get("president") or {}
    line = f"""INSERT INTO mh_municipal_councils (id, name, election_year, local_body_type, total_wards, total_councillors, president_winner_name, president_party, president_votes, leading_party, source_url) VALUES ({c['id']}, {sql_e(c['name'])}, 2025, 'Municipal Council', {c['wards_count']}, {c['total_councillor_seats']}, {sql_e(pres.get('winner_name'))}, {sql_e(pres.get('party_code'))}, {sql_n(pres.get('votes'))}, {sql_e(c['leading_party'])}, {sql_e(c['source'])});\n"""
    sql_inserts.append(line)

sql_inserts.append("COMMIT;\n")

with open(PROJ_ROOT / "supabase_mh_local_bodies_data.sql", "w", encoding="utf-8") as f:
    f.writelines(sql_inserts)

print(f"  Saved SQL data migration: supabase_mh_local_bodies_data.sql ({os.path.getsize(PROJ_ROOT / 'supabase_mh_local_bodies_data.sql'):,} bytes)")
print("Done!")
