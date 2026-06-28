# ERPNext AI Assistant

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
   bench get-app https://github.com/abdul-haseeb-sales/ai_assistant.git
   bench --site your-site.com install-app ai_assistant
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
Click it to open the AI Assistant. 

Try asking:
- *"Find sales invoices created for Sysnova"*
- *"Search for a file named report.pdf"*

## Detailed Troubleshooting / Common Errors

If you encounter any of the following errors during installation, renaming, or execution, follow these steps to resolve them:

---

### 1. Error: `Module HR not found` (Site crash during migrate/startup)
* **Cause:** The `sites/apps.txt` file is either missing or does not end with a newline character, causing the `hrms` app entry to get corrupted or linked with the prompt hostname. Thus, the virtual environment fails to load it.
* **Solution:** Run these commands on your server:
  ```bash
  # Rewrite apps.txt with correct line breaks
  printf "frappe\nemployee_self_service\ncrm\ndrive\neducation\npayments\nerpnext\ntelephony\nhelpdesk\nhrms\nai_assistant\n" > sites/apps.txt
  
  # Manually link HRMS in the python virtual environment
  ./env/bin/pip install -e apps/hrms
  
  # Migrate the database and restart bench
  bench clear-cache
  bench --site your-site.com migrate
  bench restart
  ```

---

### 2. Error: `ModuleNotFoundError: No module named 'ai_assistant'` (Bench commands crash loop)
* **Cause:** The app `ai_assistant` is registered in `sites/apps.txt`, but it has not been linked in the python virtual environment yet. Frappe crashes during startup trying to load the missing module, blocking all other bench commands.
* **Solution:** 
  1. Link the app module manually in the virtual environment first:
     ```bash
     ./env/bin/pip install -e apps/ai_assistant
     ```
  2. Once linked, proceed with the normal setup commands:
     ```bash
     bench --site your-site.com install-app ai_assistant
     bench build --app ai_assistant
     bench clear-cache
     bench restart
     ```

---

### 3. Error: `TypeError [ERR_INVALID_ARG_TYPE]` (bench build crash during compilation)
* **Cause:** The custom app directory is missing a `package.json` file, causing Yarn workspaces and esbuild compilation to fail during asset building.
* **Solution:** Ensure that the `apps/ai_assistant/package.json` file exists. Then run:
  ```bash
  bench setup requirements
  bench build --app ai_assistant
  bench clear-cache
  bench restart
  ```

---

### 4. Error: `404 Not Found` in browser console (Chat bubble not showing)
* **Cause:** The asset symlink (`sites/assets/ai_assistant`) was not automatically created in the sites assets directory during build, leading Nginx to return a 404 error when loading `ai_assistant_widget.js`.
* **Solution:** Create the symlink manually on your server:
  ```bash
  ln -s ../../apps/ai_assistant/ai_assistant/public sites/assets/ai_assistant
  bench clear-cache
  bench restart
  ```

---

### 5. Error: `No module named 'ai_assistant.ai_assistant'`
* **Cause:** The whitelisted method path in the JavaScript API call has a duplicate namespace (`ai_assistant.ai_assistant`).
* **Solution:** Verify `ai_assistant_widget.js` and change the API call path to `ai_assistant.api.chat_with_gemini`.

---

### 6. Error: `404 models/gemini-1.5-flash is not found`
* **Cause:** Google has deprecated and retired the `gemini-1.5-flash` model on the `v1beta` / `v1` endpoints.
* **Solution:** Update the model name in your `api.py` to **`gemini-2.5-flash`**.

---

### 7. Error: `429 You exceeded your current quota (limit: 0)`
* **Cause:** Google AI Studio has set your free tier limits to **0** for this Google account or project due to a missing billing method or regional/account policy flags.
* **Solution:** 
  Go to Google AI Studio and click **"Create API key in new project"** (do not select an existing GCP project). Creating the key in a new clean project automatically enables the free tier quota.

---

### 8. Error: `429 You exceeded your current quota (limit: 20)`
* **Cause:** The Gemini 2.5 Flash free tier has a daily request limit of **20 calls per day per project**. Exceeding it triggers this rate-limit error.
* **Solution:** 
  1. Wait for the 24-hour cycle to reset (resets automatically at UTC midnight).
  2. Or go to Google AI Studio and click **"Create API key in new project"** to get a fresh API key with another 20 daily requests limit.

---

## License
MIT License. Free to use and modify.
