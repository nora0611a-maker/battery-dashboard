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
    """
    读取单独 worksheet 的表格数据。
    例如：agg_market_month -> US_agg_market_month
    """
    real_name = _sheet_name(name)
    sh = get_workbook().worksheet(real_name)
    rows = sh.get_all_records()
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False, ttl=300)
def load_text(name: str) -> str:
    """
    读取单独 worksheet 的文本内容。
    例如：insight_home -> US_insight_home
    同步脚本写入格式为：
    第1行：text
    第2行：具体文本
    """
    real_name = _sheet_name(name)
    ws = get_workbook().worksheet(real_name)
    values = ws.get_all_values()

    if not values or len(values) < 2:
        return ""
    return values[1][0] if values[1] else ""


@st.cache_data(show_spinner=False, ttl=300)
def load_all_data() -> dict[str, pd.DataFrame | str]:
    csv_names = [
        "agg_market_month",
        "agg_segment_month",
        "agg_segment_total",
        "agg_brand_market_month",
        "agg_brand_market_total",
        "agg_brand_segment_total",
        "dashboard_asin_master",
        "dashboard_brand_new_summary",
        "qa_report",
        "mapping_coverage",
        "unmapped_asin",
    ]

    text_names = [
        "insight_home",
        "insight_segment",
        "insight_brand",
        "insight_asin",
        "insight_markdown",
        "insight_full_cleaned",
    ]

    out: dict[str, pd.DataFrame | str] = {}
    for n in csv_names:
        out[n] = load_csv(n)
    for n in text_names:
        out[n] = load_text(n)
    return out
