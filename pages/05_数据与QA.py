import streamlit as st
from utils.loaders import load_csv
from utils.helpers import show_empty
from utils.styles import apply_global_styles,section_header
apply_global_styles()

st.title("05 数据与 QA")
st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

qa = load_csv("qa_report")
coverage = load_csv("mapping_coverage")
unmapped = load_csv("unmapped_asin")

section_header("QA 报告")
if not show_empty(qa, "qa_report.csv 为空"):
    st.dataframe(qa, use_container_width=True, hide_index=True)

section_header("映射覆盖率")
if not show_empty(coverage, "mapping_coverage.csv 为空"):
    st.dataframe(coverage, use_container_width=True, hide_index=True)

section_header("未匹配 ASIN")
if not show_empty(unmapped, "unmapped_asin.csv 为空"):
    st.dataframe(unmapped, use_container_width=True, hide_index=True)