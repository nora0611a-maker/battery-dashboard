import pandas as pd
import streamlit as st
from utils.loaders import load_csv, load_text
from utils.helpers import show_empty, add_download_button
from utils.charts import bar_top_n
from utils.styles import section_header, insight_card, apply_global_styles

apply_global_styles()

st.title("04 ASIN运营监控")
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

asin_master = load_csv("dashboard_asin_master")
brand_new = load_csv("dashboard_brand_new_summary")
insight = load_text("insight_asin")

if show_empty(asin_master, "dashboard_asin_master.csv 为空"):
    st.stop()


def rename_for_display(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.rename(columns=mapping).copy()


def coerce_bool(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype="boolean")
    s = series.copy()
    if str(s.dtype).lower() in {"bool", "boolean"}:
        return s.fillna(False).astype(bool)
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"])


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
    if "最新月份" in show_cols:
        column_config["最新月份"] = st.column_config.TextColumn("最新月份")
    if "上架月份" in show_cols:
        column_config["上架月份"] = st.column_config.TextColumn("上架月份")

    num_formats = {
        "累计销量": ("%.0f", "center"),
        "累计销售额": ("%.2f", "center"),
        "ASP": ("%.2f", "center"),
        "最新月销量": ("%.0f", "center"),
        "最新月销售额": ("%.2f", "center"),
        "销量增长率(%)": ("%.2f%%", "center"),
        "销售额增长率(%)": ("%.2f%%", "center"),
        "新品数": ("%.0f", "center"),
        "新品销量": ("%.0f", "center"),
        "新品销售额": ("%.2f", "center"),
        "平均新品销量": ("%.2f", "center"),
        "平均新品销售额": ("%.2f", "center"),
        "起量新品数": ("%.0f", "center"),
        "新品成功率(%)": ("%.2f%%", "center"),
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


brand_options = ["全部"] + sorted([x for x in asin_master["brand"].dropna().unique().tolist()])
seg_options = ["全部"] + sorted([x for x in asin_master["segment"].dropna().unique().tolist()])
row_options = [10, 20, 30, 50, 100]

c1, c2, c3 = st.columns([1, 1, 0.8])
selected_brand = c1.selectbox("选择品牌", brand_options)
selected_segment = c2.selectbox("选择型号段", seg_options)
top_n = c3.selectbox("显示行数", row_options, index=2)

work = asin_master.copy()
brand_new_work = brand_new.copy()

if selected_brand != "全部":
    work = work[work["brand"] == selected_brand].copy()
    if not brand_new_work.empty:
        brand_new_work = brand_new_work[brand_new_work["brand"] == selected_brand].copy()

if selected_segment != "全部":
    work = work[work["segment"] == selected_segment].copy()

# 统一中文映射
master_zh = rename_for_display(work, {
    "market": "市场",
    "asin": "ASIN",
    "brand": "品牌",
    "segment": "型号段",
    "title": "标题",
    "detail_url": "链接",
    "launch_date": "上架时间",
    "launch_month": "上架月份",
    "launch_stage": "上架阶段",
    "rating": "评分",
    "review_count": "评分数",
    "total_units": "累计销量",
    "total_revenue": "累计销售额",
    "asp": "ASP",
    "latest_month": "最新月份",
    "latest_units": "最新月销量",
    "latest_revenue": "最新月销售额",
    "units_growth_pct": "销量增长率(%)",
    "revenue_growth_pct": "销售额增长率(%)",
    "is_new": "是否新品",
    "new_status": "新品状态",
})

numeric_cols = [
    "累计销量",
    "累计销售额",
    "ASP",
    "最新月销量",
    "最新月销售额",
    "销量增长率(%)",
    "销售额增长率(%)",
    "评分",
    "评分数",
]

for col in numeric_cols:
    if col in master_zh.columns:
        master_zh[col] = pd.to_numeric(master_zh[col], errors="coerce")

if "销量增长率(%)" in master_zh.columns:
    master_zh["销量增长率(%)"] = master_zh["销量增长率(%)"] * 100
if "销售额增长率(%)" in master_zh.columns:
    master_zh["销售额增长率(%)"] = master_zh["销售额增长率(%)"] * 100
if "是否新品" in master_zh.columns:
    master_zh["是否新品"] = coerce_bool(master_zh["是否新品"])

section_header("头部 ASIN", "优先看全市场和分型号段的头部 ASIN。")

c4, c5 = st.columns(2)
with c4:
    st.markdown("##### 全市场 Top ASIN")
    top_total = master_zh.sort_values("累计销售额", ascending=False).head(top_n).copy()
    show_df(top_total, ["市场", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"])

with c5:
    st.markdown("##### 分型号段 Top ASIN")
    top_segment = master_zh.sort_values(["型号段", "累计销售额"], ascending=[True, False]).copy()
    if selected_segment == "全部":
        top_segment = top_segment.groupby("型号段", group_keys=False).head(min(10, top_n))
    else:
        top_segment = top_segment.head(top_n)

    if top_segment.empty:
        st.info("暂无分型号段数据")
    else:
        show_df(top_segment, ["市场", "型号段", "品牌", "ASIN", "链接", "累计销量", "累计销售额", "ASP"])

section_header("新品与上新", "看新品质量与品牌上新效果。")

c6, c7 = st.columns([2, 1])
with c6:
    st.markdown("##### 新品 ASIN 清单")
    new_df = master_zh[master_zh["是否新品"] == True].sort_values("最新月销售额", ascending=False).head(top_n).copy()
    if new_df.empty:
        st.info("当前口径下暂无新品数据")
    else:
        show_df(new_df, [
            "市场", "型号段", "品牌", "ASIN", "链接",
            "上架月份", "上架阶段", "新品状态", "最新月份", "最新月销售额"
        ])

with c7:
    if not brand_new_work.empty:
        brand_new_zh = rename_for_display(brand_new_work, {
            "brand": "brand",
            "new_asin_revenue": "new_asin_revenue",
        })
        st.plotly_chart(
            bar_top_n(
                brand_new_zh,
                "brand",
                "new_asin_revenue",
                "品牌上新表现",
                n=min(10, len(brand_new_zh)),
                horizontal=True,
                height=380,
            ),
            use_container_width=True,
        )

section_header("ASIN 异动榜", "识别近期增长最快的 ASIN。")

growth_df = master_zh[master_zh["销售额增长率(%)"].notna()].sort_values("销售额增长率(%)", ascending=False).head(top_n).copy()
if growth_df.empty:
    st.info("暂无 ASIN 异动数据")
else:
    show_df(growth_df, [
        "市场", "型号段", "品牌", "ASIN", "链接",
        "最新月份", "最新月销售额", "销售额增长率(%)", "销量增长率(%)"
    ])

add_download_button(work, "dashboard_asin_master.csv", "下载 ASIN 主表")

section_header("数据解读")
insight_card(insight)
