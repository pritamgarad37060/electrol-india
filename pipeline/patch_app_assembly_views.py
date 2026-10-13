# -*- coding: utf-8 -*-
"""
patch_app_assembly_views.py - Adds the universal 31-State Assembly Hub,
interactive cartogram seat maps, candidate drilldown views, and cleans up historical AP/MH handlers.
"""

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update pages['assembly']
old_assembly_route = content[content.find("'assembly':") : content.find("'ls':(yr)=>")]

new_assembly_route = """'assembly':(stateKey, acNo)=>{
  // Sub-route: If a specific state assembly is requested
  if(stateKey){
    stateKey = stateKey.toLowerCase();
    if(stateKey === 'mh') return pages['mh']();
    if(stateKey === 'ap') return pages['ap']();

    setTimeout(()=>{
      const el = $('app'); if(!el) return;
      el.innerHTML = '<p>Loading state assembly data…</p>';
      loadStateAsm(stateKey, data => {
        if(!data){
          el.innerHTML = `${bc([['Home',''],['All Assemblies','assembly'],['Error']])}<div class="card"><p class="note">Data for ${esc(stateKey)} could not be loaded.</p><button class="btn on" onclick="go('assembly')">← Back to All State Assemblies</button></div>`;
          return;
        }
        window._curAsmState = data;
        renderUniversalAssemblyView(data, acNo);
      });
    }, 10);
    return `${bc([['Home',''],['All Assemblies','assembly'],[esc(stateKey.toUpperCase())]])}<p>Loading assembly election data…</p>`;
  }

  // Master Hub: All 31 States / UTs
  setTimeout(()=>{
    const el = $('app'); if(!el) return;
    loadAsmIndex(idx => {
      const states = idx.states || [];
      renderAssemblyHub(states);
    });
  }, 10);
  return `${bc([['Home',''],['All State Assemblies']])}<p>Loading all 31 state assemblies…</p>`;
},
"""

content = content.replace(old_assembly_route, new_assembly_route, 1)

# 2. Add the helper rendering functions for Assembly Hub and Universal Assembly View
# We place these right before `function updateNavTabs()`
nav_tabs_pos = content.find("function updateNavTabs()")

extra_asm_functions = """
/* ═══════════════════════════════════════════════════════════════════════
   UNIVERSAL 31-STATE ASSEMBLY HUB & INTERACTIVE SEAT MAP ENGINE
   ═══════════════════════════════════════════════════════════════════════ */
let _ASM_HUB_REGION = 'all';
let _ASM_FILTER_PARTY = '';
let _ASM_FILTER_CAT = '';
let _ASM_FILTER_MG = '';

function setAsmHubRegion(reg){
  _ASM_HUB_REGION = reg;
  document.querySelectorAll('.tab-pill[data-reg]').forEach(b=>{
    b.classList.toggle('on', b.dataset.reg === reg);
  });
  filterAsmHub();
}

function filterAsmHub(){
  const q = ($('asm-hub-search') ? $('asm-hub-search').value : '').toLowerCase().trim();
  document.querySelectorAll('#asm-hub-grid .asm-card').forEach(card=>{
    const name = (card.dataset.name||'').toLowerCase();
    const reg = card.dataset.reg||'';
    const win = (card.dataset.win||'').toLowerCase();
    const matchReg = _ASM_HUB_REGION === 'all' || reg === _ASM_HUB_REGION;
    const matchQ = !q || name.includes(q) || win.includes(q);
    card.style.display = (matchReg && matchQ) ? 'flex' : 'none';
  });
}

function renderAssemblyHub(states){
  const el = $('app'); if(!el) return;
  const totConsts = states.reduce((s,x)=>s+(x.seats||0),0);

  const cardsHtml = states.map(s => {
    const reg = STATE_REGIONS[s.key] || 'Other';
    const top = s.top_parties || [];
    const majMark = Math.floor(s.seats / 2) + 1;
    const winP = s.leading_party || (top[0] ? top[0].party : '–');
    const winSeats = s.leading_seats || (top[0] ? top[0].seats : 0);
    const isMaj = winSeats >= majMark;
    const link = s.key === 'mh' ? 'mh' : (s.key === 'ap' ? 'ap' : `assembly/${s.key}`);

    return `
      <div class="asm-card" data-key="${s.key}" data-name="${esc(s.name)}" data-reg="${reg}" data-win="${esc(winP)}" onclick="go('${link}')" role="button" tabindex="0" onkeydown="if(event.key==='Enter')this.click()">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
          <div class="asm-name">${s.icon||'🏛️'} ${esc(s.name)} ${s.year}</div>
          <span class="tag" style="background:${colC(winP)};color:#fff;font-weight:700;font-size:11px">${dot2(winP)}${esc(lc(winP))} ${winSeats}</span>
        </div>
        <div class="asm-meta" style="margin:4px 0 8px">${s.seats} Seats · Majority: ${majMark} ${isMaj ? '· <span style="color:#0a7d3b;font-weight:600">Majority</span>' : '· <span style="color:#e67e22;font-weight:600">Plurality</span>'}</div>
        <div class="asm-winner" style="display:flex;flex-wrap:wrap;gap:4px">
          ${top.slice(0, 4).map(p=>`<span class="tag" style="font-size:11px;padding:2px 7px">${dot2(p.party)}${esc(lc(p.party))} <b>${p.seats}</b></span>`).join('')}
        </div>
        <div style="margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;align-items:center;width:100%;font-size:11.5px;color:var(--text-3)">
          <span>Region: <b>${reg}</b></span>
          <span style="color:var(--saffron);font-weight:600">Explore Seat Map →</span>
        </div>
      </div>
    `;
  }).join('');

  el.innerHTML = `
    ${bc([['Home',''],['All State Assemblies']])}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:8px">
      <div>
        <h1 style="margin:0 0 4px">🏘️ State Legislative Assembly Elections</h1>
        <div class="sub" style="margin:0;font-size:13px;color:var(--text-2)">Official ECI Election Results · All 31 States &amp; Union Territories · ${f(totConsts)} Constituencies</div>
      </div>
    </div>

    <!-- Region Filters & Search -->
    <div class="card" style="padding:14px;margin:14px 0">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px">
        <div class="tab-pills" style="margin:0">
          <button class="tab-pill on" data-reg="all" onclick="setAsmHubRegion('all')">All (31)</button>
          <button class="tab-pill" data-reg="North" onclick="setAsmHubRegion('North')">North (7)</button>
          <button class="tab-pill" data-reg="South" onclick="setAsmHubRegion('South')">South (5)</button>
          <button class="tab-pill" data-reg="West" onclick="setAsmHubRegion('West')">West (3)</button>
          <button class="tab-pill" data-reg="East" onclick="setAsmHubRegion('East')">East (4)</button>
          <button class="tab-pill" data-reg="Central" onclick="setAsmHubRegion('Central')">Central (2)</button>
          <button class="tab-pill" data-reg="North-East" onclick="setAsmHubRegion('North-East')">North-East (8)</button>
          <button class="tab-pill" data-reg="UT" onclick="setAsmHubRegion('UT')">UTs (3)</button>
        </div>
        <input id="asm-hub-search" placeholder="Search state name or winning party…" style="min-width:240px;padding:8px 14px;border-radius:20px;font-size:13px" oninput="filterAsmHub()">
      </div>
      <div style="font-size:12px;color:var(--text-3);display:flex;gap:14px;flex-wrap:wrap">
        <span>⚡ Latest held election for each state</span>
        <span>🗺️ Interactive constituency seat maps</span>
        <span>👥 Full candidate vote counts</span>
      </div>
    </div>

    <div class="asm-grid" id="asm-hub-grid" style="margin-top:16px">${cardsHtml}</div>
    ${footer()}
  `;
  tr(el);
}

function tipAsmSeat(e, key, no){
  const t = $('tp-ac'); if(!t) return;
  const d = ASM_CACHE[key]; if(!d) return;
  const c = (d.constituencies||[]).find(x => x.ac_no === +no); if(!c) return;
  t.style.display = 'block';
  t.style.left = Math.min(window.innerWidth - 220, e.clientX + 12) + 'px';
  t.style.top = (e.clientY + 14) + 'px';
  t.innerHTML = `<b>AC ${c.ac_no}. ${esc(c.name)}</b><br>Winner: <b>${esc(c.winner_name||'–')}</b> (${esc(lc(c.winner_party||'–'))})<br>Margin: <b>${f(c.margin||0)}</b> · Turnout: ${c.turnout_pct ? c.turnout_pct.toFixed(1)+'%' : '–'}`;
}

function pickAsmSeat(key, no){
  const d = ASM_CACHE[key]; if(!d) return;
  const c = (d.constituencies||[]).find(x => x.ac_no === +no); if(!c) return;
  const card = $('state-seat-card'); if(!card) return;
  const wp = c.winner_party || 'IND';
  const rp = c.runner_up_party || '';
  const tv = c.votes_polled || ((c.winner_votes||0) + (c.runner_up_votes||0));
  
  card.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
      <div>
        <h3 style="margin:0;color:var(--g)">AC ${c.ac_no}. ${esc(c.name)}</h3>
        <span class="note">${c.category} Category · Turnout: <b>${c.turnout_pct ? c.turnout_pct.toFixed(1)+'%' : '–'}</b> (${f(c.votes_polled||0)} polled / ${f(c.electors||0)} electors)</span>
      </div>
      <button class="btn on" onclick="showAsmCandBreakdown('${key}', ${c.ac_no})">Full Candidate Breakdown ↓</button>
    </div>
    <div class="g g2" style="margin-top:10px">
      <div class="pb win">
        <div class="av" style="font-size:22px">${shc(wp,44)||av(c.winner_name||'')}</div>
        <div>
          <small>Winner</small><br>
          <b style="font-size:16px">${esc(c.winner_name||'–')}</b><br>
          ${dot2(wp)}${shc(wp,16)} ${esc(lc(wp))}<br>
          <b>${f(c.winner_votes||0)} votes (${pc(c.winner_votes||0, tv)}%)</b>
        </div>
      </div>
      <div class="pb run">
        <div class="av" style="font-size:22px">${shc(rp,44)||av(c.runner_up_name||'')}</div>
        <div>
          <small>Runner-up</small><br>
          <b style="font-size:16px">${esc(c.runner_up_name||'–')}</b><br>
          ${rp ? dot2(rp)+' '+shc(rp,16)+' '+esc(lc(rp)) : '–'}<br>
          <b>${c.runner_up_votes ? f(c.runner_up_votes)+' votes ('+pc(c.runner_up_votes, tv)+'%)' : '–'}</b>
        </div>
      </div>
    </div>
    <div style="margin-top:10px;font-size:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
      <span>Victory Margin: <b style="color:#0a7d3b">${f(c.margin||0)}</b> votes · NOTA: <b>${f(c.nota_votes||0)}</b></span>
      <a onclick="showAsmCandBreakdown('${key}', ${c.ac_no})" style="cursor:pointer;font-weight:600">Inspect all ${c.num_candidates||(c.candidates?c.candidates.length:0)} candidates →</a>
    </div>
  `;
  card.scrollIntoView && card.scrollIntoView({block:'nearest',behavior:'smooth'});
}

function filterAsmParty(p){
  _ASM_FILTER_PARTY = p;
  document.querySelectorAll('.map-legend-item[data-p]').forEach(el => el.classList.toggle('active', el.dataset.p === p));
  applyAsmSeatFilters();
}
function filterAsmCat(cat){
  _ASM_FILTER_CAT = cat;
  applyAsmSeatFilters();
}
function filterAsmMargin(mg){
  _ASM_FILTER_MG = mg;
  applyAsmSeatFilters();
}
function filterAsmSearch(q){
  applyAsmSeatFilters(q);
}
function applyAsmSeatFilters(searchQ){
  const q = (searchQ !== undefined ? searchQ : ($('asm-search-seat') ? $('asm-search-seat').value : '')).toLowerCase().trim();
  document.querySelectorAll('#state-seats-grid .seat-tile').forEach(el => {
    const p = el.dataset.party;
    const cat = el.dataset.cat;
    const mg = +el.dataset.margin;
    const n = (el.dataset.name||'').toLowerCase();
    const w = (el.dataset.winner||'').toLowerCase();
    const no = el.dataset.no;
    
    let matchP = !_ASM_FILTER_PARTY || p === _ASM_FILTER_PARTY;
    let matchCat = !_ASM_FILTER_CAT || cat === _ASM_FILTER_CAT;
    let matchMg = true;
    if(_ASM_FILTER_MG === 'close5k') matchMg = mg < 5000;
    else if(_ASM_FILTER_MG === 'close25k') matchMg = mg < 25000;
    else if(_ASM_FILTER_MG === 'landslide') matchMg = mg >= 50000;
    
    let matchQ = !q || n.includes(q) || w.includes(q) || no === q;
    el.classList.toggle('dim', !(matchP && matchCat && matchMg && matchQ));
  });
}

function filterAsmTable(data){
  const wrap = $('state-table-wrap'); if(!wrap) return;
  const q = ($('asmtab-q') ? $('asmtab-q').value : '').toLowerCase().trim();
  const pf = $('asmtab-p') ? $('asmtab-p').value : '';
  const catf = $('asmtab-cat') ? $('asmtab-cat').value : '';
  const consts = data.constituencies || [];
  
  const filtered = consts.filter(c => {
    const matchQ = !q || c.name.toLowerCase().includes(q) || (c.winner_name||'').toLowerCase().includes(q) || (c.runner_up_name||'').toLowerCase().includes(q) || String(c.ac_no) === q;
    const matchP = !pf || c.winner_party === pf;
    const matchCat = !catf || c.category === catf;
    return matchQ && matchP && matchCat;
  });

  wrap.innerHTML = `<p class="note">${filtered.length} constituencies · tap any row or button to view candidate breakdown</p>` + tbl(
    ['AC No.', 'Constituency', 'Category', 'Winner Candidate', 'Party', 'Margin', 'Turnout %', 'Runner-up Candidate', 'Action'],
    filtered.map(c => `
      <tr class="r" style="cursor:pointer" onclick="showAsmCandBreakdown('${data.key}', ${c.ac_no})">
        <td>${c.ac_no}</td>
        <td><b><a onclick="event.stopPropagation();showAsmCandBreakdown('${data.key}', ${c.ac_no})">${esc(c.name)}</a></b></td>
        <td>${c.category}</td>
        <td><b>${esc(c.winner_name||'–')}</b></td>
        <td>${dot2(c.winner_party)}${shc(c.winner_party,16)} ${esc(lc(c.winner_party))}</td>
        <td><b>${f(c.margin||0)}</b></td>
        <td>${c.turnout_pct ? c.turnout_pct.toFixed(1)+'%' : '–'}</td>
        <td>${esc(c.runner_up_name||'–')} (${c.runner_up_party ? esc(lc(c.runner_up_party)) : '–'})</td>
        <td><button class="btn" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();showAsmCandBreakdown('${data.key}', ${c.ac_no})">Candidates →</button></td>
      </tr>
    `)
  );
  tr(wrap);
}

function showAsmCandBreakdown(key, acNo){
  const d = ASM_CACHE[key]; if(!d) return;
  const c = (d.constituencies||[]).find(x => x.ac_no === +acNo); if(!c) return;
  const wrap = $('state-cand-drilldown'); if(!wrap) return;
  const cands = c.candidates || [];
  const tv = c.votes_polled || cands.reduce((s,x)=>s+(x.total_votes||0),0);
  const mx = (cands[0] && cands[0].total_votes) ? cands[0].total_votes : 1;

  wrap.style.display = 'block';
  wrap.innerHTML = `
    <div class="card" style="border:2px solid var(--saffron);margin-top:16px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
        <div>
          <h2 style="margin:0;color:var(--g)">🗳️ AC ${c.ac_no}. ${esc(c.name)} — Detailed Election Contest</h2>
          <span class="note">${c.category} Category · ${d.state} Assembly ${d.year} · Turnout: <b>${c.turnout_pct ? c.turnout_pct.toFixed(2)+'%' : '–'}</b> (${f(c.votes_polled||0)} / ${f(c.electors||0)})</span>
        </div>
        <button class="btn" onclick="$('state-cand-drilldown').style.display='none'">✕ Close Box</button>
      </div>

      <div class="g g2" style="margin:14px 0">
        <div class="pb win">
          <div class="av" style="font-size:24px">${shc(c.winner_party,46)||av(c.winner_name||'')}</div>
          <div>
            <small>🏆 Winning Candidate</small><br>
            <b style="font-size:17px">${esc(c.winner_name||'–')}</b><br>
            ${dot2(c.winner_party)}${shc(c.winner_party,16)} ${esc(lc(c.winner_party))}<br>
            <b>${f(c.winner_votes||0)} votes (${pc(c.winner_votes||0, tv)}%)</b>
          </div>
        </div>
        <div class="pb run">
          <div class="av" style="font-size:24px">${shc(c.runner_up_party,46)||av(c.runner_up_name||'')}</div>
          <div>
            <small>Runner-up</small><br>
            <b style="font-size:17px">${esc(c.runner_up_name||'–')}</b><br>
            ${c.runner_up_party ? dot2(c.runner_up_party)+' '+shc(c.runner_up_party,16)+' '+esc(lc(c.runner_up_party)) : '–'}<br>
            <b>${c.runner_up_votes ? f(c.runner_up_votes)+' votes ('+pc(c.runner_up_votes, tv)+'%)' : '–'}</b>
          </div>
        </div>
      </div>

      <div style="margin:12px 0">
        <h3>Vote Share Breakdown (Top Candidates)</h3>
        ${cands.slice(0, 6).map(x => `
          <div style="margin:6px 0">
            ${dot2(x.party)}${shc(x.party,15)} <b>${esc(x.name)}</b> (${esc(lc(x.party))}) — ${f(x.total_votes||0)} votes (${pc(x.total_votes||0, tv)}%)
            <div class="bar" style="width:${(x.total_votes||0)/mx*100}%;background:${colC(x.party)};margin-top:3px"></div>
          </div>
        `).join('')}
      </div>

      <h3 style="margin-top:16px">All Contesting Candidates (${cands.length})</h3>
      ${tbl(
        ['#', 'Candidate Name', 'Party', 'Gender', 'Age', 'EVM Votes', 'Postal Votes', 'Total Votes', 'Vote %'],
        cands.map((cd, idx) => `
          <tr class="r"${idx===0?' style="background:rgba(22,163,74,0.12);font-weight:600"':''}>
            <td>${idx+1}</td>
            <td><b>${esc(cd.name)}</b>${idx===0?' 🏆':''}</td>
            <td>${dot2(cd.party)}${shc(cd.party,16)} ${esc(lc(cd.party))}</td>
            <td>${cd.gender||'–'}</td>
            <td>${cd.age||'–'}</td>
            <td>${f(cd.evm_votes||0)}</td>
            <td>${f(cd.postal_votes||0)}</td>
            <td><b>${f(cd.total_votes||0)}</b></td>
            <td>${pc(cd.total_votes||0, tv)}%</td>
          </tr>
        `)
      )}
      <div style="margin-top:10px;font-size:12px;color:var(--text-3)">
        Winning margin: <b style="color:#0a7d3b">${f(c.margin||0)} votes</b> · NOTA votes: <b>${f(c.nota_votes||0)} (${pc(c.nota_votes||0, tv)}%)</b>
      </div>
    </div>
  `;
  tr(wrap);
  wrap.scrollIntoView({behavior:'smooth', block:'start'});
}

function renderUniversalAssemblyView(data, initialAcNo){
  const el = $('app'); if(!el) return;
  const psList = data.parties || [];
  const consts = data.constituencies || [];
  const totSeats = data.total_seats || consts.length;
  const majMark = data.majority_mark || (Math.floor(totSeats/2) + 1);
  const winP = data.leading_party || (psList[0] ? psList[0].party : '–');
  const winSeats = data.leading_seats || (psList[0] ? psList[0].seats : 0);
  const elCr = data.total_electors ? (data.total_electors / 1e7).toFixed(2) + ' Cr' : '–';
  const poCr = data.total_votes_polled ? (data.total_votes_polled / 1e7).toFixed(2) + ' Cr' : '–';
  const turnoutStr = data.avg_turnout_pct ? data.avg_turnout_pct.toFixed(2) + '%' : (data.total_electors ? pc(data.total_votes_polled, data.total_electors) + '%' : '–');

  // Seat grid tiles
  const tilesHtml = consts.map(c => {
    const wp = c.winner_party || 'IND';
    const bg = colC(wp);
    return `<div class="seat-tile" data-party="${esc(wp)}" data-cat="${esc(c.category)}" data-margin="${c.margin||0}" data-no="${c.ac_no}" data-name="${esc(c.name)}" data-winner="${esc(c.winner_name||'')}" style="background:${bg}" onclick="pickAsmSeat('${data.key}', ${c.ac_no})" onmousemove="tipAsmSeat(event, '${data.key}', ${c.ac_no})" onmouseleave="tipAC()"><span style="font-size:11px">${c.ac_no}</span><small>${esc(c.name)}</small></div>`;
  }).join('');

  // Party filter chips
  const partyLegend = psList.slice(0, 10).map(p => `
    <span class="map-legend-item" data-p="${esc(p.party)}" onclick="filterAsmParty('${p.party===_ASM_FILTER_PARTY?'':p.party}')">
      ${dot2(p.party)}${shc(p.party,15)} ${esc(lc(p.party))} <b>${p.seats}</b>
    </span>
  `).join('');

  el.innerHTML = `
    ${bc([['Home',''],['All State Assemblies','assembly'],[`${data.state} Assembly ${data.year}`]])}

    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:12px">
      <div>
        <h1 style="margin:0 0 6px">${data.icon||'🏛️'} ${esc(data.state)} Assembly Election ${data.year}</h1>
        <div class="sub" style="margin:0;font-size:13px;color:var(--text-2)">Official ECI Results · ${totSeats} Constituencies · Majority mark: <b>${majMark}</b></div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn on" onclick="document.getElementById('state-seat-map-section').scrollIntoView({behavior:'smooth'})">🗺️ Seat Map</button>
        <button class="btn" onclick="document.getElementById('state-const-table-section').scrollIntoView({behavior:'smooth'})">🏛️ All ${totSeats} Seats</button>
        <button class="btn" onclick="go('assembly')">← All 31 States</button>
      </div>
    </div>

    ${stats([
      [totSeats, 'Total Seats'],
      [data.status || `${winP} Leading`, 'Outcome'],
      [elCr, 'Total Electors'],
      [poCr, 'Votes Polled'],
      [turnoutStr, 'Turnout %'],
      [psList.length, 'Parties Winning Seats']
    ])}

    <!-- Semicircle Parliament & Party Tallies -->
    <div class="g g2" style="margin-top:14px">
      <div class="card">
        <h2>Legislative Chamber (${totSeats} Seats)</h2>
        ${hemi(psList.map(p=>({c:p.party, seats:p.seats})), totSeats)}
      </div>
      <div class="card">
        <h2>Party-wise Results</h2>
        ${tbl(['Party', 'Seats Won', 'Total Votes', 'Vote Share %'],
          psList.slice(0, 12).map(p => `
            <tr class="r">
              <td>${dot2(p.party)}${shc(p.party,16)} <b>${esc(lc(p.party))}</b></td>
              <td><b>${p.seats}</b></td>
              <td>${f(p.votes||0)}</td>
              <td>${data.total_votes_polled ? pc(p.votes||0, data.total_votes_polled)+'%' : '–'}</td>
            </tr>
          `)
        )}
      </div>
    </div>

    <!-- Interactive Seat Map & Grid -->
    <div id="state-seat-map-section" class="card" style="margin-top:16px">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;border-bottom:1px solid var(--border);padding-bottom:10px;margin-bottom:12px">
        <div>
          <h2 style="margin:0">🗺️ Interactive Constituency Seat Map (${totSeats} Seats)</h2>
          <span class="note">Click any seat tile to inspect the full candidate results, margin, and vote share</span>
        </div>
        <input id="asm-search-seat" placeholder="Search constituency or winner…" style="width:220px;font-size:12px;padding:6px 12px;border-radius:20px" oninput="filterAsmSearch(this.value)">
      </div>

      <div class="map-legend-bar">
        <b>Filter Party:</b> ${partyLegend}
        <button class="btn" style="padding:2px 8px;font-size:11px;margin-left:auto" onclick="filterAsmParty('')">Show All</button>
      </div>

      <div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center">
        <span class="note">Quick Filters:</span>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmMargin('')">All Margins</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmMargin('close5k')">Close &lt; 5k</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmMargin('close25k')">Medium &lt; 25k</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmMargin('landslide')">Landslides &gt; 50k</button>
        <span style="border-left:1px solid var(--border);margin:0 4px;height:14px"></span>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmCat('')">All Categories</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmCat('GEN')">GEN</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmCat('SC')">SC</button>
        <button class="btn" style="padding:2px 8px;font-size:11px" onclick="filterAsmCat('ST')">ST</button>
      </div>

      <div class="seat-map-grid" id="state-seats-grid">${tilesHtml}</div>
      <div class="card" id="state-seat-card" style="margin-top:14px;background:var(--surface-2)">
        <span class="note">👈 Click on any constituency tile above to view full matchup details, votes, margin and candidates.</span>
      </div>
    </div>

    <!-- Candidate Drilldown Target Container -->
    <div id="state-cand-drilldown" style="display:none"></div>

    <!-- All Constituencies Table -->
    <div id="state-const-table-section" class="card" style="margin-top:16px">
      <h2>🏛️ All ${totSeats} Constituencies</h2>
      <div class="f" style="margin-bottom:12px">
        <input id="asmtab-q" placeholder="Search constituency name or candidate…" style="flex:1;min-width:200px" oninput="filterAsmTable(window._curAsmState)">
        <select id="asmtab-p" onchange="filterAsmTable(window._curAsmState)"><option value="">All winning parties</option>${psList.map(p=>`<option value="${p.party}">${esc(lc(p.party))} (${p.seats})</option>`)}</select>
        <select id="asmtab-cat" onchange="filterAsmTable(window._curAsmState)"><option value="">All categories</option><option value="GEN">General</option><option value="SC">SC</option><option value="ST">ST</option></select>
      </div>
      <div id="state-table-wrap"></div>
    </div>

    <div id="tp-ac" style="position:fixed;display:none;background:#000c;color:#fff;padding:6px 10px;border-radius:6px;font-size:12px;pointer-events:none;z-index:99;box-shadow:0 4px 14px rgba(0,0,0,.4)"></div>
    ${footer()}
  `;

  tr(el);
  filterAsmTable(data);
  if(initialAcNo){
    showAsmCandBreakdown(data.key, initialAcNo);
  }
}
"""

content = content[:nav_tabs_pos] + extra_asm_functions + "\n" + content[nav_tabs_pos:]

# 3. Clean up the bottom: remove `loadSeatHistory();` call
content = content.replace("loadSeatHistory();", "")

# 4. Save updated app.js
with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Pass 2 of patch_app_assembly_views.py completed successfully.")
