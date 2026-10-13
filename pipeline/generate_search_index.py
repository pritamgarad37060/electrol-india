# -*- coding: utf-8 -*-
"""
generate_search_index.py - Aggregates all 4,123 assembly constituencies
and key candidates from all 31 state JSONs into a fast, unified search index.
"""
import os
import json

ELECTIONS_DIR = "data/elections"
INDEX_FILE = os.path.join(ELECTIONS_DIR, "assemblies_index.json")

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    master_index = json.load(f)

constituencies = []
candidates = []

for st in master_index["states"]:
    key = st["key"]
    state_name = st["name"]
    year = st["year"]
    file_path = os.path.join(ELECTIONS_DIR, f"{key}_assembly_{year}.json")
    
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, "r", encoding="utf-8") as sf:
        sdata = json.load(sf)
        
    for c in sdata.get("constituencies", []):
        ac_no = c["ac_no"]
        name = c["name"]
        cat = c.get("category", "GEN")
        winner = c.get("winner_name", "")
        party = c.get("winner_party", "")
        runner = c.get("runner_up_name", "")
        runner_party = c.get("runner_up_party", "")
        margin = c.get("margin", 0)
        votes = c.get("votes_polled", 0)
        electors = c.get("electors", 0)
        turnout = c.get("turnout_pct", 0)
        
        # Add constituency
        constituencies.append({
            "n": name,
            "st": state_name,
            "k": key,
            "yr": year,
            "no": ac_no,
            "cat": cat,
            "w": winner,
            "wp": party,
            "r": runner,
            "rp": runner_party,
            "m": margin,
            "t": turnout
        })
        
        # Add winning & runner-up candidates for instant candidate search
        if winner:
            candidates.append({
                "n": winner,
                "p": party,
                "ac": name,
                "no": ac_no,
                "k": key,
                "st": state_name,
                "yr": year,
                "won": True,
                "m": margin
            })
        if runner:
            candidates.append({
                "n": runner,
                "p": runner_party,
                "ac": name,
                "no": ac_no,
                "k": key,
                "st": state_name,
                "yr": year,
                "won": False,
                "m": margin
            })

out_path = os.path.join(ELECTIONS_DIR, "universal_search_index.json")
with open(out_path, "w", encoding="utf-8") as out_f:
    json.dump({
        "total_constituencies": len(constituencies),
        "total_candidates": len(candidates),
        "constituencies": constituencies,
        "candidates": candidates
    }, out_f, separators=(',', ':'))

compact_consts = [[c["n"], c["st"], c["k"], c["no"], c["w"], c["wp"], c["m"], c["t"]] for c in constituencies]
compact_path = os.path.join(ELECTIONS_DIR, "constituencies_compact.json")
with open(compact_path, "w", encoding="utf-8") as cf:
    json.dump(compact_consts, cf, separators=(',', ':'))

print(f"Generated universal search index with {len(constituencies)} constituencies and {len(candidates)} candidates.")
print(f"Full search index size: {os.path.getsize(out_path) / 1024:.1f} KB")
print(f"Compact index size: {os.path.getsize(compact_path) / 1024:.1f} KB")

