/* Electrol India — Complete Multilingual Engine v4.0
 * 10 Official Languages: en, hi, bn, mr, te, ta, gu, ur (RTL), kn, ml
 * Backed by Supabase PostgreSQL centralized catalog with offline/local fallback.
 */

window.LANG = 'en';
window.SUPPORTED_LANGUAGES = [
  {
    "code": "en",
    "name": "English",
    "native_name": "English",
    "is_default": true,
    "text_direction": "ltr"
  },
  {
    "code": "hi",
    "name": "Hindi",
    "native_name": "हिन्दी",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "bn",
    "name": "Bengali",
    "native_name": "বাংলা",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "mr",
    "name": "Marathi",
    "native_name": "मराठी",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "te",
    "name": "Telugu",
    "native_name": "తెలుగు",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "ta",
    "name": "Tamil",
    "native_name": "தமிழ்",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "gu",
    "name": "Gujarati",
    "native_name": "ગુજરાતી",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "ur",
    "name": "Urdu",
    "native_name": "اردو",
    "is_default": false,
    "text_direction": "rtl"
  },
  {
    "code": "kn",
    "name": "Kannada",
    "native_name": "ಕನ್ನಡ",
    "is_default": false,
    "text_direction": "ltr"
  },
  {
    "code": "ml",
    "name": "Malayalam",
    "native_name": "മലയാളം",
    "is_default": false,
    "text_direction": "ltr"
  }
];

window.I18N = (function() {
  const en = {};

  const hi = Object.assign({}, {"Home": "होम", "Lok Sabha": "लोकसभा", "Lok Sabha 2024": "लोकसभा 2024", "Lok Sabha MPs": "लोकसभा सांसद", "Maharashtra": "महाराष्ट्र", "Municipal Corporations": "नगर निगम (महानगर पालिका)", "Municipal Councils": "नगर परिषद (नगर पालिका)", "All Assemblies": "सभी विधानसभाएं", "Women": "महिलाएं", "Map": "नक्शा", "Constituencies": "निर्वाचन क्षेत्र", "Compare": "तुलना", "Parties": "पार्टियाँ", "Statistics": "आँकड़े", "Search seat / candidate…": "सीट / उम्मीदवार खोजें…", "Civic Governance": "नागरिक शासन", "Total Seats": "कुल सीटें", "Results": "परिणाम", "Winner": "विजेता", "Runner-up": "उपविजेता", "Votes": "वोट", "Margin": "जीत का अंतर", "Turnout": "मतदान %", "Candidate": "उम्मीदवार", "Party": "पार्टी", "District": "जिला", "State": "राज्य", "Select State": "राज्य चुनें", "Quick State": "त्वरित राज्य", "Mayor": "महापौर (मेयर)", "President": "नगराध्यक्ष (अध्यक्ष)", "Councillor": "पार्षद", "Majority Mark": "बहुमत का आंकड़ा", "Historical Comparison": "ऐतिहासिक तुलना", "Urban Population": "शहरी आबादी", "Wards": "वार्ड", "Seats Won": "जीती सीटें", "All Municipal Corporations": "सभी नगर निगम", "All Municipal Councils": "सभी नगर परिषद"}, {
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
  });

  const bn = Object.assign({}, {"Home": "হোম", "Lok Sabha": "লোকসভা", "Lok Sabha 2024": "লোকসভা ২০২৪", "Lok Sabha MPs": "লোকসভার সাংসদ", "Maharashtra": "মহারাষ্ট্র", "Municipal Corporations": "পৌর নিগম (মহানগর পালিকা)", "Municipal Councils": "পৌরসভা (নগর পরিষদ)", "All Assemblies": "সমস্ত বিধানসভা", "Women": "নারী", "Map": "মানচিত্র", "Constituencies": "নির্বাচনী এলাকা", "Compare": "তুলনা", "Parties": "দলসমূহ", "Statistics": "পরিসংখ্যান", "Search seat / candidate…": "আসন / প্রার্থী খুঁজুন…", "Civic Governance": "পৌর প্রশাসন", "Total Seats": "মোট আসন", "Results": "ফলাফল", "Winner": "বিজয়ী", "Runner-up": "রানার-আপ", "Votes": "ভোট", "Margin": "ব্যবধান", "Turnout": "ভোটদানের হার", "Candidate": "প্রার্থী", "Party": "দল", "District": "জেলা", "State": "রাজ্য", "Select State": "রাজ্য নির্বাচন করুন", "Quick State": "দ্রুত রাজ্য", "Mayor": "মেয়র", "President": "পৌরপ্রধান (সভাপতি)", "Councillor": "কাউন্সিলর", "Majority Mark": "সংখ্যাগরিষ্ঠতার মাত্রা", "Historical Comparison": "ঐতিহাসিক তুলনা", "Urban Population": "শহুরে জনসংখ্যা", "Wards": "ওয়ার্ড", "Seats Won": "প্রাপ্ত আসন", "All Municipal Corporations": "সমস্ত পৌর নিগম", "All Municipal Councils": "সমস্ত পৌরসভা"}, {
    "543 seats · full results": "৫৪৩ আসন · সম্পূর্ণ ফলাফল",
    "Lok Sabha Election 2024": "লোকসভা নির্বাচন ২০২৪",
    "Results Declared": "ঘোষিত ফলাফল",
    "Electors": "ভোটার",
    "Votes Polled": "গৃহীত ভোট",
    "NOTA": "নোটা",
    "Clear filters": "ফিল্টার মুছুন",
    "maharashtra": "মহারাষ্ট্র", "west bengal": "পশ্চিমবঙ্গ", "assam": "আসাম", "bihar": "বিহার"
  });

  const mr = Object.assign({}, {"Home": "मुख्यपृष्ठ", "Lok Sabha": "लोकसभा", "Lok Sabha 2024": "लोकसभा २०२४", "Lok Sabha MPs": "लोकसभा खासदार", "Maharashtra": "महाराष्ट्र", "Municipal Corporations": "महानगरपालिका", "Municipal Councils": "नगरपरिषदा", "All Assemblies": "सर्व विधानसभा", "Women": "महिला", "Map": "नकाशा", "Constituencies": "मतदारसंघ", "Compare": "तुलना", "Parties": "पक्ष", "Statistics": "आकडेवारी", "Search seat / candidate…": "जागा / उमेदवार शोधा…", "Civic Governance": "नागरी प्रशासन", "Total Seats": "एकूण जागा", "Results": "निकाल", "Winner": "विजयी", "Runner-up": "उपविजेता", "Votes": "मते", "Margin": "मताधिक्य", "Turnout": "मतदान %", "Candidate": "उमेदवार", "Party": "पक्ष", "District": "जिल्हा", "State": "राज्य", "Select State": "राज्य निवडा", "Quick State": "जलद राज्य", "Mayor": "महापौर", "President": "नगराध्यक्ष", "Councillor": "नगरसेवक", "Majority Mark": "बहुमत रेषा", "Historical Comparison": "ऐतिहासिक तुलना", "Urban Population": "शहरी लोकसंख्या", "Wards": "प्रभाग (वॉर्ड)", "Seats Won": "जिंकलेल्या जागा", "All Municipal Corporations": "सर्व महानगरपालिका", "All Municipal Councils": "सर्व नगरपरिषदा"}, {
    "543 seats · full results": "543 जागा · संपूर्ण निकाल",
    "Lok Sabha Election 2024": "लोकसभा निवडणूक 2024",
    "18th Lok Sabha": "18वी लोकसभा",
    "Results Declared": "जाहीर निकाल",
    "Electors": "मतदार",
    "NOTA": "नोटा",
    "Clear filters": "फिल्टर काढा",
    "Mahayuti": "महायुती", "MVA": "महाविकास आघाडी",
    "maharashtra": "महाराष्ट्र", "gujarat": "गुजरात", "karnataka": "कर्नाटक"
  });

  const te = Object.assign({}, {"Home": "హోమ్", "Lok Sabha": "లోక్‌సభ", "Lok Sabha 2024": "లోక్‌సభ 2024", "Lok Sabha MPs": "లోక్‌సభ ఎంపీలు", "Maharashtra": "మహారాష్ట్ర", "Municipal Corporations": "మున్సిపల్ కార్పొరేషన్లు", "Municipal Councils": "మున్సిపల్ కౌన్సిళ్లు", "All Assemblies": "అన్ని అసెంబ్లీలు", "Women": "మహిళలు", "Map": "మ్యాప్", "Constituencies": "నియోజకవర్గాలు", "Compare": "పోల్చు", "Parties": "పార్టీలు", "Statistics": "గణాంకాలు", "Search seat / candidate…": "సీటు / అభ్యర్థిని వెతకండి…", "Civic Governance": "పౌర పాలన", "Total Seats": "మొత్తం స్థానాలు", "Results": "ఫలితాలు", "Winner": "విజేత", "Runner-up": "రన్నరప్", "Votes": "ఓట్లు", "Margin": "మెజారిటీ", "Turnout": "ఓటింగ్ శాతం", "Candidate": "అభ్యర్థి", "Party": "పార్టీ", "District": "జిల్లా", "State": "రాష్ట్రం", "Select State": "రాష్ట్రాన్ని ఎంచుకోండి", "Quick State": "శీఘ్ర రాష్ట్రం", "Mayor": "మేయర్", "President": "కౌన్సిల్ అధ్యక్షుడు", "Councillor": "కౌన్సిలర్", "Majority Mark": "మెజారిటీ మార్క్", "Historical Comparison": "చారిత్రక పోలిక", "Urban Population": "పట్టణ జనాభా", "Wards": "వార్డులు", "Seats Won": "గెలిచిన స్థానాలు", "All Municipal Corporations": "అన్ని మున్సిపల్ కార్పొరేషన్లు", "All Municipal Councils": "అన్ని మున్సిపల్ కౌన్సిళ్లు"}, {
    "543 seats · full results": "543 స్థానాలు · పూర్తి ఫలితాలు",
    "Lok Sabha Election 2024": "లోక్‌సభ ఎన్నికలు 2024",
    "Results Declared": "ప్రకటించిన ఫలితాలు",
    "Electors": "ఓటర్లు",
    "NOTA": "నోటా",
    "Clear filters": "ఫిల్టర్లను క్లియర్ చేయండి",
    "andhra pradesh": "ఆంధ్రప్రదేశ్", "telangana": "తెలంగాణ", "maharashtra": "మహారాష్ట్ర"
  });

  const ta = Object.assign({}, {"Home": "முகப்பு", "Lok Sabha": "மக்களவை", "Lok Sabha 2024": "மக்களவை 2024", "Lok Sabha MPs": "மக்களவை எம்.பி.க்கள்", "Maharashtra": "மகாராஷ்டிரா", "Municipal Corporations": "மாநகராட்சிகள்", "Municipal Councils": "நகராட்சிகள்", "All Assemblies": "அனைத்து சட்டசபைகள்", "Women": "மகளிர்", "Map": "வரைபடம்", "Constituencies": "தொகுதிகள்", "Compare": "ஒப்பிடு", "Parties": "கட்சிகள்", "Statistics": "புள்ளிவிவரங்கள்", "Search seat / candidate…": "தொகுதி / வேட்பாளர் தேடுக…", "Civic Governance": "குடிமை நிர்வாகம்", "Total Seats": "மொத்த இடங்கள்", "Results": "முடிவுகள்", "Winner": "வெற்றியாளர்", "Runner-up": "இரண்டாமிடம்", "Votes": "வாக்குகள்", "Margin": "வாக்கு வித்தியாസം", "Turnout": "வாக்குப்பதிவு %", "Candidate": "வேட்பாளர்", "Party": "கட்சி", "District": "மாவட்டம்", "State": "மாநிலம்", "Select State": "மாநிலத்தைத் தேர்ந்தெடுக்கவும்", "Quick State": "விரைவு மாநிலம்", "Mayor": "மேயர்", "President": "நகர்மன்றத் தலைவர்", "Councillor": "மன்ற உறுப்பினர்", "Majority Mark": "பெரும்பான்மை எல்லை", "Historical Comparison": "வரலாற்று ஒப்பீடு", "Urban Population": "நகர்ப்புற மக்கள் தொகை", "Wards": "வார்டுகள்", "Seats Won": "வென்ற இடங்கள்", "All Municipal Corporations": "அனைத்து மாநகராட்சிகள்", "All Municipal Councils": "அனைத்து நகராட்சிகள்"}, {
    "543 seats · full results": "543 தொகுதிகள் · முழு முடிவுகள்",
    "Lok Sabha Election 2024": "மக்களவை தேர்தல் 2024",
    "Results Declared": "அறிவிக்கப்பட்ட முடிவுகள்",
    "Electors": "வாக்காளர்கள்",
    "NOTA": "நோட்டா",
    "Clear filters": "வடிகட்டிகளை அழிக்கவும்",
    "tamil nadu": "தமிழ்நாடு", "kerala": "கேரளா", "karnataka": "கர்நாடகா", "maharashtra": "மகாராஷ்டிரா"
  });

  const gu = Object.assign({}, {"Home": "હોમ", "Lok Sabha": "લોકસભા", "Lok Sabha 2024": "લોકસભા ૨૦૨૪", "Lok Sabha MPs": "લોકસભા સાંસદો", "Maharashtra": "મહારાષ્ટ્ર", "Municipal Corporations": "મ્યુનિસિપલ કોર્પોરેશન", "Municipal Councils": "નગર પાલિકાઓ", "All Assemblies": "તમામ વિધાનસભાઓ", "Women": "મહિલાઓ", "Map": "નકશો", "Constituencies": "મતવિસ્તારો", "Compare": "સરખામણી", "Parties": "પક્ષો", "Statistics": "આંકડાકીય માહિતી", "Search seat / candidate…": "બેઠક / ઉમેદવાર શોધો…", "Civic Governance": "નાગરિક શાસન", "Total Seats": "કુલ બેઠકો", "Results": "પરિણામો", "Winner": "વિજેતા", "Runner-up": "રનર-અપ", "Votes": "મતો", "Margin": "તફાવત", "Turnout": "મતદાન %", "Candidate": "ઉમેદવાર", "Party": "પક્ષ", "District": "જિલ્લો", "State": "રાજ્ય", "Select State": "રાજ્ય પસંદ કરો", "Quick State": "ઝડપી રાજ્ય", "Mayor": "મેયર", "President": "નગરાધ્યક્ષ", "Councillor": "કાઉન્સિલર", "Majority Mark": "બહુમતી આંકડો", "Historical Comparison": "ઐતિહાસિક સરખામણી", "Urban Population": "શહેરી વસ્તી", "Wards": "વોર્ડ", "Seats Won": "જીતેલી બેઠકો", "All Municipal Corporations": "તમામ મ્યુનિસિપલ કોર્પોરેશન", "All Municipal Councils": "તમામ નગર પાલિકાઓ"}, {
    "543 seats · full results": "543 બેઠકો · સંપૂર્ણ પરિણામો",
    "Lok Sabha Election 2024": "લોકસભા ચૂંટણી 2024",
    "Results Declared": "જાહેર પરિણામો",
    "Electors": "મતદારો",
    "NOTA": "નોટા",
    "Clear filters": "ફિલ્ટર દૂર કરો",
    "gujarat": "ગુજરાત", "maharashtra": "મહારાષ્ટ્ર", "rajasthan": "રાજસ્થાન"
  });

  const ur = Object.assign({}, {"Home": "ہوم", "Lok Sabha": "لوک سبھا", "Lok Sabha 2024": "لوک سبھا 2024", "Lok Sabha MPs": "لوک سبھا ارکان پارلیمنٹ", "Maharashtra": "مہاراشٹر", "Municipal Corporations": "میونسپل کارپوریشنز", "Municipal Councils": "میونسپل کونسلز", "All Assemblies": "تمام اسمبلیاں", "Women": "خواتین", "Map": "نقشہ", "Constituencies": "انتخابی حلقے", "Compare": "موازنہ", "Parties": "جماعتیں", "Statistics": "شماریات", "Search seat / candidate…": "نشست / امیدوار تلاش کریں…", "Civic Governance": "شہری نظم و نسق", "Total Seats": "کل نشستیں", "Results": "نتائج", "Winner": "فاتح", "Runner-up": "دوسرے نمبر پر", "Votes": "ووٹ", "Margin": "مارجن", "Turnout": "ٹرن آؤٹ %", "Candidate": "امیدوار", "Party": "جماعت", "District": "ضلع", "State": "ریاست", "Select State": "ریاست منتخب کریں", "Quick State": "فوری ریاست", "Mayor": "میئر", "President": "صدر بلدیہ", "Councillor": "کونسلر", "Majority Mark": "اکثریتی ہدف", "Historical Comparison": "تاریخی موازنہ", "Urban Population": "شہری آبادی", "Wards": "وارڈز", "Seats Won": "جیتی گئی نشستیں", "All Municipal Corporations": "تمام میونسپل کارپوریشنز", "All Municipal Councils": "تمام میونسپل کونسلز"}, {
    "543 seats · full results": "543 نشستیں · مکمل نتائج",
    "Lok Sabha Election 2024": "لوک سبھا انتخابات 2024",
    "18th Lok Sabha": "18 ویں لوک سبھا",
    "Results Declared": "اعلان کردہ نتائج",
    "Electors": "ووٹرز",
    "NOTA": "نوٹا",
    "Clear filters": "فلٹرز صاف کریں",
    "maharashtra": "مہاراشٹر", "uttar pradesh": "اتر پردیش", "delhi (nct)": "دہلی", "bihar": "بہار"
  });

  const kn = Object.assign({}, {"Home": "ಮುಖಪುಟ", "Lok Sabha": "ಲೋಕಸಭೆ", "Lok Sabha 2024": "ಲೋಕಸಭೆ 2024", "Lok Sabha MPs": "ಲೋಕಸಭಾ ಸಂಸದರು", "Maharashtra": "ಮಹಾರಾಷ್ಟ್ರ", "Municipal Corporations": "ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು", "Municipal Councils": "ಪುರಸಭೆಗಳು", "All Assemblies": "ಎಲ್ಲಾ ವಿಧಾನಸಭೆಗಳು", "Women": "ಮಹಿಳೆಯರು", "Map": "ನಕ್ಷೆ", "Constituencies": "ಕ್ಷೇತ್ರಗಳು", "Compare": "ಹೋಲಿಕೆ", "Parties": "ಪಕ್ಷಗಳು", "Statistics": "ಅಂಕಿಅಂಶಗಳು", "Search seat / candidate…": "ಕ್ಷೇತ್ರ / ಅಭ್ಯರ್ಥಿಯನ್ನು ಹುಡುಕಿ…", "Civic Governance": "ನಾಗರಿಕ ಆಡಳಿತ", "Total Seats": "ಒಟ್ಟು ಸ್ಥಾನಗಳು", "Results": "ಫಲಿತಾಂಶಗಳು", "Winner": "ವಿಜೇತ", "Runner-up": "ದ್ವಿತೀಯ ಸ್ಥಾನಿ", "Votes": "ಮತಗಳು", "Margin": "ಅಂತರ", "Turnout": "ಮತದಾನ %", "Candidate": "ಅಭ್ಯರ್ಥಿ", "Party": "ಪಕ್ಷ", "District": "ಜಿಲ್ಲೆ", "State": "ರಾಜ್ಯ", "Select State": "ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ", "Quick State": "ತ್ವರಿತ ರಾಜ್ಯ", "Mayor": "ಮೇಯರ್", "President": "ನಗರಾಧ್ಯಕ್ಷರು", "Councillor": "ಕೌನ್ಸಿಲರ್", "Majority Mark": "ಬಹುಮತದ ಗಡಿ", "Historical Comparison": "ಐತಿಹಾಸಿಕ ಹೋಲಿಕೆ", "Urban Population": "ನಗರ ಜನಸಂಖ್ಯೆ", "Wards": "ವಾರ್ಡ್‌ಗಳು", "Seats Won": "ಗೆದ್ದ ಸ್ಥಾನಗಳು", "All Municipal Corporations": "ಎಲ್ಲಾ ಮಹಾನಗರ ಪಾಲಿಕೆಗಳು", "All Municipal Councils": "ಎಲ್ಲಾ ಪುರಸಭೆಗಳು"}, {
    "543 seats · full results": "543 ಕ್ಷೇತ್ರಗಳು · ಸಂಪೂರ್ಣ ಫಲಿತಾಂಶಗಳು",
    "Lok Sabha Election 2024": "ಲೋಕಸಭಾ ಚುನಾವಣೆ 2024",
    "Results Declared": "ಘೋಷಿತ ಫಲಿತಾಂಶಗಳು",
    "Electors": "ಮತದಾರರು",
    "NOTA": "ನೋಟಾ",
    "Clear filters": "ಫಿಲ್ಟರ್ ತೆರವುಗೊಳಿಸಿ",
    "karnataka": "ಕರ್ನಾಟಕ", "maharashtra": "ಮಹಾರಾಷ್ಟ್ರ", "tamil nadu": "ತಮಿಳುನಾಡು"
  });

  const ml = Object.assign({}, {"Home": "ഹോം", "Lok Sabha": "ലോക്സഭ", "Lok Sabha 2024": "ലോക്സഭ 2024", "Lok Sabha MPs": "ലോക്സഭാ എം.പിമാർ", "Maharashtra": "മഹാരാഷ്ട്ര", "Municipal Corporations": "മുനിസിപ്പൽ കോർപ്പറേഷനുകൾ", "Municipal Councils": "മുനിസിപ്പൽ കൗൺസിലുകൾ", "All Assemblies": "എല്ലാ നിയമസഭകളും", "Women": "വനിതകൾ", "Map": "ഭൂപടം", "Constituencies": "മണ്ഡലങ്ങൾ", "Compare": "താരതമ്യം", "Parties": "പാർട്ടികൾ", "Statistics": "സ്ഥിതിവിവരക്കണക്കുകൾ", "Search seat / candidate…": "സീറ്റ് / സ്ഥാനാർത്ഥിയെ തിരയുക…", "Civic Governance": "നഗര ഭരണം", "Total Seats": "ആകെ സീറ്റുകൾ", "Results": "ഫലങ്ങൾ", "Winner": "വിജയി", "Runner-up": "രണ്ടാം സ്ഥാനം", "Votes": "വോട്ടുകൾ", "Margin": "ഭൂരിപക്ഷം", "Turnout": "പോളിംഗ് ശതമാനം", "Candidate": "സ്ഥാനാർത്ഥി", "Party": "പാർട്ടി", "District": "ജില്ല", "State": "സംസ്ഥാനം", "Select State": "സംസ്ഥാനം തിരഞ്ഞെടുക്കുക", "Quick State": "ദ്രുത സംസ്ഥാനം", "Mayor": "മേയർ", "President": "നഗരസഭാ അധ്യക്ഷൻ", "Councillor": "കൗൺസിലർ", "Majority Mark": "ഭൂരിപക്ഷ പരിധി", "Historical Comparison": "ചരിത്രപരമായ താരതമ്യം", "Urban Population": "നഗര ജനസംഖ്യ", "Wards": "വാർഡുകൾ", "Seats Won": "ജയിച്ച സീറ്റുകൾ", "All Municipal Corporations": "എല്ലാ മുനിസിപ്പൽ കോർപ്പറേഷനുകളും", "All Municipal Councils": "എല്ലാ മുനിസിപ്പൽ കൗൺസിലുകളും"}, {
    "543 seats · full results": "543 മണ്ഡലങ്ങൾ · പൂർണ്ണ ഫലങ്ങൾ",
    "Lok Sabha Election 2024": "ലോക്സഭാ തിരഞ്ഞെടുപ്പ് 2024",
    "Results Declared": "പ്രഖ്യാപിച്ച ഫലങ്ങൾ",
    "Electors": "വോട്ടർമാർ",
    "NOTA": "നോട്ട",
    "Clear filters": "ഫിൽട്ടറുകൾ നീക്കുക",
    "kerala": "കേരളം", "tamil nadu": "തമിഴ്നാട്", "karnataka": "കർണാടക", "maharashtra": "മഹാരാഷ്ട്ര"
  });

  return {
    en, hi, bn, mr, te, ta, gu, ur, kn, ml,
    p: [
      ["^([\\d,]+) constituencies$", "$1 निर्वाचन क्षेत्र", "$1 নির্বাচনী এলাকা", "$1 मतदारसंघ", "$1 నియోజకవర్గాలు", "$1 தொகுதிகள்", "$1 મતવિસ્તારો", "$1 انتخابی حلقے", "$1 ಕ್ಷೇತ್ರಗಳು", "$1 മണ്ഡലങ്ങൾ"],
      ["^(\d+) seats$", "$1 सीटें", "$1 আসন", "$1 जागा", "$1 స్థానాలు", "$1 இடங்கள்", "$1 બેઠકો", "$1 نشستیں", "$1 ಸ್ಥಾನಗಳು", "$1 സീറ്റുകൾ"],
      ["^Ward (\\d+)$", "वार्ड $1", "ওয়ার্ড $1", "प्रभाग $1", "వార్డు $1", "வார்டு $1", "વોર્ડ $1", "وارڈ $1", "ವಾರ್ಡ್ $1", "വാർഡ് $1"]
    ]
  };
})();

/* ─── Unified Translation Service & Runtime ───────────────────────── */
window.setLang = function(lang) {
  window.LANG = lang || 'en';
  try {
    localStorage.setItem('lang', window.LANG);
    localStorage.setItem('lg', window.LANG);
  } catch(e) {}

  const el = document.getElementById('lg');
  if (el && el.value !== window.LANG) el.value = window.LANG;

  // Language & Direction Management (Urdu RTL support)
  const isRTL = (window.LANG === 'ur');
  document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
  document.documentElement.setAttribute('lang', window.LANG);

  if (isRTL) {
    document.documentElement.classList.add('rtl-mode');
  } else {
    document.documentElement.classList.remove('rtl-mode');
  }

  // Attempt background sync from Supabase if online
  syncSupabaseTranslations(window.LANG);

  // Run DOM translation
  translatePage();
  if (typeof render === 'function') render();
};

window.t = function(key) {
  if (!key || window.LANG === 'en') return key;
  const dict = window.I18N && window.I18N[window.LANG];
  if (!dict) return key;
  if (dict[key]) return dict[key];

  const lk = key.toLowerCase();
  if (dict[lk]) return dict[lk];

  // Regex patterns
  const patterns = (window.I18N && window.I18N.p) || [];
  const langIndex = ['hi', 'bn', 'mr', 'te', 'ta', 'gu', 'ur', 'kn', 'ml'].indexOf(window.LANG);
  if (langIndex >= 0) {
    for (const p of patterns) {
      const re = new RegExp(p[0]);
      const m = key.match(re);
      if (m && p[langIndex + 1]) {
        let r = p[langIndex + 1];
        m.slice(1).forEach((g, i) => r = r.replace('$' + (i + 1), g));
        return r;
      }
    }
  }

  return key;
};

window.translatePage = function(rootEl) {
  const el = rootEl || document.body;
  if (!el) return;

  // 1. Data-i18n attributes
  el.querySelectorAll('[data-i18n]').forEach(e => {
    const k = e.getAttribute('data-i18n');
    const v = window.t(k);
    if (v && v !== k) e.textContent = v;
  });

  // 2. Form controls & accessibility attributes
  el.querySelectorAll('[placeholder], [aria-label], [title]').forEach(e => {
    ['placeholder', 'aria-label', 'title'].forEach(a => {
      if (e.hasAttribute(a)) {
        const k = '_o_' + a;
        if (e[k] === undefined) e[k] = e.getAttribute(a);
        const trans = window.t(e[k]);
        if (trans && trans !== e[k]) e.setAttribute(a, trans);
      }
    });
  });

  // 3. TreeWalker text nodes (selective & fast)
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = [];
  let curr;
  while (curr = walker.nextNode()) {
    const p = curr.parentElement;
    if (p && !['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(p.tagName)) {
      nodes.push(curr);
    }
  }

  for (const n of nodes) {
    const val = (n.nodeValue || '').trim();
    if (!val || /^[\d.,\s%#№+-]+$/.test(val)) continue;
    if (n._orig === undefined) n._orig = n.nodeValue;

    if (window.LANG === 'en') {
      if (n.nodeValue !== n._orig) n.nodeValue = n._orig;
    } else {
      const trText = window.t(val);
      if (trText && trText !== val) {
        n.nodeValue = n.nodeValue.replace(val, trText);
      }
    }
  }
};

// Background Supabase Translation Sync with localStorage Cache
function syncSupabaseTranslations(lang) {
  if (!lang || lang === 'en') return;
  try {
    // Check local storage cached catalog version
    const cacheKey = 'electoral_india_i18n_' + lang;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const data = JSON.parse(cached);
      if (data && typeof data === 'object') {
        Object.assign(window.I18N[lang], data);
      }
    }

    // If online & Supabase client available, fetch published translations
    if (window.supabase && typeof window.supabase.from === 'function') {
      window.supabase
        .from('ui_translations')
        .select('translation_key, translated_text')
        .eq('language_code', lang)
        .eq('translation_status', 'published')
        .then(res => {
          if (res.data && res.data.length) {
            const remoteMap = {};
            res.data.forEach(r => remoteMap[r.translation_key] = r.translated_text);
            Object.assign(window.I18N[lang], remoteMap);
            localStorage.setItem(cacheKey, JSON.stringify(remoteMap));
            translatePage();
          }
        }).catch(() => {});
    }
  } catch(e) {}
}

// Initialize language from saved preference or browser setting
(function() {
  try {
    let saved = localStorage.getItem('lang') || localStorage.getItem('lg');
    if (!saved) {
      const navLangs = navigator.languages || [navigator.language || 'en'];
      for (const nl of navLangs) {
        const c = nl.slice(0, 2).toLowerCase();
        if (['en','hi','bn','mr','te','ta','gu','ur','kn','ml'].includes(c)) {
          saved = c;
          break;
        }
      }
    }
    saved = saved || 'en';
    window.LANG = saved;
    const el = document.getElementById('lg');
    if (el) el.value = saved;
    const isRTL = (saved === 'ur');
    document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', saved);
  } catch(e) {}
})();
