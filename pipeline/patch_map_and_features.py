"""
Patch js/app.js cleanly with exact string replacements
"""
with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add mh-local routes if not already added
if "'mh-local':" not in content:
    old_routes = "'members':()=>window.renderLsMembersHub?window.renderLsMembersHub():'<p>Loading Lok Sabha members…</p>',"
    new_routes = """'mh-local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Maharashtra Local Bodies…</p>',
'local':()=>window.renderMhLocalHub?window.renderMhLocalHub():'<p>Loading Maharashtra Local Bodies…</p>',
'members':()=>window.renderLsMembersHub?window.renderLsMembersHub():'<p>Loading Lok Sabha members…</p>',"""
    content = content.replace(old_routes, new_routes, 1)
    print("1. Added mh-local routes")
else:
    print("1. mh-local route already present")

# 2. Add Local Bodies banner to Maharashtra Assembly view
mh_old = "initMH();const d=MH.ps.filter(p=>p.seats),al={Mahayuti:0,MVA:0,Others:0};d.forEach(p=>al[mal(p.c)]+=p.seats);\n  return`${bc([['Home',''],['Maharashtra Assembly 2024']])}"
mh_banner = """<div class="card" style="background:linear-gradient(135deg, rgba(255,153,51,0.12), rgba(56,189,248,0.12));border:1px solid rgba(255,153,51,0.3);margin-bottom:14px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;border-radius:10px">
  <div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
      <span class="badge" style="background:#ff9933;color:#000;font-weight:700;font-size:10.5px">URBAN LOCAL ELECTIONS</span>
      <b style="font-size:15px;color:var(--text)">🏢 Maharashtra Urban Local Bodies Hub</b>
    </div>
    <div style="font-size:12.5px;color:var(--text-2)">
      Explore <b>29 Municipal Corporations</b> (BMC, Pune, Thane, Nagpur, etc.) &amp; <b>224 Municipal Councils</b> with Ward results &amp; Presidents.
    </div>
  </div>
  <button class="btn on" onclick="go('mh-local')" style="white-space:nowrap">Explore Local Bodies →</button>
</div>"""
mh_new = f"initMH();const d=MH.ps.filter(p=>p.seats),al={{Mahayuti:0,MVA:0,Others:0}};d.forEach(p=>al[mal(p.c)]+=p.seats);\n  return`${{bc([['Home',''],['Maharashtra Assembly 2024']])}}\n  {mh_banner}"

if mh_old in content:
    content = content.replace(mh_old, mh_new, 1)
    print("2. Added Local Bodies banner to Maharashtra Assembly")
else:
    print("2. Local Bodies banner check: already present or different")

# 3. Patch Map paths and party filter
map_target = """const paths=vis.map(x=>{const nm=x.pc?x.pc.n:x.f[2];return`<path data-i="${x.i}" data-s="${x.si}" d="${x.f[3]}" fill="${mcol(x)}" fill-rule="evenodd" stroke="var(--c)" stroke-width=".6" vector-effect="non-scaling-stroke" role="link" ${st==null?'':'tabindex="0"'} aria-label="${esc(nm)}, ${esc(x.pc?lab(x.pc.w[3]):'BJP')}" onclick="mclick(${x.i},${x.si})" onkeydown="if(event.key==='Enter')mclick(${x.i},${x.si})" onmousemove="tip(event,${x.i})" onmouseleave="tip()"/>`}).join('');"""

map_replacement = """// Calculate Party Seats for Map Filter
const mapPartyCounts={};vis.forEach(x=>{const p=x.pc?x.pc.w[3]:BJPI;mapPartyCounts[p]=(mapPartyCounts[p]||0)+1;});
const sortedMapParties=Object.entries(mapPartyCounts).sort((a,b)=>b[1]-a[1]).map(([p,cnt])=>({id:+p,name:lab(+p),seats:cnt}));

const paths=vis.map(x=>{
  const nm=x.pc?x.pc.n:x.f[2];
  const isMatch=window.SELECTED_MAP_PARTY==null||(x.pc&&x.pc.w[3]===window.SELECTED_MAP_PARTY)||(window.SELECTED_MAP_PARTY===BJPI&&!x.pc);
  const opacity=isMatch?'1':'0.14';
  const strokeW=isMatch?(window.SELECTED_MAP_PARTY!=null?'1.4':'.6'):'.3';
  const strokeCol=isMatch?(window.SELECTED_MAP_PARTY!=null?'#ffffff':'var(--c)'):'rgba(255,255,255,0.1)';
  return`<path data-i="${x.i}" data-s="${x.si}" d="${x.f[3]}" fill="${mcol(x)}" fill-rule="evenodd" stroke="${strokeCol}" stroke-width="${strokeW}" style="opacity:${opacity};transition:all 0.15s ease" vector-effect="non-scaling-stroke" role="link" tabindex="0" title="${esc(nm)}" aria-label="${esc(nm)}, ${esc(x.pc?lab(x.pc.w[3]):'BJP')}" onclick="mclick(${x.i},${x.si})" onkeydown="if(event.key==='Enter')mclick(${x.i},${x.si})" onmousemove="tip(event,${x.i})" onmouseleave="tip()"/>`
}).join('');"""

if map_target in content:
    content = content.replace(map_target, map_replacement, 1)
    print("3. Patched map paths and party seat filter logic")
else:
    print("WARNING: Could not find map_target")

# 4. Patch map toolbar for Party Seats Filter dropdown
map_toolbar_old = """<div class="f"><button class="btn ${MM=='party'?'on':''}" onclick="MM='party';render()">By party</button><button class="btn ${MM!='party'?'on':''}" onclick="MM='alliance';render()">By alliance</button>${st==null?`<select aria-label="Jump to state" onchange="if(this.value!=='')go('map/'+this.value)"><option value="">Jump to state…</option>${S.map((s,i)=>`<option value="${i}">${s}</option>`)}</select>`:`<button class="btn" onclick="go('map')">← All India</button>`}</div>"""

map_toolbar_new = """<div class="f">
  <button class="btn ${MM=='party'?'on':''}" onclick="MM='party';render()">By party</button>
  <button class="btn ${MM!='party'?'on':''}" onclick="MM='alliance';render()">By alliance</button>
  <select id="map-party-filter" aria-label="Filter by Party Seats" onchange="filterMapParty(this.value)">
    <option value="">Filter by Party Seats (${vis.length} seats)…</option>
    ${sortedMapParties.map(p=>`<option value="${p.id}" ${window.SELECTED_MAP_PARTY===p.id?'selected':''}>${esc(p.name)} (${p.seats} seats)</option>`).join('')}
  </select>
  ${st==null?`<select aria-label="Jump to state" onchange="if(this.value!=='')go('map/'+this.value)"><option value="">Jump to state…</option>${S.map((s,i)=>`<option value="${i}">${s}</option>`)}</select>`:`<button class="btn" onclick="go('map')">← All India</button>`}
</div>"""

if map_toolbar_old in content:
    content = content.replace(map_toolbar_old, map_toolbar_new, 1)
    print("4. Added Party Seats Filter to Map toolbar")
else:
    print("WARNING: Could not find map_toolbar_old")

# 5. Patch mclick to directly open constituency
old_mclick = "function mclick(i,si){if(MOVED)return;if(MAPST==null){if(SEL===si)go('map/'+si);else stSel(si)}else pick(i)}"
new_mclick = """let SELECTED_MAP_PARTY = null;
window.filterMapParty = function(pid) {
  window.SELECTED_MAP_PARTY = pid === '' ? null : +pid;
  render();
};

function mclick(i, si) {
  if (MOVED) return;
  const feat = GEO.f[i];
  const c = feat && feat[0] >= 0 ? PC[feat[0]] : null;
  if (c) {
    // Direct open constituency! Don't add middle states
    go('pc/' + c.id);
  } else if (feat) {
    pick(i);
  }
}"""

if old_mclick in content:
    content = content.replace(old_mclick, new_mclick, 1)
    print("5. Patched mclick to direct open constituency")
else:
    print("WARNING: Could not find old_mclick")

# 6. Patch tip(e, i)
old_tip = """function tip(e,i){
  if(i==null){hideFloatingTip();return}
  const feat=GEO.f[i],c=feat[0]>=0?PC[feat[0]]:null;
  if(!c){
    showFloatingTip(e,`<div style="font-weight:700">${esc(feat[2])}</div><div style="color:#ff6b00;font-size:11.5px">BJP (unopposed)</div>`);
    return;
  }
  const wp=P[c.w[3]];
  showFloatingTip(e,`
    <div style="font-weight:700;font-size:13px;margin-bottom:2px">${esc(c.n)} <span style="font-size:11px;opacity:0.75">(${S[c.si]})</span></div>
    <div style="font-size:11px;color:var(--text-2);margin-bottom:3px">${c.cat} · Turnout: <b>${c.t.toFixed(1)}%</b></div>
    <div style="font-size:12px">Winner: <b>${esc(c.w[0])}</b> (${dot2(wp)} ${esc(lab(c.w[3]))})</div>
    <div style="font-size:11px;color:#4ade80">Margin: <b>${f(c.m)}</b> votes</div>
  `);
}"""

new_tip = """function tip(e,i){
  if(i==null){hideFloatingTip();return}
  const feat=GEO.f[i],c=feat[0]>=0?PC[feat[0]]:null;
  if(!c){
    showFloatingTip(e,`<div style="font-weight:700">${esc(feat[2])}</div><div style="color:#ff6b00;font-size:11.5px">BJP (unopposed)</div><div style="font-size:10.5px;color:var(--text-2);margin-top:3px">👉 Click to open constituency directly</div>`);
    return;
  }
  const wp=P[c.w[3]];
  showFloatingTip(e,`
    <div style="font-weight:800;font-size:13.5px;margin-bottom:2px;color:var(--g)">${esc(c.n)} <span style="font-size:11px;opacity:0.8;font-weight:500">(${S[c.si]})</span></div>
    <div style="font-size:11px;color:var(--text-2);margin-bottom:4px">${c.cat} · Turnout: <b>${c.t.toFixed(1)}%</b> · Electors: <b>${f(c.el)}</b></div>
    <div style="font-size:12px;margin-bottom:2px">Winner: <b>${esc(c.w[0])}</b> (${dot2(wp)} ${esc(lab(c.w[3]))})</div>
    <div style="font-size:11px;color:#4ade80">Margin: <b>${f(c.m)}</b> votes (${pc(c.m, c.va)}%)</div>
    <div style="font-size:10.5px;color:#ff9933;margin-top:4px;border-top:1px dashed rgba(255,255,255,0.15);padding-top:3px">👉 Click to open constituency directly</div>
  `);
}"""

if old_tip in content:
    content = content.replace(old_tip, new_tip, 1)
    print("6. Patched tip() for rich hover and direct open prompt")
else:
    print("WARNING: Could not find old_tip")

# 7. Patch locMap and add openBigConstituencyModal
old_locmap = "function locMap(id){lazy('GEO','js/geo-ls.js').then(()=>{const b=$('lm'),c=PC[id];if(!b||!c)return;b.innerHTML=`<svg viewBox=\"0 0 ${GEO.w} ${GEO.h}\" width=\"100%\" style=\"max-height:260px\">${GEO.f.map(x=>`<path d=\"${x[3]}\" fill=\"${x[0]===c.id?col(c.w[3]):'var(--b)'}\" ${x[0]===c.id?'stroke=\"#000\" stroke-width=\"1.5\"':''}/>`).join('')}</svg>`})}"

new_locmap = """function locMap(id){
  lazy('GEO','js/geo-ls.js').then(()=>{
    const b=$('lm'),c=PC[id];if(!b||!c)return;
    const feat=GEO.f.find(x=>x[0]===c.id);
    if(!feat){
      b.innerHTML=`<svg viewBox="0 0 ${GEO.w} ${GEO.h}" width="100%" style="max-height:260px">${GEO.f.map(x=>`<path d="${x[3]}" fill="${x[0]===c.id?col(c.w[3]):'var(--b)'}"/>`).join('')}</svg>`;
      return;
    }

    // Compute Constituency Bounding Box for Big Zoom
    const nums=feat[3].match(/-?\\d+\\.?\\d*/g).map(Number);
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
      const sn=x[3].match(/-?\\d+\\.?\\d*/g).map(Number);
      for(let k=0;k<sn.length;k+=2){
        sMinX=Math.min(sMinX,sn[k]);sMaxX=Math.max(sMaxX,sn[k]);
        sMinY=Math.min(sMinY,sn[k+1]);sMaxY=Math.max(sMaxY,sn[k+1]);
      }
    });
    const sPad=Math.max(sMaxX-sMinX,sMaxY-sMinY)*0.08;
    const vbState=[sMinX-sPad,sMinY-sPad,(sMaxX-sMinX)+2*sPad,(sMaxY-sMinY)+2*sPad].map(n=>n.toFixed(1)).join(' ');
    const vbIndia=`0 0 ${GEO.w} ${GEO.h}`;

    b.innerHTML=`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px">
        <div class="tab-pills" style="margin:0">
          <button class="tab-pill on" id="lm-btn-zoom" onclick="setLocView('${vbZoom}','zoom')">🔍 Big Zoom</button>
          <button class="tab-pill" id="lm-btn-state" onclick="setLocView('${vbState}','state')">🗺️ ${esc(S[c.si])}</button>
          <button class="tab-pill" id="lm-btn-india" onclick="setLocView('${vbIndia}','india')">🇮🇳 India</button>
        </div>
        <button class="btn on" onclick="openBigConstituencyModal(${c.id})" style="padding:4px 10px;font-size:12px">⛶ Enlarge / Big Popup</button>
      </div>

      <div style="background:#060a14;border:1px solid var(--b);border-radius:8px;overflow:hidden;position:relative">
        <svg id="lm-svg" viewBox="${vbZoom}" width="100%" style="height:min(340px, 45vh);display:block;transition:all 0.3s ease">
          ${stateFeats.map(x=>`<path d="${x[3]}" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.15)" stroke-width="0.6" vector-effect="non-scaling-stroke"/>`).join('')}
          <path d="${feat[3]}" fill="${col(c.w[3])}" stroke="#ffffff" stroke-width="2.2" vector-effect="non-scaling-stroke" style="filter:drop-shadow(0 0 10px ${col(c.w[3])})"/>
          <circle cx="${(minX+maxX)/2}" cy="${(minY+maxY)/2}" r="3.5" fill="#ffffff" stroke="${col(c.w[3])}" stroke-width="1.8" vector-effect="non-scaling-stroke"/>
        </svg>

        <div style="position:absolute;bottom:8px;left:8px;background:rgba(11,20,40,0.85);backdrop-filter:blur(4px);padding:4px 8px;border-radius:4px;border:1px solid var(--b);font-size:11px;display:flex;align-items:center;gap:6px">
          ${dot(c.w[3])} <b>${esc(c.n)}</b> · ${esc(lab(c.w[3]))}
        </div>
      </div>
    `;
  });
}

window.setLocView=function(vb,type){
  const svg=$('lm-svg');if(svg)svg.setAttribute('viewBox',vb);
  ['zoom','state','india'].forEach(t=>{const btn=$('lm-btn-'+t);if(btn)btn.classList.toggle('on',t===type)});
};

window.openBigConstituencyModal=function(id){
  const c=PC[id];if(!c)return;
  lazy('GEO','js/geo-ls.js').then(()=>{
    const feat=GEO.f.find(x=>x[0]===c.id);if(!feat)return;
    const nums=feat[3].match(/-?\\d+\\.?\\d*/g).map(Number);
    let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
    for(let k=0;k<nums.length;k+=2){
      minX=Math.min(minX,nums[k]);maxX=Math.max(maxX,nums[k]);
      minY=Math.min(minY,nums[k+1]);maxY=Math.max(maxY,nums[k+1]);
    }
    const cW=maxX-minX,cH=maxY-minY;
    const pad=Math.max(cW,cH)*0.32;
    const vbZoom=[minX-pad,minY-pad,cW+2*pad,cH+2*pad].map(n=>n.toFixed(1)).join(' ');
    const stateFeats=GEO.f.filter(x=>{const pc=x[0]>=0?PC[x[0]]:null;return pc&&pc.si===c.si});

    let modal=document.getElementById('big-constituency-modal');
    if(!modal){
      modal=document.createElement('div');
      modal.id='big-constituency-modal';
      document.body.appendChild(modal);
    }

    modal.innerHTML=`
      <div class="modal-backdrop" onclick="document.getElementById('big-constituency-modal').style.display='none'" style="position:fixed;inset:0;background:rgba(0,0,0,0.85);backdrop-filter:blur(8px);z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#090e1c;border:1px solid rgba(255,255,255,0.15);border-radius:14px;width:min(900px, 96vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 30px 80px rgba(0,0,0,0.9);overflow:hidden">
          <div style="padding:16px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="display:flex;align-items:center;gap:8px">
                <span class="badge" style="background:${col(c.w[3])};color:#fff;font-weight:700;font-size:11px">${esc(lab(c.w[3]))}</span>
                <span style="font-size:12px;color:var(--text-2)">${esc(S[c.si])} · ${c.cat}</span>
              </div>
              <h2 style="margin:4px 0 0;font-size:24px;color:var(--text)">🏛️ ${esc(c.n)} Constituency Map</h2>
            </div>
            <button class="btn" onclick="document.getElementById('big-constituency-modal').style.display='none'" style="font-size:16px">✕</button>
          </div>

          <div style="flex:1;overflow-y:auto;padding:18px">
            <div style="background:#040711;border:1px solid var(--b);border-radius:10px;padding:10px;text-align:center;margin-bottom:16px;box-shadow:inset 0 0 40px rgba(0,0,0,0.7)">
              <svg viewBox="${vbZoom}" width="100%" style="height:min(440px, 50vh);display:block">
                ${stateFeats.map(x=>`<path d="${x[3]}" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.12)" stroke-width="0.5" vector-effect="non-scaling-stroke"/>`).join('')}
                <path d="${feat[3]}" fill="${col(c.w[3])}" stroke="#ffffff" stroke-width="2.5" vector-effect="non-scaling-stroke" style="filter:drop-shadow(0 0 16px ${col(c.w[3])})"/>
                <circle cx="${(minX+maxX)/2}" cy="${(minY+maxY)/2}" r="4" fill="#ffffff" stroke="${col(c.w[3])}" stroke-width="2" vector-effect="non-scaling-stroke"/>
              </svg>
            </div>

            <div class="g g3" style="gap:10px">
              <div class="card" style="margin:0;padding:12px;background:var(--s1)">
                <small style="color:var(--text-2)">Winner Candidate</small>
                <div style="font-size:16px;font-weight:800;color:#4ade80;margin:3px 0">${esc(c.w[0])}</div>
                <div style="font-size:12px">${dot(c.w[3])} ${esc(lab(c.w[3]))} · ${f(c.w[6])} votes</div>
              </div>
              <div class="card" style="margin:0;padding:12px;background:var(--s1)">
                <small style="color:var(--text-2)">Winning Margin</small>
                <div style="font-size:16px;font-weight:800;color:var(--text);margin:3px 0">${f(c.m)} votes</div>
                <div style="font-size:12px;color:var(--text-2)">${pc(c.m, c.va)}% of valid votes</div>
              </div>
              <div class="card" style="margin:0;padding:12px;background:var(--s1)">
                <small style="color:var(--text-2)">Turnout &amp; Electors</small>
                <div style="font-size:16px;font-weight:800;color:var(--text);margin:3px 0">${c.t.toFixed(1)}% Turnout</div>
                <div style="font-size:12px;color:var(--text-2)">${f(c.el)} registered electors</div>
              </div>
            </div>
          </div>

          <div style="padding:14px 22px;border-top:1px solid var(--b);display:flex;justify-content:space-between;align-items:center">
            <span class="note">Lok Sabha 2024 General Election Results</span>
            <div style="display:flex;gap:8px">
              <button class="btn on" onclick="document.getElementById('big-constituency-modal').style.display='none';go('pc/${c.id}')">View Full Result Details →</button>
              <button class="btn" onclick="document.getElementById('big-constituency-modal').style.display='none'">Close</button>
            </div>
          </div>
        </div>
      </div>
    `;
    modal.style.display='block';
  });
};"""

if old_locmap in content:
    content = content.replace(old_locmap, new_locmap, 1)
    print("7. Patched locMap for big constituency view and big modal popup")
else:
    print("WARNING: Could not find old_locmap")

# 8. Patch pcs party filter with seat counts
pcs_old = """      <select id="fp" aria-label="Filter by Party" onchange="fl()">
        <option value="">All Winning Parties</option>
        ${sortedParties.map(p=>`<option value="${p}">${esc(lc(p))}</option>`)}
      </select>"""

pcs_new = """      <select id="fp" aria-label="Filter by Party Seats" onchange="fl()">
        <option value="">All Winning Parties (with Seats)</option>
        ${sortedParties.map(p=>{
          const cnt=getUnifiedPCs().filter(c=>c.winnerParty===p).length;
          return `<option value="${p}">${esc(lc(p))} (${cnt} seats)</option>`;
        }).join('')}
      </select>"""

if pcs_old in content:
    content = content.replace(pcs_old, pcs_new, 1)
    print("8. Patched pcs filter to display party seat counts")
else:
    print("WARNING: Could not find pcs_old")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete!")
