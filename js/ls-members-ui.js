/**
 * ELECTROL INDIA — Lok Sabha Members & Candidate Intelligence UI
 * Handles MP profile cards, search directory, dossier modals, social links & oath video player.
 */

(function() {
  'use strict';

  // SVG Icons Library
  const ICONS = {
    x: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
    instagram: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    facebook: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`,
    youtube: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>`,
    linkedin: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>`,
    phone: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
    mail: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`,
    play: `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`,
    parliament: `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 1L3 5v2h18V5l-9-4zm-7 8v10h2V9H5zm4 0v10h2V9H9zm4 0v10h2V9h-2zm4 0v10h2V9h-2zM2 21v2h20v-2H2z"/></svg>`,
    external: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`,
    check: `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`
  };

  // Helper: Find MP by Constituency Name & State Name
  function getMemberForPC(pcName, stateName) {
    if (!window.LS_MEMBERS || !window.LS_MEMBERS.length) return null;
    const cleanStr = s => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
    const pClean = cleanStr(pcName);
    const sClean = cleanStr(stateName);

    // 1. Direct matched_pc match
    let found = window.LS_MEMBERS.find(m => cleanStr(m.matched_pc) === pClean && (!sClean || cleanStr(m.state).includes(sClean) || sClean.includes(cleanStr(m.state))));
    if (found) return found;

    // 2. Constituency field match
    found = window.LS_MEMBERS.find(m => cleanStr(m.constituency) === pClean && (!sClean || cleanStr(m.state).includes(sClean) || sClean.includes(cleanStr(m.state))));
    if (found) return found;

    // 3. Fallback name only match
    found = window.LS_MEMBERS.find(m => cleanStr(m.constituency) === pClean || cleanStr(m.matched_pc) === pClean);
    return found || null;
  }

  function getMemberById(id) {
    if (!window.LS_MEMBERS) return null;
    const mid = parseInt(id, 10);
    return window.LS_MEMBERS.find(m => m.id === mid) || null;
  }

  // Safe Avatar image with high-performance local cache and remote fallback
  function renderMpAvatar(m, size) {
    size = size || 54;
    const initial = (m.first_name || m.name || 'M')[0].toUpperCase();
    const localPhoto = m.local_photo || ('data/photos/' + m.id + '.jpg');
    const remotePhoto = m.photo_url ? esc(m.photo_url) : '';
    return `
      <div class="mp-avatar-wrap" style="width:${size}px;height:${size}px;min-width:${size}px">
        <img src="${esc(localPhoto)}" alt="${esc(m.name)}" class="mp-avatar-img" referrerpolicy="no-referrer" loading="lazy" onerror="if(!this.dataset.retried&&'${remotePhoto}'){this.dataset.retried='1';this.src='${remotePhoto}';}else{this.style.display='none';if(this.nextElementSibling)this.nextElementSibling.style.display='flex';}">
        <div class="mp-avatar-fallback" style="display:none;width:${size}px;height:${size}px;font-size:${Math.round(size*0.42)}px">${initial}</div>
      </div>
    `;
  }

  // Render Social and Contact Buttons
  function renderSocialLinks(m, compact) {
    const s = m.social || {};
    const btns = [];

    if (s.twitter) {
      btns.push(`<a href="${esc(s.twitter)}" target="_blank" rel="noopener noreferrer" class="social-icon-btn btn-x" title="X (Twitter)">${ICONS.x}</a>`);
    }
    if (s.instagram) {
      btns.push(`<a href="${esc(s.instagram)}" target="_blank" rel="noopener noreferrer" class="social-icon-btn btn-insta" title="Instagram">${ICONS.instagram}</a>`);
    }
    if (s.facebook) {
      btns.push(`<a href="${esc(s.facebook)}" target="_blank" rel="noopener noreferrer" class="social-icon-btn btn-fb" title="Facebook">${ICONS.facebook}</a>`);
    }
    if (s.linkedin) {
      btns.push(`<a href="${esc(s.linkedin)}" target="_blank" rel="noopener noreferrer" class="social-icon-btn btn-in" title="LinkedIn">${ICONS.linkedin}</a>`);
    }
    if (m.email) {
      const firstEmail = m.email.split(/[\n,;]/)[0].trim();
      if (firstEmail) btns.push(`<a href="mailto:${esc(firstEmail)}" class="social-icon-btn btn-mail" title="Email: ${esc(firstEmail)}">${ICONS.mail}</a>`);
    }
    if (m.delhi_phone || m.phone) {
      const cleanPhone = (m.delhi_phone || m.phone).replace(/[^0-9+]/g, '');
      if (cleanPhone) btns.push(`<a href="tel:${cleanPhone}" class="social-icon-btn btn-phone" title="Call: ${esc(m.delhi_phone || m.phone)}">${ICONS.phone}</a>`);
    }

    if (!btns.length) return '';
    return `<div class="mp-social-row ${compact ? 'compact' : ''}">${btns.join('')}</div>`;
  }

  // Render MP Profile Card for Lok Sabha Constituency View
  function renderConstituencyMpCard(c) {
    if (!c) return '';
    const stateName = window.S ? window.S[c.si] : '';
    const m = getMemberForPC(c.n, stateName);
    if (!m) return '';

    const partyColor = (window.CM && window.CM[m.party_code]) ? window.CM[m.party_code] : '#ff6b00';

    return `
      <div class="mp-constituency-card" style="border-left: 4px solid ${partyColor}">
        <div class="mp-card-inner">
          <div class="mp-card-top">
            ${renderMpAvatar(m, 62)}
            <div class="mp-info-col">
              <div class="mp-badge-line">
                <span class="mp-sitting-pill"><span class="pulse-dot"></span> SITTING MP</span>
                <span class="mp-terms-badge">${m.num_terms > 1 ? m.num_terms + ' Terms' : '1st Term'} (18th LS)</span>
                <span class="mp-id-badge">#LS-${m.id}</span>
              </div>
              <h2 class="mp-name">${esc(m.name)}</h2>
              <div class="mp-meta">
                <span class="mp-party-badge" style="background:${partyColor}22;color:${partyColor};border:1px solid ${partyColor}55">
                  <b>${esc(m.party_code || m.party)}</b>
                </span>
                <span class="mp-dot">·</span>
                <span class="mp-const-text">${esc(m.constituency)}, ${esc(m.state)}</span>
              </div>
            </div>
          </div>

          <div class="mp-action-bar">
            <!-- Sleek Oath Watch Option: No raw link, clean player action -->
            <button class="btn-oath-watch" onclick="window.openOathVideoModal(${m.id})">
              <span class="oath-play-icon">${ICONS.play}</span>
              <span>Watch Oath Taking</span>
            </button>

            <!-- Dossier modal button -->
            <button class="btn-dossier" onclick="window.openMpDossierModal(${m.id})">
              <span>Member Dossier &amp; Positions (${(m.positions || []).length})</span>
            </button>

            <!-- Social/contact buttons -->
            ${renderSocialLinks(m, true)}
          </div>
        </div>
      </div>
    `;
  }

  // Full Directory / Hub Page: #members / #mps
  let DIR_STATE = {
    search: '',
    state: '',
    party: '',
    gender: '',
    terms: '',
    view: 'cards', // 'cards' or 'table'
    page: 1,
    pageSize: 24
  };

  function renderLsMembersHub() {
    if (!window.LS_MEMBERS || !window.LS_MEMBERS.length) {
      return `
        <div class="ls-members-hub">
          <p>Loading Lok Sabha members dataset…</p>
        </div>
      `;
    }

    const members = window.LS_MEMBERS;
    const states = [...new Set(members.map(m => m.state).filter(Boolean))].sort();
    const parties = [...new Set(members.map(m => m.party_code || m.party).filter(Boolean))].sort();

    // Key Stats
    const totalCount = members.length;
    const femaleCount = members.filter(m => (m.gender || '').toLowerCase() === 'female').length;
    const multiTermCount = members.filter(m => m.num_terms > 1).length;
    const avgAge = Math.round(members.reduce((acc, m) => acc + (m.age || 50), 0) / totalCount);

    return `
      <div class="ls-members-hub">
        <!-- Breadcrumbs -->
        <div class="bc">
          <a onclick="go('')">Home</a> <span>/</span>
          <a onclick="go('ls')">Lok Sabha 2024</a> <span>/</span>
          <b>18th Lok Sabha Members</b>
        </div>

        <!-- Hero Title Banner -->
        <div class="members-hero">
          <div class="members-hero-badge">
            ${ICONS.parliament}
            <span>PARLIAMENT OF INDIA · 18TH LOK SABHA DIRECTORY</span>
          </div>
          <h1>🏛️ Lok Sabha Members Directory &amp; Dossiers</h1>
          <p class="members-hero-sub">Complete verified dossiers of all 540 Sitting Members of Parliament with portfolios, committee tenures, contact details, social media, and Sansad TV oath ceremonies.</p>
        </div>

        <!-- Stats Overview Cards -->
        <div class="members-stats-strip">
          <div class="mstat-card">
            <div class="mstat-val">${totalCount}</div>
            <div class="mstat-lbl">Sitting MPs</div>
          </div>
          <div class="mstat-card">
            <div class="mstat-val" style="color:var(--saffron)">${parties.length}</div>
            <div class="mstat-lbl">Parties Represented</div>
          </div>
          <div class="mstat-card">
            <div class="mstat-val" style="color:#ec4899">${femaleCount}</div>
            <div class="mstat-lbl">Women MPs (${((femaleCount/totalCount)*100).toFixed(1)}%)</div>
          </div>
          <div class="mstat-card">
            <div class="mstat-val" style="color:#38bdf8">${multiTermCount}</div>
            <div class="mstat-lbl">Multi-Term MPs</div>
          </div>
          <div class="mstat-card">
            <div class="mstat-val" style="color:#4ade80">${avgAge} yrs</div>
            <div class="mstat-lbl">Average Age</div>
          </div>
        </div>

        <!-- Filter & Search Control Panel -->
        <div class="members-filter-box">
          <div class="mf-search-wrap">
            <input type="text" id="mf-search" placeholder="Search by MP Name, Constituency, State, Party, Profession…" value="${esc(DIR_STATE.search)}" oninput="window.onMemberSearch(this.value)">
          </div>

          <div class="mf-dropdowns">
            <select id="mf-state" onchange="window.onMemberFilter('state', this.value)">
              <option value="">All States / UTs (${states.length})</option>
              ${states.map(s => `<option value="${esc(s)}" ${DIR_STATE.state === s ? 'selected' : ''}>${esc(s)}</option>`).join('')}
            </select>

            <select id="mf-party" onchange="window.onMemberFilter('party', this.value)">
              <option value="">All Parties (${parties.length})</option>
              ${parties.map(p => `<option value="${esc(p)}" ${DIR_STATE.party === p ? 'selected' : ''}>${esc(p)}</option>`).join('')}
            </select>

            <select id="mf-gender" onchange="window.onMemberFilter('gender', this.value)">
              <option value="">Gender: All</option>
              <option value="Male" ${DIR_STATE.gender === 'Male' ? 'selected' : ''}>Male</option>
              <option value="Female" ${DIR_STATE.gender === 'Female' ? 'selected' : ''}>Female</option>
            </select>

            <select id="mf-terms" onchange="window.onMemberFilter('terms', this.value)">
              <option value="">Terms: All</option>
              <option value="1" ${DIR_STATE.terms === '1' ? 'selected' : ''}>1st Term (New MP)</option>
              <option value="multi" ${DIR_STATE.terms === 'multi' ? 'selected' : ''}>Multi-Term (2+)</option>
            </select>

            <div class="mf-view-toggle">
              <button class="view-btn ${DIR_STATE.view === 'cards' ? 'on' : ''}" onclick="window.onMemberView('cards')" title="Card Grid View">Cards</button>
              <button class="view-btn ${DIR_STATE.view === 'table' ? 'on' : ''}" onclick="window.onMemberView('table')" title="Data Table View">Table</button>
            </div>
          </div>
        </div>

        <!-- Result Container -->
        <div id="members-results-container">
          ${renderFilteredMembersHtml()}
        </div>
      </div>
    `;
  }

  function getFilteredMembers() {
    if (!window.LS_MEMBERS) return [];
    let list = window.LS_MEMBERS;
    const q = (DIR_STATE.search || '').trim().toLowerCase();

    if (q) {
      list = list.filter(m => {
        return (m.name && m.name.toLowerCase().includes(q)) ||
               (m.constituency && m.constituency.toLowerCase().includes(q)) ||
               (m.state && m.state.toLowerCase().includes(q)) ||
               (m.party && m.party.toLowerCase().includes(q)) ||
               (m.party_code && m.party_code.toLowerCase().includes(q)) ||
               (m.education && m.education.toLowerCase().includes(q)) ||
               (m.profession && m.profession.toLowerCase().includes(q)) ||
               (m.other_profession && m.other_profession.toLowerCase().includes(q));
      });
    }

    if (DIR_STATE.state) {
      list = list.filter(m => m.state === DIR_STATE.state);
    }
    if (DIR_STATE.party) {
      list = list.filter(m => (m.party_code === DIR_STATE.party) || (m.party === DIR_STATE.party));
    }
    if (DIR_STATE.gender) {
      list = list.filter(m => (m.gender || '').toLowerCase() === DIR_STATE.gender.toLowerCase());
    }
    if (DIR_STATE.terms === '1') {
      list = list.filter(m => m.num_terms === 1);
    } else if (DIR_STATE.terms === 'multi') {
      list = list.filter(m => m.num_terms > 1);
    }

    return list;
  }

  function renderFilteredMembersHtml() {
    const filtered = getFilteredMembers();
    const count = filtered.length;

    if (!count) {
      return `
        <div class="members-empty">
          <h3>No Lok Sabha members match your search</h3>
          <p>Try clearing filters or checking the spelling.</p>
          <button class="btn on" onclick="window.clearMemberFilters()">Reset All Filters</button>
        </div>
      `;
    }

    const startIdx = 0;
    const endIdx = DIR_STATE.page * DIR_STATE.pageSize;
    const pageItems = filtered.slice(0, endIdx);
    const hasMore = endIdx < count;

    let content = '';

    if (DIR_STATE.view === 'table') {
      content = `
        <div class="mp-table-wrap">
          <div class="table-count-banner">Showing <b>${Math.min(endIdx, count)}</b> of <b>${count}</b> Lok Sabha Members</div>
          <table class="mp-data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Member &amp; Photo</th>
                <th>Constituency &amp; State</th>
                <th>Party</th>
                <th>Gender / Age</th>
                <th>Tenure</th>
                <th>Contact &amp; Social</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${pageItems.map(m => {
                const partyColor = (window.CM && window.CM[m.party_code]) ? window.CM[m.party_code] : '#ff6b00';
                return `
                  <tr class="mp-table-row">
                    <td class="mp-mono-id">#${m.id}</td>
                    <td>
                      <div class="mp-table-name-cell" onclick="window.openMpDossierModal(${m.id})">
                        ${renderMpAvatar(m, 36)}
                        <div>
                          <div class="mp-table-name">${esc(m.name)}</div>
                          <div class="mp-table-sub">${esc(m.qualification || m.other_profession || 'Parliamentarian')}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="mp-table-const">${esc(m.constituency)}</div>
                      <div class="mp-table-state">${esc(m.state)}</div>
                    </td>
                    <td>
                      <span class="mp-party-badge" style="background:${partyColor}22;color:${partyColor};border:1px solid ${partyColor}55">
                        ${esc(m.party_code || m.party)}
                      </span>
                    </td>
                    <td>${esc(m.gender || '–')}, ${m.age ? m.age + 'y' : '–'}</td>
                    <td>
                      <span class="mp-terms-badge">${m.num_terms > 1 ? m.num_terms + ' Terms' : '1st Term'}</span>
                    </td>
                    <td>
                      ${renderSocialLinks(m, true)}
                    </td>
                    <td>
                      <div class="mp-table-actions">
                        <button class="btn-table-oath" onclick="window.openOathVideoModal(${m.id})" title="Watch Oath Ceremony">
                          ${ICONS.play}
                        </button>
                        <button class="btn-table-view" onclick="window.openMpDossierModal(${m.id})">
                          Profile →
                        </button>
                      </div>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    } else {
      // Cards Grid View
      content = `
        <div class="table-count-banner">Showing <b>${Math.min(endIdx, count)}</b> of <b>${count}</b> Lok Sabha Members</div>
        <div class="mp-cards-grid">
          ${pageItems.map(m => {
            const partyColor = (window.CM && window.CM[m.party_code]) ? window.CM[m.party_code] : '#ff6b00';
            return `
              <div class="mp-grid-card">
                <div class="mp-grid-top">
                  ${renderMpAvatar(m, 56)}
                  <div class="mp-grid-info">
                    <div class="mp-grid-badges">
                      <span class="mp-id-badge">#LS-${m.id}</span>
                      <span class="mp-terms-badge">${m.num_terms > 1 ? m.num_terms + ' Terms' : '1st Term'}</span>
                    </div>
                    <h3 class="mp-grid-name" onclick="window.openMpDossierModal(${m.id})">${esc(m.name)}</h3>
                    <div class="mp-grid-loc">${esc(m.constituency)}, ${esc(m.state)}</div>
                  </div>
                </div>

                <div class="mp-grid-meta-row">
                  <span class="mp-party-badge" style="background:${partyColor}22;color:${partyColor};border:1px solid ${partyColor}55">
                    ${esc(m.party_code || m.party)}
                  </span>
                  <span class="mp-prof-pill">${esc(m.other_profession || m.profession || m.qualification || 'Lok Sabha MP')}</span>
                </div>

                ${renderSocialLinks(m, false)}

                <div class="mp-grid-footer">
                  <button class="btn-grid-oath" onclick="window.openOathVideoModal(${m.id})">
                    ${ICONS.play} <span>Watch Oath</span>
                  </button>
                  <button class="btn-grid-dossier" onclick="window.openMpDossierModal(${m.id})">
                    Dossier →
                  </button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `;
    }

    if (hasMore) {
      content += `
        <div style="text-align:center;margin:28px 0">
          <button class="btn on" style="padding:10px 24px;font-size:14px;border-radius:24px" onclick="window.loadMoreMembers()">
            Load More Members (${count - endIdx} remaining)
          </button>
        </div>
      `;
    }

    return content;
  }

  // Interactive filtering helpers
  window.onMemberSearch = function(val) {
    DIR_STATE.search = val;
    DIR_STATE.page = 1;
    const c = document.getElementById('members-results-container');
    if (c) c.innerHTML = renderFilteredMembersHtml();
  };

  window.onMemberFilter = function(key, val) {
    DIR_STATE[key] = val;
    DIR_STATE.page = 1;
    const c = document.getElementById('members-results-container');
    if (c) c.innerHTML = renderFilteredMembersHtml();
  };

  window.onMemberView = function(view) {
    DIR_STATE.view = view;
    const c = document.getElementById('members-results-container');
    if (c) c.innerHTML = renderFilteredMembersHtml();
    document.querySelectorAll('.view-btn').forEach(b => {
      b.classList.toggle('on', b.textContent.toLowerCase().includes(view));
    });
  };

  window.loadMoreMembers = function() {
    DIR_STATE.page += 1;
    const c = document.getElementById('members-results-container');
    if (c) c.innerHTML = renderFilteredMembersHtml();
  };

  window.clearMemberFilters = function() {
    DIR_STATE = { search: '', state: '', party: '', gender: '', terms: '', view: DIR_STATE.view, page: 1, pageSize: 24 };
    const si = document.getElementById('mf-search'); if (si) si.value = '';
    const st = document.getElementById('mf-state'); if (st) st.value = '';
    const sp = document.getElementById('mf-party'); if (sp) sp.value = '';
    const sg = document.getElementById('mf-gender'); if (sg) sg.value = '';
    const sm = document.getElementById('mf-terms'); if (sm) sm.value = '';
    const c = document.getElementById('members-results-container');
    if (c) c.innerHTML = renderFilteredMembersHtml();
  };

  // Video Theater Modal (Does NOT expose raw URL, provides sleek player UI)
  window.openOathVideoModal = function(id) {
    const m = getMemberById(id);
    if (!m) return;

    let modal = document.getElementById('oath-video-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'oath-video-modal';
      modal.className = 'oath-video-modal-backdrop';
      document.body.appendChild(modal);
    }

    const videoObj = m.video || {};
    const directYtId = videoObj.yt_id;
    const searchUrl = videoObj.search_url;

    let playerHtml = '';
    if (directYtId) {
      playerHtml = `
        <div class="video-iframe-container">
          <iframe src="https://www.youtube-nocookie.com/embed/${directYtId}?autoplay=1&rel=0" title="Sansad TV Oath Ceremony" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
      `;
    } else {
      // Safe, theater-like Sansad TV Player launcher without printing raw URL string
      playerHtml = `
        <div class="oath-player-card">
          <div class="oath-player-screen">
            <div class="oath-play-trigger" onclick="window.open('${esc(searchUrl || 'https://www.youtube.com/@SansadTV')}', '_blank', 'noopener,noreferrer')">
              <span class="pulse-play-ring"></span>
              <span class="player-big-play">${ICONS.play}</span>
            </div>
            <div class="oath-broadcast-badge">SANSAD TV OFFICIAL BROADCAST ARCHIVE</div>
          </div>
          <div class="oath-player-desc">
            <h4>Parliament of India — Oath Taking Broadcast</h4>
            <p>Watch the official Lok Sabha swearing-in ceremony for <b>${esc(m.name)}</b> recorded live on Sansad TV.</p>
            <button class="btn-play-launch" onclick="window.open('${esc(searchUrl || 'https://www.youtube.com/@SansadTV')}', '_blank', 'noopener,noreferrer')">
              ${ICONS.play} <span>Play Swearing-in Video on Sansad TV</span>
            </button>
          </div>
        </div>
      `;
    }

    modal.innerHTML = `
      <div class="oath-video-dialog" role="dialog" aria-modal="true">
        <div class="oath-video-header">
          <div class="oath-video-title-wrap">
            <span class="oath-tag">PARLIAMENTARY VIDEO</span>
            <h3>Oath Ceremony: ${esc(m.name)}</h3>
            <div class="oath-subtitle">18th Lok Sabha · ${esc(m.constituency)}, ${esc(m.state)}</div>
          </div>
          <button class="oath-close-btn" onclick="window.closeOathVideoModal()" aria-label="Close video player">✕</button>
        </div>
        <div class="oath-video-body">
          ${playerHtml}
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  };

  window.closeOathVideoModal = function() {
    const modal = document.getElementById('oath-video-modal');
    if (modal) {
      modal.innerHTML = '';
      modal.style.display = 'none';
    }
    document.body.style.overflow = '';
  };

  // Full Member Dossier Modal
  window.openMpDossierModal = function(id) {
    const m = getMemberById(id);
    if (!m) return;

    let modal = document.getElementById('mp-dossier-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'mp-dossier-modal';
      modal.className = 'mp-dossier-backdrop';
      document.body.appendChild(modal);
    }

    const partyColor = (window.CM && window.CM[m.party_code]) ? window.CM[m.party_code] : '#ff6b00';
    const positions = m.positions || [];

    modal.innerHTML = `
      <div class="mp-dossier-dialog" role="dialog" aria-modal="true">
        <!-- Close Button -->
        <button class="dossier-close-btn" onclick="window.closeMpDossierModal()" aria-label="Close dossier">✕</button>

        <!-- Header Hero -->
        <div class="dossier-hero">
          ${renderMpAvatar(m, 86)}
          <div class="dossier-hero-info">
            <div class="dossier-badge-row">
              <span class="mp-sitting-pill"><span class="pulse-dot"></span> SITTING MP</span>
              <span class="mp-id-badge">#LS-${m.id}</span>
              <span class="mp-terms-badge">${m.num_terms > 1 ? m.num_terms + ' Terms' : '1st Term'} (18th LS)</span>
            </div>
            <h2 class="dossier-name">${esc(m.name)}</h2>
            <div class="dossier-meta">
              <span class="mp-party-badge" style="background:${partyColor}22;color:${partyColor};border:1px solid ${partyColor}55">
                <b>${esc(m.party_code || m.party)}</b>
              </span>
              <span>${esc(m.constituency)}, ${esc(m.state)}</span>
              <span>·</span>
              <span>Age: ${m.age || '–'}</span>
              <span>·</span>
              <span>${esc(m.gender || '–')}</span>
            </div>
          </div>
        </div>

        <!-- Quick Action Bar -->
        <div class="dossier-action-bar">
          <button class="btn-oath-watch" onclick="window.openOathVideoModal(${m.id})">
            ${ICONS.play} <span>Watch Oath Ceremony</span>
          </button>
          ${m.source_profile ? `<a href="${esc(m.source_profile)}" target="_blank" rel="noopener noreferrer" class="btn-sansad-link">${ICONS.external} <span>Official Sansad Profile</span></a>` : ''}
          ${renderSocialLinks(m, false)}
        </div>

        <!-- Tabbed Content Section -->
        <div class="dossier-tabs-nav">
          <button class="dtab-btn on" id="dtab-overview-btn" onclick="window.switchDossierTab('overview')">📋 Overview &amp; Bio</button>
          <button class="dtab-btn" id="dtab-positions-btn" onclick="window.switchDossierTab('positions')">🏛️ Positions Held (${positions.length})</button>
          <button class="dtab-btn" id="dtab-contact-btn" onclick="window.switchDossierTab('contact')">📞 Offices &amp; Contact</button>
          <button class="dtab-btn" id="dtab-activities-btn" onclick="window.switchDossierTab('activities')">🌟 Interests &amp; Activities</button>
        </div>

        <div class="dossier-tab-content">
          <!-- Overview Tab -->
          <div class="dtab-panel" id="dtab-overview">
            <div class="dossier-grid-2">
              <div class="dossier-box">
                <h4>🎓 Education &amp; Background</h4>
                <div class="dbox-item"><b>Qualification:</b> <span>${esc(m.qualification || '–')}</span></div>
                <div class="dbox-item"><b>Education:</b> <span style="white-space:pre-line">${esc(m.education || '–')}</span></div>
                <div class="dbox-item"><b>Profession:</b> <span>${esc(m.other_profession || m.profession || '–')}</span></div>
              </div>

              <div class="dossier-box">
                <h4>👨‍👩‍👧 Family &amp; Birth Details</h4>
                <div class="dbox-item"><b>Date of Birth:</b> <span>${esc(m.dob || '–')}</span></div>
                <div class="dbox-item"><b>Birth Place:</b> <span>${esc(m.birth_place || '–')}</span></div>
                <div class="dbox-item"><b>Father's Name:</b> <span>${esc(m.father || '–')}</span></div>
                <div class="dbox-item"><b>Mother's Name:</b> <span>${esc(m.mother || '–')}</span></div>
                <div class="dbox-item"><b>Spouse:</b> <span>${esc(m.spouse || '–')}</span></div>
                <div class="dbox-item"><b>Children:</b> <span>${m.sons} Son(s), ${m.daughters} Daughter(s)</span></div>
                <div class="dbox-item"><b>Marital Status:</b> <span>${esc(m.marital_status || '–')}</span></div>
              </div>
            </div>

            <div class="dossier-box" style="margin-top:14px">
              <h4>🏛️ Parliamentary Terms</h4>
              <p>Lok Sabha Terms Represented: <b>${esc(m.terms || '18')}</b> (Total: <b>${m.num_terms}</b> terms)</p>
            </div>
          </div>

          <!-- Positions Held Tab -->
          <div class="dtab-panel" id="dtab-positions" style="display:none">
            ${positions.length ? `
              <div class="positions-timeline">
                ${positions.map(p => `
                  <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <div class="timeline-period">${esc(p.period || 'Parliamentary Tenure')}</div>
                      <div class="timeline-title">${esc(p.position || '–')}</div>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `<p class="note">No specific committee positions recorded yet for this tenure.</p>`}
          </div>

          <!-- Contact Tab -->
          <div class="dtab-panel" id="dtab-contact" style="display:none">
            <div class="dossier-grid-2">
              <div class="dossier-box">
                <h4>🏛️ Delhi Residence &amp; Office</h4>
                <div class="dbox-item"><b>Address:</b> <span>${esc(m.present_address || 'New Delhi')}</span></div>
                <div class="dbox-item"><b>Delhi Phone:</b> <span>${m.delhi_phone ? `<a href="tel:${esc(m.delhi_phone)}">${esc(m.delhi_phone)}</a>` : '–'}</span></div>
              </div>

              <div class="dossier-box">
                <h4>🏡 Permanent Home Residence</h4>
                <div class="dbox-item"><b>Address:</b> <span>${esc(m.permanent_address || '–')}</span></div>
                <div class="dbox-item"><b>Personal Phone:</b> <span>${m.phone ? `<a href="tel:${esc(m.phone)}">${esc(m.phone)}</a>` : '–'}</span></div>
                <div class="dbox-item"><b>Email:</b> <span style="white-space:pre-line">${m.email ? esc(m.email) : '–'}</span></div>
              </div>
            </div>
          </div>

          <!-- Activities Tab -->
          <div class="dtab-panel" id="dtab-activities" style="display:none">
            <div class="dossier-box">
              <h4>🌟 Social &amp; Literary Pursuits</h4>
              <div class="dbox-item"><b>Social Activities:</b> <span>${esc(m.social_activities || '–')}</span></div>
              <div class="dbox-item"><b>Hobbies:</b> <span>${esc(m.hobbies || '–')}</span></div>
              <div class="dbox-item"><b>Interests:</b> <span>${esc(m.interests || '–')}</span></div>
              <div class="dbox-item"><b>Sports:</b> <span>${esc(m.sports || '–')}</span></div>
              <div class="dbox-item"><b>Books Published:</b> <span>${esc(m.books || '–')}</span></div>
              <div class="dbox-item"><b>Countries Visited:</b> <span>${esc(m.countries_visited || '–')}</span></div>
            </div>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  };

  window.closeMpDossierModal = function() {
    const modal = document.getElementById('mp-dossier-modal');
    if (modal) {
      modal.style.display = 'none';
    }
    document.body.style.overflow = '';
  };

  window.switchDossierTab = function(tabName) {
    ['overview', 'positions', 'contact', 'activities'].forEach(t => {
      const btn = document.getElementById('dtab-' + t + '-btn');
      const panel = document.getElementById('dtab-' + t);
      if (btn) btn.classList.toggle('on', t === tabName);
      if (panel) panel.style.display = (t === tabName) ? 'block' : 'none';
    });
  };

  // Close modals on outside click or ESC key
  window.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      window.closeOathVideoModal();
      window.closeMpDossierModal();
    }
  });

  document.addEventListener('click', function(e) {
    const vModal = document.getElementById('oath-video-modal');
    if (vModal && e.target === vModal) window.closeOathVideoModal();
    const dModal = document.getElementById('mp-dossier-modal');
    if (dModal && e.target === dModal) window.closeMpDossierModal();
  });

  // Export functions to global scope
  window.getMemberForPC = getMemberForPC;
  window.getMemberById = getMemberById;
  window.renderConstituencyMpCard = renderConstituencyMpCard;
  window.renderLsMembersHub = renderLsMembersHub;

})();
