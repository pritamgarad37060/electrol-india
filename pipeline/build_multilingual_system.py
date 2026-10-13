import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

# ══════════════════════════════════════════════════════════════════════
# 1. Ten Supported Languages Metadata & Rich UI Dictionary
# ══════════════════════════════════════════════════════════════════════

LANGUAGES = [
    {"code": "en", "name": "English", "native_name": "English", "is_default": True, "text_direction": "ltr"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "is_default": False, "text_direction": "ltr"},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "is_default": False, "text_direction": "ltr"},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी", "is_default": False, "text_direction": "ltr"},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "is_default": False, "text_direction": "ltr"},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "is_default": False, "text_direction": "ltr"},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી", "is_default": False, "text_direction": "ltr"},
    {"code": "ur", "name": "Urdu", "native_name": "اردو", "is_default": False, "text_direction": "rtl"},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ", "is_default": False, "text_direction": "ltr"},
    {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം", "is_default": False, "text_direction": "ltr"}
]

# Core UI Translation Catalog across all 10 languages
# Format: key: {lang_code: translated_string}
TRANSLATIONS = {
    "Home": {
        "hi": "होम", "bn": "হোম", "mr": "मुख्यपृष्ठ", "te": "హోమ్", "ta": "முகப்பு",
        "gu": "હોમ", "ur": "ہوم", "kn": "ಮುಖಪುಟ", "ml": "ഹോം"
    },
    "Lok Sabha": {
        "hi": "लोकसभा", "bn": "লোকসভা", "mr": "लोकसभा", "te": "లోక్‌సభ", "ta": "மக்களவை",
        "gu": "લોકસભા", "ur": "لوک سبھا", "kn": "ಲೋಕಸಭೆ", "ml": "ലോക്സഭ"
    },
    "Lok Sabha 2024": {
        "hi": "लोकसभा 2024", "bn": "লোকসভা ২০২৪", "mr": "लोकसभा २०२४", "te": "లోక్‌సభ 2024", "ta": "மக்களவை 2024",
        "gu": "લોકસભા ૨૦૨૪", "ur": "لوک سبھا 2024", "kn": "ಲೋಕಸಭೆ 2024", "ml": "ലോക്സഭ 2024"
    },
    "Lok Sabha MPs": {
        "hi": "लोकसभा सांसद", "bn": "লোকসভার সাংসদ", "mr": "लोकसभा खासदार", "te": "లోక్‌సభ ఎంపీలు", "ta": "மக்களவை எம்.பி.க்கள்",
        "gu": "લોકસભા સાંસદો", "ur": "لوک سبھا ارکان پارلیمنٹ", "kn": "ಲೋಕಸಭಾ ಸಂಸದರು", "ml": "ലോക്സഭാ എം.പിമാർ"
    },
    "Maharashtra": {
        "hi": "महाराष्ट्र", "bn": "মহারাষ্ট্র", "mr": "महाराष्ट्र", "te": "మహారాష్ట్ర", "ta": "மகாராஷ்டிரா",
        "gu": "મહારાષ્ટ્ર", "ur": "مہاراشٹر", "kn": "ಮಹಾರಾಷ್ಟ್ರ", "ml": "മഹാരാഷ്ട്ര"
    },
    "Municipal Corporations": {
        "hi": "नगर निगम (महानगर पालिका)", "bn": "পৌর নিগম (মহানগর পালিকা)", "mr": "महानगरपालिका", "te": "మున్సిపల్ కార్పొరేషన్లు", "ta": "மாநகராட்சிகள்",
        "gu": "મ્યુનિસિપલ કોર્પોરેશન", "ur": "میونسپل کارپوریشنز", "kn": "ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು", "ml": "മുനിസിപ്പൽ കോർപ്പറേഷനുകൾ"
    },
    "Municipal Councils": {
        "hi": "नगर परिषद (नगर पालिका)", "bn": "পৌরসভা (নগর পরিষদ)", "mr": "नगरपरिषदा", "te": "మున్సిపల్ కౌన్సిళ్లు", "ta": "நகராட்சிகள்",
        "gu": "નગર પાલિકાઓ", "ur": "میونسپل کونسلز", "kn": "ಪುರಸಭೆಗಳು", "ml": "മുനിസിപ്പൽ കൗൺസിലുകൾ"
    },
    "All Assemblies": {
        "hi": "सभी विधानसभाएं", "bn": "সমস্ত বিধানসভা", "mr": "सर्व विधानसभा", "te": "అన్ని అసెంబ్లీలు", "ta": "அனைத்து சட்டசபைகள்",
        "gu": "તમામ વિધાનસભાઓ", "ur": "تمام اسمبلیاں", "kn": "ಎಲ್ಲಾ ವಿಧಾನಸಭೆಗಳು", "ml": "എല്ലാ നിയമസഭകളും"
    },
    "Women": {
        "hi": "महिलाएं", "bn": "নারী", "mr": "महिला", "te": "మహిళలు", "ta": "மகளிர்",
        "gu": "મહિલાઓ", "ur": "خواتین", "kn": "ಮಹಿಳೆಯರು", "ml": "വനിതകൾ"
    },
    "Map": {
        "hi": "नक्शा", "bn": "মানচিত্র", "mr": "नकाशा", "te": "మ్యాప్", "ta": "வரைபடம்",
        "gu": "નકશો", "ur": "نقشہ", "kn": "ನಕ್ಷೆ", "ml": "ഭൂപടം"
    },
    "Constituencies": {
        "hi": "निर्वाचन क्षेत्र", "bn": "নির্বাচনী এলাকা", "mr": "मतदारसंघ", "te": "నియోజకవర్గాలు", "ta": "தொகுதிகள்",
        "gu": "મતવિસ્તારો", "ur": "انتخابی حلقے", "kn": "ಕ್ಷೇತ್ರಗಳು", "ml": "മണ്ഡലങ്ങൾ"
    },
    "Compare": {
        "hi": "तुलना", "bn": "তুলনা", "mr": "तुलना", "te": "పోల్చు", "ta": "ஒப்பிடு",
        "gu": "સરખામણી", "ur": "موازنہ", "kn": "ಹೋಲಿಕೆ", "ml": "താരതമ്യം"
    },
    "Parties": {
        "hi": "पार्टियाँ", "bn": "দলসমূহ", "mr": "पक्ष", "te": "పార్టీలు", "ta": "கட்சிகள்",
        "gu": "પક્ષો", "ur": "جماعتیں", "kn": "ಪಕ್ಷಗಳು", "ml": "പാർട്ടികൾ"
    },
    "Statistics": {
        "hi": "आँकड़े", "bn": "পরিসংখ্যান", "mr": "आकडेवारी", "te": "గణాంకాలు", "ta": "புள்ளிவிவரங்கள்",
        "gu": "આંકડાકીય માહિતી", "ur": "شماریات", "kn": "ಅಂಕಿಅಂಶಗಳು", "ml": "സ്ഥിതിവിവരക്കണക്കുകൾ"
    },
    "Search seat / candidate…": {
        "hi": "सीट / उम्मीदवार खोजें…", "bn": "আসন / প্রার্থী খুঁজুন…", "mr": "जागा / उमेदवार शोधा…", "te": "సీటు / అభ్యర్థిని వెతకండి…", "ta": "தொகுதி / வேட்பாளர் தேடுக…",
        "gu": "બેઠક / ઉમેદવાર શોધો…", "ur": "نشست / امیدوار تلاش کریں…", "kn": "ಕ್ಷೇತ್ರ / ಅಭ್ಯರ್ಥಿಯನ್ನು ಹುಡುಕಿ…", "ml": "സീറ്റ് / സ്ഥാനാർത്ഥിയെ തിരയുക…"
    },
    "Civic Governance": {
        "hi": "नागरिक शासन", "bn": "পৌর প্রশাসন", "mr": "नागरी प्रशासन", "te": "పౌర పాలన", "ta": "குடிமை நிர்வாகம்",
        "gu": "નાગરિક શાસન", "ur": "شہری نظم و نسق", "kn": "ನಾಗರಿಕ ಆಡಳಿತ", "ml": "നഗര ഭരണം"
    },
    "Total Seats": {
        "hi": "कुल सीटें", "bn": "মোট আসন", "mr": "एकूण जागा", "te": "మొత్తం స్థానాలు", "ta": "மொத்த இடங்கள்",
        "gu": "કુલ બેઠકો", "ur": "کل نشستیں", "kn": "ಒಟ್ಟು ಸ್ಥಾನಗಳು", "ml": "ആകെ സീറ്റുകൾ"
    },
    "Results": {
        "hi": "परिणाम", "bn": "ফলাফল", "mr": "निकाल", "te": "ఫలితాలు", "ta": "முடிவுகள்",
        "gu": "પરિણામો", "ur": "نتائج", "kn": "ಫಲಿತಾಂಶಗಳು", "ml": "ഫലങ്ങൾ"
    },
    "Winner": {
        "hi": "विजेता", "bn": "বিজয়ী", "mr": "विजयी", "te": "విజేత", "ta": "வெற்றியாளர்",
        "gu": "વિજેતા", "ur": "فاتح", "kn": "ವಿಜೇತ", "ml": "വിജയി"
    },
    "Runner-up": {
        "hi": "उपविजेता", "bn": "রানার-আপ", "mr": "उपविजेता", "te": "రన్నరప్", "ta": "இரண்டாமிடம்",
        "gu": "રનર-અપ", "ur": "دوسرے نمبر پر", "kn": "ದ್ವಿತೀಯ ಸ್ಥಾನಿ", "ml": "രണ്ടാം സ്ഥാനം"
    },
    "Votes": {
        "hi": "वोट", "bn": "ভোট", "mr": "मते", "te": "ఓట్లు", "ta": "வாக்குகள்",
        "gu": "મતો", "ur": "ووٹ", "kn": "ಮತಗಳು", "ml": "വോട്ടുകൾ"
    },
    "Margin": {
        "hi": "जीत का अंतर", "bn": "ব্যবধান", "mr": "मताधिक्य", "te": "మెజారిటీ", "ta": "வாக்கு வித்தியாസം",
        "gu": "તફાવત", "ur": "مارجن", "kn": "ಅಂತರ", "ml": "ഭൂരിപക്ഷം"
    },
    "Turnout": {
        "hi": "मतदान %", "bn": "ভোটদানের হার", "mr": "मतदान %", "te": "ఓటింగ్ శాతం", "ta": "வாக்குப்பதிவு %",
        "gu": "મતદાન %", "ur": "ٹرن آؤٹ %", "kn": "ಮತದಾನ %", "ml": "പോളിംഗ് ശതമാനം"
    },
    "Candidate": {
        "hi": "उम्मीदवार", "bn": "প্রার্থী", "mr": "उमेदवार", "te": "అభ్యర్థి", "ta": "வேட்பாளர்",
        "gu": "ઉમેદવાર", "ur": "امیدوار", "kn": "ಅಭ್ಯರ್ಥಿ", "ml": "സ്ഥാനാർത്ഥി"
    },
    "Party": {
        "hi": "पार्टी", "bn": "দল", "mr": "पक्ष", "te": "పార్టీ", "ta": "கட்சி",
        "gu": "પક્ષ", "ur": "جماعت", "kn": "ಪಕ್ಷ", "ml": "പാർട്ടി"
    },
    "District": {
        "hi": "जिला", "bn": "জেলা", "mr": "जिल्हा", "te": "జిల్లా", "ta": "மாவட்டம்",
        "gu": "જિલ્લો", "ur": "ضلع", "kn": "ಜಿಲ್ಲೆ", "ml": "ജില്ല"
    },
    "State": {
        "hi": "राज्य", "bn": "রাজ্য", "mr": "राज्य", "te": "రాష్ట్రం", "ta": "மாநிலம்",
        "gu": "રાજ્ય", "ur": "ریاست", "kn": "ರಾಜ್ಯ", "ml": "സംസ്ഥാനം"
    },
    "Select State": {
        "hi": "राज्य चुनें", "bn": "রাজ্য নির্বাচন করুন", "mr": "राज्य निवडा", "te": "రాష్ట్రాన్ని ఎంచుకోండి", "ta": "மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
        "gu": "રાજ્ય પસંદ કરો", "ur": "ریاست منتخب کریں", "kn": "ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ", "ml": "സംസ്ഥാനം തിരഞ്ഞെടുക്കുക"
    },
    "Quick State": {
        "hi": "त्वरित राज्य", "bn": "দ্রুত রাজ্য", "mr": "जलद राज्य", "te": "శీఘ్ర రాష్ట్రం", "ta": "விரைவு மாநிலம்",
        "gu": "ઝડપી રાજ્ય", "ur": "فوری ریاست", "kn": "ತ್ವರಿತ ರಾಜ್ಯ", "ml": "ദ്രുത സംസ്ഥാനം"
    },
    "Mayor": {
        "hi": "महापौर (मेयर)", "bn": "মেয়র", "mr": "महापौर", "te": "మేయర్", "ta": "மேயர்",
        "gu": "મેયર", "ur": "میئر", "kn": "ಮೇಯರ್", "ml": "മേയർ"
    },
    "President": {
        "hi": "नगराध्यक्ष (अध्यक्ष)", "bn": "পৌরপ্রধান (সভাপতি)", "mr": "नगराध्यक्ष", "te": "కౌన్సిల్ అధ్యక్షుడు", "ta": "நகர்மன்றத் தலைவர்",
        "gu": "નગરાધ્યક્ષ", "ur": "صدر بلدیہ", "kn": "ನಗರಾಧ್ಯಕ್ಷರು", "ml": "നഗരസഭാ അധ്യക്ഷൻ"
    },
    "Councillor": {
        "hi": "पार्षद", "bn": "কাউন্সিলর", "mr": "नगरसेवक", "te": "కౌన్సిలర్", "ta": "மன்ற உறுப்பினர்",
        "gu": "કાઉન્સિલર", "ur": "کونسلر", "kn": "ಕೌನ್ಸಿಲರ್", "ml": "കൗൺസിലർ"
    },
    "Majority Mark": {
        "hi": "बहुमत का आंकड़ा", "bn": "সংখ্যাগরিষ্ঠতার মাত্রা", "mr": "बहुमत रेषा", "te": "మెజారిటీ మార్క్", "ta": "பெரும்பான்மை எல்லை",
        "gu": "બહુમતી આંકડો", "ur": "اکثریتی ہدف", "kn": "ಬಹುಮತದ ಗಡಿ", "ml": "ഭൂരിപക്ഷ പരിധി"
    },
    "Historical Comparison": {
        "hi": "ऐतिहासिक तुलना", "bn": "ঐতিহাসিক তুলনা", "mr": "ऐतिहासिक तुलना", "te": "చారిత్రక పోలిక", "ta": "வரலாற்று ஒப்பீடு",
        "gu": "ઐતિહાસિક સરખામણી", "ur": "تاریخی موازنہ", "kn": "ಐತಿಹಾಸಿಕ ಹೋಲಿಕೆ", "ml": "ചരിത്രപരമായ താരതമ്യം"
    },
    "Urban Population": {
        "hi": "शहरी आबादी", "bn": "শহুরে জনসংখ্যা", "mr": "शहरी लोकसंख्या", "te": "పట్టణ జనాభా", "ta": "நகர்ப்புற மக்கள் தொகை",
        "gu": "શહેરી વસ્તી", "ur": "شہری آبادی", "kn": "ನಗರ ಜನಸಂಖ್ಯೆ", "ml": "നഗര ജനസംഖ്യ"
    },
    "Wards": {
        "hi": "वार्ड", "bn": "ওয়ার্ড", "mr": "प्रभाग (वॉर्ड)", "te": "వార్డులు", "ta": "வார்டுகள்",
        "gu": "વોર્ડ", "ur": "وارڈز", "kn": "ವಾರ್ಡ್‌ಗಳು", "ml": "വാർഡുകൾ"
    },
    "Seats Won": {
        "hi": "जीती सीटें", "bn": "প্রাপ্ত আসন", "mr": "जिंकलेल्या जागा", "te": "గెలిచిన స్థానాలు", "ta": "வென்ற இடங்கள்",
        "gu": "જીતેલી બેઠકો", "ur": "جیتی گئی نشستیں", "kn": "ಗೆದ್ದ ಸ್ಥಾನಗಳು", "ml": "ജയിച്ച സീറ്റുകൾ"
    },
    "All Municipal Corporations": {
        "hi": "सभी नगर निगम", "bn": "সমস্ত পৌর নিগম", "mr": "सर्व महानगरपालिका", "te": "అన్ని మున్సిపల్ కార్పొరేషన్లు", "ta": "அனைத்து மாநகராட்சிகள்",
        "gu": "તમામ મ્યુનિસિપલ કોર્પોરેશન", "ur": "تمام میونسپل کارپوریشنز", "kn": "ಎಲ್ಲಾ ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು", "ml": "എല്ലാ മുനിസിപ്പൽ കോർപ്പറേഷനുകളും"
    },
    "All Municipal Councils": {
        "hi": "सभी नगर परिषद", "bn": "সমস্ত পৌরসভা", "mr": "सर्व नगरपरिषदा", "te": "అన్ని మున్సిపల్ కౌన్సిళ్లు", "ta": "அனைத்து நகராட்சிகள்",
        "gu": "તમામ નગર પાલિકાઓ", "ur": "تمام میونسپل کونسلز", "kn": "ಎಲ್ಲಾ ಪುರಸಭೆಗಳು", "ml": "എല്ലാ മുനിസിപ്പൽ കൗൺസിലുകളും"
    }
}

# ══════════════════════════════════════════════════════════════════════
# 2. Generate supabase_multilingual_schema.sql
# ══════════════════════════════════════════════════════════════════════

sql_lines = [
    "-- =====================================================================",
    "-- ELECTORAL INDIA: CENTRALIZED MULTILINGUAL SYSTEM (SUPABASE POSTGRES)",
    "-- 10 Official Languages: en, hi, bn, mr, te, ta, gu, ur (RTL), kn, ml",
    "-- Production Ready | RLS Protected | High-Speed Catalog Functions",
    "-- =====================================================================\n",
    "-- 1. LANGUAGES TABLE",
    """CREATE TABLE IF NOT EXISTS languages (
  code VARCHAR(10) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  native_name VARCHAR(100) NOT NULL,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  text_direction VARCHAR(3) NOT NULL DEFAULT 'ltr' CHECK (text_direction IN ('ltr', 'rtl')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);""",
    "\n-- 2. UI TRANSLATIONS TABLE",
    """CREATE TABLE IF NOT EXISTS ui_translations (
  id BIGSERIAL PRIMARY KEY,
  translation_key VARCHAR(150) NOT NULL,
  language_code VARCHAR(10) NOT NULL REFERENCES languages(code) ON DELETE CASCADE,
  translated_text TEXT NOT NULL,
  translation_status VARCHAR(20) NOT NULL DEFAULT 'published' CHECK (translation_status IN ('draft', 'reviewed', 'published')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_by VARCHAR(100) DEFAULT 'system',
  CONSTRAINT uq_translation_key_lang UNIQUE (translation_key, language_code)
);""",
    "\n-- 3. CONTENT TRANSLATIONS TABLE (For Candidates, Parties, Wards, Assemblies)",
    """CREATE TABLE IF NOT EXISTS content_translations (
  id BIGSERIAL PRIMARY KEY,
  content_type VARCHAR(50) NOT NULL, -- 'candidate', 'party', 'constituency', 'local_body', 'election'
  entity_id VARCHAR(100) NOT NULL,
  field_name VARCHAR(50) NOT NULL,   -- 'name', 'bio', 'description', 'title'
  language_code VARCHAR(10) NOT NULL REFERENCES languages(code) ON DELETE CASCADE,
  translated_text TEXT NOT NULL,
  translation_status VARCHAR(20) NOT NULL DEFAULT 'published' CHECK (translation_status IN ('draft', 'reviewed', 'published')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_content_translation UNIQUE (content_type, entity_id, field_name, language_code)
);""",
    "\n-- 4. PERFORMANCE INDEXES",
    "CREATE INDEX IF NOT EXISTS idx_ui_trans_lang ON ui_translations(language_code);",
    "CREATE INDEX IF NOT EXISTS idx_ui_trans_key ON ui_translations(translation_key);",
    "CREATE INDEX IF NOT EXISTS idx_ui_trans_lookup ON ui_translations(language_code, translation_status);",
    "CREATE INDEX IF NOT EXISTS idx_content_trans_lookup ON content_translations(content_type, entity_id, language_code);",
    "\n-- 5. ROW LEVEL SECURITY (RLS) POLICIES",
    "ALTER TABLE languages ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE ui_translations ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE content_translations ENABLE ROW LEVEL SECURITY;",
    "\n-- Public read access for visitors",
    """DROP POLICY IF EXISTS "Allow public read access to enabled languages" ON languages;
CREATE POLICY "Allow public read access to enabled languages" ON languages
  FOR SELECT USING (is_enabled = true);""",
    """DROP POLICY IF EXISTS "Allow public read access to published UI translations" ON ui_translations;
CREATE POLICY "Allow public read access to published UI translations" ON ui_translations
  FOR SELECT USING (translation_status = 'published');""",
    """DROP POLICY IF EXISTS "Allow public read access to published content translations" ON content_translations;
CREATE POLICY "Allow public read access to published content translations" ON content_translations
  FOR SELECT USING (translation_status = 'published');""",
    "\n-- 6. RPC FUNCTION: GET FAST LANGUAGE CATALOG IN ONE JSON CALL",
    """CREATE OR REPLACE FUNCTION get_language_catalog(p_lang_code VARCHAR(10))
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
$$;""",
    "\n-- 7. SEED DATA: 10 SUPPORTED LANGUAGES",
]

# Insert languages
for l in LANGUAGES:
    is_def = "TRUE" if l["is_default"] else "FALSE"
    sql_lines.append(f"""INSERT INTO languages (code, name, native_name, is_enabled, is_default, text_direction)
VALUES ('{l["code"]}', '{l["name"]}', '{l["native_name"]}', TRUE, {is_def}, '{l["text_direction"]}')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, native_name = EXCLUDED.native_name, text_direction = EXCLUDED.text_direction, updated_at = NOW();""")

sql_lines.append("\n-- 8. SEED DATA: UI TRANSLATIONS (CATALOG)")

# Insert translations
for key, trans_dict in TRANSLATIONS.items():
    # Insert English key itself
    safe_key = key.replace("'", "''")
    sql_lines.append(f"""INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('{safe_key}', 'en', '{safe_key}', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;""")
    
    # Insert other languages
    for lang, val in trans_dict.items():
        safe_val = val.replace("'", "''")
        sql_lines.append(f"""INSERT INTO ui_translations (translation_key, language_code, translated_text, translation_status)
VALUES ('{safe_key}', '{lang}', '{safe_val}', 'published')
ON CONFLICT (translation_key, language_code) DO UPDATE SET translated_text = EXCLUDED.translated_text;""")

with open('supabase_multilingual_schema.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated supabase_multilingual_schema.sql with {len(sql_lines)} lines.")

# ══════════════════════════════════════════════════════════════════════
# 3. Update js/i18n.js with all 10 languages + Urdu RTL + Supabase sync
# ══════════════════════════════════════════════════════════════════════

# Read current i18n.js to extract patterns and existing maps
with open('js/i18n.js', 'r', encoding='utf-8') as f:
    existing_i18n = f.read()

# Build comprehensive dictionary objects
catalogs_json = {}
for lang in ['hi', 'bn', 'mr', 'te', 'ta', 'gu', 'ur', 'kn', 'ml']:
    catalogs_json[lang] = {}
    for key, trans_dict in TRANSLATIONS.items():
        if lang in trans_dict:
            catalogs_json[lang][key] = trans_dict[lang]

# Generate enhanced js/i18n.js
i18n_js_content = f"""/* Electrol India — Complete Multilingual Engine v4.0
 * 10 Official Languages: en, hi, bn, mr, te, ta, gu, ur (RTL), kn, ml
 * Backed by Supabase PostgreSQL centralized catalog with offline/local fallback.
 */

window.LANG = 'en';
window.SUPPORTED_LANGUAGES = {json.dumps(LANGUAGES, ensure_ascii=False, indent=2)};

window.I18N = (function() {{
  const en = {{}};

  const hi = Object.assign({{}}, {json.dumps(catalogs_json['hi'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 सीटें · पूरे नतीजे",
    "Lok Sabha Election 2024": "लोकसभा चुनाव 2024",
    "18th Lok Sabha": "18वीं लोकसभा",
    "Results Declared": "घोषित नतीजे",
    "Electors (542 PCs)": "मतदाता (542 सीटें)",
    "Votes Polled": "पड़े वोट",
    "Winning party (seats)": "विजयी पार्टी (सीटें)",
    "NOTA": "नोटा",
    "Clear filters": "फ़िल्टर हटाएँ",
    "maharashtra": "महाराष्ट्र", "andhra pradesh": "आंध्र प्रदेश", "gujarat": "गुजरात",
    "karnataka": "कर्नाटक", "tamil nadu": "तमिलनाडु", "delhi (nct)": "दिल्ली", "uttar pradesh": "उत्तर प्रदेश"
  }});

  const bn = Object.assign({{}}, {json.dumps(catalogs_json['bn'], ensure_ascii=False)}, {{
    "543 seats · full results": "৫৪৩ আসন · সম্পূর্ণ ফলাফল",
    "Lok Sabha Election 2024": "লোকসভা নির্বাচন ২০২৪",
    "Results Declared": "ঘোষিত ফলাফল",
    "Electors": "ভোটার",
    "Votes Polled": "গৃহীত ভোট",
    "NOTA": "নোটা",
    "Clear filters": "ফিল্টার মুছুন",
    "maharashtra": "মহারাষ্ট্র", "west bengal": "পশ্চিমবঙ্গ", "assam": "আসাম", "bihar": "বিহার"
  }});

  const mr = Object.assign({{}}, {json.dumps(catalogs_json['mr'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 जागा · संपूर्ण निकाल",
    "Lok Sabha Election 2024": "लोकसभा निवडणूक 2024",
    "18th Lok Sabha": "18वी लोकसभा",
    "Results Declared": "जाहीर निकाल",
    "Electors": "मतदार",
    "NOTA": "नोटा",
    "Clear filters": "फिल्टर काढा",
    "Mahayuti": "महायुती", "MVA": "महाविकास आघाडी",
    "maharashtra": "महाराष्ट्र", "gujarat": "गुजरात", "karnataka": "कर्नाटक"
  }});

  const te = Object.assign({{}}, {json.dumps(catalogs_json['te'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 స్థానాలు · పూర్తి ఫలితాలు",
    "Lok Sabha Election 2024": "లోక్‌సభ ఎన్నికలు 2024",
    "Results Declared": "ప్రకటించిన ఫలితాలు",
    "Electors": "ఓటర్లు",
    "NOTA": "నోటా",
    "Clear filters": "ఫిల్టర్లను క్లియర్ చేయండి",
    "andhra pradesh": "ఆంధ్రప్రదేశ్", "telangana": "తెలంగాణ", "maharashtra": "మహారాష్ట్ర"
  }});

  const ta = Object.assign({{}}, {json.dumps(catalogs_json['ta'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 தொகுதிகள் · முழு முடிவுகள்",
    "Lok Sabha Election 2024": "மக்களவை தேர்தல் 2024",
    "Results Declared": "அறிவிக்கப்பட்ட முடிவுகள்",
    "Electors": "வாக்காளர்கள்",
    "NOTA": "நோட்டா",
    "Clear filters": "வடிகட்டிகளை அழிக்கவும்",
    "tamil nadu": "தமிழ்நாடு", "kerala": "கேரளா", "karnataka": "கர்நாடகா", "maharashtra": "மகாராஷ்டிரா"
  }});

  const gu = Object.assign({{}}, {json.dumps(catalogs_json['gu'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 બેઠકો · સંપૂર્ણ પરિણામો",
    "Lok Sabha Election 2024": "લોકસભા ચૂંટણી 2024",
    "Results Declared": "જાહેર પરિણામો",
    "Electors": "મતદારો",
    "NOTA": "નોટા",
    "Clear filters": "ફિલ્ટર દૂર કરો",
    "gujarat": "ગુજરાત", "maharashtra": "મહારાષ્ટ્ર", "rajasthan": "રાજસ્થાન"
  }});

  const ur = Object.assign({{}}, {json.dumps(catalogs_json['ur'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 نشستیں · مکمل نتائج",
    "Lok Sabha Election 2024": "لوک سبھا انتخابات 2024",
    "18th Lok Sabha": "18 ویں لوک سبھا",
    "Results Declared": "اعلان کردہ نتائج",
    "Electors": "ووٹرز",
    "NOTA": "نوٹا",
    "Clear filters": "فلٹرز صاف کریں",
    "maharashtra": "مہاراشٹر", "uttar pradesh": "اتر پردیش", "delhi (nct)": "دہلی", "bihar": "بہار"
  }});

  const kn = Object.assign({{}}, {json.dumps(catalogs_json['kn'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 ಕ್ಷೇತ್ರಗಳು · ಸಂಪೂರ್ಣ ಫಲಿತಾಂಶಗಳು",
    "Lok Sabha Election 2024": "ಲೋಕಸಭಾ ಚುನಾವಣೆ 2024",
    "Results Declared": "ಘೋಷಿತ ಫಲಿತಾಂಶಗಳು",
    "Electors": "ಮತದಾರರು",
    "NOTA": "ನೋಟಾ",
    "Clear filters": "ಫಿಲ್ಟರ್ ತೆರವುಗೊಳಿಸಿ",
    "karnataka": "ಕರ್ನಾಟಕ", "maharashtra": "ಮಹಾರಾಷ್ಟ್ರ", "tamil nadu": "ತಮಿಳುನಾಡು"
  }});

  const ml = Object.assign({{}}, {json.dumps(catalogs_json['ml'], ensure_ascii=False)}, {{
    "543 seats · full results": "543 മണ്ഡലങ്ങൾ · പൂർണ്ണ ഫലങ്ങൾ",
    "Lok Sabha Election 2024": "ലോക്സഭാ തിരഞ്ഞെടുപ്പ് 2024",
    "Results Declared": "പ്രഖ്യാപിച്ച ഫലങ്ങൾ",
    "Electors": "വോട്ടർമാർ",
    "NOTA": "നോട്ട",
    "Clear filters": "ഫിൽട്ടറുകൾ നീക്കുക",
    "kerala": "കേരളം", "tamil nadu": "തമിഴ്നാട്", "karnataka": "കർണാടക", "maharashtra": "മഹാരാഷ്ട്ര"
  }});

  return {{
    en, hi, bn, mr, te, ta, gu, ur, kn, ml,
    p: [
      ["^([\\\\d,]+) constituencies$", "$1 निर्वाचन क्षेत्र", "$1 নির্বাচনী এলাকা", "$1 मतदारसंघ", "$1 నియోజకవర్గాలు", "$1 தொகுதிகள்", "$1 મતવિસ્તારો", "$1 انتخابی حلقے", "$1 ಕ್ಷೇತ್ರಗಳು", "$1 മണ്ഡലങ്ങൾ"],
      ["^(\\d+) seats$", "$1 सीटें", "$1 আসন", "$1 जागा", "$1 స్థానాలు", "$1 இடங்கள்", "$1 બેઠકો", "$1 نشستیں", "$1 ಸ್ಥಾನಗಳು", "$1 സീറ്റുകൾ"],
      ["^Ward (\\\\d+)$", "वार्ड $1", "ওয়ার্ড $1", "प्रभाग $1", "వార్డు $1", "வார்டு $1", "વોર્ડ $1", "وارڈ $1", "ವಾರ್ಡ್ $1", "വാർഡ് $1"]
    ]
  }};
}})();

/* ─── Unified Translation Service & Runtime ───────────────────────── */
window.setLang = function(lang) {{
  window.LANG = lang || 'en';
  try {{
    localStorage.setItem('lang', window.LANG);
    localStorage.setItem('lg', window.LANG);
  }} catch(e) {{}}

  const el = document.getElementById('lg');
  if (el && el.value !== window.LANG) el.value = window.LANG;

  // Language & Direction Management (Urdu RTL support)
  const isRTL = (window.LANG === 'ur');
  document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
  document.documentElement.setAttribute('lang', window.LANG);

  if (isRTL) {{
    document.documentElement.classList.add('rtl-mode');
  }} else {{
    document.documentElement.classList.remove('rtl-mode');
  }}

  // Attempt background sync from Supabase if online
  syncSupabaseTranslations(window.LANG);

  // Run DOM translation
  translatePage();
  if (typeof render === 'function') render();
}};

window.t = function(key) {{
  if (!key || window.LANG === 'en') return key;
  const dict = window.I18N && window.I18N[window.LANG];
  if (!dict) return key;
  if (dict[key]) return dict[key];

  const lk = key.toLowerCase();
  if (dict[lk]) return dict[lk];

  // Regex patterns
  const patterns = (window.I18N && window.I18N.p) || [];
  const langIndex = ['hi', 'bn', 'mr', 'te', 'ta', 'gu', 'ur', 'kn', 'ml'].indexOf(window.LANG);
  if (langIndex >= 0) {{
    for (const p of patterns) {{
      const re = new RegExp(p[0]);
      const m = key.match(re);
      if (m && p[langIndex + 1]) {{
        let r = p[langIndex + 1];
        m.slice(1).forEach((g, i) => r = r.replace('$' + (i + 1), g));
        return r;
      }}
    }}
  }}

  return key;
}};

window.translatePage = function(rootEl) {{
  const el = rootEl || document.body;
  if (!el) return;

  // 1. Data-i18n attributes
  el.querySelectorAll('[data-i18n]').forEach(e => {{
    const k = e.getAttribute('data-i18n');
    const v = window.t(k);
    if (v && v !== k) e.textContent = v;
  }});

  // 2. Form controls & accessibility attributes
  el.querySelectorAll('[placeholder], [aria-label], [title]').forEach(e => {{
    ['placeholder', 'aria-label', 'title'].forEach(a => {{
      if (e.hasAttribute(a)) {{
        const k = '_o_' + a;
        if (e[k] === undefined) e[k] = e.getAttribute(a);
        const trans = window.t(e[k]);
        if (trans && trans !== e[k]) e.setAttribute(a, trans);
      }}
    }});
  }});

  // 3. TreeWalker text nodes (selective & fast)
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = [];
  let curr;
  while (curr = walker.nextNode()) {{
    const p = curr.parentElement;
    if (p && !['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(p.tagName)) {{
      nodes.push(curr);
    }}
  }}

  for (const n of nodes) {{
    const val = (n.nodeValue || '').trim();
    if (!val || /^[\\d.,\\s%#№+-]+$/.test(val)) continue;
    if (n._orig === undefined) n._orig = n.nodeValue;

    if (window.LANG === 'en') {{
      if (n.nodeValue !== n._orig) n.nodeValue = n._orig;
    }} else {{
      const trText = window.t(val);
      if (trText && trText !== val) {{
        n.nodeValue = n.nodeValue.replace(val, trText);
      }}
    }}
  }}
}};

// Background Supabase Translation Sync with localStorage Cache
function syncSupabaseTranslations(lang) {{
  if (!lang || lang === 'en') return;
  try {{
    // Check local storage cached catalog version
    const cacheKey = 'electoral_india_i18n_' + lang;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {{
      const data = JSON.parse(cached);
      if (data && typeof data === 'object') {{
        Object.assign(window.I18N[lang], data);
      }}
    }}

    // If online & Supabase client available, fetch published translations
    if (window.supabase && typeof window.supabase.from === 'function') {{
      window.supabase
        .from('ui_translations')
        .select('translation_key, translated_text')
        .eq('language_code', lang)
        .eq('translation_status', 'published')
        .then(res => {{
          if (res.data && res.data.length) {{
            const remoteMap = {{}};
            res.data.forEach(r => remoteMap[r.translation_key] = r.translated_text);
            Object.assign(window.I18N[lang], remoteMap);
            localStorage.setItem(cacheKey, JSON.stringify(remoteMap));
            translatePage();
          }}
        }}).catch(() => {{}});
    }}
  }} catch(e) {{}}
}}

// Initialize language from saved preference or browser setting
(function() {{
  try {{
    let saved = localStorage.getItem('lang') || localStorage.getItem('lg');
    if (!saved) {{
      const navLangs = navigator.languages || [navigator.language || 'en'];
      for (const nl of navLangs) {{
        const c = nl.slice(0, 2).toLowerCase();
        if (['en','hi','bn','mr','te','ta','gu','ur','kn','ml'].includes(c)) {{
          saved = c;
          break;
        }}
      }}
    }}
    saved = saved || 'en';
    window.LANG = saved;
    const el = document.getElementById('lg');
    if (el) el.value = saved;
    const isRTL = (saved === 'ur');
    document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', saved);
  }} catch(e) {{}}
}})();
"""

with open('js/i18n.js', 'w', encoding='utf-8') as f:
    f.write(i18n_js_content)
print("Updated js/i18n.js with 10 languages + Urdu RTL + Supabase sync.")

# ══════════════════════════════════════════════════════════════════════
# 4. Update index.html Language Selector <select id="lg">
# ══════════════════════════════════════════════════════════════════════
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_select_lg = r'''      <select id="lg" aria-label="Select Language" onchange="setLang(this.value)">
        <option value="en">English</option>
        <option value="hi">हिन्दी</option>
        <option value="mr">मराठी</option>
        <option value="te">తెలుగు</option>
        <option value="ta">தமிழ்</option>
        <option value="bn">বাংলা</option>
        <option value="kn">ಕನ್ನಡ</option>
        <option value="gu">ગુજરાતી</option>
        <option value="pa">ਪੰਜਾਬੀ</option>
        <option value="ml">മലയാളം</option>
        <option value="or">ଓଡ଼ିଆ</option>
      </select>'''

new_select_lg = r'''      <select id="lg" aria-label="Select Language" onchange="setLang(this.value)">
        <option value="en">English</option>
        <option value="hi">हिन्दी</option>
        <option value="bn">বাংলা</option>
        <option value="mr">मराठी</option>
        <option value="te">తెలుగు</option>
        <option value="ta">தமிழ்</option>
        <option value="gu">ગુજરાતી</option>
        <option value="ur">اردو</option>
        <option value="kn">ಕನ್ನಡ</option>
        <option value="ml">മലയാളം</option>
      </select>'''

if old_select_lg in html:
    html = html.replace(old_select_lg, new_select_lg)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html language selector with 10 supported languages.")
else:
    # Try normalizing newlines
    old_norm = old_select_lg.replace('\r\n', '\n')
    html_norm = html.replace('\r\n', '\n')
    if old_norm in html_norm:
        html = html_norm.replace(old_norm, new_select_lg)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Updated index.html language selector (normalized newlines).")
    else:
        print("Warning: old_select_lg not matched in index.html.")

print("Multilingual System build complete!")
