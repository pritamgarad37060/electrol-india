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
YEAR = 2019

print('=' * 60)
print(f'  MAHARASHTRA LOK SABHA {YEAR} — EXCEL IMPORT')
print('=' * 60)
print(f'Source Excel: {EXCEL_PATH}')

print('\n[1/5] Reading Lok Sabha Excel data...')
df = pd.read_excel(EXCEL_PATH, header=2)
df.columns = [str(c).strip() for c in df.columns]
df = df[df['State Name'].str.contains('Maharashtra', case=False, na=False)]

constituencies_dict = {}

PARTY_MAP = {
    'JNP': 'JSP', 'CONGRESS': 'INC', 'BHARATIYA JANATA PARTY': 'BJP',
    'SHIVSENA': 'SHS', 'AAM AADMI PARTY': 'AAAP', 'NCP': 'NCP',
    'NONE OF THE ABOVE': 'NOTA', 'VBA': 'VBA', 'MNS': 'MNS',
    'AIMIM': 'AIMIM', 'CPI': 'CPI', 'CPIM': 'CPI(M)', 'SWP': 'SWP'
}

print(f'  Loaded {len(df)} candidate rows for Maharashtra.')

df['PC NAME'] = df['PC NAME'].astype(str).str.strip()
pc_list = df['PC NAME'].unique()
pc_to_no = {pc: idx+1 for idx, pc in enumerate(pc_list)}

for _, row in df.iterrows():
    raw_pc_name = str(row['PC NAME']).strip()
    pc_no = pc_to_no[raw_pc_name]
    
    category = 'GEN'
    if pd.notna(row.get('CATEGORY')) and row['CATEGORY'] != 'GEN':
        cat_val = str(row['CATEGORY']).strip().upper()
        if cat_val in ['SC', 'ST']: category = cat_val
        elif cat_val == 'GENERAL': category = 'GEN'
        
    electors = int(row['Total Electors']) if pd.notna(row['Total Electors']) else 0
    
    if pc_no not in constituencies_dict:
        constituencies_dict[pc_no] = {
            'ac_no': pc_no, # Maps to ac_no for the unique constraint, or we can use pc_no column
            'pc_no': pc_no,
            'name': raw_pc_name,
            'category': category,
            'electors': electors,
            'candidates': [],
            'votes_polled': 0,
            'nota_votes': 0
        }
    
    raw_cand_name = str(row['CANDIDATES NAME']).strip()
    
    raw_party = str(row['PARTY NAME']).strip().upper()
    party = PARTY_MAP.get(raw_party, raw_party)
    
    is_nota = False
    if 'NOTA' in raw_cand_name.upper() or party == 'NOTA':
        is_nota = True
        raw_cand_name = 'None of the Above'
        party = 'NOTA'
    
    gender_raw = str(row['SEX']).strip().upper()
    if pd.isna(row['SEX']) or gender_raw == 'NAN':
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
    
    vote_pct = float(row.get('OVER TOTAL VOTES POLLED IN CONSTITUENCY', 0))
    if pd.isna(vote_pct): vote_pct = 0.0

    constituencies_dict[pc_no]['candidates'].append({
        'name': raw_cand_name,
        'party': party,
        'gender': gender,
        'age': age,
        'evm_votes': evm_votes,
        'postal_votes': postal_votes,
        'total_votes': total_votes,
        'vote_pct': vote_pct,
        'is_nota': is_nota
    })

constituencies = []
for ac_no, c in constituencies_dict.items():
    cands = c['candidates']
    total_polled = sum(cand['total_votes'] for cand in cands)
    for cand in cands:
        if cand['vote_pct'] == 0.0 and total_polled > 0:
            cand['vote_pct'] = round((cand['total_votes'] / total_polled) * 100, 2)
            
    c['votes_polled'] = total_polled
    c['turnout_pct'] = round((total_polled / c['electors']) * 100, 2) if c['electors'] else 0.0
    
    nota_cand = next((cand for cand in cands if cand['is_nota']), None)
    c['nota_votes'] = nota_cand['total_votes'] if nota_cand else 0
    
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
print(f'  Constituencies: {len(constituencies)}')
total_candidates = sum(len(c['candidates']) for c in constituencies)
print(f'  Candidates:     {total_candidates}')

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

print('\n[4/5] Uploading to Supabase...')
st_res = sb.table('states').select('id').eq('name', 'Maharashtra').execute()
state_id = st_res.data[0]['id'] if st_res.data else sb.table('states').insert({'name': 'Maharashtra'}).execute().data[0]['id']

el_q = sb.table('elections').select('id').eq('year', YEAR).eq('type', 'loksabha').eq('state', 'Maharashtra').execute()
if el_q.data:
    election_id = el_q.data[0]['id']
    print(f'  Using Election ID {election_id}. Clearing existing records...')
    sb.table('candidates').delete().eq('election_id', election_id).execute()
    sb.table('constituencies').delete().eq('election_id', election_id).execute()
else:
    el_ins = sb.table('elections').insert({
        'year': YEAR,
        'type': 'loksabha',
        'state': 'Maharashtra',
        'name': f'Maharashtra Lok Sabha {YEAR}',
        'total_seats': len(constituencies)
    }).execute()
    election_id = el_ins.data[0]['id']
    print(f'  Created Election record: Maharashtra Lok Sabha {YEAR} (ID {election_id})')

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

cand_rows = []
for c in constituencies:
    cid = ac_to_id.get(c['ac_no'])
    if not cid:
        continue
    for idx, cand in enumerate(c['candidates']):
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

print('\n[5/5] Exporting website JSON bundle & updating manifest...')

elections_dir = PROJ_ROOT / 'data' / 'elections'
elections_dir.mkdir(parents=True, exist_ok=True)

cand_map = {c['ac_no']: c['candidates'] for c in constituencies}
export_payload = {
    'election': {
        'id': election_id,
        'name': f'Maharashtra Lok Sabha {YEAR}',
        'state': 'Maharashtra',
        'type': 'loksabha',
        'year': YEAR,
        'total_seats': len(constituencies),
        'updated_at': datetime.now().isoformat()
    },
    'constituencies': [
        {
            'ac_no': c['ac_no'],
            'pc_no': c['pc_no'],
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

json_file = elections_dir / f'maharashtra_loksabha_{YEAR}.json'
json_file.write_text(json.dumps(export_payload, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'  Website JSON created: data/elections/maharashtra_loksabha_{YEAR}.json')

index_file = elections_dir / 'elections_index.json'
manifest = []
if index_file.exists():
    try: manifest = json.loads(index_file.read_text(encoding='utf-8'))
    except Exception: manifest = []

manifest = [m for m in manifest if not (m.get('state') == 'Maharashtra' and m.get('type') == 'loksabha' and m.get('year') == YEAR)]
manifest.append({
    'id': election_id,
    'name': f'Maharashtra Lok Sabha {YEAR}',
    'state': 'Maharashtra',
    'type': 'loksabha',
    'year': YEAR,
    'total_seats': len(constituencies),
    'file': f'data/elections/maharashtra_loksabha_{YEAR}.json',
    'updated_at': datetime.now().isoformat()
})
manifest.sort(key=lambda x: (x.get('state') or '', -(x.get('year') or 0)))
index_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'  elections_index.json updated.')

print('\n' + '=' * 60)
print(f'  MAHARASHTRA LOK SABHA {YEAR} IMPORT COMPLETED SUCCESSFULLY!')
print('=' * 60)
