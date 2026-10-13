import os, re, json
from pathlib import Path
import pandas as pd

SOURCE_DIR = Path(r"C:\Users\prita\OneDrive\Desktop\Last assembly elctions")
OUT_DIR = Path("data/elections")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# State mapping to canonical slugs, names, correct years, and icons
STATE_INFO = {
    "Andhra_Pradesh": {"key": "ap", "name": "Andhra Pradesh", "year": 2024, "icon": "🏛️"},
    "Arunachal_Pradesh": {"key": "ar", "name": "Arunachal Pradesh", "year": 2024, "icon": "🏔️"},
    "Assam": {"key": "as", "name": "Assam", "year": 2021, "icon": "🦏"},
    "Bihar": {"key": "br", "name": "Bihar", "year": 2020, "icon": "🌾"},
    "Chhattisgarh": {"key": "cg", "name": "Chhattisgarh", "year": 2023, "icon": "🌳"},
    "Delhi": {"key": "dl", "name": "Delhi", "year": 2020, "icon": "🏛️"},
    "Goa": {"key": "ga", "name": "Goa", "year": 2022, "icon": "🏖️"},
    "Gujarat": {"key": "gj", "name": "Gujarat", "year": 2022, "icon": "🦁"},
    "Haryana": {"key": "hr", "name": "Haryana", "year": 2024, "icon": "🚜"},
    "Himachal_Pradesh": {"key": "hp", "name": "Himachal Pradesh", "year": 2022, "icon": "🏔️"},
    "Jammu_and_Kashmir": {"key": "jk", "name": "Jammu & Kashmir", "year": 2024, "icon": "❄️"},
    "Jharkhand": {"key": "jh", "name": "Jharkhand", "year": 2024, "icon": "⛏️"},
    "Karnataka": {"key": "ka", "name": "Karnataka", "year": 2023, "icon": "🐘"},
    "Kerala": {"key": "kl", "name": "Kerala", "year": 2021, "icon": "🌴"},
    "Madhya_Pradesh": {"key": "mp", "name": "Madhya Pradesh", "year": 2023, "icon": "🐅"},
    "Maharashtra": {"key": "mh", "name": "Maharashtra", "year": 2024, "icon": "🏢"},
    "Manipur": {"key": "mn", "name": "Manipur", "year": 2022, "icon": "🌺"},
    "Meghalaya": {"key": "ml", "name": "Meghalaya", "year": 2023, "icon": "🌧️"},
    "Mizoram": {"key": "mz", "name": "Mizoram", "year": 2023, "icon": "🌿"},
    "Nagaland": {"key": "nl", "name": "Nagaland", "year": 2023, "icon": "🌄"},
    "Odisha": {"key": "or", "name": "Odisha", "year": 2024, "icon": "🌊"},
    "Puducherry": {"key": "py", "name": "Puducherry", "year": 2021, "icon": "⛵"},
    "Punjab": {"key": "pb", "name": "Punjab", "year": 2022, "icon": "🌾"},
    "Rajasthan": {"key": "rj", "name": "Rajasthan", "year": 2023, "icon": "🏰"},
    "Sikkim": {"key": "sk", "name": "Sikkim", "year": 2024, "icon": "🏔️"},
    "Tamil_Nadu": {"key": "tn", "name": "Tamil Nadu", "year": 2021, "icon": "🛕"},
    "Telangana": {"key": "tg", "name": "Telangana", "year": 2023, "icon": "🏛️"},
    "Tripura": {"key": "tr", "name": "Tripura", "year": 2023, "icon": "🎋"},
    "Uttar_Pradesh": {"key": "up", "name": "Uttar Pradesh", "year": 2022, "icon": "🛕"},
    "Uttarakhand": {"key": "uk", "name": "Uttarakhand", "year": 2022, "icon": "⛰️"},
    "West_Bengal": {"key": "wb", "name": "West Bengal", "year": 2021, "icon": "🐅"}
}

def clean_party(p):
    if not p or pd.isna(p): return "IND"
    s = str(p).strip().upper()
    s = re.sub(r"[\.:\(\)]", "", s)
    mp = {
        "BHARATIYA JANATA PARTY": "BJP", "INDIAN NATIONAL CONGRESS": "INC",
        "AAM AADMI PARTY": "AAP", "AAAP": "AAP", "SAMAJWADI PARTY": "SP",
        "BAHUJAN SAMAJ PARTY": "BSP", "COMMUNIST PARTY OF INDIA MARXIST": "CPI(M)",
        "COMMUNIST PARTY OF INDIA": "CPI", "TELUGU DESAM": "TDP",
        "ALL INDIA TRINAMOOL CONGRESS": "AITC", "DRAVIDA MUNNETRA KAZHAGAM": "DMK",
        "ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM": "AIADMK",
        "JANATA DAL UNITED": "JD(U)", "JANATA DAL SECULAR": "JD(S)",
        "RASHTRIYA JANATA DAL": "RJD", "SHIVSENA": "SHS", "SHIV SENA": "SHS",
        "NATIONALIST CONGRESS PARTY": "NCP", "BHARAT RASHTRA SAMITHI": "BRS",
        "TELANGANA RASHTRA SAMITHI": "TRS", "YSR CONGRESS PARTY": "YSRCP",
        "JANASENA PARTY": "JSP", "INDIAN NATIONAL LOK DAL": "INLD",
        "JANNAYAK JANTA PARTY": "JJP", "RASHTRIYA LOK DAL": "RLD",
        "SHIROMANI AKALI DAL": "SAD", "JHARKHAND MUKTI MORCHA": "JMM",
        "BIJU JANATA DAL": "BJD", "NONE OF THE ABOVE": "NOTA"
    }
    return mp.get(s, s)

def to_int(v, default=0):
    try:
        val = pd.to_numeric(v, errors="coerce")
        return int(val) if pd.notna(val) else default
    except Exception:
        return default

def clean_candidate_name(n):
    if not n or pd.isna(n): return ""
    s = str(n).strip()
    # Remove leading numbering like '1 Shakti Rani Sharma'
    s = re.sub(r"^\d+\s*[\.\-]?\s*", "", s).strip()
    return s.title() if s.isupper() else s

def clean_ac_name(n):
    if not n or pd.isna(n): return ""
    s = str(n).strip()
    s = re.sub(r"^\d+\s*[\.\-]?\s*", "", s).strip()
    return s.title() if s.isupper() else s

index_entries = []
sql_lines = [
    "-- ==========================================================================",
    "-- Supabase Database Cleanup & Multi-State Assembly Migration",
    "-- ==========================================================================",
    "BEGIN;",
    "",
    "-- 1. CLEANUP PREVIOUS YEARS FOR MAHARASHTRA & ANDHRA PRADESH (Keep ONLY 2024)",
    "DELETE FROM candidates WHERE constituency_id IN (",
    "  SELECT c.id FROM constituencies c",
    "  JOIN elections e ON c.election_id = e.id",
    "  WHERE e.type = 'assembly' AND (",
    "    (e.state ILIKE '%Maharashtra%' AND e.year != 2024) OR",
    "    (e.state ILIKE '%Andhra Pradesh%' AND e.year != 2024)",
    "  )",
    ");",
    "DELETE FROM constituencies WHERE election_id IN (",
    "  SELECT id FROM elections",
    "  WHERE type = 'assembly' AND (",
    "    (state ILIKE '%Maharashtra%' AND year != 2024) OR",
    "    (state ILIKE '%Andhra Pradesh%' AND year != 2024)",
    "  )",
    ");",
    "DELETE FROM elections WHERE type = 'assembly' AND (",
    "  (state ILIKE '%Maharashtra%' AND year != 2024) OR",
    "  (state ILIKE '%Andhra Pradesh%' AND year != 2024)",
    ");",
    ""
]

files = sorted(SOURCE_DIR.glob("*.xlsx"))

for f in files:
    # Match state info
    matched_info = None
    for pattern, info in STATE_INFO.items():
        if pattern.lower() in f.name.lower():
            matched_info = info
            break
    if not matched_info:
        # fallback by name splitting
        clean_stem = f.stem.split("_")[0]
        matched_info = {"key": clean_stem.lower()[:4], "name": clean_stem.replace("_", " "), "year": 2024, "icon": "🏛️"}

    state_key = matched_info["key"]
    state_name = matched_info["name"]
    year = matched_info["year"]
    icon = matched_info["icon"]

    # Header row detection
    df_raw = pd.read_excel(f, header=None, nrows=6)
    hdr_row = 3
    for idx, row in df_raw.iterrows():
        txts = [str(x).upper() for x in row.dropna().tolist()]
        if any("AC NO" in x for x in txts) and any("CANDIDATE" in x for x in txts):
            hdr_row = idx
            break

    df = pd.read_excel(f, header=hdr_row)
    col_map = {}
    for c in df.columns:
        cu = str(c).upper().strip()
        if "STATE" in cu: col_map[c] = "state"
        elif "AC NO" in cu: col_map[c] = "ac_no"
        elif "AC NAME" in cu: col_map[c] = "ac_name"
        elif "CANDIDATE" in cu: col_map[c] = "candidate"
        elif "PARTY" in cu: col_map[c] = "party"
        elif cu == "TOTAL ELECTORS": col_map[c] = "electors"
        elif "OVER TOTAL ELECTORS" in cu: col_map[c] = "pct_electors"
        elif "POSTAL" in cu: col_map[c] = "postal"
        elif "GENERAL" in cu: col_map[c] = "general"
        elif cu == "TOTAL": col_map[c] = "total_votes"
        elif "CATEGORY" in cu: col_map[c] = "category"
        elif "SEX" in cu or "GENDER" in cu: col_map[c] = "gender"
        elif "AGE" in cu: col_map[c] = "age"

    df = df.rename(columns=col_map)
    df = df[df["ac_no"].notna()]
    df = df[pd.to_numeric(df["ac_no"], errors="coerce").notna()]
    df["ac_no"] = df["ac_no"].astype(int)

    constituencies = []
    party_seats = {}
    party_votes = {}
    total_electors_sum = 0
    total_votes_polled_sum = 0

    # Group by AC NO
    for ac_no, ac_group in df.groupby("ac_no", sort=True):
        ac_name_raw = str(ac_group["ac_name"].iloc[0]) if "ac_name" in ac_group else f"AC {ac_no}"
        ac_name = clean_ac_name(ac_name_raw)
        category = str(ac_group["category"].iloc[0]).strip() if "category" in ac_group else "GEN"
        if category not in ["SC", "ST"]: category = "GEN"

        # Candidates list
        cands = []
        ac_electors = 0
        if "electors" in ac_group.columns:
            s_el = ac_group["electors"]
            if isinstance(s_el, pd.DataFrame):
                s_el = s_el.iloc[:, 0]
            val_el = pd.to_numeric(s_el, errors="coerce").dropna()
            if len(val_el) > 0:
                ac_electors = int(val_el.max())

        for _, crow in ac_group.iterrows():
            cname = clean_candidate_name(crow.get("candidate", ""))
            if not cname: continue
            party = clean_party(crow.get("party", ""))
            tot_v = to_int(crow.get("total_votes", 0))
            gen_v = to_int(crow.get("general", 0))
            pos_v = to_int(crow.get("postal", 0))
            gender = str(crow.get("gender", "-")).strip().upper()
            gender = "F" if gender in ["F", "FEMALE"] else ("M" if gender in ["M", "MALE"] else "-")
            raw_age = crow.get("age", None)
            age = to_int(raw_age, None) if pd.notna(raw_age) and str(raw_age).strip() not in ["", "NOTA", "-"] else None

            cands.append({
                "name": cname,
                "party": party,
                "gender": gender,
                "age": age,
                "evm_votes": gen_v,
                "postal_votes": pos_v,
                "total_votes": tot_v
            })
            if party != "NOTA":
                party_votes[party] = party_votes.get(party, 0) + tot_v

        # Sort candidates by total_votes desc
        cands.sort(key=lambda x: x["total_votes"], reverse=True)
        ac_votes_polled = sum(c["total_votes"] for c in cands)
        nota_cand = next((c for c in cands if c["party"] == "NOTA"), None)
        nota_votes = nota_cand["total_votes"] if nota_cand else 0

        # Winner & runner-up (excluding NOTA if possible)
        non_nota = [c for c in cands if c["party"] != "NOTA"]
        winner = non_nota[0] if len(non_nota) > 0 else (cands[0] if len(cands)>0 else {"name": "-", "party": "IND", "total_votes": 0})
        runner = non_nota[1] if len(non_nota) > 1 else None

        margin = winner["total_votes"] - (runner["total_votes"] if runner else 0)
        win_party = winner["party"]
        party_seats[win_party] = party_seats.get(win_party, 0) + 1

        turnout_pct = round((ac_votes_polled / ac_electors * 100), 2) if ac_electors > 0 else 0.0

        total_electors_sum += ac_electors
        total_votes_polled_sum += ac_votes_polled

        constituencies.append({
            "ac_no": int(ac_no),
            "name": ac_name,
            "category": category,
            "electors": ac_electors,
            "votes_polled": ac_votes_polled,
            "turnout_pct": turnout_pct,
            "winner_name": winner["name"],
            "winner_party": win_party,
            "winner_votes": winner["total_votes"],
            "runner_up_name": runner["name"] if runner else "",
            "runner_up_party": runner["party"] if runner else "",
            "runner_up_votes": runner["total_votes"] if runner else 0,
            "margin": margin,
            "nota_votes": nota_votes,
            "num_candidates": len(cands),
            "candidates": cands
        })

    # Sort party seats
    sorted_parties = sorted(
        [{"party": p, "seats": s, "votes": party_votes.get(p, 0)} for p, s in party_seats.items()],
        key=lambda x: (x["seats"], x["votes"]),
        reverse=True
    )

    leading_party = sorted_parties[0]["party"] if len(sorted_parties) > 0 else "OTH"
    leading_seats = sorted_parties[0]["seats"] if len(sorted_parties) > 0 else 0
    majority_mark = (len(constituencies) // 2) + 1
    has_majority = leading_seats >= majority_mark

    state_election_data = {
        "state": state_name,
        "key": state_key,
        "year": year,
        "type": "assembly",
        "icon": icon,
        "total_seats": len(constituencies),
        "majority_mark": majority_mark,
        "leading_party": leading_party,
        "leading_seats": leading_seats,
        "status": f"{leading_party} Majority ({leading_seats}/{len(constituencies)})" if has_majority else f"{leading_party} Leading / Plurality",
        "total_electors": total_electors_sum,
        "total_votes_polled": total_votes_polled_sum,
        "avg_turnout_pct": round((total_votes_polled_sum / total_electors_sum * 100), 2) if total_electors_sum > 0 else 0.0,
        "parties": sorted_parties,
        "constituencies": constituencies
    }

    # Save state JSON
    state_file_path = OUT_DIR / f"{state_key}_assembly_{year}.json"
    with open(state_file_path, "w", encoding="utf-8") as out_f:
        json.dump(state_election_data, out_f, ensure_ascii=False, indent=2)

    index_entries.append({
        "key": state_key,
        "name": state_name,
        "year": year,
        "seats": len(constituencies),
        "icon": icon,
        "leading_party": leading_party,
        "leading_seats": leading_seats,
        "top_parties": sorted_parties[:4],
        "file": f"data/elections/{state_key}_assembly_{year}.json"
    })

    # Prepare SQL statements for this state
    clean_state_name_sql = state_name.replace("'", "''")
    sql_lines.append(f"-- State: {state_name} ({year})")
    sql_lines.append(f"INSERT INTO elections (state, type, year, total_seats, is_active, notes) "
                     f"VALUES ('{clean_state_name_sql}', 'assembly', {year}, {len(constituencies)}, TRUE, '{icon} {clean_state_name_sql} Assembly {year}') "
                     f"ON CONFLICT DO NOTHING;")

# Save index JSON
index_entries.sort(key=lambda x: x["name"])
with open(OUT_DIR / "assemblies_index.json", "w", encoding="utf-8") as idx_f:
    json.dump({"total_states": len(index_entries), "states": index_entries}, idx_f, ensure_ascii=False, indent=2)

sql_lines.append("")
sql_lines.append("-- 3. REFRESH & OPTIMIZE DATABASE")
sql_lines.append("VACUUM (ANALYZE) elections;")
sql_lines.append("VACUUM (ANALYZE) constituencies;")
sql_lines.append("VACUUM (ANALYZE) candidates;")
sql_lines.append("COMMIT;")

with open("supabase_cleanup_and_import.sql", "w", encoding="utf-8") as sql_f:
    sql_f.write("\n".join(sql_lines) + "\n")

print(f"SUCCESS! Processed {len(index_entries)} states.")
print(f"Wrote {len(index_entries)} state JSON files to {OUT_DIR}")
print(f"Master index saved to {OUT_DIR / 'assemblies_index.json'}")
print("Saved Supabase cleanup & import script to supabase_cleanup_and_import.sql")
