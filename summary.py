import requests
from datetime import datetime, timedelta, timezone

# -------------------------
# CONFIG
# -------------------------
GITHUB_REPO = "extematm/weekly-summary"  # Change to any public repo
OLLAMA_MODEL = "lfm2.5-thinking:latest"  # Change to your installed Ollama model
OLLAMA_URL = "http://localhost:11434/api/generate"

# -------------------------
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
    commit_messages = [
        f"- {commit['commit']['author']['name']}: {commit['commit']['message']}"
        for commit in commits
    ]
    
    return "\n".join(commit_messages) if commit_messages else "No commits in the last week."

def summarize_commits(commit_text):
    """
    Summarize commit messages using Ollama.
    """
    prompt = f"Summarize the following GitHub commit activity for a weekly update, keep it very short, highly informative with numbers if they are important. The target audience is the team management who are interested in progress and productivity and this response shall provide a stomach feeling of the overall progress/security. Write no more then two sentence paragraphs and keep it very structured for simple and quick reading:\n\n{commit_text}"
    
    payload = {
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
    print("Raw commit activity:\n", commits, "\n")
    
    print("Generating AI summary...\n")
    summary = summarize_commits(commits)
    print("Weekly Summary:\n", summary)
