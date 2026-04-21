import streamlit as st
from utils.config import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.styles import apply_global_styles

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
)

apply_global_styles()

st.title("🔋 Battery Market Dashboard")
st.caption("Amazon 电池市场观测平台")

st.markdown(
    """
    这是基于 `marketingAnalyze_step3_v2.py` 输出数据构建的网页看板。  
    左侧导航可查看：
    - 市场总览
    - 型号段结构
    - 品牌竞争
    - ASIN运营监控
    - 数据与QA
    """
)