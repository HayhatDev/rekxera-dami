import streamlit as st
import time
import random
from datetime import datetime

st.set_page_config(
    page_title="Rekxare Dami",
    page_icon="📚",
    initial_sidebar_state="collapsed"
)

# --- تهيئة الإحصائيات ---
if "total_study_seconds" not in st.session_state:
    st.session_state.total_study_seconds = 0
if "completed_sessions" not in st.session_state:
    st.session_state.completed_sessions = 0
if "last_subject" not in st.session_state:
    st.session_state.last_subject = "—"
if "study_history" not in st.session_state:
    st.session_state.study_history = []
    # --- الشريط الجانبي: لوحة الإحصائيات ---
with st.sidebar:
    st.title("📊 ئامارێن تە")
    st.divider()
    
    # تحويل الثواني إلى ساعات ودقائق
    total_minutes = st.session_state.total_study_seconds // 60
    hours = total_minutes // 60
    mins = total_minutes % 60
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱️ هەمی دەم", f"{hours} س {mins} خ")
    with col2:
        st.metric("✅ دانیشتن", st.session_state.completed_sessions)
    
    st.divider()
    st.write(f"📚 دویماهین دەرس: **{st.session_state.last_subject}**")
    
    # عرض آخر 3 جلسات
    if st.session_state.study_history:
        st.write("**📋 دویماهین چالاکی:**")
        for entry in st.session_state.study_history[-3:][::-1]:
            st.caption(entry)
    
    st.divider()
    if st.button("🧹 ئاماران پاک بکە"):
        st.session_state.total_study_seconds = 0
        st.session_state.completed_sessions = 0
        st.session_state.last_subject = "—"
        st.session_state.study_history = []
        st.rerun()
st.title("📚 Rekxare Dami | بو قوتابیان و خوێندەکاران")

# تهيئة session_state
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0
if "paused" not in st.session_state:
    st.session_state.paused = False
if "remaining_at_pause" not in st.session_state:
    st.session_state.remaining_at_pause = 0

nav = st.text_input("ناڤێ خوە بنڤیسە:", "قوتابی")
if nav:
    st.write(f"بخێر هاتێ {nav}! 🌟")

ders = st.selectbox("تو كيژ دەرسێ دخوینی؟", 
    ["🧮 بیرکاری", "⚛️ فیزیا", "🧪 کیمیا", "🇬🇧 ئینگلیزی", 
     "🧬 زیندەوەرزانی", "📜 مێژوو", "🌍 جوگرافیا", "💻 کۆمپیوتەر","ئايين  ☪️"])

deqe = st.slider("چەند دەقیقە؟", 1, 90, 25)

total_seconds = deqe * 60

# أزرار التحكم (تتغير حسب الحالة)
col1, col2, col3 = st.columns(3)

with col1:
    if not st.session_state.timer_running and not st.session_state.paused:
        dest_pe_bike = st.button("🚀 دەست پێ بکە")
    elif st.session_state.paused:
        resume = st.button("▶️ بەردەوام بە")
    else:
        st.button("🚀 دەست پێ بکە", disabled=True)

with col2:
    if st.session_state.timer_running:
        stop_timer = st.button("⏸️ راوەستاندن")
    elif st.session_state.paused:
        stop_timer = st.button("⏸️ راوەستاندن", disabled=True)
    else:
        st.button("⏸️ راوەستاندن", disabled=True)

with col3:
    dubare = st.button("🔄 دووبارە")

hezt = ["بەردەوام بە!", "تو دێ سەرکەڤێ!", "ئەڤ چەندە باشە!", "بەرێ خوە بدە ئارمانجان!"]

# منطق الأزرار
if "dest_pe_bike" in locals() and dest_pe_bike:
    st.session_state.timer_running = True
    st.session_state.paused = False
    st.session_state.end_time = time.time() + total_seconds
    st.session_state.total_seconds = total_seconds
    st.rerun()

if "resume" in locals() and resume:
    st.session_state.timer_running = True
    st.session_state.paused = False
    st.session_state.end_time = time.time() + st.session_state.remaining_at_pause
    st.rerun()

if "stop_timer" in locals() and stop_timer:
    st.session_state.timer_running = False
    st.session_state.paused = True
    st.session_state.remaining_at_pause = st.session_state.end_time - time.time()
    st.rerun()

if dubare:
    # إذا كان المؤقت يعمل، نوقفه بدون تسجيل الجلسة
    st.session_state.timer_running = False
    st.session_state.paused = False
    st.session_state.end_time = None
    st.session_state.total_seconds = 0
    st.session_state.remaining_at_pause = 0
    st.rerun()

# عرض المؤقت أو حالة الإيقاف
if st.session_state.timer_running and st.session_state.end_time:
    remaining = st.session_state.end_time - time.time()
    if remaining > 0:
        mins, secs = divmod(int(remaining), 60)
        progress = 1 - (remaining / st.session_state.total_seconds)
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 20px;">
            <div style="position: relative; width: 200px; height: 200px;">
                <svg width="200" height="200" viewBox="0 0 36 36">
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#333" stroke-width="2"/>
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831" fill="none" stroke="#4CAF50" stroke-width="2" stroke-dasharray="{progress * 100}, 100"/>
                    <text x="18" y="20.5" text-anchor="middle" fill="white" font-size="8" font-weight="bold">{mins:02d}:{secs:02d}</text>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success(f"✅ باشە {nav}! تو دێ {deqe} دەقیقان بۆ {ders} تەرخان دکەی.")
        st.info(f"💬 {random.choice(hezt)}")
        time.sleep(1)
        st.rerun()
        else:
        # تمت الجلسة بنجاح
        st.session_state.timer_running = False
        st.session_state.paused = False
        
        # إضافة الوقت إلى الإحصائيات
        st.session_state.total_study_seconds += st.session_state.total_seconds
        st.session_state.completed_sessions += 1
        
        # استخراج اسم المادة بدون الإيموجي
        subject_name = ders.split(" ", 1)[1] if " " in ders else ders
        
        # تحديث آخر مادة
        st.session_state.last_subject = subject_name
        
        # إضافة إلى السجل
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        minutes = st.session_state.total_seconds // 60
        st.session_state.study_history.append(f"{now} - {subject_name} ({minutes} خ)")
        
        st.balloons()
        st.success("🎉 وەختی تە تەواو بوو! هێژا تە!")
elif st.session_state.paused and st.session_state.remaining_at_pause > 0:
    # عرض الدائرة متوقفة
    mins, secs = divmod(int(st.session_state.remaining_at_pause), 60)
    progress = 1 - (st.session_state.remaining_at_pause / st.session_state.total_seconds)
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin: 20px;">
        <div style="position: relative; width: 200px; height: 200px;">
            <svg width="200" height="200" viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831" fill="none" stroke="#FFA500" stroke-width="2" stroke-dasharray="{progress * 100}, 100"/>
                <text x="18" y="20.5" text-anchor="middle" fill="white" font-size="8" font-weight="bold">{mins:02d}:{secs:02d}</text>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.warning(f"⏸️ دەم هاتە راوەستاندن. {deqe} دەقیقان بۆ {ders}")
elif not st.session_state.timer_running and not st.session_state.paused and st.session_state.total_seconds > 0:
    # عرض الدائرة بعد إعادة الضبط (فارغة أو ممتلئة حسب الحالة)
    st.info("🔄 دەم هاتە راوەستاندن. دووبارە دەست پێ بکە.")
