import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

# ══════════════════════════════════════════════════════════════════════
# 1. Update css/style.css with sleek Top State Bar & Pills styles
# ══════════════════════════════════════════════════════════════════════
with open('css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

top_state_bar_css = """
/* ── Sleek Top State Filter Bar & Quick Pills ─────────────────────── */
.munc-top-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}
.munc-top-state-box {
  display: flex;
  align-items: center;
  gap: 8px;
}
.munc-top-state-select {
  padding: 8px 14px;
  border-radius: 8px;
  background: var(--s1);
  color: var(--text);
  border: 1px solid var(--b);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}
.munc-top-state-select:hover,
.munc-top-state-select:focus {
  border-color: #ff9933;
  box-shadow: 0 0 10px rgba(255,153,51,0.25);
  outline: none;
}
.munc-top-pills-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--b);
  border-radius: 10px;
  padding: 8px 12px;
}
@media (max-width: 768px) {
  .munc-top-nav-bar {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
  }
  .munc-top-state-box {
    justify-content: space-between !important;
    width: 100% !important;
  }
  .munc-top-state-select {
    flex: 1 !important;
  }
  .munc-top-pills-bar {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    padding-bottom: 8px !important;
  }
  .munc-top-pills-bar .tab-pill {
    flex-shrink: 0 !important;
  }
}
"""

if '.munc-top-nav-bar' not in css_content:
    css_content += "\n" + top_state_bar_css
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Updated css/style.css with top state bar styles.")

# ══════════════════════════════════════════════════════════════════════
# 2. Update js/mh-local-ui.js:
#    - renderHeroHeader for Councils to match Corporations perfectly
#    - onStateFilterChange to update top state pills
#    - renderMunicipalCorporationsSection with top state filter & NO step card
#    - renderMunicipalCouncilsSection with top state filter & NO step card
# ══════════════════════════════════════════════════════════════════════
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 2A. Update renderHeroHeader
# Replace councils hero block in renderHeroHeader
old_councils_hero = r'''      if (isMh) {
        return `
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
                  🏢 Maharashtra Municipal Councils
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
        `;'''

new_councils_hero = r'''      if (isMh) {
        return `
          <div class="mh-local-hero">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
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
                <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">224</div>
                <div style="font-size:11.5px;color:var(--text-2)">Akluj, Ambarnath, Barshi, Beed, etc.</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">COUNCILLOR SEATS</div>
                <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">5,389</div>
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
        `;'''

# Also update Corporations title from "🏛️ Maharashtra Municipal Corporations" to "🏛️ Municipal Corporations"
old_corp_title = '<h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">\n                  🏛️ Maharashtra Municipal Corporations\n                </h1>'
new_corp_title = '<h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">\n                  🏛️ Municipal Corporations\n                </h1>'

if old_corp_title in js_content:
    js_content = js_content.replace(old_corp_title, new_corp_title)
    print("Updated Corporations hero title to '🏛️ Municipal Corporations'.")

if old_councils_hero in js_content:
    js_content = js_content.replace(old_councils_hero, new_councils_hero)
    print("Updated Councils hero section to match Municipal Corporations.")
else:
    # Try normalizing newlines
    old_councils_hero_norm = old_councils_hero.replace('\r\n', '\n')
    js_content_norm = js_content.replace('\r\n', '\n')
    if old_councils_hero_norm in js_content_norm:
        js_content = js_content_norm.replace(old_councils_hero_norm, new_councils_hero)
        print("Updated Councils hero section (normalized newlines).")
    else:
        print("Warning: old_councils_hero not matched exactly.")

# Also update non-active state councils hero header background to .mh-local-hero
js_content = js_content.replace(
    '<div class="mh-local-hero" style="background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(19,136,8,0.10) 100%);border-color:rgba(56,189,248,0.3)">',
    '<div class="mh-local-hero">'
)
js_content = js_content.replace(
    '<div class="mh-local-hero" style="background:linear-gradient(135deg, rgba(255,107,0,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(56,189,248,0.10) 100%);border-color:rgba(255,153,51,0.3)">',
    '<div class="mh-local-hero">'
)

# 2B. Update onStateFilterChange to update top state pills
old_onStateFilterChange = """    // 1. Dynamic Hero Header Update (changes attached image / hero banner)
    const heroWrap = document.getElementById('munc-hero-wrap');
    if (heroWrap) {
      heroWrap.innerHTML = renderHeroHeader(ACTIVE_SECTION, ACTIVE_STATE);
    }"""

new_onStateFilterChange = """    // 1. Dynamic Hero Header Update (changes attached image / hero banner)
    const heroWrap = document.getElementById('munc-hero-wrap');
    if (heroWrap) {
      heroWrap.innerHTML = renderHeroHeader(ACTIVE_SECTION, ACTIVE_STATE);
    }

    // Update Top State Pills Active State
    document.querySelectorAll('.munc-top-pills-bar .tab-pill').forEach(btn => {
      const txt = (btn.textContent || '').trim().replace(/^📍\\s*/, '');
      btn.classList.toggle('on', txt.toLowerCase() === ACTIVE_STATE.toLowerCase());
    });"""

if old_onStateFilterChange in js_content:
    js_content = js_content.replace(old_onStateFilterChange, new_onStateFilterChange)
    print("Updated onStateFilterChange with top pill synchronization.")

# 2C. Update renderMunicipalCorporationsSection
# Replace from `<!-- Breadcrumb -->` down to `<!-- Featured BMC myCorporator Banner`
corp_pattern = re.compile(
    r'(window\.renderMunicipalCorporationsSection\s*=\s*function\(stateParam,\s*yearParam\)\s*\{[\s\S]*?return\s*`)\s*<!-- Breadcrumb -->[\s\S]*?(<!-- Featured BMC myCorporator Banner)',
    re.MULTILINE
)

new_corp_top = r'''\1
      <!-- Top Bar: Breadcrumb + State Filter -->
      <div class="munc-top-nav-bar">
        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('mh')">Maharashtra</a> <span>›</span>
          <span>Municipal Corporations (Mahanagar Palika)</span>
        </div>
        <div class="munc-top-state-box">
          <span style="font-size:12px;font-weight:700;color:var(--text-2);display:flex;align-items:center;gap:4px">
            📍 Select State:
          </span>
          <select id="munc-state-filter" class="munc-top-state-select" onchange="onStateFilterChange(this.value)">
            ${renderStateFilterOptions(ACTIVE_STATE)}
          </select>
        </div>
      </div>

      <!-- Top Quick State Selection Pills -->
      <div class="munc-top-pills-bar">
        <span style="font-size:11px;font-weight:800;color:var(--text-3);text-transform:uppercase;letter-spacing:0.5px;margin-right:4px">Quick State:</span>
        ${['Maharashtra', 'Andhra Pradesh', 'Delhi (NCT)', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal'].map(st => `
          <button class="tab-pill ${st.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="padding:4px 10px;font-size:12px;margin:0;cursor:pointer" onclick="onStateFilterChange('${st}')">
            ${st.toLowerCase() === 'maharashtra' ? '📍 ' : ''}${st}
          </button>
        `).join('')}
      </div>

      <!-- Dedicated Corporations Hero Header (Dynamic - Updates with State Selection) -->
      <div id="munc-hero-wrap">
        ${renderHeroHeader('corps', ACTIVE_STATE)}
      </div>

      \2'''

if corp_pattern.search(js_content):
    js_content = corp_pattern.sub(new_corp_top, js_content)
    print("Replaced Corporations top section with clean Top State Filter and removed step card.")
else:
    print("Warning: corp_pattern did not match.")

# 2D. Update renderMunicipalCouncilsSection
# Replace from `<!-- Breadcrumb -->` down to `<!-- Compact Sleek Filter Toolbar -->`
councils_pattern = re.compile(
    r'(window\.renderMunicipalCouncilsSection\s*=\s*function\(stateParam,\s*yearParam\)\s*\{[\s\S]*?return\s*`)\s*<!-- Breadcrumb -->[\s\S]*?(<!-- Compact Sleek Filter Toolbar -->)',
    re.MULTILINE
)

new_councils_top = r'''\1
      <!-- Top Bar: Breadcrumb + State Filter -->
      <div class="munc-top-nav-bar">
        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('mh')">Maharashtra</a> <span>›</span>
          <span>Municipal Councils (Nagar Parishads)</span>
        </div>
        <div class="munc-top-state-box">
          <span style="font-size:12px;font-weight:700;color:var(--text-2);display:flex;align-items:center;gap:4px">
            📍 Select State:
          </span>
          <select id="munc-state-filter" class="munc-top-state-select" onchange="onStateFilterChange(this.value)">
            ${renderStateFilterOptions(ACTIVE_STATE)}
          </select>
        </div>
      </div>

      <!-- Top Quick State Selection Pills -->
      <div class="munc-top-pills-bar">
        <span style="font-size:11px;font-weight:800;color:var(--text-3);text-transform:uppercase;letter-spacing:0.5px;margin-right:4px">Quick State:</span>
        ${['Maharashtra', 'Andhra Pradesh', 'Delhi (NCT)', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'West Bengal'].map(st => `
          <button class="tab-pill ${st.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="padding:4px 10px;font-size:12px;margin:0;cursor:pointer" onclick="onStateFilterChange('${st}')">
            ${st.toLowerCase() === 'maharashtra' ? '📍 ' : ''}${st}
          </button>
        `).join('')}
      </div>

      <!-- Dedicated Councils Hero Header (Dynamic - Updates with State Selection) -->
      <div id="munc-hero-wrap">
        ${renderHeroHeader('councils', ACTIVE_STATE)}
      </div>

      <!-- Featured Ambarnath myCorporator Banner (For Maharashtra) -->
      <div id="munc-featured-council-banner" style="display:${(ACTIVE_STATE.toLowerCase() === 'maharashtra') ? 'flex' : 'none'};margin:0 0 16px;background:linear-gradient(135deg, rgba(56,189,248,0.14) 0%, rgba(15,23,42,0.92) 100%);border:1px solid rgba(56,189,248,0.45);border-radius:14px;padding:16px 20px;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 10px 30px rgba(0,0,0,0.45)">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span class="mycorp-brand-pill" style="background:linear-gradient(90deg, #38bdf8, #0284c7);color:#fff">FEATURED CIVIC HUB</span>
            <span class="mycorp-stat-pill">59 SEATS · 30 MAJORITY MARK</span>
            <span class="mycorp-stat-pill">THANE DISTRICT</span>
          </div>
          <h2 style="margin:2px 0 4px;font-size:19px;color:var(--text);display:flex;align-items:center;gap:8px">
            🏢 Ambarnath Municipal Council — myCorporator Portal
          </h2>
          <p style="margin:0;font-size:13px;color:var(--text-2);max-width:760px;line-height:1.45">
            Explore ward-by-ward councillor election results, directly-elected President details, party tally, and candidate rosters.
          </p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn on" style="padding:9px 18px;font-size:13px;font-weight:700;background:linear-gradient(90deg, #38bdf8, #0284c7);color:#fff;border:none;box-shadow:0 4px 16px rgba(56,189,248,0.45);cursor:pointer" onclick="go('council/ambarnath')">
            Open Ambarnath Portal (59 Seats) →
          </button>
        </div>
      </div>

      \2'''

if councils_pattern.search(js_content):
    js_content = councils_pattern.sub(new_councils_top, js_content)
    print("Replaced Councils top section with clean Top State Filter and removed step card.")
else:
    print("Warning: councils_pattern did not match.")

# Write back js/mh-local-ui.js
with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Finished updating js/mh-local-ui.js.")
