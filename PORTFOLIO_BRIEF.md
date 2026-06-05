# PolicyGuard Portfolio Brief

## One-Line Pitch

PolicyGuard is an offline cybersecurity policy analyzer that scores policy completeness, identifies NIST-style control gaps, ranks remediation severity, and generates an improved policy draft using local LLM workflows.

## Best Resume Bullets

- Built an offline Streamlit dashboard for cybersecurity policy gap analysis with weighted compliance scoring, NIST-style control mapping, severity ranking, and report exports.
- Implemented a Python control-analysis engine that detects missing governance, access control, risk, monitoring, incident response, recovery, and compliance sections with evidence snippets and remediation guidance.
- Integrated Ollama-compatible local LLM rewriting with a deterministic fallback policy generator, making the demo reliable without cloud APIs or external credentials.
- Added CLI reporting and pytest coverage for gap detection, scoring consistency, and offline rewrite behavior.

## Demo Script

1. Open the Streamlit app.
2. Select the sample Patch Management policy.
3. Show the compliance score, missing controls, and critical gap count.
4. Open the Gap Register tab and explain severity-based remediation.
5. Generate the improved policy and point out the 30/60/90 roadmap.
6. Open Exports and show downloadable gap report and JSON analysis.

## Interview Talking Points

- Privacy-sensitive policy analysis should avoid cloud LLMs by default.
- Weighted scoring is more realistic than checking whether section names exist.
- Local LLM output is useful, but deterministic fallback keeps the product reliable.
- Severity and NIST function mapping make findings actionable for executives and auditors.

## Tech Stack

- Python
- Streamlit
- Ollama-compatible local LLM API
- Pytest
- TXT/JSON reports
