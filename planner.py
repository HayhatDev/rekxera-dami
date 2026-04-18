import streamlit as st

st.set_page_config(page_title="Rekxare Dami", page_icon="📚")

st.title("📚 Rekxare Dami Ji Bo Xwendekaran")

st.write("ئەم ئامێرە هاریکاری تە دکەت بۆ ڕێکخستنا دەمی خۆندنا تە.")

ders = st.selectbox("تو کێژان دەرسێ دخوینی؟", ["بیرکاری", "فیزیا", "کیمیا", "ئینگلیزی"])

deqe = st.slider("چەند دەقیقە؟", 5, 60, 25)

if st.button("دەست پێ بکە"):
    st.success(f"✅ باشە! تو ئێ {deqe} دەقیقان بۆ {ders} تەرخان دکەی.")
    st.info("پشتی قەداندنێ، دووبارە ڤەگەڕە بو ئەم ئامێرێ.")
