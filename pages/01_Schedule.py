import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, time as dtime, date, timedelta
import requests
import json
import time
import base64
import time as _time
from utils import save_schedule, load_schedule, save_preferences, load_preferences

    

# ── Translations
with open("translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

# ── Session-state guards
if "lang" not in st.session_state:
    st.session_state.lang = "badini"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


def t(key, **kwargs):
    text = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["badini"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


# ══════════════════════════════════════════════════════════
#  CONSTANTS  (kept exactly as original)
# ══════════════════════════════════════════════════════════
DAYS = [
    ("sun", "☀️ ئێکشەمب", "Sunday"),
    ("mon", "📖 دووشەمب", "Monday"),
    ("tue", "📖 سێشەمب",  "Tuesday"),
    ("wed", "📖 چارشەمب", "Wednesday"),
    ("thu", "📖 پێنجشەمب","Thursday"),
    ("fri", "🕌 خودبە",   "Friday"),
    ("sat", "🎉 شەمبی",   "Saturday"),
]
DAY_EMOJIS = {"sun":"☀️","mon":"📖","tue":"📖","wed":"📖","thu":"📖","fri":"🕌","sat":"🎉"}


# ══════════════════════════════════════════════════════════
#  HELPERS  (kept exactly as original)
# ══════════════════════════════════════════════════════════
def get_day_name(day_key):
    for dk, badini_name, eng_name in DAYS:
        if dk == day_key:
            if st.session_state.lang == "badini":
                return badini_name
            elif st.session_state.lang == "arabic":
                ar = {
                    "sun": "☀️ الأحد",  "mon": "📖 الاثنين", "tue": "📖 الثلاثاء",
                    "wed": "📖 الأربعاء","thu": "📖 الخميس", "fri": "🕌 الجمعة",
                    "sat": "🎉 السبت",
                }
                return ar.get(day_key, eng_name)
            else:
                return f"{DAY_EMOJIS.get(day_key,'📖')} {eng_name}"
    return day_key


def get_time_label():
    if st.session_state.lang == "badini": return "دەستپێک", "دووماهی"
    if st.session_state.lang == "arabic": return "بداية",   "نهاية"
    return "Start", "End"


def get_column_labels():
    if st.session_state.lang == "badini": return "دەم", "چالاکی"
    if st.session_state.lang == "arabic": return "الوقت", "المهمة"
    return "Time", "Task"


def parse_time(s):
    try:
        dt = datetime.strptime(s, "%H:%M")
        return (dt.hour, dt.minute)
    except Exception:
        return (0, 0)


def format_duration(start_str, end_str):
    try:
        s    = datetime.strptime(start_str, "%H:%M")
        e    = datetime.strptime(end_str,   "%H:%M")
        diff = int((e - s).total_seconds() // 60)
        if diff <= 0: return ""
        if diff < 60: return f"{diff}m"
        h, m = divmod(diff, 60)
        return f"{h}h {m}m" if m else f"{h}h"
    except Exception:
        return ""


def total_day_minutes(day_entries):
    total = 0
    for e in day_entries:
        if not e.get("task", "").strip(): continue
        try:
            s   = datetime.strptime(e.get("start","00:00"), "%H:%M")
            end = datetime.strptime(e.get("end",  "00:00"), "%H:%M")
            diff = int((end - s).total_seconds() // 60)
            if diff > 0: total += diff
        except Exception:
            pass
    return total


def fmt_minutes(mins):
    if mins <= 0: return ""
    if mins < 60: return f"{mins}m"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if m else f"{h}h"


def copy_week_to_next(today_key):
    new_schedule = {dk: [] for dk, _, _ in DAYS}
    for dk, _, _ in DAYS:
        for task_item in st.session_state.schedule.get(dk, []):
            new_task = task_item.copy()
            new_task["done"] = False
            new_schedule[dk].append(new_task)
    st.session_state.schedule = new_schedule
    st.session_state.active_day = today_key  
    save_schedule()
    
# ══════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "schedule" not in st.session_state:
    loaded = load_schedule()
    base   = {dk: [] for dk, _, _ in DAYS}
    if loaded: base.update(loaded)
    st.session_state.schedule = base

for dk, _, _ in DAYS:
    if dk not in st.session_state.schedule:
        st.session_state.schedule[dk] = []
    if f"{dk}_reset" not in st.session_state:
        st.session_state[f"{dk}_reset"] = 0
    if f"{dk}_clear_confirm" not in st.session_state:
        st.session_state[f"{dk}_clear_confirm"] = False

today_map = {6:"sun", 0:"mon", 1:"tue", 2:"wed", 3:"thu", 4:"fri", 5:"sat"}
today_key = today_map[datetime.now().weekday()]
is_dark   = st.session_state.dark_mode

# ══════════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════════
if is_dark:
    APP_BG        = "#1a1a2e"
    SB_BG         = "#16213e"
    INPUT_BG      = "#252542"
    CARD_BG       = "rgba(255,255,255,0.05)"
    CARD_BORDER   = "rgba(255,255,255,0.09)"
    TEXT_PRIMARY  = "#e2e2e2"
    TEXT_MUTED    = "#8a8fa8"
    BTN_BG        = "#252542"
    BTN_COLOR     = "#e2e2e2"
    BTN_BORDER    = "#3a3a5c"
    PROG_TRACK    = "rgba(255,255,255,0.12)"
    DIVIDER       = "rgba(255,255,255,0.08)"
    TODAY_BG      = "rgba(76,175,80,0.15)"
    TODAY_COLOR   = "#81c784"
    OVERVIEW_BG   = "rgba(255,255,255,0.04)"
    OVERVIEW_BDR  = "rgba(255,255,255,0.09)"
    DURATION_CLR  = "#8a8fa8"
    EMPTY_CLR     = "#555c72"
    PILL_BG       = "rgba(76,175,80,0.15)"
    PILL_COLOR    = "#81c784"
    PILL_BORDER   = "rgba(76,175,80,0.25)"
    TASK_ROW_BG   = "rgba(255,255,255,0.03)"
    TASK_ROW_DONE = "rgba(76,175,80,0.07)"
    TASK_ROW_BDR  = "rgba(255,255,255,0.07)"
    TOTAL_BG      = "rgba(33,150,243,0.12)"
    TOTAL_COLOR   = "#64b5f6"
    TOTAL_BDR     = "rgba(33,150,243,0.25)"
    AI_EXP_BG     = "rgba(255,255,255,0.03)"
    AI_EXP_BDR    = "rgba(171,71,188,0.25)"
    SECTION_BG    = "rgba(255,255,255,0.03)"
    SECTION_BDR   = "rgba(255,255,255,0.08)"
    SHADOW        = "rgba(0,0,0,0.35)"
else:
    APP_BG        = "#eef1f8"
    SB_BG         = "#f5f7fc"
    INPUT_BG      = "#ffffff"
    CARD_BG       = "#ffffff"
    CARD_BORDER   = "#dde4f0"
    TEXT_PRIMARY  = "#1a1a2e"
    TEXT_MUTED    = "#6b7280"
    BTN_BG        = "#e2e8f5"
    BTN_COLOR     = "#1a1a2e"
    BTN_BORDER    = "#c5d0e6"
    PROG_TRACK    = "#dde4f0"
    DIVIDER       = "#e2e8f5"
    TODAY_BG      = "rgba(76,175,80,0.09)"
    TODAY_COLOR   = "#2e7d32"
    OVERVIEW_BG   = "#ffffff"
    OVERVIEW_BDR  = "#dde4f0"
    DURATION_CLR  = "#9ca3af"
    EMPTY_CLR     = "#b0b8c8"
    PILL_BG       = "rgba(76,175,80,0.08)"
    PILL_COLOR    = "#2e7d32"
    PILL_BORDER   = "rgba(76,175,80,0.18)"
    TASK_ROW_BG   = "#fafbfd"
    TASK_ROW_DONE = "rgba(76,175,80,0.05)"
    TASK_ROW_BDR  = "#e8edf8"
    TOTAL_BG      = "rgba(33,150,243,0.07)"
    TOTAL_COLOR   = "#1565c0"
    TOTAL_BDR     = "rgba(33,150,243,0.16)"
    AI_EXP_BG     = "#faf8ff"
    AI_EXP_BDR    = "rgba(171,71,188,0.18)"
    SECTION_BG    = "#f8faff"
    SECTION_BDR   = "#e2e8f5"
    SHADOW        = "rgba(0,0,0,0.08)"

# ══════════════════════════════════════════════════════════
#  CSS
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

/* ── MOBILE: no double-tap zoom ── */
button, input, select, textarea, label {{
    touch-action: manipulation !important;
}}

/* ── MOBILE: safe-area insets ── */
.main .block-container {{
    padding-left:   max(1rem, env(safe-area-inset-left))   !important;
    padding-right:  max(1rem, env(safe-area-inset-right))  !important;
    padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
}}

/* ── Inputs  (font-size 16px prevents iOS auto-zoom) ── */
.stTextInput input,
.stTimeInput input {{
    background-color: {INPUT_BG} !important;
    border: 1.5px solid {CARD_BORDER} !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    padding: 8px 10px !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    min-height: 44px !important;
}}
.stTextInput input:focus {{
    border-color: #4CAF50 !important;
    box-shadow: 0 0 0 3px rgba(76,175,80,0.13) !important;
    outline: none !important;
}}
.stTextInput input:disabled {{
    text-decoration: line-through !important;
    opacity: 0.42 !important;
    background-color: {TASK_ROW_DONE} !important;
}}
[data-testid="stCheckbox"] svg       {{ stroke: #4CAF50 !important; }}
[data-testid="stCheckbox"]           {{ margin-top: 4px !important; }}
[data-testid="stCheckbox"] label     {{ min-height: 44px !important;
                                        display: flex !important;
                                        align-items: center !important; }}

/* ── Selectbox ── */
.stSelectbox > div > div {{
    background-color: {INPUT_BG} !important;
    border: 1.5px solid {CARD_BORDER} !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    min-height: 44px !important;
}}

/* ══════════════════════════════════════════
   BASE BUTTON (48px min — Apple HIG)
   ══════════════════════════════════════════ */
.stButton > button {{
    background-color: {BTN_BG} !important;
    color:            {BTN_COLOR} !important;
    border:           1.5px solid {BTN_BORDER} !important;
    border-radius:    10px !important;
    font-weight:      600 !important;
    font-size:        13px !important;
    font-family:      'Inter', system-ui, sans-serif !important;
    transition:       all 0.18s ease !important;
    padding:          10px 8px !important;
    min-height:       44px !important;
    width:            100% !important;
    letter-spacing:   0.1px !important;
    -webkit-tap-highlight-color: transparent !important;
}}
.stButton > button:hover:not(:disabled) {{
    filter: brightness(1.07) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px {SHADOW} !important;
}}
.stButton > button:active:not(:disabled) {{
    transform: translateY(0) !important;
    box-shadow: none !important;
}}
.stButton > button:disabled {{
    opacity: 0.28 !important;
    cursor: not-allowed !important;
}}

/* ══════════════════════════════════════════
   ACTION BAR — per-column marker approach
   ══════════════════════════════════════════ */

/* ── Add Task → green ── */
[data-testid="stColumn"]:has(.add-btn-marker) .stButton > button {{
    background: linear-gradient(135deg, #388e3c, #4caf50) !important;
    color: #fff !important; border-color: #2e7d32 !important;
    box-shadow: 0 2px 8px rgba(67,160,71,0.28) !important;
}}
[data-testid="stColumn"]:has(.add-btn-marker) .stButton > button:hover:not(:disabled) {{
    box-shadow: 0 5px 16px rgba(67,160,71,0.40) !important;
    filter: brightness(1.06) !important;
}}

/* ── All Done → blue ── */
[data-testid="stColumn"]:has(.done-btn-marker) .stButton > button:not(:disabled) {{
    background: linear-gradient(135deg, #1565c0, #2196f3) !important;
    color: #fff !important; border-color: #0d47a1 !important;
    box-shadow: 0 2px 8px rgba(21,101,192,0.25) !important;
}}
[data-testid="stColumn"]:has(.done-btn-marker) .stButton > button:not(:disabled):hover {{
    box-shadow: 0 5px 16px rgba(21,101,192,0.38) !important;
    filter: brightness(1.06) !important;
}}

/* ── Sort → purple (JS also handles inline styles + hover) ── */
[data-testid="stColumn"]:has(.sort-btn-marker) .stButton > button:not(:disabled) {{
    background: linear-gradient(135deg, #6a1b9a, #ab47bc) !important;
    color: #fff !important; border-color: #4a148c !important;
    box-shadow: 0 2px 8px rgba(106,27,154,0.28) !important;
}}
[data-testid="stColumn"]:has(.sort-btn-marker) .stButton > button:not(:disabled):hover {{
    box-shadow: 0 5px 16px rgba(106,27,154,0.42) !important;
    filter: brightness(1.08) !important;
}}

/* ── Clear → red outline ── */
[data-testid="stColumn"]:has(.clear-btn-marker) .stButton > button {{
    background: transparent !important;
    color: #ef5350 !important;
    border-color: rgba(239,83,80,0.35) !important;
    box-shadow: none !important;
}}
[data-testid="stColumn"]:has(.clear-btn-marker) .stButton > button:hover:not(:disabled) {{
    background: rgba(239,83,80,0.09) !important;
    border-color: #ef5350 !important;
    box-shadow: 0 2px 8px rgba(239,83,80,0.18) !important;
    filter: none !important;
}}

/* ── Copy Week → teal ── */
[data-testid="stColumn"]:has(.copy-week-marker) .stButton > button,
.copy-week-btn .stButton > button {{
    background: linear-gradient(135deg, #00695c, #26a69a) !important;
    color: #fff !important; border-color: #004d40 !important;
    box-shadow: 0 2px 8px rgba(0,105,92,0.25) !important;
}}

/* ── Confirm YES → red ── */
[data-testid="stColumn"]:has(.confirm-yes-marker) .stButton > button {{
    background: linear-gradient(135deg, #c62828, #ef5350) !important;
    color: #fff !important; border-color: #b71c1c !important;
}}

/* ── AI button → purple ── */
[data-testid="stColumn"]:has(.ai-btn-marker) .stButton > button,
.ai-btn-wrap .stButton > button {{
    background: linear-gradient(135deg, #6a1b9a, #ab47bc) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: 15px !important; padding: 14px 20px !important;
    min-height: 50px !important;
    box-shadow: 0 4px 14px rgba(106,27,154,0.28) !important;
}}
[data-testid="stColumn"]:has(.ai-btn-marker) .stButton > button:hover:not(:disabled),
.ai-btn-wrap .stButton > button:hover:not(:disabled) {{
    box-shadow: 0 6px 18px rgba(106,27,154,0.40) !important;
    filter: brightness(1.06) !important;
}}

/* marker spans are invisible */
.add-btn-marker, .done-btn-marker, .sort-btn-marker,
.clear-btn-marker, .copy-week-marker, .confirm-yes-marker,
.ai-btn-marker {{ display: none !important; }}

/* ══════════════════════════════════════════
   STRUCTURAL COMPONENTS
   ══════════════════════════════════════════ */

/* ── Page header ── */
.page-header {{ padding: 4px 0 20px; }}
.page-header-title {{
    font-size: 26px; font-weight: 900; letter-spacing: -0.8px;
    color: {TEXT_PRIMARY} !important; line-height: 1.2;
}}
.page-header-sub {{
    font-size: 13px; color: {TEXT_MUTED} !important;
    margin-top: 4px; font-weight: 500;
}}

/* ── Week overview card ── */
.week-card {{
    background: {OVERVIEW_BG};
    border: 1.5px solid {OVERVIEW_BDR};
    border-radius: 20px; padding: 18px 16px 14px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px {SHADOW};
}}
.week-card-label {{
    font-size: 10px; font-weight: 800; letter-spacing: 1.2px;
    text-transform: uppercase; color: {TEXT_MUTED} !important;
    margin-bottom: 14px;
}}

/* ── Day mini bar (custom — avoids st.progress quirks) ── */
.mini-bar-track {{
    height: 6px; border-radius: 99px;
    background: {PROG_TRACK}; overflow: hidden; margin: 4px 0;
}}
.mini-bar-fill {{
    height: 6px; border-radius: 99px;
    transition: width 0.5s cubic-bezier(.4,0,.2,1);
}}

/* ── Day header ── */
.day-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px; padding-bottom: 12px;
    border-bottom: 1.5px solid {DIVIDER};
}}
.day-header-name {{
    font-size: 20px; font-weight: 900; letter-spacing: -0.3px;
}}
.today-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    background: {TODAY_BG}; color: {TODAY_COLOR} !important;
    border: 1.5px solid {TODAY_COLOR}44;
    font-size: 11px; font-weight: 700;
    padding: 5px 14px; border-radius: 20px;
    white-space: nowrap;
}}
.today-pill span {{ color: {TODAY_COLOR} !important; }}

/* ── Progress bar ── */
.prog-wrap   {{ margin-bottom: 16px; }}
.prog-header {{ display: flex; justify-content: space-between; align-items: center;
                font-size: 12px; margin-bottom: 8px; }}
.prog-label  {{ font-weight: 700; color: {TEXT_PRIMARY} !important; }}
.prog-pct    {{ color: {TEXT_MUTED} !important; font-variant-numeric: tabular-nums;
                font-weight: 700; background: {PROG_TRACK};
                padding: 2px 9px; border-radius: 20px; font-size: 11px; }}
.prog-track  {{ background: {PROG_TRACK}; border-radius: 99px; height: 8px; overflow: hidden; }}
.prog-fill   {{ height: 8px; border-radius: 99px;
                transition: width 0.5s cubic-bezier(.4,0,.2,1); }}

/* ── All-done banner ── */
.all-done-banner {{
    background: linear-gradient(135deg, rgba(76,175,80,0.14), rgba(76,175,80,0.06));
    border: 1.5px solid rgba(76,175,80,0.28);
    border-radius: 14px; padding: 16px; text-align: center;
    font-size: 16px; font-weight: 800;
    color: #4CAF50 !important; margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(76,175,80,0.12);
}}

/* ── Per-day total strip ── */
.day-total-strip {{
    display: flex; align-items: center; gap: 10px;
    background: {TOTAL_BG}; border: 1.5px solid {TOTAL_BDR};
    border-radius: 12px; padding: 10px 16px; margin-bottom: 16px;
    font-size: 12px; font-weight: 700; color: {TOTAL_COLOR} !important;
}}
.day-total-strip span {{ color: {TOTAL_COLOR} !important; }}

/* ── Time pill ── */
.time-pill {{
    display: inline-flex; align-items: center; gap: 5px;
    background: {PILL_BG}; color: {PILL_COLOR} !important;
    border: 1.5px solid {PILL_BORDER};
    font-size: 11px; font-weight: 700;
    padding: 4px 10px; border-radius: 20px;
    margin-bottom: 5px; white-space: nowrap;
    font-variant-numeric: tabular-nums;
}}

/* ── Duration badge ── */
.duration-badge {{
    font-size: 10px; color: {DURATION_CLR} !important;
    display: block; text-align: center; margin-top: 3px;
    font-weight: 700; background: {PROG_TRACK};
    border-radius: 6px; padding: 1px 4px;
}}

/* ── Empty state ── */
.empty-day {{
    text-align: center; padding: 48px 16px 40px;
    color: {EMPTY_CLR} !important;
    background: {TASK_ROW_BG};
    border: 2px dashed {CARD_BORDER};
    border-radius: 18px; margin-bottom: 12px;
}}
.empty-day-icon {{ font-size: 52px; margin-bottom: 16px; display: block;
                   animation: pulse 2.5s ease-in-out infinite; }}
@keyframes pulse {{
    0%,100% {{ transform: scale(1); opacity: 1; }}
    50%      {{ transform: scale(1.06); opacity: 0.8; }}
}}
.empty-day-text {{ font-size: 15px; font-weight: 700; color: {EMPTY_CLR} !important; }}
.empty-day-hint {{ font-size: 12px; margin-top: 8px; opacity: 0.60;
                   color: {EMPTY_CLR} !important; }}

/* ── Danger confirm ── */
.danger-confirm {{
    background: rgba(239,83,80,0.08); border: 1.5px solid rgba(239,83,80,0.25);
    border-radius: 12px; padding: 12px 16px;
    font-size: 13px; font-weight: 700;
    color: #ef5350 !important; text-align: center; margin-bottom: 10px;
}}

/* ── Action bar ── */
.action-bar {{
    background: {SECTION_BG}; border: 1.5px solid {SECTION_BDR};
    border-radius: 14px; padding: 12px 14px; margin-top: 12px;
}}

/* ── AI expander ── */
[data-testid="stExpander"] {{
    background: {AI_EXP_BG} !important;
    border: 1.5px solid {AI_EXP_BDR} !important;
    border-radius: 16px !important; margin-bottom: 16px !important;
    box-shadow: 0 2px 12px {SHADOW} !important; overflow: hidden;
}}
[data-testid="stExpander"] summary {{
    font-weight: 700 !important; font-size: 14px !important;
    padding: 14px 16px !important; color: {TEXT_PRIMARY} !important;
    min-height: 48px !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: rgba(171,71,188,0.04) !important;
}}

/* ── Day radio tabs ── */
[data-testid="stRadio"] > div {{
    gap: 6px !important; flex-wrap: wrap !important;
}}
[data-testid="stRadio"] label {{
    font-size: 12px !important; font-weight: 600 !important;
    min-height: 40px !important;
    display: flex !important; align-items: center !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    background: {OVERVIEW_BG} !important;
    border: 1px solid {OVERVIEW_BDR} !important;
    transition: all 0.15s ease !important;
    -webkit-tap-highlight-color: transparent !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background: {TODAY_BG} !important;
    color: {TODAY_COLOR} !important;
    border-color: {TODAY_COLOR}55 !important;
}}
[data-testid="stRadio"] input[type="radio"] {{ display: none !important; }}

/* ── Divider / toast ── */
hr {{ border-color: {DIVIDER} !important; margin: 14px 0 !important; }}
.stAlert {{ border-radius: 14px !important; font-size: 14px !important; }}

{"""/* ── Arabic RTL ── */
.page-header, .page-header-title, .page-header-sub,
.week-card, .week-card-label,
.day-card, .day-card-header, .day-title,
.task-row, .task-label, .task-time,
.ai-card, .ai-card-title { direction: rtl; text-align: right; }
""" if st.session_state.lang == "arabic" else ""}

/* ── Responsive ── */
@media (max-width: 640px) {{
    .stTimeInput input  {{ font-size: 14px !important; }}
    .stTextInput input  {{ font-size: 16px !important; }}
    .time-pill          {{ font-size: 10px !important; padding: 3px 8px !important; }}
    .page-header-title  {{ font-size: 22px !important; }}
    .day-header-name    {{ font-size: 17px !important; }}
    .week-card          {{ padding: 14px 12px 12px !important; border-radius: 16px !important; }}
    .action-bar         {{ padding: 10px 10px !important; }}
    .all-done-banner    {{ font-size: 14px !important; padding: 14px !important; }}
    .empty-day          {{ padding: 36px 12px 28px !important; border-radius: 14px !important; }}
    .empty-day-icon     {{ font-size: 40px !important; }}
}}
@media (max-width: 380px) {{
    .stButton > button  {{ font-size: 11px !important; padding: 8px 4px !important; }}
    .time-pill          {{ display: none !important; }}
    .day-total-strip    {{ font-size: 11px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  SORT BUTTON JS — purple + hover animation
#
#  st.markdown strips <script> tags. components.html() runs
#  in a sandboxed iframe and reaches the parent document via
#  window.parent — the ONLY reliable way to inject JS.
# ══════════════════════════════════════════════════════════
components.html("""
<script>
(function () {
    var GRAD        = 'linear-gradient(135deg, #6a1b9a, #ab47bc)';
    var BORDER      = '#4a148c';
    var SHADOW_REST = '0 2px 8px rgba(106,27,154,0.30)';
    var SHADOW_HOVER= '0 5px 16px rgba(106,27,154,0.45)';
    var TRANSITION  = 'all 0.18s ease';

    function attachAnimation(btn) {
        if (btn._sortStyled) return;
        btn._sortStyled = true;
        btn.style.setProperty('transition', TRANSITION, 'important');

        btn.addEventListener('mouseenter', function () {
            if (btn.disabled) return;
            btn.style.setProperty('transform',  'translateY(-1px)', 'important');
            btn.style.setProperty('box-shadow', SHADOW_HOVER,       'important');
            btn.style.setProperty('filter',     'brightness(1.08)', 'important');
        });
        btn.addEventListener('mouseleave', function () {
            btn.style.setProperty('transform',  'translateY(0)', 'important');
            btn.style.setProperty('box-shadow', SHADOW_REST,     'important');
            btn.style.removeProperty('filter');
        });
        btn.addEventListener('mousedown', function () {
            if (btn.disabled) return;
            btn.style.setProperty('transform',  'translateY(0)', 'important');
            btn.style.setProperty('box-shadow', 'none',          'important');
        });
        btn.addEventListener('mouseup', function () {
            if (btn.disabled) return;
            btn.style.setProperty('transform',  'translateY(-1px)', 'important');
            btn.style.setProperty('box-shadow', SHADOW_HOVER,       'important');
        });
    }

    function styleSortBtn() {
        try {
            var doc = window.parent.document;
            doc.querySelectorAll('button').forEach(function (btn) {
                var txt = (btn.textContent || btn.innerText || '').trim();
                if (txt.indexOf('🔃') !== -1 && !btn.disabled) {
                    btn.style.setProperty('background',   GRAD,        'important');
                    btn.style.setProperty('color',        '#fff',      'important');
                    btn.style.setProperty('border-color', BORDER,      'important');
                    btn.style.setProperty('box-shadow',   SHADOW_REST, 'important');
                    btn.style.setProperty('transition',   TRANSITION,  'important');
                    attachAnimation(btn);
                }
            });
        } catch (e) {}
    }

    styleSortBtn();
    setInterval(styleSortBtn, 300);
})();
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════════════
#  PAGE HEADER + DARK TOGGLE
# ══════════════════════════════════════════════════════════


# Week-level stats for subtitle
total_tasks_week = sum(
    len([tk for tk in st.session_state.schedule.get(dk, []) if tk.get("task","").strip()])
    for dk, _, _ in DAYS
)
done_tasks_week = sum(
    sum(1 for tk in st.session_state.schedule.get(dk, [])
        if tk.get("task","").strip() and tk.get("done", False))
    for dk, _, _ in DAYS
)
week_pct  = int((done_tasks_week / total_tasks_week) * 100) if total_tasks_week else 0
week_time = fmt_minutes(sum(
    total_day_minutes(st.session_state.schedule.get(dk, [])) for dk, _, _ in DAYS
))

sub_parts = []
if total_tasks_week:
    sub_parts.append(f"{done_tasks_week}/{total_tasks_week} {t('week_tasks')} ({week_pct}%)")
if week_time:
    sub_parts.append(f"{week_time} {t('week_scheduled')}")
sub_str = "  ·  ".join(sub_parts) if sub_parts else {
    "badini":  "هیچ کار نینە ئەڤێ حەفتیێ",
    "english": "No tasks this week yet",
    "arabic":  "لا توجد مهام هذا الأسبوع",
}.get(st.session_state.lang, "No tasks this week yet")

st.markdown(f"""
<div class="page-header">
    <div class="page-header-title">📅 {t("schedule_title")}</div>
    <div class="page-header-sub">{sub_str}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  WEEK OVERVIEW  (custom HTML bars — no st.progress)
# ══════════════════════════════════════════════════════════
_weekly_title = {
    "badini":  "📊 پێشکەفتنا حەفتیانە",
    "english": "📊 WEEKLY OVERVIEW",
    "arabic":  "📊 التقدم الأسبوعي",
}.get(st.session_state.lang, "📊 WEEKLY OVERVIEW")

_week_cols_html = ""
for dk, _, eng in DAYS:
    tasks      = st.session_state.schedule.get(dk, [])
    named      = [tk for tk in tasks if tk.get("task", "").strip()]
    total      = len(named)
    done       = sum(1 for tk in named if tk.get("done", False))
    pct        = done / total if total > 0 else 0.0
    is_today_d = dk == today_key
    short      = eng[:3].upper()
    count      = f"{done}/{total}" if total else "—"
    time_lbl   = fmt_minutes(total_day_minutes(tasks))

    bar_color  = "#4CAF50" if pct == 1.0 and total > 0 else ("#2196F3" if pct > 0 else "#9E9E9E")
    if is_today_d:
        bar_color = "#4CAF50"

    dot_html   = "<div style='text-align:center;font-size:9px;color:#4CAF50;margin-bottom:1px;'>●</div>" if is_today_d else "<div style='height:12px;'></div>"
    day_clr    = "#4CAF50" if is_today_d else TEXT_MUTED
    weight     = "900" if is_today_d else "600"
    fill_w     = f"{pct * 100:.0f}%"
    time_row   = f"<div style='text-align:center;font-size:9px;color:{TEXT_MUTED};opacity:0.70;font-weight:600;margin-top:2px;'>{time_lbl}</div>" if time_lbl else ""

    _week_cols_html += f"""
    <div style="flex:1;display:flex;flex-direction:column;align-items:center;min-width:0;">
        {dot_html}
        <div style="text-align:center;font-size:10px;font-weight:{weight};color:{day_clr};margin-bottom:4px;">{short}</div>
        <div style="width:80%;height:6px;background:{PROG_TRACK};border-radius:99px;overflow:hidden;">
            <div style="height:100%;width:{fill_w};background:{bar_color};border-radius:99px;transition:width 0.5s ease;"></div>
        </div>
        <div style="text-align:center;font-size:10px;color:{TEXT_MUTED};margin-top:3px;font-weight:600;">{count}</div>
        {time_row}
    </div>
    """

components.html(f"""
<div style="background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:16px;
            padding:16px 14px 14px;font-family:Inter,system-ui,sans-serif;">
    <div style="font-size:11px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;
                color:{TEXT_MUTED};margin-bottom:12px;">{_weekly_title}</div>
    <div style="display:flex;gap:4px;justify-content:space-between;align-items:flex-end;">
        {_week_cols_html}
    </div>
</div>
""", height=130)

# ══════════════════════════════════════════════════════════
#  AI SCHEDULER
# ══════════════════════════════════════════════════════════
ai_lbl = {
    "badini":  "🤖 ڕێکخستنی زیرەک ب AI",
    "english": "🤖 AI Smart Scheduler",
    "arabic":  "🤖 الجدولة الذكية بالذكاء الاصطناعي",
}.get(st.session_state.lang, "🤖 AI Smart Scheduler")

if "ai_input"   not in st.session_state: st.session_state.ai_input   = ""
if "ai_loading" not in st.session_state: st.session_state.ai_loading = False

with st.expander(ai_lbl, expanded=False):
    goal_hint = {
        "badini":  "ئارمانجێن خوە بنڤیسە (ب زمانێ ئینگلیزی باشتر کار دکەت):",
        "english": "Describe your study goals (English works best):",
        "arabic":  "اكتب أهدافك الدراسية (الإنجليزية تعمل بشكل أفضل):",
    }.get(st.session_state.lang, "Describe your study goals:")
    st.markdown(
        f"<div style='font-size:13px;font-weight:600;margin-bottom:8px;'>{goal_hint}</div>",
        unsafe_allow_html=True,
    )
    user_goal = st.text_area(
        "Goal", value=st.session_state.ai_input,
        placeholder="e.g., I need to study math for 10 hours, physics for 5 hours. I prefer mornings.",
        label_visibility="collapsed", key="ai_goal_input", height=90,
    )
    st.session_state.ai_input = user_goal

    generate_lbl = "🚀 " + {
        "badini":  "دروست بکە",
        "english": "Generate Schedule",
        "arabic":  "توليد الجدول",
    }.get(st.session_state.lang, "Generate Schedule")

    st.markdown('<span class="ai-btn-marker"></span>', unsafe_allow_html=True)
    st.markdown('<div class="ai-btn-wrap">', unsafe_allow_html=True)
    if st.button(generate_lbl, use_container_width=True, disabled=st.session_state.ai_loading):
        if not user_goal.strip():
            st.error({
                "badini":  "تکایە ئامانجێن خوە بنڤیسە.",
                "english": "Please enter your goals.",
                "arabic":  "يرجى كتابة أهدافك.",
            }.get(st.session_state.lang, "Please enter your goals."))
        else:
            st.session_state.ai_loading = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    
# AI execution block
if st.session_state.ai_loading and st.session_state.ai_input:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error(t("ai_key_error"))
        st.session_state.ai_loading = False

    today_str_ai = datetime.now().strftime("%A")
    prompt = f"""You are a realistic study schedule generator. The user has the following study goals for the upcoming week (starting today, {today_str_ai}):

{st.session_state.ai_input}

CRITICAL RULES FOR REALISTIC SCHEDULES:

1. **No one studies every single day.** Always include at least 1-2 rest days per week (typically Saturday and/or Sunday).
2. **Maximum 2-4 hours of focused study per day.** More than 4 hours is unrealistic and leads to burnout.
3. **If the user mentions a total number of hours (e.g., "10 hours of math")**, distribute it across 4-5 days (not 7 days).
4. **Breaks are mandatory** — include a 15-minute break after every 50-90 minutes of study.
5. **Respect realistic time slots** — typical study times are 9:00-12:00, 13:00-16:00, 18:00-21:00.
6. **Weekends (Sat/Sun) should be lighter** — 1-2 hours max, or rest days.

INTERPRETATION EXAMPLES:

- "I need to study math for 10 hours" → Schedule 2-2.5 hours per day across 4-5 days (Mon-Fri), with rest on Sat/Sun.
- "I need to study physics for 5 hours" → Schedule 1-1.5 hours per day across 3-4 days.
- "I need to study math for 10 hours, physics for 5 hours" → 10 math hours across 4-5 days, 5 physics hours across 3-4 days. Max 3 hours total per day.
- "I need to study 8 hours every day" → User specifically requested this, honor it but include breaks.
- "I prefer evenings" → Schedule sessions after 17:00.

Return ONLY a valid JSON object (no extra text):
{{
  "mon": [{{"start": "HH:MM", "end": "HH:MM", "task": "Subject"}}, ...],
  "tue": [...], "wed": [...], "thu": [...],
  "fri": [...], "sat": [...], "sun": [...]
}}

If the user's goal is unrealistic (e.g., "study 15 hours a day"), politely adjust to a realistic schedule (max 4 hours/day). Do NOT exceed 4 hours of study on any single day unless the user explicitly demands it in capital letters.

Use 24-hour format. Distribute hours per user preferences. Include breaks (15 min after 50-90 min sessions)."""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2, "max_tokens": 2000,
    }
    try:
        with st.spinner("⏳ " + {
            "english": "Generating your schedule…",
            "badini":  "خشتە دروست دکت…",
            "arabic":  "جاري إنشاء الجدول…",
        }.get(st.session_state.lang, "Generating…")):
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=30,
            )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        new_schedule = json.loads(content)
        for day_k in {"sun","mon","tue","wed","thu","fri","sat"}:
            if day_k in new_schedule and isinstance(new_schedule[day_k], list):
                st.session_state.schedule[day_k] = [
                    {"start": item.get("start","08:00"), "end": item.get("end","09:00"),
                     "task": item.get("task","Study"), "done": False}
                    for item in new_schedule[day_k]
                ]
        save_schedule()
        st.session_state.ai_input = ""
        st.success({
            "badini":  "✅ خشتە ب سەرکەفتی دروست بوو!",
            "english": "✅ Schedule generated successfully!",
            "arabic":  "✅ تم إنشاء الجدول بنجاح!",
        }.get(st.session_state.lang, "✅ Schedule generated!"))
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Network error: {str(e)}")
    except json.JSONDecodeError:
        st.error(t("ai_format_error"))
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
    st.session_state.ai_loading = False
    st.rerun()

# ══════════════════════════════════════════════════════════
#  LABEL HELPERS
# ══════════════════════════════════════════════════════════
time_start_label, time_end_label = get_time_label()
col_time_label,   col_task_label = get_column_labels()


def get_tab_label(day_key):
    day_name = get_day_name(day_key)
    tasks = [tk for tk in st.session_state.schedule.get(day_key, [])
             if tk.get("task","").strip()]
    if not tasks:
        return day_name
    done  = sum(1 for tk in tasks if tk.get("done", False))
    total = len(tasks)
    badge = " ✅" if done == total else f" {done}/{total}"
    dot   = " 🔵" if day_key == today_key else ""
    return f"{day_name}{dot}{badge}"


# ══════════════════════════════════════════════════════════
#  DAY SELECTOR
# ══════════════════════════════════════════════════════════
if "active_day" not in st.session_state:
    st.session_state.active_day = today_key

day_labels = [get_tab_label(dk) for dk, _, _ in DAYS]
day_keys   = [dk for dk, _, _ in DAYS]
active_idx = day_keys.index(st.session_state.active_day) if st.session_state.active_day in day_keys else 0

selected_label = st.radio(
    "", day_labels, index=active_idx, horizontal=True,
    label_visibility="collapsed", key="schedule_day_radio",
)
st.session_state.active_day = day_keys[day_labels.index(selected_label)]

# ══════════════════════════════════════════════════════════
#  PER-DAY SCHEDULE VIEW
# ══════════════════════════════════════════════════════════
active_day_key = st.session_state.active_day

for day_key, _, eng_name in DAYS:
    if day_key != active_day_key:
        continue

    schedule    = st.session_state.schedule[day_key]
    day_display = get_day_name(day_key)
    named       = [tk for tk in schedule if tk.get("task","").strip()]
    n_total     = len(named)
    n_done      = sum(1 for tk in named if tk.get("done", False))
    pct         = int((n_done / n_total) * 100) if n_total else 0
    day_time    = fmt_minutes(total_day_minutes(schedule))

    # ── Day header
    is_today_flag = day_key == today_key
    today_pill_html = ""
    if is_today_flag:
        extra_parts = []
        if n_total: extra_parts.append(f"{n_done}/{n_total}")
        if day_time: extra_parts.append(day_time)
        extra = "  ·  ".join(extra_parts)
        today_pill_html = (
            f'<span class="today-pill"><span>🔵 {t("today_badge")}</span>'
            f'<span style="font-weight:500;opacity:0.80;">'
            f'{" · " + extra if extra else ""}</span></span>'
        )

    st.markdown(f"""
    <div class="day-header">
        <div class="day-header-name">{day_display}</div>
        {today_pill_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Clear-day confirmation
    if st.session_state[f"{day_key}_clear_confirm"]:
        warn_msg = {
            "badini":  "⚠️ هەمی کاران ژێببە؟",
            "english": "⚠️ Clear all tasks for this day?",
            "arabic":  "⚠️ مسح جميع المهام لهذا اليوم؟",
        }.get(st.session_state.lang, "⚠️ Clear all tasks?")
        st.markdown(f'<div class="danger-confirm">{warn_msg}</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<span class="confirm-yes-marker"></span>', unsafe_allow_html=True)
            if st.button(
                "✓ " + {"badini":"بەلێ، ژێببە","english":"Yes, clear","arabic":"نعم، امسح"}.get(
                    st.session_state.lang, "Yes"),
                key=f"{day_key}_clear_yes", use_container_width=True,
            ):
                st.session_state.schedule[day_key] = []
                st.session_state[f"{day_key}_reset"] += 1
                st.session_state[f"{day_key}_clear_confirm"] = False
                save_schedule(); st.rerun()
        with cc2:
            if st.button(
                "✗ " + {"badini":"نەخێر","english":"Cancel","arabic":"إلغاء"}.get(
                    st.session_state.lang, "Cancel"),
                key=f"{day_key}_clear_no", use_container_width=True,
            ):
                st.session_state[f"{day_key}_clear_confirm"] = False
                st.rerun()

    # ── Progress bar
    if n_total > 0:
        if n_done == n_total:
            st.markdown(
                f'<div class="all-done-banner">🎉 {t("tasks_completed")} — {n_done}/{n_total} · 100%</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"""
            <div class="prog-wrap">
                <div class="prog-header">
                    <span class="prog-label">{t("tasks_completed")}</span>
                    <span class="prog-pct">{n_done}/{n_total} — {pct}%</span>
                </div>
                <div class="prog-track">
                    <div class="prog-fill" style="width:{pct}%;background:#4CAF50;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Total time strip
    day_total_min = total_day_minutes(schedule)
    if day_total_min > 0:
        done_min = sum(
            max(0, int((datetime.strptime(e.get("end","00:00"), "%H:%M") -
                        datetime.strptime(e.get("start","00:00"), "%H:%M")).total_seconds() // 60))
            for e in schedule
            if e.get("done") and e.get("task","").strip()
        )
        total_lbl = {
            "badini":  f"⏱ هەمی دەم: {fmt_minutes(day_total_min)}",
            "english": f"⏱ Total: {fmt_minutes(day_total_min)}",
            "arabic":  f"⏱ الإجمالي: {fmt_minutes(day_total_min)}",
        }.get(st.session_state.lang, f"⏱ {fmt_minutes(day_total_min)}")
        done_lbl = (
            f"<span style='margin-left:auto;'>✅ {fmt_minutes(done_min)}</span>"
            if done_min else ""
        )
        st.markdown(
            f'<div class="day-total-strip"><span>{total_lbl}</span>{done_lbl}</div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════
    #  TASK LIST
    # ══════════════════════════════════════════
    if not schedule:
        no_tasks = {
            "badini":  "هیچ کار نینە.",
            "english": "No tasks yet.",
            "arabic":  "لا توجد مهام بعد.",
        }.get(st.session_state.lang, "No tasks yet.")
        hint = {
            "badini":  "➕ زێدەکرن کلیک بکە بو دروستکرنا کارەکێ",
            "english": "Tap ➕ Add Task below to get started",
            "arabic":  "انقر على ➕ إضافة مهمة أدناه للبدء",
        }.get(st.session_state.lang, "Tap ➕ Add Task below to get started")
        st.markdown(f"""
        <div class="empty-day">
            <span class="empty-day-icon">📭</span>
            <div class="empty-day-text">{no_tasks}</div>
            <div class="empty-day-hint">{hint}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Column header row
        h1, h2, h3, h4 = st.columns([2.8, 0.7, 4.8, 0.7])
        with h1:
            st.markdown(
                f'<div style="font-size:10px;font-weight:800;letter-spacing:0.9px;'
                f'text-transform:uppercase;color:{TEXT_MUTED};padding-bottom:6px;'
                f'border-bottom:2px solid {TEXT_MUTED}33;">🕐 {col_time_label}</div>',
                unsafe_allow_html=True,
            )
        with h2:
            st.markdown(
                f'<div style="font-size:10px;font-weight:800;letter-spacing:0.9px;'
                f'text-transform:uppercase;color:{TEXT_MUTED};padding-bottom:6px;'
                f'border-bottom:2px solid {TEXT_MUTED}33;">✓</div>',
                unsafe_allow_html=True,
            )
        with h3:
            st.markdown(
                f'<div style="font-size:10px;font-weight:800;letter-spacing:0.9px;'
                f'text-transform:uppercase;color:{TEXT_MUTED};padding-bottom:6px;'
                f'border-bottom:2px solid {TEXT_MUTED}33;">📝 {col_task_label}</div>',
                unsafe_allow_html=True,
            )
        with h4:
            st.markdown(
                f'<div style="font-size:10px;font-weight:800;padding-bottom:6px;'
                f'border-bottom:2px solid {TEXT_MUTED}33;"></div>',
                unsafe_allow_html=True,
            )

        changed      = False
        done_changed = False

        for i, entry in enumerate(schedule):
            c_time, c_done, c_task, c_del = st.columns([2.8, 0.7, 4.8, 0.7])

            with c_time:
                try:    start_val = datetime.strptime(entry["start"], "%H:%M").time()
                except: start_val = datetime.strptime("07:00", "%H:%M").time()
                try:    end_val   = datetime.strptime(entry["end"],   "%H:%M").time()
                except: end_val   = datetime.strptime("08:00", "%H:%M").time()

                _sk     = f"{day_key}_start_{i}_{st.session_state[f'{day_key}_reset']}"
                _ek     = f"{day_key}_end_{i}_{st.session_state[f'{day_key}_reset']}"
                _live_s = st.session_state.get(_sk, start_val)
                _live_e = st.session_state.get(_ek, end_val)
                _cap_s  = _live_s.strftime("%H:%M") if hasattr(_live_s,"strftime") else entry.get("start","--:--")
                _cap_e  = _live_e.strftime("%H:%M") if hasattr(_live_e,"strftime") else entry.get("end","--:--")

                st.markdown(
                    f'<div class="time-pill">🕐 {_cap_s}→{_cap_e}</div>',
                    unsafe_allow_html=True,
                )
                start_time = st.time_input(time_start_label, value=start_val, key=_sk,
                                           label_visibility="collapsed")
                end_time   = st.time_input(time_end_label,   value=end_val,   key=_ek,
                                           label_visibility="collapsed")
                dur = format_duration(start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))
                if dur:
                    st.markdown(f'<span class="duration-badge">⏱ {dur}</span>',
                                unsafe_allow_html=True)

            with c_done:
                done = st.checkbox(
                    "", value=entry.get("done", False),
                    key=f"{day_key}_done_{i}_{st.session_state[f'{day_key}_reset']}",
                    label_visibility="collapsed",
                )

            with c_task:
                task_text = st.text_input(
                    "", value=entry.get("task",""),
                    key=f"{day_key}_task_{i}_{st.session_state[f'{day_key}_reset']}",
                    disabled=done, label_visibility="collapsed",
                    placeholder=t("activity_placeholder"),
                )

            with c_del:
                delete_btn = st.button(
                    "✕", key=f"{day_key}_del_{i}_{st.session_state[f'{day_key}_reset']}"
                )

            # Sync
            if entry.get("done", False) != done:
                entry["done"] = done; changed = done_changed = True
            if entry.get("task","") != task_text:
                entry["task"] = task_text; changed = True
            ns = start_time.strftime("%H:%M")
            if entry.get("start") != ns:
                entry["start"] = ns; changed = True
            ne = end_time.strftime("%H:%M")
            if entry.get("end") != ne:
                entry["end"] = ne; changed = True

            if delete_btn:
                schedule.pop(i)
                st.session_state.schedule[day_key] = schedule
                st.session_state[f"{day_key}_reset"] += 1
                save_schedule(); st.rerun()

        if changed:
            st.session_state.schedule[day_key] = schedule
            save_schedule()
            if done_changed: st.rerun()

    # ══════════════════════════════════════════
    #  ACTION BAR
    # ══════════════════════════════════════════
    st.markdown('<div class="action-bar">', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.markdown('<span class="add-btn-marker"></span>', unsafe_allow_html=True)
        add_lbl = {"badini":"➕ زێدەکرن","english":"➕ Add","arabic":"➕ إضافة"}.get(
            st.session_state.lang, "➕ Add")
        if st.button(add_lbl, key=f"{day_key}_add_{st.session_state[f'{day_key}_reset']}",
                     use_container_width=True):
            schedule.append({"start":"08:00","end":"09:00","task":"","done":False})
            st.session_state.schedule[day_key] = schedule
            save_schedule(); st.rerun()

    with b2:
        st.markdown('<span class="done-btn-marker"></span>', unsafe_allow_html=True)
        has_incomplete = any(not e.get("done", False) for e in schedule)
        if st.button(
            {"badini":"✅ هەموو","english":"✅ Done","arabic":"✅ إتمام"}.get(
                st.session_state.lang, "✅ Done"),
            key=f"{day_key}_markall_{st.session_state[f'{day_key}_reset']}",
            use_container_width=True, disabled=not has_incomplete,
        ):
            for e in schedule: e["done"] = True
            st.session_state[f"{day_key}_reset"] += 1
            st.session_state.schedule[day_key] = schedule
            save_schedule(); st.rerun()

    with b3:
        st.markdown('<span class="sort-btn-marker"></span>', unsafe_allow_html=True)
        sort_lbl = {"badini":"🔃 ڕیزکرن","english":"🔃 Sort","arabic":"🔃 ترتيب"}.get(
            st.session_state.lang, "🔃 Sort")
        if st.button(sort_lbl,
                     key=f"{day_key}_sort_{st.session_state[f'{day_key}_reset']}",
                     use_container_width=True, disabled=len(schedule) <= 1,
                     help="Sort by start time"):
            schedule.sort(key=lambda e: parse_time(e.get("start","00:00")))
            st.session_state.schedule[day_key] = schedule
            st.session_state[f"{day_key}_reset"] += 1
            save_schedule(); st.rerun()

    with b4:
        st.markdown('<span class="clear-btn-marker"></span>', unsafe_allow_html=True)
        clear_lbl = {"badini":"🗑️ ژێبرن","english":"🗑️ Clear","arabic":"🗑️ مسح"}.get(
            st.session_state.lang, "🗑️ Clear")
        if st.button(clear_lbl,
                     key=f"{day_key}_clear_{st.session_state[f'{day_key}_reset']}",
                     use_container_width=True, disabled=not schedule):
            st.session_state[f"{day_key}_clear_confirm"] = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  COPY DAY TO ANOTHER DAY
    # ══════════════════════════════════════════
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    copy_day_lbl = {
        "badini":  "📋 ڕۆژێ کۆپی بکە بو ڕۆژەکێ دی",
        "english": "📋 Copy This Day to Another Day",
        "arabic":  "📋 نسخ اليوم إلى يوم آخر",
    }.get(st.session_state.lang, "📋 Copy This Day to Another Day")

    with st.expander(copy_day_lbl, expanded=False):
        target_days       = [(dk, get_day_name(dk)) for dk, _, _ in DAYS if dk != active_day_key]
        target_day_labels = [name for _, name in target_days]
        target_day_keys   = [dk   for dk, _   in target_days]

        if target_day_labels:
            col_target, col_btn = st.columns([3, 1])
            with col_target:
                target_label = {
                    "badini":  "ڕۆژا ئامانجی",
                    "english": "Target day",
                    "arabic":  "اليوم المستهدف",
                }.get(st.session_state.lang, "Target day")
                st.markdown(
                    f"<div style='font-size:11px;color:{TEXT_MUTED};font-weight:700;"
                    f"letter-spacing:0.5px;margin-bottom:4px;'>👉 {target_label}</div>",
                    unsafe_allow_html=True,
                )
                target_day = st.selectbox(
                    "Target day", target_day_labels,
                    key=f"copy_day_target_{active_day_key}",
                    label_visibility="collapsed",
                )
            with col_btn:
                selected_target_key = target_day_keys[target_day_labels.index(target_day)]
                copy_day_btn_lbl = {
                    "badini":  "📋 کۆپی",
                    "english": "📋 Copy",
                    "arabic":  "📋 نسخ",
                }.get(st.session_state.lang, "📋 Copy")
                st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
                if st.button(copy_day_btn_lbl,
                             key=f"copy_day_btn_{active_day_key}",
                             use_container_width=True):
                    st.session_state.schedule[selected_target_key] = [
                        {
                            "start": task_item.get("start","08:00"),
                            "end":   task_item.get("end",  "09:00"),
                            "task":  task_item.get("task", ""),
                            "done":  False,
                        }
                        for task_item in st.session_state.schedule[active_day_key]
                    ]
                    st.session_state[f"{selected_target_key}_reset"] += 1
                    save_schedule()
                    st.toast({
                        "badini":  f"✅ هاتە کۆپیکرن بۆ {get_day_name(selected_target_key)}!",
                        "english": f"✅ Copied to {get_day_name(selected_target_key)}!",
                        "arabic":  f"✅ تم النسخ إلى {get_day_name(selected_target_key)}!",
                    }.get(st.session_state.lang, "✅ Copied!"))

# ══════════════════════════════════════════════════════════
#  COPY WEEK TO NEXT
# ══════════════════════════════════════════════════════════
st.divider()
copy_lbl = {
    "badini":  "📋 کوپی بکە بو حەفتیا دهێت",
    "english": "📋 Copy Schedule to Next Week",
    "arabic":  "📋 نسخ إلى الأسبوع القادم",
}.get(st.session_state.lang, "📋 Copy Schedule to Next Week")

st.markdown('<div class="copy-week-btn">', unsafe_allow_html=True)
st.markdown('<span class="copy-week-marker"></span>', unsafe_allow_html=True)
if st.button(copy_lbl, use_container_width=True):
    copy_week_to_next()
    st.toast({
        "badini":  "✅ حەفتی هاتە کۆپیکرن!",
        "english": "✅ Week copied — tasks reset to pending.",
        "arabic":  "✅ تم نسخ الأسبوع بنجاح!",
    }.get(st.session_state.lang, "✅ Week copied!"))
    time.sleep(0.8)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown(
    f"<div style='text-align:center;font-size:11px;color:{TEXT_MUTED};padding:4px 0 8px;'>"
    f"📅 {t('schedule_title')}</div>",
    unsafe_allow_html=True,
)
