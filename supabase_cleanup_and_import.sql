-- ==========================================================================
-- Supabase Database Cleanup & Multi-State Assembly Migration
-- ==========================================================================
BEGIN;

-- 1. CLEANUP PREVIOUS YEARS FOR MAHARASHTRA & ANDHRA PRADESH (Keep ONLY 2024)
DELETE FROM candidates WHERE constituency_id IN (
  SELECT c.id FROM constituencies c
  JOIN elections e ON c.election_id = e.id
  WHERE e.type = 'assembly' AND (
    (e.state ILIKE '%Maharashtra%' AND e.year != 2024) OR
    (e.state ILIKE '%Andhra Pradesh%' AND e.year != 2024)
  )
);
DELETE FROM constituencies WHERE election_id IN (
  SELECT id FROM elections
  WHERE type = 'assembly' AND (
    (state ILIKE '%Maharashtra%' AND year != 2024) OR
    (state ILIKE '%Andhra Pradesh%' AND year != 2024)
  )
);
DELETE FROM elections WHERE type = 'assembly' AND (
  (state ILIKE '%Maharashtra%' AND year != 2024) OR
  (state ILIKE '%Andhra Pradesh%' AND year != 2024)
);

-- State: Andhra Pradesh (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Andhra Pradesh', 'assembly', 2024, 175, TRUE, '🏛️ Andhra Pradesh Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Arunachal Pradesh (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Arunachal Pradesh', 'assembly', 2024, 50, TRUE, '🏔️ Arunachal Pradesh Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Assam (2021)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Assam', 'assembly', 2021, 126, TRUE, '🦏 Assam Assembly 2021') ON CONFLICT DO NOTHING;
-- State: Bihar (2020)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Bihar', 'assembly', 2020, 243, TRUE, '🌾 Bihar Assembly 2020') ON CONFLICT DO NOTHING;
-- State: Chhattisgarh (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Chhattisgarh', 'assembly', 2023, 90, TRUE, '🌳 Chhattisgarh Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Delhi (2020)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Delhi', 'assembly', 2020, 70, TRUE, '🏛️ Delhi Assembly 2020') ON CONFLICT DO NOTHING;
-- State: Goa (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Goa', 'assembly', 2022, 40, TRUE, '🏖️ Goa Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Gujarat (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Gujarat', 'assembly', 2022, 182, TRUE, '🦁 Gujarat Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Haryana (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Haryana', 'assembly', 2024, 90, TRUE, '🚜 Haryana Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Himachal Pradesh (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Himachal Pradesh', 'assembly', 2022, 68, TRUE, '🏔️ Himachal Pradesh Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Jammu & Kashmir (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Jammu & Kashmir', 'assembly', 2024, 90, TRUE, '❄️ Jammu & Kashmir Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Jharkhand (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Jharkhand', 'assembly', 2024, 81, TRUE, '⛏️ Jharkhand Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Karnataka (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Karnataka', 'assembly', 2023, 224, TRUE, '🐘 Karnataka Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Kerala (2021)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Kerala', 'assembly', 2021, 140, TRUE, '🌴 Kerala Assembly 2021') ON CONFLICT DO NOTHING;
-- State: Madhya Pradesh (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Madhya Pradesh', 'assembly', 2023, 230, TRUE, '🐅 Madhya Pradesh Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Maharashtra (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Maharashtra', 'assembly', 2024, 288, TRUE, '🏢 Maharashtra Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Manipur (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Manipur', 'assembly', 2022, 60, TRUE, '🌺 Manipur Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Meghalaya (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Meghalaya', 'assembly', 2023, 60, TRUE, '🌧️ Meghalaya Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Mizoram (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Mizoram', 'assembly', 2023, 40, TRUE, '🌿 Mizoram Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Nagaland (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Nagaland', 'assembly', 2023, 60, TRUE, '🌄 Nagaland Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Odisha (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Odisha', 'assembly', 2024, 147, TRUE, '🌊 Odisha Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Puducherry (2021)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Puducherry', 'assembly', 2021, 30, TRUE, '⛵ Puducherry Assembly 2021') ON CONFLICT DO NOTHING;
-- State: Punjab (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Punjab', 'assembly', 2022, 117, TRUE, '🌾 Punjab Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Rajasthan (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Rajasthan', 'assembly', 2023, 200, TRUE, '🏰 Rajasthan Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Sikkim (2024)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Sikkim', 'assembly', 2024, 32, TRUE, '🏔️ Sikkim Assembly 2024') ON CONFLICT DO NOTHING;
-- State: Tamil Nadu (2021)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Tamil Nadu', 'assembly', 2021, 234, TRUE, '🛕 Tamil Nadu Assembly 2021') ON CONFLICT DO NOTHING;
-- State: Telangana (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Telangana', 'assembly', 2023, 119, TRUE, '🏛️ Telangana Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Tripura (2023)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Tripura', 'assembly', 2023, 60, TRUE, '🎋 Tripura Assembly 2023') ON CONFLICT DO NOTHING;
-- State: Uttar Pradesh (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Uttar Pradesh', 'assembly', 2022, 403, TRUE, '🛕 Uttar Pradesh Assembly 2022') ON CONFLICT DO NOTHING;
-- State: Uttarakhand (2022)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('Uttarakhand', 'assembly', 2022, 70, TRUE, '⛰️ Uttarakhand Assembly 2022') ON CONFLICT DO NOTHING;
-- State: West Bengal (2021)
INSERT INTO elections (state, type, year, total_seats, is_active, notes) VALUES ('West Bengal', 'assembly', 2021, 294, TRUE, '🐅 West Bengal Assembly 2021') ON CONFLICT DO NOTHING;

-- 2. CREATE PERFORMANCE INDEXES FOR HIGH-SPEED QUERIES
CREATE INDEX IF NOT EXISTS idx_elections_type_year ON elections(type, year);
CREATE INDEX IF NOT EXISTS idx_constituencies_election_id ON constituencies(election_id);
CREATE INDEX IF NOT EXISTS idx_candidates_constituency_id ON candidates(constituency_id);

COMMIT;

-- 3. REFRESH & OPTIMIZE DATABASE (Runs outside transaction)
VACUUM (ANALYZE) elections;
VACUUM (ANALYZE) constituencies;
VACUUM (ANALYZE) candidates;

