import os, sys, re, json, time
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

sys.stdout.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJ_ROOT / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('ERROR: SUPABASE_URL and SUPABASE_KEY must be in .env')
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
EXCEL_PATH = sys.argv[1]
YEAR = int(sys.argv[2])

print('=' * 60)
print(f'  MAHARASHTRA ASSEMBLY {YEAR} — EXCEL IMPORT')
print('=' * 60)
print(f'Source Excel: {EXCEL_PATH}')

# Load Excel
print('\n[1/5] Reading Excel data...')
df = pd.read_excel(EXCEL_PATH, header=2)  # Row 2 contains the headers
# Sometimes the first few rows are empty or headers are slightly offset. 
# We can find the row that has 'STATE/UT NAME' and use it as header
df_raw = pd.read_excel(EXCEL_PATH, header=None)
header_idx = df_raw[df_raw.eq('STATE/UT NAME').any(axis=1)].index
if len(header_idx) > 0:
    df = pd.read_excel(EXCEL_PATH, header=header_idx[0])
else:
    print("Could not find headers. Assuming row 2.")
    df = pd.read_excel(EXCEL_PATH, header=2)

df = df[df['STATE/UT NAME'].notna()]
df = df[df['STATE/UT NAME'].str.contains('Maharashtra', case=False, na=False)]

constituencies_dict = {}

PARTY_MAP = {
    'JNP': 'JSP', 'CONGRESS': 'INC', 'BHARATIYA JANATA PARTY': 'BJP',
    'SHIVSENA': 'SHS', 'AAM AADMI PARTY': 'AAAP', 'NCP': 'NCP',
    'NONE OF THE ABOVE': 'NOTA', 'VBA': 'VBA', 'MNS': 'MNS',
    'AIMIM': 'AIMIM', 'CPI': 'CPI', 'CPIM': 'CPI(M)', 'SWP': 'SWP'
}

print(f'  Loaded {len(df)} candidate rows.')

for _, row in df.iterrows():
    ac_no = int(row['AC NO.'])
    raw_ac_name = str(row['AC NAME']).strip()
    
    # Clean AC name and get category
    category = 'GEN'
    if '(SC)' in raw_ac_name.upper() or '(S.C.)' in raw_ac_name.upper():
        category = 'SC'
    elif '(ST)' in raw_ac_name.upper() or '(S.T.)' in raw_ac_name.upper():
        category = 'ST'
    clean_ac_name = re.sub(r'\s*\((?:SC|ST|S\.C\.|S\.T\.)\)', '', raw_ac_name, flags=re.IGNORECASE).strip()
    
    electors = int(row['TOTAL ELECTORS']) if pd.notna(row['TOTAL ELECTORS']) else 0
    
    if ac_no not in constituencies_dict:
        constituencies_dict[ac_no] = {
            'ac_no': ac_no,
            'name': clean_ac_name,
            'category': category,
            'electors': electors,
            'candidates': [],
            'votes_polled': 0,
            'nota_votes': 0
        }
    
    raw_cand_name = str(row['CANDIDATE NAME']).strip()
    # Remove prefix numbers like "1 AMSHYA"
    clean_cand_name = re.sub(r'^\d+[\.\s]+', '', raw_cand_name).strip()
    
    raw_party = str(row['PARTY']).strip().upper()
    party = PARTY_MAP.get(raw_party, raw_party)
    
    is_nota = False
    if 'NOTA' in raw_cand_name.upper() or party == 'NOTA':
        is_nota = True
        clean_cand_name = 'None of the Above'
        party = 'NOTA'
    
    gender_raw = str(row['GENDER']).strip().upper()
    if pd.isna(row['GENDER']) or gender_raw == 'NAN':
        gender = None
    elif 'M' in gender_raw:
        gender = 'M'
    elif 'F' in gender_raw:
        gender = 'F'
    else:
        gender = 'O'
        
    age = int(row['AGE']) if pd.notna(row['AGE']) and str(row['AGE']).isdigit() else None
    
    evm_votes = int(row['GENERAL']) if pd.notna(row['GENERAL']) else 0
    postal_votes = int(row['POSTAL']) if pd.notna(row['POSTAL']) else 0
    total_votes = int(row['TOTAL']) if pd.notna(row['TOTAL']) else 0
    
    # % VOTES POLLED OVER VALID VOTES + NOTA is usually column 'OVER VALID VOTES + NOTA' or just use math
    vote_pct = float(row.get('OVER VALID VOTES + NOTA', 0)) if 'OVER VALID VOTES + NOTA' in df.columns and pd.notna(row.get('OVER VALID VOTES + NOTA')) else 0.0
    if vote_pct == 0.0 and total_votes > 0:
        # We calculate later if needed
        pass

    constituencies_dict[ac_no]['candidates'].append({
        'name': clean_cand_name,
        'party': party,
        'gender': gender,
        'age': age,
        'evm_votes': evm_votes,
        'postal_votes': postal_votes,
        'total_votes': total_votes,
        'vote_pct': vote_pct,
        'is_nota': is_nota
    })

# Process constituency aggregations
constituencies = []
for ac_no, c in constituencies_dict.items():
    cands = c['candidates']
    # Calculate vote_pct if not set
    total_polled = sum(cand['total_votes'] for cand in cands)
    for cand in cands:
        if cand['vote_pct'] == 0.0 and total_polled > 0:
            cand['vote_pct'] = round((cand['total_votes'] / total_polled) * 100, 2)
            
    c['votes_polled'] = total_polled
    c['turnout_pct'] = round((total_polled / c['electors']) * 100, 2) if c['electors'] else 0.0
    
    nota_cand = next((cand for cand in cands if cand['is_nota']), None)
    c['nota_votes'] = nota_cand['total_votes'] if nota_cand else 0
    
    # Sort candidates
    non_nota = [cand for cand in cands if not cand['is_nota']]
    non_nota.sort(key=lambda x: x['total_votes'], reverse=True)
    
    winner = non_nota[0] if non_nota else {}
    runner = non_nota[1] if len(non_nota) > 1 else {}
    margin = (winner.get('total_votes', 0) - runner.get('total_votes', 0)) if (winner and runner) else 0
    
    c['winner_name'] = winner.get('name')
    c['winner_party'] = winner.get('party')
    c['winner_votes'] = winner.get('total_votes')
    c['runner_up_name'] = runner.get('name')
    c['runner_up_party'] = runner.get('party')
    c['runner_up_votes'] = runner.get('total_votes')
    c['margin'] = margin
    c['num_candidates'] = len(cands)
    
    constituencies.append(c)

print(f'\n[2/5] Extraction Complete!')
print(f'  Constituencies: {len(constituencies)}/288')
total_candidates = sum(len(c['candidates']) for c in constituencies)
print(f'  Candidates:     {total_candidates}')

# ─── PART 3: PARTIES REGISTRATION ────────────────────────────────────────────
print('\n[3/5] Registering parties in Supabase...')
all_parties = set()
for c in constituencies:
    if c.get('winner_party'): all_parties.add(c['winner_party'])
    if c.get('runner_up_party'): all_parties.add(c['runner_up_party'])
    for cand in c['candidates']:
        if cand.get('party'): all_parties.add(cand['party'])

KNOWN_META = {
    'BJP': {'name': 'Bharatiya Janata Party', 'color': '#ff7a00', 'symbol': 'Lotus'},
    'SHS': {'name': 'Shiv Sena', 'color': '#f4a261', 'symbol': 'Bow and Arrow'},
    'NCP': {'name': 'Nationalist Congress Party', 'color': '#1565c0', 'symbol': 'Clock'},
    'INC': {'name': 'Indian National Congress', 'color': '#1d6fe8', 'symbol': 'Hand'},
    'AIMIM': {'name': 'All India Majlis-e-Ittehadul Muslimeen', 'color': '#006266', 'symbol': 'Kite'},
    'SP': {'name': 'Samajwadi Party', 'color': '#d62828', 'symbol': 'Bicycle'},
    'CPI(M)': {'name': 'Communist Party of India (Marxist)', 'color': '#b71c1c', 'symbol': 'Hammer, Sickle and Star'},
    'MNS': {'name': 'Maharashtra Navnirman Sena', 'color': '#e67e22', 'symbol': 'Railway Engine'},
    'VBA': {'name': 'Vanchit Bahujan Aaghadi', 'color': '#5c6bc0', 'symbol': 'Gas Cylinder'},
    'PWPI': {'name': 'Peasants and Workers Party of India', 'color': '#c0392b', 'symbol': 'Cart'},
    'SWP': {'name': 'Swabhimani Paksha', 'color': '#f39c12', 'symbol': 'Bat'},
    'BTP': {'name': 'Bharatiya Tribal Party', 'color': '#16a085', 'symbol': 'Auto-Rickshaw'},
    'JSS': {'name': 'Jan Surajya Shakti', 'color': '#8e44ad', 'symbol': 'Cup and Saucer'},
    'RSPS': {'name': 'Rashtriya Samaj Paksha', 'color': '#e74c3c', 'symbol': 'Cup and Saucer'},
    'AAAP': {'name': 'Aam Aadmi Party', 'color': '#0072b2', 'symbol': 'Broom'},
    'BSP': {'name': 'Bahujan Samaj Party', 'color': '#0984e3', 'symbol': 'Elephant'},
    'IND': {'name': 'Independent', 'color': '#8d8d8d', 'symbol': 'Free Symbol'},
    'NOTA': {'name': 'None of the Above', 'color': '#bbbbbb', 'symbol': 'NOTA'},
}

existing_parties = set(p['code'] for p in sb.table('parties').select('code').limit(5000).execute().data)
new_parties = []

for code in all_parties:
    if not code or code in existing_parties:
        continue
    meta = KNOWN_META.get(code, {})
    h = sum(ord(ch) * (i + 1) for i, ch in enumerate(code)) % 360
    new_parties.append({
        'code': code,
        'full_name': meta.get('name', code),
        'color_hex': meta.get('color', f'hsl({h}, 45%, 48%)'),
        'eci_symbol': meta.get('symbol')
    })

if new_parties:
    for i in range(0, len(new_parties), 100):
        sb.table('parties').upsert(new_parties[i:i+100], on_conflict='code').execute()
    print(f'  Registered {len(new_parties)} new parties.')
else:
    print('  All parties already registered.')

# ─── PART 4: UPLOAD TO SUPABASE ──────────────────────────────────────────────
print('\n[4/5] Uploading to Supabase...')
st_res = sb.table('states').select('id').eq('name', 'Maharashtra').execute()
state_id = st_res.data[0]['id'] if st_res.data else sb.table('states').insert({'name': 'Maharashtra'}).execute().data[0]['id']

# Get or create election ID
el_q = sb.table('elections').select('id').eq('year', YEAR).eq('type', 'assembly').eq('state', 'Maharashtra').execute()
if el_q.data:
    election_id = el_q.data[0]['id']
    print(f'  Using Election ID {election_id}. Clearing existing records...')
    sb.table('candidates').delete().eq('election_id', election_id).execute()
    sb.table('constituencies').delete().eq('election_id', election_id).execute()
else:
    el_ins = sb.table('elections').insert({
        'year': YEAR,
        'type': 'assembly',
        'state': 'Maharashtra',
        'name': f'Maharashtra Assembly {YEAR}',
        'total_seats': len(constituencies)
    }).execute()
    election_id = el_ins.data[0]['id']
    print(f'  Created Election record: Maharashtra Assembly {YEAR} (ID {election_id})')

# Insert constituencies
const_rows = []
for c in constituencies:
    const_rows.append({
        'election_id': election_id,
        'state_id': state_id,
        'ac_no': c['ac_no'],
        'name': c['name'],
        'category': c['category'],
        'electors': c['electors'],
        'votes_polled': c['votes_polled'],
        'turnout_pct': c['turnout_pct'],
        'winner_name': c['winner_name'],
        'winner_party': c['winner_party'],
        'winner_votes': c['winner_votes'],
        'runner_up_name': c['runner_up_name'],
        'runner_up_party': c['runner_up_party'],
        'runner_up_votes': c['runner_up_votes'],
        'margin': c['margin'],
        'nota_votes': c['nota_votes'],
        'num_candidates': c['num_candidates']
    })

ac_to_id = {}
for i in range(0, len(const_rows), 100):
    batch = const_rows[i:i+100]
    res = sb.table('constituencies').insert(batch).execute()
    for row in res.data:
        ac_to_id[row['ac_no']] = row['id']
    print(f'  Constituencies uploaded: {min(i+100, len(const_rows))}/{len(const_rows)}')

sb.table('elections').update({'total_seats': len(constituencies)}).eq('id', election_id).execute()

# Insert candidates
cand_rows = []
for c in constituencies:
    cid = ac_to_id.get(c['ac_no'])
    if not cid:
        continue
    for idx, cand in enumerate(c['candidates']):
        # Determine if winner (sorted by votes desc earlier)
        is_winner = (cand['name'] == c['winner_name'] and cand['party'] == c['winner_party'])
        
        cand_rows.append({
            'constituency_id': cid,
            'election_id': election_id,
            'name': cand['name'],
            'party': cand['party'],
            'gender': cand['gender'],
            'age': cand['age'],
            'evm_votes': cand['evm_votes'],
            'postal_votes': cand['postal_votes'],
            'total_votes': cand['total_votes'],
            'vote_pct': cand['vote_pct'],
            'is_winner': is_winner,
            'is_nota': cand.get('is_nota', False)
        })

print(f'\n  Uploading {len(cand_rows)} candidates...')
for i in range(0, len(cand_rows), 200):
    batch = cand_rows[i:i+200]
    sb.table('candidates').insert(batch).execute()
    print(f'  Candidates uploaded: {min(i+200, len(cand_rows))}/{len(cand_rows)}')

# ─── PART 5: WEBSITE EXPORT & MANIFEST ───────────────────────────────────────
print('\n[5/5] Exporting website JSON bundle & updating manifest...')

elections_dir = PROJ_ROOT / 'data' / 'elections'
elections_dir.mkdir(parents=True, exist_ok=True)

cand_map = {c['ac_no']: c['candidates'] for c in constituencies}
export_payload = {
    'election': {
        'id': election_id,
        'name': f'Maharashtra Assembly {YEAR}',
        'state': 'Maharashtra',
        'type': 'assembly',
        'year': YEAR,
        'total_seats': len(constituencies),
        'updated_at': datetime.now().isoformat()
    },
    'constituencies': [
        {
            'ac_no': c['ac_no'],
            'name': c['name'],
            'category': c['category'],
            'electors': c['electors'],
            'votes_polled': c['votes_polled'],
            'turnout_pct': c['turnout_pct'],
            'winner_name': c['winner_name'],
            'winner_party': c['winner_party'],
            'winner_votes': c['winner_votes'],
            'runner_up_name': c['runner_up_name'],
            'runner_up_party': c['runner_up_party'],
            'runner_up_votes': c['runner_up_votes'],
            'margin': c['margin'],
            'nota_votes': c['nota_votes'],
            'num_candidates': c['num_candidates']
        } for c in constituencies
    ],
    'candidates_by_ac': cand_map
}

json_file = elections_dir / f'maharashtra_assembly_{YEAR}.json'
json_file.write_text(json.dumps(export_payload, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'  Website JSON created: data/elections/maharashtra_assembly_{YEAR}.json')

index_file = elections_dir / 'elections_index.json'
manifest = []
if index_file.exists():
    try: manifest = json.loads(index_file.read_text(encoding='utf-8'))
    except Exception: manifest = []

manifest = [m for m in manifest if not (m.get('state') == 'Maharashtra' and m.get('type') == 'assembly' and m.get('year') == YEAR)]
manifest.append({
    'id': election_id,
    'name': f'Maharashtra Assembly {YEAR}',
    'state': 'Maharashtra',
    'type': 'assembly',
    'year': YEAR,
    'total_seats': len(constituencies),
    'file': f'data/elections/maharashtra_assembly_{YEAR}.json',
    'updated_at': datetime.now().isoformat()
})
manifest.sort(key=lambda x: (x.get('state') or '', -(x.get('year') or 0)))
index_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'  elections_index.json updated.')

html_file = PROJ_ROOT / 'index.html'
if html_file.exists():
    content = html_file.read_text(encoding='utf-8')
    new_v = [0]
    def bump(m):
        v = int(m.group(1)) + 1
        new_v[0] = v
        return m.group(0).replace(m.group(1), str(v))
    new_content = re.sub(r'\?v=(\d+)', bump, content)
    html_file.write_text(new_content, encoding='utf-8')
    if new_v[0]:
        print(f'  index.html version bumped to v{new_v[0]}')

log_file = PROJ_ROOT / 'upload_log.json'
logs = []
if log_file.exists():
    try: logs = json.loads(log_file.read_text(encoding='utf-8'))
    except Exception: logs = []
logs.append({
    'timestamp': datetime.now().isoformat(),
    'election': f'Maharashtra Assembly {YEAR}',
    'seats': len(constituencies),
    'candidates': len(cand_rows),
    'election_id': election_id
})
log_file.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')

print('\n' + '=' * 60)
print(f'  MAHARASHTRA {YEAR} IMPORT COMPLETED SUCCESSFULLY!')
print(f'  Constituencies: {len(constituencies)}/288')
print(f'  Candidates:     {len(cand_rows)}')
print(f'  Election ID:    {election_id}')
print('=' * 60)
