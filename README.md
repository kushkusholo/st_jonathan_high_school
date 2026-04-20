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
- 👥 **NEW:** Parent/Student/Staff authentication and dashboards
- 💰 **NEW:** Payment tracking and mobile money integration
- 📱 **NEW:** WhatsApp messaging integration
- 🔔 **NEW:** Notification system for announcements
- 🎤 **NEW:** Voice assistant with browser speech recognition
- 👨‍🏫 **NEW:** Staff portal for attendance and exam management
- 👨‍💼 **NEW:** Admin dashboard for full school management

## School Information

**St. Jonathan High School**
- **Address:** P.O. Box 12352, Kampala
- **Location:** Jinja-Kampala Highway, next to Mbalala Trading Centre
- **Phone:** +256701416197
- **Email:** info@stjonathan.ug
- **Principal:** Dr. MAIKI PROTUS
- **Established:** 2017

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

## New Features Overview

### User Authentication & Portals
- **Parent Portal:** Register children, view fees, make payments, receive notifications
- **Student Portal:** View personal records and notifications
- **Staff Portal:** Manage attendance, record exam results, send WhatsApp messages
- **Admin Portal:** Full school management including students, staff, payments, notifications

### Payment System
- Mobile money payment requests
- Payment reconciliation dashboard
- Mobile money callback simulation
- Payment status tracking (pending/confirmed/rejected)

### WhatsApp Integration
- Automated WhatsApp webhook for incoming messages
- Admin inbox for viewing and replying to messages
- Message history storage

### Notification System
- Create targeted announcements (all users, parents, students, staff, admins)
- Notification dashboard for users
- Automated delivery system

### Voice Assistant
- Browser-based speech recognition
- Voice input for chatbot queries
- Real-time response display

### Staff Management Tools
- Attendance recording with date, status, and remarks
- Exam result entry with scores and grades
- Student record management

### Admin Management Tools
- Student and staff CRUD operations
- FAQ management (add/delete)
- Chat log viewing and clearing
- Payment reconciliation
- Notification creation
- WhatsApp message management

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

### Step 3.1: Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```bash
# Required
SECRET_KEY=your_secure_random_secret_here

# Optional - AI Features
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Admin Access
ADMIN_PASSWORD=your_admin_password_here

# Optional - WhatsApp Integration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Optional - Deployment
DEBUG=False
PORT=5000
```

### Step 3.2: Admin Setup
After setting `ADMIN_PASSWORD`, access the admin dashboard at:
```
http://localhost:5000/admin/login
```

Use the admin dashboard to:
- Manage FAQs
- View chat logs
- Manage students, staff, and notifications
- Reconcile payments
- View WhatsApp messages

### Step 3.3: User Registration
Parents can register at:
```
http://localhost:5000/auth/register
```

Staff and students can also register and access role-specific portals.

### Step 3.4: WhatsApp Setup (Optional)
To enable WhatsApp messaging:
1. Set up a Twilio account
2. Configure a WhatsApp sandbox or business account
3. Set the webhook URL to: `https://yourdomain.com/whatsapp/webhook`
4. Add the Twilio credentials to `.env`

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
├── config.py                   # Configuration settings
├── runtime.txt                 # Python runtime version
├── Procfile                    # Heroku deployment
├── render.yaml                 # Render deployment
├── run.bat                     # Windows startup script
├── run.sh                      # Linux/Mac startup script
│
├── data/
│   └── faqs.json              # FAQ database
│
├── logs/
│   └── chat_logs.json         # Conversation logs
│
├── static/
│   ├── style.css              # Main styling
│   ├── script.js              # Frontend JavaScript
│   └── admission_form.txt     # Admission form download
│
└── templates/
    ├── index.html             # Main chatbot interface
    ├── admin_dashboard.html   # Admin FAQ management
    ├── admin_login.html       # Admin authentication
    ├── admin_logs.html        # Chat log viewer
    ├── admin_students.html    # Student management
    ├── admin_staff.html       # Staff management
    ├── admin_notifications.html # Notification management
    ├── admin_whatsapp.html    # WhatsApp inbox
    ├── admin_payments.html    # Payment reconciliation
    ├── auth_login.html        # User login
    ├── auth_register.html     # User registration
    ├── dashboard.html         # User dashboard
    ├── admissions.html        # Admissions guide
    ├── payments.html          # Payment portal
    ├── notifications.html     # Notification viewer
    ├── voice.html             # Voice assistant
    ├── staff_attendance.html  # Attendance management
    └── staff_exams.html       # Exam management
```

## Usage Guide

### For Parents/Guardians:
1. **Register:** Create an account and add your children
2. **Chat:** Ask questions about school services
3. **Pay Fees:** Submit payment requests via mobile money
4. **View Records:** Check notifications and payment status
5. **Contact:** Use WhatsApp or call for urgent matters

### For Students:
1. **Login:** Access your personal dashboard
2. **View Notifications:** Stay updated on school announcements
3. **Access Services:** Use voice assistant and payment portal

### For Staff:
1. **Login:** Access staff portal
2. **Record Attendance:** Mark daily attendance for students
3. **Enter Exam Results:** Record scores and grades
4. **Send Messages:** Reply to WhatsApp inquiries

### For Administrators:
1. **Login:** Access admin dashboard
2. **Manage Data:** Add/edit students, staff, FAQs
3. **Reconcile Payments:** Confirm or reject payment requests
4. **Send Notifications:** Create announcements for users
5. **Monitor Communications:** View chat logs and WhatsApp messages

## API Endpoints

### Public Endpoints
- `GET /` - Main chatbot interface
- `POST /api/chat` - Chat API
- `GET /api/faqs` - Get all FAQs
- `GET /api/fees` - Fee information
- `GET /api/admissions` - Admission requirements
- `GET /api/school-info` - School contact details

### Authentication Required
- `GET /dashboard` - User dashboard
- `GET /payments` - Payment portal
- `GET /notifications` - User notifications
- `GET /voice` - Voice assistant

### Admin Only
- `GET /admin` - Admin dashboard
- `GET /admin/students` - Student management
- `GET /admin/staff` - Staff management
- `GET /admin/payments` - Payment reconciliation
- `GET /admin/whatsapp` - WhatsApp inbox

### Webhooks
- `POST /whatsapp/webhook` - WhatsApp message receiver
- `POST /api/mobile-money/callback` - Payment confirmation callback

## Deployment

The application is configured for deployment on:
- **Heroku** (using `Procfile`)
- **Render** (using `render.yaml`)
- **Local** (using `run.bat` or `run.sh`)

Set environment variables in your deployment platform's dashboard.


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
