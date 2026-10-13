# -*- coding: utf-8 -*-
"""
patch_app_js.py - Updates js/app.js to integrate all 31 state assemblies,
interactive seat maps & grids, candidate drilldowns, and purge pre-2024 historical AP & MH data.
"""
import re
import shutil

# 1. Back up app.js
shutil.copyfile('js/app.js', 'js/app.js.bak')

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 2. Add extra party colors into CM
extra_parties = {
    'AAP': '#008ece', 'AGP': '#006400', 'BJD': '#006400', 'INLD': '#006400',
    'JMM': '#2e7d32', 'JD(S)': '#2e7d32', 'SAD': '#d35400', 'IUML': '#006400',
    'SKM': '#d35400', 'NPP': '#0984e3', 'NPEP': '#0984e3', 'NPF': '#00b894',
    'NDPP': '#e67e22', 'MNF': '#2980b9', 'ZPM': '#e74c3c', 'AIADMK': '#1b8a3a',
    'PMK': '#f39c12', 'VCK': '#2980b9', 'RLP': '#e67e22', 'BAP': '#16a085',
    'HAMS': '#e67e22', 'VIP': '#e74c3c', 'RLD': '#006400', 'LJPRV': '#1565c0',
    'LJP': '#1565c0', 'CPI(ML)(L)': '#c0392b', 'JKN': '#d63031', 'PDP': '#16a085',
    'TIPRA': '#e74c3c', 'IPFT': '#f39c12', 'SDF': '#0984e3', 'BOPF': '#f39c12',
    'UPPL': '#f39c12', 'KEC': '#006400', 'RSP': '#c0392b', 'AJSUP': '#9b59b6'
}
cm_additions = ','.join(f"'{k}':'{v}'" if '(' in k or ')' in k else f"{k}:'{v}'" for k, v in extra_parties.items())
content = content.replace("KMPP:'#fdcb6e'};", "KMPP:'#fdcb6e'," + cm_additions + "};", 1)

# 3. Clean up AP historical section at top (lines 57-110)
# Find from "// AP historical years config" to "loadSeatHistory();"
old_top_hist_start = content.find("// AP historical years config")
old_top_hist_end = content.find("const pages={")
if old_top_hist_start != -1 and old_top_hist_end != -1:
    replacement_top = """// Universal State Assemblies Configuration & Cache
const STATE_REGIONS = {
  hr:'North',hp:'North',jk:'North',pb:'North',uk:'North',up:'North',dl:'North',
  ap:'South',ka:'South',kl:'South',tn:'South',tg:'South',
  mh:'West',gj:'West',ga:'West',
  br:'East',jh:'East',or:'East',wb:'East',
  cg:'Central',mp:'Central',
  ar:'North-East',as:'North-East',mn:'North-East',ml:'North-East',mz:'North-East',nl:'North-East',sk:'North-East',tr:'North-East',
  py:'UT',dl:'UT',jk:'UT'
};
let ASM_INDEX = null;
const ASM_CACHE = {};

function loadAsmIndex(cb){
  if(ASM_INDEX){cb&&cb(ASM_INDEX);return}
  fetch('data/elections/assemblies_index.json').then(r=>r.json()).then(d=>{
    ASM_INDEX=d;cb&&cb(d);
  }).catch(()=>{cb&&cb({total_states:0,states:[]})});
}

function loadStateAsm(key, cb){
  if(ASM_CACHE[key]){cb&&cb(ASM_CACHE[key]);return}
  loadAsmIndex(idx=>{
    const st=(idx.states||[]).find(s=>s.key===key);
    const file=st?st.file:`data/elections/${key}_assembly_2024.json`;
    fetch(file).then(r=>r.json()).then(d=>{
      ASM_CACHE[key]=d;cb&&cb(d);
    }).catch(err=>{console.error(err);cb&&cb(null)});
  });
}

"""
    content = content[:old_top_hist_start] + replacement_top + content[old_top_hist_end:]

# 4. Update home page tile description from '175 seats · 1955–2024' to '175 seats · 2024'
content = content.replace("['🏛️','Andhra Pradesh','175 seats · 1955–2024','ap']", "['🏛️','Andhra Pradesh','175 seats · 2024','ap']")

# 5. Remove historical years bar and pre-2024 years in 'mh'
old_mh_code = """'mh':(yr)=>{
  if(yr && yr!=='2024'){
    setTimeout(()=>{
      const el=$('app');if(!el)return;
      el.innerHTML=`<p>Loading Maharashtra ${yr} data…</p>`;
      fetch(`data/elections/maharashtra_assembly_${yr}.json`).then(r=>r.json()).then(data=>{
        if(!data){el.innerHTML=`<p class="note">Data for ${yr} not available.</p>`;return}
        window._mh19Data=data;
        const consts=data.constituencies||[];
        const partyCounts={};
        const partyVotes={};
        const totVotes=consts.reduce((s,c)=>s+(c.votes_polled||0),0);
        const totElectors=consts.reduce((s,c)=>s+(c.electors||0),0);
        const avgTurnout=totElectors?(totVotes/totElectors*100).toFixed(1):'61.4';
        consts.forEach(c=>{
          if(c.winner_party){
            partyCounts[c.winner_party]=(partyCounts[c.winner_party]||0)+1;
          }
          if(c.candidates){
            c.candidates.forEach(cd=>{
              if(cd.party&&!cd.is_nota){
                partyVotes[cd.party]=(partyVotes[cd.party]||0)+(cd.total_votes||0);
              }
            });
          }
        });
        const psList=Object.keys(partyCounts).map(p=>({c:p,seats:partyCounts[p],votes:partyVotes[p]||0})).sort((a,b)=>b.seats-a.seats||b.votes-a.votes);
        const ndaSeats=(partyCounts['BJP']||0)+(partyCounts['SHS']||0);
        const upaSeats=(partyCounts['NCP']||0)+(partyCounts['INC']||0);
        const othSeats=288-ndaSeats-upaSeats;
        
        el.innerHTML=`
          ${bc([['Home',''],['Maharashtra Assembly','mh'],[yr]])}
          <div class="card" style="padding:12px 16px;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
              <span class="yr-label">📅 Select Year:</span>
              <button class="yr-btn" onclick="go('mh')">2024</button>
              <button class="yr-btn ${yr==='2019'?'on':''}" onclick="go('mh/2019')">2019</button>
              <button class="yr-btn ${yr==='2014'?'on':''}" onclick="go('mh/2014')">2014</button>
              <button class="yr-btn ${yr==='2009'?'on':''}" onclick="go('mh/2009')">2009</button>
              <button class="yr-btn ${yr==='2004'?'on':''}" onclick="go('mh/2004')">2004</button>
            </div>
            <p class="note" style="margin:4px 0 0">Viewing: <b>${yr} Assembly Election</b> · Maharashtra · 288 Seats</p>
          </div>
          <h1>🏢 Maharashtra Assembly Election ${yr}</h1>
          <div class="f" style="margin:12px 0">
            <button class="btn on">Results</button>
            <button class="btn" onclick="go('mhmap/${yr}')">🗺️ Map</button>
            <button class="btn" onclick="document.getElementById('mh19-seats-card').scrollIntoView({behavior:'smooth'})">All 288 Constituencies ↓</button>
          </div>
          ${stats([[288,'Total Seats'],[288,'Results Declared'],[(totElectors/1e7).toFixed(2)+' Cr','Total Electors'],[(totVotes/1e7).toFixed(2)+' Cr','Votes Polled'],[avgTurnout+'%','Turnout'],[psList.length,'Parties Winning']])}
          <div class="g g2" style="margin-top:14px">
            <div class="card">
              <h2>Seats Won by Party</h2>
              ${hemi(psList.map(p=>({c:p.c,seats:p.seats})),288)}
            </div>
            <div class="card">
              <h2>Party-wise Results</h2>
              ${tbl(['Party','Seats','Seats %'],psList.map(p=>`<tr class="r"><td>${dot2(p.c)}${shc(p.c,18)} ${esc(lc(p.c))}</td><td><b>${p.seats}</b></td><td>${(p.seats/288*100).toFixed(1)}%</td></tr>`))}
            </div>
          </div>
          <div class="card">
            <h2>Alliance Tally (${yr})</h2>
            <div style="margin:8px 0">NDA (BJP + Shiv Sena): <b>${ndaSeats}</b><br><span class="bar" style="width:${ndaSeats/288*100}%;background:#ff7a00"></span></div>
            <div style="margin:8px 0">UPA (NCP + Congress): <b>${upaSeats}</b><br><span class="bar" style="width:${upaSeats/288*100}%;background:#1d6fe8"></span></div>
            <div style="margin:8px 0">Others &amp; Independents: <b>${othSeats}</b><br><span class="bar" style="width:${othSeats/288*100}%;background:#8a8f98"></span></div>
            <p class="note">Majority mark: 145. Source: ECI ${yr} Detailed Results.</p>
          </div>
          <div class="card" id="mh19-seats-card" style="margin-top:16px">
            <h2>🏛️ All 288 Constituencies (${yr})</h2>
            <div class="f" style="margin-bottom:10px">
              <input id="mh19q" placeholder="Search constituency / candidate / party…" style="flex:1;min-width:200px" oninput="mh19Filter()">
              <select id="mh19p" onchange="mh19Filter()"><option value="">All winning parties</option>${psList.map(p=>`<option value="${p.c}">${esc(lc(p.c))} (${p.seats})</option>`)}</select>
              <select id="mh19cat" onchange="mh19Filter()"><option value="">All categories</option><option value="GEN">General</option><option value="SC">SC</option><option value="ST">ST</option></select>
            </div>
            <div id="mh19-table-wrap"></div>
          </div>
        `;
        window.mh19Filter=function(){
          const wrap=$('mh19-table-wrap');if(!wrap)return;
          const q=($('mh19q')?$('mh19q').value:'').toLowerCase().trim();
          const pf=$('mh19p')?$('mh19p').value:'';
          const catf=$('mh19cat')?$('mh19cat').value:'';
          const filtered=consts.filter(c=>{
            const mQ=!q||c.name.toLowerCase().includes(q)||(c.winner_name||'').toLowerCase().includes(q)||(c.winner_party||'').toLowerCase().includes(q)||String(c.ac_no)===q;
            const mP=!pf||c.winner_party===pf;
            const mC=!catf||c.category===catf;
            return mQ&&mP&&mC;
          });
          wrap.innerHTML=`<p class="note">${filtered.length} constituencies · tap any row to view candidate votes</p>`+tbl(
            ['AC No.','Constituency','Category','Winner Candidate','Party','Margin','Turnout %','Runner-up','Action'],
            filtered.map(c=>`<tr class="r" style="cursor:pointer" onclick="go('mhac/${yr}/${c.ac_no}')">
              <td>${c.ac_no}</td>
              <td><b><a onclick="go('mhac/${yr}/${c.ac_no}')">${esc(c.name)}</a></b></td>
              <td>${c.category}</td>
              <td><b>${esc(c.winner_name||'–')}</b></td>
              <td>${dot2(c.winner_party)}${shc(c.winner_party,16)} ${esc(lc(c.winner_party))}</td>
              <td>${c.margin?f(c.margin):'–'}</td>
              <td>${c.turnout_pct?c.turnout_pct.toFixed(1)+'%':'–'}</td>
              <td>${esc(c.runner_up_name||'–')}</td>
              <td><button class="btn" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();go('mhac/${yr}/${c.ac_no}')">Details →</button></td>
            </tr>`)
          );
          tr(wrap);
        };
        window.mh19Filter();
        tr(el);
      }).catch(err=>{el.innerHTML=`<p class="note">Could not load ${yr} data.</p>`;});
    },10);
    return'<p>Loading Maharashtra 2019 data…</p>';
  }
  initMH();const d=MH.ps.filter(p=>p.seats),al={Mahayuti:0,MVA:0,Others:0};d.forEach(p=>al[mal(p.c)]+=p.seats);
  return`${bc([['Home',''],['Maharashtra Assembly 2024']])}
  <div class="card" style="padding:10px 14px;margin-bottom:12px">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <span class="yr-label">📅 Select Year:</span>
      <button class="yr-btn on" onclick="go('mh')">2024</button>
      <button class="yr-btn" onclick="go('mh/2019')">2019</button>
      <button class="yr-btn" onclick="go('mh/2014')">2014</button>
      <button class="yr-btn" onclick="go('mh/2009')">2009</button>
      <button class="yr-btn" onclick="go('mh/2004')">2004</button>
    </div>
  </div>"""

new_mh_code = """'mh':()=>{
  initMH();const d=MH.ps.filter(p=>p.seats),al={Mahayuti:0,MVA:0,Others:0};d.forEach(p=>al[mal(p.c)]+=p.seats);
  return`${bc([['Home',''],['All Assemblies','assembly'],['Maharashtra Assembly 2024']])}"""

content = content.replace(old_mh_code, new_mh_code, 1)

# 6. In AP: Remove previous years section
old_ap_prev = """  const yrBar=AP_YEARS.map(yr=>`<button class="yr-btn${yr===2024?' on':''}" onclick="go('aph/${yr}')">${yr}</button>`).join('');
  return`${bc([['Home',''],['Andhra Pradesh']])}<h1>🏛️ Andhra Pradesh Assembly Elections</h1>
<div class="card" style="padding:14px">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px">
    <span class="yr-label">📅 Select Year:</span>${yrBar}
  </div>
  <p class="note" style="margin:4px 0 0">Viewing: <b>2024</b> · ${AP_YEAR_META[2024].note} · <a onclick="go('cmp')">Compare two years side by side →</a></p>
</div>
<div class="f" style="margin-top:12px">
  <button class="btn on">2024 Results</button>
  <button class="btn" onclick="go('apmap')">🗺️ Interactive Map</button>
  <button class="btn" onclick="go('aps')">All 175 Constituencies</button>
  <button class="btn" onclick="document.getElementById('ap-prev-years').scrollIntoView({behavior:'smooth'})">📅 Previous Years (1955–2019)</button>
</div>"""

new_ap_prev = """  return`${bc([['Home',''],['All Assemblies','assembly'],['Andhra Pradesh Assembly 2024']])}<h1>🏛️ Andhra Pradesh Assembly Election 2024</h1>
<div class="f" style="margin-top:12px">
  <button class="btn on">2024 Results</button>
  <button class="btn" onclick="go('apmap')">🗺️ Interactive Map</button>
  <button class="btn" onclick="go('aps')">All 175 Constituencies</button>
</div>"""

content = content.replace(old_ap_prev, new_ap_prev, 1)

# Also remove the #ap-prev-years block from AP page
ap_prev_years_idx = content.find("<!-- Previous Years section right inside Andhra Pradesh -->")
if ap_prev_years_idx != -1:
    ap_prev_years_end = content.find("</div>`\n},", ap_prev_years_idx)
    if ap_prev_years_end != -1:
        content = content[:ap_prev_years_idx] + "`\n}," + content[ap_prev_years_end + 7:]

# Write back
with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Pass 1 of patch_app_js.py completed successfully.")
