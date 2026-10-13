import os, sys, re, json, time
from pathlib import Path
from datetime import datetime
import pdfplumber
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJ_ROOT / '.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('ERROR: SUPABASE_URL and SUPABASE_KEY must be in .env')
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)
PDF_PATH = sys.argv[1]
YEAR = sys.argv[2]
ELECTION_ID = sys.argv[3]

print('=' * 60)
print('  MAHARASHTRA ASSEMBLY {YEAR} — FULL EXTRACTION & IMPORT')
print('=' * 60)
print(f'Source PDF: {PDF_PATH}')

SYMBOLS = ['BOW AND ARROW', 'BOW AND', 'ARROW', 'LOTUS', 'HAND', 'CLOCK', 'BICYCLE', 'ELEPHANT',
           'KITE', 'BROOM', 'RAILWAY ENGINE', 'GAS CYLINDER', 'AUTO- RICKSHAW', 'AUTO-RICKSHAW',
           'AUTO-', 'RICKSHAW', 'CUP & SAUCER', 'CUP AND SAUCER', 'WHISTLE', 'BAT', 'TELEVISION',
           'GAS STOVE', 'COT', 'PRESSURE COOKER', 'ALMIRAH', 'HELICOPTER', 'CAMERA', 'RING',
           'BALLOON', 'KEY', 'ROAD ROLLER', 'BATSMAN', 'LAPTOP', 'FLUTE', 'FOOTBALL', 'CHALATA',
           'AIR CONDITIONER', 'BATTERY TORCH', 'BABY WALKER', 'BENCH', 'BINOCULARS', 'BLACK BOARD',
           'BREAD', 'BRIEF CASE', 'BRUSH', 'BUCKET', 'CAKE', 'CALCULATOR', 'CCTV CAMERA', 'CHAIN',
           'CHAKKI', 'CHESS BOARD', 'CHIMNEY', 'CLIP', 'COAT', 'DIAMOND', 'DISH ANTENNA', 'DOLL',
           'DRILL MACHINE', 'ELECTRIC POLE', 'ENVELOPE', 'FIBRE TRAY', 'FRYING PAN', 'FUNNEL',
           'GIFT PACK', 'GLASS TUMBLER', 'GRAMOPHONE', 'GRAPES', 'HARMONIUM', 'HAT', 'HEADPHONE',
           'HELMET', 'ICE CREAM', 'IMMERSION ROD', 'IRON', 'KETTLE', 'KITCHEN SINK', 'LADY PURSE',
           'LETTER BOX', 'LUNCH BOX', 'MIKE', 'MIXEE', 'NAIL CUTTER', 'NECK TIE', 'NOODLES BOWL',
           'PAN', 'PANT', 'PEANUTS', 'PEARS', 'PEN DRIVE', 'PENCIL SHARPENER', 'PENDULUM',
           'PINEAPPLE', 'PLASTER TROWEL', 'PLATE STAND', 'POT', 'PUNCHING MACHINE', 'RAZOR',
           'REFRIGERATOR', 'ROOM COOLER', 'ROOM HEATER', 'SAFETY PIN', 'SAW', 'SCISSORS',
           'SEWING MACHINE', 'SHIRT', 'SHOE', 'SINK', 'SKATES', 'SLATE', 'SOAP DISH', 'SOCKS',
           'STAMP', 'STAPLER', 'STETHOSCOPE', 'STOOL', 'SUITCASE', 'SWINGS', 'SYRINGE', 'TABLE',
           'TABLE LAMP', 'TEA STRAINER', 'TELEPHONE', 'TENT', 'TOOTH BRUSH', 'TOOTH PASTE',
           'TRACTOR CHALATA KISAN', 'TRUMPET', 'TYPEWRITER', 'TYRES', 'VACUUM CLEANER', 'VIOLIN',
           'WALKING STICK', 'WALL HANGING', 'WALLET', 'WATER CAN', 'WATER HEATER', 'WATER TANK',
           'WATER MELON', 'WINDOW', 'WINNOW', 'WOOL']

def clean_cand_name(name):
    name = re.sub(r'^\d+[\.\s]+', '', name).strip()
    name = re.sub(r'TURNOUT TOTAL.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'VALID VOTES.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Cup\s*&\s*Saucer', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Cup\s*&', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Bow\s*&\s*Arrow', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Bow\s*&', '', name, flags=re.IGNORECASE)
    for s in SYMBOLS:
        name = re.sub(r'\b' + re.escape(s) + r'\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip(' -.,')
    return name

PARTY_MAP = {
    'JNP': 'JSP', 'CONGRESS': 'INC', 'BHARATIYA JANATA PARTY': 'BJP',
    'SHIVSENA': 'SHS', 'AAM AADMI PARTY': 'AAAP', 'NCP': 'NCP',
    'NONE OF THE ABOVE': 'NOTA', 'VBA': 'VBA', 'MNS': 'MNS',
    'AIMIM': 'AIMIM', 'CPI': 'CPI', 'CPIM': 'CPI(M)', 'SWP': 'SWP'
}

# ─── PART 1: EXTRACT ALL TEXT ────────────────────────────────────────────────
print('\n[1/5] Reading PDF text across all pages...')
with pdfplumber.open(PDF_PATH) as pdf:
    full_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
print(f'  Loaded full text ({len(full_text):,} characters).')

pattern = r'(Constituency\s*[:\-.]?\s*(\d+)\s*\.?\s*([A-Za-z0-9\s\(\)\.\-]+?)\s+TOTAL ELECTORS\s*[:\-]?\s*([\d,]+))'
splits = list(re.finditer(pattern, full_text, flags=re.IGNORECASE))
print(f'  Detected {len(splits)} constituencies.')

constituencies = []

for idx, match in enumerate(splits):
    ac_no = int(match.group(2))
    raw_name = match.group(3).strip()
    electors = int(match.group(4).replace(',', ''))
    
    category = 'GEN'
    if '(SC)' in raw_name.upper() or '(S.C.)' in raw_name.upper():
        category = 'SC'
    elif '(ST)' in raw_name.upper() or '(S.T.)' in raw_name.upper():
        category = 'ST'
    clean_name = re.sub(r'\s*\((?:SC|ST|S\.C\.|S\.T\.)\)', '', raw_name, flags=re.IGNORECASE).strip()
    
    start_pos = match.end()
    end_pos = splits[idx+1].start() if idx+1 < len(splits) else len(full_text)
    block_text = full_text[start_pos:end_pos]
    
    # Turnout
    tm = re.search(r'TURN\s*OUT\s*TOTAL:\s*([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d\.]+)', block_text, re.IGNORECASE)
    votes_polled = int(tm.group(3).replace(',', '')) if tm else None
    turnout_pct = float(tm.group(4)) if tm else None
    
    candidates = []
    lines = [l.strip() for l in block_text.split('\n') if l.strip()]
    curr_name_parts = []
    nota_votes = 0
    
    candidates = []
    lines = [l.strip() for l in block_text.split('\n') if l.strip()]
    
    blocks = []
    curr_block = []
    for line in lines:
        if 'TURN OUT TOTAL:' in line.upper() or 'VALID VOTES' in line.upper() or 'CANDIDATE NAME' in line.upper() or line.upper().startswith('PAGE '):
            continue
        if re.match(r'^\d+\s+[A-Za-z]', line) or re.match(r'^\d+\s+NOTA', line):
            if curr_block: blocks.append(curr_block)
            curr_block = [line]
        elif line.strip() != '0':
            curr_block.append(line)
    if curr_block: blocks.append(curr_block)

    for block in blocks:
        block_text_cand = ' '.join(block)
        
        vm = re.search(r'\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d\.]+)\s*', block_text_cand)
        if not vm:
            continue
            
        evm = int(vm.group(1).replace(',', ''))
        postal = int(vm.group(2).replace(',', ''))
        total = int(vm.group(3).replace(',', ''))
        pct = float(vm.group(4))
        
        meta_part = block_text_cand[:vm.start()].strip()
        end_part = block_text_cand[vm.end():].strip()
        
        if 'NOTA' in meta_part.upper():
            candidates.append({
                'name': 'None of the Above',
                'party': 'NOTA',
                'gender': None,
                'age': None,
                'evm_votes': evm,
                'postal_votes': postal,
                'total_votes': total,
                'vote_pct': pct,
                'is_nota': True
            })
            continue
            
        gm = re.search(r'(MALE|FEMALE|THIRD GENDER|M|F|O)\s+(\d+)\s+(GENERAL|GEN|SC|ST)\s+([A-Za-z0-9\(\)\-]+)', meta_part, re.IGNORECASE)
        if gm:
            gender = 'M' if 'M' in gm.group(1).upper() else ('F' if 'F' in gm.group(1).upper() else 'O')
            age = int(gm.group(2))
            raw_party = gm.group(4).upper()
            party = PARTY_MAP.get(raw_party, raw_party)
            
            cand_name_start = meta_part[:gm.start()].strip()
            cand_name_end = meta_part[gm.end():].strip()
            
            raw_full = f"{cand_name_start} {cand_name_end} {end_part}".strip()
            raw_full = re.sub(r'^\d+\s+', '', raw_full).strip()
            clean_full = clean_cand_name(raw_full)
            
            candidates.append({
                'name': clean_full or f'Candidate {len(candidates)+1}',
                'party': party,
                'gender': gender,
                'age': age,
                'evm_votes': evm,
                'postal_votes': postal,
                'total_votes': total,
                'vote_pct': pct,
                'is_nota': False
            })

    non_nota = [c for c in candidates if not c.get('is_nota')]
    non_nota.sort(key=lambda x: x.get('total_votes') or 0, reverse=True)
    winner = non_nota[0] if non_nota else {}
    runner = non_nota[1] if len(non_nota) > 1 else {}
    margin = (winner.get('total_votes', 0) - runner.get('total_votes', 0)) if (winner and runner) else 0
    
    if not votes_polled and candidates:
        votes_polled = sum(c.get('total_votes', 0) for c in candidates)
    if not turnout_pct and electors and votes_polled:
        turnout_pct = round(votes_polled / electors * 100, 2)
        
    constituencies.append({
        'ac_no': ac_no,
        'name': clean_name,
        'category': category,
        'electors': electors,
        'votes_polled': votes_polled,
        'turnout_pct': turnout_pct,
        'winner_name': winner.get('name'),
        'winner_party': winner.get('party'),
        'winner_votes': winner.get('total_votes'),
        'runner_up_name': runner.get('name'),
        'runner_up_party': runner.get('party'),
        'runner_up_votes': runner.get('total_votes'),
        'margin': margin,
        'nota_votes': nota_votes,
        'num_candidates': len(candidates),
        'candidates': candidates
    })

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
el_q = sb.table('elections').select('id').eq('year', int(YEAR)).eq('type', 'assembly').eq('state', 'Maharashtra').execute()
if el_q.data:
    election_id = el_q.data[0]['id']
    print(f'  Using Election ID {election_id}. Clearing existing records...')
    sb.table('candidates').delete().eq('election_id', election_id).execute()
    sb.table('constituencies').delete().eq('election_id', election_id).execute()
else:
    el_ins = sb.table('elections').insert({
        'year': int(YEAR),
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
            'is_winner': (idx == 0 and not cand.get('is_nota')),
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
        'year': int(YEAR),
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

manifest = [m for m in manifest if not (m.get('state') == 'Maharashtra' and m.get('type') == 'assembly' and m.get('year') == int(YEAR))]
manifest.append({
    'id': election_id,
    'name': f'Maharashtra Assembly {YEAR}',
    'state': 'Maharashtra',
    'type': 'assembly',
    'year': int(YEAR),
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
