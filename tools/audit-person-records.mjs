import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = async f => JSON.parse(await fs.readFile(path.join(root, f), 'utf8'));

const norm = s => String(s || '').normalize('NFKC').toLowerCase()
  .replace(/municipal corporation|municipal council|nagar panchayat|\((?:sc|st)\)|\b(?:shri|smt|shrimati|sushri|dr|adv|prof|mr|mrs|ms|alias|haji)\b\.?/gi, '')
  .replace(/[^\p{L}\p{N}]/gu, '');

const partyAliases = {
  'IND.': 'IND',
  'INDEPENDENT': 'IND',
  'J&KNC': 'JKN',
  'JKNC': 'JKN',
  'LJSP(RV)': 'LJPRV',
  'LJPRV': 'LJPRV',
  'LJSP': 'LJPRV',
  'LJP': 'LJPRV',
  'JSP': 'JNP',
  'JNP': 'JNP',
  'AJSU': 'AJSUP',
  'AJSUP': 'AJSUP',
  'RLP': 'RLTP',
  'RLTP': 'RLTP',
  'HAM (S)': 'HAMS',
  'HAMS': 'HAMS',
  'YSR CONGRESS PARTY': 'YSRCP',
  'YSRCP': 'YSRCP',
  'APNA DAL (S)': 'ADAL',
  'ADAL': 'ADAL',
  'BAP': 'BHRTADVSIP',
  'BHRTADVSIP': 'BHRTADVSIP',
  'CPI(ML)(L)': 'CPIMLL',
  'CPI(M-L)(L)': 'CPIMLL',
  'CPIMLL': 'CPIMLL',
  'CPIM': 'CPI(M)',
  'CPI(M)': 'CPI(M)',
  'SHS': 'SS',
  'SHSUBT': 'SS'
};

const canonParty = (parties, p) => {
  const raw = parties?.aliases?.[p] || String(p || '').toUpperCase().trim();
  return partyAliases[raw] || raw;
};

const partyCompatible = (parties, p1, p2) => {
  const c1 = canonParty(parties, p1), c2 = canonParty(parties, p2);
  if (c1 === c2) return true;
  if ((c1 === 'SS' && ['SHS', 'SHSUBT'].includes(c2)) || (c2 === 'SS' && ['SHS', 'SHSUBT'].includes(c1))) return true;
  if ((c1 === 'NCP' && ['NCP', 'NCPSP'].includes(c2)) || (c2 === 'NCP' && ['NCP', 'NCPSP'].includes(c1))) return true;
  return false;
};

const tokensMatch = (a, b) => {
  const cleanA = norm(a), cleanB = norm(b);
  if (cleanA === cleanB) return true;
  if (cleanA.includes(cleanB) || cleanB.includes(cleanA)) return true;
  return false;
};

export async function auditPersonRecords() {
  const profileText = await fs.readFile(path.join(root, 'js/html-profile-seats.js'), 'utf8');
  const profileSeats = JSON.parse(profileText.match(/window.ELECTROL_PROFILE_SEATS=(.*);/)[1]);
  const bodyName = s => norm(String(s || '').replace(/\([^)]*\)/g, '')).replace(/^brihanmumbai$/, 'mumbai');
  const catalog = await read('data/catalog.json');
  const bodies = await read('data/local-catalog.json');
  const parties = await read('data/party-directory.json');
  const editions = new Map(), bodyData = new Map();

  for (const e of catalog) editions.set(e.id, await read(e.file));

  const report = { people: 0, sourceMatches: 0, localMatches: 0, oldLocalURLsCorrected: 0, pending: [], outcomeMismatches: [] };
  const people = await read('data/people-directory.json');

  // Filter out any obsolete test scratch keys from people directory
  people.rows = people.rows.filter(r => !r.key?.startsWith('local-council-test-'));

  for (const r of people.rows) {
    report.people++;
    if (!['mp', 'mla', 'local'].includes(r.kind)) continue;
    let matches = [];

    if (r.kind === 'local') {
      const possible = bodies.filter(b => norm(String(b.state).replace(/Delhi \(NCT\)|NCT OF Delhi/g, 'Delhi')) === norm(String(r.state).replace(/Delhi \(NCT\)|NCT OF Delhi/g, 'Delhi')) && b.kind === ({corp: 'corporation', municipal: 'corporation'}[r.body_kind] || r.body_kind) && bodyName(b.name) === bodyName(r.body));
      if (possible.length === 1 && (r.seat || /president/i.test(r.role || ''))) {
        const b = possible[0];
        if (!bodyData.has(b.id)) bodyData.set(b.id, await read(b.file));
        const s = bodyData.get(b.id).snapshots[r.year];
        if (!r.seat && s?.president && tokensMatch(s.president.candidate, r.name) && partyCompatible(parties, s.president.party, r.party)) {
          matches.push({ exact: true, candidate_uid: s.president.candidate_uid, body_id: b.id, body: b.name, kind: b.kind, year: Number(r.year), seat: 'head', winner: true, source: b.source, url: '/municipal-councils/' + b.slug + '/?year=' + r.year + '&view=head', district: b.district });
        }
        for (const row of s?.rows || []) {
          if (norm(String(row.ward) + (row.seat || '')) !== norm(r.seat) || row.review) continue;
          const cs = row.cands?.length ? row.cands : [[row.name || row.candidate, row.party, row.votes ?? null]];
          cs.forEach((c, i) => {
            if (partyCompatible(parties, c[1], r.party)) {
              const isExact = norm(c[0]) === norm(r.name);
              const isToken = tokensMatch(c[0], r.name);
              if (isExact) {
                matches.push({ exact: true, candidate_uid: row.candidate_uids?.[i], body_id: b.id, body: b.name, kind: b.kind, year: Number(r.year), seat: String(row.ward) + (row.seat || ''), winner: (row.name || row.candidate) === c[0] && row.party === c[1], source: b.source, url: '/' + ({corporation: 'municipal-corporations', council: 'municipal-councils', nagar: 'panchayat-elections', zp: 'zilla-parishad-elections', samiti: 'panchayat-samitis'}[b.kind]) + '/' + b.slug + '/?year=' + r.year + '&ward=' + encodeURIComponent(r.seat), district: b.district });
              } else if (isToken) {
                matches.push({ exact: false, candidate_uid: row.candidate_uids?.[i], body_id: b.id, body: b.name, kind: b.kind, year: Number(r.year), seat: String(row.ward) + (row.seat || ''), winner: (row.name || row.candidate) === c[0] && row.party === c[1], source: b.source, url: '/' + ({corporation: 'municipal-corporations', council: 'municipal-councils', nagar: 'panchayat-elections', zp: 'zilla-parishad-elections', samiti: 'panchayat-samitis'}[b.kind]) + '/' + b.slug + '/?year=' + r.year + '&ward=' + encodeURIComponent(r.seat), district: b.district });
              }
            }
          });
        }
      }
    } else {
      const e = catalog.find(e => e.level === (r.kind === 'mp' ? 'lok' : 'assembly') && Number(e.year) === Number(r.year) && (e.state === r.state || e.state === 'All India'));
      if (e) {
        const d = editions.get(e.id);
        // Direct MP seat mapping via profileSeats
        if (r.kind === 'mp' && r.mpid) {
          for (const s of d.seats) {
            const altStates = [
              s.state,
              s.state === 'Delhi (NCT)' ? 'NCT OF Delhi' : null,
              s.state === 'Dadra and Nagar Haveli and Daman and Diu' ? 'Dadra & Nagar Haveli and Daman & Diu' : null,
              s.state === 'Andaman and Nicobar Islands' ? 'Andaman & Nicobar Islands' : null
            ].filter(Boolean);

            let isSeatMatch = false;
            for (const alt of altStates) {
              if (Number(profileSeats[alt + '|' + s.n]) === Number(r.mpid)) {
                isSeatMatch = true;
                break;
              }
            }

            if (isSeatMatch) {
              const i = s.c.findIndex(c => d.parties[c[1]].short !== 'NOTA');
              const c = s.c[i];
              if (c && (partyCompatible(parties, d.parties[c[1]].short, r.party) || tokensMatch(c[0], r.name))) {
                matches.push({ exact: true, candidate_uid: s.candidate_uids[i], year: d.year, seat: s.url, winner: true, source: e.source, url: s.url });
              }
            }
          }
        }

        // Standard seat / candidate search
        if (!matches.length) {
          for (const s of d.seats) {
            const stateMatch = norm(s.state) === norm(r.state) || (s.state.includes('Dadra') && r.state.includes('Dadra'));
            const seatMatch = norm(s.t) === norm(r.constituency) || norm(s.t).includes(norm(r.constituency)) || norm(r.constituency).includes(norm(s.t));
            if (!stateMatch || !seatMatch) continue;
            s.c.forEach((c, i) => {
              if (partyCompatible(parties, d.parties[c[1]].short, r.party)) {
                const isExactName = norm(c[0]) === norm(r.name);
                const isExactVotes = r.votes && c[2] === r.votes;
                const isTokenMatch = tokensMatch(c[0], r.name);
                if (isExactName || isExactVotes) {
                  matches.push({ exact: true, candidate_uid: s.candidate_uids[i], year: d.year, seat: s.url, winner: i === s.c.findIndex(c => d.parties[c[1]].short !== 'NOTA'), source: e.source, url: s.url });
                } else if (isTokenMatch) {
                  matches.push({ exact: false, candidate_uid: s.candidate_uids[i], year: d.year, seat: s.url, winner: i === s.c.findIndex(c => d.parties[c[1]].short !== 'NOTA'), source: e.source, url: s.url });
                }
              }
            });
          }
        }
      }
    }

    const exactMatches = matches.filter(m => m.exact);
    const finalMatches = exactMatches.length === 1 ? exactMatches : (matches.length === 1 ? matches : (exactMatches.length > 1 ? exactMatches : matches));

    if (finalMatches.length === 1) {
      const m = finalMatches[0];
      report.sourceMatches++;
      if (r.kind === 'local') {
        report.localMatches++;
        if (r.election_url !== m.url) {
          r.source_election_url ||= r.election_url;
          r.election_url = m.url;
          report.oldLocalURLsCorrected++;
        }
        r.body_id = m.body_id;
        if (m.district) r.district = m.district;
      }
      r.source_candidate_uid = m.candidate_uid;
      r.source_match_status = 'matched-imported-contest';
      r.election_outcome = m.winner ? 'winner' : 'contested';
      if (!m.winner) report.outcomeMismatches.push({ key: r.key, name: r.name, source: m.source, reason: 'Directory says winner; matched imported candidate is not first non-NOTA result' });
    } else {
      r.source_match_status = finalMatches.length ? 'ambiguous' : 'not-reconciled';
      report.pending.push({ key: r.key, name: r.name, kind: r.kind, state: r.state, body: r.body, year: r.year, seat: r.seat, reason: finalMatches.length ? 'Multiple source contest matches' : 'No exact source contest match with the same name, party, state, seat and year' });
    }
  }

  for (const f of ['data/people-directory.json', 'data/representatives-index.json']) {
    const d = await read(f);
    const updated = new Map(people.rows.map(r => [r.key, r]));
    d.rows = d.rows.filter(r => !r.key?.startsWith('local-council-test-')).map(r => updated.get(r.key) || r);
    await fs.writeFile(path.join(root, f), JSON.stringify(d));
  }

  await fs.mkdir(path.join(root, 'reports/identity-audit'), { recursive: true });
  await fs.writeFile(path.join(root, 'reports/identity-audit/record-reconciliation.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ ...report, pending: report.pending.length, outcomeMismatches: report.outcomeMismatches.length }));
  return report;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await auditPersonRecords();
