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
from datetime import date, datetime
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
    try:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    except AttributeError:
        openai_client = None
else:
    openai_client = None

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
            "For exact current rates, please contact the Accounts Department. "
            "Payments can be made by MTN Mobile Money or Airtel Money Uganda. "
            "Create a payment request in the parent portal to receive a payment reference number, "
            "then pay using mobile money and include that reference in the payment reason/reference field. "
            "For MTN, dial *165#, choose Payments, select School Fees or Pay Bill, enter the school payment details, amount, reference number, and confirm with your PIN. "
            "For Airtel, dial *185#, choose Payments, select School Fees or Pay Bill, enter the school payment details, amount, reference number, and confirm with your PIN."
        )
    return None


def get_admission_text_for_level(level):
    if not level:
        return None

    return (
        f"📝 Admission requirements for {level} at {SCHOOL_INFO['name']}: "
        "Complete the application form, provide a copy of the Primary Leaving Certificate or PSLC, "
        "submit a school report, birth certificate or ID, and ensure parent/guardian sign-off. "
        "Bring medical information and admission fee payment proof to the admissions office. "
        "For admission fee payment, create a payment request in the parent portal to get a reference number. "
        "Use MTN Mobile Money by dialing *165# or Airtel Money Uganda by dialing *185#, then enter the reference number during payment. "
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


class StudentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref='comments', lazy=True)
    teacher = db.relationship('User', backref='student_comments', lazy=True)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    method = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdmissionApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(120), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(30), nullable=True)
    previous_school = db.Column(db.String(150), nullable=True)
    parent_name = db.Column(db.String(120), nullable=False)
    parent_phone = db.Column(db.String(50), nullable=False)
    parent_email = db.Column(db.String(150), nullable=True)
    home_address = db.Column(db.Text, nullable=True)
    emergency_name = db.Column(db.String(120), nullable=True)
    emergency_phone = db.Column(db.String(50), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    admission_fee_amount = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(100), nullable=True)
    payment_reference = db.Column(db.String(150), nullable=True)
    transaction_id = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default='submitted')
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


class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_level = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=True)
    room = db.Column(db.String(50), nullable=True)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_level = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ExamSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_level = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    venue = db.Column(db.String(100), nullable=True)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')  # urgent, important, normal
    target_class = db.Column(db.String(50), nullable=True)  # All or specific class
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # List of options
    correct_answer = db.Column(db.Integer, nullable=False)  # Index of correct option
    explanation = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='general')
    points = db.Column(db.Integer, default=10)


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    building = db.Column(db.String(100), nullable=True)
    floor = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=False)  # classroom, lab, office, dorm, cafeteria, etc.


class CounselorContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    available_days = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.Text, nullable=True)


class LibraryBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=True)
    category = db.Column(db.String(80), nullable=True)
    class_level = db.Column(db.String(50), nullable=True)
    copies_available = db.Column(db.Integer, default=1)
    shelf_location = db.Column(db.String(80), nullable=True)


class LabItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # chemical, apparatus, equipment
    quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    safety_notes = db.Column(db.Text, nullable=True)
    reorder_level = db.Column(db.Float, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class LabExperiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    objective = db.Column(db.Text, nullable=False)
    materials = db.Column(db.Text, nullable=False)
    procedure = db.Column(db.Text, nullable=False)
    safety_precautions = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=True)


class LabSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('lab_experiment.id'), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    laboratory = db.Column(db.String(80), default='Science Lab')
    technician = db.Column(db.String(120), nullable=True)
    experiment = db.relationship('LabExperiment', backref='schedules', lazy=True)


class LabReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('lab_experiment.id'), nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    class_level = db.Column(db.String(50), nullable=False)
    observations = db.Column(db.Text, nullable=False)
    conclusion = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    experiment = db.relationship('LabExperiment', backref='reports', lazy=True)


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
    if CounselorContact.query.count() == 0:
        db.session.add_all([
            CounselorContact(
                name='Ms. Grace Nakanjako',
                role='School Counselor',
                phone=SCHOOL_INFO['phone'],
                email='counselor@stjonathan.ug',
                available_days='Monday to Friday, 9:00 AM - 4:00 PM',
                specialization='Guidance, wellbeing, study support, and student safety'
            ),
            CounselorContact(
                name='Mr. Peter Okello',
                role='Deputy Counselor',
                phone=SCHOOL_INFO['phone'],
                email='support@stjonathan.ug',
                available_days='Tuesday and Thursday, 10:00 AM - 3:00 PM',
                specialization='Peer relations, discipline support, and family follow-up'
            ),
        ])
        db.session.commit()
    if LibraryBook.query.count() == 0:
        db.session.add_all([
            LibraryBook(title='New Secondary Mathematics', author='MK Publishers', category='Mathematics', class_level='S.1 - S.4', copies_available=6, shelf_location='Math Shelf A'),
            LibraryBook(title='Integrated Science for Uganda', author='Longhorn', category='Science', class_level='S.1 - S.4', copies_available=4, shelf_location='Science Shelf B'),
            LibraryBook(title='English Grammar in Use', author='Raymond Murphy', category='English', class_level='O-Level', copies_available=3, shelf_location='English Shelf C'),
            LibraryBook(title='African History Revision Guide', author='Fountain Publishers', category='History', class_level='O-Level', copies_available=5, shelf_location='Humanities Shelf D'),
            LibraryBook(title='Computer Studies Made Simple', author='KLB', category='Computer Studies', class_level='S.1 - S.4', copies_available=2, shelf_location='ICT Shelf E'),
        ])
        db.session.commit()
    if TimetableEntry.query.count() == 0:
        db.session.add_all([
            TimetableEntry(class_level='S.1', day_of_week='Monday', period=1, subject='Mathematics', teacher='Mr. Kato', room='Room 1', start_time='08:00', end_time='08:40'),
            TimetableEntry(class_level='S.1', day_of_week='Monday', period=2, subject='English', teacher='Ms. Namata', room='Room 1', start_time='08:40', end_time='09:20'),
            TimetableEntry(class_level='S.1', day_of_week='Tuesday', period=1, subject='Integrated Science', teacher='Mr. Okello', room='Lab 1', start_time='08:00', end_time='08:40'),
            TimetableEntry(class_level='S.2', day_of_week='Monday', period=1, subject='Biology', teacher='Ms. Auma', room='Lab 2', start_time='08:00', end_time='08:40'),
            TimetableEntry(class_level='S.3', day_of_week='Wednesday', period=1, subject='Chemistry', teacher='Mr. Ssekandi', room='Lab 1', start_time='08:00', end_time='08:40'),
            TimetableEntry(class_level='S.4', day_of_week='Thursday', period=1, subject='Physics', teacher='Ms. Atim', room='Lab 2', start_time='08:00', end_time='08:40'),
        ])
        db.session.commit()
    if Assignment.query.count() == 0:
        db.session.add_all([
            Assignment(class_level='S.1', subject='Mathematics', title='Fractions practice', description='Complete exercises 1 to 10 in your notebook.', due_date=date.today()),
            Assignment(class_level='S.2', subject='English', title='Composition writing', description='Write one page about school life.', due_date=date.today()),
            Assignment(class_level='S.3', subject='Biology', title='Cell structure revision', description='Draw and label a plant cell.', due_date=date.today()),
        ])
        db.session.commit()
    if ExamSchedule.query.count() == 0:
        db.session.add_all([
            ExamSchedule(class_level='S.1', subject='Mathematics', exam_date=date.today(), start_time='09:00', end_time='10:30', venue='Main Hall'),
            ExamSchedule(class_level='S.2', subject='English', exam_date=date.today(), start_time='11:00', end_time='12:30', venue='Room 2'),
            ExamSchedule(class_level='S.3', subject='Biology', exam_date=date.today(), start_time='09:00', end_time='10:30', venue='Lab 2'),
        ])
        db.session.commit()
    if LabItem.query.count() == 0:
        db.session.add_all([
            LabItem(name='Sodium hydroxide', item_type='chemical', quantity=2.5, unit='litres', location='Chemical Store A', reorder_level=1, safety_notes='Corrosive. Wear gloves and goggles. Rinse spills with plenty of water.'),
            LabItem(name='Copper sulfate solution', item_type='chemical', quantity=1.8, unit='litres', location='Chemical Store A', reorder_level=1, safety_notes='Harmful if swallowed. Avoid skin contact and wash hands after use.'),
            LabItem(name='Test tubes', item_type='apparatus', quantity=80, unit='pieces', location='Lab Cabinet 2', reorder_level=20, safety_notes='Handle glassware carefully and report breakages immediately.'),
            LabItem(name='Bunsen burners', item_type='equipment', quantity=12, unit='pieces', location='Physics/Chemistry Lab', reorder_level=4, safety_notes='Check gas taps before and after practical lessons.'),
            LabItem(name='Microscopes', item_type='equipment', quantity=10, unit='pieces', location='Biology Lab', reorder_level=3, safety_notes='Carry with two hands and clean lenses only with lens tissue.'),
        ])
        db.session.commit()
    if LabExperiment.query.count() == 0:
        biuret = LabExperiment(
            title='Testing for Proteins Using the Biuret Test',
            subject='Biology',
            class_level='S.3',
            objective='To identify the presence of proteins in a food sample.',
            materials='Food sample solution, sodium hydroxide, copper sulfate solution, test tubes, dropper, test tube rack.',
            procedure='Place 2 cm3 of the food sample in a test tube. Add 2 cm3 of sodium hydroxide and shake gently. Add a few drops of copper sulfate solution. Observe the colour change.',
            safety_precautions='Wear goggles and gloves. Do not taste chemicals or food samples. Keep sodium hydroxide away from skin and eyes. Clean spills immediately.',
            expected_result='A violet or purple colour shows that proteins are present.'
        )
        db.session.add_all([
            biuret,
            LabExperiment(
                title='Preparing Oxygen Gas',
                subject='Chemistry',
                class_level='S.2',
                objective='To prepare oxygen gas in the laboratory and test its properties.',
                materials='Hydrogen peroxide, manganese dioxide, conical flask, delivery tube, gas jar, water trough, glowing splint.',
                procedure='Add manganese dioxide to hydrogen peroxide in a flask. Collect the gas over water in a gas jar. Insert a glowing splint into the gas jar.',
                safety_precautions='Wear eye protection. Do not point apparatus at people. Handle glassware carefully. Keep chemicals away from the mouth.',
                expected_result='A glowing splint relights in oxygen gas.'
            ),
            LabExperiment(
                title='Measuring Density of an Irregular Solid',
                subject='Physics',
                class_level='S.1',
                objective='To determine density using mass and displaced water volume.',
                materials='Irregular stone, measuring cylinder, water, beam balance, thread.',
                procedure='Measure the mass of the stone. Record the initial water volume in a measuring cylinder. Lower the stone into water and record the new volume. Calculate density as mass divided by volume displaced.',
                safety_precautions='Do not drop objects into glass cylinders. Wipe water spills to prevent slipping.',
                expected_result='Density is calculated in g/cm3 from measured mass and displaced volume.'
            ),
        ])
        db.session.commit()
    if LabSchedule.query.count() == 0:
        first_experiment = LabExperiment.query.first()
        if first_experiment:
            db.session.add(LabSchedule(
                experiment_id=first_experiment.id,
                class_level=first_experiment.class_level,
                scheduled_date=date.today(),
                start_time='10:00',
                end_time='11:20',
                laboratory='Biology Lab',
                technician='Mr. Lab Technician'
            ))
            db.session.commit()

# OpenAI intelligence support

def call_openai_model(messages, max_tokens=350, temperature=0.2):
    """Call OpenAI chat completion and return text result."""
    if not AI_ENABLED:
        raise RuntimeError("OpenAI is not configured.")
    model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    if openai_client:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    response = openai.ChatCompletion.create(
        model=model,
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


def build_lab_response(user_query):
    query_lower = user_query.lower()
    lab_keywords = [
        'laboratory', 'lab ', ' lab', 'experiment', 'practical', 'chemical',
        'apparatus', 'equipment', 'safety', 'biuret', 'protein', 'oxygen gas',
        'microscope', 'test tube'
    ]
    if not any(keyword in query_lower for keyword in lab_keywords):
        return None

    level = parse_class_level(user_query)
    subject_match = None
    for subject in ['biology', 'chemistry', 'physics', 'science']:
        if subject in query_lower:
            subject_match = subject
            break

    if any(word in query_lower for word in ['inventory', 'chemical', 'apparatus', 'equipment', 'stock', 'available']):
        items_query = LabItem.query
        for item_type in ['chemical', 'apparatus', 'equipment']:
            if item_type in query_lower:
                items_query = items_query.filter_by(item_type=item_type)
                break
        items = items_query.order_by(LabItem.item_type, LabItem.name).limit(8).all()
        if items:
            response = "**Laboratory inventory:**\n\n"
            for item in items:
                stock_note = " - low stock" if item.is_low_stock else ""
                response += f"- {item.name}: {item.quantity:g} {item.unit or ''} ({item.item_type}, {item.location or 'Lab store'}){stock_note}\n"
            return {"response": response, "type": "lab_inventory", "category": "Smart Laboratory"}

    if any(word in query_lower for word in ['schedule', 'when', 'lesson', 'booking', 'booked']):
        schedules_query = LabSchedule.query
        if level:
            schedules_query = schedules_query.filter_by(class_level=level)
        schedules = schedules_query.order_by(LabSchedule.scheduled_date, LabSchedule.start_time).limit(5).all()
        if schedules:
            response = "**Upcoming practical lessons:**\n\n"
            for schedule in schedules:
                response += (
                    f"- {schedule.class_level}: {schedule.experiment.title} on "
                    f"{schedule.scheduled_date.strftime('%Y-%m-%d')} from {schedule.start_time} to {schedule.end_time} "
                    f"in {schedule.laboratory}\n"
                )
            return {"response": response, "type": "lab_schedule", "category": "Smart Laboratory"}

    experiments_query = LabExperiment.query
    if level:
        experiments_query = experiments_query.filter_by(class_level=level)
    if subject_match and subject_match != 'science':
        experiments_query = experiments_query.filter(LabExperiment.subject.ilike(f"%{subject_match}%"))

    if 'biuret' in query_lower or 'protein' in query_lower:
        experiments_query = LabExperiment.query.filter(LabExperiment.title.ilike('%protein%'))
    elif 'oxygen' in query_lower:
        experiments_query = LabExperiment.query.filter(LabExperiment.title.ilike('%oxygen%'))
    elif 'density' in query_lower:
        experiments_query = LabExperiment.query.filter(LabExperiment.title.ilike('%density%'))

    experiments = experiments_query.order_by(LabExperiment.subject, LabExperiment.class_level).limit(3).all()
    if experiments:
        response = "**Smart laboratory guidance:**\n\n"
        for experiment in experiments:
            response += (
                f"**{experiment.title}** ({experiment.subject}, {experiment.class_level})\n"
                f"Objective: {experiment.objective}\n"
                f"Materials: {experiment.materials}\n"
                f"Procedure: {experiment.procedure}\n"
                f"Safety: {experiment.safety_precautions}\n"
            )
            if experiment.expected_result:
                response += f"Expected result: {experiment.expected_result}\n"
            response += "\n"
        return {"response": response.strip(), "type": "lab_experiment", "category": "Smart Laboratory"}

    return {
        "response": "The smart laboratory module can help with experiment procedures, chemical safety, apparatus inventory, practical schedules, and lab reports. Try asking: How do I test for proteins?",
        "type": "lab_help",
        "category": "Smart Laboratory"
    }


SUBJECT_ALIASES = {
    'math': 'Mathematics',
    'maths': 'Mathematics',
    'mathematics': 'Mathematics',
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'biology': 'Biology',
    'english': 'English',
    'ict': 'ICT',
    'computer': 'ICT',
    'computer studies': 'ICT',
}


def detect_subject(text):
    text_lower = text.lower()
    for token, subject in SUBJECT_ALIASES.items():
        if token in text_lower:
            return subject
    return None


def is_learning_request(text):
    text_lower = text.lower()
    learning_keywords = [
        'explain', 'solve', 'summarize', 'summary', 'teach me', 'what is',
        'define', 'homework', 'hint', 'answer this', 'revision', 'study material',
        'quiz me', 'give me a quiz', 'generate quiz', 'osmosis', 'photosynthesis'
    ]
    return any(keyword in text_lower for keyword in learning_keywords) or bool(detect_subject(text))


def fallback_tutor_answer(question, subject=None):
    question_lower = question.lower()
    if 'osmosis' in question_lower:
        return (
            "Osmosis is the movement of water molecules from a region of high water concentration "
            "to a region of low water concentration through a semi-permeable membrane. For example, "
            "plant root hairs absorb water from the soil by osmosis."
        )
    if 'photosynthesis' in question_lower:
        return (
            "Photosynthesis is the process by which green plants make food using sunlight, carbon dioxide, "
            "and water. Chlorophyll traps light energy, and the products are glucose and oxygen. "
            "Word equation: carbon dioxide + water -> glucose + oxygen."
        )
    if 'protein' in question_lower or 'biuret' in question_lower:
        lab_response = build_lab_response(question)
        if lab_response:
            return lab_response['response']
    if 'summarize' in question_lower or 'summary' in question_lower:
        return summarize_notes_text(question)
    if 'quiz' in question_lower:
        return generate_quiz_text(subject or 'General Science', 5)

    subject_text = subject or 'the subject'
    return (
        f"I can help with {subject_text}. Send the exact question, topic, or notes, and I will explain it step by step, "
        "give hints first, and then show a clear answer. Example: Explain osmosis for S.3 Biology."
    )


def ai_tutor_answer(question, subject=None, level=None):
    subject = subject or detect_subject(question) or 'General Studies'
    level = level or parse_class_level(question) or 'O-Level'
    if AI_ENABLED:
        try:
            return call_openai_model([
                {
                    "role": "system",
                    "content": (
                        "You are an AI tutor for St. Jonathan High School in Uganda. "
                        "Teach clearly for secondary school learners. Give step-by-step explanations, "
                        "use simple examples, and avoid doing harmful lab instructions without safety notes. "
                        "When solving homework, give hints and reasoning before the final answer."
                    )
                },
                {
                    "role": "user",
                    "content": f"Subject: {subject}\nLevel: {level}\nStudent question: {question}"
                }
            ], max_tokens=650, temperature=0.25)
        except Exception as e:
            print(f"AI tutor error: {e}")
    return fallback_tutor_answer(question, subject=subject)


def summarize_notes_text(notes):
    notes = notes.strip()
    if not notes:
        return "Paste your notes and I will summarize the key points."
    if AI_ENABLED:
        try:
            return call_openai_model([
                {"role": "system", "content": "Summarize student notes into concise revision points, key terms, and likely exam questions."},
                {"role": "user", "content": notes}
            ], max_tokens=550, temperature=0.2)
        except Exception as e:
            print(f"Notes summary error: {e}")

    sentences = re.split(r'(?<=[.!?])\s+', notes)
    summary = sentences[:4] if len(sentences) > 1 else [notes[:450]]
    return "Revision summary:\n- " + "\n- ".join(line.strip() for line in summary if line.strip())


def generate_quiz_text(subject, count=5, level='O-Level'):
    try:
        count = max(1, min(int(count), 10))
    except (TypeError, ValueError):
        count = 5
    subject = subject or 'General Science'
    if AI_ENABLED:
        try:
            return call_openai_model([
                {
                    "role": "system",
                    "content": (
                        "Generate a school revision quiz. Include numbered questions, four options for MCQ questions, "
                        "the correct answer, and a short marking guide."
                    )
                },
                {"role": "user", "content": f"Create {count} {level} questions for {subject}."}
            ], max_tokens=850, temperature=0.35)
        except Exception as e:
            print(f"Quiz generation error: {e}")

    samples = {
        'Biology': [
            ('What is osmosis?', 'Movement of water through a semi-permeable membrane from high to low water concentration.'),
            ('Which organelle carries out photosynthesis?', 'Chloroplast.'),
            ('What is the function of red blood cells?', 'Transporting oxygen.'),
        ],
        'Chemistry': [
            ('What gas relights a glowing splint?', 'Oxygen.'),
            ('What is a mixture?', 'Two or more substances physically combined.'),
            ('What colour does blue litmus turn in acid?', 'Red.'),
        ],
        'Mathematics': [
            ('Solve 2x + 5 = 13.', 'x = 4.'),
            ('Find 20% of 150.', '30.'),
            ('What is the area of a rectangle?', 'Length x width.'),
        ],
    }
    questions = samples.get(subject, samples['Biology'])
    response = f"{subject} quiz:\n\n"
    for index in range(count):
        question, answer = questions[index % len(questions)]
        response += f"{index + 1}. {question}\nAnswer: {answer}\n\n"
    return response.strip()


def build_performance_analysis(student):
    if not student:
        return "No linked student record was found yet, so I cannot analyze performance."

    marks = Exam.query.filter_by(student_id=student.id).all()
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    if not marks and not attendance:
        return f"No marks or attendance records are available yet for {student.name}."

    lines = [f"Performance analysis for {student.name} ({student.class_level}):"]
    if marks:
        subject_scores = {}
        for mark in marks:
            subject_scores.setdefault(mark.subject, []).append(mark.score)
        averages = {
            subject: sum(scores) / len(scores)
            for subject, scores in subject_scores.items()
        }
        best_subject = max(averages, key=averages.get)
        weak_subject = min(averages, key=averages.get)
        lines.append(f"- Strongest subject: {best_subject} ({averages[best_subject]:.1f} average).")
        lines.append(f"- Needs more revision: {weak_subject} ({averages[weak_subject]:.1f} average).")
        if averages[weak_subject] < 50:
            lines.append(f"- Recommendation: schedule extra practice and teacher support in {weak_subject}.")
    if attendance:
        present = sum(1 for item in attendance if item.status.lower() == 'present')
        rate = (present / len(attendance)) * 100
        lines.append(f"- Attendance rate: {rate:.1f}% based on {len(attendance)} records.")
        if rate < 85:
            lines.append("- Recommendation: improve attendance consistency because missed lessons affect performance.")
    return "\n".join(lines)


def get_current_student_record():
    if not current_user.is_authenticated:
        return None
    if current_user.role == 'student':
        return Student.query.filter_by(name=current_user.name).first()
    if current_user.role == 'parent':
        return Student.query.filter_by(parent_id=current_user.id).first()
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

    lab_response = build_lab_response(user_query)
    if lab_response:
        return lab_response

    query_lower = user_query.lower()
    if any(keyword in query_lower for keyword in ['performance', 'weak subject', 'attendance trend', 'analyze my marks', 'analyse my marks']):
        student = get_current_student_record()
        return {
            "response": build_performance_analysis(student),
            "type": "performance_analysis",
            "category": "Academic Assistant"
        }

    if any(keyword in query_lower for keyword in ['give me a quiz', 'generate quiz', 'quiz me', 'revision questions']):
        subject = detect_subject(user_query) or 'General Science'
        count_match = re.search(r'\b(\d{1,2})\b', user_query)
        count = int(count_match.group(1)) if count_match else 5
        level = parse_class_level(user_query) or context.get('level') or 'O-Level'
        return {
            "response": generate_quiz_text(subject, count=count, level=level),
            "type": "quiz_generator",
            "category": "AI Tutor"
        }

    if any(keyword in query_lower for keyword in ['summarize', 'summarise', 'summary of', 'summarize this note', 'summarise this note']):
        return {
            "response": summarize_notes_text(user_query),
            "type": "notes_summarizer",
            "category": "AI Tutor"
        }

    if is_learning_request(user_query):
        subject = detect_subject(user_query)
        level = parse_class_level(user_query) or context.get('level')
        return {
            "response": ai_tutor_answer(user_query, subject=subject, level=level),
            "type": "ai_tutor",
            "category": subject or "AI Tutor"
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
    fee_keywords = ['fee', 'fees', 'cost', 'charge', 'tuition', 'payment', 'payments', 'mobile money', 'mtn', 'airtel', 'reference']
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

    # STUDENT-CENTRIC FEATURES

    # Timetable queries
    timetable_keywords = ['timetable', 'schedule', 'next class', 'next lesson', 'what class', 'when is', 'class today', 'period']
    if any(keyword in user_query.lower() for keyword in timetable_keywords):
        level = parse_class_level(user_query) or context.get('level')
        day = None
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for d in day_names:
            if d in user_query.lower():
                day = d.capitalize()
                break

        if not day:
            today = datetime.now().weekday()
            day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            day = day_map.get(today, 'Monday')

        if 'next' in user_query.lower() or 'tomorrow' in user_query.lower():
            tomorrow = (datetime.now().weekday() + 1) % 7
            day = day_map.get(tomorrow, 'Monday')

        entries = []
        if level:
            entries = TimetableEntry.query.filter_by(class_level=level, day_of_week=day).order_by(TimetableEntry.period).all()
        else:
            entries = TimetableEntry.query.filter_by(day_of_week=day).order_by(TimetableEntry.period).limit(10).all()

        if entries:
            response = f"📅 **Your timetable for {day}:**\n\n"
            for e in entries:
                response += f"🕐 Period {e.period}: {e.subject}"
                if e.teacher:
                    response += f" (Mr/Ms {e.teacher})"
                if e.room:
                    response += f" - Room {e.room}"
                response += f" {e.start_time}-{e.end_time}\n"
            return {"response": response, "type": "timetable", "category": "Academics"}
        else:
            level_text = f" for {level}" if level else ""
            return {
                "response": f"📅 No timetable found{level_text} for {day}. Ask your class teacher or check the notice board!",
                "type": "timetable",
                "category": "Academics"
            }

    # Assignment queries
    assignment_keywords = ['assignment', 'homework', 'task', 'due', 'submit', 'work']
    if any(keyword in user_query.lower() for keyword in assignment_keywords):
        level = parse_class_level(user_query) or context.get('level')
        subject_match = None
        subjects = ['math', 'maths', 'english', 'biology', 'chemistry', 'physics', 'history', 'geography', 'kiswahili', 'computer', 'economics']
        for s in subjects:
            if s in user_query.lower():
                subject_match = s.capitalize() if s != 'maths' else 'Mathematics'
                break

        query = Assignment.query
        if level:
            query = query.filter_by(class_level=level)
        if subject_match:
            query = query.filter(Assignment.subject.ilike(f"%{subject_match}%"))

        assignments = query.order_by(Assignment.due_date).limit(5).all()

        if assignments:
            response = "📝 **Your upcoming assignments:**\n\n"
            for a in assignments:
                due_str = a.due_date.strftime('%a, %b %d')
                response += f"📌 **{a.subject}:** {a.title}\n   Due: {due_str}\n"
                if a.description:
                    response += f"   {a.description[:80]}...\n" if len(a.description or '') > 80 else f"   {a.description}\n"
                response += "\n"
            return {"response": response, "type": "assignment", "category": "Academics"}
        else:
            return {
                "response": "📝 No pending assignments found! Enjoy your free time 😄 Or check with your subject teacher.",
                "type": "assignment",
                "category": "Academics"
            }

    # Exam queries
    exam_keywords = ['exam', 'test', 'examination', 'when is exam', 'exam date', 'paper']
    if any(keyword in user_query.lower() for keyword in exam_keywords):
        level = parse_class_level(user_query) or context.get('level')
        subject_match = None
        subjects = ['math', 'maths', 'english', 'biology', 'chemistry', 'physics', 'history', 'geography', 'kiswahili', 'computer', 'economics']
        for s in subjects:
            if s in user_query.lower():
                subject_match = s.capitalize() if s != 'maths' else 'Mathematics'
                break

        query = ExamSchedule.query
        if level:
            query = query.filter_by(class_level=level)
        if subject_match:
            query = query.filter(ExamSchedule.subject.ilike(f"%{subject_match}%"))

        exams = query.order_by(ExamSchedule.exam_date).limit(5).all()

        if exams:
            response = "📚 **Upcoming Exams:**\n\n"
            for e in exams:
                date_str = e.exam_date.strftime('%a, %b %d')
                response += f"📅 **{e.subject}** - {date_str}\n   Time: {e.start_time}-{e.end_time}"
                if e.venue:
                    response += f" | Venue: {e.venue}"
                response += f" | Class: {e.class_level}\n\n"
            return {"response": response, "type": "exam", "category": "Academics"}
        else:
            return {
                "response": "📚 No upcoming exams found! Keep preparing though! 💪",
                "type": "exam",
                "category": "Academics"
            }

    # Announcements
    announcement_keywords = ['announcement', 'news', 'notice', 'update', 'happening']
    if any(keyword in user_query.lower() for keyword in announcement_keywords):
        level = parse_class_level(user_query) or context.get('level')
        query = Announcement.query.filter(
            (Announcement.expires_at == None) |
            (Announcement.expires_at >= datetime.utcnow())
        )
        if level:
            query = query.filter((Announcement.target_class == level) | (Announcement.target_class == None))
        announcements = query.order_by(Announcement.created_at.desc()).limit(5).all()

        if announcements:
            response = "📢 **Latest Announcements:**\n\n"
            for a in announcements:
                priority_emoji = "🔴" if a.priority == "urgent" else "🟡" if a.priority == "important" else "📌"
                response += f"{priority_emoji} **{a.title}**\n{a.message}\n\n"
            return {"response": response, "type": "announcement", "category": "General"}
        else:
            return {
                "response": "📢 No new announcements at the moment. Check the notice board regularly!",
                "type": "announcement",
                "category": "General"
            }

    # Directions
    direction_keywords = ['where is', 'direction', 'find', 'location of', 'how to get', 'room', 'lab', 'office', 'dorm', 'dining', 'library', 'playground', 'headmaster', 'principal', 'staffroom', 'sickbay', 'reception']
    if any(keyword in user_query.lower() for keyword in direction_keywords):
        search_term = user_query.lower()
        loc = Location.query.filter(
            (Location.name.ilike(f"%{search_term}%")) |
            (Location.description.ilike(f"%search_term%")) |
            (Location.category.ilike(f"%search_term%"))
        ).first()

        if loc:
            response = f"📍 **{loc.name}**\n"
            if loc.building:
                response += f"🏢 Building: {loc.building}\n"
            if loc.floor:
                response += f"� floor: {loc.floor}\n"
            if loc.description:
                response += f"📝 {loc.description}\n"
            return {"response": response, "type": "location", "category": "General"}

        locations = Location.query.limit(10).all()
        if locations:
            response = "📍 **School Locations:**\n\n"
            for l in locations:
                emoji = {"classroom": "🚪", "lab": "🔬", "office": "🏫", "dorm": "🛏️", "cafeteria": "🍽️", "library": "📚", "sports": "⚽"}.get(l.category, "📍")
                response += f"{emoji} {l.name}"
                if l.building:
                    response += f" - {l.building}"
                response += "\n"
            response += "\nJust ask 'Where is [place]' for directions!"
            return {"response": response, "type": "location", "category": "General"}
        return {"response": "📍 Need directions? Try asking 'Where is the lab?' or 'Where is the staffroom?'", "type": "location", "category": "General"}

    # Quiz
    quiz_keywords = ['quiz', 'question of the day', 'trivia', 'challenge']
    if any(keyword in user_query.lower() for keyword in quiz_keywords):
        quiz = Quiz.query.order_by(db.func.random()).first()
        if quiz:
            response = f"🎮 **Quiz Time!** (Earn 10 points)\n\n{quiz.question}\n\n"
            for i, opt in enumerate(quiz.options):
                response += f"{i+1}. {opt}\n"
            response += "\nReply with the number of your answer!"
            return {"response": response, "type": "quiz", "category": "Fun"}
        return {"response": "🎮 No quiz available right now. Check back later!", "type": "quiz", "category": "Fun"}

    # Well-being / Help
    help_keywords = ['help', 'counselor', 'talk to someone', 'support', 'stress', 'feeling', 'bullying', 'report', 'unsafe']
    if any(keyword in user_query.lower() for keyword in help_keywords):
        if 'bully' in user_query.lower() or 'report' in user_query.lower():
            return {
                "response": "🛡️ **Report Safely**\n\nI'm sorry you're experiencing this. You can:\n\n1. Tell a teacher you trust\n2. Talk to the counselor: +256701416197\n3. Report anonymously via the school office\n\nYour safety matters. 💙",
                "type": "support",
                "category": "Well-being"
            }

        if 'counselor' in user_query.lower() or 'talk to' in user_query.lower():
            counselors = CounselorContact.query.all()
            if counselors:
                response = "🧠 **Counselor Contact:**\n\n"
                for c in counselors:
                    response += f"📞 **{c.name}** - {c.role}\n   Phone: {c.phone}\n"
                    if c.available_days:
                        response += f"   Available: {c.available_days}\n"
                    response += "\n"
                response += "They are here to help! 💙"
                return {"response": response, "type": "support", "category": "Well-being"}

        return {
            "response": "💙 **Need Support?**\n\nI'm here for you! You can:\n• Talk to the school counselor\n• Report bullying safely\n• Get study tips\n• Ask for motivation\n\nWhat do you need help with?",
            "type": "support",
            "category": "Well-being"
        }

    # Study tips
    study_keywords = ['study', 'how to study', 'tips', 'motivation', 'motivated', 'exam tips']
    if any(keyword in user_query.lower() for keyword in study_keywords):
        tips = [
            "📖 **Start with the hard stuff** - Tackle difficult topics when you're fresh!",
            "⏰ **Use the Pomodoro method** - 25 min study, 5 min break. Repeat!",
            "📝 **Practice past papers** - This is the best way to prepare!",
            "💤 **Sleep well** - Don't pull all-nighters before exams!",
            "🍎 **Take breaks** - Your brain needs rest to remember things.",
            "💪 **Stay positive** - You've got this! Believe in yourself!"
        ]
        import random
        tip = random.choice(tips)
        return {
            "response": f"💡 **Study Tip:**\n\n{tip}\n\nNeed more tips? Just ask!",
            "type": "study_tip",
            "category": "Well-being"
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


@app.route('/learning')
@login_required
def learning_assistant():
    student = get_current_student_record()
    performance_summary = build_performance_analysis(student)
    return render_template(
        'learning_assistant.html',
        student=student,
        performance_summary=performance_summary,
        subjects=['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'ICT']
    )


@app.route('/api/tutor', methods=['POST'])
@login_required
def api_tutor():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    subject = data.get('subject') or detect_subject(question)
    level = data.get('level') or parse_class_level(question)
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    answer = ai_tutor_answer(question, subject=subject, level=level)
    return jsonify({'answer': answer, 'subject': subject or 'AI Tutor'})


@app.route('/api/quiz/generate', methods=['POST'])
@login_required
def api_generate_quiz():
    data = request.get_json(silent=True) or {}
    subject = data.get('subject') or 'General Science'
    count = data.get('count', 5)
    level = data.get('level') or 'O-Level'
    return jsonify({'quiz': generate_quiz_text(subject, count=count, level=level)})


@app.route('/api/notes/summarize', methods=['POST'])
@login_required
def api_summarize_notes():
    notes = ''
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        notes = request.form.get('notes', '').strip()
        uploaded_file = request.files.get('file')
        if uploaded_file and not notes:
            filename = uploaded_file.filename or 'uploaded file'
            notes = f"The student uploaded {filename}. Text extraction is not configured yet, so ask them to paste the note text for summarizing."
    else:
        data = request.get_json(silent=True) or {}
        notes = data.get('notes', '').strip()

    if not notes:
        return jsonify({'error': 'Notes text is required'}), 400
    return jsonify({'summary': summarize_notes_text(notes)})


@app.route('/api/homework/help', methods=['POST'])
@login_required
def api_homework_help():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    subject = data.get('subject') or detect_subject(question)
    if not question:
        return jsonify({'error': 'Homework question is required'}), 400
    prompt = (
        "Help with this homework. Give hints first, explain the method, and then provide a clear final answer. "
        f"Question: {question}"
    )
    return jsonify({'answer': ai_tutor_answer(prompt, subject=subject), 'subject': subject or 'Homework'})


@app.route('/api/performance')
@login_required
def api_performance():
    student = get_current_student_record()
    return jsonify({'analysis': build_performance_analysis(student)})


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
        "payment_options": [
            "MTN Mobile Money Uganda",
            "Airtel Money Uganda",
            "Bank Transfer"
        ],
        "reference_note": "Create a payment request in the parent portal to get a payment reference number. For MTN Mobile Money dial *165# and for Airtel Money dial *185#, then include that reference in the payment reason/reference field.",
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
                "Medical form",
                "Admission fee payment proof"
            ],
            "admission_fee_payment": {
                "reference": "Create an admission fee payment request in the parent portal to receive a payment reference number.",
                "mtn_mobile_money": [
                    "Dial *165#",
                    "Select Payments",
                    "Select School Fees or Pay Bill",
                    "Enter the school payment details requested by the menu",
                    "Enter the admission fee amount",
                    "Enter the payment reference number",
                    "Confirm with your Mobile Money PIN",
                    "Keep the MTN transaction message"
                ],
                "airtel_money_uganda": [
                    "Dial *185#",
                    "Select Payments",
                    "Select School Fees or Pay Bill",
                    "Enter the school payment details requested by the menu",
                    "Enter the admission fee amount",
                    "Enter the payment reference number",
                    "Confirm with your Airtel Money PIN",
                    "Keep the Airtel transaction message"
                ]
            },
            "contact": {
                "phone": SCHOOL_INFO['phone'],
                "email": SCHOOL_INFO['email']
            },
            "online_form": "/admissions"
        }
    })


@app.route('/admissions', methods=['GET', 'POST'])
def admissions_page():
    """Render the admissions information page."""
    message = None
    error = None
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        class_level = request.form.get('class_level', '').strip()
        parent_name = request.form.get('parent_name', '').strip()
        parent_phone = request.form.get('parent_phone', '').strip()
        if not student_name or not class_level or not parent_name or not parent_phone:
            error = 'Please fill in student name, class applying for, parent name, and parent phone.'
        else:
            fee_amount_raw = request.form.get('admission_fee_amount', '').strip()
            try:
                fee_amount = float(fee_amount_raw) if fee_amount_raw else None
            except ValueError:
                fee_amount = None
            application = AdmissionApplication(
                student_name=student_name,
                class_level=class_level,
                date_of_birth=request.form.get('date_of_birth', '').strip(),
                gender=request.form.get('gender', '').strip(),
                previous_school=request.form.get('previous_school', '').strip(),
                parent_name=parent_name,
                parent_phone=parent_phone,
                parent_email=request.form.get('parent_email', '').strip(),
                home_address=request.form.get('home_address', '').strip(),
                emergency_name=request.form.get('emergency_name', '').strip(),
                emergency_phone=request.form.get('emergency_phone', '').strip(),
                medical_notes=request.form.get('medical_notes', '').strip(),
                admission_fee_amount=fee_amount,
                payment_method=request.form.get('payment_method', '').strip(),
                payment_reference=request.form.get('payment_reference', '').strip(),
                transaction_id=request.form.get('transaction_id', '').strip(),
            )
            db.session.add(application)
            db.session.commit()
            message = f'Admission application submitted successfully. Your application number is ADM-{application.id:05d}.'
    return render_template('admissions.html', school_info=SCHOOL_INFO, message=message, error=error)


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
            elif role == 'student' and child_level:
                student = Student(name=name, class_level=child_level)
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
        return redirect(url_for('admin_dashboard'))
    if current_user.role == 'staff':
        return redirect(url_for('teacher_portal'))
    if current_user.role == 'student':
        return redirect(url_for('student_portal'))
    return redirect(url_for('parent_portal'))


def get_learner_portal_context(role):
    child_students = []
    student = None
    marks = []
    timetable = []
    reminders = []
    comments = []
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).limit(5).all()

    if role == 'parent':
        child_students = Student.query.filter_by(parent_id=current_user.id).all()
        if child_students:
            student = child_students[0]
    elif role == 'student':
        student = Student.query.filter_by(name=current_user.name).first()

    if student:
        marks = Exam.query.filter_by(student_id=student.id).order_by(Exam.year.desc(), Exam.term.desc()).limit(8).all()
        comments = StudentComment.query.filter_by(student_id=student.id).order_by(StudentComment.created_at.desc()).limit(8).all()
        timetable = TimetableEntry.query.filter_by(class_level=student.class_level).order_by(TimetableEntry.day_of_week, TimetableEntry.period).limit(12).all()
        assignments = Assignment.query.filter_by(class_level=student.class_level).order_by(Assignment.due_date).limit(5).all()
        exams = ExamSchedule.query.filter_by(class_level=student.class_level).order_by(ExamSchedule.exam_date).limit(5).all()
        reminders = [
            {
                'title': assignment.title,
                'meta': f"{assignment.subject} assignment due {assignment.due_date.strftime('%Y-%m-%d')}",
            }
            for assignment in assignments
        ]
        reminders.extend([
            {
                'title': f"{exam.subject} exam",
                'meta': f"{exam.exam_date.strftime('%Y-%m-%d')} from {exam.start_time} to {exam.end_time}",
            }
            for exam in exams
        ])

    notices = Notification.query.filter((Notification.recipient_role == role) | (Notification.recipient_role == 'all')).order_by(Notification.created_at.desc()).limit(10).all()
    counselors = CounselorContact.query.order_by(CounselorContact.name).all()
    library_books = LibraryBook.query.order_by(LibraryBook.category, LibraryBook.title).limit(12).all()
    return {
        'child_students': child_students,
        'student': student,
        'notices': notices,
        'marks': marks,
        'comments': comments,
        'timetable': timetable,
        'reminders': reminders,
        'counselors': counselors,
        'library_books': library_books,
        'payments': payments,
    }


@app.route('/portals')
def portal_home():
    return render_template('portal_home.html')


@app.route('/parent')
@login_required
def parent_portal():
    if current_user.role != 'parent':
        return redirect(url_for('dashboard'))
    return render_template('parent_portal.html', **get_learner_portal_context('parent'))


@app.route('/parent/child/<int:student_id>')
@login_required
def parent_child_portal(student_id):
    if current_user.role != 'parent':
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(id=student_id, parent_id=current_user.id).first_or_404()
    marks = Exam.query.filter_by(student_id=student.id).order_by(Exam.year.desc(), Exam.term.desc()).all()
    comments = StudentComment.query.filter_by(student_id=student.id).order_by(StudentComment.created_at.desc()).all()
    timetable = TimetableEntry.query.filter_by(class_level=student.class_level).order_by(TimetableEntry.day_of_week, TimetableEntry.period).all()
    assignments = Assignment.query.filter_by(class_level=student.class_level).order_by(Assignment.due_date).limit(8).all()
    exams = ExamSchedule.query.filter_by(class_level=student.class_level).order_by(ExamSchedule.exam_date).limit(8).all()
    reminders = [
        {'title': assignment.title, 'meta': f"{assignment.subject} assignment due {assignment.due_date.strftime('%Y-%m-%d')}"}
        for assignment in assignments
    ]
    reminders.extend([
        {'title': f"{exam.subject} exam", 'meta': f"{exam.exam_date.strftime('%Y-%m-%d')} from {exam.start_time} to {exam.end_time}"}
        for exam in exams
    ])
    notices = Notification.query.filter((Notification.recipient_role == 'parent') | (Notification.recipient_role == 'all')).order_by(Notification.created_at.desc()).limit(8).all()
    return render_template(
        'parent_child_portal.html',
        student=student,
        marks=marks,
        comments=comments,
        timetable=timetable,
        reminders=reminders,
        notices=notices,
    )


@app.route('/student')
@login_required
def student_portal():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))
    return render_template('student_portal.html', **get_learner_portal_context('student'))


@app.route('/teacher')
@login_required
def teacher_portal():
    if current_user.role != 'staff':
        return redirect(url_for('dashboard'))
    students = Student.query.order_by(Student.class_level, Student.name).limit(20).all()
    recent_marks = Exam.query.options(db.joinedload(Exam.student)).order_by(Exam.year.desc(), Exam.term.desc()).limit(8).all()
    recent_comments = StudentComment.query.options(db.joinedload(StudentComment.student), db.joinedload(StudentComment.teacher)).order_by(StudentComment.created_at.desc()).limit(8).all()
    notices = Notification.query.filter((Notification.recipient_role == 'staff') | (Notification.recipient_role == 'all')).order_by(Notification.created_at.desc()).limit(6).all()
    timetable = TimetableEntry.query.order_by(TimetableEntry.day_of_week, TimetableEntry.period).limit(10).all()
    reminders = Assignment.query.order_by(Assignment.due_date).limit(6).all()
    return render_template(
        'teacher_portal.html',
        students=students,
        recent_marks=recent_marks,
        recent_comments=recent_comments,
        notices=notices,
        timetable=timetable,
        reminders=reminders,
    )


@app.route('/teacher/marks/add', methods=['POST'])
@login_required
def teacher_add_mark():
    if current_user.role != 'staff':
        return redirect(url_for('dashboard'))
    student_id = request.form.get('student_id')
    subject = request.form.get('subject', '').strip()
    score = request.form.get('score', '').strip()
    if student_id and subject and score:
        exam = Exam(
            student_id=int(student_id),
            subject=subject,
            score=float(score),
            grade=request.form.get('grade', '').strip(),
            term=request.form.get('term', '').strip(),
            year=request.form.get('year', '').strip(),
        )
        db.session.add(exam)
        db.session.commit()
    return redirect(url_for('teacher_portal'))


@app.route('/teacher/comments/add', methods=['POST'])
@login_required
def teacher_add_comment():
    if current_user.role != 'staff':
        return redirect(url_for('dashboard'))
    student_id = request.form.get('student_id')
    comment = request.form.get('comment', '').strip()
    if student_id and comment:
        student_comment = StudentComment(
            student_id=int(student_id),
            teacher_id=current_user.id,
            category=request.form.get('category', 'General').strip() or 'General',
            comment=comment,
        )
        db.session.add(student_comment)
        db.session.commit()
    return redirect(url_for('teacher_portal'))


def can_manage_laboratory():
    return session.get('admin_authenticated') or (
        current_user.is_authenticated and current_user.role in ['admin', 'staff']
    )


@app.route('/laboratory', methods=['GET', 'POST'])
def laboratory():
    message = None
    error = None
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type in ['item', 'experiment', 'schedule'] and not can_manage_laboratory():
            return redirect(url_for('auth_login'))
        if form_type == 'report' and not current_user.is_authenticated:
            return redirect(url_for('auth_login'))

        if form_type == 'item':
            name = request.form.get('name', '').strip()
            item_type = request.form.get('item_type', '').strip()
            if not name or not item_type:
                error = 'Please provide item name and type.'
            else:
                item = LabItem(
                    name=name,
                    item_type=item_type,
                    quantity=float(request.form.get('quantity') or 0),
                    unit=request.form.get('unit', '').strip(),
                    location=request.form.get('location', '').strip(),
                    safety_notes=request.form.get('safety_notes', '').strip(),
                    reorder_level=float(request.form.get('reorder_level') or 0),
                )
                db.session.add(item)
                db.session.commit()
                message = 'Laboratory inventory item saved.'
        elif form_type == 'experiment':
            title = request.form.get('title', '').strip()
            if not title:
                error = 'Please provide the experiment title.'
            else:
                experiment = LabExperiment(
                    title=title,
                    subject=request.form.get('subject', '').strip() or 'Science',
                    class_level=request.form.get('class_level', '').strip() or 'All',
                    objective=request.form.get('objective', '').strip(),
                    materials=request.form.get('materials', '').strip(),
                    procedure=request.form.get('procedure', '').strip(),
                    safety_precautions=request.form.get('safety_precautions', '').strip(),
                    expected_result=request.form.get('expected_result', '').strip(),
                )
                db.session.add(experiment)
                db.session.commit()
                message = 'Experiment procedure saved.'
        elif form_type == 'schedule':
            experiment_id = request.form.get('experiment_id')
            scheduled_date = request.form.get('scheduled_date')
            if not experiment_id or not scheduled_date:
                error = 'Please choose an experiment and date.'
            else:
                schedule = LabSchedule(
                    experiment_id=int(experiment_id),
                    class_level=request.form.get('class_level', '').strip(),
                    scheduled_date=datetime.strptime(scheduled_date, '%Y-%m-%d').date(),
                    start_time=request.form.get('start_time', '').strip(),
                    end_time=request.form.get('end_time', '').strip(),
                    laboratory=request.form.get('laboratory', '').strip() or 'Science Lab',
                    technician=request.form.get('technician', '').strip(),
                )
                db.session.add(schedule)
                db.session.commit()
                message = 'Practical lesson scheduled.'
        elif form_type == 'report':
            experiment_id = request.form.get('experiment_id')
            student_name = request.form.get('student_name', '').strip()
            if not experiment_id or not student_name:
                error = 'Please choose an experiment and provide student name.'
            else:
                report = LabReport(
                    experiment_id=int(experiment_id),
                    student_name=student_name,
                    class_level=request.form.get('class_level', '').strip(),
                    observations=request.form.get('observations', '').strip(),
                    conclusion=request.form.get('conclusion', '').strip(),
                )
                db.session.add(report)
                db.session.commit()
                message = 'Laboratory report submitted.'

    items = LabItem.query.order_by(LabItem.item_type, LabItem.name).all()
    experiments = LabExperiment.query.order_by(LabExperiment.subject, LabExperiment.class_level, LabExperiment.title).all()
    schedules = LabSchedule.query.options(db.joinedload(LabSchedule.experiment)).order_by(LabSchedule.scheduled_date, LabSchedule.start_time).all()
    reports = LabReport.query.options(db.joinedload(LabReport.experiment)).order_by(LabReport.submitted_at.desc()).limit(12).all()
    return render_template(
        'laboratory.html',
        items=items,
        experiments=experiments,
        schedules=schedules,
        reports=reports,
        can_manage=can_manage_laboratory(),
        message=message,
        error=error,
    )


@app.route('/api/laboratory')
def api_laboratory():
    items = LabItem.query.order_by(LabItem.item_type, LabItem.name).all()
    experiments = LabExperiment.query.order_by(LabExperiment.subject, LabExperiment.class_level).all()
    schedules = LabSchedule.query.options(db.joinedload(LabSchedule.experiment)).order_by(LabSchedule.scheduled_date).all()
    return jsonify({
        'inventory': [
            {
                'name': item.name,
                'type': item.item_type,
                'quantity': item.quantity,
                'unit': item.unit,
                'location': item.location,
                'safety_notes': item.safety_notes,
                'low_stock': item.is_low_stock,
            }
            for item in items
        ],
        'experiments': [
            {
                'title': experiment.title,
                'subject': experiment.subject,
                'class_level': experiment.class_level,
                'objective': experiment.objective,
                'materials': experiment.materials,
                'procedure': experiment.procedure,
                'safety_precautions': experiment.safety_precautions,
                'expected_result': experiment.expected_result,
            }
            for experiment in experiments
        ],
        'schedules': [
            {
                'experiment': schedule.experiment.title if schedule.experiment else 'Experiment',
                'class_level': schedule.class_level,
                'date': schedule.scheduled_date.isoformat(),
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'laboratory': schedule.laboratory,
                'technician': schedule.technician,
            }
            for schedule in schedules
        ],
    })


@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    message = None
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        method = request.form.get('method', 'MTN Mobile Money')
        reference = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
        payment = Payment(user_id=current_user.id, amount=amount, method=method, reference=reference, status='pending')
        db.session.add(payment)
        db.session.commit()
        message = f'Payment request created. Your payment reference number is {reference}. Use it when completing the mobile money payment.'
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template('payments.html', payments=payments, message=message, school_info=SCHOOL_INFO)


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
