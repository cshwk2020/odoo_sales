
from .vault_utils import mock_get_odoo_user, mock_get_odoo_pass, mock_get_deepseek_key
from .vault_utils import vault_get_odoo_user, vault_get_odoo_pass, vault_get_deepseek_key 

LLM_API_MODEL_VER = "deepseek-v4-flash"
LLM_API_KEY = vault_get_deepseek_key()
LLM_API_URL = "https://api.deepseek.com/chat/completions"

ODOO_BASE_URL = "http://localhost:8069"
ODOO_DB = "odoo"

PATH_BASE = "/Volumes/sdcard/PORTFOLIO_2026/PY3.10_BASE"
PATH_MODEL = f"{PATH_BASE}/embedding_model/all-MiniLM-L6-v2"
PATH_CHROMA_STORE = f"{PATH_BASE}/embedding_chrome_store/all-MiniLM-L6-v2"

TEST_PROMPT_1="i need 2 aluminum fold, please give me 1 good coffee maker, 1 glass jar, and a formal shirt"
TEST_PROMPT_2="please give 10 shiiping box, 1 eco bag, 1 pair of hiking boot"