import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert Pharma Sales Intelligence Analyst for an Indian pharmaceutical company (Prima Division).
You analyse Primary Sales (company → stockist), Secondary Sales (stockist → market), and Scheme data.
Give specific, actionable bullet-point insights. Use Indian pharma terms: stockist, MR, HQ, PTR, PTS.
Always reference actual numbers from the data provided. Be concise."""


def get_client(api_key: str = None):
    key = api_key or os.getenv("GROQ_API_KEY", "")
    if not key or key == "your_groq_api_key_here":
        return None
    return Groq(api_key=key)


def ask_groq(client, data_context: str, question: str) -> str:
    if client is None:
        return "⚠️ Please enter your Groq API key in the sidebar. Get a FREE key at https://console.groq.com"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # free model on Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"DATA:\n{data_context}\n\nQUESTION: {question}\n\nGive 4-6 specific insights with numbers."}
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ── Preset insight functions ──────────────────────────────────────────────────

def insight_overview(client, pri_monthly, sec_monthly):
    ctx = f"Monthly Primary Sales: {pri_monthly}\nMonthly Secondary Sales: {sec_monthly}"
    return ask_groq(client, ctx, "Give an executive summary of 3-month Prima Division sales performance with top 3 action items.")


def insight_stockist(client, gap_df):
    top = gap_df.nlargest(15, "gap")[["stockistname", "region", "primary", "secondary", "gap", "gap_pct"]].to_string(index=False)
    return ask_groq(client, top, "Which stockists have the highest unsold inventory gap? What are likely causes and recommended field actions?")


def insight_product(client, prod_df):
    summary = prod_df.groupby("product").agg(
        primary=("pri_value", "sum"), secondary=("sec_value", "sum"), sellthrough=("sellthrough", "mean")
    ).reset_index().sort_values("primary", ascending=False).to_string(index=False)
    return ask_groq(client, summary, "Identify fast movers, slow movers, and products at risk. What should the sales team prioritise?")


def insight_region(client, region_df):
    summary = region_df.groupby("region").agg(
        primary=("primary", "sum"), secondary=("secondary", "sum")
    ).reset_index().to_string(index=False)
    return ask_groq(client, summary, "Which regions are growing, declining, or underperforming? Name top 3 priority regions for management.")


def insight_scheme(client, scheme_df):
    impact = scheme_df.groupby("has_scheme").agg(
        avg_secondary=("sec_value", "mean"), avg_closing=("cls", "mean"), count=("stockistcode", "count")
    ).reset_index().to_string(index=False)
    return ask_groq(client, impact, "Are schemes effectively driving secondary sales? What is the impact on closing stock? Any wastage?")


def insight_forecast(client, forecast_df):
    trend = forecast_df.groupby(["product", "month"])["ptsvalue"].sum().unstack(fill_value=0).to_string()
    return ask_groq(client, trend, "Based on the 3-month trend, which products are growing or declining? Forecast next month for top 5 products.")
