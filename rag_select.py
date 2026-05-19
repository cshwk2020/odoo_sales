import os
import json
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer

PATH_BASE = "/Volumes/linuxkernel/PY3.10_BASE"
PATH_MODEL = f"{PATH_BASE}/embedding_model/all-MiniLM-L6-v2"
PATH_CHROMA_STORE = f"{PATH_BASE}/embedding_chrome_store/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(PATH_MODEL)
client = chromadb.PersistentClient(path=PATH_CHROMA_STORE)
collection = client.get_or_create_collection(name="odoo_products")

def get_embedding(text: str):
    return embedding_model.encode(text).tolist()

def rag_filter(parsed_items: List[Dict[str, Any]], per_item_limit: int = 3) -> List[Dict[str, Any]]:
    results = []

    for item in parsed_items:
        print('item: ', item)
        status = item.get("status")
        qty = item.get("qty", 1)

        query_text = " ".join(item["candidates"])

        query_vec = get_embedding(query_text)
        print('query_text: ', query_text)
        rag_matches = []

        try:
            res = collection.query(
                query_embeddings=[query_vec],
                n_results=per_item_limit  # 直接用 per_item_limit 控制
            )

            for i in range(len(res["ids"][0])):
               
                distance = res["distances"][0][i]
                 
             
                rag_matches.append({
                    "product": res["documents"][0][i],
                    "code": res["metadatas"][0][i].get("default_code"),
                    "odoo_id": res["metadatas"][0][i].get("odoo_id"),
                    "qty_available": res["metadatas"][0][i].get("qty_available"),
                    "distance": distance,        
                })

            # keep only the one with min distance
            if rag_matches:
                
                print("candidates list: ", rag_matches)
                best_match = min(rag_matches, key=lambda x: x["distance"])
                print("best_match: ", best_match)
                rag_matches = [best_match]
                
                print("------------------------------")

        except Exception as e:
            print(f"Query error for input={item['input']}: {e}")
            rag_matches = []

        # 規則處理
        if status == "exact":
            item["qty"] = 1
            rag_matches = rag_matches[:1]  # top-1
        elif status == "ambiguous":
            #rag_matches = rag_matches[:min(qty, per_item_limit)]
            rag_matches = rag_matches[:per_item_limit]
        elif status == "not_found":
            rag_matches = []

        item["rag_matches"] = rag_matches
        results.append(item)

    return results



if __name__ == "__main__":
    parsed_items = [
        {"input": "aluminum fold", "candidates": ["aluminum foil", "aluminum fold"], "qty": 2, "status": "ambiguous"},
        {"input": "coffee maker", "candidates": ["coffee maker"], "qty": 1, "status": "exact"},
        {"input": "glass jar", "candidates": ["glass jar"], "qty": 1, "status": "exact"},
        {"input": "formal shirt", "candidates": ["formal shirt"], "qty": 1, "status": "exact"}
    ]

    enriched = rag_filter(parsed_items, per_item_limit=10)
    print(json.dumps(enriched, indent=2))
