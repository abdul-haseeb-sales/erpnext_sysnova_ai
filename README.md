# ERPNext Sysnova AI Assistant

[![Frappe Framework](https://img.shields.io/badge/Frappe-v16-blue.svg)](https://frappeframework.com/)
[![ERPNext](https://img.shields.io/badge/ERPNext-v16-brightgreen.svg)](https://erpnext.com/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://aistudio.google.com/)

An advanced Floating Chat Assistant for ERPNext v16 powered by **Google Gemini API**. 

It allows users to interact with ERPNext via natural language. The AI uses **Function Calling (Tools)** to search the ERPNext database (e.g., finding Invoices, Customers) and locate uploaded files automatically.

## Features
- ✅ **Floating Chat UI:** Always available on the bottom right of your ERPNext Desk.
- ✅ **Gemini AI Integration:** Connects directly using your personal Gemini API key.
- ✅ **Database Search Tool:** Ask AI to "Find an invoice for John Doe" and it will query the database.
- ✅ **File Search Tool:** Ask AI "Where is the file logo.png?" and it will search Frappe's file manager.

## Installation

1. Switch to your frappe-bench directory on your Ubuntu server:
   ```bash
   cd frappe-bench
   ```

2. Clone and install the app:
   ```bash
   bench get-app https://github.com/abdul-haseeb-sales/erpnext_sysnova_ai.git
   bench --site your-site.com install-app erpnext_sysnova_ai
   ```

3. **Install the Google Generative AI Library:**
   You must install the python library in your frappe virtual environment.
   ```bash
   ./env/bin/pip install google-generativeai
   ```

## Configuration (API Key Setup)

The AI needs your personal Gemini API key to work.

1. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Save the API key in your site's config using bench:
   ```bash
   bench --site your-site.com set-config gemini_api_key "YOUR_ACTUAL_API_KEY_HERE"
   ```
3. Restart bench:
   ```bash
   bench restart
   ```

## Usage

Once installed and configured, log in to ERPNext. You will see a blue chat bubble icon in the bottom right corner of the screen.
Click it to open the Sysnova AI Assistant. 

Try asking:
- *"Find sales invoices created for Sysnova"*
- *"Search for a file named report.pdf"*

## License
MIT License. Free to use and modify.
