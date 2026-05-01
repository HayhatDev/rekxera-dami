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
        "sun": [],
        "mon": [],
        "tue": [],
        "wed": [],
        "thu": [],
        "fri": [],
        "sat": [],
    }

if "sun_reset" not in st.session_state:
    st.session_state.sun_reset = 0

# --- ئێکشەمب ---
st.write("### ☀️ ئێکشەمب")

sun_schedule = st.session_state.schedule["sun"]

if not sun_schedule:
    sun_schedule.append({"start": "07:00", "end": "08:00", "task": "", "done": False})

for i, entry in enumerate(sun_schedule):
    col_time, col_done, col_task, col_delete = st.columns([2, 1, 5, 1])
    
    with col_time:
        start_time = st.time_input(
            "دەستپێک",
            value=datetime.strptime(entry["start"], "%H:%M").time() if entry["start"] else datetime.time(7, 0),
            key=f"sun_start_{i}_{st.session_state.sun_reset}",
            label_visibility="collapsed"
        )
        end_time = st.time_input(
            "دووماهی",
            value=datetime.strptime(entry["end"], "%H:%M").time() if entry["end"] else datetime.time(8, 0),
            key=f"sun_end_{i}_{st.session_state.sun_reset}",
            label_visibility="collapsed"
        )
    
    with col_done:
        done = st.checkbox(
            "✅",
            value=entry["done"],
            key=f"sun_done_{i}_{st.session_state.sun_reset}",
            label_visibility="collapsed"
        )
    
    with col_task:
        task_text = st.text_input(
            "چالاکی",
            value=entry["task"],
            key=f"sun_task_{i}_{st.session_state.sun_reset}",
            disabled=done,
            label_visibility="collapsed"
        )
    
    with col_delete:
        delete_btn = st.button("🗑️", key=f"sun_del_{i}_{st.session_state.sun_reset}")
    
    entry["task"] = task_text
    entry["done"] = done
    entry["start"] = start_time.strftime("%H:%M")
    entry["end"] = end_time.strftime("%H:%M")
    
    if delete_btn:
        sun_schedule.pop(i)
        st.session_state.sun_reset += 1
        st.session_state.schedule["sun"] = sun_schedule
        st.rerun()

if st.button("+ ئەرکێ نوی", key=f"sun_add_{st.session_state.sun_reset}"):
    sun_schedule.append({"start": "08:00", "end": "09:00", "task": "", "done": False})
    st.session_state.schedule["sun"] = sun_schedule
    st.rerun()
