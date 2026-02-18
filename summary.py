import requests
from datetime import datetime, timedelta
import openai

# -------------------------
# CONFIG
# -------------------------
GITHUB_REPO = "octocat/Hello-World"  # Change to any public repo
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Set your API key

# -------------------------
# HELPER FUNCTIONS
# -------------------------

def get_last_week_commits(repo):
    """
    Fetch commits from the last week for a given GitHub repo.
    """
    one_week_ago = datetime.utcnow() - timedelta(days=7)
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
    Summarize commit messages using OpenAI.
    """
    openai.api_key = OPENAI_API_KEY
    prompt = f"Summarize the following GitHub commit activity for a weekly update:\n\n{commit_text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    summary = response['choices'][0]['message']['content']
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
