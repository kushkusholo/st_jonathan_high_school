# 📚 Chatbot Administration Guide

## For School Administrators

This guide explains how to manage and maintain the St. Jonathan High School Chatbot.

---

## 1️⃣ Managing FAQs

### Adding New FAQs

1. **Open** the FAQ file: `data/faqs.json`
2. **Find** the last FAQ entry (highest ID number)
3. **Add** a new entry:

```json
{
    "id": 13,
    "question": "What is your question?",
    "answer": "Your detailed answer here. You can use:\n• Bullet points\n**Bold text**",
    "category": "CategoryName",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

4. **Save** the file
5. **Restart** the chatbot (stop and run again)
6. **Test** by asking the question in the chatbot

### Editing Existing FAQs

1. Open `data/faqs.json`
2. Find the FAQ you want to edit
3. Update the "answer" or other fields
4. Save and restart the chatbot

### Deleting FAQs

1. Open `data/faqs.json`
2. Remove the entire FAQ entry
3. Save and restart

### Guidelines for Good FAQs

✅ **Do:**
- Be clear and concise
- Answer common parent questions
- Include specific details (dates, fees, processes)
- Use keywords that parents would search for
- Update regularly

❌ **Don't:**
- Use overly technical language
- Make assumptions
- Leave incomplete information
- Forget to test new FAQs

---

## 2️⃣ Monitoring Conversations

### Accessing Chat Logs

1. Navigate to: `logs/chat_logs.json`
2. Each entry shows:
   - **timestamp**: When the conversation happened
   - **user_message**: What the parent asked
   - **bot_response_type**: Type of response (FAQ, greeting, etc.)
   - **bot_response**: What the chatbot replied

### Analyzing Logs

**To identify common questions:**
```bash
# Look for frequently asked questions patterns
# Questions that didn't get good answers (response_type: "unknown")
# These areas may need new FAQs
```

**What to look for:**
- Repeated "unknown" responses → Need new FAQs
- Multi-stage conversations → FAQ clarity issue
- Time patterns → Peak inquiry times
- Common misconceptions → Unclear FAQ

### Backup Logs

- Back up `logs/chat_logs.json` regularly
- Archive old logs monthly
- Keep for historical reference

---

## 3️⃣ Updating School Information

### Method 1: Edit app.py (Direct)

Find this section in `app.py` and update:

```python
SCHOOL_INFO = {
    "name": "St. Jonathan High School",
    "address": "P.O. Box 12352, Kampala",
    "location": "Jinja-Kampala Highway, next to Mbalala Trading Centre",
    "phone": "+256325516717",
    "email": "info@stjonathan.ug",
    "established": 2010,
    "principal": "Dr. Samuel Mugisha"
}
```

Then restart the chatbot.

### Method 2: Use config.py

The `config.py` file contains detailed configuration for different departments.

Update any information needed and reference it in the app.

---

## 4️⃣ Customizing the Chatbot

### Change School Colors

Edit `static/style.css`:

```css
:root {
    --primary-color: #2c3e50;      /* Dark blue */
    --secondary-color: #3498db;    /* Light blue */
    --accent-color: #e74c3c;       /* Red */
    --success-color: #27ae60;      /* Green */
    --light-bg: #ecf0f1;           /* Light gray */
}
```

### Add Custom Greeting

In `app.py`, modify the `generate_response()` function:

```python
def generate_response(user_query):
    # Modify greeting response
    if any(greeting in user_query.lower() for greeting in greetings):
        return {
            "response": "Your custom greeting here...",
            "type": "greeting"
        }
```

### Change Default Welcome Message

Edit `templates/index.html` to modify the welcome message that appears when the page first loads.

---

## 5️⃣ Performance & Optimization

### Monitor Server Load

- Check if chatbot is running: `http://localhost:5000`
- Monitor response times
- Check memory usage

### Optimize FAQs

- Remove duplicate FAQs
- Combine related topics
- Improve keyword matching
- Test query matching accuracy

### Clean Up Logs

```python
# Keep only recent conversations to save space
# In app.py, modify max_log_entries: logs[-1000:] means keep last 1000
```

---

## 6️⃣ Troubleshooting

### Chatbot Not Responding

1. Check if Flask is running
2. Check browser console (F12) for errors
3. Verify JSON syntax in FAQs file
4. Restart the application

### FAQ Not Found

1. Verify keyword matches user query
2. Check JSON format in faqs.json
3. Ensure similarity_threshold is appropriate (0.3 is default)
4. Add more similar keywords

### Styling Issues

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check CSS file for syntax errors
4. Verify file paths in HTML

---

## 7️⃣ Regular Maintenance

### Weekly Tasks
- [ ] Check chat logs for common questions
- [ ] Review unanswered queries
- [ ] Update any outdated information
- [ ] Test chatbot functionality

### Monthly Tasks
- [ ] Back up chat logs
- [ ] Analyze usage patterns
- [ ] Add new FAQs based on inquiries
- [ ] Update school calendar/dates

### Quarterly Tasks
- [ ] Review and refine FAQ accuracy
- [ ] Update fees and charges
- [ ] Refresh school contact information
- [ ] Optimize chatbot performance

---

## 8️⃣ FAQ Improvement Workflow

1. **Monitor** conversations in logs
2. **Identify** unanswered questions (response_type: "unknown")
3. **Create** new FAQs for common questions
4. **Test** new FAQs with sample queries
5. **Track** improvement in response quality
6. **Update** based on feedback

---

## 9️⃣ User Support

### For Technical Issues

**Common Problems & Solutions:**

| Problem | Solution |
|---------|----------|
| Chatbot won't start | Verify Python installed, check port availability |
| FAQs not showing | Check JSON syntax, restart app |
| Page won't load | Check if Flask is running on port 5000 |
| Chat not responding | Check browser console, verify internet connection |

### For Content Issues

| Problem | Solution |
|---------|----------|
| Old information shown | Update FAQs and restart |
| FAQ quality poor | Review and rewrite for clarity |
| Missing FAQs | Check logs for unanswered questions |

---

## 🔟 Best Practices

✅ **Do:**
1. Keep FAQs accurate and up-to-date
2. Monitor user queries weekly
3. Back up chat logs regularly
4. Test new changes before going live
5. Document changes made
6. Respond to feedback quickly
7. Update school info when it changes
8. Archive old logs annually

❌ **Don't:**
1. Leave outdated information
2. Ignore unanswered questions
3. Skip backups
4. Make changes without testing
5. Use sensitive information in FAQs
6. Overload with too many FAQs
7. Ignore performance issues

---

## 📞 Support Contacts

**For Chatbot Support:**
- Contact IT Department at +2563
- Email: tech@stjonathan.ug

**For Content Updates:**
- Contact Academic Department
- Contact Admissions Office

---

## 📋 Maintenance Checklist

Use this checklist for regular maintenance:

```
Weekly:
□ Check chat logs
□ Review unanswered questions
□ Update urgent information
□ Verify chatbot is running

Monthly:
□ Back up chat logs
□ Analyze usage patterns
□ Add new FAQs
□ Verify school contact info
□ Test all FAQ links

Quarterly:
□ Full FAQ audit
□ Update fees/charges
□ Refresh event calendar
□ Performance review
□ Archive old logs

Annually:
□ Complete system review
□ Update school motto/vision
□ Refresh all content
□ Plan improvements
```

---

**Last Updated:** April 2024
**Next Review:** July 2024
