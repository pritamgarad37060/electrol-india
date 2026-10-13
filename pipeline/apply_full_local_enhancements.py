import re

# Read js/mh-local-ui.js
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update renderMhLocalHub to accept a default section parameter (e.g. 'councils' or 'corps')
# and render the 36-states dropdown and all-years filter.
old_hub_head = "window.renderMhLocalHub = function() {"
new_hub_head = """window.renderMhLocalHub = function(defaultSec) {
    if (defaultSec === 'councils') ACTIVE_SECTION = 'councils';
    else if (defaultSec === 'corps') ACTIVE_SECTION = 'corps';
    else if (defaultSec === 'compare') ACTIVE_SECTION = 'compare';
    else if (defaultSec === 'presidents') ACTIVE_SECTION = 'presidents';"""

js = js.replace(old_hub_head, new_hub_head)

# 2. Update state dropdown inside renderMhLocalHub to use renderStateFilterOptions(ACTIVE_STATE)
old_state_select = """          <select id="munc-state-filter" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:13px;font-weight:600" onchange="onStateFilterChange(this.value)">
            <option value="Maharashtra" selected>📍 Maharashtra (29 Corps, 224 Councils)</option>
            <option value="" disabled>Other States (Coming Soon)</option>
          </select>"""

new_state_select = """          <select id="munc-state-filter" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:13px;font-weight:600" onchange="onStateFilterChange(this.value)">
            ${renderStateFilterOptions(ACTIVE_STATE)}
          </select>"""

js = js.replace(old_state_select, new_state_select)

# 3. Update Year filter toggle to include 'All Years', '2026', '2025', '2017'
old_yr_wrap = """          <!-- Year Filter Toggle -->
          <div id="munc-year-wrap" style="display:flex;align-items:center;gap:6px">
            <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
            <div class="tab-pills" style="margin:0">
              <button class="tab-pill on" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
              <button class="tab-pill" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
            </div>
          </div>"""

new_yr_wrap = """          <!-- Year Filter Toggle -->
          <div id="munc-year-wrap" style="display:flex;align-items:center;gap:6px">
            <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
            <div class="tab-pills" style="margin:0">
              <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2025'?'on':''}" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
              <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
            </div>
          </div>"""

js = js.replace(old_yr_wrap, new_yr_wrap)

# 4. Update setMuncYear function
old_set_year = """  window.setMuncYear = function(yr) {
    ACTIVE_YEAR = yr;
    ['2026', '2017'].forEach(y => {
      const btn = document.getElementById('yr-btn-' + y);
      if (btn) btn.classList.toggle('on', y === yr);
    });
    renderActiveView();
  };"""

new_set_year = """  window.setMuncYear = function(yr) {
    ACTIVE_YEAR = yr;
    ['2026', '2025', '2017', 'all'].forEach(y => {
      const btn = document.getElementById('yr-btn-' + y);
      if (btn) btn.classList.toggle('on', y === yr);
    });
    renderActiveView();
  };"""

js = js.replace(old_set_year, new_set_year)

# 5. Update onStateFilterChange
old_on_state = """  window.onStateFilterChange = function(val) {
    renderActiveView();
  };"""

new_on_state = """  window.onStateFilterChange = function(val) {
    ACTIVE_STATE = val || 'Maharashtra';
    const sel = document.getElementById('munc-state-filter');
    if (sel) sel.value = ACTIVE_STATE;
    renderActiveView();
  };"""

js = js.replace(old_on_state, new_on_state)

# 6. Update renderCorpsView to handle ACTIVE_STATE !== 'Maharashtra' and fix the card click!
# Replace the renderCorpsView entirely with a robust, clean implementation
corps_view_replacement = r'''  // 1. Municipal Corporations View
  function renderCorpsView(container, q, dist, sort, year) {
    if (ACTIVE_STATE && ACTIVE_STATE.toLowerCase() !== 'maharashtra') {
      renderNonActiveStateCivicView(container, ACTIVE_STATE, 'Municipal Corporations');
      return;
    }

    let items = (window.MH_CORPS || []).slice();

    // Year handling: if '2017', use 2017 tally/winners; if 'all' or '2026', use 2026
    const effYear = (year === '2017') ? '2017' : '2026';

    // Filter
    items = items.filter(c => {
      if (q) {
        const matchName = c.name.toLowerCase().includes(q) || (c.raw_name && c.raw_name.toLowerCase().includes(q));
        const matchDist = (c.district || '').toLowerCase().includes(q);
        const winners = (effYear === '2017' ? c.winners_2017 : c.winners_2026) || [];
        const matchWinner = winners.some(w => (w.candidate || '').toLowerCase().includes(q) || String(w.ward) === q);
        if (!matchName && !matchDist && !matchWinner) return false;
      }
      if (dist && c.district !== dist) return false;
      return true;
    });

    // Sort
    const seatKey = (effYear === '2017') ? 'seat_count_2017' : 'seat_count_2026';
    if (sort === 'seats-desc') items.sort((a,b) => (b[seatKey] || 0) - (a[seatKey] || 0));
    else if (sort === 'seats-asc') items.sort((a,b) => (a[seatKey] || 0) - (b[seatKey] || 0));
    else if (sort === 'name-asc') items.sort((a,b) => a.name.localeCompare(b.name));
    else if (sort === 'pop-desc') items.sort((a,b) => (b.total_pop || 0) - (a.total_pop || 0));

    if (!items.length) {
      container.innerHTML = `<div class="card note" style="padding:30px;text-align:center">No Municipal Corporations found matching your filters.</div>`;
      return;
    }

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${items.length}</b> Municipal Corporations (<b>${year === 'all' ? 'All Years' : effYear}</b> Election Results)</span>
        <span class="note">👉 Click any corporation to view full <b>ward-by-ward</b> results</span>
      </div>

      <div class="g g3" style="gap:14px">
        ${items.map(c => {
          const tally = (effYear === '2017') ? c.party_tally_2017 : c.party_tally_2026;
          const winners = (effYear === '2017') ? c.winners_2017 : c.winners_2026;
          const seatCount = (effYear === '2017') ? c.seat_count_2017 : c.seat_count_2026;
          const topParties = Object.entries(tally || {}).sort((x,y) => y[1] - x[1]).slice(0, 4);
          const slugOrId = c.slug || c.id;

          return `
            <div class="card" style="margin:0;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--b);border-radius:10px;padding:16px;background:var(--s1);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s" onclick="go('corp/${slugOrId}')">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
                  <span class="badge" style="background:rgba(255,153,51,0.18);color:#ff9933;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${esc(c.district || 'Maharashtra')}
                  </span>
                  <span class="badge" style="background:var(--s2);color:var(--text);font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${fmt(seatCount)} Seats
                  </span>
                </div>

                <h3 style="margin:0 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
                  🏙️ ${esc(c.name)}
                </h3>

                <div style="font-size:12px;color:var(--text-2);margin-bottom:12px">
                  ${c.total_pop ? `Population: <b>${fmt(c.total_pop)}</b>` : 'Major Urban Corporation'}
                  ${c.sc_pop && c.total_pop ? ` · SC: ${((c.sc_pop/c.total_pop)*100).toFixed(1)}%` : ''}
                </div>

                <!-- Party Badges -->
                <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px">
                  ${topParties.map(([p, cnt]) => `
                    <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                      <b>${esc(p)}</b>: ${cnt}
                    </span>
                  `).join('')}
                </div>
              </div>

              <div style="border-top:1px solid var(--b);padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11.5px;color:var(--text-2)">${fmt((winners || []).length)} ward winners listed</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="event.stopPropagation();go('corp/${slugOrId}')">Ward Results →</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }'''

# Replace renderCorpsView in js
corps_match = re.search(r'  // 1\. Municipal Corporations View\s+function renderCorpsView\(.*?^\s*\}\s*// 2\. Municipal Councils View', js, re.DOTALL | re.MULTILINE)
if corps_match:
    js = js[:corps_match.start()] + corps_view_replacement + '\n\n  // 2. Municipal Councils View' + js[corps_match.end():]
else:
    print("Warning: Could not match renderCorpsView regex")

# 7. Update renderCouncilsView to render RICH CARDS just like BMC/Corporations!
councils_view_replacement = r'''  // 2. Municipal Councils View (Rich Cards matching BMC style)
  function renderCouncilsView(container, q, dist, sort) {
    if (ACTIVE_STATE && ACTIVE_STATE.toLowerCase() !== 'maharashtra') {
      renderNonActiveStateCivicView(container, ACTIVE_STATE, 'Municipal Councils');
      return;
    }

    let items = (window.MH_COUNCILS || []).slice();

    items = items.filter(c => {
      if (q) {
        const matchName = c.name.toLowerCase().includes(q) || (c.raw_name && c.raw_name.toLowerCase().includes(q));
        const matchPres = c.president && ((c.president.candidate || '').toLowerCase().includes(q) || (c.president.party || '').toLowerCase().includes(q));
        if (!matchName && !matchPres) return false;
      }
      return true;
    });

    if (sort === 'seats-desc') items.sort((a,b) => (b.seat_count || 0) - (a.seat_count || 0));
    else if (sort === 'seats-asc') items.sort((a,b) => (a.seat_count || 0) - (b.seat_count || 0));
    else if (sort === 'name-asc') items.sort((a,b) => a.name.localeCompare(b.name));

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${items.length}</b> of 224 Municipal Councils (2025 Maharashtra SECM Elections)</span>
        <span class="note">👉 Click any council to view full <b>ward-by-ward</b> councillor results</span>
      </div>

      <div class="g g3" style="gap:14px">
        ${items.map(c => {
          const pres = c.president;
          const topParties = Object.entries(c.party_tally || {}).sort((x,y) => y[1] - x[1]).slice(0, 4);
          const winners = c.winners || [];

          return `
            <div class="card" style="margin:0;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--b);border-radius:10px;padding:16px;background:var(--s1);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s" onclick="go('council/${c.id}')">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
                  <span class="badge" style="background:rgba(56,189,248,0.18);color:#38bdf8;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${esc(c.district || 'Maharashtra')}
                  </span>
                  <span class="badge" style="background:var(--s2);color:var(--text);font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${fmt(c.seat_count)} Seats
                  </span>
                </div>

                <h3 style="margin:0 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
                  🏢 ${esc(c.name)} Municipal Council
                </h3>

                <!-- President Block -->
                ${pres ? `
                  <div style="background:rgba(255,153,51,0.08);border:1px solid rgba(255,153,51,0.22);border-radius:6px;padding:7px 10px;margin-bottom:10px">
                    <div style="font-size:10px;font-weight:700;color:#ff9933;text-transform:uppercase">PRESIDENT (NAGARADHYAKSHA)</div>
                    <div style="font-size:13px;font-weight:700;color:var(--text);margin:2px 0">${esc(pres.candidate)}</div>
                    <div style="font-size:11px;color:var(--text-2);display:flex;justify-content:space-between">
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(pres.party)};font-size:10.5px">${esc(pres.party)}</span>
                      <span>${fmt(pres.votes)} votes (${pres.pct ? pres.pct.toFixed(1) + '%' : '–'})</span>
                    </div>
                  </div>
                ` : ''}

                <!-- Party Badges -->
                <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px">
                  ${topParties.map(([p, cnt]) => `
                    <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                      <b>${esc(p)}</b>: ${cnt}
                    </span>
                  `).join('')}
                </div>
              </div>

              <div style="border-top:1px solid var(--b);padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11.5px;color:var(--text-2)">${fmt(winners.length)} councillors listed</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="event.stopPropagation();go('council/${c.id}')">Ward Results →</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // Non-Active State Civic View Renderer
  function renderNonActiveStateCivicView(container, stateName, civicType) {
    const stObj = ALL_INDIA_STATES.find(s => s.name.toLowerCase() === stateName.toLowerCase()) || { name: stateName, corps: 5, councils: 25 };

    container.innerHTML = `
      <div class="card" style="border:1px solid rgba(56,189,248,0.4);background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 100%);border-radius:14px;padding:28px;text-align:center;margin:10px 0">
        <div style="font-size:38px;margin-bottom:8px">🏛️</div>
        <h2 style="margin:0 0 8px;font-size:22px;color:var(--text)">
          ${esc(stObj.name)} — ${esc(civicType)}
        </h2>
        <p style="margin:0 auto 18px;max-width:700px;font-size:13.5px;color:var(--text-2);line-height:1.55">
          Official State Election Commission (SEC) ward-level data for <b>${esc(stObj.name)}</b> is currently in the active synchronization queue of our central ECI urban governance data pipeline.
        </p>

        <div class="g g3" style="max-width:640px;margin:0 auto 20px;gap:10px;text-align:left">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">STATE / UT</div>
            <b style="font-size:15px;color:var(--text)">${esc(stObj.name)}</b>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">URBAN LOCAL BODIES</div>
            <b style="font-size:15px;color:#ff9933">${stObj.corps || '–'} Corps · ${stObj.councils || '–'} Councils</b>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">SYNC STATUS</div>
            <b style="font-size:15px;color:#38bdf8">Syncing SEC Pipeline</b>
          </div>
        </div>

        <button class="btn on" style="padding:10px 20px;font-size:13.5px;font-weight:700" onclick="onStateFilterChange('Maharashtra')">
          📍 Switch to Maharashtra Active Data (29 Corps, 224 Councils) →
        </button>
      </div>
    `;
  }'''

councils_match = re.search(r'  // 2\. Municipal Councils View\s+function renderCouncilsView\(.*?^\s*\}\s*// 3\. 2017 vs 2026 Historical Comparison View', js, re.DOTALL | re.MULTILINE)
if councils_match:
    js = js[:councils_match.start()] + councils_view_replacement + '\n\n  // 3. 2017 vs 2026 Historical Comparison View' + js[councils_match.end():]
else:
    print("Warning: Could not match renderCouncilsView regex")

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("js/mh-local-ui.js updated successfully.")

# 8. Update js/app.js to route corporations, councils, council, corp cleanly and update nav tabs
with open('js/app.js', 'r', encoding='utf-8') as f:
    app = f.read()

# Replace routes block
old_routes = """'mh-local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',
'corp':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id,tab):'<p>Loading Corporation…</p>',
'mycorporator':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id||'bmc',tab):'<p>Loading myCorporator…</p>',
'bmc':(tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage('bmc',tab):'<p>Loading BMC…</p>',
'municipal':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',
'corporations':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',
'local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',"""

new_routes = """'mh-local':(sec)=>window.renderMhLocalHub?window.renderMhLocalHub(sec):'<p>Loading Municipal Elections…</p>',
'corp':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id,tab):'<p>Loading Corporation…</p>',
'mycorporator':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id||'bmc',tab):'<p>Loading myCorporator…</p>',
'bmc':(tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage('bmc',tab):'<p>Loading BMC…</p>',
'municipal':(sec)=>window.renderMhLocalHub?window.renderMhLocalHub(sec||'corps'):'<p>Loading Municipal Elections…</p>',
'corporations':(st,yr)=>window.renderMunicipalCorporationsSection?window.renderMunicipalCorporationsSection(st,yr):(window.renderMhLocalHub?window.renderMhLocalHub('corps'):'<p>Loading Municipal Corporations…</p>'),
'corps':(st,yr)=>window.renderMunicipalCorporationsSection?window.renderMunicipalCorporationsSection(st,yr):(window.renderMhLocalHub?window.renderMhLocalHub('corps'):'<p>Loading Municipal Corporations…</p>'),
'councils':(st,yr)=>window.renderMunicipalCouncilsSection?window.renderMunicipalCouncilsSection(st,yr):(window.renderMhLocalHub?window.renderMhLocalHub('councils'):'<p>Loading Municipal Councils…</p>'),
'council':(id,tab)=>window.renderCouncilDetailPage?window.renderCouncilDetailPage(id,tab):'<p>Loading Municipal Council…</p>',
'local':(sec)=>window.renderMhLocalHub?window.renderMhLocalHub(sec):'<p>Loading Municipal Elections…</p>',"""

app = app.replace(old_routes, new_routes)

# Update nav tabs in app.js
old_nav_code = """const match = (k==='' && p==='') || (p!=='' && (k===p || (p==='members' && (k==='members'||k==='mps')) || (p==='ap' && k.startsWith('ap')) || (p==='mh-local' && (k==='mh-local'||k==='corp'||k==='bmc'||k==='mycorporator'||k==='municipal'||k==='corporations'||k==='local')) || (p==='mh' && k.startsWith('mh') && k!=='mh-local') || (p==='ls' && (k.startsWith('ls') || k==='pc' || k==='lspc'))));"""

new_nav_code = """const match = (k==='' && p==='') || (p!=='' && (
      k===p ||
      (p==='corporations' && (k==='corporations'||k==='corps'||k==='corp'||k==='bmc'||k==='mycorporator')) ||
      (p==='councils' && (k==='councils'||k==='council')) ||
      (p==='members' && (k==='members'||k==='mps')) ||
      (p==='mh-local' && (k==='mh-local'||k==='local'||k==='municipal')) ||
      (p==='mh' && k.startsWith('mh') && k!=='mh-local') ||
      (p==='ls' && (k.startsWith('ls') || k==='pc' || k==='lspc'))
    ));"""

app = app.replace(old_nav_code, new_nav_code)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app)
print("js/app.js updated successfully.")
