-- ============================================================
-- Electrol India — Lok Sabha Members & Positions Schema
-- ============================================================
CREATE TABLE IF NOT EXISTS ls_members (
  member_id            INTEGER PRIMARY KEY,
  full_name            TEXT NOT NULL,
  first_name           TEXT,
  last_name            TEXT,
  constituency         TEXT,
  matched_pc           TEXT,
  state                TEXT,
  party_name           TEXT,
  party_code           TEXT,
  member_status        TEXT DEFAULT 'Sitting',
  gender               TEXT,
  date_of_birth        DATE,
  age                  INTEGER,
  marital_status       TEXT,
  birth_place          TEXT,
  father_name          TEXT,
  mother_name          TEXT,
  spouse_name          TEXT,
  sons                 INTEGER DEFAULT 0,
  daughters            INTEGER DEFAULT 0,
  qualification        TEXT,
  education            TEXT,
  profession           TEXT,
  other_profession     TEXT,
  email                TEXT,
  personal_phone       TEXT,
  delhi_phone          TEXT,
  present_address      TEXT,
  permanent_address    TEXT,
  photo_url            TEXT,
  facebook_url         TEXT,
  twitter_url          TEXT,
  instagram_url        TEXT,
  pinterest_url        TEXT,
  linkedin_url         TEXT,
  other_social_activities TEXT,
  interests            TEXT,
  hobbies              TEXT,
  sports               TEXT,
  books_published      TEXT,
  countries_visited    TEXT,
  lok_sabha_terms      TEXT,
  number_of_terms      INTEGER DEFAULT 1,
  oath_video_url       TEXT,
  oath_video_search_url TEXT,
  oath_video_status    TEXT,
  source_profile_url   TEXT,
  source_positions_url TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ls_member_positions (
  id                   BIGSERIAL PRIMARY KEY,
  member_id            INTEGER REFERENCES ls_members(member_id) ON DELETE CASCADE,
  member_name          TEXT,
  period               TEXT,
  position_held        TEXT,
  source_profile_url   TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ls_members_pc ON ls_members(matched_pc);
CREATE INDEX IF NOT EXISTS idx_ls_members_state ON ls_members(state);
CREATE INDEX IF NOT EXISTS idx_ls_members_party ON ls_members(party_code);
CREATE INDEX IF NOT EXISTS idx_ls_member_pos_mid ON ls_member_positions(member_id);

-- Enable RLS
ALTER TABLE ls_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE ls_member_positions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read ls_members" ON ls_members FOR SELECT USING (true);
CREATE POLICY "Public read ls_member_positions" ON ls_member_positions FOR SELECT USING (true);
