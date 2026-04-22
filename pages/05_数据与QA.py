import streamlit as st
from utils.loaders import load_csv
from utils.helpers import show_empty, make_brand_table_config
from utils.styles import apply_global_styles, section_header

apply_global_styles()

st.title("05 数据与 QA")
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

qa = load_csv("qa_report")
coverage = load_csv("mapping_coverage")
inactive = load_csv("inactive_asin_in_window")

section_header("QA 报告")
if not show_empty(qa, "qa_report.csv 为空"):
    qa_zh = qa.rename(columns={
        "check_name": "检查项",
        "check_value": "检查值",
        "status": "状态",
    })
    st.dataframe(qa_zh, use_container_width=True, hide_index=True, column_config=make_brand_table_config(list(qa_zh.columns)))

section_header("映射覆盖率")
if not show_empty(coverage, "mapping_coverage.csv 为空"):
    coverage_zh = coverage.rename(columns={
        "segment_raw": "原型号段",
        "product_asin_count": "产品ASIN数",
        "source_mapped_asin_count": "源表映射成功ASIN数",
        "active_asin_count": "窗口内激活ASIN数",
        "source_mapping_rate": "源表映射率",
        "active_window_rate": "窗口内激活率",
    }).copy()
    if "源表映射率" in coverage_zh.columns:
        coverage_zh["源表映射率"] = coverage_zh["源表映射率"] * 100
    if "窗口内激活率" in coverage_zh.columns:
        coverage_zh["窗口内激活率"] = coverage_zh["窗口内激活率"] * 100
    st.dataframe(coverage_zh, use_container_width=True, hide_index=True, column_config=make_brand_table_config(list(coverage_zh.columns)))

section_header("窗口内未激活 ASIN")
if not show_empty(inactive, "inactive_asin_in_window.csv 为空"):
    inactive_zh = inactive.rename(columns={
        "segment_raw": "原型号段",
        "asin": "ASIN",
        "brand": "品牌",
        "model": "型号",
        "sku": "SKU",
        "title": "标题",
        "detail_url": "链接",
        "reason": "原因",
    })
    show_cols = ["原型号段", "品牌", "ASIN", "型号", "SKU", "标题", "链接", "原因"]
    show_cols = [c for c in show_cols if c in inactive_zh.columns]
    st.dataframe(inactive_zh[show_cols], use_container_width=True, hide_index=True, column_config=make_brand_table_config(show_cols))
