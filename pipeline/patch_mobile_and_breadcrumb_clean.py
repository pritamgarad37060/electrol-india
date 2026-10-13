import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

# ══════════════════════════════════════════════════════════════════════
# 1. Update js/mh-local-ui.js:
#    - renderStateFilterOptions: Return clean state name only (no counts, no emojis)
#    - renderMunicipalCorporationsSection: Home › Municipal Corporations › State
#    - renderMunicipalCouncilsSection: Home › Municipal Councils › State
#    - onStateFilterChange: update munc-bc-state dynamically
#    - quick state pills: clean names only
# ══════════════════════════════════════════════════════════════════════
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 1A. renderStateFilterOptions: Return clean state name only
old_state_opt = r'''  function renderStateFilterOptions(selectedState) {
    selectedState = selectedState || ACTIVE_STATE || 'Maharashtra';
    return ALL_INDIA_STATES.map(st => {
      const isSel = st.name.toLowerCase() === selectedState.toLowerCase();
      const badge = st.active ? '📍 ' : '';
      const countInfo = st.active ? ` (${st.corps} Corps, ${st.councils} Councils)` : '';
      return `<option value="${esc(st.name)}" ${isSel ? 'selected' : ''}>${badge}${esc(st.name)}${countInfo}</option>`;
    }).join('');
  }'''

new_state_opt = r'''  function renderStateFilterOptions(selectedState) {
    selectedState = selectedState || ACTIVE_STATE || 'Maharashtra';
    return ALL_INDIA_STATES.map(st => {
      const isSel = st.name.toLowerCase() === selectedState.toLowerCase();
      return `<option value="${esc(st.name)}" ${isSel ? 'selected' : ''}>${esc(st.name)}</option>`;
    }).join('');
  }'''

if old_state_opt in js_content:
    js_content = js_content.replace(old_state_opt, new_state_opt)
    print("Updated renderStateFilterOptions with clean state names (no counts/emojis).")
else:
    # Try with regex
    pat = re.compile(r'function renderStateFilterOptions\([^)]*\)\s*\{[\s\S]*?return ALL_INDIA_STATES\.map[\s\S]*?\}\.join\(\'\'\);\s*\}')
    if pat.search(js_content):
        js_content = pat.sub(new_state_opt.strip(), js_content)
        print("Updated renderStateFilterOptions via regex.")
    else:
        print("Warning: renderStateFilterOptions not matched.")

# 1B. Breadcrumb in renderMunicipalCorporationsSection
old_corp_bc = r'''        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('mh')">Maharashtra</a> <span>›</span>
          <span>Municipal Corporations (Mahanagar Palika)</span>
        </div>'''

new_corp_bc = r'''        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('corporations')">Municipal Corporations</a> <span>›</span>
          <span id="munc-bc-state">${esc(ACTIVE_STATE)}</span>
        </div>'''

if old_corp_bc in js_content:
    js_content = js_content.replace(old_corp_bc, new_corp_bc)
    print("Updated Corporations breadcrumb to 'Home › Municipal Corporations › State'.")

# 1C. Breadcrumb in renderMunicipalCouncilsSection
old_council_bc = r'''        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('mh')">Maharashtra</a> <span>›</span>
          <span>Municipal Councils (Nagar Parishads)</span>
        </div>'''

new_council_bc = r'''        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('councils')">Municipal Councils</a> <span>›</span>
          <span id="munc-bc-state">${esc(ACTIVE_STATE)}</span>
        </div>'''

if old_council_bc in js_content:
    js_content = js_content.replace(old_council_bc, new_council_bc)
    print("Updated Councils breadcrumb to 'Home › Municipal Councils › State'.")

# 1D. Clean quick state pills: remove any '📍 ' prefix from buttons
js_content = js_content.replace("${st.toLowerCase() === 'maharashtra' ? '📍 ' : ''}${st}", "${st}")

# 1E. Update onStateFilterChange to update munc-bc-state
old_onStateChange_anchor = r'''    // Update Top State Pills Active State
    document.querySelectorAll('.munc-top-pills-bar .tab-pill').forEach(btn => {
      const txt = (btn.textContent || '').trim().replace(/^📍\s*/, '');
      btn.classList.toggle('on', txt.toLowerCase() === ACTIVE_STATE.toLowerCase());
    });'''

new_onStateChange_anchor = r'''    // Update Breadcrumb State
    const bcState = document.getElementById('munc-bc-state');
    if (bcState) bcState.textContent = ACTIVE_STATE;

    // Update Top State Pills Active State
    document.querySelectorAll('.munc-top-pills-bar .tab-pill').forEach(btn => {
      const txt = (btn.textContent || '').trim().replace(/^📍\s*/, '');
      btn.classList.toggle('on', txt.toLowerCase() === ACTIVE_STATE.toLowerCase());
    });'''

if old_onStateChange_anchor in js_content:
    js_content = js_content.replace(old_onStateChange_anchor, new_onStateChange_anchor)
    print("Updated onStateFilterChange with dynamic breadcrumb state label.")

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Saved js/mh-local-ui.js.")

# ══════════════════════════════════════════════════════════════════════
# 2. Update css/style.css: Comprehensive Mobile Optimization
#    Covering every size: 320px, 360px, 390px, 412px, 480px, 640px, 768px
# ══════════════════════════════════════════════════════════════════════
with open('css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

mobile_enhancement_css = """
/* ═══════════════════════════════════════════════════════════════════
   COMPREHENSIVE MOBILE PHONE RESPONSIVENESS (EVERY SCREEN SIZE 320px+)
   ═══════════════════════════════════════════════════════════════════ */

/* Universal Breadcrumb Responsive Wrapping */
.bc {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 4px 6px !important;
  font-size: clamp(11.5px, 3.2vw, 13px) !important;
  line-height: 1.45 !important;
  word-break: break-word !important;
}

/* Tablet & Mobile Breakpoint (<= 768px) */
@media (max-width: 768px) {
  /* Prevent side-overflow on html / body */
  body, html {
    overflow-x: hidden !important;
    max-width: 100vw !important;
  }
  .w {
    padding: 10px 12px !important;
    max-width: 100vw !important;
    box-sizing: border-box !important;
  }

  /* Top Bar & State Filter */
  .munc-top-nav-bar {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    margin-bottom: 10px !important;
  }
  .munc-top-state-box {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    width: 100% !important;
  }
  .munc-top-state-select {
    flex: 1 !important;
    width: 100% !important;
    height: 42px !important;
    font-size: 14px !important; /* Prevents auto-zoom on iOS */
    padding: 8px 12px !important;
    border-radius: 8px !important;
  }

  /* Horizontal Smooth Swipeable Pills */
  .munc-top-pills-bar {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
    padding: 6px 10px !important;
    margin-bottom: 14px !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }
  .munc-top-pills-bar::-webkit-scrollbar {
    display: none !important;
  }
  .munc-top-pills-bar .tab-pill {
    flex-shrink: 0 !important;
    font-size: 12px !important;
    padding: 5px 12px !important;
  }
  .munc-top-pills-bar span {
    flex-shrink: 0 !important;
    font-size: 11px !important;
  }

  /* Civic Hero Section on Mobile */
  .mh-local-hero {
    padding: 16px 14px !important;
    border-radius: 12px !important;
    margin-bottom: 16px !important;
    box-sizing: border-box !important;
  }
  .mh-local-hero h1 {
    font-size: clamp(20px, 5.5vw, 28px) !important;
    margin: 4px 0 8px !important;
    word-break: break-word !important;
  }
  .mh-local-hero p {
    font-size: 13px !important;
    line-height: 1.45 !important;
  }
  
  /* Buttons inside hero */
  .mh-local-hero div:has(> button) {
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
    gap: 8px !important;
    margin-top: 10px !important;
  }
  .mh-local-hero button.btn {
    width: 100% !important;
    text-align: center !important;
    justify-content: center !important;
    padding: 10px 14px !important;
    font-size: 13px !important;
    box-sizing: border-box !important;
  }

  /* Hero Metric Cards (2x2 Grid) */
  .mh-local-hero .g4 {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 8px !important;
    margin-top: 16px !important;
  }
  .mh-local-hero .stat-card {
    padding: 10px 10px !important;
    border-radius: 8px !important;
    box-sizing: border-box !important;
  }
  .mh-local-hero .stat-card div:nth-child(1) {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
  }
  .mh-local-hero .stat-card div:nth-child(2) {
    font-size: clamp(18px, 5vw, 24px) !important;
    margin: 2px 0 !important;
  }
  .mh-local-hero .stat-card div:nth-child(3) {
    font-size: 10px !important;
    line-height: 1.3 !important;
  }

  /* Featured Portal Banners */
  #munc-featured-bmc-banner,
  #munc-featured-council-banner {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 12px !important;
    padding: 14px 14px !important;
    border-radius: 12px !important;
    box-sizing: border-box !important;
  }
  #munc-featured-bmc-banner button,
  #munc-featured-council-banner button {
    width: 100% !important;
    text-align: center !important;
    justify-content: center !important;
    padding: 10px 14px !important;
    font-size: 13.5px !important;
    box-sizing: border-box !important;
  }

  /* Compact Toolbar Controls */
  .munc-compact-toolbar {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    padding: 12px !important;
    box-sizing: border-box !important;
  }
  .munc-compact-search-box {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    box-sizing: border-box !important;
  }
  .munc-compact-search-box input {
    width: 100% !important;
    height: 42px !important;
    font-size: 14px !important;
    box-sizing: border-box !important;
  }
  .munc-compact-toolbar select {
    width: 100% !important;
    height: 40px !important;
    font-size: 13.5px !important;
    box-sizing: border-box !important;
  }

  /* Municipal Corporations / Councils Cards Grid */
  .g3 {
    grid-template-columns: 1fr !important;
    gap: 12px !important;
  }
  .card {
    padding: 14px 14px !important;
    box-sizing: border-box !important;
  }

  /* Tables on mobile */
  .tbl, table {
    display: block !important;
    width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    box-sizing: border-box !important;
  }

  /* Council / Corporation Detail Views */
  .mycorp-hero {
    padding: 14px 14px !important;
    border-radius: 12px !important;
    box-sizing: border-box !important;
  }
  .mycorp-title {
    font-size: clamp(19px, 5.2vw, 26px) !important;
  }
  .mycorp-hero div:has(> select#mycouncil-switcher),
  .mycorp-hero div:has(> select#mycorp-switcher) {
    width: 100% !important;
    align-items: stretch !important;
    margin-top: 10px !important;
  }
  #mycouncil-switcher, #mycorp-switcher {
    width: 100% !important;
    max-width: 100% !important;
  }
  .mycorp-tabs-bar {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none !important;
    padding-bottom: 6px !important;
  }
  .mycorp-tabs-bar::-webkit-scrollbar {
    display: none !important;
  }
  .mycorp-tab-btn {
    flex-shrink: 0 !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
  }

  /* Modals on Mobile */
  .modal-dialog {
    max-width: 95vw !important;
    width: 95vw !important;
    margin: 8px auto !important;
    max-height: 92vh !important;
    border-radius: 12px !important;
    box-sizing: border-box !important;
  }
  .modal-dialog [style*="grid-template-columns: 1fr 1fr"],
  .modal-dialog [style*="grid-template-columns:1fr 1fr"] {
    grid-template-columns: 1fr !important;
    gap: 10px !important;
  }
}

/* Extra Small Phones (320px - 380px) */
@media (max-width: 380px) {
  .mh-local-hero .g4 {
    grid-template-columns: 1fr 1fr !important;
    gap: 6px !important;
  }
  .mh-local-hero .stat-card {
    padding: 8px 6px !important;
  }
  .mh-local-hero .stat-card div:nth-child(2) {
    font-size: 18px !important;
  }
  .badge {
    font-size: 10px !important;
    padding: 2px 6px !important;
  }
  .btn {
    font-size: 11.5px !important;
  }
}
"""

if 'COMPREHENSIVE MOBILE PHONE RESPONSIVENESS' not in css_content:
    css_content += "\n" + mobile_enhancement_css
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Appended comprehensive mobile phone responsiveness CSS.")
else:
    # Replace existing block with the updated one
    pat = re.compile(r'/\* ═══════════════════════════════════════════════════════════════\s*COMPREHENSIVE MOBILE PHONE RESPONSIVENESS[\s\S]*', re.MULTILINE)
    css_content = pat.sub(mobile_enhancement_css.strip(), css_content)
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Replaced existing mobile responsiveness block with updated rules.")

print("All updates applied successfully.")
