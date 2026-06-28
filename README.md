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

Agar installation, rename, ya execution ke dauran niche diye gaye errors aate hain, to in steps se solve karein:

---

### 1. Error: `Module HR not found` (Site crash during migrate/startup)
* **Wajah (Cause):** `sites/apps.txt` ke missing hone ya aakhir mein line break (newline) na hone ki wajah se prompt ya other text `hrms` ke sath chipak jata hai aur system use load nahi kar pata.
* **Hal (Solution):** Run these commands on your server:
  ```bash
  # Rewrite apps.txt with correct line breaks
  printf "frappe\nemployee_self_service\ncrm\ndrive\neducation\npayments\nerpnext\ntelephony\nhelpdesk\nhrms\nai_assistant\n" > sites/apps.txt
  
  # Manually link HRMS in python env
  ./env/bin/pip install -e apps/hrms
  
  # Migrate and restart
  bench clear-cache
  bench --site your-site.com migrate
  bench restart
  ```

---

### 2. Error: `ModuleNotFoundError: No module named 'ai_assistant'` (Bench commands crash loop)
* **Wajah (Cause):** Agar `sites/apps.txt` mein app ka naam register ho par python virtual environment mein app link na hui ho, to bench startup par crash ho jata hai aur baqi commands block ho jati hain.
* **Hal (Solution):** 
  1. Pehle manually python environment mein link karein:
     ```bash
     ./env/bin/pip install -e apps/ai_assistant
     ```
  2. Phir normal setup run karein:
     ```bash
     bench --site your-site.com install-app ai_assistant
     bench build --app ai_assistant
     bench clear-cache
     bench restart
     ```

---

### 3. Error: `TypeError [ERR_INVALID_ARG_TYPE]` (bench build crash during compilation)
* **Wajah (Cause):** Custom app folder ke andar `package.json` file missing ho ya system ko na mile, jis se Yarn workspaces link nahi hotey aur esbuild script crash ho jati hai.
* **Hal (Solution):** Make sure karein ke `apps/ai_assistant/package.json` file exist karti ho. Phir commands run karein:
  ```bash
  bench setup requirements
  bench build --app ai_assistant
  bench clear-cache
  bench restart
  ```

---

### 4. Error: `404 Not Found` in browser console (Chat bubble not showing)
* **Wajah (Cause):** `/assets/ai_assistant/js/ai_assistant_widget.js` ka status 404 hota hai kyunki bench build ke dauran assets symlink (`sites/assets/ai_assistant`) generate nahi ho saki.
* **Hal (Solution):** PuTTY terminal par manually symlink link karein:
  ```bash
  ln -s ../../apps/ai_assistant/ai_assistant/public sites/assets/ai_assistant
  bench clear-cache
  bench restart
  ```

---

### 5. Error: `No module named 'ai_assistant.ai_assistant'`
* **Wajah (Cause):** Frontend JavaScript whitelisted API call path mein module ka naam duplicate ho raha ho (`ai_assistant.ai_assistant`).
* **Hal (Solution):** `ai_assistant_widget.js` file check karein aur call path ko badal kar `ai_assistant.api.chat_with_gemini` karein.

---

### 6. Error: `404 models/gemini-1.5-flash is not found`
* **Wajah (Cause):** Google ne `gemini-1.5-flash` model ko complete deprecate kar diya hai aur ab yeh `v1beta` ya `v1` par available nahi hai.
* **Hal (Solution):** Code (`api.py`) mein model ka naam badal kar **`gemini-2.5-flash`** karein.

---

### 7. Error: `429 You exceeded your current quota (limit: 0)`
* **Wajah (Cause):** Google AI Studio par aapke Google account ke free tier ki request limits **0** ho sakti hain agar aapka account Cloud restrictions ya regional policy ke tehat flagged ho.
* **Hal (Solution):** 
  Google AI Studio par jaakar click karein: **"Create API key in new project"** (existing GCP project select na karein). Ek naye project mein bani key automatic free limits allow kar deti hai.

---

### 8. Error: `429 You exceeded your current quota (limit: 20)`
* **Wajah (Cause):** Google AI Studio Free Tier par `gemini-2.5-flash` ka daily requests limit **20 calls per day** hai. Agar debugging ke dauran 20 calls pure ho jayein to yeh error reset hone tak aata hai.
* **Hal (Solution):** 
  1. Reset hone ka wait karein (har 24 ghante mein automatically reset ho jata hai).
  2. Ya phir AI Studio par **"Create API key in new project"** par click kar ke ek naya project key generate karein (naye project se mazeed 20 requests ki limit mil jayegi).

---

## License
MIT License. Free to use and modify.
