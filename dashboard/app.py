from streamlit_mic_recorder import mic_recorder
import io
import speech_recognition as sr
from gtts import gTTS
import html
import json
import re
import time
import os
try:
    from google import genai
except ImportError:
    genai = None

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px


from src.data_loader import load_health_data
from src.health_analysis import (
    calculate_health_summary,
    analyze_health_trends,
    generate_health_recommendations
)


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="ASTRA | Mission Control",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- ASTRA NAVIGATION ----------------

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def navigate_to(page):
    st.session_state.current_page = page


# ---------------- HOME SCREEN ----------------

if st.session_state.current_page == "Home":

    st.markdown(
        """
        <div style="text-align:center; padding:35px 10px 25px;">
            <h1 style="color:#5EE4FF; font-size:42px;">
                ASTRA
            </h1>
            <h3 style="color:white;">
                Astronaut Health Monitoring System
            </h3>
            <p style="color:#A9BED3;">
                Intelligent Health Monitoring for Space Missions
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">◈ SELECT YOUR SERVICE</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 🩺 Manual Health Input")
            st.write("Enter health measurements and view health analysis, alerts and recommendations.")

            if st.button("Open Manual Input", use_container_width=True):
                navigate_to("Manual")

        with st.container(border=True):
            st.markdown("### 🎙️ Voice Input")
            st.write("Enter astronaut health information using voice commands.")

            if st.button("Open Voice Interface", use_container_width=True):
                navigate_to("Voice")

    with col2:
        with st.container(border=True):
            st.markdown("### 📡 ASTRA Smart Patch")
            st.write("Monitor simulated wearable sensors and live biometric readings.")

            if st.button("Open Smart Patch", use_container_width=True):
                navigate_to("Patch")

        with st.container(border=True):
            st.markdown("### 📂 Import Health Data")
            st.write("Upload external health measurement files.")

            if st.button("Import Health Data", use_container_width=True):
                navigate_to("Import")

    st.markdown('<div class="section-title">◈ ADVANCED MISSION SYSTEMS</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 🚀 Explore Advanced Mission Systems")
        st.write("Access ASTRA's ten advanced modules for health intelligence, mission analysis, crew monitoring and reporting.")
        if st.button("Open Advanced Mission Systems  →", key="open_advanced_mission_systems", use_container_width=True):
            navigate_to("Advanced Mission Systems")
            st.rerun()

    st.markdown(
        """
        <div style="text-align:center; color:#8299B0;
                    padding:30px 0 10px; font-size:12px;">
            ASTRA | Space Health Monitoring Prototype
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #07111f, #0d1930);
    color: #eaf2ff;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    visibility: visible !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
    color: #5ee4ff !important;
    background: #142640 !important;
    border: 1px solid #345274 !important;
    border-radius: 8px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0b1729;
    border-right: 1px solid #345274;
}

[data-testid="stSidebar"] * {
    color: #eaf2ff !important;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}

/* General text */
h1, h2, h3, h4, p, label {
    color: #eaf2ff;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 4px;
    color: #ffffff;
}

.subtitle {
    color: #a9bdd8;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 1px;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #5ee4ff;
    margin-top: 25px;
    margin-bottom: 15px;
}

/* Navigation bar */
.navbar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    background: #10223a;
    border: 1px solid #345274;
    border-radius: 12px;
    padding: 12px;
    margin: 18px 0;
}

.navbar a {
    color: #d9eaff !important;
    text-decoration: none !important;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 14px;
    border-radius: 8px;
    background: #1a3452;
    transition: 0.2s;
}

.navbar a:hover {
    background: #15516b;
    color: #5ee4ff !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg, #192c48, #101d33);
    border: 1px solid #345274;
    border-radius: 16px;
    padding: 20px;
    min-height: 135px;
    box-shadow: 0 8px 25px rgba(0,0,0,.25);
}

.metric-label {
    color: #c5d7ed;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    color: #ffffff;
    font-size: 32px;
    font-weight: 800;
    margin-top: 12px;
}

.metric-unit {
    color: #5ee4ff;
    font-size: 14px;
    font-weight: 600;
}

/* Status and alerts */
.status-card {
    background: #142640;
    border: 1px solid #345274;
    border-radius: 14px;
    padding: 18px;
}

.alert-card {
    background: #382b1b;
    border: 1px solid #b77925;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
    color: #ffe0a3 !important;
    font-size: 14px;
}

.normal-card {
    background: #12352e;
    border: 1px solid #278c70;
    border-radius: 12px;
    padding: 15px;
    color: #a7f3d0 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] label {
    color: #5ee4ff !important;
    font-weight: 700 !important;
}

/* White selection box */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #345274 !important;
    border-radius: 9px !important;
}

/* Astronaut ID text */
[data-testid="stSelectbox"] div[data-baseweb="select"] div[class*="singleValue"] {
    color: #172B4D !important;
    font-weight: 700 !important;
}

/* Search input */
[data-testid="stSelectbox"] input {
    color: #172B4D !important;
}

/* Dropdown arrow */
[data-testid="stSelectbox"] svg {
    fill: #172B4D !important;
}

/* Dropdown menu */
div[data-baseweb="popover"] {
    background: #ffffff !important;
}

div[data-baseweb="popover"] li {
    color: #172B4D !important;
}

/* Metrics and tables */
div[data-testid="stMetric"] {
    background: #192c48;
    border: 1px solid #345274;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #345274;
    border-radius: 12px;
}

hr {
    border-color: #345274;
}

/* Daily Health Check Submit Button */
div.stFormSubmitButton > button {
    background-color: #5EE4FF !important;
    color: #07111F !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}

div.stFormSubmitButton > button:hover {
    background-color: #38CFFF !important;
    color: #07111F !important;
}




/* Home Page Open Buttons */
div.stButton > button {
    background-color: #5EE4FF !important;
    color: #07111F !important;
    border: 1px solid #5EE4FF !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

/* Button Text */
div.stButton > button p {
    color: #07111F !important;
}

/* Hover Effect */
div.stButton > button:hover {
    background-color: #38CFFF !important;
    color: #07111F !important;
    border-color: #38CFFF !important;
}




.astra-hero{background:radial-gradient(circle at 85% 15%,rgba(40,190,225,.20),transparent 32%),linear-gradient(125deg,#102844,#0b192d 62%,#122b45);border:1px solid rgba(94,228,255,.35);border-radius:22px;padding:24px 28px;margin:12px 0 22px;box-shadow:0 18px 45px rgba(0,0,0,.22)}
.astra-kicker{color:#5ee4ff;font-size:11px;letter-spacing:2.5px;font-weight:800}.astra-heading{color:#f4f9ff;font-size:29px;font-weight:800;margin:7px 0 4px}.astra-sub{color:#a9bdd8;font-size:13px}
.astra-panel{background:linear-gradient(145deg,rgba(24,48,75,.96),rgba(12,28,48,.98));border:1px solid #345274;border-radius:17px;padding:17px 18px;min-height:112px;box-shadow:0 10px 25px rgba(0,0,0,.16)}
.astra-panel-label{color:#a9bdd8;font-size:11px;font-weight:800;letter-spacing:1px}.astra-panel-value{color:#f7fbff;font-size:27px;font-weight:800;margin-top:9px}.astra-panel-unit{color:#5ee4ff;font-size:12px;font-weight:700}.astra-muted{color:#9fb3cb;font-size:11px}

</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

@st.cache_data
def get_data():
    return load_health_data()


df = get_data()

if df.empty:
    st.error("No health data is available.")
    st.stop()

astronauts = df["astronaut_id"].dropna().unique().tolist()

if not astronauts:
    st.error("No astronaut records were found.")
    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## ASTRA")
    st.caption("ASTRONAUT SMART HEALTH COMPANION")

    st.image(
        "https://images-assets.nasa.gov/image/iss061e040708/iss061e040708~orig.jpg",
        use_container_width=True
    )

    st.caption("NASA Astronaut | Spacewalk")

    st.divider()

    st.markdown("### MISSION CONTROL")

    selected_astronaut = st.selectbox(
        "Search / Select Astronaut",
        astronauts
    )

    st.markdown("""
    <div class="status-card">
        <span style="color:#a9bdd8;">MISSION STATUS</span>
        <h3 style="color:#5ee4ff;">● ACTIVE</h3>
        <span style="color:#a9bdd8;font-size:12px;">
            Health monitoring system online
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.caption("ASTRA SYSTEM v1.0")
    st.caption("Space Health Intelligence")


# ---------------- FILTER DATA ----------------

astronaut_df = df[
    df["astronaut_id"] == selected_astronaut
].sort_values("timestamp")

if astronaut_df.empty:
    st.warning("No records found for this astronaut.")
    st.stop()

latest = astronaut_df.iloc[-1]

summary = calculate_health_summary(selected_astronaut)

health_analysis = analyze_health_trends(selected_astronaut)

alerts = health_analysis["Alerts"]
health_status = health_analysis["Status"]

recommendations = generate_health_recommendations(
    selected_astronaut
)


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">ASTRA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">ASTRONAUT SMART HEALTH COMPANION '
    '| MISSION HEALTH MONITORING</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="navbar">
        <a href="#overview">Health Overview</a>
        <a href="#biometrics">Biometric Trends</a>
        <a href="#insights">AI Health Insights</a>
        <a href="#latest-record">Latest Record</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"**Astronaut ID:** `{selected_astronaut}`"
    f"　　**Latest Update:** `{latest['timestamp']}`"
)

st.divider()

if st.session_state.current_page == "Home":
    st.markdown('<div class="astra-hero"><div class="astra-kicker">ASTRA / MISSION ACTIVE</div><div class="astra-heading">Mission Control · Astronaut Health Intelligence</div><div class="astra-sub">Unified biometric overview, explainable screening and crew health visibility</div></div>', unsafe_allow_html=True)
    st.markdown("### ◈ LIVE BIOMETRIC SNAPSHOT")
    vital_specs=[("❤️ HEART RATE","heart_rate","BPM"),("🫁 OXYGEN SATURATION","spo2","%"),("🌡️ BODY TEMPERATURE","temperature","°C"),("🌙 SLEEP DURATION","sleep_hours","hrs")]
    vcols=st.columns(4)
    for vc,(label,field,unit) in zip(vcols,vital_specs):
        value=latest.get(field)
        try: display=f"{float(value):.1f}" if field in ("temperature","sleep_hours") else f"{float(value):.0f}"
        except (TypeError,ValueError): display="—"
        vc.markdown(f'<div class="astra-panel"><div class="astra-panel-label">{label}</div><div class="astra-panel-value">{display}<span class="astra-panel-unit"> {unit}</span></div><div class="astra-muted">Latest available record</div></div>',unsafe_allow_html=True)
    st.caption("Snapshot values come from the latest loaded record for the selected astronaut; they are not a live medical-device feed.")

# ---------------- PAGE ROUTING ----------------



if st.session_state.current_page == "Advanced Mission Systems":
    st.markdown('<div class="astra-hero"><div class="astra-kicker">ASTRA / EXTENDED CAPABILITIES</div><div class="astra-heading">◈ ADVANCED MISSION SYSTEMS</div><div class="astra-sub">Ten integrated modules for astronaut health intelligence and mission research</div></div>', unsafe_allow_html=True)

    if st.button("← Back to Home", key="advanced_systems_back_home"):
        navigate_to("Home")
        st.rerun()

    astra_modules = [
        ("🧑‍🚀", "Digital Health Profile", "Digital Profile", "Personal biometric identity and health timeline."),
        ("🧠", "ASTRA Intelligence Engine", "Intelligence", "Personal baseline and multi-signal screening."),
        ("📈", "Health Trend Prediction", "Trend Prediction", "Illustrative short-range trend projections."),
        ("🛰️", "Mission Simulation Lab", "Mission Simulation", "Explore hypothetical mission scenarios."),
        ("📡", "Real-Time Monitoring", "Real-Time Monitoring", "Live-style view and sensor architecture."),
        ("🚨", "Explainable Health Alerts", "Health Alerts", "Understand each screening flag and rule."),
        ("📄", "Automated Health Reports", "Health Reports", "Generate downloadable astronaut summaries."),
        ("👥", "Crew Health Overview", "Crew Overview", "Review latest readings across the crew."),
        ("⚖️", "Mission Comparison", "Mission Comparison", "Compare indicators across crew members."),
        ("✨", "ASTRA Assistant", "ASTRA Assistant", "Ask questions about the loaded health dataset."),
    ]

    for n in range(0, len(astra_modules), 2):
        module_cols = st.columns(2)
        for col, (emoji, title, page, desc) in zip(module_cols, astra_modules[n:n+2]):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {emoji} {title}")
                    st.caption(desc)
                    if st.button(f"Open {title}", key=f"advanced_module_{page}", use_container_width=True):
                        navigate_to(page)
                        st.rerun()

    st.stop()


if st.session_state.current_page == "Patch":

    st.title("📡 ASTRA SMART PATCH")
    st.caption("Wearable Health Monitoring System")

    if st.button("← Back to Home", key="patch_back_home"):
        navigate_to("Home")
        st.rerun()

    st.divider()

    st.subheader("◈ DEVICE STATUS")

    st.success("Device Connected — Simulation Mode")

    st.caption(
        "All sensors are currently represented by software simulation."
    )

    st.subheader("◈ ACTIVE SENSORS")

    patch_col1, patch_col2 = st.columns(2)

    with patch_col1:
        with st.container(border=True):
            st.markdown("### ❤️ Heart Rate")
            st.markdown("**Status:** Active")
            st.caption("Pulse monitoring sensor")

        with st.container(border=True):
            st.markdown("### 🌡️ Temperature")
            st.markdown("**Status:** Active")
            st.caption("Skin temperature sensor")

    with patch_col2:
        with st.container(border=True):
            st.markdown("### 🫁 SpO2")
            st.markdown("**Status:** Active")
            st.caption("Blood oxygen monitoring sensor")

        with st.container(border=True):
            st.markdown("### 🏃 Motion Sensor")
            st.markdown("**Status:** Active")
            st.caption("Movement and activity monitoring")

    st.divider()

    st.subheader("◈ SYSTEM INFORMATION")

    info1, info2, info3 = st.columns(3)

    info1.metric("Data Source", "SIMULATED")
    info2.metric("Device", "ASTRA Prototype")
    info3.metric("Connection", "Software")

    st.info(
        "No physical wearable device is connected. "
        "Sensor readings are simulated for demonstration."
    )

    st.stop()











elif st.session_state.current_page == "Voice":

    import re
    import io
    import html
    import pandas as pd
    import streamlit as st
    import speech_recognition as sr
    from gtts import gTTS

    # =====================================================
    # ASTRA VOICE ASSISTANT - BILINGUAL VERSION
    # =====================================================

    st.markdown("""
    <style>
    .voice-title {
        color: #5ee4ff;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    .voice-subtitle {
        color: #a9bdd5;
        text-align: center;
        margin-bottom: 25px;
        font-size: 14px;
    }
    .conversation-header {
        background: linear-gradient(135deg,#102a43,#0d1930);
        border: 1px solid #294765;
        border-radius: 16px;
        padding: 18px;
        margin: 15px 0;
    }
    .conversation-header h3 {
        color: #5ee4ff;
        margin: 0;
        font-size: 20px;
    }
    .conversation-header p {
        color: #b8c8df;
        margin: 5px 0 0 0;
        font-size: 13px;
    }
    .astra-message {
        background: linear-gradient(135deg,#102b45,#142b46);
        border: 1px solid #28516d;
        border-left: 4px solid #5ee4ff;
        border-radius: 14px;
        padding: 16px;
        margin: 12px 0;
        color: #f0f6ff;
        line-height: 1.7;
    }
    .commander-message {
        background: linear-gradient(135deg,#172b42,#1b3550);
        border: 1px solid #34516d;
        border-left: 4px solid #91bfff;
        border-radius: 14px;
        padding: 16px;
        margin: 12px 0;
        color: #ffffff;
        line-height: 1.7;
    }
    .message-name {
        font-weight: 800;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .report-header {
        background: linear-gradient(120deg,#102a43,#123c5a,#0d1930);
        border: 1px solid #28516d;
        border-radius: 18px;
        padding: 25px;
        margin: 15px 0 20px 0;
    }
    .report-header h2 {
        color: #5ee4ff;
        margin: 0;
        font-size: 25px;
    }
    .report-header p {
        color: #c3d5e8;
        margin: 8px 0 0 0;
        font-size: 13px;
    }
    .report-section {
        color: #5ee4ff;
        font-size: 19px;
        font-weight: 800;
        margin: 22px 0 12px 0;
    }
    .report-card {
        background: linear-gradient(145deg,#11243c,#0d1930);
        border: 1px solid #294765;
        border-radius: 15px;
        padding: 17px;
        min-height: 115px;
        margin-bottom: 12px;
    }
    .report-card-label {
        color: #a9bdd5;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .report-card-value {
        color: #ffffff;
        font-size: 27px;
        font-weight: 800;
    }
    .report-card-unit {
        color: #8fa8c3;
        font-size: 12px;
        margin-top: 5px;
    }
    .report-info-card {
        background: #10243a;
        border: 1px solid #294765;
        border-radius: 14px;
        padding: 17px;
        margin: 10px 0;
        color: #e8f1ff;
        line-height: 1.8;
    }
    .report-info-title {
        color: #5ee4ff;
        font-weight: 800;
        margin-bottom: 8px;
        font-size: 16px;
    }
    .report-footer {
        background: #10243a;
        border: 1px solid #294765;
        border-radius: 12px;
        padding: 14px;
        color: #9fb3ca;
        font-size: 12px;
        margin-top: 20px;
        line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # PAGE HEADER
    # =====================================================

    st.markdown(
        '<div class="voice-title">ASTRA VOICE ASSISTANT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="voice-subtitle">'
        'Your intelligent mission health companion'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("← Back to Home", key="voice_back_home"):
        st.session_state.current_page = "Home"
        # Allow the greeting to play again when the Voice page is reopened.
        st.session_state.voice_greeting_played = False
        st.session_state.voice_greeting_audio = None
        st.rerun()

    # =====================================================
    # SESSION STATE
    # =====================================================

    defaults = {
        "voice_messages": [],
        "voice_greeting_played": False,
        "voice_greeting_audio": None,
        "voice_reply_audio": None,
        "voice_recorder_version": 0,
        "voice_recording": None,
        "voice_stage": "feeling",
        "health_context": {},
        "daily_check_completed": False,
        "daily_report_data": None,
        "daily_report_audio": None,
        "voice_language": "English",
        "play_daily_report": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # =====================================================
    # LANGUAGE SELECTION
    # =====================================================

    st.markdown("### 🌐 Conversation Language")

    st.selectbox(
        "Choose the language ASTRA will use:",
        ["English", "العربية"],
        key="voice_language"
    )

    is_arabic = st.session_state.voice_language == "العربية"

    speech_language = "ar-EG" if is_arabic else "en-US"
    tts_language = "ar" if is_arabic else "en"

    # =====================================================
    # AUDIO GENERATION
    # =====================================================

    def create_astra_audio(text, language=None):

        try:
            language = language or tts_language

            audio_buffer = io.BytesIO()

            tts = gTTS(
                text=text,
                lang=language,
                slow=False
            )

            tts.write_to_fp(audio_buffer)

            return audio_buffer.getvalue()

        except Exception as error:
            st.warning(
                f"ASTRA audio could not be generated: {error}"
            )
            return None

    # =====================================================
    # GREETING - ALWAYS ENGLISH
    # =====================================================

    if not st.session_state.voice_greeting_played:
        greeting = (
            "Good morning, Commander. "
            "Welcome to ASTRA. "
            "I am your mission health companion. "
            "I am ready to listen and follow your health status. "
            "How are you feeling today?"
        )

        st.session_state.voice_messages.append({
            "role": "ASTRA",
            "text": greeting
        })

        st.session_state.voice_greeting_audio = create_astra_audio(
            greeting, "en"
        )

        st.session_state.voice_greeting_played = True


    # =====================================================
    # LANGUAGE HELPERS
    # =====================================================

    def say(english, arabic):

        return arabic if is_arabic else english

    def normalize_text(text):

        text = text.lower().strip()

        replacements = {
            "أ": "ا",
            "إ": "ا",
            "آ": "ا",
            "ة": "ه",
            "ى": "ي",
            "ؤ": "و",
            "ئ": "ي"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def contains_any(text, words):

        return any(word in text for word in words)

    # =====================================================
    # SLEEP HOURS EXTRACTION
    # =====================================================

    def extract_sleep_hours(text):

        text = normalize_text(text)

        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr|h)",
            r"(\d+(?:\.\d+)?)\s*(?:ساعه|ساعات)",
            r"(?:slept|sleep)\s*(\d+(?:\.\d+)?)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)

            if match:
                return float(match.group(1))

        numbers = {
            "one": 1, "two": 2, "three": 3,
            "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9,
            "ten": 10,
            "واحد": 1, "واحده": 1,
            "اتنين": 2, "اثنين": 2,
            "تلاته": 3, "تلات": 3, "ثلاثه": 3, "ثلاث": 3,
            "اربعه": 4, "اربعة": 4,
            "خمسه": 5, "خمسة": 5,
            "سته": 6, "ستة": 6,
            "سبعه": 7, "سبعة": 7,
            "تمانيه": 8, "ثمانيه": 8,
            "تسعه": 9, "تسعة": 9,
            "عشره": 10, "عشرة": 10
        }

        for word, number in numbers.items():
            if word in text:
                return float(number)

        match = re.search(r"\b(\d+(?:\.\d+)?)\b", text)

        if match:
            return float(match.group(1))

        return None

    # =====================================================
    # NEGATION DETECTION
    # =====================================================

    def is_negated(text, keyword):

        text = normalize_text(text)

        negations = [
            "no ", "not ", "without ",
            "don't have", "do not have",
            "مفيش", "مش عندي", "مافيش",
            "لا يوجد", "بدون", "مش حاسس", "مش حاسه"
        ]

        position = text.find(keyword)

        if position == -1:
            return False

        before = text[max(0, position - 25):position]

        return contains_any(before, negations)

    # =====================================================
    # SYMPTOM DETECTION
    # =====================================================

    def detect_symptoms(text):

        text = normalize_text(text)

        symptom_keywords = {
            "fatigue": [
                "tired", "fatigue", "exhausted", "weak",
                "تعبان", "تعبانه", "مرهق", "مرهقه",
                "ارهاق", "ضعف"
            ],
            "dizziness": [
                "dizzy", "dizziness", "lightheaded",
                "دوخه", "دايخ", "دايخه", "دوار"
            ],
            "headache": [
                "headache", "head hurts", "migraine",
                "صداع", "راسي بتوجعني", "دماغي بتوجعني"
            ],
            "nausea": [
                "nausea", "nauseous", "feel sick",
                "غثيان", "ترجيع", "عايز ارجع", "عاوزه ارجع"
            ],
            "pain": [
                "pain", "ache", "hurts", "hurt",
                "وجع", "الم", "بتوجعني", "بيوجعني"
            ],
            "stress": [
                "stressed", "stress", "anxious", "worried",
                "متوتر", "متوتره", "قلقان", "قلقانه",
                "ضغط نفسي"
            ],
            "low_mood": [
                "sad", "unhappy", "low mood",
                "حزين", "حزينه", "مضايق", "مضايقه",
                "مش مبسوط", "مش مبسوطه"
            ],
            "breathing": [
                "shortness of breath",
                "difficulty breathing",
                "trouble breathing",
                "ضيق تنفس", "مش قادر اتنفس",
                "صعوبه في التنفس", "نهجان شديد"
            ],
            "chest_pain": [
                "chest pain", "chest pressure",
                "الم في الصدر", "وجع في الصدر",
                "ضغط على الصدر", "صدري بيوجعني"
            ]
        }

        detected = []

        for symptom, keywords in symptom_keywords.items():

            for keyword in keywords:

                if keyword in text and not is_negated(text, keyword):
                    detected.append(symptom)
                    break

        return list(set(detected))

    # =====================================================
    # EMERGENCY CHECK
    # =====================================================

    def check_urgent_symptoms(text):

        symptoms = detect_symptoms(text)

        urgent = (
            "chest_pain" in symptoms
            or "breathing" in symptoms
        )

        if urgent:

            return say(
                "Commander, chest pain or breathing difficulty can "
                "require urgent medical attention. Please contact "
                "the mission medical team immediately and follow "
                "your emergency protocol. I cannot diagnose the cause.",
                "يا Commander، ألم الصدر أو صعوبة التنفس ممكن "
                "يحتاجوا تدخل طبي عاجل. تواصل فورًا مع الفريق الطبي "
                "واتبع بروتوكول الطوارئ الخاص بالمهمة. أنا لا أستطيع "
                "تشخيص سبب الأعراض."
            )

        return None

    # =====================================================
    # CONVERSATION ENGINE
    # =====================================================

    def generate_astra_response(reply):

        text = normalize_text(reply)
        stage = st.session_state.voice_stage
        context = st.session_state.health_context

        symptoms = detect_symptoms(reply)

        context["reported_symptoms"] = list(set(
            context.get("reported_symptoms", []) + symptoms
        ))

        # -------------------------------------------------
        # FINISH CONVERSATION AT ANY TIME
        # -------------------------------------------------

        finish_phrases = [
            "that's all", "thats all", "finish",
            "end conversation", "goodbye",
            "done", "stop",
            "كفايه", "كفاية", "خلصنا",
            "انهاء", "انهي", "بس كده",
            "مش عايز اكمل", "مش عايزه اكمل"
        ]

        if contains_any(text, finish_phrases):

            st.session_state.voice_stage = "completed"

            return say(
                "Understood, Commander. I will close this health check "
                "and prepare your report using the information available.",
                "تمام يا Commander. هننهي الفحص هنا، وهجهز التقرير "
                "باستخدام المعلومات والقياسات المتاحة."
            )

        # -------------------------------------------------
        # EMERGENCY PRIORITY
        # -------------------------------------------------

        urgent_response = check_urgent_symptoms(reply)

        if urgent_response:

            context["urgent_symptoms_reported"] = True

            return urgent_response

        # -------------------------------------------------
        # INITIAL FEELING
        # -------------------------------------------------

        if stage == "feeling":

            context["original_message"] = reply

            positive = [
                "fine", "good", "great", "normal",
                "okay", "ok", "well", "better",
                "كويس", "كويسه", "تمام", "الحمد لله",
                "بخير", "زي الفل", "ممتاز"
            ]

            tired = [
                "tired", "exhausted", "fatigue", "weak",
                "تعبان", "تعبانه", "مرهق", "مرهقه",
                "ارهاق", "مجهد", "مجهده"
            ]

            if contains_any(text, positive):

                context["feeling"] = "Generally feeling well"

                st.session_state.voice_stage = "sleep_hours"

                return say(
                    "That is good to hear, Commander. "
                    "Let's check your recovery as well. "
                    "How many hours did you sleep?",
                    "الحمد لله، كويس إنك بخير. خلينا نطمن على راحتك "
                    "كمان. نمت كام ساعة؟"
                )

            if contains_any(text, tired):

                context["feeling"] = "Feeling tired"

                st.session_state.voice_stage = "sleep_hours"

                return say(
                    "I'm sorry you're feeling tired, Commander. "
                    "I want to understand what might be affecting "
                    "your energy. How many hours did you sleep?",
                    "آسفة إنك حاسس بالتعب يا Commander. عايزة أفهم "
                    "إيه ممكن يكون مأثر على طاقتك. نمت كام ساعة؟"
                )

            if contains_any(text, [
                "dizz", "دوخه", "دايخ", "دايخه", "دوار"
            ]):

                context["feeling"] = "Experiencing dizziness"

                st.session_state.voice_stage = "dizziness_duration"

                return say(
                    "I understand. When did the dizziness start? "
                    "Did it begin recently, or has it been happening "
                    "for a while?",
                    "فاهمة. الدوخة بدأت إمتى؟ من وقت قريب ولا بقالها "
                    "فترة؟"
                )

            if contains_any(text, [
                "headache", "migraine", "صداع", "راسي بتوجعني",
                "دماغي بتوجعني"
            ]):

                context["feeling"] = "Experiencing headache"

                st.session_state.voice_stage = "headache_severity"

                return say(
                    "I'm sorry you're dealing with that. "
                    "How severe is your headache: mild, moderate, "
                    "or severe?",
                    "ألف سلامة عليك. الصداع شدته إيه: بسيط، متوسط، "
                    "ولا شديد؟"
                )

            if contains_any(text, [
                "pain", "ache", "hurt", "وجع", "الم",
                "بتوجعني", "بيوجعني"
            ]):

                context["feeling"] = "Experiencing pain"

                st.session_state.voice_stage = "pain_details"

                return say(
                    "I understand. Where exactly do you feel the pain, "
                    "and how severe is it?",
                    "فهمت. الوجع فين بالظبط؟ وشدته عاملة إزاي؟"
                )

            if contains_any(text, [
                "stress", "anxious", "worried", "sad",
                "unhappy", "متوتر", "قلقان", "حزين",
                "مضايق", "مضايقه"
            ]):

                context["feeling"] = "Emotional discomfort"

                st.session_state.voice_stage = "mood_details"

                return say(
                    "I'm here with you, Commander. "
                    "Would you like to tell me what has been making "
                    "you feel this way?",
                    "أنا معاكي يا Commander. تحبي تحكيلي إيه اللي "
                    "مخليكي حاسة كده؟"
                )

            context["feeling"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "I want to understand you better. "
                "Can you tell me a little more about what you're feeling?",
                "عايزة أفهم إحساسك أكتر. ممكن توضحيلي شوية "
                "إيه اللي حاسه بيه؟"
            )

        # -------------------------------------------------
        # SLEEP HOURS
        # -------------------------------------------------

        if stage == "sleep_hours":

            hours = extract_sleep_hours(reply)

            if hours is None:

                return say(
                    "I didn't catch the number. Could you tell me "
                    "approximately how many hours you slept?",
                    "مقدرتش أحدد عدد الساعات. ممكن تقولي نمتي "
                    "تقريبًا كام ساعة؟"
                )

            if hours < 0 or hours > 24:

                return say(
                    "That number doesn't seem valid for a sleep duration. "
                    "Could you check it and tell me again?",
                    "الرقم ده مش منطقي كعدد ساعات نوم. ممكن تتأكدي "
                    "وتقوليهولي تاني؟"
                )

            context["reported_sleep_hours"] = hours

            st.session_state.voice_stage = "sleep_quality"

            if hours < 6:

                return say(
                    f"Only {hours:g} hours? That's a short sleep period. "
                    "Did you sleep continuously, or did you wake up "
                    "several times?",
                    f"{hours:g} ساعات بس؟ دي فترة نوم قصيرة نسبيًا. "
                    "نومك كان متواصل ولا صحيتي كذا مرة؟"
                )

            return say(
                f"I recorded {hours:g} hours of sleep. "
                "Was your sleep continuous, or did you wake up "
                "several times?",
                f"سجلت إنك نمتي {hours:g} ساعات. "
                "نومك كان متواصل ولا صحيتي كذا مرة؟"
            )

        # -------------------------------------------------
        # SLEEP QUALITY
        # -------------------------------------------------

        if stage == "sleep_quality":

            context["sleep_quality"] = reply

            good_sleep = contains_any(text, [
                "well", "good", "continuous", "deep",
                "كويس", "كويسه", "تمام", "متواصل",
                "عميق", "مريح"
            ])

            poor_sleep = contains_any(text, [
                "not well", "bad", "poor", "interrupted",
                "woke up", "مش كويس", "مش كويسه",
                "متقطع", "بصحى", "صحيت كتير",
                "وحش", "مش مريح"
            ])

            if good_sleep and not poor_sleep:

                return_message = say(
                    "That's good. Did you wake up feeling refreshed, "
                    "or are you still feeling tired?",
                    "كويس إن نومك كان مريح. صحيتي حاسة إنك ارتحتي "
                    "ولا لسه حاسة بالتعب؟"
                )

            else:

                return_message = say(
                    "I see. Interrupted or poor-quality sleep can "
                    "affect recovery. How is your energy and "
                    "concentration today?",
                    "فهمت. النوم المتقطع أو غير المريح ممكن يأثر "
                    "على الراحة. طاقتك وتركيزك النهارده عاملين إيه؟"
                )

            st.session_state.voice_stage = "energy"

            return return_message

        # -------------------------------------------------
        # ENERGY FOLLOW-UP
        # -------------------------------------------------

        if stage == "energy":

            context["energy_status"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "Thanks for explaining. Apart from your sleep and "
                "energy, have you noticed any other symptoms, "
                "such as dizziness, headache, nausea, or pain?",
                "شكرًا إنك وضحتيلي. بعيدًا عن النوم والطاقة، "
                "هل لاحظتي أي أعراض تانية زي الدوخة أو الصداع "
                "أو الغثيان أو أي وجع؟"
            )

        # -------------------------------------------------
        # DIZZINESS
        # -------------------------------------------------

        if stage == "dizziness_duration":

            context["dizziness_details"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "Thank you for explaining. Are you experiencing "
                "anything else along with the dizziness?",
                "شكرًا إنك وضحتيلي. هل فيه أي أعراض تانية مع الدوخة؟"
            )

        # -------------------------------------------------
        # HEADACHE
        # -------------------------------------------------

        if stage == "headache_severity":

            context["headache_severity"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "Understood. Have you noticed any other symptoms "
                "along with the headache?",
                "فهمت. هل فيه أعراض تانية مصاحبة للصداع؟"
            )

        # -------------------------------------------------
        # PAIN
        # -------------------------------------------------

        if stage == "pain_details":

            context["pain_details"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "Thank you for explaining. Are you experiencing "
                "any other discomfort or unusual symptoms?",
                "شكرًا إنك وضحتيلي. هل فيه أي تعب أو أعراض تانية؟"
            )

        # -------------------------------------------------
        # MOOD
        # -------------------------------------------------

        if stage == "mood_details":

            context["mood_details"] = reply

            st.session_state.voice_stage = "additional_symptoms"

            return say(
                "I appreciate you sharing that with me. "
                "Have you noticed any physical symptoms as well?",
                "شكرًا إنك شاركتيني إحساسك. هل لاحظتي أي أعراض "
                "جسدية كمان؟"
            )

        # -------------------------------------------------
        # ADDITIONAL SYMPTOMS
        # -------------------------------------------------

        if stage == "additional_symptoms":

            no_symptoms = [
                "no", "nothing", "none", "that's all",
                "thats all", "not really", "no more",
                "لا", "لأ", "لا مفيش", "مفيش",
                "مفيش حاجه", "مفيش حاجة", "ولا حاجه",
                "ولا حاجة", "بس كده", "مش حاسس بحاجه",
                "مش حاسه بحاجه"
            ]

            if contains_any(text, no_symptoms):

                context["additional_symptoms"] = (
                    "No additional symptoms reported"
                )

                st.session_state.voice_stage = "completed"

                return say(
                    "That's good to know, Commander. "
                    "Thank you for completing the check-in. "
                    "I'll now prepare your daily health report.",
                    "تمام يا Commander، شكرًا إنك جاوبتيني. "
                    "كده خلصنا الأسئلة، وهجهزلك تقرير الحالة الصحية اليومي."
                )

            context["additional_symptoms"] = reply

            context["reported_symptoms"] = list(set(
                context.get("reported_symptoms", []) + symptoms
            ))

            st.session_state.voice_stage = "completed"

            return say(
                "Thank you for telling me, Commander. "
                "I've recorded your response and completed the "
                "conversational check-in. I'll prepare your health report.",
                "شكرًا إنك قلتيلي يا Commander. سجلت إجابتك "
                "وخلصنا الفحص الحواري. هجهزلك التقرير الصحي دلوقتي."
            )

        # -------------------------------------------------
        # COMPLETED
        # -------------------------------------------------

        if stage == "completed":

            return say(
                "Your health check is already complete, Commander. "
                "You can review your report or start a new check-in.",
                "إحنا خلصنا الفحص بالفعل يا Commander. "
                "تقدري تراجعي التقرير أو تبدأي فحص جديد."
            )

        return say(
            "I'm listening, Commander. Could you explain that "
            "a little more?",
            "أنا معاكي وبسمعك يا Commander. ممكن توضحيلي أكتر؟"
        )

    # =====================================================
    # OPEN-ENDED ASTRA AI ASSISTANT
    # =====================================================

    def get_astra_api_key():
        """Read the Gemini API key from Streamlit secrets or environment."""
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
        return key or os.getenv("GEMINI_API_KEY", "")

    def is_general_question(message):
        """Identify questions intended for the open-ended project assistant."""
        value = message.strip().lower()
        starters = (
            "what ", "what's", "whats", "why ", "how ", "when ",
            "where ", "who ", "which ", "can you", "could you",
            "would you", "explain ", "describe ", "tell me",
            "هل ", "ما ", "ماذا ", "لماذا ", "ازاي ", "كيف ",
            "إزاي ", "اشرح ", "احكي ", "ايه ", "إيه ",
            "ماهو ", "ما هي ", "هل يمكنك", "ممكن تشرح"
        )
        return ("?" in value or "؟" in value or value.startswith(starters))

    def build_astra_knowledge_context():
        """Build a compact, factual knowledge brief from the running app."""
        latest_values = {}
        try:
            for field in ("heart_rate", "spo2", "temperature", "sleep_hours", "mood_score", "activity_level"):
                if field in astronaut_df.columns:
                    value = pd.to_numeric(astronaut_df[field], errors="coerce").dropna()
                    if not value.empty:
                        latest_values[field] = float(value.iloc[-1])
        except Exception:
            latest_values = {}

        return {
            "project": "ASTRA - Astronaut Smart Health Monitoring System",
            "purpose": "A prototype for organizing astronaut health measurements, displaying vital-sign trends, screening for changes using transparent rules, and supporting mission-health review.",
            "implemented_capabilities": [
                "Manual health input and health analysis",
                "Voice-based bilingual check-in in Arabic and English",
                "CSV and Excel health-data import and analysis",
                "ASTRA Smart Patch page currently uses simulated sensor readings; no physical wearable is connected by default",
                "Mission Control crew overview and biometric snapshot",
                "Prototype baseline screening and explainable alerts",
                "Health trend, mission simulation, report, crew overview and comparison modules, with some outputs explicitly illustrative or dependent on loaded data"
            ],
            "selected_astronaut": str(selected_astronaut),
            "latest_available_measurements": latest_values,
            "important_limitations": [
                "ASTRA is a student/research prototype, not a certified medical device and not a diagnostic system.",
                "The Smart Patch currently simulates sensor status; it must not be described as physically connected hardware.",
                "The current screening rules are prototype thresholds and require validation on appropriate datasets.",
                "Trend projections and mission simulations are illustrative unless separately validated.",
                "The assistant must not invent experimental results, sensor integrations, clinical accuracy, or features not listed here."
            ]
        }

    def generate_open_ai_answer(question):
        """Answer arbitrary judge questions using Gemini and ASTRA-specific context."""
        api_key = get_astra_api_key()
        if not api_key:
            return say(
                "The open-ended AI connection is not configured yet. Please add your Gemini API key as GEMINI_API_KEY in Streamlit secrets or as an environment variable, then restart ASTRA.",
                "اتصال الذكاء الاصطناعي المفتوح لسه مش متفعّل. أضف مفتاح Gemini باسم GEMINI_API_KEY في إعدادات Streamlit Secrets أو كمتغير بيئة، وبعدها أعد تشغيل ASTRA."
            )

        if genai is None:
            return say(
                "The Google GenAI package is missing. Install it with: pip install google-genai",
                "مكتبة Google GenAI غير مثبتة. ثبّتها بالأمر: pip install google-genai"
            )

        history = st.session_state.get("voice_messages", [])[-12:]
        history_text = "\n".join(
            f"{item.get('role', 'User')}: {item.get('text', '')}"
            for item in history
        )
        knowledge = build_astra_knowledge_context()
        language_instruction = (
            "Answer in clear Egyptian Arabic. Keep scientific terms in English when useful."
            if is_arabic else
            "Answer in clear, professional English suitable for a scientific competition judge."
        )
        prompt = f"""You are ASTRA's open-ended scientific project assistant, answering questions from competition judges.
{language_instruction}
Use the ASTRA facts below as the primary source of truth. You may explain general scientific concepts, but clearly distinguish general knowledge from features actually implemented in this prototype.
Be direct, accurate, confident but not exaggerated. Give a structured answer of roughly 2-5 short paragraphs unless the question needs more detail. Explain technical terms simply when helpful.
Never claim ASTRA is clinically validated, medically certified, connected to real sensors, or powered by a feature unless the facts explicitly say so. If you do not know a project-specific detail, say it is not currently specified rather than inventing it. For medical questions, provide general educational information only and direct urgent concerns to qualified medical professionals; do not diagnose.

ASTRA KNOWLEDGE:
{json.dumps(knowledge, ensure_ascii=False, default=str)}

RECENT CONVERSATION:
{history_text}

QUESTION:
{question}
"""
        try:
            client = genai.Client(api_key=api_key)
            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            answer = getattr(result, "text", None)
            if not answer or not answer.strip():
                return say(
                    "I couldn't generate a complete answer just now. Please repeat the question.",
                    "مقدرتش أجهز إجابة كاملة دلوقتي. ممكن تعيد السؤال؟"
                )
            return answer.strip()
        except Exception as error:
            return say(
                f"The AI service could not complete the request: {error}",
                f"خدمة الذكاء الاصطناعي مقدرتش تكمل الطلب: {error}"
            )

    # =====================================================
    # PROCESS USER RESPONSE
    # =====================================================

    def process_astronaut_reply(reply):

        if not reply or not reply.strip():
            return

        reply = reply.strip()

        st.session_state.voice_messages.append({
            "role": "Commander",
            "text": reply
        })

        # Open-ended questions (including judge questions) go to the AI model.
        # Ordinary health-check answers continue through the existing guided flow.
        if is_general_question(reply):
            response = generate_open_ai_answer(reply)
        else:
            response = generate_astra_response(reply)

        st.session_state.voice_messages.append({
            "role": "ASTRA",
            "text": response
        })

        # Generate speech in the selected language
        st.session_state.voice_reply_audio = create_astra_audio(
            response,
            tts_language
        )

    # =====================================================
    # DAILY HEALTH REPORT
    # =====================================================

    def build_daily_health_report():

        try:
            df = load_health_data().copy()
        except Exception as error:
            return {"error": f"Could not load health data: {error}"}

        astronaut_id = st.session_state.get(
            "selected_astronaut",
            None
        )

        if (
            astronaut_id is not None
            and "astronaut_id" in df.columns
        ):
            df = df[
                df["astronaut_id"].astype(str)
                == str(astronaut_id)
            ]

        if df.empty:
            return {
                "error": "No recorded health measurements are available."
            }

        if "timestamp" not in df.columns:
            return {
                "error": "The health dataset does not contain a timestamp column."
            }

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="mixed",
            errors="coerce"
        )

        df = df.dropna(subset=["timestamp"])

        if df.empty:
            return {
                "error": "No valid timestamps were found in the data."
            }

        latest_time = df["timestamp"].max()
        start_time = latest_time - pd.Timedelta(hours=24)

        recent_df = df[
            df["timestamp"] >= start_time
        ].copy()

        if recent_df.empty:
            recent_df = df.tail(1)

        metric_config = {
            "heart_rate": {
                "label": "Heart Rate",
                "unit": "BPM",
                "threshold": 100
            },
            "spo2": {
                "label": "SpO2",
                "unit": "%",
                "threshold": 95
            },
            "temperature": {
                "label": "Temperature",
                "unit": "°C",
                "threshold": 38
            },
            "sleep_hours": {
                "label": "Sleep",
                "unit": "Hours",
                "threshold": None
            },
            "mood_score": {
                "label": "Mood Score",
                "unit": "Points",
                "threshold": None
            },
            "activity_level": {
                "label": "Activity",
                "unit": "Level",
                "threshold": None
            }
        }

        averages = {}
        ranges = {}
        alerts = []

        for column, config in metric_config.items():

            if column not in recent_df.columns:
                continue

            values = pd.to_numeric(
                recent_df[column],
                errors="coerce"
            ).dropna()

            if values.empty:
                continue

            averages[column] = float(values.mean())

            ranges[column] = {
                "min": float(values.min()),
                "max": float(values.max())
            }

            threshold = config["threshold"]
            value = averages[column]

            if threshold is not None:

                if column == "heart_rate" and value > threshold:
                    alerts.append(
                        "Average heart rate is above the prototype threshold."
                    )

                elif column == "spo2" and value < threshold:
                    alerts.append(
                        "Average SpO2 is below the prototype threshold."
                    )

                elif column == "temperature" and value >= threshold:
                    alerts.append(
                        "Average temperature is elevated according to the prototype threshold."
                    )

        context = st.session_state.health_context
        symptoms = context.get("reported_symptoms", [])

        recommendations = []

        if "fatigue" in symptoms:
            recommendations.append(
                "Review sleep duration and allow an appropriate rest period."
            )

        if "dizziness" in symptoms:
            recommendations.append(
                "Report dizziness to the mission medical team, especially if persistent or worsening."
            )

        if "headache" in symptoms:
            recommendations.append(
                "Monitor headache severity and report persistent symptoms."
            )

        if "nausea" in symptoms:
            recommendations.append(
                "Monitor nausea and report worsening or persistent symptoms."
            )

        if "stress" in symptoms or "low_mood" in symptoms:
            recommendations.append(
                "Consider a wellbeing check-in with the mission support team."
            )

        if "chest_pain" in symptoms or "breathing" in symptoms:
            recommendations.append(
                "Follow the mission emergency medical protocol immediately and contact the medical team."
            )

        if alerts:
            recommendations.append(
                "Review flagged measurements with the mission medical team."
            )

        if not recommendations:
            recommendations.append(
                "Continue routine monitoring and maintain regular sleep, hydration, and activity routines according to mission guidance."
            )

        return {
            "averages": averages,
            "ranges": ranges,
            "alerts": alerts,
            "recommendations": recommendations,
            "record_count": len(recent_df),
            "start_time": recent_df["timestamp"].min(),
            "end_time": recent_df["timestamp"].max(),
            "symptoms": symptoms,
            "feeling": context.get("feeling", "Not specified"),
            "reported_sleep": context.get("reported_sleep_hours"),
            "sleep_quality": context.get("sleep_quality"),
            "additional_symptoms": context.get(
                "additional_symptoms",
                "Not specified"
            )
        }

    # =====================================================
    # GREETING AUDIO
    # =====================================================

    if st.session_state.voice_greeting_audio:

        st.audio(
            st.session_state.voice_greeting_audio,
            format="audio/mp3",
            autoplay=True
        )

        # Clear after rendering to avoid replay on every rerun
        st.session_state.voice_greeting_audio = None

    # =====================================================
    # CONVERSATION DISPLAY
    # =====================================================

    st.markdown("""
    <div class="conversation-header">
        <h3>💬 CONVERSATION</h3>
        <p>Your private mission health conversation with ASTRA</p>
    </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.voice_messages:

        safe_text = html.escape(message["text"])

        if message["role"] == "ASTRA":

            st.markdown(
                f"""
                <div class="astra-message">
                    <div class="message-name" style="color:#5ee4ff;">
                        🤖 ASTRA
                    </div>
                    {safe_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="commander-message">
                    <div class="message-name" style="color:#a6c8ff;">
                        👨‍🚀 COMMANDER
                    </div>
                    {safe_text}
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # AUTOMATIC ASTRA REPLY AUDIO
    # =====================================================

    if st.session_state.voice_reply_audio:

        st.markdown("### 🔊 ASTRA Voice Response")

        st.audio(
            st.session_state.voice_reply_audio,
            format="audio/mp3",
            autoplay=True
        )

        # Clear only after the audio component is rendered
        st.session_state.voice_reply_audio = None

    # =====================================================
    # MICROPHONE INPUT
    # =====================================================

    st.markdown("### 🎙️ Voice Response")

    audio_data = mic_recorder(
        start_prompt="🎙️ Start Listening",
        stop_prompt="⏹️ Stop Listening",
        key=f"astronaut_recorder_{st.session_state.voice_recorder_version}",
        use_container_width=True,
        format="wav"
    )

    if audio_data and audio_data.get("bytes"):
        st.session_state.voice_recording = audio_data["bytes"]

    if st.session_state.voice_recording:

        st.audio(
            st.session_state.voice_recording,
            format="audio/wav"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🗑️ Delete Recording",
                key="delete_voice_recording",
                use_container_width=True
            ):

                st.session_state.voice_recording = None
                st.session_state.voice_recorder_version += 1
                st.rerun()

        with col2:

            if st.button(
                "📤 Send Voice Response",
                key="send_voice_recording",
                use_container_width=True
            ):

                try:

                    recognizer = sr.Recognizer()

                    with sr.AudioFile(
                        io.BytesIO(st.session_state.voice_recording)
                    ) as source:

                        audio = recognizer.record(source)

                    recognized_text = recognizer.recognize_google(
                        audio,
                        language=speech_language
                    )

                    process_astronaut_reply(recognized_text)

                    st.session_state.voice_recording = None
                    st.session_state.voice_recorder_version += 1

                    st.rerun()

                except sr.UnknownValueError:

                    st.error(
                        "ASTRA could not understand the recording. "
                        "Please try again or type your response."
                    )

                except sr.RequestError as error:

                    st.error(
                        f"Speech recognition service error: {error}"
                    )

                except Exception as error:

                    st.error(
                        f"Voice recognition error: {error}"
                    )

    # =====================================================
    # TEXT INPUT
    # =====================================================

    st.markdown("### 💬 Type Your Response")

    placeholder = (
        "اكتبي ردك هنا..."
        if is_arabic
        else "Example: I slept for three hours..."
    )

    with st.form(
        "voice_text_response_form",
        clear_on_submit=True
    ):

        text_reply = st.text_input(
            "Your response",
            placeholder=placeholder
        )

        submit_text = st.form_submit_button(
            "Send Message",
            use_container_width=True
        )

        if submit_text and text_reply.strip():

            process_astronaut_reply(text_reply.strip())

            st.rerun()

    # =====================================================
    # DAILY HEALTH REPORT
    # =====================================================

    if st.session_state.voice_stage == "completed":

        st.markdown("---")

        st.markdown("""
        <div class="report-header">
            <h2>📊 ASTRA DAILY HEALTH REPORT</h2>
            <p>Mission health overview | Measurements and reported symptoms</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.daily_check_completed:

            st.info(
                "Your conversation is complete. Generate your report "
                "to review the available mission health measurements."
            )

            if st.button(
                "📊 Generate Daily Health Report",
                key="generate_daily_health_report",
                use_container_width=True
            ):

                st.session_state.daily_report_data = (
                    build_daily_health_report()
                )

                st.session_state.daily_check_completed = True
                st.rerun()

        if st.session_state.daily_check_completed:

            report = st.session_state.daily_report_data

            if report and report.get("error"):

                st.error(report["error"])

            elif report:

                # -----------------------------------------
                # REPORT INFORMATION
                # -----------------------------------------

                start_time = report["start_time"]
                end_time = report["end_time"]

                st.markdown(
                    f"""
                    <div class="report-info-card">
                        <div class="report-info-title">
                            🛰️ REPORT INFORMATION
                        </div>
                        <b>Records analyzed:</b> {report["record_count"]}<br>
                        <b>From:</b> {start_time.strftime("%Y-%m-%d %H:%M")}<br>
                        <b>To:</b> {end_time.strftime("%Y-%m-%d %H:%M")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # -----------------------------------------
                # BIOMETRIC OVERVIEW
                # -----------------------------------------

                st.markdown(
                    '<div class="report-section">'
                    '💓 BIOMETRIC OVERVIEW'
                    '</div>',
                    unsafe_allow_html=True
                )

                metric_config = {
                    "heart_rate": ("❤️", "Heart Rate", "BPM"),
                    "spo2": ("🫁", "Oxygen Saturation", "%"),
                    "temperature": ("🌡️", "Temperature", "°C"),
                    "sleep_hours": ("🌙", "Sleep Duration", "Hours"),
                    "mood_score": ("🧠", "Mood Score", "Points"),
                    "activity_level": ("🏃", "Activity Level", "Level")
                }

                available_metrics = [
                    key for key in metric_config
                    if key in report["averages"]
                ]

                for i in range(0, len(available_metrics), 3):

                    cols = st.columns(3)

                    for j, column in enumerate(
                        available_metrics[i:i + 3]
                    ):

                        icon, label, unit = metric_config[column]
                        average = report["averages"][column]

                        with cols[j]:

                            st.markdown(
                                f"""
                                <div class="report-card">
                                    <div class="report-card-label">
                                        {icon} {label}
                                    </div>
                                    <div class="report-card-value">
                                        {average:.1f}
                                    </div>
                                    <div class="report-card-unit">
                                        {unit} · Average
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                if not available_metrics:
                    st.warning(
                        "No numeric health measurements were found."
                    )

                # -----------------------------------------
                # MEASUREMENT RANGES
                # -----------------------------------------

                st.markdown(
                    '<div class="report-section">'
                    '📈 MEASUREMENT RANGES'
                    '</div>',
                    unsafe_allow_html=True
                )

                range_labels = {
                    "heart_rate": "Heart Rate",
                    "spo2": "SpO2",
                    "temperature": "Temperature",
                    "sleep_hours": "Sleep",
                    "mood_score": "Mood Score",
                    "activity_level": "Activity"
                }

                range_rows = []

                for column, values in report["ranges"].items():

                    range_rows.append({
                        "Measurement": range_labels.get(
                            column, column
                        ),
                        "Minimum": round(values["min"], 2),
                        "Average": round(
                            report["averages"][column], 2
                        ),
                        "Maximum": round(values["max"], 2)
                    })

                if range_rows:

                    st.dataframe(
                        pd.DataFrame(range_rows),
                        use_container_width=True,
                        hide_index=True
                    )

                # -----------------------------------------
                # ALERTS
                # -----------------------------------------

                st.markdown(
                    '<div class="report-section">'
                    '⚠️ HEALTH ALERTS'
                    '</div>',
                    unsafe_allow_html=True
                )

                if report["alerts"]:

                    for alert in report["alerts"]:
                        st.warning(alert)

                else:

                    st.success(
                        "No measurement threshold alerts were detected "
                        "using the current prototype rules."
                    )

                # -----------------------------------------
                # REPORTED SYMPTOMS
                # -----------------------------------------

                st.markdown(
                    '<div class="report-section">'
                    '🗣️ REPORTED SYMPTOMS'
                    '</div>',
                    unsafe_allow_html=True
                )

                symptoms = report["symptoms"]

                symptom_text = (
                    ", ".join(
                        html.escape(
                            symptom.replace("_", " ").title()
                        )
                        for symptom in symptoms
                    )
                    if symptoms
                    else "No symptoms identified from the conversation."
                )

                st.markdown(
                    f"""
                    <div class="report-info-card">
                        <div class="report-info-title">
                            Commander Health Feedback
                        </div>
                        <b>General feeling:</b>
                        {html.escape(str(report["feeling"]))}<br>
                        <b>Reported symptoms:</b>
                        {symptom_text}<br>
                        <b>Sleep hours reported in conversation:</b>
                        {report["reported_sleep"]
                         if report["reported_sleep"] is not None
                         else "Not provided"}<br>
                        <b>Sleep quality:</b>
                        {html.escape(str(report["sleep_quality"] or "Not provided"))}<br>
                        <b>Additional symptoms response:</b>
                        {html.escape(str(report["additional_symptoms"]))}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # -----------------------------------------
                # RECOMMENDATIONS
                # -----------------------------------------

                st.markdown(
                    '<div class="report-section">'
                    '💡 ASTRA RECOMMENDATIONS'
                    '</div>',
                    unsafe_allow_html=True
                )

                for index, recommendation in enumerate(
                    report["recommendations"], start=1
                ):

                    st.markdown(
                        f"""
                        <div class="report-info-card">
                            <span style="color:#5ee4ff;font-weight:800;">
                                {index}.
                            </span>
                            {html.escape(recommendation)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # -----------------------------------------
                # REPORT BASIS
                # -----------------------------------------

                st.markdown("""
                <div class="report-footer">
                    <b>How were these statistics calculated?</b><br>
                    Averages, minimums and maximums are calculated
                    from numeric records in the selected astronaut's
                    CSV data within the latest available 24-hour
                    data window. The window is based on the latest
                    timestamp in the file, not necessarily the
                    current calendar day.<br><br>

                    Alert thresholds are experimental prototype
                    rules and are not medical diagnostic limits.
                    Reported symptoms are collected separately from
                    recorded measurements. These averages are not
                    automatically a personal baseline.
                </div>
                """, unsafe_allow_html=True)

                # -----------------------------------------
                # REPORT AUDIO
                # -----------------------------------------

                st.markdown("---")
                st.markdown("### 🔊 Listen to Your Daily Report")

                report_audio_text = (
                    "ASTRA daily mission health report. "
                    f"Number of records analyzed: {report['record_count']}. "
                )

                metric_names = {
                    "heart_rate": "Average heart rate",
                    "spo2": "Average oxygen saturation",
                    "temperature": "Average temperature",
                    "sleep_hours": "Average sleep duration",
                    "mood_score": "Average mood score",
                    "activity_level": "Average activity level"
                }

                for column, value in report["averages"].items():

                    report_audio_text += (
                        f"{metric_names.get(column, column)}: {value:.1f}. "
                    )

                if report["alerts"]:

                    report_audio_text += (
                        "Health alerts. "
                        + " ".join(report["alerts"])
                        + " "
                    )

                else:

                    report_audio_text += (
                        "No measurement threshold alerts were detected. "
                    )

                if symptoms:

                    report_audio_text += (
                        "Reported symptoms include "
                        + ", ".join(symptoms)
                        + ". "
                    )

                report_audio_text += (
                    "Recommendations. "
                    + " ".join(report["recommendations"])
                )

                if st.button(
                    "🔊 ASTRA Read Daily Report",
                    key="listen_daily_report",
                    use_container_width=True
                ):

                    st.session_state.daily_report_audio = (
                        create_astra_audio(report_audio_text, "en")
                    )

                    st.session_state.play_daily_report = True

                if st.session_state.daily_report_audio:

                    st.audio(
                        st.session_state.daily_report_audio,
                        format="audio/mp3",
                        autoplay=st.session_state.play_daily_report
                    )

                    st.session_state.play_daily_report = False

            # ---------------------------------------------
            # RESTART CHECK
            # ---------------------------------------------

            if st.button(
                "🔄 Start New Health Check",
                key="restart_daily_health_check",
                use_container_width=True
            ):

                st.session_state.voice_messages = []
                st.session_state.voice_greeting_played = False
                st.session_state.voice_greeting_audio = None
                st.session_state.voice_reply_audio = None

                st.session_state.voice_recording = None
                st.session_state.voice_recorder_version += 1

                st.session_state.voice_stage = "feeling"
                st.session_state.health_context = {}

                st.session_state.daily_check_completed = False
                st.session_state.daily_report_data = None
                st.session_state.daily_report_audio = None
                st.session_state.play_daily_report = False

                st.rerun()

    # =====================================================
    # FOOTER
    # =====================================================


    st.stop()
  

elif st.session_state.current_page == "Import":

    st.markdown(
        '<div class="astra-hero"><div class="astra-kicker">ASTRA / DATA INGESTION</div>'
        '<div class="astra-heading">Health Data Import Center</div>'
        '<div class="astra-sub">Upload · Validate · Analyze · Review · Integrate into mission records</div></div>',
        unsafe_allow_html=True
    )

    if st.button("← Back to Home", key="import_back_home"):
        navigate_to("Home")
        st.rerun()

    st.markdown("### Upload astronaut health records")
    st.write(
        "Upload a CSV or Excel file. ASTRA will validate the measurements, "
        "summarize the astronaut's health data, highlight prototype alerts, "
        "and provide monitoring recommendations before you save the records."
    )

    import_columns = [
        "astronaut_id", "timestamp", "heart_rate", "spo2",
        "temperature", "sleep_hours", "mood_score", "activity_level"
    ]
    template_example = pd.DataFrame([{
        "astronaut_id": "AST-001",
        "timestamp": "2026-11-13 08:00:00",
        "heart_rate": 72,
        "spo2": 98,
        "temperature": 36.7,
        "sleep_hours": 7.5,
        "mood_score": 4,
        "activity_level": 6
    }], columns=import_columns)
    st.download_button(
        "⬇️ Download CSV Template",
        data=template_example.to_csv(index=False).encode("utf-8-sig"),
        file_name="astra_health_data_template.csv",
        mime="text/csv",
        use_container_width=True
    )

    uploaded_health_file = st.file_uploader(
        "Choose astronaut health data (CSV, XLSX, XLS)",
        type=["csv", "xlsx", "xls"],
        key="health_data_uploader",
        help="One row should represent one measurement record."
    )

    if uploaded_health_file is not None:
        try:
            file_extension = Path(uploaded_health_file.name).suffix.lower()
            if file_extension == ".csv":
                try:
                    imported_df = pd.read_csv(uploaded_health_file, encoding="utf-8-sig")
                except UnicodeDecodeError:
                    uploaded_health_file.seek(0)
                    imported_df = pd.read_csv(uploaded_health_file, encoding="latin-1")
            else:
                imported_df = pd.read_excel(uploaded_health_file)

            imported_df.columns = [
                str(column).strip().lower().replace(" ", "_").replace("-", "_")
                for column in imported_df.columns
            ]
            aliases = {
                "astronaut": "astronaut_id", "astronaut_name": "astronaut_id",
                "id": "astronaut_id", "date": "timestamp", "datetime": "timestamp",
                "recorded_at": "timestamp", "heart_rate_bpm": "heart_rate",
                "pulse": "heart_rate", "oxygen_saturation": "spo2",
                "spo2_percent": "spo2", "temperature_c": "temperature",
                "body_temperature": "temperature", "temp": "temperature",
                "sleep": "sleep_hours", "sleep_duration": "sleep_hours",
                "mood": "mood_score", "activity": "activity_level"
            }
            imported_df = imported_df.rename(columns=aliases)

            missing_columns = [c for c in import_columns if c not in imported_df.columns]
            if missing_columns:
                st.error("Missing required columns: " + ", ".join(missing_columns))
                st.info("Use the downloadable template and keep its column names.")
            elif imported_df.empty:
                st.error("The uploaded file contains no records.")
            else:
                imported_df = imported_df[import_columns].copy()
                imported_df["astronaut_id"] = imported_df["astronaut_id"].astype("string").str.strip()
                imported_df["timestamp"] = pd.to_datetime(imported_df["timestamp"], errors="coerce", format="mixed")
                numeric_columns = ["heart_rate", "spo2", "temperature", "sleep_hours", "mood_score", "activity_level"]
                for column in numeric_columns:
                    imported_df[column] = pd.to_numeric(imported_df[column], errors="coerce")

                issues = []
                for idx, row in imported_df.iterrows():
                    row_no = idx + 2
                    if pd.isna(row["astronaut_id"]) or not str(row["astronaut_id"]).strip():
                        issues.append(f"Row {row_no}: astronaut ID is empty")
                    if pd.isna(row["timestamp"]):
                        issues.append(f"Row {row_no}: timestamp is missing or invalid")
                    for col in numeric_columns:
                        if pd.isna(row[col]):
                            issues.append(f"Row {row_no}: {col} is missing or not numeric")

                limits = {
                    "heart_rate": (30, 220), "spo2": (50, 100),
                    "temperature": (30, 45), "sleep_hours": (0, 24),
                    "mood_score": (1, 5), "activity_level": (1, 10)
                }
                for col, (low, high) in limits.items():
                    bad = imported_df[col].notna() & ~imported_df[col].between(low, high)
                    for idx in imported_df.index[bad]:
                        issues.append(f"Row {idx + 2}: {col} must be between {low} and {high}")

                st.markdown("### File overview")
                a, b, c = st.columns(3)
                a.metric("Records detected", f"{len(imported_df):,}")
                b.metric("Astronauts", f"{imported_df['astronaut_id'].nunique(dropna=True):,}")
                c.metric("Data issues", f"{len(issues):,}")
                st.dataframe(imported_df, use_container_width=True, hide_index=True)

                if issues:
                    st.error(f"Please correct {len(issues)} issue(s) before importing. Analysis below uses valid rows only.")
                    with st.expander("View data validation details"):
                        for issue in issues[:40]:
                            st.write("• " + issue)
                        if len(issues) > 40:
                            st.caption(f"And {len(issues) - 40} additional issue(s).")

                # Analyze rows with complete, valid measurements. Never silently save invalid rows.
                valid_mask = imported_df["astronaut_id"].notna() & imported_df["timestamp"].notna()
                for col in numeric_columns:
                    valid_mask &= imported_df[col].notna() & imported_df[col].between(*limits[col])
                valid_df = imported_df.loc[valid_mask].copy()

                duplicate_records = int(imported_df.duplicated(subset=["astronaut_id", "timestamp"]).sum())
                quality_score = int(round((len(valid_df) / max(len(imported_df), 1)) * 100))
                st.markdown("### ◈ Import quality & integrity")
                quality_cols = st.columns(4)
                quality_cols[0].metric("Rows received", f"{len(imported_df):,}")
                quality_cols[1].metric("Valid rows", f"{len(valid_df):,}")
                quality_cols[2].metric("Duplicate timestamps", f"{duplicate_records:,}")
                quality_cols[3].metric("Validation score", f"{quality_score}%")
                st.progress(quality_score / 100)
                st.caption(f"{quality_score}% of uploaded rows passed the current validation checks.")
                if duplicate_records:
                    st.warning("Duplicate astronaut/timestamp pairs were detected. Review these records before saving to avoid repeated measurements.")
                st.caption("The validation score is a file-integrity indicator only; it is not a measure of astronaut health.")

                if not valid_df.empty:
                    st.markdown("---")
                    st.markdown(
                        '<div class="astra-hero"><div class="astra-kicker">ASTRA / BIOMETRIC ANALYSIS</div>'
                        '<div class="astra-heading">Uploaded Health Intelligence</div>'
                        '<div class="astra-sub">Review the selected astronaut, vital-sign patterns and explainable screening notes before importing.</div></div>',
                        unsafe_allow_html=True
                    )
                    astronaut_options = sorted(valid_df["astronaut_id"].astype(str).unique().tolist())
                    selected_upload_astronaut = st.selectbox(
                        "Select astronaut to analyze", astronaut_options,
                        key="import_analysis_astronaut"
                    )
                    analysis_df = valid_df[
                        valid_df["astronaut_id"].astype(str) == selected_upload_astronaut
                    ].sort_values("timestamp").copy()

                    first_time = analysis_df["timestamp"].min()
                    last_time = analysis_df["timestamp"].max()
                    st.caption(
                        f"Analysis period: {first_time:%Y-%m-%d %H:%M} to {last_time:%Y-%m-%d %H:%M} "
                        f"| {len(analysis_df)} valid record(s)"
                    )

                    metric_info = {
                        "heart_rate": ("Heart rate", "BPM"),
                        "spo2": ("Blood oxygen (SpO₂)", "%"),
                        "temperature": ("Body temperature", "°C"),
                        "sleep_hours": ("Sleep duration", "hours"),
                        "mood_score": ("Mood score", "/ 5"),
                        "activity_level": ("Activity level", "/ 10")
                    }
                    averages = analysis_df[numeric_columns].mean()
                    latest_record = analysis_df.iloc[-1]

                    st.markdown("#### Average measurements")
                    metric_cols = st.columns(3)
                    for i, col in enumerate(numeric_columns):
                        label, unit = metric_info[col]
                        value = float(averages[col])
                        precision = 1 if col == "temperature" else 1 if col == "sleep_hours" else 0
                        metric_cols[i % 3].metric(label, f"{value:.{precision}f} {unit}")

                    st.markdown("#### Latest recorded measurements")
                    latest_cols = st.columns(3)
                    for i, col in enumerate(numeric_columns):
                        label, unit = metric_info[col]
                        value = float(latest_record[col])
                        precision = 1 if col in ("temperature", "sleep_hours") else 0
                        latest_cols[i % 3].metric(
                            f"Latest {label}", f"{value:.{precision}f} {unit}"
                        )

                    # Transparent prototype screening rules, not a medical diagnosis.
                    alerts = []
                    recommendations = []
                    avg_hr = float(averages["heart_rate"])
                    avg_spo2 = float(averages["spo2"])
                    avg_temp = float(averages["temperature"])
                    avg_sleep = float(averages["sleep_hours"])
                    if avg_hr > 100:
                        alerts.append(("warning", f"Average heart rate is {avg_hr:.1f} BPM, above the prototype review threshold of 100 BPM."))
                        recommendations.append("Review the heart-rate trend, measurement conditions and symptoms with the mission medical team.")
                    if avg_spo2 < 95:
                        alerts.append(("error", f"Average SpO₂ is {avg_spo2:.1f}%, below the prototype review threshold of 95%."))
                        recommendations.append("Verify the sensor reading and promptly escalate persistently low oxygen readings through the mission medical protocol.")
                    if avg_temp >= 38:
                        alerts.append(("warning", f"Average temperature is {avg_temp:.1f} °C, at or above the prototype review threshold of 38 °C."))
                        recommendations.append("Recheck temperature with a reliable device and report elevated or persistent readings to the medical team.")
                    if avg_sleep < 6:
                        alerts.append(("warning", f"Average sleep duration is {avg_sleep:.1f} hours, below ASTRA's prototype sleep-review target of 6 hours."))
                        recommendations.append("Review the sleep schedule, workload and sleep quality; discuss persistent sleep restriction with mission support.")
                    if float(averages["mood_score"]) < 3:
                        alerts.append(("info", "Average mood score is below 3 out of 5."))
                        recommendations.append("Offer a wellbeing check-in and review stressors, rest and social support.")
                    if not alerts:
                        st.success("No measurements crossed the current ASTRA prototype review thresholds in this uploaded dataset.")
                    else:
                        st.markdown("#### Health alerts")
                        for level, message in alerts:
                            if level == "error":
                                st.error(message)
                            elif level == "warning":
                                st.warning(message)
                            else:
                                st.info(message)

                    if not recommendations:
                        recommendations.append("Continue routine monitoring, keep measurements consistent, and review trends over time rather than relying on a single reading.")
                    st.markdown("#### ASTRA recommendations")
                    for number, recommendation in enumerate(recommendations, start=1):
                        st.markdown(f"**{number}.** {recommendation}")

                    st.markdown("#### Measurement trends")
                    trend_metric = st.selectbox(
                        "Choose a measurement", numeric_columns,
                        format_func=lambda x: metric_info[x][0],
                        key="import_trend_metric"
                    )
                    trend_fig = px.line(
                        analysis_df, x="timestamp", y=trend_metric,
                        markers=True,
                        title=f"{metric_info[trend_metric][0]} over time"
                    )
                    trend_fig.update_layout(
                        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=55, b=10),
                        xaxis_title="Recorded time", yaxis_title=metric_info[trend_metric][1]
                    )
                    st.plotly_chart(trend_fig, use_container_width=True)

                    st.markdown("#### Data quality & coverage")
                    q1, q2, q3 = st.columns(3)
                    q1.metric("Valid records", len(analysis_df))
                    q2.metric("Duplicate timestamps", int(analysis_df["timestamp"].duplicated().sum()))
                    duration_days = max((last_time - first_time).total_seconds() / 86400, 0)
                    q3.metric("Coverage", f"{duration_days:.1f} days")
                    st.caption(
                        "Thresholds are screening rules for this prototype, not clinical diagnostic criteria. "
                        "ASTRA's output cannot replace assessment by qualified medical staff."
                    )

                    if issues:
                        st.info("Fix all validation issues in the source file before importing. No records have been saved yet.")
                    else:
                        st.markdown("### Save analyzed data")
                        st.write("The validated records will be appended to ASTRA's local health dataset.")
                        if st.button("⬆️ Import validated records into ASTRA", key="confirm_health_import", use_container_width=True):
                            data_path = PROJECT_ROOT / "data" / "sample_health_data.csv"
                            data_path.parent.mkdir(parents=True, exist_ok=True)
                            if data_path.exists():
                                existing_df = pd.read_csv(data_path)
                            else:
                                existing_df = pd.DataFrame(columns=import_columns)
                            all_columns = list(dict.fromkeys(list(existing_df.columns) + import_columns))
                            existing_df = existing_df.reindex(columns=all_columns)
                            records_to_add = imported_df.reindex(columns=all_columns)
                            combined_df = pd.concat([existing_df, records_to_add], ignore_index=True)
                            combined_df.to_csv(data_path, index=False)
                            st.cache_data.clear()
                            st.session_state["health_import_success_count"] = len(imported_df)
                            st.rerun()
                else:
                    st.warning("There are no complete, valid records to analyze. Please correct the file and upload it again.")

        except ImportError:
            st.error("Excel support is missing. Install it in your project environment using: pip install openpyxl")
        except Exception as import_error:
            st.error(f"Could not read or analyze this file: {import_error}")

    imported_count = st.session_state.pop("health_import_success_count", None)
    if imported_count is not None:
        st.success(f"Successfully imported {imported_count} health record(s) into ASTRA.")

    st.stop()


elif st.session_state.current_page in ("Digital Profile","Intelligence","Trend Prediction","Mission Simulation","Real-Time Monitoring","Health Alerts","Health Reports","Crew Overview","Mission Comparison","ASTRA Assistant"):
    page=st.session_state.current_page
    def astra_head(kicker,title,sub):
        st.markdown(f'<div class="astra-hero"><div class="astra-kicker">{kicker}</div><div class="astra-heading">{title}</div><div class="astra-sub">{sub}</div></div>',unsafe_allow_html=True)
    def astra_back(key):
        if st.button("← Back to Advanced Mission Systems",key=key):
            navigate_to("Advanced Mission Systems"); st.rerun()
    def astra_flags(frame):
        if frame.empty:return []
        r=frame.sort_values("timestamp").iloc[-1]; out=[]
        rules=[("heart_rate","Heart rate","BPM",lambda x:x>100,"above 100 BPM"),("spo2","SpO₂","%",lambda x:x<95,"below 95%"),("temperature","Temperature","°C",lambda x:x>=38,"at or above 38 °C"),("sleep_hours","Sleep","hours",lambda x:x<6,"below 6 hours"),("mood_score","Mood score","/5",lambda x:x<3,"below 3/5")]
        for f,label,unit,test,rule in rules:
            if f in r.index and pd.notna(r[f]) and test(float(r[f])):out.append({"Indicator":label,"Value":float(r[f]),"Unit":unit,"Rule":rule,"Explanation":f"{label} is {float(r[f]):.1f} {unit}, {rule}."})
        return out
    def astra_report(frame,aid):
        latest_row=frame.sort_values("timestamp").iloc[-1]; fields=[("heart_rate","Heart rate","BPM"),("spo2","Oxygen saturation","%"),("temperature","Temperature","°C"),("sleep_hours","Sleep","hours"),("mood_score","Mood score","/5"),("activity_level","Activity","/10")]
        rows=[]
        for f,label,unit in fields:
            if f in frame and pd.notna(latest_row.get(f)):rows.append(f"<tr><td>{label}</td><td>{float(latest_row[f]):.1f} {unit}</td><td>{frame[f].mean():.1f} {unit}</td></tr>")
        alerts="".join(f"<li>{x['Explanation']}</li>" for x in astra_flags(frame)) or "<li>No latest values crossed the prototype screening rules.</li>"
        return f"<!doctype html><html><head><meta charset='utf-8'><style>body{{font-family:Arial;background:#eef4f9;padding:30px;color:#18314b}}main{{max-width:900px;margin:auto;background:white;padding:32px;border-radius:18px}}h1{{color:#087e9b}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;border-bottom:1px solid #dce6ef;text-align:left}}</style></head><body><main><h1>ASTRA · Astronaut Health Summary</h1><p>Astronaut: {aid}<br>Records: {len(frame)}<br>Period: {frame.timestamp.min()} — {frame.timestamp.max()}</p><h2>Latest and average readings</h2><table><tr><th>Indicator</th><th>Latest</th><th>Average</th></tr>{''.join(rows)}</table><h2>Screening notes</h2><ul>{alerts}</ul><p><b>Prototype notice:</b> These rules are not clinical diagnostic criteria. This report is not a substitute for assessment by qualified medical staff.</p></main></body></html>"

    if page=="Digital Profile":
        astra_head("MODULE 01 / DIGITAL IDENTITY","Astronaut Digital Health Profile","A consolidated biometric identity and record timeline."); astra_back("profile_back")
        hist=astronaut_df.sort_values("timestamp"); first,lastrow=hist.iloc[0],hist.iloc[-1]; span=max((lastrow.timestamp-first.timestamp).total_seconds()/86400,0)
        a,b,c,d=st.columns(4); a.metric("Astronaut ID",str(selected_astronaut)); b.metric("Health records",len(hist)); c.metric("Monitoring span",f"{span:.1f} days"); d.metric("Latest update",str(lastrow.timestamp)[:16])
        st.markdown("### Latest biometric profile")
        for start in (0,3):
            cols=st.columns(3)
            for col,(label,f,unit) in zip(cols,[("Heart rate","heart_rate","BPM"),("SpO₂","spo2","%"),("Temperature","temperature","°C"),("Sleep","sleep_hours","hrs"),("Mood","mood_score","/5"),("Activity","activity_level","/10")][start:start+3]):
                v=lastrow.get(f); val=f"{float(v):.1f} {unit}" if pd.notna(v) else "—"; col.metric(label,val)
        st.markdown("### Health record timeline"); st.dataframe(hist.sort_values("timestamp",ascending=False),use_container_width=True,hide_index=True)

    elif page=="Intelligence":
        astra_head("MODULE 02 / ASTRA INTELLIGENCE","ASTRA Intelligence Engine","Compare a personal baseline with recent records and explain every screened change."); astra_back("intel_back")
        hist=astronaut_df.sort_values("timestamp").copy(); metrics=["heart_rate","spo2","temperature","sleep_hours","mood_score"]
        if len(hist)<3:st.info("At least three records are recommended to separate a baseline window from recent readings.")
        else:
            n=st.slider("Recent records",1,min(5,len(hist)-1),min(3,len(hist)-1),key="intel_recent")
            base=hist.iloc[:-n][metrics].median(); recent=hist.tail(n)[metrics].mean(); limits={"heart_rate":10,"spo2":2,"temperature":.5,"sleep_hours":1,"mood_score":1}; signs={"heart_rate":1,"spo2":-1,"temperature":1,"sleep_hours":-1,"mood_score":-1}; rows=[]
            for f in metrics:
                delta=float(recent[f]-base[f]); flagged=delta*signs[f]>=limits[f]; rows.append({"Indicator":f.replace("_"," ").title(),"Baseline":round(float(base[f]),2),"Recent average":round(float(recent[f]),2),"Change":round(delta,2),"Screening":"Review" if flagged else "No threshold crossed"})
            flagged=sum(x["Screening"]=="Review" for x in rows); a,b,c=st.columns(3); a.metric("Signals reviewed",5); b.metric("Signals to review",flagged); c.metric("Recent records",n)
            if flagged>=2:st.warning("Multiple indicators crossed prototype change-screening rules; review the source readings and context.")
            elif flagged:st.info("One indicator crossed a prototype change-screening rule.")
            else:st.success("No tested indicator crossed the current baseline-change rules.")
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            st.caption("Baseline = median of earlier records; recent window = mean. Change thresholds are illustrative screening assumptions, not clinical criteria.")
            f=st.selectbox("Trend indicator",metrics,key="intel_plot_metric"); fig=px.line(hist,x="timestamp",y=f,markers=True,title=f.replace("_"," ").title()); fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)"); st.plotly_chart(fig,use_container_width=True)

    elif page=="Trend Prediction":
        astra_head("MODULE 03 / TREND EXPLORER","Health Trend Prediction","Illustrative mathematical projections based on historical measurements."); astra_back("trend_back")
        fields=["heart_rate","spo2","temperature","sleep_hours","mood_score"]; f=st.selectbox("Indicator",fields,key="trend_field"); hist=astronaut_df[["timestamp",f]].dropna().sort_values("timestamp").copy()
        if len(hist)<3:st.info("At least three valid measurements are needed for a projection.")
        else:
            x=pd.Series(range(len(hist)),dtype=float); y=hist[f].astype(float); slope=((x-x.mean())*(y-y.mean())).sum()/((x-x.mean())**2).sum() if len(x)>1 else 0; intercept=y.mean()-slope*x.mean(); step=hist.timestamp.iloc[-1]-hist.timestamp.iloc[-2]; step=step if pd.notna(step) and step.total_seconds()>0 else pd.Timedelta(days=1); dates=[hist.timestamp.iloc[-1]+step*i for i in (1,2,3)]; proj=[intercept+slope*i for i in range(len(hist),len(hist)+3)]
            fig=px.scatter(hist,x="timestamp",y=f,title=f"{f.replace('_',' ').title()} · history"); fig.add_scatter(x=dates,y=proj,mode="lines+markers",name="Illustrative projection",line=dict(dash="dash")); fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)"); st.plotly_chart(fig,use_container_width=True); st.dataframe(pd.DataFrame({"Projected timestamp":dates,"Illustrative value":proj}),use_container_width=True,hide_index=True)
            st.warning("This simple linear extrapolation is not a validated forecast and must not guide medical or mission-safety decisions.")

    elif page=="Mission Simulation":
        astra_head("MODULE 04 / SCENARIO LAB","Mission Simulation Lab","Explore hypothetical changes without altering the astronaut's saved records."); astra_back("sim_back"); r=astronaut_df.sort_values("timestamp").iloc[-1]; st.info("Simulation only. These adjustable coefficients are illustrative, not a physiological model.")
        c1,c2=st.columns(2); workload=c1.slider("Workload change",-30,50,0,5,key="sim_workload"); sleep=c2.slider("Sleep change (hours)",-4.,3.,0.,.5,key="sim_sleep"); env=st.select_slider("Environmental stress",["Low","Moderate","High"],value="Moderate",key="sim_env"); stress={"Low":0,"Moderate":3,"High":7}[env]
        values={"Heart rate":(max(30,float(r.heart_rate)+workload*.12+stress),"BPM"),"SpO₂":(max(50,min(100,float(r.spo2)-stress*.12)),"%"),"Temperature":(float(r.temperature)+stress*.025,"°C"),"Sleep":(max(0,min(24,float(r.sleep_hours)+sleep)),"hrs")}
        cols=st.columns(4)
        for col,(label,(value,unit)) in zip(cols,values.items()):col.metric(label,f"{value:.1f} {unit}")
        notes=[]
        if values["Heart rate"][0]>100:notes.append("Heart rate exceeds the prototype review threshold.")
        if values["SpO₂"][0]<95:notes.append("SpO₂ is below the prototype review threshold.")
        if values["Temperature"][0]>=38:notes.append("Temperature reaches the prototype review threshold.")
        if values["Sleep"][0]<6:notes.append("Sleep is below the prototype review target.")
        if notes:st.warning("Scenario flags: " + " ".join(notes))
        else:st.success("No simulated value crossed the current prototype review thresholds.")

    elif page=="Real-Time Monitoring":
        astra_head("MODULE 05 / SENSOR NETWORK","Real-Time Monitoring Architecture","Live-style console and proposed data pipeline for future wearable integration."); astra_back("rt_back"); r=astronaut_df.sort_values("timestamp").iloc[-1]
        st.info("No physical sensor is connected in this build. Values refresh from the loaded dataset, not from a live device.")
        cols=st.columns(4)
        for col,(label,f,unit) in zip(cols,[("Heart rate","heart_rate","BPM"),("SpO₂","spo2","%"),("Temperature","temperature","°C"),("Sleep","sleep_hours","hrs")]):col.metric(label,f"{float(r[f]):.1f} {unit}")
        st.markdown("### Proposed sensor pipeline"); cols=st.columns(4)
        for col,title,desc in zip(cols,["Wearable sensors","Data gateway","ASTRA analytics","Mission dashboard"],["ECG / pulse-ox / temperature","Validated data transport","Quality checks + rules","Visualization + review"]):
            col.markdown(f'<div class="astra-panel"><div class="astra-panel-label">{title.upper()}</div><p>{desc}</p><span class="astra-panel-unit">ARCHITECTURE LAYER</span></div>',unsafe_allow_html=True)
        st.markdown("### Recent records"); st.dataframe(astronaut_df.sort_values("timestamp",ascending=False).head(30),use_container_width=True,hide_index=True)

    elif page=="Health Alerts":
        astra_head("MODULE 06 / EXPLAINABLE ALERTS","Explainable Health Alerts","Each flag is connected to a visible reading and a plain-language rule."); astra_back("alerts_back"); findings=astra_flags(astronaut_df)
        if not findings:st.success("No latest measurement crossed the prototype screening rules.")
        for item in findings:
            with st.container(border=True):st.markdown(f"### {item['Indicator']} · {item['Value']:.1f} {item['Unit']}"); st.warning(item["Explanation"]); st.caption("Why displayed: this value crossed the named ASTRA prototype rule. Verify sensor quality and interpret with qualified mission medical staff.")
        st.markdown("### Active prototype rules"); st.dataframe(pd.DataFrame([{"Indicator":"Heart rate","Rule":"> 100 BPM"},{"Indicator":"SpO₂","Rule":"< 95%"},{"Indicator":"Temperature","Rule":"≥ 38 °C"},{"Indicator":"Sleep","Rule":"< 6 hours"},{"Indicator":"Mood","Rule":"< 3 / 5"}]),use_container_width=True,hide_index=True)

    elif page=="Health Reports":
        astra_head("MODULE 07 / REPORT CENTER","Automated Health Reports","Create a shareable summary from the selected astronaut's recorded data."); astra_back("report_back"); report=astra_report(astronaut_df,selected_astronaut); st.components.v1.html(report,height=500,scrolling=True)
        st.download_button("⬇ Download formatted HTML report",report.encode("utf-8"),file_name=f"ASTRA_{selected_astronaut}_report.html",mime="text/html",use_container_width=True)
        st.download_button("⬇ Download source records (CSV)",astronaut_df.to_csv(index=False).encode("utf-8-sig"),file_name=f"ASTRA_{selected_astronaut}_records.csv",mime="text/csv",use_container_width=True)

    elif page=="Crew Overview":
        astra_head("MODULE 08 / CREW MONITOR","Crew Health Overview","A crew-wide snapshot using each astronaut's latest available record."); astra_back("crew_back"); crew=df.sort_values("timestamp").groupby("astronaut_id",as_index=False).tail(1).copy(); a,b,c=st.columns(3); a.metric("Crew members",crew.astronaut_id.nunique()); b.metric("Records loaded",len(df)); c.metric("Latest update",str(crew.timestamp.max())[:16]); cols=[x for x in ["astronaut_id","timestamp","heart_rate","spo2","temperature","sleep_hours","mood_score"] if x in crew.columns]; st.dataframe(crew[cols],use_container_width=True,hide_index=True)
        f=st.selectbox("Crew indicator",["heart_rate","spo2","temperature","sleep_hours","mood_score"],key="crew_field"); chart=px.bar(crew,x="astronaut_id",y=f,color="astronaut_id",title=f.replace("_"," ").title()); chart.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False); st.plotly_chart(chart,use_container_width=True)

    elif page=="Mission Comparison":
        astra_head("MODULE 09 / COMPARATIVE ANALYTICS","Mission Comparison","Compare the same health indicator across selected crew members."); astra_back("compare_back"); people=sorted(df.astronaut_id.dropna().astype(str).unique()); chosen=st.multiselect("Astronauts to compare",people,default=people[:min(4,len(people))],key="compare_people"); f=st.selectbox("Indicator",["heart_rate","spo2","temperature","sleep_hours","mood_score"],key="compare_metric"); subset=df[df.astronaut_id.astype(str).isin(chosen)]
        if subset.empty:st.info("Select at least one astronaut with available records.")
        else:
            summary=subset.groupby("astronaut_id")[f].agg(["mean","min","max","count"]).reset_index(); st.dataframe(summary,use_container_width=True,hide_index=True); fig=px.box(subset,x="astronaut_id",y=f,color="astronaut_id",title=f"Distribution · {f.replace('_',' ').title()}"); fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False); st.plotly_chart(fig,use_container_width=True)

    elif page=="ASTRA Assistant":
        astra_head("MODULE 10 / DATA ASSISTANT","ASTRA Assistant","Ask simple questions about the selected astronaut and loaded dataset."); astra_back("assistant_back"); st.caption("Dataset assistant only; it does not diagnose or replace professional advice."); q=st.text_input("Ask ASTRA",placeholder="e.g. What is the latest heart rate?",key="astra_q")
        if st.button("Analyze question",key="astra_ask"):
            ql=q.lower(); r=astronaut_df.sort_values("timestamp").iloc[-1]
            if any(x in ql for x in ["heart rate","pulse","نبض"]):ans=f"Latest heart rate for {selected_astronaut}: {r.heart_rate} BPM."
            elif any(x in ql for x in ["spo2","oxygen","أكسجين"]):ans=f"Latest SpO₂ for {selected_astronaut}: {r.spo2}%."
            elif any(x in ql for x in ["temperature","حرارة"]):ans=f"Latest temperature: {r.temperature} °C."
            elif any(x in ql for x in ["sleep","نوم"]):ans=f"Latest sleep duration: {r.sleep_hours} hours."
            elif any(x in ql for x in ["alert","warning","تنبيه"]):
                fs=astra_flags(astronaut_df); ans="; ".join(x["Explanation"] for x in fs) if fs else "No latest value crossed the prototype rules."
            elif any(x in ql for x in ["record","data","سجل","بيانات"]):ans=f"{selected_astronaut} has {len(astronaut_df)} records from {astronaut_df.timestamp.min()} to {astronaut_df.timestamp.max()}."
            else:ans="I can summarize heart rate, SpO₂, temperature, sleep, alerts and record coverage."
            st.session_state["astra_answer"]=ans
        if st.session_state.get("astra_answer"):st.info(st.session_state["astra_answer"])
    st.stop()


elif st.session_state.current_page == "Manual":

    pass


else:
    st.stop()


if st.button("← Back to Home"):
    navigate_to("Home")
    st.rerun()


# ---------------- DAILY HEALTH CHECK ----------------

st.markdown(
    '<div class="section-title">◈ DAILY HEALTH CHECK</div>',
    unsafe_allow_html=True
)

st.caption("Enter the astronaut's latest health measurements.")

with st.form("daily_health_form"):

    col1, col2, col3 = st.columns(3)

    with col1:

        new_heart_rate = st.number_input(
            "Heart Rate (BPM)",
            min_value=30,
            max_value=220,
            value=72
        )

        new_spo2 = st.number_input(
            "SpO2 (%)",
            min_value=50,
            max_value=100,
            value=98
        )

    with col2:

        new_temperature = st.number_input(
            "Temperature (°C)",
            min_value=30.0,
            max_value=45.0,
            value=36.7,
            step=0.1
        )

        new_sleep = st.number_input(
            "Sleep Hours",
            min_value=0.0,
            max_value=24.0,
            value=8.0,
            step=0.5
        )

    with col3:

        new_mood = st.slider(
            "Mood Score",
            min_value=1,
            max_value=5,
            value=5
        )

        new_activity = st.slider(
            "Activity Level",
            min_value=1,
            max_value=10,
            value=7
        )

    submit_health = st.form_submit_button(
        "Submit Health Measurements",
        use_container_width=True
    )


# ---------------- SAVE NEW HEALTH RECORD ----------------

if submit_health:

    new_record = {
        "astronaut_id": selected_astronaut,
        "timestamp": datetime.now(),
        "heart_rate": new_heart_rate,
        "spo2": new_spo2,
        "temperature": new_temperature,
        "sleep_hours": new_sleep,
        "mood_score": new_mood,
        "activity_level": new_activity
    }

    data_path = (
        PROJECT_ROOT
        / "data"
        / "sample_health_data.csv"
    )

    current_data = pd.read_csv(data_path)

    updated_data = pd.concat(
        [current_data, pd.DataFrame([new_record])],
        ignore_index=True
    )

    updated_data.to_csv(
        data_path,
        index=False
    )

    # Clear cached data
    st.cache_data.clear()

    # Show success message after rerun
    st.session_state["health_saved"] = True

    st.rerun()


# ---------------- SUCCESS MESSAGE ----------------

if st.session_state.pop("health_saved", False):

    st.markdown(
        """
        <div style="
            background-color: #102D2A;
            color: #75F0B5;
            border: 1px solid #32C98A;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: 600;
            margin-top: 10px;
        ">
            ✓ Health measurements saved successfully!
        </div>
        """,
        unsafe_allow_html=True
    )




# ---------------- HEALTH METRICS ----------------

st.markdown(
    '<div id="overview"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">◈ HEALTH OVERVIEW</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


def metric_card(column, label, value, unit):

    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


metric_card(
    col1,
    "❤️ HEART RATE",
    f"{summary['Average Heart Rate']:.1f}",
    "BPM"
)

metric_card(
    col2,
    "🫁 OXYGEN LEVEL",
    f"{summary['Average SpO2']:.1f}",
    "SpO2 %"
)

metric_card(
    col3,
    "🌡️ TEMPERATURE",
    f"{summary['Average Temperature']:.1f}",
    "°C"
)

metric_card(
    col4,
    "🌙 SLEEP",
    f"{summary['Average Sleep Hours']:.1f}",
    "HOURS"
)


# ---------------- HEALTH CHARTS ----------------

st.markdown(
    '<div id="biometrics"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">◈ BIOMETRIC TRENDS</div>',
    unsafe_allow_html=True
)

chart1, chart2 = st.columns(2)


with chart1:

    fig_hr = px.line(
        astronaut_df,
        x="timestamp",
        y="heart_rate",
        title="Heart Rate Monitoring",
        markers=True
    )

    fig_hr.update_traces(
        line=dict(color="#38bdf8", width=3),
        marker=dict(size=8)
    )

    fig_hr.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#eaf2ff",
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title="BPM",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig_hr,
        use_container_width=True
    )


with chart2:

    fig_spo2 = px.line(
        astronaut_df,
        x="timestamp",
        y="spo2",
        title="Blood Oxygen Monitoring",
        markers=True
    )

    fig_spo2.update_traces(
        line=dict(color="#a78bfa", width=3),
        marker=dict(size=8)
    )

    fig_spo2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#eaf2ff",
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title="SpO2 %",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig_spo2,
        use_container_width=True
    )


# ---------------- TEMPERATURE & SLEEP TRENDS ----------------

st.markdown(
    '<div class="section-title">◈ TEMPERATURE & SLEEP TRENDS</div>',
    unsafe_allow_html=True
)

chart3, chart4 = st.columns(2)


with chart3:

    fig_temp = px.line(
        astronaut_df,
        x="timestamp",
        y="temperature",
        title="Body Temperature Monitoring",
        markers=True
    )

    fig_temp.update_traces(
        line=dict(color="#FFB86C", width=3),
        marker=dict(size=8)
    )

    fig_temp.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#eaf2ff",
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title="Temperature °C",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )


with chart4:

    fig_sleep = px.line(
        astronaut_df,
        x="timestamp",
        y="sleep_hours",
        title="Sleep Hours Monitoring",
        markers=True
    )

    fig_sleep.update_traces(
        line=dict(color="#5EE4FF", width=3),
        marker=dict(size=8)
    )

    fig_sleep.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#eaf2ff",
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title="Sleep Hours",
        xaxis_title="Date"
    )

    st.plotly_chart(
        fig_sleep,
        use_container_width=True
    )


# ---------------- AI HEALTH ANALYSIS ----------------

st.markdown(
    '<div id="insights"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">◈ AI HEALTH INSIGHTS</div>',
    unsafe_allow_html=True
)

left, right = st.columns([2, 1])


with left:

    if alerts:

        for alert in alerts:

            st.markdown(
                f'<div class="alert-card">⚠️ {alert}</div>',
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            '<div class="normal-card">'
            '✓ No unusual changes detected against the current baseline.'
            '</div>',
            unsafe_allow_html=True
        )


with right:

    if health_status == "Warning":
        status_color = "#fbbf24"
    else:
        status_color = "#34d399"

    st.markdown(
        f"""
        <div class="status-card">
            <span style="color:#a9bdd8;">
                HEALTH STATUS
            </span>
            <h2 style="color:{status_color};">
                {health_status}
            </h2>
            <span style="color:#a9bdd8;">
                DETECTED CHANGES
            </span>
            <h1 style="color:{status_color};">
                {len(alerts)}
            </h1>
            <span style="color:#a9bdd8;font-size:12px;">
                Experimental baseline alerts
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- HEALTH SUMMARY DETAILS ----------------

st.markdown(
    '<div class="section-title">◈ HEALTH SUMMARY DETAILS</div>',
    unsafe_allow_html=True
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric(
    "Average Mood Score",
    f"{summary['Average Mood Score']:.1f} / 5"
)

summary_col2.metric(
    "Average Activity Level",
    f"{summary['Average Activity Level']:.1f}"
)

summary_col3.metric(
    "Average Sleep",
    f"{summary['Average Sleep Hours']:.1f} hours"
)


# ---------------- SMART HEALTH RECOMMENDATIONS ----------------

st.markdown(
    '<div class="section-title">◈ SMART HEALTH RECOMMENDATIONS</div>',
    unsafe_allow_html=True
)

st.caption(
    "Personalized suggestions based on detected health changes."
)

for item in recommendations:

    with st.container(border=True):

        st.markdown(
            f"""
            <p style="
                color: #5EE4FF;
                font-size: 16px;
                font-weight: 700;
                margin-bottom: 10px;
            ">
                {item['Category']}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <p style="
                color: #FFB86C;
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 10px;
            ">
                ⚠️ {item['Alert']}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"💡 **Recommendation:** {item['Recommendation']}"
        )


# ---------------- LATEST RECORD ----------------

st.markdown(
    '<div id="latest-record"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">◈ LATEST HEALTH RECORD</div>',
    unsafe_allow_html=True
)

st.dataframe(
    astronaut_df.tail(5),
    use_container_width=True,
    hide_index=True
)


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "ASTRA prototype | Synthetic test data | "
    "Experimental baseline alerts | "
    "Not intended for medical diagnosis."
)
