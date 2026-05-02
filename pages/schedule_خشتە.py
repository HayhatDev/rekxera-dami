import streamlit as st
from datetime import datetime
import json
import os

SCHEDULE_FILE = "schedule_data.json"

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_schedule():
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.schedule, f, ensure_ascii=False, indent=2)

st.set_page_config(
    page_title="خشتەیێ حەفتیانە",
    page_icon="📅"
)

st.title("📅 خشتەیێ حەفتیانە")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- تهيئة الجدول الأسبوعي ---
if "schedule" not in st.session_state:
    loaded = load_schedule()
    if loaded:
        st.session_state.schedule = loaded
    else:
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

# إنشاء ألسنة للأيام
tab_labels = [day_name for _, day_name in days]
tab_keys = [day_key for day_key, _ in days]
tabs = st.tabs(tab_labels)

for tab, day_key, day_name in zip(tabs, tab_keys, tab_labels):
    with tab:
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
            
            if entry["done"] != done:
                entry["done"] = done
                save_schedule()
            
            entry["task"] = task_text
            entry["start"] = start_time.strftime("%H:%M")
            entry["end"] = end_time.strftime("%H:%M")
            
            if delete_btn:
                schedule.pop(i)
                st.session_state[f"{day_key}_reset"] += 1
                st.session_state.schedule[day_key] = schedule
                save_schedule()
                st.rerun()
        
        if st.button("+ ئەرکێ نوی", key=f"{day_key}_add_{st.session_state[f'{day_key}_reset']}"):
            schedule.append({"start": "08:00", "end": "09:00", "task": "", "done": False})
            st.session_state.schedule[day_key] = schedule
            save_schedule()
            st.rerun()

# --- تطبيق الوضع الليلي والتشطيب ---
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp {
            background-color: #1a1a2e;
        }
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: #16213e;
        }
        .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label {
            color: #e0e0e0 !important;
        }
        .stTextInput input, .stSelectbox select, .stTimeInput input {
            background-color: #2d2d44;
            color: #ffffff;
            border: 1px solid #444;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
        }
        input[disabled] {
            text-decoration: line-through;
            color: #888 !important;
            background-color: #2d2d44 !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        input[disabled] {
            text-decoration: line-through;
            color: #888 !important;
        }
    </style>
    """, unsafe_allow_html=True)
