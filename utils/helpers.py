import pandas as pd
import streamlit as st


PCT_COL_CANDIDATES = {
    "销量份额", "销售额份额", "销量市占率(%)", "销售额市占率(%)",
    "新品成功率(%)", "销量增长率(%)", "销售额增长率(%)",
    "mapping_rate", "映射率",
}


def show_empty(df: pd.DataFrame, msg: str = "暂无数据") -> bool:
    if df is None or df.empty:
        st.warning(msg)
        return True
    return False


def fmt_int(x):
    try:
        return f"{int(float(x)):,}"
    except Exception:
        return ""


def fmt_money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return ""


def fmt_pct(x):
    try:
        return f"{float(x):.2f}%"
    except Exception:
        return ""


def add_download_button(df: pd.DataFrame, file_name: str, label: str):
    if df is None or df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(label=label, data=csv, file_name=file_name, mime="text/csv")


def prepare_share_table(
    df: pd.DataFrame,
    rename_map: dict[str, str] | None = None,
    percent_cols: list[str] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    if rename_map:
        out = out.rename(columns=rename_map)

    for col in (percent_cols or []):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce") * 100

    return out


def make_brand_table_config(cols: list[str]) -> dict:
    config = {}
    text_cols = {"市场", "品牌", "型号段", "ASIN", "标题", "上架阶段", "新品状态", "最新月份", "上架月份", "原因"}
    link_cols = {"链接", "商品链接", "详情页链接"}

    for col in cols:
        if col in text_cols:
            config[col] = st.column_config.TextColumn(col)
        elif col in link_cols:
            config[col] = st.column_config.LinkColumn(col, display_text="详情")
        elif col in PCT_COL_CANDIDATES or "%" in col:
            config[col] = st.column_config.NumberColumn(col, format="%.2f%%", alignment="center")
        elif any(key in col for key in ["销售额", "ASP"]):
            config[col] = st.column_config.NumberColumn(col, format="%.2f", alignment="center")
        elif any(key in col for key in ["销量", "评分数", "新品数", "起量新品数"]):
            config[col] = st.column_config.NumberColumn(col, format="%.0f", alignment="center")
        elif col == "评分":
            config[col] = st.column_config.NumberColumn(col, format="%.2f", alignment="center")

    return config
