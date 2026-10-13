/**
 * ELECTROL INDIA — Municipal Corporations & Municipal Councils Hub
 * Covers 29 Municipal Corporations & 224 Municipal Councils
 * Features:
 * - Ward-by-ward results & reservations
 * - Standardized party names (No duplicate Shiv Sena / BJP entries)
 * - State filter (Maharashtra with 29 Corps & 224 Councils)
 * - 2026 vs 2017 Historical Election Comparison & Seat Swings
 * - Directly-Elected Council Presidents (Nagaradhyaksha)
 */

(function() {
  'use strict';

  // Standard Party Colors
  const PARTY_COLORS = {
    'BJP': '#ff6b00',
    'Shiv Sena': '#ff9933',
    'Shiv Sena (UBT)': '#d84315',
    'INC': '#1565c0',
    'NCP': '#00838f',
    'NCP (SP)': '#c2185b',
    'AIMIM': '#00796b',
    'MNS': '#d63031',
    'VBA': '#8e24aa',
    'BVA': '#e67e22',
    'PWPI': '#c0392b',
    'SP': '#d62828',
    'BSP': '#0984e3',
    'CPI(M)': '#b71c1c',
    'RPI(A)': '#2980b9',
    'Independent': '#78909c',
    'NOTA': '#9e9e9e'
  };

  function getPartyColor(p) {
    if (!p) return '#78909c';
    if (PARTY_COLORS[p]) return PARTY_COLORS[p];
    const up = p.toUpperCase();
    if (up.includes('UBT') || up.includes('UDDHAV')) return PARTY_COLORS['Shiv Sena (UBT)'];
    if (up.includes('SHIV')) return PARTY_COLORS['Shiv Sena'];
    if (up.includes('JANATA') || up.includes('BJP')) return PARTY_COLORS['BJP'];
    if (up.includes('CONGRESS') && !up.includes('NATIONALIST')) return PARTY_COLORS['INC'];
    if (up.includes('SHARAD') || up.includes('(SP)')) return PARTY_COLORS['NCP (SP)'];
    if (up.includes('NATIONALIST') || up.includes('NCP')) return PARTY_COLORS['NCP'];
    return '#64748b';
  }

  const fmt = n => (n === null || n === undefined || isNaN(n)) ? '–' : Number(n).toLocaleString('en-IN');
  const esc = s => String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  // All 36 States & Union Territories of India for Civic Governance Filter
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

  // Known Urban Local Bodies for All States & Union Territories
  const STATE_LOCAL_BODIES = {
    'Andhra Pradesh': {
      corps: ['Greater Visakhapatnam (GVMC)', 'Vijayawada (VMC)', 'Guntur (GMC)', 'Tirupati (MCT)', 'Kurnool', 'Nellore', 'Rajahmundry', 'Kakinada', 'Kadapa', 'Anantapur', 'Eluru', 'Ongole', 'Vizianagaram', 'Machilipatnam', 'Chittoor', 'Srikakulam', 'Mangalagiri-Tadepalli'],
      councils: ['Tadepalligudem', 'Narasaraopet', 'Gudivada', 'Madanapalle', 'Hindupur', 'Bhimavaram', 'Tenali', 'Proddatur', 'Adoni', 'Dharmavaram']
    },
    'Gujarat': {
      corps: ['Ahmedabad (AMC)', 'Surat (SMC)', 'Vadodara (VMC)', 'Rajkot (RMC)', 'Bhavnagar (BMC)', 'Jamnagar (JMC)', 'Junagadh (JMC)', 'Gandhinagar (GMC)'],
      councils: ['Anand', 'Nadiad', 'Morbi', 'Mehsana', 'Surendranagar', 'Bharuch', 'Navsari', 'Vapi', 'Porbandar', 'Godhra', 'Patan', 'Veraval']
    },
    'Karnataka': {
      corps: ['Bruhat Bengaluru Mahanagara Palike (BBMP)', 'Mysuru (MCC)', 'Hubballi-Dharwad (HDMC)', 'Mangaluru (MCC)', 'Belagavi', 'Kalaburagi', 'Davanagere', 'Ballari', 'Vijayapura', 'Shivamogga', 'Tumakuru'],
      councils: ['Udupi', 'Bidar', 'Hospet', 'Gadag-Betageri', 'Robertsonpet', 'Bhadravati', 'Chitradurga', 'Kolar', 'Mandya', 'Hassan']
    },
    'Tamil Nadu': {
      corps: ['Greater Chennai Corporation', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Tiruppur', 'Erode', 'Vellore', 'Thoothukudi', 'Dindigul', 'Thanjavur', 'Hosur', 'Nagercoil', 'Avadi', 'Tambaram', 'Kancheepuram', 'Karur', 'Cuddalore', 'Sivakasi'],
      councils: ['Kumbakonam', 'Rajapalayam', 'Pudukkottai', 'Ambur', 'Karaikudi', 'Neyveli', 'Nagapattinam', 'Viluppuram', 'Paramakudi', 'Tiruchengode']
    },
    'Telangana': {
      corps: ['Greater Hyderabad Municipal Corporation (GHMC)', 'Warangal (GWMC)', 'Nizamabad', 'Karimnagar', 'Ramagundam', 'Khammam', 'Badangpet', 'Bandlaguda Jagir', 'Meerpet', 'Boduppal', 'Peerzadiguda', 'Jawaharnagar', 'Nizampet'],
      councils: ['Siddipet', 'Suryapet', 'Miryalaguda', 'Nalgonda', 'Adilabad', 'Mancherial', 'Kothagudem', 'Jagtial', 'Kamareddy', 'Mahbubnagar']
    },
    'Uttar Pradesh': {
      corps: ['Lucknow', 'Kanpur', 'Varanasi', 'Agra', 'Prayagraj', 'Ghaziabad', 'Meerut', 'Bareilly', 'Aligarh', 'Moradabad', 'Saharanpur', 'Gorakhpur', 'Firozabad', 'Jhansi', 'Mathura-Vrindavan', 'Ayodhya', 'Shahjahanpur'],
      councils: ['Muzaffarnagar', 'Mathura', 'Rampur', 'Shahjahanpur', 'Farrukhabad', 'Maunath Bhanjan', 'Hapur', 'Etawah', 'Mirzapur', 'Bulandshahr']
    },
    'West Bengal': {
      corps: ['Kolkata (KMC)', 'Howrah (HMC)', 'Asansol', 'Siliguri', 'Durgapur', 'Chandannagar', 'Bidhannagar'],
      councils: ['Bhatpara', 'South Dum Dum', 'Kamarhati', 'Baranagar', 'North Dum Dum', 'Panihati', 'Kharagpur', 'Haldia', 'Burdwan', 'Baharampur']
    },
    'Delhi (NCT)': {
      corps: ['Municipal Corporation of Delhi (MCD)'],
      councils: ['New Delhi Municipal Council (NDMC)', 'Delhi Cantonment Board']
    },
    'Madhya Pradesh': {
      corps: ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna', 'Ratlam', 'Rewa', 'Singrauli', 'Burhanpur', 'Morena', 'Khandwa', 'Chhindwara', 'Katni'],
      councils: ['Vidisha', 'Damoh', 'Mandsaur', 'Khargone', 'Neemuch', 'Pithampur', 'Hoshangabad', 'Sehore', 'Betul', 'Seoni']
    },
    'Bihar': {
      corps: ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Bihar Sharif', 'Darbhanga', 'Purnia', 'Begusarai', 'Katihar', 'Munger', 'Chhapra', 'Arrah', 'Saharsa', 'Sasaram', 'Bettiah', 'Motihari', 'Samastipur'],
      councils: ['Dehri', 'Siwan', 'Buxar', 'Kishanganj', 'Sitamarhi', 'Jamui', 'Bagaha', 'Hajipur', 'Jehanabad', 'Nawada']
    },
    'Rajasthan': {
      corps: ['Jaipur Greater', 'Jaipur Heritage', 'Jodhpur North', 'Jodhpur South', 'Kota North', 'Kota South', 'Bikaner', 'Ajmer', 'Udaipur', 'Bharatpur'],
      councils: ['Alwar', 'Bhilwara', 'Sriganganagar', 'Pali', 'Sikar', 'Tonk', 'Kishangarh', 'Beawar', 'Hanumangarh', 'Dholpur']
    },
    'Kerala': {
      corps: ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Kollam', 'Thrissur', 'Kannur'],
      councils: ['Alappuzha', 'Palakkad', 'Kottayam', 'Thalassery', 'Ponnani', 'Manjeri', 'Vatakara', 'Kanhangad', 'Payyanur', 'Koyilandy']
    },
    'Punjab': {
      corps: ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali (SAS Nagar)', 'Hoshiarpur', 'Moga', 'Pathankot', 'Phagwara', 'Batala', 'Abohar', 'Kapurthala'],
      councils: ['Khanna', 'Muktsar', 'Barnala', 'Firozpur', 'Malerkotla', 'Rajpura', 'Sunam', 'Fazilka', 'Mansa', 'Faridkot']
    },
    'Haryana': {
      corps: ['Gurugram (MCG)', 'Faridabad (MCF)', 'Panipat', 'Karnal', 'Rohtak', 'Hisar', 'Yamunanagar', 'Panchkula', 'Sonipat', 'Ambala', 'Manesar'],
      councils: ['Sirsa', 'Thanesar', 'Bahadurgarh', 'Jind', 'Rewari', 'Palwal', 'Hansi', 'Narnaul', 'Fatehabad', 'Kaithal']
    },
    'Chhattisgarh': {
      corps: ['Raipur', 'Bhilai', 'Bilaspur', 'Korba', 'Durg', 'Rajnandgaon', 'Jagdalpur', 'Ambikapur', 'Raigarh', 'Dhamtari', 'Birgaon', 'Chirmiri', 'Risali', 'Bhilai-Charoda'],
      councils: ['Mahasamund', 'Kanker', 'Kawardha', 'Bhatapara', 'Dalli-Rajhara', 'Dongargarh', 'Naila Janjgir', 'Tilda Newra']
    },
    'Goa': {
      corps: ['Corporation of the City of Panaji (CCP)'],
      councils: ['Margao', 'Mormugao', 'Mapusa', 'Ponda', 'Curchorem-Cacora', 'Cuncolim', 'Canacona', 'Bicholim', 'Valpoi', 'Sanquelim', 'Pernem', 'Quepem', 'Sanguem']
    },
    'Assam': {
      corps: ['Guwahati Municipal Corporation (GMC)', 'Silchar Municipal Corporation'],
      councils: ['Dibrugarh', 'Jorhat', 'Nagaon', 'Tinsukia', 'Tezpur', 'Bongaigaon', 'Dhubri', 'Diphu', 'North Lakhimpur', 'Karimganj']
    },
    'Himachal Pradesh': {
      corps: ['Shimla', 'Dharamshala', 'Mandi', 'Solan', 'Palampur'],
      councils: ['Baddi', 'Nahan', 'Paonta Sahib', 'Sundernagar', 'Kullu', 'Chamba', 'Una', 'Bilaspur', 'Hamirpur', 'Nurpur']
    },
    'Uttarakhand': {
      corps: ['Dehradun', 'Haridwar', 'Haldwani', 'Rudrapur', 'Roorkee', 'Kashipur', 'Rishikesh', 'Kotdwar', 'Srinagar'],
      councils: ['Pithoragarh', 'Ramnagar', 'Manglaur', 'Jaspur', 'Kichha', 'Mussoorie', 'Nainital', 'Almora', 'Tehri', 'Pauri']
    },
    'Odisha': {
      corps: ['Bhubaneswar (BMC)', 'Cuttack (CMC)', 'Rourkela', 'Berhampur', 'Sambalpur'],
      councils: ['Puri', 'Balasore', 'Bhadrak', 'Baripada', 'Jharsuguda', 'Bargarh', 'Jeypore', 'Angul', 'Dhenkanal', 'Kendrapara']
    },
    'Jharkhand': {
      corps: ['Ranchi (RMC)', 'Dhanbad (DMC)', 'Giridih', 'Chas', 'Deoghar', 'Adityapur', 'Hazaribagh', 'Medininagar', 'Mango'],
      councils: ['Jamshedpur', 'Ramgarh', 'Bishrampur', 'Chaibasa', 'Chakradharpur', 'Dumka', 'Gumia', 'Jhumri Telaiya', 'Lohardaga', 'Pakur']
    }
  };

  let ACTIVE_STATE = 'Maharashtra';
  let ACTIVE_SECTION = 'corps'; // 'corps', 'councils', 'compare', 'presidents'
  let ACTIVE_YEAR = '2026';      // '2026', '2017'
  let ACTIVE_MODAL_CORP = null;
  let ACTIVE_MODAL_COUNCIL = null;

  // Render Hub
  window.renderMhLocalHub = function(defaultSec) {
    if (defaultSec === 'councils') ACTIVE_SECTION = 'councils';
    else if (defaultSec === 'corps') ACTIVE_SECTION = 'corps';
    else if (defaultSec === 'compare') ACTIVE_SECTION = 'compare';
    else if (defaultSec === 'presidents') ACTIVE_SECTION = 'presidents';
    const summary = window.MH_MUNC_SUMMARY || {
      total_corps: 29,
      total_councils: 224,
      corps_seats_2026: 2810,
      corps_seats_2017: 2056,
      councils_seats_2025: 5389,
      corp_tally_2026: [],
      corp_tally_2017: [],
      comparison_parties: []
    };

    const corps = window.MH_CORPS || [];
    const councils = window.MH_COUNCILS || [];

    // Distinct districts in Maharashtra
    const distSet = new Set();
    corps.forEach(c => c.district && distSet.add(c.district));
    const sortedDistricts = Array.from(distSet).sort();

    setTimeout(() => {
      initListeners();
      renderActiveView();
    }, 10);

    return `
      <div class="bc">
        <a onclick="go('')">Home</a> <span>›</span>
        <a onclick="go('mh')">Maharashtra</a> <span>›</span>
        <span>Municipal Corporations &amp; Councils</span>
      </div>

      <!-- Hero Header -->
      <div class="mh-local-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                URBAN LOCAL ELECTIONS
              </span>
              <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                MAHARASHTRA
              </span>
            </div>
            <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
              🏛️ Municipal Corporations &amp; Municipal Councils
            </h1>
            <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
              Comprehensive ward-by-ward election results, reservation matrix, and historical seat comparison across <b>29 Municipal Corporations</b> (2,810 Wards) and <b>224 Municipal Councils</b> (5,389 Seats &amp; Council Presidents).
            </p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn" onclick="go('mh')">🏢 MH Assembly (288 AC) →</button>
            <button class="btn" onclick="go('ls')">🏛️ Lok Sabha (48 PC) →</button>
          </div>
        </div>

        <!-- High Level Metrics Bar -->
        <div class="g g4" style="margin-top:20px;gap:12px">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL CORPORATIONS</div>
            <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">29</div>
            <div style="font-size:11.5px;color:var(--text-2)">2,810 Wards &amp; Seats · BMC, Pune, Thane, etc.</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL COUNCILS</div>
            <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">224</div>
            <div style="font-size:11.5px;color:var(--text-2)">5,389 Wards &amp; Nagaradhyaksha Presidents</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">HISTORICAL COMPARISON</div>
            <div style="font-size:26px;font-weight:800;color:#4ade80;margin:4px 0">2017 vs 2026</div>
            <div style="font-size:11.5px;color:var(--text-2)">Track seat gains, swings &amp; party shifts</div>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
            <div style="font-size:12px;color:var(--text-2);font-weight:600">POPULATION COVERED</div>
            <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">3.2+ Cr</div>
            <div style="font-size:11.5px;color:var(--text-2)">Voters in Urban Maharashtra Governance</div>
          </div>
        </div>
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
      </div>

            <!-- State & Year Selection Layer Gateway -->
      <div class="civic-gateway-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
              <span class="mycorp-brand-pill" style="background:#ff9933;color:#000">CIVIC GOVERNANCE GATEWAY</span>
              <span class="mycorp-stat-pill">📍 ALL 36 STATES &amp; UNION TERRITORIES</span>
              <span class="mycorp-stat-pill">⚡ CURRENT ACTIVE: ${esc(ACTIVE_STATE)}</span>
            </div>
            <h3 style="margin:2px 0;font-size:17px;color:var(--text)">
              Select State &amp; Election Year
            </h3>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <span style="font-size:12px;color:var(--text-2);font-weight:600">State:</span>
            <select style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:12.5px;font-weight:700" onchange="onStateFilterChange(this.value)">
              ${renderStateFilterOptions(ACTIVE_STATE)}
            </select>
          </div>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${ALL_INDIA_STATES.slice(0, 12).map(st => `
            <button class="tab-pill ${st.name.toLowerCase() === (ACTIVE_STATE||'').toLowerCase() ? 'on' : ''}" style="font-size:11.5px;padding:3px 10px;margin:0" onclick="onStateFilterChange('${esc(st.name)}')">
              ${st.active ? '📍 ' : ''}${esc(st.name)} ${st.active ? `(${st.corps || st.councils})` : ''}
            </button>
          `).join('')}
          <button class="tab-pill" style="font-size:11.5px;padding:3px 10px;margin:0;opacity:0.8" onclick="document.getElementById('munc-state-filter').focus()">
            + More States (${ALL_INDIA_STATES.length - 12})
          </button>
        </div>
      </div>

      <!-- Primary Navigation Toolbar: Section Tabs & State Selector -->
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin:20px 0 16px">
        <!-- Section Tabs -->
        <div class="tab-pills" style="margin:0">
          <button class="tab-pill on" id="sec-btn-corps" onclick="switchMuncSection('corps')">
            🏙️ Municipal Corporations (29)
          </button>
          <button class="tab-pill" id="sec-btn-councils" onclick="switchMuncSection('councils')">
            🏢 Municipal Councils (224)
          </button>
          <button class="tab-pill" id="sec-btn-compare" onclick="switchMuncSection('compare')">
            ⚖️ 2017 vs 2026 Comparison
          </button>
          <button class="tab-pill" id="sec-btn-presidents" onclick="switchMuncSection('presidents')">
            👑 Council Presidents
          </button>
        </div>

        <!-- State Filter Dropdown -->
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:12px;font-weight:600;color:var(--text-2);white-space:nowrap">Select State:</span>
          <select id="munc-state-filter" style="padding:6px 12px;border-radius:6px;background:var(--s1);color:var(--text);border:1px solid var(--b);font-size:13px;font-weight:600" onchange="onStateFilterChange(this.value)">
            ${renderStateFilterOptions(ACTIVE_STATE)}
          </select>
        </div>
      </div>

      <!-- Controls & Filter Toolbar (Compact Sleek Design) -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Search corporation, council, or ward..." aria-label="Search Municipal" oninput="renderActiveView()">
        </div>

        <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
          <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
          ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
        </select>

        <!-- Year Filter Toggle -->
        <div id="munc-year-wrap" style="display:flex;align-items:center;gap:6px">
          <span style="font-size:12px;color:var(--text-2);font-weight:600">Year:</span>
          <div class="tab-pills" style="margin:0">
            <button class="tab-pill ${ACTIVE_YEAR==='2026'?'on':''}" id="yr-btn-2026" onclick="setMuncYear('2026')">2026</button>
            <button class="tab-pill ${ACTIVE_YEAR==='2025'?'on':''}" id="yr-btn-2025" onclick="setMuncYear('2025')">2025</button>
            <button class="tab-pill ${ACTIVE_YEAR==='2017'?'on':''}" id="yr-btn-2017" onclick="setMuncYear('2017')">2017</button>
            <button class="tab-pill ${ACTIVE_YEAR==='all'?'on':''}" id="yr-btn-all" onclick="setMuncYear('all')">All Years</button>
          </div>
        </div>

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
          <option value="pop-desc">Population: Largest first</option>
        </select>
      </div>

      <!-- Main Dynamic Content Container -->
      <div id="munc-content-area">
        <p class="note">Loading municipal records…</p>
      </div>

      <!-- Full-Screen Ward-by-Ward Modal Container -->
      <div id="munc-modal-wrap" style="display:none"></div>
    `;
  };

  function initListeners() {
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeMuncModal();
    });
  }

  window.switchMuncSection = function(sec) {
    ACTIVE_SECTION = sec;
    ['corps', 'councils', 'compare', 'presidents'].forEach(s => {
      const btn = document.getElementById('sec-btn-' + s);
      if (btn) btn.classList.toggle('on', s === sec);
    });

    // Hide or show year toggle depending on section
    const yrWrap = document.getElementById('munc-year-wrap');
    if (yrWrap) {
      yrWrap.style.display = (sec === 'corps') ? 'flex' : 'none';
    }

    renderActiveView();
  };

  window.setMuncYear = function(yr) {
    ACTIVE_YEAR = yr;
    ['2026', '2025', '2017', 'all'].forEach(y => {
      const btn = document.getElementById('yr-btn-' + y);
      if (btn) btn.classList.toggle('on', y === yr);
    });
    renderActiveView();
  };

  // Dynamic Hero Header Generator for Corporations & Councils
  function renderHeroHeader(section, stateName) {
    stateName = stateName || ACTIVE_STATE || 'Maharashtra';
    const stObj = ALL_INDIA_STATES.find(s => s.name.toLowerCase() === stateName.toLowerCase()) || {
      name: stateName, corps: '–', councils: '–', active: false
    };
    const isMh = stObj.name.toLowerCase() === 'maharashtra';
    const isCorps = section === 'corps';

    if (isCorps) {
      if (isMh) {
        return `
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
        `;
      } else {
        return `
          <div class="mh-local-hero">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span class="badge" style="background:#ff9933;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                    CIVIC GOVERNANCE
                  </span>
                  <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                    ${esc(stObj.name.toUpperCase())}
                  </span>
                </div>
                <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
                  🏛️ ${esc(stObj.name)} Municipal Corporations
                </h1>
                <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
                  Urban local body election records, ward delimitations, and municipal governance across <b>${stObj.corps || '–'} Municipal Corporations</b> in ${esc(stObj.name)}.
                </p>
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="btn on" onclick="go('councils')">🏢 Municipal Councils (${stObj.councils || '–'}) →</button>
                <button class="btn" onclick="onStateFilterChange('Maharashtra')">📍 Switch to Maharashtra Active Data →</button>
              </div>
            </div>

            <!-- Metrics Cards -->
            <div class="g g4" style="margin-top:20px;gap:12px">
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL CORPORATIONS</div>
                <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">${stObj.corps || '–'}</div>
                <div style="font-size:11.5px;color:var(--text-2)">Mahanagar Palikas in ${esc(stObj.name)}</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL COUNCILS</div>
                <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">${stObj.councils || '–'}</div>
                <div style="font-size:11.5px;color:var(--text-2)">Nagar Palikas &amp; Municipalities</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">SEC SYNC STATUS</div>
                <div style="font-size:26px;font-weight:800;color:#4ade80;margin:4px 0">Pipeline Queue</div>
                <div style="font-size:11.5px;color:var(--text-2)">Syncing State Election Commission</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">COVERAGE</div>
                <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">All Districts</div>
                <div style="font-size:11.5px;color:var(--text-2)">Urban local bodies across ${esc(stObj.name)}</div>
              </div>
            </div>
          </div>
        `;
      }
    } else {
      // councils
      if (isMh) {
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
        `;
      } else {
        return `
          <div class="mh-local-hero">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span class="badge" style="background:#38bdf8;color:#000;font-weight:800;font-size:11px;padding:3px 8px;border-radius:4px">
                    CIVIC GOVERNANCE
                  </span>
                  <span class="badge" style="background:rgba(255,255,255,0.12);color:var(--text);font-size:11px;padding:3px 8px;border-radius:4px">
                    ${esc(stObj.name.toUpperCase())}
                  </span>
                </div>
                <h1 style="margin:4px 0 8px;font-size:clamp(22px, 3.2vw, 32px);color:var(--text)">
                  🏢 ${esc(stObj.name)} Municipal Councils
                </h1>
                <p style="color:var(--text-2);margin:0;max-width:820px;font-size:14px;line-height:1.5">
                  Urban local body councillor tallies, Nagar Palika governance, and council elections across <b>${stObj.councils || '–'} Municipal Councils</b> in ${esc(stObj.name)}.
                </p>
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="btn on" onclick="go('corporations')">🏛️ Municipal Corporations (${stObj.corps || '–'}) →</button>
                <button class="btn" onclick="onStateFilterChange('Maharashtra')">📍 Switch to Maharashtra Active Data →</button>
              </div>
            </div>

            <!-- Metrics Cards -->
            <div class="g g4" style="margin-top:20px;gap:12px">
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL COUNCILS</div>
                <div style="font-size:26px;font-weight:800;color:#38bdf8;margin:4px 0">${stObj.councils || '–'}</div>
                <div style="font-size:11.5px;color:var(--text-2)">Nagar Palikas &amp; Parishads in ${esc(stObj.name)}</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">MUNICIPAL CORPORATIONS</div>
                <div style="font-size:26px;font-weight:800;color:#ff9933;margin:4px 0">${stObj.corps || '–'}</div>
                <div style="font-size:11.5px;color:var(--text-2)">Mahanagar Palikas</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">SEC SYNC STATUS</div>
                <div style="font-size:26px;font-weight:800;color:#4ade80;margin:4px 0">Pipeline Queue</div>
                <div style="font-size:11.5px;color:var(--text-2)">Syncing State Election Commission</div>
              </div>
              <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px 16px">
                <div style="font-size:12px;color:var(--text-2);font-weight:600">COVERAGE</div>
                <div style="font-size:26px;font-weight:800;color:#facc15;margin:4px 0">All Districts</div>
                <div style="font-size:11.5px;color:var(--text-2)">Urban councils across ${esc(stObj.name)}</div>
              </div>
            </div>
          </div>
        `;
      }
    }
  }

  // Update Corporation / Council Dropdown Options based on Selected State
  function updateEntitySelectOptions(section, stateName) {
    stateName = stateName || ACTIVE_STATE || 'Maharashtra';
    const sel = document.getElementById(section === 'corps' ? 'munc-corp-select' : 'munc-council-select');
    if (!sel) return;

    const isMh = stateName.toLowerCase() === 'maharashtra';
    let optionsHtml = '';

    if (section === 'corps') {
      if (isMh) {
        const corps = window.MH_CORPS || [];
        optionsHtml = `<option value="">All 29 Corporations (BMC, Pune, Thane...)</option>` +
          corps.map(c => `<option value="${esc(c.name)}">${esc(c.name)}${c.seat_count_2026 ? ` (${c.seat_count_2026} Seats)` : ''}</option>`).join('');
      } else {
        const data = STATE_LOCAL_BODIES[stateName];
        const corpsList = (data && data.corps) ? data.corps : [];
        if (corpsList.length) {
          optionsHtml = `<option value="">All Corporations in ${esc(stateName)} (${corpsList.length})</option>` +
            corpsList.map(name => `<option value="${esc(name)}">${esc(name)}</option>`).join('');
        } else {
          optionsHtml = `<option value="">Select or Enter Corporation in ${esc(stateName)}</option>`;
        }
      }
    } else {
      if (isMh) {
        const councils = window.MH_COUNCILS || [];
        optionsHtml = `<option value="">All 224 Municipal Councils (Akluj, Ambarnath...)</option>` +
          councils.map(c => `<option value="${esc(c.name)}">${esc(c.name)}${c.district ? ` (${c.district})` : ''}</option>`).join('');
      } else {
        const data = STATE_LOCAL_BODIES[stateName];
        const councilsList = (data && data.councils) ? data.councils : [];
        if (councilsList.length) {
          optionsHtml = `<option value="">All Municipal Councils in ${esc(stateName)} (${councilsList.length})</option>` +
            councilsList.map(name => `<option value="${esc(name)}">${esc(name)}</option>`).join('');
        } else {
          optionsHtml = `<option value="">Select or Enter Council in ${esc(stateName)}</option>`;
        }
      }
    }

    sel.innerHTML = optionsHtml;
  }

  // Non-Active State / Entity View
  function renderNonActiveEntityView(entityName, entityType) {
    const area = document.getElementById('munc-content-area');
    if (!area) return;
    if (!entityName) {
      renderNonActiveStateCivicView(area, ACTIVE_STATE, entityType + 's');
      return;
    }
    area.innerHTML = `
      <div class="card" style="padding:32px 24px;text-align:center;background:var(--s1);border:1px solid var(--b);border-radius:14px;margin:20px 0">
        <div style="font-size:38px;margin-bottom:8px">🏛️</div>
        <h2 style="margin:0 0 8px;font-size:22px;color:var(--text)">
          ${esc(entityName)} — ${esc(ACTIVE_STATE)}
        </h2>
        <p style="margin:0 auto 18px;max-width:700px;font-size:13.5px;color:var(--text-2);line-height:1.55">
          Official ward delimitation, corporator directory, and election statistics for <b>${esc(entityName)}</b> in <b>${esc(ACTIVE_STATE)}</b> are currently being indexed in our SEC governance synchronization pipeline.
        </p>
        <button class="btn on" style="padding:10px 20px;font-size:13.5px;font-weight:700" onclick="onStateFilterChange('Maharashtra')">
          📍 Switch to Maharashtra Active Data (29 Corps, 224 Councils) →
        </button>
      </div>
    `;
  }

  // State Filter Change Handler (Updates Hero Header, Badges, Dropdowns, and Results)
  window.onStateFilterChange = function(val) {
    ACTIVE_STATE = val || 'Maharashtra';
    const sel = document.getElementById('munc-state-filter');
    if (sel) sel.value = ACTIVE_STATE;

    // 1. Dynamic Hero Header Update (changes attached image / hero banner)
    const heroWrap = document.getElementById('munc-hero-wrap');
    if (heroWrap) {
      heroWrap.innerHTML = renderHeroHeader(ACTIVE_SECTION, ACTIVE_STATE);
    }

    // Update Breadcrumb State
    const bcState = document.getElementById('munc-bc-state');
    if (bcState) bcState.textContent = ACTIVE_STATE;

    // Update Top State Pills Active State
    document.querySelectorAll('.munc-top-pills-bar .tab-pill').forEach(btn => {
      const txt = (btn.textContent || '').trim().replace(/^📍\s*/, '');
      btn.classList.toggle('on', txt.toLowerCase() === ACTIVE_STATE.toLowerCase());
    });

    // 2. Step Badge Update
    const stateBadge = document.getElementById('munc-step-state-badge');
    if (stateBadge) stateBadge.textContent = '2. State: ' + ACTIVE_STATE;
    const corpBadge = document.getElementById('munc-step-corp-badge');
    if (corpBadge) {
      corpBadge.textContent = (ACTIVE_SECTION === 'corps' ? '3. Corporation: All' : '3. Council: All');
    }

    // 3. Update Dropdown Options for Corporation / Council
    updateEntitySelectOptions(ACTIVE_SECTION, ACTIVE_STATE);

    // 4. Update Featured BMC Banner (Maharashtra Corporations only)
    const bmcBanner = document.getElementById('munc-featured-bmc-banner');
    if (bmcBanner) {
      bmcBanner.style.display = (ACTIVE_STATE.toLowerCase() === 'maharashtra' && ACTIVE_SECTION === 'corps') ? 'flex' : 'none';
    }

    // 5. Update Toolbar Visibility
    const tb = document.getElementById('munc-toolbar');
    if (tb) {
      tb.style.display = (ACTIVE_STATE.toLowerCase() === 'maharashtra') ? 'flex' : 'none';
    }

    // 6. Reset search input
    const s = document.getElementById('munc-search');
    if (s) s.value = '';

    // 7. Dispatch View Renderer
    renderActiveView();
  };

  // Corporation Select Dropdown Handler
  window.onCorpSelectChange = function(val) {
    const badge = document.getElementById('munc-step-corp-badge');
    if (badge) badge.textContent = '3. Corporation: ' + (val || 'All');

    const s = document.getElementById('munc-search');
    if (s) s.value = val || '';

    if (ACTIVE_STATE.toLowerCase() === 'maharashtra') {
      renderActiveView();
    } else {
      renderNonActiveEntityView(val, 'Municipal Corporation');
    }
  };

  // Council Select Dropdown Handler
  window.onCouncilSelectChange = function(val) {
    const badge = document.getElementById('munc-step-corp-badge');
    if (badge) badge.textContent = '3. Council: ' + (val || 'All');

    const s = document.getElementById('munc-search');
    if (s) s.value = val || '';

    if (ACTIVE_STATE.toLowerCase() === 'maharashtra') {
      renderActiveView();
    } else {
      renderNonActiveEntityView(val, 'Municipal Council');
    }
  };

  // Toolbar Search Input Handler (syncs with step flow badge)
  window.onMuncSearchInput = function(val) {
    const badge = document.getElementById('munc-step-corp-badge');
    if (badge) {
      badge.textContent = (ACTIVE_SECTION === 'corps' ? '3. Corporation: ' : '3. Council: ') + (val ? val : 'All');
    }
    renderActiveView();
  };

  // Dispatch renderer
  window.renderActiveView = function() {
    const area = document.getElementById('munc-content-area');
    if (!area) return;

    const q = (document.getElementById('munc-search') ? document.getElementById('munc-search').value : '').toLowerCase().trim();
    const dist = document.getElementById('munc-dist-filter') ? document.getElementById('munc-dist-filter').value : '';
    const sort = document.getElementById('munc-sort') ? document.getElementById('munc-sort').value : 'seats-desc';

    if (ACTIVE_SECTION === 'corps') {
      renderCorpsView(area, q, dist, sort, ACTIVE_YEAR);
    } else if (ACTIVE_SECTION === 'councils') {
      renderCouncilsView(area, q, dist, sort);
    } else if (ACTIVE_SECTION === 'compare') {
      renderComparisonView(area);
    } else if (ACTIVE_SECTION === 'presidents') {
      renderPresidentsView(area, q, dist);
    }
  };

  // 1. Municipal Corporations View
  function renderCorpsView(container, q, dist, sort, year) {
    if (ACTIVE_STATE && ACTIVE_STATE.toLowerCase() !== 'maharashtra') {
      renderNonActiveStateCivicView(container, ACTIVE_STATE, 'Municipal Corporations');
      return;
    }

    let items = (window.MH_CORPS || []).slice();

    // Year handling: if '2017', use 2017 tally/winners; if 'all' or '2026', use 2026
    const effYear = (year === '2017') ? '2017' : '2026';

    // Filter
    items = items.filter(c => {
      if (q) {
        const matchName = c.name.toLowerCase().includes(q) || (c.raw_name && c.raw_name.toLowerCase().includes(q));
        const matchDist = (c.district || '').toLowerCase().includes(q);
        const winners = (effYear === '2017' ? c.winners_2017 : c.winners_2026) || [];
        const matchWinner = winners.some(w => (w.candidate || '').toLowerCase().includes(q) || String(w.ward) === q);
        if (!matchName && !matchDist && !matchWinner) return false;
      }
      if (dist && c.district !== dist) return false;
      return true;
    });

    // Sort
    const seatKey = (effYear === '2017') ? 'seat_count_2017' : 'seat_count_2026';
    if (sort === 'seats-desc') items.sort((a,b) => (b[seatKey] || 0) - (a[seatKey] || 0));
    else if (sort === 'seats-asc') items.sort((a,b) => (a[seatKey] || 0) - (b[seatKey] || 0));
    else if (sort === 'name-asc') items.sort((a,b) => a.name.localeCompare(b.name));
    else if (sort === 'pop-desc') items.sort((a,b) => (b.total_pop || 0) - (a.total_pop || 0));

    if (!items.length) {
      container.innerHTML = `<div class="card note" style="padding:30px;text-align:center">No Municipal Corporations found matching your filters.</div>`;
      return;
    }

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${items.length}</b> Municipal Corporations (<b>${year === 'all' ? 'All Years' : effYear}</b> Election Results)</span>
        <span class="note">👉 Click any corporation to view full <b>ward-by-ward</b> results</span>
      </div>

      <div class="g g3" style="gap:14px">
        ${items.map(c => {
          const tally = (effYear === '2017') ? c.party_tally_2017 : c.party_tally_2026;
          const winners = (effYear === '2017') ? c.winners_2017 : c.winners_2026;
          const seatCount = (effYear === '2017') ? c.seat_count_2017 : c.seat_count_2026;
          const topParties = Object.entries(tally || {}).sort((x,y) => y[1] - x[1]).slice(0, 4);
          const slugOrId = c.slug || c.id;

          return `
            <div class="card" style="margin:0;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--b);border-radius:10px;padding:16px;background:var(--s1);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s" onclick="go('corp/${slugOrId}')">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
                  <span class="badge" style="background:rgba(255,153,51,0.18);color:#ff9933;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${esc(c.district || 'Maharashtra')}
                  </span>
                  <span class="badge" style="background:var(--s2);color:var(--text);font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${fmt(seatCount)} Seats
                  </span>
                </div>

                <h3 style="margin:0 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
                  🏙️ ${esc(c.name)}
                </h3>

                <div style="font-size:12px;color:var(--text-2);margin-bottom:12px">
                  ${c.total_pop ? `Population: <b>${fmt(c.total_pop)}</b>` : 'Major Urban Corporation'}
                  ${c.sc_pop && c.total_pop ? ` · SC: ${((c.sc_pop/c.total_pop)*100).toFixed(1)}%` : ''}
                </div>

                <!-- Party Badges -->
                <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px">
                  ${topParties.map(([p, cnt]) => `
                    <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                      <b>${esc(p)}</b>: ${cnt}
                    </span>
                  `).join('')}
                </div>
              </div>

              <div style="border-top:1px solid var(--b);padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11.5px;color:var(--text-2)">${fmt((winners || []).length)} ward winners listed</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="event.stopPropagation();go('corp/${slugOrId}')">Ward Results →</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // 2. Municipal Councils View (Rich Cards matching BMC style)
  function renderCouncilsView(container, q, dist, sort) {
    if (ACTIVE_STATE && ACTIVE_STATE.toLowerCase() !== 'maharashtra') {
      renderNonActiveStateCivicView(container, ACTIVE_STATE, 'Municipal Councils');
      return;
    }

    let items = (window.MH_COUNCILS || []).slice();

    items = items.filter(c => {
      if (q) {
        const matchName = c.name.toLowerCase().includes(q) || (c.raw_name && c.raw_name.toLowerCase().includes(q));
        const matchPres = c.president && ((c.president.candidate || '').toLowerCase().includes(q) || (c.president.party || '').toLowerCase().includes(q));
        if (!matchName && !matchPres) return false;
      }
      return true;
    });

    if (sort === 'seats-desc') items.sort((a,b) => (b.seat_count || 0) - (a.seat_count || 0));
    else if (sort === 'seats-asc') items.sort((a,b) => (a.seat_count || 0) - (b.seat_count || 0));
    else if (sort === 'name-asc') items.sort((a,b) => a.name.localeCompare(b.name));

    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
        <span class="note">Showing <b>${items.length}</b> of 224 Municipal Councils (2025 Maharashtra SECM Elections)</span>
        <span class="note">👉 Click any council to view full <b>ward-by-ward</b> councillor results</span>
      </div>

      <div class="g g3" style="gap:14px">
        ${items.map(c => {
          const pres = c.president;
          const topParties = Object.entries(c.party_tally || {}).sort((x,y) => y[1] - x[1]).slice(0, 4);
          const winners = c.winners || [];

          return `
            <div class="card" style="margin:0;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--b);border-radius:10px;padding:16px;background:var(--s1);cursor:pointer;transition:transform 0.15s,box-shadow 0.15s" onclick="go('council/${c.id}')">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
                  <span class="badge" style="background:rgba(56,189,248,0.18);color:#38bdf8;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${esc(c.district || 'Maharashtra')}
                  </span>
                  <span class="badge" style="background:var(--s2);color:var(--text);font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                    ${fmt(c.seat_count)} Seats
                  </span>
                </div>

                <h3 style="margin:0 0 6px;font-size:17px;color:var(--text);display:flex;align-items:center;gap:6px">
                  🏢 ${esc(c.name)} Municipal Council
                </h3>

                <!-- President Block -->
                ${pres ? `
                  <div style="background:rgba(255,153,51,0.08);border:1px solid rgba(255,153,51,0.22);border-radius:6px;padding:7px 10px;margin-bottom:10px">
                    <div style="font-size:10px;font-weight:700;color:#ff9933;text-transform:uppercase">PRESIDENT (NAGARADHYAKSHA)</div>
                    <div style="font-size:13px;font-weight:700;color:var(--text);margin:2px 0">${esc(pres.candidate)}</div>
                    <div style="font-size:11px;color:var(--text-2);display:flex;justify-content:space-between">
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(pres.party)};font-size:10.5px">${esc(pres.party)}</span>
                      <span>${fmt(pres.votes)} votes (${pres.pct ? pres.pct.toFixed(1) + '%' : '–'})</span>
                    </div>
                  </div>
                ` : ''}

                <!-- Party Badges -->
                <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:12px">
                  ${topParties.map(([p, cnt]) => `
                    <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                      <b>${esc(p)}</b>: ${cnt}
                    </span>
                  `).join('')}
                </div>
              </div>

              <div style="border-top:1px solid var(--b);padding-top:10px;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:11.5px;color:var(--text-2)">${fmt(winners.length)} councillors listed</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="event.stopPropagation();go('council/${c.id}')">Ward Results →</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  // Non-Active State Civic View Renderer
  function renderNonActiveStateCivicView(container, stateName, civicType) {
    const stObj = ALL_INDIA_STATES.find(s => s.name.toLowerCase() === stateName.toLowerCase()) || { name: stateName, corps: 5, councils: 25 };

    container.innerHTML = `
      <div class="card" style="border:1px solid rgba(56,189,248,0.4);background:linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(15,23,42,0.92) 100%);border-radius:14px;padding:28px;text-align:center;margin:10px 0">
        <div style="font-size:38px;margin-bottom:8px">🏛️</div>
        <h2 style="margin:0 0 8px;font-size:22px;color:var(--text)">
          ${esc(stObj.name)} — ${esc(civicType)}
        </h2>
        <p style="margin:0 auto 18px;max-width:700px;font-size:13.5px;color:var(--text-2);line-height:1.55">
          Official State Election Commission (SEC) ward-level data for <b>${esc(stObj.name)}</b> is currently in the active synchronization queue of our central ECI urban governance data pipeline.
        </p>

        <div class="g g3" style="max-width:640px;margin:0 auto 20px;gap:10px;text-align:left">
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">STATE / UT</div>
            <b style="font-size:15px;color:var(--text)">${esc(stObj.name)}</b>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">URBAN LOCAL BODIES</div>
            <b style="font-size:15px;color:#ff9933">${stObj.corps || '–'} Corps · ${stObj.councils || '–'} Councils</b>
          </div>
          <div class="stat-card" style="background:var(--s1);border:1px solid var(--b);padding:12px 14px;border-radius:8px">
            <div style="font-size:11px;color:var(--text-2);font-weight:600">SYNC STATUS</div>
            <b style="font-size:15px;color:#38bdf8">Syncing SEC Pipeline</b>
          </div>
        </div>

        <button class="btn on" style="padding:10px 20px;font-size:13.5px;font-weight:700" onclick="onStateFilterChange('Maharashtra')">
          📍 Switch to Maharashtra Active Data (29 Corps, 224 Councils) →
        </button>
      </div>
    `;
  }

  // 3. 2017 vs 2026 Historical Comparison View
  function renderComparisonView(container) {
    const summary = window.MH_MUNC_SUMMARY || {};
    const comparison = summary.comparison_parties || [];
    const corps = window.MH_CORPS || [];

    container.innerHTML = `
      <!-- Overall Party Swing Analysis Table -->
      <div class="card" style="margin-bottom:18px;background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:16px">
        <h3 style="margin:0 0 4px;font-size:16px">📊 Maharashtra Municipal Corporations: 2017 vs 2026 Seat Swing</h3>
        <p class="note" style="margin:0 0 14px">Compare previous 2017 election wins vs current 2026 election wins across all political parties.</p>

        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:40px">#</th>
                <th>Political Party</th>
                <th style="text-align:right">2017 Won (Previous)</th>
                <th style="text-align:right">2026 Won (Current)</th>
                <th style="text-align:right">Net Seat Change</th>
                <th>Trend / Shift</th>
              </tr>
            </thead>
            <tbody>
              ${comparison.slice(0, 16).map((item, i) => {
                const diff = item.diff;
                const isGain = diff > 0;
                const isLoss = diff < 0;
                const diffBadge = isGain ? `+${diff}` : `${diff}`;
                const diffColor = isGain ? '#4ade80' : (isLoss ? '#ef4444' : '#94a3b8');

                return `
                  <tr class="r">
                    <td>${i + 1}</td>
                    <td>
                      <div style="display:flex;align-items:center;gap:8px">
                        <span class="dot" style="background:${getPartyColor(item.party)};width:10px;height:10px;border-radius:50%"></span>
                        <b>${esc(item.party)}</b>
                      </div>
                    </td>
                    <td style="text-align:right"><b style="font-size:13.5px">${fmt(item.seats_2017)}</b></td>
                    <td style="text-align:right"><b style="font-size:14px;color:#ff9933">${fmt(item.seats_2026)}</b></td>
                    <td style="text-align:right">
                      <span class="badge" style="background:rgba(255,255,255,0.06);color:${diffColor};font-weight:800;font-size:12px;padding:2px 8px;border-radius:4px">
                        ${diffBadge}
                      </span>
                    </td>
                    <td>
                      <small style="color:${diffColor};font-weight:600">
                        ${isGain ? `▲ Gained ${diff} seats` : (isLoss ? `▼ Dropped ${Math.abs(diff)} seats` : `Equal`)}
                      </small>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Corporation by Corporation Comparative Table -->
      <div class="card" style="padding:0;overflow:hidden;border:1px solid var(--b);border-radius:10px">
        <div style="padding:14px 18px;border-bottom:1px solid var(--b);background:rgba(255,255,255,0.02)">
          <h3 style="margin:0 0 2px;font-size:15px">🏙️ Corporation-by-Corporation Shift (2017 vs 2026)</h3>
          <span class="note">Leading party and seats won comparison</span>
        </div>
        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:40px">#</th>
                <th>Municipal Corporation</th>
                <th>District</th>
                <th>2017 Top Party</th>
                <th>2026 Top Party</th>
                <th style="text-align:right">Action</th>
              </tr>
            </thead>
            <tbody>
              ${corps.map((c, i) => {
                const top17 = Object.entries(c.party_tally_2017 || {}).sort((x,y) => y[1]-x[1])[0] || ['–', 0];
                const top26 = Object.entries(c.party_tally_2026 || {}).sort((x,y) => y[1]-x[1])[0] || ['–', 0];

                return `
                  <tr class="r">
                    <td>${i + 1}</td>
                    <td><b>${esc(c.name)}</b></td>
                    <td><small style="color:var(--text-2)">${esc(c.district)}</small></td>
                    <td>
                      ${top17[0] !== '–' ? `
                        <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(top17[0])}">
                          ${esc(top17[0])} (${top17[1]})
                        </span>
                      ` : '<span class="note">–</span>'}
                    </td>
                    <td>
                      ${top26[0] !== '–' ? `
                        <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(top26[0])}">
                          ${esc(top26[0])} (${top26[1]})
                        </span>
                      ` : '<span class="note">–</span>'}
                    </td>
                    <td style="text-align:right">
                      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="openCorpModal(${c.id}, '2026')">Explore →</button>
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

  // 4. Council Presidents View
  function renderPresidentsView(container, q, dist) {
    let councils = (window.MH_COUNCILS || []).filter(c => c.president);

    councils = councils.filter(c => {
      const pres = c.president;
      if (q) {
        const matchName = c.name.toLowerCase().includes(q) || pres.candidate.toLowerCase().includes(q) || pres.party.toLowerCase().includes(q);
        if (!matchName) return false;
      }
      return true;
    });

    const summary = window.MH_MUNC_SUMMARY || {};
    const presTally = summary.council_pres_tally || [];

    container.innerHTML = `
      <div class="card" style="margin-bottom:16px;background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px">
        <h3 style="margin:0 0 10px;font-size:15px">👑 Directly-Elected Nagaradhyaksha (Council Presidents) Party Tally</h3>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          ${presTally.map(item => `
            <div style="display:flex;align-items:center;gap:6px;background:var(--s2);border:1px solid var(--b);padding:5px 10px;border-radius:16px">
              <span class="dot" style="background:${getPartyColor(item.party)};width:9px;height:9px;border-radius:50%"></span>
              <span style="font-size:12.5px;font-weight:600">${esc(item.party)}</span>
              <span style="background:rgba(255,255,255,0.15);padding:1px 6px;border-radius:8px;font-size:11px;font-weight:700">${item.seats}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="card" style="padding:0;overflow:hidden;border:1px solid var(--b);border-radius:10px">
        <div style="overflow-x:auto">
          <table class="tbl" style="margin:0">
            <thead>
              <tr>
                <th style="width:40px">#</th>
                <th>Municipal Council</th>
                <th>Nagaradhyaksha Winner</th>
                <th>Political Party</th>
                <th>Votes Polled</th>
                <th>Vote Share</th>
                <th style="text-align:right">Action</th>
              </tr>
            </thead>
            <tbody>
              ${councils.map((c, i) => {
                const pres = c.president;
                return `
                  <tr class="r">
                    <td>${i + 1}</td>
                    <td><b>${esc(c.name)}</b></td>
                    <td><b style="color:#4ade80">${esc(pres.candidate)}</b></td>
                    <td>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(pres.party)};font-weight:600">
                        ${esc(pres.party)}
                      </span>
                    </td>
                    <td>${fmt(pres.votes)}</td>
                    <td>${pres.pct ? pres.pct.toFixed(1) + '%' : '–'}</td>
                    <td style="text-align:right">
                      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="openCouncilModal(${c.id})">Council Details →</button>
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

  // Open Corporation Modal with Complete Ward-Wise View
  window.openCorpModal = function(id, year) {
    year = year || ACTIVE_YEAR || '2026';
    const corp = (window.MH_CORPS || []).find(c => c.id === id);
    if (!corp) return;

    ACTIVE_MODAL_CORP = { corp, year };
    const modalWrap = document.getElementById('munc-modal-wrap');
    if (!modalWrap) return;

    const tally = year === '2017' ? corp.party_tally_2017 : corp.party_tally_2026;
    const winners = year === '2017' ? corp.winners_2017 : corp.winners_2026;
    const topParties = Object.entries(tally || {}).sort((x,y) => y[1] - x[1]);

    modalWrap.innerHTML = `
      <div class="modal-backdrop" onclick="closeMuncModal()" style="position:fixed;inset:0;background:rgba(0,0,0,0.78);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#0b1428;border:1px solid var(--b);border-radius:14px;width:min(960px, 96vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 60px rgba(0,0,0,0.85);overflow:hidden">
          
          <!-- Header -->
          <div style="padding:18px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:flex-start;gap:12px;background:rgba(255,255,255,0.02)">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="badge" style="background:#ff9933;color:#000;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">${esc(corp.district || 'Maharashtra')}</span>
                <span class="badge" style="background:var(--s2);color:var(--text);font-size:11px;padding:2px 8px;border-radius:4px">${year} ELECTION RESULTS</span>
                <span class="badge" style="background:var(--s2);color:var(--text-2);font-size:11px;padding:2px 8px;border-radius:4px">${fmt(winners.length)} Wards/Seats</span>
              </div>
              <h2 style="margin:2px 0 4px;font-size:22px;color:var(--text)">🏙️ ${esc(corp.name)} Municipal Corporation</h2>
              <p style="margin:0;font-size:12px;color:var(--text-2)">
                ${corp.total_pop ? `Total Population: <b>${fmt(corp.total_pop)}</b> · SC: <b>${fmt(corp.sc_pop)}</b> · ST: <b>${fmt(corp.st_pop)}</b>` : 'Official Maharashtra Urban Governance'}
              </p>
            </div>
            <button class="btn" onclick="closeMuncModal()" style="padding:6px 10px;font-size:16px;line-height:1" title="Close">✕</button>
          </div>

          <!-- Party Breakdown Chips (Standardized) -->
          <div style="padding:12px 22px;background:var(--s1);border-bottom:1px solid var(--b);display:flex;flex-wrap:wrap;gap:6px">
            <span style="font-size:12px;font-weight:600;margin-right:6px;align-self:center">Party Tally:</span>
            ${topParties.map(([p, cnt]) => `
              <span style="font-size:11.5px;padding:3px 9px;border-radius:12px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                <b>${esc(p)}</b>: ${cnt}
              </span>
            `).join('')}
          </div>

          <!-- Ward Search Input inside Modal -->
          <div style="padding:10px 22px;border-bottom:1px solid var(--b);display:flex;gap:10px;align-items:center">
            <input id="modal-ward-input" placeholder="Filter ward number (e.g. 1, 2), candidate name, or party…" style="width:100%;padding:8px 12px;border-radius:6px;border:1px solid var(--b);background:var(--s2);color:var(--text)" oninput="filterWardList()">
            <span style="font-size:11px;color:var(--text-2);white-space:nowrap">${winners.length} Wards Listed</span>
          </div>

          <!-- Scrollable Ward Table -->
          <div id="modal-ward-list-wrap" style="padding:0;overflow-y:auto;flex:1">
            ${renderWardTableHtml(winners)}
          </div>

          <!-- Modal Footer -->
          <div style="padding:12px 22px;border-top:1px solid var(--b);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02)">
            <span class="note">Source: State Election Commission of Maharashtra (SECM)</span>
            <div style="display:flex;gap:8px">
              <button class="btn ${year==='2026'?'on':''}" onclick="openCorpModal(${corp.id}, '2026')">2026 View</button>
              <button class="btn ${year==='2017'?'on':''}" onclick="openCorpModal(${corp.id}, '2017')">2017 View</button>
              <button class="btn" onclick="closeMuncModal()">Close</button>
            </div>
          </div>

        </div>
      </div>
    `;
    modalWrap.style.display = 'block';
  };

  function renderWardTableHtml(winners) {
    if (!winners || !winners.length) {
      return `<div class="note" style="padding:30px;text-align:center">No ward winner records available for this corporation.</div>`;
    }

    return `
      <table class="tbl" style="margin:0">
        <thead>
          <tr>
            <th style="width:70px">Ward</th>
            <th style="width:55px">Seat</th>
            <th>Reservation Category</th>
            <th>Winner Candidate</th>
            <th>Political Party</th>
            <th style="text-align:right">Votes Polled</th>
            <th style="text-align:right">Vote Share</th>
          </tr>
        </thead>
        <tbody>
          ${winners.map(w => `
            <tr class="r">
              <td><b>Ward ${esc(w.ward)}</b></td>
              <td><span class="badge" style="background:var(--s2);font-size:11px">${esc(w.seat)}</span></td>
              <td><small style="color:var(--text-2)">${esc(w.res || 'General')}</small></td>
              <td><b style="color:#4ade80">${esc(w.candidate)}</b></td>
              <td>
                <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w.party)};font-weight:600">
                  ${esc(w.party)}
                </span>
              </td>
              <td style="text-align:right"><b>${fmt(w.votes)}</b></td>
              <td style="text-align:right">${w.pct ? w.pct.toFixed(1) + '%' : '–'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }

  window.filterWardList = function() {
    if (!ACTIVE_MODAL_CORP) return;
    const q = (document.getElementById('modal-ward-input') ? document.getElementById('modal-ward-input').value : '').toLowerCase().trim();
    const wrap = document.getElementById('modal-ward-list-wrap');
    if (!wrap) return;

    const { corp, year } = ACTIVE_MODAL_CORP;
    const winners = year === '2017' ? corp.winners_2017 : corp.winners_2026;

    let filtered = winners;
    if (q) {
      filtered = filtered.filter(w => {
        return String(w.ward).toLowerCase().includes(q) ||
               String(w.seat).toLowerCase().includes(q) ||
               w.candidate.toLowerCase().includes(q) ||
               w.party.toLowerCase().includes(q) ||
               (w.res && w.res.toLowerCase().includes(q));
      });
    }
    wrap.innerHTML = renderWardTableHtml(filtered);
  };

  // Open Council Modal
  window.openCouncilModal = function(id) {
    const council = (window.MH_COUNCILS || []).find(c => c.id === id);
    if (!council) return;

    ACTIVE_MODAL_COUNCIL = council;
    const modalWrap = document.getElementById('munc-modal-wrap');
    if (!modalWrap) return;

    const pres = council.president;
    const topParties = Object.entries(council.party_tally || {}).sort((x,y) => y[1] - x[1]);

    modalWrap.innerHTML = `
      <div class="modal-backdrop" onclick="closeMuncModal()" style="position:fixed;inset:0;background:rgba(0,0,0,0.78);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#0b1428;border:1px solid var(--b);border-radius:14px;width:min(880px, 96vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 60px rgba(0,0,0,0.85);overflow:hidden">
          
          <!-- Header -->
          <div style="padding:18px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:flex-start;gap:12px;background:rgba(255,255,255,0.02)">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="badge" style="background:#38bdf8;color:#000;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">MUNICIPAL COUNCIL</span>
                <span class="badge" style="background:var(--s2);color:var(--text-2);font-size:11px;padding:2px 8px;border-radius:4px">${fmt(council.seat_count)} Seats</span>
              </div>
              <h2 style="margin:2px 0 4px;font-size:22px;color:var(--text)">🏛️ ${esc(council.name)} Municipal Council</h2>
              <p style="margin:0;font-size:12px;color:var(--text-2)">Maharashtra Urban Governance (${esc(council.raw_name)})</p>
            </div>
            <button class="btn" onclick="closeMuncModal()" style="padding:6px 10px;font-size:16px;line-height:1" title="Close">✕</button>
          </div>

          <!-- President Spotlight Card if present -->
          ${pres ? `
            <div style="margin:14px 22px 0;padding:14px 18px;background:rgba(56, 189, 248, 0.08);border:1px solid rgba(56, 189, 248, 0.25);border-radius:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
              <div>
                <small style="font-size:11px;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.5px">👑 DIRECTLY-ELECTED COUNCIL PRESIDENT (NAGARADHYAKSHA)</small>
                <div style="font-size:18px;font-weight:800;color:#fff;margin:2px 0">${esc(pres.candidate)}</div>
                <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text-2)">
                  <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(pres.party)};font-weight:600">${esc(pres.party)}</span>
                  <span>Votes: <b>${fmt(pres.votes)}</b></span>
                  ${pres.pct ? `<span>Share: <b>${pres.pct.toFixed(1)}%</b></span>` : ''}
                </div>
              </div>
              <span class="badge" style="background:#38bdf8;color:#000;font-weight:800;padding:4px 10px;border-radius:6px">WINNER</span>
            </div>
          ` : ''}

          <!-- Party Tally -->
          <div style="padding:12px 22px;background:var(--s1);border-bottom:1px solid var(--b);margin-top:14px;display:flex;flex-wrap:wrap;gap:6px">
            <span style="font-size:12px;font-weight:600;margin-right:6px;align-self:center">Councillor Tally:</span>
            ${topParties.map(([p, cnt]) => `
              <span style="font-size:11.5px;padding:3px 9px;border-radius:12px;background:var(--s2);border-left:3px solid ${getPartyColor(p)};color:var(--text)">
                <b>${esc(p)}</b>: ${cnt}
              </span>
            `).join('')}
          </div>

          <!-- Councillor Winners Table -->
          <div style="padding:0;overflow-y:auto;flex:1">
            <table class="tbl" style="margin:0">
              <thead>
                <tr>
                  <th style="width:65px">Ward</th>
                  <th style="width:50px">Seat</th>
                  <th>Councillor Winner</th>
                  <th>Political Party</th>
                  <th style="text-align:right">Votes</th>
                  <th style="text-align:right">Vote Share</th>
                </tr>
              </thead>
              <tbody>
                ${(council.winners || []).map(w => `
                  <tr class="r">
                    <td><b>Ward ${esc(w.ward)}</b></td>
                    <td><span class="badge" style="background:var(--s2);font-size:11px">${esc(w.seat)}</span></td>
                    <td><b style="color:#4ade80">${esc(w.candidate)}</b></td>
                    <td>
                      <span class="tag" style="background:var(--s2);border-left:3px solid ${getPartyColor(w.party)};font-weight:600">
                        ${esc(w.party)}
                      </span>
                    </td>
                    <td style="text-align:right"><b>${fmt(w.votes)}</b></td>
                    <td style="text-align:right">${w.pct ? w.pct.toFixed(1) + '%' : '–'}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>

          <!-- Footer -->
          <div style="padding:12px 22px;border-top:1px solid var(--b);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02)">
            <span class="note">Source: Maharashtra Municipal Councils (SECM)</span>
            <button class="btn on" onclick="closeMuncModal()">Close</button>
          </div>

        </div>
      </div>
    `;
    modalWrap.style.display = 'block';
  };

  window.closeMuncModal = function() {
    const modalWrap = document.getElementById('munc-modal-wrap');
    if (modalWrap) modalWrap.style.display = 'none';
    ACTIVE_MODAL_CORP = null;
    ACTIVE_MODAL_COUNCIL = null;
  };


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
        <div class="mycorp-majority-bar-box" style="margin-top:16px;border:1px solid var(--b);border-radius:8px;padding:12px 14px">
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

      <!-- Office of the Mayor & Executive Governance Insight -->
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
            <input id="mycorp-jump-input" placeholder="Ward # e.g. 1, 1A" style="width:110px;padding:4px 8px;border-radius:6px;border:1px solid var(--b);background:var(--s2);color:var(--text);font-size:12px" onkeydown="if(event.key==='Enter')jumpToMyCorpWard(this.value)">
            <button class="btn on" style="padding:4px 10px;font-size:12px" onclick="jumpToMyCorpWard(document.getElementById('mycorp-jump-input').value)">Jump →</button>
          </div>
        </div>

        <!-- Matrix Pills Grid with 1A, 1B, 1C like ward -->
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
        </div>
      </div>

      <!-- Compact Find Your Ward Result Toolbar -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="mycorp-search-input"
                 placeholder="Search ward # (e.g. 1, 1A), candidate name, runner-up…"
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

  window.jumpToMyCorpWard = function(wardVal) {
    if (!wardVal) return;
    const wStr = String(wardVal).trim().toLowerCase();

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
      const el = document.getElementById('mycorp-ward-card-' + wStr) ||
                 document.getElementById('mycorp-ward-card-' + parseInt(wStr, 10));
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.outline = '3px solid #ff9933';
        el.style.boxShadow = '0 0 20px rgba(255,153,51,0.6)';
        setTimeout(() => {
          el.style.outline = '';
          el.style.boxShadow = '';
        }, 2200);
      } else {
        openMyCorpWardModal(wStr);
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
        const wLbl = (w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`)).toLowerCase();
        const matchWard = String(w.ward) === q || ('ward ' + w.ward).includes(q) || wLbl === q || ('ward ' + wLbl).includes(q);
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

          const wLabel = w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`);
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
                <span style="font-size:11px;color:var(--text-3)">Ward ${wLabel} · ${esc(corp.name)}</span>
                <button class="btn on" style="padding:4px 10px;font-size:11.5px" onclick="openMyCorpWardModal('${wLabel}')">
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
            <div class="mycorp-corporator-card" onclick="openMyCorpWardModal('${c.ward_label || (c.seat ? c.ward + c.seat : c.ward)}')">
              <div class="mycorp-avatar" style="background:${pColor}">
                ${initial}
              </div>
              <div style="flex:1;min-width:0">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:4px">
                  <span class="badge" style="background:var(--s2);color:#ffd07a;font-weight:700;font-size:10.5px;padding:1px 5px;border-radius:4px">
                    Ward ${c.ward_label || (c.seat ? c.ward + c.seat : c.ward)}
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

                const wLabel = w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`);
                return `
                  <tr class="r" onclick="openMyCorpWardModal('${wLabel}')" style="cursor:pointer">
                    <td><b>Ward ${wLabel}</b></td>
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
                      <button class="btn" style="padding:2px 8px;font-size:11px" onclick="event.stopPropagation();openMyCorpWardModal('${wLabel}')">Details →</button>
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
  window.openMyCorpWardModal = function(wardIdentifier) {
    const corp = MYCORP_STATE.corp;
    if (!corp) return;

    const winners2026 = corp.winners_2026 || [];
    const winners2017 = corp.winners_2017 || [];
    const wStr = String(wardIdentifier || '').trim().toLowerCase();
    const wNum = parseInt(wStr, 10);

    const currIdx = winners2026.findIndex(w => {
      const lbl = (w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`)).toLowerCase();
      return lbl === wStr || (wNum && w.ward === wNum);
    });

    const w2026 = currIdx !== -1 ? winners2026[currIdx] : (winners2026[0] || { ward: 1, candidate: 'Candidate', party: 'Independent', votes: 0 });
    const wLabel = w2026.ward_label || (w2026.seat ? `${w2026.ward}${w2026.seat}` : `${w2026.ward}`);
    const w2017 = winners2017.find(w => w.ward === w2026.ward);

    const prevIdx = currIdx > 0 ? currIdx - 1 : winners2026.length - 1;
    const nextIdx = currIdx < winners2026.length - 1 ? currIdx + 1 : 0;
    const prevLabel = winners2026[prevIdx] ? (winners2026[prevIdx].ward_label || `${winners2026[prevIdx].ward}${winners2026[prevIdx].seat||''}`) : '1';
    const nextLabel = winners2026[nextIdx] ? (winners2026[nextIdx].ward_label || `${winners2026[nextIdx].ward}${winners2026[nextIdx].seat||''}`) : '1';

    const modalWrap = document.getElementById('mycorp-modal-wrap');
    if (!modalWrap) return;

    const pColor = getPartyColor(w2026.party);

    modalWrap.innerHTML = `
      <div class="modal-backdrop" onclick="closeMyCorpWardModal()" style="position:fixed;inset:0;background:rgba(0,0,0,0.82);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="modal-dialog" onclick="event.stopPropagation()" style="background:#0b1428;border:1px solid var(--b);border-radius:14px;width:min(760px, 95vw);max-height:92vh;display:flex;flex-direction:column;box-shadow:0 24px 60px rgba(0,0,0,0.85);overflow:hidden">
          
          <!-- Header -->
          <div style="padding:18px 22px;border-bottom:1px solid var(--b);display:flex;justify-content:space-between;align-items:flex-start;background:rgba(255,255,255,0.02)">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap">
                <span class="badge" style="background:#ff9933;color:#000;font-weight:700;font-size:11px;padding:2px 8px;border-radius:4px">
                  WARD ${wLabel} ${w2026.seat ? `· SEAT ${w2026.seat}` : ''}
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
                🗳️ Ward ${wLabel} Election Result Breakdown
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

            <!-- Complete Candidate Vote Leaderboard (All Candidates Polled) -->
            <div class="card" style="background:var(--s1);border:1px solid var(--b);border-radius:10px;padding:14px;margin-bottom:18px">
              <div style="font-size:12px;color:#38bdf8;font-weight:800;letter-spacing:0.5px">
                📊 ALL CANDIDATES &amp; COMPLETE VOTE TALLY
              </div>
              ${renderCandidateLeaderboardHtml(w2026.cands)}
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
            <button class="btn" onclick="openMyCorpWardModal('${prevLabel}')">← Ward ${prevLabel}</button>
            <span style="font-size:12px;color:var(--text-2)">Ward ${wLabel} of ${winners2026.length}</span>
            <button class="btn" onclick="openMyCorpWardModal('${nextLabel}')">Ward ${nextLabel} →</button>
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


  // ═══════════════════════════════════════════════════════════════
  // DEDICATED SECTIONS: Municipal Corporations & Municipal Councils
  // ═══════════════════════════════════════════════════════════════

  // ═══════════════════════════════════════════════════════════════
  // SEPARATED DEDICATED SECTIONS: Municipal Corporations vs Councils
  // ═══════════════════════════════════════════════════════════════

  // 1. DEDICATED MUNICIPAL CORPORATIONS SECTION (Step 1: Section -> Step 2: State -> Step 3: Corporation -> Step 4: Results)
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
      updateEntitySelectOptions('corps', ACTIVE_STATE);
      renderActiveView();
    }, 15);

    return `
      <!-- Top Bar: Breadcrumb + State Filter -->
      <div class="munc-top-nav-bar">
        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('corporations')">Municipal Corporations</a> <span>›</span>
          <span id="munc-bc-state">${esc(ACTIVE_STATE)}</span>
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
            ${st}
          </button>
        `).join('')}
      </div>

      <!-- Dedicated Corporations Hero Header (Dynamic - Updates with State Selection) -->
      <div id="munc-hero-wrap">
        ${renderHeroHeader('corps', ACTIVE_STATE)}
      </div>

      <!-- Featured BMC myCorporator Banner (For Maharashtra) -->
      <div id="munc-featured-bmc-banner" style="display:${(ACTIVE_STATE.toLowerCase() === 'maharashtra') ? 'flex' : 'none'};margin:0 0 16px;background:linear-gradient(135deg, rgba(255,107,0,0.14) 0%, rgba(15,23,42,0.92) 100%);border:1px solid rgba(255,153,51,0.45);border-radius:14px;padding:16px 20px;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 10px 30px rgba(0,0,0,0.45)">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span class="mycorp-brand-pill">FEATURED CIVIC HUB</span>
            <span class="mycorp-stat-pill">227 WARDS · 114 MAJORITY MARK</span>
            <span class="mycorp-stat-pill">₹65,000+ CR BUDGET</span>
          </div>
          <h2 style="margin:2px 0 4px;font-size:19px;color:var(--text);display:flex;align-items:center;gap:8px">
            🏛️ Brihanmumbai Municipal Corporation (BMC) — myCorporator Portal
          </h2>
          <p style="margin:0;font-size:13px;color:var(--text-2);max-width:760px;line-height:1.45">
            Explore complete ward-wise election results (Ward 1 to 227), corporator directory, vote shares, and victory margins.
          </p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn on" style="padding:9px 18px;font-size:13px;font-weight:700;background:linear-gradient(90deg, #ff9933, #ff6b00);color:#000;border:none;box-shadow:0 4px 16px rgba(255,107,0,0.45);cursor:pointer" onclick="go('corp/bmc')">
            Open BMC Portal (227 Wards) →
          </button>
        </div>
      </div>

      <!-- Compact Sleek Filter Toolbar -->
      <div class="munc-compact-toolbar" id="munc-toolbar" style="display:${(ACTIVE_STATE.toLowerCase() === 'maharashtra') ? 'flex' : 'none'}">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Type to search or enter corporation..." aria-label="Search Corporations" oninput="onMuncSearchInput(this.value)">
        </div>

        <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
          <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
          ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
        </select>

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
          <option value="pop-desc">Population: Largest first</option>
        </select>
      </div>

      <!-- Main Dynamic Corporations Content -->
      <div id="munc-content-area">
        <p class="note">Loading municipal corporations…</p>
      </div>

      <div id="munc-modal-wrap" style="display:none"></div>
    `;
  };

  // 2. DEDICATED MUNICIPAL COUNCILS SECTION (Step 1: Section -> Step 2: State -> Step 3: Council -> Step 4: Results)
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
      updateEntitySelectOptions('councils', ACTIVE_STATE);
      renderActiveView();
    }, 15);

    return `
      <!-- Top Bar: Breadcrumb + State Filter -->
      <div class="munc-top-nav-bar">
        <div class="bc" style="margin-bottom:0">
          <a onclick="go('')">Home</a> <span>›</span>
          <a onclick="go('councils')">Municipal Councils</a> <span>›</span>
          <span id="munc-bc-state">${esc(ACTIVE_STATE)}</span>
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
            ${st}
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

      <!-- Compact Sleek Filter Toolbar -->
      <div class="munc-compact-toolbar" id="munc-toolbar" style="display:${(ACTIVE_STATE.toLowerCase() === 'maharashtra') ? 'flex' : 'none'}">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="munc-search" placeholder="Type to search or enter council..." aria-label="Search Councils" oninput="onMuncSearchInput(this.value)">
        </div>

        ${sortedDistricts.length > 1 ? `
          <select id="munc-dist-filter" aria-label="Filter District" onchange="renderActiveView()">
            <option value="">All Maharashtra Districts (${sortedDistricts.length})</option>
            ${sortedDistricts.map(d => `<option value="${esc(d)}">${esc(d)}</option>`).join('')}
          </select>
        ` : ''}

        <select id="munc-sort" aria-label="Sort Order" onchange="renderActiveView()">
          <option value="seats-desc">Seats: Highest first</option>
          <option value="seats-asc">Seats: Lowest first</option>
          <option value="name-asc">Name: A to Z</option>
        </select>
      </div>

      <!-- Main Dynamic Councils Content -->
      <div id="munc-content-area">
        <p class="note">Loading municipal councils…</p>
      </div>

      <div id="munc-modal-wrap" style="display:none"></div>
    `;
  };

  // Helper to render state filter dropdown options
  function renderStateFilterOptions(selectedState) {
    selectedState = selectedState || ACTIVE_STATE || 'Maharashtra';
    return ALL_INDIA_STATES.map(st => {
      const isSel = st.name.toLowerCase() === selectedState.toLowerCase();
      return `<option value="${esc(st.name)}" ${isSel ? 'selected' : ''}>${esc(st.name)}</option>`;
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
      <div class="mycorp-hero council-detail-hero">
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
        <div class="mycorp-majority-bar-box" style="margin-top:16px;border:1px solid var(--b);border-radius:8px;padding:12px 14px">
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
            <input id="mycouncil-jump-input" placeholder="Ward # e.g. 1, 1A" style="width:110px;padding:4px 8px;border-radius:6px;border:1px solid var(--b);background:var(--s2);color:var(--text);font-size:12px" onkeydown="if(event.key==='Enter')jumpToMyCouncilWard(this.value)">
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

      <!-- Compact Find Your Councillor Result Toolbar -->
      <div class="munc-compact-toolbar">
        <div class="munc-compact-search-box">
          <svg class="munc-search-icon-svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input id="mycouncil-search-input"
                 placeholder="Search ward # (e.g. 1, 1A), councillor, or party…"
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
    const idx = winners.findIndex(w => String(w.ward).toLowerCase() === q || `${w.ward}${w.seat}`.toLowerCase() === q || String(w.ward_label || '').toLowerCase() === q);
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
      const winners = MYCOUNCIL_STATE.council ? (MYCOUNCIL_STATE.council.winners || []) : [];
      const w = winners[idx];
      const wKey = w ? (w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`)).toLowerCase() : '';
      const el = (wKey ? document.getElementById('mycouncil-card-' + wKey) : null) ||
                 document.getElementById('mycouncil-card-' + idx);
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
        const matchWard = String(w.ward) === q || `${w.ward}${w.seat}`.toLowerCase().includes(q) || ('ward ' + w.ward).includes(q) || String(w.ward_label || '').toLowerCase().includes(q);
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
          const wLabel = w.ward_label || (w.seat ? `${w.ward}${w.seat}` : `${w.ward}`);

          return `
            <div class="mycorp-ward-card" id="mycouncil-card-${wLabel.toLowerCase()}" data-card-idx="${idx}" style="--card-accent:${pColor}">
              <div>
                <!-- Card Header with 1A, 1B, 1C like ward -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="font-size:16px;font-weight:800;color:var(--text)">
                      Ward ${wLabel} ${w.seat ? '· Seat ' + esc(w.seat) : ''}
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

  // 2: Nagaradhyaksha President View (Complete Candidates Roster + Governance Insight)
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
        const wLbl = (w.ward_label || `${w.ward}${w.seat || ''}`).toLowerCase();
        const matchWard = String(w.ward) === q || wLbl === q || wLbl.includes(q) || ('ward ' + wLbl).includes(q);
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
                    Ward ${w.ward_label || (w.seat ? w.ward + w.seat : w.ward)} ${w.seat ? '· Seat ' + esc(w.seat) : ''}
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
                  WARD ${w.ward_label || (w.seat ? w.ward + w.seat : w.ward)} ${w.seat ? '· SEAT ' + esc(w.seat) : ''}
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


  function renderCandidateLeaderboardHtml(cands) {
    if (!cands || !cands.length) return '<p class="note">No candidate breakdown available.</p>';
    return `
      <div style="overflow-x:auto;margin-top:10px">
        <table class="tbl" style="margin:0;font-size:12px">
          <thead>
            <tr>
              <th style="width:40px">Pos</th>
              <th>Candidate</th>
              <th>Political Party</th>
              <th style="text-align:right">Votes</th>
              <th style="text-align:right">Vote Share</th>
            </tr>
          </thead>
          <tbody>
            ${cands.map((c, idx) => {
              const posLabel = idx === 0 ? '🥇 1st (Win)' : (idx === 1 ? '🥈 2nd' : (idx === 2 ? '🥉 3rd' : `${idx + 1}th`));
              const isWin = idx === 0;
              const pCol = getPartyColor(c[1]);
              return `
                <tr class="r" style="${isWin ? 'background:rgba(34,197,94,0.06)' : ''}">
                  <td><b>${posLabel}</b></td>
                  <td><b style="color:${isWin ? '#4ade80' : 'var(--text)'}">${esc(c[0])}</b></td>
                  <td>
                    <span class="tag" style="background:var(--s2);border-left:3px solid ${pCol};font-size:11px">
                      ${esc(c[1])}
                    </span>
                  </td>
                  <td style="text-align:right"><b style="color:${isWin ? '#ff9933' : 'var(--text)'}">${fmt(c[2])}</b></td>
                  <td style="text-align:right"><b>${c[3] ? c[3].toFixed(1) + '%' : '–'}</b></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

})();
