import pandas as pd
import streamlit as st
from utils.loaders import load_csv, load_text
from utils.helpers import show_empty, add_download_button
from utils.charts import segment_trend_chart, bar_top_n
from utils.styles import section_header, insight_card, kpi_card
from utils.styles import apply_global_styles

apply_global_styles()

trend_df = load_csv("agg_segment_month")
insight = load_text("insight_segment")

if show_empty(trend_df, "agg_segment_month.csv 为空"):
    st.stop()

work_all = trend_df.copy()
work_all["month_date"] = pd.to_datetime(work_all["month"].astype(str) + "-01", errors="coerce")
work_all["month_period"] = pd.to_datetime(work_all["month"].astype(str), format="%Y-%m", errors="coerce").dt.to_period("M")
work_all = work_all.sort_values("month_date")

month_options = (
    pd.to_datetime(work_all["month"].astype(str), format="%Y-%m", errors="coerce")
    .dropna()
    .dt.strftime("%Y-%m")
    .drop_duplicates()
    .sort_values()
    .tolist()
)

st.title("02 型号段结构")
st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
start_month = c1.selectbox("开始月份", month_options, index=0, key="segment_start_month")
end_month = c2.selectbox("结束月份", month_options, index=len(month_options) - 1, key="segment_end_month")

start_period = pd.Period(start_month, freq="M")
end_period = pd.Period(end_month, freq="M")

if start_period > end_period:
    st.warning("开始月份不能晚于结束月份")
    st.stop()

work_all = work_all[
    (work_all["month_period"] >= start_period) &
    (work_all["month_period"] <= end_period)
].copy()

if work_all.empty:
    st.warning("当前筛选范围内暂无数据")
    st.stop()

segment_options = ["全部"] + sorted([x for x in work_all["segment"].dropna().unique().tolist()])
selected_segment = c3.selectbox("选择型号段", segment_options)

work = work_all.copy()
if selected_segment != "全部":
    work = work[work["segment"] == selected_segment].copy()

summary_work = (
    work_all.groupby(["market", "segment"], as_index=False)
    .agg(units=("units", "sum"), revenue=("revenue", "sum"))
)

market_total = (
    work_all.groupby(["market"], as_index=False)
    .agg(market_units=("units", "sum"), market_revenue=("revenue", "sum"))
)

summary_work = summary_work.merge(market_total, on="market", how="left")
summary_work["asp"] = summary_work["revenue"] / summary_work["units"]
summary_work["share_units"] = summary_work["units"] / summary_work["market_units"]
summary_work["share_revenue"] = summary_work["revenue"] / summary_work["market_revenue"]
summary_work["share_units_pct"] = summary_work["share_units"] * 100
summary_work["share_revenue_pct"] = summary_work["share_revenue"] * 100

if selected_segment != "全部":
    summary_work = summary_work[summary_work["segment"] == selected_segment].copy()

summary_work = summary_work.sort_values("units", ascending=False)

top_segment = summary_work.sort_values("units", ascending=False).iloc[0]["segment"] if not summary_work.empty else "-"
top_units = summary_work.sort_values("units", ascending=False).iloc[0]["units"] if not summary_work.empty else 0
top_asp_segment = summary_work.sort_values("asp", ascending=False).iloc[0]["segment"] if not summary_work.empty else "-"
top_asp = summary_work.sort_values("asp", ascending=False).iloc[0]["asp"] if not summary_work.empty else 0

c1, c2, c3 = st.columns([0.8, 1.1, 1.1])
with c1:
    kpi_card("型号段数量", f"{summary_work['segment'].nunique():,}", "当前筛选范围累计")
with c2:
    kpi_card("走量第一型号段", f"{top_segment} ｜ {int(top_units):,}", "当前筛选范围累计")
with c3:
    kpi_card("高 ASP 型号段", f"{top_asp_segment} ｜ ${top_asp:,.2f}", "当前筛选范围累计")

st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

section_header("型号段月销量趋势")
st.plotly_chart(segment_trend_chart(work, "units", ""), use_container_width=True)

section_header("型号段月销售额趋势")
st.plotly_chart(segment_trend_chart(work, "revenue", ""), use_container_width=True)

c6, c7 = st.columns([1.5, 1],gap="medium")
with c6:
    section_header("型号段汇总表", "看不同型号段的 ASP 与市占率分布情况")

    summary_zh = summary_work.rename(columns={
        "market": "市场",
        "segment": "型号段",
        "units": "销量",
        "revenue": "销售额",
        "market_units": "市场总销量",
        "market_revenue": "市场总销售额",
        "share_units": "销量份额",
        "share_revenue": "销售额份额",
        "share_units_pct": "销量市占率(%)",
        "share_revenue_pct": "销售额市占率(%)",
        "asp": "ASP",
    }).copy()

    if "销量份额" in summary_zh.columns:
        summary_zh["销量份额"] = summary_zh["销量份额"] * 100
    if "销售额份额" in summary_zh.columns:
        summary_zh["销售额份额"] = summary_zh["销售额份额"] * 100

    show_cols = ["市场", "型号段", "销量", "销售额", "销量份额", "销售额份额", "ASP"]
    show_cols = [c for c in show_cols if c in summary_zh.columns]

    st.dataframe(
        summary_zh[show_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "市场": st.column_config.TextColumn("市场"),
            "型号段": st.column_config.TextColumn("型号段"),
            "销量": st.column_config.NumberColumn("销量", format="%.0f", alignment="center"),
            "销售额": st.column_config.NumberColumn("销售额", format="%.2f", alignment="center"),
            "销量份额": st.column_config.NumberColumn("销量份额", format="%.2f%%", alignment="center"),
            "销售额份额": st.column_config.NumberColumn("销售额份额", format="%.2f%%", alignment="center"),
            "ASP": st.column_config.NumberColumn("ASP", format="%.2f", alignment="center"),
        },
    )
    add_download_button(summary_work, "segment_summary.csv", "下载型号段汇总")

with c7:
    if not summary_work.empty:
        if selected_segment == "全部":
            st.plotly_chart(
                bar_top_n(summary_work, "segment", "asp", "高 ASP 型号段", n=min(10, len(summary_work)), height=420),
                use_container_width=True,
            )
        else:
            seg_row = summary_work.iloc[0]
            st.markdown("#### 当前型号段摘要")
            st.markdown(f"**型号段：** {seg_row['segment']}")
            st.markdown(f"**ASP：** ${seg_row['asp']:,.2f}")
            st.markdown(f"**销量：** {int(seg_row['units']):,} ｜ **销售额：** ${seg_row['revenue']:,.2f}")
            st.markdown(f"**销量份额：** {seg_row['share_units_pct']:.2f}% ｜ **销售额份额：** {seg_row['share_revenue_pct']:.2f}%")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
section_header("数据解读")
insight_card(insight)