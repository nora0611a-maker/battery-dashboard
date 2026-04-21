import pandas as pd
import streamlit as st


def show_empty(df: pd.DataFrame, msg: str = "暂无数据") -> bool:
    if df is None or df.empty:
        st.warning(msg)
        return True
    return False


def fmt_int(x):
    try:
        return f"{int(x):,}"
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
    rename_map: dict,
    percent_cols: list[str] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    out = df.rename(columns=rename_map).copy()
    percent_cols = percent_cols or []

    for col in percent_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce") * 100

    return out


def make_brand_table_config(columns: list[str]) -> dict:
    config = {}

    text_cols = ["市场", "品牌", "型号段"]
    for col in text_cols:
        if col in columns:
            config[col] = st.column_config.TextColumn(col)

    number_specs = {
        "销量": ("%.0f", "center"),
        "销售额": ("%.2f", "center"),
        "市场总销量": ("%.0f", "center"),
        "市场总销售额": ("%.2f", "center"),
        "型号段总销量": ("%.0f", "center"),
        "型号段总销售额": ("%.2f", "center"),
        "销量份额": ("%.2f%%", "center"),
        "销售额份额": ("%.2f%%", "center"),
        "ASP": ("%.2f", "center"),
    }

    for col, (fmt, align) in number_specs.items():
        if col in columns:
            config[col] = st.column_config.NumberColumn(
                col,
                format=fmt,
                alignment=align,
            )

    return config