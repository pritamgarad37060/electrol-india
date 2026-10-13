"""
Enhanced Data Builder for Maharashtra Municipal Corporations & Councils
Computes:
- Winners, Runner-ups, and Margins for every Ward (2026 and 2017)
- Standardized Party Names (BJP, Shiv Sena, Shiv Sena (UBT), INC, NCP, NCP (SP), AIMIM, MNS, etc.)
- All 227 Wards for BMC (Brihanmumbai) and all 29 Municipal Corporations
- Complete Ward Matrices, Corporator Lists, and Historical Swings
"""
import os, sys, re, json
import pandas as pd

CORP_FILE = 'scratch_corp.xlsx'
COUNCIL_FILE = 'scratch_council.xlsx'

CORP_CLEAN_MAP = {
    'Brihanmumbai Municipal Corporation (BMC)': 'Brihanmumbai (BMC)',
    'Pune Municipal Corporation (PMC)': 'Pune (PMC)',
    'Nagpur Municipal Corporation (NMC)': 'Nagpur (NMC)',
    'Thane Municipal Corporation (TMC)': 'Thane (TMC)',
    'Pimpari Chinchwad Municipal Corporation (PCMC)': 'Pimpri-Chinchwad (PCMC)',
    'Nashik Municipal Corporation (NMC)': 'Nashik (NMC)',
    'Navi Mumbai Municipal Corporation (NMMC)': 'Navi Mumbai (NMMC)',
    'Kalyan Dombivali Municipal Corporation (KDMC)': 'Kalyan-Dombivli (KDMC)',
    'Vasai Virar City Municipal Corporation (VVCMC)': 'Vasai-Virar (VVCMC)',
    'Chhatrapati Sambhajinagar Municipal': 'Chhatrapati Sambhajinagar',
    'Ahilyanagar Municipal Corporation': 'Ahilyanagar',
    'Solapur Municipal Corporation (SMC)': 'Solapur (SMC)',
    'Amravati Municipal Corporation (AMC)': 'Amravati (AMC)',
    'Kolhapur Municipal Corporation': 'Kolhapur',
    'Akola Municipal Corporation': 'Akola',
    'Bhiwandi-Nizampur Municipal Corporation (BNMC)': 'Bhiwandi-Nizampur (BNMC)',
    'Mira-Bhaindar Municipal Corporation (MBMC)': 'Mira-Bhayandar (MBMC)',
    'Ulhasnagar Municipal Corporation (UMC)': 'Ulhasnagar (UMC)',
    'Sangali-Miraj-Kupwad Municipal Corporation (SMKMC)': 'Sangli-Miraj-Kupwad',
    'Panvel Municipal Corporation': 'Panvel',
    'Jalgaon': 'Jalgaon',
    'Dhule Municipal Corporation (DMC)': 'Dhule',
    'Latur Municipal Corporation (LMC)': 'Latur',
    'Chandrapur Municipal Corporation (CMC)': 'Chandrapur',
    'Parbhani Municipal Corporation': 'Parbhani',
    'Nanded- Waghala Municipal Corporation (NWMC)': 'Nanded-Waghala',
    'Jalna Municipal Corporation': 'Jalna',
    'Malegaon Municipal Corporation (MNC)': 'Malegaon',
    'Ichalkaranji Municipal Corporation (IMC)': 'Ichalkaranji'
}

CORP_DISTRICT_MAP = {
    'Brihanmumbai (BMC)': 'Mumbai & Mumbai Suburban',
    'Pune (PMC)': 'Pune',
    'Nagpur (NMC)': 'Nagpur',
    'Thane (TMC)': 'Thane',
    'Pimpri-Chinchwad (PCMC)': 'Pune',
    'Nashik (NMC)': 'Nashik',
    'Navi Mumbai (NMMC)': 'Thane',
    'Kalyan-Dombivli (KDMC)': 'Thane',
    'Vasai-Virar (VVCMC)': 'Palghar',
    'Chhatrapati Sambhajinagar': 'Chhatrapati Sambhajinagar',
    'Ahilyanagar': 'Ahilyanagar',
    'Solapur (SMC)': 'Solapur',
    'Amravati (AMC)': 'Amravati',
    'Kolhapur': 'Kolhapur',
    'Akola': 'Akola',
    'Bhiwandi-Nizampur (BNMC)': 'Thane',
    'Mira-Bhayandar (MBMC)': 'Thane',
    'Ulhasnagar (UMC)': 'Thane',
    'Sangli-Miraj-Kupwad': 'Sangli',
    'Panvel': 'Raigad',
    'Jalgaon': 'Jalgaon',
    'Dhule': 'Dhule',
    'Latur': 'Latur',
    'Chandrapur': 'Chandrapur',
    'Parbhani': 'Parbhani',
    'Nanded-Waghala': 'Nanded',
    'Jalna': 'Jalna',
    'Malegaon': 'Nashik',
    'Ichalkaranji': 'Kolhapur'
}

def clean_corp_name(raw):
    raw_str = str(raw or '').strip()
    for k, v in CORP_CLEAN_MAP.items():
        if k.lower() in raw_str.lower():
            return v
    c = re.sub(r'[\uFFFD\?]', ' ', raw_str)
    c = re.sub(r'2026|All Wards|\(.*\)', '', c).strip()
    c = re.sub(r'Municipal Corporation.*', '', c).strip()
    return c or raw_str

def normalize_party(p):
    if not p or pd.isna(p):
        return 'Independent'
    p_str = str(p).strip()
    p_up = p_str.upper()

    # Shiv Sena splits & spellings
    if 'UBT' in p_up or 'UDDHAV' in p_up:
        return 'Shiv Sena (UBT)'
    if p_up in ['SHIVSENA', 'SHIVESENA', 'SHIV SENA', 'SHS'] or p_up.startswith('SHIV SENA'):
        return 'Shiv Sena'

    # BJP
    if 'BHARATIYA JANATA' in p_up or 'BHARTIYA JANATA' in p_up or p_up == 'BJP':
        return 'BJP'

    # Congress
    if 'CONGRESS' in p_up and 'NATIONALIST' not in p_up:
        return 'INC'

    # NCP splits
    if 'SHARADCHANDRA' in p_up or '(SP)' in p_up or '- SP' in p_up or 'NCPSP' in p_up:
        return 'NCP (SP)'
    if 'NATIONALIST CONGRESS' in p_up or p_up == 'NCP':
        return 'NCP'

    # AIMIM
    if 'MAJLIS' in p_up or 'AIMIM' in p_up:
        return 'AIMIM'

    # MNS
    if 'NAVNIRMAN' in p_up or p_up == 'MNS':
        return 'MNS'

    # VBA
    if 'VANCHIT' in p_up or 'BHARIP' in p_up or p_up == 'VBA':
        return 'VBA'

    # BVA
    if 'BAHUJAN VIKAS' in p_up or p_up == 'BVA':
        return 'BVA'

    # BSP
    if 'BAHUJAN SAMAJ' in p_up or p_up == 'BSP':
        return 'BSP'

    # SP
    if p_up in ['SAMAJWADI PARTY', 'SP']:
        return 'SP'

    # Communist
    if 'COMMUNIST' in p_up or 'CPI(M)' in p_up or 'CPM' in p_up:
        return 'CPI(M)'

    # PWPI
    if 'SHETKARI KAMGAR' in p_up or 'PWPI' in p_up:
        return 'PWPI'

    # RPI
    if 'REPUBLICAN' in p_up or 'RPI' in p_up:
        return 'RPI(A)'

    if 'NOTA' in p_up:
        return 'NOTA'
    if 'INDEPENDENT' in p_up or p_up == 'IND':
        return 'Independent'

    return p_str

print("Loading Corporation and Council datasets...")
df_corp_meta = pd.read_excel(CORP_FILE, sheet_name='Corporations')
df_corp_c26 = pd.read_excel(CORP_FILE, sheet_name='Candidates_2026')
df_corp_c17 = pd.read_excel(CORP_FILE, sheet_name='Candidates_2017')
df_counc_meta = pd.read_excel(COUNCIL_FILE, sheet_name='Municipal_Councils')
df_counc_cand = pd.read_excel(COUNCIL_FILE, sheet_name='Candidate_Results')

df_corp_c26['Party_Norm'] = df_corp_c26['Political_Party'].apply(normalize_party)
df_corp_c17['Party_Norm'] = df_corp_c17['Political_Party'].apply(normalize_party)
df_counc_cand['Party_Norm'] = df_counc_cand['Party'].apply(normalize_party)

corps_list = []
corp_tally_2026 = {}
corp_tally_2017 = {}

for _, r in df_corp_meta.iterrows():
    raw_name = str(r['Municipal_Corporation'])
    cname = clean_corp_name(raw_name)
    dist = CORP_DISTRICT_MAP.get(cname, 'Maharashtra')

    # Candidates for this corporation
    c26_sub = df_corp_c26[df_corp_c26['Municipal_Corporation'] == raw_name]
    if len(c26_sub) == 0:
        c26_sub = df_corp_c26[df_corp_c26['Municipal_Corporation'].str.contains(cname[:6], case=False, na=False)]
    
    c17_sub = df_corp_c17[df_corp_c17['Municipal_Corporation'] == raw_name]
    if len(c17_sub) == 0:
        c17_sub = df_corp_c17[df_corp_c17['Municipal_Corporation'].str.contains(cname[:6], case=False, na=False)]

    # Process 2026 Wards (Group by ward and seat to extract winner, runner-up & margin)
    wards_26 = []
    tally_26 = {}
    grouped_26 = {}
    for _, row in c26_sub.iterrows():
        w_no = row['Ward']
        s_id = row.get('Seat', '')
        key = (w_no, s_id)
        if key not in grouped_26:
            grouped_26[key] = []
        grouped_26[key].append(row)

    for (w_no, s_id), cands in grouped_26.items():
        cands_sorted = sorted(cands, key=lambda x: x.get('Votes', 0) if pd.notnull(x.get('Votes')) else 0, reverse=True)
        winner = cands_sorted[0]
        runner = cands_sorted[1] if len(cands_sorted) > 1 else None

        w_votes = int(winner['Votes']) if pd.notnull(winner.get('Votes')) else 0
        r_votes = int(runner['Votes']) if runner is not None and pd.notnull(runner.get('Votes')) else 0
        margin = w_votes - r_votes if runner is not None else w_votes

        p_norm = winner['Party_Norm']
        tally_26[p_norm] = tally_26.get(p_norm, 0) + 1
        corp_tally_2026[p_norm] = corp_tally_2026.get(p_norm, 0) + 1

        wards_26.append({
            'ward': int(w_no) if str(w_no).isdigit() else str(w_no),
            'seat': str(s_id) if pd.notnull(s_id) else '',
            'candidate': str(winner.get('Candidate', '')),
            'party': p_norm,
            'raw_party': str(winner.get('Political_Party', '')),
            'votes': w_votes,
            'pct': float(winner['Vote_Share_Pct']) if pd.notnull(winner.get('Vote_Share_Pct')) else 0.0,
            'res': str(winner.get('Ward_Reservation', 'General')) if pd.notnull(winner.get('Ward_Reservation')) else 'General',
            'runner': str(runner.get('Candidate', '')) if runner is not None else '',
            'runner_party': runner['Party_Norm'] if runner is not None else '',
            'runner_votes': r_votes,
            'margin': margin
        })

    def ward_sort_key(x):
        w = x['ward']
        if isinstance(w, int):
            return (w, str(x['seat']))
        return (9999, str(w), str(x['seat']))

    wards_26.sort(key=ward_sort_key)

    # Process 2017 Wards
    wards_17 = []
    tally_17 = {}
    grouped_17 = {}
    for _, row in c17_sub.iterrows():
        w_no = row['Ward']
        s_id = row.get('Seat', '')
        key = (w_no, s_id)
        if key not in grouped_17:
            grouped_17[key] = []
        grouped_17[key].append(row)

    for (w_no, s_id), cands in grouped_17.items():
        cands_sorted = sorted(cands, key=lambda x: x.get('Votes', 0) if pd.notnull(x.get('Votes')) else 0, reverse=True)
        winner = cands_sorted[0]
        runner = cands_sorted[1] if len(cands_sorted) > 1 else None

        w_votes = int(winner['Votes']) if pd.notnull(winner.get('Votes')) else 0
        r_votes = int(runner['Votes']) if runner is not None and pd.notnull(runner.get('Votes')) else 0
        margin = w_votes - r_votes if runner is not None else w_votes

        p_norm = winner['Party_Norm']
        tally_17[p_norm] = tally_17.get(p_norm, 0) + 1
        corp_tally_2017[p_norm] = corp_tally_2017.get(p_norm, 0) + 1

        wards_17.append({
            'ward': int(w_no) if str(w_no).isdigit() else str(w_no),
            'seat': str(s_id) if pd.notnull(s_id) else '',
            'candidate': str(winner.get('Candidate', '')),
            'party': p_norm,
            'votes': w_votes,
            'pct': float(winner['Vote_Share_Pct']) if pd.notnull(winner.get('Vote_Share_Pct')) else 0.0,
            'runner': str(runner.get('Candidate', '')) if runner is not None else '',
            'runner_party': runner['Party_Norm'] if runner is not None else '',
            'runner_votes': r_votes,
            'margin': margin
        })
    wards_17.sort(key=ward_sort_key)

    # Slug for direct URL (e.g. 'bmc', 'pune', 'thane', 'nagpur')
    slug = 'bmc' if 'brihanmumbai' in cname.lower() or 'bmc' in cname.lower() else re.sub(r'[^a-z0-9]+', '-', cname.lower()).strip('-')

    corp_obj = {
        'id': len(corps_list) + 1,
        'slug': slug,
        'name': cname,
        'raw_name': raw_name,
        'district': dist,
        'total_pop': int(r['Total_Population']) if pd.notnull(r.get('Total_Population')) else None,
        'sc_pop': int(r['SC_Population']) if pd.notnull(r.get('SC_Population')) else None,
        'st_pop': int(r['ST_Population']) if pd.notnull(r.get('ST_Population')) else None,
        'ward_count_2026': len(c26_sub['Ward'].dropna().unique()),
        'seat_count_2026': len(wards_26),
        'party_tally_2026': tally_26,
        'winners_2026': wards_26,
        'ward_count_2017': len(c17_sub['Ward'].dropna().unique()),
        'seat_count_2017': len(wards_17),
        'party_tally_2017': tally_17,
        'winners_2017': wards_17
    }
    corps_list.append(corp_obj)

# Process Municipal Councils
councils_list = []
council_tally_2025 = {}
council_pres_tally = {}

def clean_council_name(name):
    c = re.sub(r'Municipal Council\s*', '', str(name or ''), flags=re.IGNORECASE).strip()
    c = re.sub(r'[\uFFFD\?]', ' ', c).strip()
    return c

for _, r in df_counc_meta.iterrows():
    raw_name = str(r['Council'])
    cname = clean_council_name(raw_name)

    c_sub = df_counc_cand[df_counc_cand['Council'] == raw_name]
    if len(c_sub) == 0:
        c_sub = df_counc_cand[df_counc_cand['Council'].str.contains(cname[:6], case=False, na=False)]
    
    # President winner
    pres_rows = c_sub[c_sub['Post_Type'].str.lower() == 'president']
    pres_winner = pres_rows[pres_rows['Winner'].astype(str).str.upper() == 'TRUE']
    president_obj = None
    if len(pres_winner) > 0:
        pw = pres_winner.iloc[0]
        p_norm = pw['Party_Norm']
        president_obj = {
            'candidate': str(pw.get('Candidate', '')),
            'party': p_norm,
            'raw_party': str(pw.get('Party', '')),
            'votes': int(pw['Votes']) if pd.notnull(pw.get('Votes')) else 0,
            'pct': float(pw['Vote_Share_Pct']) if pd.notnull(pw.get('Vote_Share_Pct')) else 0.0
        }
        council_pres_tally[p_norm] = council_pres_tally.get(p_norm, 0) + 1

    # Councillor winners & Tally
    councillor_winners = []
    tally = {}
    winners = c_sub[c_sub['Winner'].astype(str).str.upper() == 'TRUE']
    for _, w in winners.iterrows():
        p = w['Party_Norm']
        tally[p] = tally.get(p, 0) + 1
        council_tally_2025[p] = council_tally_2025.get(p, 0) + 1
        if str(w.get('Post_Type', '')).lower() != 'president':
            councillor_winners.append({
                'ward': str(w.get('Ward', '')),
                'seat': str(w.get('Seat', '')),
                'candidate': str(w.get('Candidate', '')),
                'party': p,
                'votes': int(w['Votes']) if pd.notnull(w.get('Votes')) else 0,
                'pct': float(w['Vote_Share_Pct']) if pd.notnull(w.get('Vote_Share_Pct')) else 0.0
            })
    councillor_winners.sort(key=lambda x: (str(x['ward']).zfill(4), str(x['seat'])))

    councils_list.append({
        'id': len(councils_list) + 1,
        'name': cname,
        'raw_name': raw_name,
        'district': 'Maharashtra',
        'has_president': bool(president_obj),
        'president': president_obj,
        'seat_count': len(winners),
        'ward_count': len(c_sub['Ward'].dropna().unique()),
        'party_tally': tally,
        'winners': councillor_winners[:50]
    })

# Comparison Summary
comparison_parties = []
all_parties = sorted(list(set(list(corp_tally_2026.keys()) + list(corp_tally_2017.keys()))))
for p in all_parties:
    s26 = corp_tally_2026.get(p, 0)
    s17 = corp_tally_2017.get(p, 0)
    diff = s26 - s17
    comparison_parties.append({
        'party': p,
        'seats_2026': s26,
        'seats_2017': s17,
        'diff': diff
    })
comparison_parties.sort(key=lambda x: (x['seats_2026'] + x['seats_2017']), reverse=True)

summary_data = {
    'total_corps': len(corps_list),
    'total_councils': len(councils_list),
    'corps_seats_2026': sum(c['seat_count_2026'] for c in corps_list),
    'corps_seats_2017': sum(c['seat_count_2017'] for c in corps_list),
    'councils_seats_2025': sum(c['seat_count'] for c in councils_list),
    'corp_tally_2026': sorted([{'party': k, 'seats': v} for k, v in corp_tally_2026.items()], key=lambda x: x['seats'], reverse=True),
    'corp_tally_2017': sorted([{'party': k, 'seats': v} for k, v in corp_tally_2017.items()], key=lambda x: x['seats'], reverse=True),
    'council_tally_2025': sorted([{'party': k, 'seats': v} for k, v in council_tally_2025.items()], key=lambda x: x['seats'], reverse=True),
    'council_pres_tally': sorted([{'party': k, 'seats': v} for k, v in council_pres_tally.items()], key=lambda x: x['seats'], reverse=True),
    'comparison_parties': comparison_parties
}

print(f"Writing js/data-mh-local-bodies.js...")
js_content = f"""/**
 * Maharashtra Municipal Corporations (2026 & 2017) & Municipal Councils (2025)
 * With Ward-wise Winners, Runner-ups, Margins, and Reservations
 */
window.MH_MUNC_SUMMARY = {json.dumps(summary_data, ensure_ascii=False)};
window.MH_CORPS = {json.dumps(corps_list, ensure_ascii=False)};
window.MH_COUNCILS = {json.dumps(councils_list, ensure_ascii=False)};
"""

with open('js/data-mh-local-bodies.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"js/data-mh-local-bodies.js written ({len(js_content)} bytes).")
print("Done!")
