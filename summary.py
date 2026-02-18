import requests
from datetime import datetime, timedelta, timezone

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

# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    print(f"Fetching last week's commits from {GITHUB_REPO}...\n")
    commits = get_last_week_commits(GITHUB_REPO)
    #print("Raw commit activity:\n", commits, "\n")
    
    #print("Last weeks commits/changes:\n")
    summary = summarize_commits(commits)
    print(summary)
