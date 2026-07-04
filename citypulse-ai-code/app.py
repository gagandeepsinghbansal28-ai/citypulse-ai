"""
CityPulse AI — An AI-powered Decision Intelligence Platform for Smart Communities
Hackathon: Gen AI Academy APAC Edition | Challenge: AI for Better Living and Smarter Communities

Run locally:   streamlit run app.py
Deploy free:   Streamlit Community Cloud (see README.md)
"""

import os
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(page_title="CityPulse AI", page_icon="🏙️", layout="wide")
DATA_FILE = "community_reports.csv"

CATEGORIES = ["Roads & Potholes", "Waste Management", "Water Supply", "Street Lighting",
              "Public Safety", "Traffic & Mobility", "Parks & Environment", "Noise/Nuisance"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

# ---------------------------------------------------------------------------
# GEMINI SETUP (optional — app works in demo mode without a key too)
# ---------------------------------------------------------------------------
def _get_gemini_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

GEMINI_API_KEY = _get_gemini_key()

GEMINI_READY = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        MODEL = genai.GenerativeModel("gemini-1.5-flash")
        GEMINI_READY = True
    except Exception:
        GEMINI_READY = False


def classify_report(description: str) -> dict:
    """Use Gemini to classify a citizen report into category + priority + a short
    recommended action. Falls back to a lightweight keyword-based classifier if
    no API key is configured, so the prototype is always fully demoable for free."""
    if GEMINI_READY:
        prompt = f"""You are a city-services triage assistant. Classify the following
citizen report and respond ONLY with compact JSON, no extra text, in this exact shape:
{{"category": one of {CATEGORIES}, "priority": one of {PRIORITIES}, "recommended_action": "<one short sentence>"}}

Report: "{description}"
"""
        try:
            resp = MODEL.generate_content(prompt)
            text = resp.text.strip().strip("`").replace("json", "", 1).strip()
            return json.loads(text)
        except Exception:
            pass  # fall through to rule-based fallback

    # --- Rule-based fallback (keeps the app 100% free and always working) ---
    d = description.lower()
    keyword_map = {
        "Roads & Potholes": ["pothole", "road", "street damage", "crack"],
        "Waste Management": ["garbage", "trash", "waste", "dumping"],
        "Water Supply": ["water", "pipeline", "leak", "sewage"],
        "Street Lighting": ["light", "dark", "streetlight"],
        "Public Safety": ["unsafe", "danger", "stray", "manhole", "accident"],
        "Traffic & Mobility": ["traffic", "congestion", "signal", "parking"],
        "Parks & Environment": ["park", "tree", "pollution", "bench"],
        "Noise/Nuisance": ["noise", "loud", "construction"],
    }
    category = "Public Safety"
    for cat, kws in keyword_map.items():
        if any(k in d for k in kws):
            category = cat
            break
    urgent_words = ["danger", "unsafe", "flooding", "accident", "critical", "fire"]
    priority = "Critical" if any(w in d for w in urgent_words) else \
               "High" if category in ["Public Safety", "Water Supply"] else "Medium"
    return {
        "category": category,
        "priority": priority,
        "recommended_action": f"Route to {category} department for inspection within "
                               f"{'24 hours' if priority in ['Critical', 'High'] else '5-7 days'}."
    }


def ask_assistant(question: str, df: pd.DataFrame) -> str:
    """Natural-language Q&A over the live reports data (a lightweight RAG-style
    pattern: relevant data is summarized and injected into the LLM prompt)."""
    context = df.groupby(["area", "category", "priority"]).size().reset_index(name="count")
    context_str = context.to_csv(index=False)

    if GEMINI_READY:
        prompt = f"""You are a city decision-intelligence assistant. Use ONLY the data
below (aggregated citizen report counts by area/category/priority) to answer the
question briefly and with concrete numbers. If the data can't answer it, say so.

DATA:
{context_str}

QUESTION: {question}
"""
        try:
            resp = MODEL.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            return f"(AI temporarily unavailable, showing raw insight instead) {fallback_answer(question, df)}"
    return fallback_answer(question, df)


def fallback_answer(question: str, df: pd.DataFrame) -> str:
    """Simple offline analytics fallback so Q&A always works even with zero API cost."""
    q = question.lower()
    if "most" in q and "area" in q:
        top = df["area"].value_counts().idxmax()
        return f"The area with the most reports is **{top}** ({df['area'].value_counts().max()} reports)."
    if "critical" in q or "urgent" in q:
        n = (df["priority"] == "Critical").sum()
        return f"There are **{n} critical-priority** reports currently open."
    if "category" in q:
        top = df["category"].value_counts().idxmax()
        return f"The most common issue category is **{top}**."
    return ("I can summarize report counts by area, category, or priority. "
            "Try asking: 'Which area has the most complaints?' or 'How many critical issues are open?'")


# ---------------------------------------------------------------------------
# DATA LOAD
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

if "reports" not in st.session_state:
    st.session_state.reports = load_data()

df = st.session_state.reports

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🏙️ CityPulse AI")
st.caption("An AI-powered Decision Intelligence Platform for Smarter, Better-Living Communities")

if not GEMINI_READY:
    st.info("Running in **free demo mode** (rule-based AI). Add a free Gemini API key in "
            "Settings → Secrets as `GEMINI_API_KEY` to enable full generative AI classification "
            "and natural-language Q&A.", icon="ℹ️")

tab1, tab2, tab3 = st.tabs(["📢 Report an Issue", "📊 City Dashboard", "🤖 Ask the AI"])

# --- TAB 1: Citizen report submission ---
with tab1:
    st.subheader("Report a community issue")
    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        area = col1.selectbox("Area / Locality", sorted(df["area"].unique()))
        description = col2.text_input("Describe the issue", placeholder="e.g. Large pothole near the bus stop")
        submitted = st.form_submit_button("Submit Report (AI will auto-triage it)")

    if submitted and description.strip():
        with st.spinner("AI is analyzing and triaging your report..."):
            result = classify_report(description)
        new_row = {
            "report_id": f"CP{2000 + len(df)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "area": area,
            "category": result["category"],
            "description": description,
            "priority": result["priority"],
            "status": "Open",
        }
        st.session_state.reports = pd.concat(
            [st.session_state.reports, pd.DataFrame([new_row])], ignore_index=True
        )
        df = st.session_state.reports
        st.success("Report submitted and triaged by AI!")
        c1, c2, c3 = st.columns(3)
        c1.metric("Category", result["category"])
        c2.metric("Priority", result["priority"])
        c3.metric("Status", "Open")
        st.write(f"**Recommended action:** {result['recommended_action']}")

    st.divider()
    st.caption("Recent reports")
    st.dataframe(df.sort_values("timestamp", ascending=False).head(8), use_container_width=True, hide_index=True)

# --- TAB 2: Dashboard ---
with tab2:
    st.subheader("Community insights dashboard")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Reports", len(df))
    k2.metric("Open Issues", int((df["status"] == "Open").sum()))
    k3.metric("Critical Priority", int((df["priority"] == "Critical").sum()))
    k4.metric("Resolved", int((df["status"] == "Resolved").sum()))

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(df["category"].value_counts().reset_index(),
                       x="category", y="count", title="Issues by Category",
                       labels={"category": "Category", "count": "Reports"})
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.pie(df, names="priority", title="Priority Distribution", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.bar(df["area"].value_counts().reset_index(),
                       x="area", y="count", title="Hotspot Areas",
                       labels={"area": "Area", "count": "Reports"})
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        trend = df.copy()
        trend["date"] = pd.to_datetime(trend["timestamp"]).dt.date
        trend = trend.groupby("date").size().reset_index(name="reports")
        fig4 = px.line(trend, x="date", y="reports", title="Reports Trend Over Time")
        st.plotly_chart(fig4, use_container_width=True)

# --- TAB 3: AI Q&A ---
with tab3:
    st.subheader("Ask the AI decision-assistant about your city")
    st.caption("Example: \"Which area has the most complaints?\" or \"What should we prioritize this week?\"")
    question = st.text_input("Your question")
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            answer = ask_assistant(question, df)
        st.markdown(answer)
