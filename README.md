# St. Jonathan High School - Parent Portal Chatbot

A comprehensive web-based chatbot system designed to facilitate communication between parents and school administration at St. Jonathan High School, Kampala, Uganda.

## Features

✨ **Key Features:**
- 🤖 AI-powered chatbot with natural language understanding
- 📚 Comprehensive FAQ database about school operations
- 💬 Real-time parent-school communication
- 📱 Responsive design for mobile and desktop
- 🎯 Smart query matching and answer retrieval
- 📊 Conversation logging for school administration
- 🔒 User-friendly interface with quick suggestions
- 📞 Direct contact information display

## School Information

**St. Jonathan High School**
- **Address:** P.O. Box 12352, Kampala
- **Location:** Jinja-Kampala Highway, next to Mbalala Trading Centre
- **Phone:** +256325516717
- **Email:** info@stjonathan.ug
- **Principal:** Dr. Samuel Mugisha
- **Established:** 2010

## FAQ Categories

The chatbot covers the following topics:

1. **Admissions** - Admission requirements and procedures
2. **Fees & Payments** - Fee structure and scholarship information
3. **Academic Calendar** - Term dates and holidays
4. **Academics** - Subjects offered and curriculum
5. **Facilities** - Boarding facilities and campus amenities
6. **Contact** - School contact information
7. **About School** - School vision, mission, and values
8. **Student Life** - Extracurricular activities and clubs
9. **School Policies** - Discipline and conduct policies

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git (optional)

### Step 1: Clone or Download the Project

```bash
cd school_chatbot
```

### Step 2: Create a Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### Step 5: Access the Chatbot

Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
school_chatbot/
│
├── app.py                      # Flask application (main backend)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data/
│   └── faqs.json              # FAQ database
│
├── logs/
│   └── chat_logs.json         # Conversation logs
│
├── templates/
│   └── index.html             # Main chatbot interface
│
└── static/
    ├── style.css              # Styling
    ├── script.js              # Frontend JavaScript
    └── ...
```

## Usage Guide

### For Parents/Guardians:

1. **Open the chatbot** in your web browser
2. **Ask questions** about:
   - School admissions
   - Fees and payment plans
   - Academic calendar and holidays
   - Boarding facilities
   - School facilities and amenities
   - Extracurricular activities
   - School policies
   - Direct school contact

3. **Use quick suggestions** on the left panel for common questions
4. **View all FAQs** by clicking "View All FAQs" button
5. **Call the school** directly at +256325516717 for urgent matters

### For Administrators:

1. **Access chat logs** in `/logs/chat_logs.json`
2. **Update FAQs** in `/data/faqs.json`
3. **Monitor queries** to understand parent concerns
4. **Improve responses** based on conversation patterns

## Adding New FAQs

To add new FAQs, edit `/data/faqs.json`:

```json
{
    "id": 13,
    "question": "Your question here?",
    "answer": "Your answer here with details.",
    "category": "Category Name",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

## API Endpoints

### Chat Endpoint
- **URL:** `/api/chat`
- **Method:** POST
- **Body:** `{ "message": "user question" }`
- **Response:** 
```json
{
    "success": true,
    "message": "bot response",
    "type": "faq|greeting|school_info|unknown",
    "category": "FAQ category"
}
```

### Get FAQs
- **URL:** `/api/faqs`
- **Method:** GET
- **Response:** Array of FAQ objects

### Get School Info
- **URL:** `/api/school-info`
- **Method:** GET
- **Response:** School information object

## Features Explained

### Smart Query Matching
The chatbot uses sequence matching to find the most relevant FAQ based on:
- Question similarity
- Keyword matching
- Contextual understanding

### Conversation Logging
All conversations are logged for:
- Quality improvement
- Analytics
- Understanding common queries
- Better FAQ development

### Responsive Design
- Works on desktop, tablet, and mobile
- Touch-friendly interface
- Adaptive layout

## Customization

### Change School Information
Edit the `SCHOOL_INFO` dictionary in `app.py`:

```python
SCHOOL_INFO = {
    "name": "Your School Name",
    "address": "Your Address",
    ...
}
```

### Modify ChatBot Behavior
Edit the `generate_response()` function in `app.py` to:
- Add new response types
- Modify matching algorithms
- Add new features

### Update Styling
Modify `static/style.css` to:
- Change colors
- Adjust fonts
- Update layout

## Deployment

### For Local Network Access
Change the host in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### For Production
Consider using:
- Gunicorn: `gunicorn app:app`
- Heroku for cloud hosting
- Docker containerization
- Nginx as reverse proxy

## Troubleshooting

### Issue: Port 5000 already in use
**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Issue: FAQs not loading
**Solution:** Ensure `/data/faqs.json` exists and has valid JSON

### Issue: Chat not responding
**Solution:** Check browser console (F12) for errors and verify Flask is running

## Security Notes

- This is a demonstration chatbot - review before deploying to production
- Implement user authentication for sensitive data
- Use HTTPS in production
- Sanitize user inputs
- Add rate limiting for API endpoints

## Contact & Support

**School Contact:**
- Phone: +256325516717
- Email: info@stjonathan.ug
- Location: Jinja-Kampala Highway, Kampala

**Technical Support:**
For technical issues with the chatbot system, contact the IT department.

## Future Enhancements

Potential improvements for future versions:
- User authentication and parent portal
- Integration with school management system
- Multiple language support (Luganda, Swahili)
- Appointment booking system
- Payment gateway integration
- Admin dashboard for FAQ management
- Advanced analytics and reporting
- Mobile app version
- AI/ML integration for better query understanding

## License

This project is proprietary to St. Jonathan High School. All rights reserved.

---

**Version:** 1.0
**Last Updated:** April 2024
**Developed for:** St. Jonathan High School, Kampala, Uganda
