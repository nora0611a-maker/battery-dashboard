# from pathlib import Path
# import pandas as pd
# import streamlit as st
# from utils.config import DATA_DIR
#
#
# def _safe_read_text(path: Path) -> str:
#     if not path.exists():
#         return ""
#     return path.read_text(encoding="utf-8")
#
#
# @st.cache_data(show_spinner=False)
# def load_csv(name: str) -> pd.DataFrame:
#     path = DATA_DIR / f"{name}.csv"
#     if not path.exists():
#         return pd.DataFrame()
#     return pd.read_csv(path)
#
#
# @st.cache_data(show_spinner=False)
# def load_text(name: str) -> str:
#     return _safe_read_text(DATA_DIR / f"{name}.txt")
#
#
# @st.cache_data(show_spinner=False)
# def load_all_data() -> dict[str, pd.DataFrame | str]:
#     csv_names = [
#         "agg_market_month",
#         "agg_segment_month",
#         "agg_segment_total",
#         "agg_brand_market_total",
#         "agg_brand_market_month",
#         "agg_brand_segment_total",
#         "dashboard_asin_master",
#         "dashboard_brand_new_summary",
#         "qa_report",
#         "mapping_coverage",
#         "unmapped_asin",
#     ]
#
#     text_names = [
#         "insight_home",
#         "insight_segment",
#         "insight_brand",
#         "insight_asin",
#         "insight_full_cleaned",
#     ]
#
#     out: dict[str, pd.DataFrame | str] = {}
#     for n in csv_names:
#         out[n] = load_csv(n)
#     for n in text_names:
#         out[n] = load_text(n)
#     return out

import pandas as pd
import streamlit as st
import gspread
from utils.config import GSHEET_ID


@st.cache_resource
def get_gspread_client():
    creds = dict(st.secrets["gcp_service_account"])
    return gspread.service_account_from_dict(creds)


@st.cache_resource
def get_workbook():
    gc = get_gspread_client()
    return gc.open_by_key(GSHEET_ID)


@st.cache_data(show_spinner=False, ttl=300)
def load_csv(name: str) -> pd.DataFrame:
    """
    约定 Google Sheets 中每个 worksheet 名称与原 csv 名一致
    比如：agg_market_month / agg_segment_month / qa_report
    """
    sh = get_workbook().worksheet(name)
    rows = sh.get_all_records()
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False, ttl=300)
def load_text(name: str) -> str:
    """
    约定 texts worksheet 中两列：
    key | value
    """
    sh = get_workbook().worksheet("texts")
    rows = sh.get_all_records()
    mapping = {r["key"]: r["value"] for r in rows}
    return mapping.get(name, "")


@st.cache_data(show_spinner=False, ttl=300)
def load_all_data() -> dict[str, pd.DataFrame | str]:
    csv_names = [
        "agg_market_month",
        "agg_segment_month",
        "agg_brand_market_total",
        "agg_brand_market_month",
        "agg_brand_segment_total",
        "agg_brand_segment_month",
        "agg_concentration_month",
        "agg_asin_market_total",
        "agg_asin_segment_total",
        "agg_asin_month",
        "agg_asin_new_month",
        "agg_brand_new_month",
        "agg_asin_growth_month",
        "fact_asin_month",
        "dim_product",
        "qa_report",
        "mapping_coverage",
        "unmapped_asin",
    ]

    text_names = [
        "insight_home",
        "insight_segment",
        "insight_brand",
        "insight_asin",
        "insight_full_cleaned",
    ]

    out: dict[str, pd.DataFrame | str] = {}
    for n in csv_names:
        out[n] = load_csv(n)
    for n in text_names:
        out[n] = load_text(n)
    return out