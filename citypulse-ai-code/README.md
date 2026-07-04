# CityPulse AI 🏙️

An AI-powered Decision Intelligence Platform for Smarter, Better-Living Communities.

Built for **Gen AI Academy APAC Edition** (Google Cloud x H2S) — Challenge: *AI for Better Living and Smarter Communities*.

## What it does
- **Citizen reporting**: residents submit community issues (potholes, garbage, water leaks, safety, etc.) in plain language.
- **AI auto-triage**: Gemini AI classifies each report into a category, assigns a priority, and recommends an action — instantly, with no manual sorting.
- **Live dashboard**: real-time charts on issue categories, hotspot areas, priority mix, and trends over time — turning raw citizen data into decisions.
- **Conversational analytics**: ask the AI natural-language questions like "Which area has the most complaints?" and get an instant, data-grounded answer (RAG-style: the AI is only given the live aggregated data, so answers stay grounded in real numbers).

## Tech stack (100% free tier)
- **Streamlit** — UI framework, hosted free on Streamlit Community Cloud
- **Google Gemini API** (`gemini-1.5-flash`) — free tier, no credit card required
- **Pandas / Plotly** — data processing & visualization
- Runs fully in **demo mode** with a built-in rule-based classifier even without an API key, so it's always live and free to demo.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
## Project structure
```
app.py                    # Main Streamlit application
generate_sample_data.py   # Generates starter synthetic dataset
community_reports.csv     # Sample data (220 synthetic reports)
requirements.txt          # Dependencies
```

## Future roadmap
- Persist reports to a real database (Firestore / BigQuery) instead of session state
- Add computer-vision report intake (photo of pothole/garbage → auto-classified)
- Predictive analytics: forecast issue hotspots before they escalate
- Multi-language support for citizen submissions
