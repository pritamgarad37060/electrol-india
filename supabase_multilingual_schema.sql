-- =====================================================================
-- ELECTORAL INDIA: CENTRALIZED MULTILINGUAL SYSTEM (SUPABASE POSTGRES)
-- 10 Official Languages: en, hi, bn, mr, te, ta, gu, ur (RTL), kn, ml
-- Production Ready | RLS Protected | High-Speed Catalog Functions
-- =====================================================================

-- 1. LANGUAGES TABLE
CREATE TABLE IF NOT EXISTS languages (
  code VARCHAR(10) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  native_name VARCHAR(100) NOT NULL,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  text_direction VARCHAR(3) NOT NULL DEFAULT 'ltr' CHECK (text_direction IN ('ltr', 'rtl')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. UI TRANSLATIONS TABLE
CREATE TABLE IF NOT EXISTS ui_translations (
  id BIGSERIAL PRIMARY KEY,
  translation_key VARCHAR(150) NOT NULL,
  language_code VARCHAR(10) NOT NULL REFERENCES languages(code) ON DELETE CASCADE,
  translated_text TEXT NOT NULL,
  translation_status VARCHAR(20) NOT NULL DEFAULT 'published' CHECK (translation_status IN ('draft', 'reviewed', 'published')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_by VARCHAR(100) DEFAULT 'system',
  CONSTRAINT uq_translation_key_lang UNIQUE (translation_key, language_code)
);

-- 3. CONTENT TRANSLATIONS TABLE (For Candidates, Parties, Wards, Assemblies)
CREATE TABLE IF NOT EXISTS content_translations (
  id BIGSERIAL PRIMARY KEY,
  content_type VARCHAR(50) NOT NULL, -- 'candidate', 'party', 'constituency', 'local_body', 'election'
  entity_id VARCHAR(100) NOT NULL,
  field_name VARCHAR(50) NOT NULL,   -- 'name', 'bio', 'description', 'title'
  language_code VARCHAR(10) NOT NULL REFERENCES languages(code) ON DELETE CASCADE,
  translated_text TEXT NOT NULL,
  translation_status VARCHAR(20) NOT NULL DEFAULT 'published' CHECK (translation_status IN ('draft', 'reviewed', 'published')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_content_translation UNIQUE (content_type, entity_id, field_name, language_code)
);

-- 4. PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_ui_trans_lang ON ui_translations(language_code);
CREATE INDEX IF NOT EXISTS idx_ui_trans_key ON ui_translations(translation_key);
CREATE INDEX IF NOT EXISTS idx_ui_trans_lookup ON ui_translations(language_code, translation_status);
CREATE INDEX IF NOT EXISTS idx_content_trans_lookup ON content_translations(content_type, entity_id, language_code);

-- 5. ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE languages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ui_translations ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_translations ENABLE ROW LEVEL SECURITY;

-- Public read access for visitors
DROP POLICY IF EXISTS "Allow public read access to enabled languages" ON languages;
CREATE POLICY "Allow public read access to enabled languages" ON languages
  FOR SELECT USING (is_enabled = true);
DROP POLICY IF EXISTS "Allow public read access to published UI translations" ON ui_translations;
CREATE POLICY "Allow public read access to published UI translations" ON ui_translations
  FOR SELECT USING (translation_status = 'published');
DROP POLICY IF EXISTS "Allow public read access to published content translations" ON content_translations;
CREATE POLICY "Allow public read access to published content translations" ON content_translations
  FOR SELECT USING (translation_status = 'published');

-- 6. RPC FUNCTION: GET FAST LANGUAGE CATALOG IN ONE JSON CALL
CREATE OR REPLACE FUNCTION get_language_catalog(p_lang_code VARCHAR(10))
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_catalog JSONB;
BEGIN
  SELECT jsonb_object_agg(translation_key, translated_text)
  INTO v_catalog
  FROM ui_translations
  WHERE language_code = p_lang_code
    AND translation_status = 'published';

  RETURN COALESCE(v_catalog, '{}'::jsonb);
END;
$$;

-- 7. SEED DATA: 10 SUPPORTED LANGUAGES
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('en', 'English', 'English', TRUE, TRUE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('hi', 'Hindi', 'हिन्दी', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('bn', 'Bengali', 'বাংলা', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('mr', 'Marathi', 'मराठी', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('te', 'Telugu', 'తెలుగు', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('ta', 'Tamil', 'தமிழ்', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('gu', 'Gujarati', 'ગુજરાતી', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('ur', 'Urdu', 'اردو', TRUE, FALSE, 'rtl')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('kn', 'Kannada', 'ಕನ್ನಡ', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();
INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('ml', 'Malayalam', 'മലയാളം', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();

-- 8. SEED DATA: UI TRANSLATIONS (CATALOG)
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'en', 'Home', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'hi', 'होम', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'bn', 'হোম', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'mr', 'मुख्यपृष्ठ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'te', 'హోమ్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'ta', 'முகப்பு', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'gu', 'હોમ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'ur', 'ہوم', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'kn', 'ಮುಖಪುಟ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Home', 'ml', 'ഹോം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'en', 'Lok Sabha', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'hi', 'लोकसभा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'bn', 'লোকসভা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'mr', 'लोकसभा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'te', 'లోక్‌సభ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'ta', 'மக்களவை', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'gu', 'લોકસભા', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'ur', 'لوک سبھا', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'kn', 'ಲೋಕಸಭೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha', 'ml', 'ലോക്സഭ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'en', 'Lok Sabha 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'hi', 'लोकसभा 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'bn', 'লোকসভা ২০২৪', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'mr', 'लोकसभा २०२४', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'te', 'లోక్‌సభ 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'ta', 'மக்களவை 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'gu', 'લોકસભા ૨૦૨૪', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'ur', 'لوک سبھا 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'kn', 'ಲೋಕಸಭೆ 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha 2024', 'ml', 'ലോക്സഭ 2024', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'en', 'Lok Sabha MPs', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'hi', 'लोकसभा सांसद', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'bn', 'লোকসভার সাংসদ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'mr', 'लोकसभा खासदार', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'te', 'లోక్‌సభ ఎంపీలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'ta', 'மக்களவை எம்.பி.க்கள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'gu', 'લોકસભા સાંસદો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'ur', 'لوک سبھا ارکان پارلیمنٹ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'kn', 'ಲೋಕಸಭಾ ಸಂಸದರು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Lok Sabha MPs', 'ml', 'ലോക്സഭാ എം.പിമാർ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'en', 'Maharashtra', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'hi', 'महाराष्ट्र', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'bn', 'মহারাষ্ট্র', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'mr', 'महाराष्ट्र', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'te', 'మహారాష్ట్ర', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'ta', 'மகாராஷ்டிரா', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'gu', 'મહારાષ્ટ્ર', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'ur', 'مہاراشٹر', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'kn', 'ಮಹಾರಾಷ್ಟ್ರ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Maharashtra', 'ml', 'മഹാരാഷ്ട്ര', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'en', 'Municipal Corporations', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'hi', 'नगर निगम (महानगर पालिका)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'bn', 'পৌর নিগম (মহানগর পালিকা)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'mr', 'महानगरपालिका', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'te', 'మున్సిపల్ కార్పొరేషన్లు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'ta', 'மாநகராட்சிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'gu', 'મ્યુનિસિપલ કોર્પોરેશન', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'ur', 'میونسپل کارپوریشنز', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'kn', 'ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Corporations', 'ml', 'മുനിസിപ്പൽ കോർപ്പറേഷനുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'en', 'Municipal Councils', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'hi', 'नगर परिषद (नगर पालिका)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'bn', 'পৌরসভা (নগর পরিষদ)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'mr', 'नगरपरिषदा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'te', 'మున్సిపల్ కౌన్సిళ్లు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'ta', 'நகராட்சிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'gu', 'નગર પાલિકાઓ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'ur', 'میونسپل کونسلز', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'kn', 'ಪುರಸಭೆಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Municipal Councils', 'ml', 'മുനിസിപ്പൽ കൗൺസിലുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'en', 'All Assemblies', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'hi', 'सभी विधानसभाएं', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'bn', 'সমস্ত বিধানসভা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'mr', 'सर्व विधानसभा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'te', 'అన్ని అసెంబ్లీలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'ta', 'அனைத்து சட்டசபைகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'gu', 'તમામ વિધાનસભાઓ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'ur', 'تمام اسمبلیاں', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'kn', 'ಎಲ್ಲಾ ವಿಧಾನಸಭೆಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Assemblies', 'ml', 'എല്ലാ നിയമസഭകളും', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'en', 'Women', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'hi', 'महिलाएं', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'bn', 'নারী', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'mr', 'महिला', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'te', 'మహిళలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'ta', 'மகளிர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'gu', 'મહિલાઓ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'ur', 'خواتین', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'kn', 'ಮಹಿಳೆಯರು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Women', 'ml', 'വനിതകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'en', 'Map', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'hi', 'नक्शा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'bn', 'মানচিত্র', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'mr', 'नकाशा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'te', 'మ్యాప్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'ta', 'வரைபடம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'gu', 'નકશો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'ur', 'نقشہ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'kn', 'ನಕ್ಷೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Map', 'ml', 'ഭൂപടം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'en', 'Constituencies', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'hi', 'निर्वाचन क्षेत्र', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'bn', 'নির্বাচনী এলাকা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'mr', 'मतदारसंघ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'te', 'నియోజకవర్గాలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'ta', 'தொகுதிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'gu', 'મતવિસ્તારો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'ur', 'انتخابی حلقے', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'kn', 'ಕ್ಷೇತ್ರಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Constituencies', 'ml', 'മണ്ഡലങ്ങൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'en', 'Compare', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'hi', 'तुलना', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'bn', 'তুলনা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'mr', 'तुलना', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'te', 'పోల్చు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'ta', 'ஒப்பிடு', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'gu', 'સરખામણી', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'ur', 'موازنہ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'kn', 'ಹೋಲಿಕೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Compare', 'ml', 'താരതമ്യം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'en', 'Parties', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'hi', 'पार्टियाँ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'bn', 'দলসমূহ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'mr', 'पक्ष', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'te', 'పార్టీలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'ta', 'கட்சிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'gu', 'પક્ષો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'ur', 'جماعتیں', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'kn', 'ಪಕ್ಷಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Parties', 'ml', 'പാർട്ടികൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'en', 'Statistics', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'hi', 'आँकड़े', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'bn', 'পরিসংখ্যান', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'mr', 'आकडेवारी', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'te', 'గణాంకాలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'ta', 'புள்ளிவிவரங்கள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'gu', 'આંકડાકીય માહિતી', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'ur', 'شماریات', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'kn', 'ಅಂಕಿಅಂಶಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Statistics', 'ml', 'സ്ഥിതിവിവരക്കണക്കുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'en', 'Search seat / candidate…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'hi', 'सीट / उम्मीदवार खोजें…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'bn', 'আসন / প্রার্থী খুঁজুন…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'mr', 'जागा / उमेदवार शोधा…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'te', 'సీటు / అభ్యర్థిని వెతకండి…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'ta', 'தொகுதி / வேட்பாளர் தேடுக…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'gu', 'બેઠક / ઉમેદવાર શોધો…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'ur', 'نشست / امیدوار تلاش کریں…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'kn', 'ಕ್ಷೇತ್ರ / ಅಭ್ಯರ್ಥಿಯನ್ನು ಹುಡುಕಿ…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Search seat / candidate…', 'ml', 'സീറ്റ് / സ്ഥാനാർത്ഥിയെ തിരയുക…', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'en', 'Civic Governance', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'hi', 'नागरिक शासन', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'bn', 'পৌর প্রশাসন', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'mr', 'नागरी प्रशासन', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'te', 'పౌర పాలన', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'ta', 'குடிமை நிர்வாகம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'gu', 'નાગરિક શાસન', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'ur', 'شہری نظم و نسق', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'kn', 'ನಾಗರಿಕ ಆಡಳಿತ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Civic Governance', 'ml', 'നഗര ഭരണം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'en', 'Total Seats', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'hi', 'कुल सीटें', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'bn', 'মোট আসন', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'mr', 'एकूण जागा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'te', 'మొత్తం స్థానాలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'ta', 'மொத்த இடங்கள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'gu', 'કુલ બેઠકો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'ur', 'کل نشستیں', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'kn', 'ಒಟ್ಟು ಸ್ಥಾನಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Total Seats', 'ml', 'ആകെ സീറ്റുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'en', 'Results', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'hi', 'परिणाम', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'bn', 'ফলাফল', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'mr', 'निकाल', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'te', 'ఫలితాలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'ta', 'முடிவுகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'gu', 'પરિણામો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'ur', 'نتائج', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'kn', 'ಫಲಿತಾಂಶಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Results', 'ml', 'ഫലങ്ങൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'en', 'Winner', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'hi', 'विजेता', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'bn', 'বিজয়ী', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'mr', 'विजयी', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'te', 'విజేత', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'ta', 'வெற்றியாளர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'gu', 'વિજેતા', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'ur', 'فاتح', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'kn', 'ವಿಜೇತ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Winner', 'ml', 'വിജയി', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'en', 'Runner-up', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'hi', 'उपविजेता', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'bn', 'রানার-আপ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'mr', 'उपविजेता', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'te', 'రన్నరప్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'ta', 'இரண்டாமிடம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'gu', 'રનર-અપ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'ur', 'دوسرے نمبر پر', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'kn', 'ದ್ವಿತೀಯ ಸ್ಥಾನಿ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Runner-up', 'ml', 'രണ്ടാം സ്ഥാനം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'en', 'Votes', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'hi', 'वोट', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'bn', 'ভোট', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'mr', 'मते', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'te', 'ఓట్లు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'ta', 'வாக்குகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'gu', 'મતો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'ur', 'ووٹ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'kn', 'ಮತಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Votes', 'ml', 'വോട്ടുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'en', 'Margin', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'hi', 'जीत का अंतर', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'bn', 'ব্যবধান', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'mr', 'मताधिक्य', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'te', 'మెజారిటీ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'ta', 'வாக்கு வித்தியாസം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'gu', 'તફાવત', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'ur', 'مارجن', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'kn', 'ಅಂತರ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Margin', 'ml', 'ഭൂരിപക്ഷം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'en', 'Turnout', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'hi', 'मतदान %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'bn', 'ভোটদানের হার', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'mr', 'मतदान %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'te', 'ఓటింగ్ శాతం', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'ta', 'வாக்குப்பதிவு %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'gu', 'મતદાન %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'ur', 'ٹرن آؤٹ %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'kn', 'ಮತದಾನ %', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Turnout', 'ml', 'പോളിംഗ് ശതമാനം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'en', 'Candidate', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'hi', 'उम्मीदवार', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'bn', 'প্রার্থী', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'mr', 'उमेदवार', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'te', 'అభ్యర్థి', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'ta', 'வேட்பாளர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'gu', 'ઉમેદવાર', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'ur', 'امیدوار', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'kn', 'ಅಭ್ಯರ್ಥಿ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Candidate', 'ml', 'സ്ഥാനാർത്ഥി', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'en', 'Party', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'hi', 'पार्टी', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'bn', 'দল', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'mr', 'पक्ष', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'te', 'పార్టీ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'ta', 'கட்சி', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'gu', 'પક્ષ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'ur', 'جماعت', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'kn', 'ಪಕ್ಷ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Party', 'ml', 'പാർട്ടി', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'en', 'District', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'hi', 'जिला', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'bn', 'জেলা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'mr', 'जिल्हा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'te', 'జిల్లా', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'ta', 'மாவட்டம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'gu', 'જિલ્લો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'ur', 'ضلع', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'kn', 'ಜಿಲ್ಲೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('District', 'ml', 'ജില്ല', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'en', 'State', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'hi', 'राज्य', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'bn', 'রাজ্য', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'mr', 'राज्य', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'te', 'రాష్ట్రం', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'ta', 'மாநிலம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'gu', 'રાજ્ય', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'ur', 'ریاست', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'kn', 'ರಾಜ್ಯ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('State', 'ml', 'സംസ്ഥാനം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'en', 'Select State', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'hi', 'राज्य चुनें', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'bn', 'রাজ্য নির্বাচন করুন', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'mr', 'राज्य निवडा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'te', 'రాష్ట్రాన్ని ఎంచుకోండి', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'ta', 'மாநிலத்தைத் தேர்ந்தெடுக்கவும்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'gu', 'રાજ્ય પસંદ કરો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'ur', 'ریاست منتخب کریں', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'kn', 'ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Select State', 'ml', 'സംസ്ഥാനം തിരഞ്ഞെടുക്കുക', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'en', 'Quick State', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'hi', 'त्वरित राज्य', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'bn', 'দ্রুত রাজ্য', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'mr', 'जलद राज्य', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'te', 'శీఘ్ర రాష్ట్రం', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'ta', 'விரைவு மாநிலம்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'gu', 'ઝડપી રાજ્ય', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'ur', 'فوری ریاست', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'kn', 'ತ್ವರಿತ ರಾಜ್ಯ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Quick State', 'ml', 'ദ്രുത സംസ്ഥാനം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'en', 'Mayor', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'hi', 'महापौर (मेयर)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'bn', 'মেয়র', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'mr', 'महापौर', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'te', 'మేయర్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'ta', 'மேயர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'gu', 'મેયર', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'ur', 'میئر', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'kn', 'ಮೇಯರ್', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Mayor', 'ml', 'മേയർ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'en', 'President', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'hi', 'नगराध्यक्ष (अध्यक्ष)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'bn', 'পৌরপ্রধান (সভাপতি)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'mr', 'नगराध्यक्ष', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'te', 'కౌన్సిల్ అధ్యక్షుడు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'ta', 'நகர்மன்றத் தலைவர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'gu', 'નગરાધ્યક્ષ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'ur', 'صدر بلدیہ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'kn', 'ನಗರಾಧ್ಯಕ್ಷರು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('President', 'ml', 'നഗരസഭാ അധ്യക്ഷൻ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'en', 'Councillor', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'hi', 'पार्षद', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'bn', 'কাউন্সিলর', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'mr', 'नगरसेवक', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'te', 'కౌన్సిలర్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'ta', 'மன்ற உறுப்பினர்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'gu', 'કાઉન્સિલર', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'ur', 'کونسلر', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'kn', 'ಕೌನ್ಸಿಲರ್', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Councillor', 'ml', 'കൗൺസിലർ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'en', 'Majority Mark', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'hi', 'बहुमत का आंकड़ा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'bn', 'সংখ্যাগরিষ্ঠতার মাত্রা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'mr', 'बहुमत रेषा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'te', 'మెజారిటీ మార్క్', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'ta', 'பெரும்பான்மை எல்லை', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'gu', 'બહુમતી આંકડો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'ur', 'اکثریتی ہدف', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'kn', 'ಬಹುಮತದ ಗಡಿ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Majority Mark', 'ml', 'ഭൂരിപക്ഷ പരിധി', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'en', 'Historical Comparison', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'hi', 'ऐतिहासिक तुलना', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'bn', 'ঐতিহাসিক তুলনা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'mr', 'ऐतिहासिक तुलना', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'te', 'చారిత్రక పోలిక', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'ta', 'வரலாற்று ஒப்பீடு', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'gu', 'ઐતિહાસિક સરખામણી', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'ur', 'تاریخی موازنہ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'kn', 'ಐತಿಹಾಸಿಕ ಹೋಲಿಕೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Historical Comparison', 'ml', 'ചരിത്രപരമായ താരതമ്യം', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'en', 'Urban Population', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'hi', 'शहरी आबादी', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'bn', 'শহুরে জনসংখ্যা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'mr', 'शहरी लोकसंख्या', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'te', 'పట్టణ జనాభా', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'ta', 'நகர்ப்புற மக்கள் தொகை', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'gu', 'શહેરી વસ્તી', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'ur', 'شہری آبادی', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'kn', 'ನಗರ ಜನಸಂಖ್ಯೆ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Urban Population', 'ml', 'നഗര ജനസംഖ്യ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'en', 'Wards', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'hi', 'वार्ड', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'bn', 'ওয়ার্ড', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'mr', 'प्रभाग (वॉर्ड)', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'te', 'వార్డులు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'ta', 'வார்டுகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'gu', 'વોર્ડ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'ur', 'وارڈز', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'kn', 'ವಾರ್ಡ್‌ಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Wards', 'ml', 'വാർഡുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'en', 'Seats Won', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'hi', 'जीती सीटें', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'bn', 'প্রাপ্ত আসন', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'mr', 'जिंकलेल्या जागा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'te', 'గెలిచిన స్థానాలు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'ta', 'வென்ற இடங்கள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'gu', 'જીતેલી બેઠકો', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'ur', 'جیتی گئی نشستیں', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'kn', 'ಗೆದ್ದ ಸ್ಥಾನಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('Seats Won', 'ml', 'ജയിച്ച സീറ്റുകൾ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'en', 'All Municipal Corporations', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'hi', 'सभी नगर निगम', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'bn', 'সমস্ত পৌর নিগম', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'mr', 'सर्व महानगरपालिका', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'te', 'అన్ని మున్సిపల్ కార్పొరేషన్లు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'ta', 'அனைத்து மாநகராட்சிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'gu', 'તમામ મ્યુનિસિપલ કોર્પોરેશન', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'ur', 'تمام میونسپل کارپوریشنز', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'kn', 'ಎಲ್ಲಾ ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Corporations', 'ml', 'എല്ലാ മുനിസിപ്പൽ കോർപ്പറേഷനുകളും', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'en', 'All Municipal Councils', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'hi', 'सभी नगर परिषद', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'bn', 'সমস্ত পৌরসভা', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'mr', 'सर्व नगरपरिषदा', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'te', 'అన్ని మున్సిపల్ కౌన్సిళ్లు', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'ta', 'அனைத்து நகராட்சிகள்', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'gu', 'તમામ નગર પાલિકાઓ', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'ur', 'تمام میونسپل کونسلز', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'kn', 'ಎಲ್ಲಾ ಪುರಸಭೆಗಳು', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;
INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('All Municipal Councils', 'ml', 'എല്ലാ മുനിസിപ്പൽ കൗൺസിലുകളും', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;