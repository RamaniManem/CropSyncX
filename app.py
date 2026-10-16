import random
import uuid
from datetime import datetime
from io import BytesIO
import html

import pandas as pd
import streamlit as st
import qrcode
from PIL import Image
import streamlit.components.v1 as components



st.set_page_config(
    page_title="CropSyncX | Smart Farm-to-Consumer",
    page_icon="🌾",
    layout="wide",
)

# ---------- Demo configuration ----------
CROP_GUIDE = {
    "Tomato": {"temp_min": 10.0, "temp_max": 13.0, "humidity_min": 85, "humidity_max": 95, "price": 30},
    "Potato": {"temp_min": 4.0, "temp_max": 8.0, "humidity_min": 90, "humidity_max": 95, "price": 25},
    "Onion": {"temp_min": 0.0, "temp_max": 4.0, "humidity_min": 65, "humidity_max": 75, "price": 28},
    "Mango": {"temp_min": 10.0, "temp_max": 13.0, "humidity_min": 85, "humidity_max": 90, "price": 60},
    "Rice": {"temp_min": 15.0, "temp_max": 25.0, "humidity_min": 50, "humidity_max": 65, "price": 35},
    "Chilli": {"temp_min": 5.0, "temp_max": 10.0, "humidity_min": 60, "humidity_max": 70, "price": 80},
}

# India's 22 scheduled languages. Voice playback uses the browser/device speech engine;
# available voices vary by device and browser. The prototype keeps profiles in session state.
LANGUAGES = {
    "English": ("en-IN", "Welcome to CropSyncX. Use the menu to monitor your field, check smart storage, sell your crops, and view your crop passport."),
    "हिन्दी (Hindi)": ("hi-IN", "CropSyncX में आपका स्वागत है। खेत की जानकारी देखें, भंडारण की स्थिति जाँचें, फसल बेचें और फसल पासपोर्ट देखें।"),
    "বাংলা (Bengali)": ("bn-IN", "CropSyncX-এ স্বাগতম। জমির তথ্য দেখুন, সংরক্ষণের অবস্থা পরীক্ষা করুন, ফসল বিক্রি করুন এবং ফসল পাসপোর্ট দেখুন।"),
    "తెలుగు (Telugu)": ("te-IN", "క్రాప్‌సింక్స్‌కు స్వాగతం. మీ పొలాన్ని చూడండి, నిల్వ పరిస్థితులను తనిఖీ చేయండి, పంటలను అమ్మండి, పంట పాస్‌పోర్ట్‌ను చూడండి."),
    "मराठी (Marathi)": ("mr-IN", "क्रॉपसिंकएक्समध्ये आपले स्वागत आहे. शेताची माहिती पाहा, साठवण तपासा, पीक विक्री करा आणि पीक पासपोर्ट पाहा."),
    "தமிழ் (Tamil)": ("ta-IN", "கிராப்சிங்க்ஸ் செயலிக்கு வரவேற்கிறோம். வயல் தகவலைப் பாருங்கள், சேமிப்பு நிலையைச் சரிபாருங்கள், பயிர்களை விற்று பயிர் பாஸ்போர்ட்டைப் பாருங்கள்."),
    "ગુજરાતી (Gujarati)": ("gu-IN", "CropSyncX-க்கு வரவேற்கிறோம். வயல் தகவலைப் பாருங்கள், சேமிப்பைச் சரிபாருங்கள், பயிர்களை விற்று பயிர் பாஸ்போர்ட்டைப் பாருங்கள்."),
    "ಕನ್ನಡ (Kannada)": ("kn-IN", "ಕ್ರಾಪ್‌ಸಿಂಕ್‌ಎಕ್ಸ್‌ಗೆ ಸ್ವಾಗತ. ಹೊಲದ ಮಾಹಿತಿಯನ್ನು ನೋಡಿ, ಸಂಗ್ರಹಣೆಯನ್ನು ಪರಿಶೀಲಿಸಿ, ಬೆಳೆಗಳನ್ನು ಮಾರಾಟ ಮಾಡಿ ಮತ್ತು ಬೆಳೆ ಪಾಸ್‌ಪೋರ್ಟ್ ನೋಡಿ."),
    "മലയാളം (Malayalam)": ("ml-IN", "CropSyncX-ലേക്ക് സ്വാഗതം. വയൽ വിവരങ്ങൾ കാണുക, സംഭരണം പരിശോധിക്കുക, വിളകൾ വിൽക്കുക, വിള പാസ്‌പോർട്ട് കാണുക."),
    "ਪੰਜਾਬੀ (Punjabi)": ("pa-IN", "CropSyncX ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ। ਖੇਤ ਦੀ ਜਾਣਕਾਰੀ ਵੇਖੋ, ਸਟੋਰੇਜ ਜਾਂਚੋ, ਫਸਲ ਵੇਚੋ ਅਤੇ ਫਸਲ ਪਾਸਪੋਰਟ ਵੇਖੋ।"),
    "ଓଡ଼ିଆ (Odia)": ("or-IN", "CropSyncX କୁ ସ୍ୱାଗତ। କ୍ଷେତର ସୂଚନା ଦେଖନ୍ତୁ, ସଂରକ୍ଷଣ ଯାଞ୍ଚ କରନ୍ତୁ, ଫସଲ ବିକ୍ରି କରନ୍ତୁ ଏବଂ ଫସଲ ପାସପୋର୍ଟ ଦେଖନ୍ତୁ।"),
    "অসমীয়া (Assamese)": ("as-IN", "CropSyncX লৈ স্বাগতম। খেতিৰ তথ্য চাওক, সংৰক্ষণ পৰীক্ষা কৰক, শস্য বিক্ৰী কৰক আৰু শস্য পাছপ'ৰ্ট চাওক।"),
    "اردو (Urdu)": ("ur-IN", "CropSyncX میں خوش آمدید۔ کھیت کی معلومات دیکھیں، ذخیرہ چیک کریں، فصل فروخت کریں اور فصل پاسپورٹ دیکھیں۔"),
    "संस्कृतम् (Sanskrit)": ("sa-IN", "CropSyncX मध्ये स्वागतम्। क्षेत्रस्य विवरणं पश्यतु, भण्डारणं परीक्षताम्, सस्यानि विक्रीणीत, सस्यपरिचयपत्रं च पश्यतु।"),
    "कोंकणी (Konkani)": ("kok-IN", "CropSyncX-ांत येवकार. शेताची म्हायती पळयात, साठवण तपासात, पीक विकात आनी पीक पासपोर्ट पळयात."),
    "মৈথিলী (Maithili)": ("mai-IN", "CropSyncX में अहाँक स्वागत अछि। खेतक जानकारी देखू, भंडारण जाँचू, फसल बेचू आ फसल पासपोर्ट देखू।"),
    "नेपाली (Nepali)": ("ne-IN", "CropSyncX मा स्वागत छ। खेतको जानकारी हेर्नुहोस्, भण्डारण जाँच्नुहोस्, बाली बेच्नुहोस् र बाली पासपोर्ट हेर्नुहोस्।"),
    "डोगरी (Dogri)": ("doi-IN", "CropSyncX च तुंदा स्वागत ऐ। खेत दी जानकारी दिक्खो, भंडारण जांचो, फसल बेचो ते फसल पासपोर्ट दिक्खो।"),
    "बोडो (Bodo)": ("brx-IN", "CropSyncX आवगनाय। फिसानि मुंनि फोरमायथि नाय, दोनथुमनाय नाय, फिसानि बेखेव आरो फिसानि पासपोर्ट नाय।"),
    "سنٿالي (Santali)": ("sat-IN", "CropSyncX रे जोहार। खेत रेयाक् खबर ञेल मे, जतन ओबोसता ञेल मे, फसल आचुर मे आर फसल पासपोर्ट ञेल मे।"),
    "سنڌي (Sindhi)": ("sd-IN", "CropSyncX ۾ ڀليڪار۔ پنهنجي زمين جي معلومات ڏسو، ذخيرو چيڪ ڪريو، فصل وڪرو ڪريو ۽ فصل پاسپورٽ ڏسو۔"),
    "کٲشُر (Kashmiri)": ("ks-IN", "CropSyncX منز خوش آمدید۔ کھیتچ معلومات وُچھو، ذخیرہ چیک کٔرِو، فصل وِکرِو تہٕ فصل پاسپورٹ وُچھو۔"),
    "मणिपुरी (Manipuri/Meitei)": ("mni-IN", "CropSyncX দা তরাম্না ওইরি। লৌমী মরমশিং ইয়েংউ, ফসল থম্নবা মফম চেক তৌ, ফসল পীবিয়ু অমসুং ফসল পাসপোর্ট ইয়েংউ।"),
}

LANG_UI = {
    "English": {"register":"Farmer Registration", "name":"Farmer name", "village":"Village", "experience":"Years of farming experience", "state":"State / Union Territory", "phone":"Phone number (optional)", "save":"Save farmer profile", "voice":"🔊 Play voice guide", "welcome":"Welcome to CropSyncX", "profile":"Registered farmer profiles", "language":"Choose language / भाषा चुनें"},
    "हिन्दी (Hindi)": {"register":"किसान पंजीकरण", "name":"किसान का नाम", "village":"गाँव", "experience":"खेती का अनुभव (वर्ष)", "state":"राज्य / केंद्र शासित प्रदेश", "phone":"फ़ोन नंबर (वैकल्पिक)", "save":"किसान प्रोफ़ाइल सहेजें", "voice":"🔊 आवाज़ में मार्गदर्शन सुनें", "welcome":"CropSyncX में आपका स्वागत है", "profile":"पंजीकृत किसान प्रोफ़ाइल", "language":"भाषा चुनें"},
    "తెలుగు (Telugu)": {"register":"రైతు నమోదు", "name":"రైతు పేరు", "village":"గ్రామం", "experience":"వ్యవసాయ అనుభవం (సంవత్సరాలు)", "state":"రాష్ట్రం / కేంద్రపాలిత ప్రాంతం", "phone":"ఫోన్ నంబర్ (ఐచ్ఛికం)", "save":"రైతు వివరాలను సేవ్ చేయండి", "voice":"🔊 వాయిస్ గైడ్ వినండి", "welcome":"క్రాప్‌సింక్స్‌కు స్వాగతం", "profile":"నమోదైన రైతుల వివరాలు", "language":"భాషను ఎంచుకోండి"},
    "தமிழ் (Tamil)": {"register":"விவசாயி பதிவு", "name":"விவசாயி பெயர்", "village":"கிராமம்", "experience":"விவசாய அனுபவம் (ஆண்டுகள்)", "state":"மாநிலம் / யூனியன் பிரதேசம்", "phone":"தொலைபேசி எண் (விருப்பம்)", "save":"விவசாயி விவரங்களைச் சேமிக்கவும்", "voice":"🔊 குரல் வழிகாட்டியைக் கேளுங்கள்", "welcome":"கிராப்சிங்க்ஸ் செயலிக்கு வரவேற்கிறோம்", "profile":"பதிவு செய்யப்பட்ட விவசாயிகள்", "language":"மொழியைத் தேர்ந்தெடுக்கவும்"},
    "ಕನ್ನಡ (Kannada)": {"register":"ರೈತರ ನೋಂದಣಿ", "name":"ರೈತರ ಹೆಸರು", "village":"ಗ್ರಾಮ", "experience":"ಕೃಷಿ ಅನುಭವ (ವರ್ಷಗಳು)", "state":"ರಾಜ್ಯ / ಕೇಂದ್ರಾಡಳಿತ ಪ್ರದೇಶ", "phone":"ಫೋನ್ ಸಂಖ್ಯೆ (ಐಚ್ಛಿಕ)", "save":"ರೈತರ ವಿವರಗಳನ್ನು ಉಳಿಸಿ", "voice":"🔊 ಧ್ವನಿ ಮಾರ್ಗದರ್ಶಿ ಕೇಳಿ", "welcome":"ಕ್ರಾಪ್‌ಸಿಂಕ್‌ಎಕ್ಸ್‌ಗೆ ಸ್ವಾಗತ", "profile":"ನೋಂದಾಯಿತ ರೈತರ ವಿವರಗಳು", "language":"ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ"},
    "മലയാളം (Malayalam)": {"register":"കർഷക രജിസ്ട്രേഷൻ", "name":"കർഷകന്റെ പേര്", "village":"ഗ്രാമം", "experience":"കൃഷി പരിചയം (വർഷങ്ങൾ)", "state":"സംസ്ഥാനം / കേന്ദ്രഭരണ പ്രദേശം", "phone":"ഫോൺ നമ്പർ (ഐച്ഛികം)", "save":"കർഷക വിവരങ്ങൾ സംരക്ഷിക്കുക", "voice":"🔊 ശബ്ദ മാർഗ്ഗനിർദ്ദേശം കേൾക്കുക", "welcome":"CropSyncX-ലേക്ക് സ്വാഗതം", "profile":"രജിസ്റ്റർ ചെയ്ത കർഷകർ", "language":"ഭാഷ തിരഞ്ഞെടുക്കുക"},
    "বাংলা (Bengali)": {"register":"কৃষক নিবন্ধন", "name":"কৃষকের নাম", "village":"গ্রাম", "experience":"কৃষিকাজের অভিজ্ঞতা (বছর)", "state":"রাজ্য / কেন্দ্রশাসিত অঞ্চল", "phone":"ফোন নম্বর (ঐচ্ছিক)", "save":"কৃষকের প্রোফাইল সংরক্ষণ করুন", "voice":"🔊 ভয়েস গাইড শুনুন", "welcome":"CropSyncX-এ স্বাগতম", "profile":"নিবন্ধিত কৃষকের প্রোফাইল", "language":"ভাষা নির্বাচন করুন"},
}

def ui(key):
    selected = st.session_state.get("language", "English")
    return LANG_UI.get(selected, LANG_UI["English"]).get(key, LANG_UI["English"].get(key, key))

def image_bytes(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

def init_state():
    defaults = {
        "listings": [
            {"id": "CSX-1001", "crop": "Tomato", "quantity": 50, "price": 30.0,
             "farmer": "Ravi Kumar", "location": "Village Market", "available": True},
            {"id": "CSX-1002", "crop": "Rice", "quantity": 100, "price": 35.0,
             "farmer": "Lakshmi Devi", "location": "Farm Gate", "available": True},
            {"id": "CSX-1003", "crop": "Mango", "quantity": 25, "price": 60.0,
             "farmer": "Suresh", "location": "Village Market", "available": True},
        ],
        "orders": [],
        "crop_batches": [],
        "last_field": {},
        "last_storage": {},
        "farmers": [],
        "language": "English",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# ---------- Friendly farmer-first design ----------
st.markdown(
    """<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
    :root { --forest:#164b32; --leaf:#28784b; --gold:#d6a83e; --cream:#f7f5e9; }
    .stApp { background: linear-gradient(rgba(247,245,233,.94), rgba(247,245,233,.97)),
      url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=2000&q=85') center/cover fixed; }
    html, body, [class*="css"] { font-family:'Nunito',sans-serif; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#123c2a,#1c6842); }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:#fffdf2; }
    [data-testid="stSidebar"] [data-testid="stAlert"] { background:#f5f1df; }
    [data-testid="stSidebar"] [data-testid="stAlert"] * { color:#164b32 !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div { background:#fffdf7; color:#173b29; }
    div[role="listbox"] * { color:#173b29 !important; background:#fffdf7; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea { color:#173b29; background:#fffdf7; }
    [data-testid="stRadio"] label { color:inherit; }
    [data-testid="stMetric"] { background:#fff; border:1px solid #e5dfc9; padding:18px 20px; border-radius:18px; box-shadow:0 5px 18px #164b3210; }
    [data-testid="stMetricValue"] { color:#164b32; font-weight:900; }
    .stButton>button, .stFormSubmitButton>button { border-radius:12px; font-weight:800; border:0; background:#1c6842; color:white; min-height:2.8rem; }
    .stButton>button:hover, .stFormSubmitButton>button:hover { background:#d6a83e; color:#173b29; border:0; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px; }
    h1,h2,h3 { color:#164b32; }
    .hero { padding:30px 32px; border-radius:24px; color:white; background:linear-gradient(90deg,rgba(15,57,37,.94),rgba(28,104,66,.63)),url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85') center/cover; margin-bottom:18px; box-shadow:0 10px 30px #164b3220; }
    .hero h1 {color:#fff9e7; font-size:2.45rem; margin-bottom:.35rem;} .hero p {color:#fff; font-size:1.08rem;}
    .small-note {color:#657565;font-size:.88rem;}
    /* Explicit high-contrast text: prevent light Streamlit theme text on cream */
    [data-testid="stAppViewContainer"] .main,
    [data-testid="stAppViewContainer"] .main p,
    [data-testid="stAppViewContainer"] .main li,
    [data-testid="stAppViewContainer"] .main label,
    [data-testid="stAppViewContainer"] .main [data-testid="stMarkdownContainer"],
    [data-testid="stAppViewContainer"] .main [data-testid="stCaptionContainer"],
    [data-testid="stAppViewContainer"] .main [data-testid="stText"],
    [data-testid="stAppViewContainer"] .main .stRadio,
    [data-testid="stAppViewContainer"] .main .stCheckbox { color:#173b29 !important; }
    [data-testid="stAppViewContainer"] .main h1,
    [data-testid="stAppViewContainer"] .main h2,
    [data-testid="stAppViewContainer"] .main h3,
    [data-testid="stAppViewContainer"] .main h4 { color:#164b32 !important; }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color:#526456 !important; }
    [data-testid="stMetricValue"] { color:#164b32 !important; }
    [data-testid="stAlert"] p, [data-testid="stAlert"] div { color:#173b29 !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label { color:#fffdf2 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#fffdf2 !important; }
    .hero, .hero p, .hero h1, .hero h2 { color:#fffdf2 !important; }
    /* FINAL OVERRIDE: Streamlit versions differ in their internal CSS classes.
       Target the actual main content area directly so text never inherits white. */
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] label,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stText"],
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] [data-testid="stWidgetLabel"] label,
    [data-testid="stMain"] .stRadio,
    [data-testid="stMain"] .stCheckbox { color:#173b29 !important; }
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5 { color:#164b32 !important; }
    [data-testid="stMain"] input,
    [data-testid="stMain"] textarea { color:#173b29 !important; background:#fffdf7 !important; }
    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] textarea::placeholder { color:#68766b !important; opacity:1 !important; }
    [data-testid="stMain"] [data-testid="stMetricLabel"],
    [data-testid="stMain"] [data-testid="stMetricLabel"] p { color:#526456 !important; }
    [data-testid="stMain"] [data-testid="stAlert"] p,
    [data-testid="stMain"] [data-testid="stAlert"] div { color:#173b29 !important; }
    [data-testid="stMain"] .hero,
    [data-testid="stMain"] .hero p,
    [data-testid="stMain"] .hero h1,
    [data-testid="stMain"] .hero h2 { color:#fffdf2 !important; }
    </style>""", unsafe_allow_html=True
)

st.sidebar.title("🌾 CropSyncX")
st.sidebar.caption("Smart Farm-to-Consumer Ecosystem")
st.sidebar.selectbox("🌐 Choose language / भाषा चुनें", list(LANGUAGES.keys()), key="language")
page = st.sidebar.radio(
    "📍 Menu / मेनू",
    ["Overview", "👨‍🌾 Farmer Registration", "🌱 Smart Field", "🏠 Smart Storage", "🛒 Direct Market", "🔎 Crop Passport"],
)
st.sidebar.divider()
# Context-aware voice guide: instructions change with the selected page.
# English and Telugu have detailed page-by-page guidance; other selected languages
# currently use English page guidance until their translations are added.
import json

# Page-by-page voice guidance. The four main demo languages have complete guides;
# the other language choices still provide a localized welcome voice.
PAGE_GUIDES = {
    "English": {
        "Overview": "Welcome to CropSyncX. This demo helps farmers monitor field conditions, check storage recommendations, list crops for sale, place sample orders, and view crop batch traceability. Start with Farmer Registration, then use Smart Field, Smart Storage, Direct Market, and Crop Passport.",
        "👨‍🌾 Farmer Registration": "Welcome to Farmer Registration. Enter the farmer name and village, choose years of farming experience and state, and optionally enter a phone number. Select a preferred language, tick the demo consent box, and press Save Farmer Profile. The profile is stored only for this app session.",
        "🌱 Smart Field": "Welcome to Smart Field Monitoring. Enter a field name and select a crop. Press Generate New Sensor Readings. The dashboard displays simulated soil moisture, soil temperature, air temperature, humidity, and soil pH. Review the alerts. These are simulated values, not real sensor readings.",
        "🏠 Smart Storage": "Welcome to Smart Storage. Select a crop, enter quantity and planned storage duration, then review the illustrative temperature and humidity targets. Adjust outside temperature, storage temperature, humidity, and sunlight. Press Evaluate Storage Conditions to see cooling, fan, and roof-louver recommendations. No physical equipment is connected. To track the batch, press Create Crop Passport for This Storage Batch, then open Crop Passport.",
        "🛒 Direct Market": "Welcome to Direct Market. In Farmer Add Listing, enter farmer name, crop, quantity, price per kilogram, and pickup location, then publish the listing. In Consumer Place Order, choose a listing, enter your name and quantity, choose pickup or farmer delivery, and review the bill. Place Demo Order creates a sample order; no real payment is collected. Open Orders to review it.",
        "🔎 Crop Passport": "Welcome to Crop Passport and Traceability. Select a batch to see its crop, quantity, storage duration, and recorded details. View or download its QR code. If there is no batch, go to Smart Storage, evaluate storage conditions, create a crop passport for that batch, and return here.",
    },
    "हिन्दी (Hindi)": {
        "Overview": "CropSyncX में आपका स्वागत है। यह डेमो खेत की स्थिति देखने, भंडारण सुझाव जाँचने, फसल की बिक्री सूची बनाने, नमूना ऑर्डर करने और फसल बैच का क्यूआर पासपोर्ट देखने में मदद करता है। पहले किसान पंजीकरण करें, फिर स्मार्ट फील्ड, स्मार्ट स्टोरेज, डायरेक्ट मार्केट और क्रॉप पासपोर्ट का उपयोग करें।",
        "👨‍🌾 Farmer Registration": "किसान पंजीकरण में आपका स्वागत है। किसान का नाम और गाँव भरें, खेती का अनुभव और राज्य चुनें, और चाहें तो फ़ोन नंबर दें। पसंदीदा भाषा चुनें, डेमो सहमति पर टिक करें और किसान प्रोफ़ाइल सहेजें दबाएँ। जानकारी केवल इस ऐप सत्र में रहती है।",
        "🌱 Smart Field": "स्मार्ट फील्ड में आपका स्वागत है। खेत का नाम भरें और फसल चुनें। नए सेंसर रीडिंग बनाने वाला बटन दबाएँ। मिट्टी की नमी, मिट्टी का तापमान, हवा का तापमान, आर्द्रता और पीएच के नमूना मान दिखेंगे। अलर्ट देखें। ये वास्तविक सेंसर रीडिंग नहीं, केवल सिमुलेटेड मान हैं।",
        "🏠 Smart Storage": "स्मार्ट स्टोरेज में आपका स्वागत है। फसल चुनें, मात्रा और भंडारण अवधि भरें, फिर तापमान और आर्द्रता के उदाहरण लक्ष्य देखें। बाहर का तापमान, स्टोरेज तापमान, आर्द्रता और धूप बदलें। भंडारण स्थिति जाँचें दबाकर कूलिंग, पंखे और छत के वेंट संबंधी सुझाव देखें। कोई वास्तविक उपकरण जुड़ा नहीं है। बैच ट्रैक करने के लिए इस बैच का क्रॉप पासपोर्ट बनाएँ और क्रॉप पासपोर्ट पेज खोलें।",
        "🛒 Direct Market": "डायरेक्ट मार्केट में आपका स्वागत है। किसान सूची जोड़ें टैब में किसान का नाम, फसल, मात्रा, प्रति किलो कीमत और पिकअप स्थान भरकर सूची प्रकाशित करें। ग्राहक ऑर्डर टैब में सूची चुनें, नाम और मात्रा भरें, पिकअप या किसान डिलीवरी चुनें और बिल देखें। डेमो ऑर्डर करने पर केवल नमूना ऑर्डर बनेगा; वास्तविक भुगतान नहीं होगा। ऑर्डर टैब में ऑर्डर देखें।",
        "🔎 Crop Passport": "क्रॉप पासपोर्ट पेज में आपका स्वागत है। सूची से बैच चुनकर फसल, मात्रा, भंडारण अवधि और दर्ज विवरण देखें। क्यूआर कोड देख या डाउनलोड कर सकते हैं। बैच न दिखे तो स्मार्ट स्टोरेज में जाएँ, स्थिति जाँचें, बैच का क्रॉप पासपोर्ट बनाएँ और फिर यहाँ लौटें।",
    },
    "తెలుగు (Telugu)": {
        "Overview": "క్రాప్‌సింక్స్‌కు స్వాగతం. ఈ డెమోలో పొల పరిస్థితులను చూడవచ్చు, నిల్వ సూచనలను పరిశీలించవచ్చు, పంటలను అమ్మకానికి జాబితా చేయవచ్చు, నమూనా ఆర్డర్లు చేయవచ్చు, పంట బ్యాచ్ క్యూఆర్ పాస్‌పోర్ట్ చూడవచ్చు. ముందుగా రైతు నమోదు చేసి, తరువాత స్మార్ట్ ఫీల్డ్, స్మార్ట్ స్టోరేజ్, డైరెక్ట్ మార్కెట్, క్రాప్ పాస్‌పోర్ట్ ఉపయోగించండి.",
        "👨‍🌾 Farmer Registration": "రైతు నమోదు పేజీకి స్వాగతం. రైతు పేరు, గ్రామం నమోదు చేసి, వ్యవసాయ అనుభవం మరియు రాష్ట్రాన్ని ఎంచుకోండి. ఫోన్ నంబర్ ఐచ్ఛికం. ఇష్టమైన భాషను ఎంచుకుని, డెమో అంగీకార పెట్టెను టిక్ చేసి, రైతు వివరాలను సేవ్ చేయండి. వివరాలు ఈ యాప్ సెషన్‌లో మాత్రమే ఉంటాయి.",
        "🌱 Smart Field": "స్మార్ట్ ఫీల్డ్ పర్యవేక్షణకు స్వాగతం. పొలం పేరు నమోదు చేసి పంటను ఎంచుకోండి. కొత్త సెన్సార్ రీడింగ్స్ బటన్ నొక్కండి. నేల తేమ, నేల ఉష్ణోగ్రత, గాలి ఉష్ణోగ్రత, తేమ శాతం మరియు పీహెచ్ నమూనా విలువలు కనిపిస్తాయి. హెచ్చరికలను పరిశీలించండి. ఇవి నిజమైన సెన్సార్ రీడింగ్స్ కావు; నమూనా విలువలు మాత్రమే.",
        "🏠 Smart Storage": "స్మార్ట్ స్టోరేజ్‌కు స్వాగతం. పంటను ఎంచుకుని పరిమాణం, నిల్వ రోజుల సంఖ్య నమోదు చేయండి. ఉష్ణోగ్రత మరియు తేమ లక్ష్యాలను చూడండి. బయట ఉష్ణోగ్రత, నిల్వ ఉష్ణోగ్రత, తేమ, సూర్యకాంతి విలువలను మార్చండి. నిల్వ పరిస్థితులను పరిశీలించు బటన్ నొక్కి కూలింగ్, ఫ్యాన్, పైకప్పు సూచనలు చూడండి. నిజమైన పరికరాలు కనెక్ట్ కాలేదు. బ్యాచ్‌ను ట్రాక్ చేయడానికి క్రాప్ పాస్‌పోర్ట్ సృష్టించి ఆ పేజీకి వెళ్లండి.",
        "🛒 Direct Market": "డైరెక్ట్ మార్కెట్‌కు స్వాగతం. రైతు జాబితా ట్యాబ్‌లో పేరు, పంట, పరిమాణం, కిలో ధర, తీసుకెళ్లే స్థలం నమోదు చేసి జాబితాను ప్రచురించండి. వినియోగదారుల ఆర్డర్ ట్యాబ్‌లో పంటను ఎంచుకుని పేరు, పరిమాణం నమోదు చేసి పికప్ లేదా డెలివరీ ఎంచుకోండి. బిల్లును చూసి నమూనా ఆర్డర్ చేయండి. నిజమైన చెల్లింపు జరగదు. ఆర్డర్ల ట్యాబ్‌లో వాటిని చూడండి.",
        "🔎 Crop Passport": "క్రాప్ పాస్‌పోర్ట్ పేజీకి స్వాగతం. బ్యాచ్‌ను ఎంచుకుని పంట, పరిమాణం, నిల్వ రోజులు, వివరాలను చూడండి. క్యూఆర్ కోడ్‌ను చూడవచ్చు లేదా డౌన్‌లోడ్ చేసుకోవచ్చు. బ్యాచ్ లేకపోతే స్మార్ట్ స్టోరేజ్‌లో పరిస్థితులను పరిశీలించి క్రాప్ పాస్‌పోర్ట్ సృష్టించి తిరిగి ఇక్కడికి రండి.",
    },
    "தமிழ் (Tamil)": {
        "Overview": "CropSyncX-க்கு வரவேற்கிறோம். இந்த டெமோவில் வயல் நிலையைப் பார்க்கலாம், சேமிப்பு பரிந்துரைகளைச் சரிபார்க்கலாம், பயிர்களை விற்பனைக்குப் பட்டியலிடலாம், மாதிரி ஆர்டர்கள் செய்யலாம், பயிர் தொகுதியின் QR பாஸ்போர்ட்டைப் பார்க்கலாம். முதலில் விவசாயி பதிவைச் செய்து, பிறகு Smart Field, Smart Storage, Direct Market, Crop Passport பக்கங்களைப் பயன்படுத்துங்கள்.",
        "👨‍🌾 Farmer Registration": "விவசாயி பதிவு பக்கத்திற்கு வரவேற்கிறோம். விவசாயியின் பெயர் மற்றும் கிராமத்தை உள்ளிடுங்கள்; அனுபவ ஆண்டுகள் மற்றும் மாநிலத்தைத் தேர்ந்தெடுக்கவும். தொலைபேசி எண் விருப்பமானது. விருப்ப மொழியைத் தேர்ந்தெடுத்து, டெமோ ஒப்புதல் பெட்டியைத் தேர்வு செய்து, விவரங்களைச் சேமிக்கவும். இந்த விவரங்கள் தற்போதைய செயலி அமர்வில் மட்டுமே இருக்கும்.",
        "🌱 Smart Field": "Smart Field கண்காணிப்புக்கு வரவேற்கிறோம். வயல் பெயரை உள்ளிட்டு பயிரைத் தேர்ந்தெடுக்கவும். புதிய சென்சார் அளவீடுகள் பொத்தானை அழுத்தவும். மண் ஈரப்பதம், மண் வெப்பநிலை, காற்று வெப்பநிலை, ஈரப்பதம் மற்றும் pH ஆகியவற்றின் மாதிரி மதிப்புகள் காட்டப்படும். எச்சரிக்கைகளைப் பாருங்கள். இவை உண்மையான சென்சார் அளவீடுகள் அல்ல; உருவகப்படுத்தப்பட்ட மதிப்புகள்.",
        "🏠 Smart Storage": "Smart Storage பக்கத்திற்கு வரவேற்கிறோம். சேமிக்க வேண்டிய பயிரைத் தேர்ந்தெடுத்து அளவு மற்றும் சேமிப்பு நாட்களை உள்ளிடுங்கள். காட்டப்படும் வெப்பநிலை மற்றும் ஈரப்பத இலக்குகளைப் பாருங்கள். வெளியிலுள்ள வெப்பநிலை, சேமிப்பு வெப்பநிலை, ஈரப்பதம் மற்றும் சூரிய ஒளியை மாற்றவும். சேமிப்பு நிலையை மதிப்பிடு பொத்தானை அழுத்தி குளிரூட்டல், விசிறி மற்றும் கூரை திறப்பு பரிந்துரைகளைப் பாருங்கள். உண்மையான கருவிகள் இணைக்கப்படவில்லை. தொகுதியைக் கண்காணிக்க Crop Passport உருவாக்கி அந்தப் பக்கத்திற்குச் செல்லுங்கள்.",
        "🛒 Direct Market": "Direct Market பக்கத்திற்கு வரவேற்கிறோம். விவசாயி பட்டியல் பகுதியில் பெயர், பயிர், அளவு, ஒரு கிலோ விலை மற்றும் எடுத்துச் செல்லும் இடத்தை உள்ளிட்டு பட்டியலை வெளியிடுங்கள். நுகர்வோர் ஆர்டர் பகுதியில் பொருளைத் தேர்ந்தெடுத்து பெயர், அளவு உள்ளிட்டு நேரடியாக எடுத்துச் செல்லுதல் அல்லது விவசாயி விநியோகத்தைத் தேர்வுசெய்யுங்கள். கட்டண விவரங்களைப் பார்த்து மாதிரி ஆர்டர் செய்யுங்கள். உண்மையான பணம் வசூலிக்கப்படாது. Orders பகுதியில் ஆர்டர்களைப் பாருங்கள்.",
        "🔎 Crop Passport": "Crop Passport பக்கத்திற்கு வரவேற்கிறோம். பட்டியலில் ஒரு தொகுதியைத் தேர்ந்தெடுத்து பயிர், அளவு, சேமிப்பு நாட்கள் மற்றும் பதிவு விவரங்களைப் பாருங்கள். QR குறியீட்டைப் பார்க்கவும் பதிவிறக்கவும் முடியும். தொகுதி இல்லையெனில் Smart Storage பக்கத்தில் நிலையை மதிப்பிட்டு Crop Passport உருவாக்கி மீண்டும் இங்கு வாருங்கள்.",
    },
}

selected_language = st.session_state.language
voice_lang, _welcome_text = LANGUAGES[selected_language]
voice_guides = PAGE_GUIDES.get(selected_language)
if voice_guides:
    voice_text = voice_guides.get(page, voice_guides["Overview"])
else:
    # All 22 language choices can play a localized welcome; full page-by-page narration
    # is currently provided in English, Hindi, Telugu and Tamil.
    voice_text = _welcome_text
voice_button_label = ui("voice")
voice_html = f"""<style>body{{font-family:Arial,sans-serif;background:transparent;margin:0}} #voiceStatus{{font-size:12px;color:#173b29;background:#f7f5e9;padding:7px;border-radius:8px;margin-top:7px}}</style><button id="voiceGuide" style="width:100%;padding:12px;border:0;border-radius:12px;background:#d6a83e;color:#173b29;font-weight:800;font-size:15px;cursor:pointer">{html.escape(voice_button_label)}</button>
<div id="voiceStatus">Press the button whenever you need help with this page.</div>
<script>
const btn = document.getElementById("voiceGuide");
const statusBox = document.getElementById("voiceStatus");
const textToSpeak = {json.dumps(voice_text, ensure_ascii=False)};
const languageCode = {json.dumps(voice_lang)};
btn.addEventListener("click", () => {{
  if (!("speechSynthesis" in window)) {{
    statusBox.innerText = "Voice guidance is not supported in this browser.";
    return;
  }}
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(textToSpeak);
  utterance.lang = languageCode;
  utterance.rate = 0.82;
  utterance.pitch = 1;
  const voices = window.speechSynthesis.getVoices();
  const prefix = languageCode.split("-")[0].toLowerCase();
  const match = voices.find(v => v.lang.toLowerCase().startsWith(prefix));
  if (match) utterance.voice = match;
  utterance.onstart = () => statusBox.innerText = "Playing page instructions…";
  utterance.onend = () => statusBox.innerText = "Instructions finished. Press again to replay.";
  utterance.onerror = () => statusBox.innerText = "Voice playback failed. Check browser/device language voices.";
  window.speechSynthesis.speak(utterance);
}});
</script>"""
components.html(voice_html, height=112)
st.sidebar.info("Demo mode: readings and device controls are simulated. Full page-by-page voice guidance: English, Hindi, Telugu and Tamil. Other listed languages include a localized welcome voice where your browser has a matching voice.")

# ---------- Farmer Registration ----------
if page == "👨‍🌾 Farmer Registration":
    st.markdown(f"<div class='hero'><h1>👨‍🌾 {html.escape(ui('register'))}</h1><p>{html.escape(ui('welcome'))} — a simple, farmer-friendly digital farm companion.</p></div>", unsafe_allow_html=True)
    st.write("Register a farmer profile to personalise the demo. This prototype stores profiles only for the current app session; it does not send them to a server.")
    with st.form("farmer_registration", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            farmer_name = st.text_input(ui("name"), placeholder="e.g., Lakshmi Devi")
            village = st.text_input(ui("village"), placeholder="e.g., Anandapuram")
            experience = st.number_input(ui("experience"), min_value=0, max_value=80, value=5, step=1)
        with col_b:
            states = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry"]
            state = st.selectbox(ui("state"), states)
            phone = st.text_input(ui("phone"), placeholder="Optional")
            preferred_language = st.selectbox("Preferred language / ఇష్టమైన భాష", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.language))
        consent = st.checkbox("I understand this is a prototype demo and my profile is stored temporarily in this session.")
        submitted = st.form_submit_button(ui("save"), type="primary", use_container_width=True)
    if submitted:
        if not farmer_name.strip() or not village.strip():
            st.error("Please enter the farmer name and village.")
        elif not consent:
            st.warning("Please confirm the demo-data note before saving.")
        else:
            profile = {"Farmer ID": f"FARM-{uuid.uuid4().hex[:6].upper()}", "Name": farmer_name.strip(), "Village": village.strip(), "Experience (years)": int(experience), "State": state, "Phone": phone.strip(), "Preferred language": preferred_language}
            st.session_state.farmers.append(profile)
            st.success(f"Profile registered successfully for {farmer_name.strip()}!")
            st.balloons()
    st.markdown(f"### 📋 {ui('profile')}")
    if st.session_state.farmers:
        st.dataframe(pd.DataFrame(st.session_state.farmers), use_container_width=True, hide_index=True)
    else:
        st.info("No farmer profiles registered in this session yet.")
    st.caption("Privacy note: do not enter sensitive identity details. Phone number is optional and this prototype does not use it.")

# ---------- Overview ----------
elif page == "Overview":
    st.markdown("<div class='hero'><h1>🌾 CropSyncX</h1><p>From healthy fields to smarter storage and fairer markets.</p><p>🌱 Field → 🏠 Storage → 🛒 Market → 🔎 Traceability</p></div>", unsafe_allow_html=True)
    st.subheader("AI-powered smart crop lifecycle: Field → Storage → Market")
    st.write("A single demo platform for crop monitoring, storage decisions, crop traceability, and direct farmer-to-consumer sales.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Platform modules", "3")
    c2.metric("Crop listings", len([x for x in st.session_state.listings if x["available"]]))
    c3.metric("Orders placed", len(st.session_state.orders))
    c4.metric("Tracked batches", len(st.session_state.crop_batches))
    st.divider()

    # Changeable agriculture photo gallery: illustrative stock photos, not photos
    # captured from real CropSyncX farms.
    farm_gallery = [
        ("Golden crop field at sunrise", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85"),
        ("Green crop rows", "https://images.unsplash.com/photo-1499529112087-3cb3b73a0f9d?auto=format&fit=crop&w=1800&q=85"),
        ("Fresh vegetables", "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1800&q=85"),
        ("Rice field landscape", "https://images.unsplash.com/photo-1536054868625-8a5e3f9d0c8c?auto=format&fit=crop&w=1800&q=85"),
        ("Tomatoes ready for harvest", "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=1800&q=85"),
        ("Farmers working in a field", "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=1800&q=85"),
        ("Fresh produce harvest", "https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1800&q=85"),
        ("Sunlit countryside", "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&w=1800&q=85"),
        ("Green plants growing", "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=1800&q=85"),
        ("Vegetable garden", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=1800&q=85"),
        ("Corn crop", "https://images.unsplash.com/photo-1601593768790-5f4d0b4d6b00?auto=format&fit=crop&w=1800&q=85"),
        ("Fresh fruit harvest", "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=1800&q=85"),
        ("Farm landscape", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85&sat=-15"),
        ("Green leaves and seedlings", "https://images.unsplash.com/photo-1497250681960-ef046c08a56e?auto=format&fit=crop&w=1800&q=85"),
        ("Vegetable market produce", "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1800&q=85"),
    ]
    st.markdown("### 🌄 CropSyncX Agriculture Gallery")
    st.caption("Each new visitor/session gets a different starting photo and an encouraging farmer quote. Use the arrows or dots to explore all 15 pictures.")
    import json
    import random as _gallery_random
    farm_quotes = [
        "Every seed you plant is a promise of tomorrow.",
        "Your hard work feeds families and strengthens the nation.",
        "Small steps in the field can grow into a great harvest.",
        "A patient farmer knows that growth takes time.",
        "Your knowledge and experience are your farm's greatest strengths.",
        "Every season teaches something new. Keep learning, keep growing.",
        "Healthy soil, hopeful hearts, and steady effort build a better future.",
        "The hands that grow food deserve respect every day.",
        "Even after a difficult season, a new sunrise brings new possibilities.",
        "Your dedication today can become tomorrow's harvest.",
        "Good farming begins with care, observation, and courage.",
        "You are not just growing crops; you are growing hope.",
        "Nature rewards care and consistency. Keep doing your best.",
        "Every farmer's journey matters. Your work makes a difference.",
        "Dream big for your farm, plan wisely, and grow one step at a time."
    ]
    gallery_items = [{"name": name, "url": url, "quote": farm_quotes[i]} for i, (name, url) in enumerate(farm_gallery)]
    if "gallery_start_index" not in st.session_state:
        st.session_state.gallery_start_index = _gallery_random.randrange(len(gallery_items))
    gallery_payload = json.dumps(gallery_items)
    gallery_html = '''\
    <div id="cropsyncx-slideshow" style="width:100%;font-family:Arial,sans-serif;">
      <div style="position:relative;overflow:hidden;border-radius:16px;background:#e9efdf;box-shadow:0 8px 24px rgba(20,70,40,.16);">
        <img id="farm-slide" src="" alt="Agriculture gallery photo" style="display:block;width:100%;height:520px;object-fit:cover;transition:opacity .7s ease;opacity:1;" />
        <div style="position:absolute;left:0;right:0;bottom:0;padding:22px 18px 16px;color:white;background:linear-gradient(transparent,rgba(0,0,0,.72));">
          <div id="farm-slide-title" style="font-size:clamp(18px,2.4vw,28px);font-weight:700;text-shadow:0 1px 3px #000;"></div>
          <div id="farm-slide-quote" style="font-size:clamp(15px,1.8vw,21px);font-style:italic;font-weight:600;margin-top:9px;max-width:900px;text-shadow:0 1px 3px #000;"></div>
          <div id="farm-slide-count" style="font-size:13px;margin-top:7px;text-shadow:0 1px 3px #000;"></div>
        </div>
        <button id="farm-slide-prev" aria-label="Previous photo" style="position:absolute;top:48%;left:14px;border:0;border-radius:50%;width:44px;height:44px;font-size:25px;background:rgba(255,255,255,.9);color:#174b32;cursor:pointer;">‹</button>
        <button id="farm-slide-next" aria-label="Next photo" style="position:absolute;top:48%;right:14px;border:0;border-radius:50%;width:44px;height:44px;font-size:25px;background:rgba(255,255,255,.9);color:#174b32;cursor:pointer;">›</button>
        <div id="farm-slide-dots" style="position:absolute;top:14px;left:0;right:0;display:flex;justify-content:center;gap:6px;flex-wrap:wrap;padding:0 55px;"></div>
      </div>
      <div style="text-align:center;font-size:12px;color:#55745f;margin-top:8px;">Illustrative stock images • A different starting image is selected for each new app session • Use arrows or dots to browse</div>
    </div>
    <script>
      const farmPhotos = __GALLERY_PAYLOAD__;
      let farmIndex = __START_INDEX__;
      const farmImg = document.getElementById('farm-slide');
      const farmTitle = document.getElementById('farm-slide-title');
      const farmQuote = document.getElementById('farm-slide-quote');
      const farmCount = document.getElementById('farm-slide-count');
      const farmDots = document.getElementById('farm-slide-dots');
      function showFarmPhoto(index) {
        farmIndex = (index + farmPhotos.length) % farmPhotos.length;
        farmImg.style.opacity = '0.2';
        const nextPhoto = farmPhotos[farmIndex];
        const preloader = new Image();
        preloader.onload = () => {
          farmImg.src = nextPhoto.url;
          farmTitle.textContent = nextPhoto.name;
          farmQuote.textContent = '“' + nextPhoto.quote + '”';
          farmCount.textContent = (farmIndex + 1) + ' / ' + farmPhotos.length;
          farmImg.style.opacity = '1';
        };
        preloader.onerror = () => {
          farmTitle.textContent = nextPhoto.name + ' (image unavailable; checking next photo…)';
          farmImg.style.opacity = '1';
        };
        preloader.src = nextPhoto.url;
        Array.from(farmDots.children).forEach((dot, i) => {
          dot.style.background = i === farmIndex ? '#ffffff' : 'rgba(255,255,255,.45)';
          dot.style.transform = i === farmIndex ? 'scale(1.25)' : 'scale(1)';
        });
      }
      farmPhotos.forEach((photo, i) => {
        const dot = document.createElement('button');
        dot.title = photo.name;
        dot.setAttribute('aria-label', 'Show ' + photo.name);
        dot.style.cssText = 'width:9px;height:9px;border:1px solid white;border-radius:50%;padding:0;cursor:pointer;background:rgba(255,255,255,.45);';
        dot.addEventListener('click', () => { showFarmPhoto(i); restartFarmTimer(); });
        farmDots.appendChild(dot);
      });
      document.getElementById('farm-slide-prev').addEventListener('click', () => showFarmPhoto(farmIndex - 1));
      document.getElementById('farm-slide-next').addEventListener('click', () => showFarmPhoto(farmIndex + 1));
      showFarmPhoto(farmIndex);
    </script>
    '''
    gallery_html = gallery_html.replace('__GALLERY_PAYLOAD__', gallery_payload).replace('__START_INDEX__', str(st.session_state.gallery_start_index))
    components.html(gallery_html, height=590, scrolling=False)

    st.markdown("### How CropSyncX works")
    a, b, c = st.columns(3)
    with a:
        st.markdown("#### 🌱 Smart Field")
        st.write("Simulated soil and environmental readings with field alerts.")
    with b:
        st.markdown("#### 🏠 Smart Storage")
        st.write("Crop-specific target ranges and rule-based fan/ventilation suggestions.")
    with c:
        st.markdown("#### 🛒 Direct Market")
        st.write("Farmer listings, consumer orders, pickup/delivery, and itemized billing.")
    st.success("Demo flow: generate readings → check storage recommendations → list produce → place an order → view a crop batch.")
    st.caption("Important: this prototype uses simulated data and simple rules. Crop storage requirements vary by variety, maturity, and local conditions; verify targets with agricultural guidance before real use.")

# ---------- Smart Field ----------
elif page == "🌱 Smart Field":
    st.title("🌱 Smart Field Monitoring")
    st.write("Generate sample sensor readings to demonstrate field monitoring and early-warning alerts.")
    left, right = st.columns([1, 2])
    with left:
        field_name = st.text_input("Field name", "North Field")
        crop = st.selectbox("Crop being grown", list(CROP_GUIDE.keys()))
        if st.button("🔄 Generate new sensor readings", type="primary"):
            st.session_state.last_field = {
                "field": field_name,
                "crop": crop,
                "moisture": round(random.uniform(15, 85), 1),
                "soil_temp": round(random.uniform(18, 38), 1),
                "air_temp": round(random.uniform(22, 42), 1),
                "humidity": round(random.uniform(30, 90), 1),
                "ph": round(random.uniform(5.0, 8.0), 1),
                "time": datetime.now().strftime("%d %b %Y, %I:%M:%S %p"),
            }
    reading = st.session_state.last_field
    if not reading:
        reading = {
            "field": "North Field", "crop": "Tomato", "moisture": 34.5,
            "soil_temp": 29.2, "air_temp": 33.1, "humidity": 48.0,
            "ph": 6.4, "time": "Sample demo reading",
        }
        st.info("Showing starter demo values. Click **Generate new sensor readings** to simulate a new reading.")
    with right:
        m1, m2, m3 = st.columns(3)
        m1.metric("Soil moisture", f'{reading["moisture"]}%')
        m2.metric("Soil temperature", f'{reading["soil_temp"]} °C')
        m3.metric("Air temperature", f'{reading["air_temp"]} °C')
        m4, m5, m6 = st.columns(3)
        m4.metric("Relative humidity", f'{reading["humidity"]}%')
        m5.metric("Soil pH", reading["ph"])
        m6.metric("Field", reading["field"])
        st.caption(f'Crop: {reading["crop"]} · Updated: {reading["time"]}')
    st.markdown("### Demo alerts")
    alerts = []
    if reading["moisture"] < 30:
        alerts.append(("warning", "Soil moisture is low in this simulated reading. Check crop-specific irrigation needs."))
    elif reading["moisture"] > 75:
        alerts.append(("warning", "Soil moisture is high in this simulated reading. Check drainage and local conditions."))
    else:
        alerts.append(("success", "Soil moisture is within the demo's general monitoring band."))
    if reading["air_temp"] > 38:
        alerts.append(("warning", "High air temperature detected in the simulated reading. Monitor heat stress risk."))
    if reading["ph"] < 5.5 or reading["ph"] > 7.5:
        alerts.append(("warning", "pH is outside this prototype's broad demo band; verify with a calibrated test."))
    for kind, message in alerts:
        getattr(st, kind)(message)
    st.caption("These are illustrative thresholds, not crop-specific agronomic advice. pH and nutrient sensors are not actually connected.")

# ---------- Smart Storage ----------
elif page == "🏠 Smart Storage":
    st.title("🏠 Smart Storage Simulator")
    st.write("Enter crop and storage details, then simulate environmental readings and a rule-based control recommendation.")
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Crop to store", list(CROP_GUIDE.keys()), key="storage_crop")
        quantity = st.number_input("Quantity (kg)", min_value=1, max_value=100000, value=100, step=10)
        duration = st.number_input("Planned storage duration (days)", min_value=1, max_value=365, value=30)
        guide = CROP_GUIDE[crop]
        st.info(f"Illustrative target for {crop}: {guide['temp_min']}–{guide['temp_max']} °C, relative humidity {guide['humidity_min']}–{guide['humidity_max']}%. Verify these demo values with a reliable crop-storage source before real use.")
    with col2:
        outside_temp = st.slider("Simulated outside temperature (°C)", 10.0, 45.0, 34.0, 0.5)
        temp = st.slider("Simulated storage temperature (°C)", 0.0, 40.0, 22.0, 0.5)
        humidity = st.slider("Simulated storage humidity (%)", 20, 100, 72, 1)
        sunlight = st.select_slider("Sunlight level", options=["Low", "Medium", "High"], value="High")
        if st.button("⚙️ Evaluate storage conditions", type="primary"):
            st.session_state.last_storage = {
                "crop": crop, "quantity": quantity, "duration": duration,
                "outside_temp": outside_temp, "temp": temp, "humidity": humidity,
                "sunlight": sunlight, "time": datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
            }
    storage = st.session_state.last_storage
    if storage:
        guide = CROP_GUIDE[storage["crop"]]
        st.divider()
        st.markdown("### Control recommendation")
        fan = storage["temp"] > guide["temp_max"] or storage["humidity"] > guide["humidity_max"]
        cooling = storage["temp"] > guide["temp_max"]
        ventilation = storage["humidity"] > guide["humidity_max"] or (storage["sunlight"] == "High" and storage["outside_temp"] < storage["temp"])
        roof = "OPEN (demo recommendation)" if ventilation else "CLOSED (demo recommendation)"
        k1, k2, k3 = st.columns(3)
        k1.metric("Temperature", f'{storage["temp"]} °C', "Above target" if cooling else "At/below upper target")
        k2.metric("Humidity", f'{storage["humidity"]}%', "Above target" if storage["humidity"] > guide["humidity_max"] else "At/below upper target")
        k3.metric("Planned storage", f'{storage["duration"]} days')
        if cooling:
            st.warning("Cooling request: simulated temperature is above the selected crop's demo target. A real system would need suitable cooling equipment.")
        else:
            st.success("No cooling request from the simple temperature rule.")
        if fan:
            st.info("Fan/ventilation: ON (simulated control decision).")
        else:
            st.info("Fan/ventilation: OFF (simulated control decision).")
        st.info(f"Roof louver: {roof}. Actual opening must also consider rain, outside humidity, pests, and food-safety requirements.")
        st.write(f"**Batch summary:** {storage['quantity']} kg of {storage['crop']} for {storage['duration']} days.")
        st.caption(f"Evaluated: {storage['time']}. No physical fan, cooling unit, or roof is connected.")
        if st.button("Create Crop Passport for this storage batch"):
            batch_id = f"CSX-{uuid.uuid4().hex[:8].upper()}"
            batch = {
                "id": batch_id, "crop": storage["crop"], "quantity": storage["quantity"],
                "duration": storage["duration"], "temperature": storage["temp"],
                "humidity": storage["humidity"], "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "field": st.session_state.last_field.get("field", "Demo Field"),
                "status": "In storage (demo)"
            }
            st.session_state.crop_batches.append(batch)
            st.success(f"Created crop batch {batch_id}. Open Crop Passport to view its QR code.")
    else:
        st.info("Choose the inputs and click **Evaluate storage conditions** to see the demo decision.")

# ---------- Direct Market ----------
elif page == "🛒 Direct Market":
    st.title("🛒 Direct Farmer-to-Consumer Market")
    farmer_tab, consumer_tab, order_tab = st.tabs(["👨‍🌾 Farmer: Add listing", "🛍️ Consumer: Place order", "📦 Orders"])
    with farmer_tab:
        st.markdown("### Add produce to marketplace")
        with st.form("listing_form", clear_on_submit=True):
            farmer = st.text_input("Farmer name", "New Farmer")
            listing_crop = st.selectbox("Crop", list(CROP_GUIDE.keys()), key="listing_crop")
            qty = st.number_input("Available quantity (kg)", min_value=1, max_value=100000, value=20)
            price = st.number_input("Price per kg (₹)", min_value=0.0, value=float(CROP_GUIDE[listing_crop]["price"]), step=1.0)
            location = st.text_input("Pickup location", "Farm Gate")
            submitted = st.form_submit_button("Publish listing")
        if submitted:
            listing_id = f"CSX-{uuid.uuid4().hex[:6].upper()}"
            st.session_state.listings.append({
                "id": listing_id, "crop": listing_crop, "quantity": int(qty),
                "price": float(price), "farmer": farmer, "location": location, "available": True
            })
            st.success(f"Listing published with batch/listing ID {listing_id}.")
        st.markdown("### Available listings")
        available = [x for x in st.session_state.listings if x["available"] and x["quantity"] > 0]
        if available:
            st.dataframe(pd.DataFrame(available), use_container_width=True, hide_index=True)
        else:
            st.info("No available listings yet.")
    with consumer_tab:
        available = [x for x in st.session_state.listings if x["available"] and x["quantity"] > 0]
        if not available:
            st.info("No produce currently available.")
        else:
            options = {f'{x["crop"]} · {x["farmer"]} · ₹{x["price"]:.2f}/kg · {x["quantity"]} kg available · {x["id"]}': x for x in available}
            with st.form("order_form"):
                selected_label = st.selectbox("Choose produce", list(options.keys()))
                selected = options[selected_label]
                buyer = st.text_input("Consumer name", "Demo Consumer")
                order_qty = st.number_input("Quantity (kg)", min_value=1, max_value=int(selected["quantity"]), value=1)
                fulfilment = st.radio("Fulfilment method", ["Pickup", "Farmer delivery"], horizontal=True)
                distance = 0.0
                if fulfilment == "Farmer delivery":
                    distance = st.number_input("Delivery distance (km)", min_value=0.0, max_value=500.0, value=5.0, step=0.5)
                delivery_rate = st.number_input("Delivery rate (₹ per km)", min_value=0.0, value=8.0, step=1.0)
                storage_days = st.number_input("Storage days to bill (0 if not used)", min_value=0, max_value=365, value=0)
                storage_rate = st.number_input("Storage charge (₹ per kg per day)", min_value=0.0, value=0.5, step=0.1)
                place_order = st.form_submit_button("Place demo order")
            if place_order:
                if order_qty > selected["quantity"]:
                    st.error("Requested quantity exceeds available stock.")
                else:
                    product_cost = float(order_qty) * float(selected["price"])
                    delivery_cost = float(distance) * float(delivery_rate) if fulfilment == "Farmer delivery" else 0.0
                    storage_cost = float(order_qty) * float(storage_days) * float(storage_rate) if storage_days > 0 else 0.0
                    total = product_cost + delivery_cost + storage_cost
                    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                    order = {
                        "order_id": order_id, "buyer": buyer, "crop": selected["crop"],
                        "farmer": selected["farmer"], "quantity": int(order_qty),
                        "product_cost": round(product_cost, 2), "storage_cost": round(storage_cost, 2),
                        "delivery_cost": round(delivery_cost, 2), "total": round(total, 2),
                        "fulfilment": fulfilment, "status": "Placed (demo)",
                        "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "listing_id": selected["id"]
                    }
                    st.session_state.orders.append(order)
                    selected["quantity"] -= int(order_qty)
                    st.success(f"Order placed! Reference: {order_id}")
                    st.markdown("#### Transparent bill")
                    st.write(f"Product: ₹{product_cost:.2f}")
                    st.write(f"Storage: ₹{storage_cost:.2f} ({'charged' if storage_days > 0 else 'not used'})")
                    st.write(f"Delivery: ₹{delivery_cost:.2f} ({fulfilment})")
                    st.markdown(f"### Total: ₹{total:.2f}")
                    st.caption("Demo checkout only: no real payment is collected.")
    with order_tab:
        if st.session_state.orders:
            st.dataframe(pd.DataFrame(st.session_state.orders), use_container_width=True, hide_index=True)
        else:
            st.info("No orders yet. Place a demo order from the Consumer tab.")

# ---------- Crop Passport ----------
elif page == "🔎 Crop Passport":
    st.title("🔎 Crop Passport & Traceability")
    st.write("A simple digital record for each batch, linking its crop details with the storage demonstration.")
    if not st.session_state.crop_batches:
        st.info("No tracked batches yet. Create one from Smart Storage.")
    else:
        batch_options = {f'{b["id"]} · {b["crop"]} · {b["quantity"]} kg': b for b in st.session_state.crop_batches}
        label = st.selectbox("Choose a crop batch", list(batch_options.keys()))
        batch = batch_options[label]
        left, right = st.columns([2, 1])
        with left:
            st.markdown("### Batch details")
            for key, value in batch.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            st.markdown("### Traceability journey")
            st.write("🌱 Field → 🏠 Smart Storage → 🛒 Marketplace → 🧑‍🍳 Consumer")
        with right:
            payload = (
                f"CropSyncX Crop Passport\nBatch ID: {batch['id']}\nCrop: {batch['crop']}\n"
                f"Quantity: {batch['quantity']} kg\nStorage duration: {batch['duration']} days\n"
                f"Status: {batch['status']}\nPrototype record only; verify data before real-world use."
            )
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(payload)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            st.image(qr_img, caption="Demo Crop Passport QR code", use_container_width=True)
            st.download_button(
                "Download QR code",
                data=image_bytes(qr_img),
                file_name=f"{batch['id']}_qr.png",
                mime="image/png",
            )

