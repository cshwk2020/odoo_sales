import requests, json
from .globals import progress_queue, stop_flag
from .app_utils import debugText

# deepseek
from .config import LLM_API_MODEL_VER  
from .config import LLM_API_KEY  
from .config import LLM_API_URL 


def mock_ai_convert_text_to_json(text_prompt):

    # UC: ALL INVALID
    """
    return [
        {
            "input": "ABCX",
            "candidates": [],
            "qty": 1,
            "status": "not_found"
        },
        {
            "input": "HEJKX",
            "candidates": [],
            "qty": 1,
            "status": "not_found"
        }
    ]
    """

    # UC: ALL VALID
    """
    return [
        {'input': 'StainlessKettle', 'candidates': ['stainless kettle'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'a great coffee machine', 'candidates': ['coffee machine'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'a new microwave oven', 'candidates': ['microwave oven'], 'qty': 1, 'status': 'exact'}
    ]
    """

    # UC: PARIAL VALID
    return [
        {'input': 'StainlessKettle', 'candidates': ['Stainless Kettle'], 'qty': 1, 'status': 'exact'}, 
        {'input': 'ABCX', 'candidates': [], 'qty': 1, 'status': 'not_found'}, 
        {'input': 'new microwave oven', 'candidates': ['microwave oven'], 'qty': 1, 'status': 'exact'}
    ]

 
 
def run_ai_convert_text_to_json(text_prompt):
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Example schema for AI to learn
    example_json = [
        {
            "input": "caf",
            "candidates": ["cat", "car", "café"],
            "qty": 2,
            "status": "ambiguous"
        },
        {
            "input": "tea",
            "candidates": ["tea"],
            "qty": 3,
            "status": "exact"
        },
        {
            "input": "xyz",
            "candidates": [],
            "qty": 1,
            "status": "not_found"
        }
    ]

    payload = {
        "model": LLM_API_MODEL_VER,
        #"thinking": {"type": "disabled"},
        "messages": [
            {
                "role": "system",
                "content": f"""
                    You are a parser that converts messy natural language order requests 
                    into JSON with fields: input, candidates, qty, status. 
                    Rules:
                    - Remove unnecessary filler words like 'I want', 'I need', 'please', 'give me'.
                    - Remove adjectives that describe product but are unhelpful for ERP product matching, 
                      such as 'good', 'best', 'great', 'nice', 'cheap'.
                    - If word is clear, status=exact with one candidate.
                    - If word is misspelled or ambiguous, status=ambiguous with multiple candidates.
                    - If consecutive words missing space, such as 'StainlessKettle', consider breaking them into 'Stainless', 'Kettle'.
                    - If remaining keywords, after adjusted for misspelled, still not a valid word in dictionary, 
                        then such word might be garbage, then status=not_found with empty candidates. .
                    - If no reasonable candidate exists, status=not_found with empty candidates.
                    - Always output valid JSON array.
                
                """
            },
            {
                "role": "user",
                "content": f"Example output:\n{json.dumps(example_json, indent=2)}\n\nNow convert this order request into JSON: {text_prompt}"
            }
        ],
        "temperature": 0.5,
        "response_format": {"type": "json_object"}  # 強制 JSON 格式
    }

 

    response = requests.post(LLM_API_URL, headers=headers, json=payload)
    data = response.json()

    print("data: ", data)

    # DeepSeek response content
    content = data["choices"][0]["message"]["content"]
    print("content: ", content)

    # 如果 content 已經係 dict/list → 直接 return
    if isinstance(content, (dict, list)):
        parsed = content
    else:
        try:
            parsed = json.loads(content)
        except Exception as e:
            print("JSON parse error:", e)
            parsed = []

    print("parsed: ", parsed)
    return parsed


# -----------------------------
# Example Run
# -----------------------------
if __name__ == "__main__":
    #text_prompt = "i need 2 aluminum fold, please give me 1 good coffee maker, 1 glass jar, and a formal shirt"
    # text_prompt = "please give 10 shiiping box, 1 eco bag, 1 pair of hiking boot"
    # text_prompt = "need a StainlessKettle, a great coffee machine, a new microwave oven" 
    text_prompt = """
    Dear customer service manager, 
    need a StainlessKettle, a great coffee machine, a new microwave oven 
    thx, kk
    """
    parsed = run_ai_convert_text_to_json(text_prompt)
    print(json.dumps(parsed, indent=2))
