# # Config (ASCII)
# from pathlib import Path
# ENGINE_DIR = Path(__file__).parent
# INPUT_DIR  = ENGINE_DIR.parent / "input"
# OUTPUT_DIR = ENGINE_DIR.parent / "APS_Market_Intelligence_Live"
# ASSETS_DIR = ENGINE_DIR.parent / "assets"
# LOGO_FILE = "APS_Master_Logo.png"
# STRICT_SCHEMA = True
# REQUIRED_HEADERS = [
#     "Owner Name","Mail Address","Property Address","City","State","ZIP",
#     "EstValue","TotalLoanBal","LastLoanDate",
#     "Equity %","LTV %","Loan_Age_Mo","APS_Score (v2.0)","APS_Tier","CCI"
# ]


# APS Config - Paths and Feed Configuration
from pathlib import Path

# Directory Configuration
ENGINE_DIR = Path(__file__).parent
INPUT_DIR = ENGINE_DIR.parent / "input"
OUTPUT_DIR = ENGINE_DIR.parent / "APS_Market_Intelligence_Live"
ASSETS_DIR = ENGINE_DIR.parent / "assets"
LOGO_FILE = "APS_Master_Logo.png"

# Feed Schema Settings
STRICT_SCHEMA = True
REQUIRED_HEADERS = [
    "Owner Name", "Mail Address", "Property Address", "City", "State", "ZIP",
    "EstValue", "TotalLoanBal", "LastLoanDate",
    "Equity %", "LTV %", "Loan_Age_Mo", "APS_Score (v2.0)", "APS_Tier", "CCI"
]

# ==================== FEED CONFIGURATIONS ====================