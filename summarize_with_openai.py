import os
from openai import OpenAI

with open("activity.txt", "r", encoding="utf-8") as f:
    activity_text = f.read()

prompt = (
    "You are generating a weekly engineering summary for leadership. "
    "Summarize the previous week of GitHub activity. Include: "
    "(1) major completed work, "
    "(2) in-progress or changing areas, "
    "(3) notable risks/blockers/security-relevant items. "
    "Keep it under 140 words, clear and factual.\n\n"
    f"Repository: {os.environ['GITHUB_REPOSITORY']}\n\n"
    f"{activity_text}"
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt,
    temperature=0.3
)
summary = response.output_text.strip()

print("--- AI Weekly Summary ---")
print(summary)
with open("weekly_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)
