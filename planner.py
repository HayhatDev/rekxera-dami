import streamlit as st
import random

st.set_page_config(page_title="Rekxare Dami", page_icon="📚")

st.title("📚 Rekxare Dami | بو قوتابیان و خوێندەکاران")

nav = st.text_input("ناڤێ خوە بنڤیسە:", "قوتابی")
if nav:
    st.write(f"بخێرهاتێ {nav}! 🌟")

st.write("ئەڤ ئامیرە هاریکاریا تە دکەت بۆ ڕێکخستنا دەمی خۆاندنا ته")

ders = st.selectbox("تو كيژ دەرسێ دخوینی؟", ["بیرکاری", "فیزیا","عەرەبی","جوگرافیا","مێژوو","کۆمپیوتەر","زیندەوەرزانی","کوردی", "کیمیا", "ئینگلیزی"])

deqe = st.slider("چەند دەقیقە؟", 5, 120, 25)
st.progress(deqe / 120)  # شريط تقدم بصري

col1, col2 = st.columns(2)
with col1:
    dest_pe_bike = st.button("🚀 دەست پێ بکە")
with col2:
    dubare = st.button("🔄 دووبارە")
hezt = [ "!بەردەوام بە!", "تو دێ سەرکەڤێ!", "ئەڤ چەندە باشە!", "بەرێ خوە بدە ئارمانجان"]
if dest_pe_bike:
    st.success(f"✅ باشە {nav}! تو دێ {deqe} دەقیقان بۆ {ders} تەرخان دکەی.")
    st.info("⏳ پشتی خواندنێ، دووبارە ڤەگەڕە بو ڤی ئامیرەی.")
    st.balloons()
    st.info(f"💬 {random.choice(hezt)}")
    

if dubare:
    st.rerun()


