# PythonAnywhere WSGI Configuration for St. Jonathan High School Chatbot
# Place this content in your WSGI configuration file (Web tab -> WSGI configuration file)

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/school_chatbot'  # Replace YOUR_USERNAME with your PythonAnywhere username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (replace with your actual values)
os.environ['SECRET_KEY'] = 'your-secure-random-secret-change-this-in-production'
os.environ['ADMIN_PASSWORD'] = 'your-admin-password-here'
os.environ['DEBUG'] = 'False'
os.environ['OPENAI_API_KEY'] = ''  # Optional: Add your OpenAI API key if using AI features
os.environ['TWILIO_ACCOUNT_SID'] = ''  # Optional: Add Twilio credentials for WhatsApp
os.environ['TWILIO_AUTH_TOKEN'] = ''  # Optional: Add Twilio credentials for WhatsApp
os.environ['TWILIO_WHATSAPP_NUMBER'] = ''  # Optional: Add Twilio WhatsApp number

# Import your Flask app
from app import app as application