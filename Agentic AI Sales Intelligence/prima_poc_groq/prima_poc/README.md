# 💊 Prima Division – Sales Intelligence POC
### Powered by Groq AI (100% FREE)

---

## 📁 Folder Structure (Simple!)
```
prima_poc/
├── app.py            ← Run this
├── data_loader.py    ← Data processing
├── groq_helper.py    ← AI (Groq)
├── requirements.txt  ← Dependencies
├── .env              ← Your API key
└── data/
    └── sales_data.xlsx
```

---

## ✅ STEP 1 – Get FREE Groq API Key
1. Go to → https://console.groq.com
2. Sign up with Google (free, no credit card)
3. Click **API Keys → Create API Key**
4. Copy the key (starts with `gsk_...`)

---

## ✅ STEP 2 – Open in VS Code
1. Extract the ZIP file
2. Open VS Code → File → Open Folder → select `prima_poc`
3. Press **Ctrl + `** to open terminal

---

## ✅ STEP 3 – Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```
You will see `(venv)` in the terminal ✅

---

## ✅ STEP 4 – Install packages
```bash
pip install -r requirements.txt
```

---

## ✅ STEP 5 – Add API Key
Open `.env` file and paste your key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

---

## ✅ STEP 6 – Run the App
```bash
streamlit run app.py
```
Opens at → http://localhost:8501 🎉

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `python not found` | Install from python.org, tick "Add to PATH" |
| `cannot activate venv` | Run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| App opens but no AI | Paste Groq key in sidebar of the app |

---

## 💡 Tips
- You can also paste your Groq key directly in the **sidebar** of the running app
- Each AI insight button calls Groq only when you click it (saves quota)
- Groq free tier: 14,400 requests/day, very generous!
