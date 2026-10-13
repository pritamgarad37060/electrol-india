import re

with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Helper function to generate candidate breakdown rows
cand_helper_js = r'''
  function renderCandidateLeaderboardHtml(cands) {
    if (!cands || !cands.length) return '<p class="note">No candidate breakdown available.</p>';
    return `
      <div style="overflow-x:auto;margin-top:10px">
        <table class="tbl" style="margin:0;font-size:12px">
          <thead>
            <tr>
              <th style="width:40px">Pos</th>
              <th>Candidate</th>
              <th>Political Party</th>
              <th style="text-align:right">Votes</th>
              <th style="text-align:right">Vote Share</th>
            </tr>
          </thead>
          <tbody>
            ${cands.map((c, idx) => {
              const posLabel = idx === 0 ? '🥇 1st (Win)' : (idx === 1 ? '🥈 2nd' : (idx === 2 ? '🥉 3rd' : `${idx + 1}th`));
              const isWin = idx === 0;
              const pCol = getPartyColor(c[1]);
              return `
                <tr class="r" style="${isWin ? 'background:rgba(34,197,94,0.06)' : ''}">
                  <td><b>${posLabel}</b></td>
                  <td><b style="color:${isWin ? '#4ade80' : 'var(--text)'}">${esc(c[0])}</b></td>
                  <td>
                    <span class="tag" style="background:var(--s2);border-left:3px solid ${pCol};font-size:11px">
                      ${esc(c[1])}
                    </span>
                  </td>
                  <td style="text-align:right"><b style="color:${isWin ? '#ff9933' : 'var(--text)'}">${fmt(c[2])}</b></td>
                  <td style="text-align:right"><b>${c[3] ? c[3].toFixed(1) + '%' : '–'}</b></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
'''

# 1. Update compact toolbar in renderMhLocalHub
compact_filter_toolbar = r'''      <!-- Compact Controls & Filter Toolbar -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Search city, council, ward, or candidate…" aria-label="Search Municipal" oninput="renderActiveView()">
        </div>

        <div class="munc-filter-group">
          <!-- State Filter Dropdown with all 36 States -->
          <select id="munc-state-filter" aria-label="Select State" onchange="onStateFilterChange(this.value)">
            ${renderStateFilterOptions(ACTIVE_STATE)}
          </select>

          <!-- District Filter -->
          <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
            <option value="">All Districts (${sortedDistricts.length})</option>
            ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
          </select>

          <!-- Year Filter Toggle -->
          <div id="munc-year-wrap" style="display:flex;align-items:center;gap:4px">
            <div class="tab-pills" style="margin:0">
              <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2025'?'on':''}" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
              <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All</button>
            </div>
          </div>

          <!-- Sort -->
          <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
            <option value="seats-desc">Seats: Highest first</option>
            <option value="seats-asc">Seats: Lowest first</option>
            <option value="name-asc">Name: A to Z</option>
            <option value="pop-desc">Population: Largest first</option>
          </select>
        </div>
      </div>'''

# Replace the old bulky toolbar in renderMhLocalHub
code = re.sub(
    r'<!-- Controls & Filter Toolbar -->\s*<div class="card".*?</div>\s*</div>\s*</div>\s*(?=<!-- Main Dynamic Content Container -->)',
    compact_filter_toolbar + '\n\n',
    code,
    flags=re.DOTALL
)

# 2. Add State & Year Selection Layer Gateway before listing items in renderMhLocalHub
state_year_gateway = r'''      <!-- State & Year Selection Layer Gateway -->
      <div class="civic-gateway-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="mycorp-brand-pill" style="background:#ff9933;color:#000">CIVIC GOVERNANCE GATEWAY</span>
              <span class="mycorp-stat-pill">📍 ALL 36 STATES &amp; UNION TERRITORIES</span>
              <span class="mycorp-stat-pill">⚡ CURRENT ACTIVE: ${esc(ACTIVE_STATE)}</span>
            </div>
            <h3 style="margin:2px 0;font-size:17px;color:var(--text)">
              Select State &amp; Election Year
            </h3>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <span style="font-size:12px;color:var(--text-2);font-weight:600">State:</span>
            <select style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:700" onchange="onStateFilterChange(this.value)">
              ${renderStateFilterOptions(ACTIVE_STATE)}
            </select>
          </div>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${ALL_INDIA_STATES.slice(0, 12).map(st => `
            <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11.5px;padding:3px 10px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
              ${st.active ? '📍 ' : ''}${esc(st.name)} ${st.active ? `(${st.corps || st.councils})` : ''}
            </button>
          `).join('')}
          <button class="tab-pill" style="font-size:11.5px;padding:3px 10px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter').focus()">
            + More States (${ALL_INDIA_STATES.length - 12})
          </button>
        </div>
      </div>'''

# Insert the gateway right before Primary Navigation Toolbar in renderMhLocalHub
if '<!-- State & Year Selection Layer Gateway -->' not in code:
    code = code.replace(
        '<!-- Primary Navigation Toolbar: Section Tabs & State Selector -->',
        state_year_gateway + '\n\n      <!-- Primary Navigation Toolbar: Section Tabs & State Selector -->'
    )

# 3. Add cand_helper_js
if 'function renderCandidateLeaderboardHtml' not in code:
    last_brace_idx = code.rfind('})();')
    if last_brace_idx != -1:
        code = code[:last_brace_idx] + cand_helper_js + '\n' + code[last_brace_idx:]

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated js/mh-local-ui.js with state layer and candidate helpers.")
