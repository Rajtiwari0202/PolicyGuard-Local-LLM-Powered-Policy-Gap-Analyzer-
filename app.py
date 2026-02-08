import streamlit as st
import time
from gap_detector import find_gaps
from llm_rewriter import rewrite_policy

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
if "gaps" not in st.session_state:
    st.session_state.gaps = None

if "improved_policy" not in st.session_state:
    st.session_state.improved_policy = None

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="PolicyGuard | Policy Gap Analysis",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# Global Styling
# --------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', system-ui;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
hr {
    border: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div style="padding-bottom: 1rem;">
    <h1 style="margin-bottom:0;">🔐 PolicyGuard</h1>
    <p style="color:#6B7280; margin-top:0.25rem;">
        Offline Policy Gap Analysis & Improvement Platform
    </p>
</div>
<hr>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Upload Section
# --------------------------------------------------
st.subheader("Upload Organizational Policy")

uploaded_file = st.file_uploader(
    "Upload policy document (TXT)",
    type=["txt"]
)

st.caption("🔒 Fully offline processing. No data leaves your system.")

# --------------------------------------------------
# Domain + Framework
# --------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    policy_domain = st.selectbox(
        "Policy Domain",
        [
            "Information Security Management System (ISMS)",
            "Data Privacy and Security",
            "Patch Management",
            "Risk Management"
        ]
    )

with col2:
    st.markdown("""
    **Benchmark Framework**  
    CIS MS-ISAC  
    NIST Cybersecurity Framework (2024)
    """)

# --------------------------------------------------
# Helper: Progress Bar + ETA Countdown
# --------------------------------------------------
def show_generation_progress():
    progress = st.progress(0)
    status = st.empty()
    eta = st.empty()

    stages = [
        ("Preparing prompt for local LLM…", 20, 1.5),
        ("Sending request to Ollama…", 40, 1.5),
        ("Generating improved policy…", 70, 3.0),
        ("Finalizing output…", 90, 1.0),
    ]

    total_time = sum(stage[2] for stage in stages)
    elapsed = 0.0

    for message, percent, duration in stages:
        status.info(message)
        steps = int(duration / 0.3)

        for _ in range(steps):
            elapsed += 0.3
            remaining = max(total_time - elapsed, 0)

            eta.caption(f"⏳ Estimated time remaining: {int(remaining)} seconds")
            progress.progress(min(percent, int((elapsed / total_time) * 100)))
            time.sleep(0.3)

    return progress, status, eta

# --------------------------------------------------
# Helper: Animated Compliance Meter
# --------------------------------------------------
def animated_compliance_meter(score):
    meter = st.progress(0)
    label = st.empty()

    target = int(score)
    current = 0

    while current <= target:
        meter.progress(current)

        if current < 40:
            label.error(f"Compliance Level: {current}% (Low)")
        elif current < 70:
            label.warning(f"Compliance Level: {current}% (Moderate)")
        else:
            label.success(f"Compliance Level: {current}% (High)")

        time.sleep(0.02)
        current += 1

# --------------------------------------------------
# Process Uploaded File
# --------------------------------------------------
if uploaded_file is not None:
    try:
        policy_text = uploaded_file.read().decode("utf-8")
    except Exception:
        st.error("Unable to read file. Please upload a valid UTF-8 encoded text file.")
        st.stop()

    st.markdown("---")
    st.subheader("Uploaded Policy Content")

    st.text_area("Policy Text", policy_text, height=220)

    # --------------------------------------------------
    # Run Gap Analysis
    # --------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Run Gap Analysis", type="primary"):
        with st.spinner("Analyzing policy against reference framework..."):
            st.session_state.gaps = find_gaps(policy_text)
            st.session_state.improved_policy = None

    # --------------------------------------------------
    # Show Analysis Results
    # --------------------------------------------------
    if st.session_state.gaps is not None:
        gaps = st.session_state.gaps

        st.markdown("---")
        st.subheader("Analysis Results")

        TOTAL_SECTIONS = 8
        found_sections = TOTAL_SECTIONS - len(gaps)
        score = (found_sections / TOTAL_SECTIONS) * 100

        st.markdown("### Compliance Meter")
        animated_compliance_meter(score)

        left, right = st.columns(2)

        with left:
            st.markdown("### Identified Gaps")
            if not gaps:
                st.success("No major gaps identified. Policy is well aligned.")
            else:
                for gap in gaps:
                    st.warning(gap)

        with right:
            st.markdown("### Policy Improvement Summary")
            st.write(
                "Based on the identified gaps, the policy requires additional "
                "controls, clearer responsibilities, and alignment with NIST functions."
            )

        # --------------------------------------------------
        # Generate Improved Policy (Progress + ETA)
        # --------------------------------------------------
        st.markdown("---")
        st.subheader("Generate Improved Policy")

        if st.button("Generate Improved Policy using Local LLM", type="primary"):
            progress, status, eta = show_generation_progress()

            try:
                st.session_state.improved_policy = rewrite_policy(
                    policy_text,
                    st.session_state.gaps
                )

                progress.progress(100)
                status.success("Policy generation completed successfully.")
                eta.empty()

            except Exception as e:
                status.error(f"Generation failed: {str(e)}")
                eta.empty()

            finally:
                time.sleep(0.3)
                progress.empty()

    # --------------------------------------------------
    # Show Improved Policy
    # --------------------------------------------------
    if st.session_state.improved_policy:
        st.success("Improved policy generated successfully.")

        st.text_area(
            "Improved Policy Output",
            st.session_state.improved_policy,
            height=320
        )

        st.download_button(
            label="Download Improved Policy",
            data=st.session_state.improved_policy,
            file_name="improved_policy.txt",
            mime="text/plain"
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("""
<hr>
<p style="text-align:center; color:#6B7280; font-size:0.85rem;">
Fully Offline • Local LLM Execution • No External APIs
</p>
""", unsafe_allow_html=True)
