import streamlit as st
import json
import os
import hashlib
import base64
import streamlit.components.v1 as components
from datetime import datetime
from utils import save_data, load_data, save_preferences, load_preferences, get_schedule_data
import time

# ══════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════
with open("translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

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
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Rekxare Dami",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<link rel="manifest" href="/manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1a1a2e">
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js').catch(function(){});
  }
</script>
""", unsafe_allow_html=True)

if st.user.is_logged_in:
    if "user_email" not in st.session_state or not st.session_state.user_email:
        st.session_state.user_email = st.user.email
        st.session_state.data_key   = hashlib.md5(st.user.email.encode()).hexdigest()[:8]
        st.session_state.logged_in  = True
    if "prefs_loaded" not in st.session_state:
        load_preferences()
        st.session_state.prefs_loaded = True

# ══════════════════════════════════════════════════════════
#  LOGIN GATE
# ══════════════════════════════════════════════════════════
if not st.user.is_logged_in:
    # Load logo as base64 for login page
    try:
        with open("logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="width:80px; height:80px; border-radius:16px; filter:drop-shadow(0 4px 20px rgba(76,175,80,0.4));">'
    except FileNotFoundError:
        logo_img = '<span style="font-size:72px;">📚</span>'

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
html,body,.stApp,[data-testid="stAppViewContainer"],
section[data-testid="stMain"],.main,.main .block-container{{
    background:linear-gradient(135deg,#0f0c29,#1a1a2e,#16213e)!important;
    font-family:'Inter',system-ui,sans-serif!important;
}}
header[data-testid="stHeader"]{{height:0!important;overflow:hidden!important;}}
/* ── Hide sidebar and all related elements ── */
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],
[data-testid="stStatusWidget"],[data-testid="stToolbar"],
[data-testid="stDecoration"],#MainMenu,footer{{display:none!important;}}
/* ── Force sidebar hidden even if JS tries to show it ── */
body:not(.st-logged-in) section[data-testid="stSidebar"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    min-width: 0 !important;
    transform: translateX(-999px) !important;
    pointer-events: none !important;
}}
.main .block-container{{
    padding-top:max(20px,calc(50vh - 280px))!important;
    padding-bottom:40px!important;padding-left:20px!important;
    padding-right:20px!important;max-width:480px!important;
}}
.lw{{width:100%;display:flex;flex-direction:column;align-items:center;}}
.ll{{line-height:1;margin-bottom:16px;animation:lfloat 3s ease-in-out infinite,lglow 3s ease-in-out infinite;}}
@keyframes lfloat{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-10px);}}}}
@keyframes lglow{{
  0%,100%{{filter:drop-shadow(0 4px 16px rgba(76,175,80,.4));}}
  50%{{filter:drop-shadow(0 4px 28px rgba(76,175,80,.85));}}
}}
.lt{{font-size:32px;font-weight:900;letter-spacing:-.8px;color:#fff;text-align:center;margin-bottom:4px;}}
.ls{{font-size:14px;color:rgba(255,255,255,.55);text-align:center;margin-bottom:24px;font-weight:500;}}
.lb{{display:inline-flex;align-items:center;gap:6px;background:rgba(76,175,80,.15);
    border:1px solid rgba(76,175,80,.25);color:#81c784;border-radius:20px;
    padding:5px 14px;font-size:11px;font-weight:700;letter-spacing:.5px;margin-bottom:24px;}}
.lc{{background:rgba(0,0,0,.5);border:1.5px solid rgba(255,255,255,.13);border-radius:28px;
    padding:32px 28px 28px;width:100%;backdrop-filter:blur(12px);box-shadow:0 8px 40px rgba(0,0,0,.40);}}
.stButton>button{{background:linear-gradient(135deg,#388e3c,#4caf50)!important;
    color:#fff!important;border:none!important;border-radius:40px!important;
    font-weight:700!important;font-size:14px!important;min-height:44px!important;
    box-shadow:0 2px 8px rgba(76,175,80,.3)!important;transition:all .18s ease!important;width:100%!important;}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 16px rgba(76,175,80,.45)!important;}}
.lc .stButton>button{{font-size:16px!important;min-height:52px!important;}}
.dv{{display:flex;align-items:center;gap:12px;margin:24px 0 20px;color:rgba(255,255,255,.35);font-size:12px;font-weight:600;}}
.dv::before,.dv::after{{content:"";flex:1;height:1px;background:rgba(255,255,255,.15);}}
.lf{{font-size:12px;color:rgba(255,255,255,.30);text-align:center;margin-top:24px;}}
/* ── Improved spacing for language buttons ── */
.lang-row .stButton button {{
    font-size:14px !important;
    min-height:48px !important;
    padding:8px 12px !important;
}}
.lang-row {{
    gap: 12px !important;
    margin-bottom: 24px !important;
}}
</style>
<div class="lw">
  <div class="ll">{logo_img}</div>
  <div class="lt">Rekxare Dami</div>
  <div class="ls">{t('login_sub')}</div>
  <div class="lb">✨ {t('login_badge')}</div>
  <div class="lc">
""", unsafe_allow_html=True)

    # Language buttons with better spacing
    st.markdown('<div class="lang-row">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        if st.button("بادينى", key="lang_badini_login", use_container_width=True):
            st.session_state.lang = "badini"; st.rerun()
    with c2:
        if st.button("English", key="lang_en_login", use_container_width=True):
            st.session_state.lang = "english"; st.rerun()
    with c3:
        if st.button("العربية", key="lang_ar_login", use_container_width=True):
            st.session_state.lang = "arabic"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="dv">{t("login_divider")}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.button("🔐 Google", on_click=st.login, use_container_width=True)
    st.markdown(f'<div class="lf">{t("login_footer")}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()
    
# ══════════════════════════════════════════════════════════
#  QUERY PARAM HANDLERS
# ══════════════════════════════════════════════════════════
if "dark_mode" in st.query_params:
    st.session_state.dark_mode = not st.session_state.get("dark_mode", True)
    save_preferences()
    st.query_params.clear()
    st.rerun()

if st.query_params.get("lang") == "cycle":
    order = ["badini", "english", "arabic"]
    cur = st.session_state.get("lang", "badini")
    st.session_state.lang = order[(order.index(cur) + 1) % 3] if cur in order else "badini"
    save_preferences()
    st.query_params.clear()
    st.rerun()

# ══════════════════════════════════════════════════════════
#  NAVIGATION
# ══════════════════════════════════════════════════════════
pg = st.navigation(
    [
        st.Page("Home.py",              title="Rekxare Dami · " + t("nav_timer"),    icon="⏱️", default=True),
        st.Page("pages/01_Schedule.py", title="Rekxare Dami · " + t("nav_schedule"), icon="📅", url_path="schedule"),
        st.Page("pages/02_About.py",    title="Rekxare Dami · " + t("nav_about"),    icon="✨",  url_path="about"),
    ],
    position="hidden",
)

_upath = getattr(pg, "url_path", "") or ""
if _upath == "schedule":
    _active = "schedule"
elif _upath == "about":
    _active = "about"
else:
    _active = "home"

st.session_state.current_page = _active

# ══════════════════════════════════════════════════════════
#  SIDEBAR CONTENT
#
#  MUST run before render_nav().
#  Without at least one st.sidebar call, Streamlit does NOT
#  render section[data-testid="stSidebar"] in the DOM, so
#  JS from the iframe component cannot find the element.
# ══════════════════════════════════════════════════════════
def render_sidebar():
    is_dark    = st.session_state.get("dark_mode", True)
    lang       = st.session_state.get("lang", "badini")
    dark_icon  = "☀️" if is_dark else "🌙"
    mode_label = t("light_mode") if is_dark else t("dark_mode")
    lang_abbr  = {"badini": "BA", "english": "EN", "arabic": "AR"}.get(lang, "EN")
    user_name  = (st.user.name or st.user.email or "Student")[:24] if st.user.is_logged_in else "Student"
    user_email = st.user.email if st.user.is_logged_in else ""

    try:
        with open("logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:28px; width:28px; border-radius:8px;">'
    except FileNotFoundError:
        logo_html = '<span style="font-size:24px;">📚</span>'

    # ── Theme tokens ──
    if is_dark:
        SB_BG           = "#0e0c24"
        SB_CARD_BG      = "rgba(255,255,255,0.05)"
        SB_CARD_BDR     = "rgba(255,255,255,0.08)"
        SB_TEXT         = "#e2e2e2"
        SB_MUTED        = "#8a8fa8"
        SB_ACT_BG       = "rgba(76,175,80,0.18)"
        SB_ACT_C        = "#81c784"
        SB_HOV_BG       = "rgba(255,255,255,0.06)"
        SB_DIVIDER      = "rgba(255,255,255,0.08)"
        SB_SHADOW       = "0 8px 32px rgba(0,0,0,0.5)"
        SB_AVATAR_GRAD  = "linear-gradient(135deg, #388e3c, #66bb6a)"
        SB_BTN_BG       = "rgba(255,255,255,0.06)"
        SB_BTN_HOVER_BG = "rgba(76,175,80,0.20)"
        SB_BTN_BORDER   = "rgba(255,255,255,0.15)"   # subtle light border on dark
    else:
        SB_BG           = "#f4f6f8"
        SB_CARD_BG      = "#ffffff"
        SB_CARD_BDR     = "#dde3ed"
        SB_TEXT         = "#1a1a2e"
        SB_MUTED        = "#6b7280"
        SB_ACT_BG       = "rgba(46,125,50,0.10)"
        SB_ACT_C        = "#2e7d32"
        SB_HOV_BG       = "rgba(0,0,0,0.04)"
        SB_DIVIDER      = "#e2e8f0"
        SB_SHADOW       = "0 8px 32px rgba(0,0,0,0.10)"
        SB_AVATAR_GRAD  = "linear-gradient(135deg, #2e7d32, #4caf50)"
        SB_BTN_BG       = "#edf0f7"
        SB_BTN_HOVER_BG = "rgba(46,125,50,0.12)"
        SB_BTN_BORDER   = "#b0b8c8"                 # visible gray for light mode

    with st.sidebar:
        st.markdown(f"""
        <style>
        /* ── Sidebar width ── */
        section[data-testid="stSidebar"] {{
            width: 300px !important;
            min-width: 300px !important;
            background: {SB_BG} !important;
            padding: 16px 14px !important;
            box-shadow: {SB_SHADOW} !important;
            border-right: 1px solid {SB_CARD_BDR} !important;
            font-family: 'Inter', system-ui, sans-serif !important;
        }}
        [data-testid="stSidebarCollapsedControl"] {{
            display: none !important;
        }}
        section[data-testid="stSidebar"] ::-webkit-scrollbar {{
            width: 3px;
        }}
        section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
            background: {SB_MUTED}44;
            border-radius: 3px;
        }}

        .sb-card {{
            background: {SB_CARD_BG};
            border: 1px solid {SB_CARD_BDR};
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .sb-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.07);
        }}
        .sb-card-title {{
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {SB_MUTED};
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .sb-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .sb-brand-name {{
            font-size: 18px;
            font-weight: 900;
            letter-spacing: -0.3px;
            color: {SB_TEXT};
        }}
        .sb-brand-sub {{
            font-size: 10px;
            color: {SB_MUTED};
            font-weight: 500;
            margin-top: 1px;
        }}

        .sb-user {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .sb-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {SB_AVATAR_GRAD};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
            color: #fff;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(76,175,80,0.25);
            transition: transform 0.25s ease;
        }}
        .sb-user:hover .sb-avatar {{
            transform: scale(1.04);
        }}
        .sb-user-name {{
            font-size: 13px;
            font-weight: 700;
            color: {SB_TEXT};
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .sb-user-email {{
            font-size: 8px;
            color: {SB_MUTED};
            font-weight: 500;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-top: 1px;
        }}

        .sb-nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 6px 10px;
            border-radius: 8px;
            transition: all 0.15s ease;
            margin-bottom: 2px;
        }}
        .sb-nav-item:hover {{
            background: {SB_HOV_BG};
            transform: translateX(3px);
        }}
        .sb-nav-item a {{
            text-decoration: none !important;
            color: {SB_TEXT} !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            display: flex;
            align-items: center;
            gap: 10px;
            width: 100%;
        }}
        .sb-nav-item a[aria-current="page"] {{
            color: {SB_ACT_C} !important;
            font-weight: 700 !important;
        }}
        .sb-nav-icon {{
            font-size: 16px;
            width: 20px;
            text-align: center;
            flex-shrink: 0;
        }}

        .sb-stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }}
        .sb-stat-item {{
            background: {SB_HOV_BG};
            border-radius: 10px;
            padding: 8px 4px;
            text-align: center;
            transition: background 0.2s;
        }}
        .sb-stat-item:hover {{
            background: {SB_ACT_BG};
        }}
        .sb-stat-number {{
            font-size: 16px;
            font-weight: 800;
            color: {SB_TEXT};
            line-height: 1.2;
        }}
        .sb-stat-label {{
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            color: {SB_MUTED};
            letter-spacing: 0.4px;
            margin-top: 2px;
        }}

        /* ── Settings ── */
        .sb-settings .stExpander {{
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        .sb-settings .stExpander summary {{
            font-weight: 600 !important;
            font-size: 12px !important;
            color: {SB_TEXT} !important;
            padding: 4px 0 !important;
        }}
        .sb-settings .stExpander summary:hover {{
            color: {SB_ACT_C} !important;
        }}

        .sb-settings .stButton button,
        .sb-settings .stDownloadButton button {{
            width: 100% !important;
            background: {SB_BTN_BG} !important;
            color: {SB_TEXT} !important;
            border: 1.5px solid {SB_BTN_BORDER} !important;
            border-radius: 10px !important;
            padding: 6px 8px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            transition: all 0.18s ease !important;
            min-height: 32px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
            white-space: nowrap !important;
        }}
        .sb-settings .stButton button:hover,
        .sb-settings .stDownloadButton button:hover {{
            background: {SB_BTN_HOVER_BG} !important;
            border-color: {SB_ACT_C} !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.07) !important;
        }}
        /* Extra compact for download buttons (JSON/CSV) */
        .sb-settings .stDownloadButton button {{
            font-size: 10px !important;
            padding: 4px 6px !important;
            min-height: 28px !important;
        }}
        .sb-settings .stSlider {{
            margin-bottom: 8px;
        }}

        .sb-logout .stButton button {{
            background: transparent !important;
            color: #ef5350 !important;
            border: 1.5px solid rgba(239,83,80,0.30) !important;
            border-radius: 10px !important;
            padding: 8px 10px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            transition: all 0.18s ease !important;
            min-height: 38px !important;
            white-space: nowrap !important;
        }}
        .sb-logout .stButton button:hover {{
            background: rgba(239,83,80,0.10) !important;
            border-color: #ef5350 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(239,83,80,0.15);
        }}

        .sb-divider {{
            border: none;
            height: 1px;
            background: {SB_DIVIDER};
            margin: 8px 0;
        }}
        .sb-footer {{
            font-size: 9px;
            color: {SB_MUTED};
            text-align: center;
            opacity: 0.4;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid {SB_DIVIDER};
        }}

        @keyframes sbFadeInUp {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .sb-card {{
            animation: sbFadeInUp 0.4s ease backwards;
        }}
        .sb-card:nth-child(1) {{ animation-delay: 0.05s; }}
        .sb-card:nth-child(2) {{ animation-delay: 0.10s; }}
        .sb-card:nth-child(3) {{ animation-delay: 0.15s; }}
        .sb-card:nth-child(4) {{ animation-delay: 0.20s; }}
        .sb-card:nth-child(5) {{ animation-delay: 0.25s; }}
        </style>
        """, unsafe_allow_html=True)

        # ─── 1. Brand ───
        st.markdown(f"""
        <div class="sb-card">
            <div class="sb-brand">
                {logo_html}
                <div>
                    <div class="sb-brand-name">Rekxare Dami</div>
                    <div class="sb-brand-sub">{t('app_title')}</div>
                </div>
            </div>
            <div style="font-size:10px; color:{SB_MUTED}; font-weight:500; opacity:0.6; margin-top:2px;">
                {t('slogan')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── 2. User ───
        st.markdown(f"""
        <div class="sb-card">
            <div class="sb-user">
                <div class="sb-avatar">{user_name[0].upper() if user_name else '?'}</div>
                <div class="sb-user-info" style="flex:1; min-width:0;">
                    <div class="sb-user-name">{user_name}</div>
                    <div class="sb-user-email">{user_email}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── 3. Navigation ───
        st.markdown('<div class="sb-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sb-card-title">{t("nav_timer")} / {t("nav_schedule")} / {t("nav_about")}</div>', unsafe_allow_html=True)
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<span class="sb-nav-icon">⏱️</span>', unsafe_allow_html=True)
            with col2:
                st.page_link("Home.py", label=t("nav_timer"), icon=None)
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<span class="sb-nav-icon">📅</span>', unsafe_allow_html=True)
            with col2:
                st.page_link("pages/01_Schedule.py", label=t("nav_schedule"), icon=None)
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown('<span class="sb-nav-icon">✨</span>', unsafe_allow_html=True)
            with col2:
                st.page_link("pages/02_About.py", label=t("nav_about"), icon=None)
        st.markdown('</div>', unsafe_allow_html=True)

        # ─── Divider ───
        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ─── 4. Stats ───
        total_seconds = st.session_state.get("total_study_seconds", 0)
        total_hours = total_seconds // 3600
        total_mins  = (total_seconds % 3600) // 60
        sessions    = st.session_state.get("completed_sessions", 0)
        streak      = st.session_state.get("streak", 0)
        daily_seconds = st.session_state.get("daily_seconds", 0)
        today_mins  = daily_seconds // 60

        st.markdown(f"""
        <div class="sb-card">
            <div class="sb-card-title">{t('sidebar_title')}</div>
            <div class="sb-stats-grid">
                <div class="sb-stat-item">
                    <div class="sb-stat-number">{total_hours}h {total_mins}m</div>
                    <div class="sb-stat-label">{t('total_time')}</div>
                </div>
                <div class="sb-stat-item">
                    <div class="sb-stat-number">{sessions}</div>
                    <div class="sb-stat-label">{t('sessions')}</div>
                </div>
                <div class="sb-stat-item">
                    <div class="sb-stat-number">{streak}</div>
                    <div class="sb-stat-label">{t('streak_days')}</div>
                </div>
                <div class="sb-stat-item">
                    <div class="sb-stat-number">{today_mins}m</div>
                    <div class="sb-stat-label">{t('today_goal')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── Divider ───
        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ─── 5. Settings ───
        st.markdown(f"""
        <div class="sb-card sb-settings">
            <div class="sb-card-title">{t('settings')}</div>
        """, unsafe_allow_html=True)

        with st.expander("⚙️ " + t("settings"), expanded=False):
            # ─── Dark mode toggle ───
            dark_label = ("☀️ " + t("light_mode")) if is_dark else (" " + t("dark_mode"))
            if st.button(dark_label, key="sidebar_darkmode_btn", use_container_width=True):
                st.session_state.dark_mode = not st.session_state.get("dark_mode", True)
                save_preferences()
                st.rerun()
        
            # ─── Language cycle ───
            lang_display = {"badini": "🌐 بادينى", "english": "🌐 English", "arabic": "🌐 العربية"}.get(lang, "🌐 Lang")
            if st.button(lang_display, key="sidebar_lang_btn", use_container_width=True):
                order = ["badini", "english", "arabic"]
                cur   = st.session_state.get("lang", "badini")
                st.session_state.lang = order[(order.index(cur) + 1) % 3] if cur in order else "badini"
                save_preferences()
                st.rerun()
        
            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            daily_goal_seconds = st.session_state.get("daily_goal_seconds", 7200)
            goal_mins = st.slider(
                f'🎯 {t("today_goal")} ({t("minutes_unit")})',
                30, 480, daily_goal_seconds // 60, step=15,
                key="sb_goal_slider"
            )
            if goal_mins * 60 != daily_goal_seconds:
                st.session_state.daily_goal_seconds = goal_mins * 60
                try:
                    save_data()
                except NameError:
                    pass
            
            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            if st.button("🔊 " + t("test_audio"), use_container_width=True, key="sb_audio_test"):
                components.html("""
                <script>
                    try {
                        var ctx = new (window.AudioContext || window.webkitAudioContext)();
                        var osc = ctx.createOscillator();
                        var gain = ctx.createGain();
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.type = 'sine';
                        osc.frequency.value = 880;
                        osc.start();
                        gain.gain.setValueAtTime(0.25, ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.8);
                        osc.stop(ctx.currentTime + 0.8);
                    } catch(e) {
                        console.log("Audio error:", e);
                    }
                </script>
                """, height=0)
                st.success("🔊 " + t("audio_test_success"))
                time.sleep(0.5)
                st.rerun()

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            if not st.session_state.get("confirm_clear", False):
                if st.button(t("clear_stats"), use_container_width=True, key="sb_clear_stats"):
                    st.session_state.confirm_clear = True
                    st.rerun()
            else:
                st.markdown(
                    f'<div style="background:rgba(239,83,80,0.08); border:1px solid rgba(239,83,80,0.25); border-radius:10px; padding:8px 10px; text-align:center; font-size:12px; font-weight:700; color:#ef5350; margin-bottom:8px;">⚠️ {t("clear_stats")}?</div>',
                    unsafe_allow_html=True
                )
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("✓", use_container_width=True, key="sb_confirm_yes"):
                        for k, v in [("total_study_seconds", 0), ("completed_sessions", 0),
                                     ("last_subject", "—"), ("study_history", []),
                                     ("streak", 0), ("daily_seconds", 0), ("last_study_date", ""),
                                     ("xp_points", 0), ("xp_level", 1)]:
                            st.session_state[k] = v
                        st.session_state.confirm_clear = False
                        try:
                            save_data()
                        except NameError:
                            pass
                        st.rerun()
                with cc2:
                    if st.button("✗", use_container_width=True, key="sb_confirm_no"):
                        st.session_state.confirm_clear = False
                        st.rerun()

            st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

            # ─── Export data (stacked vertically) ───
            with st.expander(t("export_data"), expanded=False):
                def json_serial(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")

                export_data = {
                    "export_info": {
                        "generated": datetime.now().isoformat(),
                        "app_version": "Rekxare Dami 1.0",
                        "user": st.session_state.get("user_email", "unknown")
                    },
                    "study_summary": {
                        "total_time_minutes": st.session_state.get("total_study_seconds", 0) // 60,
                        "completed_sessions": st.session_state.get("completed_sessions", 0),
                        "current_streak_days": st.session_state.get("streak", 0),
                        "daily_goal_minutes": st.session_state.get("daily_goal_seconds", 7200) // 60,
                        "today_study_minutes": st.session_state.get("daily_seconds", 0) // 60,
                        "last_subject": st.session_state.get("last_subject", "—")
                    },
                    "preferences": {
                        "dark_mode": st.session_state.get("dark_mode", True),
                        "language": st.session_state.get("lang", "badini"),
                        "student_name": st.session_state.get("student_name", "")
                    },
                    "study_history": st.session_state.get("study_history", []),
                    "weekly_schedule": {}
                }
                try:
                    export_data["weekly_schedule"] = get_schedule_data()
                except Exception as e:
                    export_data["schedule_error"] = str(e)

                json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=json_serial)

                csv_lines = ["timestamp,subject,minutes"]
                history = st.session_state.get("study_history", [])
                if history:
                    for entry in history:
                        parts = entry.split(" - ")
                        time_part = parts[0] if len(parts) > 0 else ""
                        rest = parts[1] if len(parts) > 1 else ""
                        subject_part = rest.split(" (")[0] if "(" in rest else rest
                        minutes_part = rest.split("(")[1].split(" ")[0] if "(" in rest else "0"
                        csv_lines.append(f"{time_part},{subject_part},{minutes_part}")
                else:
                    csv_lines.append("No history,,")
                csv_data = "\n".join(csv_lines)

                # ── Stacked download buttons ──
                st.download_button(
                    label="📄 JSON",
                    data=json_str,
                    file_name=f"rekxare_export_{st.session_state.get('user_email', 'user').split('@')[0]}.json",
                    mime="application/json",
                    key="export_json_btn",
                    use_container_width=True
                )
                st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="📊 CSV",
                    data=csv_data,
                    file_name=f"study_history_{st.session_state.get('user_email', 'user').split('@')[0]}.csv",
                    mime="text/csv",
                    key="export_csv_btn",
                    use_container_width=True
                )

        st.markdown('</div>', unsafe_allow_html=True)  # end settings card

        # ─── 6. Logout ───
        st.markdown('<div class="sb-card sb-logout">', unsafe_allow_html=True)
        if st.button("🚪 " + t("logout"), key="sb_logout_btn", use_container_width=True):
            for key in ["user_email", "data_key", "logged_in"]:
                st.session_state.pop(key, None)
            st.logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ─── 7. Footer ───
        st.markdown('<div class="sb-footer">Rekxare Dami v1.0</div>', unsafe_allow_html=True)

render_sidebar()


# ══════════════════════════════════════════════════════════
#  CUSTOM NAV BAR
# ══════════════════════════════════════════════════════════
def render_nav(active: str):
    is_dark   = st.session_state.get("dark_mode", True)
    lang      = st.session_state.get("lang", "badini")
    dark_icon = "☀️" if is_dark else "🌙"
    lang_abbr = {"badini": "BA", "english": "EN", "arabic": "AR"}.get(lang, "EN")
    user_name = "Student"
    if st.user.is_logged_in:
        user_name = (st.user.name or st.user.email or "Student")[:20]

    try:
        with open("logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="rd-logo" alt="logo">'
    except FileNotFoundError:
        logo_html = '<span class="rd-logo-emoji">📚</span>'

    if is_dark:
        NAV_BG   = "rgba(13,11,36,0.96)"
        NAV_BDR  = "rgba(255,255,255,0.08)"
        NAV_SH   = "0 4px 32px rgba(0,0,0,0.60),0 1px 0 rgba(255,255,255,0.04)"
        TXT      = "#ececec"
        MUTED    = "rgba(255,255,255,0.42)"
        ACT_BG   = "rgba(76,175,80,0.18)"
        ACT_C    = "#7ec87f"
        HOV_BG   = "rgba(255,255,255,0.07)"
        PILL_BG  = "rgba(255,255,255,0.06)"
        PILL_BDR = "rgba(255,255,255,0.10)"
        HAM_BG   = "rgba(76,175,80,0.14)"
        HAM_BDR  = "rgba(76,175,80,0.40)"
        HAM_C    = "#7ec87f"
        BTN_BG   = "rgba(255,255,255,0.06)"
        BTN_BDR  = "rgba(255,255,255,0.10)"
        BTN_HOV  = "rgba(76,175,80,0.20)"
        SB_BG    = "#0e0c24"
        SB_BDR   = "rgba(255,255,255,0.07)"
    else:
        NAV_BG   = "rgba(255,255,255,0.97)"
        NAV_BDR  = "rgba(0,0,0,0.08)"
        NAV_SH   = "0 4px 24px rgba(0,0,0,0.12),0 1px 0 rgba(0,0,0,0.04)"
        TXT      = "#18182a"
        MUTED    = "rgba(0,0,0,0.44)"
        ACT_BG   = "rgba(46,125,50,0.12)"
        ACT_C    = "#2e7d32"
        HOV_BG   = "rgba(0,0,0,0.05)"
        PILL_BG  = "rgba(0,0,0,0.05)"
        PILL_BDR = "rgba(0,0,0,0.09)"
        HAM_BG   = "rgba(46,125,50,0.11)"
        HAM_BDR  = "rgba(46,125,50,0.32)"
        HAM_C    = "#2e7d32"
        BTN_BG   = "rgba(0,0,0,0.05)"
        BTN_BDR  = "rgba(0,0,0,0.09)"
        BTN_HOV  = "rgba(76,175,80,0.12)"
        SB_BG    = "#f4f6f8"
        SB_BDR   = "rgba(0,0,0,0.07)"

    ha = " nav-active" if active == "home"     else ""
    sa = " nav-active" if active == "schedule" else ""
    aa = " nav-active" if active == "about"    else ""
    nt, ns, na = t("nav_timer"), t("nav_schedule"), t("nav_about")

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── 1. Strip Streamlit header ── */
header[data-testid="stHeader"] {{
    height:0!important;min-height:0!important;
    overflow:visible!important;background:transparent!important;
    box-shadow:none!important;border:none!important;padding:0!important;
}}
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],#MainMenu,footer{{display:none!important;}}

/* ── 2. All native sidebar toggle buttons — moved off-screen.
   MUST NOT be display:none — the iframe JS needs them in the DOM.
   pointer-events:auto keeps them JS-clickable even off-screen. ── */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapse"],
[data-testid="stSidebarCollapseButton"] {{
    position:fixed!important;
    top:-9999px!important;left:-9999px!important;
    width:1px!important;height:1px!important;
    opacity:0!important;pointer-events:auto!important;
    overflow:hidden!important;
}}

/* ── 3. Sidebar panel ── */
section[data-testid="stSidebar"] {{
    background:{SB_BG}!important;
    border-right:1px solid {SB_BDR}!important;
    box-shadow:4px 0 24px rgba(0,0,0,.18)!important;
    transition:transform .28s cubic-bezier(0.4,0,0.2,1)!important;
    z-index:1100000!important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    font-size:14px!important;font-weight:500!important;
    padding:8px 12px!important;border-radius:8px!important;
    display:block!important;text-decoration:none!important;
    transition:background .15s,color .15s!important;margin-bottom:2px!important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {{
    background:{ACT_BG}!important;color:{ACT_C}!important;font-weight:700!important;
}}

/* ── 4. CSS-class sidebar override  (backup for JS approach)
   When JS sets body.rd-sb-open the sidebar shows regardless of
   what Streamlit's own React state says. ── */
body.rd-sb-open section[data-testid="stSidebar"] {{
    transform:translateX(0)!important;
    visibility:visible!important;
    display:flex!important;
    min-width:244px!important;width:244px!important;
}}
/* Default hidden state when body class is absent */
body:not(.rd-sb-open) section[data-testid="stSidebar"] {{
    transform:translateX(-110%)!important;
}}

/* ── 5. Hamburger button ── */
#rd-ham {{
    position:fixed!important;top:8px!important;left:10px!important;
    z-index:2200000!important;
    width:36px!important;height:36px!important;
    background:{HAM_BG}!important;
    border:1.5px solid {HAM_BDR}!important;
    border-radius:10px!important;cursor:pointer!important;
    display:flex!important;align-items:center!important;justify-content:center!important;
    box-shadow:0 2px 12px rgba(0,0,0,.22)!important;
    transition:background .18s,border-color .18s,box-shadow .18s,transform .14s!important;
    outline:none!important;-webkit-tap-highlight-color:transparent!important;
    padding:0!important;margin:0!important;
}}
#rd-ham:hover {{
    background:rgba(76,175,80,.28)!important;
    border-color:rgba(76,175,80,.65)!important;
    box-shadow:0 0 16px rgba(76,175,80,.38)!important;
    transform:scale(1.07)!important;
}}
#rd-ham:active{{transform:scale(0.91)!important;}}
#rd-ham svg{{pointer-events:none;}}

/* ── 6. Nav bar ── */
.rd-nav {{
    position:fixed;top:0;left:0;right:0;height:52px;
    display:flex;align-items:center;justify-content:space-between;
    padding:0 12px 0 56px;
    background:{NAV_BG};border-bottom:1px solid {NAV_BDR};box-shadow:{NAV_SH};
    backdrop-filter:blur(28px) saturate(1.6);-webkit-backdrop-filter:blur(28px) saturate(1.6);
    z-index:1500000;font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
    box-sizing:border-box;animation:rdSlideDown .48s cubic-bezier(0.16,1,0.3,1) both;
}}
@keyframes rdSlideDown {{
    from{{transform:translateY(-100%);opacity:0;}}
    to  {{transform:translateY(0);    opacity:1;}}
}}
.rd-brand {{
    display:flex;align-items:center;gap:7px;flex-shrink:0;
    text-decoration:none!important;cursor:pointer;
    padding:4px 6px;border-radius:8px;transition:background .18s;
}}
.rd-brand:hover{{background:{HOV_BG};}}
.rd-logo,.rd-logo-emoji {{
    width:24px;height:24px;border-radius:6px;font-size:22px;
    filter:drop-shadow(0 0 4px rgba(76,175,80,.35));
    transition:transform .28s cubic-bezier(0.34,1.56,0.64,1),filter .25s;
}}
.rd-brand:hover .rd-logo,.rd-brand:hover .rd-logo-emoji {{
    transform:translateY(-3px) scale(1.12);
    filter:drop-shadow(0 0 10px rgba(76,175,80,.80));
}}
.rd-name {{
    font-size:14px;font-weight:800;letter-spacing:-0.3px;color:{TXT};
    transition:color .22s;
}}
.rd-brand:hover .rd-name{{color:{ACT_C};}}
.rd-dot {{
    width:7px;height:7px;border-radius:50%;flex-shrink:0;
    background:#4caf50;box-shadow:0 0 5px 1px rgba(76,175,80,.55);
    animation:dotBreath 2.4s ease-in-out infinite;
}}
@keyframes dotBreath {{
    0%,100%{{transform:scale(1);   box-shadow:0 0 4px 1px rgba(76,175,80,.50);opacity:.9;}}
    40%     {{transform:scale(1.8); box-shadow:0 0 12px 5px rgba(76,175,80,.80),0 0 20px 7px rgba(76,175,80,.25);opacity:1;}}
    70%     {{transform:scale(0.55);box-shadow:0 0 2px 0px rgba(76,175,80,.25);opacity:.65;}}
}}
.rd-links {{
    display:flex;align-items:center;gap:2px;
    position:absolute;left:50%;transform:translateX(-50%);
}}
.rd-link {{
    font-size:13px;font-weight:500;color:{MUTED}!important;
    padding:6px 12px;border-radius:9px;cursor:pointer;white-space:nowrap;
    text-decoration:none!important;position:relative;
    transition:background .17s,color .17s,box-shadow .17s;
}}
.rd-link::after {{
    content:'';position:absolute;bottom:4px;left:50%;transform:translateX(-50%);
    width:0;height:2px;background:{ACT_C};border-radius:1px;
    transition:width .22s cubic-bezier(0.25,1,0.5,1);
}}
.rd-link:hover{{background:{HOV_BG}!important;color:{TXT}!important;}}
.rd-link:hover::after{{width:50%;}}
.rd-link.nav-active{{
    background:{ACT_BG}!important;color:{ACT_C}!important;font-weight:700!important;
    box-shadow:0 0 14px rgba(76,175,80,.18),inset 0 0 10px rgba(76,175,80,.07);
}}
.rd-link.nav-active::after{{width:58%;}}
.rd-link:nth-child(1){{animation:rdFadeUp .44s .08s cubic-bezier(0.16,1,0.3,1) both;}}
.rd-link:nth-child(2){{animation:rdFadeUp .44s .15s cubic-bezier(0.16,1,0.3,1) both;}}
.rd-link:nth-child(3){{animation:rdFadeUp .44s .22s cubic-bezier(0.16,1,0.3,1) both;}}
@keyframes rdFadeUp {{
    from{{transform:translateY(7px);opacity:0;}}
    to  {{transform:translateY(0);  opacity:1;}}
}}
.rd-right {{
    display:flex;align-items:center;gap:4px;flex-shrink:0;
    animation:rdFadeUp .44s .28s cubic-bezier(0.16,1,0.3,1) both;
}}
.rd-user {{
    font-size:11px;font-weight:600;color:{MUTED}!important;
    background:{PILL_BG};border:1px solid {PILL_BDR};
    padding:3px 9px;border-radius:20px;
    max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.rd-btn {{
    display:inline-flex;align-items:center;justify-content:center;
    font-size:13px;cursor:pointer;background:{BTN_BG};border:1px solid {BTN_BDR};
    color:{MUTED}!important;padding:4px 9px;border-radius:8px;
    transition:background .17s,color .17s,box-shadow .17s,transform .12s,border-color .17s;
    text-decoration:none!important;white-space:nowrap;min-height:28px;line-height:1;font-family:inherit;
}}
.rd-btn:hover {{
    background:{BTN_HOV}!important;color:{ACT_C}!important;
    border-color:rgba(76,175,80,.38)!important;
    box-shadow:0 0 10px rgba(76,175,80,.20)!important;transform:translateY(-1px);
}}
.rd-btn:active{{transform:scale(0.93);}}
.main .block-container,
section[data-testid="stMain"] .block-container{{padding-top:68px!important;}}
@media(max-width:600px){{
    .rd-nav{{padding:0 8px 0 56px!important;height:48px;}}
    .rd-name,.rd-dot,.rd-user{{display:none!important;}}
    .rd-link{{font-size:11px!important;padding:5px 7px!important;}}
    .rd-btn{{font-size:11px!important;padding:3px 7px!important;}}
}}
@media(max-width:380px){{
    .rd-link{{font-size:10px!important;padding:4px 5px!important;}}
    .rd-right{{gap:2px;}}
}}
</style>

<!-- Hamburger — NO inline onclick (Streamlit CSP blocks inline handlers).
     The click is wired via addEventListener inside the iframe component below. -->
<button id="rd-ham" aria-label="Toggle sidebar" title="Open menu">
  <svg width="18" height="18" viewBox="0 0 18 18" fill="{HAM_C}" xmlns="http://www.w3.org/2000/svg">
    <rect y="3"  width="18" height="2" rx="1"/>
    <rect y="8"  width="13" height="2" rx="1"/>
    <rect y="13" width="18" height="2" rx="1"/>
  </svg>
</button>

<div class="rd-nav">
  <a class="rd-brand" href="/" target="_self">
    {logo_html}
    <span class="rd-name">Rekxare Dami</span>
    <span class="rd-dot"></span>
  </a>
  <div class="rd-links">
    <a class="rd-link{ha}" href="/"         target="_self">⏱️ {nt}</a>
    <a class="rd-link{sa}" href="/schedule" target="_self">📅 {ns}</a>
    <a class="rd-link{aa}" href="/about"    target="_self">✨ {na}</a>
  </div>
  <div class="rd-right">
    <span class="rd-user">👤 {user_name}</span>
  </div>
</div>
""", unsafe_allow_html=True)


render_nav(_active)
        

# ══════════════════════════════════════════════════════════
#  SIDEBAR TOGGLE — iframe component (bypasses page CSP)
#
#  WHY THIS WORKS
#  ─────────────────────────────────────────────────────────
#  Streamlit's Content Security Policy blocks ALL inline
#  JavaScript on the main page (onclick=, onload=, and
#  even <script> tags injected via st.markdown).
#
#  st.components.v1.html() runs inside a sandboxed iframe
#  served from the SAME origin as the main Streamlit page.
#  Same-origin iframes can access window.parent.document
#  freely, so we can:
#    • find #rd-ham in the parent DOM
#    • attach a real click listener (addEventListener)
#    • toggle body.rd-sb-open on the parent document
#    • directly set inline styles on the sidebar element
#
#  Two-track toggle:
#   Track A — CSS body class:
#     body.rd-sb-open overrides Streamlit's sidebar CSS
#     with !important, making the sidebar visible even if
#     React's isCollapsed state says closed.
#   Track B — inline style with setProperty(...,'important'):
#     Inline !important beats stylesheet rules, so even if
#     Streamlit applies a CSS class to hide the sidebar,
#     our inline override wins.
#
#  State persistence:
#   localStorage key 'rdSB' (1 = open, 0 = closed) survives
#   Streamlit reruns and dark-mode changes.  A setInterval
#   re-applies the open state after any rerun that rebuilds
#   the sidebar DOM element.
# ══════════════════════════════════════════════════════════
components.html("""
<script>
(function() {
  var LS_KEY = 'rdSB';
  var p = window.parent.document;

  /* ── helpers ── */
  function getSidebar() {
    return p.querySelector('section[data-testid="stSidebar"]');
  }

  function wantOpen() {
    try { return window.parent.localStorage.getItem(LS_KEY) === '1'; } catch(e) { return false; }
  }

  function setWant(v) {
    try { window.parent.localStorage.setItem(LS_KEY, v ? '1' : '0'); } catch(e) {}
  }

  /* ── open sidebar (Track A + B) ── */
  function openSidebar() {
    setWant(true);
    // Track A — CSS body class
    p.body.classList.add('rd-sb-open');
    // Track B — inline !important overrides Streamlit's CSS class
    var sb = getSidebar();
    if (sb) {
      sb.style.setProperty('transform',  'translateX(0)',  'important');
      sb.style.setProperty('visibility', 'visible',        'important');
      sb.style.setProperty('display',    'flex',           'important');
      sb.style.setProperty('min-width',  '244px',          'important');
    }
  }

  /* ── close sidebar ── */
  function closeSidebar() {
    setWant(false);
    // Track A — remove CSS class so Streamlit's own CSS hides it
    p.body.classList.remove('rd-sb-open');
    // Track B — remove our inline overrides so Streamlit's rules apply
    var sb = getSidebar();
    if (sb) {
      sb.style.removeProperty('transform');
      sb.style.removeProperty('visibility');
      sb.style.removeProperty('display');
      sb.style.removeProperty('min-width');
    }
  }

  /* ── is sidebar currently open? ── */
  function isOpen() {
    var sb = getSidebar();
    if (!sb) return false;
    var rect = sb.getBoundingClientRect();
    return rect.left > -50 && rect.width > 50;
  }

  /* ── toggle ── */
  function toggle() {
    if (isOpen()) { closeSidebar(); } else { openSidebar(); }
  }

  /* ── wire hamburger ── */
  function wireHam() {
    var ham = p.getElementById('rd-ham');
    if (!ham) { setTimeout(wireHam, 120); return; }
    if (ham.__rdWired) return;
    ham.__rdWired = true;
    ham.addEventListener('click', toggle);
  }

  /* ── restore state on reruns (sidebar DOM rebuilds) ── */
  setInterval(function() {
    if (!wantOpen()) return;
    if (!isOpen()) {
      // Streamlit rebuilt/collapsed the sidebar after a rerun — reopen it
      p.body.classList.add('rd-sb-open');
      var sb = getSidebar();
      if (sb) {
        sb.style.setProperty('transform',  'translateX(0)', 'important');
        sb.style.setProperty('visibility', 'visible',       'important');
        sb.style.setProperty('display',    'flex',          'important');
        sb.style.setProperty('min-width',  '244px',         'important');
      }
    }
  }, 300);

  /* ── restore on iframe reload (dark-mode / lang change) ── */
  if (wantOpen()) { openSidebar(); }

  /* ── start wiring ── */
  wireHam();
  setTimeout(wireHam, 300);
  setTimeout(wireHam, 800);
})();
</script>
""", height=0)


# ══════════════════════════════════════════════════════════
#  RUN THE CURRENT PAGE
# ══════════════════════════════════════════════════════════
pg.run()
