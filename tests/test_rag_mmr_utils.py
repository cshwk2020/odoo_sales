import pytest
from odoo_sales.rag_mmr_utils import real_mmr_pipeline 


@pytest.mark.skip(reason="temporarily disabled")
def test_run_mmr_pipeline_uc_all_invalid():

    parsed_items = [
        {'input': 'ABCX', 'candidates': [], 'qty': 1, 'status': 'not_found'}, 
        {'input': 'HEJKX', 'candidates': [], 'qty': 1, 'status': 'not_found'}
    ]

    result = real_mmr_pipeline(parsed_items)
    print("result: ", result)


@pytest.mark.skip(reason="temporarily disabled")
def test_run_mmr_pipeline_uc_all_valid():

    parsed_items = [
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

    result = real_mmr_pipeline(parsed_items)
    print("result: ", result)


@pytest.mark.skip(reason="temporarily disabled")
def test_run_mmr_pipeline_uc_partial_valid():

    parsed_items = [
        {
            "input": "StainlessKettle",
            "candidates": ["stainless kettle"],
            "qty": 1,
            "status": "exact"
        },
        {
            'input': 'ABCX', 
            'candidates': [], 
            'qty': 1, 
            'status': 'not_found'
        }, 
        {
            "input": "coffee machine",
            "candidates": ["coffee machine"],
            "qty": 1,
            "status": "exact"
        },
    ]

    result = real_mmr_pipeline(parsed_items)
    print("result: ", result)



