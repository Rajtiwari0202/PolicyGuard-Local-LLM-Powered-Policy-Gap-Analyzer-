from __future__ import annotations

import json
import time

import streamlit as st

from gap_detector import CONTROL_LIBRARY, analyze_policy, build_gap_report
from llm_rewriter import rewrite_policy


SAMPLE_POLICIES = {
    "Patch Management - incomplete": """Patch Management Policy

Purpose:
This policy defines patching rules.

Scope:
Applies to organizational servers and laptops.

Responsibilities:
IT installs updates monthly when possible.
""",
    "Data Privacy - weak controls": """Data Privacy Policy

Purpose:
Protect customer data.

Scope:
Applies to customer databases.

Access:
Only approved employees should access customer data.

Compliance:
The policy is reviewed periodically.
""",
}


st.set_page_config(
    page_title="PolicyGuard | Local Policy Gap Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
:root {
    --ink: #ecfdf5;
    --muted: #a7b4c7;
    --panel: rgba(15, 23, 42, 0.82);
    --line: rgba(148, 163, 184, 0.22);
    --green: #34d399;
    --blue: #60a5fa;
    --amber: #fbbf24;
    --rose: #fb7185;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(52, 211, 153, 0.18), transparent 30rem),
        radial-gradient(circle at 90% 8%, rgba(96, 165, 250, 0.18), transparent 28rem),
        linear-gradient(135deg, #020617 0%, #0f172a 50%, #111827 100%);
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}

.hero {
    padding: 2rem;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(8, 47, 73, 0.72));
    box-shadow: 0 30px 90px rgba(0,0,0,0.28);
}

.eyebrow {
    display: inline-flex;
    gap: .45rem;
    padding: .4rem .7rem;
    border: 1px solid rgba(52, 211, 153, .32);
    border-radius: 999px;
    color: #a7f3d0;
    background: rgba(52, 211, 153, .08);
    font-weight: 800;
    font-size: .82rem;
}

.hero h1 {
    margin: 1rem 0 0;
    max-width: 12ch;
    font-size: clamp(3rem, 7vw, 5.8rem);
    line-height: .92;
    letter-spacing: 0;
}

.hero p {
    max-width: 52rem;
    color: #cbd5e1;
    font-size: 1.05rem;
    line-height: 1.7;
}

.metric-card {
    padding: 1rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: rgba(15, 23, 42, .72);
}

.metric-card span {
    color: var(--muted);
    font-size: .82rem;
}

.metric-card strong {
    display: block;
    font-size: 2rem;
}

.control-card {
    padding: 1rem;
    margin-bottom: .75rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: rgba(15, 23, 42, .68);
}

.severity {
    display: inline-block;
    padding: .22rem .5rem;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 800;
}

.Critical { background: rgba(251, 113, 133, .18); color: #fecdd3; }
.High { background: rgba(251, 191, 36, .18); color: #fde68a; }
.Medium { background: rgba(96, 165, 250, .18); color: #bfdbfe; }

.footer-note {
    text-align: center;
    color: var(--muted);
    font-size: .85rem;
    margin-top: 2rem;
}

textarea, input, select {
    border-radius: 10px !important;
}

.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    color: #f8fafc !important;
    background: rgba(15, 23, 42, .9) !important;
    border: 1px solid var(--line) !important;
}

section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    color: #111827 !important;
    background: #ffffff !important;
}

.stTabs [data-baseweb="tab"] {
    color: #cbd5e1;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


def get_policy_text() -> tuple[str, str]:
    with st.sidebar:
        st.header("Policy input")
        input_mode = st.radio("Input mode", ["Sample policy", "Upload TXT", "Paste text"])
        domain = st.selectbox(
            "Policy domain",
            [
                "Patch Management",
                "Information Security Management System",
                "Data Privacy and Security",
                "Risk Management",
                "Incident Response",
            ],
        )

        if input_mode == "Upload TXT":
            uploaded_file = st.file_uploader("Upload policy document", type=["txt"])
            if uploaded_file is None:
                return "", domain
            return uploaded_file.read().decode("utf-8", errors="replace"), domain

        if input_mode == "Paste text":
            return st.text_area("Policy text", height=260), domain

        sample_name = st.selectbox("Sample", list(SAMPLE_POLICIES.keys()))
        return SAMPLE_POLICIES[sample_name], domain


def render_gap_card(gap: dict) -> None:
    st.markdown(
        f"""
        <div class="control-card">
            <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;">
                <strong>{gap['control_id']} - {gap['title']}</strong>
                <span class="severity {gap['severity']}">{gap['severity']}</span>
            </div>
            <p style="color:#cbd5e1;margin:.55rem 0 0;">{gap['recommendation']}</p>
            <small style="color:#94a3b8;">NIST function: {gap['nist_function']} | Weight: {gap['weight']}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


policy_text, domain = get_policy_text()

st.markdown(
    """
    <section class="hero">
        <span class="eyebrow">Local LLM governance analyzer</span>
        <h1>PolicyGuard</h1>
        <p>
            Analyze cybersecurity policies against a NIST-style control baseline,
            identify missing governance language, rank remediation severity, and
            generate an improved policy draft without sending sensitive content to cloud APIs.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")

if not policy_text.strip():
    st.info("Choose a sample, upload a TXT policy, or paste policy text to begin.")
    st.stop()

analysis = analyze_policy(policy_text, domain)

metric_cols = st.columns(4)
metric_cols[0].markdown(f"<div class='metric-card'><span>Compliance score</span><strong>{analysis['score']}%</strong></div>", unsafe_allow_html=True)
metric_cols[1].markdown(f"<div class='metric-card'><span>Readiness</span><strong>{analysis['readiness']}</strong></div>", unsafe_allow_html=True)
metric_cols[2].markdown(f"<div class='metric-card'><span>Missing controls</span><strong>{analysis['summary']['missing']}</strong></div>", unsafe_allow_html=True)
metric_cols[3].markdown(f"<div class='metric-card'><span>Critical gaps</span><strong>{analysis['summary']['critical_gaps']}</strong></div>", unsafe_allow_html=True)

st.write("")
st.progress(int(analysis["score"]))

tab_overview, tab_gaps, tab_policy, tab_export = st.tabs([
    "Executive view",
    "Gap register",
    "Improved policy",
    "Exports",
])

with tab_overview:
    left, right = st.columns([1.1, .9])
    with left:
        st.subheader("Uploaded policy")
        st.markdown(
            f"""
            <div class="control-card" style="white-space:pre-wrap;min-height:260px;">
                {policy_text}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.subheader("Control coverage")
        st.write(f"Present controls: **{analysis['summary']['present']} / {analysis['summary']['total_controls']}**")
        st.write(f"High severity gaps: **{analysis['summary']['high_gaps']}**")
        if analysis["vague_findings"]:
            st.warning("Vague language found: " + ", ".join(analysis["vague_findings"]))
        else:
            st.success("No vague language flags detected.")

        st.markdown("#### Present evidence")
        for control in analysis["present_controls"][:5]:
            st.caption(f"{control['control_id']} {control['title']}: {control['evidence']}")

with tab_gaps:
    st.subheader("Prioritized remediation register")
    if not analysis["gaps"]:
        st.success("No major missing controls detected.")
    for gap in analysis["gaps"]:
        render_gap_card(gap)

with tab_policy:
    st.subheader("Generated improved policy")
    st.caption("Uses Ollama when available. If not, PolicyGuard generates a deterministic audit-ready fallback draft.")
    if st.button("Generate improved policy", type="primary"):
        with st.spinner("Generating improved policy draft..."):
            time.sleep(.4)
            st.session_state["improved_policy"] = rewrite_policy(policy_text, analysis["gaps"], domain)

    improved_policy = st.session_state.get("improved_policy")
    if improved_policy:
        st.text_area("Improved policy output", improved_policy, height=420)
        st.download_button("Download improved policy", improved_policy, "improved_policy.txt", "text/plain")
    else:
        st.info("Click the button to generate a revised policy and remediation roadmap.")

with tab_export:
    gap_report = build_gap_report(analysis)
    analysis_json = json.dumps(analysis, indent=2)
    st.subheader("Download analysis artifacts")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Gap report", gap_report, "policyguard_gap_report.txt", "text/plain")
    c2.download_button("Analysis JSON", analysis_json, "policyguard_analysis.json", "application/json")
    c3.download_button("Original policy", policy_text, "uploaded_policy.txt", "text/plain")

    st.markdown("#### Control baseline")
    rows = "".join(
        f"""
        <tr>
            <td>{control.control_id}</td>
            <td>{control.title}</td>
            <td>{control.nist_function}</td>
            <td><span class="severity {control.severity}">{control.severity}</span></td>
            <td>{control.weight}</td>
        </tr>
        """
        for control in CONTROL_LIBRARY
    )
    st.markdown(
        f"""
        <div class="control-card" style="padding:0;overflow:hidden;">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="color:#a7b4c7;text-align:left;">
                        <th style="padding:.8rem;">Control</th>
                        <th style="padding:.8rem;">Title</th>
                        <th style="padding:.8rem;">Function</th>
                        <th style="padding:.8rem;">Severity</th>
                        <th style="padding:.8rem;">Weight</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        <style>
            td {{ padding:.75rem .8rem; border-top:1px solid rgba(148,163,184,.18); color:#e2e8f0; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<p class='footer-note'>Fully offline workflow | Local Ollama support | No cloud LLM dependency</p>", unsafe_allow_html=True)
