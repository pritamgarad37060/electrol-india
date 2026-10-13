import re

with open('js/mh-local-ui.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Corporation Ward Card: Add 3rd, 4th candidates and all votes
corp_card_old = r'''                <!-- Margin & Previous Election Snippet -->
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;padding:4px 0">
                  <span style="font-size:12px;font-weight:700;color:#38bdf8">
                    Victory Margin: +${fmt(w.margin)}
                  </span>
                  ${is2026 && w2017 ? `
                    <span style="font-size:11px;color:var(--text-3)">
                      2017: <b>${esc(w2017.party)}</b> (${fmt(w2017.votes)})
                    </span>
                  ` : ''}
                </div>'''

corp_card_new = r'''                <!-- 3rd and 4th Candidates -->
                ${(w.third || w.fourth) ? `
                  <div class="mycorp-other-cands">
                    ${w.third ? `
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:${w.fourth ? '3px' : '0'}">
                        <span>🥉 <b>3rd:</b> ${esc(w.third)} <span class="tag" style="background:var(--s2);border-left:2px solid ${getPartyColor(w.third_party)};font-size:10px;padding:1px 4px">${esc(w.third_party)}</span></span>
                        <span style="font-weight:600">${fmt(w.third_votes)} (${w.third_pct ? w.third_pct.toFixed(1) + '%' : '–'})</span>
                      </div>
                    ` : ''}
                    ${w.fourth ? `
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <span><b>4th:</b> ${esc(w.fourth)} <span class="tag" style="background:var(--s2);border-left:2px solid ${getPartyColor(w.fourth_party)};font-size:10px;padding:1px 4px">${esc(w.fourth_party)}</span></span>
                        <span style="font-weight:600">${fmt(w.fourth_votes)} (${w.fourth_pct ? w.fourth_pct.toFixed(1) + '%' : '–'})</span>
                      </div>
                    ` : ''}
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
                </div>'''

code = code.replace(corp_card_old, corp_card_new)

# 2. Update Corporation Modal: Include full candidate leaderboard
corp_modal_search = r'''            <!-- Victory Margin Card -->
            <div class="card" style="background:var(--s2);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-size:11px;color:var(--text-2);text-transform:uppercase;font-weight:700">VICTORY MARGIN</div>
                <div style="font-size:22px;font-weight:800;color:#38bdf8;margin:2px 0">+${fmt(w2026.margin)} Votes</div>
              </div>
              <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:12px;padding:4px 10px;font-weight:700">
                ${w2026.votes && w2026.margin ? ((w2026.margin / w2026.votes) * 100).toFixed(1) + '% Margin' : 'Decisive'}
              </span>
            </div>'''

corp_modal_replace = r'''            <!-- Victory Margin Card -->
            <div class="card" style="background:var(--s2);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-size:11px;color:var(--text-2);text-transform:uppercase;font-weight:700">VICTORY MARGIN</div>
                <div style="font-size:22px;font-weight:800;color:#38bdf8;margin:2px 0">+${fmt(w2026.margin)} Votes</div>
              </div>
              <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:12px;padding:4px 10px;font-weight:700">
                ${w2026.votes && w2026.margin ? ((w2026.margin / w2026.votes) * 100).toFixed(1) + '% Margin' : 'Decisive'}
              </span>
            </div>

            <!-- Complete Candidate Vote Leaderboard (All Candidates Polled) -->
            <div class="card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:18px">
              <div style="font-size:12px;color:#38bdf8;font-weight:800;letter-spacing:0.5px">
                📊 ALL CANDIDATES &amp; COMPLETE VOTE TALLY
              </div>
              ${renderCandidateLeaderboardHtml(w2026.cands)}
            </div>'''

code = code.replace(corp_modal_search, corp_modal_replace)

# 3. Update Council Councillor Card: Include runner-up, 3rd, 4th, and margin
council_card_old = r'''                  ${w.pct ? `
                    <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;margin-top:6px">
                      <div style="width:${Math.min(w.pct, 100)}%;background:${pColor};height:100%"></div>
                    </div>
                  ` : ''}
                </div>
              </div>

              <!-- Action Card Footer -->'''

council_card_new = r'''                  ${w.pct ? `
                    <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;margin-top:6px">
                      <div style="width:${Math.min(w.pct, 100)}%;background:${pColor};height:100%"></div>
                    </div>
                  ` : ''}
                </div>

                <!-- Runner-Up Block -->
                ${w.runner ? `
                  <div class="mycorp-runner-box">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
                      <span style="font-size:10px;color:var(--text-3);text-transform:uppercase;font-weight:700">🥈 RUNNER-UP</span>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w.runner_party)};font-size:10.5px">${esc(w.runner_party)}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <span style="font-size:12.5px;color:var(--text-2);font-weight:600">${esc(w.runner)}</span>
                      <span style="font-size:12px;color:var(--text-3)">${fmt(w.runner_votes)} (${w.runner_pct ? w.runner_pct.toFixed(1) + '%' : '–'})</span>
                    </div>
                  </div>
                ` : ''}

                <!-- 3rd and 4th Candidates -->
                ${(w.third || w.fourth) ? `
                  <div class="mycorp-other-cands">
                    ${w.third ? `
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:${w.fourth ? '3px' : '0'}">
                        <span>🥉 <b>3rd:</b> ${esc(w.third)} <span class="tag" style="background:var(--s2);border-left:2px solid ${getPartyColor(w.third_party)};font-size:10px;padding:1px 4px">${esc(w.third_party)}</span></span>
                        <span style="font-weight:600">${fmt(w.third_votes)} (${w.third_pct ? w.third_pct.toFixed(1) + '%' : '–'})</span>
                      </div>
                    ` : ''}
                    ${w.fourth ? `
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <span><b>4th:</b> ${esc(w.fourth)} <span class="tag" style="background:var(--s2);border-left:2px solid ${getPartyColor(w.fourth_party)};font-size:10px;padding:1px 4px">${esc(w.fourth_party)}</span></span>
                        <span style="font-weight:600">${fmt(w.fourth_votes)} (${w.fourth_pct ? w.fourth_pct.toFixed(1) + '%' : '–'})</span>
                      </div>
                    ` : ''}
                  </div>
                ` : ''}

                ${w.margin ? `
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-size:12px">
                    <span style="font-weight:700;color:#38bdf8">Victory Margin: +${fmt(w.margin)} votes</span>
                  </div>
                ` : ''}
              </div>

              <!-- Action Card Footer -->'''

code = code.replace(council_card_old, council_card_new)

# 4. Update Council Modal: Add candidate leaderboard table
council_modal_old = r'''          <div style="padding:22px;overflow-y:auto;flex:1">
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
          </div>'''

council_modal_new = r'''          <div style="padding:22px;overflow-y:auto;flex:1">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
              <div class="mycorp-winner-box" style="margin:0;background:rgba(56,189,248,0.08);border-color:rgba(56,189,248,0.3)">
                <span style="font-size:10px;font-weight:800;color:#38bdf8;text-transform:uppercase">🥇 ELECTED COUNCILLOR</span>
                <h3 style="margin:4px 0;font-size:16px;color:var(--text)">${esc(w.candidate)}</h3>
                <span class="tag" style="background:var(--s2);border-left:3px solid ${pColor};font-size:11.5px">
                  ${esc(w.party)}
                </span>
                <div style="margin-top:8px;font-size:12.5px;color:var(--text-2)">
                  Votes: <b style="color:var(--text)">${fmt(w.votes)}</b> (${w.pct ? w.pct.toFixed(1) + '%' : '–'})
                </div>
              </div>

              ${w.runner ? `
                <div class="mycorp-runner-box" style="margin:0">
                  <span style="font-size:10px;font-weight:800;color:var(--text-3);text-transform:uppercase">🥈 RUNNER-UP</span>
                  <h3 style="margin:4px 0;font-size:16px;color:var(--text-2)">${esc(w.runner)}</h3>
                  <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w.runner_party)};font-size:11.5px">
                    ${esc(w.runner_party)}
                  </span>
                  <div style="margin-top:8px;font-size:12.5px;color:var(--text-2)">
                    Votes: <b style="color:var(--text-2)">${fmt(w.runner_votes)}</b> (${w.runner_pct ? w.runner_pct.toFixed(1) + '%' : '–'})
                  </div>
                </div>
              ` : '<div></div>'}
            </div>

            <!-- Complete Candidate Vote Leaderboard -->
            <div class="card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:14px">
              <div style="font-size:12px;color:#38bdf8;font-weight:800;letter-spacing:0.5px">
                📊 ALL CONTESTING CANDIDATES &amp; VOTES POLLED
              </div>
              ${renderCandidateLeaderboardHtml(w.cands)}
            </div>
          </div>'''

code = code.replace(council_modal_old, council_modal_new)

# 5. Replace bulky toolbars in renderCorporationDetailPage and renderCouncilDetailPage
corp_toolbar_old = r'''      <!-- "Find Your Ward Result" Toolbar -->
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
      </div>'''

corp_toolbar_new = r'''      <!-- Compact Find Your Ward Result Toolbar -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="mycorp-search-input"
                 placeholder="Search ward # (e.g. 1), candidate name, runner-up…"
                 oninput="onMyCorpFilterChange()">
        </div>

        <div class="munc-filter-group">
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
            <option value="">All Margins</option>
            <option value="close">Razor Thin (< 1,000)</option>
            <option value="mid">Moderate (1k–4k)</option>
            <option value="big">Landslide (> 4,000)</option>
          </select>

          <select id="mycorp-sort-select" onchange="onMyCorpFilterChange()">
            <option value="ward-asc">Ward: 1 → ${winners2026.length}</option>
            <option value="ward-desc">Ward: ${winners2026.length} → 1</option>
            <option value="margin-desc">Margin: Highest First</option>
            <option value="margin-asc">Margin: Closest First</option>
            <option value="votes-desc">Votes: Highest First</option>
            <option value="name-asc">Candidate: A → Z</option>
          </select>
        </div>
      </div>'''

code = code.replace(corp_toolbar_old, corp_toolbar_new)

council_toolbar_old = r'''      <!-- "Find Your Councillor Result" Toolbar -->
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
      </div>'''

council_toolbar_new = r'''      <!-- Compact Find Your Councillor Result Toolbar -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="mycouncil-search-input"
                 placeholder="Search ward # (e.g. 1), councillor, or party…"
                 oninput="onMyCouncilFilterChange()">
        </div>

        <div class="munc-filter-group">
          <select id="mycouncil-party-filter" onchange="onMyCouncilFilterChange()">
            <option value="">All Parties (${Object.keys(tally).length})</option>
            ${topParties.map(([p, cnt]) => `
              <option value="${esc(p)}">${esc(p)} (${cnt} Seats)</option>
            `).join('')}
          </select>

          <select id="mycouncil-sort-select" onchange="onMyCouncilFilterChange()">
            <option value="ward-asc">Ward: Lowest First</option>
            <option value="ward-desc">Ward: Highest First</option>
            <option value="votes-desc">Votes: Highest First</option>
            <option value="name-asc">Candidate: A → Z</option>
          </select>
        </div>
      </div>'''

code = code.replace(council_toolbar_old, council_toolbar_new)

with open('js/mh-local-ui.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied candidate positions and compact search fixes to js/mh-local-ui.js successfully.")
