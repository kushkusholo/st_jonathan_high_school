# 📂 Project File Structure & Overview

## St. Jonathan High School Chatbot - Complete File Reference

```
school_chatbot/
│
├── 📄 Documentation Files
│   ├── README.md                 - Complete project documentation
│   ├── QUICKSTART.md            - 5-minute setup guide (START HERE!)
│   ├── ADMINISTRATION.md        - Admin guide & FAQ management
│   ├── DEPLOYMENT.md            - How to deploy online
│   └── PROJECT_STRUCTURE.md     - This file
│
├── 🐍 Python Backend
│   ├── app.py                   - Main Flask application (chatbot logic)
│   ├── config.py                - Configuration file (school info, settings)
│   └── requirements.txt         - Python dependencies
│
├── 🚀 Quick Launch Scripts
│   ├── run.bat                  - Windows launcher (double-click to run)
│   └── run.sh                   - Mac/Linux launcher
│
├── 📁 data/
│   └── faqs.json               - FAQ database (add new FAQs here!)
│
├── 📁 templates/
│   └── index.html              - Web interface (chatbot page)
│
├── 📁 static/
│   ├── style.css               - Styling & colors
│   └── script.js               - Chat functionality (JavaScript)
│
└── 📁 logs/ (auto-created)
    └── chat_logs.json          - Conversation history (created automatically)
```

---

## 📚 File Descriptions

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Full technical documentation | Developers, IT staff |
| **QUICKSTART.md** | 5-minute setup guide | Everyone (START HERE) |
| **ADMINISTRATION.md** | How to manage chatbot & FAQs | School administrators |
| **DEPLOYMENT.md** | How to deploy online | IT staff, developers |

### Backend (Python)

| File | Purpose | Edit When |
|------|---------|-----------|
| **app.py** | Main chatbot logic & Flask server | Adding features, fixing bugs |
| **config.py** | School info & departments | Updating school details |
| **requirements.txt** | Python packages needed | Adding new packages |

### Startup Files

| File | Purpose | Platform |
|------|---------|----------|
| **run.bat** | Easy startup script | Windows (double-click!) |
| **run.sh** | Easy startup script | Mac/Linux |

### Frontend (Web Interface)

| File | Purpose | Edit When |
|------|---------|-----------|
| **templates/index.html** | Chatbot webpage | Changing layout, adding sections |
| **static/style.css** | Colors, fonts, styling | Changing appearance |
| **static/script.js** | Chat interaction logic | Adding features, bug fixes |

### Data

| File | Purpose | Edit When |
|------|---------|-----------|
| **data/faqs.json** | FAQ questions &  answers | Adding new FAQs, updating info |

### Logs (Auto-generated)

| File | Purpose | Review When |
|------|---------|-----------|
| **logs/chat_logs.json** | Conversation history | Finding common questions |

---

## 🎯 Quick Navigation Guide

### "I want to..."

#### ...Start the chatbot
- **Windows:** Double-click `run.bat`
- **Mac/Linux:** Run `./run.sh`
- Then open: http://localhost:5000

#### ...Add a new FAQ
→ Edit: `data/faqs.json`
See: [ADMINISTRATION.md](ADMINISTRATION.md#1️⃣-managing-faqs)

#### ...Change school phone/address
→ Edit: `app.py` (lines 14-21)
Or Edit: `config.py`

#### ...Change colors/styling
→ Edit: `static/style.css`

#### ...Fix chatbot responses
→ Edit: `app.py` (generate_response function)

#### ...See what parents asked
→ View: `logs/chat_logs.json`

#### ...Deploy online
→ Read: [DEPLOYMENT.md](DEPLOYMENT.md)

#### ...Update FAQ/add admin panel
→ Edit: `app.py` and `templates/index.html`

#### ...Backup everything
→ Copy entire `school_chatbot` folder

---

## 📊 File Statistics

```
Total Files: 12
Total Folders: 4

Lines of Code:
- app.py:         ~250 lines
- script.js:      ~150 lines  
- style.css:      ~500 lines
- index.html:     ~100 lines
- faqs.json:      ~350 lines (12 FAQs)

Documentation:
- README.md:      ~400 lines
- QUICKSTART.md:  ~200 lines
- DEPLOYMENT.md:  ~400 lines
- ADMINISTRATION.md: ~500 lines
```

---

## 🔄 Data Flow

```
User Input (Browser)
        ↓
    script.js (Frontend)
        ↓
    /api/chat (Flask API)
        ↓
    app.py (Chatbot Logic)
        ↓
    faqs.json (Search FAQs)
        ↓
    Generate Response
        ↓
    logs/chat_logs.json (Log it)
        ↓
    Return Response
        ↓
    Display to User (Browser)
```

---

## 🛠️ How It Works

1. **User visits chatbot** → Index.html loads with styling
2. **User types question** → JavaScript sends to Flask
3. **Flask processes** → Matches best FAQ
4. **Response generated** → Logged to chat_logs.json
5. **Answer displayed** → User sees response

---

## 🔐 Important Files (Backup These!)

- 🔴 **faqs.json** - Your FAQ database
- 🔴 **logs/chat_logs.json** - Conversation history
- 🟡 **app.py** - Chatbot logic
- 🟡 **config.py** - Configuration

---

## ⚙️ Configuration Points

### In **app.py**:
```python
SCHOOL_INFO = {}          # Update school details here
generate_response()        # Modify chatbot behavior here
```

### In **config.py**:
```python
SCHOOL_CONFIG = {}        # Detailed school configuration
```

### In **static/style.css**:
```css
:root {}                   # Change colors here
```

### In **data/faqs.json**:
```json
[]                        # Add FAQs here
```

---

## 📱 Features by File

### app.py provides:
- Chat API endpoint
- FAQ matching algorithm
- School information display
- Conversation logging
- Greeting detection

### script.js provides:
- Message sending
- Chat display
- User input handling
- FAQ modal
- Keyboard shortcuts

### style.css provides:
- Color scheme
- Layout/grid system
- Responsive design
- Animations
- Mobile optimization

### index.html provides:
- Page structure
- Information panel
- Chat window
- Input area
- School branding

---

## 🚀 Getting Started

### Quick Path:
1. Read: `QUICKSTART.md`
2. Run: `run.bat` (Windows) or `run.sh` (Mac/Linux)
3. Visit: http://localhost:5000
4. Edit: `data/faqs.json` to add FAQs

### Admin Path:
1. Read: `ADMINISTRATION.md`
2. Monitor: `logs/chat_logs.json`
3. Update: Add new FAQs regularly
4. Improve: Based on user queries

### Deployment Path:
1. Read: `DEPLOYMENT.md`
2. Choose: Hosting platform
3. Deploy: Following platform guide
4. Share: URL with parents

---

## 💡 Pro Tips

✅ **DO:**
- Keep FAQs updated
- Monitor chat logs weekly
- Back up regularly
- Test before deploying
- Add new FAQs based on queries

❌ **DON'T:**
- Leave outdated info
- Ignore unanswered questions
- Edit files while running
- Forget to save changes
- Deploy untested changes

---

## 📞 Support

**For Technical Issues:**
- Check error logs
- Review browser console (F12)
- Restart the application
- Read relevant documentation file

**For Content Issues:**
- Update FAQs
- Verify school information
- Test new additions

---

## 🎓 Learning Resources

### Within Project:
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [README.md](README.md) - Full documentation
- [ADMINISTRATION.md](ADMINISTRATION.md) - Managing content
- [DEPLOYMENT.md](DEPLOYMENT.md) - Going online

### External:
- Flask Documentation: https://flask.palletsprojects.com/
- JavaScript Tutorial: https://www.javascript.info/
- HTML/CSS Guide: https://www.w3schools.com/

---

## 📝 Editing Checklist

Before editing files:
- [ ] Stop the chatbot (if running)
- [ ] Make backup copy
- [ ] Edit the file
- [ ] Check syntax
- [ ] Save
- [ ] Restart chatbot
- [ ] Test changes
- [ ] Verify it works

---

## 🔍 File Dependencies

```
index.html
├── Loads: style.css
├── Loads: script.js
└── Requires: app.py backend

app.py
├── Reads: data/faqs.json
├── Writes: logs/chat_logs.json
└── Serves: templates/index.html

script.js
└── Calls: /api/chat endpoint
```

---

## 📊 Version Info

- **Version:** 1.0
- **Created:** April 2024
- **For:** St. Jonathan High School
- **Location:** Kampala, Uganda
- **Python:** 3.11+
- **Flask:** 3.0.2

---

## 🎉 You're All Set!

Your chatbot is ready to use. Start with:

**Windows:** `run.bat`
**Mac/Linux:** `run.sh`

Then visit: `http://localhost:5000`

Happy chatting! 🤖

---

Last Updated: April 2024
