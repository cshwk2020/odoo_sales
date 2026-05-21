import os
import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
import xmlrpc.client
import chromadb
from .config import ODOO_BASE_URL
from .vault_utils import vault_get_odoo_user, vault_get_odoo_pass

# -----------------------------
# 0. CONFIGURATION & PATHS
# -----------------------------
PATH_BASE = "/Volumes/sdcard/PORTFOLIO_2026/PY3.10_BASE"
PATH_MODEL = f"{PATH_BASE}/embedding_model/all-MiniLM-L6-v2"
PATH_CHROMA_STORE = f"{PATH_BASE}/embedding_chrome_store/all-MiniLM-L6-v2"

URL = ODOO_BASE_URL
DB = "odoo"
USERNAME = vault_get_odoo_user()
PASSWORD = vault_get_odoo_pass()

# -----------------------------
# 1. EMBEDDING LOGIC
# -----------------------------
print("Loading Model and Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(PATH_MODEL)
model = AutoModel.from_pretrained(PATH_MODEL)

def get_embedding(text):
    """Encodes text and performs Mean Pooling."""
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        model_output = model(**inputs)
    
    token_embeddings = model_output[0]
    mask = inputs['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * mask, 1)
    sum_mask = torch.clamp(mask.sum(1), min=1e-9)
    
    embedding = sum_embeddings / sum_mask
    return F.normalize(embedding, p=2, dim=1).tolist()[0]

# -----------------------------
# 2. CONNECT TO ODOO
# -----------------------------
print("Connecting to Odoo...")
try:
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    products = models.execute_kw(
        DB, uid, PASSWORD,
        'product.product', 'search_read',
        [[]], 
        {'fields': ['id', 'name', 'default_code', 'description', 'qty_available']}
    )
    print(f"Fetched {len(products)} products.")

except Exception as e:
    print(f"Odoo Error: {e}")
    products = []

# -----------------------------
# 3. SETUP CHROMADB
# -----------------------------
os.makedirs(PATH_CHROMA_STORE, exist_ok=True)
client = chromadb.PersistentClient(path=PATH_CHROMA_STORE)
#collection = client.get_or_create_collection(name="odoo_products")

# 如果 collection 已存在 → delete
collections = client.list_collections()
if any(c.name == "odoo_products" for c in collections):
    print("Deleting existing collection 'odoo_products'...")
    client.delete_collection("odoo_products")

#
collection = client.get_or_create_collection(name="odoo_products")


# -----------------------------
# 4. UPSERT WITH MERGE LOGIC (by default_code)
# -----------------------------
print("Syncing...")

merged_products = {}

for p in products:
    code = p.get("default_code") or f"NO_CODE_{p['id']}"
    qty = p.get("qty_available", 0)
    text = f"{p.get('name') or ''} {code} {p.get('description') or ''}".strip()
    name = p.get("name")
    
    if code in merged_products:
        merged_products[code]["qty_available"] += qty
    else:
        merged_products[code] = {
            "name": name,
            "text": text,
            "vector": get_embedding(text),
            "odoo_id": p["id"],   # keep one id (first seen)
            "default_code": code,
            "qty_available": qty
        }

# Upsert merged results
for code, data in merged_products.items():
    collection.upsert(
        ids=[code],  # use default_code as unique id
        embeddings=[data["vector"]],
        documents=[data["text"]],
        metadatas=[{
            "odoo_id": data["odoo_id"],
            "default_code": data["default_code"],
            "qty_available": data["qty_available"],
            "odoo_name": data["name"]
        }]
    )
    print(f"Upserted {code}: qty={data['qty_available']}")


print(f"Sync complete. Total unique products: {collection.count()}")

# -----------------------------
# 5. TEST QUERY
# -----------------------------
#query_text = "cot"
#query_vec = get_embedding(query_text)
#results = collection.query(query_embeddings=[query_vec], n_results=1)
#print(f"\nTop Match Content: {results['documents'][0][0]}")
