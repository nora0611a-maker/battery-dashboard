# from pathlib import Path
#
# BASE_DIR = Path(__file__).resolve().parents[1]   # Streamlit_dashboard
# PROJECT_DIR = BASE_DIR.parent                    # PyCharmMiscProject
#
# DATA_DIR = PROJECT_DIR / "MarketingData" / "outputFile" / "dashboard_v2_US"
#
# PAGE_TITLE = "Battery Market Dashboard"
# PAGE_ICON = "🔋"
# LAYOUT = "wide"

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

PAGE_TITLE = "Battery Market Dashboard"
PAGE_ICON = "🔋"
LAYOUT = "wide"

# Google Sheets 配置
# 填写 Google Sheet 链接中 /d/ 与 /edit 之间的那段 ID
GSHEET_ID = "1f0pSC9usNTrd1YZaBSoZm8z3hp3UDb3JJSfYiymGy5A"
# 与同步脚本中的 GSHEET_TAB_PREFIX 保持一致
GSHEET_TAB_PREFIX = "US_"
