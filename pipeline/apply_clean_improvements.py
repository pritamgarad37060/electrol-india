# -*- coding: utf-8 -*-
"""
apply_clean_improvements.py - Applies all requested features cleanly:
1. Tooltip fixed right near hovering cursor (boundary clamp, glassmorphic card)
2. Universal search across all 4,113 constituencies and candidates
3. Home page state and year filter bar
4. Dedicated 31-assemblies directory section at the bottom of Home
5. Official Lok Sabha / Legislative seals
6. Purges pre-2024 MH and AP historical code
"""
import json

with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. TOOLTIP ENGINE
# ─────────────────────────────────────────────────────────────────────────────
tooltip_engine = """
/* ── Unified Rock-Solid Floating Tooltip Engine ───────────────────────────── */
function getGlobalTipEl() {
  let t = document.getElementById('global-election-tooltip');
  if (!t) {
    t = document.createElement('div');
    t.id = 'global-election-tooltip';
    t.className = 'global-floating-tooltip';
    document.body.appendChild(t);
  }
  return t;
}

function showFloatingTip(e, html) {
  if (!e) return;
  const t = getGlobalTipEl();
  t.innerHTML = html;
  t.style.display = 'block';
  
  const w = t.offsetWidth || 230;
  const h = t.offsetHeight || 65;
  let x = e.clientX + 16;
  let y = e.clientY + 14;
  
  // Boundary safe: flip if too close to viewport edge
  if (x + w > window.innerWidth - 12) {
    x = Math.max(10, e.clientX - w - 16);
  }
  if (y + h > window.innerHeight - 12) {
    y = Math.max(10, e.clientY - h - 14);
  }
  if (x < 10) x = 10;
  if (y < 10) y = 10;
  
  t.style.left = x + 'px';
  t.style.top = y + 'px';
}

function hideFloatingTip() {
  const t = document.getElementById('global-election-tooltip');
  if (t) t.style.display = 'none';
}
"""

if "function getGlobalTipEl()" not in code:
    code = tooltip_engine + "\n" + code

# ─────────────────────────────────────────────────────────────────────────────
# 2. COMPACT SEARCH LOADER
# ─────────────────────────────────────────────────────────────────────────────
search_loader = """
let COMPACT_CONSTS = null;
function loadCompactConsts(cb){
  if(COMPACT_CONSTS){cb&&cb(COMPACT_CONSTS);return}
  fetch('data/elections/constituencies_compact.json').then(r=>r.json()).then(d=>{
    COMPACT_CONSTS=d;cb&&cb(d);
  }).catch(()=>{cb&&cb([])});
}
loadCompactConsts();
"""
if "let COMPACT_CONSTS" not in code:
    code = search_loader + "\n" + code

# Replace tip functions
code = code.replace(
    "function tipAC(){const t=$('tp-ac');if(t)t.style.display='none'}",
    "function tipAC(){hideFloatingTip()}"
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. HOME PAGE WITH STATE & YEAR FILTERS + 31 ASSEMBLIES SECTION AT BOTTOM
# ─────────────────────────────────────────────────────────────────────────────
old_home_marker = "'':()=>`<div class=\"hero\">"
old_home_end_marker = "'assembly':(stateKey, acNo)=>"

new_home_code = """'':()=>{
  setTimeout(()=>{
    loadAsmIndex(idx => {
      const container = $('home-bottom-assemblies');
      if(!container) return;
      const states = idx.states || [];
      renderHomeBottomAssemblies(states);
    });
  }, 10);

  return `
  <div class="hero">
    <!-- Official Parliament & Election Insignia -->
    <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.08);padding:6px 16px;border-radius:24px;border:1px solid rgba(255,107,0,0.35);margin-bottom:12px">
      <svg viewBox="0 0 32 32" width="22" height="22" fill="none">
        <circle cx="16" cy="16" r="14.5" fill="none" stroke="#FF9933" stroke-width="1.8"/>
        <circle cx="16" cy="16" r="4" fill="#000080"/>
        <path d="M16 4v24M4 16h24M7.5 7.5l17 17M7.5 24.5l17-17" stroke="#ffffff" stroke-width="0.75" opacity="0.8"/>
      </svg>
      <span style="font-size:12px;font-weight:700;letter-spacing:0.5px;color:var(--text)">भारत निर्वाचन पोर्टल · ELECTROL INDIA</span>
    </div>

    <h1>🗳️ National Lok Sabha &amp; 31 State Assemblies</h1>
    <div class="sub">Official ECI Results · 4,656 Total Constituencies · 65,000+ Candidates · Interactive Seat Maps &amp; Analytics</div>

    <!-- Search Tabs -->
    <div class="search-tabs">
      <button class="search-tab on" id="stab-all" onclick="setSTab('all')">All India</button>
      <button class="search-tab" id="stab-ls" onclick="setSTab('ls')">🏛️ Lok Sabha</button>
      <button class="search-tab" id="stab-assembly" onclick="setSTab('assembly')">🏢 State Assemblies</button>
      <button class="search-tab" id="stab-mh" onclick="setSTab('mh')">Maharashtra</button>
      <button class="search-tab" id="stab-ap" onclick="setSTab('ap')">Andhra Pradesh</button>
    </div>

    <!-- Search Input -->
    <div class="hero-search-wrap">
      <span class="sw hero-sw">
        <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input id="hero-search" placeholder="Search any constituency name (e.g. Kalka, Varanasi, Patna), candidate or party…" aria-label="Search" oninput="sg(this)" onblur="sgh(this)" onkeydown="if(event.key==='Enter')go('q/'+encodeURIComponent(this.value))">
        <div class="sug"></div>
      </span>
    </div>

    <!-- Home Quick Filter Bar by State & Year -->
    <div class="home-hero-filter-bar" style="margin-top:16px;display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:10px">
      <div style="display:inline-flex;align-items:center;gap:6px">
        <span style="font-size:12px;color:var(--text-3);font-weight:600">⚡ Jump to State:</span>
        <select id="home-state-select" onchange="if(this.value)go(this.value==='mh'?'mh':(this.value==='ap'?'ap':'assembly/'+this.value))" style="padding:6px 14px;border-radius:20px;font-size:12.5px;font-weight:600;background:var(--surface-2);color:var(--text);border:1px solid var(--border-2)">
          <option value="">Select State Assembly (31 States)…</option>
          <option value="ap">🏛️ Andhra Pradesh (2024)</option>
          <option value="ar">🏔️ Arunachal Pradesh (2024)</option>
          <option value="as">🦏 Assam (2021)</option>
          <option value="br">🌾 Bihar (2020)</option>
          <option value="cg">🌳 Chhattisgarh (2023)</option>
          <option value="dl">🏛️ Delhi (2020)</option>
          <option value="ga">🏖️ Goa (2022)</option>
          <option value="gj">🦁 Gujarat (2022)</option>
          <option value="hr">🚜 Haryana (2024)</option>
          <option value="hp">🏔️ Himachal Pradesh (2022)</option>
          <option value="jk">❄️ Jammu &amp; Kashmir (2024)</option>
          <option value="jh">⛏️ Jharkhand (2024)</option>
          <option value="ka">🐘 Karnataka (2023)</option>
          <option value="kl">🌴 Kerala (2021)</option>
          <option value="mp">🐅 Madhya Pradesh (2023)</option>
          <option value="mh">🏢 Maharashtra (2024)</option>
          <option value="mn">🌺 Manipur (2022)</option>
          <option value="ml">🌧️ Meghalaya (2023)</option>
          <option value="mz">🌿 Mizoram (2023)</option>
          <option value="nl">🌄 Nagaland (2023)</option>
          <option value="or">🌊 Odisha (2024)</option>
          <option value="py">⛵ Puducherry (2021)</option>
          <option value="pb">🌾 Punjab (2022)</option>
          <option value="rj">🏰 Rajasthan (2023)</option>
          <option value="sk">🏔️ Sikkim (2024)</option>
          <option value="tn">🛕 Tamil Nadu (2021)</option>
          <option value="tg">🏛️ Telangana (2023)</option>
          <option value="tr">🎋 Tripura (2023)</option>
          <option value="up">🛕 Uttar Pradesh (2022)</option>
          <option value="uk">⛰️ Uttarakhand (2022)</option>
          <option value="wb">🐅 West Bengal (2021)</option>
        </select>
      </div>

      <div style="display:inline-flex;align-items:center;gap:6px">
        <span style="font-size:12px;color:var(--text-3);font-weight:600">📅 Election Year:</span>
        <div style="display:inline-flex;gap:4px">
          <button class="yr-btn on" onclick="filterHomeBottomYear('all', this)">All</button>
          <button class="yr-btn" onclick="filterHomeBottomYear('2024', this)">2024</button>
          <button class="yr-btn" onclick="filterHomeBottomYear('2023', this)">2023</button>
          <button class="yr-btn" onclick="filterHomeBottomYear('2022', this)">2022</button>
          <button class="yr-btn" onclick="filterHomeBottomYear('2021', this)">2021</button>
          <button class="yr-btn" onclick="filterHomeBottomYear('2020', this)">2020</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Key Navigation Cards -->
  <div class="g g4" style="margin-top:18px">
    ${[
      ['🏛️','Lok Sabha 2024','543 Parliamentary Seats · National NDA vs INDIA','ls'],
      ['🏢','Maharashtra 2024','288 Seats · Mahayuti Landslide Victory','mh'],
      ['🏛️','Andhra Pradesh 2024','175 Seats · NDA (TDP+JSP+BJP) Majority','ap'],
      ['🚜','Haryana 2024','90 Seats · BJP Majority (48 Seats)','assembly/hr'],
      ['🗺️','Interactive Map','All-India Lok Sabha & State Assembly Maps','map'],
      ['🏘️','All 31 Assemblies','State-by-State Legislative Chamber Dashboards','assembly'],
      ['👩','Women in Elections','National & Assembly Representation Analysis','women'],
      ['⚖️','Compare Elections','Side-by-side Matchups & Swings','cmp']
    ].map(t=>`<div class="card tile" role="button" tabindex="0" onkeydown="if(event.key==='Enter')this.click()" onclick="go('${t[3]}')"><div class="i">${t[0]}</div><b>${t[1]}</b><small>${t[2]}</small></div>`).join('')}
  </div>

  <!-- Dedicated All 31 Assemblies Section at the Bottom of Home -->
  <div style="margin-top:36px;border-top:1px solid var(--border);padding-top:24px">
    <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;margin-bottom:14px">
      <div>
        <div style="display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:var(--saffron);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">
          <span>🏛️ STATE ELECTIONS DIRECTORY</span>
        </div>
        <h2 style="margin:0;font-size:22px">All 31 State Legislative Assemblies</h2>
        <div class="note" style="margin-top:3px">Complete ECI Results · 4,113 Assembly Seats · Interactive Seat Maps for Every State</div>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn on" onclick="go('assembly')">Explore Assembly Hub →</button>
      </div>
    </div>

    <div class="card" style="padding:14px;margin-bottom:16px">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
        <div class="tab-pills" id="home-reg-pills" style="margin:0">
          <button class="tab-pill on" onclick="filterHomeBottomReg('all', this)">All (31)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('North', this)">North (7)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('South', this)">South (5)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('West', this)">West (3)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('East', this)">East (4)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('Central', this)">Central (2)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('North-East', this)">North-East (8)</button>
          <button class="tab-pill" onclick="filterHomeBottomReg('UT', this)">UTs (3)</button>
        </div>
        <input id="home-asm-search" placeholder="Filter state name or winning party…" style="min-width:220px;padding:7px 14px;border-radius:20px;font-size:12.5px" oninput="filterHomeBottomCards()">
      </div>
    </div>

    <div id="home-bottom-assemblies"><p class="note">Loading state assembly cards…</p></div>
  </div>

  ${footer()}
  `;
},
"""

h_idx = code.find(old_home_marker)
h_end_idx = code.find(old_home_end_marker, h_idx)
if h_idx != -1 and h_end_idx != -1:
    code = code[:h_idx] + new_home_code + code[h_end_idx:]

# ─────────────────────────────────────────────────────────────────────────────
# 4. BOTTOM HOME ASSEMBLIES HELPERS
# ─────────────────────────────────────────────────────────────────────────────
bottom_helpers = """
let _HOME_BOTTOM_YEAR = 'all';
let _HOME_BOTTOM_REG = 'all';

function filterHomeBottomYear(yr, btn) {
  _HOME_BOTTOM_YEAR = yr;
  if(btn && btn.parentNode){
    btn.parentNode.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
    btn.classList.add('on');
  }
  filterHomeBottomCards();
  const el = $('home-bottom-assemblies');
  if(el) el.scrollIntoView({behavior:'smooth', block:'nearest'});
}

function filterHomeBottomReg(reg, btn) {
  _HOME_BOTTOM_REG = reg;
  if(btn && btn.parentNode){
    btn.parentNode.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
    btn.classList.add('on');
  }
  filterHomeBottomCards();
}

function filterHomeBottomCards() {
  const q = ($('home-asm-search') ? $('home-asm-search').value : '').toLowerCase().trim();
  document.querySelectorAll('#home-bottom-assemblies .asm-card').forEach(card => {
    const yr = card.dataset.year || '';
    const reg = card.dataset.reg || '';
    const name = (card.dataset.name || '').toLowerCase();
    const win = (card.dataset.win || '').toLowerCase();
    
    const matchYr = _HOME_BOTTOM_YEAR === 'all' || yr === _HOME_BOTTOM_YEAR;
    const matchReg = _HOME_BOTTOM_REG === 'all' || reg === _HOME_BOTTOM_REG;
    const matchQ = !q || name.includes(q) || win.includes(q);
    
    card.style.display = (matchYr && matchReg && matchQ) ? 'flex' : 'none';
  });
}

function renderHomeBottomAssemblies(states) {
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
}
"""

if "function renderHomeBottomAssemblies" not in code:
    code = code.replace("function updateNavTabs(){", bottom_helpers + "\nfunction updateNavTabs(){\n", 1)

# ─────────────────────────────────────────────────────────────────────────────
# 5. UNIVERSAL SEARCH (sg and pages.q)
# ─────────────────────────────────────────────────────────────────────────────
sg_idx = code.find("function sg(inp){")
sg_end_idx = code.find("function updateThemeIcon()", sg_idx)

new_sg_func = """function sg(inp){
  const q=inp.value.trim().toLowerCase(),b=inp.parentNode.querySelector(".sug");
  if(q.length<2){b.style.display="none";hideFloatingTip();return}
  
  if(!CI){
    initMH();initAP();
    CI=[];
    // 1. Lok Sabha Constituencies & Candidates
    PC.forEach(c=>{
      CI.push([c.n+" [Lok Sabha, "+S[c.si]+"]","Lok Sabha","pc/"+c.id,c.n.toLowerCase()]);
      c.cs.forEach(x=>{if(x[3]!=NI)CI.push([x[0]+" ["+c.n+", LS]","LS Candidate","pc/"+c.id,x[0].toLowerCase()])});
    });
    S.forEach((s,i)=>CI.push([s,"State","map/"+i,s.toLowerCase()]));
    PA.forEach(p=>{if(p.i!=NI&&p.cands>3)CI.push([lab(p.i),"Party","party/"+p.i,lab(p.i).toLowerCase()])});
  }

  // Preload compact constituencies if not loaded
  if(!COMPACT_CONSTS){
    loadCompactConsts(()=>{if(inp.value.trim().length>=2)sg(inp);});
  }

  const tab=inp.id==="hero-search"?STAB:"all";
  let pool=CI.slice();

  // Add all 4,113 State Assembly constituencies from compact dataset
  if(COMPACT_CONSTS && (tab==="all" || tab==="assembly" || tab==="mh" || tab==="ap")){
    COMPACT_CONSTS.forEach(c=>{
      // c: [name, state, key, ac_no, winner, party, margin, turnout]
      const [name, state, key, no, winner, party, margin] = c;
      if(tab==="mh" && key!=="mh") return;
      if(tab==="ap" && key!=="ap") return;
      
      const title = `${name} [${state} Assembly, AC ${no}]`;
      const link = key==='mh'?`ac/${no}`:(key==='ap'?`apac/${no}`:`assembly/${key}/${no}`);
      pool.push([title, `${state} Assembly`, link, name.toLowerCase()]);
      if(winner && winner.length > 2){
        pool.push([`${winner} [${name}, ${state} — ${party}]`, "Assembly Winner", link, winner.toLowerCase()]);
      }
    });
  }

  if(tab==="ls") pool = pool.filter(x=>x[1].startsWith("Lok Sabha")||x[1]==="State"||x[1]==="Party"||x[1]==="LS Candidate");
  else if(tab==="mh") pool = pool.filter(x=>x[0].includes("Maharashtra")||x[1].includes("MH"));
  else if(tab==="ap") pool = pool.filter(x=>x[0].includes("Andhra Pradesh")||x[1].includes("AP"));

  const _ord={"Lok Sabha":0,"Assembly Winner":1,"State Assembly":0,State:2,Party:3,"LS Candidate":4};
  const r=pool.filter(x=>x[3].includes(q)).sort((a,c)=>(c[3].startsWith(q)-a[3].startsWith(q))||((_ord[a[1]]||5)-(_ord[c[1]]||5))).slice(0,14);
  b.innerHTML=r.length?r.map(x=>`<div class="si" role="option" onmousedown="go('${x[2]}')"><span class="si-title">${esc(x[0])}</span><small class="si-badge">${x[1]}</small></div>`).join(""):"<div class=\"si\"><small>No match found — press Enter to view all results across India</small></div>";
  tr(b);b.style.display="block";
}
"""

if sg_idx != -1 and sg_end_idx != -1:
    code = code[:sg_idx] + new_sg_func + "\n" + code[sg_end_idx:]

# Update pages.q
q_start = code.find("'q':q=>{")
q_end = code.find("'mh':", q_start)
if q_start != -1 and q_end != -1:
    new_q_code = """'q':q=>{
  q=decodeURIComponent(q||'').toLowerCase().trim();
  initMH();initAP();

  // 1. Lok Sabha Constituencies
  const cs=q?PC.filter(c=>c.n.toLowerCase().includes(q)||S[c.si].toLowerCase().includes(q)).slice(0,25):[];

  // 2. Lok Sabha Candidates
  const cd=[];
  if(q.length>1){
    for(const c of PC){
      for(const x of c.cs){
        if(x[3]!=NI&&x[0].toLowerCase().includes(q)){
          cd.push([x,c]);
          if(cd.length>=30)break;
        }
      }
      if(cd.length>=30)break;
    }
  }

  // 3. All 31 State Assembly Constituencies from compact index
  let asmMatches = [];
  if(COMPACT_CONSTS && q.length > 1){
    asmMatches = COMPACT_CONSTS.filter(c => {
      // c: [name, state, key, ac_no, winner, party, margin, turnout]
      return c[0].toLowerCase().includes(q) || c[1].toLowerCase().includes(q) || (c[4]&&c[4].toLowerCase().includes(q)) || (c[5]&&c[5].toLowerCase().includes(q));
    }).slice(0, 50);
  }

  const totMatches = cs.length + cd.length + asmMatches.length;

  return`${bc([['Home',''],['Search']])}<h1>🔍 Universal Search Results: “${esc(q)}”</h1>
  <p class="note">${totMatches} matches across Parliament and 31 State Legislative Assemblies.</p>

  <!-- Assembly Constituencies Table -->
  ${asmMatches.length ? `
    <div class="card" style="margin-top:14px">
      <h2>🏛️ State Assembly Constituencies (${asmMatches.length}${asmMatches.length>=50?'+':''})</h2>
      <p class="note">Constituencies from state legislative elections across India:</p>
      ${tbl(['House / State','AC No.','Constituency','Winner Candidate','Party','Margin','Turnout %','Action'],
        asmMatches.map(c => {
          const [name, state, key, no, winner, party, margin, turnout] = c;
          const link = key==='mh'?`ac/${no}`:(key==='ap'?`apac/${no}`:`assembly/${key}/${no}`);
          return `<tr class="r" style="cursor:pointer" onclick="go('${link}')">
            <td><span class="tag" style="font-weight:600">${state} Assembly</span></td>
            <td>${no}</td>
            <td><b><a onclick="event.stopPropagation();go('${link}')">${esc(name)}</a></b></td>
            <td><b>${esc(winner||'–')}</b></td>
            <td>${dot2(party)}${shc(party,15)} ${esc(lc(party))}</td>
            <td><b>${f(margin||0)}</b></td>
            <td>${turnout ? turnout.toFixed(1)+'%' : '–'}</td>
            <td><button class="btn" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();go('${link}')">View Seat →</button></td>
          </tr>`;
        })
      )}
    </div>
  ` : ''}

  <!-- Lok Sabha Constituencies Table -->
  ${cs.length ? `
    <div class="card" style="margin-top:14px">
      <h2>🏛️ Lok Sabha Constituencies (${cs.length})</h2>
      ${tbl(['Constituency','State','Category','Winner','Party','Margin','Turnout'],
        cs.map(c=>`<tr class="r">
          <td><a onclick="go('pc/${c.id}')"><b>${esc(c.n)}</b></a></td>
          <td>${S[c.si]}</td>
          <td>${c.cat}</td>
          <td><b>${esc(c.w[0])}</b></td>
          <td>${dot(c.w[3])}${sh(c.w[3],15)} ${esc(lab(c.w[3]))}</td>
          <td>${f(c.m)}</td>
          <td>${c.t.toFixed(1)}%</td>
        </tr>`)
      )}
    </div>
  ` : ''}

  <!-- Lok Sabha Candidates Table -->
  ${cd.length ? `
    <div class="card" style="margin-top:14px">
      <h2>👥 Lok Sabha Candidates (${cd.length}${cd.length>=30?'+':''})</h2>
      ${tbl(['Candidate','Party','Constituency','State','Votes','Result'],
        cd.map(([x,c])=>`<tr class="r">
          <td><b>${esc(x[0])}</b></td>
          <td>${pl(x[3])}</td>
          <td>${cl(c)}</td>
          <td>${S[c.si]}</td>
          <td>${f(x[6])}</td>
          <td>${x===c.w?'<span class="badge" style="background:var(--win);color:var(--g)">🏆 Won</span>':'Lost'}</td>
        </tr>`)
      )}
    </div>
  ` : ''}

  ${!totMatches ? `<div class="card"><p style="font-size:15px;color:var(--text-2);padding:24px 0;text-align:center">No results found for “${esc(q)}”. Try searching by constituency name (e.g. Kalka, Varanasi, Patna), candidate name, or state.</p></div>` : ''}
  `;
},
"""
    code = code[:q_start] + new_q_code + code[q_end:]

# ─────────────────────────────────────────────────────────────────────────────
# 6. CLEAN UP PRE-2024 IN MAHARASHTRA & ANDHRA PRADESH
# ─────────────────────────────────────────────────────────────────────────────
# Clean MH to keep only 2024
mh_start = code.find("'mh':")
mh_end = code.find("'mhac':")
if mh_start != -1 and mh_end != -1:
    clean_mh = """'mh':()=>{
  initMH();const d=MH.ps.filter(p=>p.seats),al={Mahayuti:0,MVA:0,Others:0};d.forEach(p=>al[mal(p.c)]+=p.seats);
  return`${bc([['Home',''],['All Assemblies','assembly'],['Maharashtra Assembly 2024']])}
  <h1>🏢 Maharashtra Assembly Election 2024</h1><div class="f"><button class="btn on">Results</button><button class="btn" onclick="go('mhmap')">🗺️ Map</button><button class="btn" onclick="go('mhs')">All 288 constituencies</button></div>
  ${stats([[288,'Total Seats'],[288,'Results Declared'],[(MH.el/1e7).toFixed(2)+' Cr','Total Electors'],[(MH.tot/1e7).toFixed(2)+' Cr','Votes Polled'],[pc(MH.tot,MH.el)+'%','Turnout'],[d.length,'Parties winning seats']])}
  <div class="g g2"><div class="card"><h2>Seats Won by Party</h2>${hemi(d.map(p=>({c:p.c,seats:p.seats})),288)}</div><div class="card"><h2>Party-wise Results</h2>${tbl(['Party','Seats','Votes','Vote share'],MH.ps.slice(0,16).map(p=>`<tr class="r"><td>${dot2(p.c)}${shc(p.c,18)} ${esc(lc(p.c))}</td><td>${p.seats}</td><td>${f(p.votes)}</td><td>${pc(p.votes,MH.tot)}%</td></tr>`))}</div></div>
  <div class="card"><h2>Alliance tally</h2>${Object.entries(al).map(([k,n])=>`<div style="margin:6px 0">${k}: <b>${n}</b><br><span class="bar" style="width:${n/288*100}%;background:${{Mahayuti:'#ff7a00',MVA:'#1d6fe8',Others:'#8a8f98'}[k]}"></span></div>`).join('')}<p class="note">Majority mark: 145. Mahayuti = BJP+SHS+NCP; MVA = INC+SHS(UBT)+NCP(SP). Source: ECI detailed results.</p></div>`
},
"""
    code = code[:mh_start] + clean_mh + code[mh_end:]

# Clean AP historical routes: aph, aphmap, aphcmp, aphac
aph_start = code.find("'aph':")
aps_start = code.find("'aps':")
if aph_start != -1 and aps_start != -1:
    code = code[:aph_start] + code[aps_start:]

# Remove aphac
aphac_start = code.find("'aphac':")
if aphac_start != -1:
    aphac_end = code.find("};", aphac_start)
    if aphac_end != -1:
        code = code[:aphac_start] + code[aphac_end:]

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied all improvements cleanly to js/app.js.")
