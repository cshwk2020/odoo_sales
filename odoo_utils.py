import os
import json
import base64
import requests
import xmlrpc.client

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import ODOO_BASE_URL, ODOO_DB
from .config import vault_get_odoo_user, vault_get_odoo_pass
from .app_utils import debugText
from .email_utils import gmail_send




def update_sale_monitoring_status(odoo_user, odoo_pass, order_id):
    """Update sale.monitoring status to 'replied' via XML-RPC"""
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
    if not uid:
        raise Exception("Odoo authentication failed")

    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

    # 找到 monitoring record
    rec_ids = models.execute_kw(
        ODOO_DB, uid, odoo_pass,
        "sale.monitoring", "search",
        [[["sale_order_id", "=", order_id]]],
        {"limit": 1}
    )
    if rec_ids:
        models.execute_kw(
            ODOO_DB, uid, odoo_pass,
            "sale.monitoring", "write",
            [rec_ids, {"status": "replied"}]
        )
    else:
        raise Exception(f"No sale.monitoring record found for order {order_id}")



def get_sale_monitoring_record(odoo_user, odoo_pass, order_id):
    """
    Fetch sale.monitoring record linked to a sale.order via XML-RPC.
    Returns dict with keys: original_email_body, sender_email
    """
    try:
        # 認證
        common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
        if not uid:
            raise Exception("Odoo authentication failed")

        models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

        # search_read
        records = models.execute_kw(
            ODOO_DB, uid, odoo_pass,
            "sale.monitoring", "search_read",
            [[["sale_order_id", "=", order_id]]],
            {"fields": ["original_email_body", "sender_email"], "limit": 1}
        )

        if not records:
            return None

        rec = records[0]

        # Normalize sender_email
        sender_email = rec.get("sender_email")
        if isinstance(sender_email, dict):
            # 如果之前存咗 Gmail JSON dict
            val = sender_email.get("value")
            if isinstance(val, list) and len(val) > 0:
                sender_email = val[0].get("address")
            else:
                sender_email = json.dumps(sender_email)
        elif isinstance(sender_email, list):
            # 如果係 list
            sender_email = sender_email[0] if sender_email else None

        # Normalize original_email_body
        original_body = rec.get("original_email_body")
        if isinstance(original_body, (dict, list)):
            original_body = json.dumps(original_body, indent=2)

        return {
            "sender_email": sender_email,
            "original_email_body": original_body
        }

    except Exception as e:
        print(f"Error fetching sale.monitoring: {e}")
        return None




def get_partner_email(odoo_user, odoo_pass, order_id):
    """查詢 sale.order → partner_id → partner email"""
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

    order = models.execute_kw(
        ODOO_DB, uid, odoo_pass,
        "sale.order", "read",
        [[order_id]], {"fields": ["partner_id"]}
    )
    if order and order[0].get("partner_id"):
        partner_id = order[0]["partner_id"][0]
        partner = models.execute_kw(
            ODOO_DB, uid, odoo_pass,
            "res.partner", "read",
            [[partner_id]], {"fields": ["email"]}
        )
        if partner and partner[0].get("email"):
            return partner[0]["email"]
    return None



def get_or_create_partner(odoo_user, odoo_pass, sender_email):
    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

    # 🔑 改成 call Odoo model method
    partner_id = models.execute_kw(
        ODOO_DB, uid, odoo_pass,
        "sale.monitoring", "get_or_create_partner",
        [sender_email]   
    )
    #
    if isinstance(partner_id, list):
        partner_id = partner_id[0] if partner_id else False

    debugText(f"Flask:: get_or_create_partner returned partner_id={partner_id}")
    return partner_id



def get_oldest_message_id(thread_json):
    """
    Given a Gmail API thread JSON, return the id of the oldest message.
    """
    messages = thread_json.get("messages", [])
    if not messages:
        return None

    # ✅ 用 internalDate 排序，確保揀最舊
    oldest_msg = min(messages, key=lambda m: int(m.get("internalDate", 0)))
    return oldest_msg.get("id")






def send_notify_email(staff_email, sale_order_id, email_data_json):
    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()

    subject = email_data_json.get("subject", "No Subject")
    original_text = (
        email_data_json.get("text")
        or email_data_json.get("html")
        or email_data_json.get("textAsHtml")
        or ""
    )
    msg_id = email_data_json.get("messageId")
    threadid = email_data_json.get("threadId")
    gmail_id = email_data_json.get("id")  # Gmail API message id of original email

    # Gmail shortcut URL
    if gmail_id:
        gmail_shortcut_url = f"https://mail.google.com/mail/u/0/#inbox/{gmail_id}"
    elif threadid:
        gmail_shortcut_url = f"https://mail.google.com/mail/u/0/#inbox/{threadid}"
    else:
        gmail_shortcut_url = "https://mail.google.com/mail/u/0/#inbox"

    # 自動生成 order_lines
    order_lines = get_sale_order_lines(odoo_user, odoo_pass, sale_order_id)

    lines_html = "".join([
        f"<tr><td>{l['product']}</td><td>{l['qty']}</td><td>{l['price']}</td></tr>"
        for l in order_lines
    ])

    confirm_url = f"http://127.0.0.1:5000/confirm_reply/{sale_order_id}"
    fix_url = f"http://localhost:8069/odoo/sales/{sale_order_id}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p><b>Original Request:</b><br><i style="color: #555;">"{original_text}"</i></p>
        <p><b>Sale Order Lines:</b></p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Product</th><th>Qty</th><th>Price</th></tr>
            {lines_html}
        </table>
        <p>
            <a href="{confirm_url}" style="background:#28a745;color:white;padding:10px;text-decoration:none;">
                CONFIRM REPLY
            </a>
            &nbsp;&nbsp;
            <a href="{fix_url}" style="background:#dc3545;color:white;padding:10px;text-decoration:none;">
                GO TO FIX
            </a>
        </p>
        <br>
        <a href="{gmail_shortcut_url}" target="_blank"
           style="background-color: #1a73e8; color: white; padding: 12px 20px;
                  text-decoration: none; font-weight: bold; border-radius: 4px;
                  display: inline-block; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
            View Original Customer Email Thread
        </a>
    </div>
    """

    # MIME message container
    mime_msg = MIMEMultipart()
    clean_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    mime_msg["To"] = staff_email
    mime_msg["Subject"] = clean_subject

    if msg_id:
        mime_msg["In-Reply-To"] = msg_id
        mime_msg["References"] = msg_id

    mime_msg.attach(MIMEText(html_body, "html"))

    # Attach PDF quotation (ensure bytes, not dict)
    pdf_path = f"./pdf/SO_{sale_order_id}.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()  # raw bytes

        part = MIMEBase("application", "pdf")
        part.set_payload(pdf_bytes)   # 必須係 bytes
        encoders.encode_base64(part)  # 第一層：附件合法化
        part.add_header("Content-Disposition", f'attachment; filename="SO_{sale_order_id}.pdf"')
        mime_msg.attach(part)

    # Gmail API 要求：整封 MIME message再 base64-url-safe encode
    raw_string = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    final_api_message = {"raw": raw_string}
    if threadid:
        final_api_message["threadId"] = threadid

    gmail_send(final_api_message)

 

def send_notify_email_failed(staff_email, monitoring_id, email_data_json):
    subject = email_data_json.get("subject", "No Subject")
    body = (
        email_data_json.get("text")
        or email_data_json.get("html")
        or email_data_json.get("textAsHtml")
        or ""
    )
    msg_id = email_data_json.get("messageId")
    threadid = email_data_json.get("threadId")
    gmail_id = email_data_json.get("id")

    # Gmail shortcut
    if gmail_id:
        gmail_shortcut_url = f"https://mail.google.com/mail/u/0/#inbox/{gmail_id}"
    elif threadid:
        gmail_shortcut_url = f"https://mail.google.com/mail/u/0/#inbox/{threadid}"
    else:
        gmail_shortcut_url = "https://mail.google.com/mail/u/0/#inbox"

    # ✅ Get Odoo credentials from Vault
    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()

    # ✅ Lookup action id dynamically
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
        models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

        action_ids = models.execute_kw(
            ODOO_DB, uid, odoo_pass,
            "ir.actions.act_window", "search",
            [[["res_model", "=", "sale.monitoring"]]],
            {"limit": 1}
        )
        if action_ids:
            action_id = action_ids[0]
            monitoring_fix_url = f"http://localhost:8069/web#action={action_id}&id={monitoring_id}&model=sale.monitoring&view_type=form"
        else:
            monitoring_fix_url = f"http://localhost:8069/web#model=sale.monitoring&id={monitoring_id}&view_type=form"
    except Exception as e:
        debugText(f"send_notify_email_failed: action lookup failed: {e}")
        monitoring_fix_url = f"http://localhost:8069/web#model=sale.monitoring&id={monitoring_id}&view_type=form"

    # Build email
    mime_msg = MIMEMultipart()
    clean_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    mime_msg["To"] = staff_email
    mime_msg["Subject"] = clean_subject

    if msg_id:
        mime_msg["In-Reply-To"] = msg_id
        mime_msg["References"] = msg_id

    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p><b>Original Request:</b><br><i style="color: #555;">"{body}"</i></p>
        <p><b>Status:</b> Sale order could not be generated automatically. Monitoring record ID: <b>{monitoring_id}</b>.</p>
        <p style="color:red; font-weight:bold;">
            Staff attention required: please handle manually in Odoo.
        </p>
        <br>
        <a href="{monitoring_fix_url}" target="_blank"
           style="background-color: #34a853; color: white; padding: 12px 20px;
                  text-decoration: none; font-weight: bold; border-radius: 4px;
                  display: inline-block; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
            Go to Odoo Monitoring Record
        </a>
        
        <br><br>

        <a href="{gmail_shortcut_url}" target="_blank"
           style="background-color: #1a73e8; color: white; padding: 12px 20px;
                  text-decoration: none; font-weight: bold; border-radius: 4px;
                  display: inline-block; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
            View Original Customer Email Thread
        </a>
        
        <br><br>
    </div>
    """
    mime_msg.attach(MIMEText(html_body, "html"))

    raw_string = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
    final_api_message = {"raw": raw_string}
    if threadid:
        final_api_message["threadId"] = threadid

    gmail_send(final_api_message)




def safe_dict(d):
    return {k: (v if v is not None else False) for k, v in d.items()}



def get_sale_order_lines(odoo_user, odoo_pass, order_id):

    common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

    lines = models.execute_kw(
        ODOO_DB, uid, odoo_pass,
        "sale.order.line", "search_read",
        [[["order_id", "=", order_id]]],
        {"fields": ["product_id", "product_uom_qty", "price_unit", "price_subtotal"]}
    )

    # return dict list for send_notify_email
    return [
        {
            "product": l["product_id"][1] if l.get("product_id") else "",
            "qty": l.get("product_uom_qty", 0),
            "price": l.get("price_unit", 0.0),
            "subtotal": l.get("price_subtotal", 0.0),
        }
        for l in lines
    ]



def create_sale_order_pdf(odoo_user, odoo_pass, order_id):

    pdf_base64 = None
    session = requests.Session()
    
    # Authenticate the session
    login_url = f"{ODOO_BASE_URL}/web/session/authenticate"
    login_payload = {
        "jsonrpc": "2.0",
        "params": {
            "db": ODOO_DB,
            "login": odoo_user,
            "password": odoo_pass
        }
    }
    auth_resp = session.post(login_url, json=login_payload)
    
    if auth_resp.status_code == 200:
        # Hit the report download URL
        report_url = f"{ODOO_BASE_URL}/report/pdf/sale.report_saleorder/{order_id}"
        report_resp = session.get(report_url)
        
        if report_resp.status_code == 200:
            # Convert the binary PDF to base64 string
            pdf_base64 = base64.b64encode(report_resp.content).decode('utf-8')

            return {"status": True, "msg": pdf_base64}
            
        else:
            return {"status": False, "msg": "PDF download failed."}
    else:
        return {"status": False, "msg": "Session Auth failed."}



def create_sale_order(odoo_user, odoo_pass, partner_id, email_data_json, parsed_items, sale_items):

    debugText("odoo_user: " + odoo_user)
    debugText("odoo_pass: " + odoo_pass)
    debugText("email_data_json: ")
    debugText(email_data_json)
    debugText("parsed_items: ")
    debugText(parsed_items)
    debugText("sale_items: ")
    debugText(sale_items)

    #
    sender = None
    receiver = None
    if email_data_json.get("from") and email_data_json["from"].get("value"):
        sender = email_data_json["from"]["value"][0].get("address")
    if email_data_json.get("to") and email_data_json["to"].get("value"):
        receiver = email_data_json["to"]["value"][0].get("address")
    #
    subject = email_data_json.get("subject", "No Subject")
    body = email_data_json.get("text")
    msg_id = email_data_json.get("messageId")   # 注意：用 messageId，而唔係 headers["message-id"]
    threadid = email_data_json.get("threadId")


    try:
        # Odoo login
        common = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, odoo_user, odoo_pass, {})
        models = xmlrpc.client.ServerProxy(f"{ODOO_BASE_URL}/xmlrpc/2/object")

        # 只處理 status = complete 嘅 items
        order_lines = []
        for item in sale_items:
            if item["status"] == "complete":
                # 用 rag_matches 嘅 odoo_id 會更準確，但你 AI items 只有 name
                # 暫時用 product name search
                product_ids = models.execute_kw(
                    ODOO_DB, uid, odoo_pass,
                    "product.product", "search",
                    [[["name", "ilike", item["name"]]]],
                    {"limit": 1}
                )
                if product_ids:
                    order_lines.append((0, 0, {
                        "product_id": product_ids[0],
                        "product_uom_qty": item["qty"]
                    }))

        #
        debugText("order_lines :")
        debugText(order_lines)        

        monitoring_vals = {
            "thread_id": threadid,
            "email_msg_id": msg_id,
            "sender_email": sender,
            "original_email_body": email_data_json,
            "ai_parse_text": json.dumps(parsed_items),
            "ai_mmr_json": json.dumps(sale_items),
        }

        if len(order_lines) == 0:

            debugText("debug...A...: order_lines IS 0...")

            monitoring_vals["status"] = "pending_fix"
             
            monitoring_vals = safe_dict(monitoring_vals)

            debugText("debug...B...: order_lines IS 0...")

            create_monitoring_result = models.execute_kw(
                ODOO_DB, uid, odoo_pass,
                "sale.monitoring", "create_monitoring_only",
                [monitoring_vals]
            )

            create_monitoring_result = safe_dict(create_monitoring_result)
            monitoring_id = create_monitoring_result.get("monitoring_id")

            debugText("debug: create_monitoring_result IS ...")
            debugText(create_monitoring_result)

            return_json = {
                    "status": False, 
                    "msg": "No valid items to create order",
                    "monitoring_id": monitoring_id
                }

            return return_json

        else:

            debugText("debug: order_lines NOT 0...")

            vals_order = {
                "partner_id": partner_id,
                "order_line": order_lines
            }
            monitoring_vals["status"] = "pending_reply"

             
            vals_order = safe_dict(vals_order)
            monitoring_vals = safe_dict(monitoring_vals)

            debugText("vals_order :")
            debugText(vals_order)
            debugText("monitoring_vals :")
            debugText(monitoring_vals)



            create_order_result = models.execute_kw(
                ODOO_DB, uid, odoo_pass,
                "sale.monitoring", "create_order_with_monitoring",
                [vals_order, monitoring_vals]
            )

            #
            debugText("create_order_result: ")
            debugText(create_order_result)
             
            if create_order_result.get("status") == True:

                order_id = create_order_result.get("order_id")

                debugText("order_id: ")
                debugText(order_id)

                create_pdf_result = create_sale_order_pdf(odoo_user, odoo_pass, order_id)
            
                debugText("create_pdf_result: ")
                debugText(create_pdf_result)

               

                pdf_base64 = create_pdf_result.get("msg")

                return {
                    "status": True,
                    "msg": f"Sale order {order_id} created",
                    "order_id": order_id,
                    "attachment": pdf_base64
                }


            else:
                return create_order_result
                
                  

    except Exception as e:
        return {"status": False, "msg": str(e)}

 

# -----------------------------
# Example Run
# -----------------------------
if __name__ == "__main__":
    ODOO_USERNAME = "testuser1"
    ODOO_PASSWORD = "51118326"

    # success

    email_data_json = {
        "id": "19e24bfcfdff4583",
        "threadid": "19e24bfcfdff4583",
        "from": "cshwk2021@gmail.com",
        "to": "cshwk2020@gmail.com",
        "subject": "request order QuoTATion",
        "body": "Dear customer service manager, need a StainlessKettle, a great coffee machine, a new microwave oven thx, kk",
    }

    
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

    sale_items_success = [
        {
            "name": "Corrugated Shipping Box Medium",
            "qty": 10,
            "confidence": 0.95,
            "remark": "clear winner",
            "status": "complete"
        },
        {
            "name": "Eco Paper Bag Medium",
            "qty": 1,
            "confidence": 0.85,
            "remark": "gap is wide enough",
            "status": "incomplete"
        },
        {
            "name": "Men’s Hiking Boots",
            "qty": 1,
            "confidence": 0.9,
            "remark": "clear winner",
            "status": "complete"
        }
    ]


    sale_items_failed = [
        {
            "name": "Corrugated Shipping Box Medium",
            "qty": 10,
            "confidence": 0.55,
            "remark": "gap is not wide enough",
            "status": "incomplete"
        },
        {
            "name": "Eco Paper Bag Medium",
            "qty": 1,
            "confidence": 0.55,
            "remark": "gap is not wide enough",
            "status": "incomplete"
        },
        {
            "name": "Men’s Hiking Boots",
            "qty": 1,
            "confidence": 0.55,
            "remark": "gap is not wide enough",
            "status": "incomplete"
        }
    ]

    result = create_sale_order(ODOO_USERNAME, ODOO_PASSWORD, 1, email_data_json, parsed_items, sale_items_success)
    #result = create_sale_order(ODOO_USERNAME, ODOO_PASSWORD, email_data_json, parsed_items, sale_items_failed)
    #print(json.dumps(result, indent=2))


    debugText(f"order_id...0...: ")

    if result.get("status"): 

        debugText(f"order_id...1...: ")

        # decode base64 PDF
        pdf_data = base64.b64decode(result["attachment"])

        # 確保 ./pdf/ 存在
        os.makedirs("./pdf", exist_ok=True)

        # 存檔，檔名可以用 order_id 或 timestamp
        order_id = result["order_id"]
        filename = f"./pdf/SO_{order_id}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_data)

        print(f"PDF saved to {filename}")

    else:
        debugText(f"order_id...2...: ")
        print("Sale order creation failed:", result.get("msg"))
   
     

