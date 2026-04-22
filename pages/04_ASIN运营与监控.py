import pandas as pd
import streamlit as st
from utils.loaders import load_csv, load_text
from utils.helpers import show_empty, add_download_button
from utils.charts import bar_top_n
from utils.styles import section_header, insight_card, apply_global_styles

apply_global_styles()

asin_month = load_csv("agg_asin_month")
asin_total = load_csv("agg_asin_market_total")
asin_segment_total = load_csv("agg_asin_segment_total")
asin_new = load_csv("agg_asin_new_month")
brand_new = load_csv("agg_brand_new_month")
asin_growth = load_csv("agg_asin_growth_month")
insight = load_text("insight_asin")

if show_empty(asin_month, "agg_asin_month.csv 为空"):
    st.stop()


def rename_for_display(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    if df is None or df.empty:
        return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    return df.rename(columns=mapping).copy()


def show_df(df: pd.DataFrame, show_cols: list[str]) -> None:
    show_cols = [c for c in show_cols if c in df.columns]

    column_config = {}
    if "市场" in show_cols:
        column_config["市场"] = st.column_config.TextColumn("市场")
    if "品牌" in show_cols:
        column_config["品牌"] = st.column_config.TextColumn("品牌")
    if "型号段" in show_cols:
        column_config["型号段"] = st.column_config.TextColumn("型号段")
    if "ASIN" in show_cols:
        column_config["ASIN"] = st.column_config.TextColumn("ASIN")
    if "链接" in show_cols:
        column_config["链接"] = st.column_config.LinkColumn("链接", display_text="详情")
    if "标题" in show_cols:
        column_config["标题"] = st.column_config.TextColumn("标题")
    if "上架阶段" in show_cols:
        column_config["上架阶段"] = st.column_config.TextColumn("上架阶段")
    if "新品状态" in show_cols:
        column_config["新品状态"] = st.column_config.TextColumn("新品状态")
    if "月份" in show_cols:
        column_config["月份"] = st.column_config.TextColumn("月份")
    if "当月" in show_cols:
        column_config["当月"] = st.column_config.TextColumn("当月")
    if "上月" in show_cols:
        column_config["上月"] = st.column_config.TextColumn("上月")
    if "上架月份" in show_cols:
        column_config["上架月份"] = st.column_config.TextColumn("上架月份")

    num_formats = {
        "累计销量": ("%.0f", "center"),
        "累计销售额": ("%.2f", "center"),
        "ASP": ("%.2f", "center"),
        "当月销量": ("%.0f", "center"),
        "当月销售额": ("%.2f", "center"),
        "销量增长率(%)": ("%.2f%%", "center"),
        "销售额增长率(%)": ("%.2f%%", "center"),
        "评分": ("%.2f", "center"),
        "评分数": ("%.0f", "center"),
    }
    for col, (fmt, align) in num_formats.items():
        if col in show_cols:
            column_config[col] = st.column_config.NumberColumn(col, format=fmt, alignment=align)

    st.dataframe(
        df[show_cols],
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )


asin_month = asin_month.copy()
asin_month["month_date"] = pd.to_datetime(asin_month["month"].astype(str) + "-01", errors="coerce")
asin_month = asin_month.sort_values(["month_date", "revenue"], ascending=[True, False])

month_options = (
    pd.to_datetime(asin_month["month"].astype(str), format="%Y-%m", errors="coerce")
    .dropna()
    .dt.strftime("%Y-%m")
    .drop_duplicates()
    .sort_values()
    .tolist()
)

st.title("04 ASIN运营监控")
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

# ===== 品牌/型号联动 =====
brand_options = ["全部"] + sorted([x for x in asin_month["brand"].dropna().unique().tolist()])

c1, c2, c3, c4 = st.columns([1, 1, 1, 0.8])
selected_month = c1.selectbox("选择月份", month_options, index=len(month_options) - 1 if month_options else 0)
selected_brand = c2.selectbox("选择品牌", brand_options)

segment_base = asin_month[asin_month["month"] == selected_month].copy()
if selected_brand != "全部":
    segment_base = segment_base[segment_base["brand"] == selected_brand].copy()

seg_options = ["全部"] + sorted([x for x in segment_base["segment"].dropna().unique().tolist()])
selected_segment = c3.selectbox("选择型号段", seg_options)

row_options = [10, 20, 30, 50, 100]
top_n = c4.selectbox("显示行数", row_options, index=2)

month_work = asin_month[asin_month["month"] == selected_month].copy()
if selected_brand != "全部":
    month_work = month_work[month_work["brand"] == selected_brand].copy()
if selected_segment != "全部":
    month_work = month_work[month_work["segment"] == selected_segment].copy()

month_zh = rename_for_display(month_work, {
    "market": "市场",
    "month": "月份",
    "asin": "ASIN",
    "brand": "品牌",
    "segment": "型号段",
    "title": "标题",
    "detail_url": "链接",
    "launch_date": "上架时间",
    "launch_month": "上架月份",
    "rating": "评分",
    "review_count": "评分数",
    "units": "当月销量",
    "revenue": "当月销售额",
    "asp": "ASP",
})

for col in ["市场", "月份", "ASIN", "品牌", "型号段", "标题", "链接", "上架月份", "当月销量", "当月销售额", "ASP", "评分", "评分数"]:
    if col not in month_zh.columns:
        month_zh[col] = pd.NA

for col in ["当月销量", "当月销售额", "ASP", "评分", "评分数"]:
    month_zh[col] = pd.to_numeric(month_zh[col], errors="coerce")

section_header("头部 ASIN", "优先看所选月份下的全市场和分型号段头部 ASIN。")

c5, c6 = st.columns(2)
with c5:
    st.markdown("##### 当月全市场 Top ASIN")
    top_total = month_zh.sort_values("当月销售额", ascending=False).head(top_n).copy()
    show_df(top_total, ["市场", "月份", "品牌", "ASIN", "链接", "当月销量", "当月销售额", "ASP"])

with c6:
    st.markdown("##### 当月分型号段 Top ASIN")
    top_segment = month_zh.sort_values(["型号段", "当月销售额"], ascending=[True, False]).copy()
    if selected_segment == "全部":
        top_segment = top_segment.groupby("型号段", group_keys=False).head(min(10, top_n))
    else:
        top_segment = top_segment.head(top_n)
    if top_segment.empty:
        st.info("暂无分型号段数据")
    else:
        show_df(top_segment, ["市场", "月份", "型号段", "品牌", "ASIN", "链接", "当月销量", "当月销售额", "ASP"])

section_header("新品与上新", "看当前月份新品质量与品牌上新效果。")

c7, c8 = st.columns([2, 1])
with c7:
    st.markdown("##### 新品 ASIN 清单")
    new_work = asin_new.copy()
    if not new_work.empty:
        new_work = new_work[new_work["month"] == selected_month].copy()
        if selected_brand != "全部":
            new_work = new_work[new_work["brand"] == selected_brand].copy()
        if selected_segment != "全部":
            new_work = new_work[new_work["segment"] == selected_segment].copy()

    new_zh = rename_for_display(new_work, {
        "market": "市场",
        "month": "月份",
        "asin": "ASIN",
        "brand": "品牌",
        "segment": "型号段",
        "title": "标题",
        "detail_url": "链接",
        "launch_date": "上架时间",
        "launch_month": "上架月份",
        "new_status": "新品状态",
        "month_units": "当月销量",
        "month_revenue": "当月销售额",
    })

    for col in ["市场", "月份", "型号段", "品牌", "ASIN", "链接", "上架月份", "新品状态", "当月销量", "当月销售额"]:
        if col not in new_zh.columns:
            new_zh[col] = pd.NA

    for col in ["当月销量", "当月销售额"]:
        new_zh[col] = pd.to_numeric(new_zh[col], errors="coerce")

    if new_zh.empty:
        st.info("当前口径下暂无新品数据")
    else:
        show_df(
            new_zh.sort_values("当月销售额", ascending=False).head(top_n).copy(),
            ["市场", "月份", "型号段", "品牌", "ASIN", "链接", "上架月份", "新品状态", "当月销量", "当月销售额"]
        )

with c8:
    if not brand_new.empty and selected_month == (month_options[-1] if month_options else selected_month):
        brand_new_work = brand_new.copy()
        if selected_brand != "全部":
            brand_new_work = brand_new_work[brand_new_work["brand"] == selected_brand].copy()
        st.plotly_chart(
            bar_top_n(
                brand_new_work,
                "brand",
                "new_asin_revenue",
                "品牌上新表现",
                n=min(10, len(brand_new_work)),
                horizontal=True,
                height=380,
            ),
            use_container_width=True,
        )
    else:
        st.info("品牌上新表现当前仅展示最新月结果")

section_header("ASIN 异动榜", "识别所选月份相较上月增长最快的 ASIN。")

growth_work = asin_growth.copy()
if not growth_work.empty:
    growth_work = growth_work[growth_work["current_month"] == selected_month].copy()
    if selected_brand != "全部":
        growth_work = growth_work[growth_work["brand"] == selected_brand].copy()
    if selected_segment != "全部":
        growth_work = growth_work[growth_work["segment"] == selected_segment].copy()

growth_zh = rename_for_display(growth_work, {
    "market": "市场",
    "brand": "品牌",
    "segment": "型号段",
    "asin": "ASIN",
    "detail_url": "链接",
    "current_month": "当月",
    "current_units": "当月销量",
    "current_revenue": "当月销售额",
    "prev_month": "上月",
    "units_growth_pct": "销量增长率(%)",
    "revenue_growth_pct": "销售额增长率(%)",
})

for col in ["市场", "型号段", "品牌", "ASIN", "链接", "当月", "上月", "当月销量", "当月销售额", "销量增长率(%)", "销售额增长率(%)"]:
    if col not in growth_zh.columns:
        growth_zh[col] = pd.NA

for col in ["当月销量", "当月销售额", "销量增长率(%)", "销售额增长率(%)"]:
    growth_zh[col] = pd.to_numeric(growth_zh[col], errors="coerce")

if "销量增长率(%)" in growth_zh.columns:
    growth_zh["销量增长率(%)"] = growth_zh["销量增长率(%)"] * 100
if "销售额增长率(%)" in growth_zh.columns:
    growth_zh["销售额增长率(%)"] = growth_zh["销售额增长率(%)"] * 100

if growth_zh.empty:
    st.info("暂无 ASIN 异动数据")
else:
    show_df(
        growth_zh.sort_values("销售额增长率(%)", ascending=False).head(top_n).copy(),
        ["市场", "型号段", "品牌", "ASIN", "链接", "当月", "上月", "当月销售额", "销售额增长率(%)", "销量增长率(%)"]
    )

section_header("累计视角补充", "用于复盘整个窗口周期内的累计表现。")

ct1, ct2 = st.columns(2)
with ct1:
    total_work = asin_total.copy()
    if selected_brand != "全部":
        total_work = total_work[total_work["brand"] == selected_brand].copy()
    if selected_segment != "全部":
        total_work = total_work[total_work["segment"] == selected_segment].copy()

    total_zh = rename_for_display(total_work, {
        "market": "市场",
        "asin": "ASIN",
        "brand": "品牌",
        "segment": "型号段",
        "detail_url": "链接",
        "units": "累计销量",
        "revenue": "累计销售额",
        "asp": "ASP",
    })

    for col in ["市场", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"]:
        if col not in total_zh.columns:
            total_zh[col] = pd.NA

    for col in ["累计销量", "累计销售额", "ASP"]:
        total_zh[col] = pd.to_numeric(total_zh[col], errors="coerce")

    st.markdown("##### 全周期累计 Top ASIN")
    show_df(total_zh.sort_values("累计销售额", ascending=False).head(top_n).copy(), ["市场", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"])

with ct2:
    seg_total_work = asin_segment_total.copy()
    if selected_brand != "全部":
        seg_total_work = seg_total_work[seg_total_work["brand"] == selected_brand].copy()
    if selected_segment != "全部":
        seg_total_work = seg_total_work[seg_total_work["segment"] == selected_segment].copy()

    seg_total_zh = rename_for_display(seg_total_work, {
        "market": "市场",
        "asin": "ASIN",
        "brand": "品牌",
        "segment": "型号段",
        "detail_url": "链接",
        "units": "累计销量",
        "revenue": "累计销售额",
        "asp": "ASP",
    })

    for col in ["市场", "型号段", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"]:
        if col not in seg_total_zh.columns:
            seg_total_zh[col] = pd.NA

    for col in ["累计销量", "累计销售额", "ASP"]:
        seg_total_zh[col] = pd.to_numeric(seg_total_zh[col], errors="coerce")

    st.markdown("##### 分型号段累计 Top ASIN")
    if seg_total_zh.empty:
        st.info("暂无分型号段累计数据")
    else:
        show_df(
            seg_total_zh.sort_values(["型号段", "累计销售额"], ascending=[True, False]).head(top_n).copy(),
            ["市场", "型号段", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"]
        )

c_dl1, c_dl2, _ = st.columns([1, 1, 4])
with c_dl1:
    add_download_button(month_work, f"agg_asin_month_{selected_month}.csv", "下载当月 ASIN 明细")

with c_dl2:
    add_download_button(asin_total, "agg_asin_market_total.csv", "下载累计 ASIN 总表")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
section_header("数据解读")
insight_card(insight)