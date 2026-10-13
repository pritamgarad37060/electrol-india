"""
Generate SQL inserts for all 2,810 Municipal Corporation 2026 winners and 5,389 Council 2025 winners
"""
import pandas as pd, re

def escape_sql(s):
    if s is None or pd.isna(s):
        return 'NULL'
    s_clean = str(s).replace("'", "''")
    return f"'{s_clean}'"

print("Reading winners...")
df_corp_c26 = pd.read_excel('scratch_corp.xlsx', sheet_name='Candidates_2026')
w26 = df_corp_c26[df_corp_c26['Winner'].astype(str).str.upper() == 'TRUE']

df_counc_cand = pd.read_excel('scratch_council.xlsx', sheet_name='Candidate_Results')
w_counc = df_counc_cand[df_counc_cand['Winner'].astype(str).str.upper() == 'TRUE']

print(f"Generating SQL for {len(w26)} corp winners and {len(w_counc)} council winners...")

sql_lines = [
    "-- ==========================================================================",
    "-- Supabase Candidates & Winners Insert Statements",
    "-- ==========================================================================",
    "BEGIN;",
    "",
    "-- 1. Corporation Winners"
]

for _, r in w26.iterrows():
    corp_esc = escape_sql(r.get('Municipal_Corporation'))
    ward_esc = escape_sql(r.get('Ward'))
    seat_esc = escape_sql(r.get('Seat'))
    cand_esc = escape_sql(r.get('Candidate'))
    party_esc = escape_sql(r.get('Political_Party'))
    votes = int(r['Votes']) if pd.notnull(r.get('Votes')) else 0
    pct = float(r['Vote_Share_Pct']) if pd.notnull(r.get('Vote_Share_Pct')) else 0.0
    res_esc = escape_sql(r.get('Ward_Reservation'))
    
    sql_lines.append(
        f"INSERT INTO mh_corporation_candidates (election_year, ward, seat, candidate_name, political_party, votes, vote_share_pct, is_winner, ward_reservation) "
        f"VALUES (2026, {ward_esc}, {seat_esc}, {cand_esc}, {party_esc}, {votes}, {pct}, TRUE, {res_esc});"
    )

sql_lines.append("\n-- 2. Council Winners")
for _, r in w_counc.iterrows():
    post_esc = escape_sql(r.get('Post_Type'))
    ward_esc = escape_sql(r.get('Ward'))
    seat_esc = escape_sql(r.get('Seat'))
    cand_esc = escape_sql(r.get('Candidate'))
    party_esc = escape_sql(r.get('Party'))
    votes = int(r['Votes']) if pd.notnull(r.get('Votes')) else 0
    pct = float(r['Vote_Share_Pct']) if pd.notnull(r.get('Vote_Share_Pct')) else 0.0

    sql_lines.append(
        f"INSERT INTO mh_council_candidates (election_year, post_type, ward, seat, candidate_name, political_party, votes, vote_share_pct, is_winner) "
        f"VALUES (2025, {post_esc}, {ward_esc}, {seat_esc}, {cand_esc}, {party_esc}, {votes}, {pct}, TRUE);"
    )

sql_lines.append("\nCOMMIT;")

with open('supabase_maharashtra_winners_import.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated supabase_maharashtra_winners_import.sql with {len(sql_lines)} lines.")
