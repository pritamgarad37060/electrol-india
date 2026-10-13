"""
Process Maharashtra Municipal Corporations & Councils Data
Generates:
1. supabase_maharashtra_local_bodies.sql (PostgreSQL/Supabase schema & migration)
2. js/data-mh-local-bodies.js (Optimized frontend dataset for Electrol India)
"""
import os, sys, re, json
import pandas as pd

CORP_FILE = 'scratch_corp.xlsx'
COUNCIL_FILE = 'scratch_council.xlsx'

CORP_DISTRICT_MAP = {
    'Ahilyanagar': 'Ahilyanagar',
    'Akola': 'Akola',
    'Amravati': 'Amravati',
    'Bhiwandi-Nizampur': 'Thane',
    'Brihanmumbai': 'Mumbai Suburban',
    'Chandrapur': 'Chandrapur',
    'Chhatrapati Sambhajinagar': 'Chhatrapati Sambhajinagar',
    'Dhule': 'Dhule',
    'Ichalkaranji': 'Kolhapur',
    'Jalgaon': 'Jalgaon',
    'Jalna': 'Jalna',
    'Kalyan Dombivali': 'Thane',
    'Kolhapur': 'Kolhapur',
    'Latur': 'Latur',
    'Malegaon': 'Nashik',
    'Mira-Bhaindar': 'Thane',
    'Nagpur': 'Nagpur',
    'Nanded- Waghala': 'Nanded',
    'Nashik': 'Nashik',
    'Navi Mumbai': 'Thane',
    'Panvel': 'Raigad',
    'Parbhani': 'Parbhani',
    'Pimpari Chinchwad': 'Pune',
    'Pune': 'Pune',
    'Sangali-Miraj-Kupwad': 'Sangli',
    'Solapur': 'Solapur',
    'Thane': 'Thane',
    'Ulhasnagar': 'Thane',
    'Vasai Virar City': 'Palghar'
}

def clean_corp_name(name):
    if not isinstance(name, str):
        return ''
    c = re.sub(r'[\uFFFD\?]', ' - ', name)
    c = re.sub(r'\s*2026|\s*All Wards|\s*\(AMC\)|\s*\(BNMC\)|\s*\(CMC\)|\s*\(DMC\)|\s*\(IMC\)|\s*\(JMC\)|\s*\(KDMC\)|\s*\(LMC\)|\s*\(MBMC\)|\s*\(MNC\)|\s*\(NMC\)|\s*\(NMMC\)|\s*\(NWMC\)|\s*\(PCMC\)|\s*\(PMC\)|\s*\(SMKMC\)|\s*\(SMC\)|\s*\(TMC\)|\s*\(UMC\)|\s*\(VVCMC\)|\s*\(BMC\)', '', c)
    c = re.sub(r'\s*Municipal\s*Corporation.*', '', c).strip()
    c = re.sub(r'[\s\-]+$', '', c).strip()
    return c

def clean_council_name(name):
    if not isinstance(name, str):
        return ''
    c = re.sub(r'[\uFFFD\?]', ' ', name)
    c = re.sub(r'Municipal Council\s*', '', c).strip()
    c = re.sub(r'Nagar\s*(Parishad|Panchayat)\s*', '', c, flags=re.IGNORECASE).strip()
    return c

print('Reading Excel files...')
df_corp_meta = pd.read_excel(CORP_FILE, sheet_name='Corporations')
df_corp_c26 = pd.read_excel(CORP_FILE, sheet_name='Candidates_2026')
df_corp_c17 = pd.read_excel(CORP_FILE, sheet_name='Candidates_2017')
df_corp_wards = pd.read_excel(CORP_FILE, sheet_name='Ward_Reservations_2026')

df_counc_meta = pd.read_excel(COUNCIL_FILE, sheet_name='Municipal_Councils')
df_counc_cand = pd.read_excel(COUNCIL_FILE, sheet_name='Candidate_Results')
df_counc_party = pd.read_excel(COUNCIL_FILE, sheet_name='Party_Summary')

print(f'Corporations: {len(df_corp_meta)}, 2026 Candidates: {len(df_corp_c26)}')
print(f'Councils: {len(df_counc_meta)}, Candidates: {len(df_counc_cand)}')

# Process Corporations
corps_list = []
corp_party_totals = {}

for _, r in df_corp_meta.iterrows():
    raw_name = str(r['Municipal_Corporation'])
    cname = clean_corp_name(raw_name)
    dist = CORP_DISTRICT_MAP.get(cname, 'Maharashtra')
    
    # Filter candidates
    cand_subset = df_corp_c26[df_corp_c26['Municipal_Corporation'] == raw_name]
    if len(cand_subset) == 0:
        cand_subset = df_corp_c26[df_corp_c26['Municipal_Corporation'].str.contains(cname[:6], case=False, na=False)]
    
    winners_subset = cand_subset[cand_subset['Winner'].astype(str).str.upper() == 'TRUE']
    
    party_tally = {}
    for p, count in winners_subset['Political_Party'].value_counts().items():
        p_str = str(p).strip()
        party_tally[p_str] = int(count)
        corp_party_totals[p_str] = corp_party_totals.get(p_str, 0) + int(count)
    
    # Top winners sample (ward, seat, candidate, party, votes, pct)
    winners_list = []
    for _, w in winners_subset.iterrows():
        winners_list.append({
            'ward': str(w.get('Ward', '')),
            'seat': str(w.get('Seat', '')),
            'candidate': str(w.get('Candidate', '')),
            'party': str(w.get('Political_Party', '')),
            'votes': int(w['Votes']) if pd.notnull(w.get('Votes')) else 0,
            'pct': float(w['Vote_Share_Pct']) if pd.notnull(w.get('Vote_Share_Pct')) else 0.0,
            'res': str(w.get('Ward_Reservation', '')) if pd.notnull(w.get('Ward_Reservation')) else ''
        })
    
    # Sort winners by ward/seat
    winners_list.sort(key=lambda x: (str(x['ward']), str(x['seat'])))

    # Pop
    tot_pop = int(r['Total_Population']) if pd.notnull(r.get('Total_Population')) else None
    sc_pop = int(r['SC_Population']) if pd.notnull(r.get('SC_Population')) else None
    st_pop = int(r['ST_Population']) if pd.notnull(r.get('ST_Population')) else None

    # Ward count
    ward_count = len(cand_subset['Ward'].unique())
    seat_count = len(winners_subset) if len(winners_subset) > 0 else len(cand_subset['Seat'].unique())

    corps_list.append({
        'id': len(corps_list) + 1,
        'raw_name': raw_name,
        'name': cname,
        'district': dist,
        'total_pop': tot_pop,
        'sc_pop': sc_pop,
        'st_pop': st_pop,
        'ward_count': ward_count,
        'seat_count': seat_count,
        'party_tally': party_tally,
        'winners': winners_list,
        'cand_count_2026': len(cand_subset),
        'source_url': str(r.get('Source_URL', ''))
    })

# Process Councils
councils_list = []
council_party_totals = {}
council_presidents_totals = {}

for _, r in df_counc_meta.iterrows():
    raw_name = str(r['Council'])
    cname = clean_council_name(raw_name)
    
    cand_subset = df_counc_cand[df_counc_cand['Council'] == raw_name]
    if len(cand_subset) == 0:
        cand_subset = df_counc_cand[df_counc_cand['Council'].str.contains(cname[:6], case=False, na=False)]
    
    winners_subset = cand_subset[cand_subset['Winner'].astype(str).str.upper() == 'TRUE']
    
    # Councillor winners vs President winners
    pres_cand = cand_subset[cand_subset['Post_Type'].str.lower() == 'president']
    pres_winner = pres_cand[pres_cand['Winner'].astype(str).str.upper() == 'TRUE']
    
    president_obj = None
    if len(pres_winner) > 0:
        pw = pres_winner.iloc[0]
        president_obj = {
            'candidate': str(pw.get('Candidate', '')),
            'party': str(pw.get('Party', '')),
            'votes': int(pw['Votes']) if pd.notnull(pw.get('Votes')) else 0,
            'pct': float(pw['Vote_Share_Pct']) if pd.notnull(pw.get('Vote_Share_Pct')) else 0.0
        }
        p_str = president_obj['party'].strip()
        council_presidents_totals[p_str] = council_presidents_totals.get(p_str, 0) + 1
    
    party_tally = {}
    for p, count in winners_subset['Party'].value_counts().items():
        p_str = str(p).strip()
        party_tally[p_str] = int(count)
        council_party_totals[p_str] = council_party_totals.get(p_str, 0) + int(count)
    
    # Top councillor winners
    councillor_winners = []
    for _, w in winners_subset[winners_subset['Post_Type'].str.lower() != 'president'].head(40).iterrows():
        councillor_winners.append({
            'ward': str(w.get('Ward', '')),
            'seat': str(w.get('Seat', '')),
            'candidate': str(w.get('Candidate', '')),
            'party': str(w.get('Party', '')),
            'votes': int(w['Votes']) if pd.notnull(w.get('Votes')) else 0,
            'pct': float(w['Vote_Share_Pct']) if pd.notnull(w.get('Vote_Share_Pct')) else 0.0
        })

    councils_list.append({
        'id': len(councils_list) + 1,
        'raw_name': raw_name,
        'name': cname,
        'has_president_page': bool(r.get('President_Result_Page', False)),
        'president': president_obj,
        'ward_count': len(cand_subset['Ward'].dropna().unique()),
        'seat_count': len(winners_subset),
        'party_tally': party_tally,
        'winners': councillor_winners,
        'cand_count': len(cand_subset),
        'url': str(r.get('Council_URL', ''))
    })

# Summary
combined_parties = {}
for p, c in corp_party_totals.items():
    combined_parties[p] = combined_parties.get(p, 0) + c
for p, c in council_party_totals.items():
    combined_parties[p] = combined_parties.get(p, 0) + c

summary_data = {
    'total_corps': len(corps_list),
    'total_councils': len(councils_list),
    'total_corp_seats': sum(c['seat_count'] for c in corps_list),
    'total_council_seats': sum(c['seat_count'] for c in councils_list),
    'corp_parties': sorted([{'party': k, 'seats': v} for k, v in corp_party_totals.items()], key=lambda x: x['seats'], reverse=True),
    'council_parties': sorted([{'party': k, 'seats': v} for k, v in council_party_totals.items()], key=lambda x: x['seats'], reverse=True),
    'combined_parties': sorted([{'party': k, 'seats': v} for k, v in combined_parties.items()], key=lambda x: x['seats'], reverse=True),
    'council_presidents': sorted([{'party': k, 'seats': v} for k, v in council_presidents_totals.items()], key=lambda x: x['seats'], reverse=True)
}

print(f'Writing js/data-mh-local-bodies.js...')
js_content = f"""/**
 * Maharashtra Urban Local Bodies Dataset
 * 29 Municipal Corporations & 224 Municipal Councils
 * Generated for Electrol India
 */
window.MH_LOCAL_SUMMARY = {json.dumps(summary_data, ensure_ascii=False)};
window.MH_CORPS = {json.dumps(corps_list, ensure_ascii=False)};
window.MH_COUNCILS = {json.dumps(councils_list, ensure_ascii=False)};
"""

with open('js/data-mh-local-bodies.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print(f'js/data-mh-local-bodies.js created ({len(js_content)} bytes).')

# Generate SQL file
print('Writing supabase_maharashtra_local_bodies.sql...')
sql_lines = [
    "-- ==========================================================================",
    "-- Supabase / PostgreSQL Schema for Maharashtra Urban Local Bodies",
    "-- Covers 29 Municipal Corporations & 224 Municipal Councils",
    "-- ==========================================================================",
    "BEGIN;",
    "",
    "-- 1. Municipal Corporations Table",
    "CREATE TABLE IF NOT EXISTS mh_municipal_corporations (",
    "    id SERIAL PRIMARY KEY,",
    "    name VARCHAR(150) NOT NULL,",
    "    district VARCHAR(100),",
    "    total_population BIGINT,",
    "    sc_population BIGINT,",
    "    st_population BIGINT,",
    "    ward_count INT DEFAULT 0,",
    "    seat_count INT DEFAULT 0,",
    "    source_url TEXT,",
    "    created_at TIMESTAMPTZ DEFAULT NOW()",
    ");",
    "CREATE INDEX IF NOT EXISTS idx_mh_corp_name ON mh_municipal_corporations(name);",
    "CREATE INDEX IF NOT EXISTS idx_mh_corp_dist ON mh_municipal_corporations(district);",
    "",
    "-- 2. Corporation Candidates & Results",
    "CREATE TABLE IF NOT EXISTS mh_corporation_candidates (",
    "    id SERIAL PRIMARY KEY,",
    "    corporation_id INT REFERENCES mh_municipal_corporations(id) ON DELETE CASCADE,",
    "    election_year INT NOT NULL DEFAULT 2026,",
    "    ward VARCHAR(50) NOT NULL,",
    "    seat VARCHAR(50),",
    "    candidate_name VARCHAR(255) NOT NULL,",
    "    political_party VARCHAR(150),",
    "    votes INT DEFAULT 0,",
    "    vote_share_pct NUMERIC(5,2),",
    "    status VARCHAR(50),",
    "    is_winner BOOLEAN DEFAULT FALSE,",
    "    ward_reservation VARCHAR(100),",
    "    source_url TEXT",
    ");",
    "CREATE INDEX IF NOT EXISTS idx_mh_corp_cand_corp ON mh_corporation_candidates(corporation_id);",
    "CREATE INDEX IF NOT EXISTS idx_mh_corp_cand_party ON mh_corporation_candidates(political_party);",
    "CREATE INDEX IF NOT EXISTS idx_mh_corp_cand_winner ON mh_corporation_candidates(is_winner);",
    "",
    "-- 3. Municipal Councils Table",
    "CREATE TABLE IF NOT EXISTS mh_municipal_councils (",
    "    id SERIAL PRIMARY KEY,",
    "    name VARCHAR(150) NOT NULL,",
    "    district VARCHAR(100),",
    "    ward_count INT DEFAULT 0,",
    "    seat_count INT DEFAULT 0,",
    "    has_president_page BOOLEAN DEFAULT FALSE,",
    "    council_url TEXT,",
    "    created_at TIMESTAMPTZ DEFAULT NOW()",
    ");",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_name ON mh_municipal_councils(name);",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_dist ON mh_municipal_councils(district);",
    "",
    "-- 4. Council Candidates & Results",
    "CREATE TABLE IF NOT EXISTS mh_council_candidates (",
    "    id SERIAL PRIMARY KEY,",
    "    council_id INT REFERENCES mh_municipal_councils(id) ON DELETE CASCADE,",
    "    election_year INT NOT NULL DEFAULT 2025,",
    "    local_body_type VARCHAR(100) DEFAULT 'Municipal Council',",
    "    post_type VARCHAR(100) DEFAULT 'Councillor',",
    "    ward VARCHAR(50),",
    "    seat VARCHAR(50),",
    "    candidate_name VARCHAR(255) NOT NULL,",
    "    political_party VARCHAR(150),",
    "    votes INT DEFAULT 0,",
    "    vote_share_pct NUMERIC(5,2),",
    "    status VARCHAR(50),",
    "    is_winner BOOLEAN DEFAULT FALSE,",
    "    source_url TEXT",
    ");",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_cand_counc ON mh_council_candidates(council_id);",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_cand_post ON mh_council_candidates(post_type);",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_cand_party ON mh_council_candidates(political_party);",
    "CREATE INDEX IF NOT EXISTS idx_mh_council_cand_win ON mh_council_candidates(is_winner);",
    "",
    "-- 5. Insert Master Data for Municipal Corporations"
]

for c in corps_list:
    name_esc = c['name'].replace("'", "''")
    dist_esc = c['district'].replace("'", "''")
    tot_pop_str = str(c['total_pop']) if c['total_pop'] is not None else 'NULL'
    sc_pop_str = str(c['sc_pop']) if c['sc_pop'] is not None else 'NULL'
    st_pop_str = str(c['st_pop']) if c['st_pop'] is not None else 'NULL'
    src_esc = c['source_url'].replace("'", "''")
    sql_lines.append(
        f"INSERT INTO mh_municipal_corporations (name, district, total_population, sc_population, st_population, ward_count, seat_count, source_url) "
        f"VALUES ('{name_esc}', '{dist_esc}', {tot_pop_str}, {sc_pop_str}, {st_pop_str}, {c['ward_count']}, {c['seat_count']}, '{src_esc}') "
        f"ON CONFLICT DO NOTHING;"
    )

sql_lines.append("\n-- 6. Insert Master Data for Municipal Councils")
for c in councils_list:
    name_esc = c['name'].replace("'", "''")
    url_esc = c['url'].replace("'", "''")
    sql_lines.append(
        f"INSERT INTO mh_municipal_councils (name, district, ward_count, seat_count, has_president_page, council_url) "
        f"VALUES ('{name_esc}', 'Maharashtra', {c['ward_count']}, {c['seat_count']}, {'TRUE' if c['has_president_page'] else 'FALSE'}, '{url_esc}') "
        f"ON CONFLICT DO NOTHING;"
    )

sql_lines.append("\nCOMMIT;")

with open('supabase_maharashtra_local_bodies.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))
print(f'supabase_maharashtra_local_bodies.sql created ({len(sql_lines)} lines).')
print('Done!')
