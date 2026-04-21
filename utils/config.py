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

# 填写 Google Sheet 文件 URL 中 /d/ 和 /edit 之间的那串 ID
GSHEET_ID = "1f0pSC9usNTrd1YZaBSoZm8z3hp3UDb3JJSfYiymGy5A"