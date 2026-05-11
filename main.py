import streamlit as st
import pandas as pd

st.set_page_config(page_title="Сканер за Вредни Вещества", layout="wide")
st.title("🔍 Сканер за Вредни Вещества в Продукти")

product_input = st.text_input("Въведи име на продукт, баркод или списък с съставки:")

if st.button("Сканирай продукт"):
    if product_input:
        input_lower = product_input.lower()
        
        harmful_db = {
            "захар": ["Захароза", "Глюкозо-фруктозен сироп", "Фруктоза"],
            "палмово масло": ["Палмово масло", "Палмова мазнина"],
            "натриев нитрит": ["E250", "Натриев нитрит"],
            "аспартам": ["E951", "Аспартам"],
            "бензоат": ["E211", "Натриев бензоат"],
            "глутамат": ["E621", "Мононатриев глутамат"],
            "транс мазнини": ["Частично хидрогенирани масла"],
            "червено 40": ["E129", "Allura Red"]
        }
        
        detected = []
        for key, names in harmful_db.items():
            for name in names:
                if name.lower() in input_lower or key in input_lower:
                    detected.append((key.capitalize(), name))
        
        if detected:
            st.error("⚠️ Намерени вредни вещества!")
            df = pd.DataFrame(detected, columns=["Вредно вещество", "Открит термин"])
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Препоръки:")
            st.write("• Избягвай честа консумация на този продукт")
            st.write("• Потърси алтернативи без добавки")
        else:
            st.success("✅ Не са открити вредни вещества в базата данни.")
            st.info("Винаги проверявай етикета внимателно!")
    else:
        st.warning("Моля въведи продукт или съставки.")

st.sidebar.header("За проекта")
st.sidebar.info("Това е демо приложение за домашно. Сканира текст и търси често срещани вредни добавки.")

st.sidebar.markdown("### Примерни продукти за тестване:")
st.sidebar.code("""Кока Кола (захар, E211)
Чипс с палмово масло
Колбаси с E250 и E621""")
