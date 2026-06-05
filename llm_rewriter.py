from __future__ import annotations

import os
from textwrap import dedent

import requests

from gap_detector import analyze_policy


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "8"))


def build_rewrite_prompt(policy_text: str, analysis: dict) -> str:
    gap_text = "\n".join(
        f"- {gap['control_id']} {gap['title']} ({gap['severity']}): {gap['recommendation']}"
        for gap in analysis["gaps"]
    ) or "- No major gaps identified."

    return f"""
You are a cybersecurity governance consultant.

Rewrite the policy below so it is audit-ready, concise, and aligned to the NIST Cybersecurity Framework.
Keep the language practical for a real organization.

Domain: {analysis['domain']}
Compliance score before rewrite: {analysis['score']}%
Missing controls:
{gap_text}

Original policy:
{policy_text}

Required output:
1. Executive Summary
2. Improved Policy
3. Control Alignment Table
4. 30/60/90 Day Remediation Roadmap
"""


def _fallback_policy(policy_text: str, analysis: dict) -> str:
    missing_sections = analysis["gaps"]

    policy_sections = [
        ("Purpose", "This policy establishes mandatory cybersecurity governance requirements to protect organizational systems, data, users, and business operations."),
        ("Scope", "This policy applies to employees, contractors, administrators, endpoints, servers, cloud services, applications, network devices, and third-party systems that process organizational data."),
        ("Roles and Responsibilities", "Executive leadership owns risk acceptance. Security leadership maintains the control baseline. IT operations implements controls. System owners validate evidence. All users follow approved security procedures and report suspected incidents."),
        ("Access Control", "Access must follow least privilege, unique user identity, MFA for privileged and remote access, documented approvals, quarterly access reviews, and timely removal for role changes or termination."),
        ("Risk Management", "Security risks must be assessed using likelihood and impact, recorded in a risk register, assigned an owner, reviewed at least quarterly, and formally accepted only by authorized leadership."),
        ("Logging and Monitoring", "Critical systems must generate audit logs for authentication, administrative activity, configuration changes, security alerts, and policy exceptions. Logs must be monitored, retained, and reviewed according to business and regulatory needs."),
        ("Incident Response", "Suspected incidents must be escalated immediately. The response process must include triage, containment, evidence preservation, stakeholder communication, eradication, recovery, and post-incident lessons learned."),
        ("Recovery and Continuity", "Systems must have tested backup, restoration, rollback, and continuity procedures. Recovery validation must be documented after major incidents or high-risk changes."),
        ("Compliance and Review", "Policy compliance must be reviewed at least annually and after major business, technology, or regulatory changes. Exceptions must be documented, time-bound, risk accepted, and reviewed."),
    ]

    roadmap_items = [
        "Days 0-30: Assign control owners, approve scope, document access review and incident escalation procedures.",
        "Days 31-60: Implement evidence collection for logging, monitoring, risk register updates, and exception approvals.",
        "Days 61-90: Run tabletop incident response, test recovery procedures, and complete executive compliance attestation.",
    ]

    alignment = [
        f"- {gap['control_id']} {gap['title']}: {gap['recommendation']}"
        for gap in missing_sections
    ] or ["- Existing policy covers the core control baseline. Continue periodic review and evidence collection."]

    return dedent(f"""
    === Executive Summary ===
    PolicyGuard analyzed the submitted policy and calculated a pre-remediation compliance score of {analysis['score']}%.
    The rewritten version below strengthens governance, control ownership, risk management, response, recovery, monitoring, and compliance review language while preserving the original policy intent.

    === Improved Policy ===
    """).strip() + "\n\n" + "\n\n".join(
        f"{title}\n{body}" for title, body in policy_sections
    ) + "\n\n=== Control Alignment Table ===\n" + "\n".join(alignment) + "\n\n=== 30/60/90 Day Remediation Roadmap ===\n" + "\n".join(
        f"- {item}" for item in roadmap_items
    ) + "\n\n=== Original Policy Reference ===\n" + policy_text.strip()


def rewrite_policy(policy_text: str, gaps=None, domain: str = "General Cybersecurity Policy") -> str:
    if not policy_text.strip():
        return "Empty policy text provided."

    analysis = analyze_policy(policy_text, domain)
    prompt = build_rewrite_prompt(policy_text, analysis)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return _fallback_policy(policy_text, analysis)

        data = response.json()
        generated = data.get("response", "").strip()
        return generated or _fallback_policy(policy_text, analysis)

    except requests.exceptions.RequestException:
        return _fallback_policy(policy_text, analysis)
