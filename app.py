"""
St. Jonathan High School Chatbot
Parent-School Communication System
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None

try:
    import openai
except ImportError:
    openai = None

try:
    from twilio.rest import Client
except ImportError:
    Client = None

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

AI_ENABLED = bool(openai and OPENAI_API_KEY)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'auth_login'

if Client and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

db = SQLAlchemy(app)

# Conversation state helpers
CLASS_KEYWORDS = {
    's1': 'S.1',
    's.1': 'S.1',
    'senior 1': 'S.1',
    'senior one': 'S.1',
    's2': 'S.2',
    's.2': 'S.2',
    'senior 2': 'S.2',
    'senior two': 'S.2',
    's3': 'S.3',
    's.3': 'S.3',
    'senior 3': 'S.3',
    'senior three': 'S.3',
    's4': 'S.4',
    's.4': 'S.4',
    'senior 4': 'S.4',
    'senior four': 'S.4',
    'o-level': 'O-Level',
    'olevel': 'O-Level',
    'o level': 'O-Level',
}


def get_pending_action():
    return session.get('pending_action')


def set_pending_action(action):
    session['pending_action'] = action
    session.modified = True


def clear_pending_action():
    session.pop('pending_action', None)
    session.modified = True


def get_dialog_context():
    return session.get('dialog_context', {})


def update_dialog_context(key, value):
    context = session.get('dialog_context', {})
    context[key] = value
    session['dialog_context'] = context
    session.modified = True


def clear_dialog_context():
    session.pop('dialog_context', None)
    session.modified = True


def get_context_summary():
    context = get_dialog_context()
    if not context:
        return ''

    parts = []
    if context.get('topic'):
        parts.append(f"Topic: {context['topic']}")
    if context.get('level'):
        parts.append(f"Student level: {context['level']}")
    if context.get('last_intent'):
        parts.append(f"Last intent: {context['last_intent']}")

    if parts:
        return 'Session context: ' + '; '.join(parts) + '.'
    return ''


def parse_class_level(text):
    text_lower = text.lower()
    for token, level in CLASS_KEYWORDS.items():
        if token in text_lower:
            return level
    return None


def get_fee_text_for_level(level):
    if not level:
        return None

    fee_map = {
        'S.1': 'UGX 2,500,000 - 3,000,000 per term',
        'S.2': 'UGX 2,500,000 - 3,000,000 per term',
        'S.3': 'UGX 2,800,000 - 3,200,000 per term',
        'S.4': 'UGX 2,800,000 - 3,200,000 per term',
        'O-Level': 'UGX 3,000,000 - 3,500,000 per term',
    }
    description = fee_map.get(level)
    if description:
        return (
            f"💰 The approximate fee for {level} at {SCHOOL_INFO['name']} is {description}. "
            "These figures typically include tuition, accommodation, meals, and basic amenities. "
            "Additional charges may apply for uniforms, books, and activities. "
            "For exact current rates, please contact the Accounts Department."
        )
    return None


def get_admission_text_for_level(level):
    if not level:
        return None

    return (
        f"📝 Admission requirements for {level} at {SCHOOL_INFO['name']}: "
        "Complete the application form, provide a copy of the Primary Leaving Certificate or PSLC, "
        "submit a school report, birth certificate or ID, and ensure parent/guardian sign-off. "
        "Bring medical information and any required fees to the admissions office. "
        "For help with the application process, contact admissions at " + SCHOOL_INFO['phone'] + "."
    )

# School Information
SCHOOL_INFO = {
    "name": "St. Jonathan High School",
    "address": "P.O. Box 12352, Kampala",
    "location": "Jinja-Kampala Highway, next to Mbalala Trading Centre",
    "phone": "+256701416197",
    "email": "info@stjJonathan.ug",
    "established": 2017,
    "principal": "Dr. MAIKI PROTUS"
}

# Load FAQs
def load_faqs():
    # Try multiple paths
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'data', 'faqs.json'),
        os.path.join(os.path.dirname(__file__), 'faqs.json'),
        '/home/maikiprotus81/school_chatbot/data/faqs.json',
        '/home/maikiprotus81/school_chatbot/faqs.json',
    ]
    
    for faq_path in possible_paths:
        if os.path.exists(faq_path):
            try:
                with open(faq_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {faq_path}: {e}")
    
    print("Warning: faqs.json not found at any location")
    return []


def save_faqs(faqs):
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'data', 'faqs.json'),
        os.path.join(os.path.dirname(__file__), 'faqs.json'),
        '/home/maikiprotus81/school_chatbot/data/faqs.json',
        '/home/maikiprotus81/school_chatbot/faqs.json',
    ]
    faq_path = next((path for path in possible_paths if os.path.exists(path)), None)
    if faq_path is None:
        faq_path = os.path.join(os.path.dirname(__file__), 'data', 'faqs.json')
    with open(faq_path, 'w', encoding='utf-8') as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)
    return faq_path


def load_chat_logs(limit=200):
    log_file = os.path.join(os.path.dirname(__file__), 'logs', 'chat_logs.json')
    if not os.path.exists(log_file):
        return []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            return logs[-limit:]
    except Exception as e:
        print(f"Error loading chat logs: {e}")
        return []

FAQS = load_faqs()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='parent')
    phone = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    children = db.relationship('Student', backref='parent', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    admission_year = db.Column(db.String(20), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    exam_results = db.relationship('Exam', backref='student', lazy=True)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.String(200), nullable=True)


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=True)
    term = db.Column(db.String(50), nullable=True)
    year = db.Column(db.String(20), nullable=True)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    method = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recipient_role = db.Column(db.String(30), nullable=False, default='parent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent = db.Column(db.Boolean, default=False)


class WhatsAppMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_number = db.Column(db.String(50), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # 'inbound' or 'outbound'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    responded = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin_user = User(
            name='School Admin',
            email='admin@stjonathan.ug',
            role='admin',
            phone=SCHOOL_INFO['phone']
        )
        admin_user.set_password(ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()

# OpenAI intelligence support

def call_openai_model(messages, max_tokens=350, temperature=0.2):
    """Call OpenAI chat completion and return text result."""
    if not AI_ENABLED:
        raise RuntimeError("OpenAI is not configured.")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message["content"].strip()


def parse_openai_json(response_text):
    """Try to parse JSON from an OpenAI response."""
    try:
        start = response_text.index("{")
        end = response_text.rindex("}") + 1
        return json.loads(response_text[start:end])
    except (ValueError, json.JSONDecodeError):
        return None


def get_faq_prompt_context():
    """Create a short text summary of the FAQ list for the AI prompt."""
    faq_context = []
    for faq in FAQS:
        faq_context.append(
            f"- Q: {faq.get('question', '')}\n  A: {faq.get('answer', '')}\n  Category: {faq.get('category', 'General')}"
        )
    return "\n".join(faq_context)


def ai_generate_response(user_query, history=None):
    """Use OpenAI to interpret the user query and generate a response."""
    if not AI_ENABLED:
        return None

    system_message = (
        "You are a helpful school assistant for St. Jonathan High School. "
        "Use the school information and FAQ data to answer parents' questions clearly and politely. "
        "If the query is about school contact details, admissions, fees, facilities, academics, or school policies, "
        "use the FAQ answer or school contact information. If you are not sure, tell the user to contact the school office."
    )

    faq_context = get_faq_prompt_context()
    user_message = f"""School name: {SCHOOL_INFO['name']}
Address: {SCHOOL_INFO['address']}
Phone: {SCHOOL_INFO['phone']}
Email: {SCHOOL_INFO['email']}
Principal: {SCHOOL_INFO['principal']}

FAQ data:
{faq_context}

User question: {user_query}

Respond with JSON exactly in this format:
{{"intent":"<intent>","answer":"<response>","category":"<category>","type":"faq|school_info|greeting|unknown","confidence":0.0}}
Keep the answer concise but helpful. Use the FAQ answer when the question matches."""

    context_summary = get_context_summary()
    messages = [
        {"role": "system", "content": system_message}
    ]
    if context_summary:
        messages.append({"role": "system", "content": context_summary})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        raw_response = call_openai_model(messages)
        parsed = parse_openai_json(raw_response)
        if parsed and parsed.get("answer"):
            return {
                "response": parsed["answer"],
                "type": parsed.get("type", "ai"),
                "category": parsed.get("category", "General"),
                "confidence": parsed.get("confidence", 0.0),
            }

        return {"response": raw_response, "type": "ai", "category": "General", "confidence": 0.0}
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

# Deployment settings
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')
PORT = int(os.environ.get('PORT', 5000))

# Utility Functions
def similar(a, b):
    """Calculate similarity between two strings (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_faq_match(user_query):
    """Find the best matching FAQ for user query"""
    best_match = None
    best_score = 0.3  # Minimum similarity threshold
    
    query_lower = user_query.lower()
    
    # Search through FAQs
    for faq in FAQS:
        question = faq.get('question', '').lower()
        keywords = [k.lower() for k in faq.get('keywords', [])]
        
        # Check question similarity
        score = similar(user_query, question)
        
        # Check keyword matches
        for keyword in keywords:
            keyword_score = similar(user_query, keyword)
            if keyword_score > score:
                score = keyword_score
        
        if score > best_score:
            best_score = score
            best_match = faq
    
    return best_match, best_score

def get_conversation_history():
    """Load recent conversation history from the user session."""
    history = session.get('conversation_history', [])
    return history[-20:]


def update_conversation_history(role, content):
    """Append a new conversation message to the user session history."""
    history = session.get('conversation_history', [])
    history.append({"role": role, "content": content})
    session['conversation_history'] = history[-40:]
    session.modified = True


def handle_pending_action(user_query):
    pending = get_pending_action()
    if not pending:
        return None

    if pending == 'awaiting_fee_class':
        level = parse_class_level(user_query)
        if level:
            clear_pending_action()
            update_dialog_context('topic', 'fees')
            update_dialog_context('level', level)
            update_dialog_context('last_intent', 'fees')
            fee_text = get_fee_text_for_level(level)
            if fee_text:
                return {
                    'response': fee_text,
                    'type': 'faq',
                    'category': 'Fees & Payments',
                    'confidence': 0.95,
                }
        return {
            'response': 'Please tell me the class for fee details, for example S.1, S.2, S.3, S.4, or O-Level.',
            'type': 'unknown',
            'category': 'Fees & Payments',
            'confidence': 0.0,
        }

    if pending == 'awaiting_admission_level':
        level = parse_class_level(user_query)
        if level:
            clear_pending_action()
            update_dialog_context('topic', 'admissions')
            update_dialog_context('level', level)
            update_dialog_context('last_intent', 'admissions')
            admission_text = get_admission_text_for_level(level)
            if admission_text:
                return {
                    'response': admission_text,
                    'type': 'faq',
                    'category': 'Admissions',
                    'confidence': 0.95,
                }
        return {
            'response': 'Which class is the admission for? Please tell me S.1, S.2, S.3, S.4, or O-Level.',
            'type': 'unknown',
            'category': 'Admissions',
            'confidence': 0.0,
        }

    return None


def generate_response(user_query, history=None):
    """Generate chatbot response based on user query"""
    pending_response = handle_pending_action(user_query)
    if pending_response:
        return pending_response

    context = get_dialog_context()
    level = parse_class_level(user_query)
    if context.get('topic') == 'fees' and level:
        fee_text = get_fee_text_for_level(level)
        if fee_text:
            update_dialog_context('level', level)
            update_dialog_context('last_intent', 'fees')
            return {
                'response': fee_text,
                'type': 'faq',
                'category': 'Fees & Payments',
                'confidence': 0.95,
            }

    if context.get('topic') == 'admissions' and level:
        admission_text = get_admission_text_for_level(level)
        if admission_text:
            update_dialog_context('level', level)
            update_dialog_context('last_intent', 'admissions')
            return {
                'response': admission_text,
                'type': 'faq',
                'category': 'Admissions',
                'confidence': 0.95,
            }

    # AI-powered response first, if available
    ai_response = ai_generate_response(user_query, history=history)
    if ai_response:
        return ai_response

    # Check for greetings
    greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in user_query.lower() for greeting in greetings):
        return {
            "response": f"Hello! Welcome to {SCHOOL_INFO['name']}. I'm your school assistant. How can I help you today? Feel free to ask me about admissions, fees, academics, or any other school-related information.",
            "type": "greeting"
        }

    # Check for fee questions and request class details if needed
    fee_keywords = ['fee', 'fees', 'cost', 'charge', 'tuition', 'payment']
    if any(keyword in user_query.lower() for keyword in fee_keywords):
        level = parse_class_level(user_query)
        if level:
            fee_text = get_fee_text_for_level(level)
            if fee_text:
                clear_pending_action()
                update_dialog_context('topic', 'fees')
                update_dialog_context('level', level)
                update_dialog_context('last_intent', 'fees')
                return {
                    'response': fee_text,
                    'type': 'faq',
                    'category': 'Fees & Payments',
                    'confidence': 0.95,
                }
        set_pending_action('awaiting_fee_class')
        update_dialog_context('topic', 'fees')
        update_dialog_context('last_intent', 'fees')
        return {
            'response': 'Sure — to give you exact fee guidance, please tell me which class you are asking about: S.1, S.2, S.3, S.4, or O-Level.',
            'type': 'unknown',
            'category': 'Fees & Payments',
            'confidence': 0.0,
        }

    # Check for admission questions and request class details if needed
    admission_keywords = ['admission', 'apply', 'enroll', 'registration', 'join school']
    if any(keyword in user_query.lower() for keyword in admission_keywords):
        level = parse_class_level(user_query)
        if level:
            admission_text = get_admission_text_for_level(level)
            if admission_text:
                clear_pending_action()
                update_dialog_context('topic', 'admissions')
                update_dialog_context('level', level)
                update_dialog_context('last_intent', 'admissions')
                return {
                    'response': admission_text,
                    'type': 'faq',
                    'category': 'Admissions',
                    'confidence': 0.95,
                }
        set_pending_action('awaiting_admission_level')
        update_dialog_context('topic', 'admissions')
        update_dialog_context('last_intent', 'admissions')
        return {
            'response': 'I can help with admission requirements. Which class is this application for: S.1, S.2, S.3, S.4, or O-Level?',
            'type': 'unknown',
            'category': 'Admissions',
            'confidence': 0.0,
        }

    # Check for school info requests
    contact_keywords = ['contact', 'phone', 'address', 'location', 'telephone', 'email']
    if any(keyword in user_query.lower() for keyword in contact_keywords):
        school_details = f"""
        📍 **School Information:**
        • Name: {SCHOOL_INFO['name']}
        • Address: {SCHOOL_INFO['address']}
        • Location: {SCHOOL_INFO['location']}
        • Phone: {SCHOOL_INFO['phone']}
        • Email: {SCHOOL_INFO['email']}
        • Principal: {SCHOOL_INFO['principal']}
        """
        return {
            "response": school_details,
            "type": "school_info"
        }

    # Search FAQs
    best_faq, score = find_best_faq_match(user_query)

    if best_faq and score > 0.4:
        return {
            "response": best_faq['answer'],
            "category": best_faq.get('category', 'General'),
            "type": "faq",
            "confidence": score
        }

    # Default response
    return {
        "response": "I'm not sure about that. Could you please rephrase your question or contact the school administration directly at " + SCHOOL_INFO['phone'],
        "type": "unknown"
    }

@app.route('/')
def index():
    """Render main chatbot page"""
    return render_template('index.html', school_info=SCHOOL_INFO)

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        history = get_conversation_history()
        
        # Generate response with context history
        bot_response = generate_response(user_message, history=history)
        
        # Store conversation history in session
        update_conversation_history('user', user_message)
        update_conversation_history('assistant', bot_response.get('response', ''))
        
        # Log conversation
        log_conversation(user_message, bot_response)
        
        return jsonify({
            "success": True,
            "message": bot_response['response'],
            "type": bot_response.get('type', 'response'),
            "category": bot_response.get('category', 'N/A')
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs"""
    return jsonify(FAQS)


@app.route('/api/fees', methods=['GET'])
def get_fees():
    """Get structured fee information."""
    return jsonify({
        "fees": {
            "S.1": "UGX 2,500,000 - 3,000,000 per term",
            "S.2": "UGX 2,500,000 - 3,000,000 per term",
            "S.3": "UGX 2,800,000 - 3,200,000 per term",
            "S.4": "UGX 2,800,000 - 3,200,000 per term",
            "O-Level": "UGX 3,000,000 - 3,500,000 per term"
        },
        "note": "Fees vary by class and academic year. Contact accounts for exact current fees."
    })


@app.route('/api/admissions', methods=['GET'])
def get_admissions():
    """Get admissions guidance."""
    return jsonify({
        "admissions": {
            "overview": "St. Jonathan High School accepts applications for S.1 through O-Level. Applicants must submit school reports, birth certificate or ID, and parent/guardian sign-off.",
            "required_documents": [
                "Completed application form",
                "Primary Leaving Certificate or PSLC",
                "Previous school report",
                "Birth certificate or national ID",
                "Parent/guardian consent",
                "Medical form"
            ],
            "contact": {
                "phone": SCHOOL_INFO['phone'],
                "email": SCHOOL_INFO['email']
            },
            "form_download": "/static/admission_form.txt"
        }
    })


@app.route('/admissions')
def admissions_page():
    """Render the admissions information page."""
    return render_template('admissions.html', school_info=SCHOOL_INFO)


@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        error = 'Invalid email or password.'

    return render_template('auth_login.html', error=error)


@app.route('/auth/register', methods=['GET', 'POST'])
def auth_register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'parent')
        phone = request.form.get('phone', '').strip()
        child_name = request.form.get('child_name', '').strip()
        child_level = request.form.get('child_level', '').strip()

        if not name or not email or not password:
            error = 'Please fill in all required fields.'
        elif User.query.filter_by(email=email).first():
            error = 'Email is already registered.'
        else:
            user = User(name=name, email=email, role=role, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            if role == 'parent' and child_name and child_level:
                student = Student(name=child_name, class_level=child_level, parent_id=user.id)
                db.session.add(student)
                db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('auth_register.html', error=error)


@app.route('/auth/logout')
def auth_logout():
    logout_user()
    return redirect(url_for('auth_login'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        student_count = Student.query.count()
        staff_count = Staff.query.count()
        payment_count = Payment.query.count()
        return render_template('dashboard.html', role='admin', student_count=student_count, staff_count=staff_count, payment_count=payment_count)

    child_students = []
    student = None
    if current_user.role == 'parent':
        child_students = Student.query.filter_by(parent_id=current_user.id).all()
    elif current_user.role == 'student':
        student = Student.query.filter_by(name=current_user.name).first()

    notices = Notification.query.filter((Notification.recipient_role == current_user.role) | (Notification.recipient_role == 'all')).order_by(Notification.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', role=current_user.role, child_students=child_students, student=student, notices=notices)


@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    message = None
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        method = request.form.get('method', 'Mobile Money')
        payment = Payment(user_id=current_user.id, amount=amount, method=method, reference=f"TXN{int(datetime.utcnow().timestamp())}", status='pending')
        db.session.add(payment)
        db.session.commit()
        message = 'Payment request created. Use the mobile money instructions below to complete the payment.'
    return render_template('payments.html', payments=payments, message=message)


@app.route('/notifications')
@login_required
def notifications():
    notices = Notification.query.filter((Notification.recipient_role == current_user.role) | (Notification.recipient_role == 'all')).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notices=notices)


@app.route('/voice', methods=['GET', 'POST'])
def voice_page():
    status_message = None
    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            history = get_conversation_history()
            bot_response = generate_response(user_message, history=history)
            update_conversation_history('user', user_message)
            update_conversation_history('assistant', bot_response.get('response', ''))
            log_conversation(user_message, bot_response)
            status_message = bot_response.get('response')
    return render_template('voice.html', status_message=status_message)


@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_message = request.values.get('Body', '')
    from_number = request.values.get('From', '')
    
    # Save incoming message
    if incoming_message.strip():
        whatsapp_msg = WhatsAppMessage(
            from_number=from_number,
            message_body=incoming_message,
            direction='inbound'
        )
        db.session.add(whatsapp_msg)
        db.session.commit()

    response_text = 'Thank you for contacting St. Jonathan High School. We will reply shortly.'

    if incoming_message.lower().strip():
        response_text = 'Hi! Your message has been received. Please visit our chatbot at / or call the school for quick help.'

    if twilio_client and TWILIO_WHATSAPP_NUMBER:
        try:
            twilio_client.messages.create(
                body=response_text,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=from_number
            )
            # Save outbound message
            outbound_msg = WhatsAppMessage(
                from_number=from_number,
                message_body=response_text,
                direction='outbound'
            )
            db.session.add(outbound_msg)
            db.session.commit()
        except Exception as e:
            print(f"Twilio error: {e}")

    return response_text


@app.route('/api/whatsapp/send', methods=['POST'])
@login_required
def api_whatsapp_send():
    if current_user.role != 'admin' and current_user.role != 'staff':
        return jsonify({'error': 'Unauthorized'}), 403
    to = request.json.get('to')
    message = request.json.get('message')
    if not to or not message:
        return jsonify({'error': 'Missing fields'}), 400

    if not twilio_client or not TWILIO_WHATSAPP_NUMBER:
        return jsonify({'error': 'WhatsApp not configured'}), 500

    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to
        )
        # Save outbound message
        outbound_msg = WhatsAppMessage(
            from_number=to,
            message_body=message,
            direction='outbound'
        )
        db.session.add(outbound_msg)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if session.get('admin_authenticated'):
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid password. Please try again.'

    return render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for managing FAQs"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', faqs=FAQS)


@app.route('/admin/faqs', methods=['POST'])
def admin_add_faq():
    """Add a new FAQ item from admin dashboard"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    category = request.form.get('category', '').strip() or 'General'
    keywords = request.form.get('keywords', '').strip().split(',')
    keywords = [k.strip() for k in keywords if k.strip()]

    if question and answer:
        new_id = max((faq.get('id', 0) for faq in FAQS), default=0) + 1
        new_faq = {
            'id': new_id,
            'question': question,
            'answer': answer,
            'category': category,
            'keywords': keywords,
        }
        FAQS.append(new_faq)
        save_faqs(FAQS)

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/faqs/delete/<int:faq_id>', methods=['POST'])
def admin_delete_faq(faq_id):
    """Delete an FAQ item by ID"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    global FAQS
    FAQS = [faq for faq in FAQS if faq.get('id') != faq_id]
    save_faqs(FAQS)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logs')
def admin_logs():
    """Admin chat log viewer"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    logs = load_chat_logs(limit=200)
    return render_template('admin_logs.html', logs=logs)


@app.route('/admin/logs/clear', methods=['POST'])
def admin_clear_logs():
    """Clear saved chat logs"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'chat_logs.json')
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    return redirect(url_for('admin_logs'))


@app.route('/admin/students')
def admin_students():
    """Admin student management page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    students = Student.query.all()
    return render_template('admin_students.html', students=students)


@app.route('/admin/students/add', methods=['POST'])
def admin_add_student():
    """Add a new student"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    name = request.form.get('name', '').strip()
    class_level = request.form.get('class_level', '').strip()
    admission_year = request.form.get('admission_year', '').strip()
    parent_id = request.form.get('parent_id')
    if parent_id:
        parent_id = int(parent_id)
    else:
        parent_id = None
    if name and class_level:
        student = Student(name=name, class_level=class_level, admission_year=admission_year, parent_id=parent_id)
        db.session.add(student)
        db.session.commit()
    return redirect(url_for('admin_students'))


@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
def admin_delete_student(student_id):
    """Delete a student"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('admin_students'))


@app.route('/admin/staff')
def admin_staff():
    """Admin staff management page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    staff = Staff.query.all()
    return render_template('admin_staff.html', staff=staff)


@app.route('/admin/staff/add', methods=['POST'])
def admin_add_staff():
    """Add a new staff member"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', '').strip()
    phone = request.form.get('phone', '').strip()
    if name and email and role:
        staff = Staff(name=name, email=email, role=role, phone=phone)
        db.session.add(staff)
        db.session.commit()
    return redirect(url_for('admin_staff'))


@app.route('/admin/staff/delete/<int:staff_id>', methods=['POST'])
def admin_delete_staff(staff_id):
    """Delete a staff member"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    staff = Staff.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    return redirect(url_for('admin_staff'))


@app.route('/admin/notifications')
def admin_notifications():
    """Admin notification management page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('admin_notifications.html', notifications=notifications)


@app.route('/admin/notifications/add', methods=['POST'])
def admin_add_notification():
    """Add a new notification"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    title = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    recipient_role = request.form.get('recipient_role', 'all')
    if title and message:
        notification = Notification(title=title, message=message, recipient_role=recipient_role)
        db.session.add(notification)
        db.session.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/admin/notifications/delete/<int:notification_id>', methods=['POST'])
def admin_delete_notification(notification_id):
    """Delete a notification"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/admin/whatsapp')
def admin_whatsapp():
    """Admin WhatsApp inbox page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    messages = WhatsAppMessage.query.order_by(WhatsAppMessage.timestamp.desc()).limit(50).all()
    return render_template('admin_whatsapp.html', messages=messages)


@app.route('/admin/payments')
def admin_payments():
    """Admin payment reconciliation page"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    payments = Payment.query.options(db.joinedload(Payment.user)).order_by(Payment.created_at.desc()).all()
    pending_count = Payment.query.filter_by(status='pending').count()
    confirmed_count = Payment.query.filter_by(status='confirmed').count()
    rejected_count = Payment.query.filter_by(status='rejected').count()
    total_confirmed = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'confirmed').scalar() or 0
    return render_template('admin_payments.html', payments=payments, pending_count=pending_count, confirmed_count=confirmed_count, rejected_count=rejected_count, total_confirmed=total_confirmed)


@app.route('/admin/payments/confirm/<int:payment_id>', methods=['POST'])
def admin_confirm_payment(payment_id):
    """Confirm a payment"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'confirmed'
    db.session.commit()
    return redirect(url_for('admin_payments'))


@app.route('/admin/payments/reject/<int:payment_id>', methods=['POST'])
def admin_reject_payment(payment_id):
    """Reject a payment"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'rejected'
    db.session.commit()
    return redirect(url_for('admin_payments'))


@app.route('/api/mobile-money/callback', methods=['POST'])
def mobile_money_callback():
    """Simulate mobile money payment callback"""
    data = request.json
    reference = data.get('reference')
    status = data.get('status')  # 'success' or 'failed'
    
    if reference and status == 'success':
        payment = Payment.query.filter_by(reference=reference).first()
        if payment and payment.status == 'pending':
            payment.status = 'confirmed'
            db.session.commit()
            return jsonify({'status': 'ok'}), 200
    
    return jsonify({'status': 'error'}), 400


@app.route('/staff/attendance')
@login_required
def staff_attendance():
    if current_user.role != 'staff' and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    students = Student.query.all()
    attendances = Attendance.query.options(db.joinedload(Attendance.student)).order_by(Attendance.date.desc()).limit(50).all()
    return render_template('staff_attendance.html', students=students, attendances=attendances)


@app.route('/staff/attendance/add', methods=['POST'])
@login_required
def staff_add_attendance():
    if current_user.role != 'staff' and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    student_id = request.form.get('student_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    remarks = request.form.get('remarks')
    
    if student_id and date_str and status:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        attendance = Attendance(student_id=int(student_id), date=date, status=status, remarks=remarks)
        db.session.add(attendance)
        db.session.commit()
    return redirect(url_for('staff_attendance'))


@app.route('/staff/exams')
@login_required
def staff_exams():
    if current_user.role != 'staff' and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    students = Student.query.all()
    exams = Exam.query.options(db.joinedload(Exam.student)).order_by(Exam.year.desc(), Exam.term.desc()).limit(50).all()
    return render_template('staff_exams.html', students=students, exams=exams)


@app.route('/staff/exams/add', methods=['POST'])
@login_required
def staff_add_exam():
    if current_user.role != 'staff' and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    student_id = request.form.get('student_id')
    subject = request.form.get('subject')
    score = request.form.get('score')
    grade = request.form.get('grade')
    term = request.form.get('term')
    year = request.form.get('year')
    
    if student_id and subject and score:
        exam = Exam(student_id=int(student_id), subject=subject, score=float(score), grade=grade, term=term, year=year)
        db.session.add(exam)
        db.session.commit()
    return redirect(url_for('staff_exams'))


@app.route('/api/school-info', methods=['GET'])
def get_school_info():
    """Get school information"""
    return jsonify(SCHOOL_INFO)

def log_conversation(user_msg, bot_response):
    """Log conversation to file for admin review"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'chat_logs.json')
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_message": user_msg,
        "bot_response_type": bot_response.get('type', 'unknown'),
        "bot_response": bot_response['response']
    }
    
    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    
    logs.append(log_entry)
    
    # Keep only recent 1000 entries
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
