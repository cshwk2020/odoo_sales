# tests/test_odoo_client.py
import pytest
from odoo_sales.ms import confirm_reply
from odoo_sales.vault_utils import vault_get_odoo_user, vault_get_odoo_pass

@pytest.mark.skip(reason="temporarily disabled")
def test_confirm_reply():
    
    order_id = 80
    confirm_reply(order_id)

