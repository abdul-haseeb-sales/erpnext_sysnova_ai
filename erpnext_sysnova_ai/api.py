import frappe
from frappe import _
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

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
            "You are Sysnova AI, an intelligent assistant inside ERPNext. "
            "You help users find files, search database records (like Invoices, Customers, Items), "
            "and answer queries based on the data. You have access to database search tools."
        )

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction,
            tools=[search_erpnext_database, find_uploaded_files]
        )

        # In a production app, you would maintain chat history in the database.
        # For this implementation, we use a stateless one-turn tool calling approach.
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(message)
        
        return {"status": "success", "reply": response.text}

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Gemini AI Error")
        return {"status": "error", "message": str(e)}


def search_erpnext_database(doctype: str, keyword: str) -> str:
    """
    Tool for Gemini to search any ERPNext Doctype.
    Returns a JSON string of matching records.
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            return json.dumps({"error": f"DocType {doctype} does not exist."})
        
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
