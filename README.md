
# LIVE DEMO - https://cross-culture-semantic-distortion-detector-k6yp4y4xxnggy7rzeeh.streamlit.app/
# Cross-Culture Semantic Distortion Detector

A Streamlit app that rewrites text into canonical English, compares how meaning changes, and flags possible semantic distortion.

The app uses:
- `Ollama` for rewrite generation
- `SentenceTransformers` for embeddings
- `scikit-learn` for similarity scoring
- `Streamlit` for the interface

## Features

- Analyze text with multiple rewrite modes:
  - `Simple`
  - `Literal`
  - `Culturally Neutral`
- Compare modes side by side
- Score each rewrite using:
  - semantic similarity
  - token overlap
  - entity preservation
  - length ratio
- Highlight changed words between original and rewritten text
- Save recent analysis history locally in SQLite
- Run an in-app health check for Ollama and embedding/scoring readiness

## Project Structure

```text
sematic/
├── app.py
├── config.py
├── requirements.txt
├── services/
│   ├── embedding.py
│   ├── history.py
│   ├── llm.py
│   ├── reporting.py
│   ├── schemas.py
│   └── scoring.py
```

## Requirements

- Python `3.11+`
- [Ollama](https://ollama.com/) installed and running
- Ollama model: `gpt-oss:120b-cloud`

## Setup

```powershell
cd C:\Users\Vishal\Documents\projects\sematic
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

Start Ollama first, then launch the app:

```powershell
streamlit run app.py
```

Open:

- [http://127.0.0.1:8501](http://127.0.0.1:8501)

## Streamlit Cloud Deployment

This app can be deployed to Streamlit Community Cloud if it uses a reachable Ollama API.

### Easiest option: Ollama Cloud API

Ollama provides a cloud API at:

`https://ollama.com/api`

For direct access, the app needs:
- `OLLAMA_BASE_URL = "https://ollama.com/api"`
- `OLLAMA_API_KEY = "your_ollama_api_key"`

You can keep using local Ollama during development and switch to Ollama Cloud for deployment.

The app supports:
- local environment variable `OLLAMA_BASE_URL`
- local environment variable `OLLAMA_API_KEY`
- Streamlit secrets `OLLAMA_BASE_URL`
- Streamlit secrets `OLLAMA_API_KEY`

### Deploy Steps

1. Push this project to GitHub.
2. Create an Ollama API key from your Ollama account.
3. In Streamlit Community Cloud, deploy the repo and choose `app.py` as the entrypoint.
4. In **Advanced settings**, add a secret like:

```toml
OLLAMA_BASE_URL = "https://ollama.com/api"
OLLAMA_API_KEY = "your_ollama_api_key"
```

5. Deploy the app.

### Local Secrets Example

There is an example file at [.streamlit/secrets.toml.example](C:\Users\Vishal\Documents\projects\sematic\.streamlit\secrets.toml.example).

For local testing with secrets, create `.streamlit/secrets.toml` and add:

```toml
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
```

Do not commit your real `secrets.toml`.

## How It Works

1. The app sends input text to Ollama and asks for a structured rewrite.
2. It generates embeddings for the original and rewritten text.
3. It calculates similarity and preservation metrics.
4. It ranks the selected rewrite modes by overall score.
5. It saves the result to a local history database.

## Notes

- The file `analysis_history.db` is local app data and should not usually be committed.
- The first embedding load can take longer because the transformer model may need to initialize.
- If the app reports a backend problem, use the `Run Health Check` button in the sidebar.

## Suggested GitHub Push Steps

This folder is not initialized as a Git repository yet. A typical flow is:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Future Improvements

- Sentence-level distortion scoring
- Exportable reports
- Better visual charts
- More rewrite modes
- Stronger contradiction or entailment checks
