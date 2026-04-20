"""
St. Jonathan High School Chatbot
Parent-School Communication System
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
import re

app = Flask(__name__)

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

FAQS = load_faqs()

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

def generate_response(user_query):
    """Generate chatbot response based on user query"""
    
    # Check for greetings
    greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in user_query.lower() for greeting in greetings):
        return {
            "response": f"Hello! Welcome to {SCHOOL_INFO['name']}. I'm your school assistant. How can I help you today? Feel free to ask me about admissions, fees, academics, or any other school-related information.",
            "type": "greeting"
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
        
        # Generate response
        bot_response = generate_response(user_message)
        
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
