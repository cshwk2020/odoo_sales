import pytest
from odoo_sales.ai_parse_utils import real_ai_convert_text_to_json 

@pytest.mark.skip(reason="temporarily disabled")
def test_run_ai_convert_text_to_json_uc_all_invalid():

    text_prompt = """
        need a ABCX and HEJKX thx, kk
    """

    result = real_ai_convert_text_to_json(text_prompt)
    print("result: ", result)


@pytest.mark.skip(reason="temporarily disabled")
def test_run_ai_convert_text_to_json_uc_all_valid():

    text_prompt = """
        Dear customer service manager, 
        need a StainlessKettle, a great coffee machine, a new microwave oven 
        thx, kk
    """
    
    result = real_ai_convert_text_to_json(text_prompt)
    print("result: ", result)


@pytest.mark.skip(reason="temporarily disabled")
def test_run_ai_convert_text_to_json_uc_partial_valid():

    text_prompt = """
        Dear customer service manager, 
        need a StainlessKettle, a ABCX, a new microwave oven 
        thx, kk
    """
    
    result = real_ai_convert_text_to_json(text_prompt)
    print("result: ", result)


