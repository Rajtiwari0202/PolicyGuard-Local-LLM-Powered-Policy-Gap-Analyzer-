from policy_reader import read_policy
from gap_detector import find_gaps
from llm_rewriter import rewrite_policy

# Input policy file
file_path = "sample_policy.txt"

print("\nReading Policy Document...\n")
policy_text = read_policy(file_path)

print("Finding Gaps...\n")
gaps = find_gaps(policy_text)

print("Missing Sections:")
print(gaps)

# -------------------------------
# ✅ Upgrade 1: Save Gap Report File
# -------------------------------
with open("outputs/gaps_report.txt", "w") as f:
    f.write("Missing Sections Found:\n\n")
    for gap in gaps:
        f.write("- " + gap + "\n")

print("\n✅ Gap Report Saved Successfully!")
print("File: outputs/gaps_report.txt")

# -------------------------------
# ✅ Upgrade 2: Compliance Score
# -------------------------------
total_sections = 8
found_sections = total_sections - len(gaps)
score = (found_sections / total_sections) * 100

print(f"\nPolicy Compliance Score: {score:.2f}%")

with open("outputs/compliance_score.txt", "w") as f:
    f.write(f"Policy Compliance Score: {score:.2f}%\n")

print("✅ Compliance Score Saved Successfully!")
print("File: outputs/compliance_score.txt")

# -------------------------------
# Generate Improved Policy using Offline LLM
# -------------------------------
print("\nGenerating Improved Policy using Offline LLM...\n")
improved_policy = rewrite_policy(policy_text, gaps)

# -------------------------------
# Save Improved Policy Output
# -------------------------------
with open("outputs/improved_policy.txt", "w") as f:
    f.write(improved_policy)

print("\n✅ Improved Policy Saved Successfully!")
print("File: outputs/improved_policy.txt")

# -------------------------------
# ✅ Upgrade 3: Save Full Final Report (Optional)
# -------------------------------
with open("outputs/final_report.txt", "w") as f:
    f.write("=== POLICY GAP ANALYSIS REPORT ===\n\n")
    f.write("Missing Sections:\n")
    for gap in gaps:
        f.write("- " + gap + "\n")

    f.write("\n-----------------------------\n")
    f.write(f"Compliance Score: {score:.2f}%\n")
    f.write("\n-----------------------------\n")
    f.write("Improved Policy Draft:\n\n")
    f.write(improved_policy)

print("\n✅ Full Final Report Saved Successfully!")
print("File: outputs/final_report.txt")
