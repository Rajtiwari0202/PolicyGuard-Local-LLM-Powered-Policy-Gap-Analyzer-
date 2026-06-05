from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class Control:
    control_id: str
    title: str
    nist_function: str
    severity: str
    weight: int
    keywords: tuple[str, ...]
    recommendation: str


CONTROL_LIBRARY: tuple[Control, ...] = (
    Control(
        "GV-01",
        "Purpose",
        "Govern",
        "Medium",
        8,
        ("purpose", "objective", "intent", "goal"),
        "State the policy objective and business/security outcomes it supports.",
    ),
    Control(
        "GV-02",
        "Scope",
        "Govern",
        "Medium",
        8,
        ("scope", "applies to", "covered systems", "in scope"),
        "Define users, systems, applications, data, and locations covered by the policy.",
    ),
    Control(
        "GV-03",
        "Roles and Responsibilities",
        "Govern",
        "High",
        12,
        ("roles", "responsibilities", "owner", "accountable", "raci", "approver"),
        "Assign accountable owners, approvers, operators, reviewers, and escalation contacts.",
    ),
    Control(
        "PR-01",
        "Access Control",
        "Protect",
        "High",
        14,
        ("access control", "least privilege", "mfa", "multi-factor", "permission", "authorization"),
        "Specify least privilege, MFA, administrative access, reviews, and joiner/mover/leaver handling.",
    ),
    Control(
        "ID-01",
        "Risk Management",
        "Identify",
        "High",
        14,
        ("risk", "risk assessment", "impact", "likelihood", "risk register", "threat"),
        "Connect the policy to risk assessment, risk acceptance, exceptions, and review cadence.",
    ),
    Control(
        "DE-01",
        "Logging and Monitoring",
        "Detect",
        "Medium",
        12,
        ("logging", "monitoring", "audit log", "event", "alert", "siem"),
        "Define monitoring, logging retention, alert triage, and evidence requirements.",
    ),
    Control(
        "RS-01",
        "Incident Response",
        "Respond",
        "Critical",
        14,
        ("incident response", "incident", "breach", "escalation", "containment", "rollback"),
        "Describe escalation, containment, communications, rollback, and post-incident review.",
    ),
    Control(
        "RC-01",
        "Recovery and Continuity",
        "Recover",
        "High",
        10,
        ("recovery", "backup", "business continuity", "restore", "rollback", "resilience"),
        "Add recovery expectations, rollback criteria, continuity steps, and restoration validation.",
    ),
    Control(
        "GV-04",
        "Compliance and Review",
        "Govern",
        "High",
        10,
        ("compliance", "audit", "review", "regulatory", "exception", "attestation"),
        "Define compliance obligations, audit evidence, exception handling, and periodic review.",
    ),
)

VAGUE_TERMS = (
    "as needed",
    "when possible",
    "best effort",
    "periodically",
    "regularly",
    "may",
    "should",
)


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _find_evidence(policy_text: str, keywords: Iterable[str]) -> str:
    lines = [line.strip() for line in policy_text.splitlines() if line.strip()]
    lowered = [(line, line.lower()) for line in lines]

    for keyword in keywords:
        keyword = keyword.lower()
        for original, normalized in lowered:
            if keyword in normalized:
                return original[:220]

    return ""


def analyze_policy(policy_text: str, domain: str = "General Cybersecurity Policy") -> dict:
    normalized = normalize_text(policy_text)
    present = []
    gaps = []

    for control in CONTROL_LIBRARY:
        evidence = _find_evidence(policy_text, control.keywords)
        control_payload = {
            **asdict(control),
            "evidence": evidence,
            "status": "Present" if evidence else "Missing",
        }

        if evidence:
            present.append(control_payload)
        else:
            gaps.append(control_payload)

    total_weight = sum(control.weight for control in CONTROL_LIBRARY)
    earned_weight = sum(item["weight"] for item in present)
    score = round((earned_weight / total_weight) * 100, 1) if total_weight else 0

    vague_findings = [
        term for term in VAGUE_TERMS
        if term in normalized
    ]

    if score >= 82:
        readiness = "Strong"
    elif score >= 62:
        readiness = "Moderate"
    elif score >= 40:
        readiness = "Needs Work"
    else:
        readiness = "High Risk"

    return {
        "domain": domain,
        "score": score,
        "readiness": readiness,
        "present_controls": present,
        "gaps": gaps,
        "vague_findings": vague_findings,
        "summary": {
            "total_controls": len(CONTROL_LIBRARY),
            "present": len(present),
            "missing": len(gaps),
            "critical_gaps": sum(1 for gap in gaps if gap["severity"] == "Critical"),
            "high_gaps": sum(1 for gap in gaps if gap["severity"] == "High"),
        },
    }


def find_gaps(policy_text: str) -> list[str]:
    """Backward-compatible helper used by the original CLI/UI."""
    return [gap["title"] for gap in analyze_policy(policy_text)["gaps"]]


def build_gap_report(analysis: dict) -> str:
    lines = [
        "POLICYGUARD GAP ANALYSIS REPORT",
        "",
        f"Domain: {analysis['domain']}",
        f"Compliance Score: {analysis['score']}%",
        f"Readiness: {analysis['readiness']}",
        "",
        "Missing Controls:",
    ]

    if not analysis["gaps"]:
        lines.append("- No missing controls detected.")
    else:
        for gap in analysis["gaps"]:
            lines.append(
                f"- [{gap['severity']}] {gap['control_id']} {gap['title']} "
                f"({gap['nist_function']}): {gap['recommendation']}"
            )

    lines.extend(["", "Present Controls:"])
    for control in analysis["present_controls"]:
        lines.append(f"- {control['control_id']} {control['title']}: {control['evidence']}")

    if analysis["vague_findings"]:
        lines.extend(["", "Vague Language Flags:"])
        for term in analysis["vague_findings"]:
            lines.append(f"- Replace vague phrase: '{term}'")

    return "\n".join(lines)
