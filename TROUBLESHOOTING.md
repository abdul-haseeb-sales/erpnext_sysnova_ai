# Troubleshooting Guide - erpnext_sysnova_ai

Agar aapko application install karte waqt ya run karte waqt niche diye gaye errors aate hain, to unhe solve karne ke liye in steps ko follow karein:

---

## 1. Error: `Module HR not found` (Site crash on migrate)

### Wajah (Cause)
`apps.txt` file ko manually edit karte waqt `hrms` ka naam missing ho jata hai ya phir file ke aakhir mein newline character (line break) miss hone ki wajah se prompt ya other text `hrms` ke sath join ho jata hai. Is se python virtual environment `hrms` app ko load nahi kar pata.

### Hal (Solution)
1. **`sites/apps.txt` ko clean aur correct format mein set karein:**
   Server terminal par yeh command run karein:
   ```bash
   printf "frappe\nemployee_self_service\ncrm\ndrive\neducation\npayments\nerpnext\ntelephony\nhelpdesk\nhrms\nerpnext_sysnova_ai\n" > sites/apps.txt
   ```
2. **HRMS App ko virtual environment mein manually link/install karein:**
   ```bash
   ./env/bin/pip install -e apps/hrms
   ```
3. **Bench database update aur cache clear karein:**
   ```bash
   bench clear-cache
   bench --site [apki-site-name] migrate
   bench restart
   ```

---

## 2. Error: `No module named 'erpnext_sysnova_ai.erpnext_sysnova_ai'`

### Wajah (Cause)
Frontend API call whitelisted method (`sysnova_ai_widget.js`) mein call path galat ho. Agar module import path double named ho to python package use load nahi kar pata.

### Hal (Solution)
Make sure karein ke `sysnova_ai_widget.js` mein whitelisted path sirf single package name ke sath ho:
* **Galat Path:** `erpnext_sysnova_ai.erpnext_sysnova_ai.api.chat_with_gemini`
* **Sahi Path:** `erpnext_sysnova_ai.api.chat_with_gemini`

---

## 3. Error: `TypeError [ERR_INVALID_ARG_TYPE]...` (bench build fails)

### Wajah (Cause)
Custom app folder ke andar `package.json` file missing ho ya system ko na mile, jis se Yarn workspaces active nahi hotey aur `bench build` process crash ho jata hai.

### Hal (Solution)
1. **App directory mein `package.json` file create karein (`apps/erpnext_sysnova_ai/package.json`):**
   ```json
   {
     "name": "erpnext_sysnova_ai",
     "version": "0.0.1",
     "description": "Gemini AI Assistant for ERPNext",
     "author": "Sysnova Solutions",
     "license": "mit",
     "dependencies": {}
   }
   ```
2. **Yarn links ko refresh kar ke build chalaayein:**
   ```bash
   bench setup requirements
   bench build --app erpnext_sysnova_ai
   bench clear-cache
   bench restart
   ```

---

## 4. Error: `429 Quota Exceeded (limit: 0)` / `404 Model Not Found`

### Wajah (Cause)
* **404:** `gemini-1.5-flash` model ab retired/deprecated ho chuka hai aur `v1beta` par support nahi karta.
* **429 (limit: 0):** Google AI Studio par aapke free account project par billing ya limit restriction lag gayi hai.

### Hal (Solution)
1. **CMD par working free model verify karein:**
   Nayi key generate karein aur terminal ya Command Prompt par test karein ke kaunsa model active hai:
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
     -H "Content-Type: application/json" \
     -H "X-goog-api-key: APKI_GEMINI_API_KEY" \
     -X POST -d "{\"contents\": [{\"parts\": [{\"text\": \"Hello\"}]}]}"
   ```
2. **api.py mein working model set karein:**
   Agar `gemini-2.5-flash` work kar raha ho to use `api.py` ke model setup mein use karein:
   ```python
   model_name='gemini-2.5-flash',
   ```
3. **Nayi API Key apply karein:**
   ```bash
   bench --site [apki-site-name] set-config gemini_api_key "APKI_NEW_STUDIO_KEY"
   bench restart
   ```
