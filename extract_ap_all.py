"""
Andhra Pradesh Historical Elections (1955–2024) Extractor
=========================================================
Extracts all election data from ECI PDF reports and Excel files.
Produces:
  - data/ap_history/{year}_summary.xlsx
  - data/ap_history/{year}_candidates.xlsx (where available)
  - data/ap_history/{year}.json (rich JSON for website frontend & API)
  - data/ap_history/index.json (master metadata index for website dropdown & stats)
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from collections import Counter, defaultdict

import pypdfium2 as pdfium
import pdfplumber
import pandas as pd
import openpyxl

DATA_DIR = Path("data")
OUT_DIR = DATA_DIR / "ap_history"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Standard metadata for each election
YEAR_META = {
    1955: {"title": "Andhra State Assembly 1955", "era": "Andhra State (pre-merger)", "total_seats": 196},
    1957: {"title": "Andhra Pradesh Assembly 1957 (Telangana)", "era": "Telangana Region post-States Reorg", "total_seats": 105},
    1962: {"title": "Andhra Pradesh Assembly 1962", "era": "Undivided Andhra Pradesh", "total_seats": 300},
    1967: {"title": "Andhra Pradesh Assembly 1967", "era": "Undivided Andhra Pradesh", "total_seats": 287},
    1972: {"title": "Andhra Pradesh Assembly 1972", "era": "Undivided Andhra Pradesh", "total_seats": 287},
    1978: {"title": "Andhra Pradesh Assembly 1978", "era": "Undivided Andhra Pradesh", "total_seats": 294},
    1983: {"title": "Andhra Pradesh Assembly 1983", "era": "N.T. Rama Rao (TDP) First Victory", "total_seats": 294},
    1985: {"title": "Andhra Pradesh Assembly 1985", "era": "TDP Landslide Midterm", "total_seats": 294},
    1989: {"title": "Andhra Pradesh Assembly 1989", "era": "Congress (INC) Comeback", "total_seats": 294},
    1994: {"title": "Andhra Pradesh Assembly 1994", "era": "TDP Wave under NTR", "total_seats": 294},
    1999: {"title": "Andhra Pradesh Assembly 1999", "era": "N. Chandrababu Naidu (TDP)", "total_seats": 294},
    2004: {"title": "Andhra Pradesh Assembly 2004", "era": "Y.S. Rajasekhara Reddy (INC)", "total_seats": 294},
    2009: {"title": "Andhra Pradesh Assembly 2009", "era": "YSR Second Term (Undivided AP)", "total_seats": 294},
    2014: {"title": "Andhra Pradesh Assembly 2014", "era": "Last Undivided Election (AP + Telangana)", "total_seats": 294},
    2019: {"title": "Andhra Pradesh Assembly 2019", "era": "Y.S. Jagan Mohan Reddy (YSRCP) Sweep", "total_seats": 175},
    2024: {"title": "Andhra Pradesh Assembly 2024", "era": "NDA Alliance (TDP+JNP+BJP) Landslide", "total_seats": 175},
}

def clean_party(party):
    if not party:
        return "IND"
    p = party.upper().strip().replace(":", "").replace(".", "")
    if p in ("INC(I)", "INCI"):
        return "INC"
    if p in ("CPI(M)", "CPIM"):
        return "CPM"
    if p in ("YSRCP", "YSR-CONGRESS"):
        return "YSRCP"
    if p in ("JANASENA", "JNP", "JNP(JP)"):
        return "JNP"
    return p

def clean_name(name):
    if not name:
        return ""
    name = re.sub(r'[\(\[\{].*?[\)\]\}]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def parse_summary_text(text, year):
    # Match constituency header
    # e.g.: "FCiOeldN7S:TITUENCY : 84 - DUGGIRALA NUMBER OF SEATS : 1"
    # or "CONSTITUENCY : 1-Sirpur"
    ac_m = re.search(r'TITUENCY\s*:\s*(\d+)\s*[-–]\s*([^\n\r]+)', text, re.I)
    if not ac_m:
        return None
    
    ac_no = int(ac_m.group(1))
    raw_name = ac_m.group(2).strip()
    
    ac_name = re.split(r'\b(MEN|WOMEN|MALE|FEMALE|NUMBER|TYPE|I\.)\b', raw_name, flags=re.I)[0].strip()
    ac_name = clean_name(ac_name)
    if not ac_name:
        ac_name = f"Constituency {ac_no}"
        
    # Electors
    el_m = re.search(r'(?:TOTAL|TOTAL\s+ELECTORS|3\.TOTAL|4\.\s*TOTAL)\s+(?:[\d,]+\s+)*?(\d[\d,]{3,})', text, re.I)
    electors = int(el_m.group(1).replace(",", "")) if el_m else None
    
    # Votes Polled / Valid
    polled_m = re.search(r'(?:1\.\s*POLLED|TOTAL\s+VALID\s+VOTES|TOTAL\s+VOTES\s+POLLED)\s+(?:ON\s+EVM\s+)?(\d[\d,]{3,})', text, re.I)
    if not polled_m:
        polled_m = re.search(r'POLLED\s+(\d[\d,]{3,})', text, re.I)
    polled = int(polled_m.group(1).replace(",", "")) if polled_m else None
    
    # Winner & Runner-up
    win_m = re.search(r'(?:WINNER|Winner)\s*[:\-]?\s*([A-Za-z0-9()\-]+)\s+(.+?)\s+(\d[\d,]+)\s*(?:\n|\r|$)', text, re.I)
    run_m = re.search(r'(?:RUNNER\s*-?\s*UP|Runner\s+up)\s*[:\-]?\s*([A-Za-z0-9()\-]+)\s+(.+?)\s+(\d[\d,]+)\s*(?:\n|\r|$)', text, re.I)
    margin_m = re.search(r'MARGIN\s*[:\-]?\s*(\d[\d,]+)', text, re.I)
    margin = int(margin_m.group(1).replace(",", "")) if margin_m else None
    
    w_party = clean_party(win_m.group(1)) if win_m else None
    w_name = clean_name(win_m.group(2)) if win_m else None
    w_votes = int(win_m.group(3).replace(",", "")) if win_m else None
    
    r_party = clean_party(run_m.group(1)) if run_m else None
    r_name = clean_name(run_m.group(2)) if run_m else None
    r_votes = int(run_m.group(3).replace(",", "")) if run_m else None
    
    if w_party and w_party.isdigit() and w_name:
        parts = w_name.split(' ', 1)
        w_party = clean_party(parts[0])
        w_name = clean_name(parts[1] if len(parts) > 1 else '')
    if r_party and r_party.isdigit() and r_name:
        parts = r_name.split(' ', 1)
        r_party = clean_party(parts[0])
        r_name = clean_name(parts[1] if len(parts) > 1 else '')
    
    calc_margin = margin or ((w_votes - r_votes) if (w_votes and r_votes) else None)
    turnout = round(polled / electors * 100, 2) if (electors and polled and electors > 0) else None
    
    return {
        "ac_no": ac_no,
        "ac_name": ac_name,
        "electors": electors,
        "votes_polled": polled,
        "turnout_pct": turnout,
        "winner_party": w_party,
        "winner_name": w_name,
        "winner_votes": w_votes,
        "runner_party": r_party,
        "runner_name": r_name,
        "runner_votes": r_votes,
        "margin": calc_margin
    }

def process_summary_pdf(pdf_path, year):
    print(f"\n--- Processing {year} ({pdf_path.name}) ---")
    doc = pdfium.PdfDocument(str(pdf_path))
    total_pages = len(doc)
    
    summary_pages = []
    for i, p in enumerate(doc):
        txt = p.get_textpage().get_text_range()
        if "CONSTITUENCY DATA - SUMMARY" in txt or "CONSTITUENCY DATA- SUMMARY" in txt:
            summary_pages.append(i)
            
    print(f"  Found {len(summary_pages)} summary pages across {total_pages} total pages")
    if not summary_pages:
        return []
    
    pl = pdfplumber.open(str(pdf_path))
    records = []
    for page_idx in summary_pages:
        try:
            txt = pl.pages[page_idx].extract_text() or ""
            rec = parse_summary_text(txt, year)
            if rec and rec["winner_party"] and rec["winner_name"]:
                records.append(rec)
        except Exception:
            continue
            
    records.sort(key=lambda x: x["ac_no"])
    print(f"  Successfully extracted {len(records)} constituencies for {year}")
    return records

def process_2019_pdf(pdf_path):
    print(f"\n--- Processing 2019 ({pdf_path.name}) ---")
    doc = pdfium.PdfDocument(str(pdf_path))
    ac_re = re.compile(r'Constituency\s+(\d+)\s*\.\s*([A-Za-z\s\(\)/\-\'\.]+?)\s+TOTAL\s+ELECTORS\s+(\d+)', re.I)
    cand_re = re.compile(
        r'^\s*(\d+)\s+([A-Za-z\s\.\-\']+?)\s+(MALE|FEMALE|THIRD\s+GENDER)\s+(\d{1,3})\s+(?:GENERAL|SC|ST|OBC)\s+([A-Za-z0-9()\-]+)\s+(.+?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*([\d.]+)?',
        re.I
    )
    
    current_ac = None
    all_candidates = []
    ac_map = {}
    
    for page in doc:
        txt = page.get_textpage().get_text_range()
        for line in txt.splitlines():
            line = line.strip()
            if not line:
                continue
            
            m_ac = ac_re.search(line)
            if m_ac:
                ac_no = int(m_ac.group(1))
                ac_name = m_ac.group(2).strip()
                electors = int(m_ac.group(3).replace(",", ""))
                current_ac = {"ac_no": ac_no, "ac_name": ac_name, "electors": electors}
                ac_map[ac_no] = current_ac
                continue
                
            m_c = cand_re.match(line)
            if m_c and current_ac:
                cand_data = {
                    "ac_no": current_ac["ac_no"],
                    "ac_name": current_ac["ac_name"],
                    "electors": current_ac["electors"],
                    "rank": int(m_c.group(1)),
                    "candidate": clean_name(m_c.group(2)),
                    "gender": m_c.group(3).upper(),
                    "age": int(m_c.group(4)),
                    "party": clean_party(m_c.group(5)),
                    "symbol": m_c.group(6).strip(),
                    "evm_votes": int(m_c.group(7).replace(",", "")),
                    "postal_votes": int(m_c.group(8).replace(",", "")),
                    "total_votes": int(m_c.group(9).replace(",", "")),
                    "vote_pct": float(m_c.group(10)) if m_c.group(10) else None
                }
                all_candidates.append(cand_data)
                
    summary_records = []
    cands_by_ac = defaultdict(list)
    for c in all_candidates:
        cands_by_ac[c["ac_no"]].append(c)
        
    for ac_no in sorted(ac_map.keys()):
        ac_info = ac_map[ac_no]
        cands = sorted(cands_by_ac.get(ac_no, []), key=lambda x: -x["total_votes"])
        w = cands[0] if cands else None
        r = cands[1] if len(cands) > 1 else None
        total_v = sum(c["total_votes"] for c in cands)
        margin = (w["total_votes"] - r["total_votes"]) if (w and r) else None
        
        summary_records.append({
            "ac_no": ac_no,
            "ac_name": ac_info["ac_name"],
            "electors": ac_info["electors"],
            "votes_polled": total_v,
            "turnout_pct": round(total_v / ac_info["electors"] * 100, 2) if ac_info["electors"] else None,
            "winner_party": w["party"] if w else None,
            "winner_name": w["candidate"] if w else None,
            "winner_votes": w["total_votes"] if w else None,
            "runner_party": r["party"] if r else None,
            "runner_name": r["candidate"] if r else None,
            "runner_votes": r["total_votes"] if r else None,
            "margin": margin
        })
        
    print(f"  2019: {len(all_candidates)} candidates across {len(summary_records)} constituencies")
    return summary_records, all_candidates

def process_2024_excel(xlsx_path):
    print(f"\n--- Processing 2024 ({xlsx_path.name}) ---")
    df = pd.read_excel(xlsx_path, header=3)
    ac_col = 'AC NO.'
    ac_name_col = 'AC NAME'
    cand_col = 'CANDIDATE NAME'
    party_col = 'PARTY'
    votes_col = 'TOTAL'
    electors_col = 'TOTAL ELECTORS'
    
    summary_records = []
    all_candidates = []
    
    grouped = df.groupby(ac_col)
    for ac_val, group in grouped:
        try:
            ac_no = int(ac_val)
        except Exception:
            continue
            
        first_row = group.iloc[0]
        ac_name = str(first_row.get(ac_name_col, f"AC {ac_no}")).strip()
        electors = int(first_row.get(electors_col, 0)) if electors_col and pd.notna(first_row.get(electors_col)) else None
        
        cands = []
        for _, row in group.iterrows():
            c_name = clean_name(str(row.get(cand_col, "")))
            c_party = clean_party(str(row.get(party_col, "")))
            v = int(row.get(votes_col, 0)) if pd.notna(row.get(votes_col)) else 0
            if c_name:
                cand_info = {
                    "ac_no": ac_no,
                    "ac_name": ac_name,
                    "candidate": c_name,
                    "party": c_party,
                    "total_votes": v
                }
                cands.append(cand_info)
                all_candidates.append(cand_info)
                
        cands.sort(key=lambda x: -x["total_votes"])
        w = cands[0] if cands else None
        r = cands[1] if len(cands) > 1 else None
        total_v = sum(c["total_votes"] for c in cands)
        margin = (w["total_votes"] - r["total_votes"]) if (w and r) else None
        
        summary_records.append({
            "ac_no": ac_no,
            "ac_name": ac_name,
            "electors": electors,
            "votes_polled": total_v,
            "turnout_pct": round(total_v / electors * 100, 2) if electors and electors > 0 else None,
            "winner_party": w["party"] if w else None,
            "winner_name": w["candidate"] if w else None,
            "winner_votes": w["total_votes"] if w else None,
            "runner_party": r["party"] if r else None,
            "runner_name": r["candidate"] if r else None,
            "runner_votes": r["total_votes"] if r else None,
            "margin": margin
        })
        
    summary_records.sort(key=lambda x: x["ac_no"])
    print(f"  2024: {len(all_candidates)} candidates across {len(summary_records)} constituencies")
    return summary_records, all_candidates


def build_export_package(year, summary_records, cand_records=None):
    if not summary_records:
        return None
    
    # 1. Excel Summary
    sum_df = pd.DataFrame(summary_records)
    sum_xlsx = OUT_DIR / f"{year}_summary.xlsx"
    sum_df.to_excel(str(sum_xlsx), index=False)
    
    # 2. Excel Candidates
    if cand_records:
        cand_df = pd.DataFrame(cand_records)
        cand_xlsx = OUT_DIR / f"{year}_candidates.xlsx"
        cand_df.to_excel(str(cand_xlsx), index=False)
        
    # 3. Party tally
    party_seats = Counter()
    party_votes = Counter()
    total_votes = 0
    total_electors = 0
    
    for r in summary_records:
        if r["winner_party"]:
            party_seats[r["winner_party"]] += 1
        if r["winner_votes"]:
            party_votes[r["winner_party"]] += r["winner_votes"]
            total_votes += r["winner_votes"]
        if r["runner_votes"]:
            party_votes[r["runner_party"]] += r["runner_votes"]
            total_votes += r["runner_votes"]
        if r["electors"]:
            total_electors += r["electors"]
            
    party_summary = []
    for p, seats in party_seats.most_common():
        v = party_votes[p]
        party_summary.append({
            "party": p,
            "seats": seats,
            "votes": v,
            "vote_share": round(v / total_votes * 100, 2) if total_votes else 0
        })
        
    winning_party = party_summary[0]["party"] if party_summary else "N/A"
    winning_seats = party_summary[0]["seats"] if party_summary else 0
    
    meta = YEAR_META.get(year, {
        "title": f"Andhra Pradesh Assembly {year}",
        "era": "Historical Assembly",
        "total_seats": len(summary_records)
    })
    
    # 4. JSON structure for website
    json_data = {
        "year": year,
        "title": meta["title"],
        "era": meta["era"],
        "total_seats": len(summary_records),
        "declared_seats": len(summary_records),
        "total_electors": total_electors,
        "total_votes": total_votes,
        "turnout_pct": round(total_votes / total_electors * 100, 2) if total_electors else None,
        "winning_party": winning_party,
        "winning_seats": winning_seats,
        "party_tally": party_summary,
        "constituencies": summary_records,
        "candidates": cand_records if cand_records else []
    }
    
    json_path = OUT_DIR / f"{year}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        
    print(f"  -> Saved {year}_summary.xlsx, {year}.json (Winner: {winning_party} with {winning_seats} seats)")
    
    return {
        "year": year,
        "title": meta["title"],
        "era": meta["era"],
        "total_seats": len(summary_records),
        "winning_party": winning_party,
        "winning_seats": winning_seats,
        "total_votes": total_votes,
        "turnout_pct": json_data["turnout_pct"],
        "party_tally": party_summary[:6]
    }

def main():
    print("=" * 70)
    print("ANDHRA PRADESH ALL-YEAR ELECTION DATA EXTRACTION (1955 - 2024)")
    print("=" * 70)
    
    all_years_index = []
    
    pdf_files = {}
    for f in DATA_DIR.glob("*.pdf"):
        for yr in YEAR_META:
            if str(yr) in f.stem:
                pdf_files[yr] = f
                break
                
    for yr in sorted(YEAR_META.keys()):
        json_file = OUT_DIR / f"{yr}.json"
        if yr not in (1955, 2024) and json_file.exists():
            print(f"Loading existing {yr} JSON...")
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                all_years_index.append({
                    "year": yr,
                    "title": d.get("title", f"Andhra Pradesh Assembly {yr}"),
                    "era": d.get("era", "Historical"),
                    "total_seats": d.get("total_seats", len(d.get("constituencies", []))),
                    "winning_party": d.get("winning_party", "N/A"),
                    "winning_seats": d.get("winning_seats", 0),
                    "total_votes": d.get("total_votes", 0),
                    "turnout_pct": d.get("turnout_pct"),
                    "party_tally": d.get("party_tally", [])[:6]
                })
                continue
            except Exception:
                pass

        if yr == 2024:
            xlsx_path = DATA_DIR / "10-Detailed-Results andra 2024.xlsx"
            if xlsx_path.exists():
                s_rec, c_rec = process_2024_excel(xlsx_path)
                idx_entry = build_export_package(2024, s_rec, c_rec)
                if idx_entry:
                    all_years_index.append(idx_entry)
            continue
            
        if yr == 2019:
            pdf_path = pdf_files.get(2019)
            if pdf_path and pdf_path.exists():
                s_rec, c_rec = process_2019_pdf(pdf_path)
                idx_entry = build_export_package(2019, s_rec, c_rec)
                if idx_entry:
                    all_years_index.append(idx_entry)
            continue
            
        pdf_path = pdf_files.get(yr)
        if pdf_path and pdf_path.exists():
            s_rec = process_summary_pdf(pdf_path, yr)
            idx_entry = build_export_package(yr, s_rec)
            if idx_entry:
                all_years_index.append(idx_entry)
        else:
            print(f"Skipping {yr} (No file found)")
            
    all_years_index.sort(key=lambda x: -x["year"])
    index_file = OUT_DIR / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(all_years_index, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print(f"ALL EXTRACTIONS COMPLETE! Master index created with {len(all_years_index)} elections:")
    for item in all_years_index:
        print(f"  {item['year']}: {item['title']} - Winner: {item['winning_party']} ({item['winning_seats']}/{item['total_seats']} seats)")
    print(f"Files saved in: {OUT_DIR.resolve()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
