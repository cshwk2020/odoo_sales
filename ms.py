import threading, os, base64
import json, ast
from flask import Flask, request, jsonify, send_from_directory, render_template_string

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .globals import progress_queue, stop_flag
from .app_utils import debugText
from .vault_utils import vault_get_odoo_user, vault_get_odoo_pass
from .ai_parse_utils import mock_ai_convert_text_to_json, run_ai_convert_text_to_json
from .rag_mmr_utils import mock_mmr_pipeline, run_mmr_pipeline
from .odoo_utils import get_sale_monitoring_record, update_sale_monitoring_status, get_or_create_partner, create_sale_order, create_sale_order_pdf, get_partner_email, get_sale_order_lines, send_notify_email, send_notify_email_failed
from .email_utils import gmail_send, gmail_send_with_attachment


app = Flask(__name__)
PDF_FOLDER = os.path.join(os.getcwd(), "pdf")

@app.route("/pdf/<path:filename>")
def serve_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)



@app.route("/confirm_reply/<int:order_id>", methods=["GET"])
def confirm_reply(order_id):
    # 第一頁：即時顯示 spinner + JS call 真正處理 endpoint
    return render_template_string("""
    <html>
    <head>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container mt-5">
      <div id="status" class="d-flex align-items-center">
        <div class="spinner-border text-primary me-2" role="status"></div>
        <strong>Processing your request...</strong>
      </div>
      <script>
        fetch('/confirm_reply_process/{{order_id}}')
          .then(resp => resp.text())
          .then(data => {
            document.getElementById("status").innerHTML = data;
          })
          .catch(err => {
            document.getElementById("status").innerHTML =
              '<div class="alert alert-danger">Error: ' + err + '</div>';
          });
      </script>
    </body>
    </html>
    """, order_id=order_id)



def extract_human_readable(original_body_raw) -> str:
    # normalize to dict
    if isinstance(original_body_raw, dict):
        parsed = original_body_raw
    elif isinstance(original_body_raw, str):
        # 🔑 用 Python parser，而唔係 JSON
        parsed = ast.literal_eval(original_body_raw)
    else:
        raise ValueError("Invalid original email body type")

    # extract headers + body
    headers = parsed.get("headers", {})
    html = parsed.get("html", "")
    text = parsed.get("text", "")

    keep_keys = ["message-id", "subject", "to", "content-type", "from", "date"]
    header_lines = []
    for k in keep_keys:
        for hk, hv in headers.items():
            if hk.lower().startswith(k.lower()):
                header_lines.append(hv)

    body_part = html or text or "(no body found)"

    return "<br>".join(header_lines) + "<hr>" + body_part



@app.route("/confirm_reply_process/<int:order_id>", methods=["GET"])
def confirm_reply_process(order_id):
    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()
    try:
        # 生成 PDF
        pdf_result = create_sale_order_pdf(odoo_user, odoo_pass, order_id)
        if not pdf_result.get("status"):
            return f"PDF generation failed: {pdf_result.get('msg')}", 500

        pdf_data = base64.b64decode(pdf_result.get("msg"))
        filepath = f"./pdf/SO_{order_id}.pdf"
        os.makedirs("./pdf", exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(pdf_data)

        # 取 order lines via XML-RPC
        order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
        lines_html = "".join([
            f"<tr><td>{l['product']}</td><td>{l['qty']}</td><td>{l['price']}</td></tr>"
            for l in order_lines
        ])

        # 取 monitoring record via XML-RPC
        monitoring = get_sale_monitoring_record(odoo_user, odoo_pass, order_id)
        raw_body = monitoring.get("original_email_body") if monitoring else None
        original_body = extract_human_readable(raw_body) if raw_body else "(no original email body stored)"
        customer_email = monitoring.get("sender_email") if monitoring else None
        if not customer_email:
            return f"Sender email not found for order {order_id}", 500

        # 建立 email HTML body
        body_html = f"""
        <p>Dear Customer,</p>
        <p>Thank you for your request. Please find attached quotation for Order {order_id}.</p>
        <p><b>Sale Order Lines:</b></p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Product</th><th>Qty</th><th>Price</th></tr>
            {lines_html}
        </table>
        <p>Best regards,<br>Sales Team</p>
        <hr>
        <p><b>Your Original Request:</b></p>
        <blockquote style="color:#555; font-style:italic;">
            {original_body}
        </blockquote>
        """

        # send email (MIME + PDF attach)
        mime_msg = MIMEMultipart()
        mime_msg["To"] = customer_email
        mime_msg["Subject"] = f"Quotation for Order {order_id}"
        mime_msg.attach(MIMEText(body_html, "html"))

        with open(filepath, "rb") as f:
            pdf_bytes = f.read()
        part = MIMEBase("application", "pdf")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="SO_{order_id}.pdf"')
        mime_msg.attach(part)

        raw_string = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")
        final_api_message = {"raw": raw_string}
        gmail_send(final_api_message)

        # 更新 status
        update_sale_monitoring_status(odoo_user, odoo_pass, order_id)

        return render_template_string("""
            <div class="alert alert-success" role="alert">
            Reply sent to {{customer_email}} for Order {{order_id}}, PDF attached.<br>
            </div>
            """, customer_email=customer_email, order_id=order_id)

    except Exception as e:
        return render_template_string("""
            <div class="alert alert-danger" role="alert">
            Error generating reply: {{error}}
            </div>
            """, error=str(e)), 500





def run_job(odoo_user, odoo_pass, partner_id, email_data_json):

    email_data_json = request.json

    # 1. Nested structure (preferred)
    sender = None
    receiver = None
    if email_data_json.get("from") and email_data_json["from"].get("value"):
        sender = email_data_json["from"]["value"][0].get("address")
    if email_data_json.get("to") and email_data_json["to"].get("value"):
        receiver = email_data_json["to"]["value"][0].get("address")

    # 2. Subject / snippet / messageId / threadId
    subject = email_data_json.get("subject", "No Subject")
    body = email_data_json.get("text")
    msg_id = email_data_json.get("messageId")   # 注意：用 messageId，而唔係 headers["message-id"]
    threadid = email_data_json.get("threadId")


    debugText(f"run_job: sender={sender}, ")
    debugText(f"run_job: receiver={receiver}, ")
    debugText(f"run_job: subject={subject}, ")
    debugText(f"run_job: body={body}, ")
    debugText(f"run_job: msg_id={msg_id}, ")
    debugText(f"run_job: threadid={threadid}, ")

    debugText(f"run_job: partner_id={partner_id}, ")

    # Step 1: parse
    parsed_items = mock_ai_convert_text_to_json(body)
    #parsed_items = run_ai_convert_text_to_json(body)
    debugText("parsed_items: ")
    debugText(parsed_items)

    if stop_flag.is_set(): return

    # Step 2: run pipeline
    sale_items = mock_mmr_pipeline(parsed_items)
    #sale_items = run_mmr_pipeline(parsed_items)
    debugText("sale_items: ")
    debugText(sale_items)

    if stop_flag.is_set(): return

    # Step 3: create sale order
    odoo_result = create_sale_order(odoo_user, odoo_pass, partner_id, email_data_json, parsed_items, sale_items)
    debugText("odoo_result: ")
    debugText(odoo_result)

    if odoo_result.get("status"):
        pdf_data = base64.b64decode(odoo_result["attachment"])
        os.makedirs("./pdf", exist_ok=True)
        filename = f"./pdf/SO_{odoo_result['order_id']}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_data)
        debugText(f"PDF saved to {filename}")

        #
        staff_email = receiver
        order_id = odoo_result['order_id']
        original_email_body = body
        order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
        # send_notify_email(staff_email, order_id, original_email_body, order_lines)


    else:
        debugText(f"Sale order creation failed: {odoo_result.get('msg')}")

    return odoo_result




@app.route("/gmail_webhook", methods=["POST"])
def gmail_webhook():
    
    email_data_json = request.json

    print("email_data_json...")
    print(email_data_json)

    # 1. Nested structure (preferred)
    sender = None
    receiver = None
    if email_data_json.get("from") and email_data_json["from"].get("value"):
        sender = email_data_json["from"]["value"][0].get("address")
    if email_data_json.get("to") and email_data_json["to"].get("value"):
        receiver = email_data_json["to"]["value"][0].get("address")

    # 2. Subject / snippet / messageId / threadId
    subject = email_data_json.get("subject", "No Subject")
    body = email_data_json.get("text")
    msg_id = email_data_json.get("messageId")   # 注意：用 messageId，而唔係 headers["message-id"]
    threadid = email_data_json.get("threadId")


    debugText(f"Webhook received: sender={sender}, ")
    debugText(f"Webhook received: receiver={receiver}, ")
    debugText(f"Webhook received: subject={subject}, ")
    debugText(f"Webhook received: body={body}, ")
    debugText(f"Webhook received: msg_id={msg_id}, ")
    debugText(f"Webhook received: threadid={threadid}, ")

     
    odoo_user = vault_get_odoo_user()
    odoo_pass = vault_get_odoo_pass()

    #
    partner_id = get_or_create_partner(odoo_user, odoo_pass, sender)
    debugText(f"Webhook received: partner_id={partner_id}, ")


    stop_flag.clear()
    #threading.Thread(target=run_job, args=(body, odoo_user, odoo_pass, sender, msg_id)).start()

    odoo_result = run_job(odoo_user, odoo_pass, partner_id, email_data_json)

    #
    if odoo_result["status"]:
        # decode base64 PDF
        pdf_data = base64.b64decode(odoo_result["attachment"])

        # 確保 ./pdf/ 存在
        os.makedirs("./pdf", exist_ok=True)

        # 存檔，檔名可以用 order_id 或 timestamp
        order_id = odoo_result["order_id"]
        filename = f"SO_{order_id}.pdf"
        filepath = f"./pdf/{filename}"
        with open(filepath, "wb") as f:
            f.write(pdf_data)

        debugText(f"PDF saved to {filepath}")

        #
        order_lines = get_sale_order_lines(odoo_user, odoo_pass, order_id)
        send_notify_email(receiver, order_id, email_data_json)
        debugText("AFTER send_notify_email...order_lines=={order_lines}")

        #
        pdf_path = f"http://127.0.0.1:5000/pdf/{filename}"


    else:
        
        debugText(f"Sale order creation failed: {odoo_result['msg']}")
        monitoring_id = odoo_result["monitoring_id"]
        send_notify_email_failed(receiver, monitoring_id, email_data_json)
        pdf_path = f""
     

    return jsonify({
        "status": odoo_result.get("status"),
        "msg_id": msg_id,
        "threadid": threadid,
        "sender": sender,
        "receiver": receiver,
        "subject": subject,
        "body": body,
        "order_id": odoo_result.get("order_id"),
        "msg": odoo_result.get("msg"),
        "pdf_path": pdf_path
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)


