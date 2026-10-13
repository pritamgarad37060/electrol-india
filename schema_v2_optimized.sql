-- ============================================================
-- Electrol India — Optimized Schema Migration v2
-- ============================================================
-- Run this in Supabase → SQL Editor
-- This ADDS to the existing schema, it does NOT drop data.
--
-- Designed for massive scale:
--   All Lok Sabha elections (1st-18th)
--   All state assembly elections (28 states x 15+ years)
--   Bypolls, Municipal Corp, Panchayat Samiti, Council
--   500+ elections, 100K+ constituencies, 1M+ candidates
-- ============================================================

-- 1. EXPAND election types
ALTER TABLE elections DROP CONSTRAINT IF EXISTS elections_type_check;
ALTER TABLE elections ADD CONSTRAINT elections_type_check
  CHECK (type IN ('loksabha','assembly','bypoll','municipal','panchayat','council','presidential','rajyasabha'));

-- Add useful columns for future data
ALTER TABLE elections ADD COLUMN IF NOT EXISTS election_number  INTEGER;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS phase_count      INTEGER;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS start_date       DATE;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS end_date         DATE;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS result_date      DATE;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS notes            TEXT;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS is_active        BOOLEAN DEFAULT TRUE;

-- 2. DISTRICTS table (for municipal/panchayat hierarchy)
CREATE TABLE IF NOT EXISTS districts (
  id        SERIAL PRIMARY KEY,
  state_id  INTEGER REFERENCES states(id),
  name      TEXT NOT NULL,
  UNIQUE(state_id, name)
);
ALTER TABLE districts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read districts" ON districts FOR SELECT USING (true);

-- 3. EXPAND constituencies table
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS district_id    INTEGER REFERENCES districts(id);
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS pc_no          INTEGER;
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS ward_no        INTEGER;
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS reserved_for   TEXT;
ALTER TABLE constituencies ADD COLUMN IF NOT EXISTS total_candidates INTEGER;

-- Prevent duplicate constituencies per election
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'uq_constituency_election'
  ) THEN
    BEGIN
      ALTER TABLE constituencies
        ADD CONSTRAINT uq_constituency_election UNIQUE (election_id, name, ac_no);
    EXCEPTION WHEN unique_violation THEN
      RAISE NOTICE 'Cannot add unique constraint yet - duplicates still exist.';
    END;
  END IF;
END $$;

-- 4. EXPAND candidates table
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS occupation      TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS education       TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS criminal_cases  INTEGER;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS assets_inr      BIGINT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS deposit_lost    BOOLEAN;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS rank            INTEGER;

-- 5. ALLIANCES table
CREATE TABLE IF NOT EXISTS alliances (
  id            SERIAL PRIMARY KEY,
  election_id   INTEGER NOT NULL REFERENCES elections(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  color_hex     TEXT,
  total_seats   INTEGER,
  UNIQUE(election_id, name)
);
CREATE TABLE IF NOT EXISTS alliance_parties (
  alliance_id   INTEGER NOT NULL REFERENCES alliances(id) ON DELETE CASCADE,
  party_code    TEXT NOT NULL REFERENCES parties(code),
  PRIMARY KEY (alliance_id, party_code)
);
ALTER TABLE alliances ENABLE ROW LEVEL SECURITY;
ALTER TABLE alliance_parties ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read alliances" ON alliances FOR SELECT USING (true);
CREATE POLICY "Public read alliance_parties" ON alliance_parties FOR SELECT USING (true);

-- 6. OPTIMIZED INDEXES for fast queries
CREATE INDEX IF NOT EXISTS idx_const_election_state ON constituencies(election_id, state_id);
CREATE INDEX IF NOT EXISTS idx_const_election_party ON constituencies(election_id, winner_party);
CREATE INDEX IF NOT EXISTS idx_elections_state_year ON elections(state, year DESC);
CREATE INDEX IF NOT EXISTS idx_elections_type_year ON elections(type, year DESC);
CREATE INDEX IF NOT EXISTS idx_candidates_const_votes ON candidates(constituency_id, total_votes DESC);
CREATE INDEX IF NOT EXISTS idx_candidates_name_winner ON candidates(name, is_winner) WHERE is_winner = TRUE;
CREATE INDEX IF NOT EXISTS idx_elections_number ON elections(election_number) WHERE election_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_districts_state ON districts(state_id);
CREATE INDEX IF NOT EXISTS idx_const_district ON constituencies(district_id) WHERE district_id IS NOT NULL;

-- 7. MATERIALIZED VIEW: Election Party Summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_election_party_summary AS
SELECT
  c.election_id,
  e.year,
  e.type,
  e.state,
  e.name AS election_name,
  c.winner_party AS party,
  COUNT(*) AS seats_won,
  SUM(c.winner_votes) AS total_winner_votes,
  SUM(c.votes_polled) AS total_votes_polled,
  SUM(c.electors) AS total_electors
FROM constituencies c
JOIN elections e ON e.id = c.election_id
WHERE c.winner_party IS NOT NULL
GROUP BY c.election_id, e.year, e.type, e.state, e.name, c.winner_party;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_election_party
  ON mv_election_party_summary(election_id, party);

-- 8. MATERIALIZED VIEW: State Election Summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_state_election_summary AS
SELECT
  e.id AS election_id,
  e.year,
  e.type,
  COALESCE(e.state, 'National') AS state_name,
  e.name AS election_name,
  e.total_seats,
  COUNT(DISTINCT c.id) AS constituencies_loaded,
  COUNT(DISTINCT ca.id) AS candidates_loaded,
  SUM(c.votes_polled) AS total_votes,
  SUM(c.electors) AS total_electors,
  ROUND(AVG(c.turnout_pct)::numeric, 2) AS avg_turnout
FROM elections e
LEFT JOIN constituencies c ON c.election_id = e.id
LEFT JOIN candidates ca ON ca.election_id = e.id
GROUP BY e.id, e.year, e.type, e.state, e.name, e.total_seats;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_state_election
  ON mv_state_election_summary(election_id);

-- 9. RPC: Fast paginated constituency search
CREATE OR REPLACE FUNCTION search_constituencies(
  query TEXT,
  election_filter INTEGER DEFAULT NULL,
  state_filter INTEGER DEFAULT NULL,
  party_filter TEXT DEFAULT NULL,
  lim INTEGER DEFAULT 50,
  off_val INTEGER DEFAULT 0
)
RETURNS TABLE(
  id INTEGER,
  election_id INTEGER,
  election_name TEXT,
  election_year INTEGER,
  election_type TEXT,
  constituency_name TEXT,
  ac_no INTEGER,
  state_name TEXT,
  category TEXT,
  winner_name TEXT,
  winner_party TEXT,
  margin BIGINT,
  turnout_pct NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    c.election_id,
    e.name AS election_name,
    e.year AS election_year,
    e.type AS election_type,
    c.name AS constituency_name,
    c.ac_no,
    s.name AS state_name,
    c.category,
    c.winner_name,
    c.winner_party,
    c.margin,
    c.turnout_pct
  FROM constituencies c
  JOIN elections e ON e.id = c.election_id
  LEFT JOIN states s ON s.id = c.state_id
  WHERE
    (query IS NULL OR query = '' OR
     c.name ILIKE '%' || query || '%' OR
     c.winner_name ILIKE '%' || query || '%')
    AND (election_filter IS NULL OR c.election_id = election_filter)
    AND (state_filter IS NULL OR c.state_id = state_filter)
    AND (party_filter IS NULL OR c.winner_party = party_filter)
  ORDER BY e.year DESC, c.ac_no ASC, c.name ASC
  LIMIT lim OFFSET off_val;
END;
$$ LANGUAGE plpgsql STABLE;

-- 10. RPC: Election dashboard stats (single call)
CREATE OR REPLACE FUNCTION get_election_dashboard(eid INTEGER)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'election', (SELECT row_to_json(e) FROM elections e WHERE e.id = eid),
    'total_constituencies', (SELECT COUNT(*) FROM constituencies WHERE election_id = eid),
    'total_candidates', (SELECT COUNT(*) FROM candidates WHERE election_id = eid),
    'total_voters', (SELECT SUM(votes_polled) FROM constituencies WHERE election_id = eid),
    'total_electors', (SELECT SUM(electors) FROM constituencies WHERE election_id = eid),
    'avg_turnout', (SELECT ROUND(AVG(turnout_pct)::numeric, 2) FROM constituencies WHERE election_id = eid),
    'party_seats', (
      SELECT json_agg(row_to_json(ps))
      FROM (
        SELECT winner_party AS party, COUNT(*) AS seats, SUM(winner_votes) AS votes
        FROM constituencies
        WHERE election_id = eid AND winner_party IS NOT NULL
        GROUP BY winner_party
        ORDER BY COUNT(*) DESC
      ) ps
    )
  ) INTO result;
  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;

-- 11. ENRICH major parties with full names and colors
UPDATE parties SET full_name = 'Bharatiya Janata Party', color_hex = '#ff7a00' WHERE code = 'BJP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Indian National Congress', color_hex = '#1d6fe8' WHERE code = 'INC' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Samajwadi Party', color_hex = '#d62828' WHERE code = 'SP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'All India Trinamool Congress', color_hex = '#2a9d8f' WHERE code = 'AITC' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Dravida Munnetra Kazhagam', color_hex = '#6a1b9a' WHERE code = 'DMK' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Telugu Desam Party', color_hex = '#f2c200' WHERE code = 'TDP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Janata Dal (United)', color_hex = '#2e7d32' WHERE code = 'JD(U)' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Shiv Sena (Uddhav Balasaheb Thackeray)', color_hex = '#e76f51' WHERE code = 'SHSUBT' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'NCP (Sharadchandra Pawar)', color_hex = '#c2185b' WHERE code = 'NCPSP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Shiv Sena', color_hex = '#f4a261' WHERE code = 'SHS' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Independent', color_hex = '#8d8d8d' WHERE code = 'IND' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'None of the Above', color_hex = '#bbbbbb' WHERE code = 'NOTA' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Rashtriya Janata Dal', color_hex = '#1b8a3a' WHERE code = 'RJD' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Communist Party of India (Marxist)', color_hex = '#b71c1c' WHERE code = 'CPI(M)' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'YSR Congress Party', color_hex = '#2e86de' WHERE code = 'YSRCP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Nationalist Congress Party', color_hex = '#1565c0' WHERE code = 'NCP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Bahujan Samaj Party', color_hex = '#0984e3' WHERE code = 'BSP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Aam Aadmi Party', color_hex = '#00b894' WHERE code = 'AAAP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Jana Sena Party', color_hex = '#e63946' WHERE code = 'JnP' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Communist Party of India', color_hex = '#d63031' WHERE code = 'CPI' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Bharat Rashtra Samithi', color_hex = '#e84393' WHERE code = 'BRS' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'All India Majlis-e-Ittehadul Muslimeen', color_hex = '#006266' WHERE code = 'AIMIM' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Lok Janshakti Party (Ram Vilas)', color_hex = '#ff6b81' WHERE code = 'LJPRV' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Jharkhand Mukti Morcha', color_hex = '#6ab04c' WHERE code = 'JMM' AND (full_name IS NULL OR full_name = '');
UPDATE parties SET full_name = 'Janata Dal (Secular)', color_hex = '#7ed6df' WHERE code = 'JD(S)' AND (full_name IS NULL OR full_name = '');

-- 12. REFRESH materialized views
REFRESH MATERIALIZED VIEW mv_election_party_summary;
REFRESH MATERIALIZED VIEW mv_state_election_summary;
