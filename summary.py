import requests
from datetime import datetime, timedelta, timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re
import os
import textwrap

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
    prompt = f"Please answer ONLY in English. Do not use any other language. Make the summary very structured for management (management does not understand code or special coding language, keep it easy to understand). Summarize last weeks progress of all commits without removing important informations. Also as last add a short text describing the weeks progress with a specified list for quick numbers acheived this week:\n\n{commit_text}"
    
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
    Save the summary as a PDF report with a filename like date_time_smallsummaryname.pdf
    The summary appears first, followed by the raw commits list.
    Wrap long lines to fit the page width. Add structure and beauty.
    """
    from datetime import datetime
    # Clean filename_hint to be filesystem safe and short
    safe_hint = re.sub(r'[^a-zA-Z0-9]+', '_', filename_hint)[:20]
    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    # Ensure 'reports' directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"{date_str}_{safe_hint}.pdf")
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40
    max_line_width = int((width - 2 * margin) // 7)  # Approx chars per line for Helvetica 12
    y = height - margin
    page_num = 1
    def draw_footer(page_num):
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width // 2, margin // 2, f"Page {page_num}")

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width // 2, y, "Weekly Project Summary Report")
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawCentredString(width // 2, y, f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20
    c.line(margin, y, width - margin, y)
    y -= 30

    # Summary Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Summary:")
    y -= 22
    c.setFont("Helvetica", 12)
    for line in summary_text.splitlines():
        for wrapped in textwrap.wrap(line, width=max_line_width):
            c.drawString(margin, y, wrapped)
            y -= 16
            if y < margin + 40:
                draw_footer(page_num)
                c.showPage()
                page_num += 1
                y = height - margin
                c.setFont("Helvetica", 12)
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    if y < margin + 60:
        draw_footer(page_num)
        c.showPage()
        page_num += 1
        y = height - margin
    c.drawString(margin, y, "Raw Commits:")
    y -= 22
    c.setFont("Helvetica", 12)
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(margin, y + 10, width - margin, y + 10)
    y -= 10
    for line in raw_commits.splitlines():
        for wrapped in textwrap.wrap(line, width=max_line_width):
            c.drawString(margin, y, wrapped)
            y -= 16
            if y < margin + 40:
                draw_footer(page_num)
                c.showPage()
                page_num += 1
                y = height - margin
                c.setFont("Helvetica", 12)
    draw_footer(page_num)
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

