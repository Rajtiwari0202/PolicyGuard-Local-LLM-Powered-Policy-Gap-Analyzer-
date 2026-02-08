import streamlit as st
from gap_detector import find_gaps
from llm_rewriter import rewrite_policy

st.set_page_config(page_title="PolicyGuard", layout="wide")

# Title
st.title("🔐 PolicyGuard - Offline Policy Gap Analyzer (PS1)")
st.write("Upload a cybersecurity policy document and get gap analysis + improved policy draft.")

st.markdown("---")

# Upload Policy File
uploaded_file = st.file_uploader("📄 Upload Policy Text File", type=["txt"])

if uploaded_file is not None:
    # Read file content
    policy_text = uploaded_file.read().decode("utf-8")

    st.subheader("✅ Uploaded Policy Content")
    st.text_area("Policy Text", policy_text, height=200)

    # Gap Detection
    st.markdown("---")
    st.subheader("🔍 Step 1: Gap Detection")

    gaps = find_gaps(policy_text)

    if len(gaps) == 0:
        st.success("🎉 No major gaps found. Policy is well aligned!")
    else:
        st.warning("Missing Sections Found:")
        for g in gaps:
            st.write("❌", g)

    # Compliance Score
    total_sections = 8
    found_sections = total_sections - len(gaps)
    score = (found_sections / total_sections) * 100

    st.info(f"📊 Compliance Score: **{score:.2f}%**")

    # Generate Improved Policy Button
    st.markdown("---")
    st.subheader("🛠 Step 2: Generate Improved Policy")

    if st.button("Generate Improved Policy using Offline LLM"):
        with st.spinner("Generating improved policy... Please wait"):
            improved_policy = rewrite_policy(policy_text, gaps)

        st.success("✅ Improved Policy Generated!")

        st.text_area("Improved Policy Output", improved_policy, height=300)

        # Download Option
        st.download_button(
            label="⬇ Download Improved Policy",
            data=improved_policy,
            file_name="improved_policy.txt",
            mime="text/plain"
        )
