# 🚀 Quick Start Guide - St. Jonathan High School Chatbot

## ⚡ 5-Minute Setup

### Step 1: Install Python
- Download Python 3.11+ from https://www.python.org/
- During installation, **check "Add Python to PATH"**
- If you already have a newer Python version, use `py -3.11` or `python3.11` when creating the virtual environment.

### Step 2: Setup Virtual Environment
Open Command Prompt/Terminal and run:

```bash
# Navigate to project folder
cd path\to\school_chatbot

# Create virtual environment
python -m venv venv
# If your default python is not 3.11, use one of these instead:
# py -3.11 -m venv venv
# python3.11 -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Chatbot
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 5: Open in Browser
Go to: **http://localhost:5000**

---

## 📋 What's Here

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application |
| `data/faqs.json` | FAQ database |
| `templates/index.html` | Web interface |
| `static/style.css` | Styling |
| `static/script.js` | Chat functionality |
| `config.py` | Configuration file |
| `requirements.txt` | Python packages |

---

## 🎯 Common Tasks

### Add a New FAQ
1. Open `data/faqs.json`
2. Add a new entry:
```json
{
    "id": 13,
    "question": "What's your question?",
    "answer": "Your detailed answer here...",
    "category": "Category",
    "keywords": ["key1", "key2"]
}
```
3. Save and refresh the browser

### Update School Information
Edit `app.py` line 14-21 with new info:
```python
SCHOOL_INFO = {
    "name": "Your School",
    "phone": "+256...",
    ...
}
```

### Access Chat Logs
- Location: `/logs/chat_logs.json`
- Contains all parent conversations
- Use for analysis and improvement

### Change Colors
Edit `static/style.css` to modify the color scheme:
- `--primary-color: #2c3e50` (Dark blue)
- `--secondary-color: #db34bc` (Light blue)
- `--accent-color: #2980e9` (Red)

---

## 🔧 Troubleshooting

**"Port 5000 is already in use"**
```bash
# Use different port
python app.py --port 5001
```
Then visit: http://localhost:5001

**"Module not found" error**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Use Python 3.11 for this project
# If needed, recreate the venv with Python 3.11:
# py -3.11 -m venv venv
# python3.11 -m venv venv

# Then install again
pip install -r requirements.txt
```

**FAQs not showing**
- Check if `/data/faqs.json` exists
- Validate JSON format (use online JSON validator)
- Restart Flask app

**Chat not responding**
- Open Browser DevTools (F12)
- Check Console for errors
- Verify Flask is running (should see "Running on...")

---

## 📱 Mobile Access

To access chatbot from other devices on network:

1. Find your computer's IP:
   - Windows: Run `ipconfig` in Command Prompt
   - Mac/Linux: Run `ifconfig`
   
2. Share IP with others (e.g., 192.168.x.x)

3. Modify `app.py` line (last few lines):
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

4. Others can now access: `http://192.168.x.x:5000`

---

## 📞 School Contact

**St. Jonathan High School**
- Phone: +256701416197
- Email: info@stjonathan.ug
- Location: Jinja-Kampala Highway, Kampala

---

## 🎓 Features Overview

✅ **What the Chatbot Can Do:**
- Answer FAQs instantly
- Provide school contact information
- Help with admissions questions
- Explain fee structure
- Share academic calendar
- Describe facilities and programs
- Suggest extracurricular activities
- Explain school policies

---

## 📊 Next Steps

1. ✅ Get it running (you're here!)
2. Add your school's specific FAQs
3. Test with sample questions
4. Share link with parents
5. Monitor conversations in logs
6. Improve FAQs based on feedback

---

## 💡 Tips

- Keep FAQs updated and accurate
- Monitor chat logs weekly
- Add new FAQs based on common questions
- Test on mobile devices
- Keep school contact info current
- Back up chat logs regularly

---

## 📚 Learn More

Full documentation: See `README.md`

Need help? Contact the school IT department or technical support.

Happy chatting! 🎉
