from flask import Flask, request, Response, render_template
import threading, json, os
import base64
from .globals import progress_queue, stop_flag
from .app_utils import debugText, mask_password
from .vault_utils import vault_get_odoo_user, vault_get_odoo_pass
from .ai_parse_utils import mock_ai_convert_text_to_json, run_ai_convert_text_to_json
from .rag_mmr_utils import mock_mmr_pipeline, run_mmr_pipeline
from .odoo_utils import create_sale_order 

app = Flask(__name__, template_folder='Template')

def run_job(text_prompt, odoo_user, odoo_pass):

    debugText("odoo_user: " + odoo_user)
    debugText("odoo_pass: " + odoo_pass)
    debugText("text_prompt: " + text_prompt)

    # Step 1: parse
    #parsed_items = mock_ai_convert_text_to_json(text_prompt)
    parsed_items = run_ai_convert_text_to_json(text_prompt)

    debugText("parsed_items: ")
    debugText(parsed_items)

    if stop_flag.is_set(): return

    # Step 2: run pipeline
    #sale_items = mock_mmr_pipeline(parsed_items)
    sale_items = run_mmr_pipeline(parsed_items)
    debugText("sale_items: ")
    debugText(sale_items)

    if stop_flag.is_set(): return

    # Step 3: create sale order
    debugText("odoo_user: " + odoo_user)
    debugText("odoo_pass: " + odoo_pass)
    debugText(sale_items)
    odoo_result = create_sale_order(odoo_user, odoo_pass, sale_items)
    
    #
    debugText("odoo_result: ")
    if "attachment" in odoo_result and isinstance(odoo_result["attachment"], str):
        preview_len = min(len(odoo_result["attachment"]), 200)
        debugText({
            **odoo_result,
            "attachment": odoo_result["attachment"][:preview_len] + "...(truncated)"
        })
    else:
        debugText(odoo_result)

    #
    if odoo_result["status"]:
        # decode base64 PDF
        pdf_data = base64.b64decode(odoo_result["attachment"])

        # 確保 ./pdf/ 存在
        os.makedirs("./pdf", exist_ok=True)

        # 存檔，檔名可以用 order_id 或 timestamp
        order_id = odoo_result["order_id"]
        filename = f"./pdf/SO_{order_id}.pdf"
        with open(filename, "wb") as f:
            f.write(pdf_data)

        debugText(f"PDF saved to {filename}")
    else:
        debugText(f"Sale order creation failed: {odoo_result['msg']}")
   
     


@app.route('/')
def index():
    return render_template(
        "menu_sale.html",
        odooUser=vault_get_odoo_user(),
        odooPass=vault_get_odoo_pass()
    )

@app.route("/automation", methods=['POST'])
def automation_upload():
    odoo_user = request.form["odooUser"]
    odoo_pass = request.form["odooPass"]
    text_prompt = request.form["textPrompt"]

    debugText(f"odoo_user: {odoo_user}")
    debugText(f"odoo_pass: {mask_password(odoo_pass)}")
    debugText(f"text_prompt: {text_prompt}")

    stop_flag.clear()
    threading.Thread(target=run_job, args=(text_prompt, odoo_user, odoo_pass)).start()
    return "Sale order request received"

@app.route("/automation/reset", methods=["POST"])
def automation_reset():
    stop_flag.set()
    while not progress_queue.empty():
        try:
            progress_queue.get_nowait()
        except queue.Empty:
            break
    return "Reset done"

@app.route("/automation/stream", methods=["GET"])
def automation_stream():
    def generate():
        while True:
            if stop_flag.is_set():
                break
            msg = progress_queue.get()
            msg_str = json.dumps(msg, ensure_ascii=False) if isinstance(msg, dict) else str(msg)
            yield f"data: {msg_str}\n\n"
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
