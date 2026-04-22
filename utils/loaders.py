# loaders.py
import pandas as pd
import streamlit as st
import gspread
from gspread.exceptions import WorksheetNotFound
from utils.config import GSHEET_ID, GSHEET_TAB_PREFIX


@st.cache_resource
def get_gspread_client():
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError(
            "Missing Streamlit secret: gcp_service_account. "
            "Please add it in Community Cloud: Manage app -> Settings -> Secrets."
        )
    creds = dict(st.secrets["gcp_service_account"])
    return gspread.service_account_from_dict(creds)


@st.cache_resource
def get_workbook():
    if not GSHEET_ID or GSHEET_ID == "在这里填写你的GoogleSheetID":
        raise RuntimeError("Please set GSHEET_ID in utils/config.py before deploying.")
    gc = get_gspread_client()
    return gc.open_by_key(GSHEET_ID)


def _sheet_name(name: str) -> str:
    return f"{GSHEET_TAB_PREFIX}{name}" if GSHEET_TAB_PREFIX else name


@st.cache_data(show_spinner=False, ttl=300)
def load_csv(name: str) -> pd.DataFrame:
    real_name = _sheet_name(name)
    try:
        sh = get_workbook().worksheet(real_name)
        rows = sh.get_all_records()
        return pd.DataFrame(rows)
    except WorksheetNotFound:
        return pd.DataFrame()


@st.cache_data(show_spinner=False, ttl=300)
def load_text(name: str) -> str:
    real_name = _sheet_name(name)
    try:
        ws = get_workbook().worksheet(real_name)
        values = ws.get_all_values()
        if not values or len(values) < 2:
            return ""
        return values[1][0] if values[1] else ""
    except WorksheetNotFound:
        return ""


@st.cache_data(show_spinner=False, ttl=300)
def load_all_data() -> dict[str, pd.DataFrame | str]:
    csv_names = [
        "agg_market_month",
        "agg_segment_month",
        "agg_segment_total",
        "agg_brand_market_month",
        "agg_brand_market_total",
        "agg_brand_segment_total",
        "agg_asin_market_total",
        "agg_asin_segment_total",
        "agg_asin_month",
        "agg_asin_new_month",
        "agg_brand_new_month",
        "agg_asin_growth_month",
        "qa_report",
        "mapping_coverage",
        "inactive_asin_in_window",
    ]

    text_names = [
        "insight_home",
        "insight_segment",
        "insight_brand",
        "insight_asin",
    ]

    out: dict[str, pd.DataFrame | str] = {}
    for n in csv_names:
        out[n] = load_csv(n)
    for n in text_names:
        out[n] = load_text(n)
    return out