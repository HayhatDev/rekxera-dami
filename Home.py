import streamlit as st
import time
import random
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import pandas as pd
import base64
import json
import os
import hashlib
from utils import save_data, load_data, save_preferences, load_preferences, get_schedule_data


# ── Translations
with open("translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

# ── Session-state guards (app.py sets these, but guard anyway)
if "lang" not in st.session_state:
    st.session_state.lang = "badini"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "data_key" not in st.session_state:
    st.session_state.data_key = "default"
if "user_email" not in st.session_state:
    st.session_state.user_email = ""


def t(key, **kwargs):
    text = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["badini"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text



if st.user.is_logged_in and "user_email" not in st.session_state:
    st.session_state.user_email = st.user.email
    st.session_state.data_key   = st.user.email.split("@")[0]
    st.session_state.logged_in  = True
    load_data()
    st.rerun()


if st.user.is_logged_in:
    st.session_state.data_key = st.user.email.split("@")[0]
    
SUBJECT_COLOR_LIST = [
    "#2196F3", "#9C27B0", "#FF5722", "#00BCD4",
    "#4CAF50", "#795548", "#FF9800", "#607D8B", "#FFC107",
]


def subject_color(label: str) -> str:
    _subjects = t("subjects")
    if not isinstance(_subjects, list):
        _subjects = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["badini"]).get("subjects", [])
    
    try:
        idx = _subjects.index(label)
        return SUBJECT_COLOR_LIST[idx % len(SUBJECT_COLOR_LIST)]
    except (ValueError, IndexError):
        return "#4CAF50"

def get_greeting():
    h = datetime.now().hour
    if 5 <= h < 12:
        return t("greeting_morning"), t("greeting_morning_en")
    elif 12 <= h < 17:
        return t("greeting_afternoon"), t("greeting_afternoon_en")
    elif 17 <= h < 21:
        return t("greeting_evening"), t("greeting_evening_en")
    else:
        return t("greeting_night"), t("greeting_night_en")


def load_today_schedule():
    today_map = {6: "sun", 0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat"}
    today_key = today_map[datetime.now().weekday()]
    schedule = get_schedule_data()
    return today_key, schedule.get(today_key, [])

def total_day_minutes(day_entries):
    total = 0
    for e in day_entries:
        if not e.get("task", "").strip():
            continue
        try:
            s   = datetime.strptime(e.get("start", "00:00"), "%H:%M")
            end = datetime.strptime(e.get("end", "00:00"), "%H:%M")
            diff = int((end - s).total_seconds() // 60)
            if diff > 0:
                total += diff
        except Exception:
            pass
    return total
    
# ── Defaults
DEFAULTS = {
    "total_study_seconds": 0, "completed_sessions": 0,
    "last_subject": "—", "study_history": [], "dark_mode": True,
    "streak": 0, "last_study_date": "", "daily_seconds": 0,
    "daily_goal_seconds": 7200, "timer_running": False,
    "end_time": None, "total_seconds": 0, "paused": False,
    "remaining_at_pause": 0, "student_name": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

if "quote_idx" not in st.session_state:
    st.session_state.quote_idx = random.randint(0, 99)

# ── Daily reset
today_str = date.today().isoformat()
if (st.session_state.last_study_date
        and st.session_state.last_study_date != today_str
        and st.session_state.daily_seconds > 0):
    st.session_state.daily_seconds = 0
    save_data()

is_dark        = st.session_state.dark_mode
total_minutes  = st.session_state.total_study_seconds // 60
hours_total    = total_minutes // 60
mins_total     = total_minutes % 60
daily_pct      = min(100, int(st.session_state.daily_seconds /
                               max(1, st.session_state.daily_goal_seconds) * 100))
daily_done_min = st.session_state.daily_seconds // 60
daily_goal_min = st.session_state.daily_goal_seconds // 60
today_h        = st.session_state.daily_seconds // 3600
today_m        = (st.session_state.daily_seconds % 3600) // 60

_days_map = {"badini": "رۆژ", "english": "days", "arabic": "أيام"}
days_lbl  = _days_map.get(st.session_state.lang, "رۆژ")

# ══════════════════════════════════════════════════════════
#  COLOUR TOKENS
# ══════════════════════════════════════════════════════════
if is_dark:
    APP_BG         = "#1a1a2e"
    SB_BG          = "#16213e"
    CARD_BG        = "rgba(255,255,255,0.06)"
    CARD_BORDER    = "rgba(255,255,255,0.09)"
    TEXT_PRIMARY   = "#e2e2e2"
    TEXT_MUTED     = "#8a8fa8"
    SECTION_LBL    = "#555c72"
    TAG_BG         = "rgba(76,175,80,0.18)"
    TAG_COLOR      = "#81c784"
    ACTIVITY_BG    = "rgba(255,255,255,0.04)"
    SETTINGS_BG    = "rgba(255,255,255,0.04)"
    SETTINGS_BDR   = "rgba(255,255,255,0.08)"
    INPUT_BG       = "#252542"
    BTN_BG         = "#252542"
    BTN_COLOR      = "#e2e2e2"
    BTN_BORDER     = "#3a3a5c"
    TIMER_TRACK    = "#252542"
    TIMER_TEXT     = "#ffffff"
    TIMER_CARD_BG  = "rgba(255,255,255,0.04)"
    TIMER_CARD_BDR = "rgba(255,255,255,0.09)"
    PROG_TRACK     = "rgba(255,255,255,0.10)"
    GREET_BG       = "rgba(255,255,255,0.05)"
    GREET_BDR      = "rgba(255,255,255,0.09)"
    DIVIDER        = "rgba(255,255,255,0.08)"
    LANG_ACTIVE_BG = "rgba(76,175,80,0.25)"
    LANG_ACTIVE_C  = "#81c784"
    LANG_IDLE_BG   = "rgba(255,255,255,0.06)"
    LANG_IDLE_C    = "#8a8fa8"
    TODAY_CARD_BG  = "rgba(76,175,80,0.10)"
    TODAY_CARD_BDR = "rgba(76,175,80,0.20)"
    WARN_BG        = "rgba(255,152,0,0.12)"
    WARN_BDR       = "rgba(255,152,0,0.25)"
    WARN_COLOR     = "#ffb74d"
    DANGER_BG      = "rgba(239,83,80,0.12)"
    DANGER_BDR     = "rgba(239,83,80,0.25)"
    DANGER_COLOR   = "#ef9a9a"
    SCHED_BG       = "rgba(255,255,255,0.04)"
    SCHED_BDR      = "rgba(255,255,255,0.10)"
    SCHED_DONE_BG  = "rgba(76,175,80,0.10)"
    SCHED_TODO_BG  = "rgba(255,255,255,0.03)"
    QUOTE_BG       = "rgba(255,255,255,0.04)"
    QUOTE_BDR      = "rgba(255,255,255,0.08)"
    QUOTE_COLOR    = "#c5cae9"
    SETUP_BG       = "rgba(255,255,255,0.04)"
    SETUP_BDR      = "rgba(255,255,255,0.09)"
    GOAL_WIN_BG    = "rgba(76,175,80,0.14)"
    GOAL_WIN_BDR   = "rgba(76,175,80,0.30)"
    PRESET_BG      = "rgba(255,255,255,0.06)"
    PRESET_BDR     = "rgba(255,255,255,0.10)"
else:
    APP_BG         = "#e8edf5"
    SB_BG          = "#f4f7fb"
    CARD_BG        = "#ffffff"
    CARD_BORDER    = "#dde3ed"
    TEXT_PRIMARY   = "#1a1a2e"
    TEXT_MUTED     = "#6b7280"
    SECTION_LBL    = "#9ca3af"
    TAG_BG         = "rgba(76,175,80,0.10)"
    TAG_COLOR      = "#2e7d32"
    ACTIVITY_BG    = "#dde5f0"
    SETTINGS_BG    = "#dde5f0"
    SETTINGS_BDR   = "#c8d4e8"
    INPUT_BG       = "#ffffff"
    BTN_BG         = "#dde5f0"
    BTN_COLOR      = "#1a1a2e"
    BTN_BORDER     = "#c0cce0"
    TIMER_TRACK    = "#dde3ed"
    TIMER_TEXT     = "#1a1a2e"
    TIMER_CARD_BG  = "#ffffff"
    TIMER_CARD_BDR = "#dde3ed"
    PROG_TRACK     = "#dde3ed"
    GREET_BG       = "#ffffff"
    GREET_BDR      = "#dde3ed"
    DIVIDER        = "#dde3ed"
    LANG_ACTIVE_BG = "rgba(76,175,80,0.12)"
    LANG_ACTIVE_C  = "#2e7d32"
    LANG_IDLE_BG   = "#edf0f7"
    LANG_IDLE_C    = "#6b7280"
    TODAY_CARD_BG  = "rgba(76,175,80,0.07)"
    TODAY_CARD_BDR = "rgba(76,175,80,0.18)"
    WARN_BG        = "#fff8e1"
    WARN_BDR       = "#ffe082"
    WARN_COLOR     = "#e65100"
    DANGER_BG      = "#ffebee"
    DANGER_BDR     = "#ef9a9a"
    DANGER_COLOR   = "#c62828"
    SCHED_BG       = "#ffffff"
    SCHED_BDR      = "#dde3ed"
    SCHED_DONE_BG  = "rgba(76,175,80,0.07)"
    SCHED_TODO_BG  = "#f9fafb"
    QUOTE_BG       = "#ffffff"
    QUOTE_BDR      = "#dde3ed"
    QUOTE_COLOR    = "#3949ab"
    SETUP_BG       = "#ffffff"
    SETUP_BDR      = "#dde3ed"
    GOAL_WIN_BG    = "rgba(76,175,80,0.08)"
    GOAL_WIN_BDR   = "rgba(76,175,80,0.22)"
    PRESET_BG      = "#edf0f7"
    PRESET_BDR     = "#c0cce0"

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

/* ── Base ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"],
.main .block-container {{
    background-color: {APP_BG} !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}}
[data-testid="stSidebar"] {{ background-color: {SB_BG} !important; }}
.stApp *, [data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY} !important; }}
h1, h2, h3 {{ font-weight: 800 !important; letter-spacing: -0.3px; }}

/* ── MOBILE: prevent double-tap zoom ── */
button, input, select, textarea, label {{
    touch-action: manipulation !important;
}}

/* ── MOBILE: safe-area insets for notched phones ── */
.main .block-container {{
    padding-left:   max(1rem, env(safe-area-inset-left))   !important;
    padding-right:  max(1rem, env(safe-area-inset-right))  !important;
    padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
}}

/* ── Text / time inputs (16px → no iOS auto-zoom) ── */
.stTextInput input,
.stTimeInput input {{
    background-color: {INPUT_BG} !important;
    border: 1.5px solid {CARD_BORDER} !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    padding: 10px 14px !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    min-height: 48px !important;
}}

/* ── Selectbox — kept separate so height:auto prevents text clipping ── */
.stSelectbox [data-baseweb="select"] {{
    background-color: {INPUT_BG} !important;
    border: 1.5px solid {CARD_BORDER} !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    overflow: visible !important;
}}
/* The inner clickable row — height:auto lets wrapped text breathe */
.stSelectbox [data-baseweb="select"] > div:first-child {{
    height: auto !important;
    min-height: 48px !important;
    padding: 10px 44px 10px 14px !important;
    overflow: visible !important;
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    line-height: 1.4 !important;
    display: flex !important;
    align-items: center !important;
}}
.stTextInput input:focus {{
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 3px rgba(76,175,80,0.15) !important;
    outline: none !important;
}}
/* ── Enhanced Card Styles ── */
.stats-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: default;
    position: relative;
    overflow: hidden;
}}
.stats-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    opacity: 0;
    transition: opacity 0.3s ease;
}}
.stats-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.15);
}}
.stats-card:hover::before {{
    opacity: 1;
}}
.stats-card:active {{
    transform: scale(0.97);

}}
/* ── Glassmorphism for cards (dark mode) ── */
.glass-card {{
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}}
/* ── Top Navigation Bar Styling ── */
.stApp > header {{
    background: rgba(26, 26, 46, 0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 4px 16px !important;
}}
/* ── Show sidebar toggle ── */
[data-testid="collapsedControl"] {{
    display: flex !important;
}}
.stSidebarCollapse {{
    display: flex !important;
}}
[data-testid="stSidebarCollapse"] {{
    display: flex !important;
}}
.stApp > header a {{
    color: #e2e2e2 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}

.stApp > header a:hover {{
    background: rgba(76, 175, 80, 0.12) !important;
    color: #4CAF50 !important;
}}

.stApp > header a[aria-current="page"] {{
    background: rgba(76, 175, 80, 0.15) !important;
    color: #4CAF50 !important;
}}

/* ── Radio language switcher ── */
[data-testid="stRadio"] > div {{ gap: 8px !important; flex-wrap: wrap !important; }}
[data-testid="stRadio"] label {{
    background: {LANG_IDLE_BG} !important;
    color: {LANG_IDLE_C} !important;
    border-radius: 20px !important;
    padding: 8px 18px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border: 1.5px solid {CARD_BORDER} !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    min-height: 44px !important;
    display: flex !important; align-items: center !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background: {LANG_ACTIVE_BG} !important;
    color: {LANG_ACTIVE_C} !important;
    border-color: {LANG_ACTIVE_C} !important;
}}
[data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}

/* ── Buttons (48px min touch target per Apple HIG) ── */
.stButton > button {{
    background-color: {BTN_BG}    !important;
    color:            {BTN_COLOR} !important;
    border:           1.5px solid {BTN_BORDER} !important;
    border-radius:    12px !important;
    font-weight:      600  !important;
    font-size:        15px !important;
    font-family:      'Inter', system-ui, sans-serif !important;
    padding:          12px 16px !important;
    min-height:       48px !important;
    transition:       all 0.18s ease !important;
    width:            100% !important;
    -webkit-tap-highlight-color: transparent !important;
    letter-spacing:   0.1px !important;
}}
.stButton > button:hover:not(:disabled) {{
    filter: brightness(1.07) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12) !important;
}}
.stButton > button:active:not(:disabled) {{
    transform: translateY(0px) !important;
    box-shadow: none !important;
}}
.stButton > button:disabled {{ opacity: 0.35 !important; cursor: not-allowed !important; }}

/* ── Timer control buttons (green start / orange pause) ── */
.tcb-anchor {{ display: none !important; }}
.element-container:has(.tcb-anchor) + div
    [data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton button:not(:disabled) {{
    background: linear-gradient(135deg, #43a047, #66bb6a) !important;
    color: #fff !important; border-color: #388e3c !important;
    box-shadow: 0 3px 12px rgba(67,160,71,0.35) !important;
}}
.element-container:has(.tcb-anchor) + div
    [data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button:not(:disabled) {{
    background: linear-gradient(135deg, #ef6c00, #ffa726) !important;
    color: #fff !important; border-color: #e65100 !important;
    box-shadow: 0 3px 12px rgba(239,108,0,0.30) !important;
}}
/* Style download buttons to match default .stButton */
.stDownloadButton button {{
    background-color: {BTN_BG} !important;
    color: {BTN_COLOR} !important;
    border: 1.5px solid {BTN_BORDER} !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    min-height: 48px !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
}}
.stDownloadButton button:hover {{
    filter: brightness(1.07) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12) !important;
}}
.stDownloadButton button:active {{
    transform: translateY(0px) !important;
    box-shadow: none !important;
}}
/* ── Preset buttons ── */
.preset-anchor {{ display: none !important; }}
.element-container:has(.preset-anchor) + div
    [data-testid="stHorizontalBlock"] .stButton button {{
    background: {PRESET_BG} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1.5px solid {PRESET_BDR} !important;
    border-radius: 20px !important;
    font-size: 13px !important;
    padding: 8px 4px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}}
.element-container:has(.preset-anchor) + div
    [data-testid="stHorizontalBlock"] .stButton button:hover:not(:disabled) {{
    border-color: #4CAF50 !important;
    color: #4CAF50 !important;
    background: {TAG_BG} !important;
    box-shadow: none !important;
}}

/* ── Cards ── */
.timer-card {{
    background: {TIMER_CARD_BG}; border: 1.5px solid {TIMER_CARD_BDR};
    border-radius: 24px; padding: 28px 16px 20px;
    margin: 8px 0 16px; text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}}
.timer-card svg {{
    width: min(260px, 80vw) !important;
    height: min(260px, 80vw) !important;
}}
.setup-card {{
    background: {SETUP_BG}; border: 1.5px solid {SETUP_BDR};
    border-radius: 18px; padding: 18px 20px; margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}}
.quote-card {{
    background: {QUOTE_BG}; border: 1.5px solid {QUOTE_BDR};
    border-radius: 18px; padding: 20px 22px;
    margin: 4px 0 14px; position: relative;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}}
.quote-mark {{
    font-size: 48px; line-height: 1; opacity: 0.12;
    position: absolute; top: 10px; left: 16px;
    font-family: Georgia, serif;
}}
.quote-text {{
    font-size: 14px; font-weight: 500; font-style: italic;
    color: {QUOTE_COLOR} !important; line-height: 1.65;
    padding-left: 26px; padding-right: 8px;
}}
.paused-banner {{
    background: {WARN_BG}; border: 1.5px solid {WARN_BDR};
    border-radius: 12px; padding: 14px 18px; text-align: center;
    font-size: 14px; font-weight: 700; color: {WARN_COLOR} !important;
    margin-bottom: 8px;
}}
.goal-win-banner {{
    background: {GOAL_WIN_BG}; border: 1.5px solid {GOAL_WIN_BDR};
    border-radius: 16px; padding: 16px 20px;
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 16px;
    box-shadow: 0 3px 16px rgba(76,175,80,0.14);
}}
.goal-win-icon {{ font-size: 36px; line-height: 1; flex-shrink: 0; }}
.goal-win-text {{ font-size: 14px; font-weight: 800; color: #4CAF50 !important; }}
.goal-win-sub  {{ font-size: 12px; color: {TEXT_MUTED} !important; margin-top: 3px; }}
.subject-color-dot {{
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 7px; flex-shrink: 0; vertical-align: middle;
}}
.subject-pill {{
    display: inline-flex; align-items: center;
    background: {TAG_BG}; color: {TAG_COLOR} !important;
    border-radius: 20px; padding: 6px 14px;
    font-size: 13px; font-weight: 700; margin-bottom: 12px;
}}
.section-hdr {{
    display: flex; align-items: center; gap: 8px;
    font-size: 11px; font-weight: 800; letter-spacing: 1.2px;
    text-transform: uppercase; color: {SECTION_LBL} !important;
    margin: 22px 0 12px;
}}
.section-hdr span {{ color: {SECTION_LBL} !important; }}
.section-line {{ flex: 1; height: 1px; background: {DIVIDER}; }}

/* ── Sidebar ── */
.sb-lbl {{
    font-size: 10px; font-weight: 800; letter-spacing: 1.4px;
    text-transform: uppercase; color: {SECTION_LBL} !important;
    margin: 20px 0 8px 2px; display: block;
}}
.stat-row  {{ display: flex; gap: 10px; margin-bottom: 10px; }}
.stat-card {{
    flex: 1; background: {CARD_BG}; border: 1.5px solid {CARD_BORDER};
    border-radius: 16px; padding: 14px 10px; text-align: center;
    box-shadow: 0 1px 8px rgba(0,0,0,0.05);
    transition: transform 0.15s ease;
}}
.stat-card:active {{ transform: scale(0.97); }}
.stat-icon {{ font-size: 22px; margin-bottom: 6px; line-height: 1; }}
.stat-val  {{ font-size: 17px; font-weight: 800; line-height: 1.2; }}
.stat-lbl  {{ font-size: 10px; color: {TEXT_MUTED} !important; margin-top: 4px; font-weight: 600; }}
.today-stat {{
    background: {TODAY_CARD_BG}; border: 1.5px solid {TODAY_CARD_BDR};
    border-radius: 14px; padding: 12px 16px; margin-bottom: 8px;
    display: flex; align-items: center; justify-content: space-between;
}}
.today-stat-label {{ font-size: 12px; font-weight: 700; }}
.today-stat-val   {{ font-size: 16px; font-weight: 800; color: #4CAF50 !important; }}
.streak-card {{
    background: {CARD_BG}; border: 1.5px solid {CARD_BORDER};
    border-radius: 16px; padding: 14px 16px;
    display: flex; align-items: center; gap: 14px; margin-bottom: 8px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.05);
}}
.streak-num {{ font-size: 26px; font-weight: 900; color: #FF9800 !important; line-height: 1; }}
.streak-sub {{ font-size: 11px; color: {TEXT_MUTED} !important; margin-top: 4px; }}
.goal-wrap {{
    background: {CARD_BG}; border: 1.5px solid {CARD_BORDER};
    border-radius: 16px; padding: 14px 16px; margin-bottom: 8px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.05);
}}
.goal-header {{ display: flex; justify-content: space-between; align-items: center;
                font-size: 12px; color: {TEXT_MUTED} !important; margin-bottom: 10px; }}
.goal-title  {{ font-weight: 700; color: {TEXT_PRIMARY} !important; font-size: 13px; }}
.goal-track  {{ background: {PROG_TRACK}; border-radius: 99px; height: 8px; overflow: hidden; }}
.goal-fill   {{ height: 8px; border-radius: 99px; transition: width 0.6s ease; }}
.subject-tag {{ display: inline-block; background: {TAG_BG}; color: {TAG_COLOR} !important;
                border-radius: 20px; padding: 6px 16px; font-size: 13px; font-weight: 700; }}
.act-list  {{ background: {ACTIVITY_BG}; border-radius: 14px; padding: 4px; overflow: hidden; }}
.act-item  {{ display: flex; align-items: flex-start; gap: 10px; padding: 8px 12px;
              border-radius: 10px; font-size: 12px; line-height: 1.4; }}
.act-dot   {{ width:8px; height:8px; border-radius:50%; background:#4CAF50;
              flex-shrink:0; margin-top:3px; }}
.act-empty {{ font-size:12px; color:{TEXT_MUTED} !important; padding:14px; text-align:center; }}
.settings-box {{ background: {SETTINGS_BG}; border: 1.5px solid {SETTINGS_BDR};
                 border-radius: 16px; padding: 16px; }}
.danger-box {{
    background: {DANGER_BG}; border: 1.5px solid {DANGER_BDR};
    border-radius: 12px; padding: 12px; margin-bottom: 8px;
    font-size: 12px; font-weight: 700; color: {DANGER_COLOR} !important; text-align: center;
}}
.greet-card {{
    background: {GREET_BG}; border: 1.5px solid {GREET_BDR};
    border-radius: 20px; padding: 20px 22px; margin-bottom: 16px;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 3px 18px rgba(0,0,0,0.07);
}}
.greet-emoji {{ font-size: 48px; line-height: 1; flex-shrink: 0; }}
.greet-name  {{ font-size: 20px; font-weight: 900; line-height: 1.2; letter-spacing: -0.3px; }}
.greet-sub   {{ font-size: 13px; color: {TEXT_MUTED} !important; margin-top: 4px; font-weight: 500; }}
.greet-time  {{ font-size: 11px; color: {TEXT_MUTED} !important; margin-top: 4px; opacity: 0.7; }}
.sched-card {{
    background: {SCHED_BG}; border: 1.5px solid {SCHED_BDR};
    border-radius: 18px; padding: 16px 18px; margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}}
.sched-title {{
    font-size: 12px; font-weight: 700; letter-spacing: 0.6px;
    text-transform: uppercase; color: {TEXT_MUTED} !important;
    margin-bottom: 12px; display: flex; align-items: center; gap: 6px;
}}
.sched-item      {{ display: flex; align-items: center; gap: 10px; padding: 9px 10px;
                    border-radius: 10px; margin-bottom: 4px; font-size: 13px; }}
.sched-item-done {{ background: {SCHED_DONE_BG}; opacity: 0.65; }}
.sched-item-todo {{ background: {SCHED_TODO_BG}; }}
.sched-time      {{ font-size: 11px; font-weight: 700; color: {TEXT_MUTED} !important;
                    min-width: 72px; flex-shrink: 0; font-variant-numeric: tabular-nums; }}
.sched-task      {{ font-weight: 500; flex: 1; min-width: 0;
                    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.sched-task-done {{ text-decoration: line-through; color: {TEXT_MUTED} !important; }}
.sched-check     {{ flex-shrink: 0; font-size: 14px; }}
.sched-prog-wrap {{ margin-top: 12px; background: {PROG_TRACK};
                    border-radius: 99px; height: 5px; overflow: hidden; }}
.sched-prog-fill {{ height: 5px; border-radius: 99px; }}

/* ── Slider ── */
[data-testid="stSlider"] > div > div {{ touch-action: none !important; }}

hr {{ border-color: {DIVIDER} !important; margin: 18px 0 !important; }}

/* ── Toasts / alerts ── */
.stAlert {{ border-radius: 14px !important; font-size: 14px !important; }}

{"""/* ── Arabic RTL ── */
.greet-card, .greet-name, .greet-sub, .greet-time,
.timer-card, .timer-subject, .stat-card, .stat-card-label,
.activity-card, .goal-banner, .xp-card, .xp-label, .xp-bar-wrap,
.streak-card, .streak-label, .goal-section, .quote-card,
.sched-card, .sched-item, .no-sched { direction: rtl; text-align: right; }
""" if st.session_state.lang == "arabic" else ""}

/* ── Mobile ── */
@media (max-width: 640px) {{
    .greet-card  {{ padding: 14px 16px; gap: 12px; border-radius: 16px; }}
    .greet-emoji {{ font-size: 36px; }}
    .greet-name  {{ font-size: 18px; }}
    .greet-sub   {{ font-size: 12px; }}
    .greet-time  {{ display: none; }}
    .stat-card   {{ padding: 12px 8px; border-radius: 14px; }}
    .stat-val    {{ font-size: 15px; }}
    .stat-icon   {{ font-size: 18px; }}
    .timer-card  {{ padding: 16px 8px 14px; border-radius: 20px; }}
    .stButton > button {{ font-size: 14px !important; padding: 11px 10px !important; }}
    .setup-card  {{ padding: 16px 14px; }}
    .quote-card  {{ padding: 16px 16px; }}
    .quote-text  {{ font-size: 13px; }}
    .goal-win-banner {{ padding: 14px 16px; gap: 12px; border-radius: 14px; }}
    .goal-win-icon   {{ font-size: 28px; }}
    .sched-time  {{ min-width: 64px; font-size: 10px; }}
    .sched-item  {{ padding: 8px 8px; font-size: 12px; }}
    .section-hdr {{ margin: 18px 0 10px; }}
}}

/* ── Very small phones ── */
@media (max-width: 380px) {{
    .greet-emoji {{ font-size: 28px; }}
    .greet-name  {{ font-size: 16px; }}
    .stat-val    {{ font-size: 13px; }}
    .stat-icon   {{ font-size: 16px; }}
    .stButton > button {{ font-size: 13px !important; padding: 10px 8px !important; }}
    .sched-time  {{ display: none; }}
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  MAIN PAGE
# ══════════════════════════════════════════════════════════

# ── Name input
_all_defaults = {
    TRANSLATIONS.get(lng, {}).get("default_name", "")
    for lng in ("badini", "english", "arabic")
}
_raw_name    = st.session_state.get("student_name", "")
_display_val = "" if _raw_name in _all_defaults else _raw_name

nav = st.text_input(
    t("enter_name"), value=_display_val,
    label_visibility="collapsed", placeholder=t("default_name"),
)
_effective_name = nav.strip() or t("default_name")
if nav != st.session_state.get("student_name", ""):
    st.session_state.student_name = nav
    save_data()

# ── Greeting card
kurd_greet, eng_greet = get_greeting()
h_now       = datetime.now().hour
greet_emoji = ("🌅" if 5 <= h_now < 12 else "☀️" if 12 <= h_now < 17
               else "🌆" if 17 <= h_now < 21 else "🌙")
now_str     = datetime.now().strftime("%A, %d %B  •  %H:%M")

st.markdown(f"""
<div class="greet-card">
    <div class="greet-emoji">{greet_emoji}</div>
    <div style="min-width:0;">
        <div class="greet-name">{kurd_greet}{t("greeting_comma")}{_effective_name}!</div>
        <div class="greet-sub">{eng_greet} — {t('welcome')} 📚</div>
        <div class="greet-time">{now_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Daily goal banner
if daily_pct >= 100:
    goal_win_msg = {
        "badini":  f"ئارمانجێن ئەڤرو تەواو بوون! {today_h}ک {today_m}خ خواندن.",
        "english": f"Daily goal reached! You studied {today_h}h {today_m}m today.",
        "arabic":  f"تم تحقيق هدف اليوم! درست {today_h}س {today_m}د اليوم.",
    }.get(st.session_state.lang, "Goal reached!")
    goal_win_sub = {
        "badini":  "زور باش تە کر! بەردەوام بە 🔥",
        "english": "Amazing work! Keep the momentum going 🔥",
        "arabic":  "عمل رائع! استمر في الزخم 🔥",
    }.get(st.session_state.lang, "Keep going! 🔥")
    st.markdown(f"""
    <div class="goal-win-banner">
        <div class="goal-win-icon">🏆</div>
        <div>
            <div class="goal-win-text">{goal_win_msg}</div>
            <div class="goal-win-sub">{goal_win_sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Today's schedule preview
_today_key, today_tasks = load_today_schedule()
DAYS_SHORT = {
    "sun": ("Sunday","☀️"), "mon": ("Monday","📖"), "tue": ("Tuesday","📖"),
    "wed": ("Wednesday","📖"), "thu": ("Thursday","📖"),
    "fri": ("Friday","🕌"), "sat": ("Saturday","🎉"),
}
_day_eng, _day_emoji = DAYS_SHORT.get(_today_key, ("Today","📅"))
today_tasks_named = [ti for ti in today_tasks if ti.get("task","").strip()]

if today_tasks_named:
    done_count  = sum(1 for ti in today_tasks_named if ti.get("done", False))
    total_count = len(today_tasks_named)
    pct_sched   = int((done_count / total_count) * 100) if total_count else 0
    prog_color  = "#2196F3" if done_count == total_count else "#4CAF50"
    sched_title_text = {
        "badini":  f"📅 خشتەیێ ئەڤروکە — {_day_emoji} {_day_eng}",
        "english": f"📅 Today's Schedule — {_day_emoji} {_day_eng}",
        "arabic":  f"📅 جدول اليوم — {_day_emoji} {_day_eng}",
    }.get(st.session_state.lang, f"📅 Today — {_day_eng}")

    html_content = '<div class="sched-card">'
    html_content += (
        f'<div class="sched-title">{sched_title_text}'
        f'<span style="margin-left:auto;font-size:11px;color:{TEXT_MUTED};font-weight:600;">'
        f'{done_count}/{total_count} — {pct_sched}%</span></div>'
    )
    for ti in today_tasks_named[:6]:
        done_cls  = "sched-item-done" if ti.get("done") else "sched-item-todo"
        task_cls  = "sched-task-done" if ti.get("done") else "sched-task"
        check_ico = "✅" if ti.get("done") else "⬜"
        html_content += (
            f'<div class="sched-item {done_cls}">'
            f'<span class="sched-time">{ti.get("start","")}–{ti.get("end","")}</span>'
            f'<span class="{task_cls}">{ti.get("task","")}</span>'
            f'<span class="sched-check">{check_ico}</span></div>'
        )
    if len(today_tasks_named) > 6:
        extra = len(today_tasks_named) - 6
        extra_lbl = {
            "badini": f"+{extra} زێدەکرن",
            "english": f"+{extra} more",
            "arabic": f"+{extra} أكثر",
        }.get(st.session_state.lang, f"+{extra} more")
        html_content += f'<div style="font-size:11px;color:{TEXT_MUTED};padding:6px 10px;font-weight:600;">{extra_lbl}</div>'
    html_content += (
        f'<div class="sched-prog-wrap">'
        f'<div class="sched-prog-fill" style="width:{pct_sched}%;background:{prog_color};"></div>'
        f'</div></div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  DASHBOARD – Professionally Designed
# ══════════════════════════════════════════════════════════

# ── Header ──
st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin: 8px 0 20px 0;">
    <h2 style="font-size: 22px; font-weight: 800; letter-spacing: -0.5px; color: {TEXT_PRIMARY}; margin: 0;">
         {t('sidebar_title')}
    </h2>
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 12px; color: {TEXT_MUTED}; font-weight: 500; background: {CARD_BG}; padding: 4px 14px; border-radius: 20px; border: 1px solid {CARD_BORDER};">
            {datetime.now().strftime('%a, %d %b')}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Row 1: Three Stat Cards ──
col1, col2, col3 = st.columns(3, gap="small")

with col1:
    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 20px 12px 18px; text-align: center;">
        <div style="font-size: 28px; margin-bottom: 4px;">⏱️</div>
        <div style="font-size: 24px; font-weight: 800; color: #4CAF50; letter-spacing: -0.5px; line-height: 1.2;">
            {hours_total}{t('hours_unit')} {mins_total}{t('minutes_unit')}
        </div>
        <div style="font-size: 12px; color: {TEXT_MUTED}; font-weight: 600; margin-top: 2px;">{t('total_time')}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 20px 12px 18px; text-align: center;">
        <div style="font-size: 28px; margin-bottom: 4px;">✅</div>
        <div style="font-size: 24px; font-weight: 800; color: #2196F3; letter-spacing: -0.5px; line-height: 1.2;">
            {st.session_state.completed_sessions}
        </div>
        <div style="font-size: 12px; color: {TEXT_MUTED}; font-weight: 600; margin-top: 2px;">{t('sessions')}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 20px 12px 18px; text-align: center;">
        <div style="font-size: 28px; margin-bottom: 4px;">🎯</div>
        <div style="font-size: 24px; font-weight: 800; color: #FF9800; letter-spacing: -0.5px; line-height: 1.2;">
            {today_h}{t('hours_unit')} {today_m}{t('minutes_unit')}
        </div>
        <div style="font-size: 12px; color: {TEXT_MUTED}; font-weight: 600; margin-top: 2px;">{t('today_goal')}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Spacer ──
st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

# ── Row 2: XP & Streak ──
col_xp, col_streak = st.columns(2, gap="small")

with col_xp:
    xp_points = st.session_state.total_study_seconds // 60
    xp_needed = 100
    if "xp_level" not in st.session_state:
        st.session_state.xp_level = 1
    current_level = st.session_state.xp_level
    if xp_points >= xp_needed:
        current_level += 1
        st.session_state.xp_level = current_level
        xp_points = 0
        st.toast(f"🎉 {t('xp_level_up').format(level=current_level)}")
    xp_progress = min(xp_points / xp_needed, 1.0)

    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 18px 18px 16px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-size: 32px; line-height: 1;">🏆</div>
            <div style="flex: 1; min-width: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY};">{t('xp_title')}</span>
                    <span style="font-size: 13px; font-weight: 700; color: #FF9800;">{t('xp_level')} {current_level}</span>
                </div>
                <div style="background: {PROG_TRACK}; border-radius: 99px; height: 6px; overflow: hidden; margin: 4px 0 2px;">
                    <div style="width: {xp_progress * 100}%; height: 6px; background: linear-gradient(90deg, #388e3c, #4caf50); border-radius: 99px; transition: width 0.5s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: {TEXT_MUTED}; font-weight: 600;">
                    <span>⚡ {xp_points} XP</span>
                    <span>{xp_needed} XP</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_streak:
    sv = st.session_state.streak
    smsg = (t("streak_start") if sv == 0 else t("streak_ready") if sv < 3
            else t("streak_keep") if sv < 7 else t("streak_champ"))

    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 18px 18px 16px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-size: 32px; line-height: 1;">🔥</div>
            <div style="flex: 1; min-width: 0;">
                <div style="display: flex; align-items: baseline; gap: 6px;">
                    <span style="font-size: 28px; font-weight: 900; color: #FF9800; line-height: 1.2;">{sv}</span>
                    <span style="font-size: 13px; color: {TEXT_MUTED}; font-weight: 600;">{days_lbl}</span>
                </div>
                <div style="font-size: 13px; color: {TEXT_PRIMARY}; font-weight: 600; margin-top: 2px;">{smsg}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Spacer ──
st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

# ── Row 3: Daily Goal Progress ──
st.markdown(f"""
<div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 16px 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 14px; font-weight: 700; color: {TEXT_PRIMARY};">🎯 {t('today_goal')}</span>
        <span style="font-size: 12px; color: {TEXT_MUTED}; font-weight: 600;">{daily_done_min} / {daily_goal_min} {t('minutes_unit')} — {daily_pct}%</span>
    </div>
    <div style="background: {PROG_TRACK}; border-radius: 99px; height: 8px; overflow: hidden; position: relative;">
        <div style="width: {daily_pct}%; height: 8px; background: {'#4CAF50' if daily_pct >= 100 else '#2196F3'}; border-radius: 99px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);"></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Spacer ──
st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

# ── Row 5: Last Subject & Recent Activity ──
col_sub, col_act = st.columns(2, gap="small")

with col_sub:
    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 16px 18px;">
        <div style="font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: {TEXT_MUTED}; margin-bottom: 8px;"> {t('last_subject')}</div>
        <div style="font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};">{st.session_state.last_subject}</div>
    </div>
    """, unsafe_allow_html=True)

with col_act:
    hist = st.session_state.study_history[-4:][::-1]
    st.markdown(f"""
    <div class="stats-card" style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 16px 18px;">
        <div style="font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: {TEXT_MUTED}; margin-bottom: 8px;"> {t('recent_activity')}</div>
    """, unsafe_allow_html=True)

    if hist:
        for e in hist[:3]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0; font-size: 13px; color: {TEXT_MUTED}; border-bottom: 1px solid {DIVIDER};">
                <div style="width: 6px; height: 6px; border-radius: 50%; background: #4CAF50; flex-shrink: 0;"></div>
                <span>{e}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 12px 0; font-size: 13px; color: {TEXT_MUTED};">{t('no_activity')}</div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Divider ──
st.markdown(f'<div style="height: 1px; background: {DIVIDER}; margin: 24px 0 18px;"></div>', unsafe_allow_html=True)

# ── Weekly Overview ──
schedule_data = get_schedule_data()
if schedule_data:
    week_data = {}
    for day, tasks in schedule_data.items():
        week_data[day] = total_day_minutes(tasks)
    
    if week_data and any(week_data.values()):
        day_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        day_labels = {"mon": "M", "tue": "T", "wed": "W", "thu": "T", "fri": "F", "sat": "S", "sun": "S"}
        max_val = max(week_data.values()) if week_data.values() else 1
        
        bars_html = ""
        for day in day_order:
            val = week_data.get(day, 0)
            pct = (val / max_val * 100) if max_val > 0 else 0
            bar_color = "#4CAF50" if val > 0 else ("#e0e0e0" if not is_dark else "rgba(255,255,255,0.08)")
            bars_html += f'''
            <div style="flex: 1; text-align: center; min-width: 0;">
                <div style="font-size: 9px; color: {TEXT_MUTED}; font-weight: 700; margin-bottom: 3px; letter-spacing: 0.5px;">{day_labels[day]}</div>
                <div style="height: 5px; background: {PROG_TRACK}; border-radius: 99px; overflow: hidden; width: 70%; margin: 0 auto;">
                    <div style="height: 5px; width: {pct}%; background: {bar_color}; border-radius: 99px; transition: width 0.5s ease;"></div>
                </div>
                <div style="font-size: 8px; color: {TEXT_MUTED}; margin-top: 3px; font-weight: 600;">{val}m</div>
            </div>
            '''
        
        components.html(f"""
        <div style="background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px;
                    padding: 16px 12px 14px; font-family: Inter, system-ui, sans-serif;">
            <div style="font-size: 11px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase;
                        color: {TEXT_MUTED}; margin-bottom: 12px; padding-left: 4px;">
                📊 {t('weekly_chart')}
            </div>
            <div style="display: flex; gap: 6px; justify-content: space-between; align-items: flex-end;">
                {bars_html}
            </div>
        </div>
        """, height=120)


# ── Weekly Study Chart ──
st.markdown(f"""
<div class="sched-card">
    <div class="sched-title">📊 {t('weekly_chart')}</div>
""", unsafe_allow_html=True)

schedule_data = get_schedule_data()

if schedule_data:
    week_data = {}
    for day, tasks in schedule_data.items():
        minutes = total_day_minutes(tasks)
        week_data[day] = minutes
    
    if week_data and any(week_data.values()):
        total_minutes = sum(week_data.values())
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        
        # Stats cards
        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
            <div style="flex: 1; background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 12px; padding: 12px; text-align: center;">
                <div style="font-size: 20px; font-weight: 800; color: #4CAF50;">{total_hours}h {total_mins}m</div>
                <div style="font-size: 11px; color: {TEXT_MUTED}; font-weight: 600;">{t('total_this_week')}</div>
            </div>
            <div style="flex: 1; background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 12px; padding: 12px; text-align: center;">
                <div style="font-size: 20px; font-weight: 800; color: #FF9800;">{len([d for d, m in week_data.items() if m > 0])}</div>
                <div style="font-size: 11px; color: {TEXT_MUTED}; font-weight: 600;">{t('days_studied')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── Custom SVG Bar Chart using st.components.v1.html() ──
        day_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        day_labels = {"mon": "Mo", "tue": "Tu", "wed": "We", "thu": "Th",
              "fri": "Fr", "sat": "Sa", "sun": "Su"}
        max_val = max(week_data.values()) if week_data.values() else 1
        
        # Build bars HTML
        bars_html = ""
        for day in day_order:
            val = week_data.get(day, 0)
            pct = (val / max_val * 100) if max_val > 0 else 0
            bar_color = "#4CAF50" if val > 0 else "rgba(255,255,255,0.08)"
            bars_html += f'''
            <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                <div style="font-size: 10px; color: {TEXT_MUTED}; font-weight: 600; margin-bottom: 4px;">{day_labels[day]}</div>
                <div style="width: 20px; height: 120px; background: rgba(255,255,255,0.06); border-radius: 6px; overflow: hidden; position: relative;">
                    <div style="width: 100%; height: {pct}%; background: {bar_color}; border-radius: 6px; position: absolute; bottom: 0; transition: height 0.5s ease;"></div>
                </div>
                <div style="font-size: 9px; color: {TEXT_MUTED}; font-weight: 600; margin-top: 4px;">{val}m</div>
            </div>
            '''
        
        # Render the chart using components.html() – this always works
        components.html(f'''
        <div style="background: rgba(255,255,255,0.03); border-radius: 12px; padding: 16px 8px; margin: 4px 0 12px 0; border: 1px solid rgba(255,255,255,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 4px; height: 140px;">
                {bars_html}
            </div>
        </div>
        ''', height=180)
        
        # Best day
        if any(week_data.values()):
            best_day = max(week_data, key=week_data.get)
            best_minutes = week_data[best_day]
            if st.session_state.lang == "arabic":
                day_names = {"mon": "الاثنين", "tue": "الثلاثاء", "wed": "الأربعاء",
                             "thu": "الخميس", "fri": "الجمعة", "sat": "السبت", "sun": "الأحد"}
            elif st.session_state.lang == "badini":
                day_names = {"mon": "دووشەمب", "tue": "سێشەمب", "wed": "چارشەمب",
                             "thu": "پێنجشەمب", "fri": "خودبە", "sat": "شەمبی", "sun": "ئێکشەمب"}
            else:
                day_names = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
                             "thu": "Thursday", "fri": "Friday", "sat": "Saturday", "sun": "Sunday"}
            best_day_name = day_names.get(best_day, best_day)
            
            st.markdown(f'''
            <div style="text-align: center; margin-top: 8px; padding: 8px; background: rgba(76,175,80,0.10); border-radius: 10px; border: 1px solid rgba(76,175,80,0.15);">
                <span style="font-size: 13px; color: {TEXT_PRIMARY}; font-weight: 600;">
                    🏆 {t('best_day')}: <span style="color: #4CAF50; font-weight: 800;">{best_day_name}</span> <span style="color: {TEXT_MUTED};">({best_minutes}m)</span>
                </span>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.caption(f"📭 {t('no_study_data')}")
else:
    st.caption(f"📭 {t('no_study_data')}")

st.markdown('</div>', unsafe_allow_html=True)

# ── Timer section header
timer_section_lbl = {
    "badini": "⏱ دەمژمێرێ خواندنێ",
    "english": "⏱ Study Timer",
    "arabic": "⏱ مؤقت الدراسة",
}.get(st.session_state.lang, "⏱ Study Timer")
st.markdown(f"""
<div class="section-hdr">
    <span>{timer_section_lbl}</span>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Setup card
st.markdown('<div class="setup-card">', unsafe_allow_html=True)

subjects_list = t("subjects")
if not isinstance(subjects_list, list):
    subjects_list = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["badini"]).get("subjects", [])

ders      = st.selectbox(t("select_subject"), subjects_list)
arc_color = subject_color(ders)
subj_name = ders.split(" ", 1)[1] if " " in ders else ders
st.markdown(
    f'<div class="subject-pill">'
    f'<span class="subject-color-dot" style="background:{arc_color};"></span>'
    f'{subj_name}</div>',
    unsafe_allow_html=True,
)

duration_lbl = {
    "badini": "⏱ دەمێ خواندنێ",
    "english": "⏱ Duration",
    "arabic": "⏱ المدة",
}.get(st.session_state.lang, "⏱ Duration")
st.markdown(
    f'<div style="font-size:12px;font-weight:700;color:{TEXT_MUTED};margin-bottom:6px;">'
    f'{duration_lbl}</div>',
    unsafe_allow_html=True,
)

SLIDER_KEY = "duration_slider_v2"
if SLIDER_KEY not in st.session_state:
    st.session_state[SLIDER_KEY] = 25

st.markdown('<div class="preset-anchor"></div>', unsafe_allow_html=True)
p1, p2, p3, p4 = st.columns(4)
with p1:
    if st.button("🍅 25m", key="p25", use_container_width=True, help="Pomodoro"):
        st.session_state[SLIDER_KEY] = 25; st.rerun()
with p2:
    if st.button("⚡ 45m", key="p45", use_container_width=True, help="Deep work"):
        st.session_state[SLIDER_KEY] = 45; st.rerun()
with p3:
    if st.button("🎯 60m", key="p60", use_container_width=True, help="Focus block"):
        st.session_state[SLIDER_KEY] = 60; st.rerun()
with p4:
    if st.button("🔥 90m", key="p90", use_container_width=True, help="Power session"):
        st.session_state[SLIDER_KEY] = 90; st.rerun()

deqe          = st.slider(t("minutes_question"), 1, 240, key=SLIDER_KEY)
total_seconds = deqe * 60
st.markdown('</div>', unsafe_allow_html=True)

# ── Timer control buttons
st.markdown('<div class="tcb-anchor"></div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if not st.session_state.timer_running and not st.session_state.paused:
        dest_pe_bike = st.button(t("start_btn"), use_container_width=True, key="start_btn")
    elif st.session_state.paused:
        resume = st.button(t("resume_btn"), use_container_width=True, key="resume_btn")
    else:
        st.button(t("start_btn"), disabled=True, use_container_width=True, key="start_disabled")
with col2:
    if st.session_state.timer_running:
        stop_timer = st.button(t("pause_btn"), use_container_width=True, key="pause_btn")
    else:
        st.button(t("pause_btn"), disabled=True, use_container_width=True, key="pause_disabled")
with col3:
    dubare = st.button(t("reset_btn"), use_container_width=True, key="reset_btn")

# ── Quote card
hezt = t("quotes")
if not isinstance(hezt, list):
    hezt = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["badini"]).get("quotes", ["Keep going!"])
current_quote = hezt[st.session_state.quote_idx % len(hezt)]

refresh_lbl = {"badini": "نوى", "english": "New quote", "arabic": "اقتباس جديد"}.get(
    st.session_state.lang, "New quote"
)
_, qbtn_col = st.columns([5, 2])
with qbtn_col:
    if st.button(f"🔄 {refresh_lbl}", key="refresh_quote", use_container_width=True):
        st.session_state.quote_idx = random.randint(0, len(hezt) - 1)
        st.rerun()
st.markdown(f"""
<div class="quote-card">
    <div class="quote-mark">"</div>
    <div class="quote-text">{current_quote}</div>
</div>
""", unsafe_allow_html=True)

# ── Button actions
if "dest_pe_bike" in locals() and dest_pe_bike:
    st.session_state.timer_running = True
    st.session_state.paused        = False
    st.session_state.end_time      = time.time() + total_seconds
    st.session_state.total_seconds = total_seconds
    st.rerun()

if "resume" in locals() and resume:
    st.session_state.timer_running = True
    st.session_state.paused        = False
    st.session_state.end_time      = time.time() + st.session_state.remaining_at_pause
    st.rerun()

if "stop_timer" in locals() and stop_timer:
    st.session_state.timer_running      = False
    st.session_state.paused             = True
    st.session_state.remaining_at_pause = max(0, st.session_state.end_time - time.time())
    st.rerun()

if dubare:
    st.session_state.timer_running      = False
    st.session_state.paused             = False
    st.session_state.end_time           = None
    st.session_state.total_seconds      = 0
    st.session_state.remaining_at_pause = 0
    st.rerun()


# ── SVG circle timer
def render_circle(mins_val, secs_val, progress, color):
    dash = progress * 100.0
    glow = f"filter:drop-shadow(0 0 14px {color}bb);" if progress > 0 else ""
    st.markdown(f"""
    <div class="timer-card">
        <div style="display:flex;justify-content:center;">
            <svg width="260" height="260" viewBox="0 0 36 36" style="{glow}">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="{TIMER_TRACK}" stroke-width="2.2"/>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="{color}" stroke-width="2.2"
                      stroke-linecap="round" stroke-dasharray="{dash:.2f}, 200"/>
                <text x="18" y="17" text-anchor="middle"
                      fill="{TIMER_TEXT}" font-size="6.5" font-weight="700" font-family="monospace">
                    {mins_val:02d}:{secs_val:02d}
                </text>
                <text x="18" y="22" text-anchor="middle"
                      fill="{TIMER_TEXT}99" font-size="2.6">{t('min_sec_labels')}</text>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)


@st.fragment(run_every=1)
def live_timer():
    is_running = st.session_state.get("timer_running", False)
    end_time   = st.session_state.get("end_time")
    is_paused  = st.session_state.get("paused", False)
    arc_c      = subject_color(st.session_state.get("last_subject", ""))

    if is_running and end_time:
        remaining = end_time - time.time()
        if remaining > 0:
            mv, sv_ = divmod(int(remaining), 60)
            prog = min(1.0, 1.0 - (remaining / max(1, st.session_state.get("total_seconds", 1))))
            render_circle(mv, sv_, prog, arc_c)
            st.success(t("timer_running",
                         name=st.session_state.get("student_name") or t("default_name"),
                         minutes=st.session_state.get("total_seconds", 0) // 60,
                         subject=st.session_state.get("last_subject", "")))
            st.info(f"💬 {hezt[st.session_state.quote_idx % len(hezt)]}")
        else:
            # ── Session complete ──
            st.session_state.timer_running = False
            st.session_state.paused        = False
            total_secs = st.session_state.get("total_seconds", 0)
            st.session_state.total_study_seconds += total_secs
            st.session_state.completed_sessions  += 1
            st.session_state.daily_seconds       += total_secs
            today_str = date.today().isoformat()
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if st.session_state.last_study_date == yesterday:
                st.session_state.streak += 1
            elif st.session_state.last_study_date != today_str:
                st.session_state.streak = 1
            st.session_state.last_study_date = today_str
            minutes = total_secs // 60
            now_ts  = datetime.now().strftime("%H:%M")
            subj    = st.session_state.get("last_subject", "")
            st.session_state.study_history.append(
                f"{now_ts} - {subj} ({minutes} {t('minutes_unit')})"
            )
            save_data()
            components.html("""<script>
            (function(){
                var AC = window.AudioContext || window.webkitAudioContext;
                if (!AC) return;
                var ctx = new AC();
                function note(f,d,dur){
                    var o=ctx.createOscillator(),g=ctx.createGain();
                    o.connect(g);g.connect(ctx.destination);
                    o.type='sine';o.frequency.value=f;
                    var t=ctx.currentTime+d;
                    g.gain.setValueAtTime(0,t);
                    g.gain.linearRampToValueAtTime(0.25,t+0.02);
                    g.gain.exponentialRampToValueAtTime(0.001,t+dur);
                    o.start(t);o.stop(t+dur);
                }
                note(659,0.0,1.2);note(830,0.22,1.2);note(988,0.44,1.4);
            })();
            </script>""", height=0)
            st.balloons()
            st.success(t("timer_done"))
            st.rerun()  # one full rerun to update stats display

    elif is_paused and st.session_state.get("remaining_at_pause", 0) > 0:
        mv, sv_ = divmod(int(st.session_state.remaining_at_pause), 60)
        prog = min(1.0, 1.0 - (st.session_state.remaining_at_pause / max(1, st.session_state.get("total_seconds", 1))))
        render_circle(mv, sv_, prog, "#FFA500")
        pause_lbl = {"badini": "⏸️ دەمژمێر راوەستیایە", "english": "⏸️ Timer paused", "arabic": "⏸️ الموقت متوقف"}.get(st.session_state.lang, "⏸️ Timer paused")
        st.markdown(f'<div class="paused-banner">{pause_lbl}</div>', unsafe_allow_html=True)

    else:
        render_circle(st.session_state.get(SLIDER_KEY, 25), 0, 0.0, arc_c)

live_timer()
