import streamlit as st
import pandas as pd
from utils.loaders import load_csv, load_text
from utils.helpers import (
    show_empty,
    add_download_button,
    prepare_share_table,
    make_brand_table_config,
)
from utils.charts import brand_share_chart, bar_top_n
from utils.styles import section_header, insight_card, kpi_card, kpi_card_wide
from utils.styles import apply_global_styles

apply_global_styles()

st.title("03 品牌竞争")
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

brand_total = load_csv("agg_brand_market_total")
brand_month = load_csv("agg_brand_market_month")
brand_segment = load_csv("agg_brand_segment_total")
insight = load_text("insight_brand")

if show_empty(brand_total, "agg_brand_market_total.csv 为空"):
    st.stop()

brand_options = ["全部"] + sorted([x for x in brand_total["brand"].dropna().unique().tolist()])
segment_options = ["全部"] + (
    sorted([x for x in brand_segment["segment"].dropna().unique().tolist()])
    if not brand_segment.empty else []
)

c1, c2 = st.columns(2)
selected_brand = c1.selectbox("选择品牌", brand_options)
selected_segment = c2.selectbox("选择型号段", segment_options)

work_total = brand_total.copy()
work_month = brand_month.copy()
work_segment = brand_segment.copy()

if selected_brand != "全部":
    work_total = work_total[work_total["brand"] == selected_brand].copy()
    if not work_month.empty:
        work_month = work_month[work_month["brand"] == selected_brand].copy()
    if not work_segment.empty:
        work_segment = work_segment[work_segment["brand"] == selected_brand].copy()

if selected_segment != "全部" and not work_segment.empty:
    work_segment = work_segment[work_segment["segment"] == selected_segment].copy()

top_brand = brand_total.sort_values("units", ascending=False).iloc[0]["brand"] if not brand_total.empty else "-"
top_share = brand_total.sort_values("units", ascending=False).iloc[0]["share_units_pct"] if not brand_total.empty else 0
top_asp_brand = brand_total.sort_values("asp", ascending=False).iloc[0]["brand"] if not brand_total.empty else "-"
top_asp = brand_total.sort_values("asp", ascending=False).iloc[0]["asp"] if not brand_total.empty else 0

c3, c4, c5 = st.columns([0.8, 1.1, 1.1])
with c3:
    kpi_card("品牌数量", f"{brand_total['brand'].nunique():,}", "当前筛选范围累计")
with c4:
    kpi_card_wide("销量份额第一品牌", f"{top_brand} ｜ {top_share:.2f}%", "当前筛选范围累计")
with c5:
    kpi_card_wide("高 ASP 品牌", f"{top_asp_brand} ｜ ${top_asp:,.2f}", "当前筛选范围累计")

st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

# ===== 品牌总市占率 =====
section_header("品牌总市占率", "看全市场品牌位置与基本价格带")

brand_total_zh = prepare_share_table(
    work_total,
    rename_map={
        "market": "市场",
        "brand": "品牌",
        "units": "销量",
        "revenue": "销售额",
        "market_units": "市场总销量",
        "market_revenue": "市场总销售额",
        "share_units": "销量份额",
        "share_revenue": "销售额份额",
        "asp": "ASP",
    },
    percent_cols=["销量份额", "销售额份额"],
)

brand_total_show_cols = [
    "市场",
    "品牌",
    "销量",
    "销售额",
    "市场总销量",
    "市场总销售额",
    "销量份额",
    "销售额份额",
    "ASP",
]
brand_total_show_cols = [c for c in brand_total_show_cols if c in brand_total_zh.columns]

st.dataframe(
    brand_total_zh[brand_total_show_cols],
    use_container_width=True,
    hide_index=True,
    column_config=make_brand_table_config(brand_total_show_cols),
)

add_download_button(
    brand_total_zh[brand_total_show_cols],
    "brand_market_total.csv",
    "下载品牌总市占率表",
)

# ===== 品牌份额趋势 =====
if not work_month.empty:
    st.plotly_chart(
        brand_share_chart(work_month, "share_units_pct", "全市场品牌份额趋势 - 销量市占率"),
        use_container_width=True,
    )
    st.plotly_chart(
        brand_share_chart(work_month, "share_revenue_pct", "全市场品牌份额趋势 - 销售额市占率"),
        use_container_width=True,
    )

# ===== 品牌 × 型号段市占率 =====
c8, c9 = st.columns([1.6, 1], gap="medium")

with c8:
    section_header("品牌 × 型号段市占率", "用于看不同品牌在哪些型号段强")

    work_segment_zh = prepare_share_table(
        work_segment,
        rename_map={
            "market": "市场",
            "segment": "型号段",
            "brand": "品牌",
            "units": "销量",
            "revenue": "销售额",
            "segment_units": "型号段总销量",
            "segment_revenue": "型号段总销售额",
            "share_units": "销量份额",
            "share_revenue": "销售额份额",
            "asp": "ASP",
        },
        percent_cols=["销量份额", "销售额份额"],
    )

    segment_show_cols = [
        "市场",
        "型号段",
        "品牌",
        "销量",
        "销售额",
        "销量份额",
        "销售额份额",
        "ASP",
    ]
    segment_show_cols = [c for c in segment_show_cols if c in work_segment_zh.columns]

    st.dataframe(
        work_segment_zh[segment_show_cols],
        use_container_width=True,
        hide_index=True,
        column_config=make_brand_table_config(segment_show_cols),
    )

with c9:
    st.plotly_chart(
        bar_top_n(
            brand_total,
            "brand",
            "asp",
            "品牌 ASP 对比",
            n=10,
            horizontal=True,
            height=500,
        ),
        use_container_width=True,
    )

# ===== 解读 =====
section_header("数据解读")
insight_card(insight)