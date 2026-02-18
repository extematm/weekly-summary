# Weekly Summary

A Python script that generates concise weekly reports for public GitHub repositories by fetching recent commits and summarizing them using a local AI model via Ollama.

## Features

- **Automated Commit Fetching**: Retrieves all commits from the last 7 days for a specified GitHub repository
- **AI-Powered Summarization**: Uses a local Ollama model to generate structured, informative summaries tailored for team management
- **Privacy-Focused**: Runs entirely locally with no external API dependencies (except GitHub's public API)
- **Customizable**: Easy to configure for different repositories and AI models
- **Concise Output**: Produces short, structured summaries highlighting progress, productivity, and key metrics

## Prerequisites

- **Python 3.11 or higher**
- **Ollama** installed and running locally ([Download Ollama](https://ollama.ai/))
- **AI Model**: At least one Ollama model pulled (e.g., `lfm2.5-thinking:latest`)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/extematm/weekly-summary.git
   cd weekly-summary
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and set up Ollama**:
   - Download and install Ollama from [ollama.ai](https://ollama.ai/)
   - Pull a model (replace `lfm2.5-thinking:latest` with your preferred model):
     ```bash
     ollama pull lfm2.5-thinking:latest
     ```
   - Start Ollama (if not running automatically):
     ```bash
     ollama serve
     ```

## Usage

1. **Configure the script**:
   Edit `summary.py` and update the following variables:
   - `GITHUB_REPO`: Set to your target repository (e.g., `"owner/repo-name"`)
   - `OLLAMA_MODEL`: Set to your installed Ollama model (e.g., `"lfm2.5-thinking:latest"`)

2. **Run the script**:
   ```bash
   python summary.py
   ```

3. **View the output**:
   The script will:
   - Fetch commits from the last week
   - Display raw commit messages
   - Generate and display an AI summary

## Example Output

```
Fetching last week's commits from extematm/weekly-summary...

Raw commit activity:
 - John Doe: Added new feature X
 - Jane Smith: Fixed bug in Y
 - John Doe: Updated documentation

Generating AI summary...

Weekly Summary:
Team made 3 commits this week, focusing on feature development and bug fixes.
Key achievements: Implemented feature X, resolved critical bug in Y.
Productivity: Steady progress with balanced commits across team members.
```

## Configuration

### GitHub Repository
Change the `GITHUB_REPO` variable to any public GitHub repository in the format `"owner/repo-name"`.

### AI Model
- Update `OLLAMA_MODEL` to match your pulled Ollama model
- The summary prompt is optimized for management-level insights, emphasizing progress and productivity
- Modify the `prompt` in `summarize_commits()` if you need different summary styles

### Date Range
The script fetches commits from the last 7 days. To change this, modify the `timedelta(days=7)` in `get_last_week_commits()`.

## Troubleshooting

- **Ollama connection error**: Ensure Ollama is running (`ollama serve`) and the model is pulled
- **GitHub API error**: Check that the repository exists and is public
- **Model not found**: Verify the model name in `OLLAMA_MODEL` matches `ollama list` output
- **Slow response**: First runs may be slower as the model loads; subsequent runs are faster

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source. See LICENSE file for details (if applicable).
