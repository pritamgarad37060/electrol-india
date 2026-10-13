import re

# Read js/mh-local-ui.js
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

# Let's inspect where renderMunicipalCorporationsSection and renderMunicipalCouncilsSection are defined
corp_sec_def = r'''  window.renderMunicipalCorporationsSection = function(stateParam, yearParam) {
    ACTIVE_SECTION = 'corps';
    if (stateParam) ACTIVE_STATE = stateParam;
    if (yearParam) ACTIVE_YEAR = yearParam;
    return window.renderMhLocalHub('corps');
  };

  window.renderMunicipalCouncilsSection = function(stateParam, yearParam) {
    ACTIVE_SECTION = 'councils';
    if (stateParam) ACTIVE_STATE = stateParam;
    if (yearParam) ACTIVE_YEAR = yearParam;
    return window.renderMhLocalHub('councils');
  };'''

new_corp_and_council_secs = r'''  // ═══════════════════════════════════════════════════════════════
  // SEPARATED DEDICATED SECTIONS: Municipal Corporations vs Councils
  // ═══════════════════════════════════════════════════════════════

  // 1. DEDICATED MUNICIPAL CORPORATIONS SECTION
  window.renderMunicipalCorporationsSection = function(stateParam, yearParam) {
    ACTIVE_SECTION = 'corps';
    if (stateParam) ACTIVE_STATE = stateParam;
    if (yearParam) ACTIVE_YEAR = yearParam;

    const corps = window.MH_CORPS || [];
    const distSet = new Set();
    corps.forEach(c => c.district && distSet.add(c.district));
    const sortedDistricts = Array.from(distSet).sort();

    setTimeout(() => {
      initListeners();
      renderActiveView();
    }, 15);

    return `
      <!-- Breadcrumb -->
      <div class="bc">
        <a onclick="go('')">Home</a> <span>›</span>
        <a onclick="go('mh')">Maharashtra</a> <span>›</span>
        <span>Municipal Corporations (Mahanagar Palika)</span>
      </div>

      <!-- Dedicated Corporations Hero Header -->
      <div class="mh-local-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                URBAN GOVERNANCE
              </span>
              <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                MAHANAGAR PALIKA
              </span>
            </div>
            <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
              🏛️ Municipal Corporations
            </h1>
            <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
              Ward-by-ward election results, seat reservations, and historical 2017 vs 2026 comparisons across <b>29 Municipal Corporations</b> (2,810 Wards) covering 3.2+ Cr urban voters.
            </p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn on" onclick="go('councils')">🏢 Municipal Councils (224) →</button>
            <button class="btn" onclick="go('mh')">🏢 MH Assembly (288 AC) →</button>
          </div>
        </div>

        <!-- Metrics Cards -->
        <div class="g g4" style="margin-top:20px;gap:12px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL CORPORATIONS</div>
            <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">29</div>
            <div style="font-size:11.5px;color:var(--text-2)">BMC, Pune, Thane, Nagpur, PCMC, etc.</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">ELECTORAL WARDS &amp; SEATS</div>
            <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">2,810</div>
            <div style="font-size:11.5px;color:var(--text-2)">Ward-by-ward candidate tallies &amp; reservations</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">HISTORICAL COMPARISON</div>
            <div style="font-size:26px;font-weight:800;color:#4ade80;margin:4px 0">2017 vs 2026</div>
            <div style="font-size:11.5px;color:var(--text-2)">Track seat gains, swings &amp; party shifts</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">URBAN POPULATION</div>
            <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">3.2+ Cr</div>
            <div style="font-size:11.5px;color:var(--text-2)">Total voters in Maharashtra Corporations</div>
          </div>
        </div>
      </div>

      <!-- LAYER OF SELECTING STATES AND YEAR (BEFORE GETTING MAHARASHTRA DATA) -->
      <div class="civic-gateway-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="mycorp-brand-pill" style="background:#ff9933;color:#000">STATE &amp; YEAR SELECTOR</span>
              <span class="mycorp-stat-pill">📍 ALL 36 STATES &amp; UNION TERRITORIES</span>
              <span class="mycorp-stat-pill">⚡ CURRENT: ${esc(ACTIVE_STATE)}</span>
            </div>
            <h3 style="margin:2px 0;font-size:17px;color:var(--text)">
              Select State &amp; Election Year
            </h3>
          </div>
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">State:</span>
              <select id="munc-state-filter" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:700" onchange="onStateFilterChange(this.value)">
                ${renderStateFilterOptions(ACTIVE_STATE)}
              </select>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
              <div class="tab-pills" style="margin:0">
                <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
                <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
                <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
              </div>
            </div>
          </div>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${ALL_INDIA_STATES.slice(0, 10).map(st => `
            <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11.5px;padding:3px 10px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
              ${st.active ? '📍 ' : ''}${esc(st.name)} ${st.active ? `(${st.corps})` : ''}
            </button>
          `).join('')}
          <button class="tab-pill" style="font-size:11.5px;padding:3px 10px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter') ? document.getElementById('munc-state-filter').focus() : null">
            + All States (${ALL_INDIA_STATES.length})
          </button>
        </div>
      </div>

      <!-- Featured BMC myCorporator Banner (For Maharashtra) -->
      ${(ACTIVE_STATE.toLowerCase() === 'maharashtra') ? `
        <div class="card" style="margin:0 0 16px;background:linear-gradient(135deg, rgba(255,107,0,0.14) 0%, rgba(15,23,42,0.92) 100%);border:1px solid rgba(255,153,51,0.45);border-radius:14px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 10px 30px rgba(0,0,0,0.45)">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="mycorp-brand-pill">FEATURED CIVIC HUB</span>
              <span class="mycorp-stat-pill">227 WARDS · 114 MAJORITY MARK</span>
              <span class="mycorp-stat-pill">₹65,000+ CR BUDGET</span>
            </div>
            <h2 style="margin:2px 0 4px;font-size:19px;color:var(--text);display:flex;align-items:center;gap:8px">
              🏛️ Brihanmumbai Municipal Corporation (BMC) — myCorporator Portal
            </h2>
            <p style="margin:0;font-size:13px;color:var(--text-2);max-width:760px;line-height:1.45">
              Explore complete ward-wise election results (Ward 1 to 227), corporator directory, vote shares, and victory margins.
            </p>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap">
            <button class="btn on" style="padding:9px 18px;font-size:13px;font-weight:700;background:linear-gradient(90deg, #ff9933, #ff6b00);color:#000;border:none;box-shadow:0 4px 16px rgba(255,107,0,0.45);cursor:pointer" onclick="go('corp/bmc')">
              Open BMC Portal (227 Wards) →
            </button>
          </div>
        </div>
      ` : ''}

      <!-- Compact Sleek Filter Toolbar (NO Big White Search Bar) -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Search corporation, district, ward..." aria-label="Search Corporations" oninput="renderActiveView()">
        </div>

        <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
          <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
          ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
        </select>

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
          <option value="pop-desc">Population: Largest first</option>
        </select>
      </div>

      <!-- Main Dynamic Corporations Content -->
      <div id="munc-content-area">
        <p class="note">Loading municipal corporations…</p>
      </div>

      <div id="munc-modal-wrap" style="display:none"></div>
    `;
  };

  // 2. DEDICATED MUNICIPAL COUNCILS SECTION
  window.renderMunicipalCouncilsSection = function(stateParam, yearParam) {
    ACTIVE_SECTION = 'councils';
    if (stateParam) ACTIVE_STATE = stateParam;
    if (yearParam) ACTIVE_YEAR = yearParam;

    const councils = window.MH_COUNCILS || [];
    const distSet = new Set();
    councils.forEach(c => c.district && distSet.add(c.district));
    const sortedDistricts = Array.from(distSet).sort();

    setTimeout(() => {
      initListeners();
      renderActiveView();
    }, 15);

    return `
      <!-- Breadcrumb -->
      <div class="bc">
        <a onclick="go('')">Home</a> <span>›</span>
        <a onclick="go('mh')">Maharashtra</a> <span>›</span>
        <span>Municipal Councils (Nagar Parishads)</span>
      </div>

      <!-- Dedicated Councils Hero Header -->
      <div class="mh-local-hero" style="background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(19,136,8,0.10) 100%);border-color:rgba(56,189,248,0.3)">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="badge" style="background:#38bdf8;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                URBAN GOVERNANCE
              </span>
              <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                NAGAR PARISHADS
              </span>
            </div>
            <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
              🏢 Municipal Councils
            </h1>
            <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
              Ward-wise councillor election results, directly-elected Nagaradhyaksha Presidents, and complete party seat tallies across <b>224 Municipal Councils</b> (5,389 Councillor Seats).
            </p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn on" onclick="go('corporations')">🏛️ Municipal Corporations (29) →</button>
            <button class="btn" onclick="go('mh')">🏢 MH Assembly (288 AC) →</button>
          </div>
        </div>

        <!-- Metrics Cards -->
        <div class="g g4" style="margin-top:20px;gap:12px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL COUNCILS</div>
            <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">224</div>
            <div style="font-size:11.5px;color:var(--text-2)">Akluj, Ambarnath, Barshi, Beed, etc.</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">COUNCILLOR SEATS</div>
            <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">5,389</div>
            <div style="font-size:11.5px;color:var(--text-2)">Ward-by-ward candidate tallies &amp; votes</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">COUNCIL PRESIDENTS</div>
            <div style="font-size:26px;font-weight:800;color:#4ade80;margin:4px 0">224</div>
            <div style="font-size:11.5px;color:var(--text-2)">Directly elected Nagaradhyakshas</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">DISTRICTS COVERED</div>
            <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">${sortedDistricts.length}</div>
            <div style="font-size:11.5px;color:var(--text-2)">Spread across all urban Maharashtra</div>
          </div>
        </div>
      </div>

      <!-- LAYER OF SELECTING STATES AND YEAR (BEFORE GETTING MAHARASHTRA DATA) -->
      <div class="civic-gateway-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="mycorp-brand-pill" style="background:#38bdf8;color:#000">STATE &amp; YEAR SELECTOR</span>
              <span class="mycorp-stat-pill">📍 ALL 36 STATES &amp; UNION TERRITORIES</span>
              <span class="mycorp-stat-pill">⚡ CURRENT: ${esc(ACTIVE_STATE)}</span>
            </div>
            <h3 style="margin:2px 0;font-size:17px;color:var(--text)">
              Select State &amp; Election Year
            </h3>
          </div>
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">State:</span>
              <select id="munc-state-filter" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:700" onchange="onStateFilterChange(this.value)">
                ${renderStateFilterOptions(ACTIVE_STATE)}
              </select>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
              <div class="tab-pills" style="margin:0">
                <button class="tab-pill on" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
                <button class="tab-pill" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
                <button class="tab-pill" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
              </div>
            </div>
          </div>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${ALL_INDIA_STATES.slice(0, 10).map(st => `
            <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11.5px;padding:3px 10px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
              ${st.active ? '📍 ' : ''}${esc(st.name)} ${st.active ? `(${st.councils})` : ''}
            </button>
          `).join('')}
          <button class="tab-pill" style="font-size:11.5px;padding:3px 10px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter') ? document.getElementById('munc-state-filter').focus() : null">
            + All States (${ALL_INDIA_STATES.length})
          </button>
        </div>
      </div>

      <!-- Compact Sleek Filter Toolbar (NO Big White Search Bar) -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Search council, district, president..." aria-label="Search Councils" oninput="renderActiveView()">
        </div>

        <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
          <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
          ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
        </select>

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
        </select>
      </div>

      <!-- Main Dynamic Councils Content -->
      <div id="munc-content-area">
        <p class="note">Loading municipal councils…</p>
      </div>

      <div id="munc-modal-wrap" style="display:none"></div>
    `;
  };'''

if corp_sec_def in js_code:
    js_code = js_code.replace(corp_sec_def, new_corp_and_council_secs)
    print("Replaced renderMunicipalCorporationsSection and renderMunicipalCouncilsSection successfully.")
else:
    print("WARNING: Could not find corp_sec_def in js/mh-local-ui.js")

# Also update renderMhLocalHub fallback to use the clean compact toolbar instead of .filter-bar-grid
old_munc_filter_grid = r'''      <!-- Controls & Filter Toolbar -->
      <div class="card" style="padding:14px;margin-bottom:18px;background:var(--s1);border:1px solid var(--b);border-radius:10px">
        <div class="filter-bar-grid">
          <input id="munc-search" placeholder="Search corporation, council, ward, or candidate…" aria-label="Search Municipal" oninput="renderActiveView()">

          <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
            <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
            ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
          </select>

          <!-- Year Filter Toggle -->
          <div id="munc-year-wrap" style="display:flex;align-items:center;gap:6px">
            <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
            <div class="tab-pills" style="margin:0">
              <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2025'?'on':''}" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
              <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
            </div>
          </div>

          <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
            <option value="seats-desc">Seats: Highest first</option>
            <option value="seats-asc">Seats: Lowest first</option>
            <option value="name-asc">Name: A to Z</option>
            <option value="pop-desc">Population: Largest first</option>
          </select>
        </div>
      </div>'''

new_munc_filter_grid = r'''      <!-- Controls & Filter Toolbar (Compact Sleek Design) -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Search corporation, council, or ward..." aria-label="Search Municipal" oninput="renderActiveView()">
        </div>

        <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
          <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
          ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
        </select>

        <!-- Year Filter Toggle -->
        <div id="munc-year-wrap" style="display:flex;align-items:center;gap:6px">
          <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
          <div class="tab-pills" style="margin:0">
            <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
            <button class="tab-pill ${ACTIVE_YEAR==='2025'?'on':''}" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
            <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
            <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
          </div>
        </div>

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
          <option value="pop-desc">Population: Largest first</option>
        </select>
      </div>'''

if old_munc_filter_grid in js_code:
    js_code = js_code.replace(old_munc_filter_grid, new_munc_filter_grid)
    print("Replaced old_munc_filter_grid in renderMhLocalHub successfully.")

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

print("Saved js/mh-local-ui.js successfully.")
