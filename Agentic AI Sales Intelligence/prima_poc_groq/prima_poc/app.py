import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

from data_loader import (
    load_data, summary_kpis, stockist_gap, product_performance,
    region_performance, scheme_impact, high_closing_stock, forecast_data
)
from groq_helper import (
    get_client, ask_groq,
    insight_overview, insight_stockist, insight_product,
    insight_region, insight_scheme, insight_forecast
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prima Division – Sales Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.kpi { background:#f0f4ff; border-radius:10px; padding:16px 10px;
       text-align:center; border:1px solid #d0d8f0; margin-bottom:8px; }
.kpi-val { font-size:1.8rem; font-weight:700; color:#1a3a6b; }
.kpi-lbl { font-size:.8rem; color:#555; margin-top:4px; }
.ai-box  { background:#f0fff4; border-left:4px solid #2ca02c;
           border-radius:8px; padding:14px; margin-top:10px; white-space:pre-wrap; }
div[data-testid="stSidebar"] { background:#0f1e3d; }
div[data-testid="stSidebar"] * { color:#e8eaf6 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💊 Prima Division")
    st.markdown("### Sales Intelligence POC")
    st.divider()

    api_key = st.text_input("🔑 Groq API Key (FREE)",
                             type="password",
                             placeholder="gsk_...",
                             help="Get FREE key → https://console.groq.com")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.markdown("[🔗 Get Free Groq Key](https://console.groq.com)", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Overview",
        "🏪 Stockist Gap",
        "💊 Product Performance",
        "🗺️ Region Analysis",
        "🎁 Scheme Impact",
        "📦 High Closing Stock",
        "📈 Forecasting",
        "🤖 Ask AI",
    ])

# ── Load data ─────────────────────────────────────────────────────────────────
pri, sec, sch = load_data()
client = get_client()
kpis = summary_kpis(pri, sec, sch)

# Pre-compute all analyses
@st.cache_data
def compute(_pri, _sec, _sch):
    return (
        stockist_gap(_pri, _sec),
        product_performance(_pri, _sec),
        region_performance(_pri, _sec),
        scheme_impact(_sec, _sch),
        high_closing_stock(_sec, _sch),
        forecast_data(_pri),
    )

gap_df, prod_df, reg_df, sch_df, hcs_df, fc_df = compute(pri, sec, sch)

# ═════════════════════════════════════════════════════════════════════════════
# 🏠 OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    st.title("💊 Prima Division – Sales Intelligence")
    st.caption(f"Period: {' | '.join(kpis['months'])}   •   {kpis['stockists']} Stockists   •   {kpis['products']} Products")

    # KPI row
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, icon, val, lbl in [
        (c1,"📦", f"₹{kpis['primary_value']/1e6:.1f}M",  "Primary Sales"),
        (c2,"🛒", f"₹{kpis['secondary_value']/1e6:.1f}M","Secondary Sales"),
        (c3,"🎁", f"₹{kpis['scheme_value']/1e6:.1f}M",   "Scheme Value"),
        (c4,"🏪", str(kpis['stockists']),                 "Stockists"),
        (c5,"💊", str(kpis['products']),                  "Products"),
        (c6,"🗺️", str(kpis['regions']),                   "Regions"),
    ]:
        col.markdown(f"<div class='kpi'><div class='kpi-val'>{icon} {val}</div><div class='kpi-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.divider()

    # Monthly trend
    p_mon = pri.groupby("month")["ptsvalue"].sum().reset_index().rename(columns={"ptsvalue":"value"})
    p_mon["type"] = "Primary"
    s_mon = sec.groupby("month")["ptsvalue"].sum().reset_index().rename(columns={"ptsvalue":"value"})
    s_mon["type"] = "Secondary"
    trend = pd.concat([p_mon, s_mon])

    c1, c2 = st.columns([2,1])
    with c1:
        fig = px.bar(trend, x="month", y="value", color="type", barmode="group",
                     title="Monthly Primary vs Secondary Sales",
                     color_discrete_map={"Primary":"#1f77b4","Secondary":"#ff7f0e"},
                     labels={"value":"₹ Value","month":"Month","type":""})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        zone = pri.groupby("zonee")["ptsvalue"].sum().reset_index()
        fig2 = px.pie(zone, values="ptsvalue", names="zonee", title="Zone-wise Sales Share",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    # Region heatmap
    pivot = reg_df.pivot_table(index="region", columns="month", values="primary", aggfunc="sum", fill_value=0)
    fig3 = px.imshow(pivot, text_auto=".2s", aspect="auto",
                     title="Region-wise Primary Sales Heatmap", color_continuous_scale="Blues")
    fig3.update_layout(height=480)
    st.plotly_chart(fig3, use_container_width=True)

    # AI insight
    with st.expander("🤖 AI Executive Summary"):
        if st.button("Generate AI Summary", key="ov_ai"):
            with st.spinner("Thinking..."):
                p_dict = p_mon.set_index("month")["value"].to_dict()
                s_dict = s_mon.set_index("month")["value"].to_dict()
                txt = insight_overview(client, str(p_dict), str(s_dict))
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 🏪 STOCKIST GAP
# ═════════════════════════════════════════════════════════════════════════════
elif "Stockist" in page:
    st.title("🏪 Stockist Gap Analysis")
    st.caption("Primary billed vs Secondary sold – unsold inventory sitting at stockists")

    c1, c2, c3 = st.columns(3)
    all_regions = ["All"] + sorted(gap_df["region"].astype(str).unique().tolist())
    all_months  = ["All"] + sorted(gap_df["month"].astype(str).unique().tolist())
    sel_region  = c1.selectbox("Region", all_regions)
    sel_month   = c2.selectbox("Month",  all_months)
    min_gap     = c3.number_input("Min Gap (₹)", value=0, step=10000)

    df = gap_df.copy()
    if sel_region != "All": df = df[df["region"] == sel_region]
    if sel_month  != "All": df = df[df["month"]  == sel_month]
    df = df[df["gap"] >= min_gap]

    # Bar chart top 15
    top15 = df.groupby(["stockistcode","stockistname"]).agg(
        primary=("primary","sum"), secondary=("secondary","sum"), gap=("gap","sum")
    ).reset_index().nlargest(15,"gap")

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Primary", x=top15["stockistname"], y=top15["primary"], marker_color="#1f77b4"))
    fig.add_trace(go.Bar(name="Secondary", x=top15["stockistname"], y=top15["secondary"], marker_color="#ff7f0e"))
    fig.update_layout(barmode="group", title="Top 15 Stockists – Primary vs Secondary Gap",
                      xaxis_tickangle=-40, height=440,
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.markdown("#### 📋 Stockist Gap Table")
    tbl = df.groupby(["stockistcode","stockistname","region"]).agg(
        Primary=("primary","sum"), Secondary=("secondary","sum"), Gap=("gap","sum")
    ).reset_index().sort_values("Gap", ascending=False)
    tbl["Gap%"] = (tbl["Gap"]/tbl["Primary"].replace(0,np.nan)*100).fillna(0).round(1)
    tbl["Primary"]   = tbl["Primary"].map("₹{:,.0f}".format)
    tbl["Secondary"] = tbl["Secondary"].map("₹{:,.0f}".format)
    tbl["Gap"]       = tbl["Gap"].map("₹{:,.0f}".format)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download CSV", tbl.to_csv(index=False), "stockist_gap.csv")

    with st.expander("🤖 AI Insight"):
        if st.button("Generate Insight", key="gap_ai"):
            with st.spinner("Thinking..."):
                txt = insight_stockist(client, gap_df)
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 💊 PRODUCT PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
elif "Product" in page:
    st.title("💊 Product Performance")

    # Scatter
    summary = prod_df.groupby("product").agg(
        primary=("pri_value","sum"), secondary=("sec_value","sum"), st=("sellthrough","mean")
    ).reset_index()
    summary["status"] = summary["st"].apply(
        lambda x: "🟢 Fast" if x>=70 else("🟡 Moderate" if x>=40 else "🔴 Slow"))

    fig = px.scatter(summary, x="primary", y="secondary", size="st", color="status",
                     hover_name="product",
                     title="Product: Primary Billed vs Secondary Sold (bubble = sell-through%)",
                     labels={"primary":"Primary ₹","secondary":"Secondary ₹"},
                     color_discrete_map={"🟢 Fast":"#2ca02c","🟡 Moderate":"#ff7f0e","🔴 Slow":"#d62728"},
                     size_max=40)
    st.plotly_chart(fig, use_container_width=True)

    # Trend lines top products
    top_prods = summary.nlargest(8,"primary")["product"].tolist()
    trend = fc_df[fc_df["product"].isin(top_prods)].groupby(["product","month"])["ptsvalue"].sum().reset_index()
    fig2 = px.line(trend, x="month", y="ptsvalue", color="product", markers=True,
                   title="Monthly Trend – Top 8 Products", labels={"ptsvalue":"₹","month":"Month"})
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📋 Product Summary Table")
    show = summary.sort_values("primary", ascending=False)
    show["primary"]   = show["primary"].map("₹{:,.0f}".format)
    show["secondary"] = show["secondary"].map("₹{:,.0f}".format)
    show["st"]        = show["st"].map("{:.1f}%".format)
    show.columns      = ["Product","Primary","Secondary","Sell-through","Status"]
    st.dataframe(show, use_container_width=True, hide_index=True)

    with st.expander("🤖 AI Insight"):
        if st.button("Generate Insight", key="prod_ai"):
            with st.spinner("Thinking..."):
                txt = insight_product(client, prod_df)
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 🗺️ REGION ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
elif "Region" in page:
    st.title("🗺️ Region / HQ Analysis")

    pivot = reg_df.pivot_table(index="region", columns="month", values="primary", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=".2s", aspect="auto",
                    title="Region-wise Primary Sales Heatmap", color_continuous_scale="Blues")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    reg_sum = reg_df.groupby("region").agg(Primary=("primary","sum"), Secondary=("secondary","sum")).reset_index()
    reg_sum["Coverage%"] = (reg_sum["Secondary"]/reg_sum["Primary"].replace(0,np.nan)*100).fillna(0).round(1)
    reg_sum["Status"] = reg_sum["Coverage%"].apply(
        lambda x: "🟢 Strong" if x>=80 else("🟡 Average" if x>=50 else "🔴 Weak"))
    reg_sum = reg_sum.sort_values("Primary", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = px.bar(reg_sum.head(15), x="region", y=["Primary","Secondary"], barmode="group",
                      title="Top 15 Regions – Primary vs Secondary",
                      color_discrete_sequence=["#1f77b4","#ff7f0e"])
        fig2.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        disp = reg_sum.copy()
        disp["Primary"]   = disp["Primary"].map("₹{:,.0f}".format)
        disp["Secondary"] = disp["Secondary"].map("₹{:,.0f}".format)
        st.dataframe(disp, use_container_width=True, hide_index=True)

    with st.expander("🤖 AI Insight"):
        if st.button("Generate Insight", key="reg_ai"):
            with st.spinner("Thinking..."):
                txt = insight_region(client, reg_df)
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 🎁 SCHEME IMPACT
# ═════════════════════════════════════════════════════════════════════════════
elif "Scheme" in page:
    st.title("🎁 Scheme Impact Analysis")

    impact = sch_df.groupby("has_scheme").agg(
        avg_sec=("sec_value","mean"), avg_cls=("cls","mean"), count=("stockistcode","count")
    ).reset_index()
    impact["label"] = impact["has_scheme"].map({True:"With Scheme", False:"Without Scheme"})

    fig = make_subplots(rows=1, cols=2, subplot_titles=["Avg Secondary Sales","Avg Closing Stock"])
    fig.add_trace(go.Bar(x=impact["label"], y=impact["avg_sec"],
                         marker_color=["#2ca02c","#7f7f7f"], name="Secondary"), row=1, col=1)
    fig.add_trace(go.Bar(x=impact["label"], y=impact["avg_cls"],
                         marker_color=["#d62728","#7f7f7f"], name="Closing Stock"), row=1, col=2)
    fig.update_layout(title="Scheme vs No-Scheme Comparison", showlegend=False, height=380)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📋 Scheme Detail Table")
    cols = ["month","stockistcode","product","sec_qty","sec_value","cls","sch_qty","free_qty","sch_value","has_scheme"]
    st.dataframe(sch_df[cols].sort_values("sch_value", ascending=False).head(100),
                 use_container_width=True, hide_index=True)

    with st.expander("🤖 AI Insight"):
        if st.button("Generate Insight", key="sch_ai"):
            with st.spinner("Thinking..."):
                txt = insight_scheme(client, sch_df)
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 📦 HIGH CLOSING STOCK
# ═════════════════════════════════════════════════════════════════════════════
elif "Closing" in page:
    st.title("📦 High Closing Stock – Scheme Recipients")
    st.info("Stockists who received schemes but still have high unsold closing stock → potential scheme misuse or market saturation.")

    fig = px.bar(hcs_df.head(20), x="product", y="clstock", color="stockistname",
                 title="Top 20 – High Closing Stock (Scheme Stockists)",
                 labels={"clstock":"Closing Stock (Units)","product":"Product"})
    fig.update_layout(xaxis_tickangle=-40, height=460, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    disp = hcs_df[["stockistcode","stockistname","product","clstock","clsvalue","sch_value","sch_qty","free_qty"]].copy()
    disp["clsvalue"]  = disp["clsvalue"].map("₹{:,.0f}".format)
    disp["sch_value"] = disp["sch_value"].map("₹{:,.0f}".format)
    disp.columns = ["Stk Code","Stockist","Product","Closing Qty","Closing Val","Scheme Val","Scheme Qty","Free Qty"]
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download CSV", hcs_df.to_csv(index=False), "high_closing_stock.csv")


# ═════════════════════════════════════════════════════════════════════════════
# 📈 FORECASTING
# ═════════════════════════════════════════════════════════════════════════════
elif "Forecast" in page:
    st.title("📈 Sales Forecasting")

    all_products = sorted(fc_df["product"].unique().tolist())
    sel = st.multiselect("Select Products", all_products, default=all_products[:5])

    if sel:
        trend = fc_df[fc_df["product"].isin(sel)].groupby(["product","month"])["ptsvalue"].sum().reset_index()
        fig = px.line(trend, x="month", y="ptsvalue", color="product", markers=True,
                      title="Product Sales Trend", labels={"ptsvalue":"₹","month":"Month"})
        st.plotly_chart(fig, use_container_width=True)

        # Simple linear forecast per selected product
        st.markdown("#### 📊 Next-Month Forecast")
        rows = []
        for prod in sel:
            df_p = fc_df[fc_df["product"]==prod].groupby("month")["ptsvalue"].sum().reset_index()
            vals = df_p["ptsvalue"].values
            if len(vals) >= 2:
                x = np.arange(len(vals))
                m, b = np.polyfit(x, vals, 1)
                nxt = max(0, m*len(vals)+b)
                rows.append({"Product":prod,
                             "Month 1":f"₹{vals[0]:,.0f}" if len(vals)>0 else"-",
                             "Month 2":f"₹{vals[1]:,.0f}" if len(vals)>1 else"-",
                             "Month 3":f"₹{vals[2]:,.0f}" if len(vals)>2 else"-",
                             "Forecast (Next)":f"₹{nxt:,.0f}",
                             "Trend":"📈 Up" if m>0 else "📉 Down"})
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("🤖 AI Forecast Insight"):
        if st.button("Generate Forecast Insight", key="fc_ai"):
            with st.spinner("Thinking..."):
                txt = insight_forecast(client, fc_df)
            st.markdown(f"<div class='ai-box'>{txt}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 🤖 ASK AI
# ═════════════════════════════════════════════════════════════════════════════
elif "Ask" in page:
    st.title("🤖 Ask AI – Natural Language Insights")
    st.caption("Ask anything about your sales data in plain English")

    if not client:
        st.warning("⚠️ Enter your Groq API key in the sidebar to use AI features.\n\n**Get FREE key → https://console.groq.com**")

    examples = [
        "Which stockists have high gap between primary and secondary?",
        "Which products are slow movers in South zone?",
        "Are schemes helping secondary sales or just increasing closing stock?",
        "Which region should the sales team focus on next month?",
        "List stockists with scheme but no secondary sales improvement",
        "What is the overall sell-through rate trend?",
    ]

    st.markdown("**💡 Click an example or type your own:**")
    cols = st.columns(3)
    for i, q in enumerate(examples):
        if cols[i%3].button(q, key=f"ex{i}", use_container_width=True):
            st.session_state["question"] = q

    question = st.text_area("Your Question", value=st.session_state.get("question",""),
                             placeholder="e.g. Which stockists received schemes but show no improvement in secondary sales?",
                             height=90)

    if st.button("🔍 Get AI Insight", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Analysing your data..."):
                ctx = f"""
PRIMARY SUMMARY (region-month):
{pri.groupby(['region','month'])['ptsvalue'].sum().reset_index().to_string(index=False)}

SECONDARY SUMMARY (region-month):
{sec.groupby(['region','month'])['ptsvalue'].sum().reset_index().to_string(index=False)}

PRODUCT PERFORMANCE:
{prod_df.groupby('product').agg(pri=('pri_value','sum'),sec=('sec_value','sum'),st=('sellthrough','mean')).reset_index().to_string(index=False)}

SCHEME IMPACT:
{sch_df.groupby('has_scheme').agg(avg_sec=('sec_value','mean'),avg_cls=('cls','mean')).reset_index().to_string(index=False)}
"""
                result = ask_groq(client, ctx, question)
            st.markdown(f"<div class='ai-box'>{result}</div>", unsafe_allow_html=True)
            if "question" in st.session_state:
                del st.session_state["question"]
