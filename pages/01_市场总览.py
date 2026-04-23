import pandas as pd
import streamlit as st
from utils.loaders import load_csv, load_text
from utils.helpers import show_empty, fmt_int, fmt_money
from utils.charts import market_combo_chart, asp_line_chart
from utils.styles import section_header, kpi_card, insight_card, apply_global_styles

apply_global_styles()
# st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

df = load_csv("agg_market_month")
insight = load_text("insight_home")

if show_empty(df, "agg_market_month.csv 为空"):
    st.stop()

df = df.copy()
df["month_date"] = pd.to_datetime(df["month"].astype(str) + "-01", errors="coerce")
df["month_period"] = pd.to_datetime(df["month"].astype(str), format="%Y-%m", errors="coerce").dt.to_period("M")
df["year"] = df["month_date"].dt.year
df = df.sort_values("month_date")

month_options = (
    pd.to_datetime(df["month"].astype(str), format="%Y-%m", errors="coerce")
    .dropna()
    .dt.strftime("%Y-%m")
    .drop_duplicates()
    .sort_values()
    .tolist()
)

title_col, filter_col = st.columns([1.4, 1.2], gap="medium")
with title_col:
    st.title("01 市场总览")
with filter_col:
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    c_start, c_end, c_grain = st.columns([1, 1, 0.8])
    with c_start:
        start_month = st.selectbox(
            "开始月份",
            month_options,
            index=0,
            key="home_start_month",
        )
    with c_end:
        end_month = st.selectbox(
            "结束月份",
            month_options,
            index=len(month_options) - 1,
            key="home_end_month",
        )
    with c_grain:
        grain = st.selectbox(
            "维度",
            ["月", "年"],
            index=0,
            key="home_grain",
        )

start_period = pd.Period(start_month, freq="M")
end_period = pd.Period(end_month, freq="M")

if start_period > end_period:
    st.warning("开始月份不能晚于结束月份")
    st.stop()

work = df[
    (df["month_period"] >= start_period) &
    (df["month_period"] <= end_period)
].copy()

if work.empty:
    st.warning("当前筛选范围内暂无数据")
    st.stop()

total_units = work["units"].sum()
total_revenue = work["revenue"].sum()
avg_asp = total_revenue / total_units if total_units > 0 else 0

c1, c2, c3 = st.columns(3, gap="small")
with c1:
    kpi_card("销量", fmt_int(total_units), "当前筛选范围累计")
with c2:
    kpi_card("销售额", fmt_money(total_revenue), "当前筛选范围累计")
with c3:
    kpi_card("ASP", fmt_money(avg_asp), "销售额 / 销量")

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ===== 图表口径切换：月 / 年 =====
if grain == "月":
    chart_work = work.copy().sort_values("month_date")
    chart_work["label"] = chart_work["month"].astype(str)
    trend_title = "月销量与销售额趋势"
    asp_title = "月 ASP 趋势"
    latest_label_name = "最新月份"
else:
    chart_work = (
        work.groupby("year", as_index=False)
        .agg(
            units=("units", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("year")
    )
    chart_work["asp"] = chart_work["revenue"] / chart_work["units"]
    chart_work["month_date"] = pd.to_datetime(chart_work["year"].astype(str) + "-01-01", errors="coerce")
    chart_work["label"] = chart_work["year"].astype(str)
    trend_title = "年销量与销售额趋势"
    asp_title = "年 ASP 趋势"
    latest_label_name = "最新年份"

section_header(trend_title)
st.plotly_chart(market_combo_chart(chart_work), use_container_width=True)

section_header(asp_title)
c4, c5 = st.columns([3, 1], gap="medium")
with c4:
    st.plotly_chart(asp_line_chart(chart_work), use_container_width=True)

with c5:
    latest = chart_work.sort_values("month_date").iloc[-1]
    prev = chart_work.sort_values("month_date").iloc[-2] if len(chart_work) >= 2 else None

    st.markdown("#### 区间摘要")
    st.markdown(f"**{latest_label_name}：** {latest['label']}")
    st.markdown(f"**销量：** {fmt_int(latest['units'])}")
    st.markdown(f"**销售额：** {fmt_money(latest['revenue'])}")
    st.markdown(f"**ASP：** {fmt_money(latest['asp'])}")

    if prev is not None:
        units_chg = (latest["units"] / prev["units"] - 1) * 100 if prev["units"] > 0 else None
        rev_chg = (latest["revenue"] / prev["revenue"] - 1) * 100 if prev["revenue"] > 0 else None
        if units_chg is not None:
            st.markdown(f"**销量环比：** {units_chg:+.1f}%")
        if rev_chg is not None:
            st.markdown(f"**销售额环比：** {rev_chg:+.1f}%")

section_header("数据解读")
insight_card(insight)