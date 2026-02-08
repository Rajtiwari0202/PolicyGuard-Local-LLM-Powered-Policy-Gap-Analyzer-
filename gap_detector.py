NIST_SECTIONS = [
    "Purpose",
    "Scope",
    "Roles and Responsibilities",
    "Access Control",
    "Incident Response",
    "Risk Management",
    "Logging and Monitoring",
    "Compliance"
]

def find_gaps(policy_text):
    missing = []
    for section in NIST_SECTIONS:
        if section.lower() not in policy_text.lower():
            missing.append(section)
    return missing
