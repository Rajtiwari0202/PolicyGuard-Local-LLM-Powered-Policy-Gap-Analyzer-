# PolicyGuard

PolicyGuard is an offline cybersecurity policy gap analyzer. It reviews organizational policy text against a NIST-style control baseline, identifies missing governance controls, ranks severity, calculates a compliance score, and generates an improved policy draft through a local LLM workflow.

The project is designed for privacy-sensitive environments where internal policy documents should not be sent to cloud AI services.

## Product Highlights

- Streamlit executive dashboard with readiness status, compliance score, and control coverage.
- Gap register with severity, evidence snippets, recommendations, and missing-policy indicators.
- NIST-style function mapping across Govern, Identify, Protect, Detect, Respond, and Recover.
- Local Ollama-compatible LLM rewriting for improved policy generation.
- Deterministic offline fallback when Ollama is unavailable, so demos still work reliably.
- CLI mode for generating reports outside the dashboard.
- Pytest coverage for scoring and fallback rewrite behavior.

## Tech Stack

| Area | Tools |
| --- | --- |
| UI | Streamlit |
| Analysis | Python rule engine |
| Local AI | Ollama-compatible API |
| Reports | TXT and JSON exports |
| Tests | pytest |

## Repository Structure

```text
PolicyGuard/
|-- app.py              # Streamlit dashboard
|-- main.py             # CLI report generator
|-- gap_detector.py     # Control library and scoring engine
|-- llm_rewriter.py     # Ollama + fallback rewrite workflow
|-- policy_reader.py    # Policy file reader
|-- sample_policy.txt   # Demo policy
|-- test_llm.py         # pytest suite
|-- requirements.txt
|-- outputs/
`-- README.md
```

## Local Setup

```powershell
git clone https://github.com/Rajtiwari0202/PolicyGuard-Local-LLM-Powered-Policy-Gap-Analyzer-.git
cd PolicyGuard-Local-LLM-Powered-Policy-Gap-Analyzer-
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Optional Ollama Setup

PolicyGuard works without Ollama because it includes a deterministic fallback. To use a real local model:

```powershell
ollama pull llama3
ollama serve
```

Optional environment variables:

```powershell
$env:OLLAMA_URL="http://localhost:11434/api/generate"
$env:OLLAMA_MODEL="llama3"
$env:OLLAMA_TIMEOUT_SECONDS="8"
```

## CLI Usage

```powershell
py main.py --policy sample_policy.txt --domain "Patch Management"
```

Generated outputs:

```text
outputs/analysis.json
outputs/compliance_score.txt
outputs/gaps_report.txt
outputs/improved_policy.txt
outputs/final_report.txt
```

## Testing

```powershell
pytest
```

## Engineering Notes

- Weighted controls produce a more useful compliance score than plain keyword matching.
- Severity ranking helps translate policy gaps into a remediation plan.
- The local LLM path supports privacy-sensitive workflows.
- The offline fallback keeps demos deterministic and reliable.
- CLI and dashboard modes share the same analysis engine.

## Portfolio Context

PolicyGuard appears in my portfolio as a security AI project focused on:

- Local LLM workflows
- Cybersecurity policy review
- Compliance scoring
- Gap remediation reports
- HackIITK 2025 finalist work

## Author

Raj Tiwari  
GitHub: https://github.com/Rajtiwari0202  
Portfolio: https://rajtiwari0202.github.io/my_portfolio/
