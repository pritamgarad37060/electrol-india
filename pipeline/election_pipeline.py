r"""
╔══════════════════════════════════════════════════════════════════╗
║     ELECTROL INDIA — MASTER ELECTION DATA PIPELINE              ║
║     Version 2.0 — All States, All Election Types                ║
╚══════════════════════════════════════════════════════════════════╝

PURPOSE:
  One script to rule them all. Give it any Excel or PDF file and it:
    1. Extracts data from PDF tables or Excel sheets
    2. Cleans and normalizes all values (party codes, turnout, etc.)
    3. Auto-detects column headers (any ECI format version)
    4. Uploads to Supabase in correct order (elections->parties->constituencies->candidates)
    5. Deduplicates - safe to run twice without creating duplicates
    6. Bumps the website version so browser caches refresh

USAGE (run from PowerShell in project root):
  python pipeline/election_pipeline.py --file "data/up_2022.xlsx" --type assembly --state "Uttar Pradesh" --year 2022
  python pipeline/election_pipeline.py --file "data/ls_2019.pdf"  --type loksabha --year 2019
  python pipeline/election_pipeline.py --scan "data/new_elections" --state "Karnataka" --type assembly
"""
import os, sys, re, json, csv, argparse, unicodedata
from pathlib import Path
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

try:
    import openpyxl
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False
    print("WARN: Run: pip install openpyxl")

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("WARN: Run: pip install pdfplumber")

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

try:
    from supabase import create_client
except ImportError:
    print("ERROR: pip install supabase")
    sys.exit(1)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

PARTY_META = {
    'BJP':    {'name': 'Bharatiya Janata Party','color': '#ff7a00','symbol': 'Lotus'},
    'INC':    {'name': 'Indian National Congress','color': '#1d6fe8','symbol': 'Hand'},
    'SP':     {'name': 'Samajwadi Party','color': '#d62828','symbol': 'Bicycle'},
    'BSP':    {'name': 'Bahujan Samaj Party','color': '#0984e3','symbol': 'Elephant'},
    'AAP':    {'name': 'Aam Aadmi Party','color': '#0072b2','symbol': 'Broom'},
    'AAAP':   {'name': 'Aam Aadmi Party','color': '#0072b2','symbol': 'Broom'},
    'AITC':   {'name': 'All India Trinamool Congress','color': '#2a9d8f','symbol': 'Flowers and Grass'},
    'DMK':    {'name': 'Dravida Munnetra Kazhagam','color': '#6a1b9a','symbol': 'Rising Sun'},
    'AIADMK':{'name': 'All India Anna Dravida Munnetra Kazhagam','color': '#008000','symbol': 'Two Leaves'},
    'TDP':    {'name': 'Telugu Desam Party','color': '#f2c200','symbol': 'Bicycle'},
    'YSRCP':  {'name': 'YSR Congress Party','color': '#2e86de','symbol': 'Ceiling Fan'},
    'JSP':    {'name': 'Jana Sena Party','color': '#e63946','symbol': 'Glass Tumbler'},
    'JD(U)':  {'name': 'Janata Dal (United)','color': '#2e7d32','symbol': 'Arrow'},
    'JD(S)':  {'name': 'Janata Dal (Secular)','color': '#00a86b','symbol': 'Lady Farmer with Paddy'},
    'SHS':    {'name': 'Shiv Sena','color': '#f4a261','symbol': 'Bow and Arrow'},
    'SHSUBT': {'name': 'Shiv Sena (Uddhav Balasaheb Thackeray)','color': '#e76f51','symbol': 'Flaming Torch'},
    'NCP':    {'name': 'Nationalist Congress Party','color': '#1565c0','symbol': 'Clock'},
    'NCPSP':  {'name': 'NCP (Sharadchandra Pawar)','color': '#c2185b','symbol': 'Man Blowing Turha'},
    'CPI(M)': {'name': 'Communist Party of India (Marxist)','color': '#b71c1c','symbol': 'Hammer, Sickle and Star'},
    'CPI':    {'name': 'Communist Party of India','color': '#d63031','symbol': 'Ears of Corn and Sickle'},
    'RJD':    {'name': 'Rashtriya Janata Dal','color': '#1b8a3a','symbol': 'Hurricane Lamp'},
    'BRS':    {'name': 'Bharat Rashtra Samithi','color': '#e84393','symbol': 'Car'},
    'TRS':    {'name': 'Telangana Rashtra Samithi','color': '#e84393','symbol': 'Car'},
    'AIMIM':  {'name': 'All India Majlis-e-Ittehadul Muslimeen','color': '#006266','symbol': 'Kite'},
    'LJPRV':  {'name': 'Lok Janshakti Party (Ram Vilas)','color': '#795548','symbol': 'Helicopter'},
    'JMM':    {'name': 'Jharkhand Mukti Morcha','color': '#16a085','symbol': 'Bow and Arrow'},
    'AGP':    {'name': 'Asom Gana Parishad','color': '#d35400','symbol': 'Elephant'},
    'IND':    {'name': 'Independent','color': '#8d8d8d','symbol': 'Free Symbol'},
    'NOTA':   {'name': 'None of the Above','color': '#bbbbbb','symbol': 'NOTA'},
}

HEADER_ALIASES = {
    'ac_no':           ['ac_no','ac no','ac no.','ac','pc_no','pc no','ward no','s.no','no.','no','serial','constituency no'],
    'name':            ['constituency','constituency name','ac name','ac_name','pc name','ward name','name','seat'],
    'district':        ['district','district name','dist','zila'],
    'category':        ['category','cat','reservation','res','seat type'],
    'electors':        ['electors','total electors','voters','electorate','registered voters','total voters'],
    'votes_polled':    ['votes polled','valid votes','total votes polled','total votes','votes cast'],
    'turnout_pct':     ['turnout','turnout %','poll %','voting %','% polled'],
    'winner_name':     ['winner','winner name','winning candidate','elected candidate','candidate 1'],
    'winner_party':    ['winner party','winning party','winner party code','party 1'],
    'winner_votes':    ['winner votes','winning votes','candidate 1 votes','votes 1'],
    'runner_up_name':  ['runner-up','runner up','runner-up name','runner up name','candidate 2'],
    'runner_up_party': ['runner-up party','runner up party','runner party','party 2'],
    'runner_up_votes': ['runner-up votes','runner up votes','runner votes','candidate 2 votes'],
    'margin':          ['margin','lead margin','victory margin','vote margin'],
    'nota_votes':      ['nota','nota votes','votes for nota'],
    'num_candidates':  ['candidates','total candidates','contestants','no. of candidates'],
    'cand_name':       ['candidate','candidate name','name'],
    'cand_party':      ['party','party code','party affiliation'],
    'cand_gender':     ['gender','sex'],
    'cand_age':        ['age'],
    'evm_votes':       ['evm votes','general votes','evm'],
    'postal_votes':    ['postal votes','postal'],
    'total_votes_cand':['total votes','votes','total'],
    'vote_pct':        ['% of votes','vote %','vote share','vote_pct','% votes'],
}

def norm_header(text):
    if not text: return ''
    text = unicodedata.normalize('NFKD', str(text))
    text = re.sub(r'[^a-z0-9 ]', '', text.lower().strip())
    return re.sub(r'\s+', ' ', text).strip()

def map_headers(headers):
    norm_hdrs = [norm_header(h) for h in headers]
    mapping = {}
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            na = norm_header(alias)
            if na in norm_hdrs:
                mapping[field] = norm_hdrs.index(na)
                break
    return mapping

def safe_float(val):
    if val is None: return None
    try:
        s = str(val).replace('%','').replace(',','').strip()
        return float(s) if s else None
    except: return None

def safe_int(val):
    v = safe_float(val)
    return int(v) if v is not None else None

def norm_party(code):
    if not code: return 'IND'
    code = str(code).strip().upper()
    MAP = {
        'JNP':'JSP','JAN SENA':'JSP','JANSENA':'JSP',
        'YSR CONGRESS':'YSRCP','YSRC':'YSRCP',
        'TELUGU DESAM':'TDP',
        'CONGRESS':'INC','INDIAN NATIONAL CONGRESS':'INC',
        'BHARATIYA JANATA PARTY':'BJP',
        'TRINAMOOL':'AITC','TMC':'AITC',
        'AAM AADMI PARTY':'AAAP',
        'NONE OF THE ABOVE':'NOTA','-':'NOTA',
        'INDEPENDENT':'IND',
    }
    return MAP.get(code, code)

def norm_category(cat):
    if not cat: return 'GEN'
    c = str(cat).strip().upper()
    if c in ('SC','ST'): return c
    return 'GEN'

def norm_gender(g):
    if not g: return None
    g = str(g).strip().upper()
    if g in ('M','MALE','MAN'): return 'M'
    if g in ('F','FEMALE','WOMAN'): return 'F'
    return None

def party_color(code):
    meta = PARTY_META.get(code)
    if meta: return meta['color']
    h = sum(ord(c) * (i+1) for i, c in enumerate(code)) % 360
    return f"hsl({h}, 45%, 48%)"

def read_excel(file_path, sheet=None):
    if not HAS_XLSX: raise ImportError("pip install openpyxl")
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    print(f"  Sheets: {wb.sheetnames}")
    ws = wb[sheet] if sheet and sheet in wb.sheetnames else wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows: return []
    headers = [str(h or '').strip() for h in rows[0]]
    records = [dict(zip(headers, r)) for r in rows[1:] if not all(v is None for v in r)]
    print(f"  Read {len(records)} rows from '{ws.title}'")
    return records

def read_csv(file_path):
    records = []
    with open(file_path, newline='', encoding='utf-8', errors='replace') as f:
        records = list(csv.DictReader(f))
    print(f"  Read {len(records)} rows from CSV")
    return records

def read_json_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    items = data if isinstance(data, list) else (
        data.get('constituencies') or data.get('results') or data.get('data') or [data])
    print(f"  Read {len(items)} records from JSON")
    return items

def extract_pdf_tables(file_path):
    if not HAS_PDF: raise ImportError("pip install pdfplumber")
    print(f"  Extracting tables from PDF...")
    records = []
    with pdfplumber.open(file_path) as pdf:
        all_rows = []
        headers = None
        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                for row in table:
                    cleaned = [str(c or '').strip().replace('\n',' ') for c in row]
                    if all(v == '' for v in cleaned): continue
                    if headers is None:
                        nh = [norm_header(c) for c in cleaned]
                        if any(k in nh for k in ['constituency','ac no','winner','electors','party']):
                            headers = cleaned; continue
                    if headers:
                        all_rows.append(cleaned)
        if not headers:
            return _pdf_text_fallback(file_path)
        col_map = map_headers(headers)
        for row in all_rows:
            if len(row) < 3: continue
            rec = {field: row[idx] for field, idx in col_map.items() if idx < len(row)}
            if rec.get('name') or rec.get('ac_no'):
                records.append(rec)
    print(f"  Extracted {len(records)} records from PDF")
    return records

def _pdf_text_fallback(file_path):
    records = []
    pat = re.compile(
        r'(?P<no>\d+)\s*[.\-|]\s*(?P<name>[A-Z][A-Za-z\s\(\)]+?)\s+'
        r'(?P<winner>[A-Z][A-Za-z\s\.]+?)\s+(?P<party>[A-Z]{2,10})\s+(?P<votes>[\d,]+)',
        re.MULTILINE)
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            for m in pat.finditer(text):
                records.append({'ac_no':m.group('no'),'name':m.group('name').strip(),
                    'winner_name':m.group('winner').strip(),'winner_party':m.group('party').strip(),
                    'winner_votes':m.group('votes').replace(',','')})
    return records

def read_file(file_path, sheet=None):
    ext = Path(file_path).suffix.lower()
    if ext in ('.xlsx','.xls'): return read_excel(file_path, sheet), 'excel'
    elif ext == '.csv': return read_csv(file_path), 'csv'
    elif ext == '.json': return read_json_file(file_path), 'json'
    elif ext == '.pdf': return extract_pdf_tables(file_path), 'pdf'
    else: raise ValueError(f"Unsupported format: {ext}")

def clean_records(records):
    if not records: return []
    headers = list(records[0].keys())
    col_map = map_headers(headers)
    cleaned = []
    for raw in records:
        def v(field):
            if field in col_map:
                idx = col_map[field]
                key = headers[idx] if idx < len(headers) else None
                return raw.get(key)
            return raw.get(field)
        name = re.sub(r'^\d+[\.\-\s]+', '', str(v('name') or '').strip()).strip()
        if not name: continue
        electors = safe_int(v('electors'))
        votes = safe_int(v('votes_polled'))
        turnout = safe_float(v('turnout_pct'))
        if turnout is not None and 0 < turnout <= 1.0: turnout *= 100
        if turnout is None and electors and votes: turnout = round(votes/electors*100, 3)
        winner_party = norm_party(v('winner_party'))
        runner_party = norm_party(v('runner_up_party'))
        winner_votes = safe_int(v('winner_votes'))
        runner_votes = safe_int(v('runner_up_votes'))
        margin = safe_int(v('margin'))
        if margin is None and winner_votes and runner_votes: margin = winner_votes - runner_votes
        cleaned.append({
            'ac_no': safe_int(v('ac_no')),
            'name': name,
            'district': str(v('district') or '').strip() or None,
            'category': norm_category(v('category')),
            'electors': electors,
            'votes_polled': votes,
            'turnout_pct': round(turnout, 3) if turnout else None,
            'winner_name': str(v('winner_name') or '').strip() or None,
            'winner_party': winner_party,
            'winner_votes': winner_votes,
            'runner_up_name': str(v('runner_up_name') or '').strip() or None,
            'runner_up_party': runner_party or None,
            'runner_up_votes': runner_votes,
            'margin': margin,
            'nota_votes': safe_int(v('nota_votes')),
            'num_candidates': safe_int(v('num_candidates')),
        })
    print(f"  Cleaned {len(cleaned)} valid records (from {len(records)} raw rows)")
    return cleaned

def clean_candidate_records(records):
    if not records: return []
    headers = list(records[0].keys())
    col_map = map_headers(headers)
    cleaned = []
    for raw in records:
        def v(field):
            if field in col_map:
                key = headers[col_map[field]]
                return raw.get(key)
            return raw.get(field)
        name = str(v('cand_name') or '').strip()
        if not name: continue
        evm = safe_int(v('evm_votes')) or 0
        postal = safe_int(v('postal_votes')) or 0
        total = safe_int(v('total_votes_cand')) or (evm + postal)
        pct = safe_float(v('vote_pct'))
        if pct and pct <= 1.0: pct *= 100
        cleaned.append({
            'ac_no': safe_int(v('ac_no')),
            'name': name,
            'party': norm_party(v('cand_party')),
            'gender': norm_gender(v('cand_gender')),
            'age': safe_int(v('cand_age')),
            'evm_votes': evm,
            'postal_votes': postal,
            'total_votes': total,
            'vote_pct': round(pct, 4) if pct else None,
        })
    return cleaned

def batch_insert(sb, table, rows, batch_size=200):
    total = len(rows)
    for i in range(0, total, batch_size):
        sb.table(table).insert(rows[i:i+batch_size]).execute()
        print(f"    {table}: {min(i+batch_size,total)}/{total}")

def ensure_state(sb, state_name, cache):
    if not state_name: return None
    if state_name in cache: return cache[state_name]
    res = sb.table('states').select('id').eq('name', state_name).execute()
    if res.data: cache[state_name] = res.data[0]['id']
    else:
        ins = sb.table('states').insert({'name': state_name}).execute()
        cache[state_name] = ins.data[0]['id']
    return cache[state_name]

def ensure_parties(sb, codes, cache):
    if not codes: return
    existing = {p['code'] for p in sb.table('parties').select('code').limit(5000).execute().data}
    new_p = []
    for code in codes:
        if not code or code in cache or code in existing: continue
        meta = PARTY_META.get(code, {})
        new_p.append({'code':code,'full_name':meta.get('name',code),
            'color_hex':meta.get('color',party_color(code)),'eci_symbol':meta.get('symbol')})
        cache.add(code)
    if new_p:
        for i in range(0, len(new_p), 100):
            sb.table('parties').upsert(new_p[i:i+100], on_conflict='code').execute()
        print(f"  Registered {len(new_p)} new parties")

def ensure_election(sb, args):
    election_name = getattr(args,'name',None) or f"{args.state or 'India'} {args.type.title()} {args.year}"
    q = sb.table('elections').select('id,name').eq('year',args.year).eq('type',args.type)
    if args.state: q = q.eq('state',args.state)
    res = q.execute()
    if res.data:
        eid = res.data[0]['id']
        print(f"  Election already exists: '{res.data[0]['name']}' (ID {eid})")
        return eid
    ins = sb.table('elections').insert({
        'year':args.year,'type':args.type,'state':args.state,
        'name':election_name,'total_seats':getattr(args,'total_seats',0) or 0
    }).execute()
    eid = ins.data[0]['id']
    print(f"  Created election: '{election_name}' (ID {eid})")
    return eid

def upload_election(sb, args, records, candidates=None):
    state_cache, party_cache = {}, set()
    all_parties = set()
    for r in records:
        if r.get('winner_party'): all_parties.add(r['winner_party'])
        if r.get('runner_up_party'): all_parties.add(r['runner_up_party'])
    if candidates:
        for c in candidates:
            if c.get('party'): all_parties.add(c['party'])
    ensure_parties(sb, all_parties, party_cache)
    state_id = ensure_state(sb, args.state, state_cache)
    election_id = ensure_election(sb, args)

    if getattr(args,'replace',False):
        print("  --replace: removing existing data...")
        sb.table('candidates').delete().eq('election_id',election_id).execute()
        sb.table('constituencies').delete().eq('election_id',election_id).execute()

    const_rows = [{
        'election_id':election_id,'state_id':state_id,
        'ac_no':r.get('ac_no'),'name':r['name'],'district':r.get('district'),
        'category':r.get('category','GEN'),'electors':r.get('electors'),
        'votes_polled':r.get('votes_polled'),'turnout_pct':r.get('turnout_pct'),
        'winner_name':r.get('winner_name'),'winner_party':r.get('winner_party'),
        'winner_votes':r.get('winner_votes'),'runner_up_name':r.get('runner_up_name'),
        'runner_up_party':r.get('runner_up_party'),'runner_up_votes':r.get('runner_up_votes'),
        'margin':r.get('margin'),'nota_votes':r.get('nota_votes'),
        'num_candidates':r.get('num_candidates'),
    } for r in records]

    print(f"\n  Uploading {len(const_rows)} constituencies...")
    ac_to_id = {}
    for i in range(0, len(const_rows), 100):
        batch = const_rows[i:i+100]
        res = sb.table('constituencies').insert(batch).execute()
        for row in res.data:
            k = row.get('ac_no') or row.get('name')
            ac_to_id[k] = row['id']
        print(f"    constituencies: {min(i+100,len(const_rows))}/{len(const_rows)}")

    sb.table('elections').update({'total_seats':len(const_rows)}).eq('id',election_id).execute()

    cand_rows = []
    if candidates:
        from collections import defaultdict
        by_ac = defaultdict(list)
        for c in candidates: by_ac[c.get('ac_no')].append(c)
        for ac_no, clist in by_ac.items():
            cid = ac_to_id.get(ac_no)
            if not cid: continue
            for idx, c in enumerate(sorted(clist, key=lambda x: x.get('total_votes') or 0, reverse=True)):
                cand_rows.append({'constituency_id':cid,'election_id':election_id,'name':c['name'],
                    'party':c.get('party','IND'),'gender':c.get('gender'),'age':c.get('age'),
                    'evm_votes':c.get('evm_votes',0),'postal_votes':c.get('postal_votes',0),
                    'total_votes':c.get('total_votes',0),'vote_pct':c.get('vote_pct'),
                    'is_winner':(idx==0),'is_nota':(c.get('party')=='NOTA')})
    else:
        for r in records:
            cid = ac_to_id.get(r.get('ac_no')) or ac_to_id.get(r['name'])
            if not cid: continue
            if r.get('winner_name'):
                cand_rows.append({'constituency_id':cid,'election_id':election_id,
                    'name':r['winner_name'],'party':r.get('winner_party','IND'),
                    'total_votes':r.get('winner_votes',0),'is_winner':True,'is_nota':False})
            if r.get('runner_up_name'):
                cand_rows.append({'constituency_id':cid,'election_id':election_id,
                    'name':r['runner_up_name'],'party':r.get('runner_up_party','IND'),
                    'total_votes':r.get('runner_up_votes',0),'is_winner':False,'is_nota':False})

    if cand_rows:
        print(f"\n  Uploading {len(cand_rows)} candidates...")
        batch_insert(sb, 'candidates', cand_rows, 200)

    print(f"\n  Upload complete! Constituencies:{len(const_rows)} Candidates:{len(cand_rows)}")
    return election_id

def export_website_json(project_root, args, records, candidates=None):
    """
    Automatically generate frontend-ready JSON for the website.
    Saves to data/elections/{slug}.json and updates elections_index.json.
    This guarantees the website immediately reflects newly uploaded data.
    """
    elections_dir = project_root / 'data' / 'elections'
    elections_dir.mkdir(parents=True, exist_ok=True)

    state_slug = re.sub(r'[^a-z0-9]+', '_', (args.state or 'india').lower()).strip('_')
    filename = f"{state_slug}_{args.type}_{args.year}.json"
    file_path = elections_dir / filename

    election_name = getattr(args, 'name', None) or f"{args.state or 'India'} {args.type.title()} {args.year}"

    # Group candidates by constituency if available
    cand_map = {}
    if candidates:
        for c in candidates:
            k = c.get('ac_no')
            if k not in cand_map:
                cand_map[k] = []
            cand_map[k].append(c)

    payload = {
        'election': {
            'name': election_name,
            'state': args.state,
            'type': args.type,
            'year': args.year,
            'total_seats': len(records),
            'updated_at': datetime.now().isoformat()
        },
        'constituencies': records,
        'candidates_by_ac': cand_map
    }

    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  Website JSON exported: data/elections/{filename}")

    # Update manifest index
    index_file = elections_dir / 'elections_index.json'
    manifest = []
    if index_file.exists():
        try:
            manifest = json.loads(index_file.read_text(encoding='utf-8'))
        except Exception:
            manifest = []

    # Update or append
    entry = {
        'name': election_name,
        'state': args.state,
        'type': args.type,
        'year': args.year,
        'total_seats': len(records),
        'file': f"data/elections/{filename}",
        'updated_at': datetime.now().isoformat()
    }
    manifest = [m for m in manifest if not (m.get('state') == args.state and m.get('type') == args.type and m.get('year') == args.year)]
    manifest.append(entry)
    manifest.sort(key=lambda x: (x.get('state') or '', -(x.get('year') or 0)))
    index_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  elections_index.json updated ({len(manifest)} total elections)")

def bump_website_version(project_root):
    html_file = project_root / 'index.html'
    if not html_file.exists(): return
    content = html_file.read_text(encoding='utf-8')
    new_v = [0]
    def bump(m):
        v = int(m.group(1)) + 1; new_v[0] = v
        return m.group(0).replace(m.group(1), str(v))
    new_content = re.sub(r'\?v=(\d+)', bump, content)
    html_file.write_text(new_content, encoding='utf-8')
    if new_v[0]: print(f"  index.html version bumped to v{new_v[0]}")

def write_upload_log(project_root, name, stats):
    log_file = project_root / 'upload_log.json'
    log = []
    if log_file.exists():
        try: log = json.loads(log_file.read_text(encoding='utf-8'))
        except: log = []
    log.append({'timestamp':datetime.now().isoformat(),'election':name,'stats':stats})
    log_file.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  Logged to upload_log.json")

def main():
    parser = argparse.ArgumentParser(description="Electrol India Master Pipeline", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--file', help='Excel/CSV/PDF/JSON file to import')
    parser.add_argument('--cands', help='Separate candidates file with full breakdown')
    parser.add_argument('--sheet', help='Excel sheet name')
    parser.add_argument('--scan', help='Auto-scan a folder for election files')
    parser.add_argument('--type', default='assembly',
        choices=['loksabha','assembly','bypoll','municipal','panchayat','council','rajyasabha'])
    parser.add_argument('--year', type=int, default=2024)
    parser.add_argument('--state', help='State name (e.g. "Andhra Pradesh")')
    parser.add_argument('--name', help='Custom election title')
    parser.add_argument('--total_seats', type=int)
    parser.add_argument('--replace', action='store_true', help='Delete existing records before upload')
    parser.add_argument('--dry-run', action='store_true', help='Parse only, skip upload')
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Set SUPABASE_URL and SUPABASE_KEY in .env"); sys.exit(1)

    print("\n" + "="*60)
    print("  ELECTROL INDIA — MASTER ELECTION DATA PIPELINE v2.0")
    print("="*60)
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("  Connected to Supabase OK\n")
    project_root = Path(__file__).parent.parent

    if args.scan:
        folder = Path(args.scan)
        files = list(folder.glob('**/*.xlsx'))+list(folder.glob('**/*.csv'))+\
                list(folder.glob('**/*.pdf'))+list(folder.glob('**/*.json'))
        year_pat = re.compile(r'(\d{4})')
        type_pats = {
            'loksabha': re.compile(r'lok.?sabha|ls_|general|parliament',re.I),
            'bypoll':   re.compile(r'bypoll|by.?poll',re.I),
            'municipal':re.compile(r'municipal|bmc|mcd|ghmc|bbmp|nagar',re.I),
        }
        for f in sorted(files):
            ym = year_pat.search(f.name)
            yr = int(ym.group(1)) if ym else args.year
            et = args.type
            for t, pat in type_pats.items():
                if pat.search(f.name): et = t; break
            print(f"\n  Auto-importing: {f.name} type={et} year={yr}")
            try:
                recs, _ = read_file(str(f))
                cleaned = clean_records(recs)
                if not cleaned: print("  SKIP: no valid records"); continue
                class A: pass
                a = A(); a.type=et; a.year=yr; a.state=args.state; a.name=None; a.replace=getattr(args,'replace',False); a.total_seats=len(cleaned)
                upload_election(sb, a, cleaned)
                export_website_json(project_root, a, cleaned)
                bump_website_version(project_root)
            except Exception as e:
                print(f"  ERROR {f.name}: {e}")
    elif args.file:
        print(f"  Reading: {args.file}")
        recs, fmt = read_file(args.file, args.sheet)
        print(f"  Format: {fmt.upper()}, rows: {len(recs)}")
        cleaned = clean_records(recs)
        if not cleaned: print("  No valid records found."); sys.exit(1)

        candidates = None
        if args.cands:
            print(f"\n  Candidates file: {args.cands}")
            crecs, _ = read_file(args.cands)
            candidates = clean_candidate_records(crecs)
            print(f"  Candidate records: {len(candidates)}")

        if args.dry_run:
            print("\n  DRY RUN — sample records:")
            for r in cleaned[:3]: print(f"    {r}")
            sys.exit(0)

        election_id = upload_election(sb, args, cleaned, candidates)
        export_website_json(project_root, args, cleaned, candidates)
        bump_website_version(project_root)
        write_upload_log(project_root, f"{args.state or 'India'} {args.type} {args.year}",
            {'constituencies':len(cleaned),'candidates':len(candidates or []),'election_id':election_id})
    else:
        parser.print_help(); sys.exit(1)

    print("\n  PIPELINE COMPLETE. Website cache refreshed.")

if __name__ == '__main__':
    main()
