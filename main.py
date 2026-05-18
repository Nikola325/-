import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import re

# ==================== НАСТРОЙКИ ====================
st.set_page_config(page_title="Сканер за Вредни Е-та", layout="wide")
st.title("🔍 Сканер за Вредни Вещества в Продукти")
st.markdown("**Качете снимка на етикета или въведете текст ръчно**")

# Инициализация на OCR (изтегля модела при първо стартиране)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr()

# ==================== БАЗА ДАННИ ====================
harmful_db = {
    "Захар / Сиропи": ["захар", "захароза", "глюкозо-фруктозен сироп", "фруктоза", "глюкоза", "E420", "E421"],
    "Палмово масло": ["палмово масло", "палмова мазнина", "palm oil"],
    "Натриев нитрит": ["e250", "натриев нитрит", "натриев нитрат", "e251"],
    "Аспартам": ["e951", "аспартам"],
    "Натриев бензоат": ["e211", "натриев бензоат"],
    "Мононатриев глутамат": ["e621", "глутамат", "msg"],
    "Транс мазнини": ["частично хидрогенирани", "транс мазнини", "hydrogenated"],
    "Изкуствени оцветители": ["e129", "allura red", "червено 40", "e102", "e110", "e124", "e133"],
    "Калиев сорбат / сорбинова киселина": ["e202", "сорбат"],
    "Сулфити": ["e220", "e221", "e222", "e223", "e224", "сулфит"],
    "BHA / BHT": ["e320", "e321", "bha", "bht"],
}

# ==================== ФУНКЦИИ ====================
def extract_text_from_image(image):
    img = Image.open(image).convert('RGB')
    result = reader.readtext(img, detail=0, paragraph=True)
    text = " ".join(result).lower()
    return text

def find_harmful_ingredients(text):
    detected = []
    text_lower = text.lower()
    
    for category, keywords in harmful_db.items():
        for keyword in keywords:
            if keyword in text_lower:
                match = re.search(r'\b.{0,30}' + re.escape(keyword) + r'.{0,30}\b', text_lower)
                context = match.group(0) if match else keyword
                detected.append({
                    "Категория": category,
                    "Открит термин": context.capitalize(),
                    "E-номер/Вещество": keyword.upper() if keyword.startswith('e') else keyword
                })
                break
    return detected

# ==================== ИНТЕРФЕЙС ====================
col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader("📸 Качи снимка на етикета", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Качена снимка", use_container_width=True)

with col2:
    manual_input = st.text_area("Или въведи съставките ръчно:", height=150, 
                               placeholder="Например: Вода, захар, глюкозо-фруктозен сироп, E211, палмово масло...")

# ==================== СКАНИРАНЕ ====================
if st.button("🚀 Сканирай за вредни вещества", type="primary"):
    text = ""
    
    if uploaded_file:
        with st.spinner("Извличане на текст от снимката..."):
            text = extract_text_from_image(uploaded_file)
            st.info(f"**Извлечен текст:**\n{text}")
    elif manual_input.strip():
        text = manual_input
    else:
        st.warning("Моля качете снимка или въведете текст.")
        st.stop()

    if text:
        detected = find_harmful_ingredients(text)
        
        if detected:
            st.error("⚠️ **НАМЕРЕНИ ВРЕДНИ ВЕЩЕСТВА!**")
            
            df = pd.DataFrame(detected)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.subheader("Препоръки:")
            st.markdown("""
            - Избягвай честата консумация на този продукт
            - Търси алтернативи без тези добавки
            - Особено внимавай ако има **E250, E621, транс мазнини или много захар**
            """)
        else:
            st.success("✅ Не са открити вредни вещества от базата.")
            st.info("Въпреки това винаги чети внимателно етикета – базата не е изчерпателна.")

# ==================== СТРАНИЧНА ЛЕНТА ====================
st.sidebar.header("ℹ️ За приложението")
st.sidebar.info("""
Това е локално Streamlit приложение, което:
- Използва **EasyOCR** за разпознаване на български и английски текст
- Търси най-често срещаните вредни добавки
""")

st.sidebar.markdown("### Примери за тестване:")
st.sidebar.code("""Кока-Кола
Чипс с палмово масло и E621
Колбас с E250, E621, нитрит""")

st.sidebar.markdown("### Инсталация:")
st.sidebar.code("""pip install streamlit easyocr pillow pandas opencv-python-headless
streamlit run app.py""", language="bash")
