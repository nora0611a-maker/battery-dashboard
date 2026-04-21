import pandas as pd
import streamlit as st
from utils.loaders import load_csv, load_text
from utils.helpers import show_empty, fmt_int, fmt_money
from utils.charts import market_combo_chart, asp_line_chart
from utils.styles import section_header, kpi_card, insight_card, apply_global_styles

apply_global_styles()
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

st.title("01 市场总览")

df = load_csv("agg_market_month")
insight = load_text("insight_home")

if show_empty(df, "agg_market_month.csv 为空"):
    st.stop()

df = df.copy()
df["month_date"] = pd.to_datetime(df["month"].astype(str) + "-01", errors="coerce")
df = df.sort_values("month_date")

# ===== 时间范围筛选 =====
min_date = df["month_date"].min().date()
max_date = df["month_date"].max().date()

date_range = st.slider(
    "选择时间范围",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM",
)

start_date, end_date = date_range

work = df[
    (df["month_date"].dt.date >= start_date) &
    (df["month_date"].dt.date <= end_date)
].copy()

if work.empty:
    st.warning("当前筛选范围内暂无数据")
    st.stop()

# ===== KPI =====
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

st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

# ===== 图表 =====
section_header("月销量与销售额趋势")
st.plotly_chart(market_combo_chart(work), use_container_width=True)

section_header("月 ASP 趋势")
c4, c5 = st.columns([3, 1], gap="medium")
with c4:
    st.plotly_chart(asp_line_chart(work), use_container_width=True)

with c5:
    latest = work.sort_values("month_date").iloc[-1]
    prev = work.sort_values("month_date").iloc[-2] if len(work) >= 2 else None

    st.markdown("#### 区间摘要")
    st.markdown(f"**最新月份：** {latest['month']}")
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

# ===== 解读 =====
section_header("数据解读")
insight_card(insight)