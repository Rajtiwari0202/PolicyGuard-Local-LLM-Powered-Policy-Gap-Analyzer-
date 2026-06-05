from gap_detector import analyze_policy, find_gaps
from llm_rewriter import rewrite_policy


def test_gap_detection_identifies_missing_controls():
    policy = "Purpose: Patch systems. Scope: Laptops and servers."
    gaps = find_gaps(policy)

    assert "Incident Response" in gaps
    assert "Access Control" in gaps


def test_analysis_score_and_summary_are_consistent():
    policy = "Purpose: Security policy. Scope: All systems. Compliance: Reviewed annually."
    analysis = analyze_policy(policy, "ISMS")

    assert analysis["score"] > 0
    assert analysis["summary"]["present"] + analysis["summary"]["missing"] == analysis["summary"]["total_controls"]


def test_rewriter_returns_fallback_without_ollama(monkeypatch):
    import llm_rewriter

    def fail_post(*args, **kwargs):
        raise llm_rewriter.requests.exceptions.ConnectionError("offline")

    monkeypatch.setattr(llm_rewriter.requests, "post", fail_post)
    output = rewrite_policy("Purpose: Protect systems.", ["Incident Response"], "Patch Management")

    assert "Improved Policy" in output
    assert "Incident Response" in output
