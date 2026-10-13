import re

# We will read js/mh-local-ui.js and replace the relevant parts cleanly.
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Ensure ALL_INDIA_STATES is defined in js/mh-local-ui.js
states_def = '''  // All 36 States & Union Territories of India for Civic Governance Filter
  const ALL_INDIA_STATES = [
    { name: 'Maharashtra', corps: 29, councils: 224, active: true },
    { name: 'Andhra Pradesh', corps: 17, councils: 75, active: false },
    { name: 'Arunachal Pradesh', corps: 2, councils: 0, active: false },
    { name: 'Assam', corps: 2, councils: 80, active: false },
    { name: 'Bihar', corps: 19, councils: 88, active: false },
    { name: 'Chhattisgarh', corps: 14, councils: 44, active: false },
    { name: 'Goa', corps: 1, councils: 13, active: false },
    { name: 'Gujarat', corps: 8, councils: 156, active: false },
    { name: 'Haryana', corps: 11, councils: 23, active: false },
    { name: 'Himachal Pradesh', corps: 5, councils: 29, active: false },
    { name: 'Jharkhand', corps: 9, councils: 20, active: false },
    { name: 'Karnataka', corps: 11, councils: 118, active: false },
    { name: 'Kerala', corps: 6, councils: 87, active: false },
    { name: 'Madhya Pradesh', corps: 16, councils: 98, active: false },
    { name: 'Manipur', corps: 1, councils: 27, active: false },
    { name: 'Meghalaya', corps: 0, councils: 6, active: false },
    { name: 'Mizoram', corps: 1, councils: 0, active: false },
    { name: 'Nagaland', corps: 0, councils: 39, active: false },
    { name: 'Odisha', corps: 5, councils: 48, active: false },
    { name: 'Punjab', corps: 13, councils: 73, active: false },
    { name: 'Rajasthan', corps: 10, councils: 34, active: false },
    { name: 'Sikkim', corps: 1, councils: 4, active: false },
    { name: 'Tamil Nadu', corps: 25, councils: 121, active: false },
    { name: 'Telangana', corps: 13, councils: 128, active: false },
    { name: 'Tripura', corps: 1, councils: 13, active: false },
    { name: 'Uttar Pradesh', corps: 17, councils: 200, active: false },
    { name: 'Uttarakhand', corps: 9, councils: 41, active: false },
    { name: 'West Bengal', corps: 7, councils: 119, active: false },
    { name: 'Andaman and Nicobar Islands', corps: 1, councils: 0, active: false },
    { name: 'Chandigarh', corps: 1, councils: 0, active: false },
    { name: 'Dadra and Nagar Haveli and Daman and Diu', corps: 0, councils: 3, active: false },
    { name: 'Delhi (NCT)', corps: 1, councils: 0, active: false },
    { name: 'Jammu and Kashmir', corps: 2, councils: 19, active: false },
    { name: 'Ladakh', corps: 0, councils: 2, active: false },
    { name: 'Lakshadweep', corps: 0, councils: 0, active: false },
    { name: 'Puducherry', corps: 0, councils: 5, active: false }
  ];

  let ACTIVE_STATE = 'Maharashtra';'''

if 'const ALL_INDIA_STATES =' not in code:
    code = code.replace("  let ACTIVE_SECTION = 'corps';", states_def + "\n  let ACTIVE_SECTION = 'corps';")

# 2. Fix the Corporation Card click bug!
# The bug was: onclick="go('corp/' + (c.slug || c.id))" without ${...}
code = code.replace(
    'onclick="go(\'corp/\' + (c.slug || c.id))"',
    'onclick="go(\'corp/\' + (c.slug || c.id))"'
)
# Make sure it uses ${c.slug || c.id} properly:
code = re.sub(
    r'onclick="go\(\'corp/\'\s*\+\s*\(c\.slug\s*\|\|\s*c\.id\)\)"',
    r'onclick="go(\'corp/\' + (this.getAttribute(\'data-slug\') || \'bmc\'))" data-slug="${c.slug || c.id}"',
    code
)
code = re.sub(
    r'onclick="event\.stopPropagation\(\);go\(\'corp/\'\s*\+\s*\(c\.slug\s*\|\|\s*c\.id\)\)"',
    r'onclick="event.stopPropagation();go(\'corp/\' + \'${c.slug || c.id}\')"',
    code
)

# 3. Dedicated Municipal Corporations Page Function: window.renderMunicipalCorporationsSection
# 4. Dedicated Municipal Councils Page Function: window.renderMunicipalCouncilsSection
# 5. Full Municipal Council Detail Page Function: window.renderCouncilDetailPage

new_sections_code = r'''
  // ═══════════════════════════════════════════════════════════════
  // DEDICATED SECTIONS: Municipal Corporations & Municipal Councils
  // ═══════════════════════════════════════════════════════════════

  window.renderMunicipalCorporationsSection = function(stateParam, yearParam) {
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
  };

  // Helper to render state filter dropdown options
  function renderStateFilterOptions(selectedState) {
    selectedState = selectedState || ACTIVE_STATE || 'Maharashtra';
    return ALL_INDIA_STATES.map(st => {
      const isSel = st.name.toLowerCase() === selectedState.toLowerCase();
      const badge = st.active ? '📍 ' : '';
      const countInfo = st.active ? ` (${st.corps} Corps, ${st.councils} Councils)` : '';
      return `<option value="${esc(st.name)}" ${isSel ? 'selected' : ''}>${badge}${esc(st.name)}${countInfo}</option>`;
    }).join('');
  }

  // ═══════════════════════════════════════════════════════════════
  // myCorporator PORTAL for Municipal Councils (Nagar Parishads)
  // ═══════════════════════════════════════════════════════════════
  let MYCOUNCIL_STATE = {
    council: null,
    tab: 'councillors', // 'councillors', 'president', 'directory', 'tally'
    search: '',
    partyFilter: '',
    seatFilter: '',
    sort: 'ward-asc'
  };

  function getCouncilBySlugOrId(idOrSlug) {
    const list = window.MH_COUNCILS || [];
    if (!idOrSlug) return list[0];
    const s = String(idOrSlug).toLowerCase().trim();
    return list.find(c => {
      const slug = (c.name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      return slug === s || String(c.id) === s || c.name.toLowerCase() === s || c.name.toLowerCase().includes(s) || (c.raw_name && c.raw_name.toLowerCase().includes(s));
    }) || list[0];
  }

  window.renderCouncilDetailPage = function(slugOrId, initialTab) {
    const council = getCouncilBySlugOrId(slugOrId);
    if (!council) return '<p class="note">Municipal Council not found.</p>';

    MYCOUNCIL_STATE.council = council;
    if (initialTab) MYCOUNCIL_STATE.tab = initialTab;

    setTimeout(() => {
      initMyCouncilEvents();
      renderMyCouncilTabContent();
    }, 10);

    const winners = council.winners || [];
    const seatCount = council.seat_count || winners.length || 27;
    const majMark = Math.floor(seatCount / 2) + 1;
    const tally = council.party_tally || {};
    const topParties = Object.entries(tally).sort((a,b) => b[1] - a[1]);
    const leadingParty = topParties[0] ? topParties[0][0] : 'BJP';
    const pres = council.president;
    const allCouncils = window.MH_COUNCILS || [];

    // Build Majority Bar Segments
    const barSegments = topParties.map(([p, cnt]) => {
      const pct = (cnt / seatCount) * 100;
      return `<div class="mycorp-bar-seg" style="width:${pct}%;background:${getPartyColor(p)}" title="${esc(p)}: ${cnt} seats (${pct.toFixed(1)}%)"></div>`;
    }).join('');

    const thresholdPct = (majMark / seatCount) * 100;

    return `
      <!-- Breadcrumb -->
      <div class="bc">
        <a onclick="go('')">Home</a> <span>›</span>
        <a onclick="go('mh')">Maharashtra</a> <span>›</span>
        <a onclick="go('councils')">Municipal Councils</a> <span>›</span>
        <span>${esc(council.name)} (myCorporator)</span>
      </div>

      <!-- Hero Header -->
      <div class="mycorp-hero" style="border-color:rgba(56,189,248,0.35);background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.88) 50%, rgba(19,136,8,0.10) 100%)">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div class="mycorp-badge-row">
              <span class="mycorp-brand-pill" style="background:linear-gradient(90deg, #38bdf8, #0284c7);color:#fff">MUNICIPAL COUNCIL PORTAL</span>
              <span class="mycorp-stat-pill">📍 ${esc(council.district || 'Maharashtra')}</span>
              <span class="mycorp-stat-pill">🗳️ ${seatCount} COUNCILLOR SEATS</span>
              <span class="mycorp-stat-pill">⚡ MAJORITY MARK: ${majMark}</span>
            </div>
            <h1 class="mycorp-title">
              🏢 ${esc(council.name)} Municipal Council (Nagar Parishad)
            </h1>
            <p style="color:var(--text-2);margin:0 0 10px;max-width:850px;font-size:14px;line-height:1.5">
              Official ward-wise councillor election results, directly-elected Nagaradhyaksha President details, party seat tallies, and civic representatives directory for <b>${esc(council.name)}</b>.
            </p>
          </div>

          <!-- Council Switcher Dropdown & Nav Back -->
          <div style="display:flex;flex-direction:column;gap:8px;align-items:flex-end">
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">Switch Council:</span>
              <select id="mycouncil-switcher" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:600;max-width:260px" onchange="go('council/' + this.value)">
                ${allCouncils.map(c => `
                  <option value="${c.id}" ${c.id === council.id ? 'selected' : ''}>
                    ${esc(c.name)} (${c.seat_count || 0} Seats)
                  </option>
                `).join('')}
              </select>
            </div>
            <div style="display:flex;gap:6px">
              <button class="btn" onclick="go('councils')">← All 224 Councils</button>
              <button class="btn" onclick="go('corporations')">🏛️ Municipal Corporations</button>
            </div>
          </div>
        </div>

        <!-- High Level Civic Metrics Cards -->
        <div class="g g4" style="margin-top:18px;gap:10px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">TOTAL COUNCILLOR SEATS</div>
            <div style="font-size:24px;font-weight:800;color:#38bdf8;margin:3px 0">${fmt(seatCount)}</div>
            <div style="font-size:11px;color:var(--text-2)">${council.ward_count ? council.ward_count + ' Electoral Wards' : 'Multi-Member Wards'}</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">MAJORITY THRESHOLD</div>
            <div style="font-size:24px;font-weight:800;color:#4ade80;margin:3px 0">${majMark} Seats</div>
            <div style="font-size:11px;color:var(--text-2)">Required for Council Majority</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">NAGARADHYAKSHA (PRESIDENT)</div>
            <div style="font-size:16px;font-weight:800;color:${pres ? getPartyColor(pres.party) : '#ff9933'};margin:5px 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${pres ? esc(pres.candidate) : 'Directly Elected'}">
              ${pres ? esc(pres.candidate) : 'Direct Election'}
            </div>
            <div style="font-size:11px;color:var(--text-2)">${pres ? esc(pres.party) + ' · ' + fmt(pres.votes) + ' votes' : 'Directly elected by citizens'}</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">LEADING POLITICAL FORCE</div>
            <div style="font-size:20px;font-weight:800;color:${getPartyColor(leadingParty)};margin:3px 0">${esc(leadingParty)}</div>
            <div style="font-size:11px;color:var(--text-2)">${topParties[0] ? topParties[0][1] + ' seats won' : 'Council Coalition'}</div>
          </div>
        </div>

        <!-- Majority Visual Bar -->
        <div style="margin-top:16px;background:rgba(0,0,0,0.22);border:1px solid var(--b);border-radius:8px;padding:12px 14px">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:600">
            <span style="color:var(--text)">Party Seat Distribution in Council</span>
            <span style="color:#ffd07a">⚡ Halfway Mark: <b>${majMark}</b> Seats</span>
          </div>
          <div class="mycorp-bar-track">
            ${barSegments}
            <div class="mycorp-threshold-mark" style="left:${thresholdPct}%" title="Majority Line: ${majMark} Seats"></div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px">
            ${topParties.map(([p, cnt]) => `
              <span style="font-size:11.5px;padding:2px 7px;border-radius:4px;background:var(--s1);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                ${esc(p)}: <b>${cnt}</b>
              </span>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- Navigation Tabs (Matching myCorporator) -->
      <div class="tab-pills" style="margin-bottom:18px">
        <button class="tab-pill ${MYCOUNCIL_STATE.tab==='councillors'?'on':''}" id="mcltab-councillors" onclick="switchMyCouncilTab('councillors')">
          🗳️ Councillor Results – Ward Wise
        </button>
        <button class="tab-pill ${MYCOUNCIL_STATE.tab==='president'?'on':''}" id="mcltab-president" onclick="switchMyCouncilTab('president')">
          👑 Nagaradhyaksha President Details
        </button>
        <button class="tab-pill ${MYCOUNCIL_STATE.tab==='directory'?'on':''}" id="mcltab-directory" onclick="switchMyCouncilTab('directory')">
          🏛️ List of Councillors (${winners.length})
        </button>
        <button class="tab-pill ${MYCOUNCIL_STATE.tab==='tally'?'on':''}" id="mcltab-tally" onclick="switchMyCouncilTab('tally')">
          📊 Party Tally &amp; Majority Analysis
        </button>
      </div>

      <!-- Quick Jump Matrix (All Councillor Seats) -->
      <div class="mycorp-matrix-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px">
          <div>
            <span style="font-size:13px;font-weight:700;color:var(--text)">
              ⚡ Quick Jump Matrix – All ${winners.length} Councillor Seats
            </span>
            <span style="font-size:11.5px;color:var(--text-2);margin-left:8px">
              Click any seat pill to jump directly to its result
            </span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <input id="mycouncil-jump-input" placeholder="Ward # e.g. 1" style="width:110px;padding:4px 8px;border-radius:6px;border:1px solid var(--b);background:var(--s2);color:var(--text);font-size:12px" onkeydown="if(event.key==='Enter')jumpToMyCouncilWard(this.value)">
            <button class="btn on" style="padding:4px 10px;font-size:12px" onclick="jumpToMyCouncilWard(document.getElementById('mycouncil-jump-input').value)">Jump →</button>
          </div>
        </div>

        <!-- Matrix Pills Grid -->
        <div class="mycorp-matrix-grid">
          ${winners.map((w, idx) => {
            const pCol = getPartyColor(w.party);
            const label = w.seat ? `${w.ward}${w.seat}` : `${w.ward}`;
            return `
              <div class="mycorp-ward-pill"
                   id="council-matrix-pill-${idx}"
                   style="border-color:${pCol};background:rgba(15,23,42,0.7);font-size:11px"
                   title="Ward ${w.ward} Seat ${w.seat || ''}: ${esc(w.candidate)} (${esc(w.party)}) · ${fmt(w.votes)} votes"
                   onclick="jumpToMyCouncilIndex(${idx})">
                ${label}
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- "Find Your Councillor Result" Toolbar -->
      <div class="card" style="padding:14px;margin-bottom:20px;background:var(--s1);border:1px solid var(--b);border-radius:10px">
        <div style="font-size:12.5px;font-weight:700;color:var(--text);margin-bottom:10px;display:flex;align-items:center;gap:6px">
          <span>🔍 Find Your Councillor Result &amp; Filter Candidates:</span>
        </div>
        <div class="filter-bar-grid">
          <input id="mycouncil-search-input"
                 placeholder="Search ward # (e.g. 1), councillor name, or party…"
                 oninput="onMyCouncilFilterChange()"
                 style="background:var(--s2);color:var(--text)">

          <select id="mycouncil-party-filter" onchange="onMyCouncilFilterChange()">
            <option value="">All Parties (${Object.keys(tally).length})</option>
            ${topParties.map(([p, cnt]) => `
              <option value="${esc(p)}">${esc(p)} (${cnt} Seats)</option>
            `).join('')}
          </select>

          <select id="mycouncil-sort-select" onchange="onMyCouncilFilterChange()">
            <option value="ward-asc">Ward No: Lowest First</option>
            <option value="ward-desc">Ward No: Highest First</option>
            <option value="votes-desc">Votes Polled: Highest First</option>
            <option value="name-asc">Candidate Name: A → Z</option>
          </select>
        </div>
      </div>

      <!-- Dynamic Tab Container -->
      <div id="mycouncil-tab-content">
        <p class="note">Loading councillor results…</p>
      </div>

      <!-- Councillor Deep-Dive Modal Wrap -->
      <div id="mycouncil-modal-wrap" style="display:none"></div>
    `;
  };

  function initMyCouncilEvents() {
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeMyCouncilModal();
    });
  }

  window.switchMyCouncilTab = function(tab) {
    MYCOUNCIL_STATE.tab = tab;
    ['councillors', 'president', 'directory', 'tally'].forEach(t => {
      const btn = document.getElementById('mcltab-' + t);
      if (btn) btn.classList.toggle('on', t === tab);
    });
    renderMyCouncilTabContent();
  };

  window.onMyCouncilFilterChange = function() {
    MYCOUNCIL_STATE.search = (document.getElementById('mycouncil-search-input') ? document.getElementById('mycouncil-search-input').value : '').toLowerCase().trim();
    MYCOUNCIL_STATE.partyFilter = document.getElementById('mycouncil-party-filter') ? document.getElementById('mycouncil-party-filter').value : '';
    MYCOUNCIL_STATE.sort = document.getElementById('mycouncil-sort-select') ? document.getElementById('mycouncil-sort-select').value : 'ward-asc';
    renderMyCouncilTabContent();
  };

  window.jumpToMyCouncilWard = function(wardQuery) {
    if (!wardQuery) return;
    const q = String(wardQuery).toLowerCase().trim();
    const winners = MYCOUNCIL_STATE.council ? (MYCOUNCIL_STATE.council.winners || []) : [];
    const idx = winners.findIndex(w => String(w.ward).toLowerCase() === q || `${w.ward}${w.seat}`.toLowerCase() === q);
    if (idx !== -1) {
      jumpToMyCouncilIndex(idx);
    }
  };

  window.jumpToMyCouncilIndex = function(idx) {
    if (MYCOUNCIL_STATE.tab !== 'councillors') {
      switchMyCouncilTab('councillors');
    }

    const sInput = document.getElementById('mycouncil-search-input');
    if (sInput && sInput.value) { sInput.value = ''; MYCOUNCIL_STATE.search = ''; }
    const pFilter = document.getElementById('mycouncil-party-filter');
    if (pFilter && pFilter.value) { pFilter.value = ''; MYCOUNCIL_STATE.partyFilter = ''; }

    renderMyCouncilTabContent();

    setTimeout(() => {
      const el = document.getElementById('mycouncil-card-' + idx);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.outline = '2px solid #38bdf8';
        el.style.boxShadow = '0 0 20px rgba(56,189,248,0.6)';
        setTimeout(() => {
          el.style.outline = '';
          el.style.boxShadow = '';
        }, 2500);
      } else {
        openMyCouncilDetailModal(idx);
      }
    }, 50);
  };

  function renderMyCouncilTabContent() {
    const area = document.getElementById('mycouncil-tab-content');
    if (!area || !MYCOUNCIL_STATE.council) return;

    if (MYCOUNCIL_STATE.tab === 'councillors') {
      renderMyCouncilCouncillorsView(area);
    } else if (MYCOUNCIL_STATE.tab === 'president') {
      renderMyCouncilPresidentView(area);
    } else if (MYCOUNCIL_STATE.tab === 'directory') {
      renderMyCouncilDirectoryView(area);
    } else if (MYCOUNCIL_STATE.tab === 'tally') {
      renderMyCouncilTallyView(area);
    }
  }

  // 1: Councillor Results View
  function renderMyCouncilCouncillorsView(container) {
    const council = MYCOUNCIL_STATE.council;
    let winners = (council.winners || []).slice();

    const q = MYCOUNCIL_STATE.search;
    const pFilter = MYCOUNCIL_STATE.partyFilter;

    winners = winners.filter(w => {
      if (q) {
        const matchWard = String(w.ward) === q || `${w.ward}${w.seat}`.toLowerCase().includes(q) || ('ward ' + w.ward).includes(q);
        const matchCand = (w.candidate || '').toLowerCase().includes(q);
        const matchParty = (w.party || '').toLowerCase().includes(q);
        if (!matchWard && !matchCand && !matchParty) return false;
      }
      if (pFilter && w.party !== pFilter) return false;
      return true;
    });

    const sort = MYCOUNCIL_STATE.sort;
    if (sort === 'ward-asc') winners.sort((a,b) => (+a.ward - +b.ward) || ((a.seat||'').localeCompare(b.seat||'')));
    else if (sort === 'ward-desc') winners.sort((a,b) => (+b.ward - +a.ward) || ((b.seat||'').localeCompare(a.seat||'')));
    else if (sort === 'votes-desc') winners.sort((a,b) => (b.votes || 0) - (a.votes || 0));
    else if (sort === 'name-asc') winners.sort((a,b) => (a.candidate || '').localeCompare(b.candidate || ''));

    if (!winners.length) {
      container.innerHTML = `<div class="card note" style="padding:40px;text-align:center">No councillor results match your filters. Try adjusting your search query or party selection.</div>`;
      return;
    }

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${winners.length}</b> Councillor Results (${esc(council.name)} Municipal Council)</span>
        <span class="note">💡 Click <b>Councillor Details</b> to inspect vote shares</span>
      </div>

      <div class="mycorp-cards-grid">
        ${winners.map((w, idx) => {
          const pColor = getPartyColor(w.party);

          return `
            <div class="mycorp-ward-card" id="mycouncil-card-${idx}" style="--card-accent:${pColor}">
              <div>
                <!-- Card Header -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="font-size:16px;font-weight:800;color:var(--text)">
                      Ward ${w.ward} ${w.seat ? '· Seat ' + esc(w.seat) : ''}
                    </span>
                  </div>
                  <span class="badge" style="background:rgba(34,197,94,0.15);color:#22c55e;font-weight:700;font-size:10.5px;padding:2px 6px;border-radius:4px">
                    ELECTED COUNCILLOR
                  </span>
                </div>

                <!-- Winner Block -->
                <div class="mycorp-winner-box" style="background:rgba(56,189,248,0.06);border-color:rgba(56,189,248,0.25)">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                    <span style="font-size:10.5px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.5px">WINNER</span>
                    <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};font-size:11px;padding:2px 6px">
                      ${esc(w.party)}
                    </span>
                  </div>

                  <div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:4px">
                    ${esc(w.candidate)}
                  </div>

                  <div style="display:flex;justify-content:space-between;align-items:baseline;font-size:12px;color:var(--text-2)">
                    <span>Votes Polled: <b style="color:var(--text)">${fmt(w.votes)}</b></span>
                    <span>Vote Share: <b style="color:var(--text)">${w.pct ? w.pct.toFixed(1) + '%' : '–'}</b></span>
                  </div>

                  ${w.pct ? `
                    <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;margin-top:6px">
                      <div style="width:${Math.min(w.pct, 100)}%;background:${pColor};height:100%"></div>
                    </div>
                  ` : ''}
                </div>
              </div>

              <!-- Action Card Footer -->
              <div style="border-top:1px solid var(--b);margin-top:10px;padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11px;color:var(--text-3)">${esc(council.name)} · SECM</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="openMyCouncilDetailModal(${idx})">
                  Councillor Details →
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // 2: Nagaradhyaksha President View
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
  }

  // 3: List of Councillors Directory View
  function renderMyCouncilDirectoryView(container) {
    const council = MYCOUNCIL_STATE.council;
    let winners = (council.winners || []).slice();

    const q = MYCOUNCIL_STATE.search;
    const pFilter = MYCOUNCIL_STATE.partyFilter;

    winners = winners.filter(w => {
      if (q) {
        const matchName = (w.candidate || '').toLowerCase().includes(q);
        const matchWard = String(w.ward) === q || `${w.ward}${w.seat}`.toLowerCase().includes(q);
        const matchParty = (w.party || '').toLowerCase().includes(q);
        if (!matchName && !matchWard && !matchParty) return false;
      }
      if (pFilter && w.party !== pFilter) return false;
      return true;
    });

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${winners.length}</b> Elected Councillors (${esc(council.name)})</span>
        <span class="note">Click any councillor card for vote breakdown</span>
      </div>

      <div class="mycorp-directors-grid">
        ${winners.map((w, idx) => {
          const pColor = getPartyColor(w.party);
          const initial = (w.candidate || 'C').charAt(0).toUpperCase();

          return `
            <div class="mycorp-corporator-card" onclick="openMyCouncilDetailModal(${idx})">
              <div class="mycorp-avatar" style="background:${pColor}">
                ${initial}
              </div>
              <div style="flex:1;min-width:0">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:4px">
                  <span class="badge" style="background:var(--s2);color:#38bdf8;font-weight:700;font-size:10.5px;padding:1px 5px;border-radius:4px">
                    Ward ${w.ward} ${w.seat ? '· Seat ' + esc(w.seat) : ''}
                  </span>
                </div>
                <h4 style="margin:2px 0 3px;font-size:14px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(w.candidate)}">
                  ${esc(w.candidate)}
                </h4>
                <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px">
                  <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};padding:1px 6px">
                    ${esc(w.party)}
                  </span>
                  <span style="color:var(--text-2);font-weight:600">
                    ${fmt(w.votes)} votes
                  </span>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // 4: Party Tally View
  function renderMyCouncilTallyView(container) {
    const council = MYCOUNCIL_STATE.council;
    const tally = council.party_tally || {};
    const seatCount = council.seat_count || (council.winners || []).length || 27;
    const majMark = Math.floor(seatCount / 2) + 1;
    const sorted = Object.entries(tally).sort((a,b) => b[1] - a[1]);

    container.innerHTML = `
      <div class="card" style="padding:0;overflow:hidden;border:1px solid var(--b);border-radius:10px">
        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:40px">#</th>
                <th>Political Party</th>
                <th style="text-align:right">Seats Won</th>
                <th style="text-align:right">Seat Share %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${sorted.map(([p, cnt], i) => {
                const pColor = getPartyColor(p);
                const sharePct = ((cnt / seatCount) * 100).toFixed(1);

                return `
                  <tr class="r">
                    <td>${i + 1}</td>
                    <td>
                      <div style="display:flex;align-items:center;gap:8px">
                        <span class="dot" style="background:${pColor};width:10px;height:10px;border-radius:50%"></span>
                        <b style="color:var(--text)">${esc(p)}</b>
                      </div>
                    </td>
                    <td style="text-align:right"><b style="color:#38bdf8;font-size:15px">${cnt}</b></td>
                    <td style="text-align:right"><b>${sharePct}%</b></td>
                    <td>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor}">
                        ${cnt >= majMark ? '🎉 Single Majority' : 'Council Partner'}
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
  }

  // Councillor Deep-Dive Modal
  window.openMyCouncilDetailModal = function(idx) {
    const council = MYCOUNCIL_STATE.council;
    if (!council) return;
    const winners = council.winners || [];
    const w = winners[idx];
    if (!w) return;

    const prevIdx = idx > 0 ? idx - 1 : winners.length - 1;
    const nextIdx = idx < winners.length - 1 ? idx + 1 : 0;

    const modalWrap = document.getElementById('mycouncil-modal-wrap');
    if (!modalWrap) return;

    const pColor = getPartyColor(w.party);

    modalWrap.innerHTML = `
      <div class="modal-backdrop" onclick="closeMyCouncilModal()" style="position:fixed;inset:0;background:rgba(0,0,0,0.82);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#0b1428;border:1px solid var(--b);border-radius:14px;width:min(640px, 95vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 60px rgba(0,0,0,0.85);overflow:hidden">
          
          <div style="padding:18px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:flex-start;background:rgba(255,255,255,0.02)">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="badge" style="background:#38bdf8;color:#000;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                  WARD ${w.ward} ${w.seat ? '· SEAT ' + esc(w.seat) : ''}
                </span>
                <span class="badge" style="background:var(--s2);color:var(--text);font-size:11px;padding:2px 8px;border-radius:4px">
                  ${esc(council.name)}
                </span>
              </div>
              <h2 style="margin:2px 0;font-size:19px;color:var(--text)">
                🏢 Councillor Election Details
              </h2>
            </div>
            <button class="btn" onclick="closeMyCouncilModal()" style="padding:4px 10px;font-size:16px" title="Close">✕</button>
          </div>

          <div style="padding:22px;overflow-y:auto;flex:1">
            <div class="mycorp-winner-box" style="margin:0 0 16px;background:rgba(56,189,248,0.08);border-color:rgba(56,189,248,0.3)">
              <span style="font-size:10px;font-weight:800;color:#38bdf8;text-transform:uppercase">ELECTED COUNCILLOR</span>
              <h3 style="margin:4px 0;font-size:18px;color:var(--text)">${esc(w.candidate)}</h3>
              <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};font-size:12px">
                ${esc(w.party)}
              </span>
              <div style="margin-top:10px;font-size:13px;color:var(--text-2)">
                Votes Polled: <b style="color:var(--text)">${fmt(w.votes)}</b> (${w.pct ? w.pct.toFixed(1) + '%' : '–'})
              </div>
            </div>
          </div>

          <div style="padding:14px 22px;border-top:1px solid var(--b);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02)">
            <button class="btn" onclick="openMyCouncilDetailModal(${prevIdx})">← Prev Councillor</button>
            <span style="font-size:12px;color:var(--text-2)">Seat ${idx + 1} of ${winners.length}</span>
            <button class="btn" onclick="openMyCouncilDetailModal(${nextIdx})">Next Councillor →</button>
          </div>

        </div>
      </div>
    `;
    modalWrap.style.display = 'block';
  };

  window.closeMyCouncilModal = function() {
    const modalWrap = document.getElementById('mycouncil-modal-wrap');
    if (modalWrap) modalWrap.style.display = 'none';
  };
'''

# Insert the new functions before the closing })();
if 'window.renderCouncilDetailPage =' not in code:
    last_brace_idx = code.rfind('})();')
    if last_brace_idx != -1:
        code = code[:last_brace_idx] + new_sections_code + '\n' + code[last_brace_idx:]

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated js/mh-local-ui.js successfully.")
