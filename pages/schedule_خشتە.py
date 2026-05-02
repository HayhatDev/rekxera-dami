import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="خشتەیێ حەفتیانە",
    page_icon="📅"
)

st.title("📅 خشتەیێ حەفتیانە")

# --- تهيئة الجدول الأسبوعي ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {
        "sun": [], "mon": [], "tue": [], "wed": [], "thu": [], "fri": [], "sat": [],
    }

# متغيرات إعادة الضبط لكل يوم
for day in ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]:
    if f"{day}_reset" not in st.session_state:
        st.session_state[f"{day}_reset"] = 0

# أسماء الأيام
days = [
    ("sun", "☀️ ئێکشەمب"), ("mon", "📖 دووشەمب"), ("tue", "📖 سێشەمب"),
    ("wed", "📖 چارشەمب"), ("thu", "📖 پێنجشەمب"), ("fri", "🕌 خودبە"), ("sat", "🎉 شەمبی"),
]

for day_key, day_name in days:
    st.write(f"### {day_name}")
    
    schedule = st.session_state.schedule[day_key]
    
    if not schedule:
        schedule.append({"start": "07:00", "end": "08:00", "task": "", "done": False})
    
    for i, entry in enumerate(schedule):
        col_time, col_done, col_task, col_delete = st.columns([2, 1, 5, 1])
        
        with col_time:
            start_time = st.time_input(
                "دەستپێک",
                value=datetime.strptime(entry["start"], "%H:%M").time() if entry["start"] else datetime.time(7, 0),
                key=f"{day_key}_start_{i}_{st.session_state[f'{day_key}_reset']}",
                label_visibility="collapsed"
            )
            end_time = st.time_input(
                "دووماهی",
                value=datetime.strptime(entry["end"], "%H:%M").time() if entry["end"] else datetime.time(8, 0),
                key=f"{day_key}_end_{i}_{st.session_state[f'{day_key}_reset']}",
                label_visibility="collapsed"
            )
        
        with col_done:
            done = st.checkbox(
                "✅",
                value=entry["done"],
                key=f"{day_key}_done_{i}_{st.session_state[f'{day_key}_reset']}",
                label_visibility="collapsed"
            )
        
        with col_task:
            task_text = st.text_input(
                "چالاکی",
                value=entry["task"],
                key=f"{day_key}_task_{i}_{st.session_state[f'{day_key}_reset']}",
                disabled=done,
                label_visibility="collapsed"
            )
        
        with col_delete:
            delete_btn = st.button("🗑️", key=f"{day_key}_del_{i}_{st.session_state[f'{day_key}_reset']}")
        
        entry["task"] = task_text
        entry["done"] = done
        entry["start"] = start_time.strftime("%H:%M")
        entry["end"] = end_time.strftime("%H:%M")
        
        if delete_btn:
            schedule.pop(i)
            st.session_state[f"{day_key}_reset"] += 1
            st.session_state.schedule[day_key] = schedule
            st.rerun()
    
    if st.button("+ ئەرکێ نوی", key=f"{day_key}_add_{st.session_state[f'{day_key}_reset']}"):
        schedule.append({"start": "08:00", "end": "09:00", "task": "", "done": False})
        st.session_state.schedule[day_key] = schedule
        st.rerun()
    
    st.divider()
