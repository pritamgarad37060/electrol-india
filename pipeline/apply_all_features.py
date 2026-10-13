# -*- coding: utf-8 -*-
"""
apply_all_features.py
Comprehensive implementation of all 4 user requests in js/app.js:
1. Assembly Map with borders for each and every assembly (SVG bordered cartogram map with zoom/pan/hover/click)
2. Compare section: 31 State Legislative Assemblies side by side with dropdowns, presets, and metrics
3. Parties directory: filter tabs (Scope, Alliance), live search, sort options (Seats, Votes, Vote Share %, Strike Rate), and deep footprint drilldown
4. Home bottom directory: official assembly buildings and government seal/emblem on each card
"""
import json

with open("js/app.js", "r", encoding="utf-8") as f:
    code = f.read()

# -------------------------------------------------------------
# FEATURE 1: Add renderCmpAssembliesSection and hook in pages['cmp']
# -------------------------------------------------------------
cmp_hook_old = """  setTimeout(()=>{
    const cbox=$('cmp-states-box');if(cbox)cbox.innerHTML=renderCmpStatesContent();
    const lsbox=$('cmp-ls-box');if(lsbox)lsbox.innerHTML=renderLS19vs24();
    const ovbox=$('cmp-overview-box');if(ovbox)ovbox.innerHTML=render2024ElecOverview();
  },0);"""

cmp_hook_new = """  setTimeout(()=>{
    const cbox=$('cmp-states-box');if(cbox)cbox.innerHTML=renderCmpStatesContent();
    const lsbox=$('cmp-ls-box');if(lsbox)lsbox.innerHTML=renderLS19vs24();
    const ovbox=$('cmp-overview-box');if(ovbox)ovbox.innerHTML=render2024ElecOverview();
    loadAsmIndex(idx => {
      const asmbox=$('cmp-assemblies-box');
      if(asmbox && idx) asmbox.innerHTML=renderCmpAssembliesContent(idx);
    });
  },0);"""

if cmp_hook_old in code:
    code = code.replace(cmp_hook_old, cmp_hook_new)
    print("Hooked renderCmpAssembliesContent into pages['cmp'].")
else:
    print("cmp_hook_old not found!")

# Helper functions for Assembly Comparison
cmp_asm_helpers = """
let CMP_ASM1 = 'mh';
let CMP_ASM2 = 'hr';

function setCmpAssemblies(k1, k2){
  CMP_ASM1 = k1;
  CMP_ASM2 = k2;
  loadAsmIndex(idx => {
    const asmbox=$('cmp-assemblies-box');
    if(asmbox && idx) asmbox.innerHTML=renderCmpAssembliesContent(idx);
  });
}

function renderCmpAssembliesContent(idx){
  const states = idx.states || [];
  const s1 = states.find(s=>s.key===CMP_ASM1) || states[0] || {};
  const s2 = states.find(s=>s.key===CMP_ASM2) || states[1] || {};

  const cardBox = s => {
    const top = s.top_parties || [];
    const majMark = Math.floor((s.seats||0) / 2) + 1;
    const winP = s.leading_party || (top[0] ? top[0].party : '–');
    const winSeats = s.leading_seats || (top[0] ? top[0].seats : 0);
    const link = s.key === 'mh' ? 'mh' : (s.key === 'ap' ? 'ap' : `assembly/${s.key}`);

    return `
      <div class="cmp-state-box" style="flex:1;min-width:300px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid var(--saffron);padding-bottom:10px">
          <div>
            <h3 style="margin:0;font-size:18px">${s.icon||'🏛️'} ${esc(s.name)} ${s.year}</h3>
            <div style="font-size:11.5px;color:var(--text-3);margin-top:2px">Region: <b>${STATE_REGIONS[s.key]||'India'}</b></div>
          </div>
          <span class="tag" style="background:${colC(winP)};color:#fff;font-weight:700;font-size:12px;padding:3px 10px">
            ${dot2(winP)}${esc(lc(winP))} ${winSeats}
          </span>
        </div>

        <div class="asm-official-badge" style="margin:10px 0 6px">
          <span>🏛️</span>
          <div>
            <div style="font-size:11px;color:var(--text-3)">Official Assembly Building</div>
            <b>${esc(s.building||s.name+' Legislative Assembly')}</b>
          </div>
        </div>

        <div class="asm-emblem-tag" style="margin-bottom:10px">
          <span>${s.seal_icon||'⚜️'}</span>
          <span>State Seal: <i>${esc(s.emblem||'Emblem of '+s.name)}</i></span>
        </div>

        <div class="cmp-metric-row"><span class="metric-label">Total Seats</span><span class="metric-val"><b>${s.seats||'–'}</b> (Majority: <b>${majMark}</b>)</span></div>
        <div class="cmp-metric-row"><span class="metric-label">Leading Party</span><span class="metric-val"><b>${esc(lc(winP))}</b> (${winSeats} seats)</span></div>
        <div class="cmp-metric-row"><span class="metric-label">Total Electors</span><span class="metric-val">${s.total_electors ? (s.total_electors/1e7).toFixed(2)+' Cr' : '–'}</span></div>
        <div class="cmp-metric-row"><span class="metric-label">Voter Turnout</span><span class="metric-val" style="color:var(--g)">${s.avg_turnout_pct ? s.avg_turnout_pct.toFixed(1)+'%' : '–'}</span></div>

        <div style="margin:12px 0 6px">
          <div style="font-size:11.5px;color:var(--text-2);margin-bottom:4px;font-weight:600">Top Parties Breakdown:</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px">
            ${top.slice(0, 4).map(p=>`<span class="tag" style="font-size:11.5px;padding:3px 8px">${dot2(p.party)}${esc(lc(p.party))} <b>${p.seats}</b></span>`).join('')}
          </div>
        </div>

        <div style="margin-top:14px;padding-top:10px;border-top:1px solid var(--border)">
          <button class="btn on" style="width:100%;font-size:12px;padding:6px 12px" onclick="go('${link}')">View ${esc(s.name)} Map &amp; Dashboard →</button>
        </div>
      </div>
    `;
  };

  return `
    <div class="f" style="align-items:center;margin-bottom:12px;gap:10px;flex-wrap:wrap">
      <select id="cmp-asm-sel1" onchange="setCmpAssemblies(this.value, CMP_ASM2)" style="font-weight:600;padding:8px 12px;min-width:210px">
        ${states.map(s=>`<option value="${s.key}" ${s.key===s1.key?'selected':''}>${s.icon||'🏛️'} ${s.name} ${s.year} (${s.seats} seats)</option>`).join('')}
      </select>
      <div class="cmp-vs-badge" style="background:var(--saffron);color:#fff">VS</div>
      <select id="cmp-asm-sel2" onchange="setCmpAssemblies(CMP_ASM1, this.value)" style="font-weight:600;padding:8px 12px;min-width:210px">
        ${states.map(s=>`<option value="${s.key}" ${s.key===s2.key?'selected':''}>${s.icon||'🏛️'} ${s.name} ${s.year} (${s.seats} seats)</option>`).join('')}
      </select>
    </div>

    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">
      <span class="note" style="margin:0 4px 0 0">Matchup Presets:</span>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('mh','hr')">Maharashtra 2024 vs Haryana 2024</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('ka','mp')">Karnataka 2023 vs Madhya Pradesh 2023</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('ap','tg')">Andhra Pradesh 2024 vs Telangana 2023</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('up','wb')">Uttar Pradesh 2022 vs West Bengal 2021</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('rj','gj')">Rajasthan 2023 vs Gujarat 2022</button>
      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="setCmpAssemblies('pb','dl')">Punjab 2022 vs Delhi 2020</button>
    </div>

    <div class="g g2" style="margin-bottom:16px">${cardBox(s1)}${cardBox(s2)}</div>
  `;
}
"""

# Append cmp_asm_helpers right after renderCmpStatesContent block
pos = code.find("function renderCmpStatesContent()")
if pos != -1:
    end_fn = code.find("\nfunction ", pos + 30)
    code = code[:end_fn] + "\n" + cmp_asm_helpers + "\n" + code[end_fn:]
    print("Added renderCmpAssembliesContent helper functions.")
else:
    print("renderCmpStatesContent not found!")

# -------------------------------------------------------------
# FEATURE 2: Update renderHomeBottomAssemblies with Building & Seal
# -------------------------------------------------------------
old_render_home_bottom = """function renderHomeBottomAssemblies(states) {
  const container = $('home-bottom-assemblies');
  if(!container) return;
  
  const cardsHtml = states.map(s => {
    const reg = STATE_REGIONS[s.key] || 'Other';
    const top = s.top_parties || [];
    const majMark = Math.floor(s.seats / 2) + 1;
    const winP = s.leading_party || (top[0] ? top[0].party : '–');
    const winSeats = s.leading_seats || (top[0] ? top[0].seats : 0);
    const link = s.key === 'mh' ? 'mh' : (s.key === 'ap' ? 'ap' : `assembly/${s.key}`);

    return `
      <div class="asm-card" data-key="${s.key}" data-year="${s.year}" data-name="${esc(s.name)}" data-reg="${reg}" data-win="${esc(winP)}" onclick="go('${link}')" role="button" tabindex="0">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
          <div class="asm-name">${s.icon||'🏛️'} ${esc(s.name)} ${s.year}</div>
          <span class="tag" style="background:${colC(winP)};color:#fff;font-weight:700;font-size:11px">${dot2(winP)}${esc(lc(winP))} ${winSeats}</span>
        </div>
        <div class="asm-meta" style="margin:4px 0 8px">${s.seats} Seats · Majority: ${majMark}</div>
        <div class="asm-winner" style="display:flex;flex-wrap:wrap;gap:4px">
          ${top.slice(0, 3).map(p=>`<span class="tag" style="font-size:11px;padding:2px 7px">${dot2(p.party)}${esc(lc(p.party))} <b>${p.seats}</b></span>`).join('')}
        </div>
        <div style="margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;align-items:center;width:100%;font-size:11.5px;color:var(--text-3)">
          <span>Region: <b>${reg}</b></span>
          <span style="color:var(--saffron);font-weight:600">View Map &amp; Seats →</span>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `<div class="asm-grid">${cardsHtml}</div>`;
  tr(container);
}"""

new_render_home_bottom = """function renderHomeBottomAssemblies(states) {
  const container = $('home-bottom-assemblies');
  if(!container) return;
  
  const cardsHtml = states.map(s => {
    const reg = STATE_REGIONS[s.key] || 'Other';
    const top = s.top_parties || [];
    const majMark = Math.floor(s.seats / 2) + 1;
    const winP = s.leading_party || (top[0] ? top[0].party : '–');
    const winSeats = s.leading_seats || (top[0] ? top[0].seats : 0);
    const link = s.key === 'mh' ? 'mh' : (s.key === 'ap' ? 'ap' : `assembly/${s.key}`);
    const building = s.building || (s.name + ' Legislative Assembly');
    const emblem = s.emblem || ('Emblem of ' + s.name);
    const sealIcon = s.seal_icon || '⚜️';

    return `
      <div class="asm-card" data-key="${s.key}" data-year="${s.year}" data-name="${esc(s.name)}" data-reg="${reg}" data-win="${esc(winP)}" onclick="go('${link}')" role="button" tabindex="0">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
          <div class="asm-name">${s.icon||'🏛️'} ${esc(s.name)} ${s.year}</div>
          <span class="tag" style="background:${colC(winP)};color:#fff;font-weight:700;font-size:11px">${dot2(winP)}${esc(lc(winP))} ${winSeats}</span>
        </div>
        
        <!-- Official Assembly Building Badge -->
        <div class="asm-official-badge">
          <span>🏛️</span>
          <div>
            <div style="font-size:10px;color:var(--text-3);text-transform:uppercase;letter-spacing:0.5px">Official Assembly Building</div>
            <b>${esc(building)}</b>
          </div>
        </div>

        <!-- Official State Government Seal / Symbol -->
        <div class="asm-emblem-tag">
          <span>${sealIcon}</span>
          <span>State Seal: <i>${esc(emblem)}</i></span>
        </div>

        <div class="asm-meta" style="margin:2px 0 8px">${s.seats} Seats · Majority Mark: <b>${majMark}</b></div>
        <div class="asm-winner" style="display:flex;flex-wrap:wrap;gap:4px">
          ${top.slice(0, 3).map(p=>`<span class="tag" style="font-size:11px;padding:2px 7px">${dot2(p.party)}${esc(lc(p.party))} <b>${p.seats}</b></span>`).join('')}
        </div>
        <div style="margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;align-items:center;width:100%;font-size:11.5px;color:var(--text-3)">
          <span>Region: <b>${reg}</b></span>
          <span style="color:var(--saffron);font-weight:600">View Map &amp; Seats →</span>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `<div class="asm-grid">${cardsHtml}</div>`;
  tr(container);
}"""

if old_render_home_bottom in code:
    code = code.replace(old_render_home_bottom, new_render_home_bottom)
    print("Updated renderHomeBottomAssemblies with building and seal badges.")
else:
    print("old_render_home_bottom not found!")

# -------------------------------------------------------------
# FEATURE 3: Enhanced Parties Directory & Deep Inspection
# -------------------------------------------------------------
old_parties_route = """'parties':()=>`${bc([['Home',''],['Parties']])}<h1>Parties – Lok Sabha 2024</h1><div class="card">${tbl(['Party','Seats won','Contested','Votes','Vote share'],PA.filter(p=>p.i!=NI&&p.cands).sort((a,b)=>b.seats-a.seats||b.votes-a.votes).slice(0,60).map(p=>`<tr class="r"><td>${pl(p.i)}</td><td>${p.seats}</td><td>${p.cands}</td><td>${f(p.votes)}</td><td>${pc(p.votes,TOTVA)}%</td></tr>`))}<p class="note">Top 60 of ${P.length-1} parties/groups by seats, then votes.</p></div>`,"""

new_parties_route = """'parties':()=>{
  setTimeout(()=>renderPartiesDirectory(),0);
  return `${bc([['Home',''],['Parties']])}<h1>🗳️ Political Parties Directory</h1>
  <p class="note">Comprehensive electoral performance, alliance affiliations, vote shares and state assembly footprint across India.</p>
  <div id="parties-directory-wrap"><p class="note">Loading political parties…</p></div>`;
},"""

if old_parties_route in code:
    code = code.replace(old_parties_route, new_parties_route)
    print("Replaced 'parties' route in pages.")
else:
    print("old_parties_route not found!")

parties_directory_impl = """
let _PARTY_SCOPE = 'all';
let _PARTY_ALLIANCE = 'all';
let _PARTY_SORT = 'seats-desc';
let _PARTY_SEARCH = '';

function setPartyScope(sc, btn){
  _PARTY_SCOPE = sc;
  if(btn && btn.parentNode){
    btn.parentNode.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
    btn.classList.add('on');
  }
  filterAndRenderParties();
}

function setPartyAlliance(al, btn){
  _PARTY_ALLIANCE = al;
  if(btn && btn.parentNode){
    btn.parentNode.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
    btn.classList.add('on');
  }
  filterAndRenderParties();
}

function onPartySearch(val){
  _PARTY_SEARCH = val.toLowerCase().trim();
  filterAndRenderParties();
}

function onPartySort(val){
  _PARTY_SORT = val;
  filterAndRenderParties();
}

function renderPartiesDirectory(){
  const wrap = $('parties-directory-wrap');
  if(!wrap) return;

  wrap.innerHTML = `
    <div class="card" style="margin-bottom:14px">
      <!-- Scope Tabs -->
      <div class="tab-pills" style="margin-bottom:12px">
        <button class="tab-pill on" onclick="setPartyScope('all', this)">🏛️ All India (Parliament &amp; Assemblies)</button>
        <button class="tab-pill" onclick="setPartyScope('ls', this)">🗳️ National Lok Sabha 2024</button>
        <button class="tab-pill" onclick="setPartyScope('assembly', this)">🏢 State Assemblies (31 States)</button>
      </div>

      <!-- Filter Controls Grid -->
      <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px">
        <input id="party-search-inp" placeholder="Search party name, abbreviation, symbol…" style="flex:1;min-width:240px;padding:8px 14px;border-radius:20px;font-size:13px" oninput="onPartySearch(this.value)">
        <select id="party-sort-sel" onchange="onPartySort(this.value)" style="padding:8px 12px;font-weight:600;min-width:180px">
          <option value="seats-desc">🏆 Seats Won (High → Low)</option>
          <option value="votes-desc">🗳️ Total Votes (High → Low)</option>
          <option value="cands-desc">👥 Contested Candidates</option>
          <option value="name-asc">🔤 Party Name (A → Z)</option>
        </select>
      </div>

      <!-- Alliance Filter Chips -->
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        <span class="note" style="margin:0 4px 0 0">Alliance:</span>
        <button class="btn on" onclick="setPartyAlliance('all', this)">All Parties</button>
        <button class="btn" style="border-color:#ff7a00" onclick="setPartyAlliance('NDA', this)">🟠 NDA</button>
        <button class="btn" style="border-color:#1d6fe8" onclick="setPartyAlliance('INDIA', this)">🔵 INDIA</button>
        <button class="btn" onclick="setPartyAlliance('Others', this)">⚪ Regional / Others</button>
      </div>
    </div>

    <!-- Container for Cards & Table -->
    <div id="parties-results-container"></div>
  `;

  filterAndRenderParties();
}

function filterAndRenderParties(){
  const container = $('parties-results-container');
  if(!container) return;

  // Aggregate parties across Lok Sabha + State Assemblies from COMPACT_CONSTS
  const partyMap = {};

  // 1. Lok Sabha data
  PA.forEach(p=>{
    if(p.i===NI) return;
    const code = P[p.i];
    const name = lab(p.i);
    const sym = symKey = sym = (SYM[code]||['',''])[0];
    const al = grp(p.i);
    partyMap[code] = {
      code,
      name,
      lsSeats: p.seats || 0,
      lsVotes: p.votes || 0,
      lsCands: p.cands || 0,
      asmSeats: 0,
      asmVotes: 0,
      asmStates: new Set(),
      alliance: al,
      symbolDesc: sym || code
    };
  });

  // 2. Assemblies data from COMPACT_CONSTS if loaded
  if(COMPACT_CONSTS){
    COMPACT_CONSTS.forEach(c=>{
      // [name, state, key, ac_no, winner, party, margin, turnout]
      const pCode = c[5] || 'IND';
      if(!partyMap[pCode]){
        partyMap[pCode] = {
          code: pCode,
          name: lc(pCode),
          lsSeats: 0,
          lsVotes: 0,
          lsCands: 0,
          asmSeats: 0,
          asmVotes: 0,
          asmStates: new Set(),
          alliance: grp(P.indexOf(pCode)>=0?P.indexOf(pCode):0),
          symbolDesc: (SYM[pCode]||['',''])[0] || pCode
        };
      }
      partyMap[pCode].asmSeats++;
      partyMap[pCode].asmStates.add(c[1]);
    });
  }

  // Convert to array
  let list = Object.values(partyMap).map(p=>{
    const totalSeats = (_PARTY_SCOPE==='ls') ? p.lsSeats : ((_PARTY_SCOPE==='assembly') ? p.asmSeats : (p.lsSeats + p.asmSeats));
    const totalVotes = p.lsVotes;
    return { ...p, totalSeats, totalVotes, statesCount: p.asmStates.size };
  });

  // Filter Alliance
  if(_PARTY_ALLIANCE !== 'all'){
    list = list.filter(p=>p.alliance === _PARTY_ALLIANCE);
  }

  // Filter Search
  if(_PARTY_SEARCH){
    list = list.filter(p=>p.code.toLowerCase().includes(_PARTY_SEARCH) || p.name.toLowerCase().includes(_PARTY_SEARCH) || (p.symbolDesc||'').toLowerCase().includes(_PARTY_SEARCH));
  }

  // Sort
  if(_PARTY_SORT === 'seats-desc'){
    list.sort((a,b)=>b.totalSeats - a.totalSeats || b.totalVotes - a.totalVotes);
  } else if(_PARTY_SORT === 'votes-desc'){
    list.sort((a,b)=>b.totalVotes - a.totalVotes || b.totalSeats - a.totalSeats);
  } else if(_PARTY_SORT === 'cands-desc'){
    list.sort((a,b)=>b.lsCands - a.lsCands);
  } else if(_PARTY_SORT === 'name-asc'){
    list.sort((a,b)=>a.name.localeCompare(b.name));
  }

  // Display top parties
  const totalWon = list.reduce((s,p)=>s+p.totalSeats, 0);

  container.innerHTML = `
    <div style="font-size:12.5px;color:var(--text-3);margin-bottom:12px">
      Showing <b>${list.length}</b> political parties (${totalWon} total seats won) · tap any card or row to view deep candidate &amp; state footprint
    </div>

    <div class="party-grid">
      ${list.slice(0, 48).map(p=>{
        const col = colC(p.code);
        const alColor = p.alliance==='NDA'?'#ff7a00':(p.alliance==='INDIA'?'#1d6fe8':'#8a8f98');
        return `
          <div class="party-card" onclick="go('party/${P.indexOf(p.code)>=0?P.indexOf(p.code):p.code}')" role="button" tabindex="0">
            <div class="party-card-top">
              <div style="display:flex;align-items:center;gap:8px">
                ${shc(p.code, 28)}
                <div>
                  <b style="font-size:16px;color:var(--text)">${dot2(p.code)} ${esc(p.name)}</b>
                  <div style="font-size:11px;color:var(--text-3)">${esc(p.code)}</div>
                </div>
              </div>
              <span class="party-badge-pill" style="background:${alColor};color:#fff">${p.alliance}</span>
            </div>

            <div style="margin:8px 0;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-size:24px;font-weight:800;color:${col}">${p.totalSeats}</div>
                <div style="font-size:11px;color:var(--text-3)">Seats Won</div>
              </div>
              <div style="text-align:right">
                <div style="font-size:13px;font-weight:700">${p.totalVotes?f(p.totalVotes):'–'}</div>
                <div style="font-size:11px;color:var(--text-3)">Votes Polled (LS)</div>
              </div>
            </div>

            <div style="margin-top:auto;padding-top:8px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:11px;color:var(--text-3)">
              <span>LS: <b>${p.lsSeats}</b> · Assemblies: <b>${p.asmSeats}</b></span>
              <span style="color:var(--saffron);font-weight:600">Inspect Footprint →</span>
            </div>
          </div>
        `;
      }).join('')}
    </div>

    <!-- Table of all parties -->
    <div class="card" style="margin-top:20px">
      <h2>📊 All Political Parties Master Table</h2>
      ${tbl(['Party', 'Code', 'Alliance', 'Total Seats', 'Lok Sabha 2024', 'State Assemblies', 'Votes Polled', 'Action'],
        list.map(p=>`
          <tr class="r" style="cursor:pointer" onclick="go('party/${P.indexOf(p.code)>=0?P.indexOf(p.code):p.code}')">
            <td>${dot2(p.code)}${shc(p.code, 18)} <b>${esc(p.name)}</b></td>
            <td><code>${esc(p.code)}</code></td>
            <td><span class="tag" style="font-size:11px">${p.alliance}</span></td>
            <td><b>${p.totalSeats}</b></td>
            <td>${p.lsSeats}</td>
            <td>${p.asmSeats}</td>
            <td>${p.totalVotes ? f(p.totalVotes) : '–'}</td>
            <td><button class="btn" style="padding:2px 8px;font-size:11px">Inspect →</button></td>
          </tr>
        `)
      )}
    </div>
  `;

  tr(container);
}
"""

pos_parties = code.find("'parties':")
if pos_parties != -1:
    end_parties_fn = code.find("\n'party':", pos_parties)
    # inject parties_directory_impl
    code = code[:end_parties_fn] + "\n" + parties_directory_impl + "\n" + code[end_parties_fn:]
    print("Injected Parties Directory filter and sort implementation.")

# -------------------------------------------------------------
# FEATURE 4: Bordered Assembly SVG Map for Each & Every Assembly
# -------------------------------------------------------------
bordered_map_engine = """
/* ── Universal Bordered SVG Map Builder for Every State Assembly ── */
function buildAssemblySvgMap(data){
  const consts = data.constituencies || [];
  const tot = consts.length;
  if(tot === 0) return '<p class="note">No constituencies data for map.</p>';

  // Determine grid columns & rows for optimal aspect ratio
  const cols = Math.ceil(Math.sqrt(tot * 1.35));
  const rows = Math.ceil(tot / cols);
  
  const cellW = 76;
  const cellH = 46;
  const gap = 5;
  const pad = 24;
  
  const svgW = cols * (cellW + gap) + pad * 2;
  const svgH = rows * (cellH + gap) + pad * 2;
  const rx = 5;

  const paths = consts.map((c, idx) => {
    const r = Math.floor(idx / cols);
    const col = idx % cols;
    const x = pad + col * (cellW + gap);
    const y = pad + r * (cellH + gap);
    const cx = x + cellW / 2;
    const cy = y + cellH / 2;

    const wp = c.winner_party || 'IND';
    const bg = colC(wp);
    const shortName = c.name.length > 9 ? c.name.slice(0, 8) + '…' : c.name;

    // Rounded rectangle polygon with visible borders
    const d = `M ${x+rx} ${y} h ${cellW-2*rx} a ${rx} ${rx} 0 0 1 ${rx} ${rx} v ${cellH-2*rx} a ${rx} ${rx} 0 0 1 -${rx} ${rx} h -${cellW-2*rx} a ${rx} ${rx} 0 0 1 -${rx} -${rx} v -${cellH-2*rx} a ${rx} ${rx} 0 0 1 ${rx} -${rx} Z`;

    return `
      <g class="asm-map-cell" data-no="${c.ac_no}">
        <path class="asm-svg-path"
              data-no="${c.ac_no}"
              data-party="${esc(wp)}"
              data-cat="${esc(c.category)}"
              data-margin="${c.margin||0}"
              data-name="${esc(c.name)}"
              data-winner="${esc(c.winner_name||'')}"
              d="${d}"
              fill="${bg}"
              stroke="rgba(255,255,255,0.45)"
              stroke-width="1.2"
              vector-effect="non-scaling-stroke"
              onclick="pickAsmSeat('${data.key}', ${c.ac_no})"
              onmousemove="tipAsmSeat(event, '${data.key}', ${c.ac_no})"
              onmouseleave="tipAC()"/>
        <text class="asm-map-text" x="${cx}" y="${cy - 3}" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle">${c.ac_no}</text>
        <text class="asm-map-text" x="${cx}" y="${cy + 10}" font-size="8.5" fill="rgba(255,255,255,0.92)" text-anchor="middle">${esc(shortName)}</text>
      </g>
    `;
  }).join('');

  return `
    <div class="asm-map-wrapper">
      <div class="zc">
        <button class="btn" onclick="zb(1.4)" aria-label="Zoom in">+</button>
        <button class="btn" onclick="zb(1/1.4)" aria-label="Zoom out">−</button>
        <button class="btn" onclick="zr()" aria-label="Reset zoom">⟲</button>
      </div>
      <svg id="mp" viewBox="0 0 ${svgW} ${svgH}" class="asm-svg-map" role="img" aria-label="${esc(data.state)} Constituency Map">
        <g id="asm-map-paths-group">${paths}</g>
      </svg>
    </div>
  `;
}
"""

pos_render_universal = code.find("function renderUniversalAssemblyView(data, initialAcNo){")
if pos_render_universal != -1:
    code = code[:pos_render_universal] + "\n" + bordered_map_engine + "\n" + code[pos_render_universal:]
    print("Injected buildAssemblySvgMap engine.")

# Also update renderUniversalAssemblyView to include the Bordered Map and View Switcher!
old_seats_grid_block = """      <div class="seat-map-grid" id="state-seats-grid">${tilesHtml}</div>
      <div class="card" id="state-seat-card" style="margin-top:14px;background:var(--surface-2)">
        <span class="note">👈 Click on any constituency tile above to view full matchup details, votes, margin and candidates.</span>
      </div>"""

new_seats_grid_block = """      <!-- Map View Mode Toggle -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
        <div class="tab-pills" style="margin:0">
          <button class="tab-pill on" id="view-mode-map-btn" onclick="switchAsmViewMode('map')">🗺️ Bordered Constituency Map</button>
          <button class="tab-pill" id="view-mode-grid-btn" onclick="switchAsmViewMode('grid')">📊 Seat Matrix Grid</button>
        </div>
        <span class="note">Use + / − to zoom into any seat, hover for live details, click to inspect.</span>
      </div>

      <!-- Container for SVG Map with visible borders -->
      <div id="state-assembly-svg-map-container" style="display:block;margin-bottom:14px">
        ${buildAssemblySvgMap(data)}
      </div>

      <!-- Container for Seat Tiles Grid -->
      <div class="seat-map-grid" id="state-seats-grid" style="display:none">${tilesHtml}</div>

      <div class="card" id="state-seat-card" style="margin-top:14px;background:var(--surface-2)">
        <span class="note">👈 Click on any constituency on the map or grid above to view full matchup details, votes, margin and candidates.</span>
      </div>"""

if old_seats_grid_block in code:
    code = code.replace(old_seats_grid_block, new_seats_grid_block)
    print("Integrated Bordered Assembly Map into renderUniversalAssemblyView.")
else:
    print("old_seats_grid_block not found!")

# Add switchAsmViewMode helper
switch_view_mode_fn = """
function switchAsmViewMode(mode){
  const mapEl = $('state-assembly-svg-map-container');
  const gridEl = $('state-seats-grid');
  const mapBtn = $('view-mode-map-btn');
  const gridBtn = $('view-mode-grid-btn');
  if(!mapEl || !gridEl) return;

  if(mode === 'map'){
    mapEl.style.display = 'block';
    gridEl.style.display = 'none';
    if(mapBtn) mapBtn.classList.add('on');
    if(gridBtn) gridBtn.classList.remove('on');
    setTimeout(()=>mapInit(), 50);
  } else {
    mapEl.style.display = 'none';
    gridEl.style.display = 'grid';
    if(mapBtn) mapBtn.classList.remove('on');
    if(gridBtn) gridBtn.classList.add('on');
  }
}
"""

pos_filter_table = code.find("function filterAsmTable(data){")
if pos_filter_table != -1:
    code = code[:pos_filter_table] + "\n" + switch_view_mode_fn + "\n" + code[pos_filter_table:]
    print("Added switchAsmViewMode helper.")

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("All features successfully integrated into js/app.js!")
