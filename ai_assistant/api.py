import frappe
from frappe import _
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# List of Doctypes considered confidential for audit email tracking
CONFIDENTIAL_DOCTYPES = [
    "Sales Invoice", 
    "Customer", 
    "Salary Slip", 
    "Employee", 
    "Payment Entry", 
    "Journal Entry", 
    "Purchase Invoice"
]

@frappe.whitelist()
def chat_with_gemini(message):
    """
    API endpoint called from Frontend Chat Widget.
    """
    if not genai:
        frappe.throw(_("google-generativeai library is not installed. Please run 'pip install google-generativeai' in your bench environment."))

    api_key = frappe.conf.get("gemini_api_key")
    if not api_key:
        frappe.throw(_("Gemini API Key not found. Please set 'gemini_api_key' in your site_config.json"))

    try:
        genai.configure(api_key=api_key)
        
        # System instructions to act as ERPNext Assistant
        system_instruction = (
            "You are AI Assistant, an intelligent assistant inside ERPNext. "
            "You help users find files, search database records (like Invoices, Customers, Items), "
            "and answer queries based on the data. You have access to database search, file finding, "
            "and Sales Invoice creation tools. If the user asks to create/generate an invoice, use "
            "the create_sales_invoice tool."
        )

        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction,
            tools=[search_erpnext_database, find_uploaded_files, create_sales_invoice]
        )

        # stateless one-turn tool calling approach.
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(message)
        
        return {"status": "success", "reply": response.text}

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Gemini AI Error")
        return {"status": "error", "message": str(e)}


def send_audit_email(action: str, details: str):
    """
    Helper function to send email notification to the manager when confidential actions occur.
    """
    try:
        manager_email = frappe.conf.get("manager_email")
        if not manager_email:
            # Fallback to Administrator or active system managers
            manager_email = frappe.db.get_value("User", {"name": "Administrator"}, "email") or "admin@example.com"
            
        user = frappe.session.user
        
        subject = f"[Security Alert] Confidential Action / Data Access by {user}"
        message = (
            f"<p>Dear Manager,</p>"
            f"<p>This is an automated alert from the AI Assistant auditing system.</p>"
            f"<p><strong>User:</strong> {user}<br>"
            f"<strong>Action:</strong> {action}<br>"
            f"<strong>Details:</strong> {details}</p>"
            f"<p>Please review this activity if necessary.</p>"
        )
        
        frappe.sendmail(
            recipients=[manager_email],
            subject=subject,
            message=message,
            now=True
        )
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="AI Assistant Audit Email Failure")


def search_erpnext_database(doctype: str, keyword: str) -> str:
    """
    Tool for Gemini to search any ERPNext Doctype.
    Returns a JSON string of matching records.
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            return json.dumps({"error": f"DocType {doctype} does not exist."})
        
        # Check if the requested Doctype is confidential and send audit alert
        if doctype in CONFIDENTIAL_DOCTYPES:
            send_audit_email(
                action=f"Searched Database ({doctype})",
                details=f"Keyword used: '{keyword}'"
            )

        meta = frappe.get_meta(doctype)
        title_field = meta.title_field or "name"
        
        records = frappe.get_list(
            doctype,
            filters={title_field: ["like", f"%{keyword}%"]},
            fields=["name", title_field],
            limit_page_length=5
        )
        return json.dumps(records) if records else json.dumps({"message": "No records found."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_sales_invoice(customer: str, item_code: str, qty: float, rate: float) -> str:
    """
    Tool for Gemini to create a Sales Invoice in ERPNext.
    Returns a JSON string indicating success or error.
    """
    try:
        # Create Sales Invoice in Draft mode
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "items": [{
                "item_code": item_code,
                "qty": qty,
                "rate": rate
            }]
        })
        invoice.insert()
        
        # Trigger audit email for creation
        send_audit_email(
            action="Generated Sales Invoice",
            details=f"Customer: {customer}, Item: {item_code}, Qty: {qty}, Rate: {rate}, Invoice Reference: {invoice.name}"
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Sales Invoice {invoice.name} created successfully in Draft mode.",
            "invoice_name": invoice.name
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def find_uploaded_files(keyword: str) -> str:
    """
    Tool for Gemini to search for uploaded files in the ERPNext File Manager.
    Returns a JSON string of matching files.
    """
    try:
        files = frappe.get_list(
            "File",
            filters={"file_name": ["like", f"%{keyword}%"]},
            fields=["name", "file_name", "file_url"],
            limit_page_length=5
        )
        return json.dumps(files) if files else json.dumps({"message": "No files found."})
    except Exception as e:
        return json.dumps({"error": str(e)})
