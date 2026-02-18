import requests
from datetime import datetime, timedelta, timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re
import os

# -------------------------
# CONFIG
# -------------------------
GITHUB_REPO = "extematm/weekly-summary"  # Change to any public repo
OLLAMA_MODEL = "qwen:7b"  # Change to your installed Ollama model
OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API endpoint /generate or /chat 
# HELPER FUNCTIONS
# -------------------------

def get_last_week_commits(repo):
    """
    Fetch commits from the last week for a given GitHub repo.
    """
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"since": one_week_ago.isoformat() + "Z"}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code}")
    
    commits = response.json()
    norway_offset = timedelta(hours=1)  # Norway winter time UTC+1
    commit_messages = []
    for commit in commits:
        date_str = commit['commit']['author']['date']
        # Parse UTC datetime
        dt_utc = datetime.fromisoformat(date_str[:-1]).replace(tzinfo=timezone.utc)
        # Convert to Norway time (simple offset for winter)
        dt_norway = dt_utc + norway_offset
        # Format human readable
        human_date = dt_norway.strftime('%Y-%m-%d %H:%M:%S')
        message = commit['commit']['message']
        commit_messages.append(f"- {human_date}: {message}")
    
    return "\n".join(commit_messages) if commit_messages else "No commits in the last week."

def summarize_commits(commit_text):
    """
    Summarize commit messages using Ollama.
    """
    prompt = f"Please answer ONLY in English. Do not use any other language. Make the summary very structured for management (management does not understand code jargon, so keep it simple) to understand the last weeks progress:\n\n{commit_text}"
    
    payload = {
        #"think": False,
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code}")
    data = response.json()
    summary = data['response']
    return summary

def save_summary_pdf(summary_text, raw_commits, filename_hint="summary"):
    """
    Save the summary as a PDF report with a filename like date_smallsummaryname.pdf
    The summary appears first, followed by the raw commits list.
    """
    from datetime import datetime
    # Clean filename_hint to be filesystem safe and short
    safe_hint = re.sub(r'[^a-zA-Z0-9]+', '_', filename_hint)[:20]
    date_str = datetime.now().strftime("%Y%m%d")
    # Ensure 'reports' directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"{date_str}_{safe_hint}.pdf")
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    y = height - 40
    c.drawString(40, y, "Summary:")
    y -= 24
    c.setFont("Helvetica", 12)
    for line in summary_text.splitlines():
        c.drawString(40, y, line)
        y -= 18
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40
    y -= 12
    c.setFont("Helvetica-Bold", 14)
    if y < 60:
        c.showPage()
        y = height - 40
    c.drawString(40, y, "Raw Commits:")
    y -= 24
    c.setFont("Helvetica", 12)
    for line in raw_commits.splitlines():
        c.drawString(40, y, line)
        y -= 18
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40
    c.save()
    print(f"PDF report saved as: {filename}")

# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    print(f"Fetching last week's commits from {GITHUB_REPO}...\n")
    commits = get_last_week_commits(GITHUB_REPO)
    print("Raw commit activity:\n", commits, "\n")
    print("----------------------------------------------\n")
    summary = summarize_commits(commits)
    print("Commit Summary. \n", summary)
    save_summary_pdf(summary, commits)

