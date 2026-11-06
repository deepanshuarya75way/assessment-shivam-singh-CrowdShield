mport streamlit as st
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# PATHS AND BACKEND
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.detect import run_detection

ASSETS = ROOT / "assets"
OUTPUTS = ROOT / "outputs"

OUTPUTS.mkdir(exist_ok=True)

LOGO = ASSETS / "logo.png"

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="CrowdShield | Command Centre",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "processed_video" not in st.session_state:
    st.session_state.processed_video = None

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

# --------------------------------------------------
# CSS - RED AND BLACK CYBERSECURITY THEME
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --red: #ff3048;
    --dark-red: #9e1027;
    --black: #070707;
    --panel: #111111;
    --border: rgba(255,48,72,0.28);
    --text: #eeeeee;
    --muted: #888888;
}

.stApp {
    background-color: #070707;
    background-image:
        linear-gradient(rgba(255,48,72,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,48,72,0.045) 1px, transparent 1px);
    background-size: 35px 35px;
    animation: gridMove 25s linear infinite;
    color: var(--text);
}

@keyframes gridMove {
    from { background-position: 0 0; }
    to { background-position: 35px 35px; }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    color: white !important;
}

p, label, span {
    color: inherit;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #0c0c0c;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
    color: var(--red) !important;
}

/* HEADER */

.cs-header {
    border: 1px solid var(--border);
    background: linear-gradient(120deg, #18080b, #090909 70%);
    padding: 28px;
    border-radius: 12px;
    position: relative;
    overflow: hidden;
    margin-bottom: 25px;
    box-shadow: 0 0 25px rgba(255,48,72,0.08);
}

.cs-header:after {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 2px;
    background: var(--red);
    box-shadow: 0 0 20px var(--red);
    animation: scan 5s linear infinite;
}

@keyframes scan {
    to { left: 150%; }
}

.cs-eyebrow {
    color: var(--red);
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    letter-spacing: 3px;
    margin-bottom: 10px;
}

.cs-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(22px, 3vw, 38px);
    font-weight: 800;
    letter-spacing: 1px;
    color: white;
}

.cs-subtitle {
    color: #999;
    font-size: 13px;
    letter-spacing: 1px;
    margin-top: 8px;
}

/* STATUS */

.status-live {
    color: #ff3048;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    letter-spacing: 2px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    50% { opacity: 0.35; }
}

/* METRIC CARDS */

.metric-card {
    background: linear-gradient(145deg, #171717, #0b0b0b);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    min-height: 120px;
    transition: 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    border-color: var(--red);
    box-shadow: 0 0 22px rgba(255,48,72,0.2);
}

.metric-label {
    color: #999;
    font-size: 11px;
    letter-spacing: 2px;
    font-family: 'Orbitron', sans-serif;
}

.metric-value {
    color: white;
    font-family: 'Rajdhani', sans-serif;
    font-size: 38px;
    font-weight: 700;
    margin-top: 8px;
}

/* PANELS */

.cs-panel {
    background: #101010;
    border: 1px solid var(--border);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
}

/* RADAR */

.radar {
    width: 170px;
    height: 170px;
    margin: 18px auto;
    border-radius: 50%;
    border: 1px solid rgba(255,48,72,0.7);
    background:
        radial-gradient(circle, transparent 20%, rgba(255,48,72,0.08) 21%, transparent 22%),
        repeating-radial-gradient(circle, transparent 0 24px, rgba(255,48,72,0.25) 25px 26px);
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 25px rgba(255,48,72,0.15);
}

.radar:before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: conic-gradient(
        from 0deg,
        transparent 0deg,
        transparent 280deg,
        rgba(255,48,72,0.5) 360deg
    );
    animation: radarSweep 4s linear infinite;
}

.radar:after {
    content: "";
    position: absolute;
    width: 7px;
    height: 7px;
    background: var(--red);
    border-radius: 50%;
    top: 48%;
    left: 68%;
    box-shadow: 0 0 12px var(--red);
}

@keyframes radarSweep {
    to { transform: rotate(360deg); }
}

/* BUTTONS */

.stButton > button {
    background: linear-gradient(90deg, #9e1027, #ff3048);
    color: white !important;
    border: 1px solid #ff3048;
    border-radius: 7px;
    font-weight: 700;
    letter-spacing: 1px;
    transition: 0.25s;
}

.stButton > button:hover {
    box-shadow: 0 0 20px rgba(255,48,72,0.45);
    transform: translateY(-2px);
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: #111;
    border: 1px dashed rgba(255,48,72,0.5);
    border-radius: 10px;
    padding: 15px;
}

/* ALERT */

.alert-box {
    background: rgba(255,48,72,0.08);
    border-left: 4px solid var(--red);
    padding: 14px;
    border-radius: 5px;
    animation: alertEntry 0.6s ease;
}

@keyframes alertEntry {
    from { opacity: 0; transform: translateX(-12px); }
    to { opacity: 1; transform: translateX(0); }
}

/* SECTION DIVIDER */

.cs-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #ff3048, transparent);
    margin: 25px 0;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

logo_col, title_col, status_col = st.columns([1.4, 6, 2])

with logo_col:
    if LOGO.exists():
        st.image(str(LOGO), width=140)
    else:
        st.error("Logo file not found")

with title_col:
    st.markdown("""
    <div class="cs-header">
        <div class="cs-eyebrow">SECURITY OPERATIONS CENTRE / 01</div>
        <div class="cs-title">CROWD INTELLIGENCE COMMAND CENTRE</div>
        <div class="cs-subtitle">
            ADVANCED VIDEO SURVEILLANCE • PERSON DETECTION • MULTI-OBJECT TRACKING
        </div>
    </div>
    """, unsafe_allow_html=True)

with status_col:
    st.markdown("""
    <div class="cs-panel" style="text-align:center;">
        <div class="status-live">● SYSTEM INTERFACE</div>
        <p style="font-size:11px;color:#888;margin-top:10px;">
            DETECTION ENGINE
        </p>
        <p style="color:#ff3048;font-family:Orbitron;font-size:12px;">
            READY
        </p>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=150)

    st.markdown("## CROWDShield")
    st.markdown("---")

    st.markdown("### SYSTEM MODULES")
    st.markdown("🔴 Person Detection")
    st.markdown("🔴 ByteTrack Tracking")
    st.markdown("🔴 Crowd Analytics")
    st.markdown("🔴 Video Intelligence")
    st.markdown("---")

    st.markdown("### SYSTEM INFORMATION")

    st.caption("PROJECT: CROWDSHIELD")
    st.caption("MODEL: YOLO11n")
    st.caption("TRACKER: BYTETRACK")
    st.caption("MODE: VIDEO ANALYSIS")

    st.markdown("---")
    st.caption(f"DATE: {datetime.now().strftime('%d %b %Y')}")

# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

left, right = st.columns([1.6, 1])

# --------------------------------------------------
# LEFT: VIDEO UPLOAD AND DETECTION
# --------------------------------------------------

with left:
    st.markdown("### VIDEO SURVEILLANCE")

    uploaded_file = st.file_uploader(
        "Upload surveillance footage",
        type=["mp4", "avi", "mov", "mkv"]
    )

    if uploaded_file:
        st.success(f"VIDEO LOADED: {uploaded_file.name}")

        # OPERATOR CONFIGURABLE CROWD THRESHOLDS

        st.markdown("### CROWD THRESHOLD SETTINGS")

        col1, col2 = st.columns(2)

        with col1:
            elevated_limit = st.number_input(
                "Elevated Crowd Limit",
                min_value=1,
                value=15,
                step=1
            )

        with col2:
            high_limit = st.number_input(
                "High Crowd Limit",
                min_value=1,
                value=30,
                step=1
            )

        st.caption(
            "Set the crowd limits for the selected surveillance video."
        )

        if st.button(
            "🚨 INITIATE CROWD DETECTION",
            use_container_width=True
        ):

            # VALIDATION

            if elevated_limit == high_limit:
                st.error(
                    "Invalid limits: Elevated limit must be lower than High limit."
                )
                st.stop()

            # AUTOMATICALLY HANDLE REVERSED INPUTS

            elevated_limit, high_limit = sorted(
                [elevated_limit, high_limit]
            )

            input_path = ROOT / uploaded_file.name

            output_path = OUTPUTS / (
                f"processed_{Path(uploaded_file.name).stem}.mp4"
            )

            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(value):
                progress_bar.progress(
                    min(max(int(value), 0), 100)
                )

                status_text.markdown(
                    f"**PROCESSING VIDEO: {int(value)}%**"
                )

            try:
                with st.spinner(
                    "ANALYSING SURVEILLANCE FOOTAGE..."
                ):

                    results = run_detection(
                        str(input_path),
                        str(output_path),
                        progress_callback=update_progress,
                        elevated_limit=elevated_limit,
                        high_limit=high_limit
                    )

                st.session_state.results = results
                st.session_state.processed_video = str(output_path)
                st.session_state.uploaded_name = uploaded_file.name

                progress_bar.progress(100)

                status_text.success(
                    "DETECTION COMPLETED SUCCESSFULLY"
                )

            except Exception as e:
                st.error(f"Detection failed: {e}")

            finally:
                if input_path.exists():
                    input_path.unlink()

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("### PROCESSED SURVEILLANCE FEED")

    if (
        st.session_state.processed_video
        and Path(st.session_state.processed_video).exists()
    ):

        st.video(st.session_state.processed_video)

        with open(
            st.session_state.processed_video,
            "rb"
        ) as video_file:

            st.download_button(
                "⬇ DOWNLOAD PROCESSED VIDEO",
                data=video_file,
                file_name=Path(
                    st.session_state.processed_video
                ).name,
                mime="video/mp4",
                use_container_width=True
            )

    else:
        st.markdown("""
        <div class="cs-panel" style="text-align:center;padding:55px 15px;">
            <div style="font-size:45px;">📹</div>
            <div class="cs-eyebrow">NO PROCESSED FEED</div>
            <p style="color:#777;font-size:12px;">
                Upload footage and initiate detection to view tracking output.
            </p>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# RIGHT: RADAR AND METRICS
# --------------------------------------------------

with right:
    st.markdown("### SURVEILLANCE SCANNER")

    st.markdown("""
    <div class="radar"></div>
    <div style="
        text-align:center;
        color:#ff3048;
        font-family:Orbitron;
        font-size:11px;
        letter-spacing:2px;
    ">
        SCANNER INTERFACE ACTIVE
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown("### DETECTION INTELLIGENCE")

    results = st.session_state.results

    current_people = results["current_people"] if results else 0
    total_people = results["total_people"] if results else 0
    fps = results["fps"] if results else 0
    frames = results["frames_processed"] if results else 0

    metric1, metric2 = st.columns(2)

    with metric1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CURRENT CROWD</div>
            <div class="metric-value">{current_people}</div>
        </div>
        """, unsafe_allow_html=True)

    with metric2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TOTAL PEOPLE SEEN</div>
            <div class="metric-value">{total_people}</div>
        </div>
        """, unsafe_allow_html=True)

    metric3, metric4 = st.columns(2)

    with metric3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PROCESSING FPS</div>
            <div class="metric-value">{fps:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    with metric4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">FRAMES ANALYSED</div>
            <div class="metric-value">{frames}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="cs-divider"></div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # CONFIGURABLE THREAT MONITOR
    # --------------------------------------------------

    st.markdown("### THREAT MONITOR")

    if results:

        elevated_limit = results.get("elevated_limit", 15)
        high_limit = results.get("high_limit", 30)

        if current_people >= high_limit:

            st.markdown("""
            <div class="alert-box">
                <b style="color:#ff3048;">⚠ HIGH CROWD LEVEL</b>
                <p style="font-size:12px;color:#aaa;">
                    Crowd count has crossed the high threshold.
                </p>
            </div>
            """, unsafe_allow_html=True)

        elif current_people >= elevated_limit:

            st.markdown("""
            <div class="alert-box">
                <b style="color:#ff9b42;">⚠ ELEVATED CROWD LEVEL</b>
                <p style="font-size:12px;color:#aaa;">
                    Monitor the crowd density.
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.success(
                "✓ Crowd count is below the configured alert thresholds."
            )

    else:
        st.info("Waiting for video analysis.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    '<div class="cs-divider"></div>',
    unsafe_allow_html=True
)

st.markdown("""
<div style="text-align:center;padding:15px;">
    <div style="
        font-family:Orbitron;
        color:#ff3048;
        font-size:13px;
        letter-spacing:3px;
    ">
        CROWDShield
    </div>
    <p style="font-size:10px;color:#666;">
        INTELLIGENT CROWD MONITORING SYSTEM
        | YOLO11 | BYTETRACK
    </p>
</div>
""", unsafe_allow_html=True)