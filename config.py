
from .vault_utils import mock_get_odoo_user, mock_get_odoo_pass, mock_get_deepseek_key
from .vault_utils import vault_get_odoo_user, vault_get_odoo_pass, vault_get_deepseek_key 
from enum import Enum

class Scenario(Enum):
    INVALID = "invalid"
    VALID = "valid"
    PARTIAL = "partial"

# REAL AI CALL OR MOCK 
MODE_REAL = True
# TEST CASES: INVALID / VALID / PARTIAL
SCENARIO = Scenario.PARTIAL


# AI DEEPSEEK
LLM_API_MODEL_VER = "deepseek-v4-flash"
LLM_API_KEY = vault_get_deepseek_key()
LLM_API_URL = "https://api.deepseek.com/chat/completions"

# ODOO SETTING
ODOO_BASE_URL = "http://localhost:8069"
ODOO_DB = "odoo"

# RAG SETTING
PATH_BASE = "/Volumes/sdcard/PORTFOLIO_2026/PY3.10_BASE"
PATH_MODEL = f"{PATH_BASE}/embedding_model/all-MiniLM-L6-v2"
PATH_CHROMA_STORE = f"{PATH_BASE}/embedding_chrome_store/all-MiniLM-L6-v2"

