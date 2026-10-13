import re

# ═══════════════════════════════════════════════════════════════════
# 1. Patch js/app.js - Fix locMap (State map on load, complete India map)
# ═══════════════════════════════════════════════════════════════════
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

new_loc_map = r'''function locMap(id){
  lazy('GEO','js/geo-ls.js').then(()=>{
    const b=$('lm'),c=PC[id];if(!b||!c)return;
    const feat=GEO.f.find(x=>x[0]===c.id);
    if(!feat){
      b.innerHTML=`<svg viewBox="0 0 ${GEO.w} ${GEO.h}" width="100%" style="max-height:260px">${GEO.f.map(x=>`<path d="${x[3]}" fill="${x[0]===c.id?col(c.w[3]):'var(--b)'}"/>`).join('')}</svg>`;
      return;
    }

    // Compute Constituency Bounding Box for Big Zoom
    const nums=feat[3].match(/-?\d+\.?\d*/g).map(Number);
    let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
    for(let k=0;k<nums.length;k+=2){
      minX=Math.min(minX,nums[k]);maxX=Math.max(maxX,nums[k]);
      minY=Math.min(minY,nums[k+1]);maxY=Math.max(maxY,nums[k+1]);
    }
    const cW=maxX-minX,cH=maxY-minY;
    const pad=Math.max(cW,cH)*0.36;
    const vbZoom=[minX-pad,minY-pad,cW+2*pad,cH+2*pad].map(n=>n.toFixed(1)).join(' ');

    // State Bounding Box
    const stateFeats=GEO.f.filter(x=>{const pc=x[0]>=0?PC[x[0]]:null;return pc&&pc.si===c.si});
    let sMinX=1e9,sMaxX=-1e9,sMinY=1e9,sMaxY=-1e9;
    stateFeats.forEach(x=>{
      const sn=x[3].match(/-?\d+\.?\d*/g).map(Number);
      for(let k=0;k<sn.length;k+=2){
        sMinX=Math.min(sMinX,sn[k]);sMaxX=Math.max(sMaxX,sn[k]);
        sMinY=Math.min(sMinY,sn[k+1]);sMaxY=Math.max(sMaxY,sn[k+1]);
      }
    });
    const sPad=Math.max(sMaxX-sMinX,sMaxY-sMinY)*0.10;
    const vbState=[sMinX-sPad,sMinY-sPad,(sMaxX-sMinX)+2*sPad,(sMaxY-sMinY)+2*sPad].map(n=>n.toFixed(1)).join(' ');
    const vbIndia=`0 0 ${GEO.w} ${GEO.h}`;

    const cX=((minX+maxX)/2).toFixed(1);
    const cY=((minY+maxY)/2).toFixed(1);

    // Default view on load: STATE VIEW with constituency popped in it!
    b.innerHTML=`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px">
        <div class="tab-pills" style="margin:0">
          <button class="tab-pill on" id="lm-btn-state" onclick="setLocView('${vbState}','state')">🗺️ ${esc(S[c.si])} (State Map)</button>
          <button class="tab-pill" id="lm-btn-zoom" onclick="setLocView('${vbZoom}','zoom')">🔍 Constituency Zoom</button>
          <button class="tab-pill" id="lm-btn-india" onclick="setLocView('${vbIndia}','india')">🇮🇳 All India Map</button>
        </div>
        <button class="btn on" onclick="openBigConstituencyModal(${c.id})" style="padding:4px 10px;font-size:12px">⛶ Enlarge / Big Popup</button>
      </div>

      <div style="background:#060a14;border:1px solid var(--b);border-radius:8px;overflow:hidden;position:relative">
        <svg id="lm-svg" viewBox="${vbState}" width="100%" style="height:min(350px, 46vh);display:block;transition:all 0.3s ease">
          <!-- All India background boundaries -->
          <g id="lm-india-bg">
            ${GEO.f.filter(x=>x[0]!==c.id && (!PC[x[0]] || PC[x[0]].si!==c.si)).map(x=>`<path d="${x[3]}" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" stroke-width="0.5" vector-effect="non-scaling-stroke"/>`).join('')}
          </g>

          <!-- Current state background constituencies -->
          <g id="lm-state-bg">
            ${stateFeats.filter(x=>x[0]!==c.id).map(x=>`<path d="${x[3]}" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.22)" stroke-width="0.8" vector-effect="non-scaling-stroke"/>`).join('')}
          </g>

          <!-- Selected constituency (POPPED OUT) -->
          <path d="${feat[3]}" fill="${col(c.w[3])}" stroke="#ffffff" stroke-width="2.6" vector-effect="non-scaling-stroke" style="filter:drop-shadow(0 0 14px ${col(c.w[3])})"/>

          <!-- Glowing Beacon Pin -->
          <circle cx="${cX}" cy="${cY}" r="5" fill="#ffffff" stroke="${col(c.w[3])}" stroke-width="2" vector-effect="non-scaling-stroke"/>
          <circle cx="${cX}" cy="${cY}" r="10" fill="none" stroke="#ffffff" stroke-width="1.4" opacity="0.8" vector-effect="non-scaling-stroke" style="animation:pulse 2s infinite"/>
        </svg>

        <div style="position:absolute;bottom:8px;left:8px;background:rgba(11,20,40,0.88);backdrop-filter:blur(6px);padding:5px 10px;border-radius:6px;border:1px solid var(--b);font-size:11.5px;display:flex;align-items:center;gap:6px">
          ${dot(c.w[3])} <b>${esc(c.n)}</b> · <span style="color:#ff9933;font-weight:700">${esc(lab(c.w[3]))}</span> (${esc(S[c.si])})
        </div>
      </div>
    `;
  });
}'''

# Replace locMap function in app_js
locmap_match = re.search(r'function locMap\(id\)\{.*?(?=window\.setLocView)', app_js, re.DOTALL)
if locmap_match:
    app_js = app_js[:locmap_match.start()] + new_loc_map + '\n\n' + app_js[locmap_match.end():]
    print("Patched locMap in js/app.js successfully.")
else:
    print("Warning: could not regex match locMap in js/app.js")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

# ═══════════════════════════════════════════════════════════════════
# 2. Patch css/style.css - Add compact search bar and position styles
# ═══════════════════════════════════════════════════════════════════
with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css_addition = r'''
/* ── Compact Search & Filter Toolbar ────────────────────────── */
.munc-compact-toolbar {
  background: var(--s1);
  border: 1px solid var(--b);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}
.munc-compact-search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 240px;
  max-width: 420px;
  position: relative;
}
.munc-compact-search-box input {
  width: 100%;
  height: 36px;
  padding: 6px 12px 6px 34px !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  background: var(--s2) !important;
  border: 1px solid var(--b) !important;
  color: var(--text) !important;
}
.munc-search-icon-svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-3);
  pointer-events: none;
}
.munc-filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.munc-filter-group select {
  height: 36px;
  padding: 4px 10px;
  font-size: 12.5px;
  border-radius: 8px;
  background: var(--s2);
  border: 1px solid var(--b);
  color: var(--text);
}

/* State & Year Selector Layer Gateway */
.civic-gateway-card {
  background: linear-gradient(135deg, rgba(255,107,0,0.12) 0%, rgba(15,23,42,0.92) 50%, rgba(56,189,248,0.10) 100%);
  border: 1px solid rgba(255,153,51,0.35);
  border-radius: 14px;
  padding: 18px 22px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
:root[data-theme=light] .civic-gateway-card {
  background: linear-gradient(135deg, rgba(255,107,0,0.08) 0%, #ffffff 50%, rgba(56,189,248,0.08) 100%);
  border-color: rgba(255,153,51,0.3);
}

/* 3rd and 4th position styling */
.mycorp-other-cands {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--b);
  border-radius: 6px;
  padding: 6px 10px;
  margin-top: 6px;
  font-size: 11.5px;
  color: var(--text-2);
}
:root[data-theme=light] .mycorp-other-cands {
  background: #f8fafc;
  border-color: #e2e8f0;
}
'''

if '.munc-compact-toolbar' not in css:
    css += '\n' + css_addition
    with open('css/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added compact search styles to css/style.css.")

print("Patching complete.")
