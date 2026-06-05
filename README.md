# PolicyGuard - Local LLM Powered Policy Gap Analyzer

PolicyGuard is an offline cybersecurity policy analysis dashboard. It reviews organizational policy text against a NIST-style control baseline, identifies missing governance controls, ranks severity, calculates a compliance score, and generates an improved policy draft using a local LLM workflow.

The project is built for privacy-sensitive environments where policy documents cannot be sent to cloud AI services.

## Portfolio Highlights

- Executive Streamlit dashboard with compliance score, readiness status, control coverage, gap register, and exports.
- Weighted policy analysis engine with NIST function mapping, severity ranking, recommendations, evidence snippets, and vague-language flags.
- Local Ollama support for LLM rewriting.
- Deterministic offline fallback writer when Ollama is not running, so the demo always works.
- CLI mode that writes gap report, score, analysis JSON, improved policy, and final report.
- Pytest coverage for gap detection, scoring, and offline rewrite fallback.

## Tech Stack

| Layer | Tools |
| --- | --- |
| UI | Streamlit |
| Analysis | Python rule engine |
| Local LLM | Ollama-compatible API |
| Reports | TXT and JSON exports |
| Tests | pytest |

## How It Works

1. User uploads, pastes, or selects a sample policy.
2. PolicyGuard checks the policy against a control library covering Govern, Identify, Protect, Detect, Respond, and Recover functions.
3. The app calculates weighted compliance and prioritizes missing controls.
4. The rewrite module asks Ollama for a revised policy when available.
5. If Ollama is unavailable, PolicyGuard still produces an audit-ready fallback policy and 30/60/90 remediation roadmap.
6. The user can download gap reports, analysis JSON, and improved policy drafts.

## Run Locally

```powershell
cd F:\PolicyGuard
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

PolicyGuard works without Ollama because it includes a deterministic offline fallback. To use a real local LLM:

```powershell
ollama pull llama3
ollama serve
```

Optional environment variables:

```powershell
$env:OLLAMA_URL="http://localhost:11434/api/generate"
$env:OLLAMA_MODEL="llama3"
```

## CLI Usage

```powershell
py main.py --policy sample_policy.txt --domain "Patch Management"
```

Generated files:

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

## Resume Bullets

- Built an offline cybersecurity policy analyzer that benchmarks policy documents against a NIST-style control baseline and calculates weighted compliance scores.
- Designed a Streamlit executive dashboard with gap severity ranking, evidence snippets, vague-language detection, remediation guidance, and downloadable reports.
- Integrated Ollama-compatible local LLM rewriting with a deterministic fallback generator, ensuring the product demo works even without a running model.
- Added CLI reporting and pytest coverage for gap detection, scoring consistency, and offline rewrite behavior.

## Interview Talking Points

- Why local LLM execution matters for policy/privacy workloads.
- How weighted controls produce a more meaningful score than simple keyword matching.
- How deterministic fallback keeps demos reliable while preserving the local AI story.
- How severity ranking supports remediation planning and executive reporting.

## Project Structure

```text
PolicyGuard/
├── app.py              # Streamlit dashboard
├── main.py             # CLI report generator
├── gap_detector.py     # Control library and scoring engine
├── llm_rewriter.py     # Ollama + fallback rewrite workflow
├── policy_reader.py    # File reader
├── sample_policy.txt   # Demo policy
├── test_llm.py         # pytest suite
├── requirements.txt
└── outputs/
```

## Author

Raj Tiwari  
GitHub: https://github.com/Rajtiwari0202
