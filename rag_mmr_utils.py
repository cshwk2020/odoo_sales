import os
import requests
import xmlrpc.client
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import json
from .app_utils import debugText
#
from .config import LLM_API_MODEL_VER  
from .config import LLM_API_KEY  
from .config import LLM_API_URL 
from .config import PATH_MODEL, PATH_CHROMA_STORE
from .config import MODE_REAL, SCENARIO, Scenario

# -----------------------------
# FUNCTION: run_mmr_pipeline
# -----------------------------

def run_mmr_pipeline(parsed_items): 

    if MODE_REAL:
        return real_mmr_pipeline(parsed_items)
    else:
        if SCENARIO is Scenario.INVALID:
            return mock_all_invalid__mmr_pipeline(parsed_items)
        elif SCENARIO is Scenario.VALID:
            return mock_all_valid__mmr_pipeline(parsed_items)
        elif SCENARIO is Scenario.PARTIAL:
            return mock_partial_valid__mmr_pipeline(parsed_items)


def mock_all_invalid__mmr_pipeline(parsed_items):
    # UC: ALL sale line items NOT FOUND
    # email input: need a ABCX and HEJKX thx, kk
    return [
        {'name': None, 'qty': 1, 'confidence': 0.0, 'remark': 'no candidates found', 'status': 'error', 'input': 'ABCX'}, 
        {'name': None, 'qty': 1, 'confidence': 0.0, 'remark': 'no candidates found', 'status': 'error', 'input': 'HEJKX'}
    ]


def mock_all_valid__mmr_pipeline(parsed_items):
    # UC: ALL sale line items FOUND
    # email input: need a StainlessKettle, a great coffee machine, a new microwave oven 
    return [
        {
            "name": "Electric Kettle Stainless Steel",
            "qty": 1,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        },
        {
            "name": "Coffee Maker Capsule",
            "qty": 1,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        },
        {
            "name": "Microwave Oven Compact",
            "qty": 1,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        }
    ]


def mock_partial_valid__mmr_pipeline(parsed_items):
    # UC: some sale line items FOUND, some NOT FOUND
    # email input: eed a StainlessKettle, a ABCX, a new microwave oven 
    return [
        {
            "name": "Electric Kettle Stainless Steel",
            "qty": 1,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        },
        {
            "name": "Unisex Hoodie Graphic",
            "qty": 1,
            "confidence": 0.2,
            "remark": "gap is tight, not safe",
            "status": "incomplete"
        },
        {
            "name": "Microwave Oven Compact",
            "qty": 1,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        }
    ]


# deepseek  
def real_mmr_pipeline(parsed_items):
    
    if all(item["status"] == "not_found" for item in parsed_items):
        return [
            {
                "name": None,
                "qty": item["qty"],
                "confidence": 0.0,
                "remark": "no candidates found",
                "status": "error",
                "input": item["input"]
            }
            for item in parsed_items
        ]


    # Embedding function
    embeddings = HuggingFaceEmbeddings(model_name=PATH_MODEL)

    # Chroma vectorstore
    os.makedirs(PATH_CHROMA_STORE, exist_ok=True)
    vectorstore = Chroma(
        collection_name="odoo_products",
        embedding_function=embeddings,
        persist_directory=PATH_CHROMA_STORE
    )
 
    
    # MMR retriever via as_retriever
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "lambda_mult": 0.5}
    )

    # Collect variations with MMR
    payload = []
    for item in parsed_items:
        query_text = " ".join(item["candidates"])
        variations = retriever.invoke(query_text)
        payload.append({
            "input": item["input"],
            "qty": item["qty"],
            "status": item["status"],
            "candidates": [doc.page_content for doc in variations]
        })

    # 6. Send to DeepSeek API
    prompt = f"""
        You are given product line items with candidate matches:
        {payload}

        For each line item:
        - Select the best candidate, but before matching it need fix each line item wordings according to these rules:
            Rules:
                - If product name has a typo, correct it to the closest valid candidate, (e.g. "shiiping" → "shipping") where shipping appear in embeddings doc.
                - If the item has variants (small/medium/large) and user did not specify, default to "Medium".
        - Compute confidence between 0 and 1:
            - 1 means top-1 is a clear winner (big gap with next).
            - 0 means top-1 and next are very close (hard to decide). 
        - Add a remark explaining the decision:
            - if confidence high, confidence >= 0.8, then, as example, remark = "clear winner" 
            - if confidence low, , confidence < 0.6, then, as example,  remark = "gap is tight, not safe"
            - else, is medium gap, as example, remark = "marginal safe"
            - based on ai assigned confidence, ai need give corresponding remark to explain the confidence.
        - Add a status field:
            - "complete" if confidence >= 0.8
            - "incomplete" otherwise
            - "error" if any processing error occurred


        Return JSON in this example format (name is embedding metadatas name without code, which is matched product name in embeddings) :
        [
            {{
                "name": "Corrugated Shipping Box Medium",
                "qty": 10,
                "confidence": 0.95,
                "remark": "clear winner",
                "status": "complete"
            }},
            {{
                "name": "Eco Paper Bag Medium",
                "qty": 1,
                "confidence": 0.55,
                "remark": "gap is not wide enough",
                "status": "incomplete"
            }},
            {{
                "name": "Men’s Hiking Boots",
                "qty": 1,
                "confidence": 0.8,
                "remark": "clear winner",
                "status": "complete"
            }}
        ]
        """

    debugText("prompt: ")
    debugText(prompt)


    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
    resp = requests.post(LLM_API_URL, json={
        "model": LLM_API_MODEL_VER,
        #"thinking": {"type": "disabled"},
        "messages": [
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content": prompt}
        ],
        "temperature": 0
    }, 
        headers=headers,
        timeout=60 
    )

    resp_json = resp.json()
    debugText("resp_json: ")
    debugText(resp_json)

    # 取出 content
    """
    content_str = resp_json["choices"][0]["message"]["content"]
    debugText("content_str: ")
    debugText(content_str)
    """

    content_str = resp_json["choices"][0]["message"]["content"]

    # 去除 markdown code fence
    if content_str.strip().startswith("```"):
        content_str = content_str.strip().strip("`")
        # 或者更安全：
        content_str = content_str.split("```json")[-1].split("```")[0].strip()


    debugText("content_str: ")
    debugText(content_str)

    #content_obj = json.loads(content_str)


    # 轉成 Python dict / list
    if isinstance(content_str, (dict, list)):
        content_obj = content_str
    else:
        try:
            content_obj = json.loads(content_str)
        except Exception as e:
            print("JSON parse error:", e)
            content_obj = []

    debugText("content_obj: ")
    debugText(content_obj)

    return content_obj
 

# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    parsed_items_1 = [
        {"input": "aluminum fold", "candidates": ["aluminum foil", "aluminum fold"], "qty": 2, "status": "ambiguous"},
        {"input": "coffee maker", "candidates": ["coffee maker"], "qty": 1, "status": "exact"},
        {"input": "glass jar", "candidates": ["glass jar"], "qty": 1, "status": "exact"},
        {"input": "formal shirt", "candidates": ["formal shirt"], "qty": 1, "status": "exact"}
    ]
    parsed_items_2 = [
        {'input': 'shiiping box', 'candidates': ['shipping box'], 'qty': 10, 'status': 'ambiguous'}, 
        {'input': 'eco bag', 'candidates': ['eco bag'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'hiking boot', 'candidates': ['hiking boot'], 'qty': 1, 'status': 'exact'}]

    parsed_items_3 = [
        {'input': 'shipping box', 'candidates': ['shipping box'], 'qty': 10, 'status': 'exact'}, 
        {'input': 'eco bag', 'candidates': ['eco bag'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'hiking boot', 'candidates': ['hiking boot'], 'qty': 1, 'status': 'exact'}]
    parsed_items_4 = [
        {
            "input": "StainlessKettle",
            "candidates": ["stainless kettle"],
            "qty": 1,
            "status": "exact"
        },
        {
            "input": "coffee machine",
            "candidates": ["coffee machine"],
            "qty": 1,
            "status": "exact"
        },
        {
            "input": "microwave oven",
            "candidates": ["microwave oven"],
            "qty": 1,
            "status": "exact"
        }
        ]

    #result = mock_mmr_pipeline(parsed_items_2)
    result = run_mmr_pipeline(parsed_items_4)
     
    print("Final Result:", result)
 