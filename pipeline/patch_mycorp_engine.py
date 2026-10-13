import re, sys

# 1. Patch js/mh-local-ui.js
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Add featured BMC banner right after High Level Metrics Bar
bmc_banner = '''        </div>
      </div>

      <!-- Featured BMC myCorporator Portal Banner -->
      <div class="card" style="margin:0 0 20px;background:linear-gradient(135deg, rgba(255,107,0,0.14) 0%, rgba(15,23,42,0.92) 100%);border:1px solid rgba(255,153,51,0.45);border-radius:14px;padding:18px 22px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 10px 30px rgba(0,0,0,0.45)">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span class="mycorp-brand-pill">FEATURED CIVIC HUB</span>
            <span class="mycorp-stat-pill">227 WARDS · 114 MAJORITY MARK</span>
            <span class="mycorp-stat-pill">₹65,000+ CR BUDGET</span>
          </div>
          <h2 style="margin:2px 0 6px;font-size:20px;color:var(--text);display:flex;align-items:center;gap:8px">
            🏛️ Brihanmumbai Municipal Corporation (BMC) — myCorporator Portal
          </h2>
          <p style="margin:0;font-size:13px;color:var(--text-2);max-width:760px;line-height:1.45">
            Explore complete ward-wise election results (Ward 1 to 227), corporator directory, vote share analysis, victory margins, and 2017 vs 2026 seat flips for India's premier civic corporation.
          </p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn on" style="padding:10px 20px;font-size:13.5px;font-weight:700;background:linear-gradient(90deg, #ff9933, #ff6b00);color:#000;border:none;box-shadow:0 4px 16px rgba(255,107,0,0.45);cursor:pointer" onclick="go('corp/bmc')">
            Open BMC Portal (227 Wards) →
          </button>
        </div>
      </div>'''

# Replace metric closing tag
if '<!-- Featured BMC myCorporator Portal Banner -->' not in js_content:
    js_content = js_content.replace('''        </div>
      </div>

      <!-- Primary Navigation Toolbar: Section Tabs & State Selector -->''', bmc_banner + '''

      <!-- Primary Navigation Toolbar: Section Tabs & State Selector -->''')

# Update card click in renderCorpsView
js_content = js_content.replace(
    'onclick="openCorpModal(${c.id}, \'${year}\')"',
    'onclick="go(\'corp/\' + (c.slug || c.id))"'
)
js_content = js_content.replace(
    'onclick="event.stopPropagation();openCorpModal(${c.id}, \'${year}\')"',
    'onclick="event.stopPropagation();go(\'corp/\' + (c.slug || c.id))"'
)

# Append full myCorporator engine before closing })();
mycorp_engine = r'''
  // ═══════════════════════════════════════════════════════════════
  // myCorporator PORTAL ENGINE — Brihanmumbai (BMC) & All 29 Corps
  // ═══════════════════════════════════════════════════════════════

  let MYCORP_STATE = {
    corp: null,
    tab: 'results2026', // 'results2026', 'results2017', 'corporators', 'compare', 'tally'
    search: '',
    partyFilter: '',
    resFilter: '',
    marginFilter: '',
    sort: 'ward-asc'
  };

  function getCorpBySlugOrId(idOrSlug) {
    const list = window.MH_CORPS || [];
    if (!idOrSlug) return list.find(c => c.slug === 'bmc') || list[0];
    const s = String(idOrSlug).toLowerCase().trim();
    return list.find(c => c.slug === s || String(c.id) === s || c.name.toLowerCase().includes(s) || (c.raw_name && c.raw_name.toLowerCase().includes(s))) || list.find(c => c.slug === 'bmc') || list[0];
  }

  window.renderCorporationDetailPage = function(slugOrId, initialTab) {
    const corp = getCorpBySlugOrId(slugOrId);
    if (!corp) return '<p class="note">Corporation not found.</p>';

    MYCORP_STATE.corp = corp;
    if (initialTab) MYCORP_STATE.tab = initialTab;

    setTimeout(() => {
      initMyCorpEvents();
      renderMyCorpTabContent();
    }, 10);

    const winners2026 = corp.winners_2026 || [];
    const winners2017 = corp.winners_2017 || [];
    const seatCount = corp.seat_count_2026 || corp.ward_count_2026 || winners2026.length || 227;
    const majMark = Math.floor(seatCount / 2) + 1;
    const tally2026 = corp.party_tally_2026 || {};
    const top2026 = Object.entries(tally2026).sort((a,b) => b[1] - a[1]);
    const leadingParty = top2026[0] ? top2026[0][0] : 'BJP';
    const allCorps = window.MH_CORPS || [];

    // Map 2017 winners by ward for fast lookup
    const w2017Map = {};
    winners2017.forEach(w => { w2017Map[w.ward] = w; });

    // Build Majority Bar Segments
    const barSegments = top2026.map(([p, cnt]) => {
      const pct = (cnt / seatCount) * 100;
      return `<div class="mycorp-bar-seg" style="width:${pct}%;background:${getPartyColor(p)}" title="${esc(p)}: ${cnt} seats (${pct.toFixed(1)}%)"></div>`;
    }).join('');

    const thresholdPct = (majMark / seatCount) * 100;

    return `
      <div class="bc">
        <a onclick="go('')">Home</a> <span>›</span>
        <a onclick="go('mh')">Maharashtra</a> <span>›</span>
        <a onclick="go('mh-local')">Municipal Corporations</a> <span>›</span>
        <span>${esc(corp.name)} (myCorporator)</span>
      </div>

      <!-- Hero Header -->
      <div class="mycorp-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div class="mycorp-badge-row">
              <span class="mycorp-brand-pill">myCorporator PORTAL</span>
              <span class="mycorp-stat-pill">📍 ${esc(corp.district || 'Maharashtra')}</span>
              <span class="mycorp-stat-pill">🗳️ ${seatCount} WARDS</span>
              <span class="mycorp-stat-pill">⚡ MAJORITY MARK: ${majMark}</span>
            </div>
            <h1 class="mycorp-title">
              🏛️ ${esc(corp.name)} Municipal Corporation
            </h1>
            <p style="color:var(--text-2);margin:0 0 10px;max-width:850px;font-size:14px;line-height:1.5">
              Official ward-by-ward election results, corporator directory, vote shares, victory margins, and 2017 vs 2026 historical seat swings for <b>${esc(corp.name)}</b>.
            </p>
          </div>

          <!-- Corporation Switcher Dropdown & Nav Back -->
          <div style="display:flex;flex-direction:column;gap:8px;align-items:flex-end">
            <div style="display:flex;align-items:center;gap:6px">
              <span style="font-size:12px;color:var(--text-2);font-weight:600">Switch Corporation:</span>
              <select id="mycorp-switcher" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:600" onchange="go('corp/' + this.value)">
                ${allCorps.map(c => `
                  <option value="${c.slug || c.id}" ${c.id === corp.id ? 'selected' : ''}>
                    ${esc(c.name)} (${c.seat_count_2026 || c.ward_count_2026 || 0} Wards)
                  </option>
                `).join('')}
              </select>
            </div>
            <div style="display:flex;gap:6px">
              <button class="btn" onclick="go('mh-local')">← All 29 Corporations</button>
              <button class="btn" onclick="go('mh')">🏢 Assembly (288 AC)</button>
            </div>
          </div>
        </div>

        <!-- High Level Civic Metrics Cards -->
        <div class="g g4" style="margin-top:18px;gap:10px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">TOTAL CIVIC WARDS</div>
            <div style="font-size:24px;font-weight:800;color:#ff9933;margin:3px 0">${fmt(seatCount)}</div>
            <div style="font-size:11px;color:var(--text-2)">Single-member electoral wards</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">MAJORITY THRESHOLD</div>
            <div style="font-size:24px;font-weight:800;color:#4ade80;margin:3px 0">${majMark} Seats</div>
            <div style="font-size:11px;color:var(--text-2)">Required to elect the Mayor</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">POPULATION COVERED</div>
            <div style="font-size:24px;font-weight:800;color:#38bdf8;margin:3px 0">${corp.total_pop ? fmt(corp.total_pop) : '1.24+ Crore'}</div>
            <div style="font-size:11px;color:var(--text-2)">${corp.district || 'Metropolitan Region'}</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:12px 14px">
            <div style="font-size:11.5px;color:var(--text-2);font-weight:600">LEADING POLITICAL FORCE</div>
            <div style="font-size:22px;font-weight:800;color:${getPartyColor(leadingParty)};margin:3px 0">${esc(leadingParty)}</div>
            <div style="font-size:11px;color:var(--text-2)">${top2026[0] ? top2026[0][1] + ' seats won' : 'Coalition'}</div>
          </div>
        </div>

        <!-- Majority Visual Bar -->
        <div style="margin-top:16px;background:rgba(0,0,0,0.22);border:1px solid var(--b);border-radius:8px;padding:12px 14px">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:600">
            <span style="color:var(--text)">Party Seat Distribution (2026)</span>
            <span style="color:#ffd07a">⚡ Halfway Mark: <b>${majMark}</b> Seats</span>
          </div>
          <div class="mycorp-bar-track">
            ${barSegments}
            <div class="mycorp-threshold-mark" style="left:${thresholdPct}%" title="Majority Line: ${majMark} Seats"></div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px">
            ${top2026.map(([p, cnt]) => `
              <span style="font-size:11.5px;padding:2px 7px;border-radius:4px;background:var(--s1);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                ${esc(p)}: <b>${cnt}</b>
              </span>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- Navigation Tabs (Matching mycorporator.in) -->
      <div class="tab-pills" style="margin-bottom:18px">
        <button class="tab-pill ${MYCORP_STATE.tab==='results2026'?'on':''}" id="mctab-results2026" onclick="switchMyCorpTab('results2026')">
          🗳️ 2026 Election Result – Ward Wise
        </button>
        <button class="tab-pill ${MYCORP_STATE.tab==='results2017'?'on':''}" id="mctab-results2017" onclick="switchMyCorpTab('results2017')">
          📅 2017 Election Result – Ward Wise
        </button>
        <button class="tab-pill ${MYCORP_STATE.tab==='corporators'?'on':''}" id="mctab-corporators" onclick="switchMyCorpTab('corporators')">
          🏛️ List of Corporators (${winners2026.length})
        </button>
        <button class="tab-pill ${MYCORP_STATE.tab==='compare'?'on':''}" id="mctab-compare" onclick="switchMyCorpTab('compare')">
          ⚖️ 2017 vs 2026 Ward Comparison (Seat Swings)
        </button>
        <button class="tab-pill ${MYCORP_STATE.tab==='tally'?'on':''}" id="mctab-tally" onclick="switchMyCorpTab('tally')">
          📊 Party Tally &amp; Majority Analysis
        </button>
      </div>

      <!-- Quick Jump Matrix (All 227 Wards) -->
      <div class="mycorp-matrix-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px">
          <div>
            <span style="font-size:13px;font-weight:700;color:var(--text)">
              ⚡ Quick Jump Matrix – All ${winners2026.length} Wards
            </span>
            <span style="font-size:11.5px;color:var(--text-2);margin-left:8px">
              Click any ward pill to jump directly to its result
            </span>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <input id="mycorp-jump-input" type="number" min="1" max="${winners2026.length}" placeholder="Ward #" style="width:75px;padding:4px 8px;border-radius:6px;border:1px solid var(--b);background:var(--s2);color:var(--text);font-size:12px" onkeydown="if(event.key==='Enter')jumpToMyCorpWard(this.value)">
            <button class="btn on" style="padding:4px 10px;font-size:12px" onclick="jumpToMyCorpWard(document.getElementById('mycorp-jump-input').value)">Jump →</button>
          </div>
        </div>

        <!-- Matrix Pills Grid -->
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
        </div>
      </div>

      <!-- "Find Your Ward Result" Toolbar -->
      <div class="card" style="padding:14px;margin-bottom:20px;background:var(--s1);border:1px solid var(--b);border-radius:10px">
        <div style="font-size:12.5px;font-weight:700;color:var(--text);margin-bottom:10px;display:flex;align-items:center;gap:6px">
          <span>🔍 Find Your Ward Result &amp; Filter Candidates:</span>
        </div>
        <div class="filter-bar-grid">
          <input id="mycorp-search-input"
                 placeholder="Search ward # (e.g. 1), candidate name, runner-up, or reservation…"
                 oninput="onMyCorpFilterChange()"
                 style="background:var(--s2);color:var(--text)">

          <select id="mycorp-party-filter" onchange="onMyCorpFilterChange()">
            <option value="">All Parties (${Object.keys(tally2026).length})</option>
            ${top2026.map(([p, cnt]) => `
              <option value="${esc(p)}">${esc(p)} (${cnt} Wards)</option>
            `).join('')}
          </select>

          <select id="mycorp-res-filter" onchange="onMyCorpFilterChange()">
            <option value="">All Reservations</option>
            <option value="General">General / Open</option>
            <option value="Women">Women (Any)</option>
            <option value="General Women">General Women</option>
            <option value="OBC">OBC</option>
            <option value="OBC Women">OBC Women</option>
            <option value="SC">SC</option>
            <option value="SC Women">SC Women</option>
            <option value="ST">ST</option>
            <option value="ST Women">ST Women</option>
          </select>

          <select id="mycorp-margin-filter" onchange="onMyCorpFilterChange()">
            <option value="">All Victory Margins</option>
            <option value="close">Razor Thin (< 1,000 votes)</option>
            <option value="mid">Moderate (1,000 – 4,000 votes)</option>
            <option value="big">Landslide (> 4,000 votes)</option>
          </select>

          <select id="mycorp-sort-select" onchange="onMyCorpFilterChange()">
            <option value="ward-asc">Ward No: 1 → ${winners2026.length}</option>
            <option value="ward-desc">Ward No: ${winners2026.length} → 1</option>
            <option value="margin-desc">Margin: Highest First</option>
            <option value="margin-asc">Margin: Closest Contests First</option>
            <option value="votes-desc">Winner Votes: Highest First</option>
            <option value="name-asc">Candidate Name: A → Z</option>
          </select>
        </div>
      </div>

      <!-- Dynamic Tab Container -->
      <div id="mycorp-tab-content">
        <p class="note">Loading ward results…</p>
      </div>

      <!-- Ward Deep-Dive Modal Wrap -->
      <div id="mycorp-modal-wrap" style="display:none"></div>
    `;
  };

  function initMyCorpEvents() {
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeMyCorpWardModal();
    });
  }

  window.switchMyCorpTab = function(tab) {
    MYCORP_STATE.tab = tab;
    ['results2026', 'results2017', 'corporators', 'compare', 'tally'].forEach(t => {
      const btn = document.getElementById('mctab-' + t);
      if (btn) btn.classList.toggle('on', t === tab);
    });
    renderMyCorpTabContent();
  };

  window.onMyCorpFilterChange = function() {
    MYCORP_STATE.search = (document.getElementById('mycorp-search-input') ? document.getElementById('mycorp-search-input').value : '').toLowerCase().trim();
    MYCORP_STATE.partyFilter = document.getElementById('mycorp-party-filter') ? document.getElementById('mycorp-party-filter').value : '';
    MYCORP_STATE.resFilter = document.getElementById('mycorp-res-filter') ? document.getElementById('mycorp-res-filter').value : '';
    MYCORP_STATE.marginFilter = document.getElementById('mycorp-margin-filter') ? document.getElementById('mycorp-margin-filter').value : '';
    MYCORP_STATE.sort = document.getElementById('mycorp-sort-select') ? document.getElementById('mycorp-sort-select').value : 'ward-asc';
    renderMyCorpTabContent();
  };

  window.jumpToMyCorpWard = function(wardNo) {
    wardNo = parseInt(wardNo, 10);
    if (!wardNo || isNaN(wardNo)) return;

    if (MYCORP_STATE.tab !== 'results2026' && MYCORP_STATE.tab !== 'results2017') {
      switchMyCorpTab('results2026');
    }

    // Clear filters if needed so ward is rendered
    const sInput = document.getElementById('mycorp-search-input');
    if (sInput && sInput.value) { sInput.value = ''; MYCORP_STATE.search = ''; }
    const pFilter = document.getElementById('mycorp-party-filter');
    if (pFilter && pFilter.value) { pFilter.value = ''; MYCORP_STATE.partyFilter = ''; }

    renderMyCorpTabContent();

    setTimeout(() => {
      const el = document.getElementById('mycorp-ward-card-' + wardNo);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.outline = '2px solid #ff9933';
        el.style.boxShadow = '0 0 20px rgba(255,153,51,0.6)';
        setTimeout(() => {
          el.style.outline = '';
          el.style.boxShadow = '';
        }, 2500);
      } else {
        openMyCorpWardModal(wardNo);
      }
    }, 50);
  };

  function renderMyCorpTabContent() {
    const area = document.getElementById('mycorp-tab-content');
    if (!area || !MYCORP_STATE.corp) return;

    if (MYCORP_STATE.tab === 'results2026') {
      renderMyCorpResultsView(area, '2026');
    } else if (MYCORP_STATE.tab === 'results2017') {
      renderMyCorpResultsView(area, '2017');
    } else if (MYCORP_STATE.tab === 'corporators') {
      renderMyCorpCorporatorsView(area);
    } else if (MYCORP_STATE.tab === 'compare') {
      renderMyCorpComparisonView(area);
    } else if (MYCORP_STATE.tab === 'tally') {
      renderMyCorpTallyView(area);
    }
  }

  // 1 & 2: Ward Results View (2026 or 2017)
  function renderMyCorpResultsView(container, year) {
    const corp = MYCORP_STATE.corp;
    const is2026 = year === '2026';
    let wards = (is2026 ? corp.winners_2026 : corp.winners_2017) || [];
    const w2017Map = {};
    (corp.winners_2017 || []).forEach(w => { w2017Map[w.ward] = w; });
    const w2026Map = {};
    (corp.winners_2026 || []).forEach(w => { w2026Map[w.ward] = w; });

    // Filter
    const q = MYCORP_STATE.search;
    const pFilter = MYCORP_STATE.partyFilter;
    const rFilter = MYCORP_STATE.resFilter;
    const mFilter = MYCORP_STATE.marginFilter;

    wards = wards.filter(w => {
      if (q) {
        const matchWard = String(w.ward) === q || ('ward ' + w.ward).includes(q);
        const matchCand = (w.candidate || '').toLowerCase().includes(q);
        const matchRunner = (w.runner || '').toLowerCase().includes(q);
        const matchParty = (w.party || '').toLowerCase().includes(q);
        const matchRes = (w.res || '').toLowerCase().includes(q);
        if (!matchWard && !matchCand && !matchRunner && !matchParty && !matchRes) return false;
      }
      if (pFilter && w.party !== pFilter) return false;
      if (rFilter) {
        const res = (w.res || '').toLowerCase();
        if (rFilter === 'Women' && !res.includes('women')) return false;
        if (rFilter !== 'Women' && !res.includes(rFilter.toLowerCase())) return false;
      }
      if (mFilter) {
        const m = w.margin || 0;
        if (mFilter === 'close' && m >= 1000) return false;
        if (mFilter === 'mid' && (m < 1000 || m > 4000)) return false;
        if (mFilter === 'big' && m <= 4000) return false;
      }
      return true;
    });

    // Sort
    const sort = MYCORP_STATE.sort;
    if (sort === 'ward-asc') wards.sort((a,b) => a.ward - b.ward);
    else if (sort === 'ward-desc') wards.sort((a,b) => b.ward - a.ward);
    else if (sort === 'margin-desc') wards.sort((a,b) => (b.margin || 0) - (a.margin || 0));
    else if (sort === 'margin-asc') wards.sort((a,b) => (a.margin || 0) - (b.margin || 0));
    else if (sort === 'votes-desc') wards.sort((a,b) => (b.votes || 0) - (a.votes || 0));
    else if (sort === 'name-asc') wards.sort((a,b) => (a.candidate || '').localeCompare(b.candidate || ''));

    if (!wards.length) {
      container.innerHTML = `<div class="card note" style="padding:40px;text-align:center">No ward results match your filters. Try adjusting your search query or party selection.</div>`;
      return;
    }

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${wards.length}</b> Wards (${year} Election Results)</span>
        <span class="note">💡 Click <b>Ward Details</b> to inspect full candidate breakdown and vote swing</span>
      </div>

      <div class="mycorp-cards-grid">
        ${wards.map(w => {
          const pColor = getPartyColor(w.party);
          const w2017 = w2017Map[w.ward];
          const isFlip = is2026 && w2017 && w2017.party && w2017.party !== w.party;

          return `
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
                  </div>

                  <!-- Flip / Retain Badge -->
                  ${is2026 ? (isFlip ? `
                    <span class="badge" style="background:rgba(245,158,11,0.18);color:#f59e0b;font-weight:700;font-size:10.5px;padding:2px 6px;border-radius:4px" title="Flipped from ${esc(w2017.party)} to ${esc(w.party)}">
                      🔄 FLIP: ${esc(w2017.party)} ➔ ${esc(w.party)}
                    </span>
                  ` : `
                    <span class="badge" style="background:rgba(34,197,94,0.15);color:#22c55e;font-weight:700;font-size:10.5px;padding:2px 6px;border-radius:4px">
                      🛡️ RETAINED
                    </span>
                  `) : ''}
                </div>

                <!-- Winner Block -->
                <div class="mycorp-winner-box">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                    <span style="font-size:10.5px;font-weight:800;color:#16a34a;text-transform:uppercase;letter-spacing:0.5px">WINNER (ELECTED)</span>
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

                <!-- Runner-Up Block -->
                ${w.runner ? `
                  <div class="mycorp-runner-box">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
                      <span style="font-size:10.5px;color:var(--text-3);text-transform:uppercase;font-weight:700">RUNNER-UP</span>
                      <span style="font-size:11px;color:var(--text-2);font-weight:600">${esc(w.runner_party || 'Opposition')}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <span style="font-size:13px;color:var(--text-2);font-weight:600">${esc(w.runner)}</span>
                      <span style="font-size:12px;color:var(--text-3)">${fmt(w.runner_votes)} votes</span>
                    </div>
                  </div>
                ` : ''}

                <!-- Margin & Previous Election Snippet -->
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;padding:4px 0">
                  <span style="font-size:12px;font-weight:700;color:#38bdf8">
                    Victory Margin: +${fmt(w.margin)}
                  </span>
                  ${is2026 && w2017 ? `
                    <span style="font-size:11px;color:var(--text-3)">
                      2017: <b>${esc(w2017.party)}</b> (${fmt(w2017.votes)})
                    </span>
                  ` : ''}
                </div>
              </div>

              <!-- Action Card Footer -->
              <div style="border-top:1px solid var(--b);margin-top:10px;padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11px;color:var(--text-3)">Ward ${w.ward} · ${esc(corp.name)}</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="openMyCorpWardModal(${w.ward})">
                  Ward Details →
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // 3: List of Corporators Directory View
  function renderMyCorpCorporatorsView(container) {
    const corp = MYCORP_STATE.corp;
    let corporators = (corp.winners_2026 || []).slice();

    const q = MYCORP_STATE.search;
    const pFilter = MYCORP_STATE.partyFilter;
    const rFilter = MYCORP_STATE.resFilter;

    corporators = corporators.filter(c => {
      if (q) {
        const matchName = (c.candidate || '').toLowerCase().includes(q);
        const matchWard = String(c.ward) === q;
        const matchParty = (c.party || '').toLowerCase().includes(q);
        if (!matchName && !matchWard && !matchParty) return false;
      }
      if (pFilter && c.party !== pFilter) return false;
      if (rFilter) {
        const res = (c.res || '').toLowerCase();
        if (rFilter === 'Women' && !res.includes('women')) return false;
        if (rFilter !== 'Women' && !res.includes(rFilter.toLowerCase())) return false;
      }
      return true;
    });

    const sort = MYCORP_STATE.sort;
    if (sort === 'name-asc') corporators.sort((a,b) => (a.candidate||'').localeCompare(b.candidate||''));
    else if (sort === 'ward-asc') corporators.sort((a,b) => a.ward - b.ward);
    else if (sort === 'ward-desc') corporators.sort((a,b) => b.ward - a.ward);
    else if (sort === 'margin-desc') corporators.sort((a,b) => (b.margin||0) - (a.margin||0));

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${corporators.length}</b> Elected Municipal Corporators (${esc(corp.name)})</span>
        <span class="note">Click any corporator profile to view ward voting demographics</span>
      </div>

      <div class="mycorp-directors-grid">
        ${corporators.map(c => {
          const pColor = getPartyColor(c.party);
          const initial = (c.candidate || 'C').charAt(0).toUpperCase();

          return `
            <div class="mycorp-corporator-card" onclick="openMyCorpWardModal(${c.ward})">
              <div class="mycorp-avatar" style="background:${pColor}">
                ${initial}
              </div>
              <div style="flex:1;min-width:0">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:4px">
                  <span class="badge" style="background:var(--s2);color:#ffd07a;font-weight:700;font-size:10.5px;padding:1px 5px;border-radius:4px">
                    Ward ${c.ward}
                  </span>
                  ${c.res ? `<span style="font-size:10.5px;color:var(--text-3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(c.res)}</span>` : ''}
                </div>
                <h4 style="margin:2px 0 3px;font-size:14px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(c.candidate)}">
                  ${esc(c.candidate)}
                </h4>
                <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px">
                  <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};padding:1px 6px">
                    ${esc(c.party)}
                  </span>
                  <span style="color:var(--text-2);font-weight:600">
                    +${fmt(c.margin)}
                  </span>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // 4: 2017 vs 2026 Historical Comparison View
  function renderMyCorpComparisonView(container) {
    const corp = MYCORP_STATE.corp;
    const w2026 = (corp.winners_2026 || []).slice();
    const w2017Map = {};
    (corp.winners_2017 || []).forEach(w => { w2017Map[w.ward] = w; });

    container.innerHTML = `
      <div class="card" style="margin-bottom:14px;background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:16px">
        <h3 style="margin:0 0 4px;font-size:16px">⚖️ Ward-by-Ward 2017 vs 2026 Swing Comparison (${esc(corp.name)})</h3>
        <p class="note" style="margin:0 0 14px">Compare which political party held each ward in 2017 vs who won in the 2026 municipal election.</p>

        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:60px">Ward</th>
                <th>Reservation</th>
                <th>2017 Winner</th>
                <th>2017 Party</th>
                <th>2026 Winner</th>
                <th>2026 Party</th>
                <th>Election Outcome</th>
                <th style="text-align:right">Action</th>
              </tr>
            </thead>
            <tbody>
              ${w2026.map(w => {
                const prev = w2017Map[w.ward];
                const prevParty = prev ? prev.party : '–';
                const isRetained = prev && prevParty === w.party;
                const isFlipped = prev && prevParty !== w.party;

                return `
                  <tr class="r" onclick="openMyCorpWardModal(${w.ward})" style="cursor:pointer">
                    <td><b>Ward ${w.ward}</b></td>
                    <td><span class="badge" style="background:var(--s2);font-size:11px">${esc(w.res || 'General')}</span></td>
                    <td><span style="color:var(--text-2)">${prev ? esc(prev.candidate) : '–'}</span></td>
                    <td>
                      ${prev ? `
                        <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(prevParty)};font-size:11px">
                          ${esc(prevParty)}
                        </span>
                      ` : '<span class="note">–</span>'}
                    </td>
                    <td><b style="color:#4ade80">${esc(w.candidate)}</b></td>
                    <td>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w.party)};font-size:11px">
                        ${esc(w.party)}
                      </span>
                    </td>
                    <td>
                      ${isRetained ? `
                        <span style="color:#22c55e;font-weight:700;font-size:11.5px">🛡️ Retained (${esc(w.party)})</span>
                      ` : (isFlipped ? `
                        <span style="color:#f59e0b;font-weight:700;font-size:11.5px">🔄 Swung: ${esc(prevParty)} ➔ ${esc(w.party)}</span>
                      ` : '<span class="note">–</span>')}
                    </td>
                    <td style="text-align:right">
                      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();openMyCorpWardModal(${w.ward})">Details →</button>
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

  // 5: Party Tally & Majority Analysis View
  function renderMyCorpTallyView(container) {
    const corp = MYCORP_STATE.corp;
    const tally2026 = corp.party_tally_2026 || {};
    const tally2017 = corp.party_tally_2017 || {};
    const seatCount = corp.seat_count_2026 || corp.ward_count_2026 || 227;
    const majMark = Math.floor(seatCount / 2) + 1;

    // Collect all parties from both elections
    const partiesSet = new Set([...Object.keys(tally2026), ...Object.keys(tally2017)]);
    const parties = Array.from(partiesSet).map(p => {
      const s2026 = tally2026[p] || 0;
      const s2017 = tally2017[p] || 0;
      const diff = s2026 - s2017;
      return { party: p, s2026, s2017, diff };
    }).sort((a,b) => b.s2026 - a.s2026 || b.s2017 - a.s2017);

    // Alliance tallies
    const mahayuti = (tally2026['BJP'] || 0) + (tally2026['Shiv Sena'] || 0) + (tally2026['NCP'] || 0);
    const mva = (tally2026['Shiv Sena (UBT)'] || 0) + (tally2026['INC'] || 0) + (tally2026['NCP (SP)'] || 0);
    const others = seatCount - (mahayuti + mva);

    container.innerHTML = `
      <!-- Coalition Box -->
      <div class="g g3" style="gap:14px;margin-bottom:20px">
        <div class="card" style="border:1px solid #ff9933;background:rgba(255,153,51,0.08);border-radius:12px;padding:16px">
          <div style="font-size:11.5px;color:#ff9933;font-weight:800;letter-spacing:0.5px">COALITION 1: MAHAYUTI</div>
          <div style="font-size:28px;font-weight:800;color:var(--text);margin:4px 0">${mahayuti} <small style="font-size:14px;color:var(--text-2)">Seats</small></div>
          <div style="font-size:12px;color:var(--text-2)">BJP (${tally2026['BJP']||0}) + Shiv Sena (${tally2026['Shiv Sena']||0}) + NCP (${tally2026['NCP']||0})</div>
          <div style="margin-top:8px;font-size:12px;font-weight:700;color:${mahayuti>=majMark?'#4ade80':'#f59e0b'}">
            ${mahayuti >= majMark ? '🎉 Reached Clear Civic Majority' : 'Needs ' + (majMark - mahayuti) + ' more for majority'}
          </div>
        </div>

        <div class="card" style="border:1px solid #38bdf8;background:rgba(56,189,248,0.08);border-radius:12px;padding:16px">
          <div style="font-size:11.5px;color:#38bdf8;font-weight:800;letter-spacing:0.5px">COALITION 2: MAHA VIKAS AGHADI</div>
          <div style="font-size:28px;font-weight:800;color:var(--text);margin:4px 0">${mva} <small style="font-size:14px;color:var(--text-2)">Seats</small></div>
          <div style="font-size:12px;color:var(--text-2)">SS (UBT) (${tally2026['Shiv Sena (UBT)']||0}) + INC (${tally2026['INC']||0}) + NCP-SP (${tally2026['NCP (SP)']||0})</div>
          <div style="margin-top:8px;font-size:12px;font-weight:700;color:${mva>=majMark?'#4ade80':'#94a3b8'}">
            ${mva >= majMark ? '🎉 Reached Clear Civic Majority' : 'Strong Urban Opposition'}
          </div>
        </div>

        <div class="card" style="border:1px solid var(--b);background:var(--s1);border-radius:12px;padding:16px">
          <div style="font-size:11.5px;color:var(--text-2);font-weight:800;letter-spacing:0.5px">NON-ALIGNED &amp; INDEPENDENTS</div>
          <div style="font-size:28px;font-weight:800;color:var(--text);margin:4px 0">${others} <small style="font-size:14px;color:var(--text-2)">Seats</small></div>
          <div style="font-size:12px;color:var(--text-2)">AIMIM (${tally2026['AIMIM']||0}), MNS (${tally2026['MNS']||0}), SP (${tally2026['SP']||0})</div>
          <div style="margin-top:8px;font-size:12px;color:var(--text-2)">Can act as potential kingmakers</div>
        </div>
      </div>

      <!-- Party Table -->
      <div class="card" style="padding:0;overflow:hidden;border:1px solid var(--b);border-radius:10px">
        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:40px">#</th>
                <th>Political Party</th>
                <th style="text-align:right">2017 Won</th>
                <th style="text-align:right">2026 Won</th>
                <th style="text-align:right">Net Gain / Loss</th>
                <th>Seat Share %</th>
              </tr>
            </thead>
            <tbody>
              ${parties.map((p, i) => {
                const pColor = getPartyColor(p.party);
                const sharePct = ((p.s2026 / seatCount) * 100).toFixed(1);

                return `
                  <tr class="r">
                    <td>${i + 1}</td>
                    <td>
                      <div style="display:flex;align-items:center;gap:8px">
                        <span class="dot" style="background:${pColor};width:10px;height:10px;border-radius:50%"></span>
                        <b style="color:var(--text)">${esc(p.party)}</b>
                      </div>
                    </td>
                    <td style="text-align:right"><b>${p.s2017}</b></td>
                    <td style="text-align:right"><b style="color:#ff9933;font-size:15px">${p.s2026}</b></td>
                    <td style="text-align:right">
                      ${p.diff > 0 ? `
                        <b style="color:#22c55e">+${p.diff}</b>
                      ` : (p.diff < 0 ? `
                        <b style="color:#ef4444">${p.diff}</b>
                      ` : '<span class="note">0</span>')}
                    </td>
                    <td>
                      <div style="display:flex;align-items:center;gap:8px">
                        <span style="font-size:12px;font-weight:600;min-width:40px">${sharePct}%</span>
                        <div style="flex:1;height:6px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden">
                          <div style="width:${sharePct}%;background:${pColor};height:100%"></div>
                        </div>
                      </div>
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

  // Ward Deep-Dive Modal with Prev/Next Navigation
  window.openMyCorpWardModal = function(wardNo) {
    wardNo = parseInt(wardNo, 10);
    const corp = MYCORP_STATE.corp;
    if (!corp) return;

    const winners2026 = corp.winners_2026 || [];
    const winners2017 = corp.winners_2017 || [];
    const w2026 = winners2026.find(w => w.ward === wardNo) || { ward: wardNo, candidate: 'Candidate', party: 'Independent', votes: 0 };
    const w2017 = winners2017.find(w => w.ward === wardNo);

    const prevWard = wardNo > 1 ? wardNo - 1 : winners2026.length;
    const nextWard = wardNo < winners2026.length ? wardNo + 1 : 1;

    const modalWrap = document.getElementById('mycorp-modal-wrap');
    if (!modalWrap) return;

    const pColor = getPartyColor(w2026.party);

    modalWrap.innerHTML = `
      <div class="modal-backdrop" onclick="closeMyCorpWardModal()" style="position:fixed;inset:0;background:rgba(0,0,0,0.82);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#0b1428;border:1px solid var(--b);border-radius:14px;width:min(760px, 95vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 60px rgba(0,0,0,0.85);overflow:hidden">
          
          <!-- Header -->
          <div style="padding:18px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:flex-start;background:rgba(255,255,255,0.02)">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="badge" style="background:#ff9933;color:#000;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                  WARD No. ${w2026.ward}
                </span>
                ${w2026.res ? `
                  <span class="badge" style="background:var(--s2);color:var(--text);font-size:11px;padding:2px 8px;border-radius:4px">
                    ${esc(w2026.res)}
                  </span>
                ` : ''}
                <span class="badge" style="background:var(--s2);color:var(--text-2);font-size:11px;padding:2px 8px;border-radius:4px">
                  ${esc(corp.name)}
                </span>
              </div>
              <h2 style="margin:2px 0;font-size:20px;color:var(--text)">
                🗳️ Ward ${w2026.ward} Election Result Breakdown
              </h2>
            </div>
            <button class="btn" onclick="closeMyCorpWardModal()" style="padding:4px 10px;font-size:16px" title="Close">✕</button>
          </div>

          <!-- Body -->
          <div style="padding:22px;overflow-y:auto;flex:1">
            
            <!-- Head to Head Contest -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px">
              
              <!-- Elected Winner -->
              <div class="mycorp-winner-box" style="margin:0">
                <span style="font-size:10px;font-weight:800;color:#16a34a;text-transform:uppercase">ELECTED WINNER (2026)</span>
                <h3 style="margin:4px 0;font-size:17px;color:var(--text)">${esc(w2026.candidate)}</h3>
                <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};font-size:11.5px">
                  ${esc(w2026.party)}
                </span>
                <div style="margin-top:10px;font-size:13px;color:var(--text-2)">
                  Votes Polled: <b style="color:var(--text)">${fmt(w2026.votes)}</b> (${w2026.pct ? w2026.pct.toFixed(1) + '%' : '–'})
                </div>
              </div>

              <!-- Runner-up -->
              <div class="mycorp-runner-box" style="margin:0">
                <span style="font-size:10px;font-weight:800;color:var(--text-3);text-transform:uppercase">RUNNER-UP (2026)</span>
                <h3 style="margin:4px 0;font-size:17px;color:var(--text-2)">${esc(w2026.runner || 'Opposition')}</h3>
                <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w2026.runner_party)};font-size:11.5px">
                  ${esc(w2026.runner_party || 'Runner-Up')}
                </span>
                <div style="margin-top:10px;font-size:13px;color:var(--text-2)">
                  Votes Polled: <b style="color:var(--text-2)">${fmt(w2026.runner_votes)}</b>
                </div>
              </div>
            </div>

            <!-- Victory Margin Card -->
            <div class="card" style="background:var(--s2);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-size:11px;color:var(--text-2);text-transform:uppercase;font-weight:700">VICTORY MARGIN</div>
                <div style="font-size:22px;font-weight:800;color:#38bdf8;margin:2px 0">+${fmt(w2026.margin)} Votes</div>
              </div>
              <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:12px;padding:4px 10px;font-weight:700">
                ${w2026.votes && w2026.margin ? ((w2026.margin / w2026.votes) * 100).toFixed(1) + '% Margin' : 'Decisive'}
              </span>
            </div>

            <!-- Historical 2017 Result Comparison -->
            ${w2017 ? `
              <div class="card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px">
                <div style="font-size:11.5px;color:#ffd07a;font-weight:800;letter-spacing:0.5px;margin-bottom:6px">
                  📅 PREVIOUS 2017 ELECTION COMPARISON
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                  <div>
                    <div style="font-size:14px;font-weight:700;color:var(--text)">${esc(w2017.candidate)}</div>
                    <div style="font-size:12px;color:var(--text-2)">Party: <b>${esc(w2017.party)}</b> · ${fmt(w2017.votes)} votes</div>
                  </div>
                  <div style="text-align:right">
                    <span class="badge" style="background:var(--s2);color:${w2017.party === w2026.party ? '#22c55e' : '#f59e0b'};font-weight:700">
                      ${w2017.party === w2026.party ? '🛡️ Seat Retained by ' + esc(w2026.party) : '🔄 Seat Flipped: ' + esc(w2017.party) + ' ➔ ' + esc(w2026.party)}
                    </span>
                  </div>
                </div>
              </div>
            ` : ''}

          </div>

          <!-- Footer with Ward Prev / Next Controls -->
          <div style="padding:14px 22px;border-top:1px solid var(--b);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02)">
            <button class="btn" onclick="openMyCorpWardModal(${prevWard})">← Ward ${prevWard}</button>
            <span style="font-size:12px;color:var(--text-2)">Ward ${w2026.ward} of ${winners2026.length}</span>
            <button class="btn" onclick="openMyCorpWardModal(${nextWard})">Ward ${nextWard} →</button>
          </div>

        </div>
      </div>
    `;
    modalWrap.style.display = 'block';
  };

  window.closeMyCorpWardModal = function() {
    const modalWrap = document.getElementById('mycorp-modal-wrap');
    if (modalWrap) modalWrap.style.display = 'none';
  };
'''

# Insert before closing })();
if 'window.renderCorporationDetailPage =' not in js_content:
    last_brace_idx = js_content.rfind('})();')
    if last_brace_idx != -1:
        js_content = js_content[:last_brace_idx] + mycorp_engine + '\n' + js_content[last_brace_idx:]
    else:
        print("Warning: could not find closing })(); in mh-local-ui.js")

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Updated js/mh-local-ui.js successfully.")

# 2. Patch js/app.js
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Add routes corp, mycorporator, bmc
route_addition = """'mh-local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',
'corp':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id,tab):'<p>Loading Corporation…</p>',
'mycorporator':(id,tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage(id||'bmc',tab):'<p>Loading myCorporator…</p>',
'bmc':(tab)=>window.renderCorporationDetailPage?window.renderCorporationDetailPage('bmc',tab):'<p>Loading BMC…</p>',"""

app_js = app_js.replace("'mh-local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Municipal Elections…</p>',", route_addition)

# Update 'mh':(yr) route to intercept 'mumbai' or 'bmc' or 'bruhanmumbai-municipal-corporation'
mh_route_original = "'mh':(yr)=>{"
mh_route_replacement = """'mh':(yr,sub)=>{
  if(yr==='mumbai'||yr==='bmc'||yr==='corporation'||yr==='bruhanmumbai-municipal-corporation'){
    return window.renderCorporationDetailPage?window.renderCorporationDetailPage('bmc',sub):'<p>Loading BMC…</p>';
  }"""

app_js = app_js.replace(mh_route_original, mh_route_replacement)

# Update updateNavTabs to recognize corp, mycorporator, bmc
app_js = app_js.replace(
    "(p==='mh' && k.startsWith('mh'))",
    "(p==='mh-local' && (k==='mh-local'||k==='corp'||k==='bmc'||k==='mycorporator'||k==='municipal'||k==='corporations'||k==='local')) || (p==='mh' && k.startsWith('mh') && k!=='mh-local')"
)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Updated js/app.js successfully.")
