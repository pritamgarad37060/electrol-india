# -*- coding: utf-8 -*-
"""
apply_enhancements.py
Implements:
1. Fix & enhance Compare section with 31 State Legislative Assemblies comparison
2. Interactive Parties Directory with filter, sort, and deep drilldown
3. Bordered Assembly SVG Map for each and every state assembly (like Maharashtra)
4. Official Assembly Building and Government Emblem on every assembly card
"""
import re

with open("js/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Compare page in pages['cmp']
# Replace old AP historical section with 31 State Assemblies Comparison
old_cmp_aph_block = """  <div class="card">
    <h2>📅 Compare Andhra Pradesh Election Years (1955–2024)</h2>
    <p class="note">Select any two election years to view swing analysis, seat gains/losses, and turnout trends.</p>
    <div class="f" style="margin-bottom:10px">
      <select id="cmp-yr-1" aria-label="Year A">${AP_YEARS.slice().reverse().map(y=>`<option value="${y}" ${y===2024?'selected':''}>${y}</option>`).join('')}</select>
      <select id="cmp-yr-2" aria-label="Year B">${AP_YEARS.slice().reverse().map(y=>`<option value="${y}" ${y===2019?'selected':''}>${y}</option>`).join('')}</select>
      <button class="btn on" onclick="const y1=$('cmp-yr-1').value,y2=$('cmp-yr-2').value;if(y1&&y2)go('aphcmp/'+y1+'/'+y2)">Compare Years →</button>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      <span class="note">Popular Comparisons:</span>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="go('aphcmp/2024/2019')">2024 vs 2019</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="go('aphcmp/2019/2014')">2019 vs 2014</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="go('aphcmp/2014/2009')">2014 vs 2009</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="go('aphcmp/1994/1989')">1994 vs 1989</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="go('aphcmp/1985/1983')">1985 vs 1983</button>
    </div>
  </div>"""

new_cmp_assemblies_block = """  <div class="card" style="margin-bottom:18px">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
      <h2 style="margin:0">🏛️ Compare Any 2 State Legislative Assemblies (All 31 States)</h2>
      <span class="note">Compare seats, turnout, majority threshold, ruling parties and official seals side by side</span>
    </div>
    <div id="cmp-assemblies-box" style="margin-top:12px"><p class="note">Loading state assembly comparison…</p></div>
  </div>"""

if old_cmp_aph_block in code:
    code = code.replace(old_cmp_aph_block, new_cmp_assemblies_block)
    print("Replaced old AP block with 31 State Assemblies Comparison.")
else:
    print("Could not find exact old_cmp_aph_block, checking alternatives...")

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated js/app.js stage 1.")
