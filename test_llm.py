from llm_rewriter import rewrite_policy

policy = "Purpose: This is a patch management policy."
gaps = ["Incident Response", "Compliance"]

output = rewrite_policy(policy, gaps)

print(output)
