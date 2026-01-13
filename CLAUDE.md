# BUD - Budget Dashboard

## Project Overview
A Streamlit app that connects to YNAB (You Need A Budget) API to provide spending insights, anomaly detection, and budget monitoring.

## Instructions
- Always use polars over pandas
- Keep things simple
- After each concept of work, git commit it and push it
- Always use the `uv` package manager
- Make logical tests and always test
- Always review for security, especially with bank data and api keys
- Always use git and also use it to understand the project history

## Architecture
- **Frontend**: Streamlit (app.py + pages/)
- **Data**: SQLite cache at `data/cache.db`
- **API**: YNAB Python SDK with rate limiting (200 req/hour)
- **Analysis**: Polars for data processing

## Key Files
```
app.py                    # Main entry point, sidebar, navigation
pages/                    # Streamlit pages (Dashboard, Spending, Alerts, etc.)
src/api/ynab_client.py    # YNAB API wrapper with rate limiting
src/cache/database.py     # SQLite operations
src/cache/sync.py         # Delta sync logic
src/alerts/               # Anomaly detection algorithms
src/utils/formatters.py   # Currency/date formatting (milliunits -> dollars)
```

## Configuration
- API token: `.streamlit/secrets.toml` (gitignored)
- Alert thresholds: Also in secrets.toml under `[alert_thresholds]`

## Development
```bash
uv sync                           # Install dependencies
uv run streamlit run app.py       # Run the app
uv run pytest                     # Run tests
```

## Data Notes
- YNAB stores amounts in "milliunits" (divide by 1000 for dollars)
- Negative amounts = outflows (spending)
- Database uses delta sync via `last_knowledge_of_server` to minimize API calls
