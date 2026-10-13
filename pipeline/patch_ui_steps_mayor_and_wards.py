import re

with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ══════════════════════════════════════════════════════════════════════
# 1. Update renderMunicipalCorporationsSection with Step Flow
# ══════════════════════════════════════════════════════════════════════
old_corp_sec_start = r'''  // 1. DEDICATED MUNICIPAL CORPORATIONS SECTION
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
      </div>'''

new_corp_sec_start = r'''  // 1. DEDICATED MUNICIPAL CORPORATIONS SECTION (Step 1: Section -> Step 2: State -> Step 3: Year -> Step 4: Results)
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
        <span>Municipal Corporations (Mahanagar Palika)</span>
      </div>

      <!-- Dedicated Corporations Hero Header (Step 1) -->
      <div class="mh-local-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                CIVIC GOVERNANCE
              </span>
              <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                MAHANAGAR PALIKA
              </span>
            </div>
            <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
              🏛️ Municipal Corporations
            </h1>
            <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
              Ward-by-ward election results, corporator rosters, seat reservations, and historical 2017 vs 2026 comparisons across <b>29 Municipal Corporations</b> (2,810 Wards) covering 3.2+ Cr urban voters.
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

      <!-- STEP PROGRESSION GATEWAY: Step 1 (Corporations) ➔ Step 2 (Filter of States) ➔ Step 3 (Filter by Year) ➔ Step 4 (Results) -->
      <div class="civic-step-card">
        <!-- Visual Flow Steps -->
        <div class="civic-step-flow-bar">
          <span class="civic-step-badge">1. Municipal Corporations</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge active">2. Select State: ${esc(ACTIVE_STATE)}</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge active">3. Year: ${ACTIVE_YEAR === 'all' ? 'All' : ACTIVE_YEAR}</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge" style="background:rgba(74,222,128,0.15);border-color:#4ade80;color:#4ade80;font-weight:700">4. Corporation Results</span>
        </div>

        <div class="civic-step-filters-grid">
          <!-- Step 2: State Filter -->
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text);margin-bottom:6px;display:flex;align-items:center;gap:6px">
              <span>📍 Step 2: Filter of States (All 36 States &amp; UTs)</span>
              ${ACTIVE_STATE.toLowerCase() === 'maharashtra' ? '<span class="badge" style="background:#ff9933;color:#000;font-size:10px;padding:1px 6px">Active Data</span>' : ''}
            </div>
            <select id="munc-state-filter" style="width:100%;padding:8px 12px;border-radius:8px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:13px;font-weight:700;margin-bottom:8px" onchange="onStateFilterChange(this.value)">
              ${renderStateFilterOptions(ACTIVE_STATE)}
            </select>
            <div style="display:flex;flex-wrap:wrap;gap:5px">
              ${ALL_INDIA_STATES.slice(0, 8).map(st => `
                <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11px;padding:3px 8px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
                  ${st.active ? '📍 ' : ''}${esc(st.name)}
                </button>
              `).join('')}
              <button class="tab-pill" style="font-size:11px;padding:3px 8px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter') ? document.getElementById('munc-state-filter').focus() : null">
                + All States
              </button>
            </div>
          </div>

          <!-- Step 3: Side-by-Side Year Filter -->
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text);margin-bottom:6px">
              📅 Step 3: Filter by Year
            </div>
            <div class="tab-pills" style="margin:0;display:flex;gap:6px">
              <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('2026')">2026 (Current)</button>
              <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('2017')">2017 (Previous)</button>
              <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('all')">All Years</button>
            </div>
            <div style="font-size:11.5px;color:var(--text-3);margin-top:8px">
              Comparing 2017 baseline vs 2026 election cycle
            </div>
          </div>
        </div>
      </div>'''

if old_corp_sec_start in code:
    code = code.replace(old_corp_sec_start, new_corp_sec_start)
    print("1. Updated renderMunicipalCorporationsSection with Step Flow.")
else:
    print("WARNING: Could not find old_corp_sec_start in js/mh-local-ui.js")

# ══════════════════════════════════════════════════════════════════════
# 2. Update renderMunicipalCouncilsSection with Step Flow
# ══════════════════════════════════════════════════════════════════════
old_council_sec_start = r'''  // 2. DEDICATED MUNICIPAL COUNCILS SECTION
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
            <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">34</div>
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
      </div>'''

new_council_sec_start = r'''  // 2. DEDICATED MUNICIPAL COUNCILS SECTION (Step 1: Section -> Step 2: State -> Step 3: Year -> Step 4: Results)
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
        <span>Municipal Councils (Nagar Parishads)</span>
      </div>

      <!-- Dedicated Councils Hero Header (Step 1) -->
      <div class="mh-local-hero" style="background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(19,136,8,0.10) 100%);border-color:rgba(56,189,248,0.3)">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="badge" style="background:#38bdf8;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                CIVIC GOVERNANCE
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
            <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">34</div>
            <div style="font-size:11.5px;color:var(--text-2)">Spread across all urban Maharashtra</div>
          </div>
        </div>
      </div>

      <!-- STEP PROGRESSION GATEWAY: Step 1 (Councils) ➔ Step 2 (Filter of States) ➔ Step 3 (Filter by Year) ➔ Step 4 (Results) -->
      <div class="civic-step-card councils-card">
        <!-- Visual Flow Steps -->
        <div class="civic-step-flow-bar">
          <span class="civic-step-badge">1. Municipal Councils</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge active-councils">2. Select State: ${esc(ACTIVE_STATE)}</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge active-councils">3. Year: ${ACTIVE_YEAR === 'all' ? 'All' : (ACTIVE_YEAR || '2025')}</span>
          <span class="civic-step-arrow">➔</span>
          <span class="civic-step-badge" style="background:rgba(56,189,248,0.15);border-color:#38bdf8;color:#38bdf8;font-weight:700">4. Council Results</span>
        </div>

        <div class="civic-step-filters-grid">
          <!-- Step 2: State Filter -->
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text);margin-bottom:6px;display:flex;align-items:center;gap:6px">
              <span>📍 Step 2: Filter of States (All 36 States &amp; UTs)</span>
              ${ACTIVE_STATE.toLowerCase() === 'maharashtra' ? '<span class="badge" style="background:#38bdf8;color:#000;font-size:10px;padding:1px 6px">Active Data</span>' : ''}
            </div>
            <select id="munc-state-filter" style="width:100%;padding:8px 12px;border-radius:8px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:13px;font-weight:700;margin-bottom:8px" onchange="onStateFilterChange(this.value)">
              ${renderStateFilterOptions(ACTIVE_STATE)}
            </select>
            <div style="display:flex;flex-wrap:wrap;gap:5px">
              ${ALL_INDIA_STATES.slice(0, 8).map(st => `
                <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11px;padding:3px 8px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
                  ${st.active ? '📍 ' : ''}${esc(st.name)}
                </button>
              `).join('')}
              <button class="tab-pill" style="font-size:11px;padding:3px 8px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter') ? document.getElementById('munc-state-filter').focus() : null">
                + All States
              </button>
            </div>
          </div>

          <!-- Step 3: Side-by-Side Year Filter -->
          <div>
            <div style="font-size:12px;font-weight:700;color:var(--text);margin-bottom:6px">
              📅 Step 3: Filter by Year
            </div>
            <div class="tab-pills" style="margin:0;display:flex;gap:6px">
              <button class="tab-pill on" id="yr-btn-2025" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('2025')">2025 (Current)</button>
              <button class="tab-pill" id="yr-btn-2017" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('2017')">2017 (Previous)</button>
              <button class="tab-pill" id="yr-btn-all" style="padding:8px 16px;font-size:12.5px;font-weight:700" onclick="setMuncYear('all')">All Years</button>
            </div>
            <div style="font-size:11.5px;color:var(--text-3);margin-top:8px">
              Showing 224 Nagar Parishads election results
            </div>
          </div>
        </div>
      </div>'''

if old_council_sec_start in code:
    code = code.replace(old_council_sec_start, new_council_sec_start)
    print("2. Updated renderMunicipalCouncilsSection with Step Flow.")
else:
    print("WARNING: Could not find old_council_sec_start in js/mh-local-ui.js")

# ══════════════════════════════════════════════════════════════════════
# 3. Corporation Ward Matrix & Card Header: Support 1A, 1B, 1C like ward
# ══════════════════════════════════════════════════════════════════════
old_corp_matrix_pills = r'''        <!-- Matrix Pills Grid -->
        <div class="mycorp-matrix-grid">
          ${winners2026.map(w => {
            const pCol = getPartyColor(w.party);
            return `
              <div class="mycorp-ward-pill"
                   id="matrix-pill-${w.ward}"
                   style="border-color:${pCol};background:rgba(15,23,42,0.7)"
                   title="Ward ${w.ward}: ${esc(w.candidate)} (${esc(w.party)}) · Margin: +${fmt(w.margin)}"
                   onclick="jumpToMyCorpWard(${w.ward})">
                ${w.ward}
              </div>
            `;
          }).join('')}
        </div>'''

new_corp_matrix_pills = r'''        <!-- Matrix Pills Grid with 1A, 1B, 1C like ward -->
        <div class="mycorp-matrix-grid">
          ${winners2026.map(w => {
            const pCol = getPartyColor(w.party);
            const wLabel = w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`);
            return `
              <div class="mycorp-ward-pill"
                   id="matrix-pill-${wLabel}"
                   style="border-color:${pCol};background:rgba(15,23,42,0.7)"
                   title="Ward ${wLabel}: ${esc(w.candidate)} (${esc(w.party)}) · Margin: +${fmt(w.margin)}"
                   onclick="jumpToMyCorpWard('${wLabel}')">
                ${wLabel}
              </div>
            `;
          }).join('')}
        </div>'''

if old_corp_matrix_pills in code:
    code = code.replace(old_corp_matrix_pills, new_corp_matrix_pills)
    print("3. Updated Corporation Matrix Pills to show 1A, 1B, 1C.")
else:
    print("WARNING: Could not find old_corp_matrix_pills")

# Also update jumpToMyCorpWard to handle alphanumeric strings (1A, 1B, 2C)
old_jump_corp = r'''  window.jumpToMyCorpWard = function(wardNum) {
    if (!wardNum) return;
    const card = document.getElementById('mycorp-ward-card-' + wardNum);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.outline = '3px solid #ff9933';
      card.style.borderRadius = '12px';
      setTimeout(() => { card.style.outline = ''; }, 2200);
    }
  };'''

new_jump_corp = r'''  window.jumpToMyCorpWard = function(wardNum) {
    if (!wardNum) return;
    const wStr = String(wardNum).trim().toLowerCase();
    const card = document.getElementById('mycorp-ward-card-' + wStr) ||
                 document.getElementById('mycorp-ward-card-' + wStr.toUpperCase()) ||
                 document.getElementById('mycorp-ward-card-' + parseInt(wStr));
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.outline = '3px solid #ff9933';
      card.style.borderRadius = '12px';
      setTimeout(() => { card.style.outline = ''; }, 2200);
    }
  };'''

if old_jump_corp in code:
    code = code.replace(old_jump_corp, new_jump_corp)
    print("4. Updated jumpToMyCorpWard to support 1A, 1B, 1C strings.")
else:
    print("WARNING: Could not find old_jump_corp")

# Update Ward Card ID and Header in renderMyCorpWardCardsHtml
old_ward_card_header = r'''          return `
            <div class="mycorp-ward-card" id="mycorp-ward-card-${w.ward}" style="--card-accent:${pColor}">
              <div>
                <!-- Card Header -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="font-size:16px;font-weight:800;color:var(--text)">
                      Ward No. ${w.ward}
                    </span>
                    ${w.res ? `
                      <span class="badge" style="background:var(--s2);color:var(--text-2);font-size:11px;padding:2px 7px;border-radius:4px">
                        ${esc(w.res)}
                      </span>
                    ` : ''}
                  </div>'''

new_ward_card_header = r'''          const wLabel = w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`);
          return `
            <div class="mycorp-ward-card" id="mycorp-ward-card-${wLabel.toLowerCase()}" style="--card-accent:${pColor}">
              <div>
                <!-- Card Header with 1A, 1B, 1C like ward -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                    <span style="font-size:16px;font-weight:800;color:var(--text)">
                      Ward ${wLabel} ${w.seat ? `· Seat ${w.seat}` : ''}
                    </span>
                    ${w.res ? `
                      <span class="badge" style="background:var(--s2);color:var(--text-2);font-size:11px;padding:2px 7px;border-radius:4px">
                        ${esc(w.res)}
                      </span>
                    ` : ''}
                  </div>'''

if old_ward_card_header in code:
    code = code.replace(old_ward_card_header, new_ward_card_header)
    print("5. Updated Corporation Ward Card Header with 1A, 1B, 1C.")
else:
    print("WARNING: Could not find old_ward_card_header")

# Also update search filter in Corporation wards to match 1a, 1b, etc.
old_corp_filter_logic = r'''      if (q) {
        const matchWard = String(w.ward) === q || ('ward ' + w.ward).includes(q);
        const matchCand = (w.candidate || '').toLowerCase().includes(q);'''

new_corp_filter_logic = r'''      if (q) {
        const wLbl = (w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`)).toLowerCase();
        const matchWard = String(w.ward) === q || ('ward ' + w.ward).includes(q) || wLbl === q || ('ward ' + wLbl).includes(q);
        const matchCand = (w.candidate || '').toLowerCase().includes(q);'''

if old_corp_filter_logic in code:
    code = code.replace(old_corp_filter_logic, new_corp_filter_logic)
    print("6. Updated Corporation ward search filter for 1A, 1B.")
else:
    print("WARNING: Could not find old_corp_filter_logic")

# Also update Council ward search filter for 1a, 1b, etc.
old_council_filter_logic = r'''        const matchWard = String(w.ward) === q || `${w.ward}${w.seat}`.toLowerCase().includes(q);'''
new_council_filter_logic = r'''        const wLbl = (w.ward_label || `${w.ward}${w.seat || ''}`).toLowerCase();
        const matchWard = String(w.ward) === q || wLbl === q || wLbl.includes(q) || ('ward ' + wLbl).includes(q);'''

if old_council_filter_logic in code:
    code = code.replace(old_council_filter_logic, new_council_filter_logic)
    print("7. Updated Council ward search filter for 1A, 1B.")
else:
    print("WARNING: Could not find old_council_filter_logic")

# Update Council Ward Card Header to clearly show Ward 1A, 1B, etc.
old_council_card_head = r'''              <div class="mycorp-card-head">
                <span class="mycorp-ward-badge">
                  Ward ${w.ward}${w.seat ? ' · Seat ' + w.seat : ''}
                </span>'''

new_council_card_head = r'''              const wLabel = w.ward_label || `${w.ward}${w.seat || ''}`;
              return `
            <div class="mycorp-ward-card" id="mycouncil-ward-card-${wLabel.toLowerCase()}" style="--card-accent:${pColor}">
              <!-- Card Header -->
              <div class="mycorp-card-head">
                <span class="mycorp-ward-badge">
                  Ward ${wLabel} ${w.seat ? '· Seat ' + w.seat : ''}
                </span>'''

# Let's check how Council card head starts in renderMyCouncilWardsGridHtml
counc_card_match = re.search(r'return `\s*<div class="mycorp-ward-card"[^>]*>\s*<!-- Card Header -->\s*<div class="mycorp-card-head">\s*<span class="mycorp-ward-badge">\s*Ward \$\{w\.ward\}\$\{w\.seat \? \' · Seat \' \+ w\.seat : \'\'\}', code)
if counc_card_match:
    target_str = counc_card_match.group(0)
    repl_str = r'''const wLabel = w.ward_label || `${w.ward}${w.seat || ''}`;
          return `
            <div class="mycorp-ward-card" id="mycouncil-ward-card-${wLabel.toLowerCase()}" style="--card-accent:${pColor}">
              <!-- Card Header -->
              <div class="mycorp-card-head">
                <span class="mycorp-ward-badge">
                  Ward ${wLabel} ${w.seat ? '· Seat ' + w.seat : ''}</span>'''
    code = code.replace(target_str, repl_str)
    print("8. Updated Council Ward Card Header to show Ward 1A, 1B, etc.")
else:
    print("Notice: check Council card head regex match")

# ══════════════════════════════════════════════════════════════════════
# 4. Add Mayor & Executive Governance Insight to Corporation Detail Page
# ══════════════════════════════════════════════════════════════════════
old_corp_metrics_block = r'''        <!-- High Level Civic Metrics Cards -->
        <div class="g g4" style="margin-top:18px;gap:10px">'''

new_corp_metrics_and_insight = r'''        <!-- High Level Civic Metrics Cards -->
        <div class="g g4" style="margin-top:18px;gap:10px">'''

# Let's insert the Mayor Insight card right below the Majority Visual Bar in renderCorporationDetailPage
old_corp_tabs_block = r'''      <!-- Navigation Tabs (Matching mycorporator.in) -->
      <div class="tab-pills" style="margin-bottom:18px">'''

new_corp_tabs_and_insight = r'''      <!-- Office of the Mayor & Executive Governance Insight -->
      <div class="civic-insight-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:10.5px;padding:2px 8px;border-radius:4px">CIVIC INSIGHT</span>
              <span class="badge" style="background:rgba(255,255,255,0.1);color:var(--text);font-size:10.5px;padding:2px 8px;border-radius:4px">MAYORAL GOVERNANCE</span>
            </div>
            <h3 style="margin:2px 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
              👑 Office of the Mayor (Mahapour) – ${esc(corp.name)}
            </h3>
            <p style="margin:0;font-size:13px;color:var(--text-2);max-width:850px;line-height:1.5">
              The Mayor is the <b>First Citizen</b> of the city and presiding officer of the Corporation General Body. Elected indirectly by the <b>${fmt(seatCount)} Corporators</b> for a 2.5-year term under the Maharashtra Municipal Corporations Act.
            </p>
          </div>
        </div>
        <div class="g g3" style="margin-top:14px;gap:10px">
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">RULING PARTY / COALITION</div>
            <div style="font-size:16px;font-weight:800;color:${getPartyColor(leadingParty)};margin:3px 0">${esc(leadingParty)} (${top2026[0] ? top2026[0][1] : 0} Seats)</div>
            <div style="font-size:11px;color:var(--text-2)">${(top2026[0] && top2026[0][1] >= majMark) ? 'Clear Majority to elect Mayor' : 'Coalition required for majority mark of ' + majMark}</div>
          </div>
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">EXECUTIVE APPARATUS</div>
            <div style="font-size:14.5px;font-weight:800;color:var(--text);margin:3px 0">Municipal Commissioner (IAS)</div>
            <div style="font-size:11px;color:var(--text-2)">Vested with administrative powers &amp; policy implementation</div>
          </div>
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">STATUTORY APEX BODY</div>
            <div style="font-size:14.5px;font-weight:800;color:#38bdf8;margin:3px 0">Standing Committee (Sthayi Samiti)</div>
            <div style="font-size:11px;color:var(--text-2)">Financial sanctioning &amp; municipal budget approval power</div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs (Matching mycorporator.in) -->
      <div class="tab-pills" style="margin-bottom:18px">'''

if old_corp_tabs_block in code:
    code = code.replace(old_corp_tabs_block, new_corp_tabs_and_insight)
    print("9. Added Mayor Insight to Corporation detail view.")
else:
    print("WARNING: Could not find old_corp_tabs_block")

# ══════════════════════════════════════════════════════════════════════
# 5. Add President Governance Insight and ALL Candidate Results to Council President View
# ══════════════════════════════════════════════════════════════════════
old_pres_view = r'''  // 2: Nagaradhyaksha President View
  function renderMyCouncilPresidentView(container) {
    const council = MYCOUNCIL_STATE.council;
    const pres = council.president;

    if (!pres) {
      container.innerHTML = `<div class="card note" style="padding:40px;text-align:center">Nagaradhyaksha President record not found for ${esc(council.name)}.</div>`;
      return;
    }

    const pColor = getPartyColor(pres.party);

    container.innerHTML = `
      <div class="card" style="border:1px solid rgba(255,153,51,0.4);background:linear-gradient(135deg, rgba(255,153,51,0.12) 0%, rgba(15,23,42,0.92) 100%);border-radius:14px;padding:24px;margin-bottom:20px;box-shadow:0 12px 36px rgba(0,0,0,0.4)">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
          <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 10px;border-radius:4px">
            👑 DIRECTLY ELECTED BY CITIZENS
          </span>
          <span class="badge" style="background:var(--s2);color:var(--text);font-size:11px;padding:3px 10px;border-radius:4px">
            ${esc(council.name)} NAGAR PARISHAD
          </span>
        </div>

        <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;margin:14px 0">
          <div class="mycorp-avatar" style="width:72px;height:72px;font-size:28px;background:${pColor}">
            ${(pres.candidate || 'P').charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 style="margin:0 0 6px;font-size:24px;color:var(--text)">
              ${esc(pres.candidate)}
            </h2>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
              <span class="tag" style="background:var(--s2);border-left:4px solid ${pColor};font-size:13px;padding:3px 10px;font-weight:700">
                ${esc(pres.party)}
              </span>
              <span style="font-size:13px;color:var(--text-2)">
                Official Affiliation: <b>${esc(pres.raw_party || pres.party)}</b>
              </span>
            </div>
          </div>
        </div>

        <div class="g g3" style="gap:12px;margin-top:20px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">TOTAL VOTES POLLED</div>
            <div style="font-size:24px;font-weight:800;color:#ff9933;margin:3px 0">${fmt(pres.votes)}</div>
            <div style="font-size:11px;color:var(--text-2)">Direct city-wide mandate</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">VOTE SHARE PERCENTAGE</div>
            <div style="font-size:24px;font-weight:800;color:#4ade80;margin:3px 0">${pres.pct ? pres.pct.toFixed(2) + '%' : '–'}</div>
            <div style="font-size:11px;color:var(--text-2)">Of total valid presidential votes</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">ELECTORAL JURISDICTION</div>
            <div style="font-size:20px;font-weight:800;color:#38bdf8;margin:3px 0">${esc(council.district || 'Maharashtra')}</div>
            <div style="font-size:11px;color:var(--text-2)">State Election Commission Certified</div>
          </div>
        </div>
      </div>
    `;
  }'''

new_pres_view = r'''  // 2: Nagaradhyaksha President View (Complete Candidates Roster + Governance Insight)
  function renderMyCouncilPresidentView(container) {
    const council = MYCOUNCIL_STATE.council;
    const pres = council.president;

    if (!pres) {
      container.innerHTML = `<div class="card note" style="padding:40px;text-align:center">Nagaradhyaksha President record not found for ${esc(council.name)}.</div>`;
      return;
    }

    const pColor = getPartyColor(pres.party);
    const presCands = pres.cands || [
      [pres.candidate, pres.party, pres.votes, pres.pct]
    ];
    const totalPresVotes = presCands.reduce((acc, c) => acc + (c[2] || 0), 0);

    container.innerHTML = `
      <!-- Nagaradhyaksha Governance Insight Card -->
      <div class="civic-insight-card council-insight">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="badge" style="background:#38bdf8;color:#000;font-weight:800;font-size:10.5px;padding:2px 8px;border-radius:4px">CIVIC INSIGHT</span>
              <span class="badge" style="background:rgba(255,255,255,0.1);color:var(--text);font-size:10.5px;padding:2px 8px;border-radius:4px">DIRECT PRESIDENTIAL MANDATE</span>
            </div>
            <h3 style="margin:2px 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
              👑 Office of the Nagaradhyaksha (Council President) – ${esc(council.name)}
            </h3>
            <p style="margin:0;font-size:13px;color:var(--text-2);max-width:850px;line-height:1.5">
              Unlike municipal corporations, Nagar Parishad Presidents are <b>directly elected by all registered voters</b> of the town. The Nagaradhyaksha exercises executive authority over council administration and policy resolutions under the Maharashtra Municipal Councils Act.
            </p>
          </div>
        </div>
        <div class="g g3" style="margin-top:14px;gap:10px">
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">ELECTORAL MANDATE</div>
            <div style="font-size:16px;font-weight:800;color:#ff9933;margin:3px 0">Direct Popular Vote</div>
            <div style="font-size:11px;color:var(--text-2)">Voted by all citizens across all wards simultaneously</div>
          </div>
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">CHIEF EXECUTIVE OFFICER</div>
            <div style="font-size:14.5px;font-weight:800;color:var(--text);margin:3px 0">Mukhya Adhikari (Chief Officer)</div>
            <div style="font-size:11px;color:var(--text-2)">State municipal cadre officer managing civic staff</div>
          </div>
          <div style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:10px 14px">
            <div style="font-size:11px;color:var(--text-3);text-transform:uppercase;font-weight:700">COUNCIL STRENGTH</div>
            <div style="font-size:14.5px;font-weight:800;color:#4ade80;margin:3px 0">${council.seat_count || (council.winners || []).length} Councillor Seats</div>
            <div style="font-size:11px;color:var(--text-2)">Legislative council members across all prabhags</div>
          </div>
        </div>
      </div>

      <!-- Elected President Winner Banner -->
      <div class="card" style="border:1px solid rgba(56,189,248,0.4);background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 100%);border-radius:14px;padding:22px;margin-bottom:20px;box-shadow:0 12px 36px rgba(0,0,0,0.4)">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
          <span class="badge" style="background:#4ade80;color:#000;font-weight:800;font-size:11px;padding:3px 10px;border-radius:4px">
            🏆 ELECTED NAGARADHYAKSHA (WINNER)
          </span>
          <span class="badge" style="background:var(--s2);color:var(--text);font-size:11px;padding:3px 10px;border-radius:4px">
            ${esc(council.name)} NAGAR PARISHAD
          </span>
          ${pres.margin ? `
            <span class="badge" style="background:rgba(56,189,248,0.2);color:#38bdf8;font-weight:700;font-size:11px;padding:3px 8px;border-radius:4px">
              Margin: +${fmt(pres.margin)} Votes
            </span>
          ` : ''}
        </div>

        <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin:14px 0">
          <div class="mycorp-avatar" style="width:68px;height:68px;font-size:26px;background:${pColor}">
            ${(pres.candidate || 'P').charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 style="margin:0 0 6px;font-size:24px;color:var(--text)">
              ${esc(pres.candidate)}
            </h2>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
              <span class="tag" style="background:var(--s2);border-left:4px solid ${pColor};font-size:13px;padding:3px 10px;font-weight:700">
                ${esc(pres.party)}
              </span>
              <span style="font-size:13px;color:var(--text-2)">
                Votes Polled: <b>${fmt(pres.votes)}</b> (${pres.pct ? pres.pct.toFixed(2) + '%' : '–'})
              </span>
            </div>
          </div>
        </div>

        <!-- Metric Badges -->
        <div class="g g4" style="gap:10px;margin-top:16px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:12px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">WINNER VOTES</div>
            <div style="font-size:22px;font-weight:800;color:#ff9933;margin:2px 0">${fmt(pres.votes)}</div>
            <div style="font-size:10.5px;color:var(--text-3)">${pres.pct ? pres.pct.toFixed(1) + '% vote share' : 'Highest Polled'}</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:12px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">RUNNER-UP VOTES</div>
            <div style="font-size:22px;font-weight:800;color:#38bdf8;margin:2px 0">${fmt(pres.runner_votes || (presCands[1] ? presCands[1][2] : 0))}</div>
            <div style="font-size:10.5px;color:var(--text-3)">${pres.runner ? esc(pres.runner) : (presCands[1] ? esc(presCands[1][0]) : '–')}</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:12px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">VICTORY MARGIN</div>
            <div style="font-size:22px;font-weight:800;color:#4ade80;margin:2px 0">+${fmt(pres.margin || (pres.votes - (presCands[1] ? presCands[1][2] : 0)))}</div>
            <div style="font-size:10.5px;color:var(--text-3)">Decisive popular lead</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:8px;padding:12px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">TOTAL PRESIDENTIAL VOTES</div>
            <div style="font-size:22px;font-weight:800;color:#facc15;margin:2px 0">${fmt(totalPresVotes)}</div>
            <div style="font-size:10.5px;color:var(--text-3)">Across ${presCands.length} candidates</div>
          </div>
        </div>
      </div>

      <!-- ALL CANDIDATES PRESIDENTIAL ELECTION RESULTS TABLE -->
      <div class="card" style="background:var(--s1);border:1px solid var(--b);border-radius:12px;padding:20px;margin-bottom:20px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
          <div>
            <h3 style="margin:0 0 4px;font-size:17px;color:var(--text)">
              📊 Complete Presidential Election Results – All Candidates Polled
            </h3>
            <p class="note" style="margin:0">
              Certified vote tallies and share percentages for all candidates who contested for Nagaradhyaksha in ${esc(council.name)}.
            </p>
          </div>
          <span class="badge" style="background:var(--s2);color:#38bdf8;font-size:12px;padding:4px 10px;font-weight:700">
            ${presCands.length} Candidates Contested
          </span>
        </div>

        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:70px">Rank</th>
                <th>Candidate Name</th>
                <th>Political Party</th>
                <th style="text-align:right">Votes Polled</th>
                <th style="text-align:right">Vote Share %</th>
                <th style="text-align:center">Result Status</th>
              </tr>
            </thead>
            <tbody>
              ${presCands.map((c, i) => {
                const isWinner = (i === 0);
                const rankBadge = isWinner ? '🥇 1st' : (i === 1 ? '🥈 2nd' : (i === 2 ? '🥉 3rd' : (i + 1) + 'th'));
                const pColorRow = getPartyColor(c[1]);
                const cVotes = c[2] || 0;
                const cPct = c[3] ? c[3].toFixed(2) + '%' : (totalPresVotes > 0 ? ((cVotes/totalPresVotes)*100).toFixed(2) + '%' : '–');

                return `
                  <tr style="${isWinner ? 'background:rgba(74,222,128,0.06);font-weight:600' : ''}">
                    <td><span style="font-weight:800;color:${isWinner ? '#4ade80' : 'var(--text)'}">${rankBadge}</span></td>
                    <td>
                      <b style="font-size:13.5px;color:var(--text)">${esc(c[0])}</b>
                      ${isWinner ? '<span class="badge" style="margin-left:6px;background:#4ade80;color:#000;font-size:10px;padding:1px 6px;font-weight:800">ELECTED</span>' : ''}
                    </td>
                    <td>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${pColorRow};font-size:11.5px;font-weight:600">
                        ${esc(c[1])}
                      </span>
                    </td>
                    <td style="text-align:right;font-weight:700;font-size:14px;color:${isWinner ? '#4ade80' : 'var(--text)'}">
                      ${fmt(cVotes)}
                    </td>
                    <td style="text-align:right;font-size:13px;color:var(--text-2)">
                      ${cPct}
                    </td>
                    <td style="text-align:center">
                      <span class="badge" style="${isWinner ? 'background:rgba(74,222,128,0.2);color:#4ade80;font-weight:700' : 'background:rgba(255,255,255,0.06);color:var(--text-3)'}">
                        ${isWinner ? 'Nagaradhyaksha' : (i === 1 ? 'Runner-Up' : 'Contested')}
                      </span>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }'''

if old_pres_view in code:
    code = code.replace(old_pres_view, new_pres_view)
    print("10. Updated renderMyCouncilPresidentView with complete candidates roster & governance insight.")
else:
    print("WARNING: Could not find old_pres_view in js/mh-local-ui.js")

# Write updated code
with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated js/mh-local-ui.js successfully.")
