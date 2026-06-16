import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "sales_data.xlsx"


@st.cache_data
def load_data():
    xl = pd.read_excel(DATA_PATH, sheet_name=None)

    # ── Primary ──────────────────────────────────────────────
    pri = xl["Primary"].copy()
    pri = pri[pri["iscancelled"] == False]
    pri["invoicedate"] = pd.to_datetime(pri["invoicedate"])
    pri["month"] = pri["invoicedate"].dt.to_period("M").astype(str)
    pri["ptsvalue"] = pd.to_numeric(pri["ptsvalue"], errors="coerce").fillna(0)
    pri["quantity"] = pd.to_numeric(pri["quantity"], errors="coerce").fillna(0)
    pri["region"] = pri["region"].astype(str)

    # ── Secondary ────────────────────────────────────────────
    sec = xl["Secondary"].copy()
    sec["statementdate"] = pd.to_datetime(sec["statementdate"])
    sec["month"] = sec["statementdate"].dt.to_period("M").astype(str)
    sec["ptsvalue"] = pd.to_numeric(sec["ptsvalue"], errors="coerce").fillna(0)
    sec["quantity"] = pd.to_numeric(sec["quantity"], errors="coerce").fillna(0)
    sec["clstock"] = pd.to_numeric(sec["clstock"], errors="coerce").fillna(0)
    sec["clsvalue"] = pd.to_numeric(sec["clsvalue"], errors="coerce").fillna(0)
    sec["region"] = sec["region"].astype(str)

    # ── Scheme ───────────────────────────────────────────────
    sch = xl["Scheme Data"].copy()
    sch = sch[sch["inactive"] == "N"]
    sch["app_date"] = pd.to_datetime(sch["app_date"])
    sch["month"] = sch["app_date"].dt.to_period("M").astype(str)
    sch["prod_value"] = pd.to_numeric(sch["prod_value"], errors="coerce").fillna(0)
    sch["prod_qty"] = pd.to_numeric(sch["prod_qty"], errors="coerce").fillna(0)
    sch["prod_free_qty"] = pd.to_numeric(sch["prod_free_qty"], errors="coerce").fillna(0)

    return pri, sec, sch


# ── KPI summary ──────────────────────────────────────────────────────────────
def summary_kpis(pri, sec, sch):
    return {
        "primary_value":    pri["ptsvalue"].sum(),
        "secondary_value":  sec["ptsvalue"].sum(),
        "scheme_value":     sch["prod_value"].sum(),
        "stockists":        pri["stockistcode"].nunique(),
        "products":         pri["pcode"].nunique(),
        "regions":          pri["region"].nunique(),
        "months":           sorted(pri["month"].unique().tolist()),
    }


# ── Stockist gap ─────────────────────────────────────────────────────────────
def stockist_gap(pri, sec):
    p = pri.groupby(["stockistcode", "stockistname", "region", "month"])["ptsvalue"].sum().reset_index()
    p.columns = ["stockistcode", "stockistname", "region", "month", "primary"]

    s = sec.groupby(["stockistcode", "month"])["ptsvalue"].sum().reset_index()
    s.columns = ["stockistcode", "month", "secondary"]

    df = p.merge(s, on=["stockistcode", "month"], how="left").fillna(0)
    df["gap"] = df["primary"] - df["secondary"]
    df["gap_pct"] = (df["gap"] / df["primary"].replace(0, np.nan) * 100).fillna(0).round(1)
    return df


# ── Product performance ───────────────────────────────────────────────────────
def product_performance(pri, sec):
    p = pri.groupby(["pcode", "product", "month"]).agg(
        pri_qty=("quantity", "sum"), pri_value=("ptsvalue", "sum")
    ).reset_index()

    s = sec.groupby(["pcode", "product", "month"]).agg(
        sec_qty=("quantity", "sum"), sec_value=("ptsvalue", "sum"),
        avg_cls=("clstock", "mean")
    ).reset_index()

    df = p.merge(s, on=["pcode", "product", "month"], how="outer").fillna(0)
    df["sellthrough"] = (df["sec_qty"] / df["pri_qty"].replace(0, np.nan) * 100).fillna(0).round(1)
    df["status"] = df["sellthrough"].apply(
        lambda x: "🟢 Fast" if x >= 70 else ("🟡 Moderate" if x >= 40 else "🔴 Slow")
    )
    return df


# ── Region performance ────────────────────────────────────────────────────────
def region_performance(pri, sec):
    p = pri.groupby(["region", "month"])["ptsvalue"].sum().reset_index().rename(columns={"ptsvalue": "primary"})
    s = sec.groupby(["region", "month"])["ptsvalue"].sum().reset_index().rename(columns={"ptsvalue": "secondary"})
    df = p.merge(s, on=["region", "month"], how="outer").fillna(0)
    return df


# ── Scheme impact ─────────────────────────────────────────────────────────────
def scheme_impact(sec, sch):
    sc = sch.groupby(["stc_code", "prod_code", "month"]).agg(
        sch_qty=("prod_qty", "sum"), free_qty=("prod_free_qty", "sum"), sch_value=("prod_value", "sum")
    ).reset_index().rename(columns={"stc_code": "stockistcode", "prod_code": "pcode"})

    s = sec.groupby(["stockistcode", "pcode", "product", "month"]).agg(
        sec_qty=("quantity", "sum"), sec_value=("ptsvalue", "sum"), cls=("clstock", "mean")
    ).reset_index()

    df = s.merge(sc, on=["stockistcode", "pcode", "month"], how="left").fillna(0)
    df["has_scheme"] = df["sch_value"] > 0
    return df


# ── High closing stock with scheme ────────────────────────────────────────────
def high_closing_stock(sec, sch):
    latest = (
        sec.sort_values("statementdate")
        .groupby(["stockistcode", "stockistname", "pcode", "product"])
        .last()
        .reset_index()[["stockistcode", "stockistname", "pcode", "product", "clstock", "clsvalue"]]
    )

    sc = sch.groupby(["stc_code", "prod_code"]).agg(
        sch_value=("prod_value", "sum"), sch_qty=("prod_qty", "sum"), free_qty=("prod_free_qty", "sum")
    ).reset_index().rename(columns={"stc_code": "stockistcode", "prod_code": "pcode"})

    df = latest.merge(sc, on=["stockistcode", "pcode"], how="inner")
    df = df[df["clstock"] > 0].sort_values("clstock", ascending=False)
    return df


# ── Forecast data ─────────────────────────────────────────────────────────────
def forecast_data(pri):
    return pri.groupby(["pcode", "product", "month"])["ptsvalue"].sum().reset_index()
