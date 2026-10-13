import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

# ══════════════════════════════════════════════════════════════════════
# 1. Update js/mh-local-ui.js:
#    - Remove hardcoded inline dark backgrounds from heroes and boxes
#    - Ensure clean structure in renderMunicipalCorporationsSection & Councils
# ══════════════════════════════════════════════════════════════════════
with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Replace hardcoded dark background on council detail hero
old_council_detail_hero = r'''<div class="mycorp-hero" style="border-color:rgba(56,189,248,0.35);background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.88) 50%, rgba(19,136,8,0.10) 100%)">'''
new_council_detail_hero = r'''<div class="mycorp-hero council-detail-hero">'''
if old_council_detail_hero in js_content:
    js_content = js_content.replace(old_council_detail_hero, new_council_detail_hero)
    print("Replaced inline dark gradient on Council detail hero.")

# Replace hardcoded dark background on majority bar box in Council detail
old_maj_box = r'''<div style="margin-top:16px;background:rgba(0,0,0,0.22);border:1px solid var(--b);border-radius:8px;padding:12px 14px">'''
new_maj_box = r'''<div class="mycorp-majority-bar-box" style="margin-top:16px;border:1px solid var(--b);border-radius:8px;padding:12px 14px">'''
if old_maj_box in js_content:
    js_content = js_content.replace(old_maj_box, new_maj_box)
    print("Added class mycorp-majority-bar-box for theme-aware majority bar.")

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Updated js/mh-local-ui.js.")

# ══════════════════════════════════════════════════════════════════════
# 2. Update css/style.css:
#    - Fix quick states overlapping with filter
#    - Robust Light Mode overrides for .mycorp-hero, .mh-local-hero,
#      stat cards, party seat distribution, and featured banners
# ══════════════════════════════════════════════════════════════════════
with open('css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

theme_and_layout_fix = """
/* ═══════════════════════════════════════════════════════════════════
   PREVENT QUICK STATES OVERLAPPING & COMPREHENSIVE LIGHT THEME STYLING
   ═══════════════════════════════════════════════════════════════════ */

/* Clear layout separation to prevent quick states overlapping with filter */
.munc-top-nav-bar {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 12px 20px !important;
  margin-bottom: 12px !important;
  width: 100% !important;
  clear: both !important;
  position: static !important;
  box-sizing: border-box !important;
}

.munc-top-state-box {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex-shrink: 0 !important;
  margin-left: auto !important;
}

.munc-top-pills-bar {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex-wrap: wrap !important;
  margin-top: 4px !important;
  margin-bottom: 20px !important;
  width: 100% !important;
  clear: both !important;
  position: static !important;
  box-sizing: border-box !important;
}

/* Majority Bar Container in Council & Corp details */
.mycorp-majority-bar-box {
  background: rgba(0, 0, 0, 0.22);
}

/* ── Light Mode Complete High-Contrast System ─────────────────────── */
:root[data-theme=light] {
  --bg: #f8fafc;
  --surface: #ffffff;
  --s1: #f1f5f9;
  --s2: #e2e8f0;
  --b: rgba(0, 0, 0, 0.12);
  --text: #0f172a;
  --text-2: #475569;
  --text-3: #64748b;
}

/* Light Mode: myCorporator Hero (Council & Corporation Portal) */
:root[data-theme=light] .mycorp-hero,
:root[data-theme=light] .council-detail-hero {
  background: linear-gradient(135deg, rgba(56,189,248,0.10) 0%, #ffffff 50%, rgba(255,153,51,0.08) 100%) !important;
  border-color: rgba(56,189,248,0.35) !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06) !important;
  color: #0f172a !important;
}

:root[data-theme=light] .mycorp-title,
:root[data-theme=light] .mycorp-hero h1,
:root[data-theme=light] .mycorp-hero h2,
:root[data-theme=light] .mycorp-hero h3 {
  color: #0f172a !important;
}

:root[data-theme=light] .mycorp-hero p {
  color: #475569 !important;
}

/* Light Mode: Stat Cards inside Heroes */
:root[data-theme=light] .mycorp-hero .stat-card,
:root[data-theme=light] .mh-local-hero .stat-card {
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.12) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
  color: #0f172a !important;
}

:root[data-theme=light] .mycorp-hero .stat-card div:first-child,
:root[data-theme=light] .mh-local-hero .stat-card div:first-child {
  color: #475569 !important;
  font-weight: 700 !important;
}

:root[data-theme=light] .mycorp-hero .stat-card div:last-child,
:root[data-theme=light] .mh-local-hero .stat-card div:last-child {
  color: #64748b !important;
}

/* Light Mode: Party Distribution Bar Box */
:root[data-theme=light] .mycorp-majority-bar-box {
  background: #f8fafc !important;
  border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

:root[data-theme=light] .mycorp-majority-bar-box span {
  color: #0f172a !important;
}

/* Light Mode: Municipal Corporations & Councils Hero Header */
:root[data-theme=light] .mh-local-hero {
  background: linear-gradient(135deg, rgba(255,153,51,0.12) 0%, #ffffff 50%, rgba(56,189,248,0.10) 100%) !important;
  border-color: rgba(0, 0, 0, 0.12) !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06) !important;
  color: #0f172a !important;
}

:root[data-theme=light] .mh-local-hero h1 {
  color: #0f172a !important;
}

:root[data-theme=light] .mh-local-hero p {
  color: #475569 !important;
}

/* Light Mode: Featured Banners (BMC & Ambarnath) */
:root[data-theme=light] #munc-featured-bmc-banner,
:root[data-theme=light] #munc-featured-council-banner {
  background: linear-gradient(135deg, rgba(255,153,51,0.10) 0%, #ffffff 50%, rgba(56,189,248,0.08) 100%) !important;
  border: 1px solid rgba(0, 0, 0, 0.12) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
}

:root[data-theme=light] #munc-featured-bmc-banner h2,
:root[data-theme=light] #munc-featured-council-banner h2 {
  color: #0f172a !important;
}

:root[data-theme=light] #munc-featured-bmc-banner p,
:root[data-theme=light] #munc-featured-council-banner p {
  color: #475569 !important;
}

/* Light Mode: Pills Bar in Local Hub */
:root[data-theme=light] .munc-top-pills-bar {
  background: #f1f5f9 !important;
  border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

:root[data-theme=light] .munc-top-state-select {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: rgba(0, 0, 0, 0.15) !important;
}

:root[data-theme=light] .munc-compact-toolbar {
  background: #ffffff !important;
  border-color: rgba(0, 0, 0, 0.12) !important;
}

:root[data-theme=light] .munc-compact-search-box input {
  background: #f8fafc !important;
  color: #0f172a !important;
  border-color: rgba(0, 0, 0, 0.12) !important;
}

:root[data-theme=light] .munc-compact-toolbar select {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: rgba(0, 0, 0, 0.12) !important;
}

:root[data-theme=light] .mycorp-stat-pill {
  background: #f1f5f9 !important;
  color: #334155 !important;
  border-color: rgba(0, 0, 0, 0.12) !important;
}

/* RTL Urdu Layout Engine */
html[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

html[dir="rtl"] .bc,
html[dir="rtl"] .munc-top-nav-bar,
html[dir="rtl"] .nav-top {
  direction: rtl;
}

html[dir="rtl"] .munc-top-state-box {
  margin-left: 0 !important;
  margin-right: auto !important;
}

html[dir="rtl"] .munc-search-icon-svg {
  left: unset !important;
  right: 14px !important;
}

html[dir="rtl"] .munc-compact-search-box input {
  padding-left: 14px !important;
  padding-right: 40px !important;
  text-align: right;
}

html[dir="rtl"] .mycorp-winner-box,
html[dir="rtl"] .mycorp-runner-box {
  text-align: right;
}
"""

if 'PREVENT QUICK STATES OVERLAPPING' not in css_content:
    css_content += "\n" + theme_and_layout_fix
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Appended light mode and quick states layout fixes to css/style.css.")
else:
    pat = re.compile(r'/\* ═══════════════════════════════════════════════════════════════\s*PREVENT QUICK STATES OVERLAPPING[\s\S]*', re.MULTILINE)
    css_content = pat.sub(theme_and_layout_fix.strip(), css_content)
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Replaced light mode styling in css/style.css.")
