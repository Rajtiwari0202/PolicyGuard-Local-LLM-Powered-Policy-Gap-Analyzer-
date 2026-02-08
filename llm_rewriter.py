import requests

def rewrite_policy(policy_text, gaps):
    prompt = f"""
You are a cybersecurity policy expert.

Policy Text:
{policy_text}

Missing Sections:
{gaps}

Rewrite the policy by adding missing sections aligned
with NIST Cybersecurity Framework.
Also provide a short roadmap for improvement.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 250
            }
        }
    )

    return response.json()["response"]
